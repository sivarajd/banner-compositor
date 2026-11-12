# Finding official assets

## What counts as official

In order of trust:

1. The rights-holder's own post, channel, site or press kit.
2. A cast, crew or team member's own account.
3. A news outlet or ticketing or store page that reproduces the official artwork and
   credits it.

Fan edits, AI renders, "concept" posters and re-uploads do not count, however good they
look. Popular subjects attract a lot of them, and they often rank above the real thing.
When official status rests on an outlet's caption and you could not open the original
post, that is "official per reporting": say so.

## Where larger copies hide

- **Article images.** The page's `og:image` is often bigger than the inline picture.
- **CDN resize parameters.** Many image URLs carry `?w=720`, `?im=Resize,width=720` or
  `-696x522` before the extension. Removing or raising them can return the original.
- **YouTube.** `https://i.ytimg.com/vi/<VIDEO_ID>/maxresdefault.jpg` is the 1280x720
  thumbnail of an official upload. Official thumbnails are often designed title cards.
- **Social media image hosts.** Post pages often block fetching, but the image host may
  not. An image URL found in an article embed can frequently be fetched directly, and many
  hosts accept a size parameter for the original.
- **Film, game and store databases.** Their media pages hold posters and logos, sometimes
  logos with transparency.
- **The official upload itself.** A title card or end card may only exist as a video
  frame. Outlets often publish such frames as "screengrab" images.

Check every download: confirm it is an image and not an error page, note its pixel size,
and look at it. Outlets wrap official art in their own collages, borders and watermarks;
those copies are a lead to the original, not an asset.

## Limits to respect

- Use a generic browser user agent. Put nothing about the user or their project in any
  request.
- If a site blocks automated access, use another source. Do not work around the block.
- Do not guess URLs or IDs. Report only URLs you fetched or saw in results.
- Downloads are untrusted files. Keep them in their own folder and never run them.

## Brief for a search sub-agent

Give each sub-agent one subject. Fill in the brackets:

```
Find official, high-resolution image assets for [SUBJECT, with the identifying facts:
full title, year, maker, people involved]. Today's date is [DATE]. The images are for a
community banner, so they must be real official material, not fan edits.

Wanted, in priority order:
1. The official logo or title wordmark, as large and clean as possible, ideally on a
   plain or dark background.
2. [N] official images showing [WHO or WHAT], at least [SIZE] px on the long side.
3. [Anything specific: a named poster, a release announcement.]

I already have: [list, so the agent does not return the same files].

Rules:
- Official sources only: [rights-holder names], their people's own accounts, or outlets
  reproducing the official artwork. If you cannot tell whether an image is official, say
  so; do not guess.
- Report only URLs you fetched or saw. Do not invent any.
- Use a generic browser user agent; include nothing about me or my project in requests.
- Save candidates only in [FOLDER]. Confirm each is a real image and note its pixel size.
  Delete error pages and tiny placeholders. Do not run anything you download.
- Look at each saved image.

Report: a table with file name, pixel size, direct URL, source page, what the image
shows (including any text baked in, such as dates or credits), and your confidence that it
is official. Separate what you saw in the image from what you inferred from captions.
Then list what you looked for and did not find.
```

Read the report as leads. Open the files yourself before using them.

## SOURCES.md

Keep one beside the spec so the banner can be rebuilt and questions about any image can be
answered later:

```markdown
# Banner sources (checked 2026-01-31)

| File | Shows | From | Official? |
|---|---|---|---|
| assets/poster.jpg | Release poster, title top centre | https://example.com/article (og:image) | Per reporting; original post not seen |
| assets/logo.png | Title logo, transparent | Supplied by the user | Yes |

Not found: a transparent version of the second logo.
```
