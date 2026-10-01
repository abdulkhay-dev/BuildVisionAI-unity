# Lift landing doors (family `doors`)

Generator `doors.py`, drawing in metres with `lift_kit.MCanvas` (4x supersampled masks) and `lift_kit.etched_metal`.
Check sheet `sheets/doors.png` (photo | albedo | smoothness | crude lit preview | 1:1 crop).

Fitted pictures, metersPerTile [1, 1], 440 x 1024 (0.9 x 2.1 m, ~2 mm/px), maskSize 1024 so the etch stays sharp.
u = left -> right seen from the hall, v = bottom -> top; the leaf joint is a dark hairline at u = 0.5. The engine's
leaves overlap the jambs by 25 mm (u slightly < 0 / > 1, wrapped): every design keeps ≥ 0.05 of plain metal at the
sides, so the wrap is invisible.

Etched mirror steel: metallic 1, mirror 0.95, etched (frosted) 0.48 and ~22 % lighter in albedo, a hair recessed in the
normal; colours baked (not tinted): stainless #d9d9d9, rose gold #d6a476, titanium gold #d2b262 (metals.md).

| id | px | albedo mean | metallic | smoothness mean | name |
|---|---|---|---|---|---|
| liftdoor_sl_7061 | 440x1024 | #dddddd | 1.00 | 0.85 | SL-7061 дверь: зеркало, травление (розетка, полосы) |
| liftdoor_sl_7105 | 440x1024 | #d8a578 | 1.00 | 0.92 | SL-7105 дверь: розовое золото, зеркало, травление |
| liftdoor_sl_7001 | 440x1024 | #dddddd | 1.00 | 0.86 | SL-7001 дверь: зеркало, травление (растительный орнамент) |
| liftdoor_sl_7014 | 440x1024 | #e0e0e0 | 1.00 | 0.78 | SL-7014 дверь: зеркало, травление (полосы) |
| liftdoor_sl_7037 | 440x1024 | #d6b564 | 1.00 | 0.72 | SL-7037 дверь: мультипроцесс титана (арка) |
| liftdoor_sl_8055 | 440x1024 | #c09455 | 0.00 | 0.50 | SL-8055 дверь: цветной металл, бук |

Designs (measured on the catalogue door photos, p.23-24):
- SL-7061: two frosted stripes 0.11..0.18 / 0.82..0.89 full height; rosette over the joint, centre 0.277 from the top,
  r 0.233 m: double ring, frosted disc with mirror-line petals (6 lobes), 8-point mirror star, centre boss.
- SL-7105: per leaf a 7 mm etched line frame (0.055..0.425, 0.035..0.968 from the top) whose inner sides join a
  square box on the joint (0.236..0.764, 0.346..0.585) holding a lattice square (rings + diamond links) with a solid
  etched border.
- SL-7001: per leaf a 0.2 m band (0.125..0.35 / mirrored at 0.60..0.82) of procedural baroque scrollwork (stem,
  volutes, acanthus leaves, buds, berries) - the catalogue's exact ornament is not reproducible; density and rhythm
  match, motifs are simplified.
- SL-7014: 40 frosted stripes (pitch 49.5 mm, half filled) from 0.038 to 0.97 of the height, 0.10..0.48 / 0.52..0.90.
- SL-7037: multi-process titanium: field hairline-brushed (0.62), arch opening mirror (0.93), etched fluted Ionic
  columns at 0.45 ± 0.30 m, beaded archivolt with keystone, thin inner arch, five festoon loops under the top edge.
- SL-8055: decided as a **fitted picture** (not the tiling lift_woodmetal): beech wood-look film, each leaf its own
  flitch with a lighter heart band, satin 0.5, metallic 0, mean #c09455 (= lift_woodmetal); the engine can use either.

Plain doors (plain-stainless, plain-stainless-4p, painted-b531p) need no picture.
