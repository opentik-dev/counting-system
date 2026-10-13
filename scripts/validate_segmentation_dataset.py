#!/usr/bin/env python3
"""Validate YOLO-Segmentation polygon labels and image/label pairing."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def audit(images_dir: Path, labels_dir: Path, classes_file: Path, require_complete: bool) -> int:
    classes = [line.strip() for line in classes_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    images = {path.stem for path in images_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES}
    labels = {path.stem: path for path in labels_dir.glob("*.txt")}
    errors, rows, empty = [], 0, 0
    for stem, path in labels.items():
        lines = path.read_text(encoding="utf-8").splitlines()
        empty += not lines
        for line_number, line in enumerate(lines, 1):
            fields = line.split()
            if len(fields) < 7 or (len(fields) - 1) % 2:
                errors.append(f"{path.name}:{line_number}: expected class plus polygon points")
                continue
            try:
                label = int(fields[0])
                values = [float(value) for value in fields[1:]]
            except ValueError:
                errors.append(f"{path.name}:{line_number}: non-numeric value")
                continue
            if not 0 <= label < len(classes) or any(not math.isfinite(v) or not 0 <= v <= 1 for v in values):
                errors.append(f"{path.name}:{line_number}: invalid class or coordinate")
            rows += 1
    missing, orphan = sorted(images - set(labels)), sorted(set(labels) - images)
    print(f"images={len(images)} label_files={len(labels)} polygon_rows={rows}")
    print(f"empty_label_files={empty} images_without_label={len(missing)} labels_without_image={len(orphan)}")
    if errors:
        print(f"structural_errors={len(errors)}")
        for error in errors[:20]:
            print(f"ERROR {error}")
        return 1
    incomplete = bool(empty or missing or orphan)
    if incomplete:
        print("status=INCOMPLETE")
        return 2 if require_complete else 0
    print("status=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--classes", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    return audit(args.images, args.labels, args.classes, args.require_complete)


if __name__ == "__main__":
    raise SystemExit(main())
