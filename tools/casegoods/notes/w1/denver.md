# «Денвер» (denver, П6.639) — wave 1 notes

Catalogue pp. 31–33 of the PDF (58–63 printed): living room on p. 31 (Кантри / белый), bedroom on p. 32 (Канзас / капучино),
module cut-outs, sizes and the two colour swatches on p. 33. Generator: `tools/casegoods/gen/denver.py` (re-runnable),
catalogue fragment `gen/denver_catalog.json`, decors `gen/denver_decors.md`, sheets `pilot/denver-*.png` (all print ok).

## Construction (from the 8 instructions)
- ЛДСП 16. The **bottom** carries the legs and runs the full L × 432; the **sides** (depth 428) stand on it, set 2 mm in from
  its ends, front and back — every panel between them is L − 36 (1360, 780, 418). Шкаф 0.01 has a full top on the sides as
  well; all other cabinets have an **inset top** (388 deep; bedside 405) between the sides, in front of a **100 mm back rail**
  (царга, parts 7 / 6).
- **Backs** ХДФ 3.5 in grooves (z 5.5–9), one piece per section, the joints behind the partitions (the back widths only add up
  that way: 0.02 458 + 450 + 458 = 1360 + 6, 0.01 332 + 456 = 780 + 8).
- **Partitions** 384 deep (комод 379), standing on the bottom in front of the rail. The cut lists make them 15 mm shorter than
  the space under the inset top (side − 31: 421 / 452, 1173 / 1204, 779 / 810) — built so, a 15 mm gap under the top; the
  reason is not visible in the drawings (0.01, whose top is on the sides, has a full-height partition).
- **Fronts** ЛДСП 16 in the oak decor, inset between the sides flush with their front edges, 1 mm gaps; doors 450 wide
  cover the inset top's edge and 6 mm of a partition (column 445/446 inner). **No handles** — push-to-open hinges
  (ZP-BICN070) and push-to-open runners (PK-P-H45-350); nothing to model.
- Drawer boxes (комод, прикроватная): ЛДСП 16 sides/back, ХДФ bottom in grooves, 13 mm runner gap each side, 350 mm
  runners; the small commode boxes have the middle divider 7.3.
- **Legs**: solid wood, tapered and splayed outward (to the sides; 10 mm fore/aft), top ~66 at 62 mm from the ends, foot ~30,
  felt pads; the fifth (middle) leg of the 1396-wide pieces is straight, set back at mid-depth (as in the cut-outs). Cut-list
  rows 80×80×130 / 86×60×130 / 85×85×200 are the blanks; built as `rod` (square, d → d2) with the row's `n`.
- Wall shelf 0.13: top/bottom 1396 × 250 over three uprights, ends open, ЛДСП backs 16 in the open sections (upright 3 is
  232 deep in front of back 7), ХДФ back 9 behind the lift-up flap 8 (hinges on the top, push latch) — `flap`, hinge top.
- Beds: headboard 1732 × 854 × 25 with two oak panels 791 × 415 × 16 (50 mm margins and gap, flush with its top), side rails
  200 × 2010 × 25 inside the foot board 1660 (L = 25 + 2010 + 25 = 2060), two splayed legs 85×85×200 inside the foot corners
  (130 visible under the rails), metal frame m 2000 × 1600 (black tubes, middle beam and leg, slats) and a mattress.
- Wardrobe 3Д (by catalogue): sides to the floor, recessed plinth, partition at x ≈ 630 (from the interior drawing next to
  the cut-out: left five shelves; right top shelf, a two-part box, hanging rail at 1550), three overlay leaves 611 in the
  Канзас decor (vertical grain) over the whole front; the right two leaves are the «WingLine L» folding pair.

## Finishes (p. 33 swatches, `catpage.py 33 --swatch …`)
- `denver-kantri-white` «Дуб Кантри золотой 389 SWN / Белый 600 SM»: body #f9fbfd (0.705,0.855,0.729,0.89), front #b39266
  (0.670,0.855,0.695,0.89, provisional — decor), legs #c1966a (the legs of the p. 33 photo, 0.2185,0.689,0.2215,0.700).
- `denver-kanzas-cappuccino` «Дуб Канзас 377 SWN / Капучино 806 PE»: body #cdcbd2 (0.792,0.855,0.818,0.89), front #7e6753
  (0.758,0.855,0.784,0.89, provisional — decor), legs = the Канзас colour (bedroom photo p. 32 legs read #564436 under
  the room light, same hue as the Канзас swatch).
- The catalogue shows the living pieces in Кантри and the bedroom in Канзас but lists both as the collection's variants:
  both finishes on the collection. `metal`: chrome (hanging rail, hangers); bed frame black.

## Modules
| id | code | source | ref of the sheet |
|---|---|---|---|
| denver-0-01 | П6.639.0.01 Шкаф | instruction | p. 33 cut-out (front-on) |
| denver-0-02 | П6.639.0.02 Тумба ТВ | instruction | p. 33 cut-out |
| denver-0-03 | П6.639.0.03 Тумба | instruction | p. 33 cut-out |
| denver-0-10 | П6.639.0.10 Тумба | by catalogue | p. 33 cut-out (+ the front-on photo p. 33 left for the proportions) |
| denver-0-13 | П6.639.0.13 Полка | instruction without text layer: table transcribed to gen/cutlists/denver-0-13.json | front view on pages/denver-0-13-p3.png |
| denver-1-01 | П6.639.1.01 Шкаф 3Д | by catalogue | p. 33 cut-out (perspective: rough) |
| denver-1-02 | П6.639.1.02 Комод | instruction (table corrected, below) | p. 33 cut-out |
| denver-1-03 | П6.639.1.03 Зеркало | instruction | p. 33 cut-out |
| denver-1-04 | П6.639.1.04 Тумба прикроватная | instruction | p. 33 cut-out (perspective: rough) |
| denver-1-05 | П6.639.1.05 Кровать 2-16 | instruction | none (no front view anywhere) |
| denver-1-15/16/17/18 | Кровати 1-09, 1-12, 2-14, 2-18 | by catalogue: the 2-16 construction at W = 1032/1332/1532/1932 (sleeping + 132), panels (W − 150)/2 each, foot W − 72; single bed 1-09 without the middle beam | none |

The instruction covers are perspective views and the table pages only exploded views, so the overlays use the
catalogue's front-on cut-outs (their scale from the known L); 0.13 has a true orthographic front view.

## Cut lists / catalogue data found wrong
- Комод 1.02 table (reference JSON = the page): row 5 «1369» is a transposition of **1396** (the full bottom under the
  sides; 1369 fits neither between nor under them); column D contradicts the drawing on the same page (6 drawers: fronts
  7 + 9 small, 8 ×2 + 10 ×2 big; two backs 684 + 684). Corrected table in `gen/cutlists/denver-1-02.json` (all rows kept,
  counts per the drawing, reason in its "source").
- Зеркало 1.03: catalogue (and index.json) L1126, but the cut list gives panels 796 + 300 = **1096** side by side (the
  drawing and the cut-out agree on the 796 : 300 split, nothing sticks out). Built and listed as [1096, 168, 763] — the
  lead should decide; B168 = panel 16 + shelf 150 + hanging plates 2.
- Кровать 2-16: H869 vs headboard 854 — the headboard stands on 15 mm glides (h2) to reach the catalogue height (not
  drawn in the instruction).
- index.json names П6.639.1.15 «сп. место: 2000х1400 Кровать 1-09»: the catalogue says «Кровать 1-09», сп. место 2000×900
  (the index took the neighbouring line). Used the catalogue.
- The covers of 0.03 carry wrong dimensions (1552 × 964 × 452, another product's drawing); ignored.

## Engine limits / for the lead
- Legs are `rod`s: preview2d/check do not draw rods, so the sheets show only the felt pads; the extent in y is reached
  through the pads. A rectangular tapered leg (86×60) is a square rod here (d 66 → 30).
- «WingLine L» folding pair (1.01): no chained/folding move. Two `door` moves: the outer leaf on its side hinge (90°), the
  inner leaf about the axis [1210.5, 1214.5] (90°, hinge "left") that lands it folded next to the outer one — correct end
  state, but the two must be opened together (and the inner leaf's path is not the real fold). The wardrobe's two thin
  vertical lines in the interior drawing (x ≈ 1156 / 1297) were not identified and not built.
- Flap 0.13 opens upward on cup hinges (no stay listed); push-to-open everywhere — no handle parts at all.

## Skipped
None: the collection has no «Стулья» items.
