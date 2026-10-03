# kinesio-5 — notes

Generators: `tools/medical/gen/k5_*.py` (+ `k5lib.py` helpers on top of `p1lib.py`); each writes only this batch's
designs: `k5_boards.py` (xy-47, xy-49), `k5_steps.py` (xyc-t1, xyc-t2), `k5_xy5.py`, `k5_wallbars.py` (xy-7, xy-8),
`k5_stands.py` (xy-51, xy-kgj-1), `k5_pulleys.py` (xy-6, xy-6a), `k5_xy54.py`, `k5_zh.py` (xy-zh-1, xy-zh-2).
Every device was rendered `ok` and checked on `renders/<id>-compare.png` (plus the full-size angle/front/side PNGs
where the sheet was too small). No device in this batch has a screenCrop, so all LCDs are dark `screen` boxes.

## Parts lists (from the photos, written before drawing) and final check

### xy-47 — balance board (rocker)
Photo: orange lacquered board 900 × 700 × 20 (faint wood grain); under it a red-orange rocker shell whose front face is
an arc along the 900 side (lowest in the middle, the ends meet the board ~30 from its ends), set back a little from the
board edge; a small round black/white badge in the middle of the rocker front.
Final check: board, rocker arc, badge and colours match. Approximate: no wood grain on the lacquer.

### xy-49 — balance board with handle
Photo: pale cream maple top with an orange edge band, 20 thick; dark-brown wooden rocker arc visible under the front
edge (arc along x); chrome U-handle Ø25 on the far (rear) edge, posts ~70 in from the edge.
**Size change** [900, 700, 220] → [700, 900, 220]: a perspective reconstruction of the board corners (vanishing points
of both edge pairs) gives handle edge / side edge = 0.75 ≈ 700/900, so the handle is on the SHORT edge; the posts map
to x ≈ 90 and 640 → drawn at 95 / 605 (510 apart), handle top at 220.
Final check: OK. The rocker is seen only from the front/low views (as on the photo, where it barely shows).

### xyc-t1 — steps + platform + ramp
Photo: white boxes with blue-grey anti-slip tops in aluminium edge frames; three nesting step boxes pulled out to the
left (each a little narrower in depth), the 350 platform box (~1.1 m), then a ramp wedge sloping to the floor on the
right with two small rimmed hand slots on its side; slots also on the step ends; small feet.
Drawn: steps 95/180/265 high with ~330 treads, platform 990–2130, ramp 2134–3030, trims, mats, slots.
Approximate: the slots are dark rounded insets with an aluminium rim; mats are plain rubber colour (no texture).

### xyc-t2 — nesting step boxes
Photo (two states): light-wood laminate boxes with dark oval hand slots on the fronts and on the big box's ends;
nested heights from the nested view ≈ 400 / 310 / 215 / 125, widths 600 / 570 / 535 / 500; pulled out they form a
staircase with the smaller boxes stepping toward the viewer.
**Size change** [1200, 400, 400] → [600, 1200, 400]: the photo staircase steps out FORWARD (along the boxes' depth),
so the 1200 run is the depth and the width is the 600 box length. Drawn as the staircase (not the nested block).
Final check: OK. Approximate: open bottoms / the small notch under the smallest box are not modelled.

### xy-5 — arched sit-up bench
Photo: blue PU board ~350 wide bowed upward (circular arc, apex near the high end), 6 chrome tufting buttons in pairs;
at the high end a white square post on a white T-foot tube (white end caps) with a hole row, a black pop-pin knob and two
pairs of black foam rollers: the upper pair right at the board end, the lower pair ~250 above the floor; the low end
rests on a short post on a second white T-foot. High end at the back, low end at the front (as the photo's near end).
Final check: board arc, rollers (concave), posts, T-feet, buttons OK. Approximate: buttons are chrome domes (the photo
shows recessed rings); the small spring latch at the post top is a chrome block.

### xy-7 — wall bar
Photo: two green rails (~50 square), the top curving forward ~330 with black end caps; 15 rungs Ø30: 5 orange wood at
the bottom, 5 green, 3 steel and 2 steel in the curved top (with a small clamp ring in their middle); green angle
brackets on the outside of both rails at ~1800; black nuts at the rung ends.
Final check: OK. Size kept (620 deep printed); the drawn top reaches z ≈ 470 (photo projection), not 620.

### xy-8 — wall bar with pull-up frame
Photo: straight green rails with small bent feet, 14 rungs (5 orange, 5 green, 4 steel at the top, one hidden by the
frame); a green pull-up frame shown FOLDED against the ladder: J side members hooked on the 1650 rung, a top bar along
x in front of the ladder whose left end sticks out, and a wide green cross plate tilted forward.
Final check: OK. Drawn in the photo's folded state, so it is ~260 deep instead of the printed 580 (size kept).

### xy-51 — upper-limb hanging frame
Photo: U base (back cross tube, two feet running forward with black front caps); TWO telescopic columns (not one as the
form text says) at the back corners: white lower tube, black inner tube with a black knob at ~1100, the top bending into
a J; a chrome spring scale hangs from each J tip, carrying a spreader bar with a khaki folded sling at each end.
The J's and spreaders point the same way (+x, to the right) on the photo — the inner tube swivels; drawn as photographed,
so the right pair overhangs the 800 base by ~240 at 1.4–2 m height (size kept at the base).
Final check: OK. Approximate: slings are flat folded khaki bands (box + inner dark layer), not soft cloth.

### xy-kgj-1 — hip rotation trainer
Photo: low platform with an aluminium rim (rivets) and a blue top; two chrome posts on square base plates, black ball
knobs low and high on each, inverted-U chrome rail with a black foam grip; in the middle a beige dome carrying a
tilted (~13°, left side down) disc, red back half / blue front half, two black foot holders with straps and buckles on a
line along x; a short chrome stop pin in front of the disc.
Final check: OK. Approximate: holders are blocky (binding shape simplified).

### xy-6 — hemiplegia rehabilitation device
Photo: white tube base frame with rounded corners and black glides; dark wooden standing board in the front part;
two white pedal plates flanking the column behind the board, rear ends raised; white column from the base middle,
slightly curved near the top, T bar on top with a black pulley (left) and a blue pulley (right); a mid cross bar at
~1130 with two black pulleys and two small guide pulleys below; blue scale strip with white ticks on the column; white
ropes, yellow rounded-triangle hand rings at ~1000 and small yellow loops at ~750, ropes on to the pedals.
**Size change** [870, 480, 1700] → [480, 870, 1700]: the base is clearly deeper than wide on the photo (the printed
L×W was mapped long-side = width).
Final check: OK. Approximate: rope routing simplified; a rear strut supports the column (the photo shows a second
tube behind it).

### xy-6a — limbs passive trainer
Photo: long white floor rail between two white T feet (black caps); black mesh office chair on a gas lift on a white
mount on the rail (facing the pulley column); between chair and column a white front post with an arm back to the
column, a short cross bar with two green D-handles on top and a lower pair on ropes, two black pedal plates on levers
at ~300; the column at the back with a top bar and a mid bar, black pulleys hanging at both ends of each; black ropes.
**Size change** [1600, 700, 1600] → [700, 1600, 1600]: the 1600 run is along the patient's facing direction (rail),
so it is the depth; chair at the front (z = 1600).
Final check: OK. Approximate: chair backrest mesh is a translucent dark panel with lumbar slats; ropes simplified;
the pedals are mostly hidden behind the chair from the front-left angle (as on the photo they are low and in front).

### xy-54 — OT table
Photos: light-maple cabinet on 4 grey castors with chrome corner trims; front (photo 2) two doors with vertical wooden
pulls and a lock; back (photo 1) a recessed panel in an aluminium frame with blue knobs and a fold-down tray (peg board
with coloured shapes + simulation tools) sloping down outward; fold-out side shelves on chrome struts: ring tree on the
left, graded wooden peg blocks (green bands, clear tray) on the right; on top: two pegboard panels with white pegs at
the back-left, bead maze with blue/red/green wires and coloured beads, a flat peg board, a white telephone, a board of
8 wooden skittles with coloured strings, a steel rod block.
Final check: OK at sheet scale. Approximate: toys are simplified shapes (163 parts — most are small toys); depth 1030 =
cabinet 620 + open tray 380.

### xy-zh-1 — four-unit progressive muscle trainer
Photo (taken from the front-right): white 50 mm square-tube frame (4 legs, top rectangle, shelf at ~780, low rectangle
at ~220), bolt heads; galvanized slide rails: floor-standing in the front face (~540 from the left), on the left face
and at the back-right leg. Units: front — tall white oval SXZ-1 trainer with crank disc, two strap pedals, foot roller
bar with black ends, black neck + dial, small LCD head; left — big white oval JGJ-1 shoulder trainer facing outward
with a crank and a black dumbbell grip; shelf — WGJ-1 wrist trainer (round white base, black joystick, lever, knobs);
right — JZ-1 shoulder-elbow trainer facing +x with an L handle and black grip, black LCD on top; black star knobs.
**Size**: estimate kept [1300, 900, 1750]; frame 940 × 760, units project to the full width/depth.
Final check: OK. Approximate: unit internals/labels, crank geometry simplified.

### xy-zh-2 — six-unit progressive muscle trainer
Photo: long white frame (shelf ~900, top ~1750) with a white wall-bar ladder (to ~2100) at the left end and two orange
peg bars (pegs pointing out, black handle and knob) on its outer side; shoulder trainer JGJ-2 (white oval on a
galvanized rail) with a long black crank arm up to a grip near the ladder top, small LCD; pulley gantry (post, top arm,
hanging yellow bar, diagonal strut, two pulleys on the top rail, ropes to grey triangle handles below the shelf);
cream upper-limb pedal trainer on the shelf (round LCD head, strap pedals both sides, foot bar with black ends);
shoulder-lifting gauge column (cream base, dark motor, slanted column with purple scale, head with LCD + red button,
chrome bar with black grips); finger-ladder strip (green spiky / white segments) on the right face near the back.
**Size**: estimate kept [1900, 800, 2100].
Final check: OK. Approximate: green "spikes" are rows of small rounded teeth; pulley rope routing simplified.

## Detail review 2026-10-03
See `tools/medical/review/kinesio-5.md`. Size changes there: xy-51 → [1255, 800, 2050] (the overhanging pairs are
inside the footprint), xy-54 → [1890, 1030, 1130] (worktop ~860 per the photos + toys), xy-zh-1 → [1460, 980, 1750],
xy-zh-2 → [2070, 1100, 2100] (units sticking out of the frames; models moved with `k5lib.shift()`).
