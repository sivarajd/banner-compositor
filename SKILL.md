---
name: banner-compositor
description: Build wide header and banner images (subreddit, Discord, YouTube channel, forum, wiki, fan site, event or team page) by compositing real photos, stills, posters and logos into one strip with soft seams, with logos and title wordmarks kept exactly as published. Use this skill whenever the user wants a banner, header, cover image or collage strip made or updated from existing images, wants several subjects (films, games, teams, products, releases) combined into one banner, asks for "a prompt for an image AI" to make such a banner, or needs a logo cut out of a poster for one. Also use it to rebuild an earlier banner when new images arrive. Not for charts, UI mock-ups, or artwork drawn from scratch.
compatibility: Python 3.9+ with Pillow (pip install pillow). No image-generation model needed. Web search and fetch tools are only needed when assets must be found online.
---

# Banner compositor

Build a banner by arranging real images side by side, blending the seams, and laying
logos on top. Nothing is redrawn: faces stay as photographed and titles stay as designed.

## Why composite and not generate

People often ask for an image-AI prompt for this job. Generation fails at exactly the two
things a community banner must get right:

- **Title wordmarks.** A generator re-letters a logo. It comes out close but wrong, and
  fans notice at once.
- **Real people.** A generator redraws faces. The result is a look-alike, which many
  communities ban as doctored content and which misrepresents the person.

So when asked for a generation prompt, say this in two or three sentences and offer the
composite. If the user still wants a generator involved, limit it to a background plate
with no text and no people, and put the real assets on top with this skill.

## Workflow

### 1. Pin down the brief

Settle these from the request and the files before asking anything:

- **Size.** Platforms change banner sizes, so use the freshest evidence you have, in this
  order: the size the user states from the platform's upload dialog; the platform's
  current help page; `references/platform-sizes.md` (dated, with sources); the pixel size
  of the existing banner, which may predate a change. Tell the user which size you used
  and where it came from. Some platforms take separate desktop and mobile banners: see
  "More than one size" below.
- **Subjects and order.** What goes in, left to right, and whether any subject should get
  more room.
- **Assets on hand.** List the folder. Open and look at every image yourself. A filename or
  caption does not tell you what a picture shows, how sharp it is, or what text is baked in.
- **House rules.** Community rules on edited images, and anything the user has said about
  tone. Read them if they are in the project.

Ask only what you cannot settle this way, such as a missing subject list.

### 2. Fill the gaps

For each subject you need a logo or wordmark and one or more images. If something is
missing, look for official material: the rights-holder's own posts and channels, press
kits, and news outlets that reproduce the official artwork. `references/asset-sourcing.md`
has the search tactics, a brief for delegating the search to sub-agents, and the format of
the sources file. Delegate when the user asks for sub-agents or your environment favours
it; otherwise search inline.

Three rules hold however you search:

- **Official only, and say how you know.** Fan edits and AI renders are everywhere. Record
  where each file came from. When "official" rests on a caption and not on the original
  post, say so in the final report.
- **Never invent an asset.** If no logo exists, the banner goes without one, or uses the
  poster crop described below. Do not design a stand-in.
- **Keep the user out of outbound requests.** No names, project names or email addresses in
  URLs, headers or search queries.

Save downloads in a working folder and view each one before trusting it.
`scripts/contact_sheet.py` puts many candidates on one sheet, which is quicker than opening
them one at a time.

### 3. Get the logos, most faithful way first

1. **A transparent logo file the user supplied.** Use it. If its edges show a coloured
   fringe on your background, run `cutout_logo.py --key alpha --defringe 2`.
2. **The poster with its title left in place.** Crop the poster so the title sits where
   the designer put it. Nothing is cut out, so the style is exact. This is the best route
   when the only source is small.
3. **A cut-out from key art.** Use `scripts/cutout_logo.py` to key the logo off its
   background. Pick the key by what separates logo from ground: a channel difference such
   as `r-b` for warm lettering on a cool ground, `luma` for light on dark, `inv-luma` for
   dark on light, `bg` for a flat background colour. Always pass `--test-sheet` and look at
   the result on light and dark grounds.

A cut-out is the least faithful route. Dark or shadowed parts of a logo vanish when they
are close to the background colour. Either place the logo on a ground like the one it came
from, or give it a `backing` in the layout spec (a filled silhouette plus a soft shadow),
and tell the user the logo is a cut-out.

Never re-letter, restyle, recolour or "clean up" a wordmark by redrawing it.

### 4. Lay it out in a spec file

Write the layout as JSON and build it with `scripts/compose_banner.py`. The spec is the
thing to keep: when better images turn up later, change one path and rebuild.
`references/spec-format.md` documents every field, and `assets/example-spec.json` is a
starting point.

The model is a row of **tiles** (photos, each scaled and cropped to a slot, each fading
into the one on its left) and then **overlays** (logos, drawn last so the fades cannot eat
them). Layout judgment that the script cannot make for you:

- **Keep faces clear of the fade.** The left `feather` pixels of every tile after the first
  are semi-transparent. A face there turns into a ghost over its neighbour. Move the crop
  or widen the slot.
- **Put a logo over a quiet area of its own subject's tile**: out-of-focus background, sky,
  a dark wall. Do not let it run into the next subject's tile.
- **Balance the subjects.** Similar logo widths and similar face sizes read as one banner.
  If one logo has to be much smaller, tell the user why.
- **Keep changeable facts out.** Crop away release dates, prices and "coming soon" lines
  baked into posters unless the user wants them. Banner text cannot be edited later.
- **Scale and crop only.** No retouching, face edits, or removing a watermark or credit. If
  the only copy carries a third party's watermark, find another copy or leave it out.
- **Mind the platform's furniture.** Many sites overlay an avatar or title on a corner and
  crop the sides on phones. Keep faces and logos out of those zones when you know them.

**More than one size.** When a platform wants several banners (desktop and mobile, or two
sites), write one spec per size and reuse the assets. Do not resize a finished banner to a
different shape: the crops and logo positions that work at one aspect ratio cut faces at
another. When the sizes differ only by a few pixels, copy the spec and adjust the last
tile.

**Very thin strips.** At around 8:1 (for example 1072x128) a face that fills the height is
only about 100 px wide, so there is room for more subjects but less of each. Crop tight on
faces, expect to use fewer images per subject than you would in a taller banner, and check
that each logo is still readable at that height. A stacked two-line wordmark or a tagline may be
too small to read; say so and let the user decide what to do about it.

### 5. Build, look, fix

```bash
python scripts/compose_banner.py layout.json --preview preview/
```

The script stops on problems it can prove: a missing file, a crop that would leave an empty
band, a gap between tiles, a fade wider than the overlap. It warns on softer ones, such as
heavy upscaling.

Then look at the result, and look at it at full size. A wide banner shrunk to fit a viewer
hides ghosted seams and broken logo edges. `--preview` writes full-resolution segments for
this, plus `guides.png` with the seams and overlay boxes drawn in. Check each segment for:

- faces cut by a seam or ghosted into a neighbour
- logo edges: holes, halos, fringes, anything unreadable at this size
- empty bands, stretched people, visible tile edges
- text you did not mean to include

Fix the spec and rebuild. Fix everything one look shows before looking again.

### 6. Save and report

- **Never overwrite the user's existing banner.** Write a new filename. The script refuses
  to overwrite unless given `--force`, which is for your own drafts only.
- Keep the spec, the assets it uses and a `SOURCES.md` together in a folder that will
  outlive the session. A temp folder loses the downloads, and then the banner cannot be
  rebuilt.
- Do not upload or publish. The user does that.

Report in this order: where the file is and its size; what is in it, left to right; the
weak spots (soft sources, cut-out logos, unreadable taglines, tiles that look pasted in);
and how sure you are that each found asset is official. Say plainly what you did not
check, for example how the site crops the banner on phones.

## Scripts

| Script | Use |
|---|---|
| `scripts/compose_banner.py` | Build the banner from a JSON spec; `--preview DIR` writes inspection segments and guides. |
| `scripts/cutout_logo.py` | Key a logo out of key art, or defringe an existing transparent logo; `--test-sheet` shows it on three grounds. |
| `scripts/contact_sheet.py` | Tile candidate images into one labelled sheet for a quick visual check. |

Run any of them with `--help` for the options.

## Rights and fair dealing

Stills, posters and logos belong to their owners. A fan or community banner that shows
official artwork unaltered is common practice, but the user decides whether their use is
acceptable, so mention it once when you source assets from the web. Do not build a banner
that would pass the page off as the rights-holder's own official account.
