from utils.tracing import build_stream_event


def test_build_stream_event_includes_trace_fields():
    event = build_stream_event(
        "token",
        {"content": "hello", "stage": "planning"},
        trace_id="trace-1",
        elapsed_ms=25,
    )

    assert event["type"] == "token"
    assert event["content"] == "hello"
    assert event["stage"] == "planning"
    assert event["trace_id"] == "trace-1"
    assert event["elapsed_ms"] == 25
    assert "timestamp" in event
