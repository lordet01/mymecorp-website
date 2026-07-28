#!/usr/bin/env python3
"""Generate myMe chrome-on-black favicons and app icons."""

from __future__ import annotations

import struct
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "myme_Design Asset" / "new" / "myMe_symbol_chrome.png"
# Prefer original longtext/symbol assets if chrome file was already flattened
SRC_FALLBACK = ROOT / "myme_Design Asset" / "new" / "myMe_symbol_chrome_clear.png"
FAVICON_DIR = ROOT / "myme_Design Asset" / "favicon"
ICON_DIR = ROOT / "myme_Design Asset" / "icon"
BG = (0, 0, 0, 255)


def cutout_chrome(src: Path) -> Image.Image:
    """Remove charcoal plate; keep metallic emblem with soft edges."""
    img = Image.open(src).convert("RGBA")
    arr = np.array(img).astype(np.float32)
    rgb = arr[:, :, :3]
    mx = rgb.max(axis=2)

    fg = (mx >= 48).astype(np.uint8) * 255
    fg_img = Image.fromarray(fg, mode="L").filter(ImageFilter.MaxFilter(3))
    fg_img = fg_img.filter(ImageFilter.GaussianBlur(radius=0.7))
    alpha = np.array(fg_img).astype(np.float32) / 255.0
    alpha[mx < 18] = 0.0
    mid = (mx >= 18) & (mx < 48)
    alpha[mid] *= np.clip((mx[mid] - 18.0) / 30.0, 0, 1)

    # If source already has transparency, respect it
    src_a = arr[:, :, 3] / 255.0
    if float(src_a.mean()) < 0.99:
        alpha = np.minimum(alpha, src_a)

    out = arr.copy()
    out[:, :, 3] = np.clip(alpha * 255.0, 0, 255)
    ys, xs = np.where(alpha > 0.06)
    if len(ys) == 0:
        return img
    pad = 8
    y0, y1 = max(0, int(ys.min()) - pad), min(out.shape[0], int(ys.max()) + pad + 1)
    x0, x1 = max(0, int(xs.min()) - pad), min(out.shape[1], int(xs.max()) + pad + 1)
    return Image.fromarray(out[y0:y1, x0:x1].astype(np.uint8), "RGBA")


def prepare_master(symbol: Image.Image, canvas_size: int = 1024, content_ratio: float = 0.78) -> Image.Image:
    master = Image.new("RGBA", (canvas_size, canvas_size), BG)
    s = symbol.copy()
    s.thumbnail((int(canvas_size * content_ratio), int(canvas_size * content_ratio)), Image.Resampling.LANCZOS)
    master.alpha_composite(s, ((canvas_size - s.width) // 2, (canvas_size - s.height) // 2))
    return master


def flatten_rgb(img: Image.Image) -> Image.Image:
    flat = Image.new("RGB", img.size, (0, 0, 0))
    flat.paste(img, mask=img.split()[-1])
    return flat


def export_png(master: Image.Image, path: Path, size: int) -> None:
    out = flatten_rgb(master.resize((size, size), Image.Resampling.LANCZOS))
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path, format="PNG", optimize=True)
    print(f"Wrote {path.relative_to(ROOT)} ({size}x{size})")


def export_ico(master: Image.Image, path: Path, sizes: list[int]) -> None:
    payloads = []
    for size in sizes:
        rgba = Image.new("RGBA", (size, size), BG)
        rgba.alpha_composite(master.resize((size, size), Image.Resampling.LANCZOS))
        buf = BytesIO()
        rgba.save(buf, format="PNG")
        payloads.append(buf.getvalue())

    offset = 6 + 16 * len(sizes)
    entries = []
    for size, data in zip(sizes, payloads):
        w = 0 if size >= 256 else size
        entries.append(struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(data), offset))
        offset += len(data)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<HHH", 0, 1, len(sizes)) + b"".join(entries) + b"".join(payloads))
    print(f"Wrote {path.relative_to(ROOT)} sizes={sizes} bytes={path.stat().st_size}")


def main() -> None:
    # Restore cutout from clear cache if current chrome file is already flattened black
    src = SRC
    clear = SRC_FALLBACK
    if clear.exists():
        symbol = Image.open(clear).convert("RGBA")
    else:
        # Prefer original uploaded asset when regenerating from scratch
        uploaded = Path("/Users/int/.cursor/projects/Users-int-Projects-mymecorp-website/assets/myMe_logo_black-c8b2717a-406f-416b-9739-aa6ab5b0ed92.png")
        if uploaded.exists():
            src = uploaded
        symbol = cutout_chrome(src)
        clear.parent.mkdir(parents=True, exist_ok=True)
        symbol.save(clear, optimize=True)

    master = prepare_master(symbol)
    FAVICON_DIR.mkdir(parents=True, exist_ok=True)
    ICON_DIR.mkdir(parents=True, exist_ok=True)

    export_png(master, FAVICON_DIR / "favicon-16x16.png", 16)
    export_png(master, FAVICON_DIR / "favicon-32x32.png", 32)
    export_png(master, FAVICON_DIR / "apple-touch-icon.png", 180)
    export_png(master, FAVICON_DIR / "android-chrome-192x192.png", 192)
    export_png(master, FAVICON_DIR / "android-chrome-512x512.png", 512)
    export_png(master, FAVICON_DIR / "android-chrome-512x512-maskable.png", 512)
    export_ico(master, FAVICON_DIR / "favicon.ico", [16, 32, 48])
    export_png(master, ICON_DIR / "apple-touch-icon.png", 180)

    # Keep brand primary symbol in sync
    export_png(master, ROOT / "myme_Design Asset" / "new" / "myme_symbol_primary.png", 1024)
    export_png(master, ROOT / "myme_Design Asset" / "new" / "myMe_symbol_chrome.png", 1024)

    print("All icons generated successfully.")


if __name__ == "__main__":
    main()
