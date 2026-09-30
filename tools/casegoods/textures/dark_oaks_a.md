# dark_oaks_a — mid / dark rustic oak films (casegoods decor wave)

Generator `tools/casegoods/textures/dark_oaks_a.py` (numpy + Pillow; builds on `tools/doors/textures/eco_oak.py`'s
sawn-board oak through its PATTERNS table in memory, plus plank joints, saw marks and a grey wash of its own).
Check sheet `sheets/dark_oaks_a.png`: (a) swatch crop 300 dpi | (b) catalogue photo crop | (c) the texture over 400 mm
resampled to the swatch's pixels | (d) 1.0 × 0.5 m | (e) 2 × 2 tiles = 4 × 2 m.

Colour = linear-light mean of the swatch crop (5–95 % luminance-trimmed); the texture's linear mean is solved to it.
ΔE76 = the texture's (written JPEG) mean vs that swatch mean. Streak hue (a*, b* per L*) is from the swatch detail
(`--analyze`). The swatches are soft prints (detail L* std 1.6–2.7 at 300 dpi); the textures have more detail (2.8–4.5
at the same scale) because the product photos and close-ups show clearly more grain, knots and cracks than the chips.

| id | name | swatch used (page, crop) | swatch mean | texture mean | ΔE76 |
|---|---|---|---|---|---|
| cg_dub_kanon | Дуб Каньон | p. 64 Формат, 0.265,0.865,0.31,0.905 | #8c6d50 | #8c6d50 | 0.26 |
| cg_dub_kanzas | Дуб Канзас 377 SWN | p. 33 Денвер, 0.757,0.850,0.784,0.895 | #7e6853 | #7f6853 | 0.50 |
| cg_dub_noks | Дуб Нокс 392 SWN | p. 14 Рокси, 0.795,0.86,0.824,0.90 | #7e5f40 | #7e5f40 | 0.34 |
| cg_dub_votan | Дуб Вотан 376 WML | p. 140 Плато, 0.716,0.852,0.77,0.895 | #9c7146 | #9c7146 | 0.10 |
| cg_dub_satter | Дуб Саттер 369 SWA | p. 41 Монако, 0.715,0.86,0.73,0.90 | #7f4e32 | #7f4e32 | 0.18 |
| cg_dub_yukon | Дуб Юкон 358 SWN | p. 93 Гранде, 0.69,0.86,0.74,0.9 | #8d8887 | #8d8787 | 0.06 |

(Conflict ΔE76 below are between catpage `--swatch` values. catpage `--swatch` sRGB trimmed means of the same crops: #8a6b4e, #7d6752, #7c5e3f, #9b7146, #7f4e31, #8c8685.)

## Per material

**cg_dub_kanon «Дуб Каньон»** — pattern `cg_kanon`: long straight planks, darker streaks, small elongated knots, short
cracks, faint cathedrals. Photo: p. 61 Турин door close-up (0.345,0.73,0.405,0.9). Prints of the decor (sRGB
trimmed): Формат / Глобус p. 64 #8a6b4e, Турин p. 62 #8a6b4e (p. 63 #8b6c4f), Оскар p. 141 #8c6d51, Плато p. 140
#8b6c4f — five prints agree, chosen. Outliers: Брауни p. 114 #856649 (flattest chip, ±6.4, but small; ΔE 2.0, a little darker),
Верес p. 135 #7f6951 (greyer, ΔE 5.6), Юнона Лайт p. 112 #978071 (grey-beige, ΔE 12.4), **Каньон Лофт p. 85 #b29e96**
(light grey-beige, ΔE 23.8 — looks like a different, bleached print; if the lead wants Каньон Лофт 1:1 it needs its
own light material or a tint, not this one).

**cg_dub_kanzas «Дуб Канзас 377 SWN» / «377ТМ» / «ЛДСП ДУБ КАНЗАС»** — pattern `cg_kanzas`: strong plank striping (board
shade dominates the broad tone), pale grey streaks (wash + light streaks), lengthwise cracks, knots, faint saw marks on
some boards, edge joints. Photo: p. 71 Форте Лофт chest fronts. Chosen: Денвер p. 33 (#7d6752 sRGB, ±6.6), which
agrees with the site swatch dub_kanzas.jpg (#816d54, ΔE 3.1). Conflicts: Форте Лофт p. 71 #705b4e (darker, greyer,
ΔE 6.6); Лари p. 137 / Мюнхен p. 138 «377ТМ» #74543b / #74543c — clearly warmer golden-brown (ΔE 9.3): the ТМ table-top
print reads like another decor; one material is used as asked, flag if the tables must match their chip.

**cg_dub_noks «Дуб Нокс 392 SWN»** — pattern `cg_noks`: bold cathedrals (75 % flat-sawn boards), larger dark knots
with radial cracks, edge and butt plank joints. Only one swatch (Рокси p. 14 «Каркас»); photo p. 14 (the dining
table, small in the room shot — the photo reads lighter / more golden than the chip under studio light).

**cg_dub_votan «Дуб Вотан» / «Дуб Вотан 376 WML»** — pattern `cg_votan`: honey ground, frequent elongated dark knots
with cracks, many lengthwise checks, saw-cut streaks on some boards, plank joints. Chosen: Плато p. 140 (#9b7146,
±8.6, the flattest; golden-honey as the product photos). Conflicts (large): Блэквуд Лофт p. 79 #9f836e (same L*,
much less saturated, ΔE 16.4), Норд Лофт p. 79 #7a5b41 (printed much darker, ΔE 14.4), Лайн «376 WML» p. 69 #c4a58c
(much lighter sand, ΔE 23.3). The Блэквуд photo (p. 79, 0.12,0.18,0.155,0.33) looks lighter and paler than the
chosen chip — the true decor is probably between Плато and Блэквуд; Лайн's light rendering is not matched.

**cg_dub_satter «Дуб Саттер 369 SWA»** — pattern `cg_satter`: warm reddish-brown, soft cathedrals, knots with cracks,
many dark lengthwise streaks and checks. Chosen p. 41 (#7f4e31, ±5.3); p. 42 #7f4d31 agrees. Photo: p. 39 close-up
(0.82,0.72,0.868,0.89) shows much stronger dark knots and olive-grey streaks than the chip — the texture follows the
chip's calmer look at furniture scale (p. 40 room shots); a bolder variant may be wanted if the lead compares with
the close-up.

**cg_dub_yukon «Дуб Юкон 358 SWN»** — pattern `cg_yukon`: grey weathered oak, pale grey wash, rough-sawn saw marks
across the grain on ~60 % of the boards (over part of their length), open cracks, grey-brown knots, low-contrast
cathedrals. Chosen p. 93 (#8c8685, the only chip; grain vertical in the chip, the sheet rotates it). Doubt: the
Гранде room photos p. 87–90 (sheet: p. 88 door, 0.79,0.30,0.86,0.40) read clearly warmer beige-grey than the neutral
grey chip; the chip is followed as the brief says.

## Notes
- Grain along U (image x) in every map; tile 2.0 × 1.0 m, tileable both ways. Matt SWN / SWA / WML: smoothness
  0.26–0.30, lower in pores and checks; normals emboss pores, checks, knot rims, joints and saw marks.
- The door generator leaves a tiny column step at x = 0 / 1024 (mean |Δ| ≈ 3 vs 1.4 / 255 inside; the same in the door
  textures) — invisible, not a seam.
- Swatch scale: the check sheet assumes a chip shows ~400 mm of decor (knots ≈ 1/25 of its width).

## Revision 1 (coordinator review: no pepper dots on the dark oaks)
Нокс, Вотан, Саттер, Юкон: the evenly scattered pin knots are gone (eco_oak pins off). Instead each 2 × 1 m tile has
a few real knots — Нокс 3, Вотан 4 (seed 8405), Саттер 4, Юкон 3 — 8–40 mm across, 3× longer along the grain, with
the rings swirling round them (bump 3, flow 3.4). Most get a short lengthwise crack through the centre (drawn into the
check field: `crack_knots`), and pin knots appear only in 1–2 small clusters per tile (`pin_clusters`). Саттер: darker,
bolder knots (knot −42 L*, rim −56) and olive-grey streaks plus an olive-grey tint round the knots (`olive`, #5a5040),
knot cores kept dark; mean still solved to the p. 41 swatch. Каньон and Канзас are unchanged (same means and statistics) (the new
features use their own rng and only run for patterns that ask for them). Нокс butt joints are fainter (0.35).

## Revision 2 (Саттер knots)
Саттер's knots are no longer eco_oak's flat cores: `paint_knots` fits an ellipse to each knot's core and paints an
olive-brown core (#3e3629) darkening to a near-black pith (#191512) with irregular growth rings, 2–4 radial checks
(#110f0c), a soft edge and a lighter rim (#8e6f55); the pin clusters are soft dark olive specks. Still 4 knots per tile,
mean solved to the p. 41 swatch (ΔE76 0.18).
