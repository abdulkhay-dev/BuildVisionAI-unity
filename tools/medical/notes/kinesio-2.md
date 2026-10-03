# Batch kinesio-2 — 14 devices (2026-10-02)

Designs: `Assets/House4696/Resources/Medical/Designs/<id>.json`. Generators: `tools/medical/gen/k2_*.py` (shared helpers in
`k2lib.py`). Each generator writes only this batch's ids:
- `k2_cart.py`: interactive-training-cart
- `k2_qjhd.py`: xy-qjhd-bh, xy-qjhd-bv
- `k2_phws.py`: xy-ph-workstation
- `k2_ph.py`: xy-ph-v, xy-ph-iv
- `k2_dgdx.py`: xy-dgdx-i
- `k2_zbd.py`: xy-zbd-id, xy-zbd-iid, xy-zbd-iiid
- `k2_zbd2.py`: xy-zbd-ib, xy-zbd-iie
- `k2_cross.py`: xy-szld-ia, recumbent-cross-trainer-interactive

All 14 render `ok`. Every device went through 2–3 rounds of render, `compare.py` and fix.

## interactive-training-cart
Parts from the photo:
- **Base:** a white flat rectangular frame (~950 × 600) on 4 grey Ø75 castors.
- **Cabinet:** 650 wide.
  - Both side panels are frames with a diagonal strut, running from top-back to bottom-front.
  - The left half has open shelves (2 shelves plus the bottom).
  - The right half is a closed white PC box. Its front has a black window with a red LED and a port.
- **Top deck:** a lectern-shaped deck (flat back, sloping front) with the blue Xiangyu logo on its left face.
- **Keyboard tray:** pulled out in front, carrying a black keyboard. It runs out to the right for a black mouse pad
  and mouse.
- **Upright:** one white upright (200 × 80) at the back of the deck, with a steel TV mount.
- **TV:** 55" (1230 × 710), thin black bezel, showing the menu picture.

Final check:
- The cabinet top was lowered to 720–810, from the photo's proportions.
- TV bottom at 1070, TV top at 1795.

Approximate:
- The screen crop is a perspective photo of the TV, so the picture is skewed. Everything outside the TV's outline in
  the crop is masked with a bezel-black slab (quad hole). The picture therefore reads as a slightly trapezoid image
  inside a black rectangle.

## xy-qjhd-bh / xy-qjhd-bv
Parts from the photos:
- **Base:** a graphite X base with long legs (to ±545 / ±300), round leg caps and light-grey Ø75 castors.
- **Cabinet:** a white column cabinet with a door seam.
  - The blue logo sits at its upper left.
  - The right side has a dark grip slot by the front edge and a white hook bracket.
- **Camera band:** a dark band on top of the cabinet with the depth-camera window.
- **Foot tray:** a white tray in front of the cabinet foot.
- **BH:** a landscape 55" display (1240 × 720) sitting on the band, bottom at 1080.
- **BV:** a portrait display, bottom at 730 and top at 2000, on a shorter cabinet (top at 640). On the right is an
  operator station:
  - a white arm from behind the display,
  - a ~15" monitor with a light UI,
  - a black V bracket,
  - a black keyboard tray with a keyboard below it.

Final check: the cabinet was narrowed to 540. The inventory guessed 450 and the first version used 600; 540 matches
the photo's display/cabinet ratio. The cabinet is 260 deep.

Screens:
- **BH:** the crop's outer 7 px (white corners and a green rim line) are under a dark frame slab.
- **BV:** the crop has its own left, top and right bezel but no bottom one. The model adds:
  - a bottom bezel strip,
  - masks over the top 14 px (white corner),
  - a mask over the right 8 px (the display's side face).

  The side monitor in the crop's lower right is covered by the modelled operator monitor.

Approximate: the operator monitor's UI is decals; the photo's monitor is turned slightly to the left, the model's
is not.

## xy-ph-workstation
**Size changed** to [900, 720, 1700] (inventory [600, 600, 1700], which was an estimate for a 24" monitor). The photo
shows a ~40" TV:
- The monitor is ~2× the keyboard width.
- Its height (~520) matches a 16:9 panel ~880 wide.

The base span is ~0.7 m.

Parts from the photo:
- **Base:** a silver 5-arm star base (arms sloping to the castors, conical hub) on 5 light Ø75 castors.
- **Pole:** a flat oval silver pole (120 × 70) with a groove.
- **Shelves:** two dark teal glass shelves on silver brackets, with alu front edges.
  - Upper shelf at 815, carrying the keyboard and mouse.
  - Lower shelf at 555, carrying a white laser printer (vents, paper slot).
- **Monitor mount:** a black VESA bracket with two clamp knobs.
- **Monitor:** 890 × 550 with a black bezel.

Approximate:
- There is no screenCrop, so the lit blue software screen is decals: a title bar, a white tree panel, a form with
  fields, a taskbar.
- The glass is an opaque teal gloss: the acrylic material rendered almost white.

## xy-ph-v (standing balance)
**Size:** D is 830 (inventory 900, an estimate): the plinth is 800 deep.

Parts from the photo:
- **Plinth:** a light-grey rounded plinth (800 × 800) on 4 levelling feet, slightly darker skirt.
  - The front-right corner has a dark grip.
  - The blue logo is on the top, near the right.
- **Rear rail:** a dark graphite rail along the rear edge carrying both posts.
- **Platform:** a round grey platform (Ø ~550, top at 247) on a dark two-tier pivot housing with a black label.
- **Posts:** two posts at the rear corners. Each has:
  - a white lower tube (to 600),
  - a black collar,
  - a steel inner tube with a black slot and white holes,
  - a tall dark-grey head block (980–1290).
- **Knobs:** a black knob on the outer side of each post.
- **Handrails:** C-shaped handrail loops pointing forward (Ø36 white bends, dark grey grips on the top bar).
- **Top crossbar:** a white crossbar between the heads.

Final check: the post proportions were re-measured (white : inner : head ≈ 410 : 330 : 310). The loops were
shortened to 280 and 180 high. A stray square decal on the platform and the harness block were removed.

Approximate: the platform's dot texture is omitted.

## xy-ph-iv (seated balance)
Parts from the photo:
- **Base:** a light base plate with rounded front lobes on 4 feet, with a small logo.
- **Column:** a central grey square column (150).
- **Seat:** a chrome bearing, a black bowl, a black rounded-square seat plate (500 × 470) and a light grey textured
  disc (Ø 380, top ~572).
- **Back frame:** a rear C-frame in the column colour. It branches off the column at ~300, runs back, slants up and
  then goes vertical to the backrest.
- **Backrest:** black upholstered (350 × 270, top 1050), on a chrome mount.
- **Armrests:** a chrome U tube behind the backrest at 750, its ends running forward as black foam armrests (to
  z 600).

Final check: the C-frame start was raised from the floor to 300 (photo). The bowl was made narrower.

Approximate: the speckled seat texture is a plain light-grey disc.

## xy-dgdx-i (isokinetic dynamometer)
Front = the column's logo face. The output shaft is on the right (+x) side and the grab handle on the left, as in
the main photo. Photo 3 shows the mirror image and is treated as a mirrored marketing view.

Parts:
- **Base:** a 4-lobe base with concave sides, a white top skin (to 182) over a dark grey trim. Ø60 castors.
- **Column:** a white rounded column (240 × 290) with a thin red line by its front-left edge. A round red S logo, a
  red name and a grey sub-line sit on the front.
- **Head:** a big rounded head (460 × 380 × 305) overhanging to the right, with a round cup on its top.
- **Output face:**
  - a light grey recessed panel,
  - a cyan rounded frame,
  - a black ring with a white inner disc,
  - a chrome shaft.
- **Steering wheel:** Ø 336, black rim, 3 spokes (left, right, down), black hub, light rim marks.
- **Grab handle:** a grey vertical loop on the left side, with a red disc logo at its root.
- **Pole and monitor arm:** a chrome pole at the back of the head (to 1296) with a black collar and lever. The
  articulated arm is white on top and black underneath, with a black joint and a tilt head.
- **Screen:** a 15.6" white-bezel touch screen (390 × 250), top at 1650, turned 22° to the front-right.

Final check:
- The base was made thicker.
- The column was narrowed from 270 to 240.
- The handle changed from a horizontal to a vertical loop (photos 1 and 3).

Approximate: there is no screenCrop, so the white UI with blue tiles is decals. The "Sunnyou 翔宇" text is plates.

## xy-zbd-ib (upper limb, rotary disc)
Orientation: the front is the face with the grab handle and the e-stop. The photo is taken from the front-right; the
rails run along x and the crossbar along z.

Parts:
- **Base:** a light-blue H base (2 rails 700 long with chrome brake rods, a crossbar). Braked Ø75 castors with brake
  pedals, 4 levelling feet with black pads, a chrome footrest loop to the left.
- **Column:** a blue square column (100) with 2 black star knobs on its front.
- **Hinge:** a steel telescopic section, a black hinge bracket with steel plates, and a gas spring on the right.
- **Head:** peanut-shaped.
  - The left box part (370 × 340) reaches lower, to 680.
  - The right round part is Ø400 with a seam line.
- **Front details:** a black grab handle on the front-left and a red e-stop.
- **Turntable:** a black turntable (Ø300) with a chrome hub and carrier plate. A black bracket carries 3 black
  vertical grips (Ø42 × 155) and one horizontal roller.
- **Screen:** a white square screen box on a neck at the rear-left, tilted back 14°, dark screen (no crop).

Approximate: the hinge and gas-spring mechanism is simplified. The grip-bracket layout is read from one photo.

## xy-zbd-id (arm ergometer)
**Size changed** D 650 → 900. Measured on the photo with the crank disc Ø230 as scale:
- the disc centre is ~480 in front of the column foot,
- the white foot cowl (~320 long) lies behind the column foot.

Orientation: the patient is at the front (z = depth), where the wheel tube is. The white cowl foot lies along z at the
back. The column leans ~20° towards the patient. The photo is a view of the right side.

Parts:
- **Base:** a white loaf cowl (250 wide, 230 high) on a navy plate. A wide navy beam rises from the front tube to
  the column foot. The front tube is Ø40 with grey Ø66 wheels and white hubs.
- **Column:** a navy column (90 × 62) with screws. A white telescopic section with a black clamp knob, a steel joint
  and a big black joint knob on the right.
- **Head:** a white head body with navy side panels; the white "XIANGYU MEDICAL" text is a bar.
- **Crank disc:** Ø230 at the front, with blue rings and white faces. Silver crank discs and arms. Black foam handles
  point outward: the left crank is up and the right one down, as in the photo.
- **Rear handle:** a black U handle behind the head.
- **Screen:** a white screen box (240 × 225) on a neck, top at 1390.

Approximate: the screen is swivelled 55° towards +x. The photo shows it turned to the camera; it swivels 0–180°. Its
face is a pale lit decal.

## xy-zbd-iid (leg trainer)
Orientation and base: the same scheme as ID (patient and wheel tube at the front, white loaf cowl along z at the
back).

Parts:
- **Drum:** a big white drum (Ø360 × 124, centre at 375 high). Navy hub plates and two flat navy spider arms per side
  join the curved navy column behind the drum.
- **Pedals:** navy crank arms. Each pedal is a white calf shell open to the back, with 2 black Velcro straps, a black
  foot cup, a heel and a foot strap.
- **Column top:** a white telescopic part with a black clamp knob and a black head knob.
- **Handle head:** a white handle head (300 wide) with a navy inset. Two black horn handlebars reach forward to the
  patient (as in the photo, not a closed U).
- **Screen:** a white screen box, top at 1150, swivelled 55°.

Approximate: the photo's curved blue spider plate around the drum centre is two flat arms. The drum's dots are a few
decals.

## xy-zbd-iiid (arms and legs)
Orientation: in the photo the roller tube is towards the patient (the inventory's "rear tube" is the front).

Parts:
- **Base:** a dark-navy T beam, a front tube with cream rollers, and a rear blue foot tube with rubber pads. The rear
  foot is hidden in the photo and added for stability; it is approximate.
- **Lower column:** a curved navy column behind the leg drum, with a black joint block and big black star knobs.
- **Leg drum:** white, Ø330 × 130, with blue rings and a yellow warning label.
- **Pedals:** calf shells with straps and foot cups.
- **Arm housing:** white, 130 × 120, sloping down to the patient, with a blue band on its sides.
- **Arm crank drum:** Ø220 × 170, with blue rings, silver discs and arms, and black foam handles (left up, right
  down).
- **Rear handle:** a black U handlebar around the rear of the housing.
- **Screen:** a white screen box (280 × 230) with a yellow label strip, on a white post, top at 1290.

## xy-zbd-iie (bedside, inclined boom)
Parts:
- **Base:** a white chamfered housing at the back, on two flat blue legs, with Ø60 castors front and rear.
- **Column:** blue lower part (to 770), a blue collar, a chrome telescopic part and a blue top block.
- **Bed-docking support:** a blue bar along z with 2 black star knobs and a black trough saddle under it. A black U
  handle sits at its rear end, as in the photo.
- **Boom:** a long blue boom (100 × 84) sloping down ~25° towards the bed, with white logo plates. A chrome inner
  section and a blue end block follow it.
- **Crank and feet:** a chrome crank hub with blue crank links and white foot shells (lofts with domed toes), black
  pads and straps.
- **Pendulum:** a narrow blue rod runs forward-up to a chrome pendulum hub with two knobs. Black rods hang from it to
  two black knee cups with blue frames and knobs: one leg is forward and one back. A blue link runs down to a front
  white foot plate.
- **Screen:** a white swivel screen on the column top.

Approximate: the pendulum and crank linkage is simplified (the photo shows it at one phase only).

## xy-szld-ia (recumbent cross trainer, printed size)
Parts from the photo:
- **Base shell:** a long rounded warm-grey shell (420 wide, top 470 under the seat, sloping to a low nose at
  z 1250).
- **Shell sides:** both sides have an embossed cross logo, a dark slot and a black star knob.
- **Rear wheels:** two Ø90 wheels with cream tyres.
- **Seat:** black slide rails and seat post. A black tractor seat (cushion 440 × 435, backrest 450 high tilted 14°,
  seams), black hinge brackets with chrome knobs.
- **Seat handles:** lime-green U handles beside the seat.
- **Frame arcs:** two white square-tube arcs (70 × 70) that:
  - start on the floor in front,
  - rise forward,
  - curve back over to the console,
  - join at the floor through a front foot bar with pads.
- **Console:** a black oval face on a white back shell, tilted 50° to the user.
- **Levers:** two white swing levers pivoting low at the shell nose, ±10° out of phase, with black vertical grips
  (top at 1150).
- **Pedals:** black pedal plates with heel cups and toe straps on steel links.
- **Gas springs:** black bodies with chrome rods.

Approximate:
- The pedal and lever linkage is simplified to a pivot at the nose.
- The arcs are symmetric; in the photo the far arc is slightly further forward.

## recumbent-cross-trainer-interactive
Parts from the photos:
- **Base shell:** a long glossy white shell (top 560) on a dark graphite plinth band.
  - A low white front foot with its own plinth carries the steel pivot hub.
  - Both sides have a dark grip recess, a row of blue LED dots on a dark line, and a blue logo.
- **Rear:** a rear wheel (Ø110) and a black stabiliser bracket with a chrome leg and foot.
- **Seat:** a black slide base and an automotive seat (cushion 500, side bolsters, backrest 560 high with seam). Two
  black armrests with orange reflectors on top and outside.
- **Arcs:** asymmetric, as in photo 2.
  - The right arc rises from the shell nose.
  - The left arc has a long foot on the floor in front.
  - Both curve back to the console.
- **Console:** a black face, a white back shell and a black bracket with the wire hook.
- **Levers, pedals, gas springs:** as on SZLD-IA, with grips to 1200.

Approximate: same linkage simplification as SZLD-IA. The seat swivel/slide details and the reflector shapes are
plates.
