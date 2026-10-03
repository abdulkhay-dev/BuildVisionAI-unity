# Brief: drawing medical devices for the House app

The House app builds rehabilitation centres; its furniture library gets the equipment of the Xiangyu Medical
(Sunnyou) catalogue, each device as a parametric 3D model. You draw devices as design files; Unity renders them for you.

## Read first
- `Docs/medical-designs.md` — the design format (frame, materials, part kinds). Follow it exactly.
- `tools/medical/inventory.json` — every device: code, names, category, mount, `size` [W, D, H] mm (`printed` =
  from the leaflet, else an estimate), `form` (a description for the modeller), `photo` (+ `views`, `screenCrop`,
  `variantPhotos`), `note`. Look at the photos (Read the jpg) — they are the truth; the form text helps.
- `Assets/House4696/Resources/Medical/Designs/_med-test.json` — an example using every part kind.

## The loop
1. Write `Assets/House4696/Resources/Medical/Designs/<id>.json` (id exactly as in the inventory; `size` = the
   inventory size unless the photo clearly contradicts an estimate — then say so in your notes).
2. Unity (running, it watches the folder) renders it within ~5–15 s to `tools/medical/renders/<id>-angle.png`,
   `-front.png`, `-side.png`, `-top.png`, then writes `tools/medical/renders/<id>.txt`: `ok`, or the errors (a part
   that fails names itself). Wait for the .txt to be NEWER than your json (poll its mtime, e.g.
   `until [ tools/medical/renders/<id>.txt -nt Assets/.../<id>.json ]; do sleep 2; done`), then Read the PNGs.
3. Compare with the photo side by side; fix and save again until it reads as that device. Typical fixes: a box that
   should be a rounded shell (r, loft), wrong proportions, colours, a missing screen / handle / castor, parts
   floating or intersecting badly. Two or three rounds are normal.

## Details first (the user checks details against the catalogue)
For every device, BEFORE drawing, write in your notes a **parts list from the photo(s)**: every visible component
with its place, shape, proportion and colour (e.g. "white X-shaped base on 4 grey 100 mm castors; grey tray 30 mm
thick on top of the cabinet, wider than it by 40 mm each side; screen 15.6" tilted 15° back with the interface picture;
two translucent acrylic arms with black joints and round grey heads…"). Draw from that list.
After every render run `python3 tools/medical/compare.py <id>` (it re-runs itself with ~/.cache/house-med-venv, which has Pillow) and Read `tools/medical/renders/<id>-compare.png`
(the photo next to the angle/front/side renders). Go through your parts list item by item — present? right place,
size, proportion, colour, shape? — and fix every difference you can see at that scale. A device is done only when
you find no more differences; record the final check (and anything left approximate, with the reason) in your notes.
Typical misses to look for: colours of bases/frames (white vs grey), trays and shelves, castor size, handles, vents
and grilles, the interface on screens (`print: "med_<id>_screen"` when a screenCrop exists), translucent parts
(`acrylic`), straps (`strap`), coiled cables (`coil`), oval/rect profiles (`sweep`, `bar`), rounded ends (`dome`).

## Rules
- Write only your devices' design files and your notes file `tools/medical/notes/<your batch>.md` (per device: what
  is approximated, size doubts). Do not edit C#, catalog.json, the inventory, other designs; no git; do not call
  Unity yourself (the watcher renders).
- Quality bar (Docs): recognisable at 2–3 m, smooth shells not bare boxes, the photo's colours, real castors,
  handles, pads, screens. Keep it efficient: a cart is typically 15–40 parts, a robot 40–90; use `mirror`/`copies`.
- Screens: `kind: "screen"` with `mat` for the casing; `print: "med_<id>_screen"` shows the interface when the
  inventory has a `screenCrop` for the device, else a dark screen.
- `mirror: "x"` reflects about the middle of the size WIDTH (not the body): on an off-centre body use explicit copies.
- Keep a generator script per device if you like (`tools/medical/gen/<id>.py`, see `tools/medical/gen/lib.py`), so
  the design can be regenerated; it must only write that device's design file.
- Engine notes: `decal` honours `copies` / `repeat` / `mirror` / `rot` (fixed 2026-10-02), `cyl` honours `rot`. A screen
  picture is stretched over the whole screen face: size the screen to the crop (panel + rim) so the crop's edges blend.
- `rots` [{axis, deg, about}, …] adds more turns after `rot` (tilt + turn on one part). Lettering: `text()` in
  `tools/medical/gen/p1lib.py` draws real letters from rotated decal strokes (capitals, digits, +/−, 翔宇) — use it for
  visible brand names instead of grey blocks. A screen crop with background/perspective: cover the bad corners with a
  thin plate in the bezel/body colour > 1.5 mm in front of the screen box.
- `repeat` steps along the design axes; `"local": true` steps in the part's turned frame (rows of slots/keys on a tilted
  panel). Open tubs/basins: any solid part at rim height closes the basin from above — make skirts, seams and rim rings
  holed slab outlines or lofts/lathes with `caps: false` (see tools/medical/gen/h1_lib.py).
- Dark marks (LED windows, black labels) on a light glossy face: a decal can render light grey — use a thin `box`
  (0.5–1 mm proud, `soft: true`) for dark marks instead.
- Brand marks: `brand()` in `tools/medical/gen/t4lib.py` draws the Xiangyu logo disc with the cross, 翔宇医疗 and
  XIANGYU MEDICAL in real letters; `tilt_parts()` there puts labels on sloping faces.
- Careful: `import p1lib` re-binds `D.decal`, `D.bar`, `D.screen`… with physio-1's argument order (decal(id, at, size,
  mat, face) instead of lib's decal(id, at, size, face, mat)). If you only need `text()`, save lib's methods before the
  import and restore them after (see tools/medical/gen/h2lib.py), or pass keyword arguments.
- Screen pictures: if you straighten/replace a picture, write both `tools/medical/reference/<id>_screen.jpg` and the albedo
  in `Assets/House4696/External/Materials/med_<id>_screen/`; the watcher reimports a changed albedo and re-renders the
  device by itself.
