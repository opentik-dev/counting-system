import json

from PIL import Image

from scripts.annotate_warehouse import ellipse_points, import_sources, parse_shapes, valid_points
from scripts.build_warehouse_dataset import build


def test_old_yolo_box_is_read_as_polygon(tmp_path):
    labels = tmp_path / "labels"
    labels.mkdir()
    path = labels / "frame.txt"
    path.write_text("0 0.5 0.5 0.4 0.2\n", encoding="utf-8")
    shapes = parse_shapes(path)
    assert len(shapes) == 1
    assert len(shapes[0].points) == 4


def test_freeform_geometry_is_valid_polygon():
    points = ellipse_points((0.2, 0.2), (0.8, 0.6))
    assert len(points) == 32
    assert len(valid_points(points)) == 32


def test_import_sources_creates_reference_copies_without_stem_collisions(tmp_path):
    first, second, reference = tmp_path / "first", tmp_path / "second", tmp_path / "reference"
    first.mkdir()
    second.mkdir()
    Image.new("RGB", (10, 10), "red").save(first / "frame.jpg")
    Image.new("RGB", (10, 10), "blue").save(second / "frame.jpg")
    imported = import_sources([first, second], reference)
    assert len(imported) == 2
    assert {path.stem for path in imported} == {"frame", "frame_2"}


def test_build_exports_segmentation_and_coco(tmp_path):
    images = tmp_path / "images"
    labels = tmp_path / "labels"
    output = tmp_path / "dataset"
    images.mkdir()
    labels.mkdir()
    Image.new("RGB", (100, 50), "white").save(images / "frame.jpg")
    labels.joinpath("frame.txt").write_text("1 0.1 0.1 0.9 0.1 0.9 0.9 0.1 0.9\n", encoding="utf-8")
    classes = tmp_path / "classes.txt"
    classes.write_text("carton\npallet\n", encoding="utf-8")

    image_count, annotation_count = build(images, labels, classes, output, include_empty=True)
    coco = json.loads((output / "annotations.json").read_text(encoding="utf-8"))
    assert (image_count, annotation_count) == (1, 1)
    assert coco["annotations"][0]["category_id"] == 2
    assert (output / "images/frame.jpg").is_file()
    assert (output / "labels/frame.txt").is_file()
    assert "names:" in (output / "data.yaml").read_text(encoding="utf-8")
