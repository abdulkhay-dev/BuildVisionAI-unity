# Detail review: batches other-1 + other-2 (15 devices)

Generators changed: `tools/medical/gen/o_swy.py`, `o_xddi.py` (rewritten), `o_xddii.py`, `o_qc.py`, `o_xy78.py`,
`o_xy79.py`, `o_xy82.py`, `o_shower.py`, `o_xy87.py`, `o_xy88.py`, `o_xy89.py`, `o_xy92.py`, `o_xy96.py`.
`o_xy97.py` is unchanged. The originals are in `scratch/other-1-review/*.orig.py`. Helpers are in the same scratch folder:
`run.sh` regenerates a design, waits for the render and builds the compare sheet, and `swy_screen.py` straightens the
warmer's screen picture. All 15 designs render `ok`, and every `.txt` is newer than its json. Each device was re-checked
on its compare sheet after its last change.

**Screen picture replaced:** `xy-k-swy-ii`. Both `reference/xy-k-swy-ii_screen.jpg` and the albedo in
`External/Materials/med_xy-k-swy-ii_screen/` were rewritten. The original crop and albedo are in the scratch folder. The
watcher has already reimported the albedo and re-rendered the device.

## xy-k-swy-ii (forced-air warmer)
- **Interface was ~10 % narrow and skewed:** the crop was a perspective shot behind a jagged black mask. The crop is now
  straightened, so its UI quad maps to the UI rectangle of the frontal photo 3 (58.5 % of the panel width, 25–78 % of
  its height). Everything outside the crop's panel is filled with panel black. The mask was removed.
- **Panel corners:** they were square. They are now rounded (r ≈ 34) by body-white corner fillers, as in photos 1 and 3.
- **Handle:** it was a round bent tube. It is now a bridge whose legs flare into the top with big fillets, as in photo 2.
  It has an arch opening across x with grey inner faces and a grey well under it.
- **Hose and cuff:** both were thin. The hose is now Ø72 and the cuff Ø84 with a Ø96 collar, and the hose lies on the
  table. The feet have a widening brown-grey disc under them.
- **Cannot match:** the UI is still a photo of a photo, slightly soft.

## xdd-i (UV lamp on an X trolley)
- **Base:** the arms now lie on the diagonals, as in the frontal photo 1, which shows an X. They taper from the hub to
  rounded ends.
- **Castors:** they now have black hoods and big silver wheel discs (they had black caps).
- **Reflector position:** it hung centred on the pole. It now hangs front-left of the pole, so the pole shows at its
  right edge (photo 1). A chrome swivel arm runs to a white plate on the reflector back (photo 2, seen from behind).
- **Levers:** both black levers are now on the back-left (photo 2).
- **Cable:** it now loops out on the pole's right and runs down to a plug.
- **Logo:** REAHER is now drawn in real letters, mirrored correctly for the back face, with a green/teal/blue swirl.
- **Cannot match:** the swirl logo is three colour strokes.

## xdd-ii (UV tower)
- **Stripe at the corner:** above the jog, the stripe used to float flat in front of the rounded corner. It now wraps the
  corner as curved band slices whose lower ends climb with the diagonal.
- **"UV-C STRIKE GERM-ZAPPING":** it is now printed ON the navy stripe in light grey-blue with spaced letters, at the
  photo's length (about 460 mm). It used to be grey on white beside the stripe. The stripe was widened to hold it.
- **"UV-C DISINFECTION":** enlarged to the photo length (h 20) and coloured blue-violet.
- **SER mark:** it was a blocky hook. It is now the photo's quarter-turned "2"-like shape: a right bar and a short left
  leg joined by a curved top, with "SER" upright under the leg.
- **Handle:** it was a C on the right side. It is now a bracket that starts on the front face right of the stripe, runs
  round the front-right corner and stands about 36 mm beyond the side, as in both photos.
- **Panel:** made flatter (1 mm proud).

## xy-qc-i (debridement cart)
- **Bottle:** it was a flat grey jerry-can shape in a 40 mm recess. The core now steps back behind the window to make a
  real dark-lined cavity. In it stands a round grey glass jar with shoulders, a wide neck and a lip, plus a second jar
  half hidden at the left. Side wall fillers keep the cabinet sides closed.
- **Cup handpieces:** the white handpieces sticking out of the cups were removed. The photo's grey cups are empty.
- **IV pole:** changed from black (photo 2) to silver, as in the main photo 1.
- **Layout:** kept as photo 1 (cups front-left, shelves and pole right). Photo 2 is a mirrored picture.

## xy-78 (lifting commode chair)
- **Armrests:** the white vertical posts were removed. Each pad now pivots on the backrest frame through a white bracket
  and rests on one chrome strut from the seat side.
- **Sling:** its bottom moved up to about 240 above the seat, as in the photo. The pocket is a separate panel with a
  slanted top edge.
- **Control box:** the black rounded box sits on the left base rail at the front, as in the photo; it was on the front
  cross bar. The cables were rerouted to it.
- **Cannot match:** the lift mechanism is read from a small, low-resolution photo.

## xy-79 (folding commode)
- **Front bar:** removed. The photo is open at the front under the seat, and the bar crossed the bucket.

## xy-82 (wheelchair with tray)
- **Tray:** it was planked wood texture with a big central cut-out. It is now a smooth tan laminate top on an
  orange-brown edge, with the photo's small round notch in the back edge, right of the middle.
- **Battens:** they are now thick yellow-orange blocks running the full armrest length.
- **Seat:** lightened to the photo's blue-grey.

## xy-84 / xy-85 (shower chairs)
- **Legs:** they now leave the seat vertically and bend outward just below it (they were straight). The xy-85 splay
  went from 18 to 40, as in the photo.
- **Tips (xy-84):** now bell-shaped grey rubber tips (they were cylinders).
- **Castors (xy-85):** they now have black bodies and lock pedals. The engine draws chrome castor forks, so a black body
  covers them.

## xy-87 (patient hoist)
- **Sling:** it was a long bag hanging straight from the spreader. It is now the photo's diamond-shaped folded sling:
  body 520–1480, widest at about 1000, pointed bottom, navy piping along the edges, and a four-colour band across the
  front.
- **Straps:** dark straps run from the hooks down to the body. Two loose leg straps carry a yellow-green stripe.
- **Leg end caps:** now light grey; they were black.
- **Cannot match:** the folded back panel of the sling (a darker inner layer) is not drawn separately.

## xy-88 (ADL kitchen)
- The small brass knob moved behind the hob's right end, as in the photo; it was at the front.
- The pedestal is a lighter beige wood.

## xy-89 (pine kitchen)
- **Finger-jointed pine:** drawn as lamellas of short blocks in three pine tones. They run vertically on the doors and
  the wall cabinet and horizontally on the back panel (about 100 flush decals).
- **Doors:** the layout now follows the photo: a left double door, a middle single door with no knob, a right double
  door, then a narrow fixed panel. Before, there were two equal pairs plus extra knobs.
- **Wall cabinet:** the knob pair and seam moved to x 360, as in the photo.
- **Cannot match:** real end-grain joints, which are finer than decals.

## xy-92 (platform lift)
- **Bellows:** the folds are now glossy and slightly puffed, with grey sheen, as in the photo.
- **Ramp:** it now has four pressed ridges along its length, up-turned side flanges and an end lip. Its colour is the
  photo's blue-grey.
- **Rails:** now white plastic; they were metal grey.

## xy-96 (pull-down wardrobe rail)
- **Hangers:** they hung flat in the front plane. They are now turned across the rail (about 52°), as they hang in the
  photo, with the hooks over the rail.
- **Dampers:** widened to 84 mm.
- **Mount:** stays wall-hung from its middle.

## xy-97 (lifting wash basin, other-2)
- Re-checked against the photo; nothing changed. The carriage, back panel, floor plate, basin with lobes, mixer, angle
  valve and switch all match. The design is a floor-standing unit on its plate.
- **Cannot match:** the bowl is about 30 mm shallower under the deck than in the photo.
