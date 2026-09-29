# «Соната Бум» (sonata-bum) — 25 дизайнов, все по каталогу

Catalogue p. 125–128 (spread 246–253). No instruction exists in reference/, no product page on pinskdrev.by (only two
«уценка» photos of the beds 2-14 / 2-16 «Соната» without prints, and guessed a.pinskdrev.ru PDF names returned 404).
Every module is **by catalogue** (note «по каталогу, без инструкции» in the models); overall sizes are exact, inner
divisions are read off the cut-outs and room photos (±20 mm). Generator `gen/sonata-bum.py`; all 25 check sheets ok.

## Construction (one scheme, the «Бум» line; Челси Бум's instructed modules as the model)
- ЛДСП 16 «Сосна Карелия»: sides to the floor, bottom on a 60 plinth rail recessed 20, top between the sides, ХДФ 3 back
  in grooves; overlay fronts 16 (2 mm reveals, 3–4 gaps); satin-chrome knobs (Ø30); drawers ЛДСП 16 + ХДФ, 13 mm gaps.
- Tall pieces: body 2250 + a wave-shaped crown board 90 (outline: ends 30, a central hump) standing on the top 32 behind
  the door faces — 2340 as catalogued. 1.19 (2200) has none.
- 1.06 шкаф 3д: left door (shelves behind), middle mirror door (12 + mirror 4 in a 45 border) over two drawers, right
  door; the middle and right share the hanging space (hat shelf + rail); 1.08 угловой 2д: like «Луна» 1.14 — walls z = 0
  and x = 0, end sides 400, top / bottom cut on x + z = 1424, wings with 5 shelves, the corner with a hat shelf and a
  rail, two doors 438 on the diagonal (swept slabs, profile `sonata-door-16x2186`), the crown turned 45° (`rot`).
- 1.12 шкаф 2д: two doors 636 below, open shelves above in two columns; 1.15: two drawers, an open niche, a tall door;
  1.18 стеллаж: 7 shelves; 1.19: an end shelving with quarter-round shelves (outline) on a side and a back panel.
- 1.21 / 1.22 тумбы: lower doors / drawers 473 high, two open rows above, 3 / 2 columns.
- 1.70 / 1.71 столы: pedestals 450 (niche 536…708 over a door or two drawers), a leg panel (1.70), a middle drawer
  under the top (1.71), a modesty rail.
- 1.25 сундук: box with a lift-up lid (B440 per p. 127 and index.json; p. 128 writes B400).
- 1.40 двухъярусная (x = length 2492): a stair of four step-drawers 450 on the left, end panels 1760 with rounded tops,
  the upper bed with a front rail, a guard rail 1560…1700 and a back rail, the lower bed with back panel, front rail,
  two drawers with arched grips.
- 1.45 раздвижная (x = length 2058): high rounded ends, back panel, the upper base on the front rail, the trundle on
  castors with an arched front rail and a 1950 mattress.
- 1.50 полка: two shaped end brackets, the plate and a back rail. Coupe 1.52 / 1.53 / 1.55: as Челси Бум, all panels
  «Карелия», 1.55 the middle door a mirror.
- Beds 1.80–1.83 (widths 950 / 1250 / 1450 / 1650, x across the bed): headboard 805 with the crown outline, footboard
  540 with rounded corners, side rails, ЛДСП base on cleats, two drawers with arched grips under the right rail
  (`slide` +x), a divider between them. 1.35–1.38 are the same beds **with the bedside shelf units** (356: side panel +
  three round-fronted shelves) — one on the left for 1-09 (B1306), both sides for the others (1962 / 2162 / 2362): the
  design size is the «с полками» size the catalogue gives in brackets (noted in the models).

## Finishes
- `sonata-bum-karelia` «Сосна Карелия» #e6e7e1 (p. 128, crop 0.715,0.865,0.772,0.90, ±1.7), role `white` for the backs;
  metal `chrome`. Decor in `gen/sonata-bum_decors.md` (already listed by other collections).

## For the lead
- By catalogue only: please compare with any product photos if they appear on the site later.
- The crown is a flat board with a wave outline; the catalogue shows a slightly carved scroll at its centre.
- Diagonal doors of 1.08 are swept slabs (see «Луна» notes); the knobs and the crown use `rot`.
