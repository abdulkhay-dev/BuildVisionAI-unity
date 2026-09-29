# «Монако» (monako) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF pages 34–42 (printed 64–81). Cut-outs: p. 41 (living, desks, tables) and
p. 42 (bedroom, hall); colour swatches p. 41 / 42; close-ups p. 39 / 40. Generator: `tools/casegoods/gen/monako.py`
(writes all 37 designs and `gen/monako_catalog.json`). Every design prints `ok` in `gen/check.py`; the sheets are
`pilot/monako-*.png` (instructed ones overlaid on the instruction's front view).

The instruction PDFs were available locally (`tools/casegoods/.cache/is/`) and most of them are **vector CAD exports**:
where a table lists names only (bedroom, desks, table, bed), every size was read off the drawing's vector geometry with
PyMuPDF (coordinates are quantised to ~0.12 pt ≈ ±1 mm at these scales), not by eye. The crescent outlines are the
drawings' own polylines.

## Modules (37)

| by instruction (19) | by catalogue / photo (18) |
|---|---|
| 0.01, 0.01-01, 0.02, 0.03, 0.05, 0.06, 0.08, 0.09, 1.01-01, 1.05 (bed 2-16), 1.06, 1.08, 1.09, 1.09-01, 1.10, 1.12, 2.14, 2.15, 2.15-01 — plus 0.01-01 / 1.09 / 2.15-01 are the mirrors the instructions name | 0.04 coffee table, 0.07 shelf 1704 (= 0.08 longer), 1.03 and 3.05 mirrors, 1.04 / 1.04-01 bedside, 1.07-01 3д wardrobe, 1.11 / 1.22 / 1.23 / 1.24 beds (construction of the 1.05 instruction), 1.15 шкаф-купе, 3.01 hall wardrobe (construction of 1.08), 3.02 / 3.03 hall тумбы, 3.04 вешалка, 3.08 / 3.09 shoe cabinets |

**Wrong PDFs on the site (index.json):** 1.04 links the bed 1.05 instruction (P6-528-1-05: Спинка / Царга / Накладка) —
used for the bed, the bedside is by catalogue; 3.01 / 3.02 / 3.03 link the instructions of 0.01 / 0.02 / 0.03 (their
tables say «Шкаф П6.528.0.01», «Тумба ТВ П6.528.0.02», «Тумба П6.528.0.03») — these three are by catalogue and their
models have no `is`.

## Construction (collection-wide)

- **Oak frame, 25 mm**: sides 25 standing on ФБ 482 glides (5 mm), the top 25 over them (living: sides 420 deep, top 421 =
  catalogue B; bedroom 605 / 605; the top overhangs the sides by ~2 mm at the ends where the drawing shows it). Plinths
  56 × 16 front and back between the sides, the bottom 16 on them (y 61–77). Inner panels 16.
- **Fronts sit 27 mm deep inside the frame** (face at D − 27, fronts 19.5, 16.5 on 0.03's push drawer): the carcass' fixed
  panels are 370 deep from the back (z 3–373 in the living room, 555 in the bedroom), the front rails / plinth fronts 16
  stand in the same front plane, and the partitions behind a front rail are 16 shallower (354 = 370 − 16 — this is why
  the cut lists have 354-deep partitions and shelves). The backs (ХДФ 3) are nailed on the rear and joined on fixed
  panels; the cut-list sizes prove the joints (e.g. 0.01: 608 + 1222 on shelf 5; 0.03: three vertical strips joined on
  the partitions). The backs are modelled inside the carcass' rear 3 mm (catalogue B is the top).
- **The crescent handle**: a circular-arc cut, ~40 mm deep, in a front's top edge. Living room: it shows the oak front rail
  70 × 16 behind it (0.01 rail 8, 0.02 rails 10 / 11, 0.03 rail 11 …). Bedroom / hall doors are two parts (upper 1334,
  lower 715) screwed to the oak «накладка» (Схема 2 of the instructions) that shows in the crescent; bedroom commode /
  desk drawers again show a front rail. Mirror-door pairs (1.01-01, 1.07-01) have the middle lower parts 41 mm shorter
  (flat bottom of the crescent), exactly as drawn.
- **V-grooves** every ~300–350 mm on the gloss fronts (drawn as 5–10 mm wide lines): `face: grooves`, w 8, depth 3, v.
  Heights from the drawings (living doors 364 / 970 / 1270 / 1570; bedroom 418 / 1109 / 1444 / 1779).
- Glass shelves 6 mm on holders; the glazed doors (0.01, 0.05) are a door with a window notch open to the free edge
  (`shape: path`) and the glass 950 × 446 × 4 behind it (moves with the door).
- Drawers: 16 mm boxes, ХДФ bottoms in grooves (0.03's push-to-open drawer 17: chipboard bottom 343 × 406 between the
  sides, back behind it, as its table gives). Boxes of names-only tables (bedroom, desks) are estimates (350 / 500 deep
  by the runner lengths in the hardware lists, heights guessed).
- Hanging rails chrome Ø25 (lengths 446 / 911 per hardware lists).

## Per module (points worth knowing)

- 0.01 / 0.01-01, 0.05: window notch 426 × 905 at the free edge; the lower door's crescent runs out 426 mm from the free
  side; 0.05 is built as its instruction (the catalogue p. 41 shows 0.05-01, the mirror).
- 0.02: door 13 hangs on overlay hinges on partition 3 (hardware list), 12 / 14 on the sides.
- 0.03: top drawers' boxes are numbered 13.x ×3 as the table does (13.2 … 13.5 counted 3).
- 0.06: row 10.5 printed 16 thick — corrected to 3.0 in `gen/cutlists/monako-0-06.json` (twin 11.5 is 3.0; 646 = 637 + 2×4.5).
- 0.09 table: built **folded** L1500 (model size [1500, 900, 760]; index.json has 2000 = unfolded). Legs are L-shaped pairs
  of 25 boards (4 + 6, 5 + 7) as the front / side views show; rails 120 high flush with the leg boards. The insert 8
  (500) is `covers` on the left half-top (the frame is too narrow to store it); moves slide the halves ±250.
  Support elements 9 position / size and the rail thickness are guesses.
- 1.01-01: interior per the p. 42 sketch and Схема 1 (левая секция: hat shelf 8, rail 911, back strip 15 carrying the joint
  of backs 22; right: shelf 9, partitions 4 / 5, shelves 13 / 14, shelf 10 with the front board 17 set behind the
  накладки, 11 / 12). Table lists «18.3 Накладка» only twice although all four doors are split — built one per door,
  noted in the cut list.
- 1.05 bed: headboard 1710 × 935 × 25, footboard 1710 × 335, rails 2010 × 200 × 25, overlays 4 (150) / 5 (310, crescent)
  19 thick on the headboard, V-grooves at the thirds; metal frame (black tubes, 22 slat rows, 9 legs) and a mattress 200
  are not in the cut list. Model size [1710, 2060, 940] (x across).
- 1.08: shelf heights inside from the p. 42 sketch / Схема 1 (±50). 3.01 (hall) is 1.08 with rails in both columns.
- 1.09 / 1.09-01: one drawing for both; the catalogue cut-outs show 1.09-01 as drawn (crescent deepest at the right,
  hinges left) and 1.09 mirrored.
- 1.10: crescents alternate (drawer 8 deepest right, drawer 9 deepest left) as drawn; backs joined by the 970 profile.
- 1.06: «царга» 5 is the modesty board at the back under the drawer housing 4 (the catalogue shows open knee space).
- 1.12: 5 fixed shelves, backs 7 ×2 + 8 ×4 = one per compartment.
- 2.14 / 2.15 / 2.15-01: pedestal backs 13 / 17 are chipboard; crescents deepest towards the knee space; 2.14's door 16
  has a groove at mid-height as drawn.
- By-photo pieces take the collection's construction and the photo's proportions; inner sizes ±20 mm, extents exact.
  1.15 купе: two 940 doors in tracks inside the frame, pull profiles as short chrome bars on the outer edges (guess).
  3.08 / 3.09: drawer + tilt-out bins (flap, bottom hinge, 35°) with a two-shelf rack. 3.04: oak panel, shelf 1395, six
  chrome hooks (knobs). Mirrors: oak board 16 + mirror 4 on 1 mm tape, 35 mm oak margin.

## Finishes (swatches p. 41, `catpage.py 41 --swatch …`)

- `monako-white-oak` «6G Белый глянец / Дуб Саттер 369 SWA»: front `door_enamel_whitey#f9fbfc@gloss` (white half of the
  swatch 0.675,0.86,0.695,0.90 → #f9fbfc, flat), body #7f4e31 (oak half 0.715,0.86,0.73,0.90).
- `monako-mokko-oak` «Серый Мокко / Дуб Саттер 369 SWA»: front `door_enamel_whitey#61594e` (0.765,0.86,0.785,0.90, flat;
  the close-ups p. 39 / 40 render it neutral #707070 — photo grading), body as above.
- «Молоко» in index.json colours is the chair's paint (p. 35 «крашение») — not a furniture finish.
- metal: chrome (rails, купе pulls, hooks); bed frame black; slats `#c9a77c`; coffee-table inserts `gloss#f3f4f4` («только
  белые» in both finishes).
- Textured decor: «Дуб Саттер 369 SWA» → `gen/monako_decors.md`.

## Engine / checker limits for the lead

- preview2d draws `shape: path` fronts as their boxes (the crescents and window notches are in the outlines only), and a
  `bar` handle as a disc (1.15's «примечание» about L is that).
- The glazed door's glass is a separate part behind a notched front (no «glass in a notch» front type).
- 0.09: no way to show the stored insert; a two-state (folded / unfolded) model would need the insert appearing on open.
- Tilt-out shoe bins: `flap` with hinge bottom; the racks are straight boards moving with it (real racks are slanted).
- Glides are small black tubes (hardware «g») so the extent reaches the floor.

## Skipped

Nothing: the collection has no chairs (the chair «Алексис М» on p. 35 is another collection's code).
