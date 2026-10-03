# Detail review: batch pediatric-2 (children's gym line, wooden OT furniture, kids' treadmills)

Generators changed: `tools/medical/gen/pd2_xyrt118.py`, `pd2_xyrt119.py`, `pd2_xyrt12.py`, `pd2_xyrt120.py`,
`pd2_xyrt121.py`, `pd2_xyrt122.py`, `pd2_xyrt13.py`, `pd2_xyrt14.py`, `pd2_tramp.py` (xyrt-15, xyrt-16), `pd2_xyrt17.py`,
`pd2_xyrt18.py`, `pd2_xyrt19.py`, `pd2_xyrt21.py`. The originals are copied to `scratch/pd2-review/*.orig.py`.
All 14 designs re-rendered `ok`. Each was re-checked on `renders/<id>-compare.png` after its last change.

Side check: the angle camera looks from the front-right. Several photos are taken from the front-left or from the tail
on the x = 0 side, so the angle render shows their mirror. Positions were placed to follow the photo.

## Per device
- **xyrt-118 waist twister**: The ring was a small circle with a wide gap in the middle of the top. The photo's ring
  is larger and slightly taller than wide, with a narrow gap a little right of the top. Fixed: the ring is now 332 × 360
  (centreline), with a 32° gap centred right of the top and rounded foam ends. The red sleeve was too long and started
  too low; it now runs 140–482, as in the photo's proportions. Removed the yellow cone socket, which the photo does
  not have. The adjustment holes are now two grey bolts on the right of the post. The disc's grey underside is
  thicker, as in the photo. Cannot match: the mottled texture of the disc top.
- **xyrt-119 exercise bike**: The pedals were black blocks. They are now open black cage pedals: two oval ring
  plates and rods, on yellow cranks. The +x pedal is forward-down and the −x pedal is rear-up, as the photo shows.
  Body: a fuller egg, big end up at the front under the stem and narrow end down at the rear, tilted 20°. It has the
  raised seam ridge where the two shells meet. The front mount was a yellow tube. The photo shows grey brackets to
  both floor bars, so both are grey brackets now. The seat post now comes out of the body, not floating above it. The
  label moved up and forward. Cannot match: the exact egg outline (the photo is a steep perspective), the cage pedal's
  fine bars.
- **xyrt-12 ladder chair**: The wood was browner and duller than the photo's honey-orange; it is now brighter and more
  orange. The seat board was the same dark wood with grain front-to-back. It is now a lighter plywood with grain
  across, as in the photo. Rung heights, armrests and runners were checked against the photo and match.
- **xyrt-120 space walker**: The cross bars had one red sleeve with yellow boxes sitting on top. The photo's bars
  carry three red foam pieces between yellow pivot collars round the bar, with a yellow tab down to each arm; drawn
  so now. The arms now drop a little outward under the collar, bend, and run down to the platform ends. The blue foam
  runs over the bend, as in the photo. Cannot match: the small black bracket on the front bar.
- **xyrt-121 manual treadmill**: The rail junction on the posts was too high: 798 → 742 (measured on both posts),
  with the yellow collar moved with it. The wave now has a clearer shoulder, a dip, then a rise into the post. The U
  bar arms reached too far back: their ends were at z 340, now z 262. The footprints were two pairs of ovals. They are
  now three pairs of shoe prints (sole plus heel) pointing to the posts, as on the photo's belt.
- **xyrt-122 treadmill with bars**: Side correction. The photo is taken from the tail on the **x = 0** side, not
  x = W as the batch notes say. So the fruit board is the board nearer x = 0 (moved to x 270), with its fruits on the
  x = 0 face. The post knobs point inward on all three visible posts, so all four now face the walkway. Sling stripes
  re-ordered as in the photo: green, white, pink, white, green, white, then three pink stripes sagging at the bottom.
  The cage spanning the whole deck was re-checked on the photo and is right. Cannot match: the console face (no
  screenCrop: boxes and keys), the fruit pictures (coloured discs). The fruits face x = 0, so the renders cannot show
  them.
- **xyrt-13 free-standing ladder**: The rungs started too high (230 with a 92 step). The photo puts them at 158–872
  (step 102), so the bottom rung is just above the braces. The rungs are lighter honey and thinner (Ø24). The posts
  are a more saturated red-brown, as in the photo.
- **xyrt-14 sanding board**: The accessories were in the wrong places. Measured on the photo's tilted top: the sanding
  block sits at the front-left, its front edge at the rim (x 85–325). Its handles are 130 apart. The clamp plate is
  right of the sander and a little behind it, at z ≈ 420. The model had it at the back edge. The wood is lighter and
  more honey. Cannot match: the tilt struts and hinge detail, which are hidden in the photo. The wood rim shows
  end-grain stripes on its front faces (the engine's grain direction on a slab).
- **xyrt-15 trampoline with handrail**: The cover was a fat padded ring. The photo shows a thin vinyl band sloping
  down to a short skirt with dense gathers. It is now a thin lathe band (`caps: false`) with 90 pleats along the lower
  edge. The legs are longer: top raised 350 → 380. The handrail posts were at ±48° and went through the cover. They
  are now at ±64° (the photo's bar spans almost the full diameter). They stand outside the skirt on black brackets
  from the frame ring.
- **xyrt-16 trampoline**: The legs were too short. The photo shows about 240 of leg under a ~65 cover, which cannot
  fit the printed 230. Size H 230 → **330** (the photo clearly contradicts the printed height).
- **xyrt-17 wooden bench**: The label was on the right end. The photo shows a small oval plate on the front apron
  near the right end; moved there. The wood is a little lighter and more yellow. Cannot match: the slight taper of the
  legs.
- **xyrt-18 training set**: The chair was a regular chair with slanted front legs. The photo shows a tall ladder on
  two runners. Its uprights are now vertical with rungs from low to the top. A seat board (at 560, above the bench)
  sticks out of it toward the bench, with half-round side aprons hanging under it. Diagonal braces run from the
  runner fronts to the uprights. The reading board leaned too steeply: 58° → 40°. The step boxes had strongly striped
  plank sides; they are now smooth tan laminate, as in the photo. Cannot match: exact accessory sizes (estimated from
  the perspective).
- **xyrt-19 safety chair**: The push handles were two separate posts with grips running forward. The photo shows one
  U push bar: posts rising from the rear legs and a black-foam grip across the back, behind the headrest, with the red
  clip at the headrest. Castors are bigger: 62 → 80. Cannot match: the backrest's soft wrap (a U slab).
  The tray and footplate grain is more striped than the photo's smooth laminate.
- **xyrt-21 PT stool**: The seat is wider (Ø372). The height lever now hangs down to the front, as in the photo. The
  ring on top of the gas cylinder is black. Base: tried `mirror` instead of `chrome`, and it renders the same satin
  grey in the render stage, so `chrome` is kept as the right material. Cannot match: the mirror-polished look of the
  base (the render stage has no environment to reflect).
