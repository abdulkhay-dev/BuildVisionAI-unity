# Batch sensory-1: multi-sensory room equipment (14 devices)

Generators: `tools/medical/gen/s1_*.py`. The shared helpers are in `gen/s1lib.py`. Each script writes only its own
ids. Wall panels use the frame of the brief: back at z = 0 on the wall, front at z = D, y from 0 to H. The app hangs
a wall item from its middle.

## Parts lists from the photos (written before drawing)

### Panel family (cognitive-training-board, color-conversion-control-panel, dynamic-color-wheel, endless-depth-light-mirror, fiber-optic-curtain-wall)
All five share one case. It is a vertical plastic slab about 90 deep with rounded edges (r ≈ 25). Two round "bear ears"
sit at the top corners and stick out above the top edge, and slightly past the sides on the narrow panels. Each ear
holds a speaker grille: a slightly darker dotted disc, Ø ≈ 60. A small green logo sits at top centre: a leaf mark in a
green square, then green characters and a line of tiny text. Two low raised rounded-square bumps (≈ 120, each with a
small ring inside) sit at the bottom corners. Three round push buttons (Ø ≈ 34, each in a darker ring) are centred near
the bottom; on most panels they are red, yellow and green. I measured each panel's width on its photo at H = 900:
- **cognitive-training-board** (photo bbox 248×361 px → W 618): green #3fab45 case, ears Ø ≈ 132. A yellow #e8cb04
  inner face (x 89–532, y 124–812, r ≈ 20). On it: a black 17" screen band across the face's full width (y 319–637),
  holding a landscape display (x 104–519). The display shows a white page with a red frame, a light column of cards
  at the left, a bamboo/green header strip and a row of 4 green buttons at the bottom. Above the screen: three black
  "whisker" bars on each side (x 100–183, y 757/726/696; the middle one longer) and a cat face of dots in the
  middle: 2 big black dots Ø 22 at x 278/336 and 6 small dots. Under the screen: 2 black round speakers Ø 66 at x
  137/479, y 222, and three black lines between them (x 229–382). Buttons red/yellow/green at x 230/310/385.
- **color-conversion-control-panel** (3/4 photo; W 600): pink #ce567e case. The ears are smaller (Ø ≈ 105). A cream
  #e6dccb face, x 100–500, y 90–850, inside a thin black frame (≈ 8). On the face: 10 small glossy 3D triangle
  buttons, about 44 across and 15 proud. Row 1: red ▶, yellow ▲, blue ◀. Row 2: pink ▶, yellow ▲, green ◀. A D-pad
  low on the face: yellow ▲ top, pink ◀ left, green ▶ right, green ▼ bottom. Three big round buttons (Ø ≈ 48, in black
  rings): red, yellow, blue.
- **dynamic-color-wheel** (241×378 px → W 575): lavender #bdb6dc case. The ears are Ø ≈ 115 and stick out ~25 past
  the sides. A black bezel (x 81–491, y 120–814, ≈ 17 thick) around a white display. The display shows a blue windmill
  of 8 curved blades of light dots inside a faint dotted disc, Ø ≈ 370, centred at (287, 469).
- **endless-depth-light-mirror** (256×372 px → W 620): green #2ca33a case. Ears Ø ≈ 128. A black bezel (x 86–529,
  y 126–811) around a white display. The display shows a red "8": two white circles (r ≈ 93) inside rings of red
  dots, which fade outwards, with a bright red waist and a small red ellipse between them.
- **fiber-optic-curtain-wall** (237×377 px → W 565): magenta #c4358b case. Ears Ø ≈ 115. No black bezel; the face is
  framed by a raised magenta lip (x 78–484, y 130–807, ≈ 12 wide). At the top is a cyan #36bcc0 band (y 719–793)
  with 5 stars: magenta, yellow, a bigger green one in the middle, yellow, magenta. Below it a glowing white
  fibre-optic area (x 96–470, y 142–715) of wavy vertical strands.

### butterfly-fiber-falls [600, 100 → 330, 1800]
The head is a butterfly-shaped plastic body, ~600 wide × 560 high × 100 thick, with yellow #f2d21a sides and edge band.
Its face is lime-green #84bf24, with a wavy outline: two upper wing lobes with scalloped tops, two lower lobes, and a
tail point at the bottom centre. A thin yellow outline line runs inside the edge. On each side a large yellow #f6dc44
inner wing (upper and lower parts in one shape, with a yellow rim) carries 3 green round spots: small at the top,
medium in the middle, big at the bottom. The yellow body in the middle has a round head with a dot pattern, a
striped abdomen of 5 chevrons, and a pointed tail. Two curled antennae run from the head to the top edge. From
behind the bottom centre hangs a thick ribbed yellow fibre sheath (Ø ≈ 60). It goes down and curves to the left,
then (per the inventory text) on to the floor.

### jy-tyhd-i [600, 700, 1550 → 1600]
Photo from the front-left, so the x = 0 side is visible.
- Light-blue #a8daee plinth (≈ 65 thick, rounded corners, y 130–195) on 4 castors Ø 100. The castors have white
  wheels, grey hubs and a white brake tab.
- Light-blue lower box on the plinth. Its x = 0 side has a quarter-curve top that runs from ~265 at the back up to
  the 690 top at the front. The yellow rear column fills the area above the curve. Front: a dark grey mesh band
  (x 40–560, y 420–525, rounded). Above the band's middle is a dark arched notch (r 50) with a white ▼ marker. At the
  bottom middle is an arched recess (≈ 240 wide × 160 high) with a black two-tier round puck (Ø 140) inside. A black
  vertical slot (20 × 170) sits on the x = 0 side.
- Yellow #f0c46a shell. A full-width rear column (≈ 300 deep) rises from the blue curve to the top, with a big
  rounded top-back corner. The head projects forward over the full depth (y 1310–1530) and has two dark grey #2d3b3e
  round mesh "eye" speakers, Ø 135, at x 150/450. Two light-blue loop handles stand on top at the rear, one on each
  side, as arches along z.
- The middle front has a yellow lower box (y 690–945) with a round blue/white Xiangyu badge (Ø 70) right of centre.
  Above it is the projector bay, a white #ededed face that slopes back as it rises. The black projector window sits
  under the head. A light-grey raised plate is in the middle and a grey diamond to the right. The bay sits between
  two yellow cheeks whose front edges slope back. A white strip of small black icon buttons is on the inner face of
  the left cheek.
- A grid of dark vent dots on the x = 0 side, near the front, y 720–1030.

### led-piano-pedals [2400, 700, 30]
A flat floor strip in a dark frame, with two keyboards side by side along the length (x). A black divider (≈ 40)
runs down the middle of the width. Each half has 16 rainbow white keys (150 along x, ≈ 300 across). The black keys
start at the divider and run outwards ~60 % of the half width. They follow the 2 + 3 piano pattern. Colours along x,
back half: lavender, pink, light blue, white, orange, yellow, green, purple (×2). Front half: lime, yellow, orange,
white, light blue, pink, purple, green (×2).

### lighting-color-changing-puzzle-table [700, 700, 200]
A white #eceeee box base (≈ 130 high, square edges, slight r). The front carries 5 round buttons (Ø 45) in black rims,
left of centre to centre: dark red, blue, green, yellow and white-blue. On top sits a transparent orange acrylic tray,
70 high, inset ≈ 15 from the base edge. Its floor is a glowing yellow #f5e97d surface. Translucent shapes lie on it:
red and green triangles, a green square, red and yellow discs, a yellow triangle and green triangles at the corners.

### multi-sensory-master-control-machine [450 → 600, 550, 950]
A white #eef0f2 kiosk cabinet. The front is vertical up to ~650. From the front top edge the top slopes up and back to
the rear top at 950 (≈ 29°). A landscape touch screen (dark bezel, ≈ 530 × 300) sits on the upper part of the slope,
with a blue interface (dark blue with lighter blue panels). Below it on the slope is a faint embossed panel outline.
The front door is outlined by thin grey seams (x 55–545, y 25–600) and has a small dark horizontal handle slot at its
top middle. The right side (x = W) has 4 slanted vent slots and a black port low down.

### multi-sensory-matching-projection-system [350, 300, 120]
A projector. The lower body and the front are black #0a0b0b; the top shell is silver #c8cacb with rounded edges, a
recessed control panel at the back and a darker grey vent. The front right has a big black lens ring (Ø 110), standing
~25 proud, with a chrome inner ring and blue-grey glass. A small silver badge is on the front left of the lens, and a
thin silver band runs at the bottom. (The ceiling pole and the projection screen of the room photo are not in the
product photo, so they are not drawn.)

### colorful-fluorescent-drawing-board [1200, 50, 800]
A dark blue/navy #1f3a52 glossy board in a dark brown wood frame (≈ 37 wide, bevelled, 50 deep). Glowing
yellow-green #b4e05a lines form the photo's drawing: a bowl with wavy vertical strokes, a rim ellipse, a foot, and two
chopsticks sticking out at the upper right.

### color-led-ball [300, 300, 450]
The photo is only a close-up of the light: a ring of white LED dots around a bright cluster on green. Drawn from the
inventory text: a white ceiling plate (Ø 120) with a small motor can, a chrome rod (~110) and a faceted mirror ball
Ø 300. A ring of small LED dots goes around the ball's equator, as in the photo's ring of dots.

### bean-bag [900, 900, 700 → 800]
A big round beach-ball-like bean bag with 6 gores alternating red #da3e3a, yellow #f2d84a and blue #1a6aa8. They meet
at a pole on the lower front-right, so the front shows a pinwheel of colours. The bag is almost as tall as it is
wide in the photo (the child sits in a dent at the top).

## Results (final checks)
All 14 render `ok`. I confirmed each device's last edit on a fresh `renders/<id>-compare.png`.

- **cognitive-training-board** [600, 100, 900] → [618, 90, 900]. The width is measured on the photo and the depth
  matches the family's ~90. The case, ears, bumps, buttons, yellow face, whisker bars, cat dots, speakers, lines and
  screen band all match the photo. Approximate: there is no screenCrop, so the display is dark, with decals for the
  interface (card column, red-framed page, header, 4 green buttons, pot and plant). The logo characters are
  stylised strokes because the glyphs are not in the font. The speaker grilles are plain discs, not dots.
- **color-conversion-control-panel** [600, 100, 900] → [600, 90, 900]. Drawn from the 3/4 photo, with perspective
  removed by eye. The 10 triangle keys have the photo's colours and directions. The photo shows no logo and no
  grilles, so neither is drawn.
- **dynamic-color-wheel** [600, 90, 900] → [575, 90, 900]. Approximate: the dotted LED windmill is 8 thin
  curved blue blade strokes over two pale-blue discs and a white core.
- **endless-depth-light-mirror** [600, 90, 900] → [620, 90, 900]. Approximate: the dotted red "8" is drawn as
  concentric pink/red discs around two touching white circles, with a red bow-tie of rays and an ellipse at the
  waist.
- **fiber-optic-curtain-wall** [600, 90, 900] → [565, 90, 900]. Raised magenta lip, cyan star band and the glowing
  white fibre area with 12 wavy strand lines.
- **butterfly-fiber-falls** [600, 100, 1800]. Approximate: the wing outline is traced by eye from a 3/4 view. The
  photo shows the sheath only down to the image edge; I continued it to the floor (per the inventory) with no glowing
  fibre ends. The ribbed tube shows small rib joints at its bends.
- **jy-tyhd-i** [600, 700, 1550] → [600, 700, 1600]. The head top is at 1530; the light-blue loop handles reach
  1600. Proportions come from the castor layout (W/D ≈ 0.86, θ ≈ 36°). The x = 0 side has the vent-dot grid and
  the black slot, as in the photo. The renderer's angle view shows the other side, so check them on the json if
  needed. Approximate: the button strip on the inner face of the left cheek, the small sticker on the bay (left
  out) and the mesh texture of the band and eyes (plain dark grey).
- **led-piano-pedals** [2400, 700, 30]. Two mirrored keyboards of 16 rainbow keys with a black divider, and black
  keys in the 2 + 3 pattern starting at the divider. Approximate: the key colours are bright gloss rather than lit
  LEDs, and the black keys read dark grey at the renderer's grazing angle.
- **lighting-color-changing-puzzle-table** [700, 700, 200]. Approximate: the loose shapes are opaque bright gloss.
  Translucent acrylic shapes looked washed out against the glowing surface.
- **multi-sensory-master-control-machine** [450, 550, 950] → [600, 550, 950]. On the photo the front is almost as
  wide as the vertical front is tall (W/H ≈ 0.63), and the screen spans ~80 % of the width, so 450 cannot be right.
  Approximate: no screenCrop, so the screen is dark with blue interface panels as decals.
- **multi-sensory-matching-projection-system** [350, 300, 120]. A projector only. The ceiling pole and the screen of
  the room photo are not in the product photo, so they are not drawn. Approximate: the top vents and the control
  panel are flat decals.
- **color-led-ball** [300, 300, 450]. The photo shows only light dots, so the shape follows the inventory text:
  ceiling plate, motor can, chrome rod, and a chrome ball with a grid of facet seams (9 latitudes, 12 meridians). The
  photo's ring of LEDs round a bright cluster sits on the underside. Approximate: real mirror facets are not
  modelled.
- **bean-bag** [900, 900, 700] → [881, 867, 786]. In the photo the bag is about as tall as it is wide. Six
  ellipsoid gores (yellow, blue, red, ×2) meet at a pole that points front-left-down, which gives the photo's
  pinwheel. Approximate: the seat dent and the deformation under the child are not modelled, so it reads as a soft
  beach ball.
