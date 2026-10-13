"""Deterministic crossing state machine."""

from __future__ import annotations

from dataclasses import dataclass

from .domain import CountingLine, CrossingEvent, Point, TrackObservation


@dataclass
class _TrackState:
    last_point: Point
    counted: bool = False


class CrossingCounter:
    """Turn tracker observations into one auditable event per track."""

    def __init__(
        self,
        line: CountingLine,
        *,
        camera_id: str,
        allowed_types: frozenset[str] = frozenset({"carton", "pallet"}),
        min_confidence: float = 0.50,
    ) -> None:
        if not camera_id:
            raise ValueError("camera_id must not be empty")
        if not 0 <= min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1")
        self.line = line
        self.camera_id = camera_id
        self.allowed_types = allowed_types
        self.min_confidence = min_confidence
        self._tracks: dict[int, _TrackState] = {}

    def process(
        self, observation: TrackObservation, *, evidence_ref: str | None = None
    ) -> CrossingEvent | None:
        if observation.object_type not in self.allowed_types:
            return None
        if observation.confidence < self.min_confidence:
            return None

        state = self._tracks.get(observation.track_id)
        if state is None:
            self._tracks[observation.track_id] = _TrackState(observation.center)
            return None

        direction = self.line.direction(state.last_point, observation.center)
        state.last_point = observation.center
        if direction is None or state.counted:
            return None

        state.counted = True
        return CrossingEvent.create(
            camera_id=self.camera_id,
            observation=observation,
            direction=direction,
            evidence_ref=evidence_ref,
        )

    def reset(self, track_id: int) -> None:
        """Forget one track when an upstream tracker reuses its ID."""

        self._tracks.pop(track_id, None)

    def reset_all(self) -> None:
        self._tracks.clear()
