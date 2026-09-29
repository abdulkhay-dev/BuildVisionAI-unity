# «Турин» (turin, П7.036) — wave 3

Catalogue «Корпусная мебель ч. II» 2025, PDF pp. 57–63 (printed 110–123): living room p. 57 / 58 / 61, bedroom p. 59 /
61, kids' / study p. 60, the module cut-outs, the close-ups (p. 61 door and drawer in Дуб Каньон, p. 62 the handle) and
the two swatches on p. 62 / 63. Generator `tools/casegoods/gen/turin.py` (re-runnable: writes the 31 designs and
`gen/turin_catalog.json`), cut lists `gen/cutlists/turin-*.json`, decors `gen/turin_decors.md`, sheets
`pilot/turin-*.png` — all 31 print `ok` in `gen/check.py`.

## Modules

**By instruction (22)** — the instructions (a.pinskdrev.ru, all downloaded) have no usable text layer; every table was
transcribed from the page pictures into `gen/cutlists/turin-<id>.json` («№, наименование, A×B, кол.» — two sizes, the
thickness only marked «T=25» on 25-mm boards; the hardware in a separate `hardware` list, the drawing notes in
`drawing`): 0.10, 0.11, 0.12, 0.21, 0.24, 0.26, 0.52, 1.02, 1.16-01, 1.18, 1.19, 1.27, 1.28, 1.30, 1.31, 1.41, 1.57,
1.77-01, 2.14, 3.22, 3.92, 4.54.

**By catalogue (9)**: 0.23 Тумба 2д (the lower part of 0.10 under a 450 top, p. 62 cut-out), 0.70 Полка (a 25 board),
1.32 Комод 1500 (1.31 widened: sections 710, fronts 715; p. 59 photo, p. 63 cut-out), 2.51 Стол письменный (two
pedestals — drawer over door — under a 25 top, a modesty panel; p. 60 photo, p. 62 cut-out), 1.01 Кровать 2-16 (1.02 at
1662), 1.03 / 1.04 / 1.05 / 1.06 Кровати с мягким изголовьем (p. 59 / 61 photos, p. 63 cut-outs). By-catalogue designs
keep the numbers of their instructed model as labels (0.23 ← 0.10, 1.32 ← 1.31) or plain ids.

Front views: only 0.12 (p3), 0.10 / 0.11 (p1 thumbnails) and 0.21 have an orthographic front view; their sheets carry the
overlay (edges, fronts, handle holes sit on the drawing). The other instructions draw only exploded perspective views.

## Construction (common, from the tables)

- ЛДСП 16; the top («крышка») and the bottom («стенка горизонтальная нижняя») are 25 («T=25»), the full width L0 with a
  rounded front edge; the sides stand on the bottom and carry the top, 16 in from its ends: the inner width is L0 − 64 in
  every table (0.12, 0.21, 2.14: L0 − 62, sides 15 in). Heights check exactly: 70 plinth + 25 + sides + 25 (+ 40 crown)
  = 600, 1018, 1200, 2200 …
- Back ДВП 3 screwed onto the back edges (washers in the hardware), in panels jointed behind shelves / partitions as the
  back schemes (рис. Г / Д) show.
- Pilasters «… × 22» on the sides' front edges: 22 wide (flush with the side's inner face, 6 proud outside) × 20 deep.
  The fronts (20) sit between them in FRONT of the carcass, flush with the pilasters, gaps 2 (the door and drawer widths
  add up to the inner width exactly: 2 × 425 + 6 = 856, 2 × 487 + 6 = 980 …); partitions and fixed shelves stand behind
  their joints; the middle doors hang on half-overlay hinges K-9,5 on the partitions, the outer ones on K-16. The depths
  confirm it: side 426 + 20 = 446 = the top of 0.10 / 0.11; 580 + 20 = 600 = the wardrobes' top.
- Plinth box 70 (front / back L0 − 10 or − 12, ends 368 / 372 / 522 between them) under the bottom, its front flush with
  the sides' front edges, the front board cut into a flat arch with scrolls (0.21 front view, photos).
- Cornice (tall pieces): a crown 40 high overhanging ~43. Either one board «карниз 710 × 491 / 1431 × 491» (0.12, 0.11:
  a slab 16 / 12 with a rounded edge over a cove moulding `turin-cove-24`) or three crown strips «× 86 / × 80» (0.10,
  1.16-01, 1.18, 1.19, 1.77-01, 2.14, 3.92: moulding `turin-crown-40` / `-36` whose outer edge is the listed outline;
  its profile runs from v −24 so that its checker box reaches H).
- Fronts: face `frame` (border 22 / 20) with the profile `turin-ogee` (a rounded edge and a wide cove down to the panel —
  the raised-panel look of the 0.21 front view and the p. 61 / 62 close-ups); glazed doors: frame 75 + rebate 10 round
  clear glass; mirror doors (1.16-01, 1.77-01 centre): the same frame round a mirror.
- Drawers: the facade is the box's front wall («стенка передняя ящика»), sides / back ЛДСП 16, ДВП bottom under the
  box, «брусок продольный» under the wide boxes (1.19, 1.27, 1.30), 13 mm runner gaps.
- Handles: antique brass (p. 62): an ornate backplate 110 × 16 (`bar`, standoff 0.5) with an oval knob (`knob` 24) —
  vertical on doors (on the free edge, heights from the drawings), horizontal on drawers.
- «Брусок» rails: flat behind the drawer / door joint in 0.10 / 0.11 / 0.23 / 0.24 (the thick joint line of the drawings),
  on the bottom behind the fronts in 0.26, rear rails under the top in 0.21 and the chests, царги as rear rails.
- LED clips («клипса светодиодная», 0.10 / 0.11 / 0.12 / 0.21 / 0.26): a `light` on each glass shelf's front edge.

Particular modules: 0.52 — an equilateral top (side 800, corners cut: 778.34 × 692.82 as listed) on three walls along
the edges of a triangular shelf (side 542), the front wall a box, the two slanted walls mouldings (below); 4.54 — L legs
of two 725 × 100 × 25 boards round a 720 / 634 apron; 3.22 — a drop-down flap (K-16 at the bottom, oil stays) under a
front rail, an upholstered lid 670 × 460 (`soft`, 4 × 2 tufts); 3.92 — a wall panel with a hat board, a crown, three
hooks (knobs standing 55 off); 1.57 — a top on two sides with a small arch, a flat front rail, a 130 drawer with the
organiser (10 × 2, 11 × 3), the rear царга with a wavy edge; 1.02 — headboard 25 with the decorative frame 4 (a milled
frame front), rails 2008 between the head- and footboard (L = 25 + 2008 + 25 = 2058), the footboard with the arch, the
metal base 900 × 2000 on its own legs, a mattress.

## Decisions / sizes

- 0.10 / 0.11: two tops 25 + the 70 plinth leave 36 for the crown (not 40): built so (profile `turin-crown-36`, and a
  12 slab on 0.11's cornice board).
- 1.77-01: rows «Штанга L=476 × 2» are optional rails for the side bays; the p. 63 interior sketch shows shelves there —
  moved to `hardware` in its cut list. The centre doors are mirror doors as in the p. 63 cut-out (the table does not say
  «зеркало», -01 is the mirror variant).
- Inner layouts of the wardrobes (heights of hat shelves, царги, loose shelves) are not dimensioned: read from the
  exploded views and the p. 63 interior sketches (±50).
- Handle heights and sides follow the drawings (0.10, 0.11, 0.12, 0.21) and the cut-outs (hinge sides of 1.16-01,
  1.77-01: doors 1, 2 left, 3, 4 right).
- Soft-headboard beds: 2211 = headboard 25 + pad 150 + base 2000 + footboard 25 (+ clearance); the pad is a straight
  `soft` panel (the photos show it leaning).
- index.json sizes all agree with the catalogue text; every design has the catalogue size.

## Finishes

- `turin-sosna-karelia` «Сосна Карелия»: body = front #e6e7e1 (p. 62 swatch, flat) — decor, provisional.
- `turin-dub-kanyon` «Дуб Каньон»: #8a6b4e (p. 62 swatch; p. 63 #8b6c50) — decor, provisional.
- metal `gold#8c7446`: the antique brass handles (p. 62 close-up, a highlight-weighted sample of the knob, raw #745e3d).
  Glass clear; rails chrome; the soft pads the default fabric (the photos: ivory / beige leatherette).
- The «Молоко» / «слоновая кость» colours in index.json are the chairs' paint (Крашение), not case finishes.

## Engine / checker limits for the lead

- **Slanted boards (0.52):** `rot` about y is fine for the engine, but check.py/preview2d measure the turned bounding box
  (the cut-list size fails) and test overlaps by boxes (false overlaps with the shelf). The two slanted walls are
  therefore `moulding`s: a 16 × 450 rectangle (`turin-wall-450`) swept along the wall's line in the top plane, covering
  row 2. A rotated panel that the checker understands (size and overlap in its own frame) would be cleaner.
- **Crown mouldings and the extent:** the checker boxes a top-plane moulding as its path × 16 in y, so the crown profile
  starts at v −24 with z = H − 16 to make the extent reach H (the geometry is the same).
- **Glazed fronts** have a flat frame; the ogee round the glass (the drawings show it) is lost. A `profile` on
  `glass` fronts (like on `face.frame`) would match the panel doors.
- **The cornice board + cove**: the listed «карниз» board is a slab; the cove under it is a separate moulding.
- **Pilasters** are plain boards; the photos show a slight bead on them — not modelled.
- **Handles:** the ornate backplate is a flat `bar` (standoff 0.5, t 2); an ornament outline (`shape: path` for
  handles) would be closer. preview2d draws bars as discs.
- preview2d draws `shape: path` parts (plinth arches, the footboards, the triangular table) as boxes and mouldings as
  bands; the engine uses the outlines.

## Skipped

Nothing. No chairs are Турин articles (the chairs on the photos are other collections).
