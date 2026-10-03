# Detail review: batch kinesio-3 (2026-10-03)

## Method
For each device:
1. Ran `compare.py <id>` and read the sheet.
2. Read the catalogue photo(s) at full size, and zoomed crops where needed.
3. Listed every visible difference.
4. Fixed the generators (`tools/medical/gen/k3_*.py`, shared helpers in `k3_lib.py`).
5. Re-rendered (waited for the .txt) and re-checked.

All 14 render `ok`. Sizes are unchanged, including the accepted xy-12 / xy-13 / xy-14 / xy-14-8a photo sizes.

## Shared helper changes (`k3_lib.py`)
- `straightener()` (xy-10, xy-11, xy-14):
  - The post now stands vertical under the board's bottom edge.
  - The diagonal now starts in the front part of the plate and rises back to a point outboard of the board. A short
    stub joins it to the post top.
  - The handle loop is now a hook bracket that bends back almost level, with one inner bar. Before, it was a straight
    ladder of two grips in line with the board.
- `pulley_unit()`:
  - Added black rubber stoppers on the base tops.
  - Added a black foot strap over each pedal.
  - Fixed a bug: the black feet are now turned with the unit. On a unit facing ±x they used to land as loose black
    squares on the floor inside the cage (visible in xy-13).
- `gallows()`: takes `gap` and `tip` (pulley spacing).
- `peg_rack()`: works with `side=-1`.
- `net()`: takes `pw` (fuller at the rim, gathered at the bottom) and `sag` (knots off the perfect circles).

## xy-10: chest and back straightener
Fixed:
- Frame tubes, per the photo:
  - vertical posts under the board's bottom edge;
  - long diagonals from the plate's front part up to stubs outboard of the board.
- Top handle: a flat rectangular hook bracket bent back from the board top. It was a vertical two-grip ladder.

Cannot match: nothing visible at sheet scale.

## xy-11: straightener with the wall pulley unit
Fixed:
- Tower top frame: the board's white rectangular loop now rises from the board top and lies back over the tower cap,
  with a cross bar and an inner bar. It was two arms and a cross tube.
- The tower is lowered to 2060 so the loop sits on the cap.
- The dark weight blocks sit right on the teal stacks (cuff_y 640 → 560).
- Frame tubes as in xy-10.

Cannot match:
- The photo's tower base is one long white box. The model keeps two base boxes.
- The pulley ropes are thinner than in the photo.

## xy-12: pulley weight
Fixed:
- Black rubber stoppers at the front corners of the base tops.
- A black foot strap over each pedal.

Cannot match:
- The photo's base boxes are open frames. The model shows the opening as a grey panel.

## xy-13: four-piece trainer
Fixed:
- Inner frame removed. The photo has none: just 4 posts, top and bottom rings and one mid ring at ~790 on all four
  faces. The draft had an inner post line, an inner top ring, an inner mid ring and two extra front crossbars.
- The wheel carriage now runs from the front mid ring to the top.
- Wrist box:
  - turned to face into the cage, so from outside it shows its plain back with a dark slot (photo);
  - its rods run from the mid ring to the top.
- Pulley unit:
  - added the white square post between the two columns, floor to cap;
  - hand rings lowered to ~1250 and cuffs to ~930;
  - weights are light translucent teal (photo: clear bags);
  - fixed the stray black feet on the floor.

Cannot match:
- The weights in the photo are translucent bags in white brackets with red cords. They are drawn as translucent
  discs plus red straps.

## xy-14: seven-piece trainer
Re-read both photos: photo 2 is from the front-left, photo 1 from the back-right. Fixed:
- The whole layout was mirrored. Now:
  - the wall bars are the RIGHT face;
  - the straightener stands outside the LEFT face, facing out, with its black back to the cage;
  - the pulley weights are in the front face's LEFT half;
  - the finger ladder is on the back-LEFT post (photo 1). It used to be at the front-right, where photo 2 shows none.
- The tall backboard above the top was really the gallows seen from behind. Now:
  - the gallows post rises from the front mid beam to 2390;
  - the arm points to +x with a gusset;
  - two pulleys carry a white D ring and a blue ring (photo 2);
  - the hoop hangs from a small white board under the back top beam.
- The cage is now 1880 high, with the wall-bar posts at 2060. Photo 2 shows the gallows rising about a third above
  the cage.
- Anklebone tilt board:
  - it now faces the front in the right part of the cage;
  - it leans back onto a new top cross beam;
  - its grey foot cradle, foot slots, castors and yellow-gripped handles stand at the front face. Before, it leaned
    sideways on the wall bars with its foot inside.
- Added the two red-gripped triangular slings hanging inside (photo 2).
- Weights are translucent (photo: water bottles).

Cannot match:
- Photo 1 and photo 2 view opposite sides at different heights, so the cage proportions and the gallows x position
  are read approximately (±150 mm).
- The slings' fabric is drawn as tubes.

## xy-14-8a: eight-piece trainer (A)
The two photos disagree. The main photo (1, from the front-right) is followed. Fixed:
- Shoulder wheel: moved to the LEFT face, facing out. Both photos show it on the face by the gallows corner, its ring
  reaching past the corner post. It used to be on the back face.
- Finger ladder: moved to the back-left post. Photo 1 shows its white saw-tooth back behind the front-right post.
- Peg rack: now hangs on the inside of the wall bars, across the whole face. Photo 1 shows its green uprights behind
  the rungs by the front and back posts. It used to be outside at the back.
- Forearm tray: now reaches to the back, as in the photo. It used to point forward.
- Wrist box (wooden bar): moved to the back end of the wall bars at ~1450.
- Gallows: both ropes run over pulleys at the arm's tip, and the two rings hang side by side at ~1260.
- Hand rings of the pulley unit raised to ~1330.

Cannot match: photo 2 puts the peg rack outside the wall bars and the gallows over another corner. One layout has to
be chosen.

## xy-14-8b: eight-piece trainer with table
Fixed:
- Gallows arm (photo 1): a short arm now stands out of the front-left corner top, with a brace along the left face, a
  pulley at the tip and a rope down to a blue ring outside the cage at ~1000. To keep the printed 2480 depth, the cage
  stops 250 short of the front. The draft had a pulley inside instead.
- Floor outrigger in front: the angled floor tube with a jog seen in photo 1.
- Roof mesh is as fine as the back grid (110 mm cells, was 160).
- Pulley unit:
  - moved into the back half of the left face;
  - grey cuff blocks added at the mid ring;
  - clear water-bottle weights.
- Hand rings: moved under the roof near the back-left corner, just above the mid ring (photo 1). They were on the
  front top ring.

Cannot match:
- Photo 2 is a different, blue variant. The grey table of the main photo is kept.

## xy-15: sandbag rack
Fixed: the sacks read as smooth glossy jerrycans. They are now:
- soft pear-shaped lofts in satin PU;
- with the belly low at the front, narrowing to a gathered neck with a chrome ring at the back top;
- the lower tier taller than before and lying more on its side.

Cannot match: crumpled cloth wrinkles. The shape and gathered neck carry the read.

## xy-16: binding-weight rack
Fixed:
- The cuffs are flatter (32 thick, was 46).
- Dark camo: black dominant, with teal and grey/white patches on every pocket. It was mostly solid teal.
- The Velcro straps are thinner and lie back over the rear ends.

Cannot match: the real camo print. It is drawn as alternating pocket colours with one patch each.

## xy-1a: commercial upright bike
Checked:
- the housing (level top, tail into the rear foot);
- collars;
- console size and tilt;
- handlebars (pulse grips by the console, horns rising at the rider-side outer ends);
- cup holder, red post, saddle, orange knob, pedals, feet.

No difference found at sheet scale.

Cannot match: the photo is taken from the rider side, so the console face (LCD and keys as decals, no screenCrop)
does not show in the front-right angle render.

## xy-2: upright bike
Fixed:
- The housing is now the photo's egg shape. Its narrow top meets the seat post, and the belly runs far back over the
  rear foot, with the rear edge sweeping down. It used to stop at the seat post with a long bare rear leg.
- The rear leg is now short.
- The cyan stripes moved back to the top-rear, by the seat post.

Cannot match: the console face is a dark plate with a blue patch. There is no screenCrop.

## xy-20 / xy-21: posture mirror (and with grid)
Fixed:
- Glass: the engine `mirror` read mid grey. It is now a light bluish glossy face (`gloss#dfeaf2`), like the photo's
  bluish white.
- The gold frame profile is wider (60, was 42; photo ~63).
- xy-21: the grid lines are fainter grey (`#b3bec8`), as in the photo.

Cannot match: the glass shows no real reflections.

## xy-23: mini basketball stand
Fixed: the net. It was a coarse, perfectly regular lattice of thin strands. It is now:
- a finer mesh of 2 × 12 strands in 8 rows;
- thicker cord (9);
- full at the rim and gathered to a narrow red bottom;
- knots slightly off level, for a looser hand-knotted look.

Cannot match: the net is still a helical lattice, not loose knotted loops.
