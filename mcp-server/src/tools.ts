// MCP tools of the House app. Every tool is a thin wrapper over one app command; the app validates, rebuilds the
// house and answers with notes, validation issues and generator warnings that the AI should act on.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { AppError, call } from "./app.js";
import { FORMAT_GUIDE } from "./guide.generated.js";

export const INSTRUCTIONS = `House — проектирование частных домов в приложении House (3D, реалистичная графика).
Порядок работы:
1) house_guide — прочитай формат проекта (один раз за сессию).
2) house_create_project (или house_list_projects + house_open_project).
3) Этажи (house_upsert kind=level) → наружные стены по контуру (house_exterior_walls) → перегородки и проёмы (house_upsert wall/opening; межкомнатные двери — модели из house_doors, размер полотна leaf) → комнаты (room) → крыша/лестница/элементы → мебель (item, см. house_catalog) → свет и точки показа.
4) Каждый ответ на правку содержит issues: ошибки и предупреждения ПО ПОСТРОЕННОМУ дому (мебель в стене или в проходе, дверь в обрыв, проём выше стены или в углу, крыша сквозь комнату, лестница в стену, комната без крыши) — с готовым исправлением. Исправляй их сразу, до следующего шага.
5) Не считай геометрию в уме: house_inspect даёт реальные числа (верх стен, проёмы в координатах, карниз и конёк крыши, габарит и проём лестницы, размеры предметов). house_catalog даёт реальные размеры моделей.
6) Проверяй глазами: house_render (orbit — снаружи, plan — план этажа, walk — вид изнутри).
Координаты в метрах: X вправо (восток), Z на север, Y вверх; точки плана [x, z]. Правки частичные: house_upsert с тем же id меняет только переданные поля. Ошибся — house_undo.`;

const KINDS = ["level", "wall", "opening", "room", "roof", "stair", "element", "item", "light", "view", "meta", "site"] as const;

const point2 = z.tuple([z.number(), z.number()]);

/** JSON for a model to read: objects indented, arrays of numbers (points, sizes) on one line — far fewer tokens. */
export function compact(value: unknown, indent = ""): string {
  if (Array.isArray(value)) {
    if (value.every((v) => v === null || typeof v !== "object" || (Array.isArray(v) && v.every((x) => typeof x !== "object"))))
      return JSON.stringify(value);
    const inner = indent + "  ";
    return "[\n" + value.map((v) => inner + compact(v, inner)).join(",\n") + "\n" + indent + "]";
  }
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) return "{}";
    const inner = indent + "  ";
    return "{\n" + entries.map(([k, v]) => inner + JSON.stringify(k) + ": " + compact(v, inner)).join(",\n") + "\n" + indent + "}";
  }
  return JSON.stringify(value);
}

function text(value: unknown): CallToolResult {
  return { content: [{ type: "text", text: typeof value === "string" ? value : compact(value) }] };
}

/** Runs an app command and turns app errors into tool errors the model can read and fix. */
async function run(command: string, args: Record<string, unknown> = {}): Promise<CallToolResult> {
  try {
    return text(await call(command, args));
  } catch (e) {
    const msg = e instanceof AppError ? e.message : `Внутренняя ошибка: ${(e as Error).message}`;
    return { content: [{ type: "text", text: msg }], isError: true };
  }
}

const readOnly = { readOnlyHint: true, openWorldHint: false } as const;
const edit = { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false } as const;

export function registerTools(server: McpServer): void {
  server.registerTool("house_guide", {
    title: "Формат проекта дома",
    description: "Справка по формату проекта (house/1): этажи, стены, проёмы, комнаты, крыши, лестницы, элементы, мебель, свет, материалы, соглашения о координатах и поворотах. Прочитай перед первым изменением.",
    annotations: readOnly,
  }, async () => text(INSTRUCTIONS + "\n\n" + FORMAT_GUIDE));

  server.registerTool("house_status", {
    title: "Состояние приложения",
    description: "Открытый проект, число проблем, глубина отмены, доступные шаблоны. Заодно проверяет, что приложение запущено.",
    annotations: readOnly,
  }, async () => run("status"));

  server.registerTool("house_list_projects", {
    title: "Список проектов",
    description: "Все проекты пользователя: id, название, описание, этажи, комнаты, площадь, дата изменения.",
    annotations: readOnly,
  }, async () => run("list_projects"));

  server.registerTool("house_create_project", {
    title: "Создать проект",
    description: "Создаёт проект и открывает его. template: 'empty' (один этаж 'ground', без стен) или имя примера из house_status.samples (например '46-96', 'barnhouse') как основа для правок.",
    inputSchema: {
      name: z.string().describe("Название дома"),
      description: z.string().optional().describe("Короткое описание"),
      template: z.string().optional().describe("'empty' (по умолчанию) или имя примера"),
    },
    annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false },
  }, async (a) => run("create_project", a));

  server.registerTool("house_open_project", {
    title: "Открыть проект",
    description: "Делает проект текущим: все остальные инструменты работают с ним.",
    inputSchema: { project_id: z.string() },
    annotations: edit,
  }, async (a) => run("open_project", { id: a.project_id }));

  server.registerTool("house_delete_project", {
    title: "Удалить проект",
    description: "Перемещает проект в корзину приложения (его можно восстановить вручную). Только по явной просьбе пользователя.",
    inputSchema: { project_id: z.string(), confirm: z.literal(true).describe("Подтверждение: пользователь просил удалить") },
    annotations: { readOnlyHint: false, destructiveHint: true, openWorldHint: false },
  }, async (a) => run("delete_project", { id: a.project_id }));

  server.registerTool("house_get_project", {
    title: "Документ проекта",
    description: "Полный JSON проекта (текущего или указанного). Для обзора дешевле house_summary.",
    inputSchema: { project_id: z.string().optional() },
    annotations: readOnly,
  }, async (a) => run("get_project", { id: a.project_id }));

  server.registerTool("house_summary", {
    title: "Сводка проекта",
    description: "Кратко: габариты, этажи, стены с длинами и проёмами, комнаты с площадями, крыши, лестницы, счётчики.",
    annotations: readOnly,
  }, async () => run("summary"));

  server.registerTool("house_replace_project", {
    title: "Заменить проект целиком",
    description: "Записывает весь документ house/1 (как вернул house_get_project, с правками). Удобно для крупных перестроек; для точечных правок используй house_upsert.",
    inputSchema: { document: z.record(z.string(), z.any()).describe("Полный документ проекта house/1") },
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: false },
  }, async (a) => run("replace_project", { document: a.document }));

  server.registerTool("house_upsert", {
    title: "Добавить или изменить элементы",
    description: "Добавляет или обновляет элементы одного вида по id (view — по name). Если id уже есть, меняются только переданные поля. " +
      "kind: level | wall | opening | room | roof | stair | element | item | light | view, либо meta/site (объект). " +
      "data — объект или массив объектов в формате house/1 (см. house_guide). Ответ содержит notes (в т.ч. предупреждения о неизвестных полях), issues и buildWarnings.",
    inputSchema: {
      kind: z.enum(KINDS),
      data: z.union([z.record(z.string(), z.any()), z.array(z.record(z.string(), z.any()))]),
    },
    annotations: edit,
  }, async (a) => run("upsert", { kind: a.kind, data: a.data }));

  server.registerTool("house_remove", {
    title: "Удалить элементы",
    description: "Удаляет элементы вида kind по id. Удаление стены удаляет её проёмы, удаление этажа — всё на нём.",
    inputSchema: { kind: z.enum(KINDS.filter((k) => k !== "meta" && k !== "site") as [string, ...string[]]), ids: z.array(z.string()).min(1) },
    annotations: { readOnlyHint: false, destructiveHint: true, openWorldHint: false },
  }, async (a) => run("remove", { kind: a.kind, ids: a.ids }));

  server.registerTool("house_exterior_walls", {
    title: "Наружные стены по контуру",
    description: "Создаёт наружные стены по контуру дома (точки наружных углов [x, z], в любом порядке обхода — будет приведён против часовой). Стена i идёт от точки i к точке i+1; id = prefix+номер (w1, w2, …). Повторный вызов с тем же prefix заменяет стены.",
    inputSchema: {
      outline: z.array(point2).min(3).describe("Наружные углы дома [[x, z], …]"),
      level: z.string().optional().describe("Этаж (по умолчанию первый)"),
      prefix: z.string().optional().describe("Префикс id, по умолчанию 'w'"),
      thickness: z.number().optional().describe("Толщина, м (по умолчанию 0.4)"),
      outside: z.string().optional().describe("Отделка снаружи: stone, plinth, stucco (тёмная), wood (рейки), render#rrggbb (светлая штукатурка) …"),
      plinth: z.number().optional().describe("Высота цоколя, м"),
    },
    annotations: edit,
  }, async (a) => run("exterior_walls", a));

  server.registerTool("house_validate", {
    title: "Проверить проект",
    description: "Проблемы проекта (ошибки и предупреждения с путём к элементу) и предупреждения генератора.",
    annotations: readOnly,
  }, async () => run("validate"));

  server.registerTool("house_undo", {
    title: "Отменить",
    description: "Отменяет последнее изменение проекта (до 30 шагов).",
    annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false },
  }, async () => run("undo"));

  server.registerTool("house_catalog", {
    title: "Каталог моделей",
    description: "Модели мебели, сантехники, света, декора и растений для items: id, название, категория, параметры со значениями по умолчанию, " +
      "реальный размер size [ширина, глубина, высота], fromOrigin — сколько предмет занимает от точки position в каждую сторону, и note — куда ставить точку и как повёрнут. " +
      "Без фильтра список длинный — лучше указывай category или id.",
    inputSchema: {
      category: z.string().optional().describe("seating, tables, storage, bedroom, kitchen, bath, lighting, walls, textiles, decor, plants, utility, outdoor"),
      id: z.string().optional().describe("Одна модель по id"),
    },
    annotations: readOnly,
  }, async (a) => run("catalog", a));

  server.registerTool("house_doors", {
    title: "Каталог дверей",
    description: "Двери из каталога производителя (el'PORTA / BRAVO, ~50 серий): межкомнатные (распашные, купе, книжки, порталы, готовые блоки) " +
      "и входные стальные. Без фильтра — обзор серий с моделями; цвета (finishes), стёкла и размеры — с фильтром series или id модели. " +
      "Дверь ставится проёмом type door с полями model, finish, glass и leaf [ширина, высота] — проём в стене посчитается из полотна сам; " +
      "у входных ещё finishIn (внутренняя панель), leaf = размер блока. " +
      "Строится весь дверной блок (коробка, доборы, наличники или классический портал, петли, ручки); двери открываются в приложении.",
    inputSchema: {
      series: z.string().optional().describe("id серии (например eco-porta-x)"),
      id: z.string().optional().describe("Одна модель по id (например porta-22)"),
    },
    annotations: readOnly,
  }, async (a) => run("doors", a));

  server.registerTool("house_materials", {
    title: "Материалы",
    description: "Материалы для отделки и параметров мебели. library — реалистичные материалы-сканы с названием и категорией " +
      "(floor, tile, wall, fabric, leather, carpet, wood, facade, roof, metal, paving, deck, ground); basic — встроенная палитра. " +
      "Любой можно окрасить: 'имя#rrggbb' (например 'velvet#6b4f3a', 'render#e8e2d6'). " +
      "У моделей из каталога параметры — слоты материалов (upholstery, legs, …): материал, '#rrggbb' (подкрасить родной) или 'original'. " +
      "Список длинный — указывай category.",
    inputSchema: { category: z.string().optional().describe("Категория library: floor, tile, wall, fabric, leather, carpet, wood, facade, roof, metal, paving, deck, ground") },
    annotations: readOnly,
  }, async (a) => run("materials", a));

  server.registerTool("house_inspect", {
    title: "Геометрия построенного дома",
    description: "Реальные числа построенного дома вместо расчётов в уме: этажи (пол, потолок), стены (концы, толщина, низ и верх, куда смотрят, " +
      "проёмы в координатах и по высоте, свободные участки), комнаты (площадь, границы), крыши (base, карниз, конёк, куда поднимается скат), " +
      "лестницы (число и высота ступеней, габарит маршей, проём в перекрытии, линия схода), предметы (реальный размер, высоты, пятно на плане), элементы. " +
      "Все высоты абсолютные (над землёй).",
    inputSchema: {
      section: z.enum(["levels", "walls", "rooms", "roofs", "stairs", "items", "elements"]).optional().describe("Раздел; без него — всё"),
      id: z.string().optional().describe("Только элемент с этим id"),
    },
    annotations: readOnly,
  }, async (a) => run("inspect", a));

  server.registerTool("house_render", {
    title: "Показать дом",
    description: "Рендер текущего дома в приложении — картинка, чтобы проверить результат. " +
      "mode=orbit: вид снаружи (yaw — откуда смотрим по компасу: 0 — с юга на север, 90 — с запада; pitch — наклон вниз; distance 0 = вписать дом). " +
      "mode=plan: план этажа сверху (level), потолки и верхние этажи скрыты. " +
      "mode=walk: вид изнутри с высоты глаз (position [x, z] + level или [x, y, z]; yaw — куда смотрим: 0 = +Z/север, 90 = +X/восток).",
    inputSchema: {
      mode: z.enum(["orbit", "plan", "walk"]).default("orbit"),
      yaw: z.number().optional(),
      pitch: z.number().optional(),
      distance: z.number().optional(),
      position: z.array(z.number()).min(2).max(3).optional(),
      level: z.string().optional(),
      width: z.number().int().min(256).max(2048).optional(),
      height: z.number().int().min(256).max(2048).optional(),
      fov: z.number().optional(),
    },
    annotations: readOnly,
  }, async (a) => {
    try {
      const r = await call<{ png: string; width: number; height: number; mode: string }>("render", { ...a, width: a.width ?? 1024, height: a.height ?? 640 });
      return {
        content: [
          { type: "image", data: r.png, mimeType: "image/png" },
          { type: "text", text: `${r.mode} ${r.width}×${r.height}` },
        ],
      };
    } catch (e) {
      return { content: [{ type: "text", text: (e as Error).message }], isError: true };
    }
  });
}
