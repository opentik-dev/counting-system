# Warehouse Vision Counting System

**Languages:** [العربية](../README.md) · [English](README.en.md) · [Français](README.fr.md) · [Español](README.es.md) · [Türkçe](README.tr.md) · [中文](README.zh-CN.md)

[![CI](https://github.com/opentik-dev/counting-system/actions/workflows/ci.yml/badge.svg)](https://github.com/opentik-dev/counting-system/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE) [![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](../pyproject.toml)

An offline-first, auditable core for counting cartons and pallets crossing a
warehouse line. The current MVP is deliberately detector-agnostic: it turns
`TrackObservation` inputs into directional `IN/OUT` events, prevents duplicate
counts, and stores evidence metadata in SQLite.

## Quick start

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

The core has no runtime dependency beyond Python 3.11+. CPU training tools are
optional and documented in [`requirements-cpu.txt`](../requirements-cpu.txt).

## Current scope

- One configured counting line and two directions.
- `carton` and `pallet` events.
- Confidence/class filtering and one-event-per-track locking.
- SQLite persistence with auditable evidence references.
- Explicit pallet-capacity rules; no hidden quantity inference.

Vision adapters, live RTSP/ONVIF input, dashboards, ERP integration, and
production accuracy validation are roadmap items. The current training videos
are supplemental material, not an acceptance benchmark.

## Architecture and roadmap

See [`architecture.md`](architecture.md), [`evaluation.md`](evaluation.md), and
[`ROADMAP.md`](../ROADMAP.md).

## Join the community

Contributions are welcome from developers, researchers, warehouse practitioners,
and translators. Help us improve the counting engine, annotation tools, tests,
documentation, and real-world evaluation data.

Please read [`CONTRIBUTING.md`](../CONTRIBUTING.md), open an Issue for ideas or
bugs, and submit focused, tested Pull Requests. The most valuable next step is
building a fixed-view acceptance video and a manually reviewed ground-truth set.

## License

MIT — see [`LICENSE`](../LICENSE).
