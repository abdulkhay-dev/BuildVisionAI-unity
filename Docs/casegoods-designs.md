# Case furniture designs — format of the casegoods catalogue

Catalogue case furniture (корпусная мебель) is data: `Assets/House4696/Resources/Casegoods/catalog.json` (finishes, moulding
profiles, collections, models) and one design per model in `Assets/House4696/Resources/Casegoods/Designs/<id>.json`. The
engine (`Runtime/Casegoods/CaseBuilder.cs`) builds a design as an item of the house: `{ "model": "flora-0-01",
"params": { "finish": "flora-samshit" } }` (`"open": true` builds the doors and drawers open). Every model of the catalogue is
an item of the furniture library automatically (ids starting with `_` are test pieces: they build but are not listed).

The source is a manufacturer's catalogue — the first one is **Pinskdrev «Корпусная мебель, часть II», 2025**
(`tools/casegoods/reference/catalog_km2.pdf`) — plus, for every module, the manufacturer's **assembly instruction**
(`IS-*.pdf`, «Инструкция по сборке»): its first pages carry the **cut list** (every panel with its three sizes and count)
and a front / back view with the part numbers. "One to one" here means literally: **a design is the list of the module's
real parts at their real positions**, and the checker proves the list against the cut list.

## Coordinates

Millimetres. Seen from the **front**: `x` from the left to the right, `y` up from the **floor** (legs included), `z` from the
**back** (the wall) to the front. The design's extent must equal the catalogue size `[L, B, H]` (L along x — legs that stand
out count, B along z — mouldings and handles inside it, H along y). The engine puts the item's origin at the middle of the
back at floor level (wall pieces — `"mount": "wall"` in the model — at their middle).

## Design file

```jsonc
{
  "id": "flora-0-01",
  "size": [611, 418, 2012],
  "parts": [ { … }, … ],       // every part of the cut list, hardware that shows, mouldings
  "moves": [ { … }, … ]        // doors, drawers, flaps, sliding doors: groups of parts that move
}
```

### Parts

Every part has a `kind` (default `panel`), a `box` `[x0, y0, z0, x1, y1, z1]` (mm) for most kinds, and:

| field | meaning |
|---|---|
| `n` | the part's number in the cut list ("1", "6.2", "14.1"); several parts with one number (shelves, drawer sides) each get an `id` |
| `id` | unique id inside the design (default = `n`); moves name parts by id |
| `covers` | cut-list numbers (or hardware letters) this part stands for without its own box: a moulding frame covers its four strips `["8", "8", "9", "9"]`, a glazed front covers its glass `["14.1"]`, legs `["g"]`, a handle `["k1"]` |
| `mat` | material role (below); default by kind |
| `edge` | rounding of the edges, mm (panel 1, front 1.5, back 0.3) |
| `grain` | `x` / `y` / `z`: the direction a wood decor runs on this part (default: its longest side) |
| `rot` | a turned part: `{"axis": "x", "deg": -8, "about": [x, y, z]}` — deg > 0 about x turns y towards z (a headboard's top forward; −8 leans it back), about y turns z towards x, about z turns x towards y; `about` defaults to the box's centre. The box is the part before the turn |
| `shape` | `rect` (default; `radius` rounds its corners) · `circle` / `ring` (an ellipse in the box, cut through its thinnest axis; `inner` = the ring's hole diameter) · `path` with `outline`: an SVG path (`M L H V C Q A Z`, absolute mm) in the plane across the box's thinnest axis — front plane (x, y), top plane (x, z) or side plane (z, y); clipped to the box |

Kinds:

| kind | what | notes |
|---|---|---|
| `panel` | chipboard (ЛДСП) panel, edge-banded | `mat` default `body` |
| `back` | hardboard (ХДФ 3.5), drawer bottoms | sits in grooves: up to 10 mm inside the panels round it is right |
| `front` | door / drawer front (МДФ / ЛДСП) | `mat` default `front`; `glass`, `face`, `print` (below) |
| `glass` | glass shelf / panel | transparent, no shadows |
| `mirror` | mirror | |
| `moulding` | a profile swept along a path | `profile`, `path`, `closed`, `z`, `plane`, `side` (below) |
| `tube` | round bar along the box's longest axis, as thick as its smaller side | legs, hanger rails; `mat` default `metal` |
| `rod` | bar between two points | `from` / `to` `[x, y, z]`, `d` (diameter at `from`), `d2` (at `to`: taper), `section` `round`/`square` — splayed and tapered legs, hairpins, metal frames, X-bases. Without a `box` a rod is left out of the checker's extent and size checks (a leg's cut-list size is its blank); give it `box` when it should count |
| `handle` | handle on a front face | `model`, `at` `[x, y]`, `z` (the face it stands on), `dir`, `d`, `band`, `t`, `standoff` (below) |
| `soft` | upholstered panel | `box`; `channels` N (vertical channels) or `tufts` `[columns, rows]` (buttoned); `mat` default `fabric` |
| `light` | LED puck / strip | glows; `shape: circle` for a puck |
| `mattress` | a mattress on a bed (not in the cut list) | |

#### Fronts

* `"glass": { "frame": 50, "rebate": 10, "t": 4, "tint": "clear", "barsX": [..], "barsY": [..], "barW": 18 }` — a glazed
  front: a milled frame `frame` mm wide round the glass, which hides `rebate` mm under it (the visible opening is
  `frame + rebate` from the edge). `tint`: clear, satin (frosted), bronze, grey, black, mirror. `barsX` / `barsY`: glazing
  bars at these x / y (absolute mm).
* `"face": { "type": … }` — the front's face (the +z face of a front; of any board, the face towards its thinnest axis'
  positive side):
  * `fluted` — ribs along `dir` (`y` vertical, `x` horizontal) every `pitch` mm, `depth` deep, `flute` `reed` (convex) or
    `groove` (concave), `gap` flat between ribs, `margin`.
  * `frame` — a milled frame `border` mm wide round a panel sunk `depth` mm, its milled edge rounded `r`; `profile` (a
    catalogue profile) runs round the panel (a classic bead).
  * `grooves` — milled lines `lines: [[a0, b0, a1, b1], …]` (absolute mm in the face plane), `w` wide, `depth` deep, `flute`
    `v` or `u` — pull grooves, fake joints, patterns.
  * `diamond` — pyramids `cell: [w, h]`, `depth` high, inside `margin` (3D relief fronts).
  * `"side": "-"` puts the face on the board's other side (−x of a left side panel, the back of a free-standing piece).
  * fluted `"area": [a0, b0, a1, b1]` — ribs on that part of the face only, standing on the flat face (applied reeds).
* `"print": "<library material>"` — a picture over the whole face (kids' fronts).
* Cut-outs (a handle notch): give the front a `shape: path` outline.

#### Mouldings

```jsonc
{ "kind": "moulding", "profile": "flora-41", "closed": true, "z": 402,
  "path": [[12.5, 568], [598.5, 568], [598.5, 2012], [12.5, 2012]], "covers": ["8", "8", "9", "9"] }
```

* `profile` — an id of `catalog.json` `profiles`: points `[u, v]` mm, **u across from the path (0 = the path, the outer
  edge) into the moulding, v up from the surface it lies on**, drawn from the outer edge (u = 0) over the top to the inner
  edge; the section closes along its back by itself. Negative u = outwards (a cornice that overhangs).
* `path` — the moulding's outer edge in the plane `plane` (`front`: x, y at `z` = the face it lies on; `top`: x, z at
  `z` = the height y; `left` / `right`: sides). `closed: true` = a frame with mitred corners; its profile lies inside the
  ring. Open paths: `side: 1` = the profile lies to the left of travel, `-1` = to the right; their ends are capped.

#### Handles

`model`: `edge` — an L profile over a front's top edge (`at` = [middle, the top edge y], `d` length, `band` the leg on the
face, `t` metal thickness, `standoff` the lip's depth = front thickness + t) · `ring-half` — a flat half ring (Flora): `at` = the middle of its cut line, `dir` = where its arc bulges (`up`, `down`,
`left`, `right`); two halves on two fronts make a ring across their joint · `knob` · `bar` (`dir` = its direction, `d` =
length, `band` = thickness; `post` = post size, `section: "square"` = square posts). Sizes: `d` outer diameter / length,
`band`, `t` thickness, `standoff` from the face; `z` = the front's face; `"on": "back"` = on a back face (z = that face,
the handle stands out towards −z: a table's back drawer).

### Material roles (`mat`)

`body` (carcass decor), `front` (fronts, mouldings), `back`, `metal` (the collection's handles and legs), `gold`, `chrome`,
`black`, `white`, `glass`, `mirror`, `led`, `fabric`, `bedding`, `gloss#rrggbb` (high gloss lacquer), `<decor>@gloss` (a
decor under high gloss lacquer, e.g. a finish role `"body": "birch_flame@gloss"`), any other role the
finish defines (`top`, `accent`, `frame` … in the finish's `roles`), or a library material name (`"door_enamel_whitey#c9a877"`).

### Moves

```jsonc
{ "type": "door",   "name": "door", "parts": ["14", "k1-door"], "hinge": "left", "angle": 105 },   // [axis: [x, z]]
{ "type": "drawer", "name": "drawer_top", "parts": ["6", "6.2-1", "6.3-1", "6.4-1", "6.5-1", "k1-top"], "travel": 300 },
{ "type": "flap",   "name": "flap", "parts": ["10"], "hinge": "bottom", "angle": 90 },            // [axis: [y, z]]; top = lifts up
{ "type": "slide",  "name": "coupe", "parts": ["20", "21"], "by": [-600, 0, 0] }                  // sliding / coupe door
```

The hinge line defaults to the front outer edge of the biggest front on the hinge side. Every part of a door or drawer
(front, drawer box, handle) is listed. A click on a door in the app opens it.

## catalog.json

```jsonc
{
  "finishes": [
    { "id": "flora-samshit", "name": "Зелёный самшит 682 PO", "body": "door_enamel_whitey#709183", "swatch": "#6d877c" },
    { "id": "monaco-grey-oak", "name": "Серый мокко / Дуб саттер 369 SWA", "body": "<oak decor>", "front": "door_enamel_whitey#8a8580",
      "roles": { "handle": "<oak decor>" } }
  ],
  "profiles": { "flora-41": { "name": "…", "pts": [[0, 0], [0, 16], [41, 5], [41, 0]] } },
  "collections": [ { "id": "flora", "name": "Флора", "brand": "Пинскдрев", "finishes": ["flora-samshit", "flora-pepel"], "metal": "gold#cdbf98" } ],
  "models": [
    { "id": "flora-0-01", "code": "П6.980.0.01", "name": "Шкаф «Флора» с витриной", "collection": "flora", "category": "storage",
      "size": [611, 418, 2012], "is": "IS-P6-980-0-01-SHkaf.pdf", "page": 13, "note": "с подсветкой" }
  ]
}
```

* A finish maps roles to library materials: `body` (carcass), `front` (default = body), `back` (default = body), more in
  `roles`. Plain colours: `door_enamel_whitey#rrggbb` (a smooth painted / uni surface) — albedo read from the catalogue's
  colour swatch. Wood and stone decors are texture materials of the library (see "Decor textures").
* `collection.metal` — handles and legs: `gold#rrggbb`, `chrome`, `black`, `brass`.
* Model ids: `<collection>-<last two groups of the code>` (`П6.980.0.01` → `flora-0-01`); `category`: storage, bedroom,
  living, tables, decor (mirrors), kids, hall, office. `is` = the instruction file in
  `tools/casegoods/reference/<collection>/is/`.

## Workflow and checks

1. The cut list: `python3 tools/casegoods/cutlist.py <IS pdf> --png /tmp/page` prints the table (some rows with broken text
   in the PDF are missed — read them from the page image) and renders the page with the front / back views.
2. Write the design: carcass panels first (who stands on whom: tops and bottoms usually span the sides; the sides stand
   between them), backs in grooves ~6 mm from the back edge, then partitions, shelves, cleats (hinge strips 25 mm), spacers
   (drawer runners), fronts with 2–3 mm gaps, drawer boxes (13 mm runner gap each side), mouldings, legs, handles. Numbers
   come from the cut list; positions from the drawings (their scale: the known overall size over its pixels).
   Scripts may generate designs (`tools/casegoods/gen/`), the file stays one part per line.
3. `python3 tools/casegoods/preview2d.py <design> [--ref <front view png> --ref-box x0,y0,x1,y1] --out <png>` checks:
   every cut-list row built as often as listed with its sizes (±1 mm), the extent = the catalogue size, no two solid parts
   overlapping (except backs in grooves) — and draws front / side / top views and our edges in red over the instruction's
   front view. It must say `ok`.
4. In Unity: `House4696.CasegoodsEditor.CasePreview.Render(model, finish, png, "front" | "angle" | "side" | "top", open)`
   renders the model in the calibrated studio (a face square to the camera shows its albedo).

Engine limits: faces work on the +W face of a board; mouldings don't carry a second material (patina lines: a thin
moulding of their own); chairs, stools and soft furniture are a separate (Blender) track.
