# Door designs — format of the door catalogue

Doors of the app are built by a generator from data, not from fixed meshes: every catalogue model is a **design**
(a JSON file) drawn at a reference leaf size, and the generator builds the leaf for any size a house needs — stiles,
rails and profiles keep their real widths, panels and glass stretch. The catalogue itself (`catalog.json`) lists
series, models, finishes and glass the way the manufacturer's catalogue does (DveriMebel / el'PORTA / BRAVO, 2020).

Files (loaded at runtime from `Resources`):

- `Assets/House4696/Resources/Doors/catalog.json` — finishes, glass (shared by all series) and the first series.
- `Assets/House4696/Resources/Doors/Series/<series-id>.json` — more series, one per file (a `SeriesDef` object as in
  `catalog.json` → `series[]`, plus `"order"`: its place in the catalogue, the manufacturer's page number). Series of
  several authors never touch the same file.
- `Assets/House4696/Resources/Doors/Designs/<design-id>.json` — one design per file.
- `Assets/House4696/Resources/Doors/Finishes/<family>.json`, `…/Glass/<family>.json` — more finishes / glass, arrays of
  the same objects as in `catalog.json` (one file per texture family, so several authors never collide). Their library
  materials go into `External/external.json` through `tools/doors/textures/merge_entries.py`.

Tools: `tools/doors/` (catalogue photo index, measuring, 2D previews, finish textures) — see its README.

## Coordinates

Millimetres. The leaf is drawn **as the catalogue photo shows it**: seen from the front, origin at the bottom-left
corner of the leaf, x to the right, y up. In the catalogue the handle (lock side) is on the left and the hinges on
the right, so **x = 0 is the lock edge**. A door hinged on the other side is the mirror image; the back face is the
same construction seen from behind (pieces go through the leaf).

## Design file

```jsonc
{
  "id": "porta-22",              // design id: lowercase latin, kebab-case (file name without .json)
  "name": "Порта-22",            // as in the catalogue, without glass/finish suffixes
  "ref": [800, 2000],            // leaf size the coordinates are drawn at (catalogue renders show 800×2000)
  "thickness": 36,               // leaf thickness
  "fixX": [[0, 120], [680, 800]],// x intervals that keep their size when the leaf is wider/narrower (stiles)
  "fixY": [[0, 120], [1880, 2000]],// y intervals that keep their size when it is taller/shorter (rails)
  "edge": { "radius": 2 },       // leaf perimeter: rounded wrap ("бескромочная"); "material": "metal" = ALU edge
  "handle": { "y": 1000, "x": 60, "style": "square", "finish": "chrome" },
                                 // handle axis: height above the leaf bottom, distance from the lock edge;
                                 // style "square" (lever on a square rose, modern) | "round" (curved lever on a round
                                 // rose, classic); finish chrome | satin | gold | bronze | black;
                                 // "wcDrop": 90 = the WC thumb-turn's distance below the handle axis
  "hinges": [250, 1750],         // hinge centres above the leaf bottom (default: 250 from the bottom and the top)
  "layout": { … },               // construction of the leaf face (below)
  "parts": [ … ]                 // features on top of the layout (below)
}
```

### Resizing

A coordinate maps through `fixX` / `fixY`: fixed intervals keep their length (and move), the rest stretches
proportionally. Widths of separators, grooves, inlays, beads and mouldings never scale. A cell or part thinner than
60 mm along an axis keeps its size along it (only its centre moves) — glass strips stay 10 mm on any door.

### Layout (frame-and-panel construction)

The layout is a tree of rectangles (guillotine cuts). The root is the whole leaf. A node either splits into cells
or is a **piece** (a board of the leaf with its grain and face level).

```jsonc
{
  "split": "x",                  // "x": cut with vertical lines at x = at[i]; "y": horizontal lines at y = at[i]
  "at": [120, 680],              // absolute cut positions (ref mm, ascending): N cuts → N+1 cells
  "sep": "joint",                // separator at every cut, or an array with one entry per cut
  "cells": [ {}, { … }, {} ],    // N+1 children ({} = plain piece inheriting everything)
  "level": -3,                   // face level of the pieces below this node: 0 = full thickness,
                                 // -3 = each face 3 mm lower (a 30 mm board in a 36 mm leaf); inherited
  "grain": "v",                  // "v" vertical / "h" horizontal wood grain of the pieces below; inherited
  "radius": 1.5,                 // edge radius of the pieces below (the hairline of a joint); inherited
  "material": "finish",          // piece material role (see Materials); inherited
  "glass": true,                 // this cell is a glass pane (the door's glass) instead of a board;
                                 // or a glass role: "mirror", "black", "clear", "satin"…
  "pane": 8                      // thickness of the glass panes below (mm, inherited): 8 = triplex; the leaf's
                                 // thickness minus ~2 = glass flush with both faces (Глейс, PORTA-51 lacobel)
}
```

Separators (centred on the cut line; the width is visible size in mm):

| sep | meaning |
|---|---|
| `joint` | the pieces touch; their rounded edges show a hairline (and a step if the levels differ) |
| `none` | no seam: the cut only changes grain/level/material |
| `glass:10` | a 10 mm glass strip between the pieces (the door's glass) |
| `black:10`, `mirror:10`, `clear:10` | a strip of a fixed glass |
| `metal:4` / `metal:4:1` | a 4 mm aluminium strip, flush (or 1 mm proud) with the higher neighbour |
| `groove:6:3` | a milled groove 6 mm wide, 3 mm deep (flat bottom) |

### Parts (features on top of the layout)

Each part has `"type"` and a `"shape"` or `"path"`, optional `"face": "both"|"front"|"back"` (default both).
Shapes: `{"rect": [x0, y0, x1, y1], "r": 0}` · `{"ellipse": [cx, cy, rx, ry]}` ·
`{"arch": [x0, y0, x1, y1], "rise": 120}` (rectangle with a circular top rising by `rise` at the centre) ·
`{"path": "M 100 200 L … C … A … Z"}` (SVG path syntax, absolute or relative commands, y up).

| type | fields | wave |
|---|---|---|
| `glass` | `shape`, `bead` (`none`, `flat`, `round`, `classic`), `role` (glass role, default the door's glass), `pane` (glass thickness, mm, as in the layout), `facet` (mm: a bevelled border of clear glass that shows inside the bead, e.g. 20; `facetRole` another glass role for it), `bars` (glazing bars through the glass: `{"x": [...], "y": [...], "width": 20, "level": -2, "radius": 1.5, "material": "finish"}` — centre positions in ref mm, width kept on any leaf, clipped to the shape, faces `level` mm below the leaf face) | ① without bead, ③ bead/facet/bars |
| `groove` | `path` (open or closed), `width`, `depth`, `profile` (`v`, `u`, `flat`) | ② |
| `inlay` | `path`, `width`, `proud`, `material` (`metal`, `black`) | ② |
| `panel` | `shape`, `profile` (`raised`, `recessed` or `[[u, v], …]`), `width` (bevel), `depth`, `patina` | ③ |
| `molding` | `path`, `profile` (`flat-10`, `bead-8`, `baget-20`, `baget-30`, `cornice` or `[[u, v], …]`), `material`, `patina` | ③ |
| `piece` | `shape`, `level`, `grain`, `material` (a free-form board over the layout) | ③ |
| `decal` | `shape`, `image` (library material id, e.g. `doorglass_…` or `door_art_…`: a picture, transparent where empty, stretched over the shape's bounds), `level` (mm relative to the board face under it — lift it onto a panel field) | ③ |

`patina` paints part of a moulding's or a panel's profile (classic "G-27" gold lines): `"patina": "gold"` — a 3 mm line
along the profile's crest; `{"material": "gold", "from": u0, "to": u1}` — the profile between u0 and u1 (mm across the
path, the same u as the profile's points); `{"material": "silver", "width": 2}` — a crest line 2 mm wide.

### Materials (roles)

`finish` — the finish the house chose (catalogue colour); `finish2` — second finish of two-tone models (a two-tone
finish entry names it: `{"id": "f-27-f-01", "material": "door_f_27_wenge", "material2": "door_f_01_oak"}`; with a
single finish `finish2` = `finish`); `metal` —
matte aluminium; `chrome`; `black` — black glass/lacobel; `gold` / `silver` — patina paint; `bronze`; `black-matte` — matte black paint; `patina-dark` — dark stain in milled channels (toned profiles of veneer doors); glass roles `glass` (the door's glass), `satin`, `clear`,
`mirror`, `black`, `lacobel-beige` / `lacobel-white` / `lacobel-smoke` (WP / WW / S), and `art:<material id>` — a picture
from the material library (category `doorglass`, transparent where the glass is clear) stretched over the pane
(glass art that belongs to the design itself, e.g. the sprig of Глейс-1 SPRIG).

A glass may carry `"facet": 20` (mm, «Алмазная грань»): every shaped pane of the door's own glass gets that bevelled
border (glass id `mf-diamond`). A glass of `catalog.json` may name a library material instead of a role: `{"id": "wc", "role": "satin",
"material": "doorglass_wc"}` tiles its pattern (metres); `"fit": true` stretches the picture over every pane.

## catalog.json

```jsonc
{
  "finishes": [ { "id": "cappuccino-veralinga", "name": "Cappuccino Veralinga", "line": "ЭкоШпон",
                  "material": "door_cappuccino_veralinga", "color": "#c7bcae" } ],
  "glass": [ { "id": "mf", "name": "Белое сатинато Magic Fog", "role": "satin" } ],
  "series": [ {
    "id": "eco-porta-x", "name": "PORTA X", "line": "ЭкоШпон", "kind": "interior",
    "block": "t70",                                  // frame/casing system (below)
    "finishes": ["cappuccino-veralinga", "…"],        // colours of the series
    "glass": ["mf", "bs"],
    "models": [ { "id": "porta-22", "name": "Порта-22", "design": "porta-22", "glass": ["mf", "bs"],
                  "finishes": null /* = the series' */, "photo": "p021_porta-22-mf__grey-veralinga.jpg",
                  "block": null /* the model's own block, e.g. "classic" for a model with a cornice */,
                  "lock": null /* "wc" = bathroom thumb-turn */,
                  "leaves": null /* a ready-made double block ("2П-03") = 2 */,
                  "hinges": null /* the model's own hinge centres, mm (a block's kit hinges) */,
                  "astragal": null /* true: a double door gets «притворная планка» on the active leaf */,
                  "handles": null /* handle finish by door colour, e.g. {"real-oak": "bronze"}; also on the series */ } ]
  } ]
}
```

A model id is what a house document names (`"model": "porta-22"`); the same model may be sold in several series
(3D-Graf and ЭкоШпон PORTA X share designs) — the finish tells which.

### Door block systems (`block`)

| block | frame | casing | extension (добор) |
|---|---|---|---|
| `t70` | «Т» 70 × 22 mm, stop 32 mm, seal | «Т» 70 × 8 mm, rounded | «Т» 8 mm, fills the wall beyond 70 mm |
| `t70-2` | same | «Т» Тип-2 70 × 10 mm (flat band, cove, bead) | same |
| `t70-3` | same | «Т» Тип-3 75 × 8 mm (three flutes) | same |
| `classic` | same | fluted pilasters (Тип-3) on plinth blocks (цоколь), capitals, a frieze between them, a cornice (карниз) over the head | same |
| `classic-rosette` | same | the same with rosette blocks (розетка) instead of capitals | same |
| `classic-square` | same | the same with plain square corner blocks | same |
| `kit` | solid «Т» ЭКО pine 70 × 40 with a rebate — a ready-made block as sold ("1П-03", "2П-03") | none | none |

Door kinds are a property of the opening (`kind` in the house document), any interior model can be installed any way:
`swing` (1–2 leaves), `sliding` (coupe on a rail along the wall, 1–2 leaves), `folding` (book, 2 or 4 panels of
0.35 / 0.4 m), `portal` (lining and casings only). A series' `kind` ("interior", "sliding", "folding", "portal",
"entrance") says how the catalogue sells it: an opening without `kind` takes it when every series selling the model is
special (TWIGGY → sliding, Портал DIY → portal), and the series of the opening's kind wins when a model is in several
(TWIGGY sliding and folding; PORTA X swing and folding).

Wall opening from the leaf (catalogue, table 1): swing door +9…10 cm in width, +6…8 cm in height (the app uses
+9.5 / +7); book fold +9…10 / +9…10; sliding with framing 0 / +2…5; entrance steel door +2…4 / +2…4.

## Entrance (steel) doors

A series with `"kind": "entrance"` sells steel doors. A model names two designs: `"design"` — the **outer face** (the
street side: a powder-coated steel skin with embossing / mouldings, or a 16 mm MDF panel with film) and `"inner"` — the
**inner panel** (EcoShpon / laminate MDF, often with glass or a mirror). The series lists the outer finishes in
`"finishes"` (Антик Серебро, WINORIT П-4 …) and the inner ones in `"finishesIn"`; a model may narrow both
(`"finishes"`, `"finishesIn"`) and names its glass/mirror of the inner panel in `"glass"`.

```jsonc
{ "id": "porta-s-4-p22", "name": "PORTA S 4.П22", "design": "porta-s-4-outer", "inner": "porta-s-p22-inner",
  "finishes": ["almond-28"], "finishesIn": ["cappuccino-veralinga", "wenge-veralinga"], "glass": ["wp", "bs"],
  "photo": "p174_…jpg" }
```

- Size: the model's size is the whole steel block, 860 or 960 × 2050 mm (catalogue "205/86", "205/96"); the engine
  builds the steel frame (30 mm face, 90 mm deep, threshold 20 mm) and fits the leaf inside it (≈ 794 × 1997). Draw both
  designs at `"ref": [800, 2000]` as usual; `fixX`/`fixY` make them fit 86 and 96.
- `thickness` of a design = that panel's own thickness: a steel skin 2–4 mm (its embossing is `groove` / `inlay` /
  `panel` with small depths), an MDF panel 10–16 mm. The steel shell (50 mm) sits between the two panels.
- Coordinates: the **outer** design is drawn as the street-side photo shows it (x = 0 at the lock edge — where the
  handle is in that photo; if the handle is on the right, set `"lock": "right"`). The **inner** design is drawn as the
  inside photo shows it — seen from inside the hinges are on the other side, so inner panels usually need
  `"lock": "right"` (check the inside photo).
- Handles, lock escutcheons, a peephole (centred at 1.5 m) and barrel hinges are added by the engine; don't draw them.
  The outer design's `handle` sets their style (`"plate"` = a long plate with the lever and the cylinder, budget doors)
  and finish (`"copper"`, `"bronze"`, `"chrome"` …).
- Series / model fields of entrance doors: `"sizes": [[0.88, 2.05], [0.98, 2.05]]` (blocks sold, m; default 86/96 × 205),
  `"steel"` (finish id of the frame, the leaf box and the rim round the inner panel; default = the outer finish when it
  is powder-coated metal, else `moonstone`), `"frame": 70` (visible frame face outside, mm), `"rim": 45` (steel rim round
  the inner panel, mm), `"locks": 2` (1 = the lower cylinder only), `"escutcheon": "round" | "square" | "oval"`. `rim` may be negative: the inner panel then overlaps the frame (GROFF).
- Inside, the opening gets an extension and «Т» casings in the inner finish; outside the reveal stays plaster.
