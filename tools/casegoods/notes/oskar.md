# «Оскар» (oskar, П7.040) — wave 5b

Catalogue p. 141 (printed 278–279): the interior with 4.51 («Сосна Карелия»), cut-outs of all five (the dining tables folded
and unfolded), swatches «Сосна Карелия» / «Дуб Каньон». Site: 4.51 («П040.512») four views, 4.52 two, 0.55 two, 0.53 and 0.54
one each. No instructions: all five **by photo**, ±15–30 mm. Generator `gen/oskar.py`; sheets `pilot/oskar-*.png` (ok; refs =
the site photos). The chairs of the page (Трио М, Фернандо М, Рустикаль М, Моника Концепт) skipped — and their paints
(«Молоко», «Дуб Сонома светлый», «Слоновая кость») are not table colours.

## Construction
- **4.51** 1100/1600×700×750: top ЛДСП 22 with rounded ends (corners R 150), split across the middle, halves run out 250
  each on runners in an apron ЛДСП 16 (936 × 576 × 100); a butterfly insert 500 × 700 (two 500 × 350 halves) stored folded in
  the apron, raised into the gap by two slides. Four bent steel tube legs Ø40 painted white — a bow bulging ≈ 20 outwards at
  45 % of the height (two rods each) — on black glides 15 (the photo 1: near-front).
- **4.52** 800/1200×600/800×750: a swivel-flip top — two leaves ЛДСП 16 800 × 600 stacked on a small apron (616 × 416 × 100)
  with a swivel plate; the same legs, set 72 in. Unfolded 1200 × 800 = the top turned 90° and the upper leaf flipped over.
- **0.55** 670×550×750: two crescent boards 16 (C open to the front; outer arc R 400, 160 thick at the middle, top and bottom
  bands 80 with curled ends — outlines), a D-shaped base 610 × 550 on four castors, two shelves between the crescents, a
  D-shaped top 530 × 480.
- **0.53** 450×450×650: round base Ø450 on castors, a hollow column 150 × 200 (two side boards and two framed boards with a
  window — stiles 20, rails 45 / 60), a round top Ø450 with a black glass Ø440 × 4 on it.
- **0.54** 340×430×662: base, an upright at the back end, a middle rib 160, the top — ЛДСП 16.

## Finishes
`oskar-sosna-kareliya` #e7e8e1 (p. 141 crop 0.677,0.865,0.731,0.905), `oskar-dub-kanon` #8c6d51 (crop 0.757,0.865,0.81,0.905),
textured, provisional (`gen/oskar_decors.md`). Role `legs` = gloss#ececec (white painted steel, both finishes; the
photos show only white legs). The black glass of 0.53: gloss#141414.

## Sizes
Model sizes = the folded tables: 4.51 [1100, 700, 750] (index.json had L1600 — corrected), 4.52 [800, 600, 750]; unfolded in
the model notes.

## Engine limits for the lead
- 4.52's swivel-flip top needs a turn about y (90°) and a flip about a horizontal hinge; with straight slides the leaves move
  apart along z → an 800 × 1200 top (the unfolded size, not turned).
- Butterfly inserts only slide up. Bent legs are two straight rods each (a curved rod / bend radius would be closer).
