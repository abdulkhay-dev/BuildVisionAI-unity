using System;
using System.Collections.Generic;
using System.Globalization;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Home, the project library (⌘O), spec §5. Opaque bg-app over everything:
    /// <list type="bullet">
    /// <item>header — mark + «House»; search (⌘F), the AI pill (same states as the status pill), «Вернуться к проекту»
    /// (Esc, only with an open project) and «Новый проект» (⌘N);</item>
    /// <item>«Начало работы» checklist (until dismissed or finished);</item>
    /// <item>«Проекты» + count, sort menu (<see cref="AppSettings.Sort"/>);</item>
    /// <item>a responsive grid of <see cref="HomeCard"/>s (4 / 3 / 2 columns at content width ≥ 1200 / ≥ 880 / less);</item>
    /// <item>no-results and empty-library states;</item>
    /// <item>keyboard: ⌘F search, arrows move the highlight, ↩ open, F2 rename, ⌘⌫ delete (Esc/⌘O/⌘N live in AppUI).</item>
    /// </list>
    /// Opening and closing animate opacity + scale 1.02 → 1 (240 ms, ease-out-cubic).
    /// </summary>
    public sealed class HomeScreen
    {
        /// <summary>Example request for the AI (checklist «Скопировать запрос»; same as the empty-site card).</summary>
        public const string ExamplePrompt =
            "Спроектируй одноэтажный дом 10×12 м: гостиная с кухней, две спальни, санузел и терраса. Расставь мебель.";

        const float ColumnGap = 24f;
        const int FadeMs = 240;

        static readonly ProjectSort[] SortModes = { ProjectSort.Recent, ProjectSort.Name, ProjectSort.Area };
        static readonly CompareInfo Collation = RussianCollation();

        readonly AppUI _ui;
        public VisualElement Element { get; }
        public bool IsOpen { get; private set; }

        // header
        readonly VisualElement _header, _back, _aiPill, _searchClear;
        readonly TextField _search;
        readonly Icon _aiSparkle;
        readonly PulseDot _aiDot;
        readonly Label _aiLabel;

        // content
        readonly ScrollView _scroll;
        readonly HomeChecklist _checklist;
        readonly VisualElement _titleRow, _grid, _noResults, _empty, _emptyAi, _sortButton;
        readonly Label _count, _noResultsText;

        readonly List<HomeCard> _cards = new List<HomeCard>();       // every project, in display order
        readonly List<HomeCard> _visible = new List<HomeCard>();     // the ones matching the search
        readonly Dictionary<string, HomeCard> _byId = new Dictionary<string, HomeCard>();
        readonly HashSet<string> _seen = new HashSet<string>();
        readonly List<string> _tokens = new List<string>();

        int _columns = 4, _highlight = -1, _keyFrame = -1, _renameFrame = -1;
        bool _keyboardNav, _aiDirty = true, _checklistDirty = true, _checklistShown, _checklistPlaced;
        HomeCard _hovered, _renaming;
        ProjectSort _sort;
        string _pendingWalk;
        float _pendingWalkAt, _nextAgo, _nextAiTip;
        IVisualElementScheduledItem _fadeJob;

        public HomeScreen(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("layer home");
            Element.pickingMode = PickingMode.Position;               // opaque: the 3D view underneath takes nothing
            Ui.Show(Element, false);

            // ---------------------------------------------------------- header
            var mark = Ui.El("home-mark", Ui.Icon(IconKind.House, 16));
            Tooltips.Tip(mark, "House", null, string.IsNullOrEmpty(_ui.S?.Version) ? null : "Версия " + _ui.S.Version);
            var brand = Ui.El("home-brand", mark, Ui.Text("House", "t-headline home-brand-name"));

            var searchWrap = Ui.Input("Поиск проектов", out _search, false, IconKind.Search, "⌘ F");
            searchWrap.AddToClassList("home-search");
            _search.maxLength = 80;
            Tooltips.Tip(_search, "Поиск по названию и описанию", "⌘ F");
            _searchClear = Ui.IconButton(IconKind.Close, ClearSearch, "Сбросить поиск", null, ButtonKind.Ghost, "btn-xs home-search-clear", 14);
            Ui.Show(_searchClear, false);
            _search.Add(_searchClear);
            _search.RegisterValueChangedCallback(e => OnSearchChanged(e.newValue));
            _search.RegisterCallback<FocusOutEvent>(_ => OnSearchBlur());

            _aiSparkle = Ui.Icon(IconKind.Sparkle, 16);
            _aiDot = new PulseDot();
            _aiLabel = Ui.Text("Подключить ИИ", "home-ai-label");
            _aiPill = Ui.OnClick(Ui.El("home-ai", _aiSparkle, _aiDot, _aiLabel), OnAiClick);

            _back = Ui.Button(ButtonKind.Ghost, "Вернуться к проекту", () => { if (IsOpen) _ui.CloseHome(); }, null, "home-back");
            _back.Add(Ui.Kbd("Esc", true));
            Tooltips.Tip(_back, "Вернуться к проекту", "Esc");
            Ui.Show(_back, false);

            var create = Ui.Button(ButtonKind.Primary, "Новый проект", () => { if (IsOpen) _ui.ShowNewProject(); }, IconKind.Plus, "home-new");
            Tooltips.Tip(create, "Создать проект", "⌘ N", "Дом в нём построит ваш ИИ-ассистент");

            var actions = Ui.El("home-actions", searchWrap, _aiPill, _back, create);
            _header = Ui.El("home-header", Ui.El("home-header-inner", brand, Ui.El("grow"), actions));

            // ---------------------------------------------------------- checklist
            _checklist = new HomeChecklist(
                () => { if (IsOpen) _ui.ShowConnectAi(); },
                () => { if (IsOpen) _ui.Copy(ExamplePrompt); },
                WalkLatest,
                DismissChecklist);
            Ui.Show(_checklist.Element, false);

            // ---------------------------------------------------------- title row
            _count = Ui.Text("", "t-title c-3 home-count");
            _sortButton = Ui.Button(ButtonKind.Ghost, AppSettings.Title(ProjectSort.Recent), OpenSortMenu, IconKind.Sort, "btn-sm home-sort");
            _sortButton.Add(Ui.Icon(IconKind.ChevronDown, 12, "trail-icon"));
            Tooltips.Tip(_sortButton, "Порядок проектов");
            _titleRow = Ui.El("home-title-row first", Ui.Text("Проекты", "t-display home-title"), _count, Ui.El("grow"), _sortButton);

            // ---------------------------------------------------------- grid & states
            _grid = Ui.El("home-grid");
            _grid.RegisterCallback<GeometryChangedEvent>(_ => Layout());
            _grid.RegisterCallback<PointerMoveEvent>(_ => { if (_keyboardNav) SetKeyboardNav(false); });

            _noResultsText = Ui.Text("", "t-headline home-state-title");
            _noResultsText.enableRichText = false;                    // the query is shown verbatim
            var reset = Ui.Button(ButtonKind.Ghost, "Сбросить поиск", ClearSearch, null, "home-state-reset");
            Tooltips.Tip(reset, "Показать все проекты");
            _noResults = Ui.El("home-noresults", Ui.Icon(IconKind.Search, 32, "home-state-icon"), _noResultsText, reset);
            Ui.Show(_noResults, false);

            var emptyNew = Ui.Button(ButtonKind.Primary, "Новый проект", () => { if (IsOpen) _ui.ShowNewProject(); }, IconKind.Plus);
            Tooltips.Tip(emptyNew, "Создать проект", "⌘ N");
            _emptyAi = Ui.Button(ButtonKind.Secondary, "Подключить ИИ", () => { if (IsOpen) _ui.ShowConnectAi(); }, IconKind.Sparkle, "home-empty-ai");
            Tooltips.Tip(_emptyAi, "Подключить ИИ-ассистента", null, "Claude, Cursor или другой клиент");
            _empty = Ui.El("home-empty",
                new HomeIllustration(),
                Ui.Text("Здесь появятся ваши дома", "t-title home-state-title"),
                Ui.Text("Дом проектирует ваш ИИ-ассистент. Создайте проект и опишите, какой дом вы хотите.", "t-body c-2 home-state-body"),
                Ui.El("home-state-actions", emptyNew, _emptyAi));
            Ui.Show(_empty, false);

            // ---------------------------------------------------------- scroll
            var column = Ui.El("home-column", _checklist.Element, _titleRow, _grid, _noResults, _empty);
            _scroll = new ScrollView(ScrollViewMode.Vertical);
            _scroll.AddToClassList("home-scroll");
            _scroll.horizontalScrollerVisibility = ScrollerVisibility.Hidden;
            _scroll.verticalScrollerVisibility = ScrollerVisibility.Auto;
            _scroll.Add(Ui.El("home-center", column));
            _scroll.verticalScroller.valueChanged += v => _header.EnableInClassList("scrolled", v > 0.5f);

            Element.Add(_header);
            Element.Add(_scroll);

            // ---------------------------------------------------------- live data
            if (_ui.Ai != null) _ui.Ai.Changed += () => { _aiDirty = true; _checklistDirty = true; };
            if (_ui.S?.Settings != null) _ui.S.Settings.Changed += () => _checklistDirty = true;
            if (_ui.S?.Thumbs != null) _ui.S.Thumbs.Updated += OnThumbUpdated;
        }

        // ================================================================== open / close
        public void Open()
        {
            _fadeJob?.Pause();
            bool wasOpen = IsOpen;
            IsOpen = true;
            if (!wasOpen)
            {
                _keyboardNav = false;
                _highlight = -1;
                _hovered = null;
                if (!string.IsNullOrEmpty(_search.value)) _search.value = "";
            }
            Refresh();

            Tooltips.HideNow();
            bool onScreen = Ui.IsShown(Element) && Element.resolvedStyle.opacity > 0.01f;
            Ui.Show(Element, true);
            if (!onScreen)
            {
                SetFade(0);
                Element.style.opacity = 0f;
                Element.style.scale = new Scale(new Vector3(1.02f, 1.02f, 1f));
            }
            _fadeJob = Element.schedule.Execute(() =>
            {
                if (!IsOpen) return;
                SetFade(FadeMs);
                Element.style.opacity = 1f;
                Element.style.scale = new Scale(Vector3.one);
            });
            _fadeJob.ExecuteLater(16);
        }

        /// <summary>Closes Home (only called when a project is open).</summary>
        public void Close()
        {
            if (!IsOpen) return;
            IsOpen = false;
            CancelRename();
            if (SearchFocused()) _search.Blur();
            _ui.ClosePopover();
            Tooltips.HideNow();
            // PulseDot keeps its 16 ms loop running under a display:none ancestor: stop the ring while Home is away
            // (Open → Refresh → UpdateAi turns it back on)
            if (_ui.Ai != null && _ui.Ai.State == AiState.Working) _aiDot.SetStyle("dot-ai", false);
            _aiDirty = true;

            _fadeJob?.Pause();
            SetFade(FadeMs);
            Element.style.opacity = 0f;
            Element.style.scale = new Scale(new Vector3(1.02f, 1.02f, 1f));
            _fadeJob = Element.schedule.Execute(() => { if (!IsOpen) Ui.Show(Element, false); });
            _fadeJob.ExecuteLater(FadeMs + 20);

            // «Перейти» in the checklist: the project it opened goes straight into the walk
            var session = _ui.S?.Session;
            if (_pendingWalk != null && session != null && session.HasProject && session.ProjectId == _pendingWalk
                && Time.unscaledTime - _pendingWalkAt < 30f)
                _ui.SwitchMode(HouseViewer.Mode.Walk);
            _pendingWalk = null;
        }

        void SetFade(int ms)
        {
            var e = Element;
            e.style.transitionProperty = new List<StylePropertyName> { new StylePropertyName("opacity"), new StylePropertyName("scale") };
            e.style.transitionDuration = new List<TimeValue> { new TimeValue(ms, TimeUnit.Millisecond), new TimeValue(ms, TimeUnit.Millisecond) };
            e.style.transitionTimingFunction = new List<EasingFunction> { new EasingFunction(EasingMode.EaseOutCubic), new EasingFunction(EasingMode.EaseOutCubic) };
        }

        // ================================================================== data
        /// <summary>Re-reads the project library (cards are reused by id, so hover and rename survive).</summary>
        public void Refresh()
        {
            var session = _ui.S?.Session;
            if (session == null) return;
            List<ProjectInfo> list;
            try { list = session.Store.List(); }
            catch (Exception e)
            {
                Debug.LogWarning("[Home] project list: " + e.Message);
                list = new List<ProjectInfo>();
            }
            string openId = session.HasProject ? session.ProjectId : null;

            _seen.Clear();
            foreach (var info in list)
            {
                if (info == null || string.IsNullOrEmpty(info.Id) || !_seen.Add(info.Id)) continue;
                if (_byId.TryGetValue(info.Id, out var card)) card.Update(info);
                else
                {
                    card = new HomeCard(this, info);
                    _byId[info.Id] = card;
                    _cards.Add(card);
                }
                card.SetOpen(info.Id == openId);
                card.SetThumb(_ui.S.Thumbs?.Get(info.Id));
            }
            for (int i = _cards.Count - 1; i >= 0; i--)
            {
                var c = _cards[i];
                if (_seen.Contains(c.Id)) continue;
                if (_renaming == c) _renaming = null;
                if (_hovered == c) _hovered = null;
                c.Root.RemoveFromHierarchy();
                _byId.Remove(c.Id);
                _cards.RemoveAt(i);
            }

            Ui.Show(_back, openId != null);
            if (openId != null) Tooltips.Tip(_back, "Вернуться к «" + _ui.NameOf(openId) + "»", "Esc");
            Ui.SetLabel(_sortButton, AppSettings.Title(CurrentSort));

            ApplyFilter();
            UpdateAi();
            UpdateChecklist();
            _nextAgo = Time.unscaledTime + 30f;
        }

        ProjectSort CurrentSort => _ui.S?.Settings != null ? _ui.S.Settings.Sort : ProjectSort.Recent;

        /// <summary>Sorts, filters by the search, orders the grid children and shows the right state.</summary>
        void ApplyFilter()
        {
            int previous = _highlight;
            var keep = _highlight >= 0 && _highlight < _visible.Count ? _visible[_highlight] : null;

            _sort = CurrentSort;                                // PlayerPrefs: read once, not per comparison
            _cards.Sort(Compare);
            _tokens.Clear();
            foreach (var t in Normalize(_search.value).Split(' '))
                if (t.Length > 0) _tokens.Add(t);

            _visible.Clear();
            foreach (var c in _cards)
            {
                bool match = _tokens.Count == 0 || c.Matches(_tokens);
                Ui.Show(c.Root, match);
                if (match) _visible.Add(c);
            }
            Reorder();

            bool none = _cards.Count == 0, noMatch = !none && _visible.Count == 0;
            Ui.Show(_titleRow, !none);
            Ui.Show(_grid, _visible.Count > 0);
            Ui.Show(_noResults, noMatch);
            Ui.Show(_empty, none);
            Ui.Show(_emptyAi, _ui.Ai == null || _ui.Ai.State == AiState.NotConnected);
            if (noMatch) _noResultsText.text = "Ничего не найдено по запросу «" + _search.value.Trim() + "»";
            _count.text = _tokens.Count > 0 ? _visible.Count + " из " + _cards.Count : _cards.Count.ToString();

            _highlight = keep != null ? _visible.IndexOf(keep) : -1;
            if (_highlight < 0 && _keyboardNav && _visible.Count > 0) _highlight = Mathf.Clamp(previous, 0, _visible.Count - 1);
            Layout();
            UpdateHighlight();
        }

        int Compare(HomeCard a, HomeCard b)
        {
            int c;
            switch (_sort)
            {
                case ProjectSort.Name:
                    c = Collation.Compare(a.DisplayName, b.DisplayName, CompareOptions.IgnoreCase);
                    break;
                case ProjectSort.Area:
                    c = b.Info.Area.CompareTo(a.Info.Area);
                    if (c == 0) c = Collation.Compare(a.DisplayName, b.DisplayName, CompareOptions.IgnoreCase);
                    break;
                default:
                    c = string.CompareOrdinal(b.Info.Modified ?? "", a.Info.Modified ?? "");
                    if (c == 0) c = Collation.Compare(a.DisplayName, b.DisplayName, CompareOptions.IgnoreCase);
                    break;
            }
            return c != 0 ? c : string.CompareOrdinal(a.Id, b.Id);
        }

        /// <summary>Puts the grid children in <see cref="_cards"/> order (no detach: hover states survive).</summary>
        void Reorder()
        {
            bool same = _grid.childCount == _cards.Count;
            for (int i = 0; same && i < _cards.Count; i++) same = _grid.ElementAt(i) == _cards[i].Root;
            if (same) return;
            foreach (var c in _cards)
            {
                if (c.Root.parent != _grid) _grid.Add(c.Root);
                else c.Root.BringToFront();
            }
        }

        /// <summary>Column count from the content width; card widths fill it with 24 px gaps (rows 32 apart).</summary>
        void Layout()
        {
            float w = _grid.contentRect.width;
            if (float.IsNaN(w) || w <= 0f) return;
            int cols = w >= 1200f ? 4 : w >= 880f ? 3 : 2;
            _columns = cols;
            float cardWidth = Mathf.Floor((w - ColumnGap * (cols - 1)) / cols);
            for (int i = 0; i < _visible.Count; i++)
                _visible[i].SetSize(cardWidth, i % cols == cols - 1 ? 0f : ColumnGap);
        }

        void OnThumbUpdated(string id)
        {
            if (!IsOpen || _ui.S?.Thumbs == null) return;
            if (_byId.TryGetValue(id, out var card)) card.SetThumb(_ui.S.Thumbs.Get(id));
        }

        // ================================================================== search
        public void FocusSearch()
        {
            if (!IsOpen) return;
            CancelRename();
            _search.Focus();
            _search.schedule.Execute(() => { if (SearchFocused()) _search.SelectAll(); }).ExecuteLater(1);
        }

        void OnSearchChanged(string value)
        {
            Ui.Show(_searchClear, !string.IsNullOrEmpty(value));
            _highlight = -1;                                    // a new query starts at its first result
            ApplyFilter();
            _scroll.scrollOffset = Vector2.zero;
        }

        void ClearSearch()
        {
            if (!string.IsNullOrEmpty(_search.value)) _search.value = "";
        }

        /// <summary>Esc in the field (AppUI blurs it) also clears the query, like Spotlight.</summary>
        void OnSearchBlur()
        {
            var kb = Keyboard.current;
            if (kb != null && kb.escapeKey.wasPressedThisFrame) ClearSearch();
        }

        bool SearchFocused()
        {
            var f = _search.panel?.focusController?.focusedElement as VisualElement;
            return f != null && (f == _search || _search.Contains(f));
        }

        // ================================================================== AI pill
        void UpdateAi()
        {
            _aiDirty = false;
            var ai = _ui.Ai;
            var state = ai?.State ?? AiState.NotConnected;
            bool connect = state == AiState.NotConnected;
            _aiPill.EnableInClassList("home-ai--connect", connect);
            Ui.Show(_aiSparkle, connect);
            Ui.Show(_aiDot, !connect);
            string label;
            switch (state)
            {
                case AiState.Waiting:
                    _aiDot.SetStyle("dot-ring", false);
                    label = "ИИ подключён";
                    break;
                case AiState.Online:
                    _aiDot.SetStyle("dot-success", false);
                    label = "ИИ на связи";
                    break;
                case AiState.Working:
                    _aiDot.SetStyle("dot-ai", true);
                    label = ai.Phrase;
                    break;
                default:
                    label = "Подключить ИИ";
                    break;
            }
            if (_aiLabel.text != label) _aiLabel.text = label;
            Ui.Show(_emptyAi, connect);
            UpdateAiTip();
        }

        void UpdateAiTip()
        {
            var ai = _ui.Ai;
            var state = ai?.State ?? AiState.NotConnected;
            if (state == AiState.NotConnected)
                Tooltips.Tip(_aiPill, "Подключить ИИ-ассистента", null, "Дом строит ваш ИИ: Claude, Cursor или другой клиент");
            else if (state == AiState.Waiting)
                Tooltips.Tip(_aiPill, "ИИ-ассистент настроен. Напишите ему — он найдёт House сам.");
            else
                Tooltips.Tip(_aiPill, ai.LastCallText);
        }

        void OnAiClick()
        {
            if (!IsOpen) return;
            if (_ui.Ai == null || _ui.Ai.State == AiState.NotConnected) { _ui.ShowConnectAi(); return; }
            _ui.TogglePopover(_aiPill, () => AiPopover.Build(_ui), 340f, PopPlacement.BelowRight);
        }

        // ================================================================== checklist
        void UpdateChecklist()
        {
            _checklistDirty = false;
            var settings = _ui.S?.Settings;
            if (settings == null) return;
            bool connected = settings.AiEverCalled || (_ui.Ai != null && _ui.Ai.AnyClientConnected);
            string walkId = WalkTargetId();
            string walkName = walkId == null ? null : _byId.TryGetValue(walkId, out var c) ? c.DisplayName : _ui.NameOf(walkId);
            int done = _checklist.Set(connected, settings.AiBuiltOnce, settings.WalkedOnce, walkName);
            ShowChecklist(!settings.ChecklistDismissed && done < 3);
        }

        void ShowChecklist(bool show)
        {
            if (_checklistPlaced && show == _checklistShown) return;
            bool animate = _checklistPlaced && IsOpen && Ui.IsShown(Element);
            _checklistPlaced = true;
            _checklistShown = show;
            if (animate) Motion.Fade(_checklist.Element, show, 180, 180, show ? 0f : -8f);
            else if (show) Motion.Fade(_checklist.Element, true, 0, 0);      // also resets a faded-out opacity
            else Ui.Show(_checklist.Element, false);
            _titleRow.EnableInClassList("first", !show);
        }

        void DismissChecklist()
        {
            if (_ui.S?.Settings == null) return;
            _ui.S.Settings.ChecklistDismissed = true;
            ShowChecklist(false);
        }

        /// <summary>The open project, else the most recently changed one.</summary>
        string WalkTargetId()
        {
            var session = _ui.S?.Session;
            if (session != null && session.HasProject) return session.ProjectId;
            HomeCard latest = null;
            foreach (var c in _cards)
                if (latest == null || string.CompareOrdinal(c.Info.Modified ?? "", latest.Info.Modified ?? "") > 0) latest = c;
            return latest?.Id;
        }

        /// <summary>«Перейти»: the latest project in «Прогулка».</summary>
        void WalkLatest()
        {
            if (!IsOpen) return;
            string id = WalkTargetId();
            if (id == null) return;
            var session = _ui.S.Session;
            if (session.HasProject && session.ProjectId == id)
            {
                _ui.CloseHome();
                _ui.SwitchMode(HouseViewer.Mode.Walk);
                return;
            }
            _pendingWalk = id;
            _pendingWalkAt = Time.unscaledTime;
            _ui.OpenProject(id);
        }

        // ================================================================== sort
        void OpenSortMenu()
        {
            if (!IsOpen) return;
            var current = CurrentSort;
            var items = new List<MenuItem>(SortModes.Length);
            foreach (var mode in SortModes)
            {
                var m = mode;
                items.Add(new MenuItem { Label = AppSettings.Title(m), Checked = m == current, Action = () => SetSort(m) });
            }
            _ui.ShowMenu(_sortButton, items, PopPlacement.BelowRight, 220f);
        }

        void SetSort(ProjectSort mode)
        {
            if (_ui.S?.Settings == null) return;
            if (_ui.S.Settings.Sort != mode) _ui.S.Settings.Sort = mode;
            Ui.SetLabel(_sortButton, AppSettings.Title(mode));
            ApplyFilter();
        }

        // ================================================================== cards
        internal void OpenCard(HomeCard card)
        {
            if (!IsOpen || card == null || card.Renaming) return;
            if (_renaming != null) CommitRename();
            _ui.OpenProject(card.Id);
        }

        internal void CardHover(HomeCard card, bool inside)
        {
            if (inside)
            {
                _hovered = card;
                if (!_keyboardNav) _highlight = _visible.IndexOf(card);
            }
            else if (_hovered == card) _hovered = null;
        }

        /// <summary>Context menu of a card: at the pointer (right click) or under «⋯».</summary>
        internal void ShowCardMenu(HomeCard card, Vector2? at)
        {
            if (!IsOpen || card == null) return;
            if (_renaming != null) CommitRename();
            int index = _visible.IndexOf(card);
            if (index >= 0) _highlight = index;
            string id = card.Id;
            var items = new List<MenuItem>
            {
                new MenuItem { Label = "Открыть", Icon = IconKind.Eye, Shortcut = "↩", Action = () => OpenCard(card) },
                new MenuItem { Label = "Переименовать", Icon = IconKind.Pencil, Shortcut = "F2", Action = () => BeginRename(card) },
                new MenuItem { Label = "Дублировать", Icon = IconKind.Duplicate, Action = () => _ui.DuplicateProject(id) },
                new MenuItem { Label = "Показать в Finder", Icon = IconKind.Folder, Action = () => _ui.RevealInFinder(_ui.S.Session.Store.FolderOf(id)) },
                MenuItem.Sep(),
                new MenuItem { Label = "Удалить…", Icon = IconKind.Trash, Shortcut = "⌘⌫", Danger = true, Action = () => _ui.ConfirmDelete(id) },
            };
            if (at.HasValue) _ui.ShowMenuAt(at.Value, items, 220f);
            else _ui.ShowMenu(card.MoreButton, items, PopPlacement.BelowRight, 220f);
        }

        HomeCard Target => _keyboardNav && _highlight >= 0 && _highlight < _visible.Count ? _visible[_highlight] : _hovered;

        void SetKeyboardNav(bool on)
        {
            _keyboardNav = on;
            UpdateHighlight();
        }

        void UpdateHighlight()
        {
            var target = _keyboardNav && _highlight >= 0 && _highlight < _visible.Count ? _visible[_highlight] : null;
            for (int i = 0; i < _cards.Count; i++) _cards[i].SetHighlight(_cards[i] == target);
        }

        /// <summary>Arrow keys: ±1 across, ±columns down/up; the first press only shows the highlight.</summary>
        void Move(int delta)
        {
            int n = _visible.Count;
            if (n == 0) return;
            int from = _highlight >= 0 && _highlight < n ? _highlight : _hovered != null ? _visible.IndexOf(_hovered) : -1;
            int to;
            if (!_keyboardNav && from >= 0) to = from;                  // first press: highlight where the pointer is
            else if (from < 0) to = 0;
            else
            {
                to = from + delta;
                if (to < 0)
                {
                    if (delta < -1) { SetKeyboardNav(false); FocusSearch(); return; }   // ↑ from the first row → search
                    to = 0;
                }
                else if (to >= n)
                {
                    // ↓ into a shorter last row lands on its last card; → at the end stays
                    int lastRow = (n - 1) / _columns, fromRow = from / _columns;
                    to = delta > 1 && fromRow < lastRow ? n - 1 : from;
                }
            }
            _highlight = to;
            SetKeyboardNav(true);
            _scroll.ScrollTo(_visible[to].Root);
        }

        // ================================================================== inline rename
        /// <summary>Inline rename of a project card (F2 / menu): ↩ saves, Esc cancels, clicking elsewhere saves.</summary>
        public void BeginRename(string projectId)
        {
            if (projectId != null && _byId.TryGetValue(projectId, out var card)) BeginRename(card);
        }

        internal void BeginRename(HomeCard card)
        {
            if (!IsOpen || card == null) return;
            if (_renaming == card) return;
            if (_renaming != null) CommitRename();
            if (!Ui.IsShown(card.Root)) return;
            _renaming = card;
            _renameFrame = Time.frameCount;
            var field = card.StartRename();
            field.RegisterCallback<KeyDownEvent>(OnRenameKey, TrickleDown.TrickleDown);
            field.RegisterCallback<FocusOutEvent>(OnRenameBlur);
            _scroll.ScrollTo(card.Root);
            field.schedule.Execute(() =>
            {
                if (_renaming != card || field.panel == null) return;
                field.Focus();
                field.SelectAll();
            }).ExecuteLater(16);
        }

        void OnRenameKey(KeyDownEvent e)
        {
            if (_renaming == null) return;
            if (e.keyCode == KeyCode.Return || e.keyCode == KeyCode.KeypadEnter)
            {
                e.StopPropagation();
                if (Time.frameCount != _renameFrame) CommitRename();
            }
            else if (e.keyCode == KeyCode.Escape)
            {
                e.StopPropagation();
                CancelRename();
            }
        }

        void OnRenameBlur(FocusOutEvent e)
        {
            if (_renaming == null) return;
            var kb = Keyboard.current;
            if (kb != null && kb.escapeKey.wasPressedThisFrame) CancelRename();
            else CommitRename();
        }

        void CommitRename()
        {
            var card = _renaming;
            if (card == null) return;
            _renaming = null;
            _keyFrame = Time.frameCount;
            string text = card.RenameText?.Trim();
            string old = card.DisplayName;
            card.EndRename();
            if (string.IsNullOrEmpty(text) || text == old) return;
            card.SetName(text);
            _ui.RenameProject(card.Id, text);          // refreshes Home on success
            if (card.DisplayName != text) card.SetName(card.DisplayName);   // failed: back to the stored name
        }

        void CancelRename()
        {
            var card = _renaming;
            if (card == null) return;
            _renaming = null;
            _keyFrame = Time.frameCount;
            card.EndRename();
        }

        // ================================================================== frame & keys
        public void Tick()
        {
            if (!IsOpen) return;
            float now = Time.unscaledTime;
            if (_aiDirty) UpdateAi();
            if (_checklistDirty) UpdateChecklist();
            if (now >= _nextAgo)
            {
                _nextAgo = now + 30f;
                for (int i = 0; i < _cards.Count; i++) _cards[i].RefreshAgo();
            }
            if (now >= _nextAiTip)
            {
                _nextAiTip = now + 1f;
                var ai = _ui.Ai;
                if (ai != null && (ai.State == AiState.Online || ai.State == AiState.Working)) UpdateAiTip();
            }
        }

        /// <summary>Keyboard while Home is open (⌘F search, ↩ open, F2 rename, ⌘⌫ delete…); Esc/⌘O/⌘N are handled by AppUI.</summary>
        public void OnKey(Keyboard kb, bool cmd, bool shift)
        {
            if (!IsOpen || kb == null || _ui.PopoverOpen || _ui.ModalOpen || _ui.VeilVisible) return;
            if (Time.frameCount == _keyFrame) return;          // this key already ended an inline rename
            bool enter = kb.enterKey.wasPressedThisFrame || kb.numpadEnterKey.wasPressedThisFrame;

            if (_renaming != null)
            {
                if (enter && Time.frameCount != _renameFrame) CommitRename();
                return;
            }

            bool typing = _ui.Typing;
            bool inSearch = typing && SearchFocused();
            if (cmd)
            {
                if (kb.fKey.wasPressedThisFrame) { FocusSearch(); return; }
                if (!typing && (kb.backspaceKey.wasPressedThisFrame || kb.deleteKey.wasPressedThisFrame))
                {
                    var t = Target;
                    if (t != null) _ui.ConfirmDelete(t.Id);
                }
                return;
            }
            if (typing && !inSearch) return;

            if (inSearch)
            {
                if (kb.downArrowKey.wasPressedThisFrame && _visible.Count > 0)
                {
                    _search.Blur();
                    _highlight = 0;
                    SetKeyboardNav(true);
                    _scroll.ScrollTo(_visible[0].Root);
                }
                else if (enter && _visible.Count > 0)
                {
                    // ↩ in the search: the highlighted card, or the only match
                    if (_keyboardNav && _highlight >= 0 && _highlight < _visible.Count) OpenCard(_visible[_highlight]);
                    else if (_visible.Count == 1) OpenCard(_visible[0]);
                    else
                    {
                        _search.Blur();
                        _highlight = 0;
                        SetKeyboardNav(true);
                    }
                }
                return;
            }

            if (kb.leftArrowKey.wasPressedThisFrame) Move(-1);
            else if (kb.rightArrowKey.wasPressedThisFrame) Move(1);
            else if (kb.upArrowKey.wasPressedThisFrame) Move(-_columns);
            else if (kb.downArrowKey.wasPressedThisFrame) Move(_columns);
            else if (enter)
            {
                var t = Target;
                if (t != null) OpenCard(t);
            }
            else if (kb.f2Key.wasPressedThisFrame)
            {
                var t = Target;
                if (t != null) BeginRename(t);
            }
        }

        // ================================================================== helpers
        /// <summary>Search form of a text: lower case, «ё» = «е», trimmed.</summary>
        internal static string Normalize(string s) => string.IsNullOrEmpty(s) ? "" : s.Trim().ToLowerInvariant().Replace('ё', 'е');

        static CompareInfo RussianCollation()
        {
            try { return CultureInfo.GetCultureInfo("ru-RU").CompareInfo; }
            catch (Exception) { return CultureInfo.InvariantCulture.CompareInfo; }
        }
    }
}
