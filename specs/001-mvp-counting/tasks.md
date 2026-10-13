# Tasks: MVP counting engine

**Input**: `spec.md` and `plan.md`  
**Status**: MVP core and tooling implemented; T017 field-validation gate pending

## Phase 1 — Setup

- [x] T001 Initialize Spec-Kit 0.9.3 in the repository with a writable generic command directory.
- [x] T002 [FR-009] Create the minimal Python package, test layout, and project configuration.

## Phase 2 — Foundational core

- [x] T003 [FR-001, FR-006] Define `TrackObservation`, `CountingLine`, `CrossingEvent`, and direction types in `src/warehouse_counting/domain.py`.
- [x] T004 [FR-002] Implement signed-side line geometry and explicit warehouse-side direction mapping.
- [x] T005 [FR-003, FR-004, FR-005] Add confidence/class filtering and one-event-per-track locking in `src/warehouse_counting/counting.py`.
- [x] T006 [FR-008] Add explicit pallet-capacity calculation in `src/warehouse_counting/quantity.py`.
- [x] T007 [FR-006, FR-007] Implement SQLite schema, event persistence, and filtered totals in `src/warehouse_counting/event_store.py`.

## Phase 3 — User Story 1: crossing count (P1)

- [x] T008 [US1, FR-002, FR-003, FR-004, FR-005] Test `IN`, `OUT`, duplicate prevention, line-edge behavior, class filtering, and confidence filtering in `tests/test_counting.py`.
- [x] T009 [US1, FR-002, FR-006] Provide an offline demonstration in `src/warehouse_counting/demo.py`.

## Phase 4 — User Story 2: audit and totals (P1)

- [x] T010 [US2, FR-006, FR-007] Test round-trip event metadata and directional/object totals in `tests/test_event_store.py`.
- [x] T011 [US2, FR-006, FR-007] Document the evidence contract and local execution in the repository README.

## Phase 5 — User Story 3: pallet honesty (P2)

- [x] T012 [US3, FR-008] Test known and unknown pallet capacity behavior in `tests/test_counting.py`.
- [x] T013 [US3, FR-008] Keep incomplete summaries explicit; never convert unknown pallet contents into a guessed total.

## Phase 6 — Handoff and quality gate

- [x] T014 Create the reusable `warehouse-vision-sdd` project skill and validate its structure.
- [x] T015 Run the full test suite and quickstart; record results in README handoff.
- [x] T016 Run the Spec-Kit-aligned read-only consistency analysis after implementation; no artifact mismatch found.
- [ ] T017 Gather a fixed-view warehouse video and define the labeled ground-truth protocol before vision integration. The current 8-clip corpus decodes successfully and is useful for training diversity, but all sampled clips are supplemental data; no clip is accepted as the final line-crossing accuracy benchmark.
- [x] T018 Create `scripts/extract_frames.py` and extract one review frame per second from the supplemental corpus with a reproducible `manifest.csv` (`219` images verified).
- [x] T019 Review and label the extracted frames using `config/annotation-classes.txt`; keep source clips separated from the eventual warehouse acceptance set. All previously missing carton frames are now labeled; the two reviewed CapCut outro frames were moved to `datasets/seed/excluded/capcut_outro` and excluded from training.
- [x] T020 Add a lightweight local GUI annotator that writes separate YOLO label files without modifying source images.
- [x] T021 Add a dependency-free YOLO dataset validator and audit the current labels.
- [x] T022 Add reproducible CPU training requirements and a bounded YOLO training wrapper; run a one-epoch pipeline smoke test without treating its `mAP=0` as a quality result.
- [x] T023 Train a five-epoch pretrained YOLO11n baseline and evaluate validation/test metrics; retain it as a comparison baseline only, not a production model.
- [x] T024 Add the warehouse annotation workbench with box, ellipse, polygon, and freehand modes; preserve old box labels and keep source images unchanged.
- [x] T025 Add YOLO-Segmentation/COCO/manifest dataset aggregation and an independent segmentation-label validator.
- [x] T026 Expand configurable warehouse classes and convert the current reviewed set to `datasets/warehouse_seg_v1`; validator result `PASS` for `217` images and `1458` polygons.
- [x] T027 Add in-app import of folders and selected images, reusable reference workspace creation, project opening, collision-safe filenames, and preserve CLI compatibility.

## Dependencies

`T003–T007` block the user stories. `T008–T013` are the current MVP. `T015–T016` are release gates. `T017` is the only prerequisite for the next vision feature; no model or camera code should be added before it.

## Coverage index

`FR-001/FR-006`: T003; `FR-002`: T004, T008; `FR-003/FR-004/FR-005`: T005, T008; `FR-007`: T007, T010; `FR-008`: T006, T012, T013; `FR-009`: T002. `SC-001/SC-003`: T008, T010, T012, T015; `SC-002/SC-004/SC-005`: T008, T010, T011.
