#!/usr/bin/env node
// House MCP server. Transports:
//   stdio (default)        — for Claude Desktop, Cursor, VS Code, Codex, Gemini CLI, LM Studio, …
//   --http <port>          — Streamable HTTP on 127.0.0.1:<port>/mcp for clients that connect by URL
import { createServer } from "node:http";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { INSTRUCTIONS, registerTools } from "./tools.js";

const VERSION = "0.2.0";

function newServer(): McpServer {
  const server = new McpServer({ name: "house", title: "House — проектирование домов", version: VERSION }, { instructions: INSTRUCTIONS });
  registerTools(server);
  return server;
}

async function stdio(): Promise<void> {
  await newServer().connect(new StdioServerTransport());
  console.error(`house-mcp ${VERSION}: stdio`); // stdout is the protocol channel
}

/** Stateless Streamable HTTP: a fresh server per request, localhost only, foreign browser origins refused. */
function http(port: number): void {
  const httpServer = createServer(async (req, res) => {
    const origin = req.headers.origin;
    if (origin && !/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) {
      res.writeHead(403).end("forbidden origin");
      return;
    }
    if (!req.url?.startsWith("/mcp")) {
      res.writeHead(404).end("use /mcp");
      return;
    }
    if (req.method !== "POST") {
      res.writeHead(405, { Allow: "POST" }).end();
      return;
    }
    const server = newServer();
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
    res.on("close", () => {
      void transport.close();
      void server.close();
    });
    try {
      await server.connect(transport);
      await transport.handleRequest(req, res);
    } catch (e) {
      if (!res.headersSent) res.writeHead(500).end(String(e));
    }
  });
  httpServer.listen(port, "127.0.0.1", () => console.error(`house-mcp ${VERSION}: http://127.0.0.1:${port}/mcp`));
}

const i = process.argv.indexOf("--http");
if (i >= 0) http(Number(process.argv[i + 1] ?? 47961));
else await stdio();
