# Batch table-2: XY-K-SF tables (Treatment Table.pdf p5–8) + XY-46, XY-70, XY-71, XY-100 (Adult catalogue)

Generators: `tools/medical/gen/sf2.py <id>` (the ten SF tables; it imports the bases of `sf.py` / `sflib.py`, batch table-1)
and `tools/medical/gen/table2.py <id>` (XY-46, XY-70, XY-71, XY-100). All 14 render `ok`.
SF frame: the length runs along x, the width along z, and the front (z = D) is the long side the photo looks at.
Orientation, checked on every photo:
- **Old Z base** (SF-6, 7, 8, 9): the beams lean "\" in SF-6 (head on the left, control box on the right), so SF-6 is
  not flipped. They lean "/" in SF-7, 8 and 9 (head on the right, control box on the left), so those are drawn head-left
  and flipped. In all of them the lettering reads "XIANG YU" on the left column's foot block and "MEDICAL" on the right one.
- **Swan base** (SF-5 new, 6B, 7 new, 8B, 9 new): in all five photos the arms run up from posts on the left ("/"), so
  all are flipped. The top is drawn so that the head ends up where the photo shows it: right in SF-5 new and 6B, left
  in 7 new, 8B and 9 new.
- New in this batch: a better old column (`z_column2` in sf2.py, which replaces sf.z_column only inside sf2.py). It is a
  stout sloping beam with a grey upper face, an arched underside and a foot block that carries the lettering, with black-capped posts.
  It is based on the SF-8 photo, where the column is clearest. The control box (`ctl_box`) is a white tray with a blue
  panel tilted to the front, 3 black knobs and a black cable.
  The steel U-frame at the head end of the old base is also new.

## xy-k-sf-6 [2000, 700, 950] (head left)
Parts from the photo: head raised 25°, split in 3 (far flap, face piece with a slot and plug, near flap); a short dark/steel strut
under the head end; body section; two full-length leg pads side by side; black hinges; old Z base with 4 legs (black
caps), castors, two Z columns, motor and actuator; lettering on the columns; control box with a blue panel at the foot end;
steel U-frame at the head end.
Final check: all present. Approximated: the lettering is rows of grey letter blocks. H = 950 for the raised head (the inventory's 750 is the flat top).

## xy-k-sf-7 [2000, 700, 1030] (head right)
Parts: head raised 40°, split in 3, with a slot; chest; body; two leg sections (far one raised 3°, near one dropped 11° with a
black gas spring and a white rail); old Z base; control box with a blue panel at the left (foot) end; head-end U-frame.
Final check: OK. H = 1030 for the head raised 40°.

## xy-k-sf-8 [2000, 700, 1000] (head right)
Parts: head raised 35°: a narrow far flap, the face piece with a raised oval plug, and a wider near flap tilted 30°;
a steel arm-rest strut with a black knob sticking out under the head end; a chest split in two halves along the length; two long leg
sections splayed in a V (±3–4°); old Z base; control box; U-frame.
Final check: OK. The strut sticks ~80 mm outside the 2000 length. H = 1000 for the raised head.

## xy-k-sf-9 [2000, 720, 950] (head right)
Parts: head raised 25° in 3 pieces (flaps 15°) with the strut; chest with a narrower near arm flap 30 mm lower on a steel post;
body; split legs (near one dropped 12° on a gas spring); old Z base; control box; U-frame.
Final check: OK. Approximated: the far head flap is hidden in the photo, so it is drawn by symmetry.

## xy-k-sf-5-new [2000, 700, 920] (head right)
Parts: long body section (1140); chest; head raised 25°: a wide face piece with a slot, narrow far and near flaps at 12°,
white rails; steel strut under the head end; black gas spring to the head; black levers under the body; swan base
(tube frame, legs with black caps, twin castors, two swan arms with grey fillets, posts, Linak actuator, top frame,
foot loop at the foot = left end).
Final check: OK. H = 920 for the raised head.

## xy-k-sf-6b [2000, 700, 1200] (back right)
Parts: split leg pads on the left (near one 15 mm lower and drooping); seat; at the right, the back in two halves along the length: the
near 470 mm raised 30° with a black actuator under it, and a far 220 mm board lying flat (it is the piece seen below the raised one in
the photo); white coiled cable hanging from the leg end; gas spring under the legs; swan base.
Final check: OK. Approximated: I read the right end as a split back (near half raised, far half flat). The photo is
almost side-on and does not show this clearly. The breathing hole that the inventory mentions is not visible, so none is drawn.
H = 1200 (the inventory's 800 is an estimate; the raised back reaches ~1150 in the photo).

## xy-k-sf-7-new [2000, 700, 1100] (head left)
Parts: head in 3 pieces (face piece with a slot) continuing the chest, which is raised 20° (the head at 28°); middle section;
split legs on the right (far one 4° up, near one 8° down) with black clamps and a steel gas spring; grey gas-spring armrest
post at the near head corner with a black handle bar; black levers; swan base without a foot loop (none in the photo).
Final check: OK. H = 1100 for the raised chest and head.

## xy-k-sf-8b [1750, 700, 1260] (chair pose, head left)
Parts: back (hole) raised 65° with a dark-grey back cover; two narrow side arm pads at 62° (dark covers); a steel coil
spring under the near pad; a horizontal steel grab rod with a black plate on the back's near side; seat; thigh in two
halves (near one 15 mm lower); leg section in two halves hanging 70°; steel gas strut under the thigh; black hand switch on a
coiled cable at the leg end; swan base; grey foot control with a cable on the floor.
Final check: OK. Size changed: the length is 1750 in the chair pose (the inventory's 2000 is the flat length) and H = 1260.
Approximated: the leg section ends inside the base end. In the photo it hangs a little beyond it.

## xy-k-sf-9-new [1950, 700, 1360] (chair pose, head left)
Parts: back raised 62°: a chest section with two side bolsters, and a head (face piece with a slot and two flaps) continuing it;
seat with narrow side pads; far leg section level to the right with a black lever; near leg section hanging 65°;
steel pole from the base to the back; black levers; swan base.
Final check: OK. H = 1360 (estimate 1300; the photo shows ~1250–1350).

## xy-k-sf-9b [2100, 750, 800] (head left, not flipped)
Parts: head in 3 pieces (face piece with an oval hole and plug), drooping 6°, with a strut; chest; a wide lower-body paddle (full width,
rounded shoulders at the chest end), 25 mm lower; black clamps and hinges; white top frame; base rails with legs (black caps
and feet) and castors; an X-truss on both sides (one bar from the top at the head side down to the foot-side post, one from
the head-side post up to the paddle, with black-capped posts and a pin at the crossing); mid plate; steel gas spring; black motor;
white control box with a blue front panel and label at the foot end on the near side; black cable.
Final check: OK. Approximated: the paddle's swing/extend mechanism under it is not drawn (it is not visible in the photo); the
truss is simplified to two crossing bars per side.

## xy-46 [1500, 800, 850]
Parts: light-wood top, 28 mm, with a lighter laminate line on the edge; white mounting plates; two white square legs with dark lower
sleeves; white T-feet with black glides and end caps; white floor stretcher between the feet; crank on the right end (shaft,
arm, grip; dark red-brown as in the photo, not chrome as the inventory says).
Final check: OK. The crank sticks out ~120 mm beyond the 1500 top. The wood material renders a little darker than the photo's honey colour.

## xy-70 [1960, 720, 450] (head left)
Parts: light-blue top, 80 mm, with an open face hole near the left end (white floor under it); white apron; 4 white legs with black
feet and diagonal knee braces; end stretchers and a long stretcher; chrome bars along both sides under the apron on
brackets; three wide padded straps over the top, down both sides round the bars, with small grey buckles.
Final check: OK. Approximated: the straps are flat plates (no stitched edges).

## xy-71 [1910, 1250, 490]
Parts: wide light-blue mat top, 90 mm, with rounded edges; white apron and centre cross member; 4 square white legs with black caps
under the apron and black feet; dark-blue label (with a white text line) and a small label on the front apron.
Final check: OK.

## xy-100 [980, 1050, 1980]
Parts: grey steel frame: side floor rails curving up to the seat, cross tubes, front legs curving down to the foot board, 4 small
castors; foot massager board with two yellow ribbed pads and black ends; blue seat on a dark mechanism; black curved
armrest loops with grey bars on both sides; tall grey column at the back left with a boom going up and forward, a pulley, the rope,
a white spreader bar, white side straps and a dark-teal chin/head sling; teal hand wheel and spool on the column; two grey posts with 4 rows of
yellow/black massage spools (4, 4, 2, 2); T-handle post on the right with a blue bar; grey twist disc on an arm at the
front right.
Final check: OK. Approximated: the photo is small (437 px), so the spool count and spacing, the curve of the base tubes and the
mechanism under the seat are my reading of it. The twist disc is grey (the photo shows grey, not blue as the inventory says).
