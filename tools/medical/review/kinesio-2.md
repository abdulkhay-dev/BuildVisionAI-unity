# kinesio-2: detail review against the catalogue photos

All 14 devices were reviewed. Every `.txt` is `ok` and newer than its json.

- **Where the fixes are:** in the generators `tools/medical/gen/k2_*.py`, which were then re-run. `k2lib.py` gained
  `text_side()`, which draws side-face lettering readable from that side, with an optional baseline slope.
- **Scratch:** `tools/medical/scratch/kinesio-2-review/`.
  - `run.sh` regenerates a design, waits for the render and builds the compare sheet.
  - `rectify.py` straightens a skewed screen photo.
  - `*.orig.*` are the files as they were before this review.
- **How the camera side was read:** from the photos (which faces and which side items are visible), and compared
  with the angle render (front-right) and the side render (right side).

## Needs a Unity asset refresh (focus the editor, or Assets → Refresh)

Two screen pictures were replaced. Each was straightened (perspective-corrected) to the screen's own outline, then
written the way `textures/screens.py` writes it:
- the albedo in `External/Materials/med_<id>_screen/`,
- the crop in `tools/medical/reference/<id>_screen.jpg`, so a rerun of `screens.py` keeps it.

The MedWatch watcher imports only the design json, so Unity has not reimported the textures yet. Until it does:
- **interactive-training-cart** shows the old skewed TV picture with white corners. The black mask slab that used to
  hide them was removed, because the new picture fills the TV.
- **xy-qjhd-bh** shows the old crop with white corners and a green rim line, and no mask.

After the refresh, touch both design jsons to re-render. The originals are in the scratch folder.

## interactive-training-cart

**Size changed: D 650 → 900.** The photo shows long base rails reaching well in front of and behind the cabinet.

Differences found and fixed:
- **Base.** The model had a 950 × 600 rectangular frame outside the cabinet. The photo has two long flat white rails
  under the side panels, about 2× the cabinet depth. They are joined by a grey front crossbar, with grey end caps and
  castors at the rail ends.
- **Castors.** They were dark; they are now light grey (beige-grey tyres).
- **Side panels.** The model had a full rectangular frame with a diagonal. The photo has a narrow back post and a wide
  diagonal strut with a long slot; the rest is open, so the shelves show through.
- **PC box.** It filled the right half (318 wide). In the photo it is about 190 wide, with a window, ports and a red
  LED. The shelves now run to it (450 wide).
- **Mouse platform.** It was a thin strip. It is now a black mouse platform (about 210 × 180) standing out past the
  cabinet's right side, with a dark pad and the mouse.
- **TV picture.** It was a skewed trapezoid inside a black mask. It is now a straightened picture filling the TV with
  a thin bezel; this needs the refresh above.
- **Logo.** It was moved to the front part of the deck's left face.

The format cannot match: the logo's "翔宇医疗" lettering stays as blocks, because 医疗 is not in the stroke font.

## recumbent-cross-trainer-interactive

Differences found and fixed:
- **Arm levers.** These were the weak spot. The model had two near-vertical levers from a pivot at the shell nose. The
  photos show long straight white levers pivoting low at the front of the arcs and rising back to the user:
  - a black collar,
  - a chrome up-bend,
  - a black grip,
  - a black clamp knob under the bar.

  Photo 2 shows them in two phases: the left lever forward and steep (56°), the right lever pulled back almost level
  (27°) to the hip.
- **Pedals.** Large black plates now hang on black swing arms from an upper pivot, with heel cups. Black link rods
  with chrome eyes run down to the nose crank, as in photo 2. These replace the gas springs.
- **Left arc.** Its floor foot is longer, running back to the front foot, as in photo 1.
- **Shell details.** They were placed from the photos:
  - Left side: the grip slot is high on the rear half, rising to the back. The blue LED dots sit on a dark line under
    it, with the blue mark and name behind.
  - Right side: the LED line is high under the seat, sloping (photo 2), with no slot.
- **Front foot.** It got black levelling feet and a black T-foot.

The format cannot match:
- The linkage is shown at one phase.
- The pivot pins are small stubs, because the real bearings are hidden.

## xy-szld-ia

Differences found and fixed:
- **Console.** It was a small flat plate. It is now a large oval: a white rim shell around a black oval face (slab with
  an ellipse outline), tilted to the user.
- **Floor crossbar.** The front floor crossbar between the arcs was removed. In the photo each arc has its own floor
  run.
- **Side slot.** The slot now slopes down to the front, as in the photo.
- **Logo.** The embossed logo is now a cross in a slightly darker grey, not a plain square.

The format cannot match:
- The arcs' floor loops (a horizontal oval loop) are a straight floor run.
- The levers are simplified (a single low pivot).
- The quilted seat bands are not drawn.

## xy-zbd-ib

Checked part by part: H base, brake rods and pedals, levelling feet, footrest loop, column knobs, hinge, gas spring,
peanut head, grab handle, e-stop, turntable, 3 grips and roller, screen. **No visible difference at the compare-sheet
scale; nothing changed.**

## xy-zbd-id

Differences found and fixed:
- **Foot.** The white loaf foot lay along z behind the column. The photo shows it lying ACROSS the width (two white
  lobes either side of the navy beam), centred under the column foot. It is now a transverse loaf (560 × 240 × 215)
  with a rounded top. The navy beam rides over it on a saddle.
- **Layout.** It was re-measured with the crank disc (Ø230) as scale:
  - column foot at z 215,
  - column top at z 430 (16° lean),
  - head running from z 370 forward to the crank disc at z 760,
  - U handle further back.
- **Head.** It was a short box. It is now a long white body with long navy side panels.
- **Lettering.** "XIANGYU MEDICAL" was a white bar. It is now real white letters on both panels, readable from each
  side.
- **Screen.** It was moved over the column top, enlarged to 270 × 250, and swivelled 68°, so it faces the photo's
  camera (front-right).

## xy-zbd-iid

Differences found and fixed:
- **Curved blue plate.** It was drawn as two flat spider arms plus a column behind the drum. Now, as in the photo:
  - the column stops at the drum's top-back;
  - a curved navy plate on each drum face runs from there round the hub as a ring (a slab with arc outline and hole),
    with a white hub face;
  - the plate continues down-back to the base beam;
  - there is no column behind the drum.
- **Foot.** It is the same transverse white loaf as on ID, and the beam rides onto it.
- **Screen.** It was swivelled 68° to face the camera, and made a little taller.

The format cannot match: the drum's dot pattern is a few decals.

## xy-zbd-iiid

Differences found and fixed:
- **Screen.** It now faces the camera: turned 40° to the left, because the photo is taken from the front-left. The
  yellow label was moved to the bezel's top-left.
- **Leg drum label.** The yellow warning label is now on the left drum face too (the face seen in the photo).
- **Lettering.** "XIANGYU MEDICAL" is now drawn along the sloping navy band of the arm housing on both sides.

The format cannot match: the rear foot tube is hidden in the photo; it was kept for stability.

## xy-zbd-iie

Differences found and fixed:
- **Saddle.** It was a box seen from the side. The photo shows a half-moon from the side (trough axis across x). It
  is now a side-plane half-moon slab.
- **Bed-docking bar.** It was shortened to the photo's extent, with its knobs and the black U handle at the back
  re-placed.
- **Column proportions.** They were measured on the photo:
  - the base housing is taller (310),
  - the blue lower column is shorter (to 690, collar at 690),
  - the steel telescopic part is longer.
- **Screen.** It was swivelled 70° to face the photo's camera (right side).

The format cannot match: the pendulum, knee-cup and crank linkage is shown at one phase. The knee cups are
simplified shells.

## xy-dgdx-i

Differences found and fixed:
- **Lettering.** The grey blocks are now real red letters, "Sunnyou 翔宇", under the red disc logo. The disc has a
  white "S" (p1lib.text). The handle's red root disc got a white "S" too.
- **Screen and arm.**
  - Photo 1 is taken about 57° off the front: the wheel looks nearly round.
  - In it, the screen stands beyond the output (wheel) side and behind the pole, facing the camera.
  - The arm now swings out to +x and back, the screen centre is at x 575 / z 150, and the screen is turned 50°.
    Before, it was over the head, turned 22°.
  - The arm parts were pulled behind the screen face, where they had poked through.

## xy-ph-iv

Difference found and fixed: the backrest is portrait-ish (320 × 330) like the photo, not landscape (350 × 270). Its
chrome mount was lowered.

The format cannot match: the speckled seat disc is plain light grey.

## xy-ph-v

Differences found and fixed:
- **Grip recesses.** In the photo the dark grip recess is in the RIGHT side face near the front corner, not on the
  front face. It is now on both side faces.
- **Rail ends.** Rounded graphite end blocks were added at the rear rail's ends, running down the plinth's back corners
  (photo).
- **Logo.** It was moved back near the rail.
- **Top crossbar.** It got its dark grip on the right part.

The format cannot match: the platform's dot texture is omitted.

## xy-ph-workstation

Differences found and fixed:
- **Glass shelves.** They were opaque teal gloss. They are now translucent dark-teal glass (`acrylic#123a32f4`), with
  dark green glass edges instead of alu strips.
- **Printer.** It was 200 high. It is now about 140 high, measured on the photo, with a dark ribbed output tray in its
  top and the power brick beside it.
- **Software screen.** The blues are lighter, as in the photo.

The format cannot match: the software screen is decals, because there is no screenCrop.

## xy-qjhd-bh

Difference found and fixed: the screen picture. The inventory crop showed a different UI (the English "Interactive
Evaluation System") from the catalogue photo (the Chinese game-card menu). The photo's own display was straightened
and is now the screen picture. This needs the refresh above. The dark mask over the old crop's rim was removed.

The format cannot match: the cabinet's "翔宇医疗" logo stays as the mark plus bars (医疗 is not in the font).

## xy-qjhd-bv

Differences found and fixed:
- **Operator monitor.** It is now turned 25° to the right (towards +x), as in the photo. It has a black thin bezel and
  a light chin, and is larger (360 × 245). Its UI tiles were made to follow the turned face.
- **V bracket.** It turns with the monitor.

The format cannot match: the operator monitor's UI is decals.
