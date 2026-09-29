# «Парма» (parma, П7.050) — wave 3

Catalogue «Корпусная мебель ч. II» 2025, PDF pp. 52–56 (printed 100–109): living rooms p. 52 / 53, bedrooms p. 54 / 55,
the module cut-outs and the swatch on p. 56; the site's product photos (pinskdrev.by: 0.13, 0.29, 0.55, 0.61, 1.00,
1.02, 1.18, 1.19, 1.31). Generator `tools/casegoods/gen/parma.py` (re-runnable: 20 designs + `gen/parma_catalog.json`),
cut lists `gen/cutlists/parma-*.json`, decors `gen/parma_decors.md`, sheets `pilot/parma-*.png` — all 20 print `ok`.

## Modules

**By instruction (6)**: 0.13 Шкаф 2Д, 0.29 Тумба, 1.31 Комод, 1.53 Стол, 1.41 Зеркало, 1.00 Кровать 2-16 (с подъёмным
механизмом). The instructions (a.pinskdrev.by / .ru) have no text layer: the tables «№, наименование, a×b мм, n» and the
lettered hardware were transcribed from the pictures; the full PDFs (6 pages; `reference/parma/pages` holds p1–p4) show
where the pilasters go (step 7 / 15). The printed titles of 1.00 / 1.41 / 1.53 are the older codes П050.1201М / П050.401 /
П050.503 — the same pieces.

**By catalogue / photo (14)**: 0.11 Шкаф (one bay of 0.13), 0.21 Тумба 1080 (0.29 without its right door bay), 0.22
Тумба (three rows of two doors 386 between oak horizontals), 0.32 Комод (a drawer over two doors), 0.61 Стеллаж (two
drawers over 4 × 3 open cells, site photos), 0.55 Стол журнальный (L legs, apron, oak top and low shelf, site photo),
0.51 Стол обеденный, 0.71 Полка (oak board on two black L brackets), 1.26 Тумба прикроватная (one door 424 × 386),
1.18 / 1.19 Шкаф 2Д (two doors 424 over two drawers, site photos and the interior sketch), 1.10-01 Шкаф 4Д (four doors,
mirrors in the middle pair, four drawers), 1.01 / 1.02 Кровати (1.00's parts without the lift, 1778 / 1378). Sizes
inside these are read off the photos with the instructed modules' parts (bays 428 / 381, fronts 424 / 386 / 636, drawer
fronts 200, bottom 80, sides 390 / 416 / 586) — ±20 mm.

The 0.13 sheet overlays the site's front photo (`Shkaf_s_vetrinoi_…__.jpg`): doors, glass openings, knobs and bands sit
on it. No module has an orthographic drawing.

## Construction (from the instructions and photos)

- Sides ЛДСП 16 to the floor (on glides) are the legs; H = sides + the top 16. The top (oak) lies on them and overhangs
  10 at each end (924 top, 872 bottom + 2 × 16 sides = 904 carcass); the bottom (oak) between the sides, raised (80 /
  84 above the floor: 0.29's partitions 370 + its rails 16 fix the height), the open recess under it.
- **Pilasters «44 × side height»** (ЛДСП 16) are dowelled edge-to-edge onto the sides' front edges: they extend each side
  44 forward. The fronts (МДФ 18) sit between them, flush with their faces, in front of the carcass edge; the partitions
  stand behind the joints (0.13's centre joint shows the partition's edge; 0.29's doors 386 overlay its partitions). This
  is the reading that lets the drawer boxes pass (runners on the sides) and matches the photos (a 16 strip at each end).
  Consequence: **B = side + 44** — 434 (0.13, 0.11, 0.29, 0.21, 0.22, 1.18), 460 (0.32, 0.61, 1.26, 1.31), 516 (1.53), 630
  (1.19, 1.10-01). The catalogue writes 10–16 less (it gives the top's depth: 420 / 450 / 500 / 620; 0.13 writes 424).
  The models carry B = side + 44 with a note — the lead should decide (the other readings — pilasters flat on the front
  edges — make B right but put the pilasters across the drawer boxes' path).
- The top (420 / 450 / 500) therefore stops 10–16 behind the fronts; the photos can't show it either way.
- Oak parts (role `top`): the tops, the bottoms, and the horizontals that show in the fronts' joints (0.13's partition 7,
  1.31's shelf 6 under the top drawer — the photo shows the band there, the instruction text had it between drawers 2 and
  3; 0.22's rows, the wardrobes' drawer tier, 0.32 / 0.61's horizontal under the drawers).
- Backs ДВП in grooves (z 6–9), jointed on the partitions; 0.29's niche open at the back as in the instruction.
- Fronts: face `frame` (border 50 on doors, 36 on drawers, sunk 3) with `parma-bevel`; glazed doors frame 62 + rebate 12
  (glass laid in from the back, 15 mm under the frame), clear. Knobs black Ø30 at the meeting edges (0.13: mid-height),
  at the inner top corners (0.29), near the top of the drawers.
- Drawers: overlay fronts 200, boxes 350 × 160, ДВП bottom under the box, «брусок продольный» 350 × 90 under it (1.31).
- Beds: headboard 25 × 1070 on glides with the quilted panel 5 (W − 100 × 450, 50 from the top and the ends; `soft`,
  12 × 3 tufts), rails 2008 × 220 from the headboard to the footboard W − 116 × 322 which closes their ends (L = 25 +
  2008 + 25 = 2058), the metal base 1600 × 2000 / 1200 × 2000 with slats and a middle beam; 1.00 with the lifting frame
  (a `flap` about [300, 29], the bedding box of black walls and a hardboard floor under it).

## Finishes

- `parma-randers-kantri` «Сосна Рандерс / Дуб Кантри золотой» (the only colour option): body = front
  `door_enamel_whitey#d9d9d9` (p. 56 swatch, flat), role `top` #a88059 (p. 56 swatch), role `fabric` `velvet#cdbfa8`
  (the champagne crushed velvet of the headboard, photo). Both wood decors are provisional (`gen/parma_decors.md`;
  «Дуб Кантри золотой» is already in decors.md from wave 1). metal `black` (knobs, shelf brackets, bed base).

## Engine limits for the lead

- The door / drawer panels are «vagonka»: vertical plank grooves on the sunk panel (photos). `face.frame` cannot carry
  grooves on its panel — left plain. A frame face with a panel pattern (grooves / fluted inside the frame) would do it.
- The lift bed: the base, slats and mattress lift as one `flap` about the head end ([y 300, z 29], 40°); the gas struts
  and the lifting frame's hinges are not modelled; please check the direction in 3D.
- The glazed door's glass lies behind the frame (from the back); `glass` fronts put it in the middle — no visible
  difference.
- preview2d draws bar/knob handles as discs and mouldings as bands.

## Skipped

The chair «Трио М» on p. 53 (another collection, a chair) — out of scope. Nothing else.
