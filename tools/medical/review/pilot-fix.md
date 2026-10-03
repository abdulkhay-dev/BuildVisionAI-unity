# Detail review — batch pilot-fix (10 devices)

Method: `compare.py <id>` sheet + every catalogue photo at full size (crops where needed), list of differences, fix in
the generator (`tools/medical/gen/*.py`, `pfx_lib.py`), regenerate, wait for the fresh `.txt`, re-check. All ten
render `ok`. Backups of the two generators reworked most are in the reviewer's scratch folder (not in the repo).

## xyg-3 — electrical parallel bars (`gen/xyg3.py`)
Found:
- Left posts leaned only ~20° and stood near the platform end; measured on the photo with the rails' vanishing point
  (cross-ratio along the near/far rails, cross-checked with the platform seam, which falls exactly in its middle):
  post tops ~570 from the rail end, feet ~985 → lean ~25°.
- The platform was as long as the rails. On the photo the rails overhang the platform's left end by ~650 (the leaning
  post tops stand beyond it) and its right ramp end by ~80; platform ≈ 650–3420 with the seam in its middle.
- Right lifting columns at 2780 → photo ~2930 (~550 from the rail end).
- Clamp lever at the near-left end was a 16 mm stub; photo: a long grey lever sticking out to the left with a black grip.
- Control box plastic and too far left; photo: brushed silver-lavender metal box right next to the near column base.
Fixed: all of the above (platform slabs, rivet rows and trim follow the shorter platform; right ramp 220 long).
Left as is: logo is icon + bars (no text); right columns are uniform tubes (the step between outer/inner stage is
barely visible on the photo).

## xy-72 — PT training table (`gen/xy72.py`)
Found: castors black → photo grey tyres with chrome forks. Everything else on the parts list matched (raised head
section, ladder at the head end, same-orientation lever plates with bolts and lettering rows, actuator, retractable
legs with grey caps, linkages, motor box low at the foot end, foot bar on Z levers).
Fixed: castor tyres grey.
Format limits: embossed "XIANG YU"/"MEDICAL" are rows of grey blocks (no text rendering).

## xygs-2 — quadriceps chair (`gen/xygs2.py`)
Found:
- Seat far too high (675) for the photo: the backrest is ~1.4× the seat height above the seat; the knee pivots sit at
  seat level. Seat top lowered to 555, the whole chair/arms/backrest/pivots/knobs/handles down by 120; backrest now
  ~600 above the seat (was ~475).
- Shin rollers: right roller on the photo is down near the floor (~170), left one higher (~330); pegs next to them.
- Front label: white with blue text → photo a BLUE label with white text.
- After lowering, the right Velcro loop went through the floor → loop depth now limited by the roller height.
Fixed: all of the above.
Left as is: sand bags are smooth translucent shapes (no plastic creases); 3 star knobs per side.

## xyj-j9 — treadmill with parallel handrails (`gen/xyjj9.py`)
Found:
- Front handlebars were small hooks; photo: tall D-loops (~400 high) — top from the console wing toward the user,
  front bend down to ~700, bottom part rising back into the upright just under the console.
- Side handrails/inner post tubes rendered as flat white "chrome"; photo: warm polished stainless.
Fixed: handlebar path redrawn as the D-loop; rail and inner tubes metal#cfc8bd.
Format limits: console text, LEDs and track display are decals (no screenCrop for this device); the belt script is
a dotted line.

## hyz-iiia — seated steam capsule (`gen/hyz3a.py`)
Found (the biggest mismatch of the batch):
- Shoulders were two separate blobs sitting on a flat top; no V-notch. Photo: the front face itself rises into two
  rounded shoulders with a deep V-notch between them at the front of the neck opening.
- Behind the split line the rear shell was a flat shelf; photo: it rises to shoulder height and the green seam runs up
  the side to the top and across behind the head.
- Leaf label sat low and was tilted at a different angle from the face (its corner stuck out).
Fixed: body loft now ends at 1100; the shoulders are a mirrored y-loft that starts identical to the body section
(so the front face flows into them without a crease) and narrows/inclines inward to form the V (bottom ~1170, tops
~1340); a mirrored rear collar loft whose front face is the seam plane rises to shoulder height; side seams continue
up the side, top seam runs over the collar and along the neck opening; ear trumpets moved onto the new inner faces;
headrest lowered to sit on the body; label at ~1000, rotated to the face slope (27°).
Format limits: the label is two rectangles (no leaf artwork / curved banner); the shell is lofted rounded-rectangles,
so it is a little less "egg"-shaped than the moulding on the photo.

## xy-cryo-3 — cryotherapy device (`gen/cryo3.py`)
Found: the hose was drawn corrugated, the photo hose is SMOOTH matte rubber (checked on a crop); its lowest point was
at ~240, photo ~1/3 of the cabinet height.
Fixed: smooth hose Ø60, lowest point ~335.
Format limits: the tablet picture looks washed out in the angle render (glossy picture material reflects the
sky at that angle — C# material, not editable here); the screen on the photo is slightly wider than the cabinet,
kept within the 500 width; Chinese logo text is a blue bar.

## xy-k-cdb-ii — shortwave therapy cart (`gen/cdb2.py`)
Found:
- Head too wide and too shallow (500 × 375). Measured on both photos against the column: ~420 wide × ~445 deep.
- Acrylic arm plates rendered opaque pale blue; photo: clear, almost invisible.
Fixed: head 70–490 × 30–475 (screen and tilt pivot moved with it); acrylic alpha lowered (#e4ecf06a).
Format limits: the screen crop is a perspective photo, so its corners show a little white housing.

## xy-szgjk-ii — upper limb training robot (`gen/szgjk.py`)
Found:
- Table too high (800). With the seated dummy and the column/table ratios of all three photos the top is ~680.
- Monitor too small and too high: photos give ~640 × 390 (27–28"), bottom only ~100 above the plinth (was 250).
Fixed: TOP 680 (column stages shortened), monitor enlarged and lowered with its UI decals, side box, camera hub,
boom and camera; size H 1560 → 1330 (camera top 1315).
Format limits: UI is decals (no screenCrop); the S-end undercut is a dark strip.

## xy-zbd-ic — bedside lower-limb exerciser (`gen/zbd.py`)
Found: the display was black; on the photo it is switched on — pale grey-blue glass with a lighter band.
Fixed: two light decals over the screen. Everything else on the parts list matched (housing, flat blue legs, castors,
blue/silver column, clamp with knobs/saddle/U handle, boom with logo, joint block with knob, arm with white cap,
drum, cradles, straps, foot plates).
Format limits: the photo is low-res, so cradle and foot-plate shapes are inferred.

## xy-k-e1 — gait training frame (`gen/e1.py`)
Found:
- Column foot too low (255): on the photo the chrome column starts ~470 up, the curved struts rise from the legs'
  REAR parts and arch over to it (they were long diagonals reaching forward).
- Top flange at ~1400 → photo ~1490; handrails ~1075 → ~1135.
- Vest ~100 too high (handrails crossed its middle); photo: vest top just under the handrails, thigh cuffs ~600.
Fixed: all of the above (straps re-ended at the lower vest).
Format limits: harness is rigid (no cloth sag); carabiners are small coils + loops; the photo is one view, so the
strut layout under the column (one per leg) is inferred.
