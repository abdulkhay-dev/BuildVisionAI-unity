# Detail review: batch table-1 (XY-K-SF treatment tables, XY-K-CZLD-III)

Generators changed: `tools/medical/gen/sf.py`, `sflib.py` (one colour), `czld3.py`. Every device re-rendered `ok` and
re-checked on `renders/<id>-compare.png`.

## Shared fixes (several tables)
- **Swan base** (SF-1/2/3 new, SF-4B, SF-4 new). The photos show a ladder frame: a transverse beam at each end resting
  on two legs, with **black plugs on the beam ends** and on the ends of the two long rails, which sit inboard. The model
  had legs sticking up through the rails with **black caps on top**, and the rails on the outside. It is redrawn as in
  the photos, with the twin castors under the rail ends.
- **Swan arm cover**. In the photo it is a broad dark-grey band over the convex face of the arm. The model had a thin
  light band that hardly showed. It is now 34 mm thick, slightly wider than the arm and `#666b73`. SF-3 new has a
  brushed-metal cover and SF-4B a light-grey one, as in their photos.
- **Old Z base** (SF-3/4/5). The model had a grey motor box and a horizontal actuator between the columns at base
  level, which none of the photos show. They are replaced by the white link plate the photos show. The black drive box
  now hangs under the apron (SF-4: under the seat; SF-5: under the pelvis). SF-3 has a black round motor on the back
  rail at the foot end. The small blue caps on the rails beside the legs were missing and are added.
- **Box base** (SF-4C/4D). The legs had black caps on top. They now end flush with the rails, with black plugs on the
  outer faces, as in the photos.

## Per device
- **xy-k-czld-iii**: the pedestal was too short along the length (660 → 820 at the bottom, 540 → 560 at the top, as in
  photo 1). The rim waves were solid humps. They are now open handle arches with the mattress showing underneath
  (photo 1). Cannot match: the "Sunnyou" lettering (the decals are flat colours, so it is drawn as blue bars). The screen
  is dark because the inventory has no screenCrop.
- **xy-k-sf-1**: the head legs stood at the very end; in the photo they are set ~330 in, between the arm rest and the
  face rest. Moved, and the H stretcher shortened to match. The pad was too pale; the photo is a deeper blue
  (`#78a8dc`). The side rails now stop at the waist notch with black plugs, with a set-back piece behind the notch. The
  blue label moved from the end face to the front rail at the head. Approximated: the exact shape of the stepped
  bracket.
- **xy-k-sf-1-new**: the ladder base, the dark arm covers and a blue warning triangle on the top frame (photo). No
  difference left at sheet scale.
- **xy-k-sf-1b**: the lift was a symmetric double X. In the photo each X is a long shallow bar rising from the head
  side, crossed by a short steep bar. Redrawn that way, with the cross tubes at the long bars' ends. The actuator is
  grey, stands under the head part and has a dark push rod from the motor (it was one big diagonal cylinder). The blue
  hand switch moved to the apron just after the waist notch. Approximated: the exact bar lengths and pivots.
- **xy-k-sf-2**: the head section had a big stadium hole with a plug. The photo shows only a thin closed slit with a
  stud at each end, so it is now drawn that way.
- **xy-k-sf-2-new**: the ladder base, the dark arm covers and the blue triangle. No other difference.
- **xy-k-sf-3**: the motor and actuator between the columns are gone (white link plate instead), the black round motor
  is added on the back rail at the foot end, and the blue rail caps are added. Cannot match: the "XIANG YU / MEDICAL"
  lettering (grey bars, no text in the format).
- **xy-k-sf-3-new**: **the head was on the opposite side to the photo** (it had been chosen for the render camera).
  Mirrored: the backrest, the round motor and the foot switch are now on the right, as in the photo. The swan arms keep
  the photo's direction (pivot up on the left, posts on the right). Two green caps on the rails replace the single blue
  button. The arm covers are brushed metal and the ladder base is drawn as in the photo. Approximated: the gas struts sit
  on the centre line.
- **xy-k-sf-4**: the panel on the control box was a dark screen. The photo shows a light blue-grey membrane panel with
  a dark window and two rows of keys, and it is now drawn that way. The base also got the Z-base changes above.
- **xy-k-sf-4-new**: **this one was mirrored too**: the photo shows the backrest on the right. Mirrored, and the
  armrests swapped: the horizontal black armrest is on the far side and the folded black pad on the near side, beside
  the backrest. The hanging leg section was raised to 78° (it hangs almost vertically in the photo). The castors are now
  Ø90 (they were Ø55). The triple foot switch moved in front of the head half. Cannot match: the photo's multi-link
  white lift linkage is drawn as the swan base. A faithful linkage would need dozens of small links, and it is mostly
  hidden in the photo.
- **xy-k-sf-4b**: the V of the leg sections was too narrow (splay ±130 → ±210 mm, as in the photo). The motor was a
  grey box; it is now a rounded light-grey housing. The arm covers are light grey and the ladder base is drawn as in the
  photo. In the splayed pose the leg sections stick outside the 700 width.
- **xy-k-sf-4c**: the box-base legs (plugs on the faces), and the base rails are deeper (230–330). Approximated: the
  lift mechanism inside the apron (drum, lever, post). The photo shows it only in part.
- **xy-k-sf-4d**: the column's top cover was mid-grey; in the photo the column is all white, with a separate grey gas
  strut above its slope. Changed that way. The box-base legs got the face plugs. Approximated: the curved outline of the
  column.
- **xy-k-sf-5**: the near leg section did not drop enough. Its foot end now drops by 115 mm and splays out by 80 mm,
  with the gas spring following. The motor and link and the blue caps follow the Z-base changes. Cannot match: the
  lettering (bars).

## What the format cannot match (all devices)
- Printed text and logos (XIANG YU / MEDICAL, Sunnyou, the rail stickers): decals are flat colours.
- Coiled white cables and thin wiring: left out or drawn as plain black cables.
