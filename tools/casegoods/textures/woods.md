# Family `woods` — pines, hickory, cedar, birch, wenge, black woodgrain, neutral solid wood

Generator: `tools/casegoods/textures/woods.py` (numpy + Pillow; the check sheet renders the catalogue with PyMuPDF).
Run: `/private/tmp/claude-501/venv/bin/python tools/casegoods/textures/woods.py [ids] [--no-write] [--no-sheet]`.
It builds on the door modules without editing them: `eco_oak.wood_structure` (boards / logs / cathedrals / knots /
checks; the patterns `cg_kareliya … cg_bereza` are added to `eco_oak.PATTERNS` in memory) and
`finish_kit.oak_structure` (straight-grain laminations: wenge, ДВП wenge, black woodgrain, the neutral massive).
Maps: albedo 2048×1024 (2.0 × 1.0 m, grain along U), normal 1024×512 (OpenGL), mask 256×128; all tile both ways
(checked 2×2 across the seams). Sheet: `sheets/woods.png` (swatch | texture at the swatch's scale | photo | 1 m × 0.5 m
| 1:1 | tints).

**Colour method.** Target = the swatch as `gen/catpage.py --swatch` measures it (sRGB trimmed mean at 150 dpi, the
provisional colour of decors.md). The texture is measured the same way (downsized to the swatch's scale, trimmed
mean) and its base colour corrected until both agree; ΔE76 below is between those two numbers, measured on the
written JPEG. "Mean" = the texture's plain mean in linear light (what it reads as from afar).

| id | catalogue name | swatch used (page, crop) | swatch | texture mean | measured | ΔE76 |
|---|---|---|---|---|---|---|
| cg_sosna_kareliya | Сосна Карелия 528 SWA | p. 128 `0.715,0.865,0.772,0.90` (Соната Бум) | #e6e7e1 | #e5e6e1 | #e5e6e1 | 0.54 |
| cg_sosna_randers | Сосна Рандерс 540 SWN | p. 122 `0.715,0.865,0.738,0.90` (Луна) | #c7c8c3 | #c7c8c3 | #c7c8c3 | 0.09 |
| cg_sosna_jackson | Сосна Джексон | p. 96 `0.715,0.86,0.775,0.905` (Ирвинг) | #6e6a60 | #6f6b60 | #6e6a5f | 0.59 |
| cg_gikori_kingston | Гикори Кингстон 579 SWN | p. 115 `0.845,0.86,0.895,0.905` (Вена «Каркас») | #a1876f | #a28870 | #a28870 | 0.28 |
| cg_kedr_oregon | Кедр Орегон 537 SWN | no swatch: p. 49 photo, lit top edges | #a47e5a | #a47e5a | #a47e5a | 0.02 |
| cg_bereza | Береза 261 SM | p. 27 `0.755,0.865,0.81,0.905` (Агата) | #4b3c3b | #4c3d3c | #4b3b3b | 0.53 |
| cg_venge | Венге | p. 140 `0.863,0.852,0.915,0.895` (Плато) | #2d211b | #2d221b | #2c211a | 0.86 |
| cg_dvp_venge | ДВП ламинированная ВЕНГЕ | no swatch: decors.md value from the 0.20 product photos | #46382f | #46382f | #46382f | 0.15 |
| cg_cherny_drevesny | Черный (Брауни) | p. 114 `0.826,0.885,0.851,0.908` | #1c1d18 | #1c1d18 | #1c1d17 | 0.22 |
| cg_massiv | neutral solid wood for tinting | — (neutral by design) | #e0e0e0 | #e0e0e0 | #e0e0e0 | 0.00 |

## Per material

**cg_sosna_kareliya** — white painted pine: rift boards (few arches), fine straight lines, faint grey streaks, rare
small knots; L* std 1.4; matt (smoothness 0.36). The same decor on p. 64 Формат `#e6e7e1` / Глобус `#e7e7e1`,
p. 62 Турин `#e6e7e1`, p. 138 Мюнхен `#e4e5e1`, p. 141 Оскар `#e7e8e1`, p. 140 Плато `#e7e7e1`, p. 128 Соната
`#e6e7e1` — all within ΔE ≈ 1 of the chosen one. **Conflict:** Визит p. 136 prints `#c6c4c5` (ΔE ≈ 13, a darker,
greyer print of the same decor) — ignored; if Визит must match its page, tint the material
(`cg_sosna_kareliya#dddadf` gives #c6c4c5) rather than making a second decor.

**cg_sosna_randers** — white-washed pine: mostly rift lines, faint grey streaks, grey pores (synchronised SWN
relief in the normal map), small pale knots; L* std 1.75. **Conflict:** Парма's p. 56 swatch prints `#d9d9d9`
(ΔE ≈ 5 lighter); Луна's swatch chosen (named with the code 540 SWN, flatter, matches the p. 122 close-up). A tint
cannot lighten (it multiplies, ≤ 1), so Парма either accepts the Луна colour or needs its own lighter material.

**cg_sosna_jackson** — weathered brushed pine: wide flat-sawn boards with long cathedrals, dense dark latewood lines,
big dark knots with cracks, checks, lighter worn streaks, deep brushed relief (normal tilt 6°, smoothness 0.28);
L* std 7.9. Swatch ±11 (strongly textured) — the trimmed-mean method matters here. Doubt: the catalogue print has
more brown / green-grey patina mottling than the texture (which reads cool grey-brown); the p. 95 close-ups show
the rings denser and more "combed" than my boards.

**cg_gikori_kingston** — light warm hickory / rustic oak: planks, soft cathedrals, pore lines, small knots and pins,
short checks; L* std 4.6. Close-ups p. 10 (in shadow, much darker — not used for colour), p. 11 bed (photo on the
sheet), p. 105. Same swatch for Тринити / Марлен / Вена (decors.md #a1876f / #a2886f).

**cg_kedr_oregon** — honey cedar / oak planks with open cathedrals and knots; L* std 5.3. **No swatch**: colour from
the p. 49 product photo — the lit front edges of the tops measure #a78361 (TV unit), #b48c6a (0.22), #bd9770 (0.23),
#8a674a (the tall cabinet, in shade); kept decors.md's #a47e5a (≈ the TV unit's, ΔE < 2). Structure by analogy (the
photo is too small to show the pattern) — the least certain material of the family.

**cg_bereza** — dark grey-brown crown-cut birch: wide flitches, flame / burl-like arches and eyes drawn as thin
lighter ring lines on the dark ground, small flecks; L* std 4.1. Mask smoothness 0.55 (satin) — the Агата fronts are
high-gloss lacquer, so the `@gloss` variant (or a smoothness override) should be used there; the texture itself has
almost no relief (tilt 1.2°). Doubt: the p. 26 close-up shows the arches denser and more regular than the texture;
the rows of small eyes in some flitches are a little systematic up close.

**cg_venge** — wenge: straight dark-chocolate stripes, fine lighter lines, long open pores, soft broad bands;
L* std 3.6. No product photo of the Плато venge body (the chairs on p. 140 are a stain, not this decor).

**cg_dvp_venge** — the hardboard backs: the wenge structure at 0.75 scale (finer), lower contrast (L* std 2.4),
flat (tilt 1.2°, smoothness 0.42). **No swatch and no usable catalogue photo** (the vitrine backs on p. 85 / 86 are
tiny and lit by LEDs): colour = decors.md's #46382f from the site's product photos of 0.20. It is noticeably lighter
and warmer than the ЛДСП «Венге» swatch (#2d211b) — normal for laminated ДВП, but unverified.

**cg_cherny_drevesny** — Брауни's «Черный»: near-black woodgrain, dense fine straight lines, no figure; L* std 2.4.
Doubt: the p. 114 room photo renders these panels as dark chocolate brown (≈ wenge), while the swatch is near-black
#1c1d18 (and the site swatch right half reads #302e2f); the swatch is followed.

**cg_massiv** — neutral beech / birch solid wood for tinting: fine straight grain, soft rings, tiny ray flecks, closed
lacquered pores, no cathedrals; **mean #e0e0e0 exactly (linear 0.7454), zero saturation**, L* std 2.7, smoothness
0.45, tilt 1.2°. The engine multiplies albedo × tint, so the result's mean is 0.7454 × tint (linear): the tint
`cg_massiv#c1966a` gives a mean of about #aa845d, darker than the provisional colour. To land exactly on a
target colour T, use tint = T / 0.7454 (linear):

| target (provisional) | where | tint that gives it |
|---|---|---|
| #c1966a | Денвер light legs (to Кантри) | #dcab7a |
| #7e6753 | Денвер dark legs (to Канзас) | #907660 |
| #8b653e | Деко slats | #9f7448 |
| #b39a7c | Вена «Опора Вена», knobs | #ccb08e |

(the sheet shows these compensated tints). Photo references: Деко slats p. 74 close-up, Денвер legs p. 33, Вена p. 115.

## Not done / notes
- Product photos from pinskdrev.by were not downloaded (no files fetched); all references are catalogue pages.
- Swatch physical scale (for "texture at the swatch's scale") is estimated per swatch (110–420 mm across), not known.
