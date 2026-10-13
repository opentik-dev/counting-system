#!/usr/bin/env python3
"""Run a deliberately small YOLO baseline; production claims require real ground truth."""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("datasets/yolo_v1/data.yaml"))
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--name", default="baseline_cpu")
    args = parser.parse_args()
    if args.epochs < 1 or args.imgsz < 32 or args.batch < 1:
        parser.error("epochs, imgsz, and batch must be positive")
    model = YOLO(args.model)
    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=0,
        project=str(Path("runs/detect").resolve()),
        name=args.name,
        exist_ok=True,
        plots=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
