# «Норд Лофт» (nord-loft, П3.0560) — 6 designs, all by catalogue + photo

Generator `tools/casegoods/gen/nord-loft.py` (designs + `gen/nord-loft_catalog.json`). Sheets `pilot/nord-loft-*.png`,
all ok (no reference overlay: the photos are perspective; there is no instruction).

Sources: catalogue p. 79 (cut-outs, sizes, «Варианты крашения»), site photos of every code (0.04 almost front-on).

## Construction
- Nesting «cube» coffee tables 410 / 460 / 510 square, H 420 / 470 / 520 — the smaller slides into the larger
  (room photo 0.03).
- Frame: black steel square tube **15 × 15** (0.04 front photo: posts 47 px at 3.02 px/mm) — four posts, four rails under
  the top, four rails on the floor; the top overhangs the frame by **6** (frame 398 under the 410 top).
- Top: 0.01 / 0.02 / 0.03 — solid oak 20 (staves, eased edges); 0.04 / 0.05 / 0.06 — ЛДСП 25 «Дуб Вотан» (edge 25 mm =
  76 px on the photo). The photos named «…Nord-22_P562-22_dyb_vatan» are the 0.04–0.06 ones.

## Finishes
- `nord-loft-dub-massiv` «Дуб натуральный (массив)» #9a866a (p. 79 crop 0.748,0.858,0.808,0.900), model finish of
  0.01–0.03; `nord-loft-votan` «Дуб Вотан (ЛДСП)» #7a5b41 (p. 79 crop 0.826,0.858,0.888,0.900), model finish of
  0.04–0.06. Both provisional (decors in `gen/nord-loft_decors.md`); the top uses role `top`. Metal: black.
- Each code has its top material fixed, so the model sets `finish`; the other finish is still offered by the collection
  (it recolours the top only).

## Limits / guesses
- The solid top's thickness (20) and the tube size (15) are read off photos (±3 mm).
- Weld details / felt glides not modelled.
