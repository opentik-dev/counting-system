#!/usr/bin/env python3
"""Build a reproducible, source-separated YOLO dataset from reviewed frames."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


SPLIT_BY_SOURCE = {
    "tests/Video by petercargoglobal [DVXCTWCkdsZ].mp4": "val",
    "tests/Video by petercargoglobal [DaOZksso2Yu].mp4": "test",
}
CLASSES = ("carton", "pallet", "forklift", "person", "truck")


def build(seed: Path, output: Path) -> tuple[int, dict[str, int]]:
    manifest_path = seed / "manifest.csv"
    rows = list(csv.DictReader(manifest_path.open(encoding="utf-8", newline="")))
    output.mkdir(parents=True, exist_ok=True)
    split_rows: list[dict[str, str]] = []
    counts = {"train": 0, "val": 0, "test": 0}

    for row in rows:
        source = row["source_video"]
        split = SPLIT_BY_SOURCE.get(source, "train")
        image = Path(row["image"])
        label = seed / "labels" / f"{image.stem}.txt"
        if not image.is_file() or not label.is_file():
            raise FileNotFoundError(f"missing pair for {image}")
        destination_images = output / split / "images"
        destination_labels = output / split / "labels"
        destination_images.mkdir(parents=True, exist_ok=True)
        destination_labels.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, destination_images / image.name)
        shutil.copy2(label, destination_labels / label.name)
        split_rows.append({"split": split, "source_video": source, "image": image.name})
        counts[split] += 1

    with (output / "split_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["split", "source_video", "image"])
        writer.writeheader()
        writer.writerows(split_rows)
    (output / "data.yaml").write_text(
        "path: datasets/yolo_v1\n"
        "train: train/images\n"
        "val: val/images\n"
        "test: test/images\n"
        f"nc: {len(CLASSES)}\n"
        f"names: {list(CLASSES)!r}\n",
        encoding="utf-8",
    )
    return len(split_rows), counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=Path("datasets/seed"))
    parser.add_argument("--output", type=Path, default=Path("datasets/yolo_v1"))
    args = parser.parse_args()
    total, counts = build(args.seed, args.output)
    print(f"images={total} train={counts['train']} val={counts['val']} test={counts['test']}")
    print(f"data_yaml={args.output / 'data.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
