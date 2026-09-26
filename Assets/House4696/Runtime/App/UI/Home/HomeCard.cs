using System.Text;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// One project in the Home grid (spec §5, "no box"): a 16:10 thumbnail (radius 12, 1 px border, image scales to 1.03
    /// on hover, «Открыт» badge, «⋯» menu button), the name (tooltip = full name + description) and a meta line with the
    /// age on the right. Click opens, right click / «⋯» opens the context menu; F2 turns the name into an inline field.
    /// The thumbnail texture is the background of the rounded frame itself (not a child clipped by overflow:hidden, which
    /// is a stencil mask: stair-stepped corners and the image over the border); the hover zoom animates background-size.
    /// Sizes are set by <see cref="HomeScreen"/> (the grid computes the columns).
    /// </summary>
    internal sealed class HomeCard
    {
        const string InputClass = "unity-base-text-field__input";
        static readonly Color Accent = new Color32(0x4B, 0x5C, 0xF0, 0xFF);
        static readonly Color FieldBg = new Color32(0x10, 0x11, 0x14, 0xFF);
        // name tooltip: the text column is .tip max-width 320 − 2×10 padding − 2×1 border (Components.uss) = 298,
        // measured against 294 for a safety margin; the description gets at most 3 lines (spec §5)
        const float TipTextWidth = 294f;
        const int TipMaxLines = 3;

        readonly HomeScreen _home;
        public readonly VisualElement Root;
        readonly VisualElement _thumb, _empty, _badge, _more, _nameRow;
        readonly Label _name, _meta, _ago;
        TextField _field;
        VisualElement _fieldWrap;
        Texture2D _tex;
        bool _hasTex, _texKnown;
        float _width = -1f, _marginRight = -1f;
        string _haystack = "";
        string _tipDesc;                 // normalized description (or the broken-file note) waiting to be fitted
        bool _tipFitted;                 // the tooltip sub-line was fitted to TipMaxLines by measuring

        public ProjectInfo Info { get; private set; }
        public string Id => Info.Id;
        /// <summary>The name shown (the id when the project has no name).</summary>
        public string DisplayName { get; private set; }
        public bool Renaming => _field != null;
        /// <summary>The «⋯» button (menu anchor).</summary>
        public VisualElement MoreButton => _more;

        public HomeCard(HomeScreen home, ProjectInfo info)
        {
            _home = home;

            _empty = Ui.El("home-thumb-empty", Ui.Icon(IconKind.House, 32),
                Ui.Text("Превью появится после расчёта света", "t-caption home-thumb-empty-text"));
            _empty.pickingMode = PickingMode.Ignore;
            _badge = Ui.El("home-open-badge", Ui.El("home-open-dot"), Ui.Text("Открыт", "t-micro home-open-text"));
            _badge.pickingMode = PickingMode.Ignore;
            Ui.Show(_badge, false);
            _more = Ui.IconButton(IconKind.More, () => _home.ShowCardMenu(this, null), "Действия с проектом", null,
                ButtonKind.Ghost, "btn-xs home-more", 16);
            _thumb = Ui.El("home-thumb", _empty, _badge, _more);
            var ring = Ui.El("home-ring");
            ring.pickingMode = PickingMode.Ignore;
            var thumbWrap = Ui.El("home-thumb-wrap", _thumb, ring);

            _name = Ui.Text("", "t-headline home-name ellipsis");
            _name.enableRichText = false;                          // names come from the AI / user: "<b>" is text
            _name.pickingMode = PickingMode.Position;              // hover target of the name/description tooltip
            _name.RegisterCallback<PointerEnterEvent>(_ => FitTip());  // measure once the text styles are resolved
            _nameRow = Ui.El("home-name-row", _name);
            // while renaming, presses in the field must not reach the card (it would open the project)
            _nameRow.RegisterCallback<PointerDownEvent>(e => { if (_field != null) e.StopPropagation(); });
            _nameRow.RegisterCallback<PointerUpEvent>(e => { if (_field != null) e.StopPropagation(); });

            _meta = Ui.Text("", "t-caption c-2 home-meta ellipsis");
            _ago = Ui.Text("", "t-caption c-3 home-ago");
            var metaRow = Ui.El("home-meta-row", _meta, _ago);
            metaRow.pickingMode = PickingMode.Ignore;

            Root = Ui.El("home-card", thumbWrap, _nameRow, metaRow);
            Ui.OnClick(Root, () => _home.OpenCard(this));
            Root.RegisterCallback<PointerUpEvent>(OnPointerUp);
            Root.RegisterCallback<PointerEnterEvent>(_ => _home.CardHover(this, true));
            Root.RegisterCallback<PointerLeaveEvent>(_ => _home.CardHover(this, false));

            Update(info);
        }

        void OnPointerUp(PointerUpEvent e)
        {
            if (e.button != 1 || _field != null) return;
            e.StopPropagation();
            _home.ShowCardMenu(this, new Vector2(e.position.x, e.position.y));
        }

        /// <summary>Takes new data (name, meta, description); an open inline rename keeps its text.</summary>
        public void Update(ProjectInfo info)
        {
            Info = info;
            DisplayName = string.IsNullOrWhiteSpace(info.Name) ? info.Id : info.Name.Trim();
            if (_field == null) _name.text = DisplayName;

            string desc = info.Description;
            bool broken = info.Levels == 0 && desc != null && desc.StartsWith("не читается", System.StringComparison.Ordinal);
            // title = the full name (the card truncates it), sub-line = the description, fitted to 3 lines on first hover
            _tipDesc = broken ? "Файл проекта не читается" : OneLine(desc);
            _tipFitted = false;
            Tooltips.Tip(_name, DisplayName, null, Clip(_tipDesc, 110));
            _meta.text = broken ? "Не удалось прочитать проект" : MetaText(info);
            _meta.EnableInClassList("c-warning", broken);
            _haystack = HomeScreen.Normalize(DisplayName + " " + (broken ? "" : desc ?? ""));
            RefreshAgo();
        }

        /// <summary>Re-computes «9 ч назад» (called every 30 s while Home is open).</summary>
        public void RefreshAgo()
        {
            string ago = Ui.Ago(Info.Modified);
            if (_ago.text != ago) _ago.text = ago;
        }

        /// <summary>Shows the name label again with this text (after a rename that did not stick).</summary>
        public void SetName(string name)
        {
            if (_field == null) _name.text = string.IsNullOrWhiteSpace(name) ? Info.Id : name;
        }

        /// <summary>True when every search token occurs in the name or the description.</summary>
        public bool Matches(System.Collections.Generic.List<string> tokens)
        {
            for (int i = 0; i < tokens.Count; i++)
                if (_haystack.IndexOf(tokens[i], System.StringComparison.Ordinal) < 0) return false;
            return true;
        }

        public void SetThumb(Texture2D tex)
        {
            bool has = tex != null;
            if (_texKnown && has == _hasTex && ReferenceEquals(tex, _tex)) return;
            _texKnown = true;
            _tex = tex;
            _hasTex = has;
            // the frame's own background: anti-aliased rounded corners, the 1 px border draws on top (see Home.uss)
            _thumb.style.backgroundImage = has ? new StyleBackground(tex) : new StyleBackground(StyleKeyword.None);
            Ui.Show(_empty, !has);
        }

        public void SetOpen(bool open) => Ui.Show(_badge, open);

        public void SetHighlight(bool on) => Root.EnableInClassList("highlight", on);

        /// <summary>Card width and right gap (0 in the last column); the thumbnail keeps 16:10.</summary>
        public void SetSize(float width, float marginRight)
        {
            if (Mathf.Approximately(width, _width) && Mathf.Approximately(marginRight, _marginRight)) return;
            _width = width;
            _marginRight = marginRight;
            Root.style.width = width;
            Root.style.marginRight = marginRight;
            _thumb.style.height = Mathf.Round(width * 0.625f);
        }

        // ------------------------------------------------------------------ inline rename
        /// <summary>Replaces the name with a field holding the current name (the caller focuses it).</summary>
        public TextField StartRename()
        {
            if (_field != null) return _field;
            var f = new TextField { maxLength = 80 };
            f.AddToClassList("home-rename");
            f.SetValueWithoutNotify(DisplayName);
            // the runtime theme styles hover/focus of text inputs with strong selectors: the look is set inline
            var input = f.Q(className: InputClass);
            if (input != null)
            {
                input.style.backgroundColor = FieldBg;
                input.style.borderTopColor = Accent;
                input.style.borderRightColor = Accent;
                input.style.borderBottomColor = Accent;
                input.style.borderLeftColor = Accent;
                input.style.borderTopWidth = 1f;
                input.style.borderRightWidth = 1f;
                input.style.borderBottomWidth = 1f;
                input.style.borderLeftWidth = 1f;
            }
            _field = f;
            _fieldWrap = Ui.El("home-rename-wrap", f);        // 2 px accent-halo ring around the field
            Ui.Show(_name, false);
            _nameRow.Add(_fieldWrap);
            Root.AddToClassList("renaming");
            Tooltips.HideNow();
            return f;
        }

        public string RenameText => _field?.value;

        /// <summary>Removes the field and shows the name label again.</summary>
        public void EndRename()
        {
            if (_field == null) return;
            var wrap = _fieldWrap;
            _field = null;
            _fieldWrap = null;
            wrap?.RemoveFromHierarchy();
            _name.text = DisplayName;
            Ui.Show(_name, true);
            Root.RemoveFromClassList("renaming");
        }

        // ------------------------------------------------------------------ text
        /// <summary>«212 м² · 2 этажа · 16 комнат»; «Пустой участок» for a house without rooms.</summary>
        static string MetaText(ProjectInfo i)
        {
            if (i.Rooms == 0 && i.Area <= 0f)
                return i.Levels > 1 ? "Пустой участок · " + Ui.Plural(i.Levels, "этаж", "этажа", "этажей") : "Пустой участок";
            var sb = new StringBuilder(48);
            if (i.Area > 0f) sb.Append(Ui.Area(i.Area));
            if (i.Levels > 0)
            {
                if (sb.Length > 0) sb.Append(" · ");
                sb.Append(Ui.Plural(i.Levels, "этаж", "этажа", "этажей"));
            }
            if (i.Rooms > 0)
            {
                if (sb.Length > 0) sb.Append(" · ");
                sb.Append(Ui.Plural(i.Rooms, "комната", "комнаты", "комнат"));
            }
            return sb.ToString();
        }

        /// <summary>One line of text: trimmed, line breaks as spaces; null when empty.</summary>
        static string OneLine(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return null;
            return text.Trim().Replace("\r", "").Replace('\n', ' ');
        }

        /// <summary>
        /// Character-count fallback before the card has resolved styles: 110 chars stay within 3 lines of Caption 12 at
        /// the tooltip width (≈ 45 chars a line after word wrap).
        /// </summary>
        static string Clip(string text, int max)
        {
            if (text == null || text.Length <= max) return text;
            int cut = text.LastIndexOf(' ', max);
            if (cut < max / 2) cut = max;
            return Ellipsize(text.Substring(0, cut));
        }

        static string Ellipsize(string text) => text.TrimEnd(' ', ',', '.', ';', ':', '—', '-') + "…";

        /// <summary>
        /// Fits the tooltip description to <see cref="TipMaxLines"/> lines by measuring it word by word with the meta
        /// label (Caption 12 Regular — the same font and size as the tooltip's sub-line). Runs once per description,
        /// on the first hover of the name, so the text styles are resolved.
        /// </summary>
        void FitTip()
        {
            if (_tipFitted || _field != null || _meta.panel == null) return;
            if (float.IsNaN(Ui.Measure(_meta, "…"))) return;       // font not resolved yet: try on the next hover
            _tipFitted = true;
            Tooltips.Tip(_name, DisplayName, null, FitLines(_tipDesc, _meta, TipTextWidth, TipMaxLines));
        }

        /// <summary>
        /// Greedy word wrap as the tooltip will lay the text out; when it needs more than <paramref name="maxLines"/>
        /// lines the text is cut after the last word that fits on the last line, with «…». Conservative: the text engine
        /// may also break after hyphens, which only makes its lines fuller.
        /// </summary>
        static string FitLines(string text, Label reference, float width, int maxLines)
        {
            if (text == null) return null;
            if (Ui.Measure(reference, text) <= width) return text;

            var words = text.Split(' ');
            var done = new StringBuilder(text.Length);   // the full lines before the current one
            string line = "";
            int lines = 1;
            for (int i = 0; i < words.Length; i++)
            {
                string word = words[i];
                if (word.Length == 0) continue;
                string candidate = line.Length == 0 ? word : line + " " + word;
                if (Ui.Measure(reference, candidate) <= width) { line = candidate; continue; }

                // the word starts a new line (a word wider than a line breaks inside itself and takes several)
                int wordLines = line.Length == 0 ? 0 : 1;
                float wordWidth = Ui.Measure(reference, word);
                int extra = Mathf.Max(0, Mathf.CeilToInt(wordWidth / width) - 1);
                if (lines + wordLines + extra > maxLines)
                {
                    // out of lines: keep what fits on the last one, then «…»
                    if (line.Length == 0) line = word;
                    while (Ui.Measure(reference, line + "…") > width)
                    {
                        int cut = line.LastIndexOf(' ');
                        if (cut <= 0) { line = TrimToWidth(line, reference, width); break; }
                        line = line.Substring(0, cut);
                    }
                    if (done.Length > 0) done.Append(' ');
                    return done.Append(Ellipsize(line)).ToString();
                }
                if (line.Length > 0)
                {
                    if (done.Length > 0) done.Append(' ');
                    done.Append(line);
                }
                lines += wordLines + extra;
                line = word;
            }
            return text;
        }

        /// <summary>Drops characters until the text plus «…» fits (one very long word on the last line).</summary>
        static string TrimToWidth(string text, Label reference, float width)
        {
            int n = text.Length;
            while (n > 1 && Ui.Measure(reference, text.Substring(0, n) + "…") > width) n--;
            return text.Substring(0, n);
        }
    }
}
