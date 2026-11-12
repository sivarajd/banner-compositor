#!/usr/bin/env python3
"""Tile images into one labelled contact sheet, so many candidates can be judged in
a single look. Each cell shows the file name and its pixel size.

Usage:
    contact_sheet.py downloads/*.jpg --out sheet.jpg [--cols 3] [--cell 640x360]

Requires Pillow.
"""
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--out", required=True, help="output sheet (.jpg or .png)")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--cell", default="640x360", help="cell size WxH")
    ap.add_argument("--force", action="store_true", help="allow overwriting the output file")
    args = ap.parse_args(argv)

    out = Path(args.out).expanduser()
    if out.exists() and not args.force:
        sys.exit(f"{out} already exists; choose a new name or pass --force")
    try:
        cw, ch = (int(v) for v in args.cell.lower().split("x"))
    except ValueError:
        sys.exit("--cell takes WxH, e.g. 640x360")
    label_h, gap = 22, 6
    try:
        font = ImageFont.load_default(size=14)
    except TypeError:  # older Pillow
        font = ImageFont.load_default()

    cells = []
    for name in args.images:
        p = Path(name).expanduser()
        try:
            im = Image.open(p)
            size = im.size
            im = ImageOps.exif_transpose(im).convert("RGB")
        except Exception as e:  # not an image, or unreadable
            print(f"skipped {p}: {e}", file=sys.stderr)
            continue
        im.thumbnail((cw, ch), Image.Resampling.LANCZOS)
        cell = Image.new("RGB", (cw, ch + label_h), "#111111")
        cell.paste(im, ((cw - im.width) // 2, (ch - im.height) // 2))
        ImageDraw.Draw(cell).text((4, ch + 3), f"{p.name}  {size[0]}x{size[1]}", fill="#ffffff", font=font)
        cells.append(cell)
    if not cells:
        sys.exit("no readable images")

    cols = max(1, min(args.cols, len(cells)))
    rows = -(-len(cells) // cols)
    sheet = Image.new("RGB", (cols * (cw + gap) + gap, rows * (ch + label_h + gap) + gap), "#000000")
    for i, cell in enumerate(cells):
        sheet.paste(cell, (gap + (i % cols) * (cw + gap), gap + (i // cols) * (ch + label_h + gap)))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88) if out.suffix.lower() in (".jpg", ".jpeg") else sheet.save(out)
    print(f"wrote {out}  {sheet.width}x{sheet.height}  {len(cells)} images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
