# Layout spec format

`compose_banner.py` reads one JSON file. Source paths are relative to the spec file, so the
spec and its assets can move together.

```json
{
  "canvas":  { "width": 1920, "height": 384, "background": "#000000" },
  "feather": 50,
  "tiles":    [ { "src": "assets/a.jpg", "x": 0, "width": 700 } ],
  "overlays": [ { "src": "assets/logo.png", "x": 380, "y": 120, "width": 300 } ],
  "output":  ["banner-draft.png", "banner-draft.jpg"]
}
```

## canvas

| Field | Meaning |
|---|---|
| `width`, `height` | Banner size in pixels. Required. |
| `background` | Colour behind the tiles. It should never show; the script stops if tiles leave a gap. |

## feather

Default width, in pixels, of the fade on the left edge of every tile after the first.
40 to 60 suits a banner about 400 px tall. `0` gives hard cuts.

## tiles

Tiles are drawn left to right by `x`. Each one fills the full canvas height.

| Field | Meaning |
|---|---|
| `src` | Image file. Required. |
| `x` | Canvas x of the tile's left edge. Required. |
| `width` | Tile width on the canvas. Required. |
| `src_crop` | `[x, y, w, h]` in source pixels, applied first. Use it to take a region of a poster, or to cut away a border or a baked-in date. |
| `scale` | Scale factor applied to the (cropped) source. Default: the smallest scale that fills the slot. A value that would leave an empty band is an error. |
| `focus` | `[fx, fy]`, each 0 to 1: which part of the scaled image the slot shows. `[0.5, 0.5]` is centred, `[0, 0]` top-left. |
| `crop_x`, `crop_y` | Exact offset of the slot inside the scaled image, in scaled pixels. Overrides `focus` for that axis. |
| `feather` | Fade width for this tile only. |

How overlap works: a tile's fade covers `x` to `x + feather`, and the tile to its left must
extend at least that far. So for slots that should meet at canvas x = 700 with a 50 px fade,
end the left tile at 725 and start the right tile at 675.

Working out a crop: decide the scale, multiply the subject's position in the source by it,
then choose `crop_x` so the subject sits clear of the fade. Example: a face spans source
x 480 to 880, scale is 0.468, so it spans 225 to 412 after scaling. With `crop_x` 150 it
lands at 75 to 262 inside the tile, clear of a 50 px fade.

## overlays

Drawn after all tiles, in list order.

| Field | Meaning |
|---|---|
| `src` | Image with transparency. Required. An opaque image pastes as a rectangle, with a warning. |
| `x`, `y` | Canvas position of the top-left corner. Required. |
| `width` or `height` | Resize, keeping proportions. Default: native size. |
| `trim` | Trim transparent margins before sizing. Default `true`. |
| `opacity` | 0 to 1. Default 1. |
| `backing` | Solid fill under the logo's own shape. For cut-outs whose dark parts were lost. Fields: `color`, `close` (fill gaps up to this many px), `grow` (extend past the edge, px), `soften` (edge blur), `opacity`. |
| `shadow` | Soft shadow of the logo's shape. Fields: `color`, `blur`, `opacity`, `dx`, `dy`. |

Use `backing` sparingly: it makes a logo read heavier than the original. Prefer placing the
logo on a ground similar to the one it was designed on.

## output

One path or a list. The extension sets the format: `.png` for the master, `.jpg` (quality
92) for upload when the platform has a size limit. Existing files are not overwritten
without `--force`.

## Preview

`--preview DIR` writes `segment_01.png`, `segment_02.png` and so on, each at full
resolution and at most 1000 px wide, plus `guides.png`: cyan lines mark tile starts,
magenta lines mark where each fade ends, yellow boxes mark overlays.
