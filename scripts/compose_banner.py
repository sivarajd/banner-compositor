#!/usr/bin/env python3
"""Compose a wide banner from a JSON layout spec.

A banner is a row of tiles (photos scaled and cropped into slots, each fading into
the tile on its left) with overlays (logos) drawn on top. Sources are only scaled
and cropped. See references/spec-format.md for the spec.

Usage:
    compose_banner.py layout.json [--out FILE ...] [--force] [--preview DIR]

Requires Pillow.
"""
import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

RESAMPLE = Image.Resampling.LANCZOS


class SpecError(Exception):
    pass


def resolve(path, base):
    p = Path(path).expanduser()
    return p if p.is_absolute() else base / p


def load(path, base, what):
    p = resolve(path, base)
    if not p.is_file():
        raise SpecError(f"{what}: source file not found: {p}")
    return Image.open(p)


def odd(n):
    """Kernel size for a rank filter that reaches about n pixels."""
    return 2 * max(0, int(round(n))) + 1


def build_tile(tile, idx, canvas_h, base, warnings):
    name = f"tile {idx} ({tile.get('src', '?')})"
    for key in ("src", "x", "width"):
        if key not in tile:
            raise SpecError(f"{name}: missing '{key}'")
    im = load(tile["src"], base, name).convert("RGB")
    if "src_crop" in tile:
        x, y, w, h = tile["src_crop"]
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > im.width or y + h > im.height:
            raise SpecError(f"{name}: src_crop {tile['src_crop']} is outside the {im.width}x{im.height} source")
        im = im.crop((x, y, x + w, y + h))
    tw = int(tile["width"])
    if tw <= 0:
        raise SpecError(f"{name}: width must be positive")
    cover = max(tw / im.width, canvas_h / im.height)
    scale = float(tile.get("scale", cover))
    if scale < cover - 1e-4:
        raise SpecError(
            f"{name}: scale {scale:.4f} would leave an empty band; it needs at least {cover:.4f} "
            f"to fill a {tw}x{canvas_h} slot"
        )
    sw = max(tw, round(im.width * scale))
    sh = max(canvas_h, round(im.height * scale))
    if scale > 1.25:
        warnings.append(f"{name}: source is enlarged {scale:.2f}x and will look soft; a larger source would help")
    im = im.resize((sw, sh), RESAMPLE)
    fx, fy = tile.get("focus", [0.5, 0.5])
    cx = int(tile.get("crop_x", round((sw - tw) * fx)))
    cy = int(tile.get("crop_y", round((sh - canvas_h) * fy)))
    if cx < 0 or cy < 0 or cx + tw > sw or cy + canvas_h > sh:
        raise SpecError(
            f"{name}: crop offset ({cx},{cy}) is outside the scaled source {sw}x{sh}; "
            f"crop_x may be 0..{sw - tw} and crop_y 0..{sh - canvas_h}"
        )
    return im.crop((cx, cy, cx + tw, cy + canvas_h)), scale


def feather_mask(width, height, feather):
    mask = Image.new("L", (width, height), 255)
    f = min(int(feather), width)
    if f > 0:
        ramp = Image.new("L", (f, 1))
        ramp.putdata([round(255 * (k + 0.5) / f) for k in range(f)])
        mask.paste(ramp.resize((f, height)), (0, 0))
    return mask


def build_overlay(ov, idx, base, warnings):
    name = f"overlay {idx} ({ov.get('src', '?')})"
    for key in ("src", "x", "y"):
        if key not in ov:
            raise SpecError(f"{name}: missing '{key}'")
    im = load(ov["src"], base, name).convert("RGBA")
    alpha = im.getchannel("A")
    if alpha.getextrema()[0] == 255:
        warnings.append(f"{name}: image has no transparency, so it will be pasted as a solid rectangle")
    if ov.get("trim", True):
        box = alpha.getbbox()
        if box:
            im = im.crop(box)
    if "width" in ov:
        w = int(ov["width"])
        h = max(1, round(im.height * w / im.width))
    elif "height" in ov:
        h = int(ov["height"])
        w = max(1, round(im.width * h / im.height))
    else:
        w, h = im.size
    if w > im.width * 1.25:
        warnings.append(f"{name}: logo is enlarged {w / im.width:.2f}x and will look soft")
    if (w, h) != im.size:
        im = im.resize((w, h), RESAMPLE)
    opacity = float(ov.get("opacity", 1.0))
    if opacity < 1.0:
        im.putalpha(im.getchannel("A").point(lambda v: round(v * opacity)))
    return im


def silhouette(overlay, pos, size, close=0, grow=0):
    """Full-canvas mask of the overlay's shape, optionally closed and grown."""
    mask = Image.new("L", size, 0)
    mask.paste(overlay.getchannel("A").point(lambda v: 255 if v > 10 else 0), pos)
    if close > 0:
        mask = mask.filter(ImageFilter.MaxFilter(odd(close))).filter(ImageFilter.MinFilter(odd(close)))
    if grow > 0:
        mask = mask.filter(ImageFilter.MaxFilter(odd(grow)))
    return mask


def paste_color(canvas, color, mask, opacity=1.0):
    if opacity < 1.0:
        mask = mask.point(lambda v: round(v * opacity))
    canvas.paste(Image.new("RGBA", canvas.size, color), (0, 0), mask)


def compose(spec, base):
    warnings = []
    canvas_spec = spec.get("canvas") or {}
    try:
        W, H = int(canvas_spec["width"]), int(canvas_spec["height"])
    except (KeyError, TypeError, ValueError):
        raise SpecError("canvas needs integer 'width' and 'height'")
    canvas = Image.new("RGBA", (W, H), canvas_spec.get("background", "#000000"))
    default_feather = int(spec.get("feather", 40))
    tiles = sorted(enumerate(spec.get("tiles") or []), key=lambda it: it[1].get("x", 0))
    if not tiles:
        raise SpecError("spec has no tiles")

    report, seams = [], []
    covered_to = 0
    for order, (idx, tile) in enumerate(tiles):
        img, scale = build_tile(tile, idx, H, base, warnings)
        x, tw = int(tile["x"]), img.width
        feather = 0 if order == 0 else int(tile.get("feather", default_feather))
        if x > covered_to:
            raise SpecError(
                f"tile {idx}: starts at x={x} but the tiles before it end at x={covered_to}, "
                f"leaving a {x - covered_to}px gap"
            )
        if feather and x + feather > covered_to:
            raise SpecError(
                f"tile {idx}: its {feather}px fade runs to x={x + feather} but the tile before it ends at "
                f"x={covered_to}; overlap them by at least the fade width or lower 'feather'"
            )
        if x + tw > W:
            warnings.append(f"tile {idx}: runs {x + tw - W}px past the right edge and is clipped")
        layer = img.convert("RGBA")
        layer.putalpha(feather_mask(tw, H, feather))
        canvas.alpha_composite(layer, (x, 0)) if x >= 0 else canvas.paste(layer, (x, 0), layer)
        covered_to = max(covered_to, x + tw)
        seams.append((x, feather))
        report.append(f"tile {idx}: x={x}..{x + tw}  scale={scale:.3f}  fade={feather}px  {tile['src']}")
    if covered_to < W:
        raise SpecError(f"tiles end at x={covered_to} but the canvas is {W} wide; the last {W - covered_to}px are empty")

    boxes = []
    for idx, ov in enumerate(spec.get("overlays") or []):
        im = build_overlay(ov, idx, base, warnings)
        pos = (int(ov["x"]), int(ov["y"]))
        x0, y0, x1, y1 = pos[0], pos[1], pos[0] + im.width, pos[1] + im.height
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            warnings.append(f"overlay {idx}: box {x0},{y0}..{x1},{y1} runs off the {W}x{H} canvas")
        shadow = ov.get("shadow")
        backing = ov.get("backing")
        close = float((backing or {}).get("close", 0))
        if shadow:
            m = silhouette(im, (pos[0] + int(shadow.get("dx", 0)), pos[1] + int(shadow.get("dy", 0))), (W, H), close)
            m = m.filter(ImageFilter.GaussianBlur(float(shadow.get("blur", 6))))
            paste_color(canvas, shadow.get("color", "#000000"), m, float(shadow.get("opacity", 0.5)))
        if backing:
            m = silhouette(im, pos, (W, H), close, float(backing.get("grow", 1)))
            m = m.filter(ImageFilter.GaussianBlur(float(backing.get("soften", 1.0))))
            paste_color(canvas, backing.get("color", "#101010"), m, float(backing.get("opacity", 1.0)))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(im, pos)
        canvas.alpha_composite(layer)
        boxes.append((x0, y0, x1, y1))
        report.append(f"overlay {idx}: {im.width}x{im.height} at {pos[0]},{pos[1]}  {ov['src']}")
    return canvas.convert("RGB"), report, warnings, seams, boxes


def save(img, path, force):
    path = Path(path)
    if path.exists() and not force:
        raise SpecError(f"{path} already exists; choose a new name, or pass --force for your own drafts")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        img.save(path, quality=92, subsampling=0, optimize=True)
    else:
        img.save(path)
    return path


def write_preview(img, seams, boxes, outdir, max_w=1000):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    n = max(1, math.ceil(img.width / max_w))
    step = math.ceil(img.width / n)
    paths = []
    for i in range(n):
        seg = img.crop((i * step, 0, min(img.width, (i + 1) * step), img.height))
        p = outdir / f"segment_{i + 1:02d}.png"
        seg.save(p)
        paths.append(p)
    guides = img.copy()
    d = ImageDraw.Draw(guides)
    for x, feather in seams:
        d.line([(x, 0), (x, img.height)], fill="#00ffff", width=1)
        if feather:
            d.line([(x + feather, 0), (x + feather, img.height)], fill="#ff00ff", width=1)
    for box in boxes:
        d.rectangle(box, outline="#ffff00", width=1)
    g = outdir / "guides.png"
    guides.save(g)
    return paths + [g]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="layout JSON file; source paths are relative to it")
    ap.add_argument("--out", nargs="+", help="output file(s); overrides 'output' in the spec (.png, .jpg, .webp)")
    ap.add_argument("--force", action="store_true", help="allow overwriting existing output files")
    ap.add_argument("--preview", metavar="DIR", help="write full-size inspection segments and guides.png here")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).expanduser().resolve()
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read spec: {e}", file=sys.stderr)
        return 2
    base = spec_path.parent
    outs = args.out or spec.get("output")
    if isinstance(outs, str):
        outs = [outs]
    if not outs:
        print("ERROR: no output given; add 'output' to the spec or pass --out", file=sys.stderr)
        return 2
    try:
        img, report, warnings, seams, boxes = compose(spec, base)
        for line in report:
            print(line)
        for w in warnings:
            print(f"WARNING: {w}")
        for out in outs:
            p = save(img, resolve(out, base), args.force)
            print(f"wrote {p}  {img.width}x{img.height}  {p.stat().st_size // 1024} KB")
        if args.preview:
            for p in write_preview(img, seams, boxes, resolve(args.preview, Path.cwd())):
                print(f"preview {p}")
    except SpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("Now look at the preview segments at full size before reporting the banner as done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
