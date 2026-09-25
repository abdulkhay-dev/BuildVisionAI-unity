# house-mcp

MCP-сервер приложения **House**. Через него любой ИИ-клиент с поддержкой MCP проектирует дом:
создаёт проект, стены, проёмы, комнаты, крыши, лестницы, расставляет мебель и видит результат
картинками (вид снаружи, план этажа, вид изнутри).

```
ИИ-клиент ⇄ MCP (stdio или HTTP) ⇄ house-mcp ⇄ http://127.0.0.1:<порт>/api (+токен) ⇄ приложение House
```

Вся логика — в приложении: сервер только описывает инструменты и пересылает вызовы.
Приложение при запуске пишет порт и токен в `~/.house-app/api.json`; сервер читает файл при каждом вызове,
поэтому перезапуск приложения не требует перезапуска сервера. **Приложение должно быть открыто.**

## Сборка

```bash
npm install
npm run build        # dist/index.js (справка по формату встраивается из ../Docs/house-format.md)
npm run smoke        # сквозная проверка через официальный MCP-клиент (нужно открытое приложение)
```

## Подключение

Ниже `/ABS/PATH` — абсолютный путь к этой папке.

**Claude Desktop** — `~/Library/Application Support/Claude/claude_desktop_config.json`
(Windows: `%APPDATA%\Claude\claude_desktop_config.json`):
```json
{ "mcpServers": { "house": { "command": "node", "args": ["/ABS/PATH/dist/index.js"] } } }
```

**Claude Code**:
```bash
claude mcp add house -- node /ABS/PATH/dist/index.js
```

**Cursor** (`~/.cursor/mcp.json`), **Windsurf** (`~/.codeium/windsurf/mcp_config.json`), **LM Studio** (`mcp.json`),
**Gemini CLI** (`~/.gemini/settings.json`) — тот же формат:
```json
{ "mcpServers": { "house": { "command": "node", "args": ["/ABS/PATH/dist/index.js"] } } }
```

**VS Code (Copilot)** — `.vscode/mcp.json` или пользовательские настройки:
```json
{ "servers": { "house": { "type": "stdio", "command": "node", "args": ["/ABS/PATH/dist/index.js"] } } }
```

**OpenAI Codex CLI** — `~/.codex/config.toml`:
```toml
[mcp_servers.house]
command = "node"
args = ["/ABS/PATH/dist/index.js"]
```

**Клиенты с подключением по URL** (Streamable HTTP):
```bash
node dist/index.js --http 47961     # → http://127.0.0.1:47961/mcp (только localhost)
```

**ChatGPT** подключает только публичные HTTPS-серверы, до `localhost` он не дотянется: нужен туннель
(например, cloudflared) — небезопасно без авторизации, поэтому по умолчанию не поддерживается.

## Инструменты

| инструмент | что делает |
|---|---|
| `house_guide` | справка по формату проекта и порядку работы |
| `house_status`, `house_list_projects` | состояние приложения, список проектов |
| `house_create_project`, `house_open_project`, `house_delete_project` | проекты (удаление — в корзину) |
| `house_get_project`, `house_summary`, `house_replace_project` | чтение и полная замена документа |
| `house_upsert`, `house_remove` | добавить/изменить/удалить элементы любого вида по id |
| `house_exterior_walls` | наружные стены по контуру |
| `house_validate`, `house_undo` | проверка, отмена (30 шагов) |
| `house_catalog`, `house_materials` | модели мебели и материалы (`имя#rrggbb` — оттенок) |
| `house_render` | картинка: `orbit` (снаружи), `plan` (план этажа), `walk` (изнутри) |

Каждое изменение отвечает `notes` (что сделано, неизвестные поля), `issues` (ошибки проверки) и
`buildWarnings` (предупреждения генератора) — модель видит последствия сразу.
