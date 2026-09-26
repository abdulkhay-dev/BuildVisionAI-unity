using System;
using System.Collections.Generic;
using System.Text;
using House4696.Generation;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Settings popover content (gear, ⌘,), w 320: graphics quality (segmented + caption), interface switches, the
    /// projects folder and a footer with the shortcut sheet and the version (spec §6).
    /// </summary>
    public static class SettingsPopover
    {
        public static VisualElement Build(AppUI ui)
        {
            AiActivityLog.Attach(ui);
            var s = ui.S.Settings;
            var root = Ui.El("dlg-pop dlg-settings");

            // ---------------- Графика
            root.Add(Dlg.Caption("Графика"));
            var items = new List<(string label, IconKind? icon, string tooltip, string keys)>(3);
            for (int i = 0; i < 3; i++)
            {
                string title = AppSettings.Title((GraphicsQuality)i);
                items.Add((title, null, title, null));
            }
            var hint = Ui.Text(AppSettings.Hint(s.Quality), "dlg-quality-hint");
            var seg = new Segmented(items, i =>
            {
                var q = (GraphicsQuality)i;
                if (s.Quality != q) s.Quality = q;
                hint.text = AppSettings.Hint(q);
            }, "sm boxed dlg-quality");
            for (int i = 0; i < seg.Items.Count; i++)
                Tooltips.Tip(seg.Items[i], "Графика: " + AppSettings.Title((GraphicsQuality)i).ToLowerInvariant(), null, AppSettings.Hint((GraphicsQuality)i));
            seg.Select((int)s.Quality);
            root.Add(seg.Element);
            root.Add(hint);

            // ---------------- Интерфейс
            root.Add(Ui.El("dlg-sep"));
            root.Add(Dlg.Caption("Интерфейс"));
            var refreshers = new List<Action>(4);
            root.Add(SwitchRow("Подсказки управления", () => s.ShowHints, v => s.ShowHints = v,
                "Подсказки управления", null, "Клавиши и мышь — на несколько секунд после смены режима", refreshers));
            // PlanPanel follows the setting itself (Settings.Changed), keeping the panel closed on an empty site
            root.Add(SwitchRow("План в прогулке", () => s.PlanInWalk, v => s.PlanInWalk = v,
                "Открывать план этажа в прогулке и полёте", null, "M — показать или скрыть план сейчас", refreshers));
            root.Add(SwitchRow("Счётчик FPS", () => s.ShowStats, v => s.ShowStats = v,
                "Счётчик кадров в секунду", null, "В левом нижнем углу окна", refreshers));
            // Screen.fullScreen applies at the end of the frame: the switch keeps its own value and re-syncs when the
            // window changes by other means (⌃⌘F / F11 while the popover is open, the window's green button)
            bool full = Screen.fullScreen;
            float fullSetAt = -10f;
            root.Add(SwitchRow("Полноэкранный режим", () => full, v =>
            {
                full = v;
                fullSetAt = Time.unscaledTime;
                Screen.fullScreen = v;
            }, "Полноэкранный режим", "⌃ ⌘ F", "Или F11", refreshers, "⌃ ⌘ F"));
            Action refreshFull = refreshers[refreshers.Count - 1];
            root.schedule.Execute(() =>
            {
                if (Time.unscaledTime - fullSetAt < 0.6f || Screen.fullScreen == full) return;
                full = Screen.fullScreen;
                refreshFull();
            }).Every(250);

            // ---------------- Файлы
            root.Add(Ui.El("dlg-sep"));
            root.Add(Dlg.Caption("Файлы"));
            string folder = ui.S.Session.Store.Root;
            var path = Dlg.Selectable(Dlg.ShortPath(folder), "dlg-files-path");
            Tooltips.Tip(path, folder);
            var show = Ui.Button(ButtonKind.Secondary, "Показать", () =>
            {
                ui.ClosePopover();
                ui.RevealInFinder(folder);
            }, null, "btn-xs");
            Tooltips.Tip(show, "Открыть папку проектов в Finder");
            // no leading icon: the label and the path start on the same 8 px inset as the switch labels
            root.Add(Ui.El("dlg-files", Ui.El("dlg-files-text", Ui.Text("Папка проектов", "dlg-files-title"), path), show));

            // ---------------- footer
            var keys = Ui.Button(ButtonKind.Ghost, "Горячие клавиши", ui.ShowShortcuts, IconKind.Keyboard, "btn-sm");
            keys.Add(Ui.Kbd("?", true));
            Tooltips.Tip(keys, "Управление и клавиши", "?");
            string version = string.IsNullOrEmpty(ui.S.Version) ? "House" : "House " + ui.S.Version;
            root.Add(Ui.El("dlg-pop-foot", keys, Ui.Text(version, "dlg-version")));

            // switches follow changes made elsewhere while the popover is open
            Action onChanged = () => { foreach (var r in refreshers) r(); };
            root.RegisterCallback<AttachToPanelEvent>(_ => s.Changed += onChanged);
            root.RegisterCallback<DetachFromPanelEvent>(_ => s.Changed -= onChanged);
            return root;
        }

        static VisualElement SwitchRow(string label, Func<bool> get, Action<bool> set, string tip, string tipKeys, string tipSub,
            List<Action> refreshers, string inlineKeys = null)
        {
            var row = Ui.Switch(label, get, set, out var refresh);
            row.AddToClassList("dlg-switch");
            if (!string.IsNullOrEmpty(inlineKeys))
            {
                var k = Ui.Keys(inlineKeys, true);
                k.AddToClassList("dlg-switch-keys");
                k.pickingMode = PickingMode.Ignore;
                row.Insert(1, k);
            }
            Tooltips.Tip(row, tip, tipKeys, tipSub);
            refreshers.Add(refresh);
            return row;
        }
    }

    /// <summary>
    /// Check issues popover content (issues badge), w 400, max-h 420: validation errors and warnings, a separate
    /// group of generator warnings and «Скопировать для ИИ». Refills itself after every rebuild while open.
    /// </summary>
    public static class IssuesPopover
    {
        public static VisualElement Build(AppUI ui)
        {
            var root = Ui.El("dlg-pop dlg-issues");
            var counts = Ui.Text("", "dlg-iss-counts");
            root.Add(Ui.El("dlg-iss-head", Ui.Text("Замечания", "t-headline"), counts));

            var scroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Auto,
            };
            scroll.AddToClassList("dlg-iss-scroll");
            root.Add(scroll);

            var copy = Dlg.CopyButton(ui, ButtonKind.Secondary, "Скопировать для ИИ", () => Report(ui), "Скопировано — вставьте в чат с ИИ",
                "btn-sm", "Скопировать список замечаний", "Вставьте его в чат — ИИ-ассистент исправит проект");
            var foot = Ui.El("dlg-iss-foot", Ui.Text("Исправления вносит ИИ — отправьте ему список.", "dlg-iss-foot-text"), copy);
            root.Add(foot);

            void Fill()
            {
                scroll.Clear();
                var session = ui.S.Session;
                List<Issue> issues = session.HasProject ? session.Issues : null;
                List<string> build = session.HasProject ? session.Result?.Warnings : null;
                int errors = 0, warnings = 0;
                if (issues != null)
                    foreach (var i in issues)
                        if (i.Level == IssueLevel.Error) errors++;
                        else warnings++;
                int buildCount = build?.Count ?? 0;
                warnings += buildCount;
                counts.text = CountsText(errors, warnings);
                bool any = errors + warnings > 0;
                Ui.Show(foot, any);
                if (!any)
                {
                    scroll.Add(EmptyState());
                    return;
                }
                if (issues != null)
                {
                    foreach (var i in issues) if (i.Level == IssueLevel.Error) scroll.Add(Row(true, i.Message, i.Path));
                    foreach (var i in issues) if (i.Level != IssueLevel.Error) scroll.Add(Row(false, i.Message, i.Path));
                }
                if (buildCount > 0)
                {
                    scroll.Add(Dlg.Caption("При сборке", "dlg-iss-group"));
                    foreach (var w in build) scroll.Add(Row(false, w, null));
                }
            }

            Fill();
            Action onRebuilt = Fill;
            root.RegisterCallback<AttachToPanelEvent>(_ =>
            {
                ui.S.Session.Rebuilt -= onRebuilt;
                ui.S.Session.Rebuilt += onRebuilt;
            });
            root.RegisterCallback<DetachFromPanelEvent>(_ => ui.S.Session.Rebuilt -= onRebuilt);
            return root;
        }

        static string CountsText(int errors, int warnings)
        {
            if (errors == 0 && warnings == 0) return "Замечаний нет";
            var parts = new List<string>(2);
            if (errors > 0) parts.Add(Ui.Plural(errors, "ошибка", "ошибки", "ошибок"));
            if (warnings > 0) parts.Add(Ui.Plural(warnings, "предупреждение", "предупреждения", "предупреждений"));
            return string.Join(" · ", parts);
        }

        static VisualElement Row(bool error, string message, string path)
        {
            var row = Ui.El("dlg-iss-row");
            row.pickingMode = PickingMode.Ignore;
            row.Add(Ui.Icon(error ? IconKind.Error : IconKind.Warning, 16, error ? "dlg-iss-icon c-danger" : "dlg-iss-icon c-warning"));
            var text = Ui.El("dlg-iss-text", Dlg.Plain(message, "dlg-iss-msg"));
            text.pickingMode = PickingMode.Ignore;
            if (!string.IsNullOrEmpty(path)) text.Add(Dlg.Plain(path, "dlg-iss-path"));
            row.Add(text);
            return row;
        }

        static VisualElement EmptyState()
        {
            var e = Ui.El("dlg-empty",
                Ui.El("dlg-empty-badge", Ui.Icon(IconKind.Check, 20)),
                Ui.Text("Всё в порядке", "dlg-empty-title"),
                Ui.Text("Проверка не нашла замечаний в проекте", "dlg-empty-text"));
            e.pickingMode = PickingMode.Ignore;
            return e;
        }

        /// <summary>«В проекте «46-96» проверка нашла замечания. Исправь их:\n— {сообщение} ({путь})».</summary>
        static string Report(AppUI ui)
        {
            var s = ui.S.Session;
            if (!s.HasProject) return "";
            var sb = new StringBuilder();
            sb.Append("В проекте «").Append(s.Doc.Meta?.Name ?? s.ProjectId).Append("» проверка нашла замечания. Исправь их:");
            int lines = 0;
            foreach (var i in s.Issues) if (i.Level == IssueLevel.Error) { Line(sb, i.Message, i.Path); lines++; }
            foreach (var i in s.Issues) if (i.Level != IssueLevel.Error) { Line(sb, i.Message, i.Path); lines++; }
            if (s.Result?.Warnings != null)
                foreach (var w in s.Result.Warnings) { Line(sb, w, null); lines++; }
            return lines > 0 ? sb.ToString() : "";
        }

        static void Line(StringBuilder sb, string message, string path)
        {
            sb.Append("\n— ").Append(message);
            if (!string.IsNullOrEmpty(path)) sb.Append(" (").Append(path).Append(')');
        }
    }

    /// <summary>
    /// AI popover content (AI segment), w 340: state with its dot and the last request, undo of the last edit
    /// (disabled with «Отменять нечего»), example prompt, the Connect AI dialog and the session's changes (P1).
    /// </summary>
    public static class AiPopover
    {
        public static VisualElement Build(AppUI ui)
        {
            AiActivityLog.Attach(ui);
            var ai = ui.Ai;
            var root = Ui.El("dlg-pop dlg-aipop");

            // ---------------- header
            var dot = new PulseDot();
            var state = Ui.Text("", "dlg-ai-state");
            var last = Ui.Text("", "dlg-ai-last");
            root.Add(Ui.El("dlg-ai-head", Ui.El("dlg-ai-dot", dot), Ui.El("dlg-ai-head-text", state, last)));
            // «Напишите в {клиент}, какой дом вы хотите, — …»; shown while the AI waits for its first request
            var hint = Ui.Text("", "dlg-ai-hint");
            root.Add(hint);
            root.Add(Ui.El("dlg-sep"));

            // ---------------- actions
            // «Открыть {клиент}»: the connected AI app, so the user can go and write to it right away (macOS)
            var app = Dlg.OpenableClient();
            if (app != null)
            {
                string appName = Dlg.ClientShort(app);
                var open = Row(new DlgArrowUpRight(), "Открыть " + appName, () =>
                {
                    ui.ClosePopover();
                    Dlg.OpenApp(ui, app);
                });
                Tooltips.Tip(open, "Перейти в " + appName, null, "Опишите там, какой дом вы хотите, — изменения появятся здесь");
                root.Add(open);
            }

            // undo: label + (when disabled) the reason under it; the ⌘Z slot keeps only the shortcut
            var undoCaption = Ui.Text("Отменять нечего", "dlg-row-caption");
            var undoText = Ui.El("dlg-row-text", Ui.Text("Отменить последнюю правку", "menu-label"), undoCaption);
            undoText.pickingMode = PickingMode.Ignore;
            var undo = Ui.El("menu-item dlg-row dlg-undo", Ui.Icon(IconKind.Undo, 16), undoText, Ui.Text("⌘Z", "menu-shortcut"));
            Ui.OnClick(undo, () =>
            {
                if (!CanUndo(ui)) return;
                ui.ClosePopover();
                ui.Undo();
            });
            root.Add(undo);

            var copy = Row(IconKind.Copy, "Скопировать пример запроса", () =>
            {
                string p = Dlg.ExamplePrompt(ui, false);
                ui.ClosePopover();
                ui.Copy(p);
            });
            Tooltips.Tip(copy, "Пример запроса для ИИ-ассистента", null, Dlg.ExamplePrompt(ui, false));
            root.Add(copy);

            var connect = Row(IconKind.Sparkle, "Настроить подключение…", ui.ShowConnectAi);
            Tooltips.Tip(connect, "Подключение ИИ-ассистента", null, "Клиенты, шаги подключения и диагностика");
            root.Add(connect);

            // ---------------- session changes (P1)
            var log = Ui.El("dlg-ai-log");
            root.Add(log);
            var times = new List<(Label label, DateTime utc)>(8);

            void UpdateLast()
            {
                last.text = ai.CalledThisSession ? "Последний запрос " + Ui.Ago(ai.LastCallUtc) : "Запросов ещё не было";
                foreach (var (label, utc) in times) label.text = Ui.Ago(utc);
            }

            void UpdateState()
            {
                switch (ai.State)
                {
                    case AiState.Working: dot.SetStyle("dot-ai", true); state.text = ai.Phrase; break;
                    case AiState.Online: dot.SetStyle("dot-success", false); state.text = "ИИ на связи"; break;
                    case AiState.Waiting: dot.SetStyle("dot-ring", false); state.text = "ИИ подключён"; break;
                    default: dot.SetStyle(null, false); state.text = "ИИ не подключён"; break;
                }
                bool waiting = ai.State == AiState.Waiting;
                if (waiting) hint.text = Dlg.WriteHint();
                Ui.Show(hint, waiting);
                UpdateLast();
            }

            void UpdateUndo()
            {
                bool can = CanUndo(ui);
                undo.EnableInClassList("dlg-row-off", !can);
                Ui.Show(undoCaption, !can);          // row h 44 with the reason, h 32 without
                if (can) Tooltips.Tip(undo, "Отменить последнюю правку ИИ", "⌘ Z", "Отменяется одна правка целиком");
                else Tooltips.Tip(undo, "Отменять нечего", null, "У этого проекта нет правок, которые можно отменить");
            }

            void UpdateLog()
            {
                log.Clear();
                times.Clear();
                var entries = AiActivityLog.Items;
                Ui.Show(log, entries.Count > 0);
                if (entries.Count == 0) return;
                log.Add(Ui.El("dlg-sep"));
                log.Add(Dlg.Caption("Изменения за сеанс"));
                foreach (var e in entries)
                {
                    var time = Ui.Text(Ui.Ago(e.Utc), "dlg-log-time");
                    times.Add((time, e.Utc));
                    var row = Ui.El("dlg-log-row", Ui.Icon(e.Icon, 14, "dlg-log-icon"), Dlg.Plain(e.Text, "dlg-log-text"), time);
                    row.pickingMode = PickingMode.Ignore;
                    log.Add(row);
                }
            }

            UpdateLog();
            UpdateUndo();
            UpdateState();

            Action onAi = UpdateState;
            Action onRebuilt = UpdateUndo;
            Action onProject = UpdateUndo;
            Action<string, bool> onCall = (command, ok) => UpdateLog();
            IVisualElementScheduledItem clock = null;
            root.RegisterCallback<AttachToPanelEvent>(_ =>
            {
                ai.Changed += onAi;
                ai.CallFinished += onCall;
                ui.S.Session.Rebuilt += onRebuilt;
                ui.S.Session.ProjectChanged += onProject;
                clock?.Pause();
                clock = root.schedule.Execute(UpdateLast).Every(1000);
            });
            root.RegisterCallback<DetachFromPanelEvent>(_ =>
            {
                ai.Changed -= onAi;
                ai.CallFinished -= onCall;
                ui.S.Session.Rebuilt -= onRebuilt;
                ui.S.Session.ProjectChanged -= onProject;
                clock?.Pause();
                clock = null;
            });
            return root;
        }

        static bool CanUndo(AppUI ui) => ui.S.Session.HasProject && ui.S.Session.UndoCount > 0;

        static VisualElement Row(IconKind icon, string label, Action onClick) => Row(Ui.Icon(icon, 16), label, onClick);

        static VisualElement Row(VisualElement icon, string label, Action onClick)
        {
            var row = Ui.El("menu-item dlg-row", icon, Ui.Text(label, "menu-label"));
            Ui.OnClick(row, onClick);
            return row;
        }
    }

    /// <summary>
    /// What the AI changed this session, newest first (up to 8), for the AI popover. Consecutive edits of one kind
    /// within 20 s merge («Внёс 4 правки»). Call <see cref="Attach"/> once at startup so early calls are kept.
    /// </summary>
    public static class AiActivityLog
    {
        public sealed class Entry
        {
            public string Command;
            public DateTime Utc;
            public int Count = 1;
            public IconKind Icon;
            public string Text;
        }

        const int Max = 8;
        const double MergeSeconds = 20;
        static readonly List<Entry> Entries = new List<Entry>();
        static AiStatus _source;

        public static IReadOnlyList<Entry> Items => Entries;

        /// <summary>Starts recording the AI's calls (idempotent per <see cref="AppUI.Ai"/>).</summary>
        public static void Attach(AppUI ui)
        {
            var ai = ui?.Ai;
            if (ai == null || ai == _source) return;
            _source = ai;
            Entries.Clear();
            ai.CallFinished += (command, ok) =>
            {
                if (!ok || ai != _source) return;
                Record(command);
            };
        }

        static void Record(string command)
        {
            var now = DateTime.UtcNow;
            if (Entries.Count > 0)
            {
                var top = Entries[0];
                if (top.Command == command && (now - top.Utc).TotalSeconds < MergeSeconds && (command == "upsert" || command == "remove"))
                {
                    top.Count++;
                    top.Utc = now;
                    top.Text = Describe(command, top.Count, out top.Icon);
                    return;
                }
            }
            string text = Describe(command, 1, out var icon);
            if (text == null) return;
            Entries.Insert(0, new Entry { Command = command, Utc = now, Icon = icon, Text = text });
            if (Entries.Count > Max) Entries.RemoveAt(Entries.Count - 1);
        }

        static string Describe(string command, int count, out IconKind icon)
        {
            icon = IconKind.Pencil;
            switch (command)
            {
                case "exterior_walls": icon = IconKind.House; return "Построил наружные стены";
                case "replace_project": icon = IconKind.House; return "Перестроил дом";
                case "upsert": return count > 1 ? "Внёс " + Ui.Plural(count, "правку", "правки", "правок") : "Внёс правку";
                case "remove": icon = IconKind.Trash; return count > 1 ? "Убрал элементы · " + Ui.Plural(count, "раз", "раза", "раз") : "Убрал элементы";
                case "undo": icon = IconKind.Undo; return "Отменил правку";
                case "create_project": icon = IconKind.Plus; return "Создал проект";
                case "open_project": icon = IconKind.Folder; return "Открыл проект";
                default: return null;
            }
        }
    }
}
