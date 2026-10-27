"""Local StripCheck API and same-origin production web host."""
import asyncio
import hmac
import hashlib
import importlib.util
import io
import json
import os
import re
import socket
import subprocess
import shutil
import threading
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from PIL import Image, UnidentifiedImageError
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.formparsers import MultiPartException

from core import config, db
from core.tracing import read_trace, record
from server.sse import stream_work

ROOT = Path(__file__).resolve().parents[1]
MAX_IMAGE_BYTES = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 24_000_000
FIELDS = ("batch", "product", "brand", "mfg", "exp", "maker")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _public(snapshot: dict) -> dict:
    return {key: value for key, value in snapshot.items() if key not in ("context", "_alerts", "_images")}


def _fields(payload: dict, required: bool = False) -> dict:
    if not isinstance(payload, dict):
        raise HTTPException(422, "Printed fields must be a JSON object.")
    fields = {}
    for key in FIELDS:
        value = payload.get(key, "")
        if value is None:
            value = ""
        if not isinstance(value, str) or len(value) > 500:
            raise HTTPException(422, f"{key} must be text with at most 500 characters.")
        fields[key] = value.strip()
    if required and not fields["batch"]:
        raise HTTPException(422, "Enter the batch number printed on the pack.")
    return {**fields, "source": "user", "confirmed": True}


async def _json(request: Request) -> dict:
    chunks, total = [], 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > 64 * 1024:
            raise HTTPException(413, "The request is too large.")
        chunks.append(chunk)
    content = b"".join(chunks)
    try:
        value = json.loads(content or b"{}")
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(400, "Send a valid JSON object.") from None
    if not isinstance(value, dict):
        raise HTTPException(422, "Send a JSON object.")
    return value


def _decode_upload(content: bytes, folder: Path) -> Path:
    """Decode/normalize away from the event loop and discard all image metadata."""
    path = folder / f"{uuid.uuid4().hex}.jpg"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as original:
                if original.width * original.height > MAX_IMAGE_PIXELS:
                    raise HTTPException(413, "Choose an image smaller than 24 megapixels.")
                original.verify()
            with Image.open(io.BytesIO(content)) as original:
                from PIL import ImageOps
                decoded = ImageOps.exif_transpose(original).convert("RGB")
                folder.mkdir(parents=True, exist_ok=True)
                decoded.save(path, "JPEG", quality=95)
                if path.stat().st_size > MAX_IMAGE_BYTES:
                    decoded.save(path, "JPEG", quality=85)
                if path.stat().st_size > MAX_IMAGE_BYTES:
                    raise HTTPException(413, "Choose a smaller photo so its decoded image stays under 15 MB.")
                return path
    except HTTPException:
        path.unlink(missing_ok=True)
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        path.unlink(missing_ok=True)
        raise HTTPException(422, "This file could not be read as an image. Use a JPEG, PNG, WebP or supported HEIC photo.") from None


async def _read_images(request: Request) -> tuple[list[Path], dict]:
    # Starlette's max_part_size only caps text fields, not uploaded file bodies.
    # Bound the entire incoming stream before its multipart parser can spool it.
    limit, received = 2 * MAX_IMAGE_BYTES + 64 * 1024, 0
    oversized = False
    try:
        if int(request.headers.get("content-length", "0")) > limit:
            raise HTTPException(413, "Upload no more than two images, each up to 15 MB.")
    except ValueError:
        raise HTTPException(400, "The upload size header is invalid.") from None
    async def bounded_receive():
        nonlocal received, oversized
        message = await request.receive()
        received += len(message.get("body", b""))
        if received > limit:
            oversized = True
            raise MultiPartException("The total upload exceeds the request limit.")
        return message
    bounded = Request(request.scope, receive=bounded_receive)
    try:
        form = await bounded.form(max_files=2, max_fields=20, max_part_size=2048)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(413 if oversized else 400, "Upload no more than two images, each up to 15 MB.") from None
    uploads = [value for _, value in form.multi_items() if isinstance(value, UploadFile)]
    paths = []
    try:
        if not 1 <= len(uploads) <= 2:
            raise HTTPException(422, "Choose one or two clear photos of the pack.")
        for upload in uploads:
            content = await upload.read(MAX_IMAGE_BYTES + 1)
            if len(content) > MAX_IMAGE_BYTES:
                raise HTTPException(413, "Each image must be no larger than 15 MB.")
            path = await asyncio.to_thread(_decode_upload, content, Path(config.DATA_DIR) / "uploads")
            paths.append(path)
        metadata = {key: value for key, value in form.items() if isinstance(value, str)}
        return paths, metadata
    except BaseException:
        for path in paths:
            path.unlink(missing_ok=True)
        raise
    finally:
        await form.close()


def _snapshot_events(emit, snapshot: dict, previous_steps: int = 0) -> None:
    emit("fields", {"fields": snapshot.get("fields", {})})
    strip = snapshot.get("strip") or {}
    emit("strip", strip if isinstance(strip, dict) else {"chars": strip})
    for item in snapshot.get("history", [])[previous_steps:]:
        emit("step", item if isinstance(item, dict) else {"summary": str(item)})
    emit("candidates", {"items": snapshot.get("candidates", [])})
    if snapshot.get("pending"):
        emit("interrupt", snapshot["pending"])
    if snapshot.get("final"):
        emit("final", snapshot["final"])
    emit("snapshot", {"snapshot": _public(snapshot)})
    emit("done", {"status": snapshot.get("status", "done")})


def _local_ip() -> str:
    try:
        # Host lookup only; no contact with the internet is required.
        addresses = socket.gethostbyname_ex(socket.gethostname())[2]
        for address in addresses:
            if not address.startswith("127."):
                return address
    except OSError:
        pass
    executable = shutil.which("ifconfig") or ("/sbin/ifconfig" if Path("/sbin/ifconfig").is_file() else None)
    if executable:
        try:
            result = subprocess.run([executable], capture_output=True, text=True, timeout=2, check=True)
            for address in re.findall(r"^\s+inet (\d+\.\d+\.\d+\.\d+)", result.stdout, re.M):
                if not address.startswith(("127.", "169.254.")):
                    return address
        except (OSError, subprocess.SubprocessError):
            pass
    return "127.0.0.1"


def _coverage_stats():
    statistics = db.stats()
    months = statistics.get("months", [])
    count = len(months) if isinstance(months, list) else int(statistics.get("month_count", 0))
    notice = "No official alert lists have been loaded yet."
    if count:
        notice = f"Checks cover only the {count} loaded month{'s' if count != 1 else ''}. Earlier or later alerts may not be included."
    return {**statistics, "coverage": {"scope": "loaded_lists_only", "month_count": count,
             "earliest_month": statistics.get("earliest_month"), "latest_month": statistics.get("latest_month"),
             "limited": True, "notice": notice}, "coverage_warning": notice}


def _cabinet_public(item):
    return {**item, "last_verdict": (item.get("final") or {}).get("label", "CANT_VERIFY"),
            "last_checked_at": item.get("last_checked"), "added_at": item.get("created_at"),
            "batch_display": item.get("fields", {}).get("batch", ""), "check_thread_id": item.get("thread_id")}


def _candidate_batches(fields, answer=None):
    """Include both current and user-edited batches when preparing a resumed check."""
    from core.textutils import batch_key
    answer = answer or {}
    values = [fields.get("batch"), answer.get("typed")]
    if isinstance(answer.get("fields"), dict):
        values.append(answer["fields"].get("batch"))
    key = batch_key(fields.get("batch"))
    if isinstance(answer.get("chars"), dict):
        chars = list(key)
        for index in range(len(chars)):
            new = answer["chars"].get(str(index + 1), answer["chars"].get(index + 1))
            if isinstance(new, str) and re.fullmatch(r"[A-Za-z0-9]", new):
                chars[index] = new.upper()
        values.append("".join(chars))
    return list(dict.fromkeys(key for value in values if 2 <= len(key := batch_key(value)) <= 40))


def create_app(db_path=None, *, lan=False, port=8000) -> FastAPI:
    bound_db_path = db.init_db(db_path)
    application = FastAPI(title="StripCheck", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)
    application.state.db_path = bound_db_path
    application.state.image_slots = asyncio.Semaphore(2)
    application.state.lan = lan
    application.state.port = port
    application.state.busy_checks = set()
    application.state.lock = threading.Lock()
    application.state.sync_lock = threading.Lock()
    application.state.eval_lock = threading.Lock()

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse({"error": {"message": str(exc.detail), "status": exc.status_code}}, status_code=exc.status_code, headers=exc.headers)

    @application.exception_handler(Exception)
    async def unexpected_error(request, exc):
        return JSONResponse({"error": {"message": "The local server could not complete this request. Please retry.", "status": 500}}, status_code=500)

    @application.exception_handler(RequestValidationError)
    async def input_error(request, exc):
        return JSONResponse({"error": {"message": "One or more request values are invalid.", "status": 422}}, status_code=422)

    @application.middleware("http")
    async def local_access(request: Request, call_next):
        origin = request.headers.get("origin")
        try:
            origin_host = urlsplit(origin).netloc if origin else None
        except ValueError:
            origin_host = "invalid-origin"
        if request.method not in ("GET", "HEAD", "OPTIONS") and origin and origin_host != request.url.netloc:
            return JSONResponse({"error": {"message": "Use the website served by this StripCheck server.", "status": 403}}, status_code=403)
        token = os.getenv("STRIPCHECK_LAN_TOKEN", "")
        supplied = request.query_params.get("k") or request.cookies.get("stripcheck_pair") or request.headers.get("X-StripCheck-Key", "")
        if application.state.lan and token and not hmac.compare_digest(supplied.encode("utf-8"), token.encode("utf-8")):
            return JSONResponse({"error": {"message": "Pair this device using the link shown on the host computer.", "status": 401}}, status_code=401)
        with db.using_database(application.state.db_path):
            response = await call_next(request)
        if application.state.lan and token and request.query_params.get("k") and hmac.compare_digest(supplied.encode("utf-8"), token.encode("utf-8")):
            response.set_cookie("stripcheck_pair", token, httponly=True, samesite="strict", max_age=86400)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    def lan_info():
        host = _local_ip() if application.state.lan else "127.0.0.1"
        url = f"http://{host}:{application.state.port}"
        token = os.getenv("STRIPCHECK_LAN_TOKEN", "")
        if application.state.lan and token:
            url += "?k=" + quote(token, safe="")
        return {"enabled": application.state.lan, "url": url, "lan_url": url,
                "token_required": bool(application.state.lan and token), "host": host, "port": application.state.port,
                "notice": "Use a device on the same trusted Wi-Fi network." if application.state.lan else "Start the server with --lan to connect a phone on the same Wi-Fi."}

    @application.get("/api/health")
    def health():
        statistics = _coverage_stats()
        pairing = lan_info()
        return {"status": "ok", "version": "1.0.0", "mode": "local", "offline_ready": True,
                "ollama": {"up": False, "models": [], "llm_ok": False, "vlm_ok": False, "status": "optional_not_connected"},
                "phoenix": {"up": False, "status": "local_traces_available"}, "db": statistics,
                "ocr": {"available": any(importlib.util.find_spec(package) is not None for package in ("rapidocr", "pytesseract", "Vision"))},
                "lan_url": pairing["url"], "lan": pairing, "coverage": statistics["coverage"], "coverage_warning": statistics["coverage_warning"],
                "notice": "Checks use the alert lists stored on this computer. Demo scenarios are isolated synthetic examples."}

    @application.get("/api/stats")
    def stats():
        return _coverage_stats()

    @application.get("/api/alerts")
    def alerts(q: str = "", batch: str = "", month: str = "", kind: str = "", level: str = "", page: int = 1, size: int = 30):
        if not 1 <= size <= 100 or page < 1:
            raise HTTPException(422, "Choose a valid page and a page size from 1 to 100.")
        if len(batch) > 80 or len(q) > 500:
            raise HTTPException(422, "Use a batch of at most 80 characters and a search of at most 500 characters.")
        if not batch:
            return db.list_alerts(q=q, month=month, kind=kind, page=page, size=size, level=level)
        from core.matching import build_index, search_exact, search_variants
        from core.textutils import batch_key
        rows = db.batch_alerts(batch, q=q, month=month, kind=kind, level=level)
        index = build_index(rows)
        requested = batch_key(batch)
        matches = search_exact(index, requested) + search_variants(index, requested)
        for item in matches:
            count = len(item.get("subs", []))
            item["match_type"] = "exact" if count == 0 else "variant"
            item["match_label"] = "Exact batch" if count == 0 else f"{count} character{'s' if count != 1 else ''} differ{'s' if count == 1 else ''}"
        return {"items": matches[(page - 1) * size:page * size], "total": len(matches), "page": page,
                "pages": max(1, (len(matches) + size - 1) // size), "size": size}

    @application.get("/api/alerts/{alert_id}")
    def alert_detail(alert_id: str):
        row = db.alert_detail(alert_id)
        if not row:
            raise HTTPException(404, "This alert was not found in the loaded lists.")
        return row

    @application.get("/api/sources")
    def sources():
        return {"items": db.list_documents("sources", limit=1000)}

    @application.get("/api/quarantine")
    def quarantine():
        return {"items": db.list_documents("quarantine", limit=1000)}

    @application.get("/api/checks")
    def checks(limit: int = 50):
        return {"items": [_public(item) for item in db.list_documents("checks", limit=max(1, min(limit, 200)))]}

    @application.get("/api/checks/{thread_id}")
    def check_snapshot(thread_id: str):
        value = db.get_document("checks", thread_id)
        if not value:
            raise HTTPException(404, "This check was not found on this computer.")
        return _public(value)

    def reserve(thread_id, expected=None):
        with application.state.lock:
            if thread_id in application.state.busy_checks:
                raise HTTPException(409, "This check is already running.")
            if expected is not None:
                current = db.get_document("checks", thread_id)
                if not current or current.get("status") != "waiting" or current.get("updated_at") != expected.get("updated_at"):
                    raise HTTPException(409, "This check changed while the answer was being prepared. Reload the check to continue.")
            application.state.busy_checks.add(thread_id)

    def release(thread_id):
        with application.state.lock:
            application.state.busy_checks.discard(thread_id)

    async def respond(request, thread_id, work, error=None):
        if "application/json" in request.headers.get("accept", ""):
            try:
                value = await asyncio.to_thread(work, lambda *_: None)
                return JSONResponse(value)
            except Exception as exc:
                if error:
                    await asyncio.to_thread(error, exc)
                raise HTTPException(500, "This operation could not complete. Please retry.") from None
        return stream_work(thread_id, work, on_error=error)

    async def run_check(request, thread_id, fields, *, images=None, previous=None, answer=None, demo_case=None):
        await asyncio.to_thread(reserve, thread_id, previous)
        created = (previous or {}).get("created_at", now())
        starter = {**(previous or {}), "thread_id": thread_id, "status": "running", "fields": fields,
                   "created_at": created, "updated_at": now(), "demo": bool(demo_case or (previous or {}).get("demo"))}
        if demo_case:
            starter["demo_case_id"] = demo_case["id"]
        try:
            await asyncio.to_thread(db.save_document, "checks", thread_id, starter)
        except Exception:
            release(thread_id)
            raise

        def failure(exc):
            failed = {**starter, "status": "error", "error": "This check could not complete. You can start a new check.", "updated_at": now()}
            try:
                db.save_document("checks", thread_id, failed)
                record(thread_id, "error", {"message": str(exc)[:400], "recoverable": False})
            finally:
                release(thread_id)

        def work(emit):
            from core.investigator import investigate
            working_fields = dict(fields)
            try:
                warnings_found = []
                if images:
                    from core.pack_tools import read_pack
                    image_fields = {}
                    reader_batches = []
                    for image_path in images:
                        emit("step", {"node": "perception", "summary": "Reading the printed pack details locally.", "source": "ocr"})
                        reading = read_pack(image_path)
                        from core.textutils import batch_key
                        observed = batch_key(reading.get("fields", {}).get("batch", ""))
                        if observed and observed not in reader_batches:
                            reader_batches.append(observed)
                        for key, value in reading.get("fields", {}).items():
                            if value and not image_fields.get(key):
                                image_fields[key] = value
                            if value and not working_fields.get(key) and answer is None:
                                working_fields[key] = value
                        warnings_found.extend(reading.get("warnings", []))
                    if answer is not None:
                        answer["fields"] = image_fields
                        answer["source"] = "carton"
                context = (previous or {}).get("context")
                alert_rows = []
                if demo_case:
                    alert_rows = demo_case.get("alerts", [])
                    context = {"demo": True, "real_alert_count": 0}
                elif (previous or {}).get("demo"):
                    from core.props import demo_cases
                    saved_case = next((case for case in demo_cases() if case["id"] == previous.get("demo_case_id")), None)
                    alert_rows = saved_case.get("alerts", []) if saved_case else []
                else:
                    from core.supervisor import confusion_counts
                    context = {**(context or {}), **db.check_coverage(), "candidate_subset": True}
                    if "confusion_counts" not in context:
                        context["confusion_counts"] = confusion_counts()
                    unique = {}
                    for key in _candidate_batches(working_fields, answer):
                        for row in db.batch_alerts(key, limit=21):
                            unique[row["id"]] = row
                    alert_rows = list(unique.values())
                if images:
                    context = {**(context or {}), "reader_disagreement": len(reader_batches) > 1, "reader_batches": reader_batches}
                    if len(reader_batches) > 1:
                        warnings_found.append("The photos show different batch readings. Confirm the printed batch before continuing.")
                snapshot = investigate(working_fields, alert_rows, context=context, answer=answer)
                snapshot.update({"thread_id": thread_id, "created_at": created, "updated_at": now(), "demo": starter["demo"]})
                if starter.get("demo_case_id"):
                    snapshot["demo_case_id"] = starter["demo_case_id"]
                if warnings_found:
                    snapshot["warnings"] = warnings_found
                from core.supervisor import remember_correction
                learned = remember_correction(thread_id, previous, snapshot, answer)
                db.save_document("checks", thread_id, snapshot)
                if learned:
                    record(thread_id, "learning", {"summary": f"Stored {learned} explicitly confirmed character correction(s) for future ranking. Confirmation gates are unchanged.", "count": learned})
                def traced_emit(event, data):
                    record(thread_id, event, data)
                    emit(event, data)
                _snapshot_events(traced_emit, snapshot, len((previous or {}).get("history", [])))
                return _public(snapshot)
            except Exception as exc:
                failure(exc)
                raise
            finally:
                release(thread_id)

        return await respond(request, thread_id, work)

    @application.post("/api/checks")
    async def start_check(request: Request):
        images = []
        if "multipart/form-data" in request.headers.get("content-type", ""):
            async with application.state.image_slots:
                images, metadata = await _read_images(request)
            fields = {key: value for key, value in metadata.items() if key in FIELDS and value}
            if fields:
                fields = _fields(fields)
        else:
            payload = await _json(request)
            fields = _fields(payload.get("fields", payload), required=True)
        thread_id = "check-" + uuid.uuid4().hex
        return await run_check(request, thread_id, fields, images=images)

    @application.post("/api/checks/{thread_id}/resume")
    async def resume_check(thread_id: str, request: Request):
        previous = await asyncio.to_thread(db.get_document, "checks", thread_id)
        if not previous:
            raise HTTPException(404, "This check was not found on this computer.")
        if previous.get("status") != "waiting":
            raise HTTPException(409, "This check has no question waiting for an answer.")
        images = []
        if "multipart/form-data" in request.headers.get("content-type", ""):
            async with application.state.image_slots:
                images, _ = await _read_images(request)
            answer = {"image": True}
        else:
            answer = await _json(request)
            answer["source"] = "user"
            if not any(key in answer for key in ("choice", "typed", "skip", "chars", "fields", "confirm")):
                raise HTTPException(422, "Choose an answer, type the printed value, or skip this question.")
            for key in ("typed", "choice"):
                if key in answer and (not isinstance(answer[key], str) or len(answer[key]) > 500):
                    raise HTTPException(422, "The answer must be text with at most 500 characters.")
            if "skip" in answer and not isinstance(answer["skip"], bool):
                raise HTTPException(422, "The skip value must be true or false.")
            if "fields" in answer:
                answer["fields"] = _fields(answer["fields"])
        return await run_check(request, thread_id, previous.get("fields", {}), images=images, previous=previous, answer=answer)

    @application.get("/api/demo/cases")
    def demo_cases():
        from core.props import demo_cases as get_cases
        return {"items": [{key: value for key, value in case.items() if key not in ("alerts", "answers")} for case in get_cases()], "synthetic": True}

    @application.post("/api/demo/checks")
    async def start_demo(request: Request):
        from core.props import demo_cases as get_cases
        payload = await _json(request)
        case_id = str(payload.get("case_id", "01"))
        case = next((case for case in get_cases() if case["id"] == case_id or case.get("slug") == case_id), None)
        if not case:
            raise HTTPException(404, "This synthetic scenario was not found.")
        return await run_check(request, "demo-" + uuid.uuid4().hex, dict(case.get("fields", {})), demo_case=case)

    @application.get("/api/demo/cases/{case_id}/image")
    def demo_image(case_id: str):
        from core.props import render_demo
        try:
            path = render_demo(case_id)
        except (KeyError, ValueError):
            raise HTTPException(404, "This synthetic scenario was not found.") from None
        return FileResponse(path, media_type="image/png")

    @application.post("/api/sync")
    async def sync_lists(request: Request):
        payload = await _json(request)
        if any(key in payload and not isinstance(payload[key], bool) for key in ("offline", "full")):
            raise HTTPException(422, "Sync options must be true or false.")
        if not application.state.sync_lock.acquire(blocking=False):
            raise HTTPException(409, "An alert list sync is already running.")
        thread_id = "sync-" + uuid.uuid4().hex
        def work(emit):
            from core.supervisor import sync_and_recheck
            try:
                def progress(event):
                    record(thread_id, event.get("type", "step"), event)
                    emit(event.get("type", "step"), event)
                report = sync_and_recheck(progress, offline=bool(payload.get("offline", False)), full=bool(payload.get("full", False)))
                db.save_document("sync", "latest", report)
                emit("report", report)
                emit("final", report)
                emit("done", {"status": "done"})
                return report
            finally:
                application.state.sync_lock.release()
        return await respond(request, thread_id, work)

    @application.get("/api/cabinet")
    def cabinet():
        return {"items": [_cabinet_public(item) for item in db.list_documents("cabinet", limit=1000)]}

    @application.post("/api/cabinet")
    async def save_cabinet(request: Request):
        payload = await _json(request)
        def save():
            snapshot = db.get_document("checks", str(payload.get("thread_id", "")))
            if not snapshot:
                raise HTTPException(404, "Finish a check before saving it to your cabinet.")
            if snapshot.get("status") != "done" or not snapshot.get("final"):
                raise HTTPException(409, "Finish this check before saving the pack.")
            if not snapshot.get("fields", {}).get("batch"):
                raise HTTPException(422, "A printed batch number is required to save this pack.")
            label = payload.get("label", "")
            if not isinstance(label, str) or len(label) > 100:
                raise HTTPException(422, "Use a label with at most 100 characters.")
            existing = db.cabinet_for_check(snapshot["thread_id"])
            identifier = existing["id"] if existing else hashlib.sha256(snapshot["thread_id"].encode()).hexdigest()[:32]
            item = {"id": identifier, "thread_id": snapshot["thread_id"], "label": label.strip() or snapshot["fields"].get("brand") or snapshot["fields"].get("product") or "Saved pack",
                    "fields": snapshot["fields"], "final": snapshot["final"], "batch_evidence": snapshot["final"].get("batch_evidence"),
                    "demo": bool(snapshot.get("demo")), "created_at": (existing or {}).get("created_at", now()), "last_checked": now()}
            db.save_document("cabinet", identifier, item)
            return _cabinet_public(item)
        return await asyncio.to_thread(save)

    @application.post("/api/cabinet/recheck")
    async def recheck():
        from core.supervisor import recheck_cabinet
        return await asyncio.to_thread(recheck_cabinet)

    @application.delete("/api/cabinet/{item_id}")
    def remove_cabinet(item_id: str):
        if not db.delete_cabinet_item(item_id):
            raise HTTPException(404, "This saved pack was not found.")
        return {"deleted": True, "id": item_id}

    @application.get("/api/notifications")
    def notifications():
        return {"items": db.list_documents("notifications", limit=1000)}

    @application.post("/api/notifications/{notification_id}/seen")
    def notification_seen(notification_id: str):
        item = db.get_document("notifications", notification_id)
        if not item:
            raise HTTPException(404, "This notification was not found.")
        item["seen"] = True
        db.save_document("notifications", notification_id, item)
        return item

    @application.get("/api/eval/latest")
    def evaluation_latest():
        from core.evaluate import latest
        return latest()

    @application.post("/api/eval/quick")
    async def evaluation_quick(request: Request):
        if not application.state.eval_lock.acquire(blocking=False):
            raise HTTPException(409, "Diagnostics are already running.")
        thread_id = "eval-" + uuid.uuid4().hex
        def work(emit):
            from core.evaluate import run_quick
            try:
                report = run_quick(lambda item: emit("step", item))
                emit("report", report)
                emit("final", report)
                emit("done", {"status": "done"})
                return report
            finally:
                application.state.eval_lock.release()
        return await respond(request, thread_id, work)

    @application.get("/api/traces/{thread_id}")
    def traces(thread_id: str):
        return {"thread_id": thread_id, "items": read_trace(thread_id), "backend": "local_jsonl"}

    @application.get("/api/lan")
    def pairing():
        return lan_info()

    @application.get("/api/lan/qr.png")
    def pairing_qr():
        import qrcode
        image = qrcode.make(lan_info()["url"])
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return Response(buffer.getvalue(), media_type="image/png")

    @application.get("/api/crops/{crop_id}.png")
    def crop(crop_id: str):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", crop_id):
            raise HTTPException(404, "This crop was not found.")
        path = Path(config.DATA_DIR) / "crops" / (crop_id + ".png")
        if not path.is_file():
            raise HTTPException(404, "This crop was not found.")
        return FileResponse(path, media_type="image/png")

    @application.get("/api/alerts/{alert_id}/source.png")
    def source_image(alert_id: str):
        row = db.alert_detail(alert_id)
        if not row:
            raise HTTPException(404, "This alert was not found.")
        path = Path(config.DATA_DIR) / "source_images" / (str(row.get("id", alert_id)) + ".png")
        if not path.is_file():
            raise HTTPException(404, "This source is stored as structured portal data; a page image is not available.")
        return FileResponse(path, media_type="image/png")

    @application.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path.startswith("api/"):
            raise HTTPException(404, "This API endpoint was not found.")
        dist = ROOT / "web" / "dist"
        requested = (dist / path).resolve()
        if requested.is_relative_to(dist.resolve()) and requested.is_file():
            return FileResponse(requested)
        index = dist / "index.html"
        if index.is_file():
            return FileResponse(index)
        return HTMLResponse("<!doctype html><html><head><title>StripCheck</title></head><body style='font-family:system-ui;padding:48px;font-size:20px'><h1>StripCheck server is running.</h1><p>Build the website with <code>npm --prefix web run build</code>, then refresh this page.</p><a href='/api/docs'>Open the API reference</a></body></html>", status_code=200)

    return application


app = create_app()
