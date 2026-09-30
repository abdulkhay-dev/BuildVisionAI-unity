# Texture family `prints` (wave 6)

Generator `tools/casegoods/textures/prints.py` (numpy + Pillow; the check sheet also reads the catalogue with PyMuPDF),
entries `entries/prints.json` (32, merged into external.json), check sheet `sheets/prints.png`.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/textures/prints.py            # everything
    /private/tmp/claude-501/venv/bin/python tools/casegoods/textures/prints.py british [motif …] | eliza | martina | ken | entries | sheet
    python3 tools/doors/textures/merge_entries.py tools/casegoods/textures/entries/prints.json

## How the engine lays these materials (what the textures are made for)

* `print` (CaseBuilder.Print): the picture is fitted to the part's box on its +W face — u = (x − x0) / w, v = (y − y0) / h,
  **up = +y** — drawn 0.25 mm above the face, inset by the part's `edge` (1.5 mm default; 0.5 on the Eliza ovals), the
  outline of a `shape: path / circle` part clipping it. The UV already spans 0…1, so every print entry has
  **metersPerTile [1, 1]** and an albedo **at the aspect of its front** (not 2048×1024). The importer's NPOT rule
  (nearest power of two) and the 2048 cap resample them in Unity; the aspect is restored by the UV, nothing to do.
* role material (a finish role → library id): metric UVs, U along the part's `grain` axis (default its longest side) in
  metres × 1/metersPerTile, anchored at the design origin (the pattern's phase depends on the part's position).

## cgprint_british_bum_<motif> — 26 «Бритиш Бум» photo-printed fronts

**The lead renames the designs' `print` references `british_bum_<motif>` → `cgprint_british_bum_<motif>`** (designs not
edited here). Albedo only (jpg), flat normal, mask R 0 / G 255 / A 0.35 (the fronts' matt film).

Ground = «Крем» **#e0d6cd** exactly (p. 131 swatch «Фасад», flat ±0.5; the mode of every texture = the swatch, ΔE 0),
so the print's edge meets the front's own colour. Cleaning, per motif: the crop is stretched to the front at 1–2 px/mm
(2 px/mm where ≤ 2048 px, else ≥ 1 px/mm), the photo's light is divided out (a robust local ground: 85th-percentile
rank filter over ~100 mm), the handle is found near its design position (grey / highlight blob + its shadow, pushed
8 mm down), cut out and in-painted along its short axis from the lightest pixels beside it (crossing lines continue,
the shadow does not), edge lines (gaps to the neighbour front) removed, the ink unmixed into the motif's 2–3 ink
colours (clustered on hue and depth, not blacker than L* 26, slightly re-saturated) and thresholded into crisp line
art. The 100-dpi catalogue crops get a stronger pre-smoothing / sharpening (`CAT` in TUNE); the site photos are clean.

| id (cgprint_british_bum_…) | front w × h mm | px | source | inks | notes |
|---|---|---|---|---|---|
| flag_england_door | 434.5 × 2096 | 434×2096 | cat. p. 129 | #a87962 #916b54 | flag + «England» **replaced by the gherkin door's (site photo, same artwork) ×0.95**: the catalogue's «England» is unreadable |
| lantern_london_door | 434.5 × 2096 | 434×2096 | cat. p. 129 | #7b502f #91552a | «London» thinner than printed (outlined letters at the source's limit) |
| stpauls_door_l | 434.5 × 1670 | 533×2048 | cat. p. 130 | #85705d #907255 | flag + «England» transplanted from gherkin_door (as above); skyline blocky |
| stpauls_door_r | 434.5 × 2096 | 434×2096 | cat. p. 131 cut-out | #91735f | dome and skyline blocky (the cut-out is ~0.3 px/mm) |
| bigben_door_l | 434.5 × 1670 | 533×2048 | cat. p. 131 cut-out | #a3866b | balloons and bridge thick / broken — the only source |
| bigben_door_r | 434.5 × 1670 | 533×2048 | cat. p. 131 cut-out | #968574 | Big Ben blobby — the only source |
| gherkin_door | 434 × 1880 | 473×2048 | site photo | #805737 #6a523b | clean |
| lamp_door | 432 × 2094 | 432×2094 | site photo | #ac775a #8b6c53 | handle area forced to ground (it sits on plain film) |
| bigben_column_door | 424 × 1391 | 624×2048 | cat. p. 130 | #5f564b #483e33 | the handle crossed the tower: the part under it is interpolated (vertical streaks) |
| shield_door | 434 × 683 | 868×1366 | cat. p. 130 | #695a4f #735241 | «England» **transplanted from football_door (site photo), rotated −10°, ×1.05** — the catalogue's is a blur |
| football_door | 421.5 × 297 | 843×594 | site photo | #9a8b7f #84756a | clean |
| guard_door | 429 × 684 | 858×1368 | cat. p. 130 | #695e4e #4f4433 | good |
| towerbridge_door_l / _r | 394 × 487 | 788×974 | cat. p. 130 | #8f7468 / #977369 | «Wow» good; the bridge's fine hatching partly lost; the handle was higher than the design says (found on the image) |
| umbrella_door | 346 × 663 | 692×1326 | cat. p. 130 | #b3897c #6f564a | terracotta canopy kept, but blobby (source ~0.3 px/mm) |
| stamp_drawer | 872 × 211 | 1744×422 | site photo | #736356 #504236 | clean |
| balloons_drawer_2 / _3 | 874 × 203 / 213 | 1748×406 / 426 | site photo | #8e4b20 #7b4521 | clean; the basket runs over the joint as on the product |
| england_drawer_4 | 874 × 203 | 1748×406 | site photo | #87553a #643f24 | clean |
| skyline_drawer_2 / _3 | 874 × 211 | 1748×422 / 423 | site photo | #894f2b #764b2d | the handle crossed Big Ben / the buildings: interpolated, slightly soft there |
| england_drawer_s | 368 × 211 | 736×422 | site photo | #99897f #83756c | clean |
| bus_drawer_s | 368 × 211 | 736×422 | site photo | #8b7568 #705e52 | **the lower deck under the handle is redrawn** (band, 6 windows, door) from the visible line ends and the upper deck's perspective |
| bus_stamp_drawer | 993 × 280 | 1986×560 | cat. p. 130 | #5c534a #4a3f35 | bus / postmark lines a little broken |
| eye_england_drawer | 993 × 280 | 1986×560 | cat. p. 130 | #4e3d34 #653223 | good; hub terracotta |
| london_rail | 2016 × 236 | 2048×240 | cat. p. 130 | #7a7066 #54473d | 1.02 px/mm; flag hatching and the skyline's fine lines partly lost; part is `shape: path` (the print is clipped by it) |

Unsure / for the lead: the 1-25 designs have the doors 2091 high (1-25-01: 2096) — the same texture serves both
(0.2 % stretch). All ink colours are measured per motif, so the site-photo prints (warm brown #7x4x2x) and the
catalogue ones (greyer, lighter) differ as their sources do; a common ink would be a guess.

## cgprint_eliza_rozy — «Элиза» gilded roses (1536×352, metersPerTile [1, 1])

**Decision: a `print` decal on the light ground, not a tiling gold.** The `ornament` parts are single ellipses
(`kind: front`, `shape: circle`, 1.5 mm thick; 220×44, 200×50, 250×68, 260×60, 320×60 mm) each carrying ONE centred,
mirror-symmetric spray (p. 108: three rose heads, the middle one larger, small leaves, buds, a hanging stem). A role
material gets metric UVs anchored at the design origin, so a tiling ornament would land at a random phase on every
oval and could never be centred; the fitted `print` UV centres it on each ellipse. Therefore: **the lead sets
`"print": "cgprint_eliza_rozy"` on the `*-orn` parts and keeps their `mat: ornament`** (gold#d2b479) — the print covers
the face (inset 0.5 mm), the gold shows as the 1.5 mm rim, as the gilded edge of the catalogue's medallions.
Ground «Белая Ваниль» #e8e6e4 (p. 108 swatch), the body's colour; gold #c9a45c (the finish's `patina`), pale gold fill
#dcc08a, incised lines #9a7a3f. Mask: gold metallic (R 230), satin (A 0.62) vs the matt film (0.30), AO in the lines;
normal: the petals and lines raised. The spray is drawn inside the inscribed ellipse (the ends pulled in). One texture
for all five sizes: aspect 3.7–5.3 against the texture's 4.36 → up to ±20 % horizontal stretch (roses a little oval on
the 250×68 and 320×60 ovals) — acceptable; a second texture per aspect is possible if the lead wants.
Unsure: the catalogue's roses are ~5 px across in the photo — the drawing is a stylisation of that, not a copy.

## cg_martina_listya — «Мартина» carved leaves under silver patina (2048×1024, metersPerTile [0.5, 0.25])

A tiling role material for role `carve` (the door / drawer panels 310–341 × 442–678, 421×120, 971×67, the headboard
band 1553×350). **Pass 2 (after the Unity renders read black-and-white):** the patina is paint, not metal — metallic 0
(0.15 only in the deepest cut lines), recess albedo a light silver-grey **#a9abad** (range #a9abad–#b8babc), leaves
milk-white **#eeeeea**, a soft patina band on the leaves' milled flanks, AO moderate (0.71–1), smoothness 0.24–0.34;
the relief is carried by the normal map (≈45° at the leaf edges) and the AO. Texture mean **#cacbca, ΔE76 0.84** to the
target #c8c9c8 (the p. 48 swatch's carved panel prints #c1c1c0 — `--swatch 0.725,0.885,0.775,0.905`, textured ±29.7 —
the lead asked for the panel to read lighter in the renders). Leaf cover 55 %. The pattern after the p. 45–48 doors:
sinuous stems along U with broad leaves (90–115 × 33–44 mm — larger than decors.md's 70×22, measured on the p. 48
interior door) branching alternately at ±22–50°, a few loose leaves, heavy overlap; leaf faces 2.5 mm proud with milled
rounded edges, V-cut outlines and midribs. The sheet shows it lit in a light studio (simulated: normal × AO).
**Orientation: leaves along U = the grain axis.** Door panels (taller than wide) get them vertical as in the catalogue;
drawer panels (421×120, 971×67 — grain x by default) would get them horizontal, whereas p. 48 shows the chests'
drawers with vertical leaves → **the lead gives those carve parts `"grain": "y"`** (or accepts horizontal).
**The carve parts' milled `face: grooves` (the provisional leaves as V-lines, up to 532 lines) must go** when this
material is used, or they cut a second, different pattern through the texture. The **lily blocks** (46×64, also role
`carve`) are a different motif (a fleur-de-lis) — with the finish mapping `carve` → cg_martina_listya they would show
leaves: give them their own role (e.g. keep `door_enamel_whitey#b4b6b8` with their grooves) — no lily texture made.
Unsure: the catalogue has a strict repeat of ~170 mm across the panel; this texture is free (tile 500 × 250 mm), which
hides the repetition better but is not the exact catalogue drawing.

## cgprint_ken_elochka_<size> — «Кен» UV print «ёлочка» (transparent decals)

**A print works with the engine's mapping**, as a transparent decal over the oak front: `Print()` draws the fitted
picture 0.25 mm above the face, and an entry with `"transparent": true` imports as a URP transparent material taking
alpha from the png — so only the lines cover the oak (Дуб Онтарио, another family's material), the chevrons stay
centred and exact per front. Because the fitted UV stretches with the front's aspect, one texture per front size /
phase: the lines are rasterised from the designs' own V-groove lines (2.5 mm, ink #3b2e27 = the p. 70 line cores),
2 px/mm:

| id | size px | fronts |
|---|---|---|
| cgprint_ken_elochka_504x698 | 1008×1397 | ken-0-01 f-low (504 × 698.5) |
| cgprint_ken_elochka_501x504_up_r | 1002×1008 | ken-0-02 f-up-r |
| cgprint_ken_elochka_501x504_low_l | 1002×1008 | ken-0-02 f-low-l (a different chevron phase from f-up-r) |
| cgprint_ken_elochka_488x374 | 976×748 | ken-0-03 f-door_l, f-door_r |

To use: the lead sets `"print": "cgprint_ken_elochka_<size>"` on these fronts **and removes their `face: grooves`** (or
the decal lies over the V-grooves). Keep the grooves if the transparent pass is unwanted: the importer's transparent
material keeps specular where alpha = 0 (`_BlendModePreserveSpecular` = 1), so the mask is smoothness 0 / metal 0 to
keep that haze minimal; transparent parts get no SSAO. Not checked in Unity (the lead imports).
