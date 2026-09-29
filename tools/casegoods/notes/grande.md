# «Гранде» (grande, П6.606) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF pages 87–93 (printed 170–183); p. 93 has every module's cut-out with its
size and the two colour swatches, p. 91 / 92 the close-ups (fronts, handles, the black inserts). Generator
`tools/casegoods/gen/grande.py` writes the 32 designs, `gen/grande_catalog.json` and the 17 completed cut lists
`gen/cutlists/grande-*.json`. Every design prints `ok` in `gen/check.py`; sheets `pilot/grande-*.png` (the instructed
ones over the instruction's front view where one exists).

**32 articles, not 33:** index.json and the catalogue text list 32 Гранде codes (the chair «Сабрина М» on p. 88 is not
a Гранде code and is skipped).

## Modules

| by instruction (17) | by catalogue / photo (15) |
|---|---|
| 0.01, 0.02, 0.04, 0.05, 0.07, 0.09, 0.10 (living room, tables without sizes); 1.01, 1.02, 1.04, 1.05, 1.06, 1.09, 1.10, 1.16 (bedroom, tables with sizes); 2.17 (desk, no sizes); 4.12 (dining table, sizes) | 0.06 (TV, as 0.02 with two columns), 0.11 (shelf as 0.10), 0.13 (coffee table), 1.08 / 1.11 / 1.12 / 1.13 (beds as 1.09), 1.17 (dressing table, the 2.17 construction with two drawers), 2.14 (desk as 2.17), 2.15 (pedestal on castors), 3.01 (hall wardrobe, 0.01 carcass, one door), 3.02 (bench, one drawer), 3.03 (two drawers over two doors), 3.04 (hanger panel, 5 hooks), 3.05 (framed mirror) |

## Construction (read off the vector drawings)

The instructions are CAD exports to scale. The bedroom ones (P6-606-1-xx, 4-12) print every size in the page-4 table
(text layer; parsed by position — 1.01, 1.02, 1.05, 1.06, 1.09 were not in the reference JSON). The living-room ones
(IS-P6-606-0-xx, 2-17) print no sizes: their parts were measured on the front / side / top views of p. 1 (line centres,
scale from the overall size, ±1.5 mm), with the bedroom tables as the model of the construction.

- **Frame.** Each front corner post is an L of a front bar (80 wide) and a side bar behind it; each back corner one bar
  80 deep. The front bars are 10 shorter than the back posts, and a black insert «Вставка», 10 thick, caps the L
  (modelled as an L outline in the top plane, so it does not collide with the side panel). The posts stand on glides
  «ФБ 482» (4 or 5 mm: 1.04 is 849 = 4 + 765 + 80, the 0.09 unit 850 = 5 + 765 + 80 with the same posts). An 80 mm
  apron runs round the top (front one full width, side ones B − T), the 16 top panel lies flush inside it, and there
  are lower rails 80 high, 75 over the glide (front rail = W − 162).
- **Bar thickness.** Bedroom line: bars 25 (tables of 1.01 … 1.16), post 80 × 105, inserts 80 × 105 × 10.
  Living-room line: every side / top view (0.01, 0.02, 0.04, 0.05, 0.07, 0.09) draws the front bars and the aprons 16
  thick and the front post 80 deep in all (side bar 64), so the living-room modules and the hall modules (B 420, by
  photo) use T = 16, post 80 × 80. **For the lead:** the photos cannot tell 16 from 25; if the living room turns out to
  use 25 too, only `line="old"` → `"new"` changes in the generator (B stays the catalogue's).
- **Carcass.** ЛДСП 16 inside the frame: the sides T in from the outer faces (their faces are seen recessed between the
  posts), standing 82 over the glide up to the top panel; the bottom 152 over the glide (bottom height = 1.04's 747 /
  661 arithmetic); runner walls «Перегородка» by the openings (bedroom: at 73…89 — the rails between them are
  W − 178 long in every table; living room: flush with the front bars' inner edge); rails 80 deep, 16 thick between the
  drawers; a bar 64 high behind the front apron («Брусок» / «Брусок (обманка)», split by the partitions); middle legs
  «Опора» 152 high under the partitions (100 deep; the TV units' and wardrobes' drawings show them under the lower rail).
- **Fronts** 16, flush with the frame's face, 3 mm in from the bars, starting 10 over the lower rail and ending at the
  front bars' top. Frame doors «Дверь рамочная» of the vitrines: a glazed front with frame 80 (drawn 80 on every door),
  clear glass; glass shelves 6 mm seen through them where the views draw them; LED pucks («Светильник Orbit») under the
  top of each vitrine section.
- **Drawers:** ball runners 350 (0.02 / 0.06: 450, «DB4501Zn/450»), sides 16, the back 14 over the bottom, ХДФ bottom
  in grooves (bedroom sizes exactly as the tables: e.g. 1.04 box 798 = 766 + 2 × 16 between the walls 824 − 2 × 13).
- **Backs** ХДФ 3.5 in grooves (the wardrobes' pieces and the chests' two halves as the tables give them; the living
  room: one piece per section, joints behind the fixed shelves).
- **Wardrobes 1.01 / 1.02 / 1.16:** sections 478 / 928 / 884 wide as the shelves; fixed shelves at the back joints
  (backs 1273 + 422 + 422, 1749 + 370); a rib 10 (1737 × 128) at the back of the hanging section; the strip «Накладка»
  28 / 27 (2019 / 2025 × 80 × 16) is screwed to the back of the middle door along its meeting edge (p. 8 step 4) and
  moves with it. Door hinge sides and the strip's edge are my reading (doors hinge on the sides and on the partitions).
- **Beds:** headboard 1 (1120 × 950 × 25) with a face frame of strips 4 (top) and 5 (sides); side rails 3 between the
  headboard and the footboard 2 (964 = the rails' outer faces); the foot carries strips 6 / 7 / 8 on its outer face, so
  L = 25 + 2010 + 25 + 25 = 2085. Metal base «m» (black bars + slats) and a mattress. Doubles: W = sleeping width + 220.
- **Dining table 4.12:** frame of long bars 2 (1443, 16) and end bars 3 (812, 25) with cross bars 9; the L legs
  (4 + 6, 5 + 7: 125 + 25 = 125 square) are bolted round the frame's corners outside (frame 1493 × 894 under the top
  1500 × 900 — the only reading where every table size fits).
- **Desk 2.17:** L legs of two 25 boards (80 face + 80 side, as the side view: 25 + 82), black inserts (hardware
  «Декоративная вставка»), sides 2 / 3 between the legs, «Царга» 4 at the back (240 … top), «Брусок» 5 under the top at
  the front.

## Finishes

Two colour options, both textured decors (listed in `gen/grande_decors.md`, provisional plain colours):
- `grande-yukon` «Дуб Юкон 358 SWN»: body #8c8685 (p. 93 swatch `--swatch 0.69,0.86,0.74,0.9`), handles satin silver
  `chrome#b3b3b3` (the Юкон photos p. 87–90).
- `grande-stirling` «Дуб Стирлинг 374 SWN»: body #8b6b4b (`--swatch 0.764,0.86,0.815,0.9`), handles black (close-ups
  p. 91–92).
- Inserts and glides `black`; hooks black; the hanger rail chrome; collection metal chrome.
- Handles «ручка-скоба С36»: bar 170 long (drawn 169–171 in every view), square posts, 30 mm out of the face (side
  views).

## Completed cut lists (`gen/cutlists/`) and where sources disagreed

- 1.01, 1.02, 1.05, 1.06, 1.09: parsed from the page-4 text layer (reference JSON empty).
- 1.04: the drawer rows 24.1–24.5 are per drawer (row 24 «в т. ч. — 3»): count 3; **24.5 printed 776 × 355 × 16** —
  it slides into grooves like 20.5 (1.05) and 21.5 (1.06), both 3.5 → 3.5.
- 0.02: the reference parse lost rows 19 / 20 and wrote the drawers as 241 … 265 → 24.1 … 26.5 from the page picture;
  the table swaps the codes of 27 / 28 (Вставка) — numbers kept.
- 0.01 row 9 and 0.04 rows 10 / 26.4 (glass, no code) were missing from the reference JSON; 0.05, 0.07, 0.10 tables
  have no text layer: transcribed from the picture (0.05 has no row 28, 0.07 no row 35).
- Old-format tables have no sizes: every size in those cut lists is the design's part (read off the drawing).
- **1.10 mirror:** p. 93 writes B21, p. 91 and index.json B20; the table gives 16 + 4 = 20 → 20.
- **2.17 desk:** the instruction's top view is dimensioned 1150 × 700, the catalogue and index 1160 × 710; the front
  view (scaled to 1160) shows the top flush with the legs → built 1160 × 710 as the catalogue. Check against a photo.
- **4.12 table:** the catalogue writes L1500/2000, index.json 2000 → built extended (the leaf 8 in place, the halves
  1 at the ends), model size 2000 × 900 × 760.
- **Beds:** size written [width, 2085, 954] (x = width, z = length, as Тринити 1.05 in wave 1); the catalogue's L is
  the length.
- 0.10 shelf: its views have different x / y scales (8.9 / 6.0 mm/pt); the shelf measures ~19 thick → 16 (the only
  table panel thickness of the line), 22 over the back board's lower edge.
- Wardrobe views (1.01, 1.16) are squashed vertically (x 17.9, y 19.6 mm/pt): heights from the tables only.

## Engine / checker notes for the lead

- Nothing essential was left out. Frame doors = glazed fronts (frame 80, rebate 10); the inserts are `shape: path`
  L outlines in the top plane (check.py tests them by outline; preview2d would warn about their boxes vs the sides).
- The dining table's extension has no move (both halves and the leaf are static); a `slide` of the halves with the
  leaf appearing would need a "hidden when closed" option.
- Bed metal base «m»: two black bars + a slat panel; it and the mattress are not cut-list parts.
- The hall hanger's hooks are `knob` handles (black); a hook model would look closer.
- The pedestal 2.15's castors are black tubes Ø36 × 40.
