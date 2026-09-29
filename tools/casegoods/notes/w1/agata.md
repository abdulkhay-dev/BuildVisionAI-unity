# «Агата» (slug `agata`) — wave 1

Catalogue «Корпусная мебель ч. II» 2025: p. 26 (БМ8.986.*, two bedroom interiors, close-ups of a drawer handle in both
colours) and p. 27 (П8.986.*, the living-room interior, the module cut-outs, the colour swatches). Generator
`tools/casegoods/gen/agata.py`, catalogue fragment `gen/agata_catalog.json`, decors `gen/agata_decors.md`, sheets
`pilot/agata-*.png`.

## Modules (15 designs, all by catalogue)

No Agata article has an instruction (index.json has no `pdf` for the collection, `reference/agata/` does not exist), so
every module is **by catalogue**: measured off the p. 27 cut-outs with the catalogue size as the scale, checked against
the p. 26 / p. 27 interior photos. П8 and БМ8 are the same pieces (the photos of p. 26 show the same wardrobes, bed,
dressing table, nightstand and mirror as the cut-outs of p. 27); the БМ codes that collide get `agata-bm-…`.

| id | code | ref on the sheet |
|---|---|---|
| agata-0-01 | П8.986.0.01 шкаф-витрина, door hinged left | cut-out p. 27 (front-on) |
| agata-0-01-01 | П8.986.0.01-01 шкаф-витрина, door hinged right | cut-out p. 27 (front-on) |
| agata-0-02 | П8.986.0.02 тумба ТВ | cut-out p. 27 (slightly from above) |
| agata-1-01, agata-bm-1-01 | тумба прикроватная | cut-out p. 27 at 3/4 — rough only |
| agata-1-02, agata-bm-1-02 | стол туалетный | cut-out p. 27 (front-on) |
| agata-1-03, agata-bm-1-03 | зеркало (wall) | cut-out p. 27 (front-on); the preview draws a shaped panel as its box, the opening outline was overlaid separately and sits on the drawing |
| agata-1-04-01, agata-bm-1-04-01 | шкаф 4Д | cut-out p. 27 (front-on) |
| agata-1-06-01, agata-bm-1-06-01 | шкаф 3Д | cut-out p. 27 (front-on) |
| agata-1-05, agata-bm-1-05 | кровать 2-16 | cut-out p. 27 at 3/4 — rough only |

Every sheet prints ok (the handle "примечание" lines: bars stand out of B as the rule says). The sheets are drawn in the
white finish (`--finish agata-bordo-light`): with the dark Береза the whole view is below the overlay's edge threshold and
turns red.

Skipped: nothing (the collection has no chairs / upholstered pieces).

## Construction (one scheme for the collection)

- Carcass ЛДСП 16, the top over the sides, the bottom between them, ХДФ back 3.5 in grooves 6 mm from the back edge.
- Fronts 18 mm overlaid on the carcass with a 12 mm reveal of the carcass edges round them (the grey side / top / bottom
  edges of the photos and the close-up), 3 mm gaps. B = carcass + front; tops run the full depth B.
- Handles: long satin bars right under the top edge of every drawer and door front (the p. 26 close-up: the bar sits on the
  top edge of the lower front) — 360 (vitrine drawer), 356 (TV doors), 348 (TV drawer), 280 (dressing table, nightstand);
  vertical bars 750 on the plain wardrobe doors at their free edge, centre 685 above the floor; 210 on the vitrine door.
  The mirror doors and the dressing table's middle drawer have no handle (none in any photo).
- Cabinets stand on bent flat metal bracket legs 100 high: outer edge flush with the side, 134 wide under the carcass, a
  concave curve down to a 45 mm foot (drawn as a `shape: path` outline in the front plane, 20 mm plate). The dressing
  table has them at both edges of each pedestal.
- Wardrobes: sides to the floor, a 50 mm plinth (front + back boards) under the bottom; four / three equal doors 460 wide,
  full overlay, up to 2 mm under the top. Mirror doors: a 4 mm mirror glued on the front leaving a 40 mm wood strip on the
  hinge side (the strips in the cut-outs); hinges read off the strips: 4Д — L, L, R, R with partitions behind the joints
  1|2 and 3|4 (shelves left and right, rail + hat shelf in the middle pair); 3Д — L, R, R with the partition behind 2|3
  (rail in the left pair, shelves right). Carcass depth = B − 18 − 4 (the mirror is the front-most face).
- Vitrine: fixed top panel 1777–2031 (no handle), one door 321–1774 = a solid bottom panel (to the fixed shelf at 652)
  under a glazed part (narrow 14 mm frame, clear glass) — the door handle sits at 978, i.e. the leaf includes the solid
  part; a drawer 113–318; two glass shelves with an LED clip each (the green edge light of the photo), a puck under the top
  compartment.
- TV unit: doors 12–528.5 and 1131.5–1648, partitions behind the joints 530 / 1130, the middle an open niche over a drawer
  (113–300), a shelf in each door section; legs only at the ends (as in the photo).
- Dressing table: top 1645×420 over two 500 wide pedestals of three drawers, a 85 mm middle drawer on runners between them,
  a modesty panel at the back of the knee hole.
- Mirror: frame board 18 with an opening 50/49/47/56 from the edges and R155 at its top-right corner, mirror 4 behind.
- Bed (x = width 1670, z = length 2247, like Flora's bed): headboard board 25 to H1000, two upholstered pads between side
  wings whose front edge curves back to the top, rails 25 (70–330), a head cross rail, cleats + a middle beam on two legs,
  24 slats, mattress 1600×2000×200, four chrome trapezoid block feet 70 high set in at the corners.

## Finishes

- `agata-bereza` «Береза 261 SM»: swatch p. 27 crop 0.755,0.865,0.81,0.905 → #4b3c3b (p. 26 close-up #433735).
- `agata-bordo-light` «Дуб Бордо лайт 380 SWN»: swatch p. 27 crop 0.675,0.865,0.73,0.905 → #e7e7e1.
  Note: the catalogue labels the white swatch «Дуб Бордо лайт» and the dark one «Береза» (p. 27), and the p. 26 captions
  agree (white room — Дуб бордо лайт, dark room — Береза); kept as written.
- Both are textured decors (provisional plain colours, listed in `gen/agata_decors.md`). One decor per finish for the
  carcass and the fronts: in the Береза photos the sides and tops sometimes read plain grey, but that is the gloss
  reflecting the room (the wardrobe side and the bed rails show the grain) — the lead may want to check this.
- Metal (handles, legs, bed feet): `chrome` (satin in the photos).

## Engine / tool limits for the lead

- High-gloss decors: both finishes are lacquered to a mirror gloss; a finish can only give a plain `gloss#` or a decor, not a
  glossy decor. Provisional colours are matte `door_enamel_whitey`.
- The carcass edge band reads grey/silver next to the fronts in the Береза close-up — no edge-band colour in the format.
- The edge bar handle really sits on the front's top edge (a cap profile); modelled as a `bar` on the face just under the
  edge.
- The upholstered headboard pads lean back in the photos; `soft` is an axis-aligned box.
- preview2d draws `bar` handles as circles of the bar's length and widens the view extent by them (the sheets pad the
  reference crop to line up); it draws `shape: path` parts as their box (the mirror's opening, the curved legs).

## Sizes

- index.json matches the catalogue for all 15 codes. БМ8.986.1.06-01 is B600 in the catalogue (p. 26) against B605 of
  П8.986.1.06-01 (p. 27) — built as written (carcass 578 instead of 583); probably a typo of p. 26, worth a look.
- The bed: catalogue L2247 (length) × B1670 (width); the design is [1670, 2247, 1000] (x = width) like flora-1-05.
