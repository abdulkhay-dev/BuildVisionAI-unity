# physio-5: detail review against the catalogue photos

Reviewed: all 11 devices. Every `.txt` is `ok` and newer than its json. Fixes were made in the generators
(`tools/medical/gen/p5_*.py`), which were then re-run. Compare sheets are at `tools/medical/renders/<id>-compare.png`.
Scratch files are in `tools/medical/scratch/physio5-review/`; `run.sh` there regenerates a design, waits for the
render and builds the compare sheet.

Measurements were taken on the photos in pixels, scaled by a known part (grip Ø, screen, module width).

## Size changes

Four sizes changed. All were estimates that the photos contradict.

| device | before | after | reason |
|---|---|---|---|
| xy-k-wic-2 | H 250 | H 284 | taller half-dome |
| xy-ipc-iid | 340 × 260 × 230 | 340 × 380 × 250 | the body is deep and overhangs the tray |
| xy-k-gzz-iii | H 1700 | H 1600 | the handpiece is lower |
| xy-dms-102b | 200 × 75 × 270 | 184 × 80 × 266 | proportions measured on the photos |
| xy-dms-103a | 230 × 80 × 345 | 250 × 80 × 372 | proportions measured on the photos |

## xy-k-wic-2

Differences found and fixed:
- **D panel too flat.** On the photo the panel is a half-ellipse about 340 wide and 160 along its slope (about 0.47:1).
  The model's panel was a flat half-stadium, 322 × 96 (about 0.3:1).
- **Hump shape.** The model's hump was a grey-shaded ellipsoid dome. The photo's hump is the D section carried to the
  back. It is now a loft of horizontal sections of the tilted half-ellipse, with its front on the panel plane and a
  rounded back. H is now 284.
- **Rim.** The rim is now a raised light-blue bead (`tube`) on a blue base, with a recessed lavender face. A slab with a
  hole showed only a thin outline, so it was replaced.
- **Keys.** The model had 6 blue keys plus a red bar. The photo has 5 oval blue keys in a 3 + 2 layout, with an oval red
  key at the bottom right.
- **Knob.** The model's knob was chrome on a blue ring. The photo's knob is light blue with a thin dark scale arc.
- **Leg graphic.** It was a thin bar. It is now a leg shape with the toe up and segment lines.
- **Panel layout.** The LED windows, 4 LED dots, text lines, logo and title were re-placed from the photo.
- **Line across the front.** A stray line across the front (the side "crease" decal) was removed. The shell corners now
  flare from a large top radius to a tighter skirt, which gives the crease facets.
- **Feet.** The feet were square boxes whose corners stuck out of the rounded tub. They now follow the tub's footprint.
- **Power socket.** Moved down to the lip, behind the socket block.

What the format cannot match:
- The LED digits are red bars, not 7-segment digits.
- The leg graphic is a flat silhouette.

## xy-ipc-iid

Differences found and fixed:
- **Body depth and shape.** In both photos the white body behind the screen is about as deep as the screen is wide
  (about 320). Its top slopes in a straight line down to a low back (about 100), and the back overhangs the tray. The
  model's body was short with a quarter-round top. D is now 380 and H is now 250.
- **Tray.** It now sticks out about 30 mm in front of the bezel, as in the photo.
- **White strip across the top of the screen.** The body's front-top corner was poking through the tilted bezel. The
  body's front now leans back with the bezel.
- **Left panel.** It is now long and low, as in the photo: DC jack, icons, the blue-ringed air connector and the white
  knob, with 3 rows of vents (there were 2).
- **Right panel.** It now has the icons, a 2 × 3-pin connector, an 11 × 5 dot grille and 3 rows of vents.

What the format cannot match:
- The screen picture is a perspective crop: it is slightly skewed and its right edge is cut off.

## xy-k-jlc-d

Differences found and fixed:
- **Base.** The model had a 5-spoke base with a big round hub. Both photos show a 4-spoke X base with no hub. The base
  now also has white swivel housings.
- **Coil arm.** It now follows the real photo `_2`: a dark bracket under the tray's left end, then a chrome rod up and
  left to a black T lock, then a blue sleeve and a ball joint, then a horizontal chrome bar to the clamp hub, whose
  knurled knob points left. The figure-8 coil centre is now about 330 mm left of the cart (it was about 100). The weak
  spot noted in the notes is fixed.
- **Hose.** It now drops straight down from the stem and loops into the plug.
- **Monitor.** It was 560 wide and is now 640 wide (27"), as measured.
- **Monitor stand.** It was a narrow Λ and is now a wide Λ on two feet.

What the format cannot match:
- The catalogue render (photo 1) shows a different, longer diagonal arm. The model follows the real photo `_2`.
- The front lettering is plain bars.

## xy-k-jlc-j

Differences found and fixed:
- **Left coil.** The model had two separate round "goggle" lobes. The photo shows a heart shape. The outline is now two
  arcs joined by tangents to a rounded bottom, with the holes and the dark window moved to match.
- **Spine.** It was at the right rear. It now stands at the front right, flush with the box fronts, with a light rail and
  the vertical text.
- **Boxes and shelves.** The boxes were 478 wide and are now 440, so the box-to-tray ratio is 0.63 as in the photo.
- **Monitor.** It is now about 19" and right of centre (it was 464 wide and centred).
- **Right arm.** The right arm and the round coil moved 40 mm inwards.

What the format cannot match:
- The host's 7" LCD is a dark screen, because the screen crop is the PC monitor's.

## tms-physiotherapy-device

Differences found and fixed:
- **Cabinet and plinth.** On the photo the cabinet is clearly narrower than the plinth: the plinth is wider by about
  50 mm on each side. The cabinet is now 400 × 380 (it was 450 × 396).
- **Head.** It is now a tall band from 832 to 1000 at the front (it was 930 to 1006). It is slightly wider than the
  cabinet, with a step and groove under it.
- **Sticker.** The blue sticker is on the head's front band, not on the cabinet below it.
- **Logo.** Moved down to about 30 % of the front panel, just above the upper groove. The grooves were re-placed.
- **Side label.** Made bigger and lower.
- **Holder.** A blue holder was added on the left of the head.

What the format cannot match:
- The source photo is very low resolution, so the key and LED layout on the top panel is still approximate.

## xy-k-gzz-iii

Differences found and fixed:
- **Base.** The model had a 5-spoke base with one spoke forward and a round hub. The photo shows a 4-spoke X base, a
  dark block hanging under its centre, Ø90 dark castors with grey swivels, and a wider column.
- **Shockwave arm.** Measured on the photo:
  - The lower dark segment runs from the tray clamp (610, 962) to (704, 1165).
  - The white segment runs from there to (866, 1440), so the arm is at about 60° (it was 69°).
  - The handpiece is lower (1530–1570; it was 1610–1665). It has finned rear rings and a nose.
  - The grip hangs under the handpiece.
  - The weak spot noted in the notes is fixed. H is now 1600.
- **Monitor.** It is now 510 × 300 (it was 578 × 334), on a wider frame neck.
- **Tray.** Narrowed to match the photo.
- **Blue lines.** Each line is now 108 long, 36 mm above the module's bottom.
- **Wings.** The trapezoid wings now have a flat bottom and a sloped top, as in the photo.
- **Cable hanger.** It is longer and lower (centre 1282, 190 mm long). The rod now runs from 790 to 1360, with a second
  thin rod and a cup at its foot.

What the format cannot match:
- The arm is a straight bar. The yellow label is a plain band.

## xy-dms-102b

Differences found and fixed:
- **Logo cap and display placement.** The in-use photo shows the round logo cap and the display on the same face. That
  face is opposite the grip, so for the device standing on its grip both are on the TOP. The model had both on the
  front face. The weak spot noted in the notes is resolved.
- **Head.** A Ø60 head cylinder now stands on the grip axis at the left end of the box. The raised cap Ø54 carries the
  white disc with the black cross. The shaft socket (Ø34) comes out of the head's left side.
- **Proportions.** Measured on the product photo: grip Ø48 and 172 mm long, box 57 tall and 75 deep, about 110 from the
  axis to the end. Size is now 184 × 80 × 266.

What the format cannot match:
- The heads and weights are accessories and are not modelled.

## xy-dms-103a

Differences found and fixed:
- **Proportions.** Measured on the photo:
  - The box was too tall and short. It is now 63 tall, 192 long plus a 21 mm dark end plate with 4 screws.
  - The grip and neck were too short. They are now about 289 long, with the flared neck and its ring, two groove lines
    on the grip, and an end cap.
  - Size is now 250 × 80 × 372.
- **Blue head.** It is now Ø38 × 23, with a Ø24 neck and a dark collar.
- **ECG line.** It was a solid white block. It is now a thin peaked polyline.
- **Front decals.** The logo, text and decals were re-placed.

What the format cannot match:
- The logo text is a plain bar.
- The aviation case is an accessory and is not modelled.

## pulse-magnetic-therapy-device

Differences found and fixed:
- **Proportions.** The model was a 50/50 split with a puffy white block on top. On the photo the blue tub is about 70 %
  of the height, and the white part is a low lid.
- **Lid shape.** The lid rises from a thin projecting lip to a plateau shifted to the back, which carries the glass.
- **Keys.** They were tall pucks floating above the slope. They now sit on the sloping lid and are tilted with it.
- **Glass colour.** The glass read as mid-grey from reflections. It is now satin black, as in the photo.
- **Vent grooves.** Re-placed on the taller tub.

What the format cannot match:
- The key legends and the printed text are bars.

## xy-k-csb-i

Differences found and fixed:
- **LCD offset (weak spot).** The screen picture is now aligned so that the crop's knob ring falls on the real knob. Its
  scale is set from the crop's knob/ring edges and checked against the photo's LCD width. Result: the LCD is 120 wide,
  about 33 mm right of the knob, and the logo sits at the left of the glass, as in the photo.
- **Glass looked like a floating sheet.** It overhung the domed top at the back corners. The shell top is now flat. The
  glass is flush and inset, with large back corner radii and smaller front ones (they were reversed).
- **Knob.** It was Ø54 on a Ø104 collar. It is now Ø44 on a Ø70 collar, with a subtle Ø128 dish, at z 205 (it was 222),
  touching the glass edge as in the photo.

What the format cannot match:
- The probe and hook stick out about 70 mm to the right of the printed 380.
- The cable runs along the desk instead of hanging over the desk edge.

## xy-k-csb-ii

Differences found and fixed:
- **Body.** It has the same fixes as CSB-I: flat top, flush glass with the correct corners, smaller knob.
- **Colour screen.** The crop is aligned so that its knob falls on the knob. The screen is 93 wide and about 40 mm right
  of the knob; before the fix it was misaligned by about 23 mm.

What the format cannot match:
- The trolley (photo `_2`) is an optional accessory and is not modelled.
- The two probes overhang the sides by about 70 mm each.
