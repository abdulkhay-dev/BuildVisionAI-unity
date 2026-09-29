# «Форте Лофт» (forte-loft, Пинскдрев П3.0583) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF p. 71 (printed 138–139): the living-room photo, the six module cut-outs
with sizes, the colour swatch «Дуб Канзас» / «Антрацит». Generator `tools/casegoods/gen/forte_loft.py` (writes the six
designs and `gen/forte-loft_catalog.json`), cut lists `gen/cutlists/forte-loft-0-08.json`, `-0-05.json`, decors
`gen/forte-loft_decors.md`, check sheets `pilot/forte-loft-*.png` — all six print `ok`.

| id | code | name | source | ref of the sheet |
|---|---|---|---|---|
| forte-loft-0-08 | П3.0583.0.08 | Шкаф 2Д 845×350×1935 | instruction (IS-P3-583-0-08, no text layer, table transcribed) | the instruction's front view (p1 at 200 dpi) |
| forte-loft-0-05 | П3.0583.0.05 | Стол журнальный 1207×604×426 | instruction (IS-P3-583-0-05, table transcribed) | the instruction's front view (p1 at 200 dpi) |
| forte-loft-0-09 | П3.0583.0.09 | Шкаф 2Д 845×350×1535 | by photo (4 site photos: front, ¾, open) | site photo П3_0583_0_09_1 (front-on) |
| forte-loft-0-02 | П3.0583.0.02 | Комод 1574×420×925 | by catalogue (cut-out + room photo p. 71) | p. 71 cut-out (crop 0.805,0.24,0.945,0.385 at 400 dpi) |
| forte-loft-0-01 | П3.0583.0.01 | Тумба ТВ 1704×420×540 | by catalogue (cut-out + room photo p. 71) | p. 71 cut-out (crop 0.705,0.54,0.85,0.63) |
| forte-loft-0-06 | П3.0583.0.06 | Полка 1370×240×210 (wall) | by catalogue (cut-out + room photo p. 71) | p. 71 cut-out (crop 0.705,0.45,0.83,0.51) |

The site (pinskdrev.by) has product pages only for 0.08, 0.09 (and the table 0.05); the chest, TV unit and shelf have
none (category listings searched), so they are by the catalogue only.

## Construction (from the two instructions; positions measured on their vector drawings, `page.get_drawings()`)
- **Carcass** ЛДСП 16 «Дуб Канзас». Top and bottom run the full L × B; the sides stand between them, **B − 20 deep**
  (330 at B 350), flush at the back; the top overhangs the doors by 3 mm. Height = legs 128 + 16 + side + 16
  (0.08: 128 + 16 + 1775 + 16 = 1935).
- **Partition** 294 deep (z 20–314) at x = L/2, between top and bottom, with **«Брусок» ЛДСП чёрный 1773 × 60** laid
  flat on its front edge, flush with the sides' front (z 314–330, 2 mm short at the top): the dark strip between the
  doors (41 mm of it shows; the doors cover 10 mm each side). The drawing gives 393–453 for the bar = centred.
- **Backs** ДВП чёрная, two per height (411 wide = 4.5 mm into the side grooves, meeting at the partition's back edge,
  screwed there with «Шайба ФБ 296»), in grooves at z 16.8–20 (the partition and the fixed shelves start at z 20),
  4 mm into top and bottom: 405 + 1378 = 1775 + 8. They meet at the fixed shelves 7 / 8 (396 × 294, y 537–553), which
  sit behind the door joint (lower doors end at 544, upper start at 546).
- **Fronts** ЛДСП 16 overlay (накладные петли GTV ZP BICN090, 10 pcs = 3 per vitrine door + 2 per lower door), back face
  1 mm off the sides, 2.5 mm in from the ends, 2 mm gaps top / bottom / at the joint. Doors 400 wide, 41 apart.
- **Vitrine doors**: two stiles «Щит двери» 1371 × 100 (outer and inner) and the clear glass 1371 × 304 × 6 screwed
  behind them (silicone bushings «Втулка силиконовая» + screws «4,2×19», 20 pcs): 200 mm of glass shows between the
  stiles, 52 mm hides behind each. Built as two `front` stiles + a `glass` part (z 325–331) moving together, hinge axis
  given explicitly.
- **Glass shelves** 396 × 288 × 6 on shelf pins, at y 1002 and 1463 in both columns (0.08; drawing).
- **Handles** «Ручка-скоба СПА-3 320» black matt (4 pcs): a round bar ~336 long (measured on the site photo: 268 px of a
  320 px = 400 mm door), across the door centre; y 1016.5 on the vitrine doors, 487 on the lower doors (drawing).
  Built as `bar`, band / t 10, post 10, standoff 25.
- **Legs**: «Опора 350×70×128» ×2 — a sled under each end: a 70 × 70 × 3 pad under the bottom at each end of a
  350 run (z 0–70 and 280–350), square posts 30 × 30 (x 20–50 from the end, drawing), and a bar 30 × 25 between the posts
  10 mm above the floor (side view). «Опора 70×70×128» ×1 — a single post 30 × 30 under a 70 × 70 pad in the middle
  (x = L/2, z = B/2). All black metal (`mat: metal`, collection metal black).
- **Coffee table 0.05**: top 1 and bottom 5 1207 × 604; sides 2 (266 × 600) between them, flush with the ends, 2 mm in at
  front and back; **partition 4** ЛДСП чёрный 266 × 500, crosswise at x 688–704 (drawing 689.5), set 50 mm in from front
  and back (the p. 71 photo shows it set back from the front edge); **partition 3** ЛДСП чёрный 266 × 672 lengthwise
  between the left side and partition 4 at mid-depth (z 294–310): two niches of the left bay, one open to the front, one to
  the back; the right bay is open through (the step-3 drawing joins 3 to the middle of 4; the photos show the black
  back of the left front niche and daylight through the right bay). Legs «Опора 465×80×128» ×2: pads 80 × 60 at both
  ends of a 465 run (z 70–534, centred), posts 30 × 30 at x 116–146 / 1061–1091 (near the pads' inner edge, drawing),
  a bar 20 high 8 mm above the floor; «Опора 70×70×128» in the middle (x 700, z 302).

## By-photo modules — built the same way
- **0.09** (845 × 350 × 1535): the 0.08 carcass 1375 high (sides, partition, bar 1373); no fixed shelf, one back per
  column 1383 × 411; left door = the vitrine door (stiles + glass 1371, the same parts as 0.08), right door = a plain
  panel 1371 × 400 (hinged right, photo 3); 3 glass shelves on the left (y 470 / 800 / 1110), 3 ЛДСП loose shelves
  396 × 290 on the right (y 505 / 842 / 1180) — heights read off the open photo (±20 mm, perspective). Handles at
  y 1118 on both doors (photo). Legs as 0.08.
- **0.02 Комод** (1574 × 420 × 925): sides 400 deep; **the top and the bottom overhang the sides by 10 mm each end** (the
  cut-out: top / bottom 74–1195 px, the fronts 82–1188 px; the room photo agrees; the vitrine and the TV unit have no
  overhang) → sides at x 10–26 / 1548–1564. Two doors 500 × 761 (x 12–512 and 545–1045) with the black bar on the
  partition between them (x 528.5), a partition at x 1048 behind the door / drawer joint, and a column of four drawers
  514 wide: fronts 192 / 196 / 196 / 168 from the bottom, 3 mm gaps (cut-out). Drawer boxes (not seen) = the Pinskdrev
  standard: ЛДСП 16 sides and back, ДВП bottom in grooves, 350 runners, 13 mm each side. One loose shelf per door
  compartment at y 520 (assumed). Handles 66 mm under each front's top edge (cut-out: 58–67). Legs: sleds 400 long with
  the posts at x 73–103 from the ends (cut-out), single posts at x 556 and 1000 (cut-out).
- **0.01 Тумба ТВ** (1704 × 420 × 540): two doors 520 × 376 (hinged at the ends) round an open niche 620 wide between
  two **black partitions** (x 526–542 / 1162–1178, their front edges show, full depth to the doors' line) with a black
  back pierced by two cable holes Ø60 on the middle line at y 300 and 413 (cut-out) — a `back` with `shape: path`
  (the rect + two 24-gon holes, even-odd). The niche bottom is the oak bottom (room photo). Handles 66 under the door
  tops. Legs: sleds 400, posts at x 26–56 from the ends; single posts at x 580 / 1124.
- **0.06 Полка** (1370 × 240 × 210, `mount: wall`): a board 1370 × 240 × 16, a back board 1246 × 190 × 16 standing on
  it against the wall (62 in from each end; cut-out: 69 / 57 in, the photo is not quite square), two black flat-bar
  brackets 30 × 4 at x 90–120 / 1250–1280: a strip down the back board's face and a leg over its top to the wall (their
  hooks point inward in the cut-out = the legs going back, seen in perspective). Board thickness 16 assumed (reads
  16–20 on the cut-out).

## Finish and colours
One colour option, `forte-loft-kanzas-antracit` «Дуб Канзас / Антрацит»:
- `body` (carcass, fronts, stiles, shelves): «Дуб Канзас» — a textured decor, provisional **#705b4e**, the p. 71 swatch
  (`catpage.py 71 --swatch 0.785,0.862,0.81,0.905`, flat ±6). It is **the same decor as wave 1's «Дуб Канзас 377 SWN»**
  (Денвер / Ариста, p. 33, provisional #7e6753); listed in `gen/forte-loft_decors.md`. The site's swatch image reads
  #816d54, the product photos #816c53 (studio light).
- `accent` (the bar «Брусок», the coffee table's partitions 3 / 4, the TV niche partitions — «ЛДСП ЧЕРНЫЙ» in the
  instructions, «Антрацит» in the catalogue): **#222b38**, the p. 71 swatch (`--swatch 0.82,0.862,0.845,0.905`, flat ±2),
  a plain colour.
- `back` (ДВП чёрная): the same #222b38 (the catalogue names only the one dark colour; the photos show the backs dark
  blue-grey).
- `metal`: black (handles, legs, shelf brackets). Glass: clear.

## Cut lists
- 0.08: transcribed from p1 (200 dpi). **Row 15 «Щит двери» is printed 398 × 100 — a misprint of 1371 × 100**: the
  exploded view labels 13 + 15 on the left vitrine door and 12 + 14 on the right one, each vitrine door is two 100 mm
  stiles 1371 high (front view and photos), and no 398 stile exists. Corrected in `gen/cutlists/forte-loft-0-08.json`
  with the reason in its "source". The table has no thickness column (ЛДСП 16, glass 6 as the material says).
- 0.05: transcribed from p1; matches the drawing exactly.

## Engine / checker limits for the lead
- **Bar handle posts**: the engine sets the posts at ±0.4 d from the centre (0.8 d apart). The СПА-3 is a скоба with
  its bent ends 320 apart; with d 336 the posts stand 269 apart (on the stiles anyway). A `post`-spacing field (or
  "posts at the ends") would make a скоба exact.
- preview2d draws a `bar` as a disc of diameter d and counts ±d/2 in the extent: the chest and the TV unit print false
  «габарит H … только из-за ручек» notes, and the overlays of 0.02 / 0.01 needed their ref-box stretched upward
  (the extent then includes the discs) — the red edges sit on the cut-outs.
- preview2d does not know finish roles (`accent`) or `black` metal: the sheets draw the black bar / partitions in the
  body colour and the legs light grey; the back's cable holes are not drawn (the engine cuts them: even-odd outline).
- Legs are built as metal boxes (pads, square posts, bars) — no rod needed; a sled is 5 boxes.
- The glass of the vitrine door stands behind the stiles (z 325–331), 1 mm clear of the sides' front edge.

## Uncertain / to review in 3D
- 0.09 shelf heights, 0.02 loose shelves (assumed), 0.02 drawer-box heights (front − 46), 0.02 / 0.01 leg positions
  (±10 mm from the low-res cut-outs), the TV niche back as ДВП (could be ЛДСП чёрный), 0.06 board thickness.
- The chest's 10 mm top / bottom overhang rests on two source pixels of the cut-out plus the room photo.

## Skipped
Nothing: the collection has no chairs or upholstered pieces.
