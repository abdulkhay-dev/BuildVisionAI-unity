# «Кен» (ken), П3.596: 3 modules, all by catalogue

Source: the single interior photo on catalogue p.70. There are no cut-outs, no swatch, no instructions and no
network, so **every module is by catalogue**. Generator: `gen/ken.py` (it also writes `gen/ken_catalog.json`).

## Construction (from the photo)
- Carcass ЛДСП 16 «Дуб Онтарио»: top and bottom over the full width, sides between them. Back ХДФ in grooves (6 mm).
- Legs: black metal Ø20 × 150 (measured 150 on all three pieces), 36 mm in from the sides and the front/back.
  4 legs, or 6 on the TV unit (the middle pair shows in the photo).
- **Inset fronts** ЛДСП 16 flush with the carcass edges, 2 mm gaps: the carcass edges show all round the fronts in the
  photo.
- The UV print «ёлочка» (chevrons, apex up on the front's centre line, 45° arms, pitch 70 mm) is on:
  - 0.02: the upper right and the lower left doors;
  - 0.01: the lower door;
  - 0.03: both doors.
  The lowest apex sits 87 mm over the front's bottom edge (0.02 upper right: 45; 0.01: 100), as measured.
- Pulls: black edge pulls ~56 mm on the top edge of the lower fronts, centred. The upper doors of 0.02 and the glazed
  door of 0.01 show no pull (opened by their lower edge, or push-to-open).
- The catalogue depth B 400 = the carcass. Pulls stand out 9 mm (the checker's "примечание").

| module | layout |
|---|---|
| 0.02 шкаф 1040×400×1196 | 4 doors 2×2 (501 × 504) round a fixed shelf at the joint, 1 loose shelf in each half, no partition (none shows between the doors) |
| 0.01 шкаф-витрина 540×400×1914 | Lower printed door to 866. Upper door 869…1896 with a big clear glass (rails 167 bottom / 180 top, stiles 20). It is written as a front with a `path` outline that has the glass hole, plus a `glass` pane in the hole, in one move. Fixed shelf at the joint, a shelf at the glass's lower edge (1038), a shelf in the glass (1390), 1 shelf below |
| 0.03 тумба ТВ 1540×400×560 | 3 openings of 492: printed doors at the ends (a shelf behind each) and an open niche between two partitions with a fixed shelf at 347…363 |

## Finishes
- `ken-ontario` «Дуб Онтарио + УФ печать «ёлочка»»: body provisional `door_enamel_whitey#a8937c`. This is a trimmed
  mean of the plain lower right door of 0.02 in the p.70 photo (`k02.png` crop 750,650–1150,1050 at 200 dpi ≈ page
  0.22–0.30 × 0.64–0.75). The plain upper left door gives #ac9e97; the catalogue has no swatch of this colour.
  The decor is listed in `gen/ken_decors.md`.
- `metal` black (legs, pulls).

## What the format / engine could not express (for the lead)
- **The print:** «ёлочка» is a printed dark line, not a milled groove. It is approximated by V-grooves (`face grooves`,
  w 2.5, depth 1), which will read as shadow lines in the oak colour, not as dark lines. Better: a `print` material
  (the lines over the oak texture) or grooves with their own material.
- **The pull:** the edge pull (a black clip over the front's top edge) is approximated by a small `bar` handle 6 mm
  under the edge.
- **Glazed door:** the engine's glazed front has one frame width all round, so a door with unequal rails had to be
  written as a `path` front with a hole plus a separate glass part.
- **Sizes:** all sizes were read off one perspective photo (±10–15 mm inside the modules). The overall sizes are the
  catalogue's (index.json agrees with p.70).

## Skipped
None.

Check sheets: `pilot/ken-*.png`, all "ok"; the ref is the p.70 photo, a rough perspective overlay.
