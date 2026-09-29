# «Сати» (sati, П7.057) — 18 modules, all by catalogue and product photos

Generator `gen/sati.py`, fragment `gen/sati_catalog.json`, decors `gen/sati_decors.md`, sheets `pilot/sati-*.png` (all
ok; 1.17 overlaid on the site's square-on photo).

## Sources
No instruction exists (none in index.json; IS-P7-057-* is 404 on a.pinskdrev.by / .ru). Catalogue pp. 21–24 (living
room p. 21 nearly front-on, bedroom p. 22, hall / bedroom p. 23 with the close-ups of the fronts, the handles and the
patina, p. 24 module cut-outs, wardrobe interior sketches, the swatch) and the pinskdrev.by product photos (all 18
articles; the 4Д wardrobe П7.057.1.17 is photographed square to the camera and gave the proportions). Inner sizes are
good to ±10–15 mm, the overall sizes are the catalogue's.

## Construction (by photo)
- Carcass ЛДСП 16 on square tapered legs 50 → 34 (the end legs splayed 10 mm out), 85 under the wardrobes (4Д photo),
  100 under the others; sides from the legs up, bottom between, ХДФ back in grooves.
- Tall pieces: crown `sati-crown` 44 high, 40 mm out at the front and both sides, and an 18 cap (62 over the carcass on
  the 4Д photo); the doors run to 2 mm under it. Low pieces: a 22 top 12 mm out.
- Fronts МДФ 19, overlay (2 mm reveal, 3 mm gaps): a milled frame — a flat border 55 (42 on small fronts), a stepped bead
  `sati-bead` down to the panel (face `frame` with `profile`) — and two bronze patina lines along the bead (rods d 1.6,
  role `patina`: the catalogue close-up p. 23 shows the dark lines at both steps). Plain fronts where the photos show them:
  the drawers of 0.10, 0.11, 0.21, 1.23, the desk and the wardrobes, the two small drawers of 1.26. Glazed doors: the
  border round clear glass with a glazing bead.
- Handles: cast bronze bows c-c 128 (the catalogue; the site's white variant has straight gold bars) — rods: two posts and
  an arc; vertical by the free edge of doors, horizontal on drawers (two on drawers wider than 700 and on 1.28).
- Layouts: 0.10 lower door 610 / drawer 200 / glazed door 1189 (hinged left, «универсальный»); 0.11 two drawers 190 under
  two glazed doors, a middle partition, 4 shelves per side; 0.21 door | 3 drawers | door (508 / 940 / 508, p. 21); 1.23
  three equal columns door | 5 drawers | door; 1.28 door (⅓) | 4 framed drawers; 1.29 4 framed drawers; 1.26 two small
  plain drawers over three framed (150 / 242); 1.25 two framed drawers; 3.29 a framed tilt-out front (flap, 40°); 2.51 two
  pedestals 440 (plain drawer over a framed door) under a 22 top, a modesty panel; wardrobes 2Д / 3Д / 4Д doors over a
  row of drawers 200, interiors after the p. 24 sketches (2Д shelves | rail; 3Д shelves | rail; 4Д shelves | rail |
  shelves), hinges from the handle positions (3Д L R R, 4Д L L R R); 3.92 a board under a 139-deep hood (crown + cap)
  with three double hooks (rods); mirrors 1.40 / 1.42 a 6 backing, the mirror, a 72 × 16 moulded frame `sati-mframe`;
  beds 2-14 / 2-16 a 22 headboard to 1000 with an upholstered panel (`soft`, velour) in a moulded frame, a storage box of
  22 panels on six tapered legs, the lifting metal base, mattress ≤ 200.

## Finishes
- `sati-zhemchug` «Персидский жемчуг»: body #c6c0ba = the collection's own swatch p. 24 (`catpage.py 24 --swatch
  0.72,0.865,0.765,0.90`, flat). NB: wave 1 used #dfe3e2 (the p. 132 swatch of the same name) — Сати's swatch and all its
  photos are clearly warmer / darker greige; the lead may want one value. Patina #5e4637 (p. 23 close-up), fabric velvet
  #ab9a93 (p. 22 headboard).
- `sati-white` «Белый» (the site's colour variant, all product photos): body #e6e7e8, patina = a light grey (no visible
  patina on the white photos), fabric velvet #d6ccbf.
- Metal gold#8a5d3f (copper-bronze handles, p. 23).

## Sizes / data
- index.json П7.057.1.40 has [1374, 653, 22]; the catalogue writes L1374 × B22 × H653 (p. 24) — built [1374, 22, 653]
  (it can hang either way).

## Limits
- Patina lines are rods: check.py counts a front-plane moulding 16 mm deep, which would push the low pieces out of B.
  A second material on mouldings (or a "line" part) would be cleaner.
- Bow handles are rods (no cast ends / rosettes).
