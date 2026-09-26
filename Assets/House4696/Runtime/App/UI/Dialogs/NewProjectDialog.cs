using System;
using System.Collections.Generic;
using System.IO;
using House4696.Model;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// New project (⌘N), w 560: name (autofocus; empty → the placeholder name), optional description and the base —
    /// an empty plot or a bundled sample house (radio rows h 56 with a 64×40 tile). ↩ creates, Esc cancels,
    /// double-click on a base row creates at once.
    /// </summary>
    public sealed class NewProjectDialog : Modal
    {
        const string EmptyTemplate = "empty";
        const string BaseName = "Новый проект";

        readonly TextField _name, _desc;
        readonly string _defaultName;
        readonly List<(string key, VisualElement row)> _options = new List<(string, VisualElement)>();
        string _template = EmptyTemplate;
        bool _done;

        public NewProjectDialog(AppUI ui)
            : base(ui, "Новый проект", "Дом построит ваш ИИ-ассистент — начните с пустого участка или готового дома.", 560)
        {
            Card.AddToClassList("dlg-new");
            _defaultName = DefaultName(ui);

            // name
            var nameInput = Ui.Input(_defaultName, out _name);
            _name.maxLength = 80;
            Tooltips.Tip(nameInput, "Название проекта", null, "Если оставить поле пустым — «" + _defaultName + "»");
            Body.Add(Dlg.Field("Название", null, nameInput));

            // description
            var descInput = Ui.Input("Пара слов о доме — ИИ это прочтёт", out _desc, true);
            _desc.maxLength = 600;
            Tooltips.Tip(descInput, "Описание проекта", null, "ИИ-ассистент прочтёт его, когда откроет проект");
            Body.Add(Dlg.Field("Описание", "необязательно", descInput));

            // base: empty plot + bundled samples
            var rows = new List<VisualElement>
            {
                Option(EmptyTemplate, "Пустой участок", "ИИ построит дом с нуля", Ui.El("dlg-radio-tile plot", new DlgPlotGlyph()),
                    "Пустой участок с одним этажом", "Опишите дом ИИ-ассистенту — он построит его здесь"),
            };
            foreach (var t in Templates.Load())
                rows.Add(Option(t.Key, t.Name, t.Meta, TemplateTile(ui, t), t.Name,
                    string.IsNullOrEmpty(t.Description) ? "Готовый дом — ИИ продолжит с него" : t.Description));
            rows[rows.Count - 1].AddToClassList("last");

            VisualElement list;
            if (rows.Count > 4)
            {
                var scroll = new ScrollView(ScrollViewMode.Vertical)
                {
                    horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                    verticalScrollerVisibility = ScrollerVisibility.Auto,
                };
                scroll.AddToClassList("dlg-templates-scroll");
                list = scroll;
            }
            else list = Ui.El("dlg-templates");
            foreach (var r in rows) list.Add(r);
            Body.Add(Dlg.Field("Основа", null, list, "last"));
            SelectTemplate(EmptyTemplate);

            // footer
            Foot.Add(Ui.El("dlg-footnote ai", Ui.Icon(IconKind.Sparkle, 14), Ui.Text("Дальше дом строит ваш ИИ-ассистент", "dlg-footnote-text")));
            var cancel = Ui.Button(ButtonKind.Secondary, "Отмена", Close);
            Tooltips.Tip(cancel, "Закрыть без создания", "Esc");
            var create = Ui.Button(ButtonKind.Primary, "Создать проект", Create);
            Tooltips.Tip(create, "Создать и открыть проект", "↩");
            Foot.Add(cancel);
            Foot.Add(create);
            Primary = Create;
        }

        public override void OnShown()
        {
            _name.Focus();
            // the shell is still scaling in; focus again once it has settled (the first call can land before layout)
            _name.schedule.Execute(() => { if (!_done && _name.panel != null) _name.Focus(); }).ExecuteLater(60);
        }

        VisualElement Option(string key, string name, string meta, VisualElement tile, string tip, string tipSub)
        {
            var row = Ui.El("dlg-radio");
            tile.pickingMode = PickingMode.Ignore;
            row.Add(tile);
            var text = Ui.El("dlg-radio-text", Dlg.Plain(name, "dlg-radio-name"), Dlg.Plain(meta, "dlg-radio-meta"));
            text.pickingMode = PickingMode.Ignore;
            row.Add(text);
            row.Add(Ui.Icon(IconKind.Check, 16, "dlg-radio-check"));
            Ui.OnClick(row, () => SelectTemplate(key));
            row.RegisterCallback<PointerDownEvent>(e =>
            {
                if (e.button == 0 && e.clickCount == 2) { SelectTemplate(key); Create(); }
            }, TrickleDown.TrickleDown);
            Tooltips.Tip(row, tip, null, tipSub);
            _options.Add((key, row));
            return row;
        }

        void SelectTemplate(string key)
        {
            _template = key;
            foreach (var (k, row) in _options) row.EnableInClassList("selected", k == key);
        }

        void Create()
        {
            if (_done) return;
            _done = true;
            string name = _name.value?.Trim();
            if (string.IsNullOrEmpty(name)) name = _defaultName;
            string desc = _desc.value?.Trim();
            string template = _template;
            Close();
            Ui_.CreateProject(name, string.IsNullOrEmpty(desc) ? null : desc, template);
        }

        /// <summary>«Новый проект N»: one more than the highest N already used.</summary>
        static string DefaultName(AppUI ui)
        {
            int max = 0;
            try
            {
                foreach (var p in ui.S.Session.Store.List())
                {
                    string n = p.Name?.Trim();
                    if (string.IsNullOrEmpty(n) || !n.StartsWith(BaseName, StringComparison.Ordinal)) continue;
                    string rest = n.Substring(BaseName.Length).Trim();
                    if (rest.Length == 0) max = Math.Max(max, 1);
                    else if (int.TryParse(rest, out int k) && k > 0) max = Math.Max(max, k);
                }
            }
            catch (Exception e) { Debug.LogWarning("[NewProject] list: " + e.Message); }
            return BaseName + " " + (max + 1);
        }

        /// <summary>Template tile: the sample's own preview when its seeded copy is unchanged, else House on press.</summary>
        static VisualElement TemplateTile(AppUI ui, Templates.Info t)
        {
            var tile = Ui.El("dlg-radio-tile");
            var tex = Templates.Thumb(ui, t);
            if (tex != null)
            {
                tile.style.backgroundImage = new StyleBackground(tex);
                tile.AddToClassList("image");
            }
            else tile.Add(Ui.Icon(IconKind.House, 20));
            return tile;
        }

        /// <summary>Bundled sample houses (StreamingAssets/Samples) with their meta line; parsed once per file version.</summary>
        static class Templates
        {
            public sealed class Info
            {
                public string Key, Name, Description, Meta;
                public int Levels, Rooms;
                public float Area;
            }

            static readonly Dictionary<string, (DateTime time, Info info)> Cache = new Dictionary<string, (DateTime, Info)>();

            public static List<Info> Load()
            {
                var list = new List<Info>();
                Dictionary<string, string> samples;
                try { samples = ProjectStore.Samples(); }
                catch (Exception e) { Debug.LogWarning("[NewProject] samples: " + e.Message); return list; }
                foreach (var kv in samples)
                {
                    try
                    {
                        var time = File.GetLastWriteTimeUtc(kv.Value);
                        if (!Cache.TryGetValue(kv.Key, out var hit) || hit.time != time || hit.info == null)
                        {
                            var doc = HouseJson.Deserialize(File.ReadAllText(kv.Value));
                            var pi = ProjectStore.Info(kv.Key, doc);
                            var info = new Info
                            {
                                Key = kv.Key, Name = string.IsNullOrWhiteSpace(pi.Name) ? kv.Key : pi.Name.Trim(),
                                Description = pi.Description, Levels = pi.Levels, Rooms = pi.Rooms, Area = pi.Area,
                            };
                            info.Meta = MetaLine(info);
                            hit = (time, info);
                            Cache[kv.Key] = hit;
                        }
                        list.Add(hit.info);
                    }
                    catch (Exception e) { Debug.LogWarning($"[NewProject] template {kv.Key}: {e.Message}"); }
                }
                list.Sort((a, b) => string.Compare(a.Name, b.Name, StringComparison.CurrentCulture));
                return list;
            }

            /// <summary>«Двухэтажный · 212 м² · 16 комнат».</summary>
            static string MetaLine(Info i)
            {
                string levels = i.Levels switch
                {
                    1 => "Одноэтажный",
                    2 => "Двухэтажный",
                    3 => "Трёхэтажный",
                    _ => Ui.Plural(i.Levels, "этаж", "этажа", "этажей"),
                };
                var parts = new List<string>(3) { levels };
                if (i.Area > 0f) parts.Add(Ui.Area(i.Area));
                if (i.Rooms > 0) parts.Add(Ui.Plural(i.Rooms, "комната", "комнаты", "комнат"));
                return string.Join(" · ", parts);
            }

            /// <summary>
            /// The seeded copy of a sample (same id) has a preview once it was opened; used only while the copy still
            /// looks like the sample (same name, levels and rooms), so an edited copy never poses as the template.
            /// </summary>
            public static Texture2D Thumb(AppUI ui, Info t)
            {
                try
                {
                    var store = ui.S?.Session?.Store;
                    if (store == null || ui.S.Thumbs == null || !store.Exists(t.Key)) return null;
                    var mine = ProjectStore.Info(t.Key, store.Load(t.Key));
                    if ((mine.Name ?? "").Trim() != t.Name || mine.Levels != t.Levels || mine.Rooms != t.Rooms) return null;
                    return ui.S.Thumbs.Get(t.Key);
                }
                catch (Exception) { return null; }
            }
        }
    }
}
