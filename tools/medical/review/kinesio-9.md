# kinesio-9 + kinesio-10: detail review against the catalogue photos

All 19 devices were reviewed. Every `.txt` is `ok` and newer than its json. Fixes were made in the generators
(`tools/medical/gen/k9_*.py`, `k9lib.py`, `k9_handtable.py`), which were then re-run. Compare sheets are at
`tools/medical/renders/<id>-compare.png`. Scratch files are in `tools/medical/scratch/k9rev/`:
- `run.sh <gen.py> <id>…` regenerates, waits for the render and builds the compare sheet.
- Photo crops are there too.
- Backups of the original screen crops / albedos and of the hand-table generators are there as well.

Sides were read from the photos with the frame's vanishing directions. The rule used: the seat front facing
image-bottom-left means the image-right side is the patient's left (+x). No inventory, catalog or C# was touched.
No design `size` was changed.

## Shared changes
- **Logo (k9lib.logo)**, used by all 9 hydraulic exercisers. 医疗 was drawn as grey blocks. It is now real stroke
  letters:
  - a white round mark (a disc, before a square) with the light-blue cross;
  - 翔宇医疗 drawn with the 医 / 疗 glyphs of `t4lib`;
  - a thin XIANGYU MEDICAL line under it.
- **Hand tables (k9_handtable.py)**:
  - `body()` takes the tower size, screen rectangle, slot and button position.
  - Smaller black tower corner caps (~48 mm; the photos show small rounded caps).
  - The slot is now a black window with plates and a rod.
  - New and reworked stations:
    - n-shaped blue arch stands (`arch_path`);
    - `post_ball` with an arch or cage stand;
    - `pegs` with given heights and a bar at the top;
    - `roller_st` with arch end stands and cap or dome ends;
    - `wheel_st` with an open spoked crank wheel;
    - `wrist_st`, the curved wrist / forearm lever;
    - `knob_post`, `oval_grip`;
    - `cradle_stool` with an X brace and an optional dome.

## xyzl-2 standing frame
Found and fixed:
- **Base.** It was square bars. On the photo it is a round-tube U loop with rounded rear corners, and its side runs
  end in square front stubs with black plugs.
- **Arches.** On the model they rose at mid-depth and converged on the post. On the photo they rise from the front
  stubs, run back at full width, and are joined by one cross run (with adjustment holes) in front of the post.
- **Footboard.** It now starts just in front of the post. The right cut-out is near the back, the left one at
  mid-depth, and the front edge is wavy (as in the photo).
- **Hip sling (weak spot).** It was a flat band. It is now a soft grey trough:
  - a U band with a sagging front wall (a curved top edge 90 mm lower in the middle);
  - a sagging back wall;
  - light piping along the front rim;
  - black strap bundles from the table frame to its 4 corners;
  - two black belts running diagonally across the front from the upper left down to the lower right (the photo has
    no X).

Not matched: the fabric's wrinkles.

## xyzl-3 two-person standing frame
Found and fixed:
- **Hip wraps (weak spot).** They were a rigid level U on black straps. They are now soft-looking grey U bands with:
  - their ends clipped to the posts and no straps (the photo shows none);
  - the outer end drooping ~10°;
  - light piping on the top edge and a seam line.

  Each wrap now has a white support arm under its front. A lower white curved arm carries the black gas strut with a
  ball knob at the wrap's outer front corner (photo, left station).
- **Knee boards.** They were small boards outside the posts. They are now blue-grey boards in the plane of the posts
  (170–720 high) with:
  - a white frame of two bars between the posts;
  - a grey pad on the patient's side;
  - clamp blocks with black knobs and chrome rods sticking out towards the middle (as in the photo).

## xy-1 upright bike
Found and fixed:
- **Flywheel shroud (weak spot).** It was a rounded box with two small ribbed squares. It is now a slab with the
  photo's D-shaped side profile:
  - a low rounded nose in front, a domed top and a full rounded rear;
  - silver ribbed covers wrapping the front-lower nose and the rear-upper corner (ribs follow the cover outline);
  - a dark round dish around the crank;
  - the whole shroud raised 30 mm.
- **Pedals.** The near (+x) crank now points down-front and the far one up-back, as in the photo.
- **Rear stabiliser.** It is now a shallow U in plan with its ends bent back to the caps. It was arched in elevation.

## xy-101c hand table (4 patients)
Found and fixed:
- **Tower.** The screen rectangle and the slot were placed from the photo (screen 275 × 168 from 69 below the top;
  narrower slot left of centre). The corner caps are smaller. The hub logo now reads 翔宇医疗.
- **Stations (weak spot), re-placed and reshaped after the main photo:**
  - **Wrist lever** (left, ~157°): blue runners, two curved blue arms to a pivot with chrome bolts, a padded forearm
    trough overhanging the edge with a tall light-grey strap loop. It replaces the A-frame box.
  - **Pegs:** moved to the back-left (222°). Shorter (150–185), with a 4th peg and a black top bar.
  - **Ball post:** moved behind the tower (255°).
  - **Crank wheel** (front-right): an open spoked blue wheel facing the patient, a lever with a black crank handle,
    and a base plate with a rectangular hole.
  - **Ball post on a blue arch stand** (right front, 22°): added, as in the photo.
  - **Roller** (right): on n-shaped ring stands, without the ball knobs.
  - **Cradle stool:** a black dome on the saddle end and an X brace.
  - **Knob post with a pulley:** replaces the lever station near the tower.
  - **Cable accessories:** black oval cable grips on the table, a cable clip, and a black grip hanging over the left
    edge.

Not matched: the small cable hardware is simplified. The top-view leaflet picture shows a different station set, so
only the main photo was followed.

## jy-ct-ii hand table (pediatric)
Found and fixed:
- **Tower.** It was the 101C tower (380 wide). On the photo it is narrower and taller (300 × 440), with:
  - large dark screens (236 × 150);
  - a wide weight-stack window (77 × 180);
  - a blue power button with a dark ring on each face.
- **Stations after the photo:**
  - **Ball post (front-left):** stands in a blue arch stand (not 4 legs).
  - **Ball post (right):** in a cage of 4 pink posts under a blue disc.
  - **Pink roller:** on blue n-stands, with a thick section, a thinner section, and a dome only at the right end.
  - **Upright blue wrist lever (back-right):** two arms to a high pivot with chrome bolts and a black strap loop.
    It replaces the A-frame box.
  - **Pink goal-frame pegs:** with the bar at the top.
  - **Pink lever on a blue post:** added behind-left.
  - **Saddles:** without the stray knob.
  - **Cable grips:** black oval grips added.

## xy-mcb-i smart peg board
Found and fixed:
- **Shape holes (weak spot).** They were flat grey outlines. They are now real recesses: the wood insert is a 15 mm
  slab with the 20 holes cut through, over the white shell floor. The rim is a ring.
- **Side seams.** The shell side had layer seams. It is now one smooth rounded side, as in the photo.

## xy-mcb-i-deluxe smart peg board with monitor
Found and fixed:
- **Screen (weak spot).** The crop was a skewed photo with masking wedges and a diagonal line. It was straightened
  with a perspective warp to 1280 × 720 (the blue game area only). It was written to
  `reference/xy-mcb-i-deluxe_screen.jpg` and the albedo.
- **Monitor.** The bezel is thin and even, and the monitor sits over a silver chin with its grille. The picture now
  covers the whole panel.
- **Holes.** The 8 × 8 holes are now real cups in the wood, with violet lit floors on 6 of them.

Not matched: the photo's screen shows reflections, and they stay in the picture.

## xy-jzj-i posture mirror
Found and fixed:
- **Base (weak spot "splayed front feet").** The photos show neither an H nor splayed front feet. They show:
  - a black pedestal block with concave flared flanks under the panel;
  - a pinwheel base: a node at the pedestal's front-left corner (castor under it) carries the long left arm back-left
    to its castor;
  - a node at the back-right (castor under it) carries the long right arm forward-right.

  The model now has this base.

## xy-jzj-ii posture mirror pro
Found and fixed:
- **Base and castors.** The base stands higher (castors Ø90, arms 115–179), so less of the white pedestal shows.
- **Panel.** It is now 830 × 1580 (bottom 370), the photo's 1 : 1.9.

Not matched: the photo seems to show only ~100 mm of pedestal. The model shows ~170 mm, because of the perspective
and the fixed overall height 1950.

## xy-msz-i smart OT table
Found and fixed:
- **PC screen (weak spot).** The skewed crop was straightened with a perspective warp to 1280 × 720 (the UI only).
  It was written to `reference/xy-msz-i_screen.jpg` and the albedo.
- **PC body.** It is now 580 wide with a thin black bezel, the white chin and the picture over the whole panel.

## xy-dssz-01a shoulder press
New logo. No other difference was found at sheet scale.

## xy-dssz-02a pec dec
Found and fixed:
- **Arm pose (weak spot).** Following the photo, the patient's right arm (−x) is now swung out about the hub by 28°.
  Its upright leans outward, with the box and handle. The left arm stays at the start position.

Not matched: in the photo the swung box is cut off by the frame edge, so the angle is estimated.

## xy-dssz-03a biceps / triceps
New logo. No other difference was found.

## xy-dsxb-01a abdominal / back
Found and fixed:
- **Lever side.** The pivot hub, arm and cylinder were on the patient's left. The photo has them on the RIGHT, so the
  lever group is mirrored.
- **Roller.** It now rests just above the lumbar pad, over the shoulders (it was high behind the head). The handles
  were re-bent to match.

## xy-dsxb-02a chest / back
Found and fixed:
- **Lever tops (weak spot "arm poses").** The model's tops bent inward over the shoulders. In the photo they are
  short hooks bending outward and up, so they were redrawn that way.

## xy-dsxb-03a back extension
Found and fixed:
- **Lever side.** The pivot, arm, roller arm and cylinder were on the patient's left. The photo has them on the
  RIGHT, so they are mirrored.

## xy-dsxz-01a leg press
New logo. No other difference was found at sheet scale.

Not matched: the footboard-to-seat distance cannot be measured exactly from the oblique photo.

## xy-dsxz-02a hip abductor / adductor
Found and fixed:
- **Cradle pads (weak spot).** The model had box walls. They are now:
  - side slabs flared outward 15°, higher at the seat end (520 → 430);
  - thick rounded blue pads following them;
  - a puffed bottom pad.

  The cradle reads as the photo's V-shaped cradle.

## xy-dsxz-03a leg extension / curl
New logo. No other difference was found.
