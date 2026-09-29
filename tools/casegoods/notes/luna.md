# «Луна» (luna) — 15 модулей: 7 по инструкции, 8 по фото

Catalogue p. 121–122 (spread 238–241), ПУП «Пинскдрев-Заславль». Generator `gen/luna.py`. All 15 check sheets ok.

## Sources
- Instructions (downloaded from a.pinskdrev.ru; tables «№, наименование, a×b, n» as pictures on p. 3, no thickness —
  ЛДСП 16 / ДВП 4 by the construction): 1.09 P049-1401, 1.14 P049-104, 1.31 LUNA_049-301, 1.72 LUNA_049-702,
  2.52 LUNA_049-502, 2.53 P049-503, 2.62 P049-602 (the site also links it to 2.61 as P049-602-1.pdf — the same file).
  Transcribed to `gen/cutlists/luna-*.json`.
- By photo (pinskdrev.by product photos, catalogue cut-outs p. 122): 1.11, 1.12, 1.13 шкафы комбинированные, 1.21 тумба,
  1.71 полка, 1.01 кровать 1-09, 2.51 стол, 2.61 стеллаж.

## Construction
- Adjustable plastic feet «опора 50×17» (17 mm): 840 + 17 = 857 (chest), 1888 + 32 + 17 = 1937, 2000 + 17 = 2017.
- Tall pieces: top and bottom full width, the sides between. The chest 1.31: the bottom 800 full, the left side 806 on
  it, the top 782 over the left side up to the right side 824 (full height, 2 mm step at the top right); the «Оникс»
  shelf tower 250 beside it (bottom 248, outer side 728, top 250, two shelves 232).
- Backs ДВП 4 nailed over the back edges: 4 + 380 + 16 = 400, 4 + 300 = 304 (the catalogue B confirms the 4).
- Overlay fronts 16 with 4 mm reveals; drawers: the front is the box's front wall, ДВП bottom nailed under; 1.31 has a
  lengthwise batten 14 under each bottom.
- Desks: 2.52 — leg panel 2, the pedestal 3 / 4 with back 6 between two shelves 7, the rail 5, three drawers; 2.53 —
  two leg panels set 49 in, two rails 4 (634), a central pedestal on feet (bottom 8, sides 5 / 6, partition 7,
  shelves 9 / 10 over the drawers, niches above with the battens 11), 6 drawers; the pedestal sits 1 mm lower (feet
  16) because 17 + 16 + 702 = 735 > 734.
- 1.14 угловой (for the back-left corner, walls z = 0 and x = 0): read from the table and the plan: ДВП on both walls
  (15–21 fill 1004 × 2000 on each wall exactly), top / bottom 1000 × 1000 cut on the diagonal x + z = 1386, end sides 2
  / 3 (378), left column: partition 5 and five shelves 10; right column 400 wide: partition 6 (300), batten 11 on side 3
  (the runner spacer), two drawers 22, rail 13, four shelves 12; the corner: ЛДСП back 7 (584) on the back wall, two
  big shelves 8, the stiffener 9 on the left wall, the rail N (660) from 7 to 5. Two doors 14 (437 × 1996) on the
  diagonal.
- By-photo modules use the same scheme: a lower box (bottom on feet, sides, a fixed top 449…465) with a lift-down flap
  or drawers, the pine wardrobe on it and an open «Оникс» tower (4 shelves, 32 lower than the wardrobe). 1.13 — three
  doors, two drawers under doors 1–2, a flap under door 3 + the tower; 2.51 — a leg panel, the top to 960, a pedestal
  480 with two drawers, a door under the top and an «Оникс» box level with the top; 1.01 — a daybed: ends with the back
  top corner rounded, back panel, front rail, ЛДСП base on cleats, two drawers with arched grips.

## Finishes (p. 122 swatch «Сосна рандерс» / «Оникс»)
- `luna-sosna-oniks`: body #c7c8c3 «Сосна рандерс» (0.715,0.865,0.738,0.90), role `accent` #726e65 «Оникс»
  (0.749,0.865,0.772,0.90, textured ±7), role `white` for the backs. Handles: dark square bars ≈160 (p. 122 close-up,
  #231a16) — collection metal `black`. Decors in `gen/luna_decors.md`.
- index.json lists «Венге» for the first six codes (the catalogue text) — the site sells them only in «Сосна рандерс +
  оникс»; the site colour is used.

## For the lead
- **Diagonal doors (1.14):** written as `moulding` slabs swept along the diagonal (profile `luna-door-16x1996`, path in
  the top plane at the door's mid-thickness) with an explicit hinge `axis`; the handles carry `rot` 45°. A `front` with
  `rot` would be the proper form, but check.py measures turned parts by their bounding box and then reports false
  overlaps with the top / bottom — please check the two doors swing correctly in 3D (hinge axis at the outer edges).
- Photos show the tower sides in a darker «Оникс» than the swatch; the swatch was used.
- Brackets of the bed guard 1.09 (hooks 105 × 27) are not modelled (they would add depth to B16).
