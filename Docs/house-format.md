# Формат проекта дома `house/1`

Файл `*.house.json` — единственный источник дома: из него приложение строит геометрию, свет,
участок и точки презентации. Его пишет ИИ через MCP. Примеры: `Assets/StreamingAssets/Samples/`
(`46-96.house.json` — двухэтажный дом с плоской кровлей, `barnhouse.house.json` — одноэтажный барнхаус).

## Соглашения

- Единицы — метры и градусы.
- Мир: X вправо, Y вверх (0 = уровень земли), Z «на север». Точка на плане — `[x, z]`, в пространстве — `[x, y, z]`.
- Повороты — вокруг вертикали, в градусах, как по компасу: 0 → +Z (север), 90 → +X (восток), 180 → −Z (юг), 270 → −X (запад). Для предмета (`rotation`) это направление, куда смотрит его перед; для лестницы (`direction`) — куда идёт первый марш; для камеры (`yaw`) — куда она смотрит.
- Всё необязательное имеет разумные значения по умолчанию. Короткий документ — нормально.
- Имена материалов не зависят от регистра и `_`: `oak_light` = `OakLight`.

## Корень

| поле | что |
|---|---|
| `format` | `"house/1"` |
| `meta` | `name`, `description`, `author`, `created`, `modified` |
| `site` | `landscape`: `garden` (газон, отмостка, дорожка, деревья) · `lawn` · `none` · `catalog4696`; `sunAzimuth` (откуда светит солнце, 0 = север, по часовой; 180 = юг), `sunElevation` |
| `levels` | этажи |
| `walls`, `openings` | стены и проёмы |
| `rooms` | комнаты (полы, потолки, свет, пробы отражений) |
| `roofs`, `stairs`, `elements` | крыши, лестницы, архитектурные элементы |
| `items`, `lights`, `views` | предметы каталога, источники света, точки презентации |

## Этажи — `levels`

`{ "id": "ground", "name": "1 этаж", "elevation": 0.3, "height": 2.8, "slab": 0.3 }`

- `elevation` — отметка чистого пола над землёй; `height` — высота до потолка; `slab` — толщина перекрытия **под** этим этажом.
- Этаж выше должен начинаться не ниже `elevation + height + slab` нижнего (иначе ошибка валидатора).

## Стены — `walls`

```json
{ "id": "front", "level": "ground", "a": [0, 0], "b": [12, 0], "outside": "wood", "plinth": 0.45 }
{ "id": "p1", "level": "ground", "kind": "interior", "a": [8, 0.4], "b": [8, 8.2] }
```

- Прямой отрезок `a → b` под любым углом.
- `kind`: `exterior` (по умолчанию) или `interior`. `system`: `masonry` или `steelGlass` (стальная остеклённая перегородка во всю стену; двери в ней — проёмы типа `door`).
- **Наружные стены перечисляй против часовой стрелки** (если смотреть сверху): линия `a→b` — наружная грань, тело стены лежит слева. Внутренние стены — по оси (`align: center`).
- `thickness`: по умолчанию 0.4 (наружные) / 0.12 (внутренние). `align`: `outer` · `center` · `inner`.
- `bottom`/`top` — абсолютные высоты. По умолчанию наружная стена идёт от земли (нижний этаж) до перекрытия следующего этажа или до `elevation + height + 0.3` на верхнем (там на неё ложится крыша, `roof.base` = этой высоте).
- Отделка снаружи `outside`: `stone`, `plinth`, `stucco`, `wood` (вертикальные рейки на чёрной подложке) или любой материал; внутри `inside` (по умолчанию `plaster`).
- `plinth`: высота цоколя. `zones`: участки другой отделки `{ "from", "to" (м от точки a), "bottom", "top" (абсолютно), "finish" }`.
- Углы: облицовка сама заворачивает на внешних углах соседних наружных стен; `wrapStart`/`wrapEnd` задают это явно.

## Проёмы — `openings`

```json
{ "id": "entry", "wall": "front", "type": "entryDoor", "at": 8.15, "width": 1.05, "sill": 0, "height": 2.3 }
```

- `at` — расстояние от точки `a` стены до края проёма; `sill` — низ проёма над полом этажа стены; `height`, `width`.
- `type`: `window` · `glazing` (витраж, толстый профиль) · `door` (внутренняя дверь, полотно из дуба) · `entryDoor` (стеклянная входная) · `solidDoor` (глухая) · `hole` (пустой проём).
- Окна: `columns` (импосты), `transoms` (высоты горизонтальных перемычек от низа проёма), `curtain`: `none` · `full` · `left` · `right`, `curtainFraction`.
- Двери: `hinge` (`start`/`end` — сторона петель), `swing` (+1 — открывается влево от `a→b`, т.е. внутрь для наружных стен; −1 — вправо). Двери открываются в приложении.

## Комнаты — `rooms`

```json
{ "id": "living", "name": "Гостиная", "level": "ground", "type": "living", "outline": [[0.4,0.4],[8,0.4],[8,8.2],[0.4,8.2]] }
```

- `outline` — многоугольник по внутренним граням стен (для смежных комнат — по оси перегородки, чтобы полы сошлись без щелей). Комнаты одного этажа **не должны перекрываться**.
- Комната даёт: плиту перекрытия с полом (`floor`, по умолчанию `oak`; санузлы/котельные — `tile`), потолок (`ceiling`), встроенные светильники (`downlights`: `auto` · `none`), пробу отражений (`probe`), мягкий свет, если в комнате нет явного источника.
- `height` больше высоты этажа = **второй свет**: над комнатой не должно быть комнаты верхнего этажа.
- Над лестницей тоже не должно быть комнаты верхнего этажа (валидатор проверит, хватает ли 2 м над ступенями).
- `type`: `living, kitchen, dining, bedroom, bathroom, hall, corridor, wardrobe, utility, office, stair, garage, terrace, other`.

## Крыши — `roofs`

```json
{ "id": "main", "type": "gable", "outline": [[0,0],[14,0],[14,8.6],[0,8.6]], "base": 3.55, "pitch": 35, "overhang": 0.5, "material": "coping", "gable": "wood" }
```

- `type`: `flat` (любой многоугольник, `parapet` — высота парапета) · `shed` · `gable` · `hip` (по охватывающему прямоугольнику контура в системе крыши; конёк вдоль локальной X, `rotation` поворачивает крышу).
- `base` — высота низа крыши на линии наружных стен (= верх стен). Крыша лежит на стенах, свес `overhang` опускается по уклону `pitch`.
- `thickness`, `material` (покрытие), `soffit` (подшивка), `gable` (отделка фронтонов: `wood` — вертикальная доска).

## Лестницы — `stairs`

```json
{ "id": "main", "type": "u", "from": "ground", "to": "upper", "start": [8.77, 6.75], "direction": 0, "width": 1.13, "going": 0.26, "risers": 19, "firstFlight": 11, "turn": "left", "gap": 0.07, "landing": 1.43 }
```

- `start` — низ первого марша по его оси; `direction` — направление подъёма первого марша (0 = +Z, 90 = +X).
- `type`: `straight` · `l` · `u`; `turn`: `left`/`right` — куда поворачивает второй марш; `firstFlight` — подступенков в первом марше; `landing` — глубина площадки.
- `style`: `floating_oak` (консольные дубовые ступени, стеклянное ограждение, подсветка) или `solid`.

## Элементы — `elements`

- `box`/`beam`/`platform`/`column`: `min`, `max` (абсолютные `[x,y,z]`), `material` (бока), `top`, `bottom` (`"none"` — без грани), `cap` (отлив сверху: `capHeight`, `capOverhang`). Так делаются пояса, козырьки, парапеты, террасы, ступени, колонны.
- `railing`: `path` (точки на плане), `y` (низ), `height`, `style`: `glass` (стеклянные панели с профилем) · `glass_oak` (цельное стекло с дубовым поручнем) · `metal`.
- `collide: false` — без коллайдера.

## Предметы — `items`

```json
{ "id": "sofa", "model": "sofa", "level": "ground", "position": [3.4, 0, 4.3], "rotation": 90, "params": { "length": 2.8, "fabric": "linen" } }
```

- `position`: X/Z на плане, Y — над полом `level` (без `level` — абсолютная высота). `rotation` — куда смотрит перед предмета (0 = +Z, 90 = +X).
- Встроенные вещи ставятся спинкой к стене: точка — у стены, перед — в комнату. Подвесы и люстры — точка на потолке (Y = высота этажа).
- Модели и параметры: см. `ItemCatalog.cs` (строка `Params` у каждой модели). Мебель: `sofa, armchair, lounge_chair, chaise_longue, dining_chair, bar_stool, bench, round_table, wire_table, dining_table, desk, wardrobe, fluted_cabinet, cubby_shelf, tv_console, media_wall, nightstand, bed`; кухня и ванная: `kitchen_base, tall_units, kitchen_island, vanity, toilet, bathtub, shower, towel_rail`; свет: `pendant_globe, linear_pendant, chandelier, table_lamp, floor_lamp, downlight, led_slot`; стены и текстиль: `slat_panel, artwork, mirror_round, rug, drapes, panel`; декор: `vase, books, twigs`; растения: `plant_tree, plant_grass`; прочее: `boiler, washer_stack, rattan_lounge_chair, bistro_set`.

## Свет — `lights`

`{ "id": "chandelier", "type": "point", "position": [7.06, 4.4, 2.2], "color": "warm", "intensity": 1.3, "range": 9, "shadows": true }`

- `type`: `point` · `spot` (`target`, `angle`). `color`: `warm` · `neutral` · `cool` · `fire` · `#rrggbb`. С `level` высота считается от пола этажа.

## Точки презентации — `views`

- `walk`: `position` (ноги), `yaw`, `pitch` — остановки экскурсии.
- `orbit`: `yaw`, `pitch`, `distance` — ракурсы вокруг дома. Без них приложение ставит стандартные.

## Материалы

Отделка и мебель: `stone, plinth, stucco, wood, plaster, ceiling, oak, oak_light, walnut, tile, tile_dark, marble, travertine, porcelain, step_riser, gravel, paver, coping, soffit, frame, steel, black_metal, brass, chrome, glass, gloss_white, linen, boucle, sage, terracotta, charcoal, bedding, leather, leather_white, rug, rug_dark, towel, ceramic, stoneware, mirror, led`.

## Проверка

`HouseValidator` возвращает ошибки и предупреждения на русском с путём к элементу (`openings/entry: проём выходит за стену…`) — их нужно исправить до сборки.
