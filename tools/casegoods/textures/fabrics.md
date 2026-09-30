# Family `fabrics` — upholstery of the casegoods (texture wave 6)

Generator `tools/casegoods/textures/fabrics.py` (numpy + Pillow, on the door kit's `make_finishes.py` colour maths and
periodic FFT noise); entries `entries/fabrics.json` (merged, `neutral: true`, category `casegoods`); check sheet
`sheets/fabrics.png`. Everything is procedural, periodic on the tile (seam check: edge differences = interior ones
on the float fields; the JPEG adds ±1 level).

## Colour rule (differs from the board decors)
All four are NEUTRAL: albedo grey, saturation 0 (R = G = B in every pixel), the pattern is a value variation only.
The finish tints it: `cgfab_velur#rrggbb` → URP `_BaseColor`, multiplied in linear light. So

    tint_linear = target_linear / mean_linear        (per channel)

`mean` below = the texture's mean in LINEAR light, written as sRGB hex (what the eye sees from afar; the solver hits
it exactly). The plain average of the sRGB pixel values is lower for contrasty textures (given for reference only).

| id | name | albedo mean (linear → hex) | sRGB pixel mean | metersPerTile | smoothness (mean) | normal rms tilt |
|---|---|---|---|---|---|---|
| cgfab_velur_myaty | Велюр мятый | 0.7455 → #e0e0e0 | 223.6 | 2.0 × 1.0 | 0.33 (0.23–0.43, follows each facet's lean) | 6.0° |
| cgfab_velur | Велюр | 0.7455 → #e0e0e0 | 224.0 | 1.0 × 0.5 | 0.30 | 3.0° |
| cgfab_rogozhka | Рогожка | 0.7455 → #e0e0e0 | 223.5 | 0.25 × 0.125 (256 × 128 yarns, 0.98 mm) | 0.225 | 15.8° |
| cgfab_ekokozha | Экокожа | 0.8389 → #ececec | 236.0 | 0.25 × 0.125 | 0.54 (0.45 valleys – 0.60 tops) | 5.0° |

**Eco-leather is lighter (#ececec, not #e0e0e0) on purpose**: Элиза's cream #e7dcc4 has R = e7 > e0, so at a mean of
#e0e0e0 it needs a tint > 1 (1.07), which a #hex cannot express. At #ececec it is `#faeed4`.

## Ready tints (tint = target / mean, linear) for the decors.md colours
- cgfab_velur_myaty: Стамбул #c6bdb6 → `#e2d7d0`; Сати #ab9a93 → `#c3b0a8`; Сати white #d6ccbf → `#f4e8da`; Парма #cdbfa8 → `#eadac0`
- cgfab_velur: Акцент #b0a28c → `#c9b9a0`; Бритиш 1.34 #9e958e → `#b4aaa2`; Бритиш 1.32 #bfbbb2 → `#dad5cb`; Юнона Лайт #846d5d → `#977d6b`; Верес #4a3a33 → `#55433b`; Деко #16110e → `#1b1512`
- cgfab_rogozhka: Марлен #c9bcab → `#e5d6c3`; Бритиш 1.32 #bfbbb2 → `#dad5cb`; Бритиш 1.34 #9e958e → `#b4aaa2`
- cgfab_ekokozha: Элиза #e7dcc4 → `#faeed4`; (Юнона Лайт as matt eco-leather #846d5d → `#8f7665`; Верес #4a3a33 → `#513f38`)

## Materials
### cgfab_velur_myaty — crushed velour (Стамбул, Сати, Парма)
Refs: p.106 headboard `catpage.py 106 --crop 0.503,0.41,0.581,0.44` and footboard `0.322,0.53,0.372,0.64`; p.22
`0.66,0.505,0.80,0.575`; p.54 `0.537,0.416,0.703,0.449`.
Pass 2 (after review: the first version's round dark blotches and flecks read as stains or mould). The model is now
pile direction only: a domain-warped ridged crumple of 45, 18 and 7 mm, stretched 2.4× along V (the crush direction).
Each crease facet takes a soft light or dark tone from its lean towards a side light (tanh, facet_k 0.19). On top:
elongated lighter / darker pile streaks (streak_k 0.07), faint fold lines (0.05), a 2.5–6 mm crinkle (0.045) and the
pile grain. Only a weak elongated tone drift is left (blot_k 0.06, not round); the round blots and flecks are gone.
The normal carries the same facets (rms 6°, was 3.5°). Smoothness follows each facet's lean, ±0.08 (0.23–0.43), so
the highlight shifts from facet to facet. sRGB 5–95 %: 205–242.
Doubts: Стамбул's photos show a little more light/dark contrast than this. Сати's calmer panel now matches well, and
Парма's photo is too blurry to judge. 1 mm per texel: the pile is not resolved closer than ~0.5 m. Map V vertical on
headboards.

### cgfab_velur — short-pile velour / suede-look (Акцент 3.02, Бритиш Бум 1.32 / 1.34, Деко, Верес 3.09, Юнона Лайт)
Refs: p.132 `0.37,0.528,0.47,0.56`; p.109 `0.60,0.465,0.72,0.50`; p.73 `0.16,0.435,0.30,0.47`; p.135
`0.02,0.572,0.155,0.61`. Model: fibre grain 0.3–1 mm, faint curved pile marks (lighter / darker brushed streaks
30–120 mm, a touch glossier), soft 12–45 mm mottle; 5–95 % sRGB 217–231. Doubts: Деко's black (#16110e) makes the
albedo pattern invisible (as on the real fabric) — its look is the normal + smoothness only. URP Lit has no sheen
lobe, so the velvet's grazing-angle glow is not there; smoothness 0.30 keeps it matt rather than plastic.

### cgfab_rogozhka — matting / linen weave (Марлен 1.20; also suits Бритиш Бум 1.32 / 1.34)
Refs: p.105 `0.703,0.475,0.879,0.524`; p.131 1.34 cut-out `0.767,0.385,0.869,0.405`. Model: 2 × 2 basket weave,
0.98 mm yarns (8 albedo px, 4 normal px), rounded yarn sections with dives at the crossings, two-ply melange
striations (1.4 mm twist), slubs, yarn tone drifting along each yarn (~30 mm) — nothing broader, so the 0.25 m tile
does not show on a 1.2–1.8 m headboard. Crevices / flanks darker in the albedo (the mask's AO is 255 per the brief).
Doubts: at 1 m it reads as a fine, calm weave (as Марлен's photo); up close the normal is only 4 px per yarn.
Бритиш Бум's upholstery ("velour / matting") is ambiguous in the photos — velur or rogozhka both fit.

### cgfab_ekokozha — smooth eco-leather (Элиза 1.15 / 1.16 diamond tufting)
Ref: p.108 `0.44,0.457,0.56,0.519` (the tufted panel). Model: periodic Voronoi pebble grain ~1 mm (rounded tops,
narrow valleys) + a faint ~4 mm coarser grain; valleys 3–5 % darker and less smooth; no broad mottle (it would repeat
every 0.25 m). Smoothness 0.54 mean (satin). Doubts: Элиза's photo is glossier-looking (highlights on the tufts) —
that comes from the tuft geometry; raise `smooth` to ~0.62 if it reads too dull in the app.

## Conflicts / notes for the lead
- Юнона Лайт is written "mocha velour / matt eco-leather": its photo (p.109) shows a matt, soft surface without
  leather highlights → cgfab_velur recommended (tint `#977d6b`); cgfab_ekokozha given as the alternative.
- The same fabric colour appears only once per collection, so there are no cross-collection colour conflicts inside
  one material; the targets are decors.md's (photo means, lit), the tint math above just reproduces them.
