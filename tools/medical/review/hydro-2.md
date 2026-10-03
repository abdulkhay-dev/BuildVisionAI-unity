# Detail review: batch hydro-2

Generators changed: `h2lib.py`, `h2_cvi.py`, `h2_cviii.py`, `h2_cxi.py`, `h2_ri.py`, `h2_rii.py`, `h2_riii.py`,
`h2_baby.py`, `h2_rhsr2.py`, `h2_srf1.py`, `h2_srf4.py`, `h2_hyziiy.py`, `h2_hyziiic.py`. All 14 designs were
regenerated and rendered `ok`. Each was re-checked on `renders/<id>-compare.png`, and the photos were also checked at
full size or zoomed.

## Shared fixes (h2lib)
- **Lettering**: `h2lib` now exposes `text()` / `text_len()` from p1lib. It adds the glyphs 医 疗 设 备 有 限 责 任 公 司 J Z
  at runtime (p1lib itself is unchanged) and provides a `brand_cn()` helper (round mark + 翔宇医疗). Every visible brand
  name that used to be drawn as blue or white bars is now real stroke letters.
- **Bug found while doing this**: importing p1lib re-binds `D.decal` (and others) with a different argument order. As
  a result, every decal made by a hydro-2 generator would have gone out with `mat` and `face` swapped. h2lib now puts
  lib's methods back right after the import.
- `logo_round` decals sit 2.4 mm in front of the disc (they were 1.6 mm, so the mark's figure could hide in the disc).

## Per device
- **xy-sl-cvi**: The model was rotated 90°. In the photo the near vertical corner is at x≈420 px, not 590. The door face
  is therefore the LONG face: 750 px wide with edge slope 0.23, against 390 px and slope 0.32 for the end face. Size is
  now as printed, [1270, 860, 1000], with the door face as the front. Front layout re-measured with perspective: narrow
  fixed panel with recess marks, then the door (x 300–880, bottom 200 mm, not 110), then the hinge strip, then the right
  panel. The right panel's tall recess now starts under the rim, and the blue 翔宇医疗 logo is inside it at the top, in
  letters. The left end has the big recessed panel, the handle moulding and a low recess band. The seat and cushion
  backrest are at the left end, with the white shower roller behind them. Rim: the black cap is at the front-left
  corner; the valves with the blue lever and a flush key strip are at the back-left. The transfer beam now runs across
  the depth near the right end. It sits on the grey wedge at the front rim, with the teal end block at the back and the
  grey L arm reaching left over the basin (red pin, loop). Curtain rail with hooks. Cannot match: the beam's exact
  length. The photo suggests it may overhang the back; it is kept inside the size.
- **xy-sl-cviii**: XIANGYU / MEDICAL is now in white letters (was bars). The round mark now shows its figure. Nothing
  else differs.
- **xy-sl-cviii-luxury**: The hood is now frosted translucent acrylic (was opaque white), with a domed head end that no
  longer overhangs the table end. The speaker is now a white housing with a round black speaker, then a black strip
  x 580–1010 (photo), where it used to be a black strip with the speaker at x 800. Added the white box on the lid and
  the lettering. Approximate: the lid's printed control graphics are dark rectangles. The lid's hinge geometry is
  ambiguous in the photo; it is drawn swung up at the back.
- **xy-sl-cxi**: XIANGYU / MEDICAL is now in letters, sized to the photo (cap height 46). The square valve and the hand
  shower moved ~140 mm toward the basin, to their positions in the photo relative to the panel. The legs moved inward
  (x 380 / 1590). Grab bars were checked against the photo (front rim ~325–590, back rim ~985–1340), and their height
  went from 120 to 105. Nothing else differs.
- **xy-sl-ri**: The window's lower-left corner is now the photo's big sweep (r 300) with a small lower-right corner, and
  its bottom moved 560 → 600. The front lilac bar now runs to the right end; the back bar is shorter and starts over
  the deck. The plinth is taller (250). The plinth plate now carries 翔宇医疗设备有限责任公司 in letters (was a blue
  bar). The left end has the mark + 翔宇医疗.
- **xy-sl-rii**: The lilac bars were sitting ON the rim, 95 mm above it. In the photo they form the rim at the shoulder
  level, flush with the front, so they were lowered. The window now runs from just under the bar down to 520, x 540–1260.
  The thin groove line was replaced by the photo's low recessed band (rounded left end, x 735 → right end).
- **xy-sl-riii**: The deck is thicker (118 → 150). The front window was re-measured with perspective: x 1130–2470,
  bottom 540, chamfer 230 × 150. The back window is now its own, further left and shorter (x 620–1700), as in the
  photo. Ribs were regenerated around each window, and the skirt has rounded green corners. Lane rails now span each
  window. The speaker grille is now on the back inner wall facing the lane (was lying flat on the deck). The left-end
  rail is a straight grab bar on the deck (was a diagonal tube). The jets no longer float in the window openings; some
  are added on the floor.
- **xy-sl-rv / xy-sl-riv**: Re-laid out. The photos' near corner is at x≈420 / 345 px. The cartoon face is the long
  front, and the knee arch with its split line is on the LEFT END, where the nurse sits. The first version had put the
  arch on the front. Front wave: green down to 250 mm on the left part, then a hump with the cartoon at x 500–800 (as
  in the photos). The cartoon now has crab claws. The raised block is now at the right end over the full depth: its
  white left face carries the green recessed handle and faces the basin, and its front is green, flush with the
  cabinet. It steps down at the right under the tray and is taller (top 950; size H 900 → 960, estimate). It used to be
  a small block at the back right. The faucet now stands at the block's front-left corner and arches back over the
  basin. Tray struts are dark and short. RIV has two green cups at the back plus the cup with the brass tap. RV has
  the green inlay. Cannot match at sheet scale: the knee arch is on the left end, which the front-right `angle` camera
  does not show.
- **rh-sr-ii**: The logo plate now carries 翔宇医疗 in letters with a sub-line (was bars). The acrylic lid handle is
  translucent grey and visible, running across the lid as in the photo; it was clear glass and invisible.
- **xy-srf-i**: The control box moved right to the photo's place (x 335–505). The steel is a little lighter, as in the
  photos. Nothing else differs.
- **xy-srf-iv**: The logo is now 翔宇医疗 + XIANGYU MEDICAL + ® in letters (was bars), sized and placed from the photo.
  The steel is lighter.
- **hyz-iiy**: The splash hood now covers only the back half of the hole and rises ~190 mm (it used to sit centred over
  the hole). The arm pockets are now low on the outer half of each arm front, with a light surround; they were mid-height
  slots across the whole front. Added the chrome knob on the left arm. The backrest is narrower (620 → 550). The logos
  are a white disc with a blue ring and a blue mark (photo), not a blue disc. The console was measured at ~540 wide in
  the photo (it was 452), so size W went 1300 → 1360 (estimate). Panel lettering was added.
- **hyz-iiic**: Seam redrawn from the photo. It drops almost vertically from the roof just right of the round panel,
  curves into a long diagonal to a sharp V at ~half the length, and rises to the hinges. It also crosses over the roof
  (it used to start diagonally at the head-end corner, with no roof crossing). The double line now keeps its spacing on
  the vertical part. The tail was lifted so it no longer sinks into the shell. The hand hole and hinges were moved to
  follow it. Approximate: the panel's controls are simple discs and decals.

## What the format cannot match
- The undersides and far faces seen only in the photos' perspective are the main remaining guesswork: the cvi beam
  length, the riii back-window position, and the luxury lid's hinge line. These were read from single perspective
  photos.
- Stroke lettering is block capitals and simplified CJK, readable at sheet scale but not the brand typeface.
- Translucent parts (acrylic) render evenly frosted. The photos' reflections and inner shading are not reproduced.
