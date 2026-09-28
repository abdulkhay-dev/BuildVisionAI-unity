# Finish and glass ids of the door catalogue

One list for every author (design files reference these ids; texture authors create them). Library material id =
`door_` + finish id with `-` → `_`; glass pictures / patterns = `doorglass_` + glass id with `-` → `_`; per-design art
glass = `doorglass_` + design id with `-` → `_`; painted ornaments (decals, e.g. SKINNY ART) = `doorart_` + design id
with `-` → `_`.
Finishes live in `Assets/House4696/Resources/Doors/catalog.json` (wave 1) and `…/Doors/Finishes/<family>.json`;
glass in `catalog.json` and `…/Doors/Glass/<family>.json`.

## Finishes

| family (file) | ids (catalogue name) |
|---|---|
| veralinga, 3d-graf (catalog.json) | cappuccino-veralinga, grey-veralinga, wenge-veralinga, bianco-veralinga, snow-veralinga, anegri-veralinga, golden-reef, 3d-cappuccino, 3d-grey, 3d-wenge |
| crosscut | cappuccino-crosscut, grey-crosscut, wenge-crosscut, bianco-crosscut |
| softwood | cappuccino-softwood, white-softwood |
| eco-oak (ЭкоШпон) | royal-oak, antique-oak, dark-oak, organic-oak, nordic-oak, original-oak, virgin, ivory, silver-ash (Silver Ash / Silver Rift), chalet-grande, chalet-grasse, chalet-provence, graphite-art |
| euro-oak (ЕвроШпон) | real-oak, milk-oak, brown-oak, thermo-oak |
| veneer (натуральный шпон Mr.Wood) | natur-oak, golden-oak, veneer-ivory, veneer-latte, veneer-whitey |
| fine-line (шпон файн-лайн) | f-01-oak (Ф-01 Дуб), f-11-walnut (Ф-11 Орех), f-15-makore (Ф-15 Макоре), f-17-chocolate (Ф-17 Шоколад), f-22-white-oak (Ф-22 БелДуб), f-27-wenge (Ф-27 Венге) |
| pvc (ПВХ) | p-23-white (П-23 Белый), p-34-shimo-light (П-34 Шимо Светлый), p-35-shimo-dark (П-35 Шимо Тёмный), p-17-italoreh (П-17 ИталОрех), p-18-milanoreh (П-18 МиланОрех), p-31-italoreh (П-31), p-32-milanoreh (П-32) |
| laminate (ламинат) | l-11-italoreh (Л-11 ИталОрех), l-12-milanoreh (Л-12 МиланОрех), l-13-wenge (Л-13 Венге), l-23-white (Л-23 Белый) |
| enamel (эмаль SKINNY) | enamel-whitey, enamel-cream, enamel-mocca |
| solid (массив) | solid-pine (без отделки) |
| two-tone (Finishes/two-tone.json, lead) | f-27-f-01 (Ф-27/Ф-01: finish = Ф-27 Венге, finish2 = Ф-01 Дуб), f-01-f-17 (Ф-01/Ф-17: finish = Дуб, finish2 = Шоколад) |
| entrance-metal | antik-silver (Антик Серебро), antik-copper (Антик Медь), moonstone (Лунный камень) |
| entrance-panel | winorit-p4 (П-4 Золотой дуб), winorit-p25 (П-25 Беленый дуб), winorit-p26 (П-26 Французский дуб), winorit-p28 (П-28 Тёмная вишня), almond-28 (Almond 28), graphite-pro (Graphite Pro) |

## Glass

| id | name | how |
|---|---|---|
| mf, tmf | Белое сатинато Magic Fog (MF), триплекс (TMF) | role satin |
| mf-diamond | Белое сатинато MF «Алмазная грань» (Classico) | role satin + facet 20 mm on shaped panes |
| bs | Чёрный Lacobel «Black Star» | role black |
| wp, ww, s | Lacobel «White Pearl» (бежевый), «White Waltz» (белый), «Smoke» (серый) | roles lacobel-beige / lacobel-white / lacobel-smoke |
| wc | Белое худож. сатинато White Crystal (ромбы) | material doorglass_wc (pattern) |
| sa | Зеркало белое худож. «Silver Art» | material doorglass_sa (fit) |
| reflex | Зеркало белое «Reflex» | role mirror |
| print, stamp | Зеркало чёрное худ. «Print», «Stamp» | materials doorglass_print / doorglass_stamp (fit) |
| crystalline | Crystalline просветлённое | role clear |
| mystic | Белое худож. «Mystic» | material doorglass_mystic |
| vitrazh | Белое сатинато «Витраж» | material doorglass_vitrazh |
| mirror-art | Зеркало белое худож-е (3D-Graf) | material doorglass_mirror_art |
| st-hud | «СТ-Худ.» — художественное стекло, СВОЁ у каждой модели (ПВХ, файн-лайн) | the design's glass parts use role `art:doorglass_<design id, - → _>` (picture per design); the model lists glass `st-hud` |
| st-118, st-121, zk-uzor | художественные стёкла СТ-118, СТ-121, ЗК-Узор (одинаковые у разных моделей) | materials doorglass_st_118 / doorglass_st_121 / doorglass_zk_uzor (fit); designs use role `glass` |
| bc | бронзовое худож. сатинато, ромбы (WOOD CLASSIC на тёмных отделках) | material doorglass_bc (pattern, like wc) |
| sprig, twig | стекло Глейс SPRIG / TWIG | materials doorglass_sprig / doorglass_twig (fit) |
