# «Формат» (format, П7.010) — wave 5b

Catalogue p. 64 (printed 124): the interior photo of 2.01, the cut-outs of 2.01 / 2.02 (the same pictures as the site's),
the swatches «Сосна Карелия» / «Дуб Каньон». No instructions exist. Both modules **by photo / by catalogue**: 2.01 measured
on the near-front interior photo (site 1.jpg = the catalogue photo; x by the top's 1200, y by the 760 at the pedestal front,
separately), 2.02 on its single 3/4 photo — inner sizes ±15 mm (2.01), ±30 mm (2.02). Generator `gen/format.py`; sheets
`pilot/format-*.png` (ok; refs: 2.01 the interior photo — the pedestal's drawers and the top sit on the red lines; 2.02 the
3/4 photo, a rough fit only).

## Construction
- ЛДСП 16 everywhere, one decor; tops with a 2 mm edge.
- **2.01** 1200×700×760: top 600 deep over the knee space, 700 over the pedestal (an S-curve at the pedestal's left side —
  the photos), corners R 40 / R 60; it overhangs the left side by 50 and the pedestal by 60. Left side 570 deep. Knee rail
  250 at the back. Pedestal 360 wide (sides 664 deep): an open niche 124 under the top (its floor's edge shows over the top
  drawer), three drawers 174 on a plinth 68 set back 24, bow handles 128, boxes 450 deep. Keyboard shelf 688×450 on
  runners 100 under the top (slides out 320). System-unit stand on castors (base, front board, right rim) rolls out 300.
- **2.02** 1300×1300×760 corner: L top (wings 600, inner corner cut by an arc R 400 — drawn with a bezier). The corner is
  at the back-left: the left wing carries the pedestal (z 880…1300) whose drawers face the knee space (+x) as in the photo;
  the niche's back-end panel is cut in a curve (outline); a square corner post 120 (four boards), knee rails 300 along both
  walls; the right wing ends in an open support (two uprights, a middle shelf notched round the outer upright and a base
  shelf with a rounded corner, on glides); the keyboard shelf 460×400 turned 45° across the corner hangs on two hanger
  boards (all three drawn by top-plane outlines — no `rot` needed) and slides out along the diagonal; the stand behind the
  pedestal rolls out towards +x.

## Finishes
`format-sosna-kareliya` #e6e7e1 (p. 64 crop 0.185,0.865,0.24,0.905), `format-dub-kanon` #8a6b4e (crop 0.265,0.865,0.31,0.905);
both textured, provisional (`gen/format_decors.md`). Metal chrome (satin bow handles).

## For the lead (engine limits)
- 2.02 drawers face +x: engine handles stand out of +z only, so their bow handles are rods (bar + two posts) and the drawers
  are `slide` moves by [380, 0, 0].
- The check sheets draw outlines as boxes (the tops' curves, the diagonal keyboard) and bar handles as circles.
- 2.01's handles stand 13 mm out of B700 (catalogue measures the top).

## Sizes
As in the catalogue (index.json agrees). Skipped: nothing.
