# kinesio-8: detail review against the catalogue photos

All 14 devices were reviewed. Every `.txt` is `ok` and newer than its json. Fixes were made in the generators
(`tools/medical/gen/k8_*.py`), which were then re-run. Compare sheets are at `tools/medical/renders/<id>-compare.png`.
Scratch files are in `tools/medical/scratch/k8r/`:
- `run.sh <id>…` regenerates the designs, waits for the renders and builds the compare sheets.
- `crop.py` and `px.py` crop the photos and sample their colours.

`k8lib.py` gained `dumbbell_round()`, a vinyl dumbbell with lathed, rounded heads. It is used by xyt-3 and xyyl-1.

Sides were read from the photos with the vanishing directions of the frames, because the angle camera is always
front-right. Sizes changed only for xyn-4 and xyn-7 (see below).

**Wood.** The photos of xyn-2, xyn-3, xyql-1 and xyzl-1 show plain lacquered wood or plywood. The `wood#` material
rendered grainy and striped. These parts now use `plastic#` honey colours sampled from each photo, and the handles
use `gloss#`.

## xym-6: pedal exerciser
- **Heel cups.** They were solid blocks with a dark inset. Now each is a black wall hanging under the outer edge of
  the pedal. It has a real oval slot through it (a slab outline with a hole), a lip curling inward at the bottom and
  a fold at the top.
- **Arch.** The legs were too shallow (about 50°) and the flat top was short. The legs are now steep (about 64°) and
  the flat top is about 60 % of the span, as on the photo.
- **Cranks.** They were too short (1.8 × the hub radius against about 2.4 on the photo). They are now 155 long and
  tilted 28°, which still fits the printed height of 410.
- Cannot match: the small rubber texture of the pedal plates.

## xyn-2: wrist exerciser (arc)
- **Plank.** It looked like grainy striped boards. It is now plain honey (`plastic#e2bd5c`) with an orange edge band.
- **Handle.** It was red-brown and hung off-centre. It is now orange-brown gloss, hangs at the exact top of the arc
  (as on the photo), is longer (140) and has a narrower neck under the ring.

## xyn-3: wrist exerciser (zig-zag)
- **Wire.** The left leg was traced almost straight. On the photo it kinks out to the left above the foot and then
  runs diagonally to the first peak. The drop after that peak is vertical. The trace was corrected.
- **Plank.** Now plain honey with an orange front edge, no grain.
- **Sticker.** It was a decal on the front edge. It is now a round white and blue sticker on the top surface at the
  right end, as on the photo.

## xyn-4: wall pulley exerciser
- **Width.** The drawn parts spanned about 330 inside the printed W 430. The roller, pulleys and rings now follow
  the photo:
  - roller 250 long, pulleys 210 apart
  - **size W is now 350** so that it covers the model, centred
- **Sleeve.** The sleeve that clamps the post to the rail sat too high (615–880). It is now at 520–780 with its knobs
  at both ends, as on the photo.
- **Ropes.** They now slant toward the wall as strongly as on the photo. The rings hang at z 150 and 185, at
  different heights.
- **Bolt.** A bolt head was added on the arm above the roller.
- Cannot match: which way the ropes slant (toward the wall, or sideways) is ambiguous on the photo. The wall reading
  was kept.

## xyn-6: elastic fingers exerciser
- **Board.** It was a thick puffed cushion standing about 46 above a rim that sloped up toward the front. On the photo
  the pad is thin and lies in a level white rim tube. The board is now a thin pad with large rounded front corners
  inside a level rim, and the cord grid starts at the pad.
- **Hooks.** The white loop tabs at the top of the cord pairs were thin pins. They are now visible white tabs.

## xyn-7: over-door pulley
- **Proportions.** These were measured on the photo (1.45 mm/px over the full 1160):
  - bracket 330 wide, apex 116 below the top
  - pulley Ø60 centred 200 below the top
  - stirrups 95 × 116, side by side and offset about 40
  - **size W is now 380** (printed 430), covering the drawn parts
- The stirrup on the left lies in front and lower. The grips are plain orange gloss. A dark foot was added at the
  lower end of the door bar.

## xyql-1: multifunctional standing frame
- **Layout.** The photo is taken from the front-left, so parts further forward appear further to the right. After
  correcting for that:
  - The **cabinet** is about 430 wide and 200 deep, at x 40–470.
  - The **floor plate** is narrower (about 420) and sits off to the right, from 95 to 515. Its left edge is about 55
    in from the cabinet's side and its right edge runs past the cabinet. It now has white side rails with black
    front caps.
  - The **tray** has no overhang on the left at the back and runs about 270 past the cabinet on the right, from
    70 to 740. It has a rounded back-left corner.
  - The **cut-out** at the front of the tray is centred over the plate.
  - The **raised grey pad** is on the right part of the tray, not across the back.
  - The **knee and shin pads**, side arms and gas spring are centred over the plate (x 300). The shin pad sits in
    front of the knee pad.
- **Knobs.** The left knobs were moved to the photo's heights: 1110, 750, 490 and 250.
- **Right grip.** It sits just past the cabinet's right side, under the tray.
- **Plywood.** Now plain (`plastic#c99c69`).
- Cannot match: the exact depth of the tray. The photo's perspective cannot be fully resolved, so it is an estimate.

## xyt-2: hydraulic step trainer
- **Linkage.** The cylinders were mounted 210 behind the front pivot and leaned about 28°. On the photo each black
  cylinder stands on a white bracket at the front end of its pedal arm (with grey bolts), almost upright. Its chrome
  rod rises to the end of the cross plate under the column top. Both are now drawn that way. The cylinder body is
  0.62 of the length.
- Already matching the photo: the U foam rail, the A strut, the bowed front foot, the left pedal down and the right
  one up, and the LCD.

## xyt-3: step trainer with twister
- **Dumbbells.** The hex dumbbells (head Ø46) are replaced by rounded vinyl dumbbells (head Ø60, length 165), closer
  to the holder, as on the photo.
- **Handlebar.** The horns flared outward at the tips. They now run out from the clamp, rise, and lean back in
  toward each other, as the photo's lyre does.

## xyx-1: seated lower-limb exerciser
- **Mechanism.** The photo does show it. It was redrawn:
  - The **floor beam** is level on the floor (it used to rise toward the box) and runs into a notch at the bottom of
    the seat box.
  - The **brace** runs from the column (about 620) down to the beam, with two bolts.
  - The **swing lever** hangs from an arm at about 880.
  - The **footplate bar** runs from the lever's lower pivot back into the box above the beam. The two footplates
    (with side knobs) sit on a carriage on this bar.
  - The old link and the carriage on the floor beam were removed.
- **Seat box.** On the photo the rounded edge is the **top-rear** one. The model had it at the top-front, so it was
  flipped. The opening is a tall dark slot low on the front face, with an arched dark opening on each side, as on
  the photo.

## xyyl-1: dumbbell rack
- **Dumbbells.** The hex dumbbells were replaced by rounded vinyl ones (lathe profiles), keeping the photo's colour
  order. Length runs from 165 to 261.
- **A-frames.** On the photo the legs land near the ends of the cross tube, so the bottom spread was widened from
  ±120 to ±165.

## xyz-5: folding walker with front wheels
- **Front wheels.** On the photo they are mounted on the **outer** side of the front legs, on an axle through a small
  bracket. The model had them centred under the legs in a fork. They are now outside the legs. The legs moved in to
  x 40 / 560, so the wheels stay inside W.
- No other differences: the rear legs lean, and the grips, cross bars, side braces and telescopic legs match.

## xyz-6: walker with seat
- **Bag hook.** The photo is taken from the rear, so the frame on the image left is the +x one. The hook hangs under
  that frame's grip. The first pass had it on the −x side, and it was moved.
- No other differences found at the compare scale: the teal frame, backrest bar, seat, braces, white wheels and tips
  match.

## xyzl-1: four-person standing frame
- **Hip slings.** They were stiff tilted slabs. Now each is a soft band:
  - 230 high, hanging from the two posts in a U loop out of the bay
  - sagging 160 at its outer part, down to just above the knee pad
  - a folded cuff along its top edge
- How the slings are built: 14 pieces per sling. Each piece is a front-plane slab drawn as a sheared quad (vertical
  ends, with its top and bottom edges following the sag) and then turned about y onto its chord. This adds about 112
  parts.
  - A wide `strap` was tried first. Its normals point along the strap's width, so it shades light on top and dark
    below.
  - Turned boxes were tried next. Rotating them tilts their ends, so they look like a fringe.
- **Slings and top.** The slings are glossy blue (`leather#`), as on the photo. The wood top is plain
  (`plastic#d49d72`).
- Cannot match: the outward flare of the top rim. That needs a band twisted along its length, which the format
  cannot do without a shear plus a turn about a non-axis line.
