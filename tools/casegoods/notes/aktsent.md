# «Акцент» (aktsent), П3.595 — 10 modules, all by catalogue + product photos

Generator `gen/aktsent.py` (writes the 10 designs and `gen/aktsent_catalog.json`). Check sheets `pilot/aktsent-*.png`,
all print ok; refs are the front-on product photos of pinskdrev.by (scratch `site/…/1.jpg`, 3.02 `0.jpg`, 3.04 / 3.10
`0.jpg`), overlaid with the handle padding of the wave's `pilot.py`. Every red outline sits on the photo within a few mm.

## Sources and scale
- Catalogue p. 132 (printed 260–261): the interior (3.05, 3.09, 3.04, 3.02, 3.03) and 3/4 cut-outs of all modules
  (closed + open) — perspective, used for the layout (flap counts, handle positions, trays), not for measuring.
- Product photos (all modules; front-on, 3/4 and open views) — measured by luminance profiles. The site photos are
  printed 4–8 % wider than true (3.01: 1.078, 3.07: 1.07, 3.09: 1.07, 3.03: 1.00), so x is scaled by L and y by H
  separately. Where a photo is cropped (3.05: feet cut) the x scale was used.
- No instructions exist: every module is «по каталогу и фото сайта, без инструкции».

## Construction (common)
- Carcass ЛДСП 16 «Дуб Мадура»: bottom over the full width on feet, sides on it, top over the sides (all photos show
  the bottom's and top's edges running the full width). ХДФ back in grooves (6–9.5 from the back), white.
- Fronts ЛДСП 16 «Персидский жемчуг», **inset** between the carcass parts, flush, 2 mm gaps (3 mm on 3.03 / 3.05 sides).
- Shoe cabinets 3.01 / 3.06 / 3.07 / 3.08 (B 200): the wood band beside the flaps measures 33–35 mm on every photo
  (both sides, so not perspective) while top / bottom are 16–17: built as side 16 + a 16 × 76 mechanism stile at the
  front (a guess at why the band is doubled; a 32 mm side would look the same). Fronts 35 in from each side (474 wide).
- Tilt-out flaps: `flap` hinged at the bottom, 80° (the open photos show the fronts nearly flat — only their edge and
  a sliver show). Each carries a grey-blue steel tray (`door_enamel_whitey#8a9ba7`, photo 3.01/3.07 open: #8496a2 lit
  #8d9fab): floor 1.5 on the flap's inner face, a 110 mm wall at the hinge end (horizontal when shut, upright when
  open — the tall back wall of the photos), sloped side cheeks (`shape: path`) and a 16 mm front lip; all in the move.
- Feet: satin metal blocks 56×56×50 (photos give 45–55 high, 52–64 wide — one standard foot used), 35 in from the
  sides. 3.03 on low 86×40×15 feet, 3.02 on 30×30×10 feet, 3.05 on black glides 10.
- Handles: satin-chrome bow handle 208 long (all photos agree 207–212) = `bar` d 208, band 22, square posts. Horizontal
  centred 50 under a front's top edge (3.03 measured 49–51 on all four), on the 3.08 lift-up flap 50 over its bottom
  edge; vertical on the 3.05 doors, 50 from the meeting edges, centre y 1050.
- Drawer boxes in the front colour (white on the 3.03 open photo), ХДФ bottoms, 13 mm runner gaps; the ball runners
  are not modelled.

## Per module
| id | what | from |
|---|---|---|
| 3.01 544×200×966 | drawer 173 over two flaps 351.5 (lower no handle), shelf under the drawer | front photo 1, open photo 2 |
| 3.02 800×400×450 | open bench: partition, a loose shelf each side (159–175), fixed shelf 306–322 under a pearl rail set back 20 (322–396), top 396–412, a 3 mm dark seat base and a `soft` cushion 415–450 inset 12 (H is to the cushion's top) | photos 0 (front), 1 (3/4) |
| 3.03 700×404×859 | four equal drawers 200.5, feet 15 | photo 1 (isotropic), 2 (open) |
| 3.04 558×21×708 | mirror 4 with a half disc R 354 on the left (fits the photo outline to 2 mm), backing ЛДСП 16 inset 20, wall | photo 0; catalogue p. 132 cut-out agrees |
| 3.05 1102×581×2064 | 2-door wardrobe (x 202–1086) + a shoe column on its left END: six flaps facing −x, trays inside the 186 deep column; one top and bottom over both; interior: hat shelf 1733, rail Ø25 at 1695, lower shelf 278, backs joined behind a pearl rail 965–1100 | photos 0–3 (front, open, 3/4 open) |
| 3.06 803×200×1798 | the 544 flap column (5 flaps 340.8, handle on the 3rd from the top) + an open column 259 wide, 1447 high: 3 flat pearl shelves (997, 1218, top 1431) and 4 sloped shoe shelves (front edge up, −29°, `rot`), back only below 1005 (the photo shows no back above) | photos 0–2 |
| 3.07 544×200×1936 | flaps 334 ×2, drawer 170, flaps ×3; handles on the 2nd flap, the drawer, the 3rd flap; shelf over the drawer | photos 1, 2 |
| 3.08 544×200×1798 | 4 flaps 340.8 (handle on the 3rd from the top) under a lift-up top flap (`flap` hinge top, 95°) over an organiser (floor shelf, two dividers, a small shelf) | photos 1, 2 |
| 3.09 760×216×1410 | three pearl boards 230 (19 apart; 802 / 802 / 1410 high), Мадура shelf 760×200 at 1111–1127 on two black brackets (a plate + a curved arm by `shape: path`), four black double hooks (`shape: path` side profile), wall | photos 0, 1 |
| 3.10 200×29×470 | moulded frame 28 (profile `aktsent-frame`, closed moulding) round a pearl board, three black L hooks (`shape: path`), wall | photos 0, 1 |

## Finishes and colours
- `aktsent-zhemchug-madura` «Персидский жемчуг / Дуб Мадура»: front and back #dfe3e2 (the p. 132 «Фасад» swatch,
  crop 0.735,0.855,0.775,0.905, ±0.9 flat); body «Дуб Мадура» provisional #beb1a1 (p. 132 «Каркас» swatch, crop
  0.815,0.855,0.87,0.905, ±6.2) — a textured decor, listed in `gen/aktsent_decors.md`.
- Pearl parts besides the fronts (from the photos): backs, all interior shelves of 3.05 / 3.06 / 3.08, the 3.02 rail,
  drawer boxes, the 3.09 boards, the 3.10 board, the 3.06 open column's top.
- Role `fabric` velvet#b0a28c (the 3.02 cushion, photo top face #afa089). Trays door_enamel_whitey#8a9ba7. Hooks,
  brackets, seat base, 3.05 glides `black`. metal = chrome (satin handles, feet, rail).

## Size decisions (catalogue wins)
- 3.04: site 700×20×550 = the same mirror hung sideways; built 558×21×708 (portrait, straight edge right).
- 3.06: site 828×200×1936; the site photo has the catalogue's proportion (0.476 against 0.447 × 1.07), so it IS the
  803×1798 piece → built 803×200×1798. The p. 132 cut-out shows the open column on the LEFT, the three site photos on
  the RIGHT: built as the photos (probably assembled either way — the lead may add a mirrored variant).
- 3.08: site H1766 → 1798 (the carcass of 3.06, same flap size).
- 3.10: site B32 → 29.
- Others: site sizes equal the catalogue.

## Engine limits for the lead
- **3.05 side-facing flaps:** the shoe column's six flaps face −x; `flap` only turns about an x line (fronts facing
  +z). They are static fronts with their trays in the shut position; needs a flap about a z line (hinge "bottom" on a
  side face). Their two bow handles are `rod`s (grip + two posts) because `handle` only sits on ±z faces.
- The bow handle is curved (a "smile" whose ends come down to the face); `bar` is straight.
- Pearl boards of 3.09 have wood-coloured (Мадура) edge band — no edge-band colour in the format.
- Mirror facets (3.04, bevel ≈ 15 mm) are not modelled; the checker draws the D-shaped mirror as its box.
- 3.08 gas struts, 3.05 / 3.03 runners and the flap mechanisms' grey side plates are not modelled.
- `rod` handles / rod parts are not drawn on the sheets.

## Skipped
Nothing — the collection has no chairs (the cushioned bench 3.02 is case furniture with a pad, built).
