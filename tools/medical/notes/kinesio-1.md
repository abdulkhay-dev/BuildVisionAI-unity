# kinesio-1 — notes

Generators: `tools/medical/gen/k1_*.py` (+ `k1lib.py` helpers); each writes only its own devices' design files.
Frames as in Docs: x from the left seen from the front, z = depth at the front, y up. The renders' "angle" view is
front-left-above, "side" is from the left — the photos below are mostly taken from the front-left too.

## Parts lists (from the photos, written before drawing)

### xy-zbd-iiidl / -iidl / -idl — seatless upper/lower-limb cycle trainers (same body)
Photo analysis: camera ~50° front-left; patient sits at the crossbar end (front, +z) facing the column; the pedal
cradles' toes point to the rear; the screen faces the patient (in the p4 page photo, more frontal, it is face-on
while the pedal discs are oblique — so it faces front, not sideways). Width (x) = across the patient.
- Base: rear box foot ~400 (x) × 220 (z) × 150 high, white top, a light-grey (#9a9ea5) inset band round its sides,
  4 black levelling pads Ø50. Front crossbar: white rounded bar ~580 wide (x) × 100 × 110 high, two small chrome
  pins on top, black pads under the ends. A low white centre rail joins them (mostly hidden by the drum).
- Main column: white rounded rectangle ~170 × 120, rising from the rear foot and leaning ~28° toward the patient up to
  ~870; light-grey collar (telescopic joint) at the top; a short grey inner tube above it; vertical grey
  "Sunnyou 翔宇" lettering on its -x side.
- Head bracket: grey/chrome clamp block under the capsule, a black ball knob on its -x side, a black lever on the +x
  side, a small black L clamp under the capsule's front.
- Head: horizontal white capsule along z (~620 long, ~180 Ø) with the rear end rounded; on both sides near the rear end
  a silver oval boss (~110 × 80) from which a black grip Ø35 × 150 sticks out sideways (x); grey "Sunnyou" on the
  side; at the front end a white sphere Ø~260 with a grey disc + pink ring on both sides.
- Upper crank (iiidl, idl): white crank arm ~170 on the -x disc, pointing down, with a white boss and a black grip
  pointing -x; the opposite crank on +x points up, its black grip pointing +x (cranks at 180°).
  iidl: no crank, a straight black grip bar through the sphere's axis, sticking out both sides.
- Screen: landscape touch screen ~600 × 375 in a black bezel, on a short white round stalk on the capsule top, facing
  the patient (+z), tilted back ~10°; red e-stop mushroom on the capsule top behind-left of the stalk.
  iiidl: `med_xy-zbd-iiidl_screen`; iidl/idl: the same UI is shown in their photos but no screenCrop → dark screen.
- Lower drum: white thick ring/drum Ø~420, ~220 wide (x), centre y ~430, at z ~660; on both sides a recessed grey
  (#8f949b) disc Ø~320 with a thin magenta (#e0457b) ring.
- Pedals (iiidl, iidl): on both sides a white foot cradle (sole ~300 × 120 with a raised heel cup and low side walls,
  toes pointing to the rear) on a chrome crank plate; from the heel a white bent stalk rises to a white C-shaped calf
  shell (~150 wide, ~150 tall) with a chrome knob. Near (-x) pedal low-rear, far (+x) pedal high-front (180°).
  idl: no pedals, plain grey discs.

### xy-cpm-ia — wrist CPM (desk)
- White glossy box (long axis x, ~480 × 230 × 160), x=0 end = console end: top front-left with a grey-silver oval
  membrane panel (~190 × 120), green LCD ~80 × 35 at its top, 8 dark-blue oval keys; the end face carries a black
  power inlet and a grey DB9 plug (cable to the controller).
- Rear part (x ~230–480) one step lower (~120), a black slot with a chrome rod on its front face.
- Black nylon sling cradle (~260 × 170, folded straps) lying on the lower step between two chrome rails Ø18 running
  along x at ~220; black end caps at the rails' x-min ends.
- At the x-max end two chrome hub discs Ø80 × 50 on posts (front and back) with a blue logo on their -x faces;
  a chrome lever linkage (two flat links) on the front face from the slot up to the front hub, a chrome knob on the
  x-max end.
- Hand controller: white with a dark-blue face (~150 × 80 × 25, wavy edge, 3 white/red buttons) lying in front, on a
  black coiled cable from the DB9.

### xy-cpm-ib — finger CPM (desk)
- Chrome rectangular tube frame Ø20 (~450 × 400) lying flat on the table; black foam grip Ø35 with chrome ferrules on
  its front edge (left half).
- White glossy body ~200 (x) × 360 (z) × 210 on the right half of the frame, the front-top edge strongly rounded
  (r≈70); grey oval panel (~180 × 120, LCD + 8 blue keys) on the top near the front; on the front face: black power
  inlet, grey DB9 plug, green rocker switch.
- Black nylon forearm sling (~180 × 300) on a chrome bracket on the left half, at the back.
- Behind the body at the back-top: an aluminium motor cylinder Ø50 on a short post and a horizontal bar holding
  4 chrome finger clamps with rods ~120 pointing -x, a black clamp knob.
- White/blue hand controller on a coiled cable, lying in front-right.

### xy-cpm-ic — elbow CPM (desk unit; the stand of view 2 is a variant, not drawn)
- White glossy box ~260 (x) × 250 (z) × 210, r≈25; grey front membrane panel: LCD ~110 × 45, 4 + 2 dark-blue keys,
  green rocker switch; black power inlet + blue label on the +x side; grey DB9 plug on the top-back right.
- On top: two chrome brackets (flat plates) carrying the hinge, axis along z, near the -x end; two chrome hubs Ø55
  (front and back) with blue logo.
- Forearm cradle: two chrome rods Ø16 along +x from the hinge over the box (~330), black nylon sling ~300 × 180
  with straps, rods' end caps black.
- Upper-arm frame: two chrome rods Ø14 rising from the hinge toward -x at ~45° (~460 long) with a black sling
  (~250 × 170) and an adjustable chrome end clamp (U frame with a rectangular plate), black star knob.
- White/blue hand controller on a coiled cable in front-right.

### xy-cpm-id — shoulder + elbow CPM on a mobile stand
- Black 5-star base Ø~620 (flat tapered arms) with 5 black twin castors Ø60; black lower column Ø60 to ~640; chrome
  collar; chrome upper tube Ø45 to the box.
- White glossy box ~320 × 240 × 230 at y 860–1090 (r≈25); grey LCD window ~100 × 70 on the front face; red e-stop on
  top; black coiled cable hanging from the -x side.
- -x side: chrome rod frame rising above the box (~to 1300) with a black square pad (~150 × 140) and two black
  knobs; below it a black forearm rest (~220 × 130) sticking out at ~960 with a white/blue hand controller on it.
- +x side: vertical chrome rod ~620 long (y ~900–1520) on a black joint block with knob, carrying two black C-shaped
  cuffs (~130 wide) at ~1300 and ~1100 with red adjustment knobs; thin chrome tip above.

### xy-cpm-iib — lower-limb CPM (bed unit), long axis = x, console at x=0
- Long white glossy base (~1000 × 260 × 150), rounded top edges, a black slot (~650) on the front face, a few screws.
- Console block at x 40–330 rising to ~270, top sloping; grey membrane panel (~210 × 140) tilted on it: green LCD,
  7 dark-blue keys, green rocker switch; black power inlet on the x=0 end; grey DB9 plug on the front.
- Foot carriage: dark-grey (#4a4f57) U bracket at x ~280–420, ~300 high, on flat steel links; upright black padded
  foot plate ~200 × 330 with a strap, slightly tilted.
- Leg frame: chrome rails Ø20 both sides: calf section x ~430–860, knee hubs Ø60 (blue logo caps) at x ~430 and 860,
  thigh section to the hip end x ~1050 where the rails bend down into the base end; flat steel links (#9aa0a6) from
  the base up to the hubs; black nylon cradles (calf ~380, thigh ~300) with straps between the rails.
- Low chrome rod frame along both long sides at ~40, black clamps; at x=0 a transverse black foam roller Ø40 with two
  cream nylon wheels Ø70.
- White/blue hand controller on a coiled cable in front.

### xy-ct-iv / xy-ct-iii — round ADL training table (iv with the screen tower)
- Graphite (#5a5f66) 3-arm star base (arms ~420 to the castor centre, ~150 wide, ~100 thick, rounded), arms at
  front-left, front-right and back; 3 grey-white twin castors Ø60.
- Light-grey (#c8ccd2) square column ~160 × 150 with vertical groove lines, up to the table; a black motor box
  under the table right of the column.
- Light-grey (#bfc3c8) skirt plate Ø~1150, ~30 thick, protruding ~40 beyond the shell; small black/red e-stop boxes
  and yellow labels under/at its edge left and right.
- White glossy domed shell Ø~1100 at the skirt, ~300 tall, large rounded shoulder to a flat top; 3 large arched
  openings (~500 W × 250 H, rounded top corners r~90) at the front and at ±120°; dark-grey interior.
- Through the front opening: (iv) a white steering wheel on a grey box, a grey box with a dark face and a chrome
  lever handle, a low white box with a screw clamp; (iii) a grey box with the 4-colour arrow pad, a white box.
- Top: a grey ring Ø~700 (band ~25); (iii) a large grey Xiangyu cross logo inside it.
- (iv) Screen tower: white post ~240 × 160 rising ~140 above the top, a white bezel head ~320 × 240 × 70 with a 12"
  landscape screen (no screenCrop → dark), two grey (#8a8d93) side wings angled back.

### xy-k-czld-vii — sonic vibration walkway with parallel bars (long axis = x)
- White walkway platform ~2400 × 800, ~150 high, light-blue (#8fb6d8) walking surface with white footprints, white
  border ~60 with ruler ticks; sloped ramps ~600 at both ends (blue top, white sides, tick marks on the edges).
- A recessed darker plinth under the platform's middle (shadow gap, a motor box visible).
- Near side (front): single light-blue rail Ø40, ~2700 long, rounded ends, on 2 white square posts 80 × 80 with a
  light-blue inlay on their outer face, T head: a short horizontal light-blue stub + chrome joint + vertical stem.
- Far side: the rail is a closed loop (two parallel tubes ~100 apart joined by U-bends at both ends) on 2 posts.
- Console column on the near side at x ~1050, standing on the floor in front of the platform edge: white
  ~200 × 160 × 1200 with a full-height light-blue inlay on its front, round "S" logo near the bottom, sloped top with
  a dark screen in a white bezel.

### xy-k-g1 — manual BWS gait frame (printed 1200 × 1090 × 1800)
- Cream (#efe9d6) steel tube frame Ø40. Two straight floor legs along z at both sides with grey castors Ø75 (brakes)
  at both ends; from a raised hub at the back centre two parallel curved tubes sweep down to each leg's rear part.
- Rear column: cream rectangular outer tube ~70 × 70 from the hub up to ~1250, inner tube above (telescopic, black
  pin/clamp), top bending forward (r~120) into a short horizontal arm.
- Top bar: black foam bar Ø50 ~520 wide across x with chrome end caps and a blue label; two chrome hooks/rings hang
  the harness.
- Handrails: a chrome crossbar through the column at ~850, black foam handles Ø40 ~300 long pointing forward at its
  ends.
- Black harness: two shoulder straps from the hooks, crossed back strap, a padded black vest (chest belt) with
  brown-grey mesh sides and blue tabs, chrome buckles, two leg loops below.

### gait-obstacle-treadmill — rehab treadmill with handrails and obstacle boards (long axis = z, console at z=0)
- Deck: grey (#8f949a) side frames ~90 × 110 along both sides, black belt ~560 wide, black end caps, black round feet.
- Console end: a low dark-grey motor hood; a curved chrome U bar rising from the rails' front ends to the console.
- Console: light-grey box ~380 × 220 × 60 tilted toward the user, LCD with blue segments, red/green buttons.
- Handrails: grey square posts 50 × 50 at 3 positions each side (console end, middle, tail) with black clamp knobs;
  grey round rails Ø40 at ~950 along both sides; at the tail end the rails bend down and outward.
- Obstacle boards: two white boards ~1500 × 140 × 30 standing on edge lengthwise on the belt (lanes), fruit pictures
  (red apples, yellow, green) on the near one.
- Striped panel: grey frame on the far side hanging from the far rail, red / green / white horizontal stripes.

### upright-exercise-bike — upright bike (front = handlebar end, z = depth)
- Silver-grey (#b8bcc2) flywheel housing ~420 long × 420 tall, rounded, in the lower middle; black pedal cranks and
  black pedals with straps on both sides.
- Black stabilizer feet (~500 wide) front and rear with round levelling caps.
- Black front stem from the housing up to ~1050, a black curved handlebar (horns rising forward to ~1300) and a small
  black console.
- Black seat post leaning back from the housing to a black saddle at ~900.

## Engine / frame notes
- The renders' "angle" view is the item's front-left = design front **right** (+x side), and "side" looks from +x
  (front on the left). Most catalogue photos are from the design front-left, so the angle render looks mirrored
  against the photo; the geometry follows the photo's sides (cranks, inlets, controls).
- `ring_disc` (k1lib): pink/grey drum faces are two stacked thin lathes; the face disc must sit outward of the ring
  (`out=-1` on the -x side).
- A lathe ring (profile not touching the axis) needs `caps: false`, otherwise the caps fill a disc (radial streaks).
- The CT shell is built from 3 wall sectors (`slab` top, polyline arcs) + a lathe lid; opening corners are `slab`
  fillets turned with `rot y`. Inner drum must stay small (r 300) or it swallows the modules.

## Final check (compare sheets) and what is approximate
- **xy-zbd-iiidl** — done; screen with `med_xy-zbd-iiidl_screen`. Matches: rear box foot with grey band (z-elongated),
  front crossbar with pins, column lean ~28° with grey collar, capsule + sphere, silver bosses with black grips,
  cranks at 180°, drum with grey disc + pink ring, pedal cradles + calf shells, e-stop. Approximate: pedal cradle /
  calf shell shapes simplified; the "90°/45°" scale marks and the chrome slotted crank plates are plain bars.
  Screen faces the patient (front); the photo render shows it at ~50° — p4 page photo confirms it faces front.
- **xy-zbd-iidl** — done; as iiidl with a straight black grip bar through the sphere, no rear grips (white knobs in the
  silver bosses). Dark screen (no screenCrop; the photo shows the same UI as iiidl).
- **xy-zbd-idl** — done; crank, no pedals, plain grey discs with pink rings. Dark screen (no screenCrop).
- **xy-cpm-ia** — done. Size D 300 → 380 to hold the hand controller lying in front (box itself 240 deep).
  Approximate: the folded nylon sling is two puffy boxes + one strap; lever linkage simplified to two flat links.
- **xy-cpm-ib** — done. Size [450, 420, 300] → [450, 490, 320]: controller in front, finger motor on its post reaches
  ~315. Finger clamps: 4 chrome blocks with rods pointing forward over the sling (read from the photo).
- **xy-cpm-ic** — done (desk unit; the mobile stand of view 2 is a variant, not drawn). Size [400, 600, 560] →
  [660, 380, 620]: the photo shows the hinge axis along z with the forearm cradle across the box (+x) and the
  upper-arm frame rising toward -x at 45°, so the long dimension is the width, not the depth.
- **xy-cpm-id** — done. Arm rod tilted 5° outward as in the photo; C cuffs open forward-right. Approximate: the small
  photo (~220 px) — knob counts and the pad frame shape are guesses.
- **xy-cpm-iib** — done. Size [1060, 380, 500] → [1060, 480, 560] (controller in front; foot plate top ~560).
  The photo puts the console and foot plate at the same (x=0) end and the hip end at x max (the inventory text says
  "console at the hip end" — the photo wins). Thigh section shortened to fit 1060 (photo cradle runs a bit past).
- **xy-ct-iv** — done. Size H 1400 → 1215: with the table Ø1100 the photo gives table top ~840 and the screen head
  top ~1215. 3 arched openings (front, ±120°) between the 3 base arms (the front photo shows no side openings).
  Dark screen (no screenCrop). Approximate: the shell wall is vertical (photo flares slightly), modules simplified.
- **xy-ct-iii** — done. Size H 950 → 845 (same table, no tower); grey ring + inner ring + grey cross logo on top,
  4-colour arrow module in the front opening.
- **xy-k-czld-vii** — done. Size H 1460 → 1210: rails drawn at the lowest printed armrest height 1050 (range
  1050–1460), console column top 1200. Approximate: footprints are ellipses + toe ellipse; the far "loop" rail read
  from the photo as two tubes 100 apart joined by U-bends; post T-heads simplified.
- **xy-k-g1** — done (printed size kept). Approximate: harness simplified (vest, mesh side panels, crossed strap,
  blue tabs, leg loops with pads); in the photo the top bar sits slightly to one side of the column top, drawn centred.
- **gait-obstacle-treadmill** — done (size kept). Low-res photo: console graphics, post count (3 per side) and the
  striped panel's exact mounting are approximate; fruit pictures are coloured discs on the near board.
- **upright-exercise-bike** — done (size kept). Generic bike; the photo is mostly hidden by a harness (not drawn — it
  belongs to the M2 frame). Housing slightly deeper than in the photo.
