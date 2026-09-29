# Рокси (roksi) — wave 1

Catalogue «Корпусная мебель ч. II» 2025, PDF pages 12–14 (printed pages 20–25). The module cut-outs, swatches and table
drawings are on PDF p. 14. There are 12 articles:
- **8 by instruction:** 0.01, 0.02, 0.03, 0.04, 1.01, 1.02, 1.03, 1.05.
- **4 by catalogue:** 1.04 bedside, and the dining tables 0.11, 0.12, 0.13.

No «Стулья» article belongs to the collection. The chair «Бруно М» П5.0909.5.01 appears on p. 14 but is not a Рокси
code, so it is skipped.

Generator: `tools/casegoods/gen/roksi.py`. It writes all 12 designs. The catalogue fragment is
`gen/roksi_catalog.json`. All 12 check sheets (`pilot/roksi-*.png`, drawn with the light finish so the red edges show)
print ok.

## Construction (every case piece)
- **Carcass:** ЛДСП 16 oak. The top and bottom run the full width and depth: 404, or 590 in the wardrobe. The sides
  stand between them and are 383 deep (569.5 in the wardrobe).
- **Legs:** the carcass stands on metal legs «Опора метал.», 100 high. The wardrobe's legs are 91, because its bottom is
  25 thick (sides 2184 + 16 + 25 = 2225, and 2316 − 2225 = 91).
- **Partitions and shelves:** fixed partitions and shelves are 363–367 deep and start at z 10. Loose shelves are 355 /
  357 deep. The thin 6-mm dividers of 0.02 / 0.04 (rows 6) and the 6-mm fixed shelves of 1.01 (row 6) are built as
  listed.
- **Backs:** ХДФ 3.5 in grooves at z 6–9.5, joined behind the fixed shelves and partitions. The cut-list sizes prove the
  joints, e.g. 0.01: 530 + 845 + 530 at the two shelves 8.
- **Commode 1.02 backs:** two ХДФ 484×994 sheets that reach 10 mm into the sides, top and bottom. They are joined on a
  back rail 8 (972×128), which stands behind the drawers at mid-height.
- **Fronts:** МДФ 19.5, or 19 on the door of 0.01. They are laid over the sides' front edges between the top and the
  bottom, so the face is at 404. Gaps are 3 at the sides and 4 between fronts; the vertical gaps vary as the cut list
  forces them (2 at the bottom, 4 at the top).
  - Hinge sides follow the instruction: in 0.04, doors 12 / 13 hinge on the 16-mm partition 6.1 behind their joint. In
    1.01, door 12 hinges on partition 5, and a 128-deep stile 10 stops doors 12 / 13.
  - The catalogue cut-outs of 0.04 (and of 0.01 and 0.02 on p. 12) show the mirror-image variant. The 0.04 check uses a
    mirrored crop, and its joints then sit on ours.
- **Reeded fronts:** face `fluted`, reed, pitch 16, depth 3, gap 2. The pitch was measured on the close-up (p. 13) and
  the living-room photo (p. 12: about 19 ribs over a 305 half-door).
- **Which fronts are reeded:**
  - 0.02: 9.1 and 11.1.
  - 0.03: 8 and 8.1, the two 500-wide doors.
  - 0.04: 10.1, 11 and 12.
  - 1.01: the drawers 14.1.
  - 1.02: 6.1.
  - 1.04: the lower drawer.
  - Bed: 2.1.
- **Handles:** «Ручка СА-1», a black aluminium edge pull on the front's top edge. It is built as a `bar` 128 long,
  band 14, t 6, standoff 2.
  - Drawers: centred.
  - Doors: flush with the free edge (0.03, 0.04), as in the cut-outs.
  - Wardrobe: the same pull stands upright (160) on the free edges of doors 11 and 13, with its centre at y 1190.
  - Doors without a handle (0.03 plain doors, 0.04 doors 12 / 13, wardrobe door 12) have none in the catalogue, and
    the hardware counts agree (i 2x, s 4x).
- **Drawer boxes:** ЛДСП 16 sides running full height, and a back (h − 14) standing on the bottom. The ХДФ bottom is
  357 / 505 long: it sits in the sides' grooves and 5 mm into the front's groove, which is why it is longer than the
  sides. Runner gap is 13–16 per side, as the widths give it.
- **Legs (hardware h / r):**
  - Each leg is a 4-mm plate under the bottom and two black rods Ø10 in a V to a foot at the floor.
  - End legs have the outer rod nearly upright, 30 in from the end, with a 110 spread. Middle legs are symmetric.
  - Counts per the hardware lists: 4 (0.01, 0.03, 1.02, 1.04); 5 (0.02, 0.04, the 5th in the middle, under the
    partition 6 in 0.02); 6 (1.01).
  - Each leg also has a small `tube` foot so the extent reaches the floor, since the checker ignores `rod`.
- **0.01:**
  - The door 7 is one panel with a 300×860 notch at its free edge (`shape: path`), between the two fixed shelves 8
    (y 634–1494). The glass 11 (860×300×3.5, as listed) fills the notch and moves with the door.
  - The free half of the door is reeded by milled grooves (face `grooves`, every 16, above and below the notch), because
    `fluted` can only cover a whole face.
  - A small upright pull «i» (Ручка СПА) sits on the glass by the free edge.
  - Two glass shelves 6 are in the showcase, and loose shelves 5 are in the closed top and bottom compartments.
- **1.01 wardrobe:**
  - Left column: 6-mm shelves 6 at the back joints 17 / 15 / 16, and 3 loose shelves 7.
  - Right column: fixed shelves 9 (over the drawers) and 8, the stile 10 between them, and the rail «Штанга 972»
    (p1, chrome Ø25) under 8.
  - Two reeded drawers 14.1 (1000 wide) are under doors 12 / 13.
- **1.05 bed:**
  - The headboard 1 (1680×950×25) stands on the floor. Two МДФ overlays are on it: 2.1 reeded, 170, at the top, and 2,
    200, plain at y 520–720. The oak strip between them (60) is the headboard showing.
  - Side rails 3 / 3.1 (25×200×2010, x 10–35 / 1645–1670) are at y 110–310. The foot 4 (1660) lies across their ends.
  - The metal base «m» (2000×1600): black rails, two rows of 26 slats, V legs at the foot corners and two middle legs.
    Its head end hangs on the headboard brackets.
  - A mattress 200.
- **1.03 mirror:** a disc Ø700×16 in the front colour, as in the catalogue (the frame is green / pepel, p. 13–14). The
  mirror Ø580×4 is on its face (1 mm of tape), which gives B 21.
- **1.04 bedside (by catalogue):** built like 0.02 at L506×B404×H507.
  - Carcass 506 (sides 375), a middle shelf, and two backs.
  - Fronts: lower 185 reeded, upper 180 plain. The photo on p. 13 shows them almost equal.
  - Drawers 136 / 130 high, 352 deep, 4 V legs.
- **Tables 0.11 / 0.12 / 0.13 (by catalogue):**
  - A top 25 (oak «Дуб нокс», grain along x, corners r 3) at y 710–735.
  - Four hairpin legs: a plate 120×60×4 and two rods Ø10 from 100 apart at the plate to a foot at the floor, in the
    long plane. Plate centres are 70 from the ends and 50 from the long edges.
  - Top thickness and leg size were estimated from the p. 14 drawings.
  - The model sets `"finish": "roksi-pepel"`, because the catalogue offers the tables in «Дуб нокс» only.

## Finishes (swatches on PDF p. 14, the «Варианты цветового исполнения» chart)
- `roksi-green` «Грин софт / Дуб Кантри золотой 389 SWN»:
  - front #3e4535 (crop 0.676,0.86,0.690,0.90, the plain half of the swatch; the p. 13 close-up of the front gives
    #282f20 in shade).
  - body #846c48 (0.695,0.86,0.724,0.90).
- `roksi-pepel` «Пепел софт / Дуб Нокс 392 SWN»:
  - front #c1bdb4 (0.776,0.86,0.789,0.90).
  - body #7c5e3f (0.795,0.86,0.824,0.90).
- Both oaks are textured decors, provisional colours for now: see `gen/roksi_decors.md`.
- `metal`: black (legs, pulls). The glass is clear.

## Cut lists corrected or completed (`gen/cutlists/`)
- **roksi-0-01:** row 7 (the door) count **1**; the reference JSON read 4.
- **roksi-0-03:** row 7 (loose shelves) count **2**; the JSON read 6.
- **roksi-0-04:** rows 9.2 / 9.3 (drawer sides, 2 + 2) are printed 3.5 and 19.5 thick. That is a misprint: the backs
  622 / 802 + 2×16 and the bottoms 632 / 812 = box − 22 prove sides 16. Written as 16.
- **roksi-1-05:** row 4 (the foot 200×1660×25) was missing from the JSON. Added from the page image.
- **Kept as printed** (plausible, built as listed): 0.02 front 11.1 is 16 thick (the other fronts are 19.5), and its
  drawer back 11.4 is 6 thick.

## Catalogue vs instruction / index.json
- Sizes in index.json match the catalogue (p. 14 text). The bed is L2060×B1680 in the catalogue (L = length). The model
  stores [1680, 2060, 950], x across the headboard, as for Flora.
- 1.02: the instruction sketch has the reeded fronts on top; the catalogue photo and cut-out show plain / reeded /
  plain / reeded from the top. Built as the catalogue shows it.
- The p. 14 cut-outs of 0.01, 0.02 and 0.04 are the mirrored variants of the instruction's layout. The instruction's
  layout is built, and it matches the p. 12 photo. 0.01 is «универсальный»: the door can hang either way.
- On 0.02 the catalogue's right-hand handles look 50–90 mm right of the fronts' centres. This is probably the photo's
  perspective, so they are centred.

## Engine / checker limits for the lead
- **Edge pull СА-1:** an L-profile over the top edge. The engine's `bar` only lies on the face.
- **Reeding on part of a face:** `fluted` covers the whole face, so the 0.01 door uses `grooves` lines instead. A
  `fluted` with a region / x-range would be closer.
- **Glass in a notch:** the part `glass` cannot take a tint; the showcase glass looks slightly grey in the photos.
- **preview2d:**
  - Does not draw `rod` parts (legs and hairpins are invisible on the sheets; only the plates and feet show).
  - Draws `bar` handles as circles of d/2, and ignores `shape: path` in the drawing, so the 0.01 notch does not show.
  - The ref overlays widen the ref box by how far the handles stand out: done by the scratch runner, not the checker.
- **V legs:** the catalogue legs may be set at 45° at the corners (their front projection varies). They are built in
  the front plane.

## Skipped
- None. The chair «Бруно М» on p. 14 is another collection's article.
