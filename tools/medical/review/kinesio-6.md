# kinesio-6: detail review against the catalogue photos

All 14 devices were reviewed. Every `.txt` is `ok` and newer than its json. Fixes were made in the generators
(`tools/medical/gen/k6_*.py`), which were then re-run. Compare sheets are at `tools/medical/renders/<id>-compare.png`.
Scratch files are in `tools/medical/scratch/kinesio6-review/`. `run.sh <gen.py> <id>…` there regenerates, waits for
the render and builds the compare sheet. Photo crops (`*.png`) are there too.

Sides were read from the photos with the vanishing directions of the frame (floor runners, rails, casters). The angle
camera sometimes shows the other side of a symmetric device, so this was not treated as a difference.
No sizes were changed. xyf-z4 keeps its separate saddle unit (size [1180, 800, 1300], from the authoring pass).

## xyf-t1: two-way wooden stair
Found and fixed:
- **Treads and risers were too grey.** The photo shows a light periwinkle blue (#aac0e6). Changed `rubber#b4c3d6` to
  `plastic#abc1e8`.
- **Handrails were silver.** On the photo they are painted light blue (#97b2cd). Changed to `metal#9fbadb`.
- **Laminate colour.** The beige was a little light and yellow. Changed to #c6ae90, as on the photo.

Still the same as the photo: 4 treads plus the platform, the separate platform module with seams and a label, the
continuous rails with turned-down ends, and 6 posts per side.

## xyf-t2: three-way stair
Found and fixed:
- **Front rails over the front flight** (a named weak spot). The model's rails sloped down the front flight and ended
  in a turned-down tip, with two posts on the treads. On the photo the rail runs **level** over the front flight
  from the platform corner. At the front end it bends **straight down** (about 380 mm of chrome) into one tall post
  standing on the bottom tread. It has no middle post. The model now matches.

## xyf-t3: two-way steel ladder
Found and fixed:
- **Risers were open.** The model had 40 mm lips with gaps. On the photo the near flight's risers are solid, lit
  faces, so the risers are now closed folded sheets running the full rise.
- **Colours.** On the photo the treads are a lighter blue (#b7c8e4) than the lavender stringers and platform box
  (#9093bc). The model used one colour for all. It now has two (`tread` #bccbe8, `steel` #a6a8d4).
- **Platform box was too shallow.** On the photo the steel box is about 200 deep (a third of the 600 height). It was
  120 and is now 190, still on the white tube frame. A tread-coloured deck top was added.
- **Post layout.** The photo has a bottom post and a top-of-flight post next to the platform corner post. The model
  had a mid-flight post. Changed to x = 150 and FL − 170.

## xyf-t4: three-way steel ladder
Found and fixed:
- **Front rails and posts** (the front box steps were a named weak spot). As on T2, the photo's front rails run level
  over the box steps and bend down into a tall front post on the lowest step. Each also has a post on the platform's
  front corner. The model had sloping rails with a post on each step.
- **The platform was a full box to the floor.** On the photo it is a ~200 sheet-steel box on the white tube frame,
  with a white leg showing beside the steps. The box steps (rise 200, 220 deep, lipped tops, seams) stand in front
  of it.
- **Closed risers and post layout**, the same fixes as T3.
- **Sheet colour.** Brushed `metal#c4d8ec` rendered teal-grey. The photo shows painted light blue (#bbd0eb), now
  `plastic#b6cbea` / `#bdd0ec`. The rail blue is now #7fa6d6.

## xyf-z1: forearm walker
Found and fixed:
- **Cushion shape** (a named weak spot). The photo's pad has big rounded ends and a clear, rounded rectangular notch
  at the back middle. The model had small corner radii and a shallow curved dip. Now: plan corners of r 110, a
  notch 300 wide and 55 deep, and a thick rounded edge (r 20 on 50).
- **Grips were too short.** On the photo they stand about 160 above the pad. They were 125.
- **The telescopic joint and blue knob were too low.** On the photo they are just under the pad, at about 84 % of the
  post. They were at 72 %.

## xyf-z2: walker with brakes and seat
Found and fixed:
- **Brake levers** (a named weak spot). The model's levers were tubes hanging forward and down from the grip top. On
  the photo each lever pivots in a black housing at the **foot** of the grip. Its blade rises in front of the grip and
  curves away from it, to about two-thirds of the grip height. Now: an oval-section `sweep` blade and a housing.
- **Cables** (a named weak spot). On the photo they bow wide **outside** the frame and come back to the base arm at
  the post foot, then run along the arm to the rear castor. The model's cables ran inside the frame to the castors.
  They now follow the photo.

## xyf-z3: walker with wooden forearm rests
Re-read from crops of the photo, which is taken from the user side (back-left).
Found and fixed:
- **Base tubes** (a named weak spot). On the photo the front cross tube of the floor U is at **castor height**, with
  castors under its corners. The model raised it to 270 in a loop. The model's extra low cross at the uprights is
  not on the photo and was removed.
- **Front posts with red legs** (a named weak spot). The photo shows **one** central post: a white square upper tube
  from the rests' cross bar down to a clamp on the front of the mid U, and a red square telescopic leg below it
  ending in a black cap just above the floor. The model had two round posts, and they are now one. The mid U is now
  closed at the post line (z = depth − 170), and the rests' cross bar is at the same z.
- **Carved armrests** (a named weak spot). On the photo they are thick (~60) varnished boards. The straight outer
  edge was kept. The inner edge is now carved as a long concave scoop between a wide front (grip) end and a narrower
  horn at the user end. It had been one small notch at the back. The brackets and knob were lowered under the
  thicker board.
- **Red wheel hubs** (a named weak spot). On the photo the castor wheels are red discs with a dark tyre rim. The model
  had small red dots off the wheel centre. They are now 58 mm red discs on the wheel's real centre (the trailing
  offset of the engine's castor).

## xyf-z4: walker + separate saddle unit
Found and fixed:
- **Top side rails.** On the photo they are **flat grey steel channels** (on edge) with black knobs, reaching past both
  legs. They were blue round tubes.
- **Thin chrome rods beside the legs.** On the photo they reach down to the mid rail and hook into the leg at the
  top. In the model they were short, straight and floating.
- **Colours.** The photo's tubes are a darker steel blue (#556682), now #58719e. The walker's pad is a lighter blue
  (#88a2cc), and the saddle pad is a darker blue (#46588a). The model had used one lavender for both. Each now has its
  own colour.
Not matched: on the photo the saddle unit stands in front of the walker's closed end. In the model it stands beside
the walker (+x), so the item keeps a compact footprint. Its parts and orientation (back pad toward −z, hooks at the
front) match.

## xyg-1: parallel bars with correction board
Found and fixed:
- **Wedge board** (a named weak spot). On the photo the board fills the walkway between the two post lines. It is a
  flat lower board with a wedge on top that rises toward the front rail. The lower board shows as a step in front of
  the wedge, and the wedge's right end is bevelled. The model's board was 400 wide in the middle. It is now 655 wide
  (z 250–905), with the wedge from 40 to 100 high. The bevel is drawn as 4 strips, because a slab takes only one
  outline.
- **Board colour.** The photo's board is smooth light laminate. The `wood` material drew plank stripes, so it is now
  satin #d9b07a / #e2bd88.
- **Rail colour.** The photo's rails are painted light blue, and the model's brushed metal looked silver. Now
  `plastic#a3bce2`.

## xyg-2: parallel bars
Found and fixed:
- **Rail colour.** The photo's rails are dark gunmetal (#3a3940–#5c5e55). The model's were light silver. Now
  `metal#4a4e55`.
- **Ball caps.** On the photo they are dark navy (#0e1d46–#314858). They were bright blue and are now #1f3468.
- **Inner tubes.** On the photo they are dark grey with light ratchet holes. They were chrome with dark holes.

## xygs-1: quadriceps board
Found and fixed:
- **Pegs.** On the photo each blue peg sits in a light ring. Rings were added.
- **The clear round level** at the front corner was an almost invisible flat decal. It is now a white rim with a pale
  translucent lens.
- **Tent colour.** It was a little too light and is now #3762b2, as on the photo.

## xyh-1: seated ankle exerciser
Found and fixed:
- **Footplates** (a named weak spot). In the model they were flat trays **beside** the beam and **below** its top, on
  side shafts. On the photo they are two black moulded shoe plates **on top of** the beam's front end, side by side,
  overhanging its sides. Their toes overhang the beam end and turn a little outward. Each has a deep heel cup with a
  high back wall and a low outer wall toward the toe, and a chrome pivot on the beam top. The model now matches. The
  beam ends 70 short of the size line, so the toes overhang it.

## xyh-2: spring ankle exerciser
Found and fixed:
- **Springs.** The photo shows **one** spring under the outer end of each plate. Where a second would be, behind it,
  is empty background. The springs are slimmer (~Ø56) and shorter (~105). The model had 4 fat Ø62 springs about
  135 tall. Now there are 2 springs, Ø56, plates at 140.
- **Plate lips.** The photo's plates are about 30 thick, with a raised tip only at the outer back corner. The model
  had 38-thick plates with full-length outer lips.
- A small round white sticker on the front-left of the base was added.

## xyd-1: electric standing frame
Found and fixed:
- **Multi-colour slings** (a named weak spot). The photo's woven straps are navy-edged with red, yellow and green
  stripes. The model's straps were mostly red with a thin yellow/green line. Each strap is now 4 stacked straps of
  falling width and rising thickness: navy 50, red 40, yellow 28, green 14. That gives navy | red | yellow | green |
  yellow | red | navy.
- **Lower thigh harness.** It was missing. On the photo two straps are buckled to black buckles at both sides of the
  knee pad and hang forward in loops above the footboard, and a loose end lies on the footboard. The model had one
  diagonal "leg" strap. The upper sling now dips to 630 (it was 520), and the hanging strap has its black buckle.
- **Frame tubes** (a named weak spot) were checked against the photo: the base rectangle with side chrome
  outriggers, the uprights, the mid frame with the ladder bars and control box, the handles rising backward from the
  front corners with foam on the top and returning down at the back, the J hooks and the lever. They are left as they
  were. The photo hides much of the tube layout behind the knee pad and slings, and nothing that can be read on it
  differs at sheet scale.

## What the format cannot match (all devices)
- Woven multi-stripe webbing is approximated with stacked straps. A thin dark line shows where a strap is seen
  edge-on.
- Smoothly varying wedges with a bevelled end (the xyg-1 board) are stepped in 4 strips.
- The photos' perspective hides parts of the tube routing (xyd-1 behind the knee pad, the xyf-z3 posts). Those parts
  follow the visible ends.
