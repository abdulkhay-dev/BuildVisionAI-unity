# «Лайн» (layn, П6.619) — 26 designs

Catalogue «Корпусная мебель ч. II» 2025, PDF pp. 65–69 (printed 126–135): living room (p. 65), study (p. 66), youth bedroom
(p. 67), bedroom (p. 68), module cut-outs, the interior sketches of the wardrobes and the colour chart (p. 69). Generator
`tools/casegoods/gen/layn.py` (re-runnable; writes the 26 designs, `gen/layn_catalog.json` and the completed cut lists
`gen/cutlists/layn-*.json`). Every design prints `ok` in `gen/check.py`; sheets `pilot/layn-*.png` (drawn with a light copy
of the finish, otherwise the dark decors turn the overlay red).

| id | code | source | ref on the sheet |
|---|---|---|---|
| layn-0-01 / 0-01-01 | П6.619.0.01 / -01 шкаф-витрина (правый / левый) | instruction | instruction front view (mirrored for -01) |
| layn-0-04 | П6.619.0.04 шкаф (instruction: «тумба») | instruction | instruction front view |
| layn-0-10 | П6.619.0.10 шкаф 2д | instruction | instruction front view |
| layn-0-12 | П6.619.0.12 тумба на металлическом основании | instruction | instruction front view |
| layn-0-06 | П6.619.0.06 стол журнальный на колёсах | instruction (built mirrored, as the catalogue shows it) | instruction front view, mirrored |
| layn-0-08 / 0-09 | полки 1670 / 1973 | instruction | instruction front view |
| layn-1-02 / 1-11 | комоды (цоколь / металлическое основание) | instruction | instruction front view |
| layn-1-04 / 1-12 | тумбы прикроватные (цоколь / основание) | instruction | instruction front view |
| layn-1-28 | шкаф для одежды 2Д | instruction | instruction front view |
| layn-2-11 | стеллаж | instruction | instruction front view |
| layn-2-15 | стол письменный 2т | instruction | instruction front view |
| layn-2-16 / 2-16-01 | стол письменный (тумба справа / слева) | instruction | instruction front view |
| layn-1-26 | шкаф для одежды 4д | **by catalogue** (p. 69 cut-out + its interior sketch) | p. 69 cut-out |
| layn-1-03 | зеркало | **by catalogue** | none (the cut-out is too small) |
| layn-1-05, 1-13, 1-14, 1-15, 1-16, 1-17, 1-18 | кровати 2-16, 1-12, 2-14, 2-18, 2-20, 1-09, 1-08 | **by catalogue** (photos p. 67–69) | none (no front view) |

## How the instructed modules were measured
The Лайн instructions (Фабрика столов) have tables **without sizes** and a front / side view with only the overall
dimensions. The drawings are vector: positions were read from the PDF line coordinates (PyMuPDF `get_drawings`, the
object's extent from the arrow tips of its overall dimension lines, scale = catalogue size / drawn size; grid ≈ 0.9 mm), so
every edge on the front view is placed to ±1 mm: shell, inner carcass, fronts and gaps, plinth, legs, handles and the
centre lines of the milled diagonal lines (each drawn as two or three parallel lines ~3 mm apart). Parts hidden behind
the doors (loose shelves, the hat shelf, drawer boxes, the rib 9 of 1.28) follow the exploded view (Схема №1); their
heights are placed sensibly (loose shelves at the fixed ones' heights or in the middle of the space).

The completed cut lists (`gen/cutlists/`) keep `size: null` (the tables have none); they restore rows the PDF parser lost
(0.01 two-column table, 0.04 row 11, 1.02 / 1.04 / 1.11 / 1.12 / 2.15 / 2.16 drawer rows), write the sub-numbers
properly (15.1, 17.1 … instead of 151, 171), and sum the drawers' shared rows (e.g. 1.02: 8.5 ×4, 9.2–9.4 ×3). Group rows
«Ящик выдвижной, в т. ч.» are left out. 0.10: the table prints the second «накладка» as 15.2; written as 16.2.

## Construction (all case pieces)
- **Two carcasses.** An outer shell ЛДСП 16 «Дуб Вотан»: top and bottom over the full width and depth (B), the sides
  (B − 1 deep, set 1 mm in from the top's ends — a line on every drawing) between them. Inside it an inner carcass ЛДСП 16
  **black**: sides between its top and bottom, 34 mm narrower in each direction; screwed to the shell (Шурупы 4×30 «для
  соединения внутреннего и внешнего корпусов»). Depth of the inner carcass z 3 … B − 23: ДВП back 3 behind it, the fronts
  16 + (glass 4) in front of it.
- **Fronts** «Камень серый» 16 inside the shell, flush to 2 mm with its front edge, on half-overlay hinges: every front
  edge is exactly 10 mm in from the inner carcass' outer faces, so a **10 mm black border** shows round the fronts
  (the photos' black outline). Gaps 1.4–3.4 mm as drawn.
- **Milled diagonal lines** on the fronts (face `grooves`, 3 mm, V, 1.5 deep) — the pattern of each module as drawn; they
  run on across neighbouring fronts (clipped per front).
- **Handles** «Ручка СПА-1 (96 мм)»: slim black bar, measured 123–129 × 9, standing 16–18 out of B (side views) → `bar`
  d 124–129, band 9, t 8, standoff 10. Horizontal near the top of drawers / low doors, vertical on tall doors.
- **Plinth**: black ЛДСП 16, 100 high, under the inner carcass (flush with its sides), fronts set 20 mm in from the front
  and the back, on ФБ 482 glides (the drawings give 2–10 mm below it; the measured level is used per module).
- **Metal base** («металлическое опорное основание», 0.12 / 1.11 / 1.12): closed rectangular frames of 20×20 black tube,
  200 / 180 high (posts, floor tube, top tube) under the inner carcass' sides (0.12 also in the middle), joined by top
  rails front and back.
- **Backs** ДВП (role `back` = black) nailed on the inner carcass, joined on fixed shelves / partitions as the counts need.
- **Vitrines 0.01 / 0.10**: the door is one L-shaped board (`shape: path`): a 150 stile on the hinge side and a solid
  lower panel up to 610.5; the rest of its field is the **glass «накладка»** screwed on the door's back (a `glass` part
  moving with the door); the handle is on the glass. Glass shelves 6 mm, a fixed horizontal at the glass line, a loose shelf
  below, Orbit LED puck(s) under the inner top.
- **Desks**: pedestals are the same double carcass without their own top (the desk top 13 / 8 is one board), a ЛДСП back
  between the outer sides, the inner carcass in front of it, modesty panel (царга) 317 high between the pedestals / the
  panel leg; drawer boxes on 450 runners.
- **Drawers**: the front is the box's front wall (Стенка передняя, fastened by Rastex), sides / back black ЛДСП 16, ДВП
  bottom in grooves; 13 mm runner gaps; 350 (bedsides, 0.12) / 450 runners (commodes, desks).
- **Coffee table 0.06**: an oak C (top 4, bottom 5, end 3) 880 long round a black box (2, 1) 560 deep that runs through it
  and stands out 120 at the other end, a lengthwise black partition 6; four black wheels 60. The catalogue shows the black
  box on the left, the instruction draws it on the right: built as the catalogue.
- **Shelves 0.08 / 0.09**: a wall board 250 and under its front a shelf 16 × 200, 24 mm above the board's lower edge and
  24 mm shorter at each end (as drawn). The catalogue photos seem to show the ledge running past the board's ends (probably
  the photo's perspective): the instruction was followed.

## By catalogue
- **1.26 шкаф 4д**: 1.28's construction at 1852 with four doors (hinges L, L, R, R from the handles of p. 68 / 69),
  partitions behind the joints 1|2 and 3|4; middle section = 1.28 (hat shelf, rib, rail 877), outer sections four loose
  shelves at the heights of the p. 69 interior sketch. The hat shelf of 1.28 (hidden in its instruction) was put at the
  same height (1870). The milled lines were traced off the p. 69 cut-out (the photo is squashed vertically ~12 %; ±30 mm).
- **1.03 зеркало**: mirror 4 on an oak board 16, 25 mm oak border (p. 69 cut-out, p. 68 photo). `mount: wall`.
- **Beds** (x = width, z = length; W = sleeping width + 76, L 2142, H 950): an oak box of side rails and the foot (16, 260
  high, top at 350) on a black plinth 86 set in 50 mm; the headboard at the head end is an oak back board with oak edge
  strips (56 deep) round a black field and a grey «Камень серый» panel (10 mm black border, milled lines — the pattern is
  schematic, from p. 67 / 68); the metal frame (металлокаркас, black 30×40 tube, a middle beam and two legs from 1200 up),
  24 slats, mattress 200. Heights of rails and plinth read off perspective photos (±30 mm).

## Finish
`layn-kamen-votan` «Камень серый / Дуб Вотан 376 WML / Черный» — the collection's only colour option (p. 69 chart):
- body = «Дуб Вотан 376 WML» provisional #c4a58c (`catpage.py 69 --swatch 0.732,0.86,0.757,0.905`),
- front = «Камень серый» provisional #4a4a4a (0.695,0.86,0.72,0.905),
- role `inner` (black ЛДСП: inner carcass, shelves, partitions, plinth, drawer boxes) and `back` (ДВП) = #272825
  (0.768,0.86,0.793,0.905, flat),
- metal black (handles, bases, wheels), rail chrome.
Both textured decors are listed in `gen/layn_decors.md`.

## Engine / tool limits for the lead
- The milled lines read light in the photos (the core shows); `grooves` will read as shadow lines in the stone decor. A
  groove material (lighter) would match better.
- The metal bases' tubes are `panel` boxes with `mat: metal` (square tube); fine, but no welded look.
- preview2d draws the L-shaped vitrine doors as full rectangles (outline ignored) and does not draw the grooves; the glass
  «накладка» is drawn behind them.
- The drawer-front / door «ручка СПА-1» is a `bar`; its posts at ±0.4 d give 99–103 mm, the real c-c is 96.
- Catalogue B excludes handles (the checker's примечание on every module with handles).

## Decisions / uncertain
- Door thickness 16 and glass 4 are assumptions (the tables give no sizes); the inner carcass depth (B − 26) follows.
- Hidden heights (loose shelves, hat shelf, drawer box heights) are placed, not measured.
- 2.15 / 2.16: the pedestals' ЛДСП backs 14 / 10 are black (not stated).
- 0.06 built mirrored to the instruction (the catalogue's orientation).

## Skipped
Nothing: the collection has no chairs or upholstered pieces.
