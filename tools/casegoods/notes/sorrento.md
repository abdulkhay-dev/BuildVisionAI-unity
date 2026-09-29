# «Сорренто» (sorrento, П6.949) — notes

Catalogue p. 113 (PDF; printed 222–223): one bedroom photo, no module cut-outs, no swatch. All 5 articles have an
instruction (P6-949-1-0x, downloaded to tools/casegoods/.cache/is/ to read the assembly steps), so **every module is by
instruction**. Generator `gen/sorrento.py` (writes the 5 designs and `gen/sorrento_catalog.json`), decors
`gen/sorrento_decors.md`, corrected cut list `gen/cutlists/sorrento-1-05.json`, sheets `pilot/sorrento-*.png` (all ok).

| id | code | what | overlay on the sheet |
|---|---|---|---|
| sorrento-1-01 | П6.949.1.01 | шкаф-купе 3Д 2000×650×2300 | none (the interior was checked against the site's scheme SHkaf-Shema.jpg: shelves, hat shelf, mezzanine, rails all sit on it) |
| sorrento-1-02 | П6.949.1.02 | комод 1084×385×1228 | the site's front-on photo 8C3A1979.jpg — fronts, handles, feet on it |
| sorrento-1-03 | П6.949.1.03 | зеркало 1000×21×700 (wall) | none needed (board + mirror) |
| sorrento-1-04 | П6.949.1.04 | тумба прикроватная 424×382×445 | the site's front-on photo 8C3A1962.jpg |
| sorrento-1-05 | П6.949.1.05 | кровать 2-16 (сп. место 2000×1600) | none (no front view exists) |

## Construction (from the instructions and the product photos)
- Cabinets: ЛДСП 16 «Дуб Бордо лайт»; the top and the bottom run the full width and depth, the sides stand between them,
  the bottom on 20 mm grey block feet «k16» (4 on the bedside, 5 on the chest: the fifth under the partition).
  H = 20 + 16 + side + 16 exactly (445, 1228).
- Backs ХДФ 3.5 are **nailed on the rear** (step 5 of the bedside: 16 nails «l»; they are 4.5–7.5 mm smaller than the
  carcass each way). The catalogue depth is the top's: sides 365 + front 16 + 1 = 382 (bedside), 385 for the chest (its
  top overhangs the fronts by 3). To keep the extent = B the back is drawn in the carcass's rear 3.5 mm (a `back` may
  overlap panels) — **the real piece is 3.5 mm deeper than the catalogue B**; in 3D the back's face is flush with the
  carcass's rear instead of standing 3.5 proud.
- Fronts ЛДСП 16 overlaid on the sides' front edges between the top and the bottom, 3 mm gaps. Chest: the partition 3
  (360 deep) stands under the joint of the drawer column (708) and the door (367, right hinges, 3 hinges a2), two
  shelves 6 behind the door at thirds; drawers 3 × 336 + 155 = the door's 1172 with 3 mm gaps. Bedside: a fixed shelf 5
  under an open niche, one drawer.
- Drawer boxes: the sides are screwed to the front (no inner front), a back between the sides, the ХДФ bottom in the
  sides' grooves; 350 runners, 13–14 mm per side.
- Colours of the fronts (photos): the chest's small top drawer 8.1 and the bedside drawer are «Дуб Монастырский» (role
  `accent`), everything else Бордо лайт.
- Handles «k1»: a square satin-aluminium pull ≈ 44 × 44 (a plate bent off the face), in the middle near the top edge; the
  door's pull is 48 mm from its free edge at the height of the top drawer's pull (photo).
- Coupe wardrobe 1.01: sides / top / bottom ЛДСП 25; sides on 4 mm glides «n» (2271 + 25 + 4 = 2300), top over the
  sides, bottom 25 between them on a 65 mm plinth (front strip set back 14, back strip). Partitions 3 / 4 (544 deep) at
  x 670.5 / 1313.5 give the scheme's 645 / 627 / 645 sections; hat shelf 8 over the whole width at 1908; the mezzanine
  (351) split by the upright 5 into 966 + 966 (the scheme). Middle column: 4 shelves (9 × 626 and 10 × 624 alternating,
  5 equal openings — they sit on the scheme's lines); rails «w1» 636 in the side sections. Backs ХДФ in the 25 mm sides'
  8 mm grooves: three 1847 pieces below (joints on the partitions) and two 377 × 992 above the hat shelf. Front rail 11
  (80) under the top hides the top track.
  Doors: three sliding doors 672 × 2165 (13, 14, 15) on a double aluminium track (F6), the outer ones on the rear track,
  the middle one on the front track (its edge profiles overlap the outer doors in the photo). Aluminium edge profiles
  «j9» (4, 2165 long): the outer edges of the outer doors and both edges of the middle door. The middle door carries a
  mirror in two panes with a «Монастырский» insert between them (y 797–1043 over the door's bottom, 480 wide, 96 margins,
  measured on the product photo): mirrors and insert 4 mm on the leaf. Moves: `slide` ±639.
- Bed 2-16: headboard 1 (1664 × 966 × 25) on 4 mm glides with the «Монастырский» strip 1.1 (217, 16 thick) 50 mm under
  its top (photo), side rails 3 / 3.1 (25 × 200 × 2010) between the headboard and the foot board 2 (322), their tops
  flush with the foot board. Metal base «m» 2000 × 1600 (black tubes, middle beam, two legs, 24 slats per half) and a
  mattress 200. The size is stored [1664, 2060, 970] (x = width), as for the other beds.
- Mirror: board 700 × 1000 × 16 (landscape as in the photo) with the 960 × 660 × 4 mirror on 1 mm tape = B 21.

## Finishes
One colour option «Дуб Бордо лайт 380» / «Дуб Монастырский 375» → `sorrento-bordo-monastyr`: body = front = Бордо лайт
#e7e7e1 (no swatch on p. 113: Агата's swatch of the same decor, p. 27 crop 0.675,0.865,0.73,0.905; the p. 113 photo
reads #d5d5d5 in the room light), role `accent` = Монастырский #5c4c44 (no swatch anywhere in the catalogue: the mean of
the site's front-on bedside photo #50443d and the p. 113 photo crop 0.875,0.73,0.93,0.80 #62534c). Both are decors (listed
in `gen/sorrento_decors.md`). Metal `chrome` (satin-aluminium pulls, door profiles, tracks, rails); block feet grey
#8f9194, glides and the bed base black.

## Cut lists
- 1.05 row 3.1 is printed 2010 × **2000** × 25 — a misprint for 200 (the second side rail): corrected in
  gen/cutlists/sorrento-1-05.json with the reason. All other tables were complete in the reference JSON.

## For the lead (engine / checker limits)
- Nailed backs vs catalogue depth (above): the design keeps B and embeds the back; decide whether B should be +3.5.
- The square bent pull is a `bar` with square posts, band = d = 44 (a flat square plate); the real pull curls off the
  face at its lower edge. A "plate" handle model would be closer.
- Coupe door edge profiles are thin face strips (the real C profile wraps the door edge); the mirror panes' thin
  bevel frame line (photo) is not modelled.
- check.py draws the `accent` insert in the default front colour on the sheets.

## Skipped
Nothing (no chairs or upholstered pieces in the collection).
