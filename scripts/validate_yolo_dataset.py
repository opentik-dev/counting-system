#!/usr/bin/env python3
"""Audit YOLO image labels without changing the dataset."""

from __future__ import annotations

import argparse
import math
from collections import Counter
from pathlib import Path


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def audit(images_dir: Path, labels_dir: Path, classes_file: Path, require_complete: bool) -> int:
    classes = [line.strip() for line in classes_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    images = {path.stem: path for path in images_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES}
    labels = {path.stem: path for path in labels_dir.glob("*.txt")}
    errors: list[str] = []
    counts: Counter[str] = Counter()
    rows = 0
    empty: list[str] = []

    for stem, label_path in labels.items():
        lines = label_path.read_text(encoding="utf-8").splitlines()
        if not lines:
            empty.append(stem)
        for line_number, line in enumerate(lines, 1):
            fields = line.split()
            if len(fields) != 5:
                errors.append(f"{label_path.name}:{line_number}: expected 5 fields")
                continue
            try:
                class_id = int(fields[0])
                values = [float(value) for value in fields[1:]]
            except ValueError:
                errors.append(f"{label_path.name}:{line_number}: non-numeric value")
                continue
            if not 0 <= class_id < len(classes):
                errors.append(f"{label_path.name}:{line_number}: invalid class {class_id}")
            if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values):
                errors.append(f"{label_path.name}:{line_number}: values must be finite and in [0, 1]")
            if values[2] <= 0 or values[3] <= 0:
                errors.append(f"{label_path.name}:{line_number}: box width/height must be positive")
            if 0 <= class_id < len(classes):
                counts[classes[class_id]] += 1
            rows += 1

    unlabeled = sorted(set(images) - set(labels))
    orphan_labels = sorted(set(labels) - set(images))
    print(f"images={len(images)} label_files={len(labels)} annotation_rows={rows}")
    print(f"empty_label_files={len(empty)} images_without_label={len(unlabeled)} labels_without_image={len(orphan_labels)}")
    print("class_counts=" + ", ".join(f"{name}:{counts[name]}" for name in classes))
    if errors:
        print(f"structural_errors={len(errors)}")
        for error in errors[:20]:
            print(f"ERROR {error}")
        return 1
    incomplete = bool(empty or unlabeled or orphan_labels)
    if incomplete:
        print("status=INCOMPLETE (syntax valid; review missing/empty labels before training)")
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
