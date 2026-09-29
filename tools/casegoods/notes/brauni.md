# «Брауни» (brauni, П7.043) — notes

Catalogue «Корпусная мебель ч. II» 2025, PDF p. 114 (printed 224–225): a bedroom photo (wardrobe, chest, mirror, bed,
bedside tables, bench), the module cut-outs with sizes, the wardrobe's interior sketch, the swatch «Дуб Каньон» /
«Черный». No instructions. The site (pinskdrev.by/collections/brauni/) lists only the section П7.043.1.21 (043.201,
two front-on photos), the mirror П7.043.1.41 (043.401, a front-on photo) and other mirrors / a shoe cabinet not in this
catalogue; guessed URLs for the wardrobe, chest, bedside table and bed return 404. So **all 6 modules are by
catalogue** (1.21 and 1.41 also by the site photos).

Generator `tools/casegoods/gen/brauni.py` (re-runnable: 6 designs + `gen/brauni_catalog.json`); decors
`gen/brauni_decors.md`; sheets `pilot/brauni-*.png` — all 6 print `ok`.

## Construction
- ЛДСП 16 «Дуб Каньон»: sides to the floor, tops over the sides, bottoms on a front plinth; backs ХДФ in grooves
  (z 6…9.5, role `back` = «Черный», so the open niches show black backs as in the photos).
- «Черный» (role `accent`): the coupe doors' panels, the chest's top and its door, the chest's niche back, the bed
  plinth.
- Handles: black bar handles (224 bedside, 256 chest drawers, 192 chest door); 1.21 has none (grip gaps).

## Modules
| id | code | construction | overlay reference |
|---|---|---|---|
| brauni-1-11 | П7.043.1.11 Шкаф-купе 2д 2000×610×2332 | top over the sides, sides to the floor, bottom at 90 on a front plinth (+ a rear plinth rail), a middle partition; aluminium tracks (top 20, bottom 6); two coupe doors ~1000 (rear track left, front track right, 32 overlap) in silver side profiles 20: a Каньон stile 320 at the outer edge + «Черный» panels over and under a Каньон band 311 (y 1050…1361) — measured on the p. 114 cut-out; `slide` moves ±940. Inside (p. 114 sketch): left two shelves over a hanging rail (the section 1.21 stands at its bottom), right four shelves over a short hanging rail | p. 114 cut-out |
| brauni-1-21 | П7.043.1.21 Тумба (секция нижняя) 500×480×670 | stands in the wardrobe's left compartment, tied to it (p. 114 text): sides to the floor, top over them, three overlay drawer fronts 188 with 31 mm grip gaps above each (no handles) | site front photo |
| brauni-1-23 | П7.043.1.23 Тумба прикроватная 402×350×500 | index name «Брауни» fixed to «Тумба прикроватная «Брауни»»; sides to the floor, front plinth 60, an inset drawer 238 with a bar handle, an open niche (black back) over it | bedroom photo p. 114 (perspective: rough) |
| brauni-1-31 | П7.043.1.31 Комод 1604×436×1065 | a chest 1322 wide × 436 deep × 896 (four Каньон drawers 197, a «Черный» door 496 hinged right, a «Черный» top) in front of a frame 336 deep: an open three-cell column 282 wide on the left (black back), a Каньон top board over the full width at 1065, a right upright over the chest top, an open niche with a «Черный» back (the chest-in-front reading: the p. 114 cut-out shows the chest standing lower = nearer, the room photo shows the upright's side face narrower than the chest's) | p. 114 cut-out |
| brauni-1-41 | П7.043.1.41 Зеркало (wall) | a Каньон board 1000 × 600 × 16 with the mirror 800 × 524 × 4 on it (margins 100 / 38, the site photo) | p. 114 cut-out |
| brauni-1-08 | П7.043.1.08 Кровать 2-16, 1678 × 2058 × 1020, сп. место 2000×1600 | Каньон headboard 22 × 1020 to the floor with a black buttoned soft panel 390 high over its top (`soft`, tufts [10, 1]: one row of buttons with channels, room photo); side rails and foot 22 × 272 at y 100…372 (foot over the rails' ends: 22 + 2014 + 22 = 2058); a «Черный» plinth 100 set 140 in from the sides and 60 from the foot, with a middle beam; a storage bottom 16 in the box; the lifting metal frame 1600 × 2000 (black tubes, a middle beam), slats, a mattress 200 | p. 114 cut-out (perspective: rough) |

Skipped: **П7.043.1.81 Скамья** (an upholstered bench with a lifting soft lid — seating, out of the case-furniture scope).

## Finish
`brauni-kanon-black` «Дуб Каньон / Черный» (the only colour option):
- body and front «Дуб Каньон» #856649 — p. 114 swatch, `catpage.py 114 --swatch 0.792,0.885,0.817,0.908`,
  **provisional** (decor; the site swatch reads #a7876d under brighter light);
- `accent` and `back` «Черный» #1c1d18 — `--swatch 0.826,0.885,0.851,0.908`. It is **not a plain colour**: the
  catalogue and the site swatch show a dark woodgrain with fine lengthwise lines → listed as a decor, provisional
  colour;
- `fabric` (the headboard's soft panel) `velvet#1f1f1f` — black upholstery (it may be eco-leather; the photos do not
  tell);
- metal: black (bar handles); the coupe profiles and tracks use `chrome` (silver aluminium in the photos); the bed's
  metal frame `black`.
Both decors are in `gen/brauni_decors.md`.

## Size / data decisions
- **Mirror 1.41:** index.json and the site: L1000 × B20 × H600; p. 114 prints L1000xB20xH600 at the cut-out and
  L600xB20xH1000 in the text under the photo, and says it hangs either way. **Built landscape [1000, 20, 600]**
  (index / site / module list); the model note says it can hang upright.
- Bed: catalogue L1678 × B2058 — stored as [1678 (width), 2058 (length), 1020].
- 1.21: its catalogue height 670 fits the wardrobe's left compartment (bottom at 106, first shelf at 1782).

## Engine limits for the lead
- The bed's lifting mechanism (gas struts, frame hinged at the foot) is not modelled as a move — the frame, slats and
  mattress are static.
- Coupe doors: side profiles are panels in `chrome`; the top / bottom horizontal profiles of the doors are not built.
- preview2d draws bar handles as discs (the extent «примечание» on 1.23 / 1.31 is only the handles standing out of B).
