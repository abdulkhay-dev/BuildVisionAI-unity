# Cloud waves — Pinskdrev «Корпусная мебель ч. II»

Each wave is one cloud session (claude.ai/code, repo abdulkhay-dev/BuildVisionAI-unity, base branch `casegoods`), given
this task text:

> Read `tools/casegoods/BRIEF.md` and do wave N of `tools/casegoods/WAVES.md`. Branch `casegoods-wN`, push it.

Counts are articles of `reference/index.json` (colour variants are finishes, not designs). The session may split its
collections between subagents (one per collection; they must not edit catalog.json at the same time — let each write
`tools/casegoods/gen/<slug>_catalog.json` and merge them at the end).

| wave | branch | collections (slug) | articles |
|---|---|---|---|
| 1 modern | casegoods-w1 | Шарли (sharli), Тринити (triniti), Рокси (roksi), Наполи (napoli), Эрида (erida), Скай (skay), Агата (agata), Ариста (arista), Денвер (denver), Джио (djio), Кен (ken), Марлен (marlen), Скарлетт (skarlett), Стамбул (stambul) | 126 |
| 2 loft | casegoods-w2 | Монако (monako), Лайн (layn), Форте Лофт (forte-loft), Деко (deko), Блэквуд Лофт (blekvud-loft), Норд Лофт (nord-loft), Каньон Лофт (kanon-loft), Хольтен Лофт (holten-loft) | 159 |
| 3 classic | casegoods-w3 | Сати (sati), Шанталь (shantal), Мартина (martina), Сорбонна (sorbonna), Парма (parma), Турин (turin), Гранде (grande), Элиза (eliza) | 136 |
| 4 oak & pine, youth | casegoods-w4 | Ирвинг (irving), Боро, Ардо (ardo), Гресс (gress), Юнона Лайт (yunona-layt), Сорренто (sorrento), Брауни (brauni), Вена (vena), Призма Нью (prizma-nyu) | 115 |
| 5 kids, hall, tables | casegoods-w5 | Челси Бум (chelsi-bum), Луна (luna), Линель (linel), Соната Бум, Бритиш Бум, Акцент (aktsent), Симпл, Верес (veres), Визит (vizit), Формат, Глобус, Мокко (mokko), tables: Лари, Мюнхен, Плато, Оскар | 123 |
| 6 decors | casegoods-w6 | the textured decors of `decors.md` (after waves 1–5): textures + library entries, like `tools/doors/BRIEF-textures.md` | — |

Collections without a slug have no collection page on the site: their articles in index.json may still carry `pdf`
(found by the code in the site map); if not, design them from the catalogue pages alone and say so in the notes.
