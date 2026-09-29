# «Вена» (vena, П6.115) — notes

Catalogue p. 115 (PDF; printed 226–227): a kids' room photo, front-on module cut-outs with sizes, the swatches
(«Фасад»: Персидский жемчуг / Базальт; «Каркас»: Гикори Кингстон). All 6 articles have an instruction
(IS-P6-115-*, downloaded to tools/casegoods/.cache/is/), so **every module is by instruction**; the site's product photos
(front-on studio shots) confirm the colours of each front. Generator `gen/vena.py` (writes the 6 designs and
`gen/vena_catalog.json`), decors `gen/vena_decors.md`, completed / transcribed cut lists `gen/cutlists/vena-*.json`,
sheets `pilot/vena-*.png` — all ok, the red outlines sit on the instructions' front views (1.01, 1.02, 1.05, 2.03-01,
2.04).

| id | code | what |
|---|---|---|
| vena-1-01 | П6.115.1.01 | шкаф для одежды 2Д 1008×590×2234: basalt full-height door left (shelves), pearl door over 3 drawers right (rail) |
| vena-1-02 | П6.115.1.02 | тумба 1300×435×782: 3 drawers, open niche (basalt shelf + upright), pearl door |
| vena-1-05 | П6.115.1.05 | кровать 1-09 2042×940×720: a day bed along the wall with three drawers on castors |
| vena-2-03-01 | П6.115.2.03-01 | стол письменный 1300×650×782: pedestal of 3 drawers on legs (left), panel leg right, modesty panel |
| vena-2-04 | П6.115.2.04 | шкаф комбинированный 900×435×2234: doors (pearl up, basalt down) round an open niche, open shelf column right |
| vena-2-06 | П6.115.2.06 | полка 1300×260×340 (wall): two cubbies under a 700 top, a long open section, a pearl back board |

## Construction
- ЛДСП 16 «Гикори Кингстон». Top and bottom run the full width and depth (435 / 590 / 650); the sides stand between them
  and are 17 shallower (418 / 573 / 627): the fronts (ЛДСП 16) lie on the sides' front edges between the top and the
  bottom, flush with the top, 1 mm off the sides; 3 mm gaps, 2 mm to the top / bottom (3 × 206 + 2 × 3 + 2 × 2 = 628,
  1449 + 3 × 206 + 3 × 3 = 2076).
- Partitions and fixed shelves are 16 shallower than the sides and stand at z 10–412 in front of the backs (2.04's
  partition runs the full depth: its right column is an open shelving without a back). Backs ХДФ 3.5 in the sides'
  grooves (z 6–9.5), one per section, joined behind the partitions and fixed shelves — the cut-list widths are the inner
  width + 12, the heights meet on the fixed shelves (1.01: 351 + 1384 on the left, 631 + 1103 on the right, 984 across the
  mezzanine; 2.04: 691 + 678 + 716).
- Legs «Опора Вена» (h): turned tapered wooden legs, 122 under the bottom (782 = 122 + 16 + 628 + 16), on flanges and felt
  pads; the end legs splay 14 mm outwards as drawn. 4 legs on the wardrobes and under the desk's pedestal; 6 on the тумба
  (4 corners + 2 at mid-depth at x 436 / 864 — the front and back views show 4 legs at mirrored positions). Built as
  round `rod`s Ø 45 → 28 + a felt pad.
- Handles «k»: turned wooden knobs Ø 44 (role `wood`), 60 mm under the top edge of the drawers, 60–65 mm from the free
  edge of the doors (wardrobe doors at 1198, as drawn).
- Drawer boxes: sides / back ЛДСП 16 screwed to the front, ХДФ bottom in grooves, 14 mm per side (350 / 500 runners).
- 1.01: left column — fixed shelves 7 (bottom) and 6 (top), 3 loose shelves 8; right column — fixed shelf 7 over the
  drawers, a rail «w» 472 under the fixed shelf 6.1; the mezzanine is closed by the doors (9 = 2076, 10 = 1449).
- 1.02: the middle niche (296 wide) has the fixed shelf 7 and the upright 8 over it, both «Базальт» with the pearl back
  15 (the photos); a loose shelf 9 behind the door; door hinged right.
- 2.04: fixed shelves 6 behind the door joints (y 820 / 1498), loose shelves 8 in the three left compartments, four
  fixed shelves 7 in the open right column (5 equal openings), both doors hinged left with the knobs at the free corners
  near the niche (as drawn).
- 2.03-01: pedestal sides 628 on the bottom 5 (on legs), its back 6 ЛДСП 16 between the sides, the top 4 over all (6 mm
  over the fronts), the right leg panel 3 (759) on three glides «o» (7 mm), the modesty panel 7 (320) under the top
  between the pedestal and the leg panel, flush with the back (its depth position is not drawn — assumed at the back).
- 1.05 bed: a day bed, stored **[2042, 940, 720] with x = the length**, because its front is the long side (the drawers);
  the other beds keep x = width. End panels 3 / 4 (716 × 940) on 4 mm glides, their front top corner rounded (outline,
  R ≈ 200 as in the cut-out). The back rest 2 (666) along the wall, a spine 5 (300 × 2010) at mid-depth, dividers 9
  (rear, 428) and 7 (front, 463) under the joints of the fronts, the base 1 (907) on top of them (the instruction warns
  its colour may vary — a neutral light grey), the front rail 6 (128) over the drawers. Three drawers on castors «o»
  (4 each, h 43): fronts 666 between the end panels; the middle box is 8 mm narrower (12.4 = 596, 12.5 = 606), so the
  middle compartment is 654 and the outer ones 662. 21 glides «h» under the ends, spine and dividers; a mattress
  2000 × 900 × 160.
- 2.06 shelf: bottom 2 (1300), back board 1 (308 × 1298, ЛДСП 16 pearl) standing on the bottom, uprights 5, 4, 4 under the
  700 top 3 (two cubbies of 326), the right end 6 without a top; wall-mounted on hangers «q».

## Which front is which colour (the odd code = the odd colour)
The site photos and the p. 115 cut-outs give the colours; the cut lists give one front a separate code, and that is the
odd-coloured one: 1.01 middle drawer 12.1 pearl (two basalt 11.1, as drawn); 1.02 top drawer pearl (the drawing puts
12.1 at the bottom, the photos show the pearl one on top — built pearl on top, numbered 12.1); 2.03-01 middle drawer pearl
= 9.1 (the drawing puts 9.1 at the bottom); 1.05 middle drawer basalt = 12.1. Doors: 1.01 left basalt / right pearl;
1.02 pearl; 2.04 upper pearl / lower basalt.

## Finishes
`vena-zhemchug-bazalt` «Персидский жемчуг / Базальт; каркас Гикори Кингстон»:
- body «Гикори Кингстон» #a1876f — the p. 115 «Каркас» swatch (crop 0.845,0.86,0.895,0.905, flat) — a decor, provisional.
- front «Персидский жемчуг» #dfe3e2 — the lead's reference for this colour (p. 132 swatch, as in wave 1); the p. 115 swatch
  prints #d8d3cc (crop 0.755,0.86,0.785,0.895) and the studio photos warmer.
- role `accent` «Базальт» #4d4e49 — the p. 115 swatch (as Скай / Джио in wave 1; crop 0.795,0.86,0.82,0.895 reads
  #4e4f4a).
- back = pearl (the visible niche backs are pearl in the photos; wardrobe backs the same).
- role `wood` #b39a7c — the turned legs and knobs (natural wood, photos; listed in `gen/vena_decors.md`).
- metal `chrome` (the hanging rail only).

## Cut lists completed (gen/cutlists/)
- vena-1-01: row 12.1 (206 × 500 × 16) added from the page image.
- vena-1-02: rows 7 (294 × 402), 11.5 (422 × 345 × 3.5 ×3), 14 (638 × 482 × 3.5 ×2) added.
- vena-1-05: rows 7 (300 × 463 ×2), 10.1 (282 × 666) added.
- vena-2-03-01: the instruction has no text layer — the whole table (13 rows) transcribed from the page.

## For the lead
- The day bed's axes (x = length) differ from the other beds on purpose (its front is the long side).
- Leg splay is only sideways (as drawn); the knob is the engine's `knob` (a flat disc on a stem) — the real knob is a
  turned mushroom.
- check.py draws unresolved roles (`accent`, `wood`) in the body colour on the sheets.

## Skipped
Nothing (the chair in the p. 115 photo is not a Вена article).
