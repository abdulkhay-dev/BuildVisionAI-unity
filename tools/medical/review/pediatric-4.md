# Detail review — batches pediatric-4 + pediatric-5 (19 devices)

Each device: the catalogue photo(s) read at full size (crops in `tools/medical/scratch/pd4-review/`) against the
angle / front / side / top renders; differences fixed in the generators `tools/medical/gen/pd4_*.py` (originals kept as
`scratch/pd4-review/*.orig.py`) and re-rendered. All 19 render `ok`, .txt newer than the json; final sheets
`tools/medical/renders/<id>-compare.png`.
Library check: `pd4lib.py` imports only `lib` and `h1lib` (no `p1lib`), and no pd4 script calls `D.decal` positionally,
so the p1lib decal argument-order pitfall does not apply to this batch.
Sides: most photos here are taken from the front-left, the angle camera looks from the front-right, so sides were
compared on the front/side/top renders.

## xyrt-44
- Found: fish were small glossy 3D blobs (beads), clumped; no tails shape/eyes/stripes; weeds single sticks; bubbles sparse singles; photo: ~12 big flat fish per panel spread evenly (yellow with black bars, orange-red, magenta, lime, violet), forked tails, dark eyes; green and violet weed sprigs; clusters of white bubbles; panel edges crisper.
- Fixed: matte flat fish bodies 96x56 on a jittered 3-column grid, forked tail slabs, dark eye, black bar on yellow fish, yellow fin on others; weed sprigs stem+2 leaves (green/violet); 3-dot bubble clusters (18 per outer face); panel edge r 22->14.
- Not matchable: printed fabric is drawn as flat marks (no texture for this device), fish shapes simplified.
## xyrt-45
- Found: cuffs were 10 identical rows of big bulbous turquoise lumps (almost no black showing), stiff paddle-like Velcro tabs in a neat row; photo: wide black bands with smaller flat turquoise pockets (black ~half of the area), laid loosely and overlapping, black straps rising at the back at random angles; castors small (52 vs ~60).
- Fixed: each cuff its own band 60 wide with 4 pockets 34 wide x 18 high, random shift/turn, alternate cuffs lying over neighbours; Velcro ends thinner, random height/lean; cuffs kept inside the tray lip; castors 60.
- Not matchable: the crumpled heap is still tidier than the photo.
## xyrt-46
- Found: bags were rigid bottle/hexagonal prisms standing in a perfectly even row with flat faces; photo: soft rounded sacks touching, slightly different sizes, leaning with the gathered neck at the back-top, rings (~75) lying on top.
- Fixed: each sack its own rounded loft (round corners, full top, neck drawn back), random width/height/tilt; rings Ø76 tilted back on the necks; castors 60.
- Not matchable: fabric creases.
## xyrt-5
- Found: side boards were a plain A-shaped plate with two rectangular windows; photo: each board is two horse necks (front + back) close together under the roof and spreading down, mane bumps on the back edge of each neck, a head with snout and an ear peg, an X brace between the necks, a lower body with two bottom lobes on the pivots and an arch, the seat seen through the window above it; the roof covered both heads (photo: the roof sits over the front necks, the back heads stand free and the back tubes meet the back necks below the heads); the white hand grip between the green necks was missing.
- Fixed: boards rebuilt from neck/body/brace slabs (mane bumps, snout, ears on necks, X brace, lobed body with arch, lower body 410 high); roof depth z 645–800; back tubes end on the back necks at 1240; white grips between the necks.
- Not matchable: exact horse-head curves (outline approximated).
## xyrt-50
- Found: slings 250 wide (photo: each ~0.2 of the rail length, ~165) so they nearly filled the frame; frame cold grey (photo: warm stainless).
- Fixed: slings 165 wide at the same centres; frame metal#c8c2b2.
- Not matchable: fabric folds in the sling bottoms.
## xyrt-6
- Found: the wooden plate had square ends; in the photo its right end runs down to the base as a ramp. Everything else (posts, levers pointing left, knobs on the front posts, rails, base colours, bevelled base ends, label) matches.
- Fixed: last 160 mm of the plate is a ramp (5 strips across, following the plate's cross slope).
- Not matchable: plate thickness/slope direction can only be estimated from the one oblique photo.
## xyrt-65
- Found: the big hoops stood on small white/red cube "clamps" on the back bridge; photos 1+2: yellow and green hoops are held by round stud connectors (blue under yellow, red under green) on the back part of the front bridge, the blue+red pair stands in a yellow brick on the floor at the bridge's right end; the small hoops were one overlapping ring (photo: 4 hoops fanned out of the red double brick); clamps were 16 plain cubes (photo: ~24 small blue/green C clips); only 3 bean bags, no prints (photo: green, red, blue, yellow with white printed labels).
- Fixed: hoops moved onto the front bridge with lathe connectors + grips; yellow half brick under the blue/red hoops; small hoops fanned (lean 6–30°, staggered); 24 C clips (arched tubes with a foot) in blue and green; 4 bean bags with white label squares.
- Not matchable: hand/foot print textures and bean-bag lettering (flat shapes only).
## xyrt-66
- Checked: boards (left set back with tongue at the back, right set forward with tongue + white label at the front), rails on the outer edges with black U grips, wheels with green holed hubs, crank axles — all match; no change.
## xyrt-67
- Found: the photo shows the threading cords' ends sticking out at the left end of the strips.
- Fixed: cords run 45 mm past the first rod.
- Not matchable: the rolled-up strips in the photo background are not part of the model (the same strips rolled).
## xyrt-7
- Found: the side faces were drawn as grained wood with strong plank lines; the photo shows plain beige laminate.
- Fixed: side faces plastic#dcc6a8 (plain laminate). Steps, rails, posts with knobs, trims match.
## xyrt-79
- Found: the two lobes were small bumps (photo: big lobes with the slot + hole well inside them); the top was thin (55) vs the photo's thick rounded edge; the blue dome base was almost as wide as the top (photo: tucked well under, ~0.7 of the top).
- Fixed: lobes +46 mm over 80°, slots/holes moved out into them; top 72 thick with r 20 edge; base Ø504 at the top tapering to Ø200 contact.
## xyrt-80
- Checked: disc, rim band, field ring, 4 tangential U handles at ~90° (measured on the photo ellipse: 50/160/244/323° vs model 62/152/242/332°, within the reading error) — no change.
## xyrt-83
- Found: the bumpy top was 4 sparse rows of tiny studs (~60 mm pitch), almost invisible; photo: the whole top densely covered with nubs.
- Fixed: 6 staggered rows of Ø12 nubs at ~22 mm pitch over every arc (following the loaf crown). Colours (yellow at back/front/left/right, green on the diagonals) checked on the top render against the photo.
- Not matchable: the straight pieces of photo 2 (separate pieces of the set; the model is the ring of photo 1); the real nubs are even finer.
## xyrt-93
- Checked: quarter colours and seam angles (photo front red spans ~57°–158°, model 65°–155°), yellow seam plates top and bottom, 20 yellow posts with collars, caps on the top ring, proportions — no change.
## xyrt-8
- Found: base and strips darker brown than the photo's light beech with orange-brown strips; pad straps narrower than the photo's wide bands (~76 vs 58).
- Fixed: base wood#ecca8e, strips/clamps wood#d08e48; straps 76 wide.
- Checked as right: J handle on the back-left into the mast top, orange top clamp with label, periwinkle plates + wedge pads, foot back plate with ticks and black heel plates, foot straps, width rod with periwinkle end blocks and black knobs, blue clamp knob.
- Not matchable: the loose diagonal drape of the fabric straps (drawn as a symmetric loop).
## xyrt-9
- Found: the tray (photo 2) is a smooth very pale laminate, the model had grained mid-brown wood; panels/strips a bit greyer than the photo's orange beech.
- Fixed: tray plastic#f1d9a8; panels wood#ffbe6a, light parts wood#fde2b0.
- Checked as right: panel shape (upright back edge, front edge leaning to the floor, arch cut, round hand hole, bolts), arm strips, maroon seat/backrest/headrest with rainbow band, pommel on the steel bar with knob, slotted footrest back, footboard with divider and rainbow straps, low stretcher, castors.
- Not matchable: the panels' wood texture renders slightly browner than the photo's orange.
## xyrt-87
- Found: the stairs were one 740-wide flight with a dark-grey left and black right side; in the photo the black stepped side shows ABOVE the treads to the right of the front flight, i.e. two stair modules side by side — the left one (dark grey sides) reaching further forward, the right one (black sides) set back by two steps.
- Fixed: two 370-wide modules, the right one set back 440 with black sides, the left with dark grey sides.
- Slide: checked against the photo — red wedge with rainbow stripes from under the left tunnel end down to the front-left, its foot beside the green mat; a longer slide (tried 1100) runs into the mat, so the 900 run is kept.
- Not matchable: foam creases; the exact depth arrangement from one photo.
## hyz-iir
- Found: the hood was a dome plus a separate boxy tunnel with a step between them (photo: one helmet shell, highest over the foot end, sloping and narrowing smoothly into the arched head tunnel); the windows were flat rounded rectangles floating on the curve, the "teardrop" was a pill/C shape; windows were whitish (photo: grey-blue tinted glass); the chrome handle hung off the shell.
- Fixed: hood rebuilt as one loft along x (low rounded nose at the foot end, constant section over the window zone, tapering into the tunnel, the dark arch opening on its end); windows drawn as thin arc bands on the shell's rounded corner (30 slices across x, following the section) — a big rounded window over the foot end, a teardrop beside it (round at the left, pointed and lower to the right), a long strip on the top; tinted glass gloss#c8d3dd; handle seated in its lilac recess on the shell.
- Not matchable: the sculpted fins/creases of the shell (tried as swept ridges — they read as tubes stuck on, removed); the window edges show faint slice steps up close.
## xyrt-41
- Found: the foot plate stood square to the bed (photo: opened past square, lying flatter towards the floor); the small rail frame at the head end ran along the bed on the front side (photo: an inverted U standing across the base, front rail to back rail); the red stripe inside the aluminium side rails was missing.
- Fixed: foot plate + bow opened 15° (rot about the hinge before the bed tilt); rail frame turned across the base at x 190; red stripe along each side rail.
- Checked as right: base frame on corner legs with levelling feet and castors, pivot posts near the foot end, black actuator, blue pad (head + main), 3 straps with buckles, leg slot, wooden chest tray with U cut-out and stainless bow, side lever with knob, blue hand switch on its cable.
