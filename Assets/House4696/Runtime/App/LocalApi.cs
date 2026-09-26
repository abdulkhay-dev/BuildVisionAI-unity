using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Local control API for the MCP server: HTTP on 127.0.0.1 only, bearer token required. The port and token are
    /// published in <c>~/.house-app/api.json</c> (deleted on exit). Requests are JSON <c>{ "command", "args" }</c>;
    /// they are queued and executed on Unity's main thread by <see cref="Pump"/>.
    /// </summary>
    public sealed class LocalApi : IDisposable
    {
        public const int DefaultPort = 47960;
        const int MaxBody = 16 * 1024 * 1024;

        public sealed class Call
        {
            public string Command;
            public JObject Args;
            public readonly TaskCompletionSource<JToken> Done = new TaskCompletionSource<JToken>();
        }

        public int Port { get; private set; }
        /// <summary>When the last command arrived (UTC; MinValue = none since start) — the UI shows whether an AI is connected.</summary>
        public DateTime LastCallUtc { get; private set; } = DateTime.MinValue;
        public string LastCommand { get; private set; }
        /// <summary>Commands received and not answered yet (the AI is working right now).</summary>
        public int InFlight => Volatile.Read(ref _inFlight);
        /// <summary>When the last command was answered (UTC).</summary>
        public DateTime LastFinishedUtc { get; private set; } = DateTime.MinValue;
        /// <summary>Raised on the main thread (from <see cref="Pump"/>) when a command was answered: command, success.</summary>
        public event Action<string, bool> CallFinished;

        int _inFlight;
        readonly ConcurrentQueue<(string command, bool ok)> _finished = new ConcurrentQueue<(string, bool)>();
        public string Token { get; }
        public static string DiscoveryPath => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".house-app", "api.json");

        readonly ConcurrentQueue<Call> _queue = new ConcurrentQueue<Call>();
        HttpListener _listener;
        Thread _thread;
        volatile bool _running;

        public LocalApi()
        {
            var bytes = new byte[24];
            using (var rng = RandomNumberGenerator.Create()) rng.GetBytes(bytes);
            Token = Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_');
        }

        public void Start(string version)
        {
            for (int port = DefaultPort; port < DefaultPort + 20; port++)
            {
                try
                {
                    var l = new HttpListener();
                    l.Prefixes.Add($"http://127.0.0.1:{port}/");
                    l.Start();
                    _listener = l; Port = port;
                    break;
                }
                catch (Exception) { /* port busy: try the next one */ }
            }
            if (_listener == null) { Debug.LogError("[LocalApi] no free port"); return; }
            _running = true;
            _thread = new Thread(Loop) { IsBackground = true, Name = "HouseLocalApi" };
            _thread.Start();

            Directory.CreateDirectory(Path.GetDirectoryName(DiscoveryPath) ?? ".");
            var info = new JObject
            {
                ["url"] = $"http://127.0.0.1:{Port}/api", ["port"] = Port, ["token"] = Token,
                ["pid"] = System.Diagnostics.Process.GetCurrentProcess().Id, ["version"] = version,
                ["started"] = DateTime.UtcNow.ToString("o"),
            };
            File.WriteAllText(DiscoveryPath, info.ToString(Formatting.Indented));
            Debug.Log($"[LocalApi] listening on 127.0.0.1:{Port}");
        }

        void Loop()
        {
            while (_running)
            {
                HttpListenerContext ctx;
                try { ctx = _listener.GetContext(); }
                catch (Exception) { if (!_running) return; continue; }
                ThreadPool.QueueUserWorkItem(_ => Handle(ctx));
            }
        }

        async void Handle(HttpListenerContext ctx)
        {
            var req = ctx.Request;
            var res = ctx.Response;
            JObject reply;
            try
            {
                if (req.HttpMethod == "GET" && req.Url.AbsolutePath == "/health")
                    reply = new JObject { ["ok"] = true, ["app"] = "house" };
                else if (req.HttpMethod != "POST" || req.Url.AbsolutePath != "/api")
                    reply = Error("POST /api");
                else if (req.Headers["Authorization"] != "Bearer " + Token)
                {
                    res.StatusCode = 401;
                    reply = Error("unauthorized");
                }
                else if (req.ContentLength64 > MaxBody)
                    reply = Error("request too large");
                else
                {
                    string body;
                    using (var r = new StreamReader(req.InputStream, Encoding.UTF8)) body = r.ReadToEnd();
                    var o = JObject.Parse(body);
                    var call = new Call { Command = (string)o["command"], Args = o["args"] as JObject ?? new JObject() };
                    Interlocked.Increment(ref _inFlight);
                    _queue.Enqueue(call);
                    Task finished;
                    try { finished = await Task.WhenAny(call.Done.Task, Task.Delay(TimeSpan.FromSeconds(180))); }
                    finally
                    {
                        Interlocked.Decrement(ref _inFlight);
                        _finished.Enqueue((call.Command, call.Done.Task.IsCompleted && !call.Done.Task.IsFaulted));
                    }
                    reply = finished == call.Done.Task
                        ? (call.Done.Task.IsFaulted ? Error(call.Done.Task.Exception?.GetBaseException().Message) : new JObject { ["ok"] = true, ["result"] = call.Done.Task.Result })
                        : Error("timeout: приложение не ответило за 180 с");
                }
            }
            catch (Exception e) { reply = Error(e.Message); }
            try
            {
                var bytes = Encoding.UTF8.GetBytes(reply.ToString(Formatting.None));
                res.ContentType = "application/json; charset=utf-8";
                res.ContentLength64 = bytes.Length;
                res.OutputStream.Write(bytes, 0, bytes.Length);
                res.Close();
            }
            catch (Exception) { /* client went away */ }
        }

        static JObject Error(string msg) => new JObject { ["ok"] = false, ["error"] = msg ?? "error" };

        /// <summary>Main-thread pump: hands queued calls to <paramref name="execute"/>.</summary>
        public void Pump(Action<Call> execute)
        {
            while (_finished.TryDequeue(out var f))
            {
                LastFinishedUtc = DateTime.UtcNow;
                try { CallFinished?.Invoke(f.command, f.ok); }
                catch (Exception e) { Debug.LogException(e); }
            }
            while (_queue.TryDequeue(out var call))
            {
                LastCallUtc = DateTime.UtcNow;
                LastCommand = call.Command;
                try { execute(call); }
                catch (Exception e) { call.Done.TrySetException(e); }
            }
        }

        public void Dispose()
        {
            _running = false;
            try { _listener?.Stop(); _listener?.Close(); } catch (Exception) { }
            try
            {
                if (File.Exists(DiscoveryPath) && File.ReadAllText(DiscoveryPath).Contains(Token)) File.Delete(DiscoveryPath);
            }
            catch (Exception) { }
        }
    }
}
