#!/usr/bin/env python3
"""Extract evenly spaced review frames and a reproducible source manifest."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import cv2


def safe_slug(value: str) -> str:
    value = re.sub(r"[^\w.-]+", "_", value, flags=re.UNICODE).strip("_.")
    return value or "video"


def extract(video: Path, output: Path, interval: float) -> list[dict[str, str | int | float]]:
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise RuntimeError(f"cannot open video: {video}")
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    prefix = safe_slug(video.stem)
    rows: list[dict[str, str | int | float]] = []
    next_timestamp = 0.0
    frame_index = 0
    sample_index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        timestamp = frame_index / fps
        if timestamp + (0.5 / fps) >= next_timestamp:
            filename = f"{prefix}__t{timestamp:08.2f}s.jpg"
            destination = output / filename
            if not cv2.imwrite(str(destination), frame, [cv2.IMWRITE_JPEG_QUALITY, 92]):
                raise RuntimeError(f"cannot write frame: {destination}")
            rows.append(
                {
                    "source_video": str(video),
                    "source_frame": frame_index,
                    "timestamp_seconds": round(timestamp, 3),
                    "image": str(destination),
                    "width": width,
                    "height": height,
                }
            )
            sample_index += 1
            next_timestamp = sample_index * interval
        frame_index += 1
    capture.release()
    if not rows:
        raise RuntimeError(f"video contains no readable frames: {video}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("videos", nargs="+", type=Path, help="input video files")
    parser.add_argument("--output", type=Path, required=True, help="frame directory")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between frames")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")

    args.output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str | int | float]] = []
    for video in args.videos:
        rows.extend(extract(video, args.output, args.interval))

    manifest = args.output / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"extracted={len(rows)} manifest={manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
