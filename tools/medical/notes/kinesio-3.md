# kinesio-3 — 14 kinesiotherapy devices (2026-10-02)

> Detail review 2026-10-03: see `tools/medical/review/kinesio-3.md`. It supersedes the layout notes below for
> xy-13 (no inner frame), xy-14 (layout was mirrored; gallows, tilt board), xy-14-8a (wheel, peg rack, ladder) and
> xy-14-8b (gallows arm, outrigger).

Generators: `tools/medical/gen/k3_*.py`, with shared helpers in `k3_lib.py`. The helpers cover the pulley unit, the
chest-and-back straightener, the wheel, wrist and forearm units, the finger ladder, wall bars, gallows, peg rack,
basketball net, `G` (a module drawn in a turned local frame) and `turn_y`. Every design renders `ok`. For each device
the compare sheet `tools/medical/renders/<id>-compare.png` was read after the last render.

Frame rule:
- Bikes: the front (z = depth) is the end the rider faces (console and handlebars), and the seat is at the back.
  This is the same as kinesio-4.
- Floor-plate devices: the front is the side the user stands on.

The catalogue photos are mostly taken from the front-RIGHT, so the angle render (front-left) shows them mirrored. The
sides follow the photos.

## Size changes (photo vs printed leaflet)
- **xy-12**: changed to [630, **500**, 1800]. The printed D of 200 is the frame only; the two black pedals lie on
  their cables in front of it.
- **xy-13**: changed to [**1400, 1280**, 1800]. The printed 1810 × 1470 does not fit the photo: the cage is clearly
  taller than it is wide. Measured from the 1800-high near post, each face is about 1000–1100. The model has:
  - a 1090 × 950 cage,
  - the pulley unit outside its left face,
  - the wheel unit standing proud of the front.

  The leaflet figure probably includes the working space.
- **xy-14-8a**: changed to [**2350, 1700**, 2390]. As with xy-13, the photos show a ~1160 × 1140 cage, plus the
  wall bars and modules at the side and the gallows overhang. Printed: 3170 × 2450.
- **xy-14**: changed to [**2840, 1360**, 2390]. The 1400 × 1300 cage plus the straightener outside it gives a
  2840-long footprint. Printed: 3170 × 2450.
- All other devices are drawn at the printed size.

## xy-20 / xy-21 — posture mirror (and with grid)
Parts (photo):
- Full-length mirror in a gold/bronze aluminium frame, ~760 × 1760, standing 150 above the floor.
- Two white square-tube A-stands outside the frame sides: a 670 floor tube, two legs meeting at ~520 where they clamp
  the frame, a black knob.
- Four small black castors.
- A low white cross tube under the mirror and a black latch at its bottom right.
- xy-21 only: a light-grey 100 mm grid on the glass.

Final check: frame, stands, castors, cross tube and grid all match.
Approximate:
- The glass is the engine `mirror`, so it shows grey studio reflections instead of the photo's bluish white.

## xy-23 — mini basketball stand
Parts:
- Grey D-shaped floor base (flat back, round front) with a blue label.
- White flat top bar of the same plan.
- Two chrome uprights ~300 apart.
- Black pulley in a chrome fork under the top bar.
- White rope to the board, plus a second strand down to a cleat on the base.
- Orange backboard ~336 × 262 (480–660 high) sliding on sleeves.
- Orange Ø370 hoop with a bracket and 12 hooks.
- Net: white top, red lower half, tapering.

Final check: done. Board and uprights were re-proportioned to the photo; the net is longer and narrower.
Approximate:
- The net is 2 × 14 helical strands (a diamond mesh) and does not gather as loosely as the real one.

## xy-15 / xy-16 — sandbag rack / binding-weight rack
Parts:
- White Ø25 tube trolley. Each side is an S tube:
  - a front leg on a castor,
  - a diagonal rising to the back top,
  - a hairpin bend into the top shelf's side rail, which ends in a black cap at the front.
- A rear U-leg from the lower shelf down to the rear castor, and a rear cross tube.
- Two slatted shelves; the top one is tipped ~7° to the front.
- Four black castors Ø64 and a small blue label on the top front rail.
- xy-15: nine lime-green vinyl sacks per tier with gathered necks and chrome rings at the back top.
- xy-16: seven rows of wrap-around cuffs per tier, made of teal / black / grey pockets, with black Velcro straps
  rising at the back.

Final check: the frame matches the photo, including the mirrored S on the right and the black caps.
Approximate:
- The sacks are puffed boxes, turned a little at random, with crease strips. They are not crumpled cloth.
- The camo print is suggested by alternating pocket colours and a blotch.

## xy-10 — chest and back straightener
Parts:
- Light-blue padded board ~470 wide, from ~620 up to 1880, leaning back ~20°. It is steeper at the bottom (bowed),
  with grey bolts at its lower corners.
- A white rectangular handle loop with two grip bars above its top.
- White Ø25 tube A-frames per side: a post from the rear foot and a diagonal from the plate, both meeting the board's
  bottom, with a cross tube.
- A yellow laminated floor plate 700 × 600 with a white edge, on floor rails with feet.

Final check: done. The plate colour was changed from a wood texture to the photo's honey laminate, and the
non-visible back struts were removed.

## xy-11 — straightener with the wall pulley unit
Parts:
- The same board, A-frames and plate as xy-10.
- Behind them, a 560-wide twin-column pulley tower 2100 high:
  - white cap with a blue label,
  - silver guide rods and white ropes,
  - blue hand ring high on the cable,
  - dark ankle cuffs just above teal disc stacks in white brackets,
  - white base boxes.
- The board's top hangs on two white arms from the tower top.

Final check: done.
Approximate:
- The tower's top frame is simplified to the two arms and a cross tube.

## xy-12 — pulley weight
Parts:
- White top cap 630 × 200 with a blue label strip and logo.
- Per column:
  - two silver guide rods and three white ropes,
  - small grey pulleys,
  - a navy oval hand ring at ~1300,
  - a white U bracket over a teal six-disc stack,
  - a white open base box with black feet.
- A centre post between the bases.
- Two black pedal pads on grey cables in front.

Final check: done (darker openings in the base boxes, smaller pulleys).

## xy-2 — upright bike
Parts:
- Silver stabilisers front and rear with black caps (wheels at the front).
- Oval legs.
- Silver teardrop housing with a darker inset panel, a cyan ring round the crank hub and three cyan stripes.
- Silver cranks and black pedals with straps.
- Curved oval silver column with a black tension knob.
- Small grey console with a blue LCD.
- Black U handlebar with rising grips.
- Black bellows seat post with a silver collar and knob.
- Silver slider with a black knob, black saddle, black carry strap.

Final check: done.
Approximate:
- The console face is a dark plate with one blue patch. There is no screen crop.

## xy-1a — commercial upright bike
Parts:
- Long silver housing:
  - tall front under the console post,
  - level top to the seat tower,
  - tail sweeping down into the rear foot,
  - dark recess behind the cranks.
- Black rubber rear stabiliser ~600 wide and a small black front foot with wheels.
- Black collars at both posts.
- Silver Ø82 console post with a black cup holder.
- Wide console tilted ~40° to the rider: silver bezel, dark face with an LCD and key rows.
- Black handlebars round it with silver pulse grips and rising horns.
- Red-anodised seat post, black contoured saddle, orange knob, black strapped pedals.

Final check: done. The dip in the housing top was removed so the top runs level, as in the photo.
Approximate:
- The handlebar loop is read from one oblique photo.
- The console has no interface picture (no screenCrop), so its keys are decal rows.

## xy-13 — four-piece multifunctional trainer
Parts:
- White 60 square-tube cage 1800 high with feet, an inner post line, an inner top ring and a mid ring at ~900.
- Front crossbars at 830 and 640.
- Twin pulley unit along the outside of the left face: blue rings, dark weight cuffs, teal stacks with red straps.
- Wrist box on chrome rods on the left face near the front.
- Shoulder wheel Ø700 on a sliding carriage standing proud of the front face, on the right. It has a white box, a
  grey/blue hub, a black handle and a grey forearm tray with a grip, all reaching to the right.

Final check: proportions, after the resize, and the module places match the photo.
Approximate:
- Smaller screws and labels are omitted.
- The inner frame is simplified to one post line.

## xy-14-8b — eight-piece trainer with table
Parts:
- White cube frame 2480 on castors, with a wire-mesh roof and a white wire grid on the back face from the mid ring up.
- Mid ring at 1080.
- Twin pulley weights inside the left face, plus a wrist carriage at its front.
- On the back grid:
  - forearm box with a tray,
  - crank wrist box,
  - finger ladder at the right,
  - two black traction slings from the roof.
- Two pulleys on the front top beam with ropes and blue rings, plus a rope ring at the left.
- Low training table 1900 × 650 × 450: three grey padded sections, white trestle legs, two grey belts, a blue label.

Final check: done.
Approximate:
- The small gallows arm outside the top-left corner in photo 1 is replaced by a pulley inside the frame, which keeps
  the printed footprint.
- The roof mesh is drawn coarser (160 mm).
- The upholstery is grey, as in the main photo. Photo 2 shows a blue version.

## xy-14-8a — eight-piece trainer (A)
Parts (photo 1 is from the front-right):
- White cage ~1160 × 1140 × 2000.
- Twin pulley weights with black stacks, cuffs and rings inside the front face.
- Gallows over the front-left post (2390) with two pulleys, ropes and dark-blue rings.
- Tall wall bars (13 rungs, 2390) along the right face.
- Outside the wall bars: a forearm box with tray at the front and a wrist box with a wooden bar in the middle.
- Green peg rack (7 black-tipped pegs per upright) hung on the bars at the back.
- Three-spoke shoulder wheel with its box on the back face.
- Red/green finger ladder next to the back-right post.

Final check: done.
Approximate:
- The photos disagree on whether the boxes and the peg rack are outside or behind the wall bars. All three are put
  outside, spread along the face so they do not collide.

## xy-14 — seven-piece trainer
Parts:
- White cage 1400 × 1300 × 2050. Its left face is the wall bars, with the left posts rising to 2390.
- Grey padded anklebone tilt board leaning on the wall bars inside, with a grey foot cradle (two foot plates, heel
  stops) and white handles with yellow grips.
- Tall white backboard on the back face rising above the top, carrying the basketball hoop and red/white net.
- Red/green finger ladder at the front-right post.
- Twin pulley weights in the front face's right half.
- Gallows with two ropes and blue rings over the back.
- Chest-and-back straightener outside the right face, facing away from the cage. Its board has a black back (photo 1
  shows the back) and a yellow plate.

Final check: done.
Approximate:
- Module places are read from two photos taken from opposite sides.
- About 210 parts; the net and finger ladder alone account for ~60.
