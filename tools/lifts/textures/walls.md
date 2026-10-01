# Lift cabin walls (family `walls`)

Generator `walls.py` (panels left -> right as width fractions, then ornaments in metres), shared `lift_kit.py`.
Check sheet `sheets/walls.png` (cabin photo | back: albedo, smoothness, lit | side: albedo, smoothness, lit).

Fitted pictures, metersPerTile [1, 1], maskSize 1024. Back 576 x 1024 (drawn for 1.34 x 2.385 m), side 864 x 1024
(2.0 x 2.385 m); u = left -> right seen from inside, v = floor -> ceiling. The pictures carry their own panel
divisions (dark reveals) - they will not coincide with the engine's equal panel seams (n = width / 0.5 m), which then
read as extra joints; if that looks wrong, the engine could skip its seams when a wall picture is present.
Both side walls get the same picture, so side designs are left/right symmetric.

| id | px | albedo mean | metallic mean | smoothness mean |
|---|---|---|---|---|
| liftwall_sl_1134_back | 576x1024 | #dbdbdb | 1.00 | 0.75 |
| liftwall_sl_1134_side | 864x1024 | #d9d9d9 | 1.00 | 0.82 |
| liftwall_sl_1095_back | 576x1024 | #d5b464 | 1.00 | 0.86 |
| liftwall_sl_1095_side | 864x1024 | #d5b464 | 1.00 | 0.86 |
| liftwall_sl_1109_back | 576x1024 | #d6a477 | 1.00 | 0.80 |
| liftwall_sl_1109_side | 864x1024 | #d6a476 | 1.00 | 0.83 |
| liftwall_sl_1135_back | 576x1024 | #a79d9a | 0.46 | 0.71 |
| liftwall_sl_1135_side | 864x1024 | #ada5a2 | 0.52 | 0.74 |
| liftwall_sl_1136_back | 576x1024 | #b08c5a | 0.20 | 0.52 |
| liftwall_sl_1137_back | 576x1024 | #bf9772 | 1.00 | 0.68 |
| liftwall_sl_1137_side | 864x1024 | #b48e6b | 1.00 | 0.71 |

- SL-1134 (SL-8045): back = hairline 0.2 | mirror with an etched dot screen (24 mm pitch, r 5.5 mm) 0.6 | hairline 0.2;
  side = hairline 0.18 | mirror 0.64 | hairline 0.18. Stainless #d9d9d9.
- SL-1095 (SL-8008): titanium gold mirror (#d2b262, 0.93) with etched arch(es) on fluted Ionic columns (one on the back,
  two on a side) and festoon loops under the ceiling - same vocabulary as door SL-7037.
- SL-1109 (SL-8048): rose gold (#d6a476): hairline pylons (0.6) and mirror panels (0.94) with an etched line frame with
  key-fret corners (back: 0.2 | 0.6 | 0.2; side: 0.12 | 0.34 | 0.08 | 0.34 | 0.12).
- SL-1135 (SL-8054): dark wood-look pylons (sapele-like, mean #64361c, satin 0.5, metallic 0) and stainless mirror
  (back: wood 0.27 | mirror 0.46 | wood 0.27; side: mirror 0.12 | wood 0.24 | mirror 0.28 | wood 0.24 | mirror 0.12).
- SL-1136 (SL-8055): back = smoky-grey hairline 0.1 | two beech wood-look panels 0.4 + 0.4 (mean #b8915a) | smoky 0.1.
  No side picture: the side is plain smoky-grey hairline (engine: lift_brushed + the smoky tint).
- SL-1137 (SL-8147): rose/champagne hairline panels (#cfa27a, 0.62) with etched sweeping strands (lighter #e2c08e,
  0.48) between black titanium mirror strips (#3b3633, 0.95); back: 0.1 | 0.8 | 0.1, side: 0.1 | 0.35 | 0.1 | 0.35 | 0.1.
  The strands are procedural (bundled cubic curves), not the exact catalogue drawing.
