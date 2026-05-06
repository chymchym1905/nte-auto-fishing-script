from pathlib import Path
import sys

from PIL import Image


ICON_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: make_icon.py <source-png> <target-ico>")
        return 1

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])

    if not source.exists():
        print(f"Missing source image: {source}")
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        image = image.convert("RGBA")
        image.save(target, format="ICO", sizes=ICON_SIZES)

    print(f"Wrote icon: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
