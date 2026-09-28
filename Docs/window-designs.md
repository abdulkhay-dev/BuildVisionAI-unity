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
  "surround": { "width": 150, "depth": 40, "material": "sandstone_light", "head": 0 }
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

Cells are clipped to the frame's inside, so an arched or gable window just splits its bounding rectangle.

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
