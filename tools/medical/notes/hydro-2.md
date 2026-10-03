# hydro-2 — notes

Generators: `tools/medical/gen/h2_*.py` + `h2lib.py` (on top of `h1lib.py`); each writes only its own design file.
Camera of the `angle` render = front-RIGHT. Photo viewpoints are noted per device; the model always follows the photo's
sides (what is on the left / right of the device seen from its front), not the render camera.
Tub technique as in hydro-1 (ring slabs for walls / rims, a basin floor); glass-front tubs: the front wall is a front-plane
slab with the window notch, the inner walls are drawn without the front strip so the water / interior shows through.

## Parts lists (from the photos, written before drawing)

### rh-sr-ii — compact hydrocollator (photo: front-left)
- Brushed stainless box ~460 W × 340 D × 630, sharp-ish vertical edges (r≈6), a darker shadow line at each corner.
- Top: a stainless frame lip ~20 high, flush/slightly proud of the body; on it a clear acrylic lid (inset, ~15 thick)
  with a moulded arched acrylic handle running across the width at the middle (~40 high).
- Left side face: chrome grab handle (horizontal bar on two short standoffs, ~170 long) at ~560 high near the front.
- Left side face, lower front corner: a square vent perforation patch ~70 × 100 (grid of small dark holes) at ~80–180.
- Front: white oval logo plate ~150 × 60 (blue round mark + blue lettering) centred at ~470 high, a bit right of centre.
- Front lower right: round black thermostat knob Ø45 in a blue ring Ø60 at ~(390, 110); two small green-white indicator
  lamps Ø10 left of it at ~(260/300, 105).
- 4 small black rubber feet ~15 high, inset from the corners.

### xy-srf-i — hydrocollator 70 L (photo 1: front, lid closed; photo 2: front-left, lid open)
- Brushed stainless cabinet; the photo's proportions give a body ~585 W × 430 D, top at ~820: wider than the 560
  estimate (W/H of the front = 0.68) → size W 620 including the side handles.
- Thin black trim strips on the four vertical corners; a black frame band ~25 high under the body; 4 swivel castors
  Ø75 (grey wheels, chrome forks), the front pair with brake pedals.
- Top: stainless rim frame ~20 high, slightly larger than the body; a flat stainless lid (inset, ~12) hinged at the back,
  with a small chrome arched bar handle at the front middle.
- Front upper right: control box ~180 × 120 × 15, light-grey frame, white face, small LED display at the top left,
  4 small blue/white keys, a blue band along its bottom.
- Both side faces: recessed grab handle (chrome bar over a dark slot) at ~740 high, near the front.
- Modelled closed (photo 1 = main photo).

### xy-srf-iv — hydrocollator 140 L (photo: front-RIGHT view)
- Brushed stainless tank cabinet 620 × 520, tank rim at ~920; 4 rubber castors Ø75 (grey wheels, brakes front).
- Open top: a flat rim ~45 wide around a basin (stainless inside, a dark water line); the sliding cover pushed to the
  back (flat stainless plate over the rear ~120 of the opening, with a round bar along its front edge).
- Rear upstand across the whole back: stainless box ~620 × 70 × 130 above the rim (top ~1050); on its front, right
  half: white control panel ~170 × 70 (LED display, blue keys, blue band).
- Chrome water-inlet pipe Ø22: out of the upstand front at the right (x≈500), forward ~140, down into the tank.
- Right side face: chrome bar grab handle on standoffs at ~800 high near the front.
- Front: big blue Xiangyu logo — round blue mark Ø110 + two blue text lines — at the left half, ~430 high.

### xy-sl-cvi — walk-in tub with transfer beam (photo: front-left; door face on the right of the photo)
- Perspective check: the face with the door is the SHORT side, the long side is the photo's left face; the rim is at
  ~720 (printed "720/1000": rim / top of the transfer beam). The door face is taken as the front →
  size [860, 1270, 1000] (inventory W and D swapped).
- White glossy box 860 × 1270, rim ~100 wide flat with rounded edges at 720; a recessed plinth band ~70 at the bottom.
- Front (door face): U-shaped door from the left ~20 to ~560, top at the rim, rounded bottom corners r≈90, framed by
  a light-teal (#8ccfd8) trim line ~18 wide; a white vertical hinge strip at its right edge; right of the door a fixed
  panel with a recessed rounded-rectangle moulding and the blue logo at the top.
- On the door: a teal horizontal swing arm ~420 long at ~620 with a red lever knob near its left, a teal diagonal rod
  (lever) from the arm's left down to ~330 at the middle of the door.
- Teal rail lying over the opening from the front rim at x≈360 back ~500 (door top bar).
- Left side (long face): a large recessed rounded panel in the back 2/3, with a horizontal handle moulding across it
  at ~400; a vertical seam near the front corner.
- Rim: chrome valve cluster with a blue lever at the back-left corner; a black round cap Ø80 on the left rim ~1/4 from
  the front; a chrome shower disc on the inner back wall.
- Inside: basin visible; a seat block at the back with a white cushion backrest standing at the back end.
- Right rim: a light-teal transfer beam ~1000 long × 150 high × 70 thick at ~850–1000 along the right long side,
  a grey support bracket on the rim near the front, at the back end a grey carriage box and a grey L arm going in over
  the seat (horizontal ~350 then down ~150) with a red pin and a grey loop handle.

### xy-sl-cviii — dry hydromassage table (photo: front-RIGHT view)
- White glossy body 2100 × 900, plan corners rounded r≈90, height to the mattress ~550.
- Thick black top: a black rim band ~110 high with rounded edges around the top, the mattress field dark grey
  (#2a2c30) with a thin lighter seam line: a head section at the left ~500 long, and an inset outline line.
- A thin black horizontal groove line all along the front at ~330 high, curving slightly.
- Black four-pointed star graphic at the LEFT end of the front: a vertical concave-sided stroke from the top band to
  ~120 off the floor, crossing the groove line.
- Black bottom band ~160 high on the right ~55% of the front (and right end) with a rounded ramp at its left start;
  white logo (round mark + XIANGYU MEDICAL) on it; small chrome feet.
- Monitor ~10" (white frame ~280 × 220 × 40, light screen) on a white square pole 60 × 60 rising behind the table
  back at ~45% of the length, top ~1330 → size H 1330 (inventory 700 = the table only; sizeNote "with pole ~1300").

### xy-sl-cviii-luxury — the same table with the hood (photo: front-RIGHT view)
- Table as above.
- Hood over the head (left) end ~950 long: a white fixed shell rising ~330 above the top (rounded, sloping down at its
  right end), a black front strip on its right end with a round speaker; the hood lid (white translucent, printed
  panels) hinged at the top back and swung up ~70°, top ~1500.
- Black thicker frame under the hood base. Monitor on the pole at the back, ~45% of the length.

### xy-sl-cxi — ozone spa bath (photo: front-RIGHT view; controls at the RIGHT end)
- White glossy tub 1970 × 800, rim top 850; a rim lip ~60 with a seam under it; the body below bulging slightly and
  tapering to a rounded bottom at ~120; plan ends rounded r≈220; 4 short white tapered legs Ø60 × 120.
- Basin 1560 × 560 open, shifted to the left: a wider deck (~290) at the right (head) end.
- Rim: chrome grab bar (U on two posts, ~300 long) on the front rim at ~1/4 of the length from the left, another on
  the back rim at ~60%.
- Right end deck: chrome round lever valve and a square chrome valve on the front rim, a flat grey operation panel
  ~250 × 120 on the deck, a chrome valve behind, a chrome hand shower on a post at the back-right.
- Light-blue (#9cb4e8) vertical band on the front near the right end, wide at the top, waisted, flaring at the bottom,
  with white jet dots along its edges; blue XIANGYU MEDICAL logo at the left of the front at ~600 high; a soft
  moulding line sweeping from the left top down to the middle of the front.
- Hand shower to ~990 → size H 990.

### xy-sl-ri — children whirlpool tub (photo: front-left)
- White glossy body 1305 × 1010, top 1010, vertical corners r≈150, upper body overhanging a recessed plinth (~230
  high, set in 40) that carries a blue lettering band (oval light-blue plate with blue text) on its front.
- Left end: control deck ~330 wide over the full depth, flat; on it 3 red buttons, 3 chrome buttons in a row, a round
  chrome dial with a blue ring; screws/seam lines on the left end face, logo at its upper front.
- Front: U-shaped clear glass window from the deck to near the right end (~x 420–1180), top at the rim, bottom at
  ~520, rounded lower corners; inside visible water.
- Lilac (#b2a8e0) padded bars ~70 × 50 on the front and back rims over the basin length.
- Right end rim with rounded shoulders; a chrome jet disc on the inner right wall; water inside.

### xy-sl-rii — children whirlpool tub with LCD (photo: front-left)
- Left end: control tower ~330 wide, top ~1128 (higher than the tub rim ~1010), white top deck with a membrane/LCD
  panel and a red button, a chrome dial with a blue ring; its left end face dark graphite (#3a3f46) with a bulging top
  profile and an inward concave cut at the bottom (white front pillar wrapping it).
- Tub part to the right: white, top ~1010, big rectangular glass window on the front (~x 520–1290, y 400–870) under a
  tall lilac padded front rim bar ~90; lilac back rim bar; right end rim with rounded shoulders.
- A horizontal recessed groove on the front at ~260; plinth with rounded bottom edges.

### xy-sl-riii — children gait pool (photo: front-left)
- 3000 × 1800 × 1080: white acrylic deck ~120 thick with rounded edges all round, overhanging the skirt slightly.
- Green (#4fb848) skirt panels with vertical ribs (~100 pitch) on all sides.
- Front: big glass window (gait observation) from ~x 1300 to 2550, top at the deck, bottom at ~430, lower right corner
  chamfered, white frame border; the same window in the back wall.
- Inside: the walk lane along the length; two stainless handrails Ø32 (at ~650 and ~850) along the front and back inner
  walls over the window length; a moulded step/seat at the left end with a stainless rail; a rail at the right end.
- Back rim: grey round speaker grille; at the back-right two chrome posts with a fold-up LCD screen (dark, grey frame)
  between them; chrome jets in the inner walls.
- Front rim, left corner: dark control keypad panel, chrome and blue buttons.

### xy-sl-rv — mobile baby swimming tub (photo: front, slightly from the left)
- Cabinet ~1000 W × 700 D, deck at ~720; 4 castors Ø90 (grey).
- Front face: green (#4fb848) upper with a wave-shaped lower edge bordered by a darker green line: a hump over the
  knee recess at the left (white below, with a vertical split line), a valley, a hump around the right-hand cartoon;
  white below the wave.
- Cartoon sticker in the right hump: white oval, blue/purple umbrella, red crabs, sand, bucket; fish and bubbles below.
- Deck: white flat top ~30; round tub Ø~640 inset at the left-centre (green-tinted basin inside in RV), blue dots
  around its rim.
- Right end: a raised white block over the back right (~420 wide × 300 deep × 180 above the deck) with green round cups
  on top and a green recessed handle on its front; a chrome gooseneck faucet in front of it arching over the tub.
- Fold-out green tray ~300 × 560 on the right end at the block's top level, on a chrome folding bracket.
- Size: cabinet ~1000 + tray ~300 = 1300; top of the block ~900.

### xy-sl-riv — baby tub, microcomputer (photo: front, slightly from the left)
- Same body as RV; basin white; wave line border lighter teal-green; the raised block wider, stepped (lower step at
  the front right), the faucet on its left; the tray on the right. Chair in the photo = accessory, not modelled.

### hyz-iiy — perianal fumigation chair + console (photo: front, chair left, console right)
- Chair ~760 wide × 800 deep: white glossy base tub (wider at the top ~640, narrowing to ~560 at the floor, rounded
  corners) to ~440; on its front a blue (#4a5fc0) inverted-U line with a round blue/white logo Ø120.
- Lilac (#c9c8e3) seat cushion ~560 × 500 × 70 with a round hole Ø170 (dark inside) in the middle; a clear acrylic
  splash dome over the back half of the seat around the hole.
- Armrests: thick white rounded blocks either side, top ~760, bottom ~430, ~650 long, a dark side pocket slot on the
  outer face, rounded front caps.
- Backrest: lilac padded panel ~600 wide × 110 thick from the seat to 1250, reclined ~10°, quilted lines.
- Console tower (right): ~420 W × 350 D × 1100; front view "C": a head ~420 wide on top, below it the column ~330 wide
  (set in on the left side, the side towards the chair), a rounded foot block sticking out to the left at the bottom
  (~350 high); blue edge line along the front left edge; blue inverted-U line with the round logo on the front;
  sloped light-grey control panel on the head (LCD, blue and orange keys, a green rocker switch at the right).

### hyz-iiic — horizontal steam capsule (photo: front, slightly from the left; head end LEFT)
- White glossy car-like shell 1950 × 900: tallest at the head end (left, ~1300), the top running level then sloping
  down over the foot end to a rounded nose at the right; flat-ish sides with rounded top edges.
- Grey (#8a909a) lower skirt: the whole lower band ~150 and the rear (head) end panel; the white shell's lower edge
  arches up over the round panel at the left.
- Blue double seam line (lid split): from the head-end top down the side, a V dipping down at ~1/3 of the length,
  rising and running level towards the foot end at ~820 high; two stainless hinge plates on it near the foot end.
- On the lid side: a rounded hand hole ~260 × 130 with a stainless bar inside; a light oval cover plate on the top;
  a blue tinted window (dome) on the top at the head-middle.
- Lower left of the side: round panel Ø~520, slightly proud, with a label, green buttons and a small display.
- Upper left: round music-player speaker disc Ø~140.
- 5 castors Ø60 (2 per side + 1 at the nose).

## Final checks
Every device rendered `ok` and was checked on `renders/<id>-compare.png` item by item against the parts list.

- **rh-sr-ii** — done. Size changed 460 → 420 W (the photo's front is narrower than the estimate: H/W ≈ 1.57),
  [420, 340, 660]. Fixed in rounds: the oval logo plate (an ellipse slab; a flattened sphere shaded dark), lid made
  clear glass with a raised rim and a shorter moulded handle, side handle as a broad chrome D near the middle, vent
  moved to the lower middle of the left side. Approximate: the vent is a 5 × 9 grid of square holes; the logo lettering
  is blue bars (no text in the format).
- **xy-srf-i** — done. Size 560 → 620 W (body 585 from the photo's W/H, + the side handles). Control box moved to the
  photo's place (centre-right, upper); corner trims thinned. Modelled with the lid closed (photo 1).
- **xy-srf-iv** — done, size as inventory. Photo is a front-right view: handle on the right side, inlet pipe and
  control panel at the right of the upstand. Approximate: the slid-back cover is a flat plate + bar at the back of the
  opening; logo lettering as bars.
- **xy-sl-cvi** — done. Size [860, 1270, 1000] (inventory [1270, 860, 1000] with W/D swapped): the perspective of the
  photo shows the door on the short side, rim at ~720 (printed "720/1000"). Plinth changed from a grey recess to white
  with a groove (photo). Approximate: exact length / position of the transfer beam (perspective; drawn along the right
  rim 100–1110 on a grey front bracket); the left long side (recessed panel + handle moulding) is not visible in the
  front-right render.
- **xy-sl-cviii** — done. Size H 700 → 1330: the monitor on its pole (photo; inventory note "with pole ~1300"). Star
  graphic redrawn with thin concave arms (first version was a fat star). Approximate: the logo text is white bars.
- **xy-sl-cviii-luxury** — done, size as inventory (lid open to ~1500). Hood made taller/flatter after the first
  render. Approximate: the hood shell is opaque white (photo: translucent white); the lid's printed interior is four
  dark rectangles; the black strip with the speaker is a simple rounded box.
- **xy-sl-cxi** — done. Size H 850 → 990 (rim at the printed 850, the hand shower above it). Photo front-right,
  controls at the right end. The light-blue band was reshaped (wide top, waist, narrow foot) and split into three
  pieces that follow the body's taper (it stood off the hull at the bottom); the hull now tapers more to the bottom.
  Approximate: the front moulding line is a thin tube; grab-bar positions read from a perspective photo.
- **xy-sl-ri** — done, size as inventory. Water volume added and the inner front wall removed so the green water shows
  through the glass (it read as a white panel). Approximate: the plinth lettering is a blue bar on a light-blue plate.
- **xy-sl-rii** — done, size as inventory. Tower: graphite core (left face + lower front recess) under a white shell
  from 300 up; window widened to the photo (515–1250) and lowered; water shows through the glass. Approximate: the LCD
  keypad on the tower top is a dark screen + grey key field (no screenCrop).
- **xy-sl-riii** — done. Size H 1080 → 1260: the fold-up LCD screen is drawn raised (photo); deck top at the printed
  1080. Inner walls rebuilt in pieces so both gait windows are see-through (lane rails visible through the front glass);
  ribs kept off both windows. Approximate: speaker grille and jets are plain discs.
- **xy-sl-rv** — done, size as inventory estimate. Wave edge drawn from sampled Béziers with a 20 mm offset border;
  cartoon (umbrella, crabs, sand, bucket, fish, bubbles) simplified to flat coloured shapes.
- **xy-sl-riv** — done, same body as RV (white basin, lighter teal border, faucet a bit further right); the chair in the
  photo is an accessory, not modelled. Approximate: the stepped block is the same two-block shape as RV.
- **hyz-iiy** — done, size as inventory. Console reworked after the first render: the head has a short vertical left
  edge then the diagonal brace, its top slopes 12° to the front with the control panel, LCD, keys and the green switch
  on it; armrest pads slope 15°. Approximate: the arm pockets are dark slots; the splash dome is an ellipsoid; the
  quilting is thin lines.
- **hyz-iiic** — done; size H 1300 → 1310 (blue window dome on top). Nose made rounder (dome 150) and the grey chassis
  shortened so it no longer shows past the nose; seam ends at the hinges. Approximate: the seam path and the white
  shell's arch over the round panel are read from one perspective photo; the music player and panel controls are
  simple discs / decals; the back side copies the front's seam, hand hole and hinges.
