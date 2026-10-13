# Feature Specification: MVP counting engine

**Feature Branch**: `001-mvp-counting`  
**Created**: 2026-08-28  
**Status**: MVP implemented; field-validation gate pending  
**Input**: Warehouse proposal supplied by the user

## Goal and scope

Build a local, auditable counting core for one warehouse doorway. It accepts tracked observations from any detector/tracker, emits at most one crossing event per physical track, derives `IN`/`OUT`, and persists events in SQLite. It does not train a model, connect to a live camera, or replace an ERP in this feature.

## User scenarios & testing

### User Story 1 — Count a crossing (Priority: P1)

As a warehouse operator, I need each carton or pallet that crosses a configured line to create one directional event so that receiving and dispatch counts are measurable.

**Independent Test**: Feed synthetic observations for a carton moving across the line and inspect the emitted event.

**Acceptance Scenarios**

1. **Given** a carton starts on the truck side and moves to the warehouse side, **when** it crosses the line, **then** exactly one `CARTON_IN` event is emitted.
2. **Given** a carton starts on the warehouse side and moves to the truck side, **when** it crosses the line, **then** exactly one `CARTON_OUT` event is emitted.
3. **Given** the same track remains visible for many frames after crossing, **when** observations continue, **then** no duplicate event is emitted.

### User Story 2 — Audit and total events (Priority: P1)

As a supervisor, I need persisted events with evidence metadata and daily totals so that an AI count can be reviewed and reconciled.

**Independent Test**: Save events to a temporary SQLite database and query totals by direction and object type.

**Acceptance Scenarios**

1. **Given** an event contains camera, timestamp, track, confidence, and evidence reference, **when** it is stored, **then** those fields can be read back unchanged.
2. **Given** three carton-in and one pallet-out events, **when** totals are requested, **then** the result separates carton/pallet and `IN`/`OUT` counts.

### User Story 3 — Handle pallet quantity honestly (Priority: P2)

As an inventory reviewer, I need the system to distinguish visible counts from rule-based pallet quantities so that concealed cartons are not presented as computer vision facts.

**Independent Test**: Calculate a summary with and without an explicit cartons-per-pallet capacity.

**Acceptance Scenarios**

1. **Given** two pallets and capacity `30`, **when** a summary is calculated, **then** pallet cartons equal `60` and total cartons include them.
2. **Given** two pallets and no capacity, **when** a summary is calculated, **then** total cartons is unknown and the summary is marked incomplete.

## Functional requirements

- **FR-001**: The engine MUST accept observations with track ID, object type, center point, timestamp, and confidence.
- **FR-002**: The engine MUST support a configurable directed counting line and map crossings to `IN` or `OUT`.
- **FR-003**: The engine MUST count only configured object types (`carton`, `pallet` in the MVP).
- **FR-004**: The engine MUST ignore observations below the configured confidence threshold.
- **FR-005**: The engine MUST emit no more than one event for a track until that track is explicitly reset.
- **FR-006**: Each event MUST include a unique ID, camera ID, track ID, object type, direction, timestamp, confidence, and optional evidence reference.
- **FR-007**: SQLite storage MUST preserve events and expose totals filtered by time range.
- **FR-008**: Pallet-derived carton quantity MUST require an explicit capacity rule; otherwise it MUST remain unknown.
- **FR-009**: The core MUST be usable without OpenCV, YOLO, a camera, or a network connection.

## Key entities

- **TrackObservation**: One tracker observation at a timestamp.
- **CountingLine**: Two points plus the configured warehouse-side orientation.
- **CrossingEvent**: Immutable auditable result of a track crossing.
- **CountSummary**: Visible carton/pallet counts plus optional rule-derived quantity.
- **EventStore**: SQLite persistence boundary.

## Edge cases

- Unknown object classes and low-confidence observations are ignored.
- A point exactly on the line does not count until a subsequent observation clearly changes side.
- A track ID reused by an upstream tracker must be explicitly reset by the caller.
- A missing pallet capacity produces an incomplete summary, never a guessed carton total.
- Timestamps are stored as ISO-8601 strings and interpreted consistently as UTC when created by the library.

## Success criteria

- **SC-001**: All acceptance scenarios pass offline with deterministic tests.
- **SC-002**: Replaying the same observation stream produces the same event IDs/counts except for intentionally generated event UUIDs.
- **SC-003**: Duplicate observations after a crossing do not change totals.
- **SC-004**: Every stored event is explainable from its input fields and evidence reference.
- **SC-005**: A new detector/tracker can feed the core through observations without changing counting or storage code.

## Assumptions and exclusions

- The first route is one doorway and one line; zones, multi-camera correlation, and truck identity are later features.
- Ground truth is supplied manually for evaluation; no claim is made about model accuracy yet.
- Live RTSP/ONVIF, CVAT export, YOLO fine-tuning, FastAPI, and dashboard work are follow-up features after this core passes.
