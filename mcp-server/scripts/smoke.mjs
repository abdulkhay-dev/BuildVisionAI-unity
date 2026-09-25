// End-to-end check over stdio with the official MCP client, the way desktop AI clients connect:
// lists tools, builds a small house step by step and saves the renders to ./smoke-out/.
import { mkdirSync, writeFileSync } from "node:fs";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const out = new URL("../smoke-out/", import.meta.url);
mkdirSync(out, { recursive: true });

const client = new Client({ name: "house-smoke", version: "1.0.0" });
// HOUSE_MCP_BIN=/path/to/house-mcp tests the single-executable build (e.g. the one inside House.app)
const bin = process.env.HOUSE_MCP_BIN;
await client.connect(new StdioClientTransport(bin ? { command: bin, args: [] } : { command: process.execPath, args: [new URL("../dist/index.js", import.meta.url).pathname] }));

const { tools } = await client.listTools();
console.log(`tools (${tools.length}): ${tools.map((t) => t.name).join(", ")}`);
console.log(`instructions: ${(client.getInstructions() ?? "").slice(0, 80)}…`);

async function tool(name, args = {}) {
  const r = await client.callTool({ name, arguments: args });
  const txt = r.content.filter((c) => c.type === "text").map((c) => c.text).join("\n");
  for (const [i, c] of r.content.entries())
    if (c.type === "image") writeFileSync(new URL(`${name}-${Date.now()}-${i}.png`, out), Buffer.from(c.data, "base64"));
  console.log(`\n# ${name}${r.isError ? " (ERROR)" : ""}\n${txt.slice(0, 700)}`);
  return r;
}

await tool("house_status");
const created = await tool("house_create_project", { name: "Дом у озера", description: "smoke test: 10×8, двускатная крыша" });
const projectId = JSON.parse(created.content[0].text).project;
await tool("house_upsert", { kind: "level", data: { id: "ground", elevation: 0.45, height: 2.9, slab: 0.45 } });
await tool("house_exterior_walls", { outline: [[0, 0], [10, 0], [10, 8], [0, 8]], outside: "render#e9e4da", plinth: 0.45 });
await tool("house_upsert", {
  kind: "wall", data: [
    { id: "p1", level: "ground", kind: "interior", a: [6, 0.4], b: [6, 7.6] },
    { id: "p2", level: "ground", kind: "interior", a: [6, 4], b: [9.6, 4] },
  ],
});
await tool("house_upsert", {
  kind: "opening", data: [
    { id: "entry", wall: "w1", type: "entryDoor", at: 6.6, width: 1.1, sill: 0, height: 2.3 },
    { id: "living", wall: "w1", type: "glazing", at: 0.8, width: 4.2, sill: 0, height: 2.5, columns: 3 },
    { id: "side", wall: "w4", at: 2.0, width: 3.0, sill: 0, height: 2.5, type: "glazing", columns: 2 },
    { id: "bed_win", wall: "w2", at: 5.0, width: 1.4, sill: 0.8, height: 1.5 },
    { id: "d1", wall: "p1", type: "door", at: 1.2, width: 0.9, sill: 0, height: 2.1 },
    { id: "d2", wall: "p1", type: "door", at: 5.0, width: 0.9, sill: 0, height: 2.1 },
  ],
});
await tool("house_upsert", {
  kind: "room", data: [
    { id: "living", name: "Гостиная-кухня", level: "ground", type: "living", outline: [[0.4, 0.4], [6, 0.4], [6, 7.6], [0.4, 7.6]] },
    { id: "hall", name: "Прихожая", level: "ground", type: "hall", floor: "tile", outline: [[6, 0.4], [9.6, 0.4], [9.6, 4], [6, 4]] },
    { id: "bed", name: "Спальня", level: "ground", type: "bedroom", outline: [[6, 4], [9.6, 4], [9.6, 7.6], [6, 7.6]] },
  ],
});
await tool("house_upsert", { kind: "roof", data: { id: "roof", type: "gable", outline: [[0, 0], [10, 0], [10, 8], [0, 8]], base: 3.65, pitch: 30, overhang: 0.6, rotation: 90, gable: "wood" } });
await tool("house_catalog", { category: "seating" });
await tool("house_upsert", {
  kind: "item", data: [
    { id: "sofa", model: "sofa", level: "ground", position: [3.0, 0, 4.0], rotation: 270, params: { length: 2.6, fabric: "linen" } },
    { id: "rug", model: "rug", level: "ground", position: [1.9, 0, 4.0], params: { width: 2.2, depth: 2.8 } },
    { id: "bed", model: "bed", level: "ground", position: [7.8, 0, 7.54], rotation: 180, params: { width: 1.6, length: 2.0 } },
    { id: "kitchen", model: "kitchen_base", level: "ground", position: [5.94, 0, 6.2], rotation: 270, params: { length: 2.4 } },
  ],
});
await tool("house_upsert", { kind: "opening", data: { id: "entry", width: 1.2, heigth: 2.4 } }); // deliberate typo
await tool("house_validate");
await tool("house_summary");
await tool("house_render", { mode: "orbit", yaw: 25, pitch: 12 });
await tool("house_render", { mode: "plan" });
await tool("house_render", { mode: "walk", position: [9.0, 1.0], level: "ground", yaw: 300 });
await tool("house_undo");
await tool("house_delete_project", { project_id: projectId, confirm: true }); // keep the user's list clean
await client.close();
console.log("\nrenders saved to", out.pathname);
