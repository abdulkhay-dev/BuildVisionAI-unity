# Lift floors (family `floors`)

Generator `floors.py` (stones + layout), shared `lift_kit.py` (`stone()`: domain-warped cloud ground, Worley-cell
breccia veins for emperador / verde / grigio, anisotropic contour veins for carrara / rosa / calacatta / marquina,
chip specks for granite / terrazzo). Check sheets: `sheets/floors.png` (pictured, with the swatch), `sheets/floors_cabins.png`
(from cabin photos, with the photo's floor).

Fitted pictures, metersPerTile [1, 1], 1024 x 1024, 1.5 mm/px for a ~1.5 m floor. u = left -> right seen from the
door, v = 0 at the door (image bottom) -> 1 at the back wall (image top). All layouts are symmetric, borders are
fractions of the size, so stretching to 0.7..1.5 keeps them; the SL-4039D medallion becomes an ellipse on non-square
cars (unavoidable with a fitted UV). Metallic 0; PVC smoothness 0.35 with a fine emboss, marble 0.8 with hairline
joints between the slabs (each marble piece is its own slab with its own veins; PVC is one printed film).

| id | kind | px | albedo mean | smoothness | layout from | stones |
|---|---|---|---|---|---|---|
| liftfloor_sl_4006p | pvc | 1024x1024 | #b0aaa9 | 0.36 | catalogue swatch p.21 | emperador, carrara |
| liftfloor_sl_4021p | pvc | 1024x1024 | #ccc296 | 0.36 | catalogue swatch p.21 | giallo, emperador_dark |
| liftfloor_sl_4025p | pvc | 1024x1024 | #c7c1b0 | 0.36 | catalogue swatch p.21 | crema_beige, verde |
| liftfloor_sl_4027p | pvc | 1024x1024 | #9c9a95 | 0.36 | catalogue swatch p.21 | verde, nero_plain, rosa |
| liftfloor_sl_4034p | pvc | 1024x1024 | #dccbb6 | 0.36 | catalogue swatch p.21 | beige_fine, taupe, gold_band |
| liftfloor_sl_4173p | pvc | 1024x1024 | #cac6c0 | 0.36 | catalogue swatch p.21 | emperador, bianco |
| liftfloor_sl_4106d | marble | 1024x1024 | #c4b69b | 0.80 | catalogue swatch p.21 | granite_black, crema_peach |
| liftfloor_sl_4145d | marble | 1024x1024 | #bebdb4 | 0.80 | catalogue swatch p.21 | grigio_onice |
| liftfloor_sl_4157d | marble | 1024x1024 | #eadeca | 0.80 | catalogue swatch p.21 | marfil, emperador_light |
| liftfloor_sl_4182d | marble | 1024x1024 | #b5a58f | 0.80 | catalogue swatch p.21 | marfil_warm, emperador_dark |
| liftfloor_sl_4028p | pvc | 1024x1024 | #cbc4bf | 0.36 | cabin photo | rosa, verde, nero_plain |
| liftfloor_sl_4017p | pvc | 1024x1024 | #b2b3ad | 0.36 | cabin photo | terrazzo_grey |
| liftfloor_sl_4012p | pvc | 1024x1024 | #dbc89d | 0.36 | cabin photo | giallo_sun, verde, calacatta_gold |
| liftfloor_sl_4072d | marble | 1024x1024 | #cdbfa8 | 0.80 | cabin photo | emperador_dark, marfil_warm |
| liftfloor_sl_4150d | marble | 1024x1024 | #e3dac7 | 0.80 | cabin photo | marfil_warm, nero_marquina, marfil |
| liftfloor_sl_4082d | marble | 1024x1024 | #bcb19c | 0.80 | cabin photo | grigio, bronze, beige_plain |
| liftfloor_sl_4039d | marble | 1024x1024 | #d9d1c5 | 0.80 | cabin photo | bianco_warm, emperador_dark, gold_marble, marfil |
| liftfloor_sl_4036p | pvc | 1024x1024 | #d7d8d4 | 0.36 | cabin photo | grigio_light, grigio, bianco |

Layouts (fractions of the floor; measured on the 400 px swatches):
- 4006P: emperador border 0.085, carrara field, emperador diamond half-diagonal 0.215.
- 4021P: giallo field, three emperador bars at v 0.24 / 0.5 / 0.76 (thin 0.11..0.885 x 0.04, thick 0.26..0.735 x 0.08).
- 4025P: crema field, verde frame (outer 0.115, 0.058 wide), verde corner squares 0.115.
- 4027P: verde border 0.17 with black corner squares, rosa field (faint 2x2 tile joints), verde diamond 0.17.
- 4034P: beige field, taupe diamond 0.32, beige square 0.355..0.645, gold pinwheel ribbons (simplified weave).
- 4173P: emperador border 0.085, bianco field with faint 2x2 joints.
- 4106D: black granite mitred border 0.09, peach crema centre. 4145D: plain grey-green onyx.
- 4157D: marfil mitred border 0.09, light-emperador mitred band 0.08, marfil centre.
- 4182D: marfil mitred border 0.085, dark emperador field, marfil diamond to the mid-edges, emperador square 0.29..0.71.

Not pictured in the floor list (from the cabin photos - guesses of the layout, flagged):
- 4028P (SL-1036): rosa field, verde bands across at 0.13..0.20 / 0.80..0.87 both ways, black crossings.
- 4017P (SL-1072): grey granite-chip / terrazzo film, no pattern.
- 4012P (SL-1095): golden giallo field, verde frame (0.16, 0.045), white-gold calacatta centre.
- 4072D (SL-1109): dark emperador border 0.075, marfil band, thin emperador line at 0.15, marfil centre.
- 4150D (SL-1135): marfil border 0.07, nero marquina band 0.045, marfil centre.
- 4082D (SL-1136): grey marble mitred border 0.09, bronze line, beige centre.
- 4039D (SL-1137): white-warm marble (4 slabs), medallion r 0.30: emperador ring, gold ring, marfil disc, four
  emperador petals with gold outline and gold leaves (simplified from the photo).
- 4036P (SL-1130): the floor is hidden by the lower canopy in the photo - **pure guess**: light grey field, grey band,
  white centre.

Not made: `checker-steel`, `checker-stainless` - a fitted picture would stretch the tread with the car size; the
engine already falls back to the tiling `lift_checker` (metals.py) for freight cars. Both reference plates are the
same lentil pattern; lift_checker is the brushed stainless one (the standard steel plate would be the same with a
duller grey).
