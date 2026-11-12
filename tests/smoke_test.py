#!/usr/bin/env python3
"""Smoke test for the three scripts, using generated images only.

Usage: python tests/smoke_test.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True)


def main():
    failures = []

    def check(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            failures.append(name)
            print("     " + detail.strip()[-400:])

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for name, color in (("a.jpg", "#804020"), ("b.jpg", "#205080"), ("c.jpg", "#e8e0c0")):
            Image.new("RGB", (1200, 700), color).save(d / name)
        art = Image.new("RGB", (600, 300), "#102030")
        ImageDraw.Draw(art).rectangle((150, 100, 450, 200), fill="#ff8020")
        art.save(d / "art.png")

        r = run("cutout_logo.py", d / "art.png", d / "logo.png", "--key", "r-b", "--test-sheet", d / "sheet.png")
        logo_ok = r.returncode == 0 and (d / "logo.png").exists() and (d / "sheet.png").exists()
        check("cutout_logo keys an orange block off a blue ground", logo_ok, r.stderr + r.stdout)
        if logo_ok:
            w, h = Image.open(d / "logo.png").size
            check("cut-out is trimmed to the logo (about 300x100)", abs(w - 300) <= 6 and abs(h - 100) <= 6, f"{w}x{h}")

        r = run("cutout_logo.py", d / "art.png", d / "logo.png", "--key", "r-b")
        check("cutout_logo refuses to overwrite", r.returncode != 0, r.stdout)

        spec = {
            "canvas": {"width": 1200, "height": 300},
            "feather": 40,
            "tiles": [
                {"src": "a.jpg", "x": 0, "width": 420},
                {"src": "b.jpg", "x": 380, "width": 440},
                {"src": "c.jpg", "x": 780, "width": 420},
            ],
            "overlays": [{"src": "logo.png", "x": 100, "y": 100, "width": 200,
                          "backing": {"color": "#000000"}, "shadow": {"blur": 4}}],
            "output": "banner.png",
        }
        (d / "ok.json").write_text(json.dumps(spec))
        r = run("compose_banner.py", d / "ok.json", "--preview", d / "prev")
        ok = r.returncode == 0 and (d / "banner.png").exists()
        check("compose_banner builds a three-tile banner", ok, r.stderr + r.stdout)
        if ok:
            im = Image.open(d / "banner.png")
            check("banner has the canvas size", im.size == (1200, 300), str(im.size))
            check("overlay is drawn", im.getpixel((200, 150))[0] > 200, str(im.getpixel((200, 150))))
            check("no background shows at the seams", all(sum(im.getpixel((x, 150))) > 60 for x in (385, 400, 785, 800)))
            check("preview segments and guides are written", (d / "prev" / "segment_01.png").exists() and (d / "prev" / "guides.png").exists())

        r = run("compose_banner.py", d / "ok.json")
        check("compose_banner refuses to overwrite", r.returncode != 0 and "already exists" in r.stderr, r.stderr)

        def expect_error(name, mutate, needle):
            bad = json.loads(json.dumps(spec))
            mutate(bad)
            bad["output"] = f"{name}.png"
            (d / f"{name}.json").write_text(json.dumps(bad))
            r = run("compose_banner.py", d / f"{name}.json")
            check(f"compose_banner rejects {name.replace('_', ' ')}", r.returncode != 0 and needle in r.stderr, r.stderr + r.stdout)

        expect_error("a_gap_between_tiles", lambda s: s["tiles"][1].update(x=500), "gap")
        expect_error("a_fade_wider_than_the_overlap", lambda s: s["tiles"][1].update(x=410), "fade")
        expect_error("a_scale_that_leaves_an_empty_band", lambda s: s["tiles"][0].update(scale=0.2), "empty band")
        expect_error("tiles_that_stop_short", lambda s: s["tiles"].pop(), "empty")
        expect_error("a_missing_source", lambda s: s["tiles"][0].update(src="nope.jpg"), "not found")

        r = run("contact_sheet.py", d / "a.jpg", d / "b.jpg", d / "c.jpg", "--out", d / "contact.jpg")
        check("contact_sheet writes a sheet", r.returncode == 0 and (d / "contact.jpg").exists(), r.stderr)

    print(f"\n{'all checks passed' if not failures else str(len(failures)) + ' check(s) failed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
