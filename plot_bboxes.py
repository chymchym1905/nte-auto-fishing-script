from __future__ import annotations

from pathlib import Path

import cv2

from nte_auto_fishing import PRESETS


IMAGES_DIR = Path("images")
TARGETS = {
    "2k": IMAGES_DIR / "2k (2).png",
    "1080p": IMAGES_DIR / "1080p (1).png",
}
COLORS = {
    "bar_region": (0, 255, 255),
    "icon_region": (0, 255, 0),
    "hook_region": (255, 200, 0),
}


def draw_region(image, label, region, color):
    x1, y1, x2, y2 = region
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)

    text_x = x1
    text_y = max(30, y1 - 12)
    cv2.putText(
        image,
        label,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        5,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        label,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
        cv2.LINE_AA,
    )


def plot_preset(name: str, image_path: Path) -> Path:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    preset = PRESETS[name]
    for key, color in COLORS.items():
        draw_region(image, key, preset[key], color)

    output_path = image_path.with_stem(f"{image_path.stem}_bbox")
    if not cv2.imwrite(str(output_path), image):
        raise RuntimeError(f"Could not write output image: {output_path}")

    return output_path


def main():
    for preset_name, image_path in TARGETS.items():
        output_path = plot_preset(preset_name, image_path)
        print(f"{preset_name}: wrote {output_path}")


if __name__ == "__main__":
    main()
