"""Local, best-effort JSONL tracing, plus optional OpenTelemetry export to Phoenix.

The JSONL log needs nothing. The OTel export runs only when STRIPCHECK_TRACING=1,
the opentelemetry SDK is installed and the collector port answers a quick probe.
Spans go through a background batch processor, so a check never waits on Phoenix.
"""
import json
import os
import re
import socket
import threading
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit

_LOCK = threading.Lock()
_OTEL = {"tracer": None, "provider": None, "tried": False, "probe_at": 0.0, "probe_ok": False}
PROBE_SECONDS, PROBE_TIMEOUT = 15, 0.25


def _folder() -> Path:
    from core import config
    return Path(config.DATA_DIR) / "traces"


def _valid(thread_id: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", thread_id))


def record(thread_id: str, event: str, data: dict | None = None) -> None:
    if not _valid(thread_id):
        return
    try:
        row = {"at": datetime.now(timezone.utc).isoformat(), "thread_id": thread_id,
               "event": event, "model": None, "tokens_in": 0, "tokens_out": 0,
               "fallback": False, **(data or {})}
        with _LOCK:
            folder = _folder()
            folder.mkdir(parents=True, exist_ok=True)
            with (folder / f"{thread_id}.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    except (OSError, TypeError, ValueError):
        pass


def read_trace(thread_id: str) -> list[dict]:
    if not _valid(thread_id):
        return []
    try:
        path = _folder() / f"{thread_id}.jsonl"
        if not path.is_file():
            return []
        rows = []
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= 2000:
                    break
                try:
                    rows.append(json.loads(line))
                except (ValueError, TypeError):
                    continue
        return rows
    except OSError:
        return []


# ---------------------------------------------------------------- OpenTelemetry

def otel_endpoint() -> str:
    return os.environ.get("STRIPCHECK_PHOENIX_URL", "http://127.0.0.1:6006/v1/traces")


def otel_enabled() -> bool:
    return os.environ.get("STRIPCHECK_TRACING", "0").strip().lower() in {"1", "true", "yes", "on"}


def _probe() -> bool:
    """Cached TCP probe of the collector so a stopped Phoenix costs nothing."""
    now = monotonic()
    if now - _OTEL["probe_at"] < PROBE_SECONDS:
        return _OTEL["probe_ok"]
    _OTEL["probe_at"] = now
    try:
        parts = urlsplit(otel_endpoint())
        if parts.hostname not in {"127.0.0.1", "localhost", "::1"}:
            _OTEL["probe_ok"] = False
            return False
        with socket.create_connection((parts.hostname, parts.port or 80), timeout=PROBE_TIMEOUT):
            _OTEL["probe_ok"] = True
    except OSError:
        _OTEL["probe_ok"] = False
    return _OTEL["probe_ok"]


def _tracer():
    if not otel_enabled() or not _probe():
        return None
    if _OTEL["tried"]:
        return _OTEL["tracer"]
    _OTEL["tried"] = True
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        provider = TracerProvider(resource=Resource.create({"service.name": "stripcheck", "openinference.project.name": "stripcheck"}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint(), timeout=3), schedule_delay_millis=500))
        _OTEL["provider"], _OTEL["tracer"] = provider, provider.get_tracer("stripcheck")
    except Exception:
        _OTEL["tracer"] = None
    return _OTEL["tracer"]


def flush(timeout_ms: int = 3000) -> bool:
    try:
        provider = _OTEL["provider"]
        return bool(provider and provider.force_flush(timeout_ms))
    except Exception:
        return False


def _text(value) -> str:
    try:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(value)
    return text[:8000]


def _attributes(kind: str, item: dict) -> dict:
    attrs = {"openinference.span.kind": kind}
    if item.get("input") is not None:
        attrs.update({"input.value": _text(item["input"]), "input.mime_type": "application/json"})
    if item.get("output") is not None:
        attrs.update({"output.value": _text(item["output"]), "output.mime_type": "application/json"})
    for key, value in (item.get("attributes") or {}).items():
        if isinstance(value, (str, bool, int, float)):
            attrs[str(key)] = value
        elif value is not None:
            attrs[str(key)] = _text(value)
    return attrs


def export_check(segment: dict) -> dict | None:
    """Export one check segment as a nested trace; return its root span ids.

    segment: {name, session, start_ns, end_ns, input, output, attributes,
              parent: {trace_id, span_id} | None,
              steps: [{name, kind, start_ns, end_ns, input, output, attributes, children: [...]}]}
    A resumed check passes the first segment's ids as `parent`, so both
    segments land in one Phoenix trace. Never raises.
    """
    try:
        tracer = _tracer()
        if tracer is None:
            return None
        from opentelemetry import trace
        from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
        parent_ctx = None
        parent = segment.get("parent") or {}
        if parent.get("trace_id") and parent.get("span_id"):
            span_context = SpanContext(int(parent["trace_id"], 16), int(parent["span_id"], 16), is_remote=True, trace_flags=TraceFlags(TraceFlags.SAMPLED))
            parent_ctx = trace.set_span_in_context(NonRecordingSpan(span_context))
        attrs = _attributes("AGENT", segment)
        if segment.get("session"):
            attrs["session.id"] = str(segment["session"])
        root = tracer.start_span(segment.get("name", "check"), context=parent_ctx, attributes=attrs, start_time=int(segment["start_ns"]))

        def emit(item, parent_span):
            ctx = trace.set_span_in_context(parent_span)
            span = tracer.start_span(item.get("name", "step"), context=ctx, attributes=_attributes(item.get("kind", "CHAIN"), item), start_time=int(item["start_ns"]))
            for child in item.get("children", [])[:20]:
                emit(child, span)
            span.end(end_time=int(item["end_ns"]))

        for step in segment.get("steps", [])[:40]:
            emit(step, root)
        root.end(end_time=int(segment["end_ns"]))
        ids = root.get_span_context()
        return {"trace_id": format(ids.trace_id, "032x"), "span_id": format(ids.span_id, "016x")}
    except Exception:
        return None
