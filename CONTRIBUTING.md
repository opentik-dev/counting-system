# Contributing

The counting core requires Python 3.11 or newer and has no runtime dependency
outside the standard library. Install the development test dependency in your
own environment, then run:

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

CPU training dependencies are intentionally separate in
`requirements-cpu.txt`; they are not required for the core library.

Keep changes focused, add deterministic tests for behavior changes, update the
relevant specification and documentation, and do not commit videos, generated
datasets, model weights, credentials, or local environments.
