from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "public" / "assets" / "superior-logo.png"
ASSET_DIR = ROOT / "site" / "public" / "assets"
DOCS_ASSET_DIR = ROOT / "docs" / "assets"
ICON_PATH = ROOT / "packaging" / "windows" / "superior.ico"


def save_png(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)


def _edge_mask(width: int, height: int) -> list[list[bool]]:
    return [[False for _ in range(width)] for _ in range(height)]


def _is_background(pixel: tuple[int, int, int, int]) -> bool:
    r, g, b, _a = pixel
    return max(r, g, b) <= 14


def remove_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    visited = _edge_mask(width, height)
    queue: deque[tuple[int, int]] = deque()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        if visited[y][x]:
            continue
        visited[y][x] = True
        if not _is_background(pixels[x, y]):
            continue
        pixels[x, y] = (0, 0, 0, 0)
        queue.extend(
            [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            ]
        )

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            luminance = max(r, g, b)
            if luminance <= 10:
                continue
            if luminance < 28:
                alpha = int(round(a * 0.55))
                pixels[x, y] = (r, g, b, alpha)
    return rgba


def crop_with_padding(image: Image.Image, *, padding_ratio: float = 0.08) -> Image.Image:
    bbox = image.getbbox()
    if bbox is None:
        return image
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top
    pad_x = int(round(width * padding_ratio))
    pad_y = int(round(height * padding_ratio))
    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(image.width, right + pad_x)
    bottom = min(image.height, bottom + pad_y)
    return image.crop((left, top, right, bottom))


def to_square(image: Image.Image, *, size: int = 2048) -> Image.Image:
    square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    image = image.copy()
    image.thumbnail((int(size * 0.9), int(size * 0.9)), Image.Resampling.LANCZOS)
    left = (size - image.width) // 2
    top = (size - image.height) // 2
    square.paste(image, (left, top), image)
    return square


def save_emblem(source: Image.Image) -> Path:
    emblem = to_square(crop_with_padding(remove_background(source)))
    output = ASSET_DIR / "superior-emblem.png"
    save_png(emblem, output)
    DOCS_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    save_png(emblem, DOCS_ASSET_DIR / "superior-emblem.png")
    return output


def save_head_mark(emblem_path: Path) -> Path:
    emblem = Image.open(emblem_path).convert("RGBA")
    width, height = emblem.size
    head = emblem.crop((int(width * 0.26), int(height * 0.08), int(width * 0.74), int(height * 0.52)))
    head = to_square(crop_with_padding(head, padding_ratio=0.14), size=1024)
    output = ASSET_DIR / "superior-head.png"
    save_png(head, output)
    save_png(head, DOCS_ASSET_DIR / "superior-head.png")
    return output


def save_wordmark(emblem_path: Path) -> Path:
    emblem = Image.open(emblem_path).convert("RGBA")
    width, height = emblem.size
    wordmark = emblem.crop((int(width * 0.08), int(height * 0.32), int(width * 0.92), int(height * 0.72)))
    wordmark = crop_with_padding(wordmark, padding_ratio=0.06)
    output = ASSET_DIR / "superior-wordmark.png"
    save_png(wordmark, output)
    save_png(wordmark, DOCS_ASSET_DIR / "superior-wordmark.png")
    return output


def save_scanner_frame() -> Path:
    width, height = 1600, 980
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def rect(box: tuple[int, int, int, int], color: tuple[int, int, int, int], line_width: int) -> None:
        draw.rounded_rectangle(box, radius=42, outline=color, width=line_width)

    rect((28, 28, width - 28, height - 28), (0, 229, 255, 220), 6)
    rect((56, 56, width - 56, height - 56), (138, 92, 255, 170), 4)
    rect((88, 88, width - 88, height - 88), (255, 255, 255, 110), 2)

    for step in range(120, width - 120, 80):
        draw.line((step, 104, step, height - 104), fill=(255, 255, 255, 28), width=1)
    for step in range(120, height - 120, 70):
        draw.line((104, step, width - 104, step), fill=(255, 255, 255, 28), width=1)

    draw.arc((370, 180, width - 370, height - 180), start=206, end=342, fill=(0, 229, 255, 120), width=6)
    draw.arc((300, 130, width - 300, height - 130), start=198, end=350, fill=(255, 0, 212, 88), width=4)
    sweep = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sweep_draw = ImageDraw.Draw(sweep)
    sweep_draw.pieslice((300, 120, width - 300, height - 120), start=320, end=336, fill=(0, 229, 255, 65))
    sweep = sweep.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(sweep)

    output = ASSET_DIR / "superior-scanner-frame.png"
    save_png(image, output)
    save_png(image, DOCS_ASSET_DIR / "superior-scanner-frame.png")
    return output


def save_icon(head_path: Path) -> Path:
    head = Image.open(head_path).convert("RGBA")
    base = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((18, 18, 494, 494), radius=120, fill=(9, 14, 40, 255), outline=(0, 229, 255, 210), width=12)
    glow = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle((34, 34, 478, 478), radius=106, outline=(138, 92, 255, 170), width=12)
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    base.alpha_composite(glow)

    icon_art = head.copy()
    icon_art.thumbnail((360, 360), Image.Resampling.LANCZOS)
    left = (512 - icon_art.width) // 2
    top = (512 - icon_art.height) // 2 - 10
    base.alpha_composite(icon_art, (left, top))
    base.save(ICON_PATH, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    png_output = ASSET_DIR / "superior-app-icon.png"
    save_png(base, png_output)
    save_png(base, DOCS_ASSET_DIR / "superior-app-icon.png")
    return png_output


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source logo: {SOURCE}")
    source = Image.open(SOURCE)
    emblem_path = save_emblem(source)
    head_path = save_head_mark(emblem_path)
    save_wordmark(emblem_path)
    save_scanner_frame()
    save_icon(head_path)


if __name__ == "__main__":
    main()
