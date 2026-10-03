# Detail review — batch pediatric-1 (14 devices)

Each device: the catalogue photo(s) checked at full size (crops in `tools/medical/scratch/pd1-review/`) against the
angle / front / side / top renders; differences fixed in the generators `tools/medical/gen/pd1_*.py` and re-rendered
(all 14 render `ok`, .txt newer than the json; final sheets `tools/medical/renders/<id>-compare.png`).
Shared change: `pd1_lib.py` adds the digits 0–9 to the stroke font (setdefault, like k4lib; only for this batch's imports).
Side check: the angle camera looks from the front-right; most photos here are taken from the front-left (mirror side),
so sides were compared on the front/side/top renders.

## circular-walking
- Found: foam arcs too pillowy (edge radius 28 → glossy rolls); the photo's arcs have nearly sharp edges.
- Fixed: edge radius 14. Order of colours, alternation back/front and the S-path match the photo (checked on the top render).
- Not matchable: none at sheet scale.

## soft-building-blocks
- Found: the big front-left blue cube doubled as the left pillar's support, so the whole left castle stood on it and the
  cube was not in front; the wedges were too close to the castles. In the photo the front blue cube (with the short red
  cylinder on its back part) stands well in front of the castle, the left pillar stands on its own blue cube hidden behind
  it (like the right pillar), the right castle is a step forward of the left one, and the two wedges lie in front of all.
- Fixed: left pillar on its own blue cube; big blue cube moved forward (z 470–740), red cylinder Ø150 on its back part;
  right castle moved 50 forward; wedges moved to the front (z 740–955). Depth now 960 (estimate 600 in the inventory; the
  photo's arrangement is deeper than wide-and-flat).
- Not matchable: exact depths from one oblique photo (relative order is right).

## square-combined-training-frame
- Found: straps were plain with a single grey line (photo: white printed straps with dark lettering every ~75 mm); the
  swing had no white tube frame and the wrong layer thicknesses (photo: thin green top, thicker yellow, red bottom); foam
  rolls on the swing too big and too far left; climbing wall had 16 holds at made-up places (photo 2 shows ~20) and plank
  joints only on the outside; cartons were 4 flat boxes with 2 labels (photo: a stack of ~5 cream cartons, red-brown
  printed labels on fronts and tops).
- Fixed: strap lettering as thin dark-grey blocks every 75 mm on both faces; white tube frame round the platform; layers
  red 52 / yellow 30 / green 16; rolls Ø172 and Ø150 at the photo's positions; 20 holds traced from photo 2 (seen from
  behind → mirrored to model x) with the photo's colours; 9 plank joints on both faces of the wall; 5 cartons stacked
  (front one turned, one end-on at the left, two at the back, one across on top) with label blocks on fronts and tops.
- Checked as right: open side faces (both photos show the sides open), ladder back-left with grey top rung, wall
  back-right leaning out, 10 blue knobs, arch boards with 3 holes.
- Not matchable: the strap/carton print is only blocks, not real characters.

## triangle-ball-pool
- Found: all walls alternated red/yellow with flat tops; in the photo the back and right walls are yellow with a wavy
  (humped) top, only the front wall and the left apex alternate. Cylinder bands were in the wrong order (photo, top → bottom:
  blue, yellow, red, blue, yellow, red); the cylinder had a red cap (photo: hollow, red inner lining).
- Fixed: back/right wall segments are yellow slabs with a rounded hump on top (liner lowered to follow); 6 bands in the
  photo's order; hollow cylinder with red inner wall and a tan inner floor.
- Not matchable: the wave is one hump per segment (the photo's waves are irregular).

## xyrt-10
- Found: backrest too short (353 vs ~480 in the photo, measured on the back plane), tray too high (750 vs ~650, the tray is
  just under the white crossbars), crossbars too high; the lower pad was 3 bulbous rolls with 3 knobs (photo: one flat
  hip pad with a darker strap across; the blue knobs are on the front posts and the tray clamp, not on the pad);
  "hinge" was one chrome block; tray top was grained wood (photo: smooth pale laminate with orange-brown edge); the
  backrest strap stuck out past the backrest.
- Fixed: backrest 760–1218 with the strap at 925–1035 flush with the edges; crossbars at 692/728; tray at 630–658 with
  the crescent chest pad on it, slide rails, clamps and front posts lowered to match, black caps on the rail ends; one
  flat lower pad 330–640 with a dark-blue strap; two locking knobs on the outer side of each front post, two on the
  clamp's left end; telescopic/hinge details on both rear uprights (black collar, chrome pivot with bolt and black knob,
  chrome clamp, thinner inner tube); laminate tray colours; foot-box back board 255 high.
- Not matchable: the photo's tray looks offset to the right of the frame (lateral slide) — kept centred within the printed
  700 width.

## xyrt-100
- Found: number column was white dashes; butterfly two grey rectangles; pink strip a solid bar (photo: small pink
  handwritten letters); rear crossbar too high; wood slightly too orange.
- Fixed: digits 1…9, 0 drawn with the stroke font (0, 5, 6, 7, 9 added in pd1_lib next to k4lib's 1–4); white butterfly
  outline with pink spots and a body, tilted; strip of small pink letter marks; ABC moved right of the number column as in
  the photo; rear crossbar 235; paler wood.
- Not matchable: "8" in the shared font reads like a B; the strip's cursive letters are marks.

## xyrt-101
- Found: the drawing was a stick figure with a skirt (photo: a chibi baby — big round head, big ears at different
  heights, hair tuft to the upper left, eyes with brows, small open mouth, shirt with hands together at the chest,
  shorts, short legs with shoes), plus two columns of Chinese characters, a crayon, bugs and a small butterfly; side rung
  too low; a green knob on each front leg missing; wood too orange.
- Fixed: drawing traced from a crop of the photo through a bilinear map of the board's perspective quad onto the board
  (head, ears with curls, eyes, brows, nose, mouth, hair tuft, shirt, arms, hands, shorts, legs, shoes, crayon); two
  columns of character marks, bugs and butterfly as dark marks; side rung at 330; green knobs on the front legs at 480;
  paler wood.
- Not matchable: characters are cross marks, not real Chinese glyphs.

## xyrt-103
- Found: the table column did not widen under the top (photo: a short T-flare).
- Fixed: flare on both pedestal boards of the table. Layout, colours, pegs (blue/yellow/red/green), hammer, picture cards
  checked as right.
- Not matchable: the picture cards' pictures are coloured patches.

## xyrt-106
- Found: band heights wrong (photo from the floor: wide 25–325, narrow 325–575, wide 575–725, narrow top 725–1000; the
  model had the steps at 360/525/730) and the wide bands too wide; base plate same dark green as the board (photo: light
  yellow-green base, darker board); strap slots as pale decals.
- Fixed: band heights/widths (hw 114 / 100), gussets moved to the new edges, base #78bc4a, board darker #3f8a32, slots as
  thin black boxes at the photo's spacing.
- Not matchable: the photo's black claw-like foot brackets are simplified to gussets and L foot stops.

## xyrt-107
- Found: the foot unit was a flat floor frame with a short roller in front of the board (the "tilt" weak spot). The photo
  (crop) shows a LONG brown wooden roller across the full width with tan wooden rings round it and a thin light-wood
  rail with small clips in front of it, mounted raised on the board's foot, tilting with the board.
- Fixed: foot unit rebuilt on the board's frame (turned with the board): side plates, full-width brown roller Ø60, three
  tan rings, light front rail with clips; the floor slats removed.
- Not matchable: none at sheet scale.

## xyrt-108
- Found: the sliding block lacked the light rim along its lower end (photo: L-shaped light rim, right side and bottom).
- Fixed: added the lower rim. Trough, rods, prop, dowel, peg, red knobs, grooves and front stops checked as right.

## xyrt-11
- Found: rails too light/yellow (photo: stained orange-brown oak), oak rungs too thick (photo ~25 mm, the white end
  rungs thicker).
- Fixed: rails #c8883e, oak rungs Ø25 in a slightly darker stain, white top/bottom rungs Ø32. Depth 200 kept (the photo
  shows a flat ladder; the brackets reach the wall).

## xyrt-116
- Found: handlebar loop too flat (photo ~400 × 195), telescopic sleeve too high on the post (photo: lower half), pedals flat
  plates (photo: bulky black pedals with a raised heel).
- Fixed: loop 808–1000 with the post shortened to it; sleeve 395–640 with the knob at 560; heel cups and side rims on the
  pedals.

## xyrt-117
- Found: rear rubber feet had no flared pad (photo: a black flared rubber foot under each end).
- Fixed: black pads under the rear feet. Lever, damper, seat, rail, footplates checked as right.

## Left approximate (format)
Printed / drawn lettering is stroke marks (Chinese characters, strap and carton print, cursive alphabet); single-photo
depth placement of the soft blocks; irregular foam wave tops as regular humps.
