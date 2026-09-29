# «Визит» (vizit, П8.971) — wave 5

Catalogue p. 136 (printed 268–269): the hall interior (3.07, 3.08, 3.01), front-on cut-outs of all eight modules, the
swatch «Сосна Карелия 528». No instructions exist; the site has one product page (3.01: closed front-on, 3/4 and open
photos). Every module is **by catalogue** (3.01 also by photo). Generator `tools/casegoods/gen/vizit.py` (writes the 8
designs and `gen/vizit_catalog.json`). Sheets `pilot/vizit-*.png`, all "ok"; refs = the p. 136 cut-outs (rendered at
250 dpi, crop 0.67,0.12,0.955,0.75 → `vizit/cut.png` in the scratch folder).

## index.json
The series has no collection page on the site, so index.json holds its articles without a slug and, except 3.01, with
the name and size of the *previous* line (e.g. «П8.971.3.07 | П8.971.3.01: L1000хB470хН500 Комод [1050, 372, 750]» is
really 3.08 …). The page text gives: 3.01 тумба для обуви 1000×470×500, 3.02 800×380×1120, 3.03 700×400×1000, 3.04
1000×300×1200, 3.05 комод 700×372×750, 3.06 1050×372×750, 3.07 1050×372×750, 3.08 536×480×1120 — used as written.
Collection id `vizit`, name «Визит».

## Construction (one scheme, measured on the cut-outs)
The cut-outs are printed ≈ 5 % wider than their real proportion, so x was scaled by L and y by H per module.
- Carcass ЛДСП 16 «Сосна Карелия»: a bottom over the full width on grey plastic glides 12 high, the sides on it, the top
  16 over the sides and flush with the fronts; back ХДФ in grooves 6 mm from the back edge (split behind partitions).
- **Overlay fronts** ЛДСП 16 over the whole front: 2 mm in from the ends, 3 mm gaps, the lowest front 2 mm over the bottom
  board (the bottom's edge shows as a thin band over the glides, as on the photos), 3 mm under the top.
  Exceptions: 3.03 stands on a recessed plinth 40 (the dark band under its doors), sides to the floor; 3.08 has **inset**
  fronts between its sides (the sides' edges show on the cut-out).
- Handles: black staple handles ≈ 190 long with square posts (c-c ≈ 150 in the engine), horizontal and centred 42 mm
  under the top edge of doors, drawers and flaps; upright by the meeting edge on the doors of 3.02, 3.03, 3.07.
- Drawers: ЛДСП 16 boxes, ХДФ bottoms, 13 mm runner gaps; 300 deep (420 in 3.08).

| module | layout |
|---|---|
| 3.01 тумба 1000×470×500 | two doors with top handles (the open site photo: side-hinged doors, one shelf, no partition) |
| 3.02 тумба 800×380×1120 | left column 500 (partition at 500): drawer 846–1101 over two tilt-out shoe flaps 446–843 / 30–443 (with racks); right a door with an upright handle, 3 shelves |
| 3.03 тумба 700×400×1000 | plinth 40, two doors 44–981 with upright handles by the meeting edge (centre 840), 3 shelves |
| 3.04 тумба 1000×300×1200 | two **unequal** doors 595 / 397 (joint at 598.5, measured), handles on top near the joint, a partition behind the joint, 3 shoe shelves each side |
| 3.05 комод 700×372×750 | door (top handle) + 3 drawers 561–731 / 386–558 / 30–383 |
| 3.06 комод 1050×372×750 | two doors + the same 3 drawers |
| 3.07 комод 1050×372×750 | door + 4 equal drawers + door (upright handles by the drawers) — the only difference from 3.06 |
| 3.08 комод 536×480×1120 | three drawers with inset fronts 772–1102 / 450–769 / 30–447, handles at 30 % of each front |

The lower fronts of 3.02 are built as tilt-out shoe flaps (a «тумба для обуви», B 380, handles on top) — a reading of the
cut-out; they could also be doors. 3.08 is named «Комод» and built with drawers although it looks like a tall shoe
cabinet in the interior photo.

## Finish
`vizit-sosna-kareliya` «Сосна Карелия 528»: body `door_enamel_whitey#c6c4c5` (swatch p. 136, crop 0.78,0.865,0.835,0.905,
flat ±1.7) — a textured decor, provisional (`gen/vizit_decors.md`). Metal: black (handles).

## For the lead
- All inner sizes are from the cut-outs (±10 mm); the shoe racks are simplified (ledges between end plates).
- check.py draws `bar` handles as circles.

## Skipped
Nothing.
