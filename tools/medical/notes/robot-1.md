# Batches robot-1 and robot-2: 17 rehabilitation robots

The designs are in `Assets/House4696/Resources/Medical/Designs/<id>.json`. Each was written by a generator, so it
can be regenerated:

| generator (`tools/medical/gen/`) | devices |
|---|---|
| `r_lib.py` | shared helpers: the hanging harness, swivel hooks |
| `r_bws.py` | xy-k-e2, xy-k-e3, xy-k-g2, xy-k-g3, xy-k-g6, xy-k-g7 |
| `r_portal.py` | xy-k-m1, xy-k-m2, xy-k-m3, xy-k-m4 |
| `r_sdk.py` | xy-r-sdk-i, xy-r-sdk-iv |
| `r_sky.py` | smart-sky-track |
| `r_llrs.py` | lower-limb-rehab-system |
| `r_ulr.py` | upper-limb-rehab-robot |
| `r_ulw.py` | upper-limb-rehab-workstation |
| `r_tms.py` | tms-navigation-robot |

All 17 render `ok`. The final check for each device was made on a fresh compare sheet after its last edit.

Render axes, checked on the first render:
- **front**: x increases to the right.
- **side**: seen from +x, so the front (z = D) is on the left.
- **angle**: seen from the front-right, the same viewpoint as most catalogue photos of the BWS frames.

## Size changes

| id | inventory | design | why |
|---|---|---|---|
| upper-limb-rehab-workstation | 650×550×1850 | 650×560×2250 | The photo shows a portrait monitor about 1 m tall (~46–50"), from ~1240 to 2250. The inventory assumed 32". |
| xy-k-m1, xy-k-m2 | W 2400 | W 2000 | Post spacing and cantilever were measured against the post height (2400): posts ~1260 apart and the beam ~600 past the right post. |
| xy-k-m3 | W 1300 | W 1200 | The arch's clear width (~960) is measured against its height. |
| smart-sky-track | 650×330×1500 | 560×820×1500 | The spreader bar hangs ACROSS the rail (photos _2/_3), so the rail runs along z. The head is ~420 wide × 800 long × 280 high (photo 1 end:side ≈ 0.5), and the spreader is ~520. |
| lower-limb-rehab-system | H 750 | H 1300 | It is drawn in its horizontal rest pose. The control pole with the monitor at the foot end reaches ~1300, and the harness frame ~1080. |
| tms-navigation-robot | 900×1300×1950 | 900×1000×1972 | The arch profile was traced from the side photo: reach ~975, top 1972. The arch is 480 wide and the host cart (x 540–890) stands beside it. The patient chair or wheelchair is not part of the model. |

## The BWS mobile frames (r_bws.py)

Common parts, from the photos:
- Two long leg tubes run forward from a rear crossbar, with an open front.
- At each side, the crossbar rests on two parallel inverted-U riser tubes bolted to the leg (bolt plate).
- Braked castors sit at both ends of each leg, with dark end caps.
- The column stands at the back centre. The control box with the blue label is on its +x side (photo: right of the column), with a white foot block on its −x side.
- Handrails: a clamp on the column front, a crossbar, and two black foam handles pointing forward. The near handle looks short in the photos only because of foreshortening.
- The top bar reaches forward from the column top. Its ends carry the hooks, and the harness hangs about 450–500 in front of the column.
- Harness: on each side, two straps (one down, one crossing), a padded vest with two black bands, a buckle on the pelvic belt, and two leg loops with pads.

Per device:
- **xy-k-e2**: done.
  - Top: two 50×50 square arms in a shallow V, with black square end caps.
  - Column: white outer section; chrome Linak actuator on the front face; blue scale on the right face; navy collar; chrome inner stage with a white top.
  - Black gas strut. Slate-grey vest.
  - Approximate: the top's exact plan shape. The photo reads equally as a V or as a U; it is drawn as a V.
- **xy-k-e3**: done. The photo shows the same frame as E2, so the design is identical. The treadmill sold with it is
  a separate entry and is not drawn.
- **xy-k-g2**: done.
  - Legs: navy, with white risers and crossbar.
  - Column: white, with a navy collar, chrome actuator rods, a blue scale and a blue pendant on a cable.
  - Handrails: black knobs on the clamp, white end rings on the handles.
  - Top: a flat white bar bent in plan into an arc, with a short tail behind the column. The dark-grey pulley housings stand on its ends, with the hooks under them.
  - Vest: grey, with a red buckle.
- **xy-k-g3**: done. The same frame as G2, with:
  - Dark graphite legs, a lavender vest, and a blue label on the top bar.
  - The treadmill sold with it is not drawn (separate entry).
  - Approximate: the dark collar block on the column is drawn the size of G2's. The photo shows it slightly bigger.
- **xy-k-g6**: done.
  - Base: navy U with short risers.
  - Column: a tall white housing 260×200 up to 1300, with the green display head showing the operation-panel picture (`print med_xy-k-g6_screen`) and a green edge stripe.
  - Two blue pendants on coiled black cables.
  - The slot has two chrome guide rods and a lead screw. A white handrail carriage carries the black handles.
  - A narrower white upper column carries the V top with cream pulleys.
  - Two ropes run up from the column pulleys and down to the springs and hooks.
- **xy-k-g7**: done.
  - Base: white-grey, with round-tube risers.
  - Column: brushed aluminium in two telescopic stages, with a gas spring.
  - A white display box with a light LCD and icons.
  - The white upper housing tapers outward towards the top.
  - Top: a white arc bar with end blocks.
  - Handles: J-shaped black handles (sideways, forward, up) on a clamp with knobs.
  - A bulky black vest at ~1330.
  - Approximate: the photo shows only the right handle. The left one is drawn by symmetry (the form text says "handrails").

## The portals (r_portal.py)

Common parts:
- Posts are 120×100. The white upper part and the dark lower part meet at a slanted split that is higher on the inner side.
- Feet: A-shaped dark plates on levelling feet (castors on M3).
- Corner plates are chamfered on the outer side, with gussets on the beam sides and bolt heads.
- Hoist: a cable to a cream ball, a chrome spreader with two hooks, and a black harness.
- A blue control panel on the post front, with its cable running to a white floor box with knobs.
- Blue scale strips.

Per device:
- **xy-k-m1**: done. Two stations: one between the posts, and one on the cantilever past the right post. Each post
  has a panel and a floor box; the scale strip is on the right post.
- **xy-k-m2**: done. The M1 frame plus the two machines the size includes:
  - Under station 1, a dark-bronze rehab treadmill: deck, motor hood, curved uprights, console with an LED window, front loops, and parallel handrails with chrome rails and knobs.
  - Under station 2, an upright bike lying along x as in the photo: silver flywheel housing, black frame, saddle and handlebar.
  - Approximate: the treadmill console is a tilted black box, not the moulded hood. Both machines are simplified.
- **xy-k-m3**: done.
  - Single arch, dark lower parts, castors on the feet.
  - Black handrails on clamps with knob locks point inward from each post, as in the photo.
  - Scale labels on both posts, a panel on the left post, a floor box.
- **xy-k-m4**: done.
  - Single arch, 1400 wide, with dark-teal lower parts. The split is low, at ~650, as in the scene photo.
  - A grey pneumatic control unit with a gauge window and a knob on the right post; an air cylinder at the cable exit.
  - Approximate: there is only an in-use scene photo, so the left post and the floor are hidden. No floor box or left panel is drawn. The treadmill and step blocks in the scene are not part of this entry.

## The walking robots (r_sdk.py)

Same chassis for both:
- Base: a low U, open to the front. Brushed skirt with a white top plate; foot-rest humps on the arms; castors at the front tips; black drive wheels at the rear.
- Tower:
  - The body is a brushed loft.
  - Its front is a white glossy band with the dark slide slot and a light-blue LED line around it.
  - An S logo on both side shells, drawn with `text()`. On the right face the S is drawn turned over so that it reads correctly from outside.
- Screen: a 10" screen on a stalk facing the patient, tilted back 12°.
  - It has a white case, a dark bezel and a blue UI with white tiles. There is no screenCrop, so the UI is boxes.
- Handle wings: grey, with oval rims, black joysticks, and red e-stops on yellow rings.

Per device:
- **xy-r-sdk-i**: done. A carriage in the slot carries a silver arm, a white joint, and a silver cross arm with SUNNYOU
  lettering and a yellow warning label. The black pelvic cuff (Ø420, 690–960) has straps and a buckle.
- **xy-r-sdk-iv**: done. The pelvic module has:
  - A carriage box and an arm.
  - A crossbar with a white hub and a knob.
  - Elbows and telescopic side arms reaching past the hips, with black clamp pads.
  - Black padded pelvic shorts with bands.
  - The mannequin and the VR headset are not drawn.

## smart-sky-track (r_sky.py)

Parts:
- A rail section along z with the trolley slot.
- Head:
  - The ends and the bottom lip are a warm-grey core, and the middle is a white glossy body.
  - Each end has a recessed dark grille with ribs, a white lower plate and a green LCD strip; one end has a yellow warning label.
  - On the side: the grey line with blue end segments, a light text line, and SUNNYOU lettering on the −x side (the side that reads correctly).
- Below the head:
  - A grey webbing strap with a buckle down to a white connector.
  - The white spreader with its grey frame and C handle.
  - A white handheld remote with 8 buttons and a screen, on a coiled white cable.
  - An emergency pull cord with a white handle, and the grey-brown training vest.

Doubts and limits:
- Mount: the inventory marks this device `ceiling`, but MedBuilder offsets only `wall` devices. The model is built from the floor up, with the rail top at 1500, so placed in a room it will stand on the floor. Hanging it from the ceiling needs an engine change, which is outside this batch.
- The text line "Dynamic Body Weight Support System" is a grey bar. The font has no lower-case letters, and it is too small to read at 2 m.

## lower-limb-rehab-system (r_llrs.py)

Done. It is drawn in the **horizontal rest pose**: the size describes that pose, and a tilted table does not fit a
room footprint. The catalogue photo shows it tilted with a patient.

Parts, from the photo:
- A white base frame on 4 castors Ø100.
- A scissor lift with grey actuators.
- A white table frame. The side panel on the leg section carries the blue cross logo, 翔宇 and XIANGYU.
- A grey brushed leg plate and a sky-blue 3-segment mattress with a pillow.
- Foot end:
  - A white housing wedge and a blue foot block.
  - Two black foot plates on carriages with toe and heel straps. They ride chrome guide rods with springs and chrome stepping rods, and stand at different steps.
- Two black knee cuffs with straps on chrome arms.
- At the head end, a chrome H-frame with the shoulder straps, plus a chest vest and a pelvic belt.
- At the foot end, a white control pole with a black monitor tilted up, a hand pendant and an encoder box on coiled black cables.

Approximate:
- The scissor linkage and the stepping drive are simplified.
- 医疗 is not drawn, because the stroke font only has 翔宇.

## upper-limb-rehab-robot (r_ulr.py)

Done. Layout from the photo: the patient faces +z; the column stands at the +x rear; the exoskeleton is in front of
the patient's right (−x) side.

Parts:
- A white L floor frame with 4 castors.
- A brushed telescopic column in 2 stages.
- A tall white box (1060–1380) with a grey end cap.
- A white boom to a chrome post with a black knob, and a tilted plate.
- The exoskeleton: shoulder joint boxes, two parallel links with a spring, an elbow box, the forearm, a black forearm cuff with a strap, a grip frame and a black vertical grip.
- An egg chair:
  - A rounded white bowl and a back curved in plan.
  - Side walls whose rim slopes from 1030 to ~650, with grey armrest strips and screws, and a seat cushion.
  - A chrome gas lift, foot ring and disc base.

Approximate:
- The exoskeleton joints are boxes and bars; the real joints are machined.
- The chair is assembled from a loft and slabs, so it is less smooth than the moulded egg shell.

## upper-limb-rehab-workstation (r_ulw.py)

Done.
- A white base plate on castors Ø75.
- A narrower white cabinet:
  - Two shelves and a diagonal plank across the open front, from top-left to bottom-right as in the photo.
  - A vent slot on the right side.
- On the top:
  - A raised deck with the laser printer at the front left, with its slot, vent and green label.
  - A side tray on the right with the mouse pad, keyboard and mouse.
- A square white pole at the rear left with a black VESA bracket.
- A portrait monitor 590×1010 with a black bezel and a light UI with coloured app tiles. There is no screenCrop, so the tiles are boxes.

## tms-navigation-robot (r_tms.py)

Done.
- The C-arch is one side-profile slab (traced from photo _2), 480 wide.
  - It stands on a plinth with 4 small castors.
  - A blue accent line runs along the outer edge on both sides; a red e-stop sits near the top.
  - Perforated grilles are low on both sides.
- On the inner (front) face of the column:
  - A blue S logo with SUNNYOU 翔宇.
  - A white hatch with a grip, and a button.
- A depth camera sits under the arch tip.
- The white 6-axis cobot is drawn as 5 cylinder joints and links. It holds the coil holder and the ring coil, and the grey coil cable runs down to the cart.
- The host cart beside the arch (+x):
  - A dark cross base on castors and a black column.
  - Two light boxes with vent fields, and an LED panel.
  - A dark tray with a keyboard and a red e-stop.
  - A white monitor with a blue header and an orange brain image.

Approximate:
- The cobot pose is compact. In the photos it is more stretched, in an elbow-up pose.
- The arch's x width is estimated from the 3/4 photo.
