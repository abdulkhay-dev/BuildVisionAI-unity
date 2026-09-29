# «Хольтен Лофт» (holten-loft, П3.0579) — 5 designs, all by instruction

Generator `tools/casegoods/gen/holten-loft.py` (designs, `gen/holten-loft_catalog.json`, cut lists
`gen/cutlists/holten-loft-3-xx.json` transcribed from the pictures). Sheets `pilot/holten-loft-*.png`, all ok, each overlaid
on the instruction's front view (cover page).

## Instructions
index.json has a pdf only for the mirror 3.50. The other four exist on a.pinskdrev.ru under the same file-name pattern:
`IS-Holten-tumba-10-1.pdf`, `IS-Holten-shkaf-01-1.pdf`, `IS-Holten-veshalka-40-1.pdf`, `IS-Holten-tumba-60-1.pdf`.
I downloaded them to `tools/casegoods/.cache/is/` and wrote `reference/holten-loft/cutlists/holten-loft-3-{01,10,40,60}.json`
(empty rows — no text layer) and `pages/*-p1…p4.png`, `*-cover.png` like prepare_refs.py does. **For the lead: add their
"pdf" to index.json** (I did not touch it). All tables have the 4th format (name, marking, material, count, L × W): the
material gives the thickness and the decor of every part.

## Construction
- Carcass ЛДСП **22** «Дуб Стирлинг»: top and bottom over the full size (963 / 802 × 374), sides 373 deep between them;
  inner width L − 44 (the tables: 585 + 16 + 318…).
- Plinth ЛДСП 22 × 40: front and back boards L − 80 (L − 82 on the wardrobe: 41 in), ends 290 between them; recessed 40
  at the front, flush at the back (step 5 / step 2 diagrams). 40 + 22 + 1004 + 22 = 1088 (3.10), 40 + 22 + 1916 + 22 =
  2000 (3.01). The drawings add 4 mm (1092 / 2004 / 496) — the nail glides «опора гвоздь», not modelled.
- Inner panels ЛДСП 16 «Антрацит» (partitions, horizontal walls, shelves) 322 / 332 deep from the back; backs ХДФ 3
  «графит» in grooves, split behind a partition (3.10: 328 + 597 at the partition 9; 3.01: 230 + 535 at 7).
- Fronts МДФ 16 inset flush (3.01's oak door МДФ 18); 3.01 mirror door = anthracite board 16 (1908 × 428) with the mirror
  1904 × 424 on it.
- 3.10: the pinwheel of the drawing — flap 589 × 362 top-left, door 319 × 634 top-right, door bottom-left, flap bottom-right
  round an open niche 251 × 256; partitions 9 / 10 (630) and walls 7 / 8 (585) interlock exactly as the table's sizes
  require. Flaps fold down on bar stays (hardware 001), doors on side hinges.
- 3.60: seat cushion over a drawer (front 590 × 214 МДФ, box ЛДСП 16 «Дуб Артизан» 300 × 100, bottom ХДФ 538 × 305) with an
  open niche over it (wall 9) and a door 319 × 364 right of the partition 8.
- 3.40: wall board 1298 × 963 × 22, shelf tray (horizontal 913 × 252, ends 252 × 64, front 963 × 64), soft back pad
  963 × 250 × 40 at the bottom, 2 hanger arms (001) and 3 double hooks (009) as black rods.
- 3.50: anthracite board 963 × 672 with the mirror, oak strips 64 × 22 top and bottom (depth 22).
- Handles: black tab pulls over the front edge (photo p. 134, the notches on the drawings) — engine `edge` handle
  (band 55, length 32, t 2.5), turned ±90° about z for side edges. 3.01's tab sits on the mirror door's left edge; the oak
  door 14 has a notch in its edge to clear it (step 10 drawing).

## Finishes
- `holten-loft-lancelot-stirling` «Дуб Ланцелот / Дуб Стирлинг» (the only option): body «Дуб Стирлинг» #755a4a (p. 134
  «Каркас», crop 0.813,0.856,0.875,0.905), front «Дуб Ланцелот» #997658 (p. 134 «Фасад», crop 0.735,0.856,0.795,0.905),
  back ХДФ «графит» #3a3b3d, role `inner` «Антрацит» #3f4144 (a uni board; the photo's niche is in shadow), role `drawer`
  «Дуб Артизан» #a2825f (no swatch), role `fabric` velvet#645c4d (seat, p. 134 photo). Metal: black. Decors in
  `gen/holten-loft_decors.md`.

## Decisions for the lead
- The instructions name the fronts «МДФ ДУБ СТИРЛИНГ»; the catalogue says «Фасад: Дуб Ланцелот» → the finish follows the
  catalogue (front role = Ланцелот).
- 3.60: catalogue H502, table: cushion «40 мм», drawing 496 → cushion built 50 (compared by two sizes in the cut list).
- 3.01: the rail «штанга» (014) under wall 12; the 4 shelves 11 in the left column (they are optional per the catalogue).

## Engine limits
- The notches cut into the fronts' edges for the tabs are not modelled (a `shape: path` notch would be possible, but the
  tab would then need to sit in it; left as a flat front with the tab on it).
- Bevelled mirror edges (3.50, 3.01) not modelled.

## Skipped
None.
