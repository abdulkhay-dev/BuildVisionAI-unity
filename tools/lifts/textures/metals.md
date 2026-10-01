# Lift metals (family `metals`)

Generator: `tools/lifts/textures/metals.py` (numpy + Pillow; `lift_kit.py` shared). Check sheet: `sheets/metals.png`.

| id | px | metersPerTile | albedo mean (sRGB, linear-light average) | notes |
|---|---|---|---|---|
| lift_brushed | 1024x1024 | 0.5 x 1.0 m | #d8d8d8 | metallic 1.00, smoothness 0.58 |
| lift_mirror | 1024x1024 | 2.0 x 2.0 m | #e6e6e6 | metallic 1.00, smoothness 0.96 |
| lift_painted | 1024x1024 | 0.5 x 0.5 m | #e6e6e6 | metallic 0.10, smoothness 0.46 |
| lift_woodmetal | 1024x1024 | 0.5 x 1.0 m | #c09455 | metallic 0.00, smoothness 0.50 |
| lift_checker | 1024x1024 | 0.4 x 0.4 m | #bcbcbc | metallic 1.00, smoothness 0.51 |

The three neutral metals (`lift_brushed`, `lift_mirror`, `lift_painted`) are grey with saturation 0 and are tinted by
the engine (`lift_brushed#rrggbb` multiplies `_BaseColor`, i.e. in **linear** light). Grain of the brushed metal runs
along V (vertical on walls and doors).

## Finish colours seen in the catalogue

The catalogue renders show reflections, not the metal itself, so the target is the bright end of the metal's own
hairline / mirror areas (the p90 of the door leaves, which reflect a light wall), i.e. the reflectance colour.

| colour | what the catalogue shows | target metal colour (sRGB) |
|---|---|---|
| rose-gold | SL-7105 door: mean #be8b5d, bright #d6a476; SL-1109 hairline pylons #7b542b..#986d40 (dim cabin) | #d6a476 |
| titanium-gold | SL-7037 door: mean #b79d52, bright #ccb36b; SL-1095 walls bright #d8b356 | #d2b262 |
| champagne-gold | no sample in the catalogue (only named in «материал стен на выбор»); typical champagne PVD | #d5c29e |
| black-titanium | SL-1137 corner inserts / SL-2039BJ: near-black mirror, slightly warm | #3b3633 |
| smoky-grey | SL-1136 side walls: #4d3a1e mean, #654f31 bright (dark bronze-brown, dim render) | #7a6650 |

## Tints for catalog.json `finishes[].tint`

`tint = srgb( linear(target) / linear(albedo mean of the base material) )`, so that `lift_<base>#tint` shows the
target colour. (Writing the plain target colour as the tint instead would come out darker than the catalogue:
×0.69 in linear light on brushed, ×0.79 on mirror.)

| finish id | base material | target | tint to write |
|---|---|---|---|
| rose-gold-mirror | lift_mirror | #d6a476 | **#edb684** |
| rose-gold-etched | lift_mirror | #d6a476 | **#edb684** |
| titanium-gold-mirror | lift_mirror | #d2b262 | **#e9c66d** |
| titanium-gold-etched | lift_mirror | #d2b262 | **#e9c66d** |
| titanium-gold-hairline | lift_brushed | #d2b262 | **#f8d375** |
| black-titanium-mirror | lift_mirror | #3b3633 | **#423d3a** |
| black-titanium-hairline | lift_brushed | #3b3633 | **#47423e** |
| champagne-gold | lift_mirror | #d5c29e | **#ecd7b0** |
| (rose gold, hairline — no finish id yet) | lift_brushed | #d6a476 | **#fdc28c** |
| (champagne, hairline — no finish id yet) | lift_brushed | #d5c29e | **#fbe5bb** |
| smoky-grey-stainless | lift_brushed | #7a6650 | **#917a60** |
| painted-b505p | lift_painted | #c1bfbf | **#d6d4d4** |
| painted-b531p | lift_painted | #a7a6b0 | **#bab8c3** |
| painted-black | lift_painted | #1a1a1a | **#1e1e1e** |

Notes
- smoky grey: the catalogue calls it «дымчато-серая», the render shows dark bronze-brown; the target keeps the render's
  hue but lifts it so it does not read as black under the app's lighting (#4a371c in catalog.json now would be a
  near-black metal).
- black titanium: near-black mirror; a metal this dark relies on reflections, so it will read as black glass-like.
- champagne: no swatch printed — a typical champagne PVD colour.
- painted-*: catalog colour / #e6e6e6 in linear light.
