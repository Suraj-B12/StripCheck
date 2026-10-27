"""Grounded local OCR/QR reads with explicit fallback to manual entry."""
import csv
import io
import json
import logging
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
from core import config
from core.textutils import find_batch, find_dates, find_party, MAKER_RE, MKT_RE, parse_qr_payload, batch_key

_rapid_engine = None
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

def validate_image(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("The uploaded image is unavailable")
    if path.stat().st_size > config.MAX_UPLOAD_BYTES:
        raise ValueError("Choose an image smaller than 15 MB")
    try:
        with Image.open(path) as image:
            if image.width * image.height > config.MAX_IMAGE_PIXELS:
                raise ValueError("Choose an image smaller than 24 megapixels")
            image.verify()
        with Image.open(path) as image:
            return ImageOps.exif_transpose(image).convert("RGB")
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError("This file could not be read as an image. Choose a JPEG, PNG or WebP photo.") from exc

def enhance(image):
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    image = ImageOps.autocontrast(ImageOps.grayscale(image))
    image = ImageEnhance.Contrast(image).enhance(1.35)
    return ImageEnhance.Sharpness(image).enhance(1.5)

def _vision_read(path, width, height):
    import Vision
    from Foundation import NSURL
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    request.setUsesLanguageCorrection_(False)
    request.setRecognitionLanguages_(["en-US"])
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_(str(path)), {})
    success, error = handler.performRequests_error_([request], None)
    if not success:
        raise RuntimeError(str(error or "Local Vision OCR could not read the image"))
    lines = []
    for observation in (request.results() or [])[:500]:
        candidates = observation.topCandidates_(1)
        if not candidates:
            continue
        candidate = candidates[0]
        rect = observation.boundingBox()
        left, top = rect.origin.x * width, (1 - rect.origin.y - rect.size.height) * height
        right, bottom = left + rect.size.width * width, top + rect.size.height * height
        lines.append({"text": str(candidate.string()), "score": float(candidate.confidence()),
                      "box": [[left, top], [right, top], [right, bottom], [left, bottom]], "engine": "Apple Vision"})
    return sorted(lines, key=lambda line: (round(line["box"][0][1] / 12), line["box"][0][0]))

def _vision_read_bounded(path, width, height, timeout=35):
    code = "import json,sys; from core.pack_tools import _vision_read; print(json.dumps(_vision_read(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))))"
    result = subprocess.run([sys.executable, "-c", code, str(path), str(width), str(height)],
                            cwd=config.ROOT, capture_output=True, text=True, timeout=timeout, check=True)
    return _worker_json(result.stdout)

def _vision_barcode(path):
    import Vision
    from Foundation import NSURL
    request = Vision.VNDetectBarcodesRequest.alloc().init()
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_(str(Path(path).resolve())), {})
    success, _ = handler.performRequests_error_([request], None)
    results = request.results() or []
    if success:
        return [{"raw": str(item.payloadStringValue() or ""), "format": str(item.symbology())}
                for item in results[:50]]
    return []

def _tesseract_read(path, timeout=30):
    result = subprocess.run([shutil.which("tesseract"), str(path), "stdout", "--psm", "6", "tsv"],
                            capture_output=True, text=True, timeout=timeout, check=True)
    if len(result.stdout) > 8 * 1024 * 1024:
        raise ValueError("Local OCR output exceeds the processing limit")
    grouped = {}
    for row in csv.DictReader(io.StringIO(result.stdout), delimiter="\t"):
        if not row.get("text", "").strip():
            continue
        key = (row.get("block_num"), row.get("par_num"), row.get("line_num"))
        grouped.setdefault(key, []).append(row)
    lines = []
    for words in list(grouped.values())[:500]:
        left = min(int(w["left"]) for w in words)
        top = min(int(w["top"]) for w in words)
        right = max(int(w["left"]) + int(w["width"]) for w in words)
        bottom = max(int(w["top"]) + int(w["height"]) for w in words)
        lines.append({"text": " ".join(w["text"] for w in words),
                      "score": sum(max(0, float(w["conf"])) for w in words) / (100 * len(words)),
                      "box": [[left, top], [right, top], [right, bottom], [left, bottom]], "engine": "Tesseract"})
    return lines

def _rapid_read(path):
    global _rapid_engine
    import rapidocr
    # Only use existing weights; an uploaded image must never trigger a model download.
    package = Path(rapidocr.__file__).parent
    if not any(package.rglob("*.onnx")):
        raise RuntimeError("RapidOCR weights are not installed locally")
    if _rapid_engine is None:
        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
        _rapid_engine = rapidocr.RapidOCR()
    result = _rapid_engine(str(path))
    if hasattr(result, "txts"):
        return [{"text": text, "score": float(score), "box": box.tolist(), "engine": "RapidOCR"}
                for text, score, box in zip([] if result.txts is None else result.txts, result.scores, result.boxes)]
    return [{"text": row[1], "score": float(row[2]), "box": row[0], "engine": "RapidOCR"} for row in (result[0] or [])]

def _worker_json(output):
    if len(output) > 8 * 1024 * 1024:
        raise ValueError("Local recognition output exceeds the processing limit")
    return json.loads(output)

def _normalize_lines(lines, width, height):
    """Untrusted local engine output must not crash evidence extraction or cropping."""
    if not isinstance(lines, list):
        return []
    clean = []
    for line in lines[:500]:
        if not isinstance(line, dict) or not isinstance(line.get("text"), str):
            continue
        text = line["text"].strip()
        box = line.get("box")
        if not text or len(text) > 2000 or not isinstance(box, list) or len(box) != 4:
            continue
        try:
            score = float(line.get("score", 0))
            points = [[float(point[0]), float(point[1])] for point in box if len(point) == 2]
            if len(points) != 4 or not math.isfinite(score) or not all(math.isfinite(v) for point in points for v in point):
                continue
        except (ValueError, TypeError, IndexError):
            continue
        points = [[min(width, max(0, x)), min(height, max(0, y))] for x, y in points]
        if max(p[0] for p in points) <= min(p[0] for p in points) or max(p[1] for p in points) <= min(p[1] for p in points):
            continue
        clean.append({"text": text, "score": min(1, max(0, score)), "box": points,
                      "engine": str(line.get("engine", "Local OCR"))[:80]})
    return clean

def _remaining(deadline, maximum):
    remaining = min(maximum, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError("Local image processing time limit reached")
    return remaining

def ocr_read(path, enhanced=False, *, _image=None, _deadline=None):
    image = (_image if _image is not None else validate_image(path)).copy()
    deadline = _deadline if _deadline is not None else time.monotonic() + 60
    original_width, original_height = image.size
    image.thumbnail((2400, 2400))
    if enhanced:
        image = enhance(image)
    with tempfile.TemporaryDirectory(prefix="stripcheck-ocr-") as folder:
        prepared = Path(folder) / "image.png"
        image.save(prepared)
        lines = []
        if sys.platform == "darwin":
            try:
                lines = _normalize_lines(_vision_read_bounded(prepared, image.width, image.height,
                                         timeout=_remaining(deadline, 30)), image.width, image.height)
            except (OSError, ImportError, RuntimeError, AttributeError, TypeError, subprocess.SubprocessError, ValueError):
                pass
        if not lines and shutil.which("tesseract"):
            try:
                lines = _normalize_lines(_tesseract_read(prepared, timeout=_remaining(deadline, 30)), image.width, image.height)
            except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
                pass
        if not lines:
            try:
                code = "import json,sys; from core.pack_tools import _rapid_read; print(json.dumps(_rapid_read(sys.argv[1])))"
                result = subprocess.run([sys.executable, "-c", code, str(prepared)], cwd=config.ROOT,
                                        capture_output=True, text=True, timeout=_remaining(deadline, 30), check=True)
                lines = _normalize_lines(_worker_json(result.stdout), image.width, image.height)
            except (OSError, ImportError, RuntimeError, AttributeError, TypeError, ValueError, subprocess.SubprocessError):
                lines = []
        for line in lines:
            line["box"] = [[x * original_width / image.width, y * original_height / image.height] for x, y in line["box"]]
        return lines

def _select_barcode(candidates):
    empty = {"found": False, "raw": "", "format": None, "fields": {}}
    if not isinstance(candidates, list):
        return empty
    decoded = []
    for item in candidates[:50]:
        if not isinstance(item, dict) or not isinstance(item.get("raw"), str) or not 0 < len(item["raw"]) <= 8192:
            continue
        raw = item["raw"]
        fields = parse_qr_payload(raw)
        fields = {key: value for key, value in fields.items() if isinstance(value, str) and len(value) <= 100}
        for name in ("mfg", "exp"):
            if name in fields and not re.fullmatch(r"(?:19|20)\d{2}-(?:0[1-9]|1[0-2])", fields[name]):
                del fields[name]
        decoded.append({"found": True, "raw": raw, "format": str(item.get("format", "Barcode"))[:80], "fields": fields})
    batches = {batch_key(item["fields"]["batch"]) for item in decoded if item["fields"].get("batch")}
    if len(batches) > 1:
        return {**empty, "found": True, "ambiguous": True}
    return next((item for item in decoded if item["fields"].get("batch")), decoded[0] if decoded else empty)

def _barcode_read(path):
    """Runs in a killable process; every recognition image stays at most 2400px."""
    candidates = []
    try:
        import zxingcpp
        with Image.open(path) as image:
            result = zxingcpp.read_barcodes(image)
            if not result:
                scale = min(2, 2400 / max(image.size))
                result = zxingcpp.read_barcodes(image.convert("L").resize((round(image.width * scale), round(image.height * scale))))
            candidates.extend({"raw": item.text, "format": str(item.format)} for item in result[:50])
    except (ImportError, OSError, ValueError, RuntimeError):
        pass
    if candidates:
        return candidates
    if sys.platform == "darwin":
        try:
            candidates = _vision_barcode(path)
        except (ImportError, OSError, RuntimeError, AttributeError, ValueError):
            pass
    if candidates:
        return candidates
    try:
        import cv2
        text, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(path)))
        if text:
            return [{"raw": text, "format": "QR"}]
    except (ImportError, OSError, ValueError, RuntimeError):
        pass
    return []

def decode_qr(path, *, _image=None, _deadline=None):
    image = (_image if _image is not None else validate_image(path)).copy()
    image.thumbnail((2400, 2400))
    deadline = _deadline if _deadline is not None else time.monotonic() + 20
    with tempfile.TemporaryDirectory(prefix="stripcheck-qr-") as folder:
        prepared = Path(folder) / "image.png"
        image.save(prepared)
        try:
            code = "import json,sys; from core.pack_tools import _barcode_read; print(json.dumps(_barcode_read(sys.argv[1])))"
            result = subprocess.run([sys.executable, "-c", code, str(prepared)], cwd=config.ROOT,
                                    capture_output=True, text=True, timeout=_remaining(deadline, 20), check=True)
            return _select_barcode(_worker_json(result.stdout))
        except (OSError, ImportError, RuntimeError, AttributeError, TypeError, ValueError, subprocess.SubprocessError):
            return _select_barcode([])

def extract_fields(ocr_lines, qr_fields=None, mode="photo"):
    lines = [line if isinstance(line, str) else str(line.get("text", "")) for line in ocr_lines]
    qr_fields = qr_fields or {}
    batch, batch_line = find_batch(lines)
    mfg, exp = find_dates(lines)
    for field, labels in (("mfg", r"mfg|mfd|manufacturing"), ("exp", r"exp|expiry|use before|best before")):
        hit = re.search(r"\b(?:" + labels + r")\.?\s*(?:date|dt)?\.?\s*[:\-]?\s*(\d{4}-(?:0[1-9]|1[0-2]))\b", " ".join(lines), re.I)
        if hit:
            if field == "mfg":
                mfg = hit.group(1)
            else:
                exp = hit.group(1)
    maker = find_party(lines, MAKER_RE) or ""
    candidates = []
    label_re = re.compile(r"\b(?:batch|lot|mfg|mfd|manufactured|exp|expiry|mrp|marketed|storage|store|keep|schedule|lic|synthetic|demonstration|fictional|not for|strip\s*check)\b", re.I)
    for i, line in enumerate(lines):
        if label_re.search(line) or len(re.sub(r"[^A-Za-z]", "", line)) < 4:
            continue
        height = 0
        if isinstance(ocr_lines[i], dict) and ocr_lines[i].get("box"):
            box = ocr_lines[i]["box"]
            height = max(p[1] for p in box) - min(p[1] for p in box)
        candidates.append((height, -i, line))
    product = max(candidates)[2] if candidates else ""
    brand = ""
    dose_form = re.compile(r"\b(?:tablet|tablets|capsules?|injection|syrup|suspension|solution|mg|ml|IP|BP|USP)\b", re.I)
    if len(candidates) > 1 and product and not dose_form.search(product) and len(product.split()) <= 4:
        if any(dose_form.search(line) for _, _, line in candidates if line != product):
            brand = product
    source = "qr" if qr_fields.get("batch") else "ocr" if batch else "none"
    fields = {"batch": qr_fields.get("batch") or batch or "", "product": product,
              "product_text": " ".join(line for _, _, line in candidates), "brand": brand,
              "mfg": qr_fields.get("mfg") or mfg or "", "exp": qr_fields.get("exp") or exp or "",
              "maker": maker, "marketer": find_party(lines, MKT_RE) or "", "source": source,
              "confirmed": source == "qr", "batch_line": batch_line}
    fields["provenance"] = {}
    for key in ("batch", "mfg", "exp", "maker", "product"):
        if fields[key]:
            fields["provenance"][key] = {"value": fields[key], "source": "qr" if qr_fields.get(key) else "ocr",
                                          "line": batch_line if key == "batch" else None}
    return fields

def read_pack(path):
    """Read only printed evidence; uncertain/missing fields remain for user confirmation."""
    image = validate_image(path)
    deadline = time.monotonic() + 60
    qr = decode_qr(path, _image=image, _deadline=deadline)
    lines = ocr_read(path, _image=image, _deadline=deadline)
    fields = extract_fields(lines, qr["fields"])
    warnings = []
    if qr.get("ambiguous"):
        warnings.append("More than one barcode batch was found. Confirm the batch printed on this pack.")
    if not fields.get("batch") and lines:
        enhanced_lines = ocr_read(path, enhanced=True, _image=image, _deadline=deadline)
        enhanced_fields = extract_fields(enhanced_lines, qr["fields"])
        if enhanced_fields.get("batch"):
            fields, lines = enhanced_fields, enhanced_lines
    if not lines:
        warnings.append("No printed text could be read locally. Enter the batch and product from the pack.")
    elif not fields.get("batch"):
        warnings.append("The batch label was not readable. Enter it exactly as printed.")
    if fields.get("source") == "ocr":
        warnings.append("Check the extracted characters against your pack before using a result.")
    if qr["fields"].get("batch"):
        ocr_batch, _ = find_batch([line["text"] for line in lines])
        if ocr_batch and batch_key(ocr_batch) != batch_key(fields["batch"]):
            warnings.append("The QR and printed batch reads differ. Confirm the batch on your pack.")
            fields["confirmed"] = False
            fields["source"] = "ocr"
            fields["batch"] = ocr_batch
            fields["provenance"]["batch"] = {"value": ocr_batch, "source": "ocr", "line": fields.get("batch_line")}
    return {"fields": fields, "lines": lines, "warnings": warnings, "boxes": [line["box"] for line in lines],
            "qr": qr, "engine": lines[0].get("engine") if lines else None}
