# «Верес» (veres, П3.564) — wave 5

Catalogue p. 135 (printed 266–267): the hall interior, the cut-outs of all ten modules, the swatches «Дуб бордо лайт»
(Фасад) / «Дуб каньон» (Каркас). No instructions exist (index.json has no `pdf`, the product pages on pinskdrev.by carry
none). The product pages have 1–3 photos per module (front-on views of 3.01, 3.05, 3.07, 3.09, 3.10, 3.14, 3.17, 3.18;
open views of 3.01, 3.05, 3.07, 3.09, 3.10; 3/4 views of 3.06 and 3.08). So every module is **by photo / by catalogue**:
sizes inside the modules were measured on the front-on photos with the catalogue L and H as scale (the photos are not
isotropic — x and y were scaled separately), good to about ±10 mm; the overall sizes are the catalogue's.

Generator `tools/casegoods/gen/veres.py` (writes the 10 designs and `gen/veres_catalog.json`). Sheets
`pilot/veres-*.png`, all "ok"; refs: the front-on site photos, for 3.06 / 3.08 the catalogue cut-outs (p. 135 at 200 dpi).

## Construction (one scheme for the set)
- The visible frame round the fronts measures 24–27 mm on every photo (sides, top and bottom alike) → carcass
  **ЛДСП 25 «Дуб каньон»**: bottom and top over the full width and depth, the sides between them. Inner partitions,
  shelves and rails ЛДСП 16. Back ХДФ 3.5 in grooves 6 mm from the back edge (split behind the partition / back rail).
- Grey plastic block feet 18 high (40 × 30), 20 mm in from the ends, front and back (extra pair under 3.05 at x 420 as in
  the photo and under the partition of 3.08).
- Fronts ЛДСП 16, **inset** between the sides / top / bottom, flush with the frame's front edge, 2–3 mm gaps. Doors and
  flaps «Дуб бордо лайт»; drawer fronts and the shoe flap of 3.07 «Дуб каньон» (as the cut-outs show).
- Shoe flaps tilt out on a bottom pivot (`flap`, 40°) and carry a two-level rack (brown plastic ends, two «каньон»
  ledges with lips) that moves with them — the open photos of 3.05 and 3.07.
- Handles: satin staple handles ≈ 170 long (c-c ≈ 136 in the engine; square posts), horizontal and centred ≈ 26–30 mm
  under the top edge of drawers and flaps, upright ≈ 30 mm from the free edge of doors.
- Drawer boxes ЛДСП 16 with ХДФ bottoms, 13 mm runner gaps.

| module | layout (mm from the floor) |
|---|---|
| 3.10 тумба 496×401×867 | drawer 641–840 over a door 45–638 (hinge right), fixed rail under the drawer, a shelf |
| 3.09 тумба 794×401×450 | carcass 376 high (two doors, a shelf) with a seat cushion 74 on top (`soft`, fabric role) |
| 3.07 тумба 812×382×1258 | open niche 1048–1233 (its floor 16 runs to the front), «каньон» shoe flap 655–1029, a rail, two doors 45–633, a shelf, a back rail behind the back joint |
| 3.06 тумба 812×382×1044 | «каньон» drawer 804–1016 over two tilt-out flaps 424–801 / 45–421 with rails between |
| 3.08 тумба 1208×382×1044 | the 3.06 block (between the left side and a partition at 812–828) + a column: open niche 857–1019 over a door 45–838 (hinge right) |
| 3.05 тумба 1064×382×627 | a bench part 450 high (flap 45–423) with an upstand board 16 behind it to the full height; a column 636–1064 (partition 16): drawer 432–600 over a door 45–429 |
| 3.01 шкаф 2д 991×597×2020 | two doors 45–1993; inside: hat shelf 1790, rail at 1720–1745, a back rail 1150–1250, a low shelf 455 (open photo) |
| 3.17 / 3.18 вешалка 794×311×2020 / 1370 | «каньон» board 25 (730 wide, 32 in from the shelf ends — the shelf overhangs it on the photos), shelf 25 × 286 (top at 1789 / 1172), chrome double hooks (a plate + two `rod` arms): 3 + 2 / 3 |
| 3.14 зеркало 496×22×1000 | board 16 «каньон» with a bevelled mirror 4 glued on (borders 45 / 45 / 38 top) |

## Finish
`veres-bordo-kanon` «Дуб бордо лайт / Дуб каньон»: body `door_enamel_whitey#7f6951` (swatch p. 135 «Каркас», crop
0.735,0.86,0.79,0.9, flat ±7.9), front `door_enamel_whitey#dbd8d7` (swatch «Фасад», crop 0.655,0.86,0.705,0.9). Both are
textured decors (provisional; `gen/veres_decors.md`). Role `fabric` = velvet#4a3a33 (the chocolate seat cushion, read
off the photos). Metal: chrome (satin handles, hooks, the rail). The site also lists older colour names («Дуб версаль»,
«Тёмно-коричневый» — the 3.06 site photo has dark brown flaps): the catalogue colours were used.

## Sizes
All catalogue sizes as on p. 135. The site writes 3.05 as L1046 — the catalogue's L1064 is used.

## For the lead
- The ЛДСП 25 frame is a reading of the photos (the band round the fronts is ≈ 25 mm everywhere); if the real carcass
  is 16 with a 25 top only, the fronts grow by 9 mm per side.
- Hooks are a plate + two `rod`s (rods are not drawn in the check sheets).
- The shoe racks are simplified (two ledges + lips between brown end plates; the real rack is a moulded plastic trough).
- The cushion of 3.09 is a plain `soft` box (the real one has rounded edges and piping).
- check.py draws `bar` handles as circles (the "примечание" lines about the extent are that artefact).

## Skipped
Nothing (the set has no chairs).
