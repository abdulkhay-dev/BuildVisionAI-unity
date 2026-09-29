# «Ардо» (ardo, П3.598) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF p. 97 (printed 190–191): a living room shot nearly front-on, the module
cut-outs with sizes, the swatch «Белый» / «Дуб мадура». No module has an instruction, so **all 9 are by photo**
(«по фото, без инструкции»). The site (pinskdrev.by) has a page for every module: two or three studio photos each —
one front-on (the overlay reference of every check sheet) plus 3/4 and open-door shots that show the interiors. All
site sizes agree with the catalogue.

Generator `tools/casegoods/gen/ardo.py` (re-runnable: writes the 9 designs and `gen/ardo_catalog.json`); decors
`gen/ardo_decors.md`; sheets `pilot/ardo-*.png` — all 9 print `ok`. No cut lists (no instructions).

## Construction (read off the photos, the same in every cabinet)
- Carcass ЛДСП 16 «Дуб мадура»: top and bottom over the full width and depth 420, the sides between them (their edges
  show beside the fronts from bottom to top). Partitions and shelves oak, set back behind the fronts (z 10…402). Backs
  white ХДФ in grooves (z 6…9.5) — the open shelves and the vitrine show a white back.
- Fronts ЛДСП 16 white, **inset** between the sides flush with the carcass front (2 mm gaps to the carcass, 3 mm between
  fronts); the joints sit over the partitions.
- **The pilaster strip** (the collection's motif): 152 mm (135 on the wall shelf) of oak made of three boards with two
  dark 5 mm lines between them. Built as three oak front boards + two black 5 mm strips set 2 mm below the face (reads
  as dark grooves). Where it sits:
  - glued to a white door as one front: 0.02 (strip at the door's free edge, the knob on the strip's middle board),
    0.03 (same), 0.07 (strips at the outer edges of both doors — the open photo shows the doors hinged on the sides with
    no column behind the strip);
  - **fixed** in front of a narrow closed column: 0.01 / 0.01-01 / 0.06 — the open-door photo of 0.01 shows the door
    hinged on an oak partition, and the 3/4 photo of 0.06 shows the shelves ending at that partition. Partition at
    x 454…470 behind the joint (x 462), strip 463…616.
- Knobs: black round, Ø30, 20 standoff. Legs: black square 40 × 40 × 100, 30 in from the corners; the 5th leg of the
  wide pieces (0.02, 0.03, 0.07) is at mid-width / mid-depth (the photos show it set back from the front legs).
- Drawer boxes: white ЛДСП 16, ХДФ bottom in grooves, 13 mm runner gaps.

## Modules
| id | code | notes | overlay reference |
|---|---|---|---|
| ardo-0-01 | П3.598.0.01 Шкаф-витрина | door = white 348 top + frameless clear glass + white 429 bottom, hinged right on the partition; knob on the glass; fixed oak shelves at the door joints (y 530, 1576), two glass shelves; the strip fixed on the right | site front photo |
| ardo-0-01-01 | П3.598.0.01-01 Шкаф-витрина (зеркальное отражение) | mirror image of 0.01 (strip left, door hinged left) | site front photo of 0.01-01 |
| ardo-0-06 | П3.598.0.06 Шкаф | open oak shelves (3 loose + a fixed one over the door), a white door **without a knob** (push-to-open assumed), fixed strip right | site front photo |
| ardo-0-02 | П3.598.0.02 Тумба | left door white + strip (shelves behind); right column: a **drop-down flap** (writing flap on two stays, open photo) at the top, a drawer, a door hinged right; the drawer knob is level with the left door's knob (y 812), not centred | site front photo |
| ardo-0-07 | П3.598.0.07 Комод | two doors strip + white hinged at the outer sides, a white loose shelf behind each (the open photo shows them white), three equal drawers | site front photo |
| ardo-0-03 | П3.598.0.03 Тумба ТВ | left door white + strip (knob high on the strip), open niche with a small partition over a wide drawer | site front photo |
| ardo-0-05 | П3.598.0.05 Стол журнальный | all oak: top 16, four L-shaped board legs 120 × 120, aprons 92 on all sides, a shelf 165 over the floor between the end boards | site front photo |
| ardo-0-04 | П3.598.0.04 Полка навесная (wall) | white back board 240 (x 45…1155) with the oak strip (398…533), a 22 mm oak shelf 199 deep over the full 1200 | site front photo |
| ardo-0-08 | П3.598.0.08 Стол письменный | see below | site photo (perspective: rough) |

**Desk 0.08 (L1250 × B1250 × H755)** — an L read from the two site photos and the cut-out: the desk (oak top
1250 × 600 × 16, a white right side panel, a white modesty panel 190 high) and a white pedestal return 450 wide ×
1250 long along the left end. The pedestal's outer (left) panel rises to the desk top (an upstand 150 over the
pedestal top at 590) and carries the top's left end. The pedestal faces the knee space (+x): open shelves (one shelf)
under the desk top, three drawers in front of it; 10 mm glides under it. The drawers slide along x (`slide` moves) and
their knobs are built on a +z face and turned 90° about y (`rot`) — the check sheet draws them unturned.

## Finish
`ardo-white-madura` «Белый / Дуб мадура» (the only colour option; site: «Белый - Дуб мадура»):
- front and back «Белый» #dee0df — p. 97 swatch, `catpage.py 97 --swatch 0.786,0.865,0.810,0.905` (flat);
- body «Дуб мадура» #b09989 — p. 97 swatch, `--swatch 0.822,0.865,0.845,0.905`, **provisional** (textured decor, in
  `gen/ardo_decors.md`);
- white inner parts (drawer boxes, the chest's shelves, the desk carcass) use the finish's `front` or the built-in `white`;
- metal: black (knobs, legs); the strip lines `black`.

## Size / data decisions
- index.json «П6.598.0.01-01 … П3.598.0.01 (» is a garbled line of p. 97 («Шкаф-витрина «Ардо» П3.598.0.01
  (П6.598.0.01-01-зеркальное отражение)»). The site sells it as **П3.598.0.01-01** — model ardo-0-01-01 uses the
  site's code (the catalogue's «П6» looks like a misprint), named «Шкаф-витрина «Ардо» (зеркальное отражение)».
- The desk's site URL says p3-598-2-08 but its page and the catalogue say П3.598.0.08 — kept 0.08.
- Leg height 100 is a choice: the photos read 88–101 (perspective).

## Engine limits for the lead
- Dark lines of the pilaster: built as black 5-mm strips recessed 2 mm; a `grooves` face with its own colour (a
  painted groove) would be the exact form.
- Drawers facing +x (desk pedestal): `slide` moves and `rot`-turned knobs; a drawer move with a direction would be
  cleaner. preview2d draws the turned knobs unturned.
- The vitrine's frameless glass door is modelled as white boards + a 4 mm glass pane in one move (glass held by clips).
- 0.02's flap is a `flap` with hinge bottom, 90° (the stays are not modelled).

## Skipped
Nothing — the collection has no chairs or upholstered pieces.
