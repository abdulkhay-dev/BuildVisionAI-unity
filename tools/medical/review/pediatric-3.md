# Detail review: batch pediatric-3 (children walkers, chairs, trainers, tunnels, swings, slide)

I changed these generators: `tools/medical/gen/pd3_lib.py` and `pd3_xyrt25/26/27/28/29/30/31/36/36a/38/39/4/40/43.py`.
The originals are copied to `tools/medical/scratch/pediatric-3-review/*.orig.py`. All 14 designs re-rendered `ok`.
I re-checked each one on `renders/<id>-compare.png` after its last change. Sides were checked with the front and side
renders. On several devices the angle camera shows the mirror side of the photo (25, 26, 27, 28, 38, 40).

## Shared
- `pd3_lib.rigid_caster()` has a new `hub_k` parameter (hub diameter / wheel). The walkers' castors now have the
  photo's large black hub inside the orange tyre.
- **Strap engine note** (for future work): a `strap` whose path starts vertically gets its width across the path
  plane, so it renders as an edge-on ribbon. Start the path with a short horizontal lead-in, for example from under
  the sole edge, or radially under a rim. The width then lies along the intended direction. Every strap I drew uses
  this.

## Per device
- **xyrt-25** (walker, rear wheels): the grips were checked against the perspective of the photo. Both grip lines run
  to the same vanishing point as the rails, so the grips are level. The apparent tilt is perspective, and I left the
  grips level. The grips are a little longer (90 mm) and start right at the post. The castors have a black hub. The
  bolts are moved to the photo's joints: mid bar, leg/bottom rail above the bracket, and middle low bar.
- **xyrt-26** (pedal chair):
  - **Seat**: it was a thick plain cushion. It is now a thin horseshoe pad with the photo's wide concave notch
    between two front horns. The backrest is a thinner pad.
  - **Armrests**: they are inverted L's, a short pad and then a vertical drop, with white posts and bolts below, as
    in the photo.
  - **Pedal shoes**: they were simplified straps. Each is now a black sole with a **C-shaped heel cup** that curls
    from the heel over the ankle, open to the toes and see-through from the side, plus a toe strap. The shoes are
    rigid on the cranks, so the lower one is upside down, as in the photo.
  - **Drum**: its support is a bent white flat bar down to the front rail with a chrome foot plate, as in the photo.
    It was a box. The drum caps are black.
  - Handlebar: the foam runs further down the corners, and the upright kink matches the photo.
- **xyrt-27** (walker, front-open): the bottom rail curves down to the foot with the photo's large radius. The castor
  hubs are black. No other differences.
- **xyrt-28** (hydraulic stepper):
  - **Floor frame**: the photo shows a front and a rear cross rail with black end plugs, joined by one middle spine.
    There are no side rails. The model had a square frame.
  - **Cylinders**: the chrome rod is at the top, up to the bracket, and the black body is below on the lever. They
    were the other way round.
  - **Pedals**: the black blocks are replaced by a wood plate, a **U-shaped heel cup** (curved, open to the toes,
    with a raised back) and two **arched padded straps** over the instep and the toes. Dark slate fabric, as in the
    photo.
- **xyrt-29** (barrel): crisp white piping rings now separate the bands, outside and in the bore, as in the photo.
  The bands' edges are less rounded. The ends are red, not white. The band order Y/B/R ×3 was already right.
- **xyrt-30** (printed tunnel): the flat patches on a smooth tube are replaced.
  - The tube is now 19 puffy bands between the spiral-wire pinches, which gives the photo's **scalloped**
    silhouette. Each band is 8 curved panels (arc sweeps with an oval section).
  - The panels follow the photo's patchwork in diagonal runs: pale yellow, white, grey-blue check, light blue.
    Small orange, green and red motifs sit on them.
  - Cannot match: the cartoon print itself. No picture texture exists for it. The library check and floral textures
    were tried, but they are far too dark, and a tint can only darken them. The check panels are therefore a plain
    grey-blue.
- **xyrt-31** (striped tunnel with net): the net was a translucent skin. It is now a **real see-through net**: ring
  wires and 72 lengthwise wires with open holes. It sags into the photo's slight waist. All five sections are equal
  length. The photo's sections shrink only with the perspective. The stripes are wider: 6 per section, as in the
  photo. Cannot match: the net's hexagonal hole shape. It is a square grid at about 34 mm.
- **xyrt-36** (OT table): the dark lower sleeve is now the wider outer tube, around the white inner column. Nothing
  else differed.
- **xyrt-36a** (desk + 3 chairs): the right chair's solid curved side panel is replaced by the photo's construction:
  straight rear post and front leg, a seat rail with an arched underside, and a **thin bent-wood arm strip** sweeping
  from the post top down to the rail. The box-side panels are lighter (`#c07a4a`, as in the photo).
- **xyrt-38** (hip trainer):
  - **Cuffs**: each lever carried two separate cuffs. Each now has **one long blue cuff** with two black straps, as
    in the photo.
  - **Armrests**: the black pad now wraps over the top and down the front bend of the chrome loop, as in the photo.
    It was a flat block.
  - **Pivots**: each lever pivot has a vertical hinge pin. The spring, threaded rod, nuts and turntable already
    matched.
- **xyrt-39** (quadriceps chair):
  - **Ratchet disc**: it was a darker inner disc. It is now a real perforated disc: a ring of 16 holes, at the
    photo's smaller size (Ø124).
  - **Ankle cuffs**: they were rounded blocks. They are now **padded U cuffs** (open to the back, round the front of
    the ankle) running inwards from the lever bottom.
- **xyrt-4** (swing frame):
  - **Ropes**: they were plain salmon rods. They are now **twisted red-and-white cords**: a pale core with a salmon
    strand coiled round it.
  - **Bucket**: it was a firm cone. It is now a **soft sling** sewn from 18 vertical stripes, red/yellow/blue/yellow,
    sagging into a round bottom, with a soft green-blue rim roll all round.
  - Cannot match: the real fabric sag and folds of the sling.
- **xyrt-40** (ankle trainer): the black blocks are replaced. Each foot holder is now a black sole, a **C-shaped heel
  cup** curling up round the heel, and two **arched straps**. Cannot match: the loose hanging strap ends of the
  photo.
- **xyrt-43** (stairs + slide):
  - **Rooster**: it was a round blob. It is now a proper silhouette with comb, beak, wattle, full breast, four sickle
    tail feathers and a leg.
  - **Grasshopper**: it has the photo's thick raised hind femur.
  - Cannot match: the decals are 1-colour silhouettes. The photo's drawings have inner detail lines.
