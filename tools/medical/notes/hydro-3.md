# hydro-3 + hydro-4 — notes

Batches hydro-3 (HYZ steam / fumigation units, XYL-I, XYL-II) and hydro-4 (XYL-V, XYL-VII A/D, XYL-VIIIB).
Generators: `tools/medical/gen/h3_*.py` + `h3lib.py` (each writes only its own devices' design files; `go()` saves,
waits for the watcher's render and builds the compare sheet). Lettering via `text3()` in h3lib (explicit reading/up
directions, so it also reads correctly on left faces; adds the glyphs 医疗 and digits to the p1lib font at runtime).

Orientation convention: front (z = depth) is the face the photo shows as the main long face (beds, capsules: the side
with the handle/logo), x = 0 is the left end as seen in the photo from that front.

## Parts lists (from the photos, written before drawing)

### xyl-i — compact wax heater (desk) (photo: 3/4 view; logo face + right side)
- Size: the logo face (with the control slope) is the front and the longer face (W 550); the stripe face is the right
  side (D 420): the handle on the lid runs parallel to the stripe face, so the stripe face is the depth.
  Photo proportions give H ≈ 340 (inventory 300 est.).
- Body: glossy white (#f4f4f4) box, big vertical corner radius (~55), softer top edges; on a dark-brown (#4a3530)
  plinth band ~25 high, slightly inset.
- Front top: a sloped strip over the whole width, ~150 deep, dropping ~90 (≈30°), covered by a pale mauve-grey
  (#c9b8b8) panel: a dark display window at its upper left, 2 round +/− keys, 3 round function keys at the lower
  right, small brand logo at the right, printed lines.
- Top behind the slope: a dark brown-grey (#544a47) rounded-rectangle lid inset ~330 × 250 with a chrome flat-bar
  U handle (~220 long, ~45 high) running front-to-back.
- Front face: dark-brown Xiangyu logo (badge + 翔宇医疗 + XIANGYU MEDICAL) at mid-height, left of centre.
- Right side: a dark-brown band ~45 high near the bottom, slanted ends; its front part a white label with a brown
  outline lettered "XYL-I"; small triangle marks (outline + filled) at both ends.

### xyl-ii — wax heater, water bath, on castors (photo: front-left 3/4)
- Body 900 × 420 × ~430 glossy white, vertical corner radius ~45, top edges ~25.
- Left end top: sloped control strip (pale mauve-grey panel, display at upper left, round keys) over the full depth,
  ~180 long, dropping ~110; brand logo (grey-brown) on the left end face.
- Top: dark brown-grey lid ~420 × 300 left of centre with a black U handle (light top face) along x; a small
  rounded recess at the back right corner of the top.
- Front: dark-brown slanted band along the bottom from x≈330 to 870, triangle marks at both ends (no label).
- Below: black (#2a2626) rectangular caster frame ~45 high, inset ~25 from the body, a small black box under the
  middle; 4 grey castors Ø75 under the frame corners; frame bottom at ~80.

### xyl-v — wax heater on an electric lift (photo: front-left 3/4)
- Tank 850 × 420 × ~470 like XYL-II: control slope at the left end with an extra oval up/down key at its right end,
  logo on the left end face, dark-grey lid with a grey U handle, recess at the back right of the top.
- Front: band along the tank bottom, white "Liftable" label with brown outline at its left part, brown fill to the
  right end, triangle marks at the left end.
- Lift: dark-brown (#4a3e3a) U frame: two rails (front, back) ~70 × 60 along the length, joined at the right end by
  a tall dark-brown column block (~150 wide, full depth) up to the tank; the U opens to the left; black accordion
  bellows (6 pleats) under the tank between the rails, from the rails up to the tank bottom.
- 4 grey castors Ø75 under the rail ends.

### xyl-viia — automatic wax cabinet, single (photo: front, slightly from the right; the leaflet render is lettered XYL-VIIC)
- White (#f2f3f5) cabinet ~1200 × 680, sides flat; dark graphite (#4a4040) plinth band ~25 high; 4 grey castors Ø55
  at the corners with a grey levelling foot (round pad) beside each.
- Front: two doors split at the middle (gap line); left door plain with grey lettering "XYL-VIIC" at its upper left;
  right door with a vertical window ~180 × 560 right of its centre showing ~18 white tray slats on dark, a chrome
  vertical bar handle at the door's left edge, 3 small hinges on its right edge.
- A white band ~25 high under the worktop across the front (top rail), a dark gap line under it.
- Worktop: brushed stainless (#c8ccd2) ~30 thick, slight overhang at the front and sides; a raised stainless lip
  (~40 high) along the left edge and the left part of the back.
- In the worktop's left half a recessed stainless wax tray lid (outline groove) with a small pull handle at its front.
- Console at the left rear: stainless box ~510 wide, ~170 high, with its front sloped back ~15°: black glass face with
  the blue touch screen at its right (the screen crop covers the whole face) — `med_xyl-viia_screen`.

### xyl-viid — automatic wax cabinet, double (photo: front-left 3/4, lettered XYL-VIIF)
- Same cabinet language, 1800 wide: left section ~550 wide with a plain door lettered "XYL-VIIF"; a white post;
  right section with two doors "A-box" / "B-box", each with a vertical tray window (~180 × 600) on its outer half;
  twin chrome bar handles in the middle; hinges at the outer edges.
- Worktop with the left lip, the recessed tray lid and the console at the left rear as on VIIA (`med_xyl-viid_screen`).
- Plinth band, 6 castors (corners + middle) with levelling feet.

### xyl-viiib — compact automatic wax cabinet (seen only partly, behind XYL-II in the group photo)
- White cube cabinet ~700 × 650 × 950; the upper front a large flap (~370 high) standing ~25 proud with a chamfered
  top edge, embossed white-on-white "XYL-VIIIB" at its upper left, a small light-blue pill indicator at its bottom
  centre-right; below it a plain lower door (hidden in the photo: assumed); plinth band + castors as the VII series.
- Top deck light grey; at the rear a black glass console over ~3/4 of the width (from the left), front sloped back,
  printed titles at the left, a blue touch screen at the right (no screenCrop: drawn as a blue panel decal).

### Steam beds — common: the photos show the head end at the LEFT (x = 0 side) and the logo / door side as the front.
Consoles that stand beside the bed in the photos are part of the design (as on HYZ-IIC, whose inventory size already
includes its trolley): they stand at the head end, left of the bed, so W grows by the console + a 100–120 gap.

### hyz-iic — acrylic steam bed + trolley (photos: front view, trolley at the left)
- Bed (~2000): glossy white. A flat ledge/top rim over the whole length at ~850 (~30 thick, rounded); at the head
  end (left ~320) it is an open shallow tray with a raised rim. Under it the tub body: rounded bulging ends curving
  down into a narrower central pedestal (concave fillets), the pedestal standing on a wide flat white base plate with
  rounded ends, a raised rim and grooves on its top, small grey feet.
- Domed lid (~1650 long, ~300 high) from the head tray to the foot end: highest near the head, rounded foot end; an
  arched dark head opening in its head-end face; a light-blue window patch on top near the head; a chrome U handle
  on the front in the middle.
- Front: blue Xiangyu logo (badge + words) on the left bulge; on the pedestal a square service door with a raised
  panel, a round embossed logo and a small handle; 4 green buttons (2 × 2) with small labels left of the door.
- Trolley (~460 × 450 × 1050) at the left: white tower whose front face curves (S profile: in at mid-height, out at
  the top); dark-grey (#4f5459) rounded rear base; a wide dark-grey top plate with a concave front edge, sloped to
  the front, carrying a light-blue digital panel (LED windows, coloured keys) and a small switch; on the tower front a
  lighter white teardrop panel and a blue-grey (#3d5f86) rounded control panel (red LED, green button, 3 keys);
  4 castors Ø60.

### hyz-iif — acrylic steam bed, built-in panel (photo: front view)
- The same bed as HYZ-IIC (ledge, head tray, bulging tub, pedestal, base plate, domed lid with chrome U handle,
  head opening, service door with emboss + small handle, 4 green buttons 2 × 2 below-left of the door).
- Head tray top light blue (#7aa0d6) with a thick blue neck pad (~260 × 380 × 70) on it.
- A stainless-framed control panel (white face, blue outline, 4 display windows, 5 round keys, a red power switch)
  on the front of the left bulge instead of the logo; a small black round port on the tub's left end. No trolley.

### hyz-iik — horizontal steam bed + console (photos: bed front view, console separately)
- Bed body: glossy white tub ~2050 × 860 with near-vertical, slightly inward-sloping sides and rounded vertical corners
  from ~420 up to a flat rim at ~850 that runs the whole length and forms a flat shelf at the head end (left), with a
  small perforated stainless plate in front of the head opening.
- Hood: big glossy dome ~1550 long, ~400 high, bulbous (highest towards the head), arched head opening at the left,
  a small round knob on top near the head, a recessed handle pocket with a bar on the front at mid-length.
- Below the tub: two legs joined by a wide shallow arch (front face): left leg with a small service door, right part
  with a tall door (rounded corners, keyhole) reaching up into the tub face; 6 green buttons in the middle (2 + 4);
  Xiangyu logo on the tub front left of centre; small black castors under the legs; a dark pipe fitting at the left end.
- Console (~500 × 450 × 1100, at the left): white cabinet with a front face that curves back at the top (S profile),
  a blue edge band around the sloped top and a light control panel (4 LED windows, keys, a green switch); a dark
  blue teardrop panel on the front; a dark handle slot on the side; a blue round logo low on the side; 4 castors.

### hyz-iib — steam bed with fabric tunnel + console (photos: bed front 3/4, console separately)
- Bed: white body; at the top a stainless trim band (~35) round the whole bed under a light-blue (#8fa9d8) padded
  top (~50 thick, slightly wider than the body). Body: the upper band over the whole length, the left end slanting
  in down to the lower body; lower body with a wide arch cut-out in the bottom of the front (middle), outlined by a
  blue (#2f4fb0) piping line that also sweeps from the top-left corner down and along; a tall door with a blue
  outline and a cut lower-left corner at the right end; a small door at the lower left; 4 green buttons with labels
  in the middle; blue logo + words at the upper middle; small grey feet.
- Tunnel: light-blue fabric half-cylinder (~1050 long, Ø~620) in two sections with a seam, on the pad, opening
  dark at the head end; a small white perforated pillow block in front of it on the pad.
- Console at the left: white column with a curved (S) front and a lighter teardrop panel, light-blue (#8ea5cf) rounded
  rear base, a wide white saddle-shaped top sloping forward with a dark-blue-framed panel (3 red LED windows, 6 blue
  keys), two green lamps and a green switch; 4 castors.

### hyz-ia — steel steam bed with control cabinet (photo: front-left 3/4, cabinet at the left)
- Long white sheet-steel box bed (x 350..2300) ~600 high on 4 black square feet: front face split into two recessed
  panels; a white rim round the top; inside it lilac-grey (#c3c2d8) top panels with slot vents and lift-out lids; a
  lilac pillow block at the right (foot? — at the right end, as in the photo).
- Control cabinet ~350 × 700 × 1000 at the left end: white box, the top sloping down to the front, with a dark-blue
  digital panel (green LEDs, keys) on the slope; a recessed panel on its side; black feet.

### hyz-ib — local fumigation device, two heads (photo: front-right 3/4)
- Wide white base plate (~600 × 550, ~60 thick, rounded front corners) on 4 castors Ø75 (grey hubs).
- Light grey-white (#eef0f3) cabinet ~450 × 400 up to ~830: blue (#3a6fe0) bands — along the front bottom edge,
  a horizontal band at ~640 and one at ~830, and a diagonal band rising across the right side face; blue Xiangyu logo
  on the front lower part; dotted vent grilles on the right side.
- Upper front section (640–830) carries a long chrome/grey horizontal U grab bar on two round mounts.
- Top console (~830–900) with a sloped light top panel: a pale-blue screen area in the middle, "LEFT"/"RIGHT"
  printing, a dark slot on the console front.
- Two white articulated arms: one rises from behind the console at the back left (tube Ø~45 to ~1450), the other is a
  column along the right side face with a knuckle joint at ~330 and a big round joint at ~900, then up to ~1500.
- Two perforated white half-open tube heads (~340 long, Ø~170, open at the front end, rows of slot holes) on the arm
  tops, pointing forward, outside the cabinet to the left and right.

### hyz-ic — local fumigation device, single head (photo: front, slightly from the left)
- Big white rounded base (~550 × 450, ~110 high, domed top, chamfered front corners) on 4 castors Ø60.
- White column ~220 × 200 from the base to ~640, its front concave (waisted) and leaning slightly back; a small
  light-blue diamond logo label on its front.
- White wavy-edged tray plate (~540 × 430 × 35) on the column with a dark grey (#3c4049) band ~25 under its edge.
- Box unit ~430 × 350 × 150 on the tray: front face with a "XYVL" blue label at the left; at the right a light grey
  control panel (dark LCD window, a row of small keys) and a big round green button with a white ring; a fan grille
  (square with a round guard) and vent slots on the left side.
- Arm: white pole Ø40 from the box top at the back left to ~1230 with a small side knob at ~1050, a white knuckle
  joint (disc with grey centre) at the top, a short arm up-left to a white funnel head (rounded-square bell ~190 mouth,
  ~170 long) pointing down-left, grey rim at its mouth.

### hyz-iid — hand-foot fumigation unit, 3 places (photo: front, one lobe facing the viewer)
- Plan = rounded triangle (W 1500 × D 1300) with a lobe pointing to the front: three white glossy lobes; the three flat
  faces between them (front-left, front-right, back) are the places: each has a recessed bay closed by a blue-violet
  (#4f43c8) fabric curtain with folds hanging from under the top ring down to ~100, a zip line at the edges.
- Front lobe: big blue Xiangyu logo with words, a brass drain valve near the bottom; 6 black feet.
- Top ring: thick white rounded ring (~150) over the whole plan; at each place two round arm holes Ø~140 on its
  outer face, lined with blue fabric sleeves.
- On the ring above each place a raised white pod with a small grey LCD panel (keys) facing outwards and upwards.
- Centre: a raised white hub with a round funnel-shaped well on the front side holding a chrome pressure lid with a
  black star knob; a round flat top disc with a small control panel (green button).

### hyz-iie — hand-foot fumigation unit, 2 places (photo: front-left 3/4)
- Lilac-blue (#8a8fe0) central spine (~360 wide over the full depth, ~1300 high) with rounded top edges: front face
  with the white logo badge and vertical white 翔宇医疗, a service door with a chrome handle near the bottom, metal
  screws; at its top front a deep U-shaped well with the chrome lid and a black knob.
- Left lobe (front place): white glossy block ~470 wide, rounded vertical edges; upper part (~820–1000) projecting
  with two round blue arm holes; below it a recessed bay with a blue-violet fabric curtain; on top a raised white block
  with a small LCD panel facing front.
- Right lobe: the same, its place facing the back (curtain visible on the back/right); plain white front.
- Levelling feet (chrome) under the corners.

### Capsules — common: glossy white shells, blue edge line along the lid/base split, consoles at the left (as in the
photos), W grown to include them.

### hyz-iiid — horizontal steam capsule (photo: front-left 3/4, head end at the left)
- Grey (#8d97aa) lower skirt along the whole length (~80–400) on 4 castors Ø75.
- White shell: tall rounded head part at the left (to ~1300) with a round speaker grille disc near its top front;
  the lid from it sloping down to the right (~780 at the foot end), domed top, rounded nose; a blue + grey double
  edge line sweeping from the head top diagonally down to ~700 and then horizontally to the foot end on both sides.
- Lid: a light-blue window patch on top near the head, a round flat cover disc on top near the head, a recessed
  handle pocket with a chrome bar on the front side.
- A big round white side panel (Ø~520) at the lower head end with an embossed logo, 6 green buttons and a small LCD,
  a label plate; the shell's lower edge arches up between the side panel and the foot end showing the grey skirt.
- A flat white hinge plate at the foot end with two chrome hinges.

### hyz-iiie — swinging steam cabin with LCD trolley (photos: 3/4, trolley at the left)
- Capsule ~1650 long, ~800 wide, ~700 thick, tilted ~40° (head up-left, foot down-right): white glossy shell, the
  lid (front/top half) outlined by a blue edge line with a stainless strip; a big transparent blue window near the
  head end of the lid; a long stainless bar handle in a recessed pocket on the lid; a separate rounded head hood at
  the top end with the head opening.
- Pedestal: white C-shaped body with a big round disc housing (~620) at the pivot (round side cover with embossed
  logo, 4 screws), a grey stub/strut above it to the capsule; a grey step block at the left on the floor; a long low
  white foot platform to the right with a pale (pinkish) foot tray at its right end under the capsule's foot end.
- Trolley (~450 × 450 × 1000): white upper box with a sloped LCD (light screen, blue frame) on top, a white middle
  section with a water-bottle window (clear bottle, flowmeter), logo; a dark grey (#3d4146) lower box/base; 4 castors.

### hyz-iiib — swinging steam capsule (printed 1450 × 840 × 1900; console printed 600 × 600 × 860)
- Capsule ~1450 long tilted ~40° (head up-left): glossy white rounded-box shell, the lid outlined all round by a blue
  edge line, a long chrome bar handle along the lid's front side, green herbal stickers + a round blue logo label on
  the lid, a head well at the top end.
- Pedestal: white trapezoid box (front face with a small panel: 2 speaker grilles, green and yellow buttons, a
  switch), gas struts on top to the capsule, on a long white base plate that ends at the right in a raised oval foot
  tray (white rim, pale inside) under the capsule's foot end.
- Console at the left: white column widening upwards (~250 → 360), sloped top with a grey LCD, a blue curve line
  round the upper part, logo; white X-shaped base on 4 castors.

## Final check (compare sheets read after the last render of each device; all `ok`)

| id | size [W, D, H] | size change vs inventory | left approximate |
|---|---|---|---|
| xyl-i | 550 × 460 × 340 | D 420→460, H 300→340 (photo proportions; the handle runs along the stripe side, so that side is the depth) | key symbols / printed panel text as grey lines; italic "XYL-I" drawn upright |
| xyl-ii | 900 × 420 × 560 | — | the render camera (front-right) never shows the control end; checked on the top view. Panel printing as lines |
| xyl-v | 850 × 450 × 750 | — | lift column drawn as a plain block; bellows as 6 stacked rounded pleats |
| xyl-viia | 1200 × 700 × 1100 | — | lettered "XYL-VIIC" as in the leaflet render (A/B/C share the body); tray slats count 18 |
| xyl-viid | 1800 × 700 × 1100 | — | lettered "XYL-VIIF" as in the leaflet; 6 castors assumed (corners + middle) |
| xyl-viiib | 700 × 650 × 1100 | — | lower door and back hidden in the only photo (assumed plain); no screenCrop → blue touch area as a gloss panel |
| hyz-iic | 2600 × 900 × 1100 | H 1150→1100 (same bed as IIF) | lid seam line not drawn; trolley S-profile simplified; head opening = dark recess on the domed end |
| hyz-iif | 2000 × 900 × 1100 | — | panel printing as lines/windows |
| hyz-iik | 2720 × 900 × 1150 | W +620: console included at the left | console printing; perforated plate as dots |
| hyz-iib | 2720 × 860 × 1320 | W +620 console, D 850→860, H 1300→1320 | blue piping path approximate; fabric folds not modelled |
| hyz-ia | 2300 × 700 × 1000 | — | top vents as grooves |
| hyz-ib | 600 × 550 × 1600 | — | head directions (both pointing front-left) estimated from one view; slots as dark dashes |
| hyz-ic | 550 × 450 × 1250 | H 1350→1250 (photo ratio) | column profile straighter than the photo's waisted S |
| hyz-iid | 1400 × 1300 × 1200 | W 1500→1400 (rounded-triangle plan of the 1300 depth) | lobes are a polygon outline (faint facets); curtain folds subtle; the 3rd station (back) not visible in the photo, drawn like the others |
| hyz-iie | 1300 × 1000 × 1300 | — | the right place's curtain/holes on the right side face is inferred from the strip of curtain visible at the photo's right edge |
| hyz-iiid | 1900 × 900 × 1300 | — | nozzle panel inside not modelled (lid closed); emboss lettering light grey |
| hyz-iiie | 2100 × 850 × 1800 | W 1700→2100: trolley included | capsule shown at ~35° (one swing position); housing/C-body simplified |
| hyz-iiib | 2200 × 840 × 1900 | W 1450→2200: console (printed 600 × 600 × 860) included | capsule drawn at 45°: its top reaches ~1740 (the printed 1900 probably covers the swing range) |

Notes for the next person:
- The studio render lights the tops of white shells to pure white: domed lids (IIC/IIF/IIK hoods) lose their top
  silhouette on the white background in the front/side views — they are there (see the angle view).
- Rotation sense, side faces: `text3()` with a reading direction u = (0, 0, -1) on the right face reads correctly from
  the right (front on the viewer's left).
- The /tmp venv lost Pillow on 2026-10-03; `go()` now just runs compare.py, which finds ~/.cache/house-med-venv itself.
