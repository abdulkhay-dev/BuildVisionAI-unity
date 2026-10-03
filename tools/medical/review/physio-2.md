# physio-2: detail review against the catalogue photos

All 14 devices were re-rendered after the fixes. Each `.txt` is `ok` and newer than its json. The generators in
`tools/medical/gen/` were edited and re-run: `hyjcart.py`, `hyj_*.py`, and one script per device. Compare sheets:
`tools/medical/renders/<id>-compare.png`.

## Shared HYJ cart (hyjcart.py → hyj-ii-enhanced, hyj-iii, hyj-iv)
Differences found:
- **Base.** The model had a flat rectangular plate with four thin grey bars and round caps. The photo has one sculpted
  X plate: a white top skin over a grey body, concave sides, and round lobes over the castors.
- **Castors.** The model had Ø75 wheels; the photo has Ø100 wheels with grey tyres.
- **Head panel.** The model's glass was near-black with red digit windows. The photo has dark-grey glass, dark digit
  windows, and a white outline frame round the button field.
- **Arms.** The upper segment was light grey with a hairline groove. The photo's upper segment is darker grey with a
  long black slot.
- **Rectangular radiator logo.** The model had a light disc with a dark bar. The photo has a dark-grey disc with a
  white "+".
- **Drum radiator.** The model had an extra grey ring on the face. The photo has a plain white face and a dark boss
  with a white "+".
- **Xiangyu logo on the column (iv).** The model had a bright blue dot. The photo has a slate-grey cross icon and
  blue-grey text.
- **Sunnyou lettering (iii, enh).** It was too small.
- **Drum face (iv).** It was turned 40° away from the camera. In the photo it faces front-left, so the turn is now 15°.

All of these are fixed. The base is now a `slab` top plane with Q-curve concave sides, and the castors are Ø100 grey.

## hyj-i
- **Arm too tall.** In the photo the device is ~3.6 box heights tall; the model was 4.5. The size H is now 720
  (it was 820, an estimate). The pole is re-proportioned as in the photo: a black base, chrome damper rods below,
  black damper bodies above, a clamp at ~400, then a bare chrome pole up to the black elbow at ~500.
- **Radiator cup too big.** It is now Ø125 × 140 (it was Ø160 × 180), with a grey knurled ring at its back.
- **LED windows.** They were red blocks; the photo has black windows with red digits.
- **Buttons.** The blue buttons were too small; they are now 22 mm squares.

## hyj-ii
- **Body structure wrong.** The photo has a white centre block (front and head) between two royal-blue side blocks
  whose tops sit ~60 mm lower. The model had blue panels up to the head and a head spanning the full width. Now:
  blue blocks reach 770, the white block is 318 wide, and a white fairing runs from the head over the right blue
  block.
- **Arm mount.** The model had a white block on the head. The photo has a blue post rising from the right blue
  block, with a black clamp and a chrome joint.
- **Sleeve.** The silver sleeve was in the middle of the arm; the photo has it on the lower half, with black end rings.
- **Radiator.** It tilted 20° down and was too big. It now tilts 10° up (left end higher, as in the photo) and is
  Ø135 × 185.
- **Castors.** They were light Ø60; they are now dark Ø68.
- **Cable.** It looped away from the arm; now it runs alongside the arm. The logo icon also gained its horizontal bar.
- **Panel.** It gained the grey title band at the rear.
- Kept: the photo is mirrored (as in the notes), and it is drawn as the photo shows it.

## xy-wb-ei
- **Base.** The model had two crossbars and a centre spine. The photo has a rectangular frame (front bar plus side
  bars) on 4 castors.
- **Tower depth.** It was too deep. In both photos the side face is much narrower than the front, so the tower is now
  420 deep (it was 500). The boom moved back with it.
- **Black vent strip.** It was too short; it now reaches ~745, about 2/3 of the tower.
- **Arch radiator.** It was too light; it is now darker grey #b4b9bf.
- Cannot match: the screenCrop is a photo that includes the bezel and a hand, so the screen shows that picture,
  not a clean blue UI.

## xy-jgc-iii
- **E-stop.** It had a yellow ring; the main photo has a grey one.
- **Side holder knobs.** They pointed sideways. In the photo they face front, so the knob is now on the holder's
  front face and the holder is moved forward.
- **C handle.** It was chrome; the photo's is satin aluminium (`metal`).
- **Castors.** They were light Ø75; they are now dark-tyred Ø100.
- **Paddle head.** It was too big (190 × 256 oval). It is now 144 × 216 and has the tapered neck down into the
  ferrule.

## sd-pdc-2
- **Decorative grooves on the side panels.** They were wrong. They are now the photo's three grooves:
  - A: a long diagonal from under the armrest down-back to the rear bottom.
  - B: horizontal from the front at ~355, then curving down-back.
  - C: horizontal from the front at ~160, then down to the floor.
- **Control panel.** It was too far forward and too high. It is now at z 500–645 and y 470–550 (front third, under
  the armrest).
- **Logo.** It was moved forward and enlarged.

## xy-lrf-i
- **Screen.** The picture was inset inside a 34 mm drawn bezel, giving a double bezel with a white photo margin.
  The bezel is now 3 mm, so the crop's own black bezel is the tablet bezel.
- **Cabinet colour.** It looked grey; it is now glossy white.
- **Castors.** They were Ø75; they are now Ø90, and the frame was raised to suit.
- **Hose port.** It had two chrome pins sticking out. The photo has one horizontal chrome coupling lying in the dark
  port, plus a dark socket hole.
- **Deck top.** It is now a grey metal skin.
- **Missing part.** The small dark switch on the right rear edge was added.
- Cannot match: the screenCrop includes a white background and a silver deck at its corners, and these show at the
  tablet corners.

## xy-k-zpjz-ii
- **Screen head.** It was too narrow (336 wide). It is now 380, as wide as the cabinet, with a bigger 300 × 160 screen.
- **Deck.** It was a thin 26 mm plate; it is now a 50 mm metal-grey deck. The green LED is on its front face.
- **Castors.** They were Ø60; they are now Ø75.
- **Spine board.** It was too tall: in the photo its top is at ~3/4 of the cart height, but the model's was nearly at
  the cart top. The board is now 770 long (it was 950, an estimate), and the stand is shorter.
- **Electrode pads.** They were a regular grid. They are now rib-shaped: a narrow spine column, with two lateral
  pads each side sloping down-outward, more steeply in the shoulder rows. All pads are one multi-subpath `slab`.
- **Mat outline.** It now has the arched shoulder top and a wavy bottom edge.
- Cannot match: there is no screenCrop, so the screen is dark.

## xy-k-gr-bii
- **Plinth.** It was a puffy pillow (r 48 on all edges). The photo has a crisp flat-topped black tray: a `slab` with
  plan corners r 75, edges r 10, and a recessed lower skirt.
- **Castors.** They were Ø75; they are now Ø100 twin wheels.
- **Output strip.** It had 6 knobs; the photo has 8 (yellow, 3 blue | 3 blue, yellow), with chrome skirts. The strip
  was beige; it is now light grey.
- **Membrane panel.** It was too white; it is now mid grey.
- Left approximate: the body's slight S-contour on the side.

## rh-jpsj-b
- **Base.** The model had a flared full plinth. The photo has four white flat feet flaring out from the body corners
  to round caps over the castors, and the body goes down to ~100. Now drawn that way.
- **Castors.** Each pair had one light wheel and one dark wheel; now both are dark.
- **Drawers.** They covered only 3/4 of the width; in the photo they span the full width.
- **Door panel.** The large outline with rounded bottom corners was missing; it is now added.
- **Head.** It was barely wider than the cabinet; it is now ~30 mm wider each side.
- **Basket.** It was a solid block with a lid-like inset. It is now an open flared tray (4 tilted walls and a bottom).
- **Logo.** It is now an oval badge.
- **Side marks.** They were moved up to ~370.

## xy-k-gr-ai
- **Front frame.** It was vertical. In the photo the deep front frame leans back (top flush with the body, bottom
  protruding, chin undercut). The whole frame, panel and socket slot now lean 10° about the frame's bottom back
  edge, the panel 18°. The body is shortened and a filler wedge closes the side gap.

## xy-k-gr-ci
- **Socket plates.** They were solid black. The photo has black outlines with blue inside and sockets in chrome rings.
- **Vacuum-cup holder.** The model had three thin curved straps. The photo has one flat stainless fork plate with
  5 tines pointing up and out, rising from the steel side. Size W is now 550 (it was 470) to hold it.
- **Steel side panel.** It was a low plate that left the blue support wedge exposed on the right. It now rises to
  cover the wedge, as in the photo.
