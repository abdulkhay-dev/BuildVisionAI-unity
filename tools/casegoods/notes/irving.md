# «Ирвинг» (irving, БМ2.748) — notes

Catalogue pp. 94–96 (spreads 184–189): interiors 94–95, cut-outs, interior schemes and the «Сосна Джексон» swatch p. 96,
close-ups p. 95 (the slanted joint of two fronts, the semicircular finger notch). No instruction is published (index.json
has no pdf), so **all 13 designs are by catalogue / product photo** (pinskdrev.by photos downloaded for 1.01-01, 1.02,
1.03-01, 1.30, 1.31, 1.40, 2.46). Generator `gen/irving.py`; all print ok; sheets `pilot/irving-*.png`. Inner sizes are
good to ±10–20 mm, the overall sizes are the catalogue's.

## Construction (one scheme)
- ЛДСП 16 sides from the floor, a 22 top, a bottom on a 60 plinth rail; the fronts sit inside a frame of front pilasters
  58 × 22 with rounded edges on the sides (the thick rounded edge of every case piece in the photos).
- Fronts ЛДСП 16, 3 mm gaps, 2 mm behind the pilasters; no hardware — a semicircular finger notch r 30 cut into the top
  edge (`shape: path`, cubic curve) of each drawer front and lower door (at the free edge). The fronts' slightly slanted
  joint edges of the close-up are not modelled (straight edges).
- Wardrobes (2176 × 586): columns of «split» doors (lower door to y 950, upper door over it) and full-height mirror doors
  (a 12 mm oak door with a mirror over its face): 2Д split+split, 3Д split/mirror/split, 4Д split/mirror/mirror/split,
  5Д split/3 mirrors/split (the cut-outs p. 96). White interior (the open photo of 1.01-01): partitions where a split
  column meets a mirror column, shelves in the split columns, hat shelf + chrome rail in the mirror columns.
- Bedside 1.30: drawer over an open niche. Chest 1.31: three equal drawers. Desk 2.46: two end panels, modesty panel,
  two drawers under the top.
- Beds 1.82 / 1.84 / 1.83 / 1.85 (W = 1684 / 1484 / 1884 / 984, L 2141, H 960): block posts 80 × 80 (head full
  height, foot 420), headboard with a notch r 60 in its top edge, side rails 22 × 220, foot rail, metal base with slats
  (middle beam and leg from 1200 up), mattress.
- 1.40 day bed (2041 × 942 × 634): shaped ends (`shape: path` in the side plane, high at the wall, rounded down to the
  front rail), a back board along the wall, front rail, two drawers under it with notches.
- 1.62 mirror: catalogue L1060 × B5 × H600, built as a 1 mm pine-decor backing whose 40 mm rim shows round a 4 mm mirror;
  the p. 96 cut-out looks like a wooden frame, which B5 does not allow — the lead may want to check the site. Not in
  index.json (listed on p. 96).

## Finish
`irving-sosna-jackson` «Сосна Джексон» provisional #6e6a60 (`catpage.py 96 --swatch 0.715,0.86,0.775,0.905`); decor in
`gen/irving_decors.md`. Metal chrome (rails). Note: the site photo of the desk 2.46 is warmer (another variant?); the
catalogue offers one colour.

## Limits
preview2d ignores outlines (notches, shaped bed ends) in its drawings; check.py tests overlaps by outline only for
`shape: path` parts. Engine: the pilasters' round-over is `edge: 6`, not a real profile.
