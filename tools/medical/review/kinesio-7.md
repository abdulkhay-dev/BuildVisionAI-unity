# Detail review: batch kinesio-7

Generators changed: `k7lib.py`, `k7_xyj1.py`, `k7_xyj2.py`, `k7_xyj3.py`, `k7_xyj4.py`, `k7_xyj5.py`, `k7_xyj6.py`,
`k7_xyj7.py`, `k7_xym1.py`, `k7_xym2.py`, `k7_xym3.py`, `k7_xym4.py`, `k7_xyhj1.py`, `k7_xyhj2.py`, `k7_xyhj4.py`.
In `k7lib.py`, `rail_unit()` gained a `lever_mat` argument; its default is chrome, so the other wall units are
unchanged. All 14 designs were regenerated. Each one rendered `ok` (the .txt is newer than the json) and was re-checked
on `renders/<id>-compare.png`. The photos were also checked at full size or as 1.3–3× crops, and colours were sampled
from them. Scratch: `tools/medical/scratch/k7rev/`.

## Per device
- **xyj-1**
  - Grip direction (weak spot). In the photo the camera is above: the bottom plate's top face shows, and the grip's
    end is seen almost end-on. The grip therefore points down and forward (~40° from vertical), not straight down. It
    now does, and its tip reaches z ≈ 250, past the printed D 220. The printed depth is taken to exclude the handle.
  - The grip was white chrome. It is now darker steel with a dark end, after a longer black collar.
  - The adjustment lever is dark metal, not chrome, as in the photo.
  - Added the chrome clamp block across the top of the crank, with its slot.
  - The hub ring is green, not near-black.
  - The green is more saturated (`#08855f`; the photo samples at #00795d–#017251).
- **xyj-2**: the layout was already right: wheel, two flat bars crossing at 31°/−57°, slots, hub, handle, lever and
  lettering. Only the green changed: the renders were too cyan and light, so it is now `#12906f`. The handle points
  forward; the photo shows it running "down" only because the camera is above.
- **xyj-3**
  - The roller steps were too thick. They are now Ø38/47/56, as measured on the photo (were 44/52/60), with a second
    step cone.
  - The roller was orange wood grain. The photo shows pale beige with no grain, so it is now satin `#e8cc98`.
  - The D grips were pointed triangles. They are now trapezoids, open ±12 mm at the hub, with a flat outer bar.
  - The drum assembly moved 6 mm left and has a dark face on its right end; the collar and lever are tighter.
  - The teal is darker and less saturated.
- **xyj-4**
  - The forearm saddle sat about 70 mm too high and covered the dial. In the photo its rim is at the carriage's bottom
    edge, with the whole dial and handle above it. It is now a concave U trough at 120–200, and its colour is mauver.
  - The reach arm, clamp and knob moved down under the saddle, with a black stem foot.
  - The handle now ends just above the saddle.
  - Kept the size [240, 480, 980] (weak spot). The photo's front view is only ~230 wide (the same plates as
    XYJ-1/2/5), so the printed 48~70 cannot be the width. 480 (the minimum of the 48~70 range) is read as the reach.
    D 400 is the other candidate; it cannot be decided from the single front photo.
- **xyj-5**: the lever's ball is higher, 43 mm above the bar as in the photo. The green-teal changed to the photo's
  `#029a8a` tone, and the fittings are unchanged.
- **xyj-6** (weak spot: teeth and checker)
  - In the photo, the tips within a section alternate green/red. That is because the two columns' teeth are staggered
    by half a pitch, and the columns were aligned. Each column's sawtooth is now generated from a triangular wave, with
    a phase offset of half a pitch on one column.
  - Kept 5 sections of ~204 mm in a checkerboard. The colour order is checked against the photo, which shows the
    opposite side from the side render: the near column is green at the top.
  - The ladder now runs down to 40, level with the bottom bracket, as in the photo (was 68).
  - The slider was 126 tall; the photo shows it at 425–698. Its two black knobs are 220 apart and moved to the −x side,
    the side the photo shows.
- **xyj-7**
  - The cushion is the photo's deeper navy.
  - The lever had a black grip at its end. It is now a tapered chrome cam handle, with the black knurled nut next to the
    post, as in the photo.
  - The straps were three flat boxes. They are now one band outline that wraps over the cushion and down its front and
    back.
  - The box's end badge is now a round metal disc with a dark ring.
- **xym-1**
  - The back wall stood 84 mm above the top shelf; the photo shows about 40–60. It is now 545, with the ends at 525.
  - The balls' patches z-fought and looked like jagged green camouflage. They are now larger, smooth caps on
    mostly red/orange balls, like the photo.
  - Kept H 720 (weak spot). The balls are round in the photo, so it is not stretched, and its H/W of ~1.8 cannot hold
    with both printed numbers (40 wide, 102 tall). Keeping W 400 gives H ≈ 720. The other reading would be H 1020 with
    1 m gym rods, which would make the rack ~555 wide.
- **xym-2**: the photo shows 5 big patchwork balls (~Ø215) with large panels, partly hidden by the front board. The model
  had 6 small balls with jagged, z-fighting patches. It now has 5 large balls with big smooth panels.
- **xym-3**
  - The table top had a strong plank grain. It is now plain laminate beige, matching the photo.
  - The stretcher between the legs moved down to 180 (was 300).
  - The black finger hooks were J shapes. They are now low black arches just above the top, as in the photo.
  - Under the top there was one chrome rod per station. There is now a pair (a chrome rod and a dark cord), and the
    bottles are bottle-shaped (shoulder, neck, cap) and larger (124 mm tall).
- **xym-4** (weak spot: crank and slot)
  - Re-read the 2× crop. The slot is a short, gently curved groove that runs from low at the front up to above the hub.
    It is not concentric with the hub. It is redrawn that way (it was a 100° concentric arc).
  - Added the flat chrome link from the hub to a pin in the slot's lower end. The photo shows this as the chrome bar
    under the grip.
  - Kept the crank phase (right grip behind and slightly below the hub, left grip at the front top). The far grip shows
    in the photo at the front top, which fits.
- **xyhj-1**
  - Added the raised white heel hoop over the board's front edge (a U tube from the base sides across the front). It is
    clearly visible in the photo and was missing.
  - The diamond plate's dashes are now a real herringbone: rows turned +45°/−45° in the plate, using `rots` and local
    repeats (they were horizontal/vertical ticks).
- **xyhj-2** (weak spot: depth parts)
  - The board outline was re-measured by scanning the photo's blue: 576 wide down to s ≈ 380, then 462 wide (was 404).
    The slot is ~118 wide from s 60 to ~735 with a round top (was 70 wide, from 90 to 640).
  - Depth: in the photo the black wheels show lower than the dark rails' feet, and the photo is taken from above. That
    puts the wheels in front of the rail feet.
  - The model had it reversed: dark rails lying along the board and cream legs going back to rear wheels. Now the dark
    rails (lock knob, ratchet block on top) are rear props down to the floor behind. The cream struts run down the
    board's sides to front wheels, and a cream cross bar near the floor joins strut and rail. In the front view this
    still reads as in the photo: dark rails vertical outside, cream struts slanting inwards.
  - The foot platform was a low slab on a flat frame. It is now a ~150 high step: a slatted top with a lip on a chrome
    stand of legs, a bottom bar and a V brace.
  - Cannot match: the depth itself, from a single front photo. The platform's distance in front of the board is also
    unknown; the photo may be a composite.
- **xyhj-4**: the side rails are now open U troughs with a notched inner wall (were solid bars). The props' tops now touch
  the board undersides (there was a gap). Added the front hinge bracket with two dark bolt heads. The rest matched; the
  remaining look differences come from the photo's low front-left perspective.

## Format limits / engine notes
- `strap` along a path that starts vertically shades half of its width dark: the section frame is ambiguous, and the
  result is the same with `roll` 0 or 180. A flat band over a pad is better drawn as a `slab` side outline (as on xyj-7).
- Patch caps on balls (a slightly smaller, offset sphere of another colour) z-fight when the two surfaces are nearly
  tangent. An offset of ~0.15–0.2 R with a radius of ~0.85–0.9 R gives clean edges.
- None of the 14 has a screenCrop. The xym-4 LCD and the small stickers stay generic, and the plates' lettering uses
  `text()` as before.
