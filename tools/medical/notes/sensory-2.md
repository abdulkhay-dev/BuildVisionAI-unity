# Batch sensory-2: multi-sensory room equipment (11 devices)

Generators: `tools/medical/gen/s2_*.py`. Shared helpers are in `gen/s2lib.py`. Each script writes only its own ids.
Wall panels use the brief's frame: the back is at z = 0 on the wall, the front at z = D, and y runs 0..H. None of the
11 devices has a `screenCrop`, so every display face is drawn from parts.

## Parts lists from the photos (written before drawing)

### Panel family: smell-perception-game-box, sound-and-light-wall-panel, wall-of-blisters, variable-speed-fan-game-box
I measured each one on its photo at H = 900; 1 px of the original photo ≈ 2.45 mm.
- **Case**: a flat plastic slab with rounded edges, one colour. Two round "bear-ear" lobes, Ø ≈ 150, sit at the top
  corners. Their centres are ≈ 73 mm in from the outer edge and 73 mm down from the top. Each lobe sticks out ≈ 27
  past the body side and ≈ 30 above the body's top edge. Each lobe holds a speaker grille: a slightly darker dotted
  disc, Ø ≈ 57, centred about 12 mm up and out from the lobe centre. Two low raised rounded squares (≈ 115 × 105,
  r ≈ 25) sit at the bottom corners, each with a thin ring (Ø ≈ 50) in it.
- **smell-perception-game-box** (photo 255 × 366 px → **W 620**): pink #e48cbe case. A raised inner panel (x 86–530,
  y 134–814) has a groove frame ≈ 16 wide. The green logo at top centre (x ≈ 310, y 843, ≈ 120 × 33) is a round
  yellow-green leaf mark with dark-green characters. On the panel:
  - a column of 5 small dots (Ø 20) at x 155, y 660/566/473/375/277: four dark red, the bottom one dark blue;
  - a vertical strip (x 208–236, y 260–677) of three stripes, red, yellow and green, with a dark-red outer edge;
  - 4 squares (53, x 293–346) at y 655/531/407/285: dark red, dark blue, lavender, light cyan;
  - 4 white round scent outlets Ø 61 at x 428, at the same heights.
  Three round buttons (Ø 33, in dark rings) sit at x 216/293/371, y 65: red, yellow and green.
- **sound-and-light-wall-panel** (244 × 373 px → **W 590**): light pink #efb6d6 case, same ears, logo, bumps and
  buttons. There is no raised panel. A black bezel (x 85–525, y 135–835, ≈ 18 thick) frames a white display. On the
  display is an LED-dot equaliser: about 24 columns of dots on a 16 mm pitch. The lower ~6 rows are rainbow coloured
  (left → right: blue, cyan, green, yellow, orange, red, magenta). Above them are black dots. The column heights
  vary; the peaks reach ≈ 60 % of the display height, at the columns ~6 and ~17.
- **wall-of-blisters** (233 × 369 px → **W 570**): sky blue #46a8e4 case, same ears, logo, bumps and buttons. A black
  bezel (x 85–490, y 140–835) frames the bubble panel. The panel is blue: lighter at the top and bottom, deep blue in
  the middle (a mirrored diamond pattern), with vertical light streaks of bubbles and a thin dark centre seam.
- **variable-speed-fan-game-box** (a CAD render seen a little from the right; the side shows ~17 px of depth):
  front 187 px wide over 358 px high, foreshortened about 17°, → **W ≈ 500**, D 150. Blue #2a9be0 case. No logo and
  no three bottom buttons: the photo has none, although the inventory form text lists them. The bottom-corner bumps
  are bigger (≈ 110 × 100) and each holds a ring. A recessed face panel (x ≈ 55–445, y 130–775) has a thin groove
  frame. On it:
  - 4 round black fan grilles, Ø ≈ 80 (slightly oval in the photo), at x ≈ 145, y 690/580/470/365. Each has a 3-blade
    blue star;
  - 4 small red LEDs at x ≈ 250, at the same heights;
  - on the right, at x ≈ 335, the controls: a yellow round knob (Ø 40) with a black ring; a push rod (a green ball
    knob on a short white bar in a slot); a tiny grey button; and a dark-blue round crank face (Ø 80) with a red eye,
    a yellow eye and a green smile.
  - The case side shows a stepped back.

### music-training-device [500, 500, 450 → 550]
Photo: the cube seen corner-on, eye height ≈ 5° above the top.
- Glossy orange #f5a21f rounded cube (edge r ≈ 80), y 140–550 (≈ 405 tall: the photo makes it taller than the estimate).
- 4 white/silver #e9ebee pads, one in the middle of each side's top edge. Each is ≈ 260 wide and runs ≈ 120 down the
  side, wraps over the edge and runs ≈ 150 onto the top, with rounded corners. The top centre between the pads is
  orange, with a faint embossed ring.
- Dark-red #b4402c "giraffe" blobs: each is two overlapping discs (Ø 40–55). There are 3 on each visible face. Left
  face: (0.16 of the face, y 380/337, vertical pair); (0.51, y 261, horizontal pair); (0.74, y 398, small vertical
  pair). Right face: (0.24, y 318); (0.60, y 285, diagonal pair); (0.84, y 441, vertical pair near the top).
- A glossy black #1c1d20 plinth, 140 high, on the same footprint. In the middle of each side is an arch cut-out ≈ 230
  wide × 115 high with a dark recess (speaker) inside. Four small dark feet sit under the corners.

### piano-water-column [1200, 350, 1000 → 900]
- A pale green #cfe0b0 base cabinet front (y 0–157). It has a round button (Ø 115) at the centre: a grey-teal ring
  with a green face. There are two round black holes (Ø 48) at x 116 and 1098, y 68; the right one is dark red.
- A white platform slab (y 157–184) that glows a little. In front of the tubes is a row of 7 coloured square keys
  (≈ 40 × 25): magenta, dark blue, blue, green, yellow, orange and red, under tubes 2–8. Under the clear tube no key
  shows.
- 8 square-section acrylic bubble columns (≈ 90 × 90) stand along the back half of the platform. Centres x 170, 293,
  423, 539, 664, 798, 921, 1037. Heights 618, 566, 501, 453, 396, 334, 280, 223 above the platform. Colours: clear
  white-blue, violet-pink, blue, cyan, mint green, yellow, orange, red. Each has white bubble sparkles.
- The niche the photo shows: a mirror back wall, a mirror on the left inner side, a cream right side panel and a
  white top frame bar (top at ≈ 893). The "second" tubes behind each tube are reflections in the mirror and are not
  drawn as tubes.

### sensory-soft-ball-pool [2000 → 1700, 1500, 600]
- Foam wall blocks 600 high and 200 thick, with slightly rounded edges, in dark red #a8282a and green #5aa03a. The front
  wall (photo 1) is red | green | red (610 / 500 / 590). The back wall top shows red, green, red, green. The side
  walls alternate.
- Inside, multicolour balls (Ø ≈ 80: red, yellow, orange, green, blue, dark blue) fill the pool almost to the top
  (the top layer is ≈ 60 below the wall top).

### smell / sound-light / blisters / fan: see the panel family above.

### sound-amplifier [430, 330, 130 → set]
- **Amplifier** (black, ≈ 430 × 330 × 165: the photo front is 2.57 : 1). The upper front is a gloss-black display panel
  (≈ 99 high) with a thin gold frame line. Two big round VU dials (blue lit rings, Ø ≈ 68) sit at x ≈ 38 and 346 from
  the left. Next to each, inside, are 2 round blue buttons (Ø 19) stacked. In the middle is a display with red/blue
  digits, and a small gold label at top centre. The lower front is a dark-grey/silver strip (≈ 53 high) with 5 black
  knobs, 2 mic jacks in a bezel, a USB port and an SD slot. The right side has a vent square and screws.
- **2 speakers**, black, landscape (the photo ratio is 1.41 : 1): ≈ 420 × 300, 240 deep. The front has a black mesh
  grille with a thin silver frame line and a silver "SAST" logo in the middle. The right speaker has a round port at
  lower right. Two small screws sit on top.
- Layout: the photo is a product composite (speakers above the amp). I place the set on a shelf: speakers to the left
  and right of the amp, all facing front.

### symphony-hemisphere-light [220, 200, 200 → set]
- A round black body, Ø 180, about 85 high, with a rounded bottom. A black rectangular front plate (≈ 115 × 85) with a
  silver frame line, a silver logo and two text lines. A black foot bracket under it.
- A clear faceted dome (≈ 0.6 × the diameter tall) with a clear faceted ring band at its base.
- A black power cord coiled on the left, with a plug.
- A black IR remote (≈ 50 × 125) on the right. Its top has 2 red buttons and 3 × 3 dark keys; its lower light-grey
  panel has 3 × 3 black round keys.

### visual-perceptual-trainer [900, 600, 1800 → set with cube]
- 3 short glowing white-blue tubes (Ø 150, ≈ 900 tall) in the front row, about 340 apart. 2 tall glowing pink tubes
  (Ø ≈ 180, ≈ 1500 tall: the photo ratio is ≈ 1.6 × the short ones, not 2 ×) in the back row, between them.
- Round clear glowing base discs (Ø ≈ 300, ≈ 20 thick) under the tubes.
- A light cube ≈ 400 to the right: red top, blue front face, violet side, light edges.

### multimedia-scenario-interactive-system [450, 350, 250 → 450, 450, 120]
- A white square ceiling plate (≈ 450 × 450 × 40) with sides tapered towards the bottom. Under its centre, on a short
  neck, a small white projector box (≈ 170 × 110 × 65) with a dark lens at the front and a small sensor.
- The floor game picture is light on the floor. It is not part of a ceiling item and is not drawn (see results).

## Results (final checks)
All 11 designs render `ok`. I checked each one's last edit on a fresh `renders/<id>-compare.png`.
The angle render looks from the front-right.

- **smell-perception-game-box** [620, 120, 900] (W 600 → 620, measured): everything on the parts list is there and
  in its measured place. The ear grilles are dot grids. **Approximate**: the logo characters are glyph-like strokes,
  not real letters (the brand's characters can't be read on the photo); the squares have no glow halo.
- **sound-and-light-wall-panel** [590, 90, 900] (W 600 → 590): the equaliser is 24 dot columns at the photo's
  column heights, with the 7 lowest rows in rainbow colours and black dots above. **Approximate**: the photo mixes
  some black dots into the coloured rows; here the colour band is solid. The display is flat white with no gradient.
- **wall-of-blisters** [570, 90, 900] (W 600 → 570): the bubble panel is a mirrored 32 × 52 pixel pattern in 4
  blues (light at the top and bottom, deep in the middle, with vertical streaks) plus the centre seam. **Approximate**:
  the pattern is a procedural likeness, not the photo's exact picture (there is no screenCrop).
- **variable-speed-fan-game-box** [500, 150, 900] (W 600 → 500, measured from the CAD render): no logo and no 3
  bottom buttons, as in the photo. The inventory form text lists them, but the photo shows none. It has 4 black fan
  grilles with 3-blade blue stars, 4 red LEDs, a yellow knob, a push rod with a green ball, a tiny grey button and the
  blue crank face (red eye, yellow eye, green smile).
- **music-training-device** [500, 500, 520] (H 450 → 520: the photo makes the cube about as tall as it is wide). It
  has the white pads over the 4 top edges and pairs of dark-red discs on all 4 faces. The front and right faces
  follow the photo; the back and left repeat them. The black plinth has real arched tunnels with dark speakers
  inside, and small feet. **Approximate**: the pad corners are chamfered (≈ 28 mm) rather than round. The top
  "touch area" is one embossed ring.
- **piano-water-column** [1200, 350, 900] (H 1000 → 900). It has 8 square acrylic columns at the photo's heights
  (618 → 223), each with a glowing core and white bubbles. The white platform has the 7 colour keys, and the pale-green
  cabinet has the round green button and the black and dark-red holes. The mirrored niche (mirror back and left inner
  side, cream sides, white top frame) is included because the photo shows it. The "doubled" tubes in the photo are
  reflections and are not drawn. **Approximate**: the mirror renders grey in the studio views; the bubbles are
  sparse, compared with the photo's dense fizz.
- **sensory-soft-ball-pool** [1700, 1500, 600] (W 2000 → 1700, from the front wall's 2.8 : 1 ratio). It has the
  photo's red | green | red front wall, 180 thick foam blocks, and a hex layer of Ø 100 balls in 6 colours.
  **Approximate**: the side and back block order (the room renders don't show it clearly) and the depth (1500, from
  the inventory estimate).
- **sound-amplifier** [1310, 330, 300]: the whole set. It has the amplifier (430 × 330 × 165: the photo front is
  2.57 : 1, so taller than 130) and a speaker on each side (landscape 420 × 300 × 190, mesh, silver frame line, "SAST"
  in real letters, a port on the right speaker, top screws). The amp has blue-lit VU dials, blue buttons,
  red/blue display digits, a gold label and frame line, a silver strip with 5 knobs, mic jacks, USB, SD and a side
  vent. **Approximate**: the layout (the photo is a composite with the speakers above the amp); I placed it as a shelf
  set.
- **symphony-hemisphere-light** [330, 200, 220]: the set as in the photo. It has a clear dome on a 14-facet clear
  ring band, a round black body with a rounded bottom, a black front plate with a silver frame, logo and text lines,
  and a foot bracket. A black cord loops on the left with its plug. The IR remote (red keys, 3 × 3 dark keys, grey
  panel with 3 × 3 black keys) **lies flat** on the right; the photo shows it standing for display. **Approximate**:
  the dome's facets (a smooth clear dome).
- **visual-perceptual-trainer** [1450, 650, 1500] (H 1800 → 1500: on the photo the tall tubes are ≈ 1.6 × the short
  ones, not 2 ×; W now includes the cube). It has 3 short white-blue tubes (Ø 150 × 900) at the front and 2 tall
  pink tubes (Ø 180) behind them in the gaps. All stand on clear Ø 300 light discs and have glowing LED cores. The
  light cube (400) has a red top, blue front and back, violet sides, and white glowing edges. **Approximate**: the
  glow reads only weakly on the white studio background.
- **multimedia-scenario-interactive-system** [450, 350, 255] (H 250 → 255; D 350 kept). It has the photo's ceiling
  box with tapered sides (450 at the ceiling → 375 at the bottom, 180 tall) and a faint round mark on its front face.
  A short neck holds a small white projector (166 × 110 × 66) with a lens, camera, LED and side vent. The projected
  floor game (≈ 3000 × 2000) is light on the floor and can't be part of a ceiling item, so it is not drawn.
