# kinesio-6 — notes

Generators: `tools/medical/gen/k6_*.py` (+ `k6lib.py`: castor, star/ball knob, telescopic handrail post, rail saddle).
Each writes only this batch's design files: `k6_t1.py` (xyf-t1), `k6_t2.py` (xyf-t2), `k6_steel.py` (xyf-t3, xyf-t4),
`k6_bars.py` (xyg-1, xyg-2), `k6_walk.py` (xyf-z1, xyf-z2), `k6_z3.py`, `k6_z4.py`, `k6_xygs1.py`, `k6_xyh1.py`,
`k6_xyh2.py`, `k6_xyd1.py`. Frame as in Docs (x from the left seen from the front, z = depth at the front, y up).
All 14 render `ok`; every device was checked on `renders/<id>-compare.png` after its last change.

Note on compare.py: on 10-03 at midnight the shared venv `/private/tmp/claude-501/venv` lost its `pyvenv.cfg` and
Pillow's .py files (macOS /tmp cleanup). The sheets were then made with a fresh venv in this session's scratchpad.
`compare.py` itself was not changed. Whoever relies on that venv needs to recreate it.

## Parts lists (from the photos, written before drawing)

### xyf-t1 — two-way wooden stair
- A symmetrical stair block in flat beige laminate (#cdb391). Each flight has 4 treads, a rise of 120 and treads
  ~321 deep. The central platform is a separate module ~800 wide at 600, with vertical seams at both of its ends and a
  small dark label at the upper right of its front face.
- Treads and risers are covered with light grey-blue anti-slip rubber. The side faces are beige.
- On both sides (front and back) there is one continuous Ø38 light-blue-silver handrail. It slopes up the left
  flight, runs level over the platform and slopes down the right flight, and its ends turn down at the bottom.
- 6 white posts per side stand on the treads: at the flight bottom, at mid-flight and at the platform edge. Each has a
  black star knob near the top, pointing outward, and a small saddle under the rail.

### xyf-t2 — three-way stair
- White body. The left and right flights run along x (4 treads, rise 120, 800 deep). The platform is ~800 × 800 at
  600. A front flight of 2 treads (300 deep, rise 200) comes toward +z, as wide as the platform, so the overall depth
  is 1400.
- Light-blue speckled covering (#a3c1e2) on all treads and risers.
- The back rail is continuous and runs level along the platform's back. The two front rails go up the side flights,
  turn at the platform's front corners and slope down both sides of the front flight. Chrome Ø38 rails on white posts
  with black knobs, including a post at the middle of the platform's back.

### xyf-t3 — two-way steel ladder
- Two flights of 5 folded sheet-steel treads (top plate + front lip), rise 100, open risers. Lavender sheet-steel
  stringers (#bab7d6) on both sides: zig-zag top, straight underside, rounded foot on the floor.
- The platform at 600 is a lavender box 120 deep with a plate top, standing on a white square-tube frame (4 legs,
  bottom and top rectangles).
- Handrails are light-blue-silver Ø38, sloped, level over the platform, ends turned down. They sit on white posts
  bolted outside the stringers, with chrome inner tubes and black knobs. Platform corner posts are included.

### xyf-t4 — three-way steel ladder
- Side flights as T3 (5 treads, light blue-grey sheet steel #c4d8ec), 700 deep.
- The platform is a closed box. Two closed box steps (rise 200, 220 deep) descend toward the front, each with a
  lipped top edge and seams.
- The rails are painted light blue (#86b4dc). The posts are white with brass-tinted chrome inner tubes
  (#cfc6a0, as on the photo) and black knobs. The front rails turn round the platform corners and slope down both
  sides of the front steps.

### xyf-z1 — forearm walker
- A cream U base of rectangular tube (30 × 38), closed at the front and open toward the user at the back. Four grey
  castors Ø100 with chrome plates, black caps on the open ends.
- Two telescopic posts on the arms at mid-depth: a cream outer tube with a collar, a lighter inner tube above, and a
  BLUE star knob on the outer side at ~70 % height.
- A cream cross tube under the rest, with black clamp blocks at its ends.
- The forearm rest is a periwinkle PU pad (#8e9fdc), 840 × 350 × 52, on a grey board, with a shallow notch at the back
  middle.
- Two black foam grips Ø36 × ~130 stand on chrome stems at the front edge (±215 from the centre), with black clamps
  and small knobs under the rest.

### xyf-z2 — walker with brakes and seat
- The Z1 frame, but the knobs are black and the pad is medium blue (#5d7ec8) with rounded lobed ends and a deeper notch.
- Black bicycle brake levers in front of the grips. Black cables loop down to the rear (open-end) castors.
- Seat sub-frame between the arms behind the posts: legs from the base arms, side bars, and two chrome width rods
  with black knobs at their ends. Blue seat 430 × 380 at ~630, with a blue backrest on a grey plate bracket at the
  open end.

### xyf-z3 — walker with wooden forearm rests
- Photo seen from the back-right (the user side). It was read with the grips and the closed end at the front, and the
  open runner ends at the back.
- White Ø25 floor runners joined at the front by a low cross tube. A mid-height U tube runs toward the front. Four
  small castors Ø75 with red hubs.
- Two main uprights: white outer tube, red-chrome inner tube above it, black star knob.
- Two front posts: white upper part, red lower leg with a black foot cap, clamped at the mid U.
- A white cross tube joins the rests.
- Two carved orange-varnished wooden rests (#dc9550) on white brackets. Each has a straight outer edge and an inner
  edge scooped toward the user, ~240 × 490 × 46. A black foam grip stands near the front end of each.

### xyf-z4 — walker + separate saddle unit
- Walker: steel-blue Ø25 tubes. Four legs with S-bent feet flared forward and backward. Side top rails with black
  knobs, side mid rails with white end caps, low side rails. An X brace across the front. Thin chrome telescopic rods
  beside the legs. Castors Ø75.
- The forearm rest is a lavender-blue horseshoe (#8592d0), closed at the front and open toward the user.
- Saddle unit (to the right, as on the photo): a smaller frame of the same tube with S-bent legs, a mid-height loop
  rail with two white hooks at its front, and castors Ø70. Four posts with chrome rods and black knobs carry an
  L-shaped padded saddle: the seat part is ~860 high and the back pad rises at the user side to ~1180.

### xyg-1 — parallel bars with correction board
- A walkway platform 3500 × 1160 × 50: grey vinyl top, beige-pink edge band, bevelled ramp ends 200 long, a small
  blue label on the front edge.
- Two light-blue Ø45 rails on four posts set 470 from the ends. Each post: white Ø60 tube on a round flange, chrome
  inner tube, black knob, and a chrome T-head saddle with an outward lever and black handle.
- Correction board: two wood layers with a wedge cross-section (higher toward the front rail). The upper layer is
  bevelled at its right end, ~2500 × 400 × ~90.

### xyg-2 — parallel bars
- Two dark-silver Ø40 rails with blue ball end caps. Each rail has two posts 420 from its ends: a white Ø50 outer
  tube, a chrome inner tube with ratchet holes, a black knob, and a saddle with a short outward arm ending in a blue
  ball.
- The posts of each end stand on one white floor plate across the walkway (250 × 1160 × 10, 4 bolts).

### xygs-1 — quadriceps board
- Base board 800 × 200 × 20 in light wood. The front section top is a cream laminate.
- A blue PU tent: a steep back panel hinged at the back end on a chrome piano hinge, and a long front panel (~60 thick)
  that rests on a wooden heel stop with a white top.
- 4 blue pegs in 2 rows in the cream section, and a clear round level at the front corner.

### xyh-1 — seated ankle exerciser
- A long white base beam (200 wide × 190 high) with a white pedestal (330 × 410 × 430) at the back.
- A white floor loop tube round the back.
- Seat frame: aluminium front bar with a blue label, chrome slide rods, rear bar.
- Grey padded seat on a white pan. A grey backrest in a white tube frame, tilted back 10°.
- Two chrome levers pivot at the ends of the front bar and lean ~33° toward the footplates, with black grips; top
  at 880.
- Black footplates with heel cups and outer walls, on chrome shafts at both sides of the beam's front end.

### xyh-2 — spring ankle exerciser
- Light-wood base plate 400 × 250 × 25 on 4 black feet.
- 4 chrome coil springs (Ø62, ~135 tall) carry two black footplates with raised outer toe lips. A black centre plate
  sits between the footplates.
- A navy U hinge block with a chrome bolt sits in the middle.
- A chrome Ø18 handspike rod rises behind the centre to 900, with a black ball knob Ø44.

### xyd-1 — electric standing frame
- Royal-blue square-tube base on 4 small black castors Ø50, with chrome outrigger rods and clamps along both sides.
- Uprights carry a mid frame at 620 (rear cross bars), with a black control box and a white roller on it.
- A black actuator under the blue central column. Twin chrome inner tubes carry the tray table.
- A blue knee pad ~310 × 350 sits on an arm in front of the column.
- Tray table in yellow wood, 760 × 590, at 1000–1026, with a front cut-out. A blue chest pad stands at the cut-out's
  inner edge, up to 1150.
- Side handles: blue tubes rise backward from the front base corners. Black foam covers the upper diagonal and the
  horizontal top, and the handles return down at the back.
- A chrome lever with a black grip at the back-left.
- Yellow wood footboard with a round cut-out at its right end and two heel hollows.
- Two chrome J hooks under the table's front corners. A red / yellow / green striped sling hangs between them, with
  one leg strap down to the footboard and one strap hanging straight.

## Final check and what is approximate
- **xyf-t1**: all items match at sheet scale. The rails are drawn at the photo's lowest setting (top 1340); size H
  stays the printed max 1550.
- **xyf-t2**: matches the parts list. The front flight's exact width and position on the photo (perspective,
  partly hidden) are approximated as the platform width, centred. Rails at 1340 as on the photo.
- **xyf-t3**: matches. The treads are thin folded plates. The photo's left flight looks closed, but it is drawn with
  open risers (the lips read as risers). Rails at 1340.
- **xyf-t4**: matches. The front box steps use rise 200 / depth 220 (estimated). Rails at 1340.
- **xyf-z1**: matches: U base, castors, blue knobs, notch, grips. The pad shape is a rounded rectangle with a notch.
- **xyf-z2**: matches. The brake levers are simple bent rods, and the cable routing is approximate.
- **xyf-z3**: approximate. The photo is busy and shot from the user's side. The tube routing (low and mid U tubes),
  the two red-legged front posts and the carved rest outlines are simplified. The red castor hubs are small discs.
- **xyf-z4**: **size changed to [1180, 800, 1300]**: the photo shows the walker (680 wide, printed) and the separate
  saddle unit side by side, and both are drawn. The saddle unit's size (~340 × 520 × 1180) is estimated from the
  photo.
- **xyg-1**: matches. Rails at 1000 (mid of 780–1200). The board's wedge angle and its two layers are estimated.
- **xyg-2**: matches. Rail spacing 640 is derived from the plate length (1160 = plate). Rails at 1000.
- **xygs-1**: matches. The tent is drawn at max height 310.
- **xyh-1**: matches. The lever-to-footplate linkage (hidden in the beam) is not drawn. The footplates are flat
  black trays.
- **xyh-2**: matches. Springs are 2 per plate (only the front ones are visible on the photo).
- **xyd-1**: approximate in the frame details (exact tube layout behind the knee pad, the ladder bars, the lever's
  mechanism). The sling stripes are red / yellow / green stacked straps, not the full multicolour weave. Table at
  1000 so that the chest pad tops out at the printed 1150.
