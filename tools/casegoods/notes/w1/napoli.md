# «Наполи» (napoli), П7.054: 11 modules, all by catalogue

Sources: catalogue pp. 15 (living-room photo, nearly front-on: 0.10, 0.11 and 0.20), 16 (bedroom photo: 1.14, 1.30, 1.41,
1.00, 1.24) and 17 (the photo of 0.11 and 0.21, the module cut-outs, the wardrobes' interior schemes and the «Капучино»
swatch). There are no instructions (no reference/napoli folder) and no network, so **every module is by catalogue**
("по каталогу, без инструкции" in the model notes). Generator: `gen/napoli.py` (it also writes `gen/napoli_catalog.json`).

## Construction (one scheme for the whole collection, taken from the photos)
- Carcass ЛДСП 16: the bottom spans the full width and stands on the legs, the sides stand on it, and a top ЛДСП 22
  lies over the sides. The top is flush with the sides and 2 mm proud of the fronts. The top's thickness comes from the
  p.15 photo: the front edge is 20 px at 0.876 px/mm.
- Back ХДФ in grooves 6 mm from the back edge (into the sides, bottom and top). Wardrobes and 0.21 have split backs,
  jointed behind a partition.
- Partitions stand on the bottom, in front of the back (z 10…).
- Loose shelves are 1 mm off the sides and 20 mm off the back and the front. Fixed shelves (horizontal partitions) run
  the full depth.
- The glass shelves of the vitrines are 6 mm.
- Overlay fronts МДФ 16 with a milled frame face (border 24, panel sunk 2 mm): 3 mm gaps, 1.5 mm reveal at the ends,
  3 mm under the top. They cover the bottom's front edge down to its underside.
- Glazed doors have a frame of 26 + rebate 6 and bronze-tinted glass. The cut-outs on p.17 show the glass
  brown-bronze, while the p.15 photo shows it lighter.
- Drawer boxes are 400 deep (sides/back 16, bottom ХДФ in grooves), 13 mm runner gap each side, 45 mm lower than their
  fronts.
- Handles: a bar «рейлинг» c-c 128 (d 160 in the engine, whose posts sit at ±0.4 d), bar 9 mm, standing 22 mm off.
  Vertical on doors, 20 mm from the free edge; horizontal and centred on drawers.
- Legs: tapered square legs in the body colour (50 → 36 mm) on 3 mm felt pads. The end legs lean out 10 mm; the inner
  legs lean only back or forth.
- The catalogue depth B is the top's depth: carcass B − 18, then the front 16, then the top's 2 mm. Handles stand out
  (the checker's "примечание").

Measured per module (the photo's scale from the catalogue size; the vertical scale separately where the camera looks
down):

| module | legs | layout |
|---|---|---|
| 0.20 тумба 1464×450×689 | 162 | 3 equal columns (partitions at 488 / 976): door, 3 drawers of 165, door. 6 legs incl. the middle pair |
| 0.21 тумба 1950×450×1061 | 200 | 4 columns (3 partitions). Drawers 158 on a fixed shelf over doors 675. Doors 1, 2 hinge left; 3, 4 right (handle positions in the cut-out) |
| 0.10 / 0.11 шкаф 2055 | 170 | Lower doors to 661, glazed doors 664…2030, fixed shelf at the joint, 3 glass shelves (1024 / 1361 / 1700), 1 shelf below. Handles at 1363 / 413 |
| 1.14 / 1.16 шкаф для одежды 2248 | 175 | Lower doors to 652, upper from 655, fixed shelf at the joint. 1-door sections: shelves at 1066 / 1460 / 1860. 2-door sections: hat shelf 1970 + rail 1880. Handles at 1100 / 400. Sections from the schemes on p.17 (4Д: 1+2+1, 3Д: 2+1). Legs at the ends and under the partitions / door joints |
| 1.30 комод 1000×454×1011 | 181 | 4 rows of 199, the top row as 2 drawers over a fixed rail with a middle divider |
| 1.24 тумба прикроватная 480×454×527 | 179 | 2 drawers of 160 |
| 0.50 стол журнальный 702×702×525 | 180 | Top 22 overhangs 16 all round. Open niche through the table over 2 drawers (front and back, opposite faces, as the p.17 photo of the open table shows) with a divider between them |
| 1.00 кровать 1678×2040×1070 | 300 | Headboard ЛДСП 22 (300…1070) with a soft panel of 8 vertical channels (730…1070, 60 thick, fabric role velvet). Rails ЛДСП 16 (300…610) forming a storage box: ХДФ bottom on 20×30 cleats. Black lifting frame with 22 slats, mattress 1600×2000 on it. 4 legs |
| 1.41 зеркало 1000×20×650 | — | Mirror 4 mm with rounded corners (R 120) on a hidden backing board ЛДСП 16 (R 100, inset 20). Mount wall. The catalogue says it hangs landscape or portrait; the design is landscape |

## Finishes
- `napoli-kapuchino` «Капучино 806 PO»: body `door_enamel_whitey#cecbc5`, taken from the swatch on
  p.17: `catpage.py 17 --swatch 0.715,0.86,0.755,0.905` (flat, ±0.7). The photos render it warmer and darker (#b2a8a1
  on p.15, #ab9d94 on p.16); the swatch wins. The bedroom photo's wardrobe looks taupe only because of the light.
- Role `fabric`: `velvet#8d7b73`, the headboard's velour, from `catpage.py 16 --swatch 0.72,0.52,0.735,0.57`.
- `metal` (handles): `gold#6d6158` dark antique bronze, from a handle post on p.15:
  `--swatch 0.4318,0.677,0.4352,0.684`. It is a small crop, so the value is approximate.
- No textured decors (`gen/napoli_decors.md` says so).

## What the format / engine could not express (for the lead)
- **Handles:** the catalogue handle has square end posts bigger than the bar. The engine's `bar` has round thin posts
  at ±0.4 d.
- **Legs:** the leg has a milled ring near its top that is not modelled.
- **Checker drawings of rods:** `rod` legs are not drawn in the checker's views, so the sheets show only their pads.
  The checker also counts no extent for rods; the 3 mm pads carry the floor level.
- **Back drawer of the table:** engine handles stand out of +z only, so the back drawer's handle of 0.50 is three
  `rod` parts (bar Ø9 + two square posts) in its move. The back drawer moves by `slide` `by [0, 0, -250]`.
- **Bar handles in preview2d:** preview2d draws and boxes a `bar` handle as a circle of diameter d (hence the round
  blobs on the sheets and the L/H "примечание" on 0.11). The engine builds the real bar.
- **Glazed-door rim:** the thin bronze rim round the glass (an aluminium-look lip) is not modelled; the tinted glass
  stands for it.
- **Bed:** the lift's gas struts and hinge are not modelled. The side rails' possible curved lower edge (unclear in
  the photos) was left straight.

## Sizes
All catalogue sizes in index.json agree with the text on p.17; nothing was corrected. Depths/heights inside the
modules were read off perspective photos: accuracy is about ±10 mm, not "to the millimetre".

## Skipped
None (the collection has no chairs or upholstered pieces).

Check sheets: `pilot/napoli-*.png`, all "ok". Refs: the p.15 photo for 0.10 / 0.11 / 0.20, the p.16 photo for 1.30 /
1.24, the p.17 cut-outs for 0.21 / 1.14 / 1.16 / 1.41 / 0.50 (perspective, rough), none for the bed (no front view
exists).
