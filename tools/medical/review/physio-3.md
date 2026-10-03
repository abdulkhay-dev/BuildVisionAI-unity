# Detail review — batch physio-3 (14 devices), 2026-10-02

Method: for each device I made a compare sheet and looked at the catalogue photo(s) at full size. I listed every visible
difference, edited the generator (`tools/medical/gen/p3_*.py`) and regenerated only this batch's ids. I waited for the
`.txt` to be newer than the json and checked again. All 14 render `ok`.
Generators touched: p3_alphatron, p3_grai, p3_grci, p3_ecart, p3_greii, p3_srd, p3_desk, p3_xyzpie, p3_xyzpii.

## xy-alpha-tron-ii
Found and fixed:
- The welcome UI was a small patch in the middle of the black glass. It now fills the rear ~3/4 of the glass, with a
  pale band and a teal wave along its lower edge, the title and subtitle lines and a progress bar. The knobs sit at the
  UI's front corners, as in the photo.
- The flanks were puffy pillows (r 32). They are now flat-sided, with r 26 edges.
- The ribbed side panel was small. It now covers almost the whole flat side: a black border, a grey groove line, a light
  field and 3 print lines plus the logo line at the front.
- The sockets were solid colour discs. They are now dark sockets with thin yellow or blue rings. The inner column of
  each group is smaller. Each group of 3 columns sits in a thin printed frame.
- The 'I/II' label now has its icon above it and a yellow warning triangle below it.
- A side-text line stuck out past the front; fixed.

Cannot match: the UI text, the fine grooves of the ribbed border and the printed lettering are not drawn (there is no
screen crop, so the UI is decals).

## xy-k-gr-ai-v2
Found and fixed:
- The socket window started too far left and sat too low. It now starts ~120 mm from the left edge and ends ~36 mm from
  the right, as in the photo.
- The triangle plates are smaller (k 0.9) and placed at the photo's positions. The warning sign is at the tips between
  A1 and B1, and the icon is between A2 and B2.
- The control-top bands now have their printed frames: two rounded frames per half, with vertical sides and a third
  band line.

Cannot match: the LED digits and the lettering of the print are blocks.

## xy-k-gr-ai-trolley
Found and fixed:
- Proportions. In the photo the front of cabinet + head is ~2.3× the width; the model was ~2.0×. The cabinet is now 810
  tall instead of 688, and the head front is 148 instead of 128. **Size H 1075 → 1210.**
- The compartment, drawer and band are re-placed at the photo's fractions. The compartment is bigger (290 tall), and
  the flap is 270 long, open 62°.
- The window and the sockets are re-measured: window 40–314, plates k 0.7.
- The castors are spread to the corners, with grey arms from the frame.
- Added the slotted inner strip and the small bracket inside the compartment.
- The box holder moved forward under the head, and the basket follows the head.

## xy-k-gr-ci-v2
Found and fixed:
- The slab tilt was 18°; it is now 24° (the photo shows much more of the face). **Size H 345 → 365.**
- Face layout re-measured on the photo:
  - The LED windows are 2 rows of 3, pale green glass with red digits, at their measured positions.
  - The A/B/C bars are shorter (130–251), each with a frame, a letter dot and a green square.
  - The mode column is at 293–337.
  - The knob was at the right edge; it is now at x 353, level with the bars.
  - The 7 keys are narrower (22 wide at a 31.7 pitch), with a white middle.
- The knob's blue ring was a full circle. It is now a partial arc on its right (a tube along 1–4 o'clock).
- The start and stop buttons were filled squares that overlapped the last key. They are now dark squares with green and
  orange outlines and icons, to the right of the keys.

## xy-k-gr-cii
Found and fixed:
- The panel showed the crop inside a black outline, with white margins. The panel is now 472 × 372, white-cased with no
  bezel, so the crop's white edges blend into the white back shell, and its black glass reads ~410 × 340 as in the photo.
- Added the vacuum cup on the right side of the collar (blue plug) with its cable straight down that side to the base,
  as in the photo.
- The cable loops hung as one straight bundle. They now fan out sideways and in depth, reaching 110–200 mm above the
  floor.
- The handle loop is taller (upper tube at 1075).

Cannot match: the photo has ~10 cable strands, the model has 6 loops (12 strands) as smooth curves. Lettering (XIANGYU,
E SERIES) is blue bars.

## xy-k-gr-dii
Found and fixed:
- The screen was a thin bezel with the UI picture filling it. The photo shows a wide black glass (~424 × 344) with the
  UI (~270 × 200) in its middle. It is now a black glass box with the UI screen on it, and a broader top strip with the
  blue logo and title lines and a bottom strip of grey print.
- The cable loops spread out, as for CII.

Cannot match: the cables are smooth tubes, and the cable hooks on the lower bar are simplified.

## xy-k-gr-eii
Found and fixed:
- The black face stopped above a wide white chin, and the start and stop buttons sat on white. The face now runs down
  to a thin white rim. A U-notch is cut into it from below (slab outline), and the white frame shows round the knob.
- The green ▶ and orange ■ are rings with icons on the black face at its lower corners.
- The knob is smaller (Ø30), with a knurled band.
- The kickstand legs are wider (14 × 7), and the floor foot is a broad plate.

Cannot match: the face print is grey bars and windows, not the photo's lettering.

## xy-k-srd-i
Found and fixed:
- The strap was a boxy flat-topped arch. It is now a round arch ~100 above the pad, with the light logo patch on its
  upper side (a second strap following the arc).
- The display bar was a box with a rectangular black plate overhanging its rounded ends. It is now stadium-shaped, with a
  stadium black top and a larger grey window (128 × 42).
- The cradles were tall white pillows with hidden rollers. They are now flat-topped grey capsules on a narrower foot.
  Each has a large black rubber roller along the lower part of one side and cyan triangles at both ends.
- The thumb cradle is shorter and taller, with rollers on both sides (photo 2).

Cannot match: the pad is a flat inset without the hand relief. The fan of the cradles is estimated from 2 photos.

## xyd-ii
Found and fixed:
- The maroon bottom shell was a thin strip under a tall white front. It is now ~20 tall, with the white bevel above it.
- The header was pale and rectangular. It is now sky blue (#5cb3ea): deep on the left, with a diagonal step to a narrow
  strip with the power switch, LED and label. It also has the white round logo and dark title lines (they were blue
  bars).
- The knobs are re-placed from the photo:
  - frequency at the rear right;
  - waveform and timer;
  - the 6 output knobs in a diagonal row that rises towards the back on the right (they were in a straight row along
    the front).
- The slide switch moved to the left middle.
- The knobs now have rib bands and silver dome caps.
- Added the printed output line and the DC socket on the right end.

Cannot match: the panel lettering and the warning-label text are not drawn. The labels are plain yellow.

## xyzp-ib
Found and fixed:
- The violet band was ~60 % of the front height; it is now ~40 %. The wedge is steeper (front 34, back 72).
- The display was a raised white pod. In the photo it is flush, in a deep pink corner of the header. The header is now
  a pink band, narrow on the left with a diagonal step to a deep pink corner holding the black display.
- The membrane now has a thin pink outline.
- The title lines moved under the header, onto the white.
- Added a second pink label strip on the right.
- The keys are re-placed.

Cannot match: the lettering. The loose electrode pads in the photo are accessories and are not drawn.

## xyzp-ic
Found and fixed:
- Shape. The model was a tall, ellipse-like puck (H 92, r 112). It is now a low unit (**H 92 → 76**) with straighter
  sides and r ~75 corners. The blue basin tapers to the bottom and is ~60 % of the side. A white lid overhangs it.
- The black island was centred and small. It is now large (212 × 128) at the back right.
- The LCD had two dark squares. It now shows '20-07' in segments, with the two gauge arcs, grey print lines and the
  dotted grid.
- The keys were a straight row along the front. They are now 6 radial pairs on an arc round the island's front-left
  corner: white, white, blue/grey, blue/grey, white, white.
- The skirt is now the photo's lighter blue.

## xyzp-id-table
Found and fixed:
- The white was a uniform band over the blue. In the photo the blue shows high on the sides, and the white cap comes
  down over the front as an apron. A loft now does this, so the white/blue boundary on the sides slopes down towards
  the front.
- The socket window was a small grey panel. It is now large (268 × 124) in the front apron, with a thick light-blue rim
  and a blue field with printed diagonals.
- The 8 sockets are re-measured. Two staggered rows rise to the right, starting ~1/4 into the window. The heads are
  light metal-grey on darker bases.
- The orange top lines were straight strokes. They are now 4 framed channel blocks, with more keys and a title line.
- The vent moved low to the front on the left side.

Cannot match: the frames' rounded notches and the lettering.

## xyzp-ie
Found and fixed (generator rewritten):
- Proportions. The photo's door is ~1.7× its width and the upper block ~0.4×; the model was squat. The cabinet is now
  380 wide, with the door to 857, the upper block 861–1005 and the head front to 1114. **Size H 1100 → 1160.**
- The cabinet is now 3 stacked parts with dark seams, as in the photo: the head with panel 1, the upper block with
  panel 2, and the door.
- The socket rows were staggered the wrong way. The lower row is now shifted LEFT, and the sockets are bigger (Ø24/20).
- The screen was dark. The photo shows a light screen (switched on), so it is now light grey in a grey frame, with 2
  UI bars.
- The swoosh was also a stripe on the front face. It is now only on the left side, from the head's top at the back down
  to the front edge.
- The comb was L-hooks at mid-height. It is now 4 inverted-U loops at the seam height, with the box holder above.
- The right hook is raised.
- The ECG line now has a grey dash, a double spike and a grey under-line. The logo is re-placed.

The 'wing piece' noted by the author turned out to be just the left side face in front of the swoosh. It is covered by
the side swoosh.

## xyzp-ii
Found and fixed:
- The keyboard was light grey; the photo shows it black.
- The shelf sat in a gap below the head; it is now sandwiched between the cabinet top and the head, as in the photo.

Cannot match: there is only a small scene photo, so the depth, the side profile and the exact angles of the green side
panels are still guessed. The UI is decals (no screen crop).

## Common limits of the format
- Lettering and fine printed text are not drawn: the format has no text. Logos and titles are bars or discs.
- Segment digits are drawn only where they are large (xyzp-ic). Elsewhere they are coloured windows.
- Cables are smooth tubes with fewer strands than the photos.
- Several photos are taken from the side opposite the render's fixed angle camera (alpha-tron, gr-ai-v2, cii, xyzp-ie),
  so those sides were checked in the front and side views.
