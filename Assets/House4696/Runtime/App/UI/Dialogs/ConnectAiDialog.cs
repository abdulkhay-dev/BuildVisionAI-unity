using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Connect AI, 760×540 (spec §6): client list with monograms on the left, three steps for the selected client on
    /// the right (auto-connect / command / config → restart → ask), a collapsed manual section (paths, config,
    /// diagnostics) and a live footer status. Link states are re-read every 2 s while the dialog is open.
    /// </summary>
    public sealed class ConnectAiDialog : Modal
    {
        const float LinkCheckEvery = 2f, StatusEvery = 0.25f;

        readonly List<AiClients.Client> _clients = new List<AiClients.Client>(AiClients.All);
        readonly Dictionary<string, AiClients.Link> _links = new Dictionary<string, AiClients.Link>();
        readonly Dictionary<string, VisualElement> _rows = new Dictionary<string, VisualElement>();
        readonly HashSet<string> _copied = new HashSet<string>();
        readonly ScrollView _panel;
        readonly VisualElement _content;
        readonly PulseDot _dot;
        readonly Label _status;
        AiClients.Client _sel;
        bool _manualOpen;
        float _nextLinks, _nextStatus;
        string _renderedKey, _statusText, _dotClass;
        bool _dotPulse;

        public ConnectAiDialog(AppUI ui)
            : base(ui, "Подключите ИИ-ассистента",
                "House показывает дом, который строит ваш ИИ. Выберите приложение, в котором вы с ним общаетесь.", 760)
        {
            AiActivityLog.Attach(ui);
            Card.AddToClassList("dlg-cai");
            Head.Insert(0, Ui.El("dlg-ai-tile", Ui.Icon(IconKind.Sparkle, 20)));

            ReadLinks();

            // left: clients — Claude Desktop first, then the developer tools under their own caption
            var list = Ui.El("dlg-cai-list");
            bool devCaption = false;
            foreach (var c in _clients)
            {
                if (!devCaption && IsDevTool(c))
                {
                    list.Add(Ui.Text("Для разработчиков", "dlg-cai-group"));
                    devCaption = true;
                }
                var client = c;
                var row = Ui.El("dlg-client");
                row.Add(Monogram(c));
                row.Add(Dlg.Plain(Dlg.ClientName(c), "dlg-client-name"));
                row.Add(Ui.Icon(IconKind.Check, 16, "dlg-client-check"));
                Ui.OnClick(row, () => Select(client));
                _rows[c.Id] = row;
                list.Add(row);
            }

            // right: steps for the selected client
            // the scroller shows only when the steps really overflow (collapsed content is within 1–2 px of the viewport)
            _panel = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Hidden,
            };
            _panel.AddToClassList("dlg-cai-panel");
            _content = Ui.El("dlg-cai-content");
            _panel.Add(_content);
            _panel.contentContainer.RegisterCallback<GeometryChangedEvent>(_ => FitScroller());
            _panel.contentViewport.RegisterCallback<GeometryChangedEvent>(_ => FitScroller());
            Body.Add(list);
            Body.Add(_panel);

            // footer: live status + «Готово»
            _dot = new PulseDot();
            _status = Ui.Text("", "dlg-foot-status-text");
            Foot.Add(Ui.El("dlg-foot-status", Ui.El("dlg-foot-dot", _dot), _status));
            var done = Ui.Button(ButtonKind.Primary, "Готово", Close);
            Tooltips.Tip(done, "Закрыть окно", "↩");
            Foot.Add(done);
            Primary = Close;

            _sel = Preselect();
            UpdateRows();
            Render(true);
            UpdateStatus();
            _nextLinks = Time.unscaledTime + LinkCheckEvery;
        }

        public override void Tick()
        {
            float now = Time.unscaledTime;
            if (now >= _nextLinks)
            {
                _nextLinks = now + LinkCheckEvery;
                if (ReadLinks())
                {
                    Ui_.Ai.RefreshClients();
                    UpdateRows();
                }
                Render(false);
            }
            if (now >= _nextStatus)
            {
                _nextStatus = now + StatusEvery;
                UpdateStatus();
            }
        }

        // ------------------------------------------------------------------ clients
        /// <summary>Re-reads every client's config; true when a link state changed.</summary>
        bool ReadLinks()
        {
            bool changed = false;
            foreach (var c in _clients)
            {
                AiClients.Link l;
                try { l = AiClients.Status(c); }
                catch (Exception) { l = AiClients.Link.Missing; }
                if (!_links.TryGetValue(c.Id, out var old) || old != l)
                {
                    _links[c.Id] = l;
                    changed = true;
                }
            }
            return changed;
        }

        AiClients.Link LinkOf(AiClients.Client c) => _links.TryGetValue(c.Id, out var l) ? l : AiClients.Link.Missing;

        bool IsConnected(AiClients.Client c) => c.CanAutoConnect && LinkOf(c) == AiClients.Link.Connected;

        /// <summary>First connected client, else the first installed one, else Claude Desktop.</summary>
        AiClients.Client Preselect()
        {
            foreach (var c in _clients) if (IsConnected(c)) return c;
            foreach (var c in _clients)
            {
                bool installed;
                try { installed = c.CanAutoConnect && c.Installed; }
                catch (Exception) { installed = false; }
                if (installed) return c;
            }
            return _clients.Find(c => c.Id == "claude") ?? (_clients.Count > 0 ? _clients[0] : null);
        }

        /// <summary>Editors and CLIs listed under «Для разработчиков» (Claude Desktop and «Другое приложение» are not).</summary>
        static bool IsDevTool(AiClients.Client c) => c.Id switch
        {
            "cursor" => true,
            "windsurf" => true,
            "claude-code" => true,
            "vscode" => true,
            "codex" => true,
            _ => false,
        };

        /// <summary>Scroller only for a real overflow; a 1–2 px excess would show a thumb of ~95 % of the track.</summary>
        void FitScroller()
        {
            float over = _panel.contentContainer.layout.height - _panel.contentViewport.layout.height;
            if (float.IsNaN(over)) return;
            var want = over > 2f ? ScrollerVisibility.Auto : ScrollerVisibility.Hidden;
            if (want == ScrollerVisibility.Hidden && _panel.scrollOffset.y != 0f) _panel.scrollOffset = Vector2.zero;
            if (_panel.verticalScrollerVisibility != want) _panel.verticalScrollerVisibility = want;
        }

        void Select(AiClients.Client c)
        {
            if (c == null || c == _sel) return;
            _sel = c;
            UpdateRows();
            Render(true);
            _panel.scrollOffset = Vector2.zero;
        }

        void UpdateRows()
        {
            foreach (var c in _clients)
            {
                var row = _rows[c.Id];
                row.EnableInClassList("selected", c == _sel);
                Ui.Show(row.Q(className: "dlg-client-check"), IsConnected(c));
                Tooltips.Tip(row, RowTip(c));
            }
        }

        string RowTip(AiClients.Client c)
        {
            if (!c.CanAutoConnect)
                return c.Id == "claude-code" ? c.Name + " — подключается командой в терминале" : Dlg.ClientName(c) + " — подключается вручную";
            switch (LinkOf(c))
            {
                case AiClients.Link.Connected: return c.Name + " — подключён";
                case AiClients.Link.Different: return c.Name + " — настроен для другой копии House";
                case AiClients.Link.NotInstalled: return c.Name + " — не найден на этом Mac";
                default: return c.Name + " — подключается в один щелчок";
            }
        }

        static VisualElement Monogram(AiClients.Client c)
        {
            string text = c.Id switch
            {
                "claude" => "C",
                "cursor" => "Cu",
                "windsurf" => "W",
                "claude-code" => ">_",
                "vscode" => "VS",
                "codex" => "Cx",
                "other" => "+",
                _ => string.IsNullOrEmpty(c.Name) ? "?" : c.Name.Substring(0, 1).ToUpperInvariant(),
            };
            var m = Ui.El("dlg-mono dlg-mono-" + c.Id, Ui.Text(text, "dlg-mono-text"));
            m.pickingMode = PickingMode.Ignore;
            return m;
        }

        /// <summary>Client name inside a sentence («Перезапустите Cursor», «…в VS Code», «Перезапустите приложение»).</summary>
        static string Short(AiClients.Client c) => Dlg.ClientShort(c);

        static bool IsCli(AiClients.Client c) => c.Id == "claude-code" || c.Id == "codex";

        static string SafeSnippet(AiClients.Client c)
        {
            try { return c.Snippet?.Invoke() ?? ""; }
            catch (Exception e) { Debug.LogWarning("[ConnectAi] snippet: " + e.Message); return ""; }
        }

        void Connect(AiClients.Client c)
        {
            try { AiClients.Connect(c); }
            catch (Exception e) { Ui_.Toast("Не удалось подключить " + Short(c) + ": " + e.Message, IconKind.Error, ToastKind.Error); }
            Ui_.Ai.RefreshClients();
            ReadLinks();
            UpdateRows();
            Render(false);
        }

        void MarkCopied(AiClients.Client c)
        {
            if (!_copied.Add(c.Id)) return;
            // let the button show «Скопировано» for a moment before the step list redraws
            _content.schedule.Execute(() => Render(false)).ExecuteLater(900);
        }

        // ------------------------------------------------------------------ right panel
        void Render(bool force)
        {
            var c = _sel;
            if (c == null) return;
            var link = LinkOf(c);
            bool s1 = c.CanAutoConnect ? link == AiClients.Link.Connected : _copied.Contains(c.Id);
            bool s2 = Ui_.Ai.CalledThisSession;
            bool s3 = s2 && Ui_.S.Settings.AiBuiltOnce;
            string prompt = Dlg.ExamplePrompt(Ui_, true);
            string key = c.Id + "|" + link + "|" + s1 + "|" + s2 + "|" + s3 + "|" + prompt;
            if (!force && key == _renderedKey) return;
            _renderedKey = key;

            _content.Clear();
            _content.Add(Dlg.Plain(Dlg.ClientName(c), "t-headline dlg-cai-name"));
            int current = !s1 ? 0 : !s2 ? 1 : !s3 ? 2 : -1;
            var steps = Ui.El("dlg-steps");
            steps.Add(Step(0, current, s1, Step1Title(c, link), Step1Body(c, link), false));
            steps.Add(Step(1, current, s2, "Перезапустите " + Short(c), Ui.Text(IsCli(c)
                ? "Начните новый сеанс в терминале."
                : "Закройте приложение полностью (⌘Q) и откройте снова.", "dlg-step-text"), false));
            steps.Add(Step(2, current, s3, "Попросите ИИ построить дом", PromptBox(prompt), true));
            _content.Add(steps);
            _content.Add(Manual(c));
        }

        static VisualElement Step(int index, int current, bool done, string title, VisualElement body, bool last)
        {
            var num = Ui.El("dlg-step-num");
            if (done) num.Add(Ui.Icon(IconKind.Check, 14));
            else num.Add(Ui.Text((index + 1).ToString(), "dlg-step-digit"));
            var rail = Ui.El("dlg-step-rail", num, Ui.El("dlg-step-line"));
            var main = Ui.El("dlg-step-body", Dlg.Plain(title, "dlg-step-title"));
            if (body != null) main.Add(body);
            var step = Ui.El("dlg-step", rail, main);
            step.EnableInClassList("done", done);
            step.EnableInClassList("current", index == current && !done);
            step.EnableInClassList("last", last);
            return step;
        }

        static string Step1Title(AiClients.Client c, AiClients.Link link)
        {
            // a done step states the fact instead of the instruction
            if (c.CanAutoConnect) return (link == AiClients.Link.Connected ? "House добавлен в " : "Добавьте House в ") + Short(c);
            if (c.Id == "claude-code") return "Выполните команду в терминале";
            return "Добавьте сервер в настройки клиента";
        }

        VisualElement Step1Body(AiClients.Client c, AiClients.Link link)
        {
            var box = Ui.El("dlg-step-content");
            if (c.CanAutoConnect)
            {
                switch (link)
                {
                    case AiClients.Link.Connected:
                    {
                        var ok = Ui.El("dlg-ok", Ui.Icon(IconKind.Check, 16), Ui.Text("Подключено", "dlg-ok-label"));
                        var again = Ui.Button(ButtonKind.Secondary, "Подключить заново", () => Connect(c), null, "btn-xs");
                        Tooltips.Tip(again, "Записать подключение ещё раз", null, "Поможет, если " + Short(c) + " не видит House");
                        box.Add(Ui.El("dlg-step-controls", ok, again));
                        break;
                    }
                    case AiClients.Link.Different:
                        box.Add(Ui.Text("Настроено для другой копии House", "dlg-step-text"));
                        box.Add(Ui.El("dlg-step-controls", ConnectButton(c, "Обновить подключение", "Направить " + Short(c) + " на эту копию House")));
                        break;
                    case AiClients.Link.NotInstalled:
                        box.Add(Ui.El("dlg-step-controls", ConnectButton(c, "Подключить автоматически", "Добавить House в настройки " + Short(c))));
                        box.Add(Ui.Text(c.Name + " не найден на этом Mac", "dlg-step-text dlg-step-note"));
                        break;
                    default:
                        box.Add(Ui.El("dlg-step-controls", ConnectButton(c, "Подключить автоматически", "Добавить House в настройки " + Short(c))));
                        break;
                }
            }
            else if (c.Id == "claude-code")
            {
                string cmd = SafeSnippet(c);
                var text = Dlg.Selectable(cmd, "dlg-code-text");
                Tooltips.Tip(text, "Команда для терминала", null, cmd);
                box.Add(Ui.El("dlg-code", text));
                box.Add(Ui.El("dlg-step-controls", Dlg.CopyButton(Ui_, ButtonKind.Secondary, "Скопировать команду", () => SafeSnippet(c),
                    "Скопировано — вставьте в терминал", "btn-sm", "Скопировать команду", "Вставьте её в терминал и нажмите ↩", () => MarkCopied(c))));
            }
            else
            {
                if (!string.IsNullOrEmpty(c.Hint)) box.Add(Dlg.Plain(c.Hint, "dlg-step-text"));
                box.Add(Ui.El("dlg-step-controls", Dlg.CopyButton(Ui_, ButtonKind.Secondary, "Скопировать конфигурацию", () => SafeSnippet(c),
                    "Скопировано — вставьте в настройки клиента", "btn-sm", "Скопировать настройки сервера House",
                    "Вставьте их в настройки MCP-серверов " + (c.Id == "other" ? "клиента" : Short(c)), () => MarkCopied(c))));
            }
            return box;
        }

        VisualElement ConnectButton(AiClients.Client c, string label, string tip)
        {
            var b = Ui.Button(ButtonKind.Primary, label, () => Connect(c), null, "btn-sm");
            Tooltips.Tip(b, tip, null, "Остальное в файле настроек не изменится, прежняя версия сохранится рядом");
            return b;
        }

        VisualElement PromptBox(string prompt)
        {
            var text = Dlg.Selectable(prompt, "dlg-prompt-text");
            var copy = Dlg.CopyButton(Ui_, ButtonKind.Ghost, "Скопировать", () => prompt, "Скопировано — вставьте в чат с ИИ",
                "btn-xs", "Скопировать запрос", "Вставьте его в чат с ИИ-ассистентом");
            return Ui.El("dlg-prompt", text, Ui.El("dlg-prompt-foot", copy));
        }

        // ------------------------------------------------------------------ manual setup
        VisualElement Manual(AiClients.Client c)
        {
            var chevron = Ui.Icon(IconKind.ChevronRight, 14);
            var toggle = Ui.El("dlg-disclosure", chevron, Ui.Text("Настроить вручную", "dlg-disclosure-label"));
            var body = Ui.El("dlg-manual");
            toggle.EnableInClassList("open", _manualOpen);
            Ui.Show(body, _manualOpen);
            Ui.OnClick(toggle, () =>
            {
                _manualOpen = !_manualOpen;
                toggle.EnableInClassList("open", _manualOpen);
                Ui.Show(body, _manualOpen);
                Tooltips.Tip(toggle, ManualTip());
                if (_manualOpen) _panel.schedule.Execute(() => { if (body.panel != null) _panel.ScrollTo(body); }).ExecuteLater(40);
            });
            Tooltips.Tip(toggle, ManualTip());

            if (c.ConfigPath != null) body.Add(PathRow("Файл настроек", c.ConfigPath, true));
            string server = ServerPath();
            if (!string.IsNullOrEmpty(server)) body.Add(PathRow("Сервер House", server, false));

            string snippet = SafeSnippet(c);
            bool command = c.Id == "claude-code";
            body.Add(Ui.Text(command ? "Команда" : "Конфигурация", "dlg-manual-caption"));
            body.Add(Ui.El("dlg-json", Dlg.Selectable(Dlg.KeepIndent(snippet), "dlg-json-text")));
            body.Add(Ui.El("dlg-step-controls", Dlg.CopyButton(Ui_, ButtonKind.Secondary, command ? "Скопировать команду" : "Скопировать конфигурацию",
                () => SafeSnippet(c), command ? "Скопировано — вставьте в терминал" : "Скопировано — вставьте в настройки клиента",
                "btn-sm", command ? "Скопировать команду" : "Скопировать конфигурацию", null, () => MarkCopied(c))));

            body.Add(Ui.Text("Диагностика", "dlg-manual-caption"));
            body.Add(Diagnostics(server));

            return Ui.El("dlg-manual-wrap", toggle, body);
        }

        string ManualTip() => _manualOpen ? "Скрыть ручную настройку" : "Путь к настройкам, конфигурация и диагностика";

        static string ServerPath()
        {
            try
            {
                var (cmd, args) = AiClients.ServerCommand();
                return args != null && args.Length > 0 ? args[0] : cmd;
            }
            catch (Exception) { return null; }
        }

        VisualElement PathRow(string caption, string path, bool reveal)
        {
            var text = Dlg.Selectable(Dlg.ShortPath(path), "dlg-path");
            Tooltips.Tip(text, path);
            var row = Ui.El("dlg-path-row", Ui.El("dlg-path-col", Ui.Text(caption, "dlg-manual-caption"), text));
            if (reveal)
            {
                string target = null;
                try
                {
                    if (File.Exists(path)) target = path;
                    else
                    {
                        string dir = Path.GetDirectoryName(path);
                        if (!string.IsNullOrEmpty(dir) && Directory.Exists(dir)) target = dir;
                    }
                }
                catch (Exception) { target = null; }
                if (target != null)
                    row.Add(Ui.IconButton(IconKind.Folder, () => Ui_.RevealInFinder(target), "Показать в Finder", null, ButtonKind.Ghost, "btn-xs on-surface-1", 16));
            }
            return row;
        }

        VisualElement Diagnostics(string serverPath)
        {
            var chips = Ui.El("dlg-chips");
            bool server;
            try { server = AiClients.ServerPresent(); }
            catch (Exception) { server = false; }
            var serverChip = Chip(server ? "Сервер найден" : "Сервер не найден", server ? "ok" : "bad", server ? IconKind.Check : IconKind.Warning);
            if (!string.IsNullOrEmpty(serverPath)) Tooltips.Tip(serverChip, server ? "MCP-сервер House" : "MCP-сервер House не найден по пути", null, serverPath);
            chips.Add(serverChip);
            int port = Ui_.S.Api?.Port ?? 0;
            chips.Add(Chip(port > 0 ? "Порт " + port : "API не запущен", port > 0 ? "ok" : "bad", port > 0 ? IconKind.Check : IconKind.Warning));
            if (!string.IsNullOrEmpty(Ui_.S.Version)) chips.Add(Chip("House " + Ui_.S.Version, null, null));
            return chips;
        }

        static VisualElement Chip(string text, string kind, IconKind? icon)
        {
            var chip = Ui.El("dlg-chip");
            Ui.AddClasses(chip, kind);
            if (icon.HasValue) chip.Add(Ui.Icon(icon.Value, 12));
            chip.Add(Ui.Text(text, "dlg-chip-text"));
            return chip;
        }

        // ------------------------------------------------------------------ footer status
        void UpdateStatus()
        {
            var ai = Ui_.Ai;
            string text, dot;
            bool pulse = false;
            if (!ai.CalledThisSession)
            {
                text = "House ждёт первого запроса";
                dot = "dot-ring";
            }
            else if (ai.State == AiState.Working)
            {
                text = ai.Phrase + " · запрос " + Dlg.AgoShort(ai.LastCallUtc);
                dot = "dot-ai";
                pulse = true;
            }
            else
            {
                text = "ИИ на связи · запрос " + Dlg.AgoShort(ai.LastCallUtc);
                dot = "dot-success";
            }
            if (text != _statusText)
            {
                _statusText = text;
                _status.text = text;
            }
            if (dot != _dotClass || pulse != _dotPulse)
            {
                _dotClass = dot;
                _dotPulse = pulse;
                _dot.SetStyle(dot, pulse);
            }
        }
    }
}
