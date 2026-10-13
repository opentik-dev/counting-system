"""Auditable, detector-agnostic warehouse counting primitives."""

from .counting import CrossingCounter
from .domain import CountingLine, CrossingEvent, Direction, Point, TrackObservation
from .quantity import CountSummary, summarize_counts

__all__ = [
    "CountSummary",
    "CountingLine",
    "CrossingEvent",
    "CrossingCounter",
    "Direction",
    "Point",
    "TrackObservation",
    "summarize_counts",
]
