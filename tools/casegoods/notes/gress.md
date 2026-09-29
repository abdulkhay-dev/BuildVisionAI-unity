# «Гресс» (gress, Пинскдрев П6.501) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF pages 98–104 (catalogue 192–205; p. 104 = all module cut-outs, sizes and
the swatch). Generator: `tools/casegoods/gen/gress.py` (`--check` also runs gen/check.py on every design and writes
`pilot/gress-*.png`, with the instruction's front view where there is one). It writes the 33 designs,
`gen/gress_catalog.json` and the completed cut lists `gen/cutlists/gress-*.json`. **All 33 check sheets print ok.**

| group | by instruction (24) | by catalogue / photo (9) |
|---|---|---|
| living | 0.02, 0.04, 0.05, 0.16, 0.17, 0.19, 0.20, 0.22, 0.25, 2.01 | — |
| bedroom | 1.10, 1.11, 1.12, 1.13-01, 1.14, 1.21, 1.26, 1.27 | 1.34 (as 1.21), 1.18 mirror, beds 1.09 / 1.28 / 1.29 / 1.30 / 1.31 |
| office | 2.15, 2.23-01 | 2.23 (the mirror image of 2.23-01, as the cut-out shows) |
| hall | 3.01, 3.02, 3.04, 3.05 | 3.06 mirror |

Skipped: nothing (the chair «Унисон М» on p. 99 is not a Гресс code).

## How the instructions were read

The Гресс instructions (IS-P6-501-*, cached in tools/casegoods/.cache/is/) list «номер, маркировка, наименование, кол.»
**without sizes**, and draw only a front / side / top view with the overall dimensions plus an exploded perspective
scheme. The PDFs are CAD exports drawn to scale, so the vector lines of the front and side views were read with
PyMuPDF (`page.get_drawings()`), scaled by the overall size (≈ 9–13 mm per pt; the line coordinates are quantised to
0.12 pt, i.e. **±1.5 mm**). That gives every visible edge: feet, bottom, top, strips and their joints, doors, drawer
fronts, handles, glass shelves, mirror insets, the fronts' plane (side views). Hidden parts (partitions, shelves behind
closed doors, backs, drawer boxes) come from the exploded scheme (which part where) and the construction below; their
sizes are consistent with the visible ones but are not measured — e.g. the fixed shelves behind the 630 wardrobe's door
were taken from 2.01, where they are visible. The completed cut lists carry the instruction's rows (numbers, names,
counts transcribed from the table pictures — most tables are vector outlines without a text layer) and the sizes of the
built parts; each file says so in "source".

## Construction (the same in every case piece)

- **Top and bottom** 25 mm (drawn 25–26), the full width and depth B. The bottom stands on grey plastic feet «Валмакс»
  20 high, 90 × 56, 11 mm in from the ends, 1 / 3 mm in from back / front (4 feet; 6 on 1400 / 1562 pieces).
- **Sides** ЛДСП 16 between top and bottom, from z 3 (the ДВП back 3 mm is **nailed** over the back edges — the
  instructions: «Прикрепите стенки задние из ДВП … гвоздями») to B − 23.
- **Fronts** 16 thick, lying over the sides' front edges; their face is 7 mm behind the top's edge (side views: B 390 →
  367 / 383 / 390; B 587 → 565 / 580 / 587).
- **«Накладка»** — the collection's look: an 80 mm strip over each side's front edge (1 mm in from the side's face),
  horizontally reeded («cross-grain»: grooves 3 mm every 10 mm, 1.5 deep, plain ends 8 mm — measured on the side-view
  profile). Tall pieces have two strips per side butted at mid height (joint drawn at 970 in the 1920 pieces).
  Doors hang on the strips with 180° hinges (the middle door of 3-door pieces on a partition, half-overlay hinges).
- **Drawers** run on roller runners 350 (500 in wardrobes, 250 in 3.02) screwed to small partitions behind the strips
  (the «Перегородка» rows); box: sides / back ЛДСП 16, ДВП bottom slid into the front's groove and nailed to the back.
  Identical drawers (one table row «(каждый)» × n) are built identical (equal openings, e.g. 1.12's partitions 4 / 5 /
  6 placed for three openings of 453.5).
- **Reeded drawer fronts** where the drawings hatch them (wardrobes 1.12 / 1.13-01 / 1.14 / 3.01, 630 cabinets, 0.02,
  0.05 bottom, 0.25 top, 1.26 bottom); plain elsewhere (0.17, 1.10, 1.11, 3.02 …), as drawn and as the photos show.
- **Backs** ДВП 3, split on fixed shelves or partitions; wide backs over a hanging section joined on a 50 × 16 batten
  («Брусок»); the chests' backs joined upright by an H profile (1.11: 870, 1.26: 1108, from the hardware lists).
- **Handles** «ручка-скоба» 128 c-c (drawn 128 long, 10 high, 29 mm out): bar d 136, band 10, t 8, standoff 21, square
  posts; hall pieces 3.04: С-25 96 (d 104). Door knob on the glass vitrine doors (drawn Ø ≈ 23).
- **Vitrines** 0.04 / 0.05: the door is bronze glass 4 mm the full height with two decor panels glued on (the handle is
  screwed through the glass with a bush — «втулка … крепление ручки к стеклу»); glass shelves on Sekura holders with a
  clip-on light («Светильник»). The engine tints glass only inside a glazed front, so the pane is a glazed front 5 mm
  thick with a 1 mm rim and the panels are fronts over it (11 mm).
- 1.13-01: the middle door carries a mirror 402 × 1583 (drawn inset), no handle.
- 3.02: two tilting shoe boxes (triangular sides as `shape: path`, two shoe rests, a bottom) as `flap` moves hinged at
  the bottom (25°), under a drawer. The table's row 12 «Стенка передняя» (not shown in the scheme) is built as the lower
  box's inner front.
- Tables: 0.16 and 0.22 stand on L-shaped legs of two boards (the four «Опора» rows × 2); 0.22 has two top halves on a
  slide mechanism with the 500 leaf 8 stored under them on the supports 9 (the leaf's depth 870, as fits between the
  aprons — a guess). 0.22's legs 115 × 129 are as drawn.
- Desks: pedestals like the chests; 2.15 has reeded strips also on the pedestals' back edges (the back view «15» × 4),
  so its pedestals start 19 mm in from the back; keyboard shelves are drawer moves.
- Beds (no instruction): 25 mm headboard as wide as B with reeded strips over its side edges and along its top (p. 101
  photo), the frame (side rails and footboard 25 × 400) round the sleeping place (+25 each side), so the headboard
  stands out 87 mm each side as the cut-out shows; metal base (black) at 230, mattress 200.

## Finishes and colours

- One colour option: `gress-sonoma` «Дуб Сонома 325» (site: «Дуб Сонома светлый») — body = every board,
  `door_enamel_whitey#caab92` from the p. 104 swatch (`catpage.py 104 --swatch 0.725,0.86,0.775,0.9`, flat ±8).
  Textured decor, provisional colour; listed in `gen/gress_decors.md`.
- Role `feet`: the grey plastic feet `door_enamel_whitey#8e8f90` (photo).
- `collection.metal`: `chrome#a9abad` — satin-aluminium handles (site photo shkaf_gress_p501_12.jpg).
- «Сантана» on p. 99 is the chairs' paint — not ours.

## Decisions where the sources disagree

- 3.05 hanger: catalogue p. 103 and index.json say H412, p. 104 says H1412, the instruction draws 1400 → built 1400
  (model size [900, 266, 1400], note).
- 0.25: the table gives shelf 7 × 1, the scheme labels a shelf 7 in both side sections → built 2, cut list corrected
  (note in gen/cutlists/gress-0-25.json).
- 1.11: the table numbers drawer 10's parts «9.2 … 9.5» (misprint) → 10.2 … 10.5.
- 2.15: the table skips 16–18 and numbers the drawer parts 21–25 → written 21.1–21.5.
- 0.17: parts 5 / 6 carry the codes of 3 / 4 (identical boards) — built as the scheme places them (niche partitions 3 /
  4, runner partitions 5 / 6); their sizes differ in the design (noted in the cut list).
- Reference cut lists parsed by cutlist.py mislabel the drawer rows (19–23 for 14.1–14.5) and miss rows: every
  instructed module has a completed list in gen/cutlists/.

## Engine / format limits for the lead

- Glass can't be tinted outside a glazed front (the vitrine doors are a 1-mm-rim glazed front under two decor
  panels). A `tint` on `kind: glass` parts would be simpler.
- preview2d draws bar handles as discs (and notes the handles standing 22–29 mm out of B, as expected).
- 2.15's back strips carry the reeds on their −z face (`face.side: "-"`) — please check in 3D.
- The tilting shoe boxes of 3.02 are flaps without the real pivot geometry (they tip 25° about the front's lower edge).
- Hooks of the hanger 3.05 are knobs (no hook model).
