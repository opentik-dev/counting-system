# Warehouse Vision Counting System Constitution

## Core Principles

### I. Evidence before authority
The system is advisory until measured against manually verified video. Every counted quantity must point to an event, timestamp, camera, confidence, and optional image/video evidence.

### II. Deterministic business logic
Detection and tracking may be probabilistic; crossing, direction, deduplication, quantity rules, and totals must be explicit, deterministic, and independently testable. Hidden cartons are never inferred without an explicit capacity rule.

### III. Small vertical slices
Prefer one camera, one route, and one demonstrable workflow before adding dashboards, multiple cameras, ERP integration, or distributed infrastructure. Each slice must run locally and be reversible.

### IV. Replaceable vision boundary
Camera vendors, detectors, and trackers are adapters. Core counting and inventory code must not depend on Hikvision, Dahua, YOLO, or a specific model name.

### V. Tests are the contract
New counting or quantity behavior requires tests for the normal path, duplicate prevention, direction, invalid input, and uncertainty. A feature is not complete until its documented acceptance scenarios pass.

## Scope and safety constraints

- MVP uses Python, SQLite, and local files; no microservices, cloud, or ERP dependency.
- Do not store camera credentials in source control or test fixtures.
- Do not claim accounting-grade accuracy until a labeled, manually verified test set and error report exist.
- Keep documentation compact: constitution, feature spec, plan, tasks, and this repository README are the canonical project record.

## Development workflow

Use the Spec-Kit sequence: specify → clarify when needed → plan → tasks → implement → analyze/converge. Keep IDs stable (`FR`, `SC`, `T`) so agents can resume work without rewriting history. At the end of each work session, update `specs/001-mvp-counting/tasks.md` and the “handoff” section of `README.md` with completed work, evidence, blockers, and the exact next command.

## Governance

This constitution governs implementation decisions for the project. Any exception must be recorded in the feature plan with a reason, risk, and simpler alternative considered. The base Codex agent reviews unresolved failures and architectural changes before expansion of scope.

**Version**: 1.0.0 | **Ratified**: 2026-08-28 | **Last Amended**: 2026-08-28
