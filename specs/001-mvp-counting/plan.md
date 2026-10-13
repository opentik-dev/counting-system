# Implementation Plan: MVP counting engine

**Branch**: `001-mvp-counting` | **Date**: 2026-08-28 | **Spec**: `spec.md`

## Summary

Implement a dependency-free Python core with three boundaries: geometry/counting, quantity rules, and SQLite persistence. A later vision adapter will translate YOLO/tracker output into `TrackObservation`; it will not enter the core in this slice.

## Technical context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Python standard library; pytest for development tests  
**Storage**: SQLite via `sqlite3`  
**Testing**: pytest  
**Target Platform**: Linux edge PC or developer workstation  
**Project Type**: Small library with a runnable demonstration  
**Performance Goal**: Process one observation in constant time and persist one event in a local transaction  
**Constraints**: Offline-first, no credentials in code, no hidden quantity inference  
**Scale/Scope**: One camera/line and carton/pallet events for the MVP

## Constitution check

- Evidence before authority: pass; event fields include evidence metadata and tests use manual synthetic inputs.
- Deterministic business logic: pass; line geometry, direction, locking, and pallet capacity are pure/tested rules.
- Small vertical slice: pass; no live camera, model training, dashboard, or distributed services.
- Replaceable vision boundary: pass; only `TrackObservation` crosses into the core.
- Tests are the contract: pass; acceptance scenarios map to tests before implementation completion.

## Architecture

```text
detector/tracker (future adapter)
          |
          v
TrackObservation -> CrossingCounter -> CrossingEvent -> EventStore(SQLite)
                                      |
                                      v
                               CountSummary/ledger
```

## Repository structure

```text
src/warehouse_counting/
  domain.py          # observations, line geometry, events
  counting.py        # deterministic crossing state machine
  quantity.py        # explicit pallet capacity rules
  event_store.py     # SQLite persistence and totals
  demo.py            # offline runnable demonstration
tests/
  test_counting.py
  test_event_store.py
specs/001-mvp-counting/
  spec.md, plan.md, tasks.md
skills/warehouse-vision-sdd/
```

## Data decisions

- An event is immutable once emitted; corrections are a later, explicit adjustment feature.
- Direction is derived from side transition relative to `warehouse_side`, not from camera brand or image coordinates.
- Event identity is UUID-based for storage; `track_id` is the upstream identity used for deduplication.
- A pallet count is a pallet fact. Carton-equivalent quantity is only calculated when a capacity integer is provided.

## Implementation order

1. Define domain records and line-side geometry.
2. Implement and test the crossing state machine.
3. Implement explicit quantity summaries.
4. Persist/query events in SQLite.
5. Add an offline demo and verify the quickstart.
6. Document the next agent handoff; only then plan the vision adapter.

## Follow-up design gates

Before adding YOLO/CVAT/RTSP, collect a real 5–10 minute video, annotate a small representative set, define the manual ground truth protocol, and set an acceptance error threshold. Do not add a dashboard before the core count is validated against that ground truth.
