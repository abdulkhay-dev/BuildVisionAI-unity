# «Симпл» (simpl), П7.058 — 2 modules, by catalogue + product photos

Generator `gen/simpl.py` (writes both designs and `gen/simpl_catalog.json`). Check sheets `pilot/simpl-3-10.png`,
`pilot/simpl-3-11.png` print ok; refs are the front-on site photos (`site/shkaf-kombinirovannyiy-simpl-p7-058-3-1x/1.jpg`)
and the red outline sits on them. No instructions exist: «по каталогу и фото сайта, без инструкции».

## Sources and scale
Catalogue p. 133 (printed 262–263): one interior photo of each module, no cut-outs, no swatches. Product photos: front,
3/4, open. x scaled by L (the body's outer edges, the legs splay only to about the body edge), y by H; anisotropy 1.04
(3.10) / 1.07 (3.11).

## Construction
- ЛДСП 16 «Дуб Кантри золотой», overlay fronts 16 with 1.5–3 mm gaps, backs ХДФ pearl in grooves, black round knobs
  (`knob` d 22), black L hooks 60 high (`shape: path` side profile), splayed tapered wooden legs (`rod` Ø36 → Ø24,
  splayed ≈ 25 outwards and to the front / back) each on a 3 mm glide (the glide carries the floor line).
- **3.10** 1026×440×2200: two tall boards 50–500 and 500–977 (the joint over the bench | cabinet line), standing on
  the carcass floor line 134 against the wall; shelf 27–998 × 200 deep at 2045–2061; three hooks 116 / 272 / 424 (the
  middle one 50 lower); mirror 448×677 (514–962, 1203–1880) glued on the right board. Bench 0–500: side, bottom,
  one shelf 288–304, top 440–456 (the bench's right wall is the cabinet side). Cabinet 500–1026: top 973–989 over the
  fronts, drawer 771–971 over two drop-down flaps 448–768 / 125–445 (`flap` bottom, 90°, as the open photo; the gas
  struts are not modelled), fixed shelves behind the joints, knobs on the drawer's centre and 20 under the flaps' top
  edges. Legs 134: four corners + one at the back under the bench | cabinet joint (none at the front middle — photo 0).
- **3.11** 994×420×2200: base 0–994 on legs 122: two drawers 242 (oak fronts, two knobs at 245 / 749), the top 612–628
  is the seat. Upper part on it: left side 48–64 (the top 23–994 overhangs it by 25, flush on the right), partition
  545–561, right side 978–994, depth 400; niche with pearl back, hat shelf 2014–2030 and hooks 141 / 305 / 469; closet
  with four shelves (940, 1290, 1560, 1840) behind a pearl door 563–992.5 × 631–2180 hinged right, a facetted mirror
  604–985 × 640–2095 glued on it (the mirror face = B 420, flush with the drawer fronts), knob at 581 / 1393.

## Finishes and colours
- `simpl-kantri-zhemchug` «Дуб Кантри золотой / Персидский жемчуг»: which part is which read from the photos —
  carcasses, boards, shelves, legs and the 3.11 drawer fronts are the oak; the 3.10 cabinet fronts, the 3.11 door, the
  backs are pearl.
- front / back #dfe3e2 = the «Персидский жемчуг» swatch of p. 132 (Акцент; Симпл has no swatch) — provisional.
- body «Дуб Кантри золотой» #b39266 = the Денвер swatch p. 33 (crop 0.670,0.855,0.695,0.89), as wave 1; Рокси p. 14
  gives #846c48, the p. 133 photos read #ac9372…#bda789 (nearer Денвер) — provisional, decor listed in
  `gen/simpl_decors.md`.
- metal black (knobs); hooks and glides black; mirrors.

## Size decisions
- 3.10: site B444 → catalogue 440. 3.11: site B431 → catalogue 420. The 3.10 depth is board 16 + bench / cabinet 424;
  the 3.11 depth is the base / top 420 (the upper carcass 400 + door 16 + mirror 4).

## Engine limits for the lead
- Gas struts of the 3.10 flaps (they link the carcass and the flap) — no linkage parts in the format.
- Mirror facets not modelled; the conical legs' feet are cut square to the axis (the known `rod` limit), and rods are
  not drawn on the sheets.

## Skipped
Nothing.
