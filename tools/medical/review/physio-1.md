# Detail review — batch physio-1 (2026-10-02)

Method: `compare.py <id>` sheet + the catalogue photo(s) and screen crops at full size, every visible difference listed,
generator fixed (`tools/medical/gen/<id>.py`), re-rendered (waited for the .txt) and re-checked until no difference was
left at the sheet scale. All 14 render `ok`.

New shared helpers in `tools/medical/gen/p1lib.py` (physio-1 only):
- `text(d, id, s, origin, h, mat, along=…, face=front|top|left|right)` — lettering drawn as decal strokes turned in the
  face plane (decals honour `rot` now). Glyphs: the capitals needed, `n u y o`, digits `8`, `+ -`, and stroke
  versions of 翔 and 宇. Replaces the earlier "blocks for letters".
- `rpoly(points, r)` — SVG outline with rounded corners, for top-plane slabs (notched bases, X bases, rounded plates).
- Screen-crop masks: when a crop is perspective-skewed or contains background, a thin slab of the bezel/body colour
  is laid 1.5 mm+ in front of the picture (the engine puts the picture 1.5 mm in front of the screen box) over the
  parts of the crop that are not the device's panel.

## xyg-500ib — IR lamp on a stand
Fixed: vertical "XIANGYU MEDICAL" lettering (was dashes) + round logo, lettering sized to end above the stripes;
plinth with the shallow notches between the four corner pads; telescopic post = light bar with two black gas springs
on chrome rods and black cross brackets (was one chrome tube + dark tube + white clamps); black cone collar with a
white ring; arm = light flat bar with a black spring bar under it, black cable loop at the joint.
Cannot match: the Chinese text of the logo and the small print under it are plates.

## xy-scjg-ii — high-power laser cart
Fixed: base is a 4-arm X on the diagonals (was a 5-spoke star), tapered flat arms, castors 75; column is a wide flat
loft (190×76) with a flared foot (was 140×90 box, a seam showed); "Sunnyou 翔宇" read downwards in grey + the row of
small marks; drawer 345 wide (was 300), grip crescent as a shaped dark recess; head 210 tall (was 180); tray now
reaches in front of the head with the long grey grip pocket there; screen sized over the whole head front so the
crop's white rim blends; vent grille on the head's left side; second fibre; foot-switch cable kept.
Cannot match: the crop's bottom edge shows a faint grey line (tray shadow in the crop).

## xy-k-zwx-ii — UV desk unit (printed size)
Fixed: red "888" digits (was a red bar); white + / − marks on the blue keys; 4th key dark with a grey ring (was grey);
logo disc and title text plates on the band; right-side grey label strip; sockets flat metal rings with dark
centres (were domes); panel / band greys matched to the photo.
Cannot match: the Chinese title and the small key captions (plates / omitted).

## xy-ppzl-ii — spectrum floor lamp
Fixed: base arms broad and flat (graphite body + wide white caps, was thin bars), castors 90, white hub disc and
graphite collar; heating plate ribs vertical and dense, 5 guard wires (were horizontal ribs + 7 wires); radiator
tilt 22° (photo) instead of 30°; display light with blue "88" digits and a blue rim (was dark), label lines.

## xy-k-gnhw-ii — high-power IR lamp
Fixed: broad flat grey star base (slab, long front arms) and 75 castors; lower body raised to ~1255 with a sloped
dark top; S logo, speaker dot field and sockets moved to the BACK face (photo 2 is taken from the back-left: the
lamp's fan faces the camera); left side handle raised to 830–1140; upper column 150 wide; lamp drum Ø290×260 (was
248×176), lens ring narrower with the white lip outside it; larger curve from column into boom; chrome loop handle
on the yoke plate; small lettering plates on the yoke plate and the body foot.

## xy-k-czld-i — vibration plate with column
Fixed: real "XIANGYU MEDICAL" lettering (was blocks) + navy logo; base as pillow slabs with big plan corner radii
(was boxy two-tier), plate/arcs raised to it.
Cannot match: the console display stays dark (no screenCrop).

## xy-k-czld-ii — low vibration platform
Fixed: ECG on the right half of the upper front with tall spikes, 4 beats – gap with the "Sunnyou Body" plate – 4
beats (was small centred wave); 8 concentric ridges on the pad (was 5); rear control box moved left and enlarged
as in the photo.

## xy-k-czld-v — vibration trainer (black cover version)
Fixed: column side profile deep (~200 at the foot) with the head bending forward ~20° (was a thin plate, photos 2/3
show the depth); base taller (~150) with a thick chrome band; plate a rounded slab with 12 finer fingerprint lines;
chrome loop smooth and wide with a round top (was angular polyline); grips are short bars from the column sides
through the loop (was one bar across the front of the column); star perforations as decals in 22 rows down to the
foot, thinning towards the top, with the wave line; bigger screen (176×128).
Cannot match: photos 2/3 show the white-column variant — modelled black per the main photo.

## xy-k-medical — shock-wave desk unit
Fixed: the crop's bottom-left corner is the catalogue's green background — covered by a white body plate so no green
band shows on the front; handpiece grip larger (Ø62×70) and barrel/tip scaled.
Cannot match: the crop is perspective-skewed, so the panel edges stay slightly slanted. Size stays [520, 400, 260]
(barrel beyond the 400 body, as before).

## xy-fswt-ic — piezo shock-wave desk unit
Fixed: the crop is skewed and shows the white rim and the turquoise applicator in its top-right and the body at
its left/bottom — masked with black glass along the measured panel edges, so the front reads as one black pane;
handgrip head now faces front-left (was straight left) with light-green face and grey eye; green band rounded
(was a flat block); cable comb on the right holder.
Cannot match: the UI picture itself stays skewed (perspective of the source photo).

## xy-k-shock-master-500 — shock-wave cart
Checked: cabinet, drawers with T-notch handles, black X base, screen, two green handpieces already matched.
Fixed: the side logo cut-out got its small top-front head bump.
Cannot match: exact Xiangyu mark (approximated cut-out).

## xy-cryo-1 — cold-air cryo unit (printed size)
Fixed: tablet as wide as the cabinet, leaning back ~45°, its switched-off screen mid-grey (was small, black, 38°);
vents as 9 rows of short slots on the front and the right side (were two tall slot bands); grip recess raised to
700–820 near the middle of the side; hose loop swings out past the left edge as in the photo.

## xy-k-spll-v — physiotherapy station
Fixed: screen crop masked black outside the skewed tablet (white head showed through); head moved back so the
tablet stands proud of it (the head's top edge cut through the screen), tilt 18°; the whole left side of the column
dark grey with a taller vent grille (was a narrow band); "Sunnyou 翔宇" lettering (was a bar); frame base notched
between the castors with its grey lower edge; arched grey recess on the head side.
Cannot match: the photo's tablet is also turned ~10° to the right; a part takes one rotation, so it only tilts.

## xy-24 — standing belt massager (printed size)
Checked: frame, platform, column, motor drum with the red band, handlebars, springs, nodule pad and twist disc match.
Fixed: belt webbing 60 wide (was 45).
Cannot match: the source is a small old JPEG — motor details are a guess.
