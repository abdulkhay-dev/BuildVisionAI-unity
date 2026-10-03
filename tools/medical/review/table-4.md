# Detail review: batches table-4 + table-5 (traction tables and chairs, decompression tables, tilt tables, TMS)

Generators changed: `tools/medical/gen/t4lib.py`, `t4_yhz_iaj.py`, `t4_yhz.py`, `t4_yhz_mw.py`, `t4_yz.py`,
`t4_rxqy.py`, `t4_jzjy.py`, `t4_xyq.py`, `t4_tms.py`. The originals are copied to `scratch/table-4-review/*.orig.py`.
All 16 designs re-rendered `ok`. Each was re-checked on `renders/<id>-compare.png` after its last change.

## Shared changes
- **Lettering**: `t4lib.text()` reuses `p1lib.text()` (p1lib's D-method patches are undone after the import). I added
  the glyphs 医 and 疗. The new `brand()` helper draws the Xiangyu logo: a blue disc with a white cross, then
  "翔宇医疗" and "XIANGYU MEDICAL" in real strokes. It replaces the blue bars on every logo and brand name. The new
  `tilt_parts()` helper lays a label on a sloping face.
- **Harnesses** (yhz-*): the old ones were thick lilac blocks with straps arched over them. The photos show thin
  contoured flaps lying on the pad. Over them run transverse grey straps with blue edging, which stand up as loops
  at the back, and two striped belts run along the pad across the split. The buckles are now drawn.
- **Halters** (yz-*): the photos show two parallel vertical cables from two pulleys that sit side by side at the
  arm end. The model had a V of cables from pulleys placed one behind the other. Each hook now carries a side strap
  down to a junction. From there a chin band and an occiput band form a cradle with blue edging. White pentagon
  pads sit at the lower corners.

## Per device
- **yhz-iaj**: the pad was too pink. It is now a dusty mauve `#ab8fae`, as in the photo. The tray split moved left,
  as in the photo. The harness was redrawn: thin flaps, standing strap loops, belts across the split, dark green
  buckles. The straps along the pads were rerouted: one runs along the back edge, the other runs from the front of
  the end into the harness. The control panel is more teal. The sticker is white with text lines. Cannot match: the
  small panel lettering.
- **yhz-ii**: the console logo is now real letters, and the panel colour is a softer blue. **Foot-end leg frame**: the
  model had a 4-leg box frame. The photo shows one end frame: a leg at each end corner, a low cross stretcher, and a
  middle post up to the beam. **Knee rest**: it was a thick block on a closed chrome loop. Now it is a thin black
  board hanging from the apex of the bow. Each side has an inclined tube from the end corner up to the apex and a
  short strut down to the tray. H 1055 → 1110 so the apex sits above the console, as in the photo. The harness is
  now the photo's periwinkle cross straps. The hand controller is white with a blue key face (one orange key).
- **yhz-ii-microwave**: the pads are darker green `#4c7a2a`. The black X of straps was replaced by the photo's
  harness: two padded green belts with dark loops. **Hood**: it was too low and too short, and the panel was on the
  wrong face. It now rises higher (H 850 → 900) and is longer, and the blue panel lies on the big front chamfer. The
  panel layout follows the photo: label, a row of LED windows, keys, a red line, a text strip. A white apron under
  the hood was added, and the skirt is a bluish grey `#bdc4d3`. The logo is real letters laid on the sloping front
  panel. The dashes on the straps are now spread along the whole strap.
- **yhz-iv**: the pad was lavender-pink; the photo shows blue-lavender `#a3a8d6`. The console panel is dark slate,
  as in the photo, not bright blue. The end housing was a deep tapering loft; it is now a shallow rounded housing
  under the tray. The knee rest, bow, harness, hand controller and logo were changed as on yhz-ii (H 1115).
- **yz-2a**: the arm loops are lower (650 → 610). A grey board now shows behind the backrest. Side stretchers were
  added on both sides. The pole carries the chrome hanging weight on a third cable beside it (the photo's
  "sleeve"); it used to be a fixed sleeve on the pole. The pulleys are metal. The spreader hangs at the photo's
  height (top at ~1520). The halter is redrawn as above.
- **yz-3**: the blue motor box was a big block above the armrest. It now hangs on the outside of the left armrest,
  with its top at the armrest. The spreader is the photo's black flat plate with chrome bolts. Crossing front straps
  were added to the halter.
- **yz-4**: the logo is real letters and the logo blue is more violet. The massage balls are bigger (62) and closer
  together vertically. The pulleys are side by side at the arm end, which reaches to the left. The halter now has
  crossing front straps.
- **xy-k-rxqy-iii**: the dark front panel of the console was off-centre to the right; it is now offset left, as in
  photo 2. The console pulleys turned the wrong way (axis x → z). The coat-hanger is now across the table: narrow in
  the elevation, wide in photo 1. The traction rod was too long; it is now short, with a spring and a fork. The
  boards and pads were too thin. The boards are now white and thick under thin blue pads, and the long pad starts
  ~150 in from the frame end, as in photo 2. The wedge was a trapezoid; now it is a tall triangle with a rounded top.
  **Feet**: each leg was one tube bending outward plus a splayed strut. Now both tubes of the twin leg go straight
  down and bend at the floor along the length, one to the front and one to the back, each to a levelling foot.
- **xy-jzjy-iii**: "XIANGYU MEDICAL" on the plinth and up the console column is real letters with the end triangles.
  The shroud has the 翔宇医疗 logo. The main top is thicker (top 760), as in photo 2. **Leg mechanism**: it was a
  big slab with the roll above the pad end. Now, from photo 2, the pad is tilted 26°. Under it is a white side-plate
  housing that rises into an end block carrying the black calf plate. The knee roll (Ø180, black end discs) sits
  over the pad end on grey ears, and a white beam runs from the housing to the shroud. The monitor is turned ~40°
  towards the table, as in photo 2. Console back: the C wall with the raised panel was kept (it matches the photo).
  Cannot match: the bellows' fine pleats are drawn as ribs.
- **xyq-1**: the leg slot is longer (from ~150 to ~840 above the foot end), as in the photo. Kept: the 72° tilt, the
  grey base, the wood tray and the foot plate.
- **xyq-2**: the slot was changed as on xyq-1. The long black rod from the tray bracket down behind the board was
  missing and is added. Kept: the 50° tilt.
- **xyq-3**: the lectern stood on a chrome V. The photo shows a chrome U frame lying on the lectern's back: side
  tubes, a top bar and a middle bar. Links go from it to hinges on the board sides, with black knobs, plus a middle
  knob. The slot was changed as on xyq-1. Kept: the 35° tilt and the column console.
- **xyq-5 / xyq-6**: the lifting frame had big crossed scissor bars, which the photos do not show. They are removed:
  the frame rises on the four yellow-capped posts, with the black actuators inside. "XIANG YU" is real letters. The
  tilt actuator was a thick cylinder from the middle to the upper board. Now it is a slender black rod from the lift
  frame to the board low near the pivot, as in the photos. On xyq-6 the console panel is light grey with red LEDs (it
  was teal). Kept: the 62° tilt. Cannot match: the pedal mechanisms under the green covers. They are simplified
  boxes, because the photo shows them only as a blur.
- **tms-special-bed**: the floor frame was a long flat ladder that ran under the leg section. The thumbnail shows a
  compact, deep box frame under the seat and back only. The leg section is cantilevered on a short chrome strut with
  a cross rod and a black knob, and a vertical post rises at the back end. The half-disc ratchets had the flat side
  down, under the joint line; now the round side is up and they have hubs. The steel is lighter. Cannot match: the
  photo is a 640 px blurred thumbnail, so the lift linkage is only a reading of it.
- **tms-treatment-chair**: the plinth was too tall and box-like, and it filled the whole length. In the photos it is
  a low rounded white body with a dark gap under the upholstery. It sits under the seat and back only, so the leg
  rest is cantilevered, and it flares out to the cyan line. The castors are inboard. The logo is a smaller blue
  roundel. Kept: the reclined pose of photo 1 (H 900). Cannot match: photo 2's rear hump, which belongs to the
  sitting pose. The Sunnyou word under the logo is too small to letter.
