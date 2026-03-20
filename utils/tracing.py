from datetime import datetime, timezone
import time
import uuid


def create_trace_id() -> str:
    return f"trace-{uuid.uuid4().hex[:12]}"


def elapsed_ms_since(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def build_stream_event(event_type: str, payload: dict, trace_id: str, elapsed_ms: int) -> dict:
    return {
        "type": event_type,
        "trace_id": trace_id,
        "elapsed_ms": elapsed_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
