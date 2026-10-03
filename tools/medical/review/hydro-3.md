# Detail review — hydro-3 + hydro-4 (2026-10-03)

Reviewer pass over the 18 devices drawn in tools/medical/gen/h3_*.py (notes: tools/medical/notes/hydro-3.md).
Each device: compare sheet + photo(s) at full size read, differences listed, generator edited, re-rendered (all `.txt`
`ok` and newer than the json), re-checked. Scratch crops in tools/medical/scratch/h3rev/.

## Batch-wide fix: the p1lib import pitfall
`h3lib.py` did `from p1lib import text, …`, which re-binds `D.decal / bar / lathe / sphere / slab / loft` with
physio-1's argument order. Every `d.decal(id, at, size, face, mat)` in these generators was therefore written as
`mat = "front"`, `face = <material>` — 37 broken decals over 15 devices (all the logo crosses, the HYZ-IC column
label, HYZ-IIID / IIIE embossed logos, HYZ-IIID label plate). h3lib now saves lib's methods before the import and
restores them after; all 18 designs regenerated. Added `turned()` in h3lib (adds `rots` to a group of parts, used to
tilt flat lettering with a sloping panel).

## Per device

### xyl-i
- Found: panel layout differed from the photo (display at the far upper left, keys in a different pattern);
  dark lid inset too small (photo's lid covers almost the whole top); logo too low.
- Fixed: display upper middle-left, power key left/below it, +/− under the display, 3 function keys lower right,
  small brand mark + text lines at right/bottom; lid enlarged to ~420 × 260; logo raised to mid-height.
- Format limits: key symbols and panel print as grey lines.

### xyl-ii
- Found: triangle marks pointed the wrong way (photo: ▽▼▽ pointing down at the left end, △▲ up at the right end);
  brown band too low (photo: at ~1/3 of the tank height).
- Fixed: triangles redrawn as in the photo, band raised to 166–200.
- Limits: the render camera never shows the control end (checked on the top view).

### xyl-v
- Found (weak spot): lift column a full-depth block sticking out past the rails; bellows 6 thin pleats starting high.
- Fixed: column narrowed (~120 wide, set between the rails at the right end); bellows: floor plate, black core and
  7 deep rounded pleats from just above the rails up to the tank.
- Limits: the photo's bellows pleat count/depth approximated.

### xyl-viia
- Found: console screen showed the whole crop including the grey console cheeks and part of the worktop drawn in
  perspective (looked like a mis-cut picture); castors at the outer corners (photo: inboard, ~75 mm); tray pull at the
  front edge.
- Fixed: a black-glass mask plate with a hole shaped like the crop's black face covers the cheeks/worktop of the
  picture; castors Ø72 moved inboard (x 200 / W−200), levelling feet stay at the corners; tray pull moved to the
  middle of the tray lid.
- Limits: screen picture still slightly perspective-distorted inside the mask.

### xyl-viid
- Found: same console-crop problem; castors at the corners.
- Fixed: same mask (own quad for the VIID crop), castors inboard (200 / 900 / W−200), feet at corners + middle.

### xyl-viiib
- Found: console had a plain blue box for the touch screen (photo: same console face as VIIA/C — logo, title,
  blue touch screen at the right); indicator pill plain light-blue blob (photo: grey pill, chrome rim, blue text);
  console cheek vents missing; castors at the corners.
- Fixed: VIIA's console picture used with the mask; pill = grey with chrome rim and blue text line; cheek vents;
  castors inboard.
- Limits: lower door and back hidden in the only photo (assumed plain).

### hyz-iic
- Found: rim/ledge thin (photo: thick ~110 band); handle too high on the lid (photo: low, ~100 above the rim);
  door/buttons/logo misplaced (door too far right, catch on the wrong edge, buttons too far apart); head opening a
  flat dark blob; trolley's control panel a tilted box floating off the S-front, teardrop panel small; trolley tower
  as wide as its top.
- Fixed: ledge 580–690; lid lower/rounder; handle lowered; door at u 940–1250 with the catch at its right edge, 2 × 2
  green buttons close together left of it; logo moved right; arched head opening drawn as an arch slab in the lid's
  head face; trolley: D-shaped blue-grey panel lying on the S-front (red LED, green key, 3 keys), big teardrop panel
  following the front curve with a grey outline, tower narrower than the top (tw = 55).
- Limits: the lid seam line not drawn; small panel print as lines.

### hyz-iif
- Found: same bed issues as IIC (shared generator) plus: control-panel switch red (photo: black rocker), head
  opening not visible, door catch side.
- Fixed: same bed fixes; flat-ish head face of the lid so the arched opening reads (dome only at the foot end);
  black rocker switch with green mark; door handle at the left edge + 2 hinges at the right.
- Limits: panel printing as lines/windows.

### hyz-iik
- Found: the lower arch was a tall symmetric parabola (photo: shallow, asymmetric — rising after the left leg, long
  and low to the right); the tall right door too high and short (photo: from under the rim almost to the floor, lock
  at upper left); button labels the photo doesn't show; handle pocket and logo placement off.
- Fixed: new body outline with the shallow asymmetric arch, an upper tub band overhanging the lower body, the right
  end flush to the floor; tall door 110–600 with lock at its upper left and 2 hinges; 2 + 4 green buttons without
  labels; pocket moved left, logo moved/raised.
- Limits: console printing simplified.

### hyz-iib
- Found (weak spot): blue piping path wrong (photo: from the head-shelf corner, a steep short drop, then a long
  shallow diagonal down to the right end of the arch and down to the floor); arch too deep; tunnel short and in the
  middle (photo: two sections ~820 each from the pillow nearly to the foot end); tall door too short; small door
  position; buttons without lamps/red labels; console tower as wide as its top.
- Fixed: body left edge near vertical with a short fairing under the overhanging head shelf; piping redrawn as
  measured; arch shallow (u 850–1480) with its own piping; tunnel 335–1975 in two sections with the seam; pillow at the
  head end; door 60–575 with cut lower-left corner; small door + handle at the lower left; 2 lamps over 4 keys with
  red labels; console tower narrower (tw = 40).
- Limits: fabric folds of the tunnel not modelled.

### hyz-ia
- Found: feet were tall black blocks (photo: short grey legs on black pads); cabinet panel a plain dark box.
- Fixed: grey legs on black pads under bed and cabinet; panel with green LED windows, a light window, red + green keys.
- Limits: top vents as grooves.

### hyz-ib
- Found (weak spot, head directions): both heads were turned front-left (photo: both point straight forward, open
  ends facing the viewer); heads were closed domed tubes (photo: open tubes — the hollow shows); right arm column at
  mid-side (photo: back third); base a plain rectangle (photo: U with two front legs); logo light blue (photo: dark
  navy); LEFT/RIGHT printing missing; vent dots one block.
- Fixed: both heads yaw 0, open lathed tubes with slot rows; right arm column moved back (z 180); left arm from behind
  the console near the left edge; U-shaped base; navy logo; LEFT/RIGHT lettered on the sloping panel (text3 +
  `turned`); vents in two blocks (upper front / lower rear) as in the photo.

### hyz-ic
- Found (weak spot): column drawn straight; the diamond logo label floated (rendered as a broken decal).
- Fixed: column lofted waisted (narrow at ~330–430, flaring forward and out into the tray), a round plinth ring at its
  foot; diamond label tilted with the column's front; grey castor wheels.
- Limits: the photo's slight backward lean of the column approximated by the forward flare.

### hyz-iid
- Found (weak spot, lobe facets): body/ring were small-radius polygons with flat 'facets'; the front lobe narrow;
  curtains on flat faces flush with the lobes (photo: bays recessed, curtains tucked behind the lobe edges); the top
  had no ridges joining the pods to the hub; logo small/off-centre.
- Fixed: plan rebuilt — three wide round lobes (r 446) with recessed bays (70) between them, a near-round top ring
  (rounded triangle r 545 with short flats); curtains with folds and zips inside the bays; raised ridges from the hub
  to each pod; logo enlarged (badge ~145) and centred on the front lobe, lettering lifted off the curve.
  Size now 1440 × 1394 × 1200 (photo proportions; inventory estimate 1500 × 1300).
- Limits: the 3rd (back) place is not visible in the photo — drawn like the others.

### hyz-iie
- Found (weak spot, second place): the left lobe had its curtain on the FRONT face (photo: the left lobe's front is
  plain white; its curtain and the two foreshortened arm holes are on the LEFT side face).
- Fixed: left lobe mirrored to the right lobe: place facing left (curtain with zips and 2 arm holes on the left face),
  plain front.
- Limits: the right place (back/right) inferred from the strip of curtain at the photo's right edge.

### hyz-iiid
- Found: the round side panel's top was cut by the bulging shell and the lower head block was a square block (photo:
  the block follows the circle).
- Fixed: head block outline follows the panel's circle; panel brought forward so it reads as a full disc.
- Limits: the inner nozzle panel (inset photo) not modelled; embossed lettering light grey.

### hyz-iiie
- Found: the cabin was a tilted rounded box with a separate hood (photo: one shell — near-vertical rounded back
  rising into a hood, the lid top sloping ~33° down to a round foot end, the underside rising to the pedestal neck);
  blue line path wrong; window/handle placement.
- Fixed: cabin redrawn as one side-profile slab measured on the photo; blue + stainless line from over the top
  behind the hood down the lid edge to the foot; window on the sloping top near the head; handle pocket along the
  slope; round housing re-centred (r 270) under the neck.
- Limits: the capsule is shown in one swing position.

### hyz-iiib
- Found: capsule tilted 45° (photos ~38–40°).
- Fixed: tilt 40°.
- Limits: the printed 1900 height probably covers the swing range; sticker pictures as green patches.

## Not matchable in the format
- Panel printing / small symbol text: grey lines and boxes (no picture crops for these devices except XYL-VIIA/D).
- Fabric folds (tunnel, curtains) only as slab ripples.
- White domed tops vanish against the background in front/side views — judged on the angle views.
