# robot-1 / robot-2: detail review against the catalogue photos (2026-10-03)

Reviewed all 17 devices of batches robot-1 and robot-2. Every `.txt` is `ok` and newer than its json. All fixes are in
the generators (`tools/medical/gen/r_*.py`), which were re-run; compare sheets are `tools/medical/renders/<id>-compare.png`.
Scratch: `tools/medical/scratch/robot-1-review/` (`run.sh <gen> [ids] -- <ids>` regenerates, waits for the render and
rebuilds the compare sheets; photo crops used for the checks).

Sides were taken from the photos with the front/side renders (front render: x to the right; side render: seen from
+x, front on the left). Several photos look from the front-LEFT (G3, M1–M4, the workstation, the TMS robot), so they
show the mirror side of the angle render.

Lettering on a +x face: `p1lib.text()` reads mirrored (or upside down) from +x. Where it is used on +x faces
(sdk "Sunnyou" and S logo, sky-track lettering) the strokes are drawn along +z and then mirrored in z, as
`k1lib.text_right()` does. `r_llrs.py` adds the 医 / 疗 glyphs to p1lib's font itself (t4lib cannot be imported
there: it restores lib's D methods under r_lib's p1lib signatures).

## Size changes (beyond those in notes/robot-1.md)
| id | before | after | why |
|---|---|---|---|
| xy-k-m1, xy-k-m2 | W 2000 | W 2320 | the left floor box stands OUTSIDE the left post in both photos (frame shifted by 320) |
| xy-k-m3 | W 1200 | W 1470 | the same: floor box outside the left post (photo) |
| tms-navigation-robot | W 900 | W 940 | arch widened 480 → 560 (the photo column is about as wide as the cart); cart moved to x 580–930 |

## lower-limb-rehab-system (r_llrs.py)
Fixed:
- **Control pole** stood at the front foot corner; the photo has it at the BACK foot corner, its foot bending into the base rail. Moved and bent.
- **Base**: thin 60 mm rails → heavy 72×70 white tubes with white castor sleeves; grey castor wheels.
- **Scissor lift**: thin bars → wide white arms (80×40) with black/white pivot bosses and bolts, lower slide rails and an upper sub-frame.
- **Side panel**: a 105 mm strip → the deep logo panel (455–655) with a rounded lower end, on both sides.
- **Brand**: a plus-in-a-disc and only 翔宇 → the round blue mark with the white "<" cut, **翔宇医疗** and XIANGYU MEDICAL under it; XIANGYU on the torso frame in dark grey.
- **Stepping drive**: flat paddles on horizontal rods → shell pedals (sole, heel cup, side walls, toe and ankle straps), slate carriages with chrome axles and orange dots, dark V links to a pivot under the leg plate, coil springs towards the head end, chrome guide rods with brackets along both sides.
- **Knee cuffs**: black blobs on posts → wrap-around arch pads with a strap band and a buckle on grey brackets.
- **Encoder**: black box → slate barrel with a chrome nose, orange tip, pistol grip and coiled cable on an arm from the pole; pendant with keys on a cable; monitor with a bezel on a black mount.
- Blue side cushions beside the feet; harness vest buckles.
Format limit: drawn in the horizontal rest pose (the photo shows it tilted with a patient).

## upper-limb-rehab-robot (r_ulr.py)
Fixed:
- **Layout**: the column stood 400 mm beside the chair; in the photo it stands right behind the chair back on the back arm of the L frame, whose front arm runs along the patient's left side (+x). Rebuilt that way.
- **Chair**: a slab assembly → smooth lofts: a domed bowl, the back lofted across x (curved in plan, rounded top shoulders), the wings lofted along z with the rim sloping from the back to the front and a domed front end; grey armrest strips follow the rim, with screws.
- **Chair base**: disc darker (the photo's chrome reads dark grey; the renderer's chrome reads white), chrome lift with a collar, lever, front U foot bar.
- **Column**: 2 → 3 brushed stages with a darker neck and a joint block; the box cap is recessed grey, with a black seam on top.
- **Boom / post**: the post is WHITE with a black cap (was chrome), with a white clamp and a black knob.
- **Exoskeleton**: joint boxes → flat brushed plates with bolt heads (shoulder plate, mid bracket, elbow plate), two round chrome parallel links with link heads, the tilted counterbalance bar with its slot, the elbow motor cylinder with a black connector and cable, the flat forearm bar, the black cuff trough, the black grip with a ball top on a base, and the bent hand frame with its tip joint and cable.

## upper-limb-rehab-workstation (r_ulw.py)
Fixed:
- **Orientation**: the keyboard and the monitor are parallel to the solid face with the black handle slot. So that face is the FRONT, and the open shelves with the diagonal plank are on the LEFT side; the model had them at the front. Rebuilt: a closed front with a handle slot, the right side and back closed, and the shelves and plank on the left side.
- The plank is a slotted frame, as in the photo.
- **Base**: plate on castors → two white rect bars along z with castors at their ends, a white platform and a grey metal front crossbar.
- **Printer**: moved to the back left; light grey body, dark top with the output recess and blue paper, a vent on the left face, the green label at the right of its front face.
- **Top**: a raised deck under the printer with a ramp; the keyboard tray overhangs the front at the right, with a mouse pad, mouse and cables.
- **Screen**: 11 big tiles → the photo's rows of small book-cover tiles (8 + 8 + 2) with captions, a title bar and logo.
Format limit: no screenCrop, so the UI is boxes. The shelves now face −x, so no render shows them, but they are drawn.

## xy-k-e2, xy-k-e3 (r_bws.py)
Fixed:
- **Top frame**: V → U, as in the photos: a crossbar over the column and two parallel square arms forward, with black square caps on the front ends and the crossbar ends.
- The handrail crossbar and elbows are black foam (were chrome).

## xy-k-g2 (r_bws.py)
Fixed:
- **Risers**: raised to ~250 above the legs (crossbar 320 → 420), as in both photos.
- Round blue Xiangyu mark on the front edge of the top bar (second photo).

## xy-k-g3 (r_bws.py)
Fixed:
- **Column collar**: now the photo's big dark block (164×160×140, at 1600–1740) with a steel band above it.
- **Sides**: the photo is a front-left view. The long control box, the blue scale and the pendant are on the column's −x side, so they were moved there.
- Risers raised as on G2.

## xy-k-g6 (r_bws.py)
Fixed:
- **Risers**: taller navy inverted-U risers (crossbar 320 → 400), as in the photo. The rest matched: housing, green display with print, pendants, coiled cables, slot, carriage, pulleys and ropes.

## xy-k-g7 (r_bws.py)
Fixed:
- **Column order**: reversed. The photo has a NARROW lower stage and the WIDER grooved stage above it; the model had wide below and narrow above. The grooves are on the front, the rail/gas spring runs along the right side, and the display box sits on top.
- **Handles**: the photo's handle runs sideways (slightly forward) from a clamp on the column's SIDE face, then bends straight up into the grip. There is no long forward run. Each handle now has a clamp with two knobs plus a knob at the handle root.
- **Left J-handle**: kept by symmetry. The photo shows a matching clamp stub on the left side face, and the handle itself is hidden behind the vest.

## xy-k-m1 (r_portal.py)
Fixed: the left post's floor box (and its cord) moved OUTSIDE the left post, as in the photo; the right box stays on
the right post's +x side.

## xy-k-m2 (r_portal.py)
Fixed:
- The floor boxes, as on M1.
- **Treadmill**: the deck frame is black, not bronze. The console is a wide black visor, arched in plan and wider than the uprights, with a display, speaker slots and a blue logo. The black "ear" handles hang outside the uprights. Red switch and logo on the motor hood.
- **Bike**: the handlebar is lower (~1030), a U bar with upturned grips, as in the photo; the console sits on the stem.
Format limit: the bike is simplified (housing, stem, bars, pedals); its saddle is hidden in the photo.

## xy-k-m3 (r_portal.py)
Fixed:
- The floor box is outside the left post (photo).
- **Scale labels**: narrower, and moved up to 1300–1530, as in the photo (they were tall, at 1500–1820).
- The panel is lower (1150).

## xy-k-m4 (r_portal.py)
Fixed:
- **Left post**: it is visible behind the nurse, so it was checked. Its dark-teal lower part reaches ~830, so the split is raised (620/720 → 760/860).
- **Hoist**: the spreader hangs lower (ball 1950 → 1750), as in the photo. The large air cylinder at the beam is now a small fitting.
Format limit: in-use scene only; the treadmill and step blocks are other entries.

## smart-sky-track (r_sky.py)
Fixed: the side lettering and lines are on the face to the RIGHT of the labelled end in photo 1, i.e. the +x face.
They were on −x. Now on +x:
- "Dynamic Body Weight Support System" (a grey line) near the labelled end;
- the grey line with blue ends;
- "Sunnyou 翔宇" with a sub-line near the back end, reading correctly from outside.
Format limits:
- the long text line stays a bar (no lower-case font at that size);
- the ceiling mount is drawn from the floor up (MedBuilder offsets only wall devices).

## xy-r-sdk-i (r_sdk.py)
Fixed:
- **Pelvic arms**: the photo shows TWO parallel silver arms along z on either side of the cuff, coming from a grey bridge on the carriage. The model had one central arm and a cross arm along x. Rebuilt with:
  - the white joint and the yellow warning label on the −x arm;
  - "Sunnyou" on the +x arm's outer face;
  - cuff mounts between the arms and the cuff.
- **Screen**: the case is light silver-grey (was white). It is ~4:3 with a thick lower border and a bezel. The UI now has the title lines, five white tiles with icons, and a brand mark.
- **Joysticks** are light grey with dark boots (were black).
- The S logo on the +x side read mirrored; it now reads correctly.

## xy-r-sdk-iv (r_sdk.py)
Fixed:
- The screen case and UI, as on sdk-i.
- Joysticks stay black (the IV photos show black ones), with dark boots.
- The S logo on +x now reads correctly.
Not drawn: the mannequin and the VR headset.

## tms-navigation-robot (r_tms.py)
Fixed:
- **Arch width**: 480 → 560.
- **Cobot pose**: from compact to the photos' stretched elbow-up pose:
  - the base hangs under the arch top and the upper arm runs back and down to a tall vertical elbow joint by the column;
  - the forearm reaches forward horizontally and the wrist turns down to the holder;
  - the coil is the flat white figure-8 lying face down (an ellipsoid with a grey face), not a ring.
- **Host cart**: the vent fields are on its FRONT face, as in photo 1 (two big grilles on the lower box, a vent field left of the LED panel); they were on the +x side.
Format limits:
- the arch is one extruded profile, so it does not narrow towards the tip as the moulded arm does;
- the patient chair and the wheelchair are not part of the model.
