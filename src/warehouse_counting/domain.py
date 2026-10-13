"""Domain records shared by detector adapters and the counting core."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

Direction = Literal["IN", "OUT"]
ObjectType = Literal["carton", "pallet"]


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class TrackObservation:
    track_id: int
    object_type: str
    center: Point
    timestamp: datetime
    confidence: float


@dataclass(frozen=True)
class CountingLine:
    """A directed line; `warehouse_side` is the signed side meaning IN."""

    start: Point
    end: Point
    warehouse_side: Literal[-1, 1] = 1

    def signed_side(self, point: Point) -> float:
        return ((self.end.x - self.start.x) * (point.y - self.start.y)) - (
            (self.end.y - self.start.y) * (point.x - self.start.x)
        )

    def side(self, point: Point) -> int:
        value = self.signed_side(point)
        return 1 if value > 0 else -1 if value < 0 else 0

    def direction(self, previous: Point, current: Point) -> Direction | None:
        previous_side = self.side(previous)
        current_side = self.side(current)
        if previous_side == 0 or current_side == 0 or previous_side == current_side:
            return None
        return "IN" if current_side == self.warehouse_side else "OUT"


@dataclass(frozen=True)
class CrossingEvent:
    event_id: UUID
    camera_id: str
    track_id: int
    object_type: str
    direction: Direction
    timestamp: datetime
    confidence: float
    evidence_ref: str | None = None

    @classmethod
    def create(
        cls,
        *,
        camera_id: str,
        observation: TrackObservation,
        direction: Direction,
        evidence_ref: str | None = None,
    ) -> "CrossingEvent":
        return cls(
            event_id=uuid4(),
            camera_id=camera_id,
            track_id=observation.track_id,
            object_type=observation.object_type,
            direction=direction,
            timestamp=observation.timestamp,
            confidence=observation.confidence,
            evidence_ref=evidence_ref,
        )
