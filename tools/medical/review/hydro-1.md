# hydro-1 — detail review (2026-10-02)

Each device was compared with its catalogue photo(s) at full size, using crops for the details, and with its compare
sheet. The generators were edited (`tools/medical/gen/h1_*.py`) and regenerated until no difference was visible at
compare-sheet scale. All 14 render `ok`. The original generators and designs are in
`tools/medical/scratch/hydro-1-review/orig/`.

Visible brand names now use real stroke letters (`p1lib.text()`) instead of bars: treadmill, CV, CI, and the LED digits
of CIII.

Engine observation: a dark `decal` (black#…) on a white gloss box rendered light grey (the CIII LED windows). Thin
boxes are used there instead.

## xy-90 (pool hoist)
- Fixed the chair:
  - The seat was 400 wide with 8 slats. It is now 470 wide with 10 slats along z, as in the photo.
  - The arms were inverted-L rails rising from the back legs. Each side is now one ∩ tube: front leg, round bend, arm
    rail, back leg.
  - The lower frame was at 160. It is now at 230.
  - Added the lap bar with clamps and black knobs.
  - The footrest hung on two diagonal tubes. It now hangs on two vertical D-frames with 3 rungs each in front of the
    legs, and the slatted tray is on the floor in front of them.
  - Added the flat aluminium carriage arm under the chair.
- Fixed the mast and column side:
  - The red pin pointed forward (z). It now points along +x from a chrome clamp.
  - The column was a square post with a grey ball cap. It is now a round pivot post behind the boom, a square front
    post with a black pendant on top, and a cross arm between them.
  - Moved the housing, actuator and cables to match.
  - Added the hole row on the mast.
- Not matched: the overall size is still an estimate, and the cable routing is simplified.

## aquatic-underwater-treadmill
- Fixed the layout. The tank was centred on the plinth and filled almost all of it. The photo shows:
  - a long flat landing at the left (~660 mm, where the optional ramp joins);
  - the tank 1370 × 820, set back from the plinth front (black deck in front);
  - a narrow, tall module (330 wide), flush with the tank front.
- Fixed the walls:
  - The stainless wall with the 6 jets and the column of cone nozzles is the right end wall (the module side), not the
    back wall.
  - The back long wall is glass.
  - The front glass is split 40/60 by a post.
  - The cone nozzles along the bottom of the front and back now point up.
- Fixed the module details:
  - Logo + touch panel (red stop button) + a vertical blue stripe with white XIANGYU MEDICAL in real letters.
  - Camera on the module's left face.
  - Monitor on its stalk at mid-depth.
- Lettering: grey XIANGYU MEDICAL on the plinth front between two lines; a white round logo + 翔宇 on the blue door band.
- Not matched: the ramp (outside the printed size). Only 翔宇 of 翔宇医疗 is lettered (the font has no 医疗). The
  monitor is dark (no screen crop).

## baby-hydrotherapy-station
- Fixed the module widths. They were 850/800/1100/1000. Correcting the photo's perspective against each module's
  height gives ≈ 0.98 / 0.95 / 1.36 / 1.13 × the 860 worktop, so they are now 840/820/1170/970 (total width 3800).
- Fixed the top:
  - The lip was 115 thick. It is now 210 (photo: 27 % of the height), with a groove line under it.
  - The splash runs from the faucet of ① over ② and ③.
  - The faucets stand on the counter in front of the splash (they were on top of it), and are taller.
- Fixed ③ (round tub):
  - The tub was a 780 circle. It is now a wide oval, about 1000 × 700, with a raised rim ring about 0.9 of the module
    width.
  - The front is a true semicircular bulge.
  - Added the sweeping step line of the front (the lower-left recess) and its vertical right edge.
- Fixed ④ (changing table): the open bay had a back panel. The photo shows the background through it, so the back is
  removed. The drawer stack is about 54 % of the width, the drawer fronts are silver-grey, and there is a right side
  panel.
- Fixed the pink boxes: ② has 2 blue keys; ③ has a blue/red dial.
- Fixed the stickers. They were coloured rectangles. They are now fish (body + tail), crabs with claws, turtles, a
  coral blob, rings for the bubbles, and the umbrella/island/crab/bucket scene, all at the photo positions. On the
  curved front of ③ they are cut into 40 mm vertical strips that follow the bulge.
- Not matched: the stickers are simplified shapes, not the cartoon art. The step of ③'s front is drawn as a line; the
  format cannot cut a recess into a curved shell.

## limb-whirlpool-bath-prototype
- Fixed the arm-rest humps. They were puffed boxes below the rim, invisible in every render. The photo's moulding is
  now drawn:
  - a raised back wall with S-curved ends down to the rim;
  - a wide arm-support block at the left end, at rim level, with a rounded concave inner face;
  - a narrow ledge at the right end;
  - the basin open between them.
- Fixed the fittings:
  - The bow rails were vertical across the depth. They now slant from the front rim and from the right ledge over to
    the raised back, as in the photo.
  - The spout, knob and a valve stand on the raised back top.
  - The hand-shower holder and hose sit at the back left.
- Added the white power cable and plug.
- Not matched: the moulded humps are approximated by a block, a ledge and an extruded back wall. The photo's exact
  geometry is hard to read from one wide-angle view. The height is drawn in the lowest position, as before.

## oval-hydromassage-bathtub
- Fixed the skirt. The rim overhung a narrow body. In the photo the skirt bulges out beyond the rim, so it is now the
  full egg outline with large edge rounding, under a slightly smaller rim, with a seam band between them.
- Fixed the lamp lenses: they were at 260 high and looked like white balls. They are now subtle clear domes with a
  rim, just under the seam (450), each turned to the surface normal of the egg.
- Moved the controls to the photo positions: the gooseneck spout on the front rim at x≈1300, the valve with its large
  plate at 1510, the dial at the front-right, the tall valve and shower post at the back right, two buttons.
- Fixed the grab bars: the back arch is at 870–1190, and the curved bar is on the front-left rim.
- Not matched: the photo is a close crop (the left end and the bottom are unseen), so the plan of the left end, the
  height and the plinth are inferred.

## xy-sl-bi
- Fixed the base. It was a full plinth; the patient's knees go under the tub, which stands on a pedestal at the left
  and a round leg at the right. The proportions are from the photo: rim band, body, and a ~310 open base.
- Fixed the body: it tapers to a domed bottom.
- Fixed the deck: there is now a wide left deck (the basin starts at x 270). The controls are diagonal from back-left
  to front-right: valve on a plate, lilac LCD keypad, valve, hand shower with a blue strip, as in the photo.
- Fixed the collar: it was a flat notch slab. It is now a thick rolled collar that dips into the basin where the
  patient's chest rests, plus a raised back wall at the back left.
- Not matched: the patient's stool (not part of the device).

## xy-sl-bii
- Fixed the rim: the overhang was 18 mm. It is now 40 mm at the front, back and right, kept within the 750 depth.
- Moved the details to the photo positions:
  - The left control is a pair of valves on plates.
  - The rocker switch is moved to x 60–90 at 220–290, with a label.
  - The power cable runs out at the bottom left.
  - The brass fittings are at 210 / 90 high.
- Fixed the seat: removed the invented arm that tied the seat to the tub; the photo shows a separate stool. The seat
  is now at 650–705, and the backrest has a dark edge.
- Not matched: the hand shower lies on the rim (in the photo the nurse holds it).

## xy-sl-biii
- Fixed the hand shower. It was on the front face. In the photo the slide bar, the handset (blue strip), the round
  valve and two hoses are on the left end face near the back, behind the step block.
- Added the thicker seat platform on the left end rim (the patient sits on it).
- Moved the facet lines (x 600 / 1000).
- Not matched: the side facets are thin lines.

## xy-sl-biv
- Fixed the facets. They were flat grey lines. The photo's vertical ribs flare out at the bottom into feet, so the
  ribs are now raised, tapered slabs that follow the body's slope (front and back, 3 each), with black feet under them.
- Fixed the steps: they were 195/390 high and are now 280/440, with the logo on the upper step.
- Not matched: the inner seat is a rounded box.

## xy-sl-bvii
- Fixed the arm troughs. They ran along z with the elbow dome at the front. In the photo both troughs show their long
  sides to the front, with the domed elbow hood at the left end, so they now run along x.
  - The left trough sits over the back of the control block, at 790–990, on a short chrome stalk 30 % from its elbow
    end.
  - The right trough is lower (700–900), on an S stalk from the rim of the foot basin, and reaches out to the printed
    width.
- Size changed: H 950 → 990.
- Fixed the screen and knobs: the touch screen is now at the back left of the block. The knobs are placed as in the
  photo: two at the back-left corner, one at the front centre, a round knob, and a square knob at the right.
- Not matched: the photo is one perspective view, so the trough heights are ±50 mm. The foot basins are one tray with
  a divider.

## xy-sl-ci
- Fixed the slatted support. It sat at 520–600, deep in the tub. In the photo the plates are just under the rim:
  - The leg plate is now at 680–725.
  - Added a seat pan.
  - The backrest is inclined 22° up to rim height.
  - The armrest is above the seat.
  - The slots are now long dark through-slots.
- Added 翔宇 lettering next to the blue logo on the control box end face.
- Not matched: the stretcher lift and hoists are accessories. In the renders the insert hides below the front rim
  because the camera is low; the photo camera is high.

## xy-sl-ciii
- Fixed the front panel. The raised panel stopped at x 1960. The photo shows it spanning nearly the whole front
  (margins ~4 %), at 125–760 high.
- Fixed the feet: there were 3 per side. The photo shows 2 per side, at x 300 and 1850.
- Fixed the LED box: there were red patches. It now has black windows with red "88" 7-segment digits, a blue logo
  bar, and a black clamp knob on the pole.
- Fixed the spout: the shower lying on the rim is now a chrome spout at the back, pointing into the tub.
- Not matched: the inner hose path is approximate.

## xy-sl-cix
- Fixed the lilac band. It was a flat slab on the front and did not wrap the corner. It now wraps the front-left
  corner: 37 thin horizontal slices follow the body's rounded section at each height, from the end face round onto
  the front. Both edges wave as in the photo (wide at the top, narrow at 60 % height, wider again at the bottom).
- Moved the legs (x 420 / 1620) and the power box with its cable (x 700–785) to the photo positions.
- Not matched: the band's screw dots are omitted. The slices leave faint horizontal banding up close.

## xy-sl-cv
- Fixed the door. It was 750 wide and symmetric U. In the photo it spans x 240–1085, right up to the louvre panel. It
  is now J-shaped: a big round corner at the bottom left and a nearly square corner on the hinge side.
- Fixed the lettering: XIANGYU / MEDICAL is now in real letters with the round logo, and the printed label has text
  lines.
- Fixed the armrest: the bar on the rim is now a grab handle on the inner back wall.
- Removed an invented door handle on the rim.
- Not matched: the door is drawn closed. The label text is drawn as lines.
