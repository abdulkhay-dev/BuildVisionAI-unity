# Window designs — format of the window catalogue

Catalogue windows are data: `Assets/House4696/Resources/Windows/catalog.json` (frame finishes and models) and one design
per model in `Assets/House4696/Resources/Windows/Designs/<design id>.json`. The engine (`Runtime/Windows/WindowBuilder.cs`)
builds a design at the size of the wall opening it is placed in. A house uses a model with an opening
`{ "type": "window", "model": "w01", "finish": "white-pvc", "width": 1.4, "height": 1.4, "sill": 0.9 }`.

The source is `katalog_okon_48.pdf` — 48 AI-made concept pictures (perspective photos, no drawings, "proportions are
approximate"). "One to one" here means the same look: the same outline, divisions, sash layout, bars, profile widths and
proportions, colour, sills and surround, read from the picture as well as it can be.

## Coordinates

Millimetres at the design's reference size `ref: [width, height]`, **seen from outside**: x from the left edge to the right,
y up from the bottom edge. The reference size should be the window's natural size read from the picture (a 2-sash window
≈ 1400 × 1400, a panorama 3600 × 2600…). `fixX` / `fixY`: intervals that keep their length when the window is built at
another size (frame edges, mullions, a fanlight's height); the rest stretches. Profile widths never scale.

## Design file

```jsonc
{
  "id": "w01", "name": "Двустворчатая классика",
  "ref": [1400, 1400],
  "shape": null,                  // outer outline of the frame; null = the ref rectangle. {"arch": [x0,y0,x1,y1], "rise": 300}
                                  // (round top), {"ellipse": [cx,cy,rx,ry]}, {"path": "M 0 0 L 3000 0 L 3000 500 L 1500 1600 L 0 500 Z"}
                                  // (SVG path, y up: M L H V C Q A Z). The wall fills its rectangular hole round the outline.
  "fixX": [[0, 90], [650, 750], [1310, 1400]], "fixY": [[0, 90], [1310, 1400]],
  "frame": { "width": 70, "depth": 70, "inset": 120 },   // face width, depth in the wall, behind the facade's face (reveal)
  "sash":  { "width": 70, "depth": 76, "offset": 6, "overlap": 30 },  // opening sashes: face width, depth, set back from
                                  // the frame's face; sliding sashes overlap their neighbours by "overlap"
  "glass": "clear",               // clear | frosted | tinted | mirror
  "layout": { … },                // divisions (below)
  "sill": { "outside": "stone", "inside": "board", "overhang": 50, "thickness": 60, "ears": 60, "material": null },
                                  // outside: metal (отлив) | stone | none; inside: board (подоконник) | none
  "surround": { "width": 150, "depth": 40, "material": "door_enamel_whitey#e4d9c2", "head": 0 }
                                  // optional band round the window on the facade (stone architrave; "material": "frame" =
                                  // a portal in the window's own finish, e.g. a thick oak portal); head = extra lintel height
}
```

### Layout

A tree of rectangles over the inside of the frame (the frame's outline moved in by `frame.width`):

```jsonc
{ "split": "x", "at": [700], "mullion": 80,        // vertical mullions at x = at[i] (ref mm); "y": horizontal transoms
  "cells": [ { … }, { … } ] }                       // N cuts → N+1 cells; "mullion": width, or an array per cut; 0 = none
```

A cell (a leaf of the tree):

| field | meaning |
|---|---|
| `sash` | `fixed` (glass straight in the frame, default), `turn` / `tilt-turn` (side-hung sash, opens into the room), `tilt` (bottom-hung, stays shut), `slide` (sliding sash) |
| `hinge` | turn: hinge side **seen from outside** (`left` / `right`); slide: the way it slides (`left` / `right`) |
| `glass` | this cell's glass (overrides the design's) |
| `bars` | glazing bars: `{"cols": 2, "rows": 4, "width": 22}` (a regular grid over the glass) or `{"x": [..], "y": [..], "width": 25}` (ref positions) |
| `frosted` | height (mm) of a frosted band from the bottom of the glass (privacy) |

| `sash` (more) | `door` (a side-hung glazed door in a shopfront: lever at 1 m), `hung` (sash window: the lower sash slides up behind the upper one; stack two `hung` cells in a `y` split with `mullion: 0`), `panel` |
| `rails` | a sash's own rail widths when they differ: `{"bottom": 140, "top": 70, "side": 70}` (French windows, doors, sash windows) |
| `panel` | an opaque panel instead of glass: `"frame"` (the window's finish — spandrels, a shopfront's low panel), `"frosted"`, or a library material |
| `blinds` | `true`: venetian blinds inside the glass unit |

Cells are clipped to the frame's inside, so an arched or gable window just splits its bounding rectangle.

### How it is built (what you get for free)

Every edge is a real profile swept along the contours with mitred corners: rounded outer edges, rebates where sashes
sit, sloped glazing beads with black gaskets on the inside, a small lip outside, double glazing with its spacer bar.
Wood grain runs along each member and meets at the mitres. Turn sashes and doors get a lever handle inside (white on
light frames, satin aluminium otherwise), sliding sashes a pull. Glazing bars sit on both faces of the unit.

### Extras (design level)

```jsonc
"members": [ { "path": "M 0 2350 L 2400 2350", "width": 180, "depth": 25, "z": -260, "material": "metal_painted#b8bbbe",
               "count": 5, "stepY": 150 } ],
      // members swept along a path (ref mm): z = null → in the frame's depth (bars on the glass, diagrid, art-deco grid);
      // z = a number → their outer face that far from the facade (negative = in front: louvres, fins); repeated count ×
      // stepX / stepY; material "frame" or a library id
"awning": { "depth": 1000, "drop": 350, "height": 200, "stripe": 150, "valance": 180, "ears": 150, "colors": ["#efe9dc", "#4f6b56"] },
"shelf": { "depth": 320, "thickness": 40, "y": 0, "ears": 150, "material": "door_natur_oak", "brackets": true },
"fixings": { "size": 110 },         // stainless spider fittings at every cell corner (frameless / structural glazing)
"surround": { …, "bottom": false, "keystone": { "width": 160, "height": 220, "proud": 15 } }
```

A frameless look: `"frame": { "width": 0 }` (cells then reach the outline; use `fixings` or thin mullions).

## catalog.json

```jsonc
{ "finishes": [ { "id": "white-pvc", "name": "Белый (ПВХ)", "material": "door_enamel_whitey#f1f0eb", "color": "#f1f0eb" } ],
  "models": [ { "id": "w01", "number": 1, "name": "Двустворчатая классика", "section": "home", "style": "Классический",
                "note": "Две равные створки и спокойные пропорции. Спальня, кабинет.", "design": "w01",
                "finish": "white-pvc", "finishes": null, "size": [1.4, 1.4], "sillHeight": 0.9, "photo": "w01.jpg" } ] }
```

Finishes are library materials (tintable `name#rrggbb`): painted PVC / wood `door_enamel_whitey#…`, powder-coated
aluminium `metal_painted#…`, wood `door_organic_oak` (light oak), `door_natur_oak`, `door_f_17_chocolate` (dark walnut).
A model's `size` and `sillHeight` are the typical opening for the AI placing it; `finish` is the picture's colour.

## Tools

- `tools/windows/preview2d.py <design> [--size 1.4x1.4] [--finish "#rrggbb"] [--photo tools/windows/reference/w01.jpg]` —
  a 2D elevation from outside (needs numpy + Pillow), beside the catalogue picture. Mirrors the engine's layout rules.
- Unity: `House4696.Windows.WindowPreview.RenderDesign(designPath, finish, outPath, view, width, height, sill, open)` —
  views `front` (orthographic from outside), `inside`, `angle`; `open: true` opens the sashes.
- Reference pictures: `tools/windows/reference/wNN.jpg` (catalogue numbers).

## Known gaps (pilot, windows 1–12)

Things the pictures show that the format cannot say yet; the designs approximate them:

- **Rails of different widths** — a sash has one face width, so the tall bottom rail of French casements (w04) and sash
  windows is drawn like the other rails; likewise the frame has one width (no thicker bottom track, w09 / w12).
- **Vertically sliding (hung) sashes** — English sash windows (w06, w08) have no `sash` kind; w08 uses two `tilt` sashes
  (a sash profile that stays shut), w06 is drawn as a three-light casement.
- **A fixed pane with a sash profile** — in sliding systems the fixed panels have the same profile as the sliding ones;
  `fixed` puts the glass straight in the frame, so those panels have a slimmer border (w03, w12).
- **Surround** — always runs all the way round the outline (also under the sill); no keystone (w05), no plinth blocks.
- **Glazing bars** — one width per cell; no thicker meeting rail between the bar rows, no sash horns (w06, w08).
