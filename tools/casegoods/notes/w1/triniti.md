# Тринити (triniti) — wave 1

Catalogue «Корпусная мебель ч. II» 2025, PDF pages 9–11 (catalogue pages 14–19). There is no spread of module cut-outs or
swatches for this collection. All 9 articles have an instruction, so every module is **by instruction** (cut list + table
page). Generator: `tools/casegoods/gen/triniti.py`. It writes the 9 designs, `gen/triniti_catalog.json` and the completed
cut lists. All 9 check sheets print ok.

## Construction (the same in every case piece)
- Carcass: ЛДСП 16 «Гикори Кингстон». The top and bottom run the full width and depth. The sides, and the partitions
  where there are any, stand between them. The partitions (and fixed shelves) are 45.5 shorter than the sides, so B−45.5
  deep: 389.5 at B 435, 544.5 at B 590. They run from z 10 and stop 16 mm behind the fronts.
- Backs: ХДФ 3.5 in grooves at z 6–9.5. They pass behind the partitions and fixed shelves, and are joined there (the
  cut-list widths and heights prove this: 507 + 601 + 507 at 1644, 608 + 608 at 1242, and so on).
- Fronts: set inside the carcass, flush with its front edge (fronts' back faces at B−19 / B−19.5). Gaps are 3 mm at the
  sides and between fronts, 2 mm top and bottom (4 between stacked drawers in 0.02 and 1.04). The fronts cover the
  partitions, which sit behind the joints at x 512.5 / 1115.5 (1644-wide pieces) and 512.5 / 1015.5 (wardrobe).
  - 19 / 19.5 fronts carry milled pyramids: face `diamond`, cells 100×100, depth 8. Their cell counts match the
    drawings exactly (6×2 on 600×200, 5×2 on 500×200 …).
  - Plain fronts are 19 (living room) or 16.5 (bedroom). When 16.5 and 19.5 fronts mix (1.01, 1.02, 1.04), the back
    faces are kept on one plane, so the plain fronts sit 3 mm behind the pyramid ones. This is an assumption.
- Opening: push-to-open everywhere (x «AM-OAM-DL-MG» / «механизм push-to-open»), so there are no handles.
- Drawer boxes: ЛДСП 16 sides and back, ХДФ bottom in grooves. Runner gap is 13–14 mm per side, as the cut-list widths
  give it.
- 0.01: the glazed door is two pyramid panels (8, 8.1, 200 each) glued to a clear glass 880×598×4 (8.2) that shows
  860 between them. The instruction says it is supplied assembled.
- Legs: tapered square oak legs 130. The cut list gives 86×60×130. Their size comes from the drawings: 60 at the top,
  32 at the floor, splayed 40 mm sideways. They stand 15 mm in from the back and from the front.
  - The middle leg of the 5-leg pieces (0.02, 0.04, 0.05) looks straight from the front, so it splays backwards
    (86 deep).
  - Wardrobe 1.01: 6 legs, the 4 corners plus 2 at mid-depth under the partitions, splayed outwards as in its front view.
  - In 0.0x the legs are cut-list rows (12 / 13). In 1.0x they are hardware «h» (`covers`).
- Wardrobe 1.01, three columns:
  - Bottom: a drawer zone (pyramid fronts 300, drawers 500 deep) under fixed panels 7 / 8.
  - Middle: plain doors 1528.
  - Top: a mezzanine behind pyramid fronts 300.
  - Rails (w1 487, chrome): left top, right top and right lower (two-tier). Middle column: fixed shelves 9 and a loose
    shelf 10. Left column: a loose shelf 11.
- 1.02: 4 drawers, pyramid and plain alternating (bottom pyramid, top plain, as in the instruction; the catalogue photo
  looks similar). There is a back rail 5 (128×1004) behind the joint of the backs 8 / 9.
- 1.03 mirror: an oak board 680×1000 with the mirror 960×660 glued on (20 margin at the sides and bottom), and a pyramid
  strip 100×1000×19.5 joined edge-to-edge on top. `mount: wall`.
- 1.05 bed:
  - The headboard is a box standing on the floor: sides 7, ribs 8 (at thirds, which is an assumption), top 4, and a lower
    panel 1 (25).
  - The sides are cut to a slope, so the upper headboard (1.1 faced with 6 and the pyramid strip 5) leans back 8.1°.
  - The frame is side rails 3 / 3.1 and foot 2 (25 thick, 200 high, at y 130–330, x 20–1680), with two legs 200 at
    the foot. The flexible base «k» is 2000×1600 (black frame, slats, 2 middle legs), with the mattress 200 on it.

## Finishes
- `triniti-vanil` «Ваниль / Гикори Кингстон 579 SWN»: front #e3e4df. There is no Ваниль swatch in the catalogue. The
  colour is the mean of the flat wardrobe doors on p. 11 (--swatch 0.655,0.40,0.675,0.50 → #e1e2dd and
  0.61,0.40,0.625,0.50 → #e5e6e1). «Белая Ваниль» p. 108 is a different, woodgrain decor.
- `triniti-antracit` «Антрацит / Гикори Кингстон 579 SWN»: front #3c3f41, the mean of flat anthracite doors on p. 9
  (0.17,0.55,0.23,0.75 → #404346; 0.74,0.66,0.8,0.74 → #393f42; 0.84,0.62,0.9,0.75 → #373a39). The «Антрацит» swatch of
  Форте Лофт (p. 71, #222b38) is a darker, bluer ЛДСП and was not used.
- body (carcass, legs, mirror board, bed): «Гикори Кингстон 579 SWN». Its colour is provisional, #a1876f, from the swatch
  on p. 115 (Вена colour chart, 0.845,0.86,0.895,0.905). The decor is listed in `gen/triniti_decors.md`.
- metal: chrome (the hanger rails only; there are no metal handles or legs).
- Side panels whose cut list gives the height first (0.02, 1.04: 408×435, 308×435) get `grain: "y"`.

## Completed cut lists (gen/cutlists/, rows lost from the PDF text, read off the table pictures)
0.02 rows 1–4 · 0.04 row 4 · 0.05 rows 1, 2, 3, 6 · 1.01 row 13.1 · 1.02 row 6.2 · 1.05 rows 5, 7.

## Sizes
- **1.05 bed: the catalogue (p. 11 text, and index.json) says L2217×B1800×H1193. The instruction's cover says
  1700 × 2217 × 1143, and the cut list agrees: the headboard parts are 1700 wide, and 1127 + 16 = 1143.** I used
  [1700, 2217, 1143] for the design and the model's size, with a model note. The catalogue photo also shows a different
  headboard (a pyramid border round a plain panel) from the instruction's (a pyramid strip on top). The design follows
  the instruction.
- All other sizes match the catalogue text exactly.

## Reference overlays
- The instructed modules are checked against their table page's front view. For 1.01 the table page's second view is
  the interior without fronts.
- 1.03: the table page and the cover are perspective drawings, so the overlay is the catalogue photo crop (p. 11), a rough
  check only.
- 1.05: no front orthographic drawing exists (the cover is perspective; the table page has a side view). The slope was
  measured from that side view: the panel 1 top at 450, and the top 4 at 60 deep.

## Engine limits for the lead
- **No rotated boards.** The bed's upper headboard leans 8°. Its panels 1.1, 6 and 5 are written as `moulding`s with a
  straight path along x and a parallelogram section (profiles `triniti-hb-*`) to get the slope. As a result:
  - the pyramid relief of strip 5 is lost (faces work only on axis-aligned boards);
  - the checker cannot measure their sizes (they are `covers`);
  - preview2d draws them only as bands.

  A `tilt` / rotation on panels (or a face on mouldings) would express this properly.
- **Rods do not count toward the extent** (neither in preview2d nor in CaseBuilder.Bounds). The tapered splayed legs are
  `rod`s that also carry their bounding `box` (86×130×60, the cut-list size). The engine draws the rod from from/to and
  uses the box only for bounds. It would be cleaner if rods computed their own bounds.
- The rod's square section is not oriented, and its ends are cut square to the axis. At a 17° splay the top pokes about
  9 mm into the bottom panel and the foot is not flat on the floor. A "cut ends horizontal" option for legs would fix this.
- preview2d draws `shape: path` side panels (bed 7 / 8) as their boxes in the side view.

## Skipped
Nothing: the collection has no chairs or upholstered pieces.
