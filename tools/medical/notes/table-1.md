# Batch table-1: treatment tables XY-K-SF (Treatment Table.pdf) + XY-K-CZLD-III

Generators: `tools/medical/gen/sf.py <id>` (all SF tables; shared parts in `gen/sflib.py`: pads, the Z-column base,
the swan-arm base, the scissor/fixed frames, `flip_design`) and `tools/medical/gen/czld3.py`.
Frame: the table's length runs along x and its width along z. The front (z = D) is the long side the photo looks at.
The head end is put where the photo shows it relative to that side. The angle render camera stands at the front-right,
so it sees the face of a raised section at the left end (x = 0) and the underside of one at the right end.
All 14 render `ok`.

Shared families (one body drawn carefully, siblings derived):
- **Old Z base** (SF-3, SF-4, SF-5): white tube frame 1700×620 on 60×60 legs with black caps, castors Ø50 inboard,
  two Z lift columns (white body, grey sloping cover on top, posts with black caps), white apron frame, lettering
  bars "XIANG YU / MEDICAL", control box at the foot end.
- **New swan base** (SF-1/2/3 new, SF-4B, SF-4 new): white tube frame on legs with black caps, twin castors inboard,
  two swan-neck arms arching up toward their top pivot (white body, dark-grey cover), posts with black caps, Linak
  actuator, top frame, foot loop at the foot end.
- **Box base** (SF-4C, SF-4D): box-section frame, 70×70 legs, twin castors Ø70, grey stirrup pedals at both ends.

## xy-k-czld-iii — vibration bed (inventory size [700, 2000, 1115], length along z, tongue/screen at the front)
Parts from the photos: dark-grey base plate (~1340×650) with white top, cyan rim line and a U-notch at the screen end;
4 castors with grey covers; white tapered pedestal with blue Sunnyou logo; black bellows; white tapering skirt under
the top with a green dot; white shell 2000×700 narrowing into a tongue with a dark tilted screen and bezel; cyan LED
line along the shell sides; light-blue mattress inset; solid wave humps on both rims at mid-length; blue pillow at the
tongue end.
Final check: all present. Approximated: the logos are blue bars. The screen is dark (the inventory has no screenCrop).
The top is drawn at 850, inside the 715–1115 travel; size H = 1115 is the top of the travel.

## xy-k-sf-1 — fixed steel couch [1900, 650, 700] (head right)
Parts: one-piece blue top (70 mm) with a waist notch on both sides at ~2/3 of the length; an oval breathing hole with
a plug in the head part; a black band under the pad; a white tube apron with black end plugs and a blue label on the
head end; 4 white 40×40 legs near the ends with black feet; an H stretcher (end bars plus a long centre bar); under the
head, a stepped white bracket carrying an L-shaped blue arm/face rest at ~370, and a second rest at ~490 on the far side.
Final check: all present. Approximated: the arm/face rests are my reading of the photo (two shelves). Their exact
layout is not clear in the photo.

## xy-k-sf-1-new — 1 section, swan base [1950, 690, 750]
Parts: one-piece thin top with tapered (chamfered) ends and a closed arc breathing slit near the head; a white top frame
with black plugs; a black lever under the foot end; the swan base with a blue button and the Sunnyou label at the head
end; a stainless foot loop at the foot end.
Final check: all present. Approximated: the posts sit beside the arms, not on the side rails.

## xy-k-sf-1b — scissor lift [1950, 700, 900]
Parts: one-piece top with waist notches, a rounded-rect breathing hole (through, dark bottom) and a seam; a thin white
apron with black corner caps; a base on legs with black caps and black adjustable feet; a double X scissor of white flat
bars on both sides with cross tubes; a grey Linak actuator; a white control box with a green switch and black knobs;
a black motor; a blue hand switch clipped on the apron with black cables (one to the floor); a blue label on the rail.
Final check: all present. Approximated: the scissors are symmetric Xs. The real linkage differs slightly in the
lengths of the head and foot pairs.

## xy-k-sf-2 — old 2 sections [1950, 700, 990] (head right, raised 30°)
Parts: thick body pad and head pad with a slot; white apron with black caps; two steel side bars running out under the
head; levers of white flat bars with lower plates on both sides; a base on legs with black caps and feet; a black motor
and pedal block; a control box with red and green buttons; a blue clip on the apron with a black cable looping on the
floor; a blue rail label.
Final check: OK. Size H = 990 for the raised head (the top is at 610, the low position in the photo).

## xy-k-sf-2-new — 2 sections, swan base [1950, 690, 1130] (head raised 35°)
Parts: as SF-1 new, plus a head section (650) with a stadium hole and plug, a gas strut, and a black lever and handle
at the foot end.
Final check: OK. Size H = 1130 for the raised head.

## xy-k-sf-3 — old 3 sections, Z base [1950, 700, 1010]
Parts: thick head pad (hole, raised 28°) with a black bracket, a middle section and a foot section; black hinges; the
old Z base; a dark-blue control panel on the box at the foot end; a white block hanging under the rail.
Final check: OK. Approximated: the lettering is grey bars. The motor is a dark box between the columns.

## xy-k-sf-3-new — 3 sections in chair pose [1950, 690, 1500]
Parts: backrest (800, raised 65°) with black side levers and a gas strut; seat (400); leg section (720, dropped 32°);
black levers; swan base (the top frame only under the seat); round grey motor; floor foot switch (2 pads) with cable.
Final check: OK. Head (backrest) on the right as in the photo (review: mirrored; the swan arms keep the photo orientation). Size H = 1500 for the chair pose.

## xy-k-sf-4 — old, split legs, Z base [1950, 700, 1060]
Parts: head (raised 30°, hole); seat tilted up 10°; two leg sections (near one 8° down, far one 12° up) with rails;
gas springs; the old Z base; an upright control box with a blue-grey panel at the foot end; a foot loop.
Final check: OK.

## xy-k-sf-4-new — chair-table in chair pose [1900, 700, 1400]
Parts: backrest with an arched top, raised 75°, a cylindrical head roll and a black lever; a black armrest on a chrome
bracket (near) and a black pad folded beside the backrest (far); a seat; two leg sections (far level, near hanging 68°);
a gas strut; swan base with white arms; black brake levers (review: mirrored, head on the right as in the photo; horizontal armrest on the far side, folded pad on the near side) at the corners; triple foot switch with 6 blue domes.
Final check: OK. Approximated: the photo's complex linkage (several white links) is drawn as the swan base, and the
castors are smaller than in the photo. Size H = 1400 for the chair pose (the inventory estimate was 1350).

## xy-k-sf-4b — split legs in a V, swan base [1950, 700, 1330] (head right)
Parts: two narrow leg sections splayed ±130 mm in plan (far one up, near one down) with black end clamps and a gas
strut; seat; back (raised 60°, hole) with a steel strut; swan base with white arms; grey motor; two double foot switches
on the floor with cables.
Final check: OK. The splayed legs stick ~80 mm outside the 700 width (pose). Size H = 1330 for the raised back.

## xy-k-sf-4c — 4 sections, box frame [2000, 700, 1040] (head right, raised 45°)
Parts: three thick flat sections and a head section with a slot; a deep white box apron with black plugs and bolts;
black release knobs with yellow tags; a white drum and a curved white lever block with a grey actuator; a lift post;
a grey motor under the base; the box base; a long stainless foot bar along the front between the two stirrups.
Final check: OK. Approximated: the lift mechanism inside the apron is a simplification (drum, lever, post).

## xy-k-sf-4d — 4 sections, single column [2000, 700, 1050] (head right)
Parts: long body section, middle section, flexion section raised 40° and a flat end piece; an apron to the end with
black plugs; a black clamp; one white Z column with a grey cover; short posts with black caps; a grey hose; a grey
pedal plate under the base; box base with stirrups (no long foot bar, none is visible in the photo).
Final check: OK. Approximated: the shape of the column is simplified.

## xy-k-sf-5 — 5 sections, split legs, Z base [2000, 700, 930] (head right; drawn head-left and mirrored)
Parts: head (raised 20°, hole); chest and pelvis sections; two leg sections (far one splayed 3°, near one splayed and
dropped 70 mm, loft) with a gas spring; the old Z base mirrored; the control box with a dark-blue panel at the foot end;
lettering in the photo's order.
Final check: OK. The inventory width is 2000 (the other old tables are 1950).
