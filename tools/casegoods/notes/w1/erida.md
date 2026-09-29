## Эрида (erida) — 13 модулей, все по каталогу (генератор gen/erida.py)

**Sources.** Catalogue pp. 18–20 only: the front-on living-room photo p. 18 (витрина, тумба — the best references),
the bedroom photo p. 19 (комод 1.31 almost front-on, шкаф 3Д, bedside), the kids' room photo, the door / side close-up
and the module cut-outs with sizes on p. 20. No module has a usable instruction:
- **erida-0-17 (витрина)**: the site links `shkaf-vitrina-Bays-2619Br-1.pdf` = «Шкаф-витрина „Байс 2619“(-01) БМ790»
  (Пинскдрев-Бобруйск) — another product: 700 wide, sides 1865, a plinth on 80-mm feet, one glazed door over two
  drawers. It does not match the catalogue module (600×450×2000 on legs, glazed door over a solid door, glazed sides).
  Its table (no text layer) is transcribed for the record in gen/cutlists/erida-0-17.json with a note; the model has
  no "is", so check.py does not use it. The витрина is built by the p. 18 photo.
- index.json's "check" entry П7.056.1.16 has a garbled name («П7.056.1.22: L508xB450xH623 Шкаф для одежды 3Д «Эрида»»):
  the page (p. 19/20) reads «Шкаф для одежды 3Д «Эрида»», L1532×B588×H2259 — the size was right, the name was fixed.

**Construction (one system for all case pieces, measured on the p. 18/19 front-on photos with the catalogue sizes as
scale):** carcass ЛДСП 16 on four square tapered legs 180 high (45 → 30, the outer faces vertical: a `rod` leaning in;
six legs on the 1632 / 1622 pieces, a middle pair on the 3Д wardrobe); top over the sides and over the face frame, bottom
between the sides, ХДФ back in 5-mm grooves 6 from the back. In front of the carcass edges a flat face frame of 16-mm
МДФ strips: stiles 45, a 28 top rail and 20 bottom rail on the tall pieces (витрина, шкафы — border ≈ 45 on three
sides as photographed), no top rail and a 12 bottom rail on the low ones (тумба, комоды, прикроватная — the fronts go
up to 3 mm under the top on the p. 18/19 photos), a 45 middle rail (витрина's belt, the desk pedestal's niche floor).
Fronts МДФ 16 are inset in the frame, flush with its face, 3-mm gaps. Knobs: round gold Ø34, 26 out of the face,
outside B (B = the frame face / top). Drawer boxes ЛДСП 16 with ХДФ bottoms, 13-mm runner gaps.
- витрина: glazed door (bronze glass, frame 30) over a solid door, belt rail between; above the belt the sides are
  glazed frames (МДФ stiles / rails 40 round a glass pane) standing on a full-width middle panel; 3 glass shelves at the
  heights of the photo, one ЛДСП shelf below. Door hinged left (it is «универсальный»: can be rehung).
- тумба: two doors and a middle column with an open niche over a drawer (partitions behind the gaps).
- шкаф 2Д: two doors over a full-width drawer; inside (the sketch on p. 20) a partition, shelves on the left, a rail on
  the right, a hat shelf. шкаф 3Д: a full-height left door (shelves), two doors over three drawers on the right (hat
  shelf, rail) — the drawer / door proportion is read from p. 19 (the cut-out's legs are perspective-stretched).
- комод 1.31: two small drawers on top (≈175), four of 225; комод 1.32: 4 small drawers over 2 + 2 wide ones.
- стол письменный: a 500-wide framed pedestal on legs (open niche ≈ 108 over two drawers), a 25 panel leg on the right,
  a modesty panel, the 16 top over all (B 650 = the top). стол туалетный: 25 panel legs to the floor, a drawer on each
  side, in the middle a lid in the top hinged at the back (flap, axis [800, 60]) with the mirror under it, over a tray
  behind a fixed apron; modesty panel.
- полка 2.71: an open box on the wall (no back: the wall shows through on p. 20). зеркало: a 75-wide ring frame over a
  round mirror (Flora-like).
- кровати 2-16 / 1-12: headboard 22 with a milled frame face (border 55), rails and foot 16 (220 high) on four tapered
  legs, cleats, 24 slats, a middle beam on two glides, mattress 1600 / 1200 × 2000 (the 128-mm width over the mattress is
  the same on both beds).

**Finish:** «Персидский жемчуг» only — `door_enamel_whitey#dfe3e2` from the p. 132 swatch (the lead's reference for this
colour across collections). Erida's own swatch on p. 20 reads #c3c1c0 and the p. 18 photo #cdc3c2 — the print differs;
p. 132 was used for consistency. Metal `gold#c6a46c` = the knobs (p. 18, a highlight-weighted sample; raw mean #a5825b).

**For the lead (engine / checker limits):**
- The sides of every case piece show a milled frame (border ≈ 40, sunk panel) in the p. 19/20 photos and the close-up;
  `face` works only on a board's +W face, so the left sides (outer face −x) can't carry it — left plain on both sides.
  A face on the −W side (or `face.side: -1`) would express it.
- A `glass` part has no tint: the витрина's side panes should be bronze like the door (`glass.tint` exists only on
  glazed fronts). A glazed front with the glass plane across x drew wrong in preview2d, hence the strip construction.
- Tapered legs are `rod`s with a `box` = their bounds, only so the checker counts them in the extent (the engine
  ignores `box` on rods).
- Sizes are measured off photos (±10–15 mm on frame widths, front heights, knob heights); the overall sizes are exact.
