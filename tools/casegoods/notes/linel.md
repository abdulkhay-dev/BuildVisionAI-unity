# «Линель» (linel) — 6 модулей, все по инструкции

Catalogue «Корпусная мебель ч. II» 2025, p. 123–124 (spread 242–245). Generator `gen/linel.py` (writes the designs, the
completed cut lists and `gen/linel_catalog.json`). Every check sheet `pilot/linel-*.png` prints ok.

## Construction (IS-Linel-P6-934-1-0x, text tables; the bed P6-934-5-01 — Pinsk factory, table picture)
- Carcass ЛДСП 16 «Белый» on nail-in glides «Опора ФБ 482» (4 mm): sides 2089 + top 16 + glides 4 = 2109. The top lies
  over the sides, 1 mm proud each side on the wardrobe / shelving / chest (865 = 863 + 2; the chest's top is 867 per
  the table while the catalogue says 865 — built 867, noted in the model).
- The bottom sits between the sides on two plinth rails 90 (front one flush with the fronts, back one 30 in).
- Fixed shelves 562 / 432 / 546 deep; backs ХДФ 3 / 3.5 in grooves at z 8, joined on the fixed shelves (1.01: 436 +
  1221 + 332 over the heights; the table sizes prove the joints).
- Fronts ЛДСП 16 INSET, flush with the carcass front, 2 mm off the sides, 2–4 mm gaps.
- No handles: milled grips — a lens cut into the meeting edges of the doors (`shape: path`, 380–440 long, 15 deep) and
  a shallow arched notch in the top edge of every drawer front (photos on pinskdrev.by).
- Drawer boxes: sides / back ЛДСП 16, ХДФ bottom in grooves 10 up, 5 mm into the front; box widths from the tables
  (13 mm runner gaps). Wardrobe rail «r» 400 (chrome).
- 1.03 стеллаж: the door 7 (306) and the drawer 8.1 under five open cubbies; the upper back 10 is ЛДСП 16 (1463.5 ×
  531), the lower 11 ХДФ.
- 5.01 кровать раздвижная: end panels 25 with a cove strip 23×23 and a cap 60×18 each, the back panel 2000×515 with its
  cap 60×1994, 14 slats on the strip 22 and the spacer 21; the trundle (castors «J») carries the back 15, ends 11 / 13,
  the middle 12 (notched round the batten 14), the front rail 9 with the arched dip, 15 slats, two drawers 16 / 17 with
  milled frame fronts (V-groove `grooves` face + an arched grip) — the drawers ride in the trundle (one `slide` group).

## Cut lists completed / corrected (`gen/cutlists/`)
- linel-1-03: row 10 (1463.5 × 531 × 16) lost from the text layer; row 8.5 (drawer bottom 474 × 405) printed 16 thick
  — a misprint, written 3 (the other Линель drawer bottoms are 3).
- linel-5-01: the whole table (no text layer), from the page-2 picture.

## Finishes
- `linel-belyi` «Белый»: #f6f6f7, p. 124 swatch (crop 0.69,0.865,0.745,0.90, ±1.9).
- `linel-moloko-belyi` «Молоко / Белый» (the bed): front #fdfcfe (0.812,0.865,0.838,0.90), body #f5f5f6
  (0.846,0.865,0.871,0.90). Slats: role `birch` #d9bf94 (provisional, the photo). No textured decors.

## For the lead
- Grips are outlines: the engine cuts them through; the real grip is a milled bevelled recess.
- The bed's trundle carries its drawers (the engine gives a part one mover): the drawers do not open on their own.
