"""Small SSE bridge that keeps work alive when a browser disconnects."""
import asyncio
import json
from typing import Any

from fastapi.responses import StreamingResponse

_TASKS: set[asyncio.Task] = set()


def frame(event: str, data: dict[str, Any], thread_id: str) -> str:
    return f"event: {event}\ndata: {json.dumps({**data, 'thread_id': thread_id}, ensure_ascii=False, default=str)}\n\n"


def stream_work(thread_id: str, work, on_error=None) -> StreamingResponse:
    """Execute blocking work in a retained task; stream queue messages and heartbeats."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=256)
    loop = asyncio.get_running_loop()
    disconnected = False

    def enqueue(item):
        if disconnected:
            return
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(item)

    def schedule(item):
        try:
            loop.call_soon_threadsafe(enqueue, item)
        except RuntimeError:
            # An HTTP client or server loop may close while the worker persists its result.
            pass

    def emit(event: str, data: dict | None = None):
        schedule((event, data or {}))

    async def run():
        try:
            await asyncio.to_thread(work, emit)
        except Exception as exc:
            if on_error:
                try:
                    await asyncio.to_thread(on_error, exc)
                except Exception:
                    pass
            emit("error", {"message": "This operation could not complete. Please retry.", "recoverable": False})
            emit("done", {"status": "error"})
        finally:
            schedule(None)

    task = asyncio.create_task(run())
    _TASKS.add(task)
    task.add_done_callback(_TASKS.discard)

    async def events():
        nonlocal disconnected
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
                    continue
                if item is None:
                    break
                yield frame(item[0], item[1], thread_id)
        finally:
            disconnected = True
            while not queue.empty():
                queue.get_nowait()

    return StreamingResponse(events(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no",
    })
