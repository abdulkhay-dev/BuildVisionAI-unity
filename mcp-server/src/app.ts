// Client of the House app's local API. The app publishes its port and token in ~/.house-app/api.json while it
// runs; every call re-reads the file, so restarting the app (new port/token) needs no MCP restart.
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export const DISCOVERY_FILE = process.env.HOUSE_APP_DISCOVERY ?? join(homedir(), ".house-app", "api.json");

interface Discovery {
  url: string;
  token: string;
  version?: string;
}

export class AppError extends Error {}

function discover(): Discovery {
  let raw: string;
  try {
    raw = readFileSync(DISCOVERY_FILE, "utf8");
  } catch {
    throw new AppError(
      "Приложение House не запущено (нет " + DISCOVERY_FILE + "). Попроси пользователя открыть приложение и повтори вызов.");
  }
  const d = JSON.parse(raw) as Discovery;
  if (!d.url || !d.token) throw new AppError("Файл " + DISCOVERY_FILE + " повреждён — перезапусти приложение.");
  return d;
}

/** Sends one command to the app and returns its result (throws AppError with the app's message on failure). */
export async function call<T = unknown>(command: string, args: Record<string, unknown> = {}, timeoutMs = 190_000): Promise<T> {
  const d = discover();
  let res: Response;
  try {
    res = await fetch(d.url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${d.token}` },
      body: JSON.stringify({ command, args }),
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (e) {
    throw new AppError(
      `Не удалось связаться с приложением House (${d.url}): ${(e as Error).message}. Проверь, что приложение открыто.`);
  }
  if (res.status === 401) throw new AppError("Приложение отклонило токен — оно было перезапущено; повтори вызов.");
  const body = (await res.json()) as { ok: boolean; result?: T; error?: string };
  if (!body.ok) throw new AppError(body.error ?? "ошибка приложения");
  return body.result as T;
}
