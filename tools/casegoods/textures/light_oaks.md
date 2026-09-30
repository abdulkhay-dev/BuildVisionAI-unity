# Family `light_oaks` — light / honey oak films (wave 6)

Generator `tools/casegoods/textures/light_oaks.py` (run with `/private/tmp/claude-501/venv/bin/python`; `--sheet`
redraws `sheets/light_oaks.png`, `--analyze` prints swatch vs texture colour and L* contrast). Builds on the door
machinery without editing it: `eco_oak.wood_structure` (boards, rings/cathedrals, pores, rays, knots, checks),
`eco_oak.albedo_linear / normal_map / mask_map`, `finish_kit.straight_lines` (Sonoma saw marks); this family adds
its own patterns (`lo_*`, injected into `eco_oak.PATTERNS` in memory), knot tails (dark stained fibre trailing the
knots along the grain) and mottled knot cores.

All maps: albedo 2048×1024 sRGB (2.0 × 1.0 m, grain along U, tileable — the edge seam equals the JPEG 8-px block
boundary difference, i.e. no seam), normal 1024×512 OpenGL, mask 256×128 (R 0, G 255, B 0, A smoothness). Matt SWN
films: smoothness 0.32 (lower in pores / cracks); the lacquered solid oak 0.45. Pores, cracks, knot rims, rays and
saw marks are embossed (rms tilt 3–3.5°). Colour: the texture's linear mean is solved to the swatch's trimmed mean
(`catpage.py --swatch`); ΔE76 below is measured on the written JPEG.

| id | name | colour source (page, crop) | target | texture mean | ΔE76 |
|---|---|---|---|---|---|
| cg_dub_bordo_layt | Дуб Бордо лайт 380 SWN | p. 27 Агата swatch `0.675,0.865,0.73,0.905` (±1.3) | #e7e7e1 | #e6e7e1 | 0.36 |
| cg_dub_sonoma | Дуб Сонома 325 / Дуб Сонома | p. 104 Гресс swatch `0.725,0.86,0.775,0.9` (±8.2) | #caab92 | #caab92 | 0.13 |
| cg_dub_kantri_zolotoy | Дуб Кантри золотой 389 SWN | p. 33 Денвер swatch `0.670,0.855,0.695,0.89` (±8.0) | #b39266 | #b39266 | 0.04 |
| cg_dub_ontario | Дуб Онтарио 385ТМ / Дуб Онтарио | p. 137 Лари swatch `0.60,0.86,0.655,0.90` (±10.4; p. 138 identical) | #a08357 | #a08357 | 0.09 |
| cg_dub_ontario_svetly | Дуб Онтарио (Кен) | site studio photo of Кен шкаф П3.596.0.02, plain upper-left front (flattest crop, ±10.6) | #bca48c | #bca48c | 0.11 |
| cg_dub_madura | Дуб Мадура | p. 132 Акцент «Каркас» swatch `0.815,0.855,0.87,0.905` (±6.2) | #beb1a1 | #beb1a1 | 0.03 |
| cg_dub_artizan | Дуб Артизан | **no swatch, no photo** — decors.md provisional colour | #a2825f | #a2825f | 0.12 |
| cg_dub_lancelot | Дуб Ланцелот | p. 134 Хольтен Лофт «Фасад» swatch `0.735,0.856,0.795,0.905` (±10.2) | #997658 | #997658 | 0.12 |
| cg_dub_naturalny | Дуб натуральный (массив) | p. 79 «Варианты крашения» swatch `0.748,0.858,0.808,0.900` (±12.3) | #9a866a | #9a866a | 0.03 |
| cg_dub_sahara | Дуб Сахара | **no swatch** — site studio photo of the bedside П6.952.1.04 top (6T3A5490, the lit top surface) | #837b64 | #837b64 | 0.14 |

## Per material: choice, conflicts, doubts

- **Дуб Бордо лайт** — four prints: Агата p. 27 #e7e7e1 (±1.3, the largest own swatch, the only one with the code),
  Верес p. 135 #dbd8d7 (ΔE 5.7), Юнона Лайт p. 112 #d4d4d8 (8.3), Челси Бум p. 120 #cecece (9.3); the Агата close-up
  p. 26 reads #bfbfbf in shade, the site photos ~#a8a8a8 (grey studio exposure). Chose Агата (flattest, own). Doubt:
  the three other swatches and all photos are greyer — if the furniture looks too white in the app, #d8d7d6 (their
  median) is the alternative. Character from the p. 26 close-up: long straight fibres, fine grey pore lines, soft
  cathedrals, long thin dark cracks along the grain (10 per m²), a few pins. Also used `@gloss` on Агата fronts: the
  material is matt SWN; the gloss is the lead's finish modifier.
- **Дуб Сонома** — Гресс «Дуб Сонома 325» p. 104 #caab92 vs Боро «Дуб Сонома» p. 96 #b99c85 (±7.4, ΔE 5.8). Chose
  p. 104: the Гресс product render p. 104 reads #bea694 (studio light, ΔE 5.4 to it, and the site calls it «Сонома
  светлый»); the Боро room photo reads #987e68 under warm room light. One material serves both (the lead's call);
  if Боро should be the darker print, it would need its own colourway. Saw marks across the grain in patches, grey-brown
  pore streaks, few small knots.
- **Дуб Кантри золотой** — Рокси p. 14 #846c48 (±6.6, flattest), Денвер p. 33 #b39266 (±8.0), Парма p. 56
  #a88059 (±10). Chose **Денвер** against the flatness rule: every photo agrees with it — the Денвер room photo p. 33
  #a4875d (ΔE 4.9), the Симпл photos p. 133 #aa9476, the decors.md reading #ac9372…#bda789 — while the Рокси spread
  is printed dark/olive (its Нокс neighbour too). Рокси is ΔE 16 away: Рокси's carcass will read lighter than its
  swatch.
- **Дуб Онтарио** — the only swatch is Лари/Мюнхен (same image) #a08357, honey-golden with dark cracked knots. Big
  conflict: Кен's catalogue photo p. 70 reads #ab9e96 (pinkish grey, purple room) and the site studio photo of the Кен
  шкаф П3.596.0.02 #bca48c (light beige, ΔE 17). Followed the swatch (the catalogue's colour statement); flag for the
  lead: if Кен should look like its photos, a lighter #bca48c colourway (same pattern) is a one-line change.
  Pattern: mostly straight grain, frequent knots with dark tails and radial cracks, many pins, short cracks.
  **Resolved:** Кен has its own material `cg_dub_ontario_svetly` (same pattern and seed as cg_dub_ontario), fitted to
  #bca48c, the flattest crop of the site studio photo: the plain upper-left front of П3.596.0.02. The other crops of
  the site photos are shaded interiors or chevron-printed fronts, which give darker readings (#806d5e…#a99179), so
  they were not used. `cg_dub_ontario` stays for Лари / Мюнхен.
- **Дуб Мадура** — Акцент p. 132 #beb1a1 (±6.2, full own swatch) vs Ардо p. 97 #b09989 (±5.4 but a narrow half-swatch
  of «Белый / Дуб мадура», ΔE 9.1; Ардо room photo #a69083). Chose p. 132. Ардо will read slightly lighter/greyer.
- **Дуб Артизан** (Хольтен Лофт drawer box only) — no swatch, no visible photo; the colour is the decors.md
  provisional #a2825f (the instruction table), pattern = the artisan pattern of Онтарио with another seed. Unverified;
  low visibility (inside a drawer).
- **Дуб Ланцелот** — p. 134 swatch #997658; the p. 134 photo of the drawer fronts #9f755b (ΔE 3.6) agrees. Rich
  rustic plank figure, dark streaks, knots with tails, cracks.
- **Дуб натуральный (массив)** — p. 79 swatch #9a866a (streaky, ±12.3). The site photos of Норд Лофт tables are
  warmer, honey-orange lacquer (#ad8a73, ΔE 7.5). Followed the swatch. Glued staves ~70 mm (each its own shade),
  straight grain, ray flecks, no knots, smoother (lacquer 0.45). End-grain lamellas on the edges are not in this
  texture (edges use the same map).
- **Дуб Сахара** — no swatch. Site studio photo (bedside top) #837b64 greige; the catalogue interiors p. 43/44 read
  #756258 / #644d3c (warm room light, ΔE 12–19 browner). Chose the studio photo. Doubt: the tops on the catalogue
  pages look clearly browner; if the lead prefers the catalogue look, ~#7a6755 would sit between.

## Contrast (swatch vs texture at the swatch's scale, L* std, `--analyze`)
bordo 0.5 / 1.5 (the print is washed out; the p. 26 close-up and the site photos show clearly visible grey grain, so
the texture keeps more), sonoma 3.2 / 3.2, kantri 3.1 / 3.0, ontario 4.3 / 3.1, madura 2.7 / 2.1, lancelot 4.2 / 4.0,
naturalny 5.3 / 4.4. The swatch scales (mm across the crop) are estimates from knot sizes: 250–320 mm.

Reference photos from pinskdrev.by were downloaded only to the session scratchpad (not in the repo); the sheet's
photo column uses catalogue crops.
