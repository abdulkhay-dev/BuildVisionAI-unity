# «Шанталь» (shantal, П6.952) — 8 modules, all by instruction

Generator `gen/shantal.py` (helpers in `gen/kit_w3a.py`, shared by my five collections), fragment `gen/shantal_catalog.json`,
decors `gen/shantal_decors.md`, cut lists `gen/cutlists/shantal-{0-03,1-01,1-02,1-04}.json`, sheets `pilot/shantal-*.png`
(all ok; 1.01 and 1.02 overlaid on the instructions' orthographic front views, the others have only exploded views).

## Sources
The instructions (a.pinskdrev.by, downloaded to the scratchpad; not committed): cut lists of 0.01 / 0.02 / 0.03 / 1.03 /
1.05 from reference/, and of 1.01 / 1.02 / 1.04 read from the PDFs' text layer (the table is laid out in columns — rows
rebuilt by x position, checked against the table pictures). 0.03: the reference JSON read row 7 as ×2 (the table says 1)
and lost row 11 (door 1120 × 546 × 16.5, code printed «6.952.0.0311») — corrected in gen/cutlists.

## Construction (from the instructions)
- Sides stand on a separate plinth box (80 high on 4-mm glides ФБ 482): the plinth is under the bottom only, 16 mm in
  from the sides (front МДФ 16.5 with an arched lower edge — `shape: path`, sides and back ЛДСП 16 between). H = 4 + 80 +
  sides + top: 0.01 4 + 80 + 1871 + 25 + 17 = 1997.
- Living room 0.0x: ХДФ backs nailed on (z 0…3.5, their sizes = carcass − 10; the joints on the fixed shelves / partitions);
  a cornice frame of 25-mm strips (front + two sides mitred = one top-plane moulding `shantal-cornice` covering them, the
  back strip a panel) 14 mm over the carcass with a cove under the overhang; the 17 top over it, 13 mm further out; both
  «Дуб Сахара» (role `top`).
- Bedroom 1.0x: a 42-mm top («крышка», 27 mm over the carcass). The instruction's front views show a board over an ogee
  step: built as a 20 board + a top-plane moulding `shantal-crown` under its overhang (the pair `covers` the cut-list row —
  the panel format has no edge profile, see limits). 1.01 has its backs in grooves (top 625 = 582 + 16.5 + 26.5), 1.02 /
  1.04 nailed.
- Fronts МДФ 16.5 overlay, 2–2.5 mm reveal, 2.5–3 mm gaps. Doors: a milled frame (stiles 55–58, rails 58 / 62–66, the
  3-door wardrobe a middle rail 127 as drawn) round sunk wainscot panels with vertical boards; drawers: stiles 55–61 with
  a band of horizontal boards between them (joints 60 mm from the edges — the 1.02 / 1.04 drawings). Glazed doors: frame
  50 (glass 1020 × 446 = door − 100) with a glazing bead.
- Hinges from the drawings / photos: 0.01 right; 0.03 12 left, 11 / 10 right; 0.02 outer; 1.01 11 left, 12 / 13 right.
  Knobs k1 Ø30 on doors, bar pulls k2 c-c 128 on drawers (antique nickel).
- 1.01 interior as drawn: partition 3 full height (right column 526: fixed shelves 8 ×2, loose 9 ×2, 8.1 over the drawer),
  left section hat shelf 7, rail w1 1068, stiffener 10 behind the back joint; drawers 14 / 16 / 15 (the middle box 506).
- 0.01 / 0.03 «с подсветкой»: LED clips L1 on the glass shelves (light parts).
- Bed 1.05: headboard 876 × 1840 on glides + cap 1.1 (43 × 42, flush at the back), foot board 1646 × 482 with an arched
  lower edge, rails 2010 × 200 inside its ends; metal base 2000 × 1600 (m) with slats and two legs; mattress 200.
- Mirror 1.03: board 1000 × 700 × 16 with the mirror 960 × 660 × 4 on it (wall).

## Finish
`shantal-pepel-sahara` «Пепел / Дуб Сахара»: body `door_enamel_whitey#dcddd6` (the «Пепел» of Flora, p. 13 swatch — the
catalogue has no Шанталь swatch), role `top` = Дуб Сахара, provisional #7a6a55 (decor listed). Metal chrome#8c8983
(antique nickel).

## Engine / checker limits met
- One `face` per board: a wainscot door (frame + sunk panel + boards) is composed — the milled frame is the cut-list part
  (`shape: path` with its openings joined to the edge by zero-width slits, a "keyhole" outline, because check.py reads an
  outline as one polygon), the sunk panels (faces `grooves`) sit in the openings, a cove bead (`shantal-cove`) round them.
  A face type "frame with grooved panel(s)" / several frame openings would express it on one board.
- No edge profile on a panel: the 42 tops are board + moulding (the cut-list size is then not measured by the checker).
- The bed's foot board has no bead: check.py counts a front-plane moulding 16 mm deep, which would push the bed out of
  B 2043.

## Skipped
Nothing (no chairs in the collection).
