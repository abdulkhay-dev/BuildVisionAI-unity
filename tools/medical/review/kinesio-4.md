# Detail review: batch kinesio-4

Generators changed: `k4lib.py` (adds the glyphs 1, 2, 3, 4 to the shared stroke font at import, for this batch only;
`p1lib.py` itself is untouched), `k4_xy2a.py`, `k4_xy2b.py`, `k4_xy3.py`, `k4_xy31.py`, `k4_xy32.py`, `k4_xy33.py`,
`k4_xy36.py`, `k4_xy39.py`, `k4_xy4.py`, `k4_xy41.py`, `k4_xy43.py`, `k4_xy44.py`, `k4_xy45.py`. All 14 designs were
regenerated. Each one rendered `ok` (the .txt is newer than the json) and was re-checked on `renders/<id>-compare.png`.
Photos were also checked at full size or as 2× crops. Scratch: `tools/medical/scratch/k4rev/`.

## Per device
- **xy-31** (unconfirmed edit): the board ribs were thin dark grooves. The photo shows a corrugated face, so they are now
  rounded ribs Ø18 in the board colour. The orange is brighter (`#f07a26`) and the pegs paler. Kept: the tent reading
  (board in front, prop leaf behind). The 2× photo is low-resolution and the inside geometry cannot be read more exactly.
- **xy-41** (unconfirmed edit): the label and logo are now drawn with letters, not grey plates. The white label sits at
  the board's top-left corner. It carries "XY-41" in stroke letters, grey text rows, a second short row and a dark QR
  square. The oval logo has a black ring, a white face, a blue band with white "XY" and grey lines. The pine is warmer.
  The knot dot moved from the board to the top step's riser, where the photo shows it. Cannot match: the label's small
  Chinese text.
- **xy-43** (unconfirmed edit): the gusset at the right end was a large triangle running the full depth. The photo
  shows a compact plate with an arched top, and it is now drawn that way. The logo was a blue rectangle; it is now a white
  oval with a blue ring, a blue "XY" and a red dot.
- **xy-45** (unconfirmed edit): the fittings tablet moved to the front-centre/right, as in the photo. Its fittings were
  re-placed from the photo: the chrome tap at the back left of centre and a chrome rod bolt at the back right. A black
  hasp with a chrome strip and a new blue switch/lock piece are on the right. The brass chain and padlock are at the front
  left. The white switch plate is larger, front right. The knob heads are larger (80 mm).
- **xy-2a**: the shroud was a tilted egg with a straight orange/grey border and a fat rear end. It is rebuilt from the
  photo's side profile as a wedge. The bottom is flat on the beam and the top rises from a low round rear nose to a tall
  front with a rounded end. The orange is now a hood band along the top edge that wraps down round the rear nose, and the
  front top corner is grey. The border therefore follows the top line and curves at the rear, as in the photo. The
  swoosh runs from the nose bottom up to the crank ring, and the grey cap now sits above it. Cannot match: the LCD has no
  interface (no screenCrop).
- **xy-2b**: the gap between the seat module and the flywheel housing was too large (about 260 mm). The module now
  reaches to z 788, with the rail and its end caps lengthened to match. In the photo the module's rear face leans back
  at the top, but the model had it leaning the other way; this is fixed. The silver panel moved to the module's front
  lower corner. Cannot match: the display has no interface.
- **xy-3**: the oar clamps were plain chrome boxes. They are now a chrome fork of two rounded cheek plates on a flat
  mounting plate, with a through-bolt and a small black clamp lever with a ball end. The rear label was a square decal;
  it is now a red triangle with a white centre.
- **xy-32**: the pole was too thick for the base (Ø40). It is now Ø32, giving the photo's base-to-pole ratio of about 9.
  The discs are thinner (10 mm), with lighter wood edges. The card was 230 wide, centred and tilted 22°. It is now
  180 × 150 with the pole hole near its back edge, a second round cut-out at a back corner, and a 30° tilt.
- **xy-33**: the tilt was too shallow, and the back legs reached up to the top. In the photo all four legs are equal,
  with copper hinges on the front legs and black caps on the back ones. The top is hinged at the front edge, its back
  standing about 250 above the frame. It is now drawn that way: tilt 17°, legs to 520, upper braces at 455, and a centre
  prop under the raised back. The accessories changed too. The right rail now has a small stop at the back and a slider
  block with a cross roller near the front (it had a tall block at the back). Cannot match: the photo does not show the
  lifting mechanism; the prop is an assumption. The accessory blocks are simple wood shapes.
- **xy-36**: **size changed to [790, 170, 660]**. The printed 23 cm height contradicts the photo. Measured against the
  790 base, the rods stand about 660, 580, 505 and 390 above the floor, and the shapes are about 130 across. The rods and
  shapes now follow the photo, and the wood colours are warmer. The printed H is kept in the inventory; the caller should
  confirm the change.
- **xy-39**: the brackets did not match the photo. Read with the camera low at the left, the photo shows the following.
  The wall net spans the whole width under the net's back edge. At each end an A-shaped side truss rises about 470 above
  the net, with its apex about 60 % of the depth from the front. It has a leg to the net's front corner and a long strut
  from the apex down through the net to the wall post at about 700. A ridge rail joins the apexes. The model is rebuilt to
  this, adding a short back leg and a middle hanger. The old wall-plane triangles, the top wall rail and the knee braces
  are removed. Cannot match: the exact member layout from one oblique, low-resolution view.
- **xy-4**: the saddle was a lofted pear. It is now a heart: two wide rear lobes, a notch at the middle of the back, a
  waist and a rounded nose. The footrests gained the photo's hanging ratchet-strap tails.
- **xy-40**: no difference at sheet scale. The roof, label strip, braces, half-width back net, pulleys, two green handles,
  two navy slings, 3-section table with face slot, straps, rail, screw feet and castors were all checked. Cannot match:
  the left back post is hidden in the photo and assumed symmetric.
- **xy-44**: the disc stack colours were green/teal/teal/red. The photo shows, from the bottom, cyan-blue, teal, red,
  red, and they are now drawn that way.
