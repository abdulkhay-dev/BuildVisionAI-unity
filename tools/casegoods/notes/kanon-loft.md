# «Каньон Лофт» (kanon-loft, П3.0561) — notes

Catalogue pp. 81–86 (spreads 158–169): interiors 81–84, module cut-outs + swatch p. 85 (living) and p. 86 (bedroom,
study, dining, coupe wardrobes). Generator `gen/kanon_loft.py` (writes the 36 designs, `gen/kanon-loft_catalog.json` and
the cut lists in `gen/cutlists/`). All 36 print ok in `gen/check.py`; sheets `pilot/kanon-loft-*.png` (instructed modules
with the instruction's front view as the red-edge reference; the sheets were drawn through a wrapper that colours the
finish's roles — preview2d itself only knows body/front, so with plain check.py the black frame draws as oak).

Instructions: 14 PDFs downloaded from a.pinskdrev.ru (curl works). Eleven have a text layer that cutlist.py could not
read (format «поз., наименование, маркировка, материал, кол-во, длина, ширина»): the tables were rebuilt from word
positions and checked against the page pictures; 1.01 / 1.02 / 1.03 (2022 format, no text layer) were typed from the
pictures. Every completed table is `gen/cutlists/<id>.json` with its source.

## Construction (common to the instructed modules)
- **Carcass** ЛДСП 16 «Дуб Каньон»: sides 322 deep stand on the black back plinth board (88 high) on 4 mm nail glides,
  i.e. from y 92 to the top; top 400 deep (2 mm proud at the sides and front). Sides = H − 16 − 92 in every table
  (1812, 1092, 792, 402, 352).
- **Loft frame** ЛДСП 16 «Черный 660»: a post 16 × 76 on the front edge of each side (Rastex into the side's edge, step 1
  of П561.20) from the glides to the top (H − 20: 1900, 1180, 880, 490, 440); a bar lying under the top and a bar lying
  on the floor between the posts (L − 36); middle boards 250 × 88 (246 in the 400-deep TV unit) under the partitions,
  dowelled to the floor bar. Seen from the side the base is the black loop of the photos.
- **Inside**: black bottom (L − 36) × 379 at y 92–108, z 19–398; partitions 379 deep from the bottom to H − 160; an oak
  apron (L − 36) × 128 hung under the top bar, 16 mm behind the frame face (the LED of the «с подсветкой» variants lies
  in a groove of the top bar in front of it, lighting it — the photos of 0.20). The TV unit П561.18 has 338-deep inner
  panels behind inset doors, a 96 apron and black niche panels; the chest П561.02 a 144 × 303 stiffener under the top.
- **Backs** ДВП (венге in the vitrine units, black elsewhere, white in the bedroom) screwed to the inner panels' back
  edges at z 16–19 (hardware: «стабилизатор задней стенки», joint profiles), split per section; vitrines have a black
  ЛДСП back 16 (row «Стенка задняя ЧЕРНЫЙ 660 WML», 1168 / 448) between their top and bottom shelves (328 deep).
- **Fronts** oak ЛДСП 16, no handles (push-to-open in the hardware lists): inset doors and glazed doors (inner hinges
  H=0) between the side and a 50 mm oak strip beside the partition; overlay doors and drawer fronts (half-overlay hinges)
  in front of the frame, outer edge 2 mm in from the carcass side, covering the partition and all but 10–20 mm of the
  strip (the photos show exactly that sliver). Vitrine doors «ЛДСП 16 + стекло»: oak parts under and over a window, the
  glass glued behind (built as two fronts + a glass; the row count is carried by the upper part via `covers`).
- **Drawers**: the front is the box front (the tables have no separate front wall); sides 350 (desk 400), ДВП bottom in
  grooves of the sides and 5 mm into the front, the back standing on it; ball runners 12.75 mm a side (widths prove it).
- Heights from the tables: overlay fronts from y 107 (door tops overlap the apron by 45: 1805 / 1085), inset fronts
  110 … H − 162, vitrine shelves at 347–363 / from the backs' split (255 + 1168 + 390 = 1815 etc.).

## Modules (36)
By instruction (cut list checked): 0.40 / 0.20 (+ mirrored 0.40-01 / 0.20-01), 0.39 / 0.19, 0.29 / 0.09, 0.32 / 0.12,
0.21 / 0.01, 0.22 / 0.02, 0.38 / 0.18, 0.03, 1.01, 1.02, 1.03, 2.30-01 (+ mirrored 2.30), 2.31, 4.28.
- LED pairs: the catalogue (p. 85) prints each cut-out with two codes, «П3.0561.0.40 (с подсветкой) П3.0561.0.20»; the
  site's 0.12 page is «каркас без подсветки», and the instructions are «П561.20 (П561.20с)» with the LED items marked
  «* только для варианта с подсветкой». So 0.40/0.39/0.29/0.32/0.21/0.22/0.38/0.37 carry `light` parts (strip under the
  top bar; the vitrines' vertical overlay profiles 1158 / 438 on the side and the partition) and 0.20/0.19/0.09/0.12/
  0.01/0.02/0.18/0.17 are the same parts without them.
- Extra codes not in index.json but printed in the catalogue: 0.40-01 (p. 85), 0.37 (p. 85), 2.30 (p. 86, «2.30-01 —
  зеркальное отражение»; the instruction П561.30-1 is the pedestal-right one = 2.30-01).
By catalogue / photo: 0.37 / 0.17 (П561.18 without its right door column — the cut-out and the site photos show door +
niche; the 984 niche and 464 column are those of П561.18), 0.08 (0.29 carcass with a plain inset door), 0.26 / 0.27
(open racks on the frame, 4 shelves), 0.04 (wall box: oak shell, black front frame, partition, inset door), 0.06 (coffee
table: black U legs, drawers through both ends, low shelf), 1.04 (= the 0.21 module under a bedroom code, with LED as in
its photo), 1.05 (mirror board with a black lip shelf), 1.06 / 1.07 / 1.09 (coupe wardrobes from the cut-outs and their
interior schemes).

Details worth knowing:
- 0.21 / 0.01: the catalogue gives 0.01 as L1400×B400 on p. 85 but 0.21 L1400×B414 on p. 83; the instruction is 414.
  Built 414. Same for 0.29 / 0.09 (catalogue B400, instruction side view 414 = sides 322 + posts 76 + overlay door 16).
  The TV units are really 400 (inset doors).
- 1.03: the instruction's drawing says 398 (the carcass); the catalogue's 414 includes the overlay drawer front. 414.
- 1.01 bed: headboard between the posts, a recessed black band 1408 with open «windows» at its ends under the top bar
  (the photo), brusok 7 (1680 × 58) behind the headboard; rails 2014 inside the posts with black bands 11 on their outer
  faces, foot 8 with band 9; L = 76 + 2014 + 16 + 16 = 2122 → the rails start 2 mm inside the posts' depth to keep 2120.
  Metal base f7 2000 × 1600 on 8 legs + mattress.
- 1.02 wardrobe: the middle door 1958 stands 16 mm proud of the side doors (B 671 = 655 + 16) between black bars 23 (on
  the door) and 26 (fixed) and rises above them; the interior (white partition 3 between the left+middle hanging space
  and the right shelves, hat shelf 14 + rail 853, low cabinet 4 + shelf 20, right shelves 13/15/19 + rail 453) follows
  the catalogue scheme; white brusok 27 (998 × 128) placed as a stiffener behind the apron — its place is a guess.
- 4.28 dining table: built open (the catalogue size L1802): the halves slid out over two fixed end frames (oak end rail
  3 on black ledge 10, U legs 13/14 + oak 5/6 + black 16/17 + feet 18, oak ledge 4 behind the rail), black aprons 8 and
  runners 7; black edge boards 9/11/12/15 under the rim (the photos' black line under the top). No move closes it.
- 2.30-01 left leg: black posts 17/19 round the oak face 13, rails 24 back to the oak rear post 9, oak end panel 4, foot
  loop 22 + 27, top piece 25 — read from the exploded view; the exact place of 25 and 24 is approximate.

## Finishes
- `kanon-loft-kanon-black` «Дуб Каньон / Черный 660»: body = front = «Дуб Каньон» provisional #b29e96 (p. 85 swatch,
  `catpage.py 85 --swatch 0.715,0.865,0.738,0.905`, same on p. 86); role `frame` «Черный 660 ТМ» #2b2c30
  (`--swatch 0.752,0.865,0.772,0.905`, flat); role `wenge` (ДВП венге backs) #46382f provisional, from the product photo.
  `white` (ЛДСП белый drawer boxes of 1.03, the wardrobe interior, white ДВП backs) and `black` (bed base) are library
  roles. Metal: chrome (rails, coupe profiles). Decors listed in `gen/kanon-loft_decors.md`.

## Engine / checker limits for the lead
- preview2d colours only body/front: the black frame, backs and white parts draw as oak with plain check.py.
- Vitrine doors: a glazed front needs a frame on all four sides; these have glass only between an upper and a lower oak
  part (no stiles) — built as two fronts + glass in one move.
- The coffee-table drawers open through the short ends: `slide` moves along x.
- The LED strips are `light` boxes; the milky covers of the profiles are not modelled.
- Coupe doors: `slide` moves (no track logic), aluminium profiles as `metal` boxes.

## Skipped
Chairs «Чикаго М» and «Бруно М» shown in the interiors are other collections' seating (out of scope).
