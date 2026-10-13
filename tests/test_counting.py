from datetime import datetime, timezone

import pytest

from warehouse_counting.counting import CrossingCounter
from warehouse_counting.domain import CountingLine, Point, TrackObservation
from warehouse_counting.quantity import summarize_counts


STAMP = datetime(2026, 8, 28, tzinfo=timezone.utc)
LINE = CountingLine(Point(0, 0), Point(10, 0), warehouse_side=1)


def observation(track_id, object_type, y, confidence=0.9):
    return TrackObservation(track_id, object_type, Point(5, y), STAMP, confidence)


def test_crossing_from_truck_to_warehouse_is_in():
    counter = CrossingCounter(LINE, camera_id="Dock-01")
    assert counter.process(observation(7, "carton", -1)) is None
    event = counter.process(observation(7, "carton", 1), evidence_ref="f.jpg")
    assert event is not None
    assert (event.object_type, event.direction, event.evidence_ref) == (
        "carton",
        "IN",
        "f.jpg",
    )


def test_crossing_from_warehouse_to_truck_is_out_and_not_duplicated():
    counter = CrossingCounter(LINE, camera_id="Dock-01")
    counter.process(observation(8, "pallet", 1))
    event = counter.process(observation(8, "pallet", -1))
    assert event is not None and event.direction == "OUT"
    assert counter.process(observation(8, "pallet", 1)) is None
    assert counter.process(observation(8, "pallet", -1)) is None


def test_unknown_class_and_low_confidence_are_ignored():
    counter = CrossingCounter(LINE, camera_id="Dock-01", min_confidence=0.8)
    assert counter.process(observation(1, "person", -1, 0.99)) is None
    assert counter.process(observation(2, "carton", -1, 0.79)) is None
    assert counter.process(observation(2, "carton", 1, 0.99)) is None


def test_track_id_can_be_reset_when_upstream_reuses_it():
    counter = CrossingCounter(LINE, camera_id="Dock-01")
    counter.process(observation(3, "carton", -1))
    assert counter.process(observation(3, "carton", 1)) is not None
    counter.reset(3)
    counter.process(observation(3, "carton", 1))
    assert counter.process(observation(3, "carton", -1)).direction == "OUT"


def test_pallet_quantity_requires_explicit_capacity():
    known = summarize_counts(loose_cartons=4, pallets=2, cartons_per_pallet=30)
    assert known.pallet_cartons == 60
    assert known.total_cartons == 64 and known.complete

    unknown = summarize_counts(loose_cartons=4, pallets=2)
    assert unknown.pallet_cartons is None
    assert unknown.total_cartons is None and not unknown.complete


@pytest.mark.parametrize("kwargs", [{"loose_cartons": -1, "pallets": 0}, {"loose_cartons": 0, "pallets": -1}])
def test_negative_counts_are_rejected(kwargs):
    with pytest.raises(ValueError):
        summarize_counts(**kwargs)
