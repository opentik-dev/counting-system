from datetime import datetime, timedelta, timezone

from warehouse_counting.domain import CrossingEvent, Point, TrackObservation
from warehouse_counting.event_store import EventStore


def make_event(object_type, direction, minutes=0):
    observation = TrackObservation(
        track_id=minutes + 1,
        object_type=object_type,
        center=Point(1, 1),
        timestamp=datetime(2026, 8, 28, tzinfo=timezone.utc) + timedelta(minutes=minutes),
        confidence=0.91,
    )
    return CrossingEvent.create(
        camera_id="Dock-01",
        observation=observation,
        direction=direction,
        evidence_ref=f"evidence/{minutes}.jpg",
    )


def test_event_round_trip_and_totals(tmp_path):
    store = EventStore(tmp_path / "events.sqlite3")
    carton_in = make_event("carton", "IN", 1)
    pallet_in = make_event("pallet", "IN", 2)
    carton_out = make_event("carton", "OUT", 3)
    store.save_many([carton_in, pallet_in, carton_out])

    row = store.get(str(carton_in.event_id))
    assert row["camera_id"] == "Dock-01"
    assert row["evidence_ref"] == "evidence/1.jpg"
    assert store.totals() == {
        ("carton", "IN"): 1,
        ("carton", "OUT"): 1,
        ("pallet", "IN"): 1,
    }
    store.close()


def test_totals_can_be_time_filtered(tmp_path):
    store = EventStore(tmp_path / "events.sqlite3")
    store.save_many([make_event("carton", "IN", 1), make_event("carton", "IN", 5)])
    start = datetime(2026, 8, 28, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=3)
    assert store.totals(start=start, end=end) == {("carton", "IN"): 1}
    store.close()
