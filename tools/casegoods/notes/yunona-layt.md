# «Юнона Лайт» (yunona-layt, Пинскдрев П3.0582) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF pp. 109–111 (interiors), 112 (module cut-outs, wardrobe schemes, the swatch
«Дуб Каньон» / «Дуб Бордо лайт»). Generator `tools/casegoods/gen/yunona-layt.py` (re-runnable: writes the 24 designs,
`gen/yunona-layt_catalog.json` and the six transcribed cut lists in `gen/cutlists/`). Decors: `gen/yunona-layt_decors.md`.
Check sheets `pilot/yunona-layt-*.png` — all 24 end with "ok".

## Sources

- The instructions (a.pinskdrev.ru, downloaded with curl) are those of the older set **«Юнона» П582.01 … .07**
  (Городищенская мебельная фабрика, 2020–21), in «ЛДСП 16 Дуб Версаль / ЛДСП 16 Белый / ДВП ламинированная белая». They
  have a text layer, but the text scrambles the row order (e.g. П582.02 rows 6–11, П582.06 rows 2/3) and loses rows
  (П582.01 row 11, the second door): **every table was transcribed off the table picture** into `gen/cutlists/`. The
  reference cut-list JSONs were empty. ДВП thickness is not listed: 3.2 assumed.
- **Two index.json links are wrong**: 1.21 (комод) points to `IS-P582-06-tumba-prikrovatnaya-1-1-1.pdf`, byte-identical to
  1.60's file (a 542 × 441 × 460 bedside table) — the chest has no instruction, built by photo. 1.28 points to
  `IS-P582-07-krovat-dvoynaya-1-3-1.pdf`, identical to 1.61's (the bed with the panel headboard) — 1.28 has no "is"; it is
  that frame with the upholstered pad instead of panel 1.2 (by photo).
- pinskdrev.by product photos (index.json "photos"; the product pages are JS shells, no more photos found).

## Colours — which decor where (from the product photos and the catalogue)

The old instruction materials map by part, not by material: carcass «Дуб Версаль» → **Каньон**; doors (white in «Юнона»)
→ **Бордо лайт**; drawer fronts «Дуб Версаль» → **Каньон**; inner white parts (shelves in wardrobes, stiles, drawer boxes)
stay **white** (1.02 / 1.55 interior photos, 1.18 open drawer); ДВП backs → **Бордо лайт** (the 1.15 photo shows a
wood-grain light back in the open shelving). Beds: headboard, wings, rails, foot Каньон; the overlays 1.2 / 1.5 / 2.2 / 3.2
Бордо лайт. Desk 1.26: drawer front Бордо лайт (p. 112 cut-out), dressing table 1.58: Каньон. Coupe doors: upper filling
Бордо лайт, lower 810 Каньон (≈ 38 % of the door, measured on the three p. 112 cut-outs).

**Edge bands:** every Каньон board shows a light (Бордо лайт) edge band on its front edge in all photos — the collection's
look. The format has no edge-band colour, so each visible front edge carries a flat moulding (profile `yunona-layt-edge16`,
16 × 0.6, role `edge`) with a `box` for the checker. Front edges only; top / side end edges and the bed boards' top edges
are not banded.

Finish `yunona-layt-kanon-bordo` «Дуб Каньон / Дуб Бордо лайт» (the only colour option): body #978071 (p. 112 swatch
left, crop 0.715,0.865,0.735,0.91), front / back / roles bordo, edge #d4d4d8 (swatch right, 0.749,0.865,0.768,0.91), role
kanon #978071, fabric velvet#846d5d (p. 109 headboard, 0.60,0.465,0.72,0.50). All provisional plain colours of textured
decors. Metal `chrome#b6b0ab` = the satin aluminium handles (1.60 product photo, flat highlight of the bar); hanger rails
chrome; coupe profiles and tracks role metal; hinges of the folding mirror gold (photo).

## Construction (instructions)

- Carcass ЛДСП 16: top and bottom over the full width, sides between them; sides 2 mm shallower than top / bottom (439 vs
  441), flush at the front. Backs ДВП in grooves (z 6–9.2), in pieces joined on fixed shelves / stiles (the widths and
  heights of the tables prove the joints: 1.55 372 + 974 + 900, 1.56 372 + 1518 + 356 with the stile 7 = 1504 between the
  shelves, 1.57 900 + 1348 joined on shelf 2).
- Wardrobes 1.55 / 1.56: 900 × 579 carcass on four 88×54×20 glides, overlay doors 446 × 2 (2 mm under the top), hat shelf
  5 at 1901, rail under it, the stile 7 / 12 (128 wide) at the back centre joining the back halves. 1.55: shelf 6
  (867 × 560) over three overlay drawers 896 × 300 (Каньон), door handles UA-AA-06-128 horizontal just above the door
  bottom near the meeting edge, drawer handles UA-AA-06-416 — exactly as the instruction's front view (the overlay sits on
  it). 1.56: two full-height doors, 416 handles vertical at the meeting edges.
- 1.57 стеллаж: 252 wide, 579 deep, four fixed shelves 219 × 540 in five equal compartments.
- 1.58 стол туалетный: top 1066 × 441, side panels 780 × 439 set 2 mm in from the top's ends (the inner width 1030 = the
  shelf / modesty panel), drawer 1026 × 135 over the shelf 5, modesty panel 6 (416) from the top down to y 368 (the front
  view gives exactly this), drawer box with the organiser partitions 1.6 / 1.7 / 1.8, nail glides 4.
- 1.60 тумба: drawer 504 × 198 inset flush on top, the rail 6 (508 × 76) under it, open niche below, glides 20.
- 1.61 кровать: headboard 1.3 1706 × 885 on nail glides (889 = 885 + 4); Каньон strips 1.1 / 1.4 (877 × 128) flat on its
  face at the ends, panel 1.2 (1434 × 256) at the top, strip 1.5 (128) lower (hidden by pillows); rails 3.1 2010 × 200 at
  y 124–324 inside the overlays 3.2 (2026 × 128 at y 160–288); foot 2.1 1642 × 320 standing on the floor between the rails,
  its overlay 2.2 1674 × 128 between the side overlays. Length 16 + 16 + 2010 + 16 + 16 = 2074 ✓. Base «Основание гибкое
  WS 1.01 (2000 × 1600 / 230-6)»: two black tube frames 800 × 2000 with slats, top of the slats 238, six legs 200 along
  the middle (the instruction's side view shows legs under the rails), mattress 200.

## By photo / catalogue (no instruction) — built with the instructed modules as the model

| id | how |
|---|---|
| 1.11, 1.65 шкафы 450 | П582.02 half: carcass 450, one door 446 **hinged right in both** (the handle is by the left edge on both p. 112 cut-outs and on p. 111); 1.11 = hat shelf + rail + lower shelf (scheme p. 112), 1.65 = shelves (scheme: 4 shelves, the two fixed ones at 381 / 1901 as in 1.56 plus two between) |
| 1.15 стеллаж | 1.57 turned front-on: 579 wide, 252 deep, 4 shelves (5 equal compartments, as the photo), shelves 6 mm behind the front edge (photo: nearly flush) |
| 1.18 тумба | 1.60 upside down: drawer at the bottom, a full-depth shelf (the niche floor, photo) over it, niche on top |
| 1.21 комод | the bedside construction 540 × 441 × 1254: five inset drawers — two 196 on top, three 264 (photo / p. 112 cut-out proportions), 128 handles near the top of each |
| 1.62 / 1.63 тумбы | top / bottom over the sides, B400; the right column (fronts 352.5) = two Каньон drawers 166 over a Бордо лайт door 454, a fixed shelf behind the door top, the partition behind the joint (the fronts cover it — no carcass edge shows between them in the photos); left one door (1.62) or two doors (1.63, no partition); handles 128 horizontal near the top of every front |
| 1.64 полка | a board 800 × 230 with two uprights 214 on its ends, no back; wall |
| 1.25 зеркало | faceted mirror 4 on a Каньон backing 16 (the backing edge shows round it); wall |
| 1.59 зеркало | folding triptych 247 + 497 + 247, each a mirror on a Каньон backing, gold hinges in the gaps; the wings are door moves (35°). It is a table mirror; `mount: wall` so the app hangs it |
| 1.02 / 1.03 / 1.05 шкафы-купе | sides 650 on glides, top over them, plinth 60 + bottom, interior 550 deep white (schemes p. 112: 1.02 — hanging section 874 wide with hat shelf 1920, rail, back rail 1130–1250, lower shelf 440, partition at 898, shelf column with 5 shelves; 1.03/1.05 — partitions at 676 / 1351, hanging sections left and right, 5 shelves in the middle); doors 2160 high in aluminium profiles (verticals 20, horizontals 30), overlapping 25, two tracks (2д: left door behind; 3д: middle door in front, as the cut-outs show its profiles on both edges); 1.05 middle door = mirror on a white backing; `slide` moves |
| 1.26 / 1.26-01 стол | the 1.58 construction at 1342 × 441 × 780 (drawer front Бордо лайт) plus a low return under its right end: two side panels 1031 long, top at 590 (below the drawer shelf), a cabinet with a Бордо лайт door at its front end (z 1051), open under the desk. -01 = the mirror image (return on the left, p. 111), both codes built as Стамбул 1.30 / 1.30-01 |
| 1.28 кровать 2-16 | 1.61's frame, the panel 1.2 replaced by a buttoned pad (`soft`, tufts 8 × 2, 360 high, 40 thick) |
| 1.45 кровать 1-09 | 1.61's frame at W 1006 (panels 734, foot 942, overlay 974), metal frame 900 × 2000 on six legs; H 890 = 885 + 5 |
| 1.47 кровать 1-09 | the same with the buttoned pad (4 × 2) and slats on cleats screwed to the rails (no metal frame) |

**The desk is the weakest reading.** p. 112's cut-out is a perspective and p. 111 shows the -01 variant behind a chair; the
catalogue size 1342 × 1051 fits a desk 1342 × 441 with a return reaching forward to 1051. The return's width (448), top
height (590), the cabinet depth (440) and the open rear part are estimates. Worth a look against a product photo.

## Size disagreements and decisions

- **1.62 тумба**: p. 112 prints L803 × **B415** × H850, p. 111 and index.json **B400**. Built **B400**: two of three
  sources, and 1.63 (the same construction) is B400 on both pages; 415 does not come from handles (they stand 30 out).
- Beds: index.json 1.28 [2074, 1706, 889] and 1.45 [2074, 1006, 890] give L as the length; the p. 112 captions write
  L1706 × B2074 / L1006 × B2074. All beds are stored [width, length, height]: 1.28 / 1.61 [1706, 2074, 889], 1.45 / 1.47
  [1006, 2074, 890] (the single beds are 1 mm taller: nail glides 5 instead of 4 — assumed).
- 1.26-01: index.json has only -01 (garbled note «-зеркально)»); the page writes «П3.0582.1.26 (П3.0582.1.26-01-зеркально)»
  — both built.

## Engine / format limits for the lead

- **Edge-band colour**: no such thing in the format; faked by 0.6 mm mouldings on the front edges (role `edge`). A panel
  `edgeMat` (per face) would be cleaner and cheaper.
- preview2d / check draw custom finish roles (`kanon`, `bordo`, `edge`, `fabric`) in the body colour: on the sheets the
  Бордо лайт overlays of the beds and the coupe fillings look Каньон — the engine resolves the roles.
- The coupe door's top enters the top track in reality; here the door stops 2 mm under a 10 mm track strip (no overlap
  allowed across moves). The top band over the doors reads ~20 mm lower than the cut-out's (~50 mm).
- Coupe doors: separate `slide` moves; opening two doors that share a track overlaps them.
- Handle UA-AA-06 is a flat aluminium bar with hidden posts; built as `bar` 10 × 8, 22 off the face, posts ±0.4 d (d 150
  for 128 c-c, 450 for 416 c-c). preview draws bars as circles (hence the "примечание" lines on B / H / L).
- The folding mirror stands on a table in reality (no such mount); it is `wall`.
- Bed base «WS 1.01»: its brackets / leg positions are not drawn in the instruction; six legs along the middle assumed.

## Skipped

Nothing. (The chair «Моника Концепт» П5.0646.5.03 on p. 111 is another collection's article.)
