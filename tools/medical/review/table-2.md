# Detail review: batch table-2 (XY-K-SF tables p5–8, XY-46, XY-70, XY-71, XY-100)

Generators changed: `tools/medical/gen/sf2.py` and `table2.py`. `sf.py` and `sflib.py` were not touched. All 14
designs were regenerated. The first run also picked up the table-1 reviewer's changes to `sf.py`, because the table-2
designs predated them. Every device re-rendered `ok` and was re-checked on `renders/<id>-compare.png`. Originals are
backed up in the reviewer's scratch folder.

## Shared fixes
- **Old Z column** (`z_column2`; SF-6, 7, 8, 9). The model drew an arch: a horizontal top that dropped steeply into
  a tall post at one end. The photos (SF-8 is the clearest) show something else:
  - a short top block under the apron;
  - a broad straight beam at about 40°, widening downwards, with a grey upper face;
  - a long, low foot block (about 125 mm) under the whole column, which carries the lettering.

  The beam lands on the far end of the foot block, which has black plugs on its corners there. The column is open
  towards the head side. Redrawn that way (`COLS` 460/1040, span 440). The lettering is now centred on the foot blocks.
- **Old base** (`old_base`). The black drive was a box under the apron. It is now a round black motor half hidden under
  the apron, in the gap between the columns, as in the photos. The castors went from Ø50 to Ø70 (photo).
- **Swan base** (`swan_fix`; SF-5 new, 6B, 7 new, 8B, 9 new). No photo shows a grey Linak actuator sloping between
  the arms. They all show a white horizontal beam just above the rails, from the first arm's foot to the second arm's
  posts, so the actuator was replaced by that beam. The ladder base with black beam-end plugs and the broad dark arm
  covers come from table-1's `sf.py` and match SF-5 new, 6B and 8B.
- Head side and arm direction: checked against every photo; all were already correct after the flips.

## Per device
- **xy-k-sf-6**: column shape; drive; the head strut is dark grey, as in the photo (it was steel). The steel frame at
  the head end lies folded up inside the base (from the end beam up towards the column, with a black gas spring
  beside it). It no longer sticks out of the end.
- **xy-k-sf-7**: column shape; drive; Ø70 castors. Added the white rail and the black gas spring with a steel rod under
  the far leg section. The photo shows them, and only the near leg had them before.
- **xy-k-sf-8**: column shape (this photo is the reference for the shape); drive; castors.
- **xy-k-sf-9**: column shape; drive; castors. No other difference at sheet scale.
- **xy-k-sf-5-new**: the head was drawn as three pieces. The photo shows a wide face piece reaching the far edge, with
  the slot near its near edge, plus one narrow near flap at a lower angle. Redrawn that way. Lift beam replaces the
  actuator.
- **xy-k-sf-6b** (side-on photo):
  - The base and arms sat about 100 mm too far towards the back end. Measured from the photo and moved: base 240–1650,
    arm posts at 370 and 1170 in final coordinates.
  - Under the raised back, the photo shows a dark line along its whole length and a steel strut from the top frame up
    to the back on the near side. These replace the black actuator, which rose steeply from the base.
  - The invented black gas spring under the legs is gone. The photo shows a steel strut sticking down from the leg end
    with a black knob, and that is drawn instead.

  Cannot be settled from a side-on photo: whether the right end is a split back (near half raised, far half flat, as
  drawn) or a full back over a separate board.
- **xy-k-sf-7-new**:
  - The handle on the armrest post pointed up. In the photo it points out past the head end and down, and is steel
    with a black grip.
  - The arm covers are light grey: this photo shows white arms with only a thin dark edge, not a broad dark band.
  - Lift beam.
- **xy-k-sf-8b** (hanging leg):
  - The base was too long, so the leg section hung inside it. In the photo the second arm's pivot sits under the
    thigh/leg hinge, the base ends there, and the leg hangs out beyond it.
  - The base was shortened to 60–1290 and the arms re-spaced (posts at 250 and 885). The leg now hangs about 190 mm
    beyond the base end.
  - The grey foot-control box now hangs under the base at the head end, with a white cable looping to the floor. It
    used to lie on the floor.
  - Lift beam.
- **xy-k-sf-9-new**: the arm covers are light grey (the photo shows no dark band); lift beam. No other difference.
- **xy-k-sf-9b** (X-frame):
  - The truss was one big symmetric X per side. The photo shows an "N":
    - bar A, from the top frame at the head end down to post 1;
    - bar B, from post 1 up to the chest/paddle joint;
    - bar C, parallel to A, from there down to post 2 at the foot end.

    Redrawn with black-capped posts at 805 and 1550, pins and a black lever on post 1.
  - The head drooped 6°. Both photos show it raised, so it is now raised 10°, with the two flaps splayed about 8° in
    plan (a fan, as in the photo).
  - Control box: the dark-blue panel is on its top face, with a small blue label on the front. It used to be a big
    blue front panel. The box, the black motor beside post 2 and the gas spring were moved to the photo's places.
  - Approximated: the paddle's swing/extend mechanism under it (not visible).
- **xy-46**:
  - The legs stood 270 mm in from the ends. In the photo they are about a quarter of the length in, so they are now
    at 360.
  - The crank stuck out 120 mm past the top. In the photo it runs from the right leg's head towards the end and stays
    under the top, so it does now.
  - Mounting plates are smaller; the dark lower sleeves are slimmer and shorter.

  Cannot match: the wood material shows plank stripes, where the photo shows a smooth honey laminate.
- **xy-70**: the three straps were too far towards the foot. They are now at 240 / 620 / 1320, measured between the
  legs. The first one crosses the face hole, as in the photo. The chrome side bars end at 1460, as in the photo.
  Approximated: stitched strap edges (flat plates with a seam decal).
- **xy-71**: the dark-blue label (with its white text line) and the small label were on the long front apron. The
  photo shows them on the end apron: the big one mid-way, the small one by the front corner. Moved. Added the black
  plugs on the ends of the long apron rails at the corners (photo).
- **xy-100** (small photo):
  - The armrest loops were too tall (top 860 → 800).
  - The twist disc was a tall flared mushroom. It is now a flat ribbed plate on a small black foot.
  - The boom pulley was a dark block; it is now grey, as in the photo.
  - The blue T-bar is longer, and the T-post got its black knob.

  Approximated, because the photo is 437 px wide: the spool spacing, the curves of the base tubes and the mechanism
  under the seat.

## What the format cannot match
- The printed "XIANG YU / MEDICAL" lettering: decals are flat colours, so it is drawn as grey letter blocks. The
  Sunnyou and label texts are drawn as plain colour patches.
- Thin coiled white cables on the old tables, and the white cable from SF-9B's control box to the paddle: left out.
- Wood grain: the `wood` material has its own plank pattern.
