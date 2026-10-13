#!/usr/bin/env python3
"""Collect annotated images into YOLO-Segmentation, COCO, and manifest outputs."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def polygon_area(points: list[tuple[float, float]]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])) / 2)


def read_shapes(path: Path, class_count: int) -> list[tuple[int, list[tuple[float, float]]]]:
    shapes = []
    if not path.exists():
        return shapes
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if len(fields) == 5:
            label, cx, cy, box_w, box_h = map(float, fields)
            points = [(clamp(cx - box_w / 2), clamp(cy - box_h / 2)), (clamp(cx + box_w / 2), clamp(cy - box_h / 2)), (clamp(cx + box_w / 2), clamp(cy + box_h / 2)), (clamp(cx - box_w / 2), clamp(cy + box_h / 2))]
        elif len(fields) >= 7 and (len(fields) - 1) % 2 == 0:
            label = int(fields[0])
            values = [float(value) for value in fields[1:]]
            points = list(zip(values[::2], values[1::2]))
        else:
            raise ValueError(f"{path.name}:{line_number}: expected YOLO box or polygon")
        if not isinstance(label, int):
            if int(label) != label:
                raise ValueError(f"{path.name}:{line_number}: invalid class")
            label = int(label)
        if not 0 <= label < class_count or len(points) < 3 or any(not 0 <= value <= 1 for point in points for value in point):
            raise ValueError(f"{path.name}:{line_number}: invalid class or polygon coordinates")
        shapes.append((label, points))
    return shapes


def build(images_dir: Path, labels_dir: Path, classes_file: Path, output: Path, include_empty: bool) -> tuple[int, int]:
    classes = [line.strip() for line in classes_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    images = sorted(path for path in images_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)
    if len({path.stem for path in images}) != len(images):
        raise ValueError("image stems must be unique")
    (output / "images").mkdir(parents=True, exist_ok=True)
    (output / "labels").mkdir(parents=True, exist_ok=True)
    coco = {"images": [], "annotations": [], "categories": [{"id": i + 1, "name": name} for i, name in enumerate(classes)]}
    manifest = []
    annotation_id = 1
    image_id = 1
    for image in images:
        label_path = labels_dir / f"{image.stem}.txt"
        shapes = read_shapes(label_path, len(classes))
        if not include_empty and not shapes:
            continue
        with Image.open(image) as opened:
            width, height = opened.size
        shutil.copy2(image, output / "images" / image.name)
        (output / "labels" / f"{image.stem}.txt").write_text(
            "\n".join(" ".join([str(label), *(f"{x:.6f} {y:.6f}" for x, y in points)]) for label, points in shapes) + ("\n" if shapes else ""),
            encoding="utf-8",
        )
        coco["images"].append({"id": image_id, "file_name": image.name, "width": width, "height": height})
        for label, points in shapes:
            pixel_points = [(x * width, y * height) for x, y in points]
            xs, ys = zip(*pixel_points)
            coco["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": label + 1,
                "segmentation": [[value for point in pixel_points for value in point]],
                "area": polygon_area(pixel_points),
                "bbox": [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)],
                "iscrowd": 0,
            })
            annotation_id += 1
        manifest.append({"image": image.name, "source_image": str(image), "label": f"labels/{image.stem}.txt", "width": width, "height": height, "annotations": len(shapes)})
        image_id += 1
    (output / "annotations.json").write_text(json.dumps(coco, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image", "source_image", "label", "width", "height", "annotations"])
        writer.writeheader()
        writer.writerows(manifest)
    (output / "data.yaml").write_text(f"path: {output.as_posix()}\ntrain: images\nval: images\nnc: {len(classes)}\nnames: {classes!r}\n", encoding="utf-8")
    return len(manifest), len(coco["annotations"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", type=Path)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--classes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exclude-empty", action="store_true")
    args = parser.parse_args()
    images, annotations = build(args.images, args.labels, args.classes, args.output, not args.exclude_empty)
    print(f"images={images} annotations={annotations} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
