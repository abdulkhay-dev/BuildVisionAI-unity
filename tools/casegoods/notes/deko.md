# «Деко» (deko, Пинскдрев БМ2.776) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF pp. 72–74 (printed 140–145): p. 72 living room, p. 73 bedroom, p. 74 a
second living-room photo, the module cut-outs with codes and sizes, a close-up of a slatted front next to a drawer, the
«Дуб Наварра» swatch. No module has an instruction, so **all 13 designs are by catalogue / photo** (model notes say
"по каталогу, без инструкции"). The pinskdrev.by product photos (studio shots, several front-on, two with the doors open,
one with the bedside drawer out) were the main source of the construction. Generator `tools/casegoods/gen/deko.py`
(re-runnable; writes the 13 designs and `gen/deko_catalog.json`), decors `gen/deko_decors.md`, sheets
`pilot/deko-*.png` — every one prints `ok` in `gen/check.py` (the edge pulls give a «примечание» on B, see below).

| id | code | what | ref of the sheet |
|---|---|---|---|
| deko-0-34 | БМ2.776.0.34 | тумба 1542×400×896: door · 3 drawers · slatted door | p. 74 cut-out |
| deko-0-33 | БМ2.776.0.33 | тумба ТВ 1542×400×450: open niche over a wide drawer · slatted door | p. 74 cut-out |
| deko-0-06 | БМ2.776.0.06 | шкаф-витрина 2Д 941×400×1820: oak door under a glazed door · slatted door | p. 74 cut-out |
| deko-0-05 | БМ2.776.0.05 | шкаф-витрина 941×400×1201: the same, low | p. 74 cut-out |
| deko-0-51 | БМ2.776.0.51 | полка 1542×266×250 (wall) | site photo, front-on |
| deko-1-31 | БМ2.776.1.31 | комод 1471×460×970 on legs: slatted door · 3 drawers | p. 74 cut-out |
| deko-1-30-01 | БМ2.776.1.30-01 | тумба прикроватная 481×460×466, slats on the **left** | site photo, front-on |
| deko-1-30 | БМ2.776.1.30 | the same, slats on the **right** (mirror image) | the same photo mirrored |
| deko-1-32 | БМ2.776.1.32 | зеркало 1100×5×600 (wall) — not in index.json, from p. 74 | p. 74 cut-out |
| deko-1-44-01 | БМ2.776.1.44-01 | шкаф для одежды 3Д 1530×621×2200 | site photo, front-on |
| deko-1-65-01 | БМ2.776.1.65-01 | шкаф для одежды 2032×621×2200 | p. 74 cut-out |
| deko-1-10 | БМ2.776.1.10 | кровать 2-16, lift, [1813, 2109, 1050] | none (no front view) |
| deko-1-15 | БМ2.776.1.15 | кровать 2-18, lift, [2013, 2109, 1050] | none |

## Construction (one scheme, read off the photos)
- **Carcass** ЛДСП 16 «Дуб Наварра»: the bottom runs the full width *under* the sides (its end edge shows on the side in
  the 0.05 photo), the sides stand on it, the top lies over the sides over the full depth; ХДФ 3.5 backs in grooves at
  z 6–9.5; partitions from z 10, ending 2 mm behind the fronts; loose shelves 1 mm off the sides, 20 mm off the back.
- **Fronts** ЛДСП 16 **inset** between sides / top / bottom and flush with their edges (every photo shows the carcass
  edges framing the fronts), 2 mm to the carcass, 3 mm between fronts; the partitions sit behind the joints.
- **The slatted front** (the collection's motif). Decision after the close-ups: neither milled grooves nor a two-decor
  board — **a black ЛДСП 16 board with solid birch slats 30 × 20 glued on upright** (the site lists «Фасад: ЛДСП; массив
  берёзы»; side photos show the slats standing proud with their side faces lit and the black board in shade; the open
  0.05 shows the slat ends sticking out at the free edge of the swung door and the screw holes on the door's back; the
  bedside photo with the drawer out shows the slats' top ends). The slats' faces are flush with the carcass edges, the
  black board 20 mm behind them (the flat black field reads recessed in the 0.34 / 0.33 photos). Parts: the board is a
  `front` (mat `accent`), each slat a `panel` (mat `slat`, grain y) in the door's move.
  - living pieces: 4 slats (pitch 57–58.5) at the free edge of the right door, then a flat black field (≈ 200 on the
    vitrines, ≈ 300 on 0.33 / 0.34). Measured on the 400-dpi cut-outs (0.06: slats 524–551, 581–609, 639–666, 697–731).
  - chest: 7 slats over the whole door (pitch 60, 30 margins); the cut-out shows 7.
  - bedside: one drawer; its front = the black board 445 × 280 with 3 slats (pitch 61) and an oak ЛДСП panel 268 on its
    other part (all moving together — the site photo with the drawer out).
  - wardrobes: the sliding door, 8 slats 32 wide at pitch 58.6, ≈ 31 margins (front-on site photo).
- **Handles**: black aluminium edge pulls over the top edge of the oak fronts (the p. 74 close-up), 152 long (measured on
  the bedside photo: 440 px at 2.89 px/mm): centred on single fronts, at ¼ / ¾ on the wide drawers (0.33, 1.31,
  wardrobes), from the slat-side end on the bedside's oak panel. Glazed doors: an upright black bar 160 at the free
  edge, mid-height. Mirror doors: a slim upright bar 150 on each meeting edge (it straddles the joint in the photo).
  Slatted doors have no handle (none in any photo: the slats are the grip).
- **Glazed doors**: black aluminium frame 22 (0.05 close-up) round bronze-tinted glass (`glass.tint` bronze), 20 thick,
  inset. The vitrines' left column is **two doors** (oak lower, glazed upper, each hinged left: four hinges in the open
  photos, two per leaf, and a pull on each) over a fixed shelf at the joint; glass shelves in the glazed part.
- **Feet**: living pieces on black plastic glides 90 × 14 × 40 (photos); chest and bedside on black metal legs (a flat
  arm under the bottom along x inwards, a tapered post splayed 8 mm out, `rod`s + a glide `tube` for the floor line);
  legs 175 (chest, from the cut-out: carcass 794 of 970) and 150 (bedside, front-on photo: 1220 px = 466).
- **Wardrobes** (1.44-01 site photos: closed front-on, 3/4, and with the sliding door moved left): sides on the floor,
  the top over them, a fascia 54 under the top's front edge (the 70 mm band of the photo), a recessed black plinth 60
  under an oak front rail, the bottom at 82–98 with the aluminium double bottom track, the top track behind the fascia.
  - Left section (984 inside): two drawers 243 with two pulls each, a fixed shelf at 591, two doors 1507 high with
    a mirror glued on, hinged on the left side and on the partition; inside a hat shelf and a rail (guess — not visible
    anywhere).
  - The slatted door slides on the front track (z 585–621) and closes the section behind it (rail at 1905–1930 and a
    fixed shelf at 591, as the photo with the door moved shows); it moves over the mirror doors (`slide` by −700, the
    photo's position). The mirror doors and drawers are set back behind the sliding zone (faces at z 553).
  - 1.65-01 (2032) = 1.44-01 + a third section (shelves) behind a sliding oak door on the rear track (z 563–579),
    which slides −500 behind the slatted one. Widths from the p. 74 cut-out (mirrors 469 / 474, slats 481, oak 505).
- **Beds**: headboard ЛДСП 25 W × 1050 with a black velour panel quilted in 2 × 6 cells (`soft`, tufts [6, 2]) as wide as
  the box, 477–990 high (site photo); the box = rails ЛДСП 25 × 320 (sleeping width + 52 — the site gives
  «2109x1652» for 1600) on a recessed plinth frame 40 high, a storage bottom ЛДСП 16; inside, the black lift frame
  (tubes 30 × 25, a middle beam) with 26 / 28 birch slats and the mattress 2000 × 1600 (1800). The catalogue's B1813 /
  B2013 is then the headboard, 80.5 wider than the box each side (the site photo shows the headboard standing out past
  the box). Model size [width, length, height] = [1813, 2109, 1050] / [2013, 2109, 1050].
- **Mirror 1.32**: B5 = a 4 mm mirror with R30 corners and a 10 mm black edge (the cut-out) — built as the mirror
  (z 0–4) and a 1 mm black ring on its face (`shape: path`, outer and inner rounded rectangles) standing for the
  printed / framed border.
- **Shelf 0.51**: an oak back board 1441 × 250 (50.5 in from the shelf's ends), the shelf 22 thick at 22–44 in front of
  it over the full 1542, and above the shelf a black board applied on the back's right part (1016–1491.5) with 4 slats
  (the site's front-on photo: below the shelf the back is oak everywhere).

## Finish (one colour option «Дуб Наварра», `deko-navarra`)
- body / front / back: «Дуб Наварра» provisional `door_enamel_whitey#956b40` — the p. 74 swatch
  (`catpage.py 74 --swatch 0.715,0.86,0.772,0.908`, flat ±10). Textured decor → `gen/deko_decors.md`.
- `accent` (the black boards of the slatted fronts, the wardrobe plinth): `door_enamel_whitey#312821` — the flat black
  door of 0.05 in the p. 74 living-room photo (`--swatch 0.4475,0.36,0.458,0.52`, flat ±2.5; 0.33's reads #372f24).
  It is a warm near-black ЛДСП, not the bluish «Антрацит» of other collections; the site names no colour for it.
- `slat` (birch slats, the bed slats): `door_enamel_whitey#8b653e` — a slat in the p. 74 close-up
  (`--swatch 0.3352,0.72,0.3398,0.865`); the solid birch reads a little darker than the ЛДСП in every photo.
- `fabric` (headboard): `velvet#16110e` — p. 73 (`--swatch 0.16,0.435,0.3,0.47`).
- `metal`: black (pulls, legs, glazed-door frames). Glass: bronze tint. Rails / tracks: chrome.

## Decisions / sizes
- index.json's entry БМ2.776.1.30 has a garbled name (the "check" flag); p. 74 reads «Тумба прикроватная «Деко»
  БМ2.776.1.30-01 (БМ2.776.1.30): L481×B460×H466» — size right. **1.30-01 = slats on the left** (the one the catalogue
  pictures and captions: p. 73 lists only 1.30-01, the p. 74 cut-out next to that code, the site's main photos);
  **1.30 = slats on the right** (the mirror; the site's «6T3A7601-kopiya-2» is the same photo flipped, the site offers
  «Левостороннее / Правостороннее»). If the lead knows Pinskdrev's convention the other way, swap the two ids.
- БМ2.776.1.32 Зеркало (p. 74) is not in index.json — added (deko-1-32).
- The p. 74 cut-out of 0.05 shows a diamond wine rack and a box in the glazed part: props / accessories, not built (the
  product photos show an empty vitrine with one glass shelf).
- Catalogue sizes agree with p. 72–74 for every code. Bed width: catalogue B1813 vs site «2109x1652» — read as headboard
  vs box (above).
- Inner sizes are measured off photos and 300–400 dpi cut-outs: ±5–10 mm on joints and slats, ±20 mm on hidden
  interiors; the overall sizes are exact.

## Engine / checker limits for the lead
- **Edge pull in preview2d**: its box counts `standoff + t` (20 mm) out of the face, hence the «примечание габарит B …
  только из-за ручек» on 0.05 / 0.06 / 0.33 / 0.34 / 1.30 / 1.31; the engine's pull stands 2 mm out. `dir: "down"` on the
  edge pulls is only for preview2d (the engine ignores it), so the pull's box stays inside the front.
- **Sliding door over hinged doors** (wardrobes): nothing stops the mirror doors from being opened while the slatted
  door is slid over them (they would swing through it) — the moves are independent.
- **Lift bed**: no move for a lifting horizontal frame (a `flap` about an x axis at the head end, lifting the foot, would
  do); the gas struts and hinges are not modelled.
- **Mirror border**: a 1 mm black ring (`shape: path` with a hole) in front of the mirror stands for a black edge that is
  really printed on / framed round the glass; preview2d draws the ring as its box (the sheet shows a black rectangle).
- Bedside: the oak panel is ЛДСП 16 on the black board, so its face is 4 mm behind the 20 mm slats (the photo cannot
  settle whether they are flush).
- preview2d draws finish roles `accent` / `slat` in the body colour and bar handles as discs; the legs are `rod`s (not
  drawn; only their glides show).

## Skipped
Nothing: the collection has no chairs or upholstered seating.
