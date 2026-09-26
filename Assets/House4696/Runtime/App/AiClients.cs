using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// How AI clients reach the app: the MCP server that ships with it (inside the bundle in a build, the Node
    /// script in the repo in the editor) and per-client connection snippets. Clients with a JSON config file in a
    /// known place can be connected with one click: the <c>house</c> entry is merged in, everything else in the
    /// file is kept and the previous file is backed up next to it.
    /// </summary>
    public static class AiClients
    {
        public const string ServerName = "house";

        public enum Link { NotInstalled, Missing, Connected, Different }

        public sealed class Client
        {
            public string Id, Name, Hint;
            /// <summary>Config file for one-click connection (null: copy the snippet by hand).</summary>
            public string ConfigPath;
            /// <summary>Snippet shown to the user (JSON, TOML or a shell command).</summary>
            public Func<string> Snippet;

            /// <summary>The client looks installed (its config folder exists).</summary>
            public bool Installed => ConfigPath != null && Directory.Exists(Path.GetDirectoryName(ConfigPath));
            public bool CanAutoConnect => ConfigPath != null;
        }

        /// <summary>Command that starts the MCP server over stdio.</summary>
        public static (string command, string[] args) ServerCommand()
        {
            if (Application.isEditor)
            {
                string script = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "mcp-server", "dist", "index.js"));
                return (NodePath(), new[] { script });
            }
            string exe = Application.platform == RuntimePlatform.OSXPlayer
                ? Path.Combine(Application.dataPath, "Resources", "mcp", "house-mcp")
                : Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? ".", "mcp", "house-mcp.exe");
            return (exe, new string[0]);
        }

        /// <summary>
        /// Absolute path of a Node ≥ 20 (GUI apps such as Claude Desktop do not see nvm's PATH); "node" if none found.
        /// Only the editor needs it — the app ships the server as a single binary.
        /// </summary>
        static string NodePath()
        {
            var found = new List<(int major, string path)>();
            string nvm = Path.Combine(Home, ".nvm", "versions", "node");
            if (Directory.Exists(nvm))
                foreach (var dir in Directory.GetDirectories(nvm))
                {
                    string exe = Path.Combine(dir, "bin", "node");
                    var name = Path.GetFileName(dir).TrimStart('v').Split('.');
                    if (File.Exists(exe) && int.TryParse(name[0], out int major)) found.Add((major, exe));
                }
            found.Sort((a, b) => b.major.CompareTo(a.major));
            if (found.Count > 0 && found[0].major >= 20) return found[0].path;
            foreach (var p in new[] { "/opt/homebrew/bin/node", "/usr/local/bin/node" })
                if (File.Exists(p)) return p;
            return "node";
        }

        /// <summary>The server binary (or script) exists where the snippets point.</summary>
        public static bool ServerPresent()
        {
            var (cmd, args) = ServerCommand();
            return File.Exists(args.Length > 0 ? args[0] : cmd);
        }

        static JObject Entry(bool vsCode = false)
        {
            var (cmd, args) = ServerCommand();
            var o = new JObject();
            if (vsCode) o["type"] = "stdio";
            o["command"] = cmd;
            if (args.Length > 0) o["args"] = new JArray(args);
            return o;
        }

        static string Json(string key, bool vsCode = false) =>
            new JObject { [key] = new JObject { [ServerName] = Entry(vsCode) } }.ToString(Formatting.Indented);

        static string Quote(string s) => s.Contains(" ") ? "\"" + s + "\"" : s;

        static string Home => Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);

        static string ClaudeDesktopConfig =>
            Application.platform == RuntimePlatform.WindowsPlayer || Application.platform == RuntimePlatform.WindowsEditor
                ? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Claude", "claude_desktop_config.json")
                : Path.Combine(Home, "Library", "Application Support", "Claude", "claude_desktop_config.json");

        public static readonly List<Client> All = new List<Client>
        {
            new Client
            {
                Id = "claude", Name = "Claude Desktop", Hint = "После подключения перезапустите Claude Desktop",
                ConfigPath = ClaudeDesktopConfig, Snippet = () => Json("mcpServers"),
            },
            new Client
            {
                Id = "cursor", Name = "Cursor", Hint = "Cursor подхватит сервер сам (Settings → MCP)",
                ConfigPath = Path.Combine(Home, ".cursor", "mcp.json"), Snippet = () => Json("mcpServers"),
            },
            new Client
            {
                Id = "windsurf", Name = "Windsurf", Hint = "Обновите список серверов в панели Cascade",
                ConfigPath = Path.Combine(Home, ".codeium", "windsurf", "mcp_config.json"), Snippet = () => Json("mcpServers"),
            },
            new Client
            {
                Id = "claude-code", Name = "Claude Code", Hint = "Выполните команду в терминале",
                Snippet = () =>
                {
                    var (cmd, args) = ServerCommand();
                    return $"claude mcp add {ServerName} -- {Quote(cmd)}" + string.Concat(args.Select(a => " " + Quote(a)));
                },
            },
            new Client
            {
                Id = "vscode", Name = "VS Code (Copilot)", Hint = "Файл .vscode/mcp.json или пользовательские настройки",
                Snippet = () => Json("servers", vsCode: true),
            },
            new Client
            {
                Id = "codex", Name = "Codex CLI", Hint = "Добавьте в ~/.codex/config.toml",
                Snippet = () =>
                {
                    var (cmd, args) = ServerCommand();
                    var sb = new StringBuilder();
                    sb.AppendLine($"[mcp_servers.{ServerName}]");
                    sb.AppendLine($"command = {JsonConvert.ToString(cmd)}");
                    sb.Append("args = [" + string.Join(", ", args.Select(JsonConvert.ToString)) + "]");
                    return sb.ToString();
                },
            },
            new Client
            {
                Id = "other", Name = "Другой клиент", Hint = "LM Studio, Gemini CLI и другие — формат mcpServers",
                Snippet = () => Json("mcpServers"),
            },
        };

        /// <summary>Whether the client's config already has our server (and whether it points to this app).</summary>
        public static Link Status(Client c)
        {
            if (c.ConfigPath == null) return Link.Missing;
            if (!c.Installed) return Link.NotInstalled;
            try
            {
                if (!File.Exists(c.ConfigPath)) return Link.Missing;
                var root = JObject.Parse(File.ReadAllText(c.ConfigPath));
                if (!(root["mcpServers"]?[ServerName] is JObject entry)) return Link.Missing;
                var (cmd, args) = ServerCommand();
                var entryArgs = (entry["args"] as JArray)?.Select(t => (string)t) ?? Enumerable.Empty<string>();
                string entryCmd = (string)entry["command"] ?? "";
                // the editor's server is a script: any node running that script is this app's server
                bool same = args.Length > 0
                    ? entryArgs.SequenceEqual(args) && Path.GetFileNameWithoutExtension(entryCmd) == Path.GetFileNameWithoutExtension(cmd)
                    : entryCmd == cmd;
                return same ? Link.Connected : Link.Different;
            }
            catch (Exception) { return Link.Missing; }
        }

        /// <summary>Adds (or points to this app) the <c>house</c> server in the client's config.</summary>
        public static void Connect(Client c)
        {
            if (c.ConfigPath == null) throw new InvalidOperationException("этот клиент подключается вручную");
            JObject root;
            if (File.Exists(c.ConfigPath))
            {
                string text = File.ReadAllText(c.ConfigPath);
                try { root = string.IsNullOrWhiteSpace(text) ? new JObject() : JObject.Parse(text); }
                catch (Exception) { throw new InvalidOperationException("файл настроек клиента не читается как JSON — он не изменён, добавьте сервер вручную"); }
                File.WriteAllText(c.ConfigPath + ".bak", text, new UTF8Encoding(false));
            }
            else root = new JObject();
            if (!(root["mcpServers"] is JObject servers)) root["mcpServers"] = servers = new JObject();
            servers[ServerName] = Entry();
            Directory.CreateDirectory(Path.GetDirectoryName(c.ConfigPath) ?? ".");
            string tmp = c.ConfigPath + ".tmp";
            File.WriteAllText(tmp, root.ToString(Formatting.Indented), new UTF8Encoding(false));
            if (File.Exists(c.ConfigPath)) File.Replace(tmp, c.ConfigPath, null); else File.Move(tmp, c.ConfigPath);
        }
    }
}
