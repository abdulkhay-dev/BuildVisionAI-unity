# table-3 — notes

Generators: `tools/medical/gen/t3_*.py` (shared: `t3_alclib.py` ALC capsule body + stroke lettering,
`t3_jyzlib.py` cervical pole/arm/sling, harness belts, louvres; `t3_jyz3.py a|b` builds JYZ-IIIA / IIIB).
All 14 render `ok`; each was checked on its compare sheet after the last change.

## xy-73 — PT training table, electric, one-piece top
Parts (photo): one-piece light-blue PU pad 2020×1240 with rounded plan corners, ~85 thick, square-ish edges; thin
white frame band under it; two white lift plates per side (vertical edge on the LEFT, straight slope down to the
right) with grey "XIANG YU" / "MEDICAL" lettering and black bolts; grey Linak actuator between; white base frame
(2 long rails, end bars, middle bar) on 4 short corner legs with grey caps top and bottom; castors inside the legs;
small dark hand-switch hook under the right end.
Final check: all present. Approximate: lettering = grey blocks; modelled at the photo's pose (top ≈ 645), not at the
max height of 1000 (size kept as printed).

## xy-80 — nesting stools, set of 5
Parts: 5 graded plywood tops (light ply edge with a ply line, honey veneer on top, small metal tag), grey Ø25 tube
legs as inverted U's along the width at front and back with bent top corners, black rubber feet.
Final check: OK. Approximate: shown STORED nested (front edges aligned, all inside the 550×380 footprint) instead of
the photo's staggered display, so the item keeps its printed size.

## xy-81 — PT stool
Parts: thick black PU saddle seat (sides higher than the middle, rounded ends), black seat plate and height lever
paddle under the left; chrome piston in a thicker chrome sleeve with black collar; black hub; 5 flat chrome arms with
black end caps; 5 black twin castors.
Final check: OK. Approximate: castors are the standard castor part (single wheel look, Ø50).

## xy-83 — overbed table
Parts: wood top 850×450 (square left end, round right end, light ply edge, brown veneer), black stops under it;
white telescopic column (lower 50 sq, upper 40 sq) near the left end with black lock knob on its left; white flat
diagonal brace to the long base bar; H base (two crossbars along the depth, long bar along x), black end caps,
4 grey castors.
Final check: OK.

## xy-kgj-2 — hip joint training chair
Parts: white square-tube base frame on 4 black foot blocks; posts and seat rails; bolted side rail; tall rear frame
on the left with a white top cap and guide rod; navy PU seat and reclined backrest on a white frame; white tube
arm supports with black padded arm pads curling down at the front; grey steel platform with two pegs of green
plates, a storage peg with a green plate at the front-left; two leg levers: pivot hubs under the seat front,
light-blue thigh cuff with black strap, double chrome rods down to a small floor wheel, light-blue shin cuff with a
black strap. Photo pose: right lever forward-down, left lever abducted 40°.
SIZE: changed to [960, 1380, 880]. The printed 144×66×88 mapped as width 1440 / depth 660 cannot hold the photo
(levers reach ~700 forward of the 640-deep chair); 1440 is most likely the length with the levers forward and 660
the chair width. The bounding box of the photo pose is used.

## xyzg-1 — electrical elbow traction chair
Parts: two white sled skis with black end caps, cross tubes, brass levelers, seat posts; light-blue seat and
backrest with a white tube rim; patient's right (x small): white upright frame with grey bracket, black graduated
elbow dial, black forearm bar with two blue foam cradles (black / grey straps), red lever with chrome end, teal
weight plate on an outward axle, grey motor box + can, small blue control box, coiled remote cord; patient's left
(x large): white bracket out from the backrest, black dial, red bar with chrome extension reaching sideways-forward,
two blue cradles with straps, white post with red sleeve and a teal plate.
Approximate: the mechanism linkages are simplified (the photo is small and busy); cradle shapes are rounded blocks.
Note: in the photo the long reach is on the patient's LEFT (viewer's right from the front); the form text says
"right side" — the photo was followed.

## alc-1 — far-infrared massage bed
Parts: long white glossy capsule shell bulging to the widest line, rounding to a flat top, tucked in to a vertical
plinth; thin pale-blue pin stripe at the widest line; light-blue towel mat over the top; navy XIANGYUYILIAO
lettering (drawn as strokes) on the front; control-panel window on the right end face; 4 small castors.
Final check: OK. Size kept (estimate).

## alc-2 — massage bed with heat cabin
Parts: ALC body (navy stripe), white glossy hood hinged at the left end and open ~60° on two gas struts (cylinder +
rod, chrome feet), hood = arched shell with a light liner and an end cap with the head cut-out; hinges; blue
pillow at the right (head) end; folded blue gown near the hinge; end-face control panel.
SIZE: height 1830 instead of 1700 — the photo's open hood rises higher than the estimate (hood 1150 long at 60°).
Approximate: the hood's free end is a flat cap with rounded edges (photo end is slightly domed).

## alc-3 — massage bed with lumbar traction
Parts: ALC body (navy stripe, no end panel); head end: blue pillow, black neck strap, stainless U hand bar
(Ø32) from both sides with two black Ø110 armpit rolls hanging from the crossbar; grey-blue striped chest and
pelvic harnesses with buckles; white traction straps running to the foot frame; quilted light-blue leg pad with
white straps; white remote with blue display and cable; stainless foot frame (two side tubes out of the end face,
top and middle crossbars, red tensioner).
SIZE: height 1030 instead of 700 (the U bar stands ~300 above the top); width 2150 includes the foot frame.

## jyz-ib — traction table, double motor
Parts: white sheet-steel cabinet on 4 corner posts with dark feet; dark frame strip under the top; split top
(two thick white rounded sections, grey-lilac pads, V gap at the junction, blue edge straps, clips); door gaps,
locks, label; blue control panel in the middle (red digits display, green/red buttons); two blue hand switches on
the right door with cables looping into the cabinet; striped harness belts; small black knob at the left end;
stainless cervical pole at the back with white bar arm, triangle bracket with hole, pulleys, knobs, rope, spring
scale, spreader, white/blue sling.
Approximate: sling is three flat straps; the panel's printed text not drawn.

## jyz-iib — traction table
Parts: console on the right (white lower cabinet on castors, front buttons/switch, label, blue logo; head box with
grille and a sloped panel: dark LCD + blue keys), pole on the console with rod arm, white truss, disc, pulleys,
knobs, scale, spreader, lilac sling to the right; bed: white aprons and cross members, leg frame with low rails
and black feet at the left end; two white rounded trays with lilac pads and purple edge straps; stainless leg-rest
frame and black knee pad at the left end; purple striped harnesses.
Approximate: console panel has no interface picture (no screenCrop).

## jyz-iiia / jyz-iiib — computer traction tables (shared generator)
Parts: head console at the left (lower cabinet, wider head box overhanging toward the head, sloped top panel —
IIIB with the printed interface `med_jyz-iiib_screen`, IIIA a blue panel with dark LCD and keys), grille, blue
logo; pole on the console back with rod arm, white truss, two pulleys, star knobs, side knobs, rope, scale,
spreader, lilac sling to the LEFT; bed cabinet with two louvred doors (3×9 slots), screws, castors; stainless tray
with lilac pad (IIIA darker mauve per its photo); harnesses and a small remote; cantilevered lumbar section: black
joint + arm, white rounded wedge housing, stainless tray + pad, two black knee rests on a crossbar, stainless hand
rails, black cable loop.
Approximate: louvres are thin raised slats; the photo shows no castors under the lumbar section, so none are drawn.

## rh-qyc-b — Rehamaster traction table
Parts: 4-section cyan-blue top (foot section split lengthwise) on a grey board and white frame; handwheel, black
levers and knob on the front; trapezoid white shroud (narrow at the bottom) with grey REHAMASTER lettering; two
white lift columns leaning outward with grey pivots; white base rail and end bars, 4 castors Ø90; traction unit at
the head: white box with the LCD on its chamfered top, post with pulley, chrome rope arm to a black cervical holder
(two pads + U strap) on the head pad; white cantilever arm down to a motor box with black knob and castors; two
black leg holders on a chrome post; black curved grab handles at the foot end; white foot pedal with two blue pads
and a coiled white cable.
Approximate: lettering is uppercase REHAMASTER (photo: "Rehamaster"); modelled at a mid height (top 870) as in
the photo, size kept as printed (H 1020 = max); the traction unit is inside the printed 2032 length.
