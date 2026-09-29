# «Челси Бум» (chelsi-bum) — 10 дизайнов (12 строк index.json): 7 по инструкции, 3 по фото

Catalogue p. 119–120 (spread 234–237); ЗАО «Холдинговая компания Пинскдрев», Городищенская фабрика. Generator
`gen/chelsi-bum.py`; the coupe wardrobes share `coupe()` / `coupe_doors()` in `gen/kit_w4k.py` with Соната Бум. All
check sheets ok (`pilot/chelsi-bum-1-03.png` also overlays the instruction's front view: the fronts, rails and the
накладка sit on the drawing).

## Sources
- П3.587.1.01 / П3.587.1.02 in index.json are the same articles as П3.0587.1.01 / .02 (the catalogue writes both codes):
  one design each (chelsi-bum-1-01 / 1-02).
- Instructions (a.pinskdrev.ru, no text layer): tables «поз., обозн., наименование, материал, кол-во, длина, ширина»
  read from the pictures → `gen/cutlists/chelsi-bum-1-0*.json` (with the decor of each part in the name).
- 1.08 шкаф-купе: the site's instruction link is the 1.01 wardrobe's PDF (same file) — built by photo (6T3A4798,
  6T3A4805/4806). 1.09 / 1.11 (3Д, 3Д with mirror): no photo, built as the 2Д widened.

## Construction
- Carcass ЛДСП 16 «Металл Бруклин 808» on 20 mm adjustable feet (1838 + 32 + 20 = 1890, 808 + 32 + 20 = 860); the
  bottom full width and depth, the sides on it (1 mm shallower), the top over them; ХДФ 3 backs in grooves joined on
  the fixed shelves (1.01: 282 + 1280 + 282 left, 3 × 614 right) and in the chest by the H-profile 25.
- Fronts ЛДСП 16 «Дуб Бордо» INSET, set back: in front of the partitions, which are 36–40 shallower than the sides
  (559 / 599, 463 / 499). The front-on site photo of the chest confirms the reveal round the recessed fronts.
- «Накладка двери» 180 (dark, top-right corner rounded r 170) on 16 mm spacer blocks «перемычка» over the door's
  meeting edge, moving with the door; it stands 7 (wardrobe) / 11 (chest) mm proud of the carcass. **The design sizes
  are B607 (1.01) and B511 (1.03)**; the catalogue's B600 / B500 is the carcass — noted in the models.
- 1.02 стеллаж: no top — the sides (rounded top-front corner, r 150 — the cover drawing) stand on the base, the back 4
  (Бордо, 1853) between them, five shelves.
- 1.04 стол (universal; built «L»): a shelf tower 224 wide — end panels 1 / 2 (976, the corner towards the desk
  rounded r 200), shelves 7 at 20 / 247 / 458, the closing panels 4 (211, lower cubby, desk side), 3 / 5 (264, the
  drawer zone, outer / inner) — the top 9 (1304) passes through the tower at 738…754; leg 6, back rail 8, one wide
  drawer 20 (1072) with two dividers 23. The partial walls are a reading of the exploded view (±).
- 1.05 кровать 1-09: along the wall (x = the length 2042, the catalogue's L980 × B2042): ends 980 × 583 with rounded tops,
  back rail 376, front rail 187, three base boards 666 on 16 МДФ posts 250 standing on two sills 84 (84 + 250 = 334 —
  the reading that makes the sizes add up), partition 5, two drawers 1001 on floor skids 26.
- 1.06 кровать раздвижная: upper ends 980 × 796, back 451, front 187, bases on 28 МДФ ribs; the trundle (castors h36):
  ends 924 × 356, back 1969 × 354, front 183, three ЛДСП 25 skids (14 / 18 / 19) carrying its base, two drawers on
  castors h28 between the skids (1969 − 3 × 25 = 2 × 947 = 921 + 2 × 13 ✓), the rails 17 over them.
- 1.07 полка: back 900 × 230 (Металл), plate 899 × 214 and a quarter-disc divider 198 (Бордо).
- Шкафы-купе: sides 16 to the floor, bottom on a 70 plinth, top between the sides, ХДФ back; two tracks in the front
  90; doors in aluminium frames (20 × 36 stiles, 30 rails) with a lower «Металл» panel 620 and an upper «Бордо» panel;
  2Д: left rail section + right shelves, 3Д: shelves / rail / shelves; 1.11 — the middle door a mirror.

## Finishes (p. 120 «Вариант цветового исполнения»)
- `chelsi-bum-metall-bordo`: body «Металл Бруклин 808» #4c4b51 (0.715,0.865,0.738,0.90), front «Дуб Бордо лайт 380»
  #cecece (0.749,0.865,0.772,0.90), role `white` (ЛДСП Белый shelves / drawer boxes, ХДФ). Both are textured decors —
  `gen/chelsi-bum_decors.md`. Metal `chrome` (rail, coupe frames).

## For the lead
- The накладка stands out of the catalogue depth (see above) — decide whether the model size should stay B607 / B511.
- The chest photo suggests the накладка is ≈ 225 wide, the tables say 180: built 180.
- Coupe doors: frame and panels are boxes; the tracks are plain boxes.
