"""Run a tiny offline demonstration: one carton IN and one pallet OUT."""

from datetime import datetime, timezone

from .counting import CrossingCounter
from .domain import CountingLine, Point, TrackObservation
from .event_store import EventStore


def main() -> None:
    line = CountingLine(Point(0, 0), Point(10, 0), warehouse_side=1)
    counter = CrossingCounter(line, camera_id="Dock-01")
    timestamp = datetime(2026, 8, 28, 10, 32, tzinfo=timezone.utc)
    observations = [
        TrackObservation(1, "carton", Point(5, -2), timestamp, 0.98),
        TrackObservation(1, "carton", Point(5, 2), timestamp, 0.98),
        TrackObservation(2, "pallet", Point(5, 2), timestamp, 0.94),
        TrackObservation(2, "pallet", Point(5, -2), timestamp, 0.94),
    ]
    store = EventStore(":memory:")
    for observation in observations:
        event = counter.process(observation, evidence_ref="demo/frame-001.jpg")
        if event:
            store.save(event)
            print(
                f"{event.object_type.upper()}_{event.direction} "
                f"track={event.track_id} evidence={event.evidence_ref}"
            )
    print(store.totals())
    store.close()


if __name__ == "__main__":
    main()
