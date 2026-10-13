#!/usr/bin/env python3
"""Annotate warehouse images with boxes, ellipses, polygons, or freehand shapes."""

from __future__ import annotations

import argparse
import math
import shutil
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
COLORS = ("#ffd166", "#06d6a0", "#118ab2", "#ef476f", "#a78bfa", "#f4a261", "#e76f51", "#2a9d8f")


@dataclass
class Shape:
    label: int
    kind: str
    points: list[tuple[float, float]]


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def valid_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cleaned = [(clamp(x), clamp(y)) for x, y in points]
    return cleaned if len(cleaned) >= 3 and abs(polygon_area(cleaned)) >= 0.00001 else []


def polygon_area(points: list[tuple[float, float]]) -> float:
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])) / 2


def rectangle_points(start: tuple[float, float], end: tuple[float, float]) -> list[tuple[float, float]]:
    x1, y1 = start
    x2, y2 = end
    left, right = sorted((clamp(x1), clamp(x2)))
    top, bottom = sorted((clamp(y1), clamp(y2)))
    return [(left, top), (right, top), (right, bottom), (left, bottom)]


def ellipse_points(start: tuple[float, float], end: tuple[float, float], segments: int = 32) -> list[tuple[float, float]]:
    x1, y1 = start
    x2, y2 = end
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    rx, ry = abs(x2 - x1) / 2, abs(y2 - y1) / 2
    return [(clamp(cx + rx * math.cos(2 * math.pi * i / segments)), clamp(cy + ry * math.sin(2 * math.pi * i / segments))) for i in range(segments)]


def collect_images(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def import_sources(sources: list[Path], reference_dir: Path) -> list[Path]:
    reference_dir.mkdir(parents=True, exist_ok=True)
    existing_stems = {path.stem for path in collect_images(reference_dir)}
    candidates: list[Path] = []
    for source in sources:
        if source.is_dir():
            candidates.extend(collect_images(source))
        elif source.is_file() and source.suffix.lower() in IMAGE_SUFFIXES:
            candidates.append(source)
    copied: list[Path] = []
    for source in dict.fromkeys(path.resolve() for path in candidates):
        destination = reference_dir / source.name
        if (destination.exists() or destination.stem in existing_stems) and destination.resolve() != source:
            stem, suffix, serial = source.stem, source.suffix, 2
            while destination.exists() or destination.stem in existing_stems:
                destination = reference_dir / f"{stem}_{serial}{suffix}"
                serial += 1
        if destination.resolve() != source:
            shutil.copy2(source, destination)
        copied.append(destination)
        existing_stems.add(destination.stem)
    return copied


def parse_shapes(path: Path) -> list[Shape]:
    shapes: list[Shape] = []
    if not path.exists():
        return shapes
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if len(fields) == 5:
            label, cx, cy, width, height = map(float, fields)
            points = rectangle_points((cx - width / 2, cy - height / 2), (cx + width / 2, cy + height / 2))
        elif len(fields) >= 7 and (len(fields) - 1) % 2 == 0:
            label = float(fields[0])
            values = list(map(float, fields[1:]))
            points = list(zip(values[::2], values[1::2]))
        else:
            raise ValueError(f"{path.name}:{line_number}: expected YOLO box or polygon")
        if int(label) != label or not 0 <= int(label):
            raise ValueError(f"{path.name}:{line_number}: invalid class")
        cleaned = valid_points(points)
        if not cleaned:
            raise ValueError(f"{path.name}:{line_number}: degenerate polygon")
        shapes.append(Shape(int(label), "polygon", cleaned))
    return shapes


class Annotator:
    def __init__(self, root: tk.Tk, images: list[Path], labels: list[str], workspace: Path, reference_dir: Path, output: Path) -> None:
        self.root, self.images, self.labels = root, images, labels
        self.workspace, self.reference_dir, self.output = workspace, reference_dir, output
        self.index = 0
        self.current_label = 0
        self.mode = "polygon"
        self.shapes: list[Shape] = []
        self.active_points: list[tuple[float, float]] = []
        self.drag_start: tuple[float, float] | None = None
        self.pointer: tuple[float, float] | None = None
        self.photo: ImageTk.PhotoImage | None = None
        self.image_size = (1, 1)
        self.scale = 1.0
        self.offset = (0.0, 0.0)
        root.title("Warehouse annotation workbench")
        root.geometry("1200x860")
        self.status = tk.StringVar()
        toolbar = tk.Frame(root)
        toolbar.pack(fill=tk.X, padx=8, pady=5)
        tk.Button(toolbar, text="Import folder", command=self.import_folder).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Import images", command=self.import_images).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Open project", command=self.open_project).pack(side=tk.LEFT, padx=2)
        for number, label in enumerate(labels):
            tk.Button(toolbar, text=f"{number + 1}: {label}", command=lambda n=number: self.select_label(n), bg=COLORS[number % len(COLORS)]).pack(side=tk.LEFT, padx=1)
        modes = tk.Frame(root)
        modes.pack(fill=tk.X, padx=8, pady=2)
        for key, title in (("box", "B: Box"), ("ellipse", "C: Circle/Ellipse"), ("polygon", "P: Polygon"), ("freehand", "F: Freehand")):
            tk.Button(modes, text=title, command=lambda value=key: self.select_mode(value)).pack(side=tk.LEFT, padx=2)
        tk.Button(modes, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=8)
        tk.Button(modes, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=2)
        tk.Button(modes, text="Previous", command=lambda: self.move(-1)).pack(side=tk.RIGHT, padx=2)
        tk.Button(modes, text="Save / Next", command=lambda: self.move(1)).pack(side=tk.RIGHT, padx=2)
        tk.Label(root, textvariable=self.status, anchor="w").pack(fill=tk.X, padx=8)
        self.canvas = tk.Canvas(root, bg="#202124", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.canvas.bind("<ButtonPress-1>", self.press)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<ButtonPress-3>", lambda _: self.finish_polygon())
        for number in range(min(9, len(labels))):
            root.bind(f"<Key-{number + 1}>", lambda _, n=number: self.select_label(n))
        root.bind("<Key-b>", lambda _: self.select_mode("box"))
        root.bind("<Key-c>", lambda _: self.select_mode("ellipse"))
        root.bind("<Key-p>", lambda _: self.select_mode("polygon"))
        root.bind("<Key-f>", lambda _: self.select_mode("freehand"))
        root.bind("<Return>", lambda _: self.finish_polygon())
        root.bind("<BackSpace>", lambda _: self.remove_active_point())
        root.bind("<Escape>", lambda _: self.cancel_active())
        root.bind("<Control-s>", lambda _: self.save())
        root.bind("<Delete>", lambda _: self.undo())
        root.bind("<Configure>", lambda _: self.render())
        root.protocol("WM_DELETE_WINDOW", self.close)
        if self.images:
            self.load()
        else:
            self.render()
            self.update_status()

    def image_path(self) -> Path:
        return self.images[self.index]

    def label_path(self) -> Path:
        return self.output / f"{self.image_path().stem}.txt"

    def select_label(self, label: int) -> None:
        if label < len(self.labels):
            self.current_label = label
            self.update_status()

    def select_mode(self, mode: str) -> None:
        self.cancel_active()
        self.mode = mode
        self.update_status()

    def import_folder(self) -> None:
        selected = filedialog.askdirectory(title="Select image folder")
        if selected:
            self.import_paths([Path(selected)])

    def import_images(self) -> None:
        selected = filedialog.askopenfilenames(title="Select images", filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All files", "*.*")])
        if selected:
            self.import_paths([Path(path) for path in selected])

    def open_project(self) -> None:
        selected = filedialog.askdirectory(title="Select annotation project")
        if not selected:
            return
        project = Path(selected)
        reference = project / "reference_images"
        if reference.is_dir():
            self.workspace, self.reference_dir, self.output = project, reference, project / "labels"
            self.output.mkdir(parents=True, exist_ok=True)
            self.images = collect_images(reference)
            self.index = 0
            self.load()
        else:
            self.import_paths([project])

    def import_paths(self, paths: list[Path]) -> None:
        copied = import_sources(paths, self.reference_dir)
        if not copied:
            messagebox.showwarning("No images", "The selected source contains no supported images.")
            return
        self.images = collect_images(self.reference_dir)
        self.index = self.images.index(copied[0]) if copied[0] in self.images else 0
        self.load()
        self.update_status(saved=True)

    def load(self) -> None:
        if not self.images:
            self.render()
            self.update_status()
            return
        self.shapes = parse_shapes(self.label_path())
        image = Image.open(self.image_path()).convert("RGB")
        self.image_size = image.size
        self.render(image)
        self.update_status()

    def render(self, image: Image.Image | None = None) -> None:
        if not self.canvas.winfo_exists():
            return
        if not self.images:
            self.canvas.delete("all")
            return
        image = image or Image.open(self.image_path()).convert("RGB")
        width, height = max(self.canvas.winfo_width(), 100), max(self.canvas.winfo_height(), 100)
        self.scale = min(width / image.width, height / image.height)
        shown = image.resize((max(1, int(image.width * self.scale)), max(1, int(image.height * self.scale))))
        self.offset = ((width - shown.width) / 2, (height - shown.height) / 2)
        self.photo = ImageTk.PhotoImage(shown)
        self.canvas.delete("all")
        self.canvas.create_image(*self.offset, image=self.photo, anchor=tk.NW)
        for shape in self.shapes:
            self.draw_shape(shape.points, shape.label, closed=True)
        if self.active_points:
            points = self.active_points[:]
            if self.mode == "polygon" and self.pointer:
                points.append(self.pointer)
            elif self.mode == "freehand" and self.pointer:
                points.append(self.pointer)
            self.draw_shape(points, self.current_label, closed=False)

    def draw_shape(self, points: list[tuple[float, float]], label: int, closed: bool) -> None:
        canvas_points = [v for point in points for v in self.to_canvas(*point)]
        if len(canvas_points) >= 4:
            self.canvas.create_line(*canvas_points, fill=COLORS[label % len(COLORS)], width=3, joinstyle=tk.ROUND)
            if closed and len(points) >= 3:
                self.canvas.create_line(*canvas_points, canvas_points[0], canvas_points[1], fill=COLORS[label % len(COLORS)], width=3, joinstyle=tk.ROUND)
            x, y = self.to_canvas(*points[0])
            self.canvas.create_text(x + 4, y + 4, text=self.labels[label], anchor=tk.NW, fill="white")
        for point in points if not closed else []:
            x, y = self.to_canvas(*point)
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=COLORS[label % len(COLORS)], outline="white")

    def to_canvas(self, x: float, y: float) -> tuple[float, float]:
        return (self.offset[0] + x * self.image_size[0] * self.scale, self.offset[1] + y * self.image_size[1] * self.scale)

    def to_normalized(self, x: float, y: float) -> tuple[float, float]:
        return (clamp((x - self.offset[0]) / (self.image_size[0] * self.scale)), clamp((y - self.offset[1]) / (self.image_size[1] * self.scale)))

    def inside(self, x: float, y: float) -> bool:
        cx, cy = self.to_normalized(x, y)
        return self.offset[0] <= x <= self.offset[0] + self.image_size[0] * self.scale and self.offset[1] <= y <= self.offset[1] + self.image_size[1] * self.scale and 0 <= cx <= 1 and 0 <= cy <= 1

    def press(self, event: tk.Event) -> None:
        if not self.inside(event.x, event.y):
            return
        point = self.to_normalized(event.x, event.y)
        self.pointer = point
        if self.mode == "polygon":
            self.active_points.append(point)
        elif self.mode == "freehand":
            self.active_points = [point]
        else:
            self.drag_start = point
            self.active_points = [point, point]
        self.render()

    def drag(self, event: tk.Event) -> None:
        if self.drag_start is None and self.mode not in {"freehand"}:
            return
        if not self.inside(event.x, event.y):
            return
        point = self.to_normalized(event.x, event.y)
        self.pointer = point
        if self.mode == "freehand":
            if not self.active_points or math.dist(self.active_points[-1], point) >= 0.002:
                self.active_points.append(point)
        elif self.mode in {"box", "ellipse"} and self.drag_start:
            self.active_points = rectangle_points(self.drag_start, point) if self.mode == "box" else ellipse_points(self.drag_start, point)
        self.render()

    def release(self, event: tk.Event) -> None:
        if self.mode == "freehand":
            self.finish_polygon()
        elif self.mode in {"box", "ellipse"} and self.drag_start:
            self.finish_polygon()
        self.drag_start = None

    def motion(self, event: tk.Event) -> None:
        if self.active_points and self.mode == "polygon" and self.inside(event.x, event.y):
            self.pointer = self.to_normalized(event.x, event.y)
            self.render()

    def finish_polygon(self) -> None:
        points = valid_points(self.active_points)
        if points:
            self.shapes.append(Shape(self.current_label, self.mode, points))
        self.cancel_active()
        self.update_status()

    def remove_active_point(self) -> None:
        if self.active_points:
            self.active_points.pop()
            self.render()

    def cancel_active(self) -> None:
        self.active_points, self.drag_start, self.pointer = [], None, None
        self.render()

    def undo(self) -> None:
        if self.shapes:
            self.shapes.pop()
            self.render()
            self.update_status()

    def clear(self) -> None:
        if self.shapes and messagebox.askyesno("Clear annotations", "Remove all shapes from this image?"):
            self.shapes = []
            self.render()
            self.update_status()

    def save(self) -> None:
        if not self.images:
            return
        self.output.mkdir(parents=True, exist_ok=True)
        content = "\n".join(" ".join([str(shape.label), *(f"{x:.6f} {y:.6f}" for x, y in shape.points)]) for shape in self.shapes)
        self.label_path().write_text(content + ("\n" if content else ""), encoding="utf-8")
        self.update_status(saved=True)

    def move(self, delta: int) -> None:
        if not self.images:
            return
        self.save()
        self.index = max(0, min(len(self.images) - 1, self.index + delta))
        self.load()

    def close(self) -> None:
        self.save()
        self.root.destroy()

    def update_status(self, saved: bool = False) -> None:
        if not self.images:
            self.status.set("No images loaded | Import folder or images to begin")
            return
        suffix = " — saved" if saved else ""
        self.status.set(f"{self.index + 1}/{len(self.images)}  {self.image_path().name} | class: {self.labels[self.current_label]} | mode: {self.mode} | shapes: {len(self.shapes)}{suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image_dir", type=Path, nargs="?", help="optional initial image folder")
    parser.add_argument("--classes", type=Path, required=True)
    parser.add_argument("--labels-out", type=Path, help="optional labels folder; defaults to workspace/labels")
    parser.add_argument("--workspace", type=Path, default=Path("datasets/annotation-workspace"), help="reference project folder")
    args = parser.parse_args()
    labels = [line.strip() for line in args.classes.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not labels:
        raise SystemExit("classes file must contain at least one class")
    workspace = args.workspace
    reference_dir = workspace / "reference_images"
    output = args.labels_out or workspace / "labels"
    workspace.mkdir(parents=True, exist_ok=True)
    reference_dir.mkdir(parents=True, exist_ok=True)
    if args.image_dir and not args.image_dir.is_dir():
        raise SystemExit(f"image folder does not exist or is not a folder: {args.image_dir}")
    if args.image_dir:
        import_sources([args.image_dir], reference_dir)
    images = collect_images(reference_dir)
    if len({image.stem for image in images}) != len(images):
        raise SystemExit("image stems must be unique so labels cannot overwrite each other")
    root = tk.Tk()
    Annotator(root, images, labels, workspace, reference_dir, output)
    root.mainloop()


if __name__ == "__main__":
    main()
