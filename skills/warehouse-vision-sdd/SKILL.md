---
name: warehouse-vision-sdd
description: Guide implementation of auditable warehouse vision counting systems using small Spec-Kit slices, deterministic crossing logic, evidence, and explicit pallet rules.
metadata:
  short-description: Warehouse counting project workflow
---

# Warehouse Vision SDD

Use this skill when working on this warehouse counting repository or a similar warehouse camera-counting feature.

## Operating rules

- Read `.specify/memory/constitution.md`, the active `spec.md`, `plan.md`, and `tasks.md` before changing code.
- Keep the first slice offline and small: detector/tracker observations → line crossing → immutable event → SQLite.
- Keep the vision boundary replaceable. YOLO, OpenCV, RTSP, ONVIF, CVAT, and camera vendors belong in adapters, not deterministic counting rules.
- Never convert hidden pallet contents to cartons without an explicit, validated capacity rule. Mark unknown totals incomplete.
- For each behavior change, add tests for the normal path, direction, duplicate prevention, invalid/uncertain input, and the relevant edge case.
- Do not claim production or accounting accuracy until a manually verified real-video ground truth set and error report exist.

## Handoff protocol

At the end of a session, update `specs/001-mvp-counting/tasks.md` and the handoff paragraph in `README.md` with:

1. completed task IDs and files changed;
2. exact validation command and result;
3. unresolved failures, assumptions, or blockers;
4. one precise next action.

If the next action would expand scope (live cameras, model training, dashboard, ERP, or infrastructure), return the decision to the base Codex agent for review before implementing it.

## Spec-Kit sequence

Use the repository's `.specify/commands/` prompts in this order: specify/clarify → plan → tasks → implement → analyze/converge. Keep requirements and task IDs stable so another agent can resume without rewriting documents.
