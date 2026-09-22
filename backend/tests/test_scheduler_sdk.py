from datetime import datetime

from firebase_functions import scheduler_fn
from flask import Flask


def test_scheduler_accepts_fractional_seconds_with_offset() -> None:
    received_events: list[scheduler_fn.ScheduledEvent] = []

    @scheduler_fn.on_schedule(schedule="0 5 * * *")
    def scheduled_handler(event: scheduler_fn.ScheduledEvent) -> None:
        received_events.append(event)

    app = Flask(__name__)
    with app.test_request_context(
        method="POST",
        headers={
            "X-CloudScheduler-JobName": "test-job",
            "X-CloudScheduler-ScheduleTime": (
                "2026-09-20T22:00:03.337437-07:00"
            ),
        },
    ) as request_context:
        response = scheduled_handler(request_context.request)

    assert response.status_code == 200
    assert len(received_events) == 1
    assert received_events[0].job_name == "test-job"
    assert received_events[0].schedule_time == datetime.fromisoformat(
        "2026-09-20T22:00:03.337437-07:00"
    )
