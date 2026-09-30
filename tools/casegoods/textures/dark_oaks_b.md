# dark_oaks_b — six rustic / sawn oak films

Generator `tools/casegoods/textures/dark_oaks_b.py` (numpy + Pillow; PyMuPDF only for the sheet). It builds on
`tools/doors/textures/eco_oak.py` (`wood_structure`: sawn boards cut from logs, so it has growth rings, cathedrals,
pores, rays, knots, checks and streaks), with this family's patterns registered in memory only. On top of that it adds
streak layers in their own colours (the pale grey streaks of the truffle and smoky decors), saw marks across the grain
(built with `finish_kit.straight_lines`), and a colour fit.

**Colour fit.** The base colour is solved so that the texture, seen the way the catalogue swatch is (box-downsized to
~0.6 px/mm and measured with `gen/catpage.py`'s trimmed sRGB mean), has the swatch's exact colour. Every map is
2.0 m × 1.0 m, tiles both ways, has its grain along U, and is matt (SWN smoothness 0.30).

Check sheet: `sheets/dark_oaks_b.png`, with five columns: swatch | texture at the swatch's scale | photo | texture at
the photo's scale | 1 m. Vertical-grain crops are turned so the grain runs along x in every column.

| id | decor | swatch used (page, crop → mean) | texture (swatch view) | ΔE76 | texture linear mean |
|---|---|---|---|---|---|
| cg_dub_stirling | «Дуб Стирлинг 374 SWN» | p. 93 `0.764,0.86,0.815,0.9` → #8b6b4b (flat ±10.7) | #8b6b4b | 0.00 | #8b6b4b |
| cg_dub_tryufelny | «Дуб Трюфельный» | p. 131 `0.755,0.85,0.81,0.89` → #786657 (±13.5, a decor) | #786657 | 0.00 | #786657 |
| cg_dub_artizan_tryufel | «Дуб Артизан Трюфель» (МДФ 19) | p. 30 `0.748,0.858,0.775,0.900` → #6e5242 (flat ±8.3) | #6d5242 | 0.50 | #6e5242 |
| cg_dub_monastyrsky | «Дуб Монастырский 375» | **no swatch**: product photos (see below) → #655249 | #65534a | 0.58 | #645249 |
| cg_dub_navarra | «Дуб Наварра» | p. 74 `0.715,0.86,0.772,0.908` → #956b40 (flat ±10.0) | #956b40 | 0.00 | #956b40 |
| cg_dub_monterey | «Дуб Монтерей» | p. 64 `0.65,0.865,0.672,0.905` → #747474 (flat ±4.9) | #747474 | 0.00 | #747474 |

## Per material

**cg_dub_stirling** (Гранде: the whole collection; Хольтен Лофт: carcass). A warm honey-brown oak with strong
cathedrals and straight lines, scattered dark knots with rims, and fine checks.
- The p. 91–92 close-ups read #886647 to #977456, which confirms the p. 93 swatch.
- **Conflict:** Хольтен Лофт's p. 134 «Каркас» swatch reads #755a4a (ΔE 11.7 from p. 93). It is darker, smoky and
  greyer, and the p. 134 room photo shows the same, so it may be a different print sold under the same name. I used the
  p. 93 swatch: it carries the code 374 SWN, it is the main user (the whole of Гранде), and the close-ups confirm it.
  If Хольтен must match its own chart, it needs a darker variant.
- «МДФ 16/18 ДУБ СТИРЛИНГ» in the Хольтен instructions names the fronts. The catalogue calls those «Дуб Ланцелот», so
  they are not this material.

**cg_dub_tryufelny** (Бритиш Бум: carcass; Плато: body). A Sonoma-truffle look: grey-brown ground, pale grey streaks,
dark lines, soft cathedrals, patchy saw marks across the grain, and few knots.
- The p. 131 bed photo (#756353) agrees with the swatch.
- **Conflict:** Плато's p. 140 swatch is #9c886c (ΔE 15.0), a much lighter greenish-beige print. I used p. 131
  because it is the larger user, it has a product photo, and its character is the classic truffle.

**cg_dub_artizan_tryufel** (Ариста accent strips, inserts and drawer fronts). A dark tobacco-brown oak: long straight
fibres, board-to-board striping, lengthwise cracks, small knots, and few cathedrals. The door strips on p. 30 read
#6c564e and agree with the swatch. The product pictures are tiny, so only the swatch is a reliable reference for
structure.

**cg_dub_monastyrsky** (Сорренто accent). The catalogue has no swatch for this decor. Its colour comes from two photos:
- **Site photo** 8C3A1962.jpg, the front-on bedside drawer. Raw it reads #4d413a with a cool cast. I white-balanced it
  against the «Дуб Бордо лайт 380» plinth in the same photo, which faces the camera, using that decor's p. 27 swatch
  (#e7e7e1). This gives #665044.
- **Catalogue room photo** p. 113, the headboard strip, reads #65554f.

The two agree, so the target is #655249. decors.md's provisional #5c4c44 is ΔE 3.2 darker, because it averaged in the
un-balanced photo. Character: dark smoky oak with dense fine light pore strokes, long black lengthwise cracks, dark
cracked knots and grey streaks. Doubt: the colour is photo-derived and depends on the white balance.

**cg_dub_navarra** (Деко: body, fronts, back). A golden-honey rustic oak with open cathedrals, dark knots and short
dark lengthwise cracks. The p. 74 close-up reads #986e3c and agrees with the swatch. The cut depth has fewer turns, so
the cathedrals do not form a regular chain of lenses.

**cg_dub_monterey** (Мокко carcass). A mid neutral-grey oak with straight fibres, soft cathedrals, grey streaks and a
few swirls. The swatch is perfectly neutral. The only product picture (the side of shkaf-kupe 1.10) is tiny and reads
lighter and slightly mauve (#817b81, ΔE 5.5), which is lighting. I followed the swatch.

## Unsure / notes
- The swatch scale (0.6 px/mm, so a chip shows about 300 mm of decor) and the photo scales on the sheet are estimates.
- Repetition: one tile is 2 m along the grain, so a 2 m wardrobe side shows it once. Across the grain the tile repeats
  every 1 m. That is visible only on faces wider than 1 m with the grain across, such as long tops or bed rails,
  viewed from afar.
