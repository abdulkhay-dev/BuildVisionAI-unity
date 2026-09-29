# «Бритиш Бум» (british-bum, П3.0551) — wave 5b

Catalogue pp. 129–131 (printed 254–259): p. 129 interior (3д 1.25, комоды 1.27 / 1.13, угловой стол 2.17, кровать 1-12),
p. 130 interior (полка 2.18 on стол 2т 2.15, шкаф 1.01, 2д 1.06, the loft bed 1.23 with the 1-08 bed under it), p. 131:
front-on cut-outs of every module, the swatches «Крем» (фасад) / «Дуб Трюфельный» (каркас) and «Рисунок на фасаде методом
цветной фотопечати». No assembly instructions exist. The site (pinskdrev.by, «Бритиш» П551.xx) has photos of 1.13, 1.27,
1.03, 1.04 (+ a dimensioned drawing), 1.09 (+ a drawing, an open photo), 2.17 / 2.17-01.

Generator `tools/casegoods/gen/british-bum.py` (19 designs + `gen/british-bum_catalog.json`), decors and prints in
`gen/british-bum_decors.md`, print crops in `gen/prints/british-bum/`. Sheets `pilot/british-bum-*.png`: all 19 print
"ok"; refs = the site photos (1.13, 1.27, 1.03, 1.04, 1.09) and the p. 131 cut-outs extracted at their native resolution
from the PDF (the others; 2.17-01 against the mirrored 2.17 cut-out). The cut-outs are ≈ 0.13–0.17 px/mm and printed
~18 % wider than true (x and y scaled separately); the beds, the loft, the desks and 2.18 are 3/4 views, so their overlay
is a rough check only.

## Construction (common, measured on the site photos of 1.13 / 1.27 / 1.03 / 1.04)
- Carcass ЛДСП 16 «Дуб Трюфельный». Sides stand on the floor with a skirting notch ≈ 50 × 50 (curved) at the back bottom
  (the 1.04 side-view drawing, the 1.13 3/4 photo) — `shape: path` in the side plane. The top 16 lies over the sides
  (full width, flush front). The bottom 16 between the sides at 72…88, on a plinth board 72 high flush with the fronts.
  ХДФ back 3 **nailed on** over the back edges (z 0…3; carcass z 3…B), cream as the niches photograph.
- **Inset fronts** «Крем» 16 between the sides, flush with the carcass front: 2 mm off the sides, 3 mm gaps, the lowest
  front from 90, 3 mm under the top (1.13: 207 / 205 / 206 on the photo → three equal 211 fronts; 1.04 drawing: door
  1880, drawer 210 → 90–300 / 304–2184). A fixed shelf stands behind every door/drawer joint.
- Handles: arched bow «скоба», satin chrome, ≈ 184 long (182 on the 1.13 photo) — built as the engine's straight `bar`
  on two posts (c-c ≈ 147). Centred on drawers; upright 22 mm from the meeting edge on wardrobe doors at y ≈ 1060–1125
  (measured per module); horizontal near the bottom edge of short top doors (1.01, 2.18, the loft's cabinet) and near
  the top edge of the 2.15 pedestal doors; the 1.04 / 1.09 door handles upright by the left edge (drawings).
- Drawer boxes ЛДСП 16, ХДФ bottoms, 13 mm runner gaps; rails Ø25 chrome, hat shelves at 1790.

## Modules
| module | source | layout |
|---|---|---|
| 1.25 шкаф 3д 1346×580×2200 | cut-out p. 131, interior p. 129 | 3 doors 434.5 (joints 454 / 892), partition behind 892; left section hat shelf + rail, right 3 shelves + hat shelf; doors hinge L / R / R; flag+England on door 1, lantern+London on door 3 |
| 1.25-01 … ×2205 | cut-out p. 131 | the same, doors to 2186; mirror 340 × 1608 on door 2 (502…2110), 1 mm proud of the door (B stays 580 ±1) |
| 1.06 шкаф 2д 908×580×2205 | cut-out p. 131, interior p. 130 | left door 516…2186 over two drawers, right door full height 90…2186; partition at 454; left shelves, right hat shelf + rail; the St Paul's skyline across both doors |
| 1.07 шкаф 908×434×2205 | cut-out p. 131 | two doors 516…2186 (no partition) over two full-width drawers; shelves; balloons + bridge / Big Ben |
| 1.01 шкаф 470×434×2205 | cut-out p. 131, interior p. 130 | two drawers, open niche 534…1484 with two shelves, a door 1503…2186 (shield + sword), handle horizontal 55 over its bottom edge |
| 1.04 шкаф 470×434×2205 | site photo + drawing П551.04 | drawer 90…300, door 304…2184 (1880 as drawn), shelves at the drawing's 683 / 1060 / 1438 / 1811 |
| 1.03 шкаф комбинированный 908×434×2205 | site photos П551.03 (front-on, open) | two-drawer chest (top at 534, full depth); on it a stepped tower 290 deep: ЛДСП back wings 48…860 to 2132 and the middle to 2189, a column 206…702 to 2205, two full-width boxes 13…895 crossing it — a drop-down flap 857…1204 and two doors 1489…1822 (dividers at the column sides); football + England on the left door, the stamp on the upper drawer |
| 1.09 шкаф угловой 759×759×2205 | site photos + drawing П551.09 | see «Corner wardrobe» below |
| 1.27 комод 910×434×1074 | site photo П551.27, cut-out p. 131 | 5 drawers 203 / 203 / 213 / 203 / 131 bottom up (the middle one ≈ 10 taller on both sources); balloons on 2–3, England on 4 |
| 1.13 комод 910×435×749 | site photos П551.13 | 3 equal drawers; the skyline on the lower two |
| 2.17 стол угловой 1340×890×749 | site photos П551.17 / 17-01, cut-out p. 131 | L top (`shape: path`): 590 deep along the back, the right 300 (x 1040…1340) coming forward to 890, a concave curve at the inner corner; pedestal 404 at the left (niche 534…733 over a fixed shelf, drawers England / bus); modesty panel 490…733 at the back; the return on two leg panels facing front (at z 858…874 and at the back), 20 in from its edges |
| 2.17-01 | site photos П551.17-01 | the mirror image (generated by mirroring x) |
| 2.16 стол 1100×590×749 | cut-out p. 131 | a leg panel at the left, the 2.17 pedestal at the right, modesty panel |
| 2.15 стол 2т 1400×590×749 | cut-out p. 131, interior p. 130 | two pedestals 430: a short drawer 580…730 over a door 90…577 (a fixed rail behind the joint, a shelf); Tower Bridge on both doors, «Wow» on the left |
| 2.18 полка 1340×340×1124 | cut-out p. 131, interior p. 130 | a hutch (mount wall): left side, a 3-compartment shelf block (bottom at 750, ЛДСП back) over an open window, a back stretcher 100 at the bottom; right column 958…1340: umbrella door 442…1105, an open niche between fixed shelves, a small drawer 18…121 |
| 1.20 кровать 1-08 2042×839×650 | cut-out p. 131, interior p. 130 | see «Beds» |
| 1.34 кровать 1-08 2042×839×800 | cut-out p. 131 | 1.20 + a buttoned back cushion — see «Size decisions» |
| 1.32 кровать 1-12 1244×2092×850 | cut-out p. 131, interior p. 131 | x = width, z = length: headboard board 850 with a buttoned upholstered panel (500…820, `soft` tufts 9×2), side boards and a foot board 400 to the floor, ЛДСП base 264…280 on a middle support, mattress 1200×2000×200 |
| 1.23 кровать двухъярусная 2981×890×2205 | cut-out p. 131, interior p. 130 | see «Loft bed» |

### Beds 1-08 (1.20 / 1.34)
Written along the length (x = length 2042, z = depth 839; the drawers' side is the front, as the catalogue draws them
and as the lead's other beds are not: note it when placing). End boards 16 with a rounded front-top corner (R 200,
`shape: path`), the back board 60…650, a front rail 312…442, an ЛДСП base 426…442 on a middle support, two under-bed
drawers 20…300 (fronts 993 × 280: bus + stamp, London Eye + England), mattress 2000×800×120. The drawers have no handle on
any source — the grip is the shadow gap under the rail. 1.34 adds a buttoned cushion (`soft`, tufts 17×3, 470…800) on a
hidden backing board.

### Loft bed 1.23
Built as shown (stairs on the left; «возможна право- и левосторонняя сборка» — the right-hand one is the mirror image,
not built). The lower 1-08 bed in the p. 130 photo is a separate article (1.20).
- Stair-chest 0…500: four steps rising from the front to the back (bands 178 deep, treads at 370 / 680 / 990 / 1300,
  the landing at the bed's level 1500). Each riser is a cream drawer front; each tread runs back to the back so the
  drawers are deep (560). S-curved left side (`shape: path` through the nosings).
- Big Ben wardrobe column 500…960 under the bed's head end: door 90…1481 (Big Ben + «Big Ben»), horizontal handle at
  790, 3 shelves.
- Bed: ЛДСП base 1484…1500 from 500 to the right end panel; the printed front board 1484…1720 (London rail print on a
  panel — the engine prints on any board), rounded at the head end; the head end board (rounded); a back rail to 1860;
  mattress 2000×800×120 at x 516…2516.
- Guard cabinet 2516…2981 over the bed's foot end (door 1502…2186, the guard print, handle at the bottom), on the
  full-height right end panel 2965…2981.
- Under the bed: an ЛДСП back panel 750…1484 and a rack (shelf at 1184…1200, 250 deep, 4 dividers → 5 compartments).

### Corner wardrobe 1.09
The site drawing (door 432 × 2094, handle upright by the left edge) and the open photo show a **470-wide carcass box set
diagonally** (the back parallel to the door, cream ХДФ; hat shelf, rail, two shelves as drawn) and two big wing panels
square to the walls. With the catalogue's 759 × 759 along the walls the wings are 426.7 deep and the box's back corners
touch both walls. **Written in the door's axes** (x along the door, z from the carcass back to the door): extent
1073.4 × 603.4 × 2205 (1073.4 = 759·√2; the room corner lies 235 behind the back's middle). The model's `size` is that
extent (the catalogue's 759 × 759 is in the note); set it into a corner turned 45°. Only the two wings are turned
(`rot` y ±45°, the skirting notch in their outline). Reason for this frame: in the wall frame every part of the box
(sides, shelves, rail, door) would be turned, and the checker tests turned parts by their bounding boxes — every one would
"overlap" its neighbours. For the same reason the wings start 16 mm behind the box's front corners (a mitred joint reads
as an overlap): the lead may close that 11-mm slot in 3D.

## Finish and colours
- `british-bum-krem-tryufel` «Крем / Дуб Трюфельный» (the only colour option):
  - `front` #e0d6cd — p. 131 swatch «Фасад», `catpage.py 131 --swatch 0.68,0.85,0.73,0.89` (flat ±0.5).
  - `body` #786657 — provisional, p. 131 swatch «Каркас» `--swatch 0.755,0.85,0.81,0.89` (±13.5: a decor) → listed in
    `gen/british-bum_decors.md`.
  - `back` #e0d6cd — the ХДФ backs photograph cream in the niches (2.17 pedestal, 1.01, the 1.09 interior); the ЛДСП
    backs of 1.03 / 2.18 / the loft's rack are `body`.
  - roles `fabric` #9e958e (1.34 cushion, p. 131 cut-out) and `fabric_light` #bfbbb2 (1.32 headboard).
- metal: chrome (the satin bow handles, rails).

## Printed fronts
26 motifs `british_bum_<motif>` on 29 fronts / boards, all listed with sizes, sources and quads in
`gen/british-bum_decors.md`; crops in `gen/prints/british-bum/<motif>.png` (site photos where they exist — 1.03, 1.04,
1.09, 1.13, 1.27, 2.17 —, otherwise the p. 129 / 130 interiors at 300 dpi rectified by the four corners, and the p. 131
cut-outs for 1.07 and the 1.06 right door). **The materials do not exist yet: every design with a print throws «нет
материала печати» in the engine until the texture wave makes them** (1.32 is the only module without a print). The crops
still show the handles and the photos' shading.

## Size decisions
- 1.27: p. 129 writes L908, p. 131 L910 (as 1.13, and the site: 910) → 910; H 1074 by the catalogue (site 1095; the site
  photo measures ≈ 1080–1095 — the catalogue wins). B 434.
- 1.25 H2200 vs 1.25-01 H2205: the 5 mm went into the doors (to 2181 / 2186); the cut-outs cannot tell where.
- 1.34: the catalogue writes H650 for both 1-08 beds, but the 1.34 cut-out shows the buttoned cushion ≈ 150 over the end
  boards, which are the same as 1.20's → built to the picture, **H 800**, model size [2042, 839, 800] with a note. If the
  lead prefers 650, lower the cushion (it then only covers 470…650).
- 1.09: size in the door's axes (above).
- 1-08 beds x = length (the catalogue's L2042 is the length); 1.32 x = width (L1244) like the other beds.

## Engine limits for the lead
- The bow handles are arched; the engine's `bar` is straight (an `arch` / bow model would match 16 modules).
- The corner wardrobe: the checker would need turned-part overlap tests by their real outlines to allow the natural wall
  frame; now the design is in the door's frame and the wings leave a small slot at the front corners.
- `print` materials missing (above). The prints are fitted to the whole front face; a front whose picture continues on
  the neighbour (skylines) relies on the two crops meeting at the joint.
- The lift/hinge side of the short top doors (1.01, 2.18, the loft cabinet) is not visible anywhere: built as side-hinged
  doors with the handle centred at the bottom; they may be lift-up flaps.

## Skipped
Nothing: 19 of 19. No chairs on these pages.
