using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// The furniture library (B, toolbar «Мебель»): a panel on the left with a search field, the categories (with counts) in a
    /// rail and the models of the chosen one as cards — picture, name, size. A click on a card starts placing the model (the
    /// next click in the house puts it down), a card dragged into the view goes down where it is dropped. While the panel is
    /// open the 3D view edits furniture (<see cref="FurnitureEditor"/>); the footer says what the mouse and keys do right now.
    /// </summary>
    public sealed class LibraryPanel
    {
        public const float Width = 440f;
        const float Gutter = 16f;
        const float DragStart = 6f;
        const int FadeMs = 180;
        const string Keys = "B";

        readonly AppUI _ui;
        readonly FurnitureEditor _editor;
        readonly VisualElement _host, _rail, _grid, _empty;
        readonly ScrollView _scroll;
        readonly TextField _search;
        readonly Label _count, _foot, _emptyTitle, _emptyText;
        readonly Dictionary<string, VisualElement> _rows = new Dictionary<string, VisualElement>();
        readonly Dictionary<FurnitureCatalog.Entry, Card> _cards = new Dictionary<FurnitureCatalog.Entry, Card>();
        FurnitureCatalog _catalog;
        string _category;           // null = all models
        string _query = "";
        bool _shown;
        Card _active;

        public VisualElement Element { get; }
        public bool IsOpen { get; private set; }
        /// <summary>Panel px the chrome at the bottom keeps clear of on the left while the panel is on screen (0 when closed).</summary>
        public float Reserve => _shown ? Gutter + Width + Gutter : 0f;

        public LibraryPanel(AppUI ui, FurnitureEditor editor)
        {
            _ui = ui;
            _editor = editor;
            Element = Ui.El("layer lib-layer");
            Element.pickingMode = PickingMode.Ignore;

            // ---- head: title, count, close
            _count = Ui.Text("", "lib-count");
            var close = Ui.IconButton(IconKind.Close, Close, "Закрыть библиотеку", Keys, ButtonKind.Ghost, "btn-xs lib-close", 16);
            var head = Ui.El("lib-head", Ui.El("lib-titles", Ui.Text("Мебель и декор", "t-headline"), _count), close);

            // ---- search
            var search = Ui.Input("Найти: диван, лампа, ваза…", out _search, false, IconKind.Search);
            search.AddToClassList("lib-search");
            _search.RegisterValueChangedCallback(e => SetQuery(e.newValue));
            _search.RegisterCallback<KeyDownEvent>(OnSearchKey, TrickleDown.TrickleDown);

            // ---- body: category rail + card grid
            _rail = Ui.El("lib-rail");
            _grid = Ui.El("lib-grid");
            _scroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Auto,
                mouseWheelScrollSize = 60f,
            };
            _scroll.AddToClassList("lib-scroll");
            _scroll.Add(_grid);
            _emptyTitle = Ui.Text("Ничего не нашлось", "lib-empty-title");
            _emptyText = Ui.Text("Попробуйте другое слово: «кресло», «светильник», «растение»", "lib-empty-text");
            _empty = Ui.El("lib-empty", Ui.Icon(IconKind.Search, 24, "lib-empty-icon"), _emptyTitle, _emptyText);
            _empty.pickingMode = PickingMode.Ignore;
            Ui.Show(_empty, false);
            var content = Ui.El("lib-content", _scroll, _empty);
            var body = Ui.El("lib-body", _rail, content);

            // ---- footer: what the mouse does now
            _foot = Ui.Text("", "lib-foot-text");
            var foot = Ui.El("lib-foot", _foot);

            var panel = Ui.El("float lib", head, search, body, foot);
            _host = Elevation.Wrap(panel, 12, 16, 4f, 0.45f, "lib-host");
            Ui.Show(_host, false);
            Element.Add(_host);

            _editor.Changed += SyncState;
        }

        // ------------------------------------------------------------------ open / close
        public void Toggle()
        {
            if (IsOpen) Close();
            else Open();
        }

        public void Open()
        {
            var s = _ui.S;
            if (IsOpen || s?.Session == null || !s.Session.HasProject) return;
            IsOpen = true;
            EnsureBuilt();
            _editor.SetActive(true);
            SyncState();
            Apply();
            _ui.OnLibraryOpened();
        }

        public void Close()
        {
            if (!IsOpen) return;
            IsOpen = false;
            _search.Blur();
            _editor.SetActive(false);
            Apply();
        }

        /// <summary>Every frame: the panel shows while open with a project and the chrome up.</summary>
        public void Tick()
        {
            var s = _ui.S;
            if (IsOpen && (s == null || !s.Session.HasProject)) Close();
            Apply();
        }

        public void Refresh() => SyncState();

        void Apply()
        {
            bool want = IsOpen && _ui.S.Session.HasProject && !_ui.HomeOpen && !_ui.VeilVisible;
            if (want == _shown) return;
            _shown = want;
            Motion.Fade(_host, want, FadeMs, FadeMs, 8f);
        }

        // ------------------------------------------------------------------ content
        void EnsureBuilt()
        {
            if (_catalog != null) return;
            _catalog = FurnitureCatalog.Instance;
            _count.text = Ui.Plural(_catalog.All.Count, "модель", "модели", "моделей");
            AddRow(null, "Все модели", IconKind.Grid, _catalog.All.Count);
            foreach (var c in _catalog.Categories) AddRow(c.Id, c.Title, CategoryIcon(c.Id), c.Entries.Count);
            SelectCategory(null);
        }

        void AddRow(string id, string title, IconKind icon, int count)
        {
            var row = Ui.El("lib-cat", Ui.Icon(icon, 16, "lib-cat-icon"), Ui.Text(title, "lib-cat-name"), Ui.Text(count.ToString(), "lib-cat-count"));
            Ui.OnClick(row, () => SelectCategory(id));
            Tooltips.Tip(row, title, null, Ui.Plural(count, "модель", "модели", "моделей"));
            _rows[id ?? ""] = row;
            _rail.Add(row);
        }

        /// <summary>Shows one category (null = all models) and clears the search.</summary>
        public void SelectCategory(string id)
        {
            _category = id;
            if (_query.Length > 0)
            {
                _query = "";
                Ui.SetValue(_search, "");
            }
            Rebuild();
        }

        void SetQuery(string q)
        {
            _query = (q ?? "").Trim();
            Rebuild();
        }

        void OnSearchKey(KeyDownEvent e)
        {
            if (e.keyCode != KeyCode.Return && e.keyCode != KeyCode.KeypadEnter) return;
            // ↩ in the search: place the first model found
            var found = _query.Length > 0 ? _catalog.Search(_query) : null;
            if (found == null || found.Count == 0) return;
            e.StopPropagation();
            _search.Blur();
            _editor.BeginPlace(found[0], false);
        }

        /// <summary>The grid for the chosen category, all models by category, or the search results.</summary>
        void Rebuild()
        {
            if (_catalog == null) return;
            foreach (var kv in _rows) kv.Value.EnableInClassList("selected", _query.Length == 0 && kv.Key == (_category ?? ""));
            _rail.EnableInClassList("lib-rail-search", _query.Length > 0);
            _grid.Clear();
            int shown = 0;
            if (_query.Length > 0)
            {
                var found = _catalog.Search(_query);
                if (found.Count > 0) _grid.Add(Section("Найдено", found.Count));
                foreach (var e in found) { _grid.Add(CardOf(e).Root); shown++; }
            }
            else
            {
                foreach (var c in _catalog.Categories)
                {
                    if (_category != null && c.Id != _category) continue;
                    _grid.Add(Section(c.Title, c.Entries.Count));
                    foreach (var e in c.Entries) { _grid.Add(CardOf(e).Root); shown++; }
                }
            }
            Ui.Show(_empty, shown == 0);
            Ui.Show(_scroll, shown > 0);
            _scroll.scrollOffset = Vector2.zero;
        }

        static VisualElement Section(string title, int count)
        {
            var row = Ui.El("lib-section", Ui.Text(title, "lib-section-title"), Ui.Text(count.ToString(), "lib-section-count"));
            row.pickingMode = PickingMode.Ignore;
            return row;
        }

        Card CardOf(FurnitureCatalog.Entry e)
        {
            if (!_cards.TryGetValue(e, out var card))
            {
                card = new Card(this, e);
                _cards[e] = card;
            }
            return card;
        }

        /// <summary>The card of the model being placed is marked; the footer follows the editor's state.</summary>
        void SyncState()
        {
            var placing = _editor.Placing;
            var active = placing != null && _cards.TryGetValue(placing, out var c) ? c : null;
            if (active != _active)
            {
                _active?.Root.RemoveFromClassList("active");
                active?.Root.AddToClassList("active");
                _active = active;
            }
            string text;
            if (_editor.Current == FurnitureEditor.State.Placing)
                text = _editor.PlacingByDrag
                    ? "Отпустите кнопку там, где должна стоять модель. Колесо — повернуть."
                    : "Щёлкните в доме, куда поставить. R — повернуть, ⇧ — поставить ещё, Esc — отмена.";
            else if (_editor.Selected != null)
                text = "Перетащите предмет, чтобы передвинуть. R — повернуть, ⌫ — удалить, ⌘D — копия, ⌥ — двигать без привязки.";
            else
                text = "Выберите модель и щёлкните место в доме — или перетащите её туда. Предметы в доме можно двигать мышью.";
            _foot.text = text;
        }

        public static IconKind CategoryIcon(string id) => id switch
        {
            "seating" => IconKind.Sofa,
            "tables" => IconKind.Table,
            "storage" => IconKind.Wardrobe,
            "bedroom" => IconKind.Bed,
            "living" => IconKind.House,
            "kids" => IconKind.Sparkle,
            "hall" => IconKind.Door,
            "office" => IconKind.Pencil,
            "kitchen" => IconKind.Kitchen,
            _ when id != null && id.StartsWith("med_") => IconKind.Plus,
            "bath" => IconKind.Bath,
            "lighting" => IconKind.Lamp,
            "decor" => IconKind.Picture,
            "textiles" => IconKind.Rug,
            "walls" => IconKind.SlatPanel,
            "plants" => IconKind.Leaf,
            "utility" => IconKind.Washer,
            "outdoor" => IconKind.Tree,
            _ => IconKind.Grid,
        };

        static string MountHint(FurnitureCatalog.Entry e)
        {
            switch (e.Mount)
            {
                case ItemMount.Wall: return "вешается на стену";
                case ItemMount.Ceiling: return "крепится к потолку";
            }
            if (e.AgainstWall) return "ставится к стене";
            return e.OnSurfaces ? "на пол, стол или полку" : "ставится на пол";
        }

        // ================================================================== card
        /// <summary>
        /// A model: picture (or its category icon), name, size. Click = place with the next click in the house (again = cancel);
        /// drag out of the panel = place where dropped.
        /// </summary>
        sealed class Card
        {
            public readonly VisualElement Root;
            readonly LibraryPanel _owner;
            readonly FurnitureCatalog.Entry _entry;
            readonly VisualElement _thumb;
            readonly Label _size;
            Vector2 _down;
            bool _pressed, _dragging;

            public Card(LibraryPanel owner, FurnitureCatalog.Entry e)
            {
                _owner = owner;
                _entry = e;
                _thumb = Ui.El("lib-thumb");
                _thumb.pickingMode = PickingMode.Ignore;
                var tex = e.Thumbnail;
                if (tex != null) _thumb.style.backgroundImage = new StyleBackground(tex);
                else _thumb.Add(Ui.Icon(CategoryIcon(e.Category?.Id), 32, "lib-thumb-icon"));
                _size = Ui.Text(e.SizeText, "lib-size");
                Root = Ui.El("lib-card", _thumb, Ui.Text(e.Name, "lib-name"), _size);
                Root.focusable = false;
                Tip();
                Root.RegisterCallback<PointerDownEvent>(OnDown);
                Root.RegisterCallback<PointerMoveEvent>(OnMove);
                Root.RegisterCallback<PointerUpEvent>(OnUp);
                Root.RegisterCallback<PointerCaptureOutEvent>(_ => Reset());
                Root.RegisterCallback<AttachToPanelEvent>(_ => { if (_size.text.Length == 0) _size.text = _entry.SizeText; });
            }

            void Tip()
            {
                string size = _entry.SizeText;
                Tooltips.Tip(Root, _entry.Name, null, (size.Length > 0 ? size + " · " : "") + MountHint(_entry));
            }

            void OnDown(PointerDownEvent e)
            {
                if (e.button != 0) return;
                _pressed = true;
                _dragging = false;
                _down = e.position;
                Root.CapturePointer(e.pointerId);
                Root.AddToClassList("pressed");
            }

            void OnMove(PointerMoveEvent e)
            {
                if (!_pressed || _dragging || !Root.HasPointerCapture(e.pointerId)) return;
                if (((Vector2)e.position - _down).sqrMagnitude < DragStart * DragStart) return;
                _dragging = true;
                Tooltips.HideNow();
                _owner._editor.BeginPlace(_entry, true);
            }

            void OnUp(PointerUpEvent e)
            {
                if (e.button != 0) return;
                bool click = _pressed && !_dragging;
                if (Root.HasPointerCapture(e.pointerId)) Root.ReleasePointer(e.pointerId);
                Reset();
                if (!click) return;             // a drag ends in the editor (it sees the button go up over the house)
                var ed = _owner._editor;
                if (ed.Placing == _entry && !ed.PlacingByDrag) ed.CancelPlacing();
                else ed.BeginPlace(_entry, false);
                Tip();                          // the size is known once the model was built
                _size.text = _entry.SizeText;
            }

            void Reset()
            {
                _pressed = false;
                _dragging = false;
                Root.RemoveFromClassList("pressed");
            }
        }
    }
}
