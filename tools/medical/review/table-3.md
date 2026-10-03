# Detail review: batch table-3

Generators changed: `t3_xy73.py`, `t3_xy80.py`, `t3_xy81.py`, `t3_xykgj2.py`, `t3_xyzg1.py`, `t3_alclib.py`, `t3_alc2.py`,
`t3_alc3.py`, `t3_jyzlib.py`, `t3_jyz1b.py`, `t3_jyz2b.py`, `t3_jyz3.py`, `t3_rhqycb.py`. All 14 designs were
regenerated, rendered `ok` and re-checked on `renders/<id>-compare.png` (photos also checked full size or zoomed).

## Shared fixes
- **ALC body (alc-1/2/3)**: the head-end "control panel" was drawn as a dark screen. The zoomed photo shows no screen
  there, only a grey rating label (toward the back) and a small dark logo sticker. Both are now decals. The castors
  were small grey forks almost hidden under the plinth. The photo shows white swivel housings with grey Ø62 wheels and
  darker hubs, clearly visible, and they are now drawn that way. The towel mat was too pale for alc-1 and alc-2 (now
  `#8fb0e2`). alc-3 keeps a pale mat, as its photo shows.
- **JYZ head sling (jyz-ib, iib, iiia, iiib)**: the sling was a V hammock of two broad planes. The photos show a spreader
  with up-turned hook ends, and from each end an outer and an inner strap. These carry two wide padded cups that sag as
  U's, and the inner straps cross, so the sling reads as an X. It is redrawn that way. The cups have a coloured
  piping band along both edges (blue on IB, lilac on IIB). The spreader is black on IB, as in its photo. The sling
  scale now follows each photo's spreader-to-arm ratio: IIB k 1.0 → 0.72, IIIA/IIIB 1.0 → 0.9.
- **JYZ harnesses**: they were thin flat sheets the colour of the pad, nearly invisible. They are now padded bands
  (34 mm) with 5 contrasting stripes and a buckle. IIIA is grey with black stripes, as in its photo.

## Per device
- **xy-73**: the "XIANG YU" / "MEDICAL" lettering was rows of grey blocks. It is now stroke letters on the lift plates,
  as in the photo. The actuator showed as a steep grey diagonal between the plates. The photo shows a near-horizontal
  bar, and it is now drawn that way. Nothing else differs.
- **xy-80**: the tube legs were dark metal; they are now the photo's lighter painted grey. The veneer was brown and is
  now honey-orange. Cannot match: the photo shows the stools staggered on display. The model keeps them nested, so the
  printed 550×380 footprint holds.
- **xy-81**: the castors were single grey forks; the photo shows black twin-wheel castors, and they are now drawn
  that way (stem, hood, 2 × Ø50 wheels). The black collar sat too low: it is now at ~360 mm, with the thick chrome
  sleeve from the hub up to it and the base raised to match. The saddle dip was too shallow (7 → 16 mm), so the seat
  read flat.
- **xy-83**: no difference at sheet scale (C-top with a round end, column, brace, H base, knob, stops, castors).
- **xy-kgj-2**: the seat and backrest were lavender. They are now the photo's royal blue (`#2c50a6`), and the cuffs are
  a light blue. Side and pose were re-checked against the photo: the rear frame and plates are on the patient's right,
  the right lever points forward-down and the left one is abducted. Size doubt kept: [960, 1380, 880] instead of the
  printed 1440×660×880, because the levers in the photo pose cannot fit the printed size (see notes).
- **xyzg-1**: the cradles were plain blocks; they are now U foam troughs with raised side lips. The weight was one
  plate on a chrome axle. The photo shows a stack of three rounded teal plates on a white axle that sticks out past
  them, and that is what is drawn now. The remote hung as a big spring with a box at seat height. The photo shows a thin
  straight cable to a long black hand switch hanging near the ski, and it is now drawn that way. The linkage geometry
  was re-checked on a 2× crop, correcting for perspective: the cradle heights, the 17° forward-outward reach of the
  left red bar and the 45° backrest bracket all match. Approximated: the small clamps and the exact linkage joints
  (the photo is 818 px and busy).
- **alc-1**: the end-face screen is now a label and logo, and the castors and mat colour are fixed (see Shared fixes).
  Nothing else differs.
- **alc-2**: the hood's free end was a thin flat cap; it is now a 130 mm end wall rounded with r 60, as in the photo.
  The hinge moved from 300 to 180 mm, at the head-end top edge as in the photo. The gown was a thick dark pad; it is now
  a thin crumpled spread with folds. The pillow was a block; it is now a flat, tilted envelope pillow. The label, logo,
  castors and mat are fixed as in Shared fixes. Size kept at H 1830 (photo hood).
- **alc-3**: the pillow is now a flat envelope pillow propped against the hand bar, and the mat is pale as in its photo.
  The hand bar, armpit rolls, harnesses, leg pad, remote and foot frame were all checked and match. Approximated: the
  quilting of the leg pad (seams only).
- **jyz-ib**: the sling (X with blue piping, black spreader) and the harness stripes are fixed. The cabinet, panel,
  hand switches, split top and pole were checked and match.
- **jyz-iib**: the sling is now smaller and lilac, and the harness stripes are fixed. Cannot match: the console panel
  has no interface picture (no screenCrop in the inventory).
- **jyz-iiia**: the pole arm was a solid triangle. The photo shows an open lattice truss, now drawn with three
  triangular windows. A second small control box is added on the bed (the photo shows two). The harnesses are grey and
  black, and the sling is fixed.
- **jyz-iiib**: the sling and the harness stripes are fixed. The printed panel, louvres, lumbar section and castors
  were checked and match.
- **rh-qyc-b**: the shroud said "REHAMASTER" in capitals. The photo reads "Rehamaster", now drawn as a mixed-case
  stroke script (capital R and lowercase glyphs). The rest was checked and matches: the 4 pads, the cantilever unit
  with the LCD, the leg holders, the cervical holder, the A columns, the base, the grab handles and the pedal with
  its coiled cable.

## What the format cannot match
- Printed text (panel captions, rating labels, Chinese logo text) is drawn as flat colour decals, and lettering as
  stroke tubes.
- JYZ-IIB has no interface picture because the inventory has no screenCrop for it.
- The xy-80 display arrangement is kept nested; see above.
