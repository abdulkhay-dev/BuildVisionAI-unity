# Pilot batch — 10 devices

Designs: `Assets/House4696/Resources/Medical/Designs/<id>.json`; renders: `tools/medical/renders/<id>-{angle,front,side,top}.png`.
All ten render `ok`. The designs were written by small Python generators (in the session scratchpad), so the JSON
has computed coordinates, for example the steam-capsule seam that follows the loft surface.

## xy-72 — PT training table (electric, 2-section). 2 rounds
- Pose: top at 620 mm with the head section raised 30° (its top reaches ~970, inside the 1000 limit). The table can go
  500–1000, so the size H 1000 is the travel limit, not this pose.
- Approximated: the scissor lift is shown as two concave lever covers per side, a centre beam, an actuator and a motor box.
  "XIANG YU / MEDICAL" lettering is a grey bar. The retractable legs and the castors are fixed. The chrome foot bar is a
  closed loop around the base (the photo shows only its right end).
- Size: as printed.

## xyg-3 — electric parallel bars. 2 rounds
- Rails at 1000 (middle of the 850–1300 range); size H stays 1300 = the top of the range. Rails are 600 apart (range 380–630).
- As in the photo, the left posts lean 20° toward the left end and the right posts stand upright. Platform halves have
  bevelled ends and aluminium edge trim. The pendant hangs on a coiled cable, which I approximated as a helix polyline.
- Approximated: no valgus board or walking kit. The logo on the control box is a blue bar.

## xygs-2 — quadriceps chair. 1 round
- Approximated: the perforated angle discs are a plain disc with a dark ring (no holes). The sandbags in plastic bags
  (photo) are drawn as teal weight plates on the pegs, matching the form text. The shin-roller straps are thin tubes.
  The lever pins and knobs are simplified.
- Size: as printed (leaflet 1060×1050×1160).

## xyj-j9 — treadmill with parallel handrails. 3 rounds
- Orientation: the console end is at the back (z≈0) and the walking tail is the front (z = depth), so the console
  screen faces the user, per the frame rule "front = where the screen faces".
- Approximated: the console is a tilted black desk with a raised display pod (dark face, two red LED windows, a blue LCD
  patch) and a strip for the keys. The uprights are round Ø75 tubes; the real ones are oval/rectangular bronze profiles.
  The handlebar loops are smaller than in the photo. The "American Motion" decal is a white strip with a red mark.
- Size: as printed.

## xy-k-cdb-ii — shortwave therapy cart. 1 round
- **Size changed** to [1050, 600, 1450] (inventory 560×560×1200). The inventory estimate covers only the body, and its
  own sizeNote says the arms rise to ~1450 and reach ~600 mm right of the body. The body sits at x 0–560 with the arms to
  the right, so the item origin (middle of the back) is off the body's centre by ~245 mm.
- Approximated: the arms are drawn as white Ø34 rods with dark hubs; in the photo they are translucent acrylic plates.
  Each arm has three joints, then a double knuckle and a Ø200 electrode (black rim, white face). The cables are soft grey
  tubes. The louvres are short dark tilted strips.

## xy-szgjk-ii — upper limb training robot. 2 rounds
- Layout: the patient sits at the front, and the monitor, plinth and arm hub are at the rear left. The top is a thick
  white slab with brushed end caps; the S logo is a grey patch. The two-link arm has a white body with a black top, a
  flat lower link, a black forearm pad and a black grip on a grey disc. There is an e-stop and three buttons at the front,
  and a 23.8" monitor on a pole with a camera boom.
- Doubt: which side the patient sits is ambiguous in the photos. I chose a long-side front, so the floor rails run
  front–back (matching photo 2).
- Approximated: the cut-out under the left end of the table is not drawn. The keyboard and mouse are omitted.

## xy-cryo-3 — cryotherapy device. 2 rounds
- Approximated: the "翔宇医疗" logo is a blue square with a bar. The grilles are drawn as slot copies. The hose is a single
  smooth tube with no corrugation. The nozzle is a tapered black rod.
- Size: estimated (by analogy with CRYO-1). The cabinet is 530 deep and the hose loop takes the front 60 mm of the 620.

## hyz-iiia — seated steam capsule. 3 rounds
- Shell: one loft along z (7 sections) plus a raised rear headrest loft. The head opening is a dark well with a white
  neck-pad ring, two side discs and a small lid fin. The front step has grip slots.
- The green seam is computed onto the loft surface: the generator finds x on the rounded section at each (z, y). Without
  this, a seam floats away from rounded shells.
- Approximated: the loft's flat end cap shows as a flat oval at the front bottom; the real shell rolls smoothly into the
  step. The photo's shell also has a door split line and more doming at the top front than lofted rounded rectangles can
  give.
- Size: estimated; the photo agrees.

## xy-zbd-ic — passive/active exerciser (bedside, lower limb). 2 rounds
- Orientation: base and column at the back, boom forward (+z) over the bed, motor drum and leg cradles at the front.
- Approximated: the drum is a plain lathe with the cranks at 35°/215°. Each pedal carries a black foot cup, with a strut
  to an open U calf cradle drawn as a slab. The bed-docking clamp is a blue arm with a black D-shaped saddle and a black
  U handle. The silver label plate is a flat strip.
- Size: estimated; it fits the photo proportions.

## xy-k-e1 — gait training frame (manual). 1 round
- Layout: a U base of two Ø42 legs open at the front with a rear cross bar and Ø100 castors. Curved struts run up to the
  column foot. The column is a chrome square outer with a white inner tube, topped by an overhead tube ~600 forward with
  two hooks and a short top handle. Two black foam handrails run forward. The harness has a spreader, straps with blue
  pads, an open padded vest (loft without caps) and two thigh loops.
- Approximated: the buckles, the D-rings and the strap slack are omitted. The harness is rigid geometry, not cloth.

## Engine wishes
1. **`sweep`: a rectangle or rounded-rectangle section along a path** (like `tube` but not round). Today square-tube
   frames that bend or tilt are boxes with `rot`, and curved profiles become round tubes.
   Helps: xyj-j9 (curved oval uprights), xy-zbd-ic (angled boom arm), xy-k-e1 and xyg-3 (tilted square posts),
   xy-72 (frame), xy-szgjk-ii (arm links). This would also help most frames, bars and tables of the catalogue.
2. **`cyl`/`box` by two points with a profile** (`box` given `from`/`to` plus a section w×h and a roll). Placing a
   tilted square tube between two known points now needs hand-worked rotation pivots. Helps: xy-zbd-ic, xygs-2 levers,
   xyg-3 posts.
3. **Loft end shaping**: `caps: "round"` (a domed cap) or a per-end fillet, so a loft closes like a moulded shell
   instead of a flat cut. Helps: hyz-iiia (front bottom and top), steam cabins, capsules, robot covers, the cryo cabinet.
4. **Surface-attached parts**: a `on: <loft id>` option (or `project: true`) for tubes and decals, so seams, trim lines
   and labels sit on curved shells without computing coordinates outside the engine. Helps: hyz-iiia (green seam and
   label) and every capsule or hydro tub with trim lines.
5. **`pattern` / `grid` repeat** (`count`, `step`) instead of listing every copy. Helps: vent slots and louvres
   (xy-cryo-3, xy-k-cdb-ii), perforated discs (xygs-2), keys.
6. **Perforation / holes on `lathe` and `slab` faces** (a hole pattern on the disc), or a `print` decal on any face
   rather than only on `screen`. Helps: xygs-2 angle discs, grilles, logos and lettering (xy-72 "XIANG YU MEDICAL", the
   Xiangyu logo on cryo, cdb-ii and xyg-3).
7. **`coil` / `helix` path generator** (diameter, pitch, turns) for coiled cables. Helps: xyg-3 pendant and other hand
   controllers.
8. **Corrugated hose option** on `tube` (`ribs: pitch`). Helps: xy-cryo-3 and other suction or air devices.
9. **`strap` / `belt` kind**: a flat band along a path with width and thickness, for harness straps, Velcro straps and
   belts. Thin tubes read as cords. Helps: xy-k-e1 harness, xygs-2 shin straps, xy-zbd-ic cradle straps, traction
   tables.
10. **Translucent coloured plastic material** (`acrylic#hex`): solid but see-through, unlike `glass`. Helps:
    xy-k-cdb-ii (acrylic arms) and the lid fin on hyz-iiia.
11. **Pose / range metadata** (for example `"range": {"y": [500, 1000]}` per part group), so size H can state the
    travel while the model shows a working pose. Helps: xy-72, xyg-3 and every height-adjustable table or frame.
12. A note in the docs: for `loft` with `axis: "z"`, `cz` is the **y** centre (and for axis x, `cx` is the y centre).
    The table text "centred at (cx, cz)" reads as x/z.
