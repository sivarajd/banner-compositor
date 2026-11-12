#!/usr/bin/env python3
"""Cut a logo or wordmark out of key art as a transparent PNG, or tidy the edges
of a logo that is already transparent. The lettering itself is never redrawn:
only the transparency is computed.

Choose --key by what separates the logo from its background:

    r-b, r-g, g-b, b-r, g-r, b-g   one colour channel minus another
                                   (r-b: warm lettering on a cool or neutral ground)
    luma       light lettering on a dark ground
    inv-luma   dark lettering on a light ground
    sat        colourful lettering on a grey, white or black ground
    bg         flat background of a known colour (--color), keep what differs from it
    alpha      the image already has transparency; use with --defringe

Usage:
    cutout_logo.py poster.jpg logo.png --box 890,350,640,470 --key r-b \
        --low 3 --high 14 --close 2 --test-sheet logo_test.png

Requires Pillow.
"""
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageColor, ImageFilter, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

CHANNEL_KEYS = {f"{a}-{b}" for a in "rgb" for b in "rgb" if a != b}
KEYS = sorted(CHANNEL_KEYS) + ["luma", "inv-luma", "sat", "bg", "alpha"]


def odd(n):
    return 2 * max(0, int(round(n))) + 1


def matte(im, key, color):
    """Greyscale image: bright where the logo is, dark where the background is."""
    rgb = im.convert("RGB")
    if key in CHANNEL_KEYS:
        ch = dict(zip("rgb", rgb.split()))
        a, b = key.split("-")
        return ImageChops.subtract(ch[a], ch[b])
    if key == "luma":
        return rgb.convert("L")
    if key == "inv-luma":
        return ImageOps.invert(rgb.convert("L"))
    if key == "sat":
        return rgb.convert("HSV").getchannel("S")
    if key == "bg":
        if not color:
            raise SystemExit("--key bg needs --color with the background colour, e.g. --color '#ffffff'")
        diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, ImageColor.getrgb(color)))
        r, g, b = diff.split()
        return ImageChops.lighter(ImageChops.lighter(r, g), b)
    if key == "alpha":
        if "A" not in im.getbands():
            raise SystemExit("--key alpha needs an image that already has transparency")
        return im.getchannel("A")
    raise SystemExit(f"unknown key {key}")


def levels(mask, low, high):
    lo, hi = 255 * low / 100.0, 255 * high / 100.0
    if hi <= lo:
        raise SystemExit("--high must be greater than --low")
    return mask.point(lambda v: 0 if v <= lo else 255 if v >= hi else round(255 * (v - lo) / (hi - lo)))


def test_sheet(logo, path):
    grounds = ["#f2efe6", "#808080", "#15191c"]
    pad = 24
    w, h = logo.width + 2 * pad, logo.height + 2 * pad
    sheet = Image.new("RGB", (w * len(grounds), h))
    for i, g in enumerate(grounds):
        cell = Image.new("RGBA", (w, h), g)
        cell.alpha_composite(logo, (pad, pad))
        sheet.paste(cell.convert("RGB"), (i * w, 0))
    if sheet.width > 1800:
        sheet = sheet.resize((1800, round(sheet.height * 1800 / sheet.width)), Image.Resampling.LANCZOS)
    sheet.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="key art, poster, or an existing transparent logo")
    ap.add_argument("out", help="output PNG")
    ap.add_argument("--box", help="x,y,w,h region of the source that holds the logo (default: whole image)")
    ap.add_argument("--key", choices=KEYS, required=True, help="how to tell logo from background")
    ap.add_argument("--color", help="background colour for --key bg, e.g. '#ffffff'")
    ap.add_argument("--low", type=float, default=5, help="matte value (percent) at or below which a pixel is transparent")
    ap.add_argument("--high", type=float, default=25, help="matte value (percent) at or above which a pixel is opaque")
    ap.add_argument("--close", type=float, default=0, help="fill pinholes up to about this many pixels")
    ap.add_argument("--defringe", type=float, default=0, help="shave this many pixels off the edge to drop colour fringes")
    ap.add_argument("--soften", type=float, default=0.6, help="edge blur radius in pixels")
    ap.add_argument("--upscale", type=float, default=1.0, help="enlarge the source first; smoother edges from small sources")
    ap.add_argument("--no-trim", action="store_true", help="keep the full box instead of trimming to the logo")
    ap.add_argument("--test-sheet", metavar="PNG", help="also write the logo on light, grey and dark grounds")
    ap.add_argument("--force", action="store_true", help="allow overwriting the output file")
    args = ap.parse_args(argv)

    out = Path(args.out).expanduser()
    if out.exists() and not args.force:
        sys.exit(f"{out} already exists; choose a new name or pass --force")
    im = Image.open(Path(args.src).expanduser())
    im = im.convert("RGBA" if "A" in im.getbands() or im.mode == "P" else "RGB")
    if args.box:
        try:
            x, y, w, h = (int(v) for v in args.box.split(","))
        except ValueError:
            sys.exit("--box takes four integers: x,y,w,h")
        if x < 0 or y < 0 or x + w > im.width or y + h > im.height:
            sys.exit(f"--box {args.box} is outside the {im.width}x{im.height} source")
        im = im.crop((x, y, x + w, y + h))
    if args.upscale != 1.0:
        im = im.resize((round(im.width * args.upscale), round(im.height * args.upscale)), Image.Resampling.LANCZOS)

    mask = matte(im, args.key, args.color)
    if args.key != "alpha":
        mask = levels(mask, args.low, args.high)
    if args.close > 0:
        mask = mask.filter(ImageFilter.MaxFilter(odd(args.close))).filter(ImageFilter.MinFilter(odd(args.close)))
    if args.defringe > 0:
        mask = mask.filter(ImageFilter.MinFilter(odd(args.defringe)))
    if args.soften > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(args.soften))

    logo = im.convert("RGB").convert("RGBA")
    logo.putalpha(mask)
    box = mask.point(lambda v: 255 if v > 8 else 0).getbbox()
    if box is None:
        sys.exit("nothing survived the key: the logo and background are not separated by this key; try another --key or wider --low/--high")
    if not args.no_trim:
        logo = logo.crop(box)
    out.parent.mkdir(parents=True, exist_ok=True)
    logo.save(out)

    hist = logo.getchannel("A").histogram()
    total = logo.width * logo.height
    opaque, partial = sum(hist[250:]) / total, sum(hist[9:250]) / total
    print(f"wrote {out}  {logo.width}x{logo.height}  opaque {opaque:.0%}  semi-transparent {partial:.0%}")
    if partial > 0.35:
        print("WARNING: much of the logo is semi-transparent; the key is weak. Try another --key or tighter --low/--high.")
    if opaque > 0.9 and args.key != "alpha":
        print("WARNING: almost the whole box is opaque; the background was not removed.")
    if args.test_sheet:
        test_sheet(logo, Path(args.test_sheet).expanduser())
        print(f"wrote {args.test_sheet}: look at it. Holes on the light ground mean dark parts of the logo were lost.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
