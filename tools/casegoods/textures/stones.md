# Casegoods decor textures: family `stones`

Generator: `tools/casegoods/textures/stones.py` (numpy + Pillow; door kit `finish_kit` / `make_finishes` for colour,
noise, laminations and maps). Run `python tools/casegoods/textures/stones.py` to rewrite all ten, then merge happens
automatically (`--no-merge` to skip; `--no-write --sheet --photos DIR` for the check sheet only, which needs PyMuPDF
and caches the pinskdrev.by photos in DIR). Entries: `entries/stones.json` (merged into external.json). Sheet:
`sheets/stones.png` — per material: swatch crop | photo crop | texture as a 400 mm chip (the assumed width of a
catalogue swatch chip) | 230 mm at 1 px/mm | 1.0 × 0.5 m | 2 × 2 tiles (seams / repetition).

Colour rule: the target is the catalogue swatch's `catpage.py --swatch` value (trimmed mean of sRGB, middle 60 % by
brightness, at 150 dpi). The texture is measured the same way: box-downsized to ~2 mm/px, trimmed sRGB mean, after the
JPEG round trip. ΔE76 is between those two. "Linear mean" is the plain linear-light mean of the albedo (what
Finishes files usually list); it differs only for the veined ones (the bright veins raise it).

All masks: R 0 (none is metallic in PBR), G 255, B 0, A smoothness (matt films 0.2–0.3, marble 0.45).
Grain / pattern axis: U = image x = the long side, as for the woods.

| id | decor | swatch (page, crop) | target | texture (swatch stat) | ΔE76 | linear mean | metersPerTile |
|---|---|---|---|---|---|---|---|
| cg_beton_layt | Бетон Лайт 818ТМ | p. 137, 0.678,0.86,0.732,0.90 | #cdcac4 | #cdcac3 | 0.35 | #cdcac4 | 2.0 × 1.0 |
| cg_mramor_nero_markina | Мрамор Неро Маркина 850ТМ | p. 137, 0.83,0.86,0.885,0.90 | #292929 | #2a2a2a | 0.29 | #2e2e2e | 2.0 × 1.0 |
| cg_kamen_sery | Камень серый | p. 69, 0.695,0.86,0.72,0.905 | #4a4a4a | #4a4a4a | 0.15 | #4a4a4a | 2.0 × 1.0 |
| cg_sharli_keramika | Шарли керамика | none — photos | #68554e | #68554e | 0.10 | #68554e | 2.0 × 1.0 |
| cg_metall_bruklin | Металл Бруклин 808 | p. 120, 0.715,0.865,0.738,0.90 | #4c4b51 | #4c4b51 | 0.06 | #4c4b51 | 2.0 × 1.0 |
| cg_oniks | Оникс 817 TM | p. 122, 0.749,0.865,0.772,0.90 | #726e65 | #726e65 | 0.03 | #736f66 | 2.0 × 1.0 |
| cg_cherny_660 | Черный 660 WML | p. 79, 0.670,0.862,0.698,0.905 | #26252b | #26252b | 0.10 | #27262c | 2.0 × 1.0 |
| cg_prizma_870 | Призма 870 | p. 118, 0.748,0.86,0.772,0.905 | #d5dce2 | #d5dce2 | 0.02 | #d5dce2 | 2.0 × 1.0 |
| cg_belaya_vanil | Белая Ваниль | p. 108, 0.80,0.87,0.845,0.905 | #e8e6e4 | #e7e6e4 | 0.35 | #e7e6e4 | 2.0 × 1.0 |
| cg_hdf_grafit | ХДФ «графит текстурный» | none — provisional | #3a3b3d | #3a3b3d | 0.12 | #3a3b3d | 1.0 × 0.5 |

## Per material

**cg_beton_layt — «Бетон Лайт 818ТМ»** (Лари body; Мюнхен body). The swatches of p. 137 and p. 138 are the same print
(both #cdcac4, ±7.6 / ±7.5): no conflict. Light warm-grey concrete: warped clouds (100–300 mm), mottled pale cement
patches (10–35 mm), a faint greener-grey cast in places (the swatch shows it), ~30 soft darker trowel smears, sparse
pin pores (~35 per dm², pressed in the normal map). Tile 2 × 1 m: no repeat on a 1.4 m table top.

**cg_mramor_nero_markina — «Мрамор Неро Маркина 850ТМ»** (Лари, Мюнхен). p. 137 and p. 138 identical (#292929).
Black with a crack-like network of grey-white veins: 24 main veins (median 0.7 m, up to 1.8 m, 1.3 mm wide, soft
edge, straight runs with kinks, some doubled, few branches), 45 hairlines, 14 wide faint "ghost" veins, a soft halo
around the main veins, faint grey clouds. The network covers the whole 2 × 1 m tile with no structure repeating
inside it, so a 1.6 × 0.8 m top shows one non-repeating piece. Satin 0.45. Doubt: the swatch's physical scale is not
printed; I assumed a ~400 mm chip — if the real film has finer, denser veins, raise `count` / lower `length` in
`s_nero`. No product photo of the marble variant exists (the sheet shows the p. 138 swatch instead of a photo).

**cg_kamen_sery — «Камень серый»** (Лайн fronts). Swatch p. 69 flat (±3.2). Dark grey concrete: clouds, soft lighter /
darker blotches (10–25 mm), fine light specks and pores, very faint streaks along U (the p. 65 fronts show faint
lengthwise streaking). The milled diagonal lines of the fronts are geometry, not in the texture.

**cg_sharli_keramika — «Шарли керамика»** (Шарли tops and niche backs). **No swatch** (the collection shows none). Target
= decors.md's provisional #68554e, checked against the photos: the top face in the site photo П6.116.0.02 (from
above, studio) reads #605659 (greyer — environment sheen at a grazing angle), the front edges #7a6655 / #4c3c30
(П6.116.0.03 / 0.01-01), the catalogue interior p. 4 #766760 (warm light). #68554e sits inside that spread; I kept it.
Character from the edges: fine lengthwise streaks (ceramic / stone-look with a linear figure), soft clouds, matt.
Doubt: the decor might be closer to a fine-line wood than a stone; the photos are too small to tell.

**cg_metall_bruklin — «Металл Бруклин 808»** (Челси Бум body). Swatch p. 120 (±2.3). Metal-look film on chipboard:
matt, **mask R 0**. Suede-like fine mottling (1–10 mm), soft blotches and oxidised clouds, faint brushed streaks along
U; slightly blue anthracite. Conflict: the site photos (П3.0587.1.08 coupe panels, 1.03 chest) show it darker and a
little greener (≈ #3c4043 under studio light); the swatch was kept, as the brief says.

**cg_oniks — «Оникс 817 TM»** (Луна accent). Swatch p. 122 (±7.0, textured); close-up p. 122 (the open shelf) and the
2.61 cut-out. Grey-brown slate: calm, large soft clouds (90–520 mm, stretched a little along U) at about half the
first version's contrast, pale thin crack veins mostly along U (55, 0.9 mm) as the main feature, soft darker smears.
(Pass 2 after the Unity review: the first version read as dark smoky camouflage at 0.5–1 m.) Doubt: the close-up is darker and greener than the swatch
(shadowed niche); the swatch was used.

**cg_cherny_660 — «Черный 660 WML»** (Блэквуд Лофт black fronts etc.). decors.md and the 3.33 product photo
(П3.0556.3.33) settle it: a **black woodgrain** film — near-black with dense straight pore lines (brushed ash / pine
look, no knots), WML = synchronised pores, so the normal map carries the grooves (tilt 4°). Wave-1 lamination model
(`PAT_CHERNY`), grain along U (horizontal on every front). Swatch p. 79 (±2.5, bluish black).

**cg_prizma_870 — «Призма 870»** (Призма Нью fronts). Swatch p. 118 (±1.6). The site photo of the bedside drawer
(П3.0592.1.05) shows that the figure is a **pressed facet relief**: loose fans of long straight creases (100–700 mm)
crossing at random angles, the surface between them piecewise planar. The relief is a sparse set of long straight
creases in fans (16 fans × 3–6, median 700 mm, facets ~90 mm to each side) → normal map at tilt 1.3° (pass 2 after
the Unity review: the first, dense 3° relief read as crumpled paper); the dense set of fine crease lines is kept in
the albedo only, a little greyer and the facets are shaded faintly into it
(lit from the top left) so they read under flat light too. Crease fans lean towards V (vertical in the image), as on
the photographed drawer; lay it unrotated.

**cg_belaya_vanil — «Белая Ваниль»** (Элиза). Swatch p. 108 (±0.8, flat) #e8e6e4 used. Conflict: the interior photo of
p. 108 reads warmer (≈ #efe6d2, warm lamp light + gilded décor) — kept the swatch. Faint fine painted-ash grain
(wave-1 laminations at very low contrast, pores in the normal map), matt.

**cg_hdf_grafit — ХДФ «графит текстурный»** (Хольтен Лофт backs). **No swatch** (instruction only); the niche of the
p. 134 photo is in deep shade (#1f1f19–#151616 measured) and cannot give a colour, so decors.md's provisional
#3a3b3d is the target. Fine non-directional linen / stone emboss (weft + warp noise, ~0.5 mm, specks), tile
1.0 × 0.5 m (2 px/mm: the emboss is finer than 1 mm), tilt 6°.

## Notes for the lead
- All ten are procedural (no CC0 source used), tileable both ways (checked on the 2 × 2 sheet and numerically).
- Another family wrote `cg_cherny_drevesny` («Черный древесный»?) — a different decor name; if it is the same film as
  «Черный 660 WML», keep one of them.
- Swatch chips are assumed to show ~400 mm; the pattern scales (marble veins, onyx veins, prizma creases) follow the
  product photos where they exist.
