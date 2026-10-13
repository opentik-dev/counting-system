#!/usr/bin/env python3
"""Small local bounding-box annotator for the extracted seed images.

Annotations are saved as YOLO ``class cx cy width height`` text files; source
images are never modified. Use CVAT later when video tracking is required.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk


COLORS = ("#ffd166", "#06d6a0", "#118ab2", "#ef476f", "#a78bfa")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


class Annotator:
    def __init__(self, root: tk.Tk, images: list[Path], labels: list[str], output: Path) -> None:
        self.root = root
        self.images = images
        self.labels = labels
        self.output = output
        self.index = 0
        self.current_label = 0
        self.boxes: list[tuple[int, float, float, float, float]] = []
        self.drag_start: tuple[float, float] | None = None
        self.preview_box: int | None = None
        self.photo: ImageTk.PhotoImage | None = None
        self.image_size = (1, 1)
        self.scale = 1.0
        self.offset = (0.0, 0.0)

        root.title("Warehouse carton annotator")
        root.geometry("1120x820")
        toolbar = tk.Frame(root)
        toolbar.pack(fill=tk.X, padx=8, pady=6)
        self.status = tk.StringVar()
        for number, label in enumerate(labels):
            tk.Button(
                toolbar,
                text=f"{number + 1}: {label}",
                command=lambda n=number: self.select_label(n),
                bg=COLORS[number % len(COLORS)],
            ).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=8)
        tk.Button(toolbar, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Previous", command=lambda: self.move(-1)).pack(side=tk.RIGHT, padx=2)
        tk.Button(toolbar, text="Save / Next", command=lambda: self.move(1)).pack(side=tk.RIGHT, padx=2)
        tk.Label(root, textvariable=self.status, anchor="w").pack(fill=tk.X, padx=8)
        self.canvas = tk.Canvas(root, bg="#202124", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.canvas.bind("<ButtonPress-1>", self.start_box)
        self.canvas.bind("<B1-Motion>", self.drag_box)
        self.canvas.bind("<ButtonRelease-1>", self.finish_box)
        root.bind("<Key-1>", lambda _: self.select_label(0))
        root.bind("<Key-2>", lambda _: self.select_label(1))
        root.bind("<Key-3>", lambda _: self.select_label(2))
        root.bind("<Key-4>", lambda _: self.select_label(3))
        root.bind("<Key-5>", lambda _: self.select_label(4))
        root.bind("<Control-s>", lambda _: self.save())
        root.bind("<Delete>", lambda _: self.undo())
        root.bind("<Configure>", lambda _: self.render())
        self.load()

    def select_label(self, label: int) -> None:
        if label < len(self.labels):
            self.current_label = label
            self.update_status()

    def label_path(self) -> Path:
        return self.output / f"{self.images[self.index].stem}.txt"

    def load(self) -> None:
        self.boxes = []
        image = Image.open(self.images[self.index]).convert("RGB")
        self.image_size = image.size
        path = self.label_path()
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                fields = line.split()
                if len(fields) == 5:
                    self.boxes.append(tuple([int(fields[0]), *map(float, fields[1:])]))
        self.render(image)
        self.update_status()

    def render(self, image: Image.Image | None = None) -> None:
        if not self.images or not self.canvas.winfo_exists():
            return
        if image is None:
            image = Image.open(self.images[self.index]).convert("RGB")
        width = max(self.canvas.winfo_width(), 100)
        height = max(self.canvas.winfo_height(), 100)
        scale = min(width / image.width, height / image.height)
        display_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
        shown = image.resize(display_size)
        self.scale = scale
        self.offset = ((width - display_size[0]) / 2, (height - display_size[1]) / 2)
        self.photo = ImageTk.PhotoImage(shown)
        self.canvas.delete("all")
        self.canvas.create_image(*self.offset, image=self.photo, anchor=tk.NW)
        for label, cx, cy, box_w, box_h in self.boxes:
            top_left = self.to_canvas(cx - box_w / 2, cy - box_h / 2)
            bottom_right = self.to_canvas(cx + box_w / 2, cy + box_h / 2)
            self.canvas.create_rectangle(top_left[0], top_left[1], bottom_right[0], bottom_right[1], outline=COLORS[label % len(COLORS)], width=3)
            self.canvas.create_text(top_left[0] + 4, top_left[1] + 4, text=self.labels[label], anchor=tk.NW, fill="white")

    def to_canvas(self, x: float, y: float) -> tuple[float, float]:
        return (self.offset[0] + x * self.image_size[0] * self.scale, self.offset[1] + y * self.image_size[1] * self.scale)

    def to_normalized(self, x: float, y: float) -> tuple[float, float]:
        return ((x - self.offset[0]) / (self.image_size[0] * self.scale), (y - self.offset[1]) / (self.image_size[1] * self.scale))

    def start_box(self, event: tk.Event) -> None:
        self.drag_start = (event.x, event.y)
        self.preview_box = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline=COLORS[self.current_label], width=3)

    def drag_box(self, event: tk.Event) -> None:
        if self.drag_start is not None and self.preview_box is not None:
            self.canvas.coords(self.preview_box, self.drag_start[0], self.drag_start[1], event.x, event.y)

    def finish_box(self, event: tk.Event) -> None:
        if self.drag_start is None:
            return
        x1, y1 = self.to_normalized(*self.drag_start)
        x2, y2 = self.to_normalized(event.x, event.y)
        left, right = sorted((max(0.0, min(1.0, x1)), max(0.0, min(1.0, x2))))
        top, bottom = sorted((max(0.0, min(1.0, y1)), max(0.0, min(1.0, y2))))
        if right - left >= 0.01 and bottom - top >= 0.01:
            self.boxes.append((self.current_label, (left + right) / 2, (top + bottom) / 2, right - left, bottom - top))
        self.drag_start = None
        self.preview_box = None
        self.render()
        self.update_status()

    def undo(self) -> None:
        if self.boxes:
            self.boxes.pop()
            self.render()
            self.update_status()

    def clear(self) -> None:
        if self.boxes and messagebox.askyesno("Clear boxes", "Remove all boxes from this image?"):
            self.boxes = []
            self.render()
            self.update_status()

    def save(self) -> None:
        self.output.mkdir(parents=True, exist_ok=True)
        content = "\n".join("%d %.6f %.6f %.6f %.6f" % box for box in self.boxes)
        self.label_path().write_text(content + ("\n" if content else ""), encoding="utf-8")
        self.update_status(saved=True)

    def move(self, delta: int) -> None:
        self.save()
        self.index = max(0, min(len(self.images) - 1, self.index + delta))
        self.load()

    def update_status(self, saved: bool = False) -> None:
        suffix = " — saved" if saved else ""
        self.status.set(f"{self.index + 1}/{len(self.images)}  {self.images[self.index].name}  | label: {self.labels[self.current_label]} | boxes: {len(self.boxes)}{suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image_dir", type=Path)
    parser.add_argument("--classes", type=Path, required=True)
    parser.add_argument("--labels-out", type=Path, required=True)
    args = parser.parse_args()
    labels = [line.strip() for line in args.classes.read_text(encoding="utf-8").splitlines() if line.strip()]
    images = sorted(p for p in args.image_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    if not labels or not images:
        raise SystemExit("classes file and image directory must both contain data")
    root = tk.Tk()
    Annotator(root, images, labels, args.labels_out)
    root.mainloop()


if __name__ == "__main__":
    main()
