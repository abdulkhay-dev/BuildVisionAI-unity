# kinesio-1: detail review against the catalogue photos

Reviewed all 14 devices. Every `.txt` is `ok` and newer than its json. All fixes are in the generators
(`tools/medical/gen/k1_*.py`, `k1lib.py`), which were then re-run. Compare sheets: `tools/medical/renders/<id>-compare.png`.
Scratch files: `tools/medical/scratch/kinesio-1-review/`. `run.sh <gen> <ids>` regenerates a design, waits for the
render and rebuilds the compare sheet. That folder also holds crops of the photos and the zbd catalogue pages.

The "angle" render looks from the design front-right. The zbd, cpm-ia, cpm-iib and czld-vii photos look from the
front-left, so they appear mirrored against it. The cpm-ib, cpm-ic and g1 photos look from the front-right, the same
side as the angle render. Sides were checked on the front and side renders.

## Shared changes (k1lib.py)
- `text` and `text_len` are imported from `p1lib`. p1lib's import replaces `D`'s helper methods with ones that take
  arguments in a different order, so k1lib puts this batch's own methods back afterwards.
- New helper `text_right()` draws lettering on a +x face. `p1lib.text()` lays letters in the (z, y) plane, so on a +x
  face they read mirrored or upside down. The helper mirrors the strokes so they read correctly from +x.

## Size changes
| device | before | after | reason |
|---|---|---|---|
| xy-cpm-ib | 450 × 490 × 320 | 480 × 560 × 320 | the photo frame reaches ~40 mm past the body's right side and ~55 mm in front of its end face; the controller lies in front of the frame |

The other sizes are unchanged from the drawing pass. Those changes are recorded in `notes/kinesio-1.md`.

## xy-zbd-iiidl / xy-zbd-iidl / xy-zbd-idl (k1_zbd.py)
Fixed:
- **Screens.** The iidl and idl photos show the same interface as iiidl, so both now use
  `print: "med_xy-zbd-iiidl_screen"`. Before, they had a dark screen.
- **Capsule.** It was an almost round tube. The photo has flat side panels, so it is now a rounded rectangle (r 62).
- **Rear boss.** The silver oval boss was too small. It is now 102 × 130 with a dark rim around it.
- **Lettering.** "Sunnyou" on the capsule sides is now real letters, not a grey block. The +x side reads correctly.
  The column shows "Sunnyou 翔宇" reading upward along the column, with a thin grey sub-line, as in the photo.
- **Sphere disc.** It was too large. It is now flush with the sphere at r 70, with a double pink ring as in the photo.
- **Lower drum.** In the photo the white rim is thick and the grey disc is recessed, at about 0.64 of the drum radius.
  It was 0.79 and sat proud. The drum is now a lathe with a recessed face, the disc ring is at r 138, and it has a
  double pink ring.
- **Pedal cradles.** They were flat trays with a black strap. They are now deep white shells: a sole with a raised
  toe, a tall rounded heel cup, and side walls that are tall at the heel and low at the toe. The black strap is gone;
  no strap shows in any of the three photos.
- **Crank plates.** Each now has a dark slot along it, like the slotted chrome plates in the photo.

Cannot match: the "90° / 45°" scale marks on the sphere. The calf shells are simple C slabs; the photo's shells have a
flared rim. The drum's lower fairing is a rounded block.

Not changed: the screen still faces the patient (+z). The p2 and p4 catalogue pages show the same render. From the
perspective (the screen's right edge recedes, as the +x direction does), the screen faces front, not the camera side.

## xy-cpm-ia (k1_cpm_ia.py)
Fixed:
- **Hub discs.** They were turned the wrong way, with the axis along x and the faces toward the ends. In the photo
  they sit on the wrist axis across the forearm, so the axis is now along z. Each has a narrower inner boss and a
  small blue logo on its inner face, as on the far hub in the photo.
- **Rails.** They now rise less steeply to the hubs (about 9°), and the hub posts are shorter.
- **LCD.** It was lime green. It is now greyish olive (#a9b48c), as in the photo.

Cannot match: the folded nylon sling is puffy boxes and a strap. The small chrome rail brackets on the step are not
drawn.

## xy-cpm-ib (k1_cpm_ib.py)
Fixed:
- **Body shape.** The photo body has a short vertical end face, a 35° sloped facet that carries the oval panel, and a
  flat top. The model had the panel flat on top. The body is now that profile, and the panel, LCD and keys are
  tilted on the facet.
- **Body length.** The body is now 372 long; it was 332 (about 1.9× its width, as in the photo). The top edges are
  more rounded.
- **Finger mechanism.** It was a white box post with a motor whose axis ran along x. It is now a thin chrome post
  with an aluminium motor cylinder on top (vertical axis), at the body's back-left corner. The finger bar reaches over
  the sling toward -x, and the 4 clamp rods are flat bars.
- **Frame.** The frame now reaches past the body at the right and the front, as in the photo (size changed, see
  above). The controller lies outside the frame.
- **Sling knob.** It stuck into the body. It is now on the outer (-x) side.
- **LCD.** The colour is now as in the photo.

## xy-cpm-ic (k1_cpm_ic.py)
Fixed:
- **Box proportions.** The box was 260 wide; it is now 300 wide by 210 tall. Both photos give a ratio of about 1.4.
- **Front panel.** It covered the whole front face. In the photo it covers only the right ~57 %. The layout now
  follows the photo: LCD at top-left, a row of 4 keys, a right column of 2 keys with a larger key below, and the green
  rocker in a black frame at bottom-left, with text lines and a logo.
- **Hub logos.** They were large blue discs. They are now small blue dots on chrome hubs.
- **Slings.** They were thick puffy pads. They are now thinner nylon hammocks.

Not drawn: the mobile-stand variant (view 2).

## xy-cpm-id (k1_cpm_id.py)
Fixed:
- **Castors.** They had chrome forks and grey hubs. The photo shows all-black hooded twin castors, so they are now
  drawn as two black wheels under a black hood on a black stem. The `caster` kind's fork is always chrome, so it could
  not be used.
- **Head box.** It is now at 900–1140 to match the photo's proportions (column, box, cuffs), and its top-front edge is
  well rounded. The LCD window has moved up near the top of the front face, as in the photo; it was in the middle.
- **Heights.** The left pad frame, forearm rest and controller moved up 50. The right cuff arm moved up 45, and the
  cuffs are now at 1360 and 1135.

Cannot match: the photo is small (~220 px wide), so the cuff ring shapes and knob counts are approximate.

## xy-cpm-iib (k1_cpm_iib.py)
Fixed:
- **Membrane panel layout.** The keys are now laid out as in the photo: green rocker (in a black frame) at the
  back-left, LCD at the back-right, 3 + 2 keys in front of them, and a larger key at the front-right.
- **Hub caps.** They were blue discs. They are now white caps with a small blue logo.
- **Lifting links.** They are now light silver, not dark steel.
- **Slings.** They are thinner, less puffy cradles.
- **LCD.** The colour is now as in the photo.

Cannot match: the folded nylon slings and the straps hanging from them are simplified.

## xy-ct-iv / xy-ct-iii (k1_ct.py)
Fixed:
- **Shell flare.** The wall was vertical. It now flares outward from r 520 under the lid to r 552 at the foot, about
  7°. It is built from 22 tilted flat facets per wall sector (slabs, `rot` tilt + `rots` turn).
- **Openings.** The openings widen toward the foot (+34 mm each side), as in the photo. The end facets are two steps
  wide so they can narrow without crossing. The arch fillets are drawn in the plane of each end facet.
- **Lid.** It now has a flat top out to r ~400 and a broad shoulder (sides 96).
- **Turns.** Every turn is now kept in (-180°, 180°].
- **Labels and column.** The yellow skirt labels moved out from under the wider shell foot. The column is wider:
  184 × 160.
- **Arrow pad (iii).** It was coloured squares on a dark face. It is now 4 coloured triangles pointing outward on a
  light face, as in the photo: blue up, green right, red down, yellow left.

Cannot match: each wall is flat facets, which show faint vertical lines up close. The modules are simplified boxes.
The iv screen is dark (no screenCrop).

## xy-k-czld-vii (k1_czld7.py)
Fixed:
- **Post T-heads.** The width-adjust stubs ran along the rails. In the photo they point outward across the walkway,
  so they now run along ±z, 125 mm long, with rounded ends.
- **Console logo.** The column foot now has a blue logo tile with a white "S", and the inlay starts above it. Before,
  there was a white disc on the inlay.
- **Console lettering.** "Sunnyou 翔宇" now reads upward on the inlay; it was a white bar.

Checked: the far rail is a closed loop of two tubes joined by U-bends at both ends. Both ends are visible in the photo
crops, so it was left as drawn. The near rail is single, with rounded ends.

Cannot match: the footprints are ellipses. The rails are at the lowest printed height (1050).

## xy-k-g1 (k1_g1.py)
Fixed:
- **Top bar offset.** The photo shows the column's short top arm clamping the black top bar about 70 % along its
  length (toward +x). The bar, its hooks, blue label and caps, and the whole harness (which hangs from the bar's hooks)
  now sit 115 mm to -x of the column. They were centred. The angle render now matches the photo's view.
- **Harness mesh panels.** They were two brown blocks standing on the vest. They are now flat brown mesh triangles on
  the vest's upper front, narrowing up to the shoulder straps.

Cannot match: the harness webbing and the vest are simplified, and the leg loops are approximate.

## gait-obstacle-treadmill (k1_treadmill.py)
Fixed:
- **Posts.** There were 3 posts per side. The photo shows 2 per side, at the console end and about 3/4 toward the
  tail, and the model now matches.
- **Rail ends.** The rails now run past the tail post and bend down in the air above the deck's tail, as in the
  photo. They used to go almost to the deck end.
- **Striped panel.** It moved toward the console end (z 540–1140); in the photo it starts at the console-end post.

Cannot match: the photo is low-res (779 × 584). The console graphics and fruit pictures (coloured discs) are
approximate, and the dark cross member at the console end is not drawn.

## upright-exercise-bike (k1_bike.py)
Fixed:
- **Housing.** The silver flywheel housing is now taller (top at 595) and wider (220), as in the photo. The cranks,
  pedals and flywheel caps moved out to match.

Cannot match: the photo is mostly hidden behind a harness. The handlebar, saddle and console are a generic bike.
