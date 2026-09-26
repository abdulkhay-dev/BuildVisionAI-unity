using System;
using System.Text;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Shared pieces of the dialogs and popovers (spec §6): field groups, copy buttons with a short «Скопировано»
    /// confirmation, selectable text, example prompts and time/path formatting. Styles: Resources/UI/Dialogs.uss (dlg-).
    /// </summary>
    internal static class Dlg
    {
        /// <summary>The empty-site prompt (spec §3.6).</summary>
        public const string BuildPrompt = "Спроектируй одноэтажный дом 10×12 м: гостиная с кухней, две спальни, санузел и терраса. Расставь мебель.";

        public static string OpenPrompt(string name) => $"Открой в House проект «{name}» и покажи его снаружи.";

        /// <summary>
        /// Example request for the AI. <paramref name="preferOpen"/>: with a project open always the «open it» prompt
        /// (Connect AI, spec); otherwise only when the open house already has walls or rooms.
        /// </summary>
        public static string ExamplePrompt(AppUI ui, bool preferOpen)
        {
            var s = ui?.S?.Session;
            if (s == null || !s.HasProject) return BuildPrompt;
            bool built = s.Doc.Walls.Count > 0 || s.Doc.Rooms.Count > 0;
            return preferOpen || built ? OpenPrompt(s.Doc.Meta?.Name ?? s.ProjectId) : BuildPrompt;
        }

        /// <summary>Label without rich text (user and AI strings may contain angle brackets).</summary>
        public static Label Plain(string text, string classes)
        {
            var l = Ui.Text(text ?? "", classes);
            l.enableRichText = false;
            return l;
        }

        /// <summary>Selectable text (paths, commands, prompts): pickable so it can be selected and carry a tooltip.</summary>
        public static Label Selectable(string text, string classes)
        {
            var l = Plain(text, classes);
            l.pickingMode = PickingMode.Position;
            l.selection.isSelectable = true;
            return l;
        }

        /// <summary>Label (UI text-2, 6 px above) + control; optional aside text on the right of the label.</summary>
        public static VisualElement Field(string label, string aside, VisualElement control, string classes = null)
        {
            var head = Ui.El("dlg-label-row", Ui.Text(label, "dlg-label"));
            if (!string.IsNullOrEmpty(aside)) head.Add(Ui.Text(aside, "dlg-label-aside"));
            var group = Ui.El("dlg-field", head, control);
            Ui.AddClasses(group, classes);
            return group;
        }

        /// <summary>Section caption of a popover (Caption Medium text-3).</summary>
        public static Label Caption(string text, string classes = null)
        {
            var l = Ui.Text(text, "pop-caption");
            Ui.AddClasses(l, classes);
            return l;
        }

        /// <summary>
        /// Button that copies <paramref name="text"/> to the clipboard: a toast, and the button itself briefly turns
        /// into «✓ Скопировано».
        /// </summary>
        public static VisualElement CopyButton(AppUI ui, ButtonKind kind, string label, Func<string> text, string toast,
            string classes, string tip, string tipSub = null, Action copied = null)
        {
            VisualElement b = null;
            IVisualElementScheduledItem revert = null;
            b = Ui.Button(kind, label, () =>
            {
                string t = text?.Invoke();
                if (string.IsNullOrEmpty(t)) return;
                ui.Copy(t, toast ?? "Скопировано — вставьте в чат с ИИ");
                revert = Flash(b, label, revert);
                copied?.Invoke();
            }, IconKind.Copy, classes);
            Tooltips.Tip(b, tip, null, tipSub);
            return b;
        }

        /// <summary>Swaps the label to «✓ Скопировано» for 1.6 s; a repeated click restarts the timer.</summary>
        static IVisualElementScheduledItem Flash(VisualElement b, string label, IVisualElementScheduledItem pending)
        {
            if (b == null) return null;
            pending?.Pause();
            if (!b.ClassListContains("dlg-copied"))
            {
                float w = b.resolvedStyle.width;
                if (!float.IsNaN(w) && w > 0f) b.style.minWidth = w;      // no width jump while the label is swapped
            }
            var icon = b.Q<Icon>();
            if (icon != null) icon.Kind = IconKind.Check;
            Ui.SetLabel(b, "Скопировано");
            b.AddToClassList("dlg-copied");
            var item = b.schedule.Execute(() =>
            {
                if (icon != null) icon.Kind = IconKind.Copy;
                Ui.SetLabel(b, label);
                b.RemoveFromClassList("dlg-copied");
                b.style.minWidth = StyleKeyword.Null;
            });
            item.ExecuteLater(1600);
            return item;
        }

        /// <summary>"только что", "12 с назад", "5 мин назад", then <see cref="Ui.Ago(DateTime)"/>.</summary>
        public static string AgoShort(DateTime utc)
        {
            var d = DateTime.UtcNow - utc;
            if (d.TotalSeconds < 5) return "только что";
            if (d.TotalSeconds < 60) return (int)d.TotalSeconds + " с назад";
            if (d.TotalMinutes < 60) return (int)d.TotalMinutes + " мин назад";
            return Ui.Ago(utc);
        }

        /// <summary>Home folder as "~".</summary>
        public static string ShortPath(string path)
        {
            if (string.IsNullOrEmpty(path)) return "";
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            return !string.IsNullOrEmpty(home) && path.StartsWith(home, StringComparison.Ordinal) ? "~" + path.Substring(home.Length) : path;
        }

        // ------------------------------------------------------------------ AI clients
        static bool IsMac => Application.platform == RuntimePlatform.OSXPlayer || Application.platform == RuntimePlatform.OSXEditor;

        /// <summary>Client name in lists and headings («Другое приложение» for the catch-all entry).</summary>
        public static string ClientName(AiClients.Client c) => c == null ? "" : c.Id == "other" ? "Другое приложение" : c.Name;

        /// <summary>Client name inside a sentence («Перезапустите Cursor», «…в VS Code», «Перезапустите приложение»).</summary>
        public static string ClientShort(AiClients.Client c) => c == null ? "" : c.Id switch
        {
            "vscode" => "VS Code",
            "other" => "приложение",
            _ => c.Name,
        };

        /// <summary>
        /// macOS application of a client for `open -a` (null: CLI clients and «Другое приложение»).
        /// TODO(lead): move into <c>AiClients.Client.AppName</c>.
        /// </summary>
        public static string AppName(AiClients.Client c) => c == null ? null : c.Id switch
        {
            "claude" => "Claude",
            "cursor" => "Cursor",
            "windsurf" => "Windsurf",
            "vscode" => "Visual Studio Code",
            _ => null,
        };

        /// <summary>The client's config has this app's server (reads its config file).</summary>
        public static bool IsConnected(AiClients.Client c)
        {
            if (c == null || !c.CanAutoConnect) return false;
            try { return AiClients.Status(c) == AiClients.Link.Connected; }
            catch (Exception) { return false; }
        }

        /// <summary>First connected client that has an app to open (macOS only), or null.</summary>
        public static AiClients.Client OpenableClient()
        {
            if (!IsMac) return null;
            foreach (var c in AiClients.All)
                if (AppName(c) != null && IsConnected(c)) return c;
            return null;
        }

        /// <summary>
        /// «Напишите в {клиент}, какой дом вы хотите, — изменения появятся здесь.» with the one connected client;
        /// «ИИ» when none or several are connected. TODO(lead): replace with AiStatus.Hint once it exists.
        /// </summary>
        public static string WriteHint()
        {
            AiClients.Client only = null;
            int n = 0;
            foreach (var c in AiClients.All)
                if (IsConnected(c)) { n++; only = c; }
            return n == 1
                ? "Напишите в " + ClientShort(only) + ", какой дом вы хотите, — изменения появятся здесь."
                : "Напишите ИИ, какой дом вы хотите, — изменения появятся здесь.";
        }

        /// <summary>
        /// Brings the client's app to the front (`open -a`). `open` exits non-zero when the app is missing: that is
        /// watched for a few seconds on the root's scheduler (the popover is gone by then) and reported with a toast.
        /// </summary>
        public static void OpenApp(AppUI ui, AiClients.Client c)
        {
            string app = AppName(c), name = ClientShort(c);
            System.Diagnostics.Process proc;
            try
            {
                if (string.IsNullOrEmpty(app) || !IsMac) throw new InvalidOperationException("no app to open");
                var info = new System.Diagnostics.ProcessStartInfo("/usr/bin/open", "-a \"" + app + "\"")
                {
                    UseShellExecute = false,
                    CreateNoWindow = true,
                };
                proc = System.Diagnostics.Process.Start(info);
                if (proc == null) throw new InvalidOperationException("open did not start");
            }
            catch (Exception e)
            {
                Debug.LogWarning("[AiPopover] open " + app + ": " + e.Message);
                ui.Toast("Не удалось открыть " + name, IconKind.Error, ToastKind.Error);
                return;
            }

            float until = Time.unscaledTime + 5f;
            IVisualElementScheduledItem watch = null;
            watch = ui.Root.schedule.Execute(() =>
            {
                bool exited;
                try { exited = proc.HasExited; }
                catch (Exception) { exited = true; }
                if (!exited && Time.unscaledTime < until) return;
                watch?.Pause();
                int code = 0;
                try { if (exited) code = proc.ExitCode; }
                catch (Exception) { code = 0; }
                proc.Dispose();
                if (code != 0)
                {
                    Debug.LogWarning("[AiPopover] open -a \"" + app + "\" exited with " + code);
                    ui.Toast("Не удалось открыть " + name, IconKind.Error, ToastKind.Error);
                }
            }).Every(100);
        }

        /// <summary>Leading spaces → no-break spaces, so the indentation of JSON/TOML survives text layout.</summary>
        public static string KeepIndent(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            var sb = new StringBuilder(s.Length);
            var lines = s.Replace("\r", "").Split('\n');
            for (int n = 0; n < lines.Length; n++)
            {
                string line = lines[n];
                int i = 0;
                while (i < line.Length && line[i] == ' ') { sb.Append('\u00A0'); i++; }
                sb.Append(line, i, line.Length - i);
                if (n < lines.Length - 1) sb.Append('\n');
            }
            return sb.ToString();
        }
    }

    /// <summary>Empty plot glyph (Painter2D): a dashed boundary with a small plus, in the element's colour.</summary>
    internal sealed class DlgPlotGlyph : VisualElement
    {
        Color _drawn;

        public DlgPlotGlyph()
        {
            AddToClassList("dlg-plot");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            schedule.Execute(() => { if (resolvedStyle.color != _drawn) MarkDirtyRepaint(); }).Every(120);
        }

        void Draw(MeshGenerationContext ctx)
        {
            var r = contentRect;
            if (r.width < 8f || r.height < 8f) return;
            var p = ctx.painter2D;
            _drawn = resolvedStyle.color;
            p.strokeColor = _drawn;
            p.lineWidth = 1.2f;
            p.lineCap = LineCap.Round;
            float w = Mathf.Min(r.width - 12f, 36f), h = Mathf.Min(r.height - 10f, 24f);
            var c = r.center;
            var a = new Vector2(c.x - w * 0.5f, c.y - h * 0.5f);
            var b = new Vector2(c.x + w * 0.5f, c.y - h * 0.5f);
            var d = new Vector2(c.x + w * 0.5f, c.y + h * 0.5f);
            var e = new Vector2(c.x - w * 0.5f, c.y + h * 0.5f);
            Dashed(p, a, b);
            Dashed(p, b, d);
            Dashed(p, d, e);
            Dashed(p, e, a);
            p.lineWidth = 1.4f;
            p.BeginPath();
            p.MoveTo(c + new Vector2(-3.5f, 0f));
            p.LineTo(c + new Vector2(3.5f, 0f));
            p.Stroke();
            p.BeginPath();
            p.MoveTo(c + new Vector2(0f, -3.5f));
            p.LineTo(c + new Vector2(0f, 3.5f));
            p.Stroke();
        }

        static void Dashed(Painter2D p, Vector2 from, Vector2 to)
        {
            const float Dash = 3f, Gap = 2.6f;
            float len = Vector2.Distance(from, to);
            if (len <= 0f) return;
            var dir = (to - from) / len;
            for (float t = 0f; t < len; t += Dash + Gap)
            {
                p.BeginPath();
                p.MoveTo(from + dir * t);
                p.LineTo(from + dir * Mathf.Min(t + Dash, len));
                p.Stroke();
            }
        }
    }

    /// <summary>
    /// ArrowUpRight 16 for «Открыть {приложение}» (IconKind has none): Painter2D on the 24 grid, stroke 1.6, round
    /// caps — (7,17)→(17,7) and (9,7)→(17,7)→(17,15). Follows the element's colour like <see cref="Icon"/>.
    /// </summary>
    internal sealed class DlgArrowUpRight : VisualElement
    {
        Color _drawn;

        public DlgArrowUpRight()
        {
            AddToClassList("icon");
            AddToClassList("icon-16");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            // hover styles recolour the row; generated content does not follow by itself
            schedule.Execute(() => { if (resolvedStyle.color != _drawn && ProgressRing.VisibleInHierarchy(this)) MarkDirtyRepaint(); }).Every(80);
        }

        void Draw(MeshGenerationContext ctx)
        {
            var r = contentRect;
            float s = Mathf.Min(r.width, r.height) / 24f;
            if (s <= 0f) return;
            var o = new Vector2(r.x + (r.width - 24f * s) * 0.5f, r.y + (r.height - 24f * s) * 0.5f);
            var p = ctx.painter2D;
            _drawn = resolvedStyle.color;
            p.strokeColor = _drawn;
            p.lineWidth = Mathf.Max(1.1f, 1.6f * s);
            p.lineCap = LineCap.Round;
            p.lineJoin = LineJoin.Round;
            p.BeginPath();
            p.MoveTo(o + new Vector2(7f, 17f) * s);
            p.LineTo(o + new Vector2(17f, 7f) * s);
            p.Stroke();
            p.BeginPath();
            p.MoveTo(o + new Vector2(9f, 7f) * s);
            p.LineTo(o + new Vector2(17f, 7f) * s);
            p.LineTo(o + new Vector2(17f, 15f) * s);
            p.Stroke();
        }
    }

    /// <summary>Delete confirmation (w 420): ↩ keeps the project (default focus on «Отмена»), «Удалить» moves it to Trash.</summary>
    public sealed class DeleteProjectDialog : Modal
    {
        readonly string _id;
        bool _done;

        public DeleteProjectDialog(AppUI ui, string projectId)
            : base(ui, $"Удалить «{ui.NameOf(projectId)}»?",
                "Проект переместится в папку «Trash» рядом с папкой проектов — вернуть его можно вручную.", 420)
        {
            _id = projectId;
            Card.AddToClassList("dlg-compact");
            Head.Q<Label>(className: "t-title")?.AddToClassList("wrap");

            var cancel = Ui.Button(ButtonKind.Secondary, "Отмена", Close, null, "dlg-default");
            Tooltips.Tip(cancel, "Оставить проект", "↩");
            var delete = Ui.Button(ButtonKind.Danger, "Удалить", Delete);
            Tooltips.Tip(delete, "Переместить проект в «Trash»", null, "Папка «Trash» лежит рядом с папкой проектов");
            Foot.Add(cancel);
            Foot.Add(delete);
            Primary = Close;          // destructive: ↩ does what the focused «Отмена» does
        }

        void Delete()
        {
            if (_done) return;
            _done = true;
            Close();
            Ui_.DeleteProject(_id);
        }
    }

    /// <summary>
    /// Keyboard shortcuts sheet (? / F1), w 720, three columns of h 32 rows (spec §6, §8). Copy matches the rest of
    /// the app (toolbar tooltips, Home, hint strip). Columns size to their widest row, so no label is cut.
    /// </summary>
    public sealed class ShortcutsDialog : Modal
    {
        // "#Caption" starts a group; rows are "label|keys": space-separated keycaps (adjacent = chord), " / " between
        // alternatives (text-3 separator), mouse glyphs by name
        static readonly string[][] Columns =
        {
            new[]
            {
                "#Общие",
                "Все проекты|⌘ O", "Новый проект|⌘ N", "Настройки|⌘ ,", "Отменить правку|⌘ Z",
                "Снимок|⌘ ⇧ S", "Полный экран|⌃ ⌘ F", "Скрыть интерфейс|H", "Горячие клавиши|? / F1",
                "#Мебель",
                "Библиотека|B", "Повернуть|R / ⇧ R", "Удалить|⌫", "Копия|⌘ D", "Сдвинуть|← ↑ → ↓", "Без привязки|⌥",
            },
            new[]
            {
                "#Камера",
                "Режим камеры|⌘ 1–3", "Сменить режим|Tab / ⇧ Tab", "Вид|1–9", "Соседний вид|[ / ]",
                "Виды|V", "План этажа|M", "Большой план|P", "Этаж|PgUp / PgDn", "К дому|F",
                "#Мышь",
                "Вращать|MouseLeft", "Сдвиг|MouseRight", "Масштаб|MouseWheel",
            },
            new[]
            {
                "#Прогулка",
                "Идти|W A S D", "Бег|Shift", "Прыжок|Space", "Присесть|C", "Дверь|E",
                "Осмотреться|MouseLeft", "Отпустить мышь|Esc",
                "#Полёт",
                "Лететь|W A S D", "Вверх / вниз|E / Q", "Быстрее|Shift",
                "#Все проекты",
                "Поиск|⌘ F", "Переименовать|F2", "Удалить проект|⌘ ⌫",
            },
        };

        public ShortcutsDialog(AppUI ui) : base(ui, "Горячие клавиши", null, 720)
        {
            Card.AddToClassList("dlg-shortcuts");
            var grid = Ui.El("dlg-sc");
#if UNITY_EDITOR || DEVELOPMENT_BUILD
            // dev check: any label narrower than its text is being cut or wrapped
            EventCallback<GeometryChangedEvent> check = null;
            check = e =>
            {
                float w = grid.resolvedStyle.width;
                if (float.IsNaN(w) || w <= 0f) return;
                grid.UnregisterCallback(check);
                ReportTruncated(grid);
            };
            grid.RegisterCallback(check);
#endif
            for (int c = 0; c < Columns.Length; c++)
            {
                var col = Ui.El("dlg-sc-col");
                if (c == Columns.Length - 1) col.AddToClassList("last");
                bool first = true;
                foreach (var entry in Columns[c])
                {
                    if (entry.StartsWith("#", StringComparison.Ordinal))
                    {
                        var cap = Ui.Text(entry.Substring(1), "dlg-sc-caption");
                        if (!first) cap.AddToClassList("later");
                        col.Add(cap);
                        first = false;
                        continue;
                    }
                    int bar = entry.IndexOf('|');
                    string label = entry.Substring(0, bar), keys = entry.Substring(bar + 1);
                    col.Add(Ui.El("dlg-sc-row", Ui.Text(label, "dlg-sc-label"), Ui.Keys(keys)));
                }
                grid.Add(col);
            }
            Body.Add(grid);

            Foot.AddToClassList("dlg-sc-foot");
            Foot.Add(Ui.El("dlg-footnote", Ui.Icon(IconKind.Keyboard, 16), Ui.Text("Клавиши-буквы работают в любой раскладке", "dlg-footnote-text")));
            var done = Ui.Button(ButtonKind.Secondary, "Закрыть", Close);
            Tooltips.Tip(done, "Закрыть справку", "Esc");
            Foot.Add(done);
            Primary = Close;
        }

        /// <summary>
        /// Logs every shortcut label under <paramref name="root"/> whose text is wider than its laid-out width (cut or
        /// wrapped); returns how many. Runs by itself in the editor and development builds when the sheet opens;
        /// UiShot/UiTour can call it on <c>ui.Root</c> after the layout pass.
        /// </summary>
        public static int ReportTruncated(VisualElement root)
        {
            int bad = 0;
            if (root == null) return 0;
            root.Query<Label>(className: "dlg-sc-label").ForEach(l =>
            {
                float have = l.resolvedStyle.width;
                if (float.IsNaN(have)) return;
                var need = l.MeasureTextSize(l.text, 0, VisualElement.MeasureMode.Undefined, 0, VisualElement.MeasureMode.Undefined);
                if (need.x <= have + 0.5f) return;
                bad++;
                Debug.LogWarning($"[Shortcuts] label «{l.text}» needs {need.x:0.#} px, has {have:0.#} px");
            });
            return bad;
        }
    }
}
