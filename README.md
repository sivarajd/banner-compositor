# banner-compositor

An agent skill for building wide banners and headers (subreddit, Discord, YouTube channel,
forum, wiki, fan site) by compositing real images and logos. Nothing is generated or
redrawn: photos are scaled and cropped, seams are feathered, and logos go on top exactly as
published.

It exists because image generators get two things wrong that a community banner must get
right: they re-letter title logos, and they redraw real people's faces.

## Install

Pick the one that matches how you use Claude. The scripts need Python 3.9 or later and
Pillow (`pip install pillow`) whichever way you install.

### Claude Code: as a plugin (recommended)

```bash
claude plugin marketplace add sivarajd/banner-compositor
claude plugin install banner-compositor@sivarajd-skills
```

On Claude Code 2.1.275 or later, one step also works:

```
/plugin install banner-compositor --marketplace sivarajd/banner-compositor
```

Update later with `claude plugin update banner-compositor@sivarajd-skills`.

### Claude Code: as a plain skill folder

```bash
# for every project on this machine
git clone https://github.com/sivarajd/banner-compositor.git ~/.claude/skills/banner-compositor

# or for one project only
git clone https://github.com/sivarajd/banner-compositor.git <project>/.claude/skills/banner-compositor
```

Start a new session after installing so the skill is picked up.

### Other agents: npx skills

```bash
npx skills add sivarajd/banner-compositor
```

This uses the open [`skills`](https://github.com/vercel-labs/skills) installer, which needs
Node.js. Not tested by the author for this repository; if it does not find the skill, use
the clone method above.

### Claude.ai and Claude Desktop: upload a ZIP

Download `banner-compositor.zip` from the latest
[release](https://github.com/sivarajd/banner-compositor/releases), then go to
Customize > Skills > "+" > Upload a skill. The ZIP must have the `banner-compositor`
folder at its top level, not `SKILL.md` loose at the root. Code execution has to be
enabled for scripts to run. To build the ZIP yourself, from the folder that contains
this repository's folder:

```bash
zip -r banner-compositor.zip banner-compositor -x 'banner-compositor/.git/*' \
    'banner-compositor/__pycache__/*' 'banner-compositor/*/__pycache__/*'
```

Uploaded skills do not sync between claude.ai, the API and Claude Code.

## Invoke

There are two ways.

**Ask in plain words.** The agent loads the skill by itself when a request matches its
description. For example:

- "Make a subreddit banner from the images in `./banner`. Three films, left to right:
  A, B, C. Use each film's own title logo."
- "Update our Discord server banner. Add the new season's poster next to the current two."
- "Write me an image-AI prompt for a channel banner with these three game logos." (The
  skill explains why generation is the wrong tool here and offers the composite.)
- "Cut the title logo out of this poster so I can use it on a banner."
- "New stills are in `banner-assets`. Rebuild the banner with them."

**Call it by name.** In Claude Code, type the skill name as a slash command, followed by
the request:

```
/banner-compositor 1072x128 desktop banner and 1080x128 mobile banner from ./assets, subjects A | B | C
```

The more of this you give, the fewer questions come back:

- the target size, as stated by the platform's upload dialog
- the subjects and their order
- where your images and logos are
- any community rules about edited images
- whether the agent may search the web for missing official images, and whether to use
  sub-agents for that

## What happens

1. **Brief.** The agent settles size, subjects and rules, and looks at every image you
   supplied.
2. **Missing assets.** If you allow it, the agent searches for official images and logos
   and records where each came from. It does not invent a logo that it cannot find.
3. **Logos.** It uses your transparent logo file if you have one. Otherwise it crops a
   poster so the title stays where the designer put it, or cuts the logo out of key art.
4. **Layout.** It writes a small JSON layout file and builds the banner from it.
5. **Check.** It inspects the result at full size and fixes what it sees.
6. **Hand-over.** It saves under a new file name and tells you what is in the banner, the
   weak spots, and how sure it is that each found image is official.

The agent does not upload anything. You do that.

## What you get

| File | Purpose |
|---|---|
| `<name>.png`, `<name>.jpg` | The banner. PNG is the master; JPEG is for upload limits. |
| `<name>.spec.json` | The layout. Keep it: changing one path and rebuilding updates the banner. |
| `SOURCES.md` | Where each image came from and whether it is confirmed official. |
| the assets folder | The images the layout uses. Keep it with the layout file. |

Your existing banner file is never overwritten.

## Update a banner later

Save the new images beside the old ones, then ask:

```
Rebuild the banner from now-next-banner.spec.json. Use the new stills for the third subject.
```

Or edit the layout file yourself and run the build script.

## Use the scripts without an agent

```bash
# look at many candidate images at once
python scripts/contact_sheet.py downloads/*.jpg --out sheet.jpg

# cut a logo out of key art and check it on light, grey and dark grounds
python scripts/cutout_logo.py poster.jpg logo.png --box 890,350,640,470 --key r-b \
    --test-sheet logo_test.png

# build the banner and write full-size segments for inspection
python scripts/compose_banner.py layout.json --preview preview/
```

Each script has `--help`. The layout file is documented in `references/spec-format.md`,
and `assets/example-spec.json` is a starting point.

## What is in here

| Path | Contents |
|---|---|
| `SKILL.md` | The workflow the agent follows. |
| `.claude-plugin/` | Plugin and marketplace manifests, so the repo installs with `claude plugin install`. |
| `scripts/compose_banner.py` | Builds a banner from a JSON layout. Stops on gaps, empty bands and missing files. |
| `scripts/cutout_logo.py` | Keys a logo out of key art, or defringes a transparent logo. |
| `scripts/contact_sheet.py` | Tiles candidate images into one labelled sheet. |
| `references/spec-format.md` | Every field of the layout file. |
| `references/asset-sourcing.md` | How to find official images, a brief for search sub-agents, the `SOURCES.md` format. |
| `references/platform-sizes.md` | Banner sizes by platform, with sources and the date checked. |
| `assets/example-spec.json` | A starting layout. |
| `tests/smoke_test.py` | Runs the three scripts on generated images. |

## Test

```bash
python tests/smoke_test.py
```

## Limits

- Layouts are a single horizontal row of full-height tiles. There are no grids or stacked
  rows.
- A logo cut out of key art loses detail that is close to the background colour. A
  supplied transparent logo is always better.
- Platform sizes change. Trust the platform's upload dialog over the table in
  `references/platform-sizes.md`.

## Rights

The images and logos you composite belong to their owners. This tool only arranges them.
Whether a given use is acceptable is for you to decide.

## Licence

MIT. See `LICENSE`.
