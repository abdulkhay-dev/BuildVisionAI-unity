using System;
using System.Collections.Generic;
using System.Text;
using House4696.Model;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Floor plan (spec §3.5). The small panel at the bottom right (288×320: level tabs, «Большой план», ✕ and the
    /// plan with the viewer marker) and the large plan (P): a 1040×680 card with level tabs, the room list with type
    /// icons and areas, and the plan — cross-highlighted on hover. Clicking a room walks into it
    /// (<see cref="AppUI.GoToRoom"/>). The shown level follows the camera; a level picked by hand sticks until the
    /// camera changes floor. Whether the panel is open is remembered per mode (walk &amp; fly / orbit) in
    /// <see cref="AppSettings.PlanInWalk"/> / <see cref="AppSettings.PlanInOrbit"/>.
    /// </summary>
    public sealed class PlanPanel
    {
        const float FollowInterval = 0.25f;
        const int PanelFadeMs = 180;
        const int LargeOutMs = 190;
        const float NavigationHold = 1.5f;
        const string LevelKeys = "PgUp / PgDn";
        static readonly float[] ScaleSteps = { 0.5f, 1f, 2f, 5f, 10f, 20f, 50f };

        readonly AppUI _ui;
        public VisualElement Element { get; }
        /// <summary>The user wants the plan (the small panel shows while this is on and the large plan is closed).</summary>
        public bool IsOpen { get; private set; }
        public bool LargeOpen { get; private set; }
        /// <summary>The small panel is on screen (open, large plan closed) — for layout around it (toolbar shift).</summary>
        public bool PanelVisible => _smallShown;
        /// <summary>Raised when <see cref="IsOpen"/> or <see cref="LargeOpen"/> changes.</summary>
        public event Action OpenChanged;

        // small panel
        readonly VisualElement _smallHost;
        readonly FloorPlanView _smallView;
        readonly LevelTabs _smallTabs;
        readonly EmptyState _smallEmpty;
        bool _smallShown;

        // large plan
        readonly VisualElement _largeHost, _largeScrim, _largeShell, _scale, _scaleBar, _north;
        readonly FloorPlanView _largeView;
        readonly LevelTabs _largeTabs;
        readonly EmptyState _largeEmpty;
        readonly ScrollView _roomList;
        readonly Label _roomsTitle, _levelArea, _listEmpty, _totals, _scaleLabel;
        readonly Dictionary<PlanGeometry.Room, VisualElement> _rows = new Dictionary<PlanGeometry.Room, VisualElement>();
        readonly List<VisualElement> _rowList = new List<VisualElement>();
        readonly List<PlanGeometry.Room> _sortedRooms = new List<PlanGeometry.Room>();
        IVisualElementScheduledItem _largeAnim;

        readonly RoomTip _tip;

        // state
        readonly List<PlanGeometry> _plans = new List<PlanGeometry>();
        readonly List<string> _titles = new List<string>(), _compactTitles = new List<string>(), _tabTips = new List<string>();
        int _shown = -1, _cameraLevel = -1;
        string _projectId;
        bool _hadGeometry, _prefWalk, _prefOrbit, _wasClean;
        float _nextFollow, _navUntil;

        public PlanPanel(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("layer plan-layer");
            Element.pickingMode = PickingMode.Ignore;
            _tip = new RoomTip();

            // ---------------------------------------------------------------- small panel (288×320, e1)
            _smallTabs = new LevelTabs(PickLevel, "plan-levels", true);
            var expand = Ui.IconButton(IconKind.Maximize, ToggleLarge, "Большой план", "P", ButtonKind.Ghost, "btn-xs plan-hbtn", 16);
            var hide = Ui.IconButton(IconKind.Close, () => SetOpen(false), "Скрыть план", "M", ButtonKind.Ghost, "btn-xs plan-hbtn", 16);
            var head = Ui.El("plan-head", _smallTabs.Element, expand, hide);
            _smallView = new FloorPlanView { Padding = 14f, LabelCharWidth = 6.2f, Labels = FloorPlanView.LabelMode.Compact };
            _smallEmpty = new EmptyState(20, "plan-empty-sm");
            var canvas = Ui.El("plan-canvas", _smallView, _smallEmpty.Element);
            var panel = Ui.El("float plan-panel", head, canvas);
            _smallHost = Elevation.Wrap(panel, 12, 16, 4f, 0.45f, "plan-host");
            Ui.Show(_smallHost, false);
            Element.Add(_smallHost);

            // ---------------------------------------------------------------- large plan (1040×680, e3)
            _largeScrim = Ui.El("scrim plan-scrim");
            _largeScrim.RegisterCallback<PointerDownEvent>(_ => CloseLarge());

            var sideHead = Ui.El("plan-side-head", Ui.Text("План этажа", "t-headline ellipsis"),
                Ui.Text("Щёлкните комнату, чтобы перейти в неё", "plan-side-sub"));
            _largeTabs = new LevelTabs(PickLevel, "plan-levels plan-levels-large", true);
            // «1 этаж · 9 комнат» … «120 м²»: the shown floor; the whole house is in the footer
            _roomsTitle = Ui.Text("Комнаты", "plan-side-caption plan-rooms-title");
            _levelArea = Ui.Text("", "plan-side-caption plan-rooms-area");
            var roomsHead = Ui.El("plan-rooms-head", _roomsTitle, _levelArea);
            _roomList = new ScrollView(ScrollViewMode.Vertical);
            _roomList.AddToClassList("plan-rooms");
            _roomList.horizontalScrollerVisibility = ScrollerVisibility.Hidden;
            _roomList.verticalScrollerVisibility = ScrollerVisibility.Auto;
            _listEmpty = Ui.Text("", "plan-rooms-empty");
            _totals = Ui.Text("", "plan-totals");
            var foot = Ui.El("plan-side-foot", _totals);
            var side = Ui.El("plan-side", sideHead, _largeTabs.Element, roomsHead, _roomList, _listEmpty, foot);

            _largeView = new FloorPlanView { Padding = 56f, ShowAreas = true, LabelCharWidth = 7f, Labels = FloorPlanView.LabelMode.Full };
            _north = NorthBadge.Create();
            _scaleBar = Ui.El("plan-scale-bar");
            _scaleBar.pickingMode = PickingMode.Ignore;
            _scaleLabel = Ui.Text("", "plan-scale-label");
            _scale = Ui.El("plan-scale", _scaleBar, _scaleLabel);
            _scale.pickingMode = PickingMode.Ignore;
            _largeEmpty = new EmptyState(32, "plan-empty-lg");
            var close = Ui.IconButton(IconKind.Close, CloseLarge, "Закрыть", "Esc", ButtonKind.Ghost, "btn-xs plan-stage-btn", 16);
            var stage = Ui.El("plan-stage", _largeView, _north, _scale, _largeEmpty.Element, close);

            var card = Ui.El("plan-large", side, stage);
            _largeShell = Elevation.Wrap(card, 16, 48, 20f, 0.60f, "modal-shell plan-large-shell");
            _largeHost = Ui.El("plan-large-host", _largeScrim, _largeShell);
            _largeHost.pickingMode = PickingMode.Ignore;
            Ui.Show(_largeHost, false);
            AttachLarge();

            // ---------------------------------------------------------------- behaviour
            HookCanvas(_smallView, Element, false);
            HookCanvas(_largeView, _largeHost, true);
            _largeView.RoomHovered += OnLargeHover;
            _largeView.CurrentRoomChanged += _ => SyncRowStates();
            _largeView.LayoutChanged += UpdateScaleBar;

            var s = _ui.S;
            if (s?.Viewer != null) s.Viewer.ModeChanged += OnModeChanged;
            if (s?.Settings != null)
            {
                _prefWalk = s.Settings.PlanInWalk;
                _prefOrbit = s.Settings.PlanInOrbit;
                s.Settings.Changed += OnSettingsChanged;
            }
            _ui.PlansChanged += SyncPlans;
            SyncPlans();
            Refresh();
        }

        /// <summary>The level shown in the plan (index into <see cref="AppUI.Plans"/>, -1 = none).</summary>
        public int ShownLevel => _shown;
        public PlanGeometry ShownPlan => _shown >= 0 && _shown < _plans.Count ? _plans[_shown] : null;

        /// <summary>
        /// Short level name as on the tabs: the level's name, or «N этаж» (the ground floor is 1; «Цоколь» / «Подвал»
        /// below it) when the name is empty or longer than 12 characters.
        /// </summary>
        public string LevelTitle(string levelId)
        {
            int i = IndexOfLevel(levelId);
            return i >= 0 && i < _titles.Count ? _titles[i] : "";
        }

        // ------------------------------------------------------------------ open / close
        /// <summary>Shows or hides the plan panel (M, toolbar «План», ✕) and remembers it for the current mode.</summary>
        public void SetOpen(bool open) => SetOpenInternal(open, true);

        /// <summary>M: hides the plan when any plan is visible (the large one included), shows the panel otherwise.</summary>
        public void Toggle()
        {
            if (LargeOpen)
            {
                CloseLarge();
                SetOpen(false);
                return;
            }
            SetOpen(!IsOpen);
        }

        /// <summary>P: the large plan with the room list.</summary>
        public void ToggleLarge()
        {
            if (LargeOpen) CloseLarge();
            else OpenLarge();
        }

        public void CloseLarge() => CloseLarge(false);

        /// <param name="instant">no fade (Home or the veil is coming up underneath)</param>
        void CloseLarge(bool instant)
        {
            if (!LargeOpen) return;
            LargeOpen = false;
            _tip.Hide();
            Tooltips.HideNow();
            _largeView.Highlighted = null;
            _largeScrim.pickingMode = PickingMode.Ignore;     // the 3D view gets its clicks back during the fade-out
            _largeScrim.RemoveFromClassList("open");
            _largeShell.RemoveFromClassList("open");
            _largeAnim?.Pause();
            _largeAnim = null;
            if (instant) Ui.Show(_largeHost, false);
            else
            {
                _largeAnim = _largeHost.schedule.Execute(() => { if (!LargeOpen) Ui.Show(_largeHost, false); });
                _largeAnim.ExecuteLater(LargeOutMs);
            }
            ApplyVisibility();
            OpenChanged?.Invoke();
        }

        /// <summary>PgUp (+1) / PgDn (-1): show the next/previous level (opens the panel when no plan is visible).</summary>
        public void LevelStep(int dir)
        {
            if (_plans.Count == 0 || dir == 0) return;
            if (!IsOpen && !LargeOpen) SetOpenInternal(true, false);
            int next = Mathf.Clamp((_shown < 0 ? 0 : _shown) + (dir > 0 ? 1 : -1), 0, _plans.Count - 1);
            if (next != _shown) ShowLevel(next);
        }

        public void Refresh()
        {
            var s = _ui.S;
            if (s == null) return;
            string pid = s.Session.HasProject ? s.Session.ProjectId : null;
            if (pid != _projectId)
            {
                _projectId = pid;
                OnProjectSwitched();
            }
            ApplyVisibility();
        }

        public void Tick()
        {
            var s = _ui.S;
            if (s == null) return;
            // «Чистый кадр» hides everything but the toast, door prompt and crosshair: the large plan goes too
            bool clean = _ui.CleanView;
            if (clean && !_wasClean && LargeOpen) CloseLarge();
            _wasClean = clean;
            if (LargeOpen)
            {
                if (!s.Session.HasProject || _ui.HomeOpen || _ui.VeilVisible) CloseLarge(true);
                else ViewerInput.KeyboardBlocked = true;     // the card owns the keyboard: no walking behind it
            }
            ApplyVisibility();
            float now = Time.unscaledTime;
            if (now >= _nextFollow)
            {
                _nextFollow = now + FollowInterval;
                FollowCamera();
            }
            UpdateMarker();
            if (Tooltips.Suppressed) _tip.Hide();
        }

        void SetOpenInternal(bool open, bool remember)
        {
            if (remember) Remember(open);
            if (IsOpen == open) { ApplyVisibility(); return; }
            IsOpen = open;
            ApplyVisibility();
            _ui.Toolbar?.Refresh();
            OpenChanged?.Invoke();
        }

        void Remember(bool open)
        {
            var st = _ui.S?.Settings;
            if (st == null) return;
            if (CurrentMode() == HouseViewer.Mode.Orbit)
            {
                _prefOrbit = open;          // first, so the Changed echo is not taken for a settings switch
                st.PlanInOrbit = open;
            }
            else
            {
                _prefWalk = open;
                st.PlanInWalk = open;
            }
        }

        void ApplyVisibility()
        {
            var s = _ui.S;
            bool want = s != null && s.Session.HasProject && IsOpen && !LargeOpen;
            if (want == _smallShown) return;
            _smallShown = want;
            _tip.Hide();
            Motion.Fade(_smallHost, want, PanelFadeMs, PanelFadeMs, 8f);
        }

        void OpenLarge()
        {
            var s = _ui.S;
            if (LargeOpen || s == null || !s.Session.HasProject || _ui.HomeOpen || _ui.VeilVisible) return;
            LargeOpen = true;
            _ui.ClosePopover();
            Tooltips.HideNow();
            _tip.Hide();
            var plan = ShownPlan;
            if (_largeView.Plan != plan) _largeView.Plan = plan;
            _largeView.Highlighted = null;
            _largeTabs.Select(_shown);
            UpdateMarker();                  // the current room first, so its row opens marked
            BuildRoomList();
            UpdateTotals();
            UpdateEmpty();
            UpdateScaleBar();
            _largeAnim?.Pause();
            _largeScrim.pickingMode = PickingMode.Position;
            Ui.Show(_largeHost, true);
            _largeAnim = _largeHost.schedule.Execute(() =>
            {
                if (!LargeOpen) return;
                _largeScrim.AddToClassList("open");
                _largeShell.AddToClassList("open");
            });
            _largeAnim.ExecuteLater(16);
            // a long list opens scrolled to the room the viewer stands in (once the rows have a layout)
            var current = _largeView.CurrentRoom;
            if (current != null && _rows.TryGetValue(current, out var currentRow))
                _roomList.schedule.Execute(() => { if (LargeOpen && currentRow.panel != null) _roomList.ScrollTo(currentRow); }).ExecuteLater(80);
            ApplyVisibility();
            OpenChanged?.Invoke();
        }

        /// <summary>
        /// The large plan sits right under the modal layer: above the chrome, HUD, Home and veil, below dialogs,
        /// popovers, toasts and tooltips.
        /// </summary>
        void AttachLarge()
        {
            var root = _ui.Root;
            var modals = root?.Q<VisualElement>("modals");
            if (modals != null && modals.parent == root) root.Insert(root.IndexOf(modals), _largeHost);
            else Element.Add(_largeHost);
        }

        // ------------------------------------------------------------------ project, mode, settings
        void OnProjectSwitched()
        {
            if (LargeOpen) CloseLarge(true);
            _cameraLevel = -1;
            _nextFollow = 0f;
            ShowLevel(GroundIndex(), true);
            _hadGeometry = HasGeometry();
            ApplyModeDefault();
        }

        void OnModeChanged(HouseViewer.Mode mode)
        {
            _cameraLevel = -1;          // the camera moved: the level follows it again
            _nextFollow = 0f;
            bool fromRoomClick = Time.unscaledTime < _navUntil;
            _navUntil = 0f;
            // a room click switched to walk: the plan the user just clicked stays (a closed one takes the walk default)
            if (fromRoomClick && IsOpen) return;
            ApplyModeDefault();
        }

        /// <summary>«План в прогулке» etc. changed in the settings: the current mode's panel follows at once.</summary>
        void OnSettingsChanged()
        {
            var st = _ui.S?.Settings;
            if (st == null) return;
            bool w = st.PlanInWalk, o = st.PlanInOrbit;
            bool orbit = CurrentMode() == HouseViewer.Mode.Orbit;
            bool changed = orbit ? o != _prefOrbit : w != _prefWalk;
            _prefWalk = w;
            _prefOrbit = o;
            if (changed && _ui.S.Session.HasProject && HasGeometry()) SetOpenInternal(orbit ? o : w, false);
        }

        /// <summary>The mode's remembered state; an empty site keeps the panel closed (the empty-site card talks there).</summary>
        void ApplyModeDefault()
        {
            var s = _ui.S;
            if (s == null || s.Settings == null || !s.Session.HasProject) return;
            bool pref = CurrentMode() == HouseViewer.Mode.Orbit ? s.Settings.PlanInOrbit : s.Settings.PlanInWalk;
            SetOpenInternal(pref && HasGeometry(), false);
        }

        HouseViewer.Mode CurrentMode()
        {
            var v = _ui.S?.Viewer;
            return v != null ? v.CurrentMode : HouseViewer.Mode.Orbit;
        }

        // ------------------------------------------------------------------ plans & levels
        void SyncPlans()
        {
            string keepId = LevelIdAt(_shown), camId = LevelIdAt(_cameraLevel);
            _plans.Clear();
            var src = _ui.Plans;
            for (int i = 0; i < src.Count; i++) _plans.Add(src[i]);

            _titles.Clear();
            _compactTitles.Clear();
            _tabTips.Clear();
            var key = new StringBuilder();
            int ground = GroundIndex();
            for (int i = 0; i < _plans.Count; i++)
            {
                int number = i - ground + 1;         // the ground floor is «1 этаж»; below it «Цоколь» / «Подвал»
                string numbered = number >= 1 ? number + " этаж" : number == 0 ? "Цоколь" : "Подвал";
                string name = LevelName(_plans[i]);
                string full = string.IsNullOrEmpty(name) ? numbered : name;
                string title = full.Length > 12 ? numbered : full;
                _titles.Add(title);
                _compactTitles.Add(number >= 1 ? number.ToString() : number == 0 ? "Ц" : "П");
                _tabTips.Add(full + " · " + LevelSummary(_plans[i]));
                key.Append(_plans[i].LevelId).Append('\u001f').Append(title).Append('\u001e');
            }

            _cameraLevel = IndexOfLevel(camId);
            int index = IndexOfLevel(keepId);
            if (index < 0) index = ground;
            string k = key.ToString();
            _smallTabs.Build(k, _titles, _compactTitles, _tabTips, index, "План этажа");
            _largeTabs.Build(k, _titles, _compactTitles, _tabTips, index, null);
            ShowLevel(index, true);
            UpdateTotals();

            bool geo = HasGeometry();
            if (geo && !_hadGeometry && _projectId != null) ApplyModeDefault();   // the AI built the first walls
            _hadGeometry = geo;
        }

        void PickLevel(int index) => ShowLevel(index);

        void ShowLevel(int index, bool force = false)
        {
            if (_plans.Count == 0)
            {
                _shown = -1;
                _tip.Hide();
                _smallView.Plan = null;
                _largeView.Plan = null;
                if (LargeOpen) BuildRoomList();
                UpdateEmpty();
                UpdateScaleBar();
                return;
            }
            index = Mathf.Clamp(index, 0, _plans.Count - 1);
            var plan = _plans[index];
            if (!force && index == _shown && _smallView.Plan == plan) return;
            _shown = index;
            _tip.Hide();
            if (_smallView.Plan != plan) _smallView.Plan = plan;
            if (LargeOpen)
            {
                if (_largeView.Plan != plan) _largeView.Plan = plan;
                BuildRoomList();
            }
            _smallTabs.Select(index);
            _largeTabs.Select(index);
            UpdateEmpty();
            UpdateScaleBar();
        }

        /// <summary>Walk/fly: the level the camera is on (4×/s). A tab picked by hand sticks until this changes.</summary>
        void FollowCamera()
        {
            var v = _ui.S.Viewer;
            if (v == null || v.CurrentMode == HouseViewer.Mode.Orbit || _plans.Count == 0) return;
            var lp = _ui.Location.Plan;
            if (lp == null) return;
            int cam = IndexOfLevel(lp.LevelId);
            if (cam < 0 || cam == _cameraLevel) return;
            _cameraLevel = cam;
            ShowLevel(cam);
        }

        /// <summary>Every frame: the viewer marker — walk/fly on the camera's level, orbit only inside the footprint.</summary>
        void UpdateMarker()
        {
            if (!_smallShown && !LargeOpen) return;
            var s = _ui.S;
            var v = s.Viewer;
            var plan = ShownPlan;
            Vector2? pos = null;
            float yaw = 0f;
            if (v != null && plan != null && s.Session.HasProject)
            {
                var t = v.transform;
                Vector3 c = t.position;
                yaw = t.eulerAngles.y;
                bool on = v.CurrentMode == HouseViewer.Mode.Orbit
                    ? plan.Bounds.Contains(new Vector2(c.x, c.z)) && c.y > plan.Elevation - 0.2f && c.y < plan.Elevation + plan.Height + 0.6f
                    : _cameraLevel == _shown;
                if (on) pos = new Vector2(c.x, c.z);
            }
            if (_smallShown) _smallView.SetViewer(pos, yaw);
            if (LargeOpen) _largeView.SetViewer(pos, yaw);
        }

        int IndexOfLevel(string levelId)
        {
            if (levelId == null) return -1;
            for (int i = 0; i < _plans.Count; i++)
                if (_plans[i].LevelId == levelId) return i;
            return -1;
        }

        string LevelIdAt(int i) => i >= 0 && i < _plans.Count ? _plans[i].LevelId : null;

        /// <summary>The ground floor: the lowest level at or above grade.</summary>
        int GroundIndex()
        {
            for (int i = 0; i < _plans.Count; i++)
                if (_plans[i].Elevation >= -0.5f) return i;
            return _plans.Count > 0 ? 0 : -1;
        }

        bool HasGeometry()
        {
            foreach (var p in _plans)
                if (p.Walls.Count > 0 || p.Rooms.Count > 0) return true;
            return false;
        }

        /// <summary>The level's own name from the document (null when it has none).</summary>
        string LevelName(PlanGeometry plan)
        {
            var doc = _ui.S?.Session?.Doc;
            if (doc == null) return null;
            foreach (var l in doc.Levels)
                if (l.Id == plan.LevelId) return string.IsNullOrWhiteSpace(l.Name) ? null : l.Name.Trim();
            return null;
        }

        static string LevelSummary(PlanGeometry p)
        {
            if (p.Rooms.Count == 0) return p.Walls.Count > 0 ? "без комнат" : "пока пусто";
            float area = 0f;
            foreach (var r in p.Rooms) area += r.Area;
            return Ui.Area(area) + " · " + Ui.Plural(p.Rooms.Count, "комната", "комнаты", "комнат");
        }

        void UpdateEmpty()
        {
            string title = null, text = null;
            var plan = ShownPlan;
            if (plan == null || (plan.Walls.Count == 0 && plan.Rooms.Count == 0))
            {
                bool other = plan != null && HasGeometry();
                title = other ? "Этаж пока пуст" : "Плана пока нет";
                text = other ? "Выберите другой этаж или попросите ИИ достроить этот" : "Он появится, как только ИИ построит стены";
            }
            _smallEmpty.Set(title, text);
            _largeEmpty.Set(title, text);
        }

        // ------------------------------------------------------------------ rooms
        void HookCanvas(FloorPlanView view, VisualElement tipLayer, bool large)
        {
            view.RoomClicked += r =>
            {
                if (large ? !LargeOpen : !_smallShown) return;
                GoRoom(view.Plan, r);
            };
            view.RegisterCallback<PointerMoveEvent>(e => _tip.Track(tipLayer, view.Hovered, e.position));
            view.RegisterCallback<PointerLeaveEvent>(_ => _tip.Leave());
            view.RegisterCallback<PointerDownEvent>(_ => _tip.Press(), TrickleDown.TrickleDown);
        }

        void GoRoom(PlanGeometry plan, PlanGeometry.Room room)
        {
            if (plan == null || room == null || _ui.S?.Viewer == null) return;
            _tip.Hide();
            Tooltips.HideNow();
            if (LargeOpen) CloseLarge();
            _navUntil = Time.unscaledTime + NavigationHold;
            _ui.GoToRoom(plan, room);
        }

        void BuildRoomList()
        {
            foreach (var r in _rowList) Tooltips.Untip(r);
            _roomList.Clear();
            _rows.Clear();
            _rowList.Clear();
            var plan = ShownPlan;
            int n = plan?.Rooms.Count ?? 0;
            float area = 0f;
            // largest first: the rooms that matter most on top, the closets at the bottom
            _sortedRooms.Clear();
            if (plan != null) _sortedRooms.AddRange(plan.Rooms);
            _sortedRooms.Sort(ByAreaDesc);
            foreach (var room in _sortedRooms)
            {
                var row = BuildRow(plan, room);
                _roomList.Add(row);
                _rows[room] = row;
                _rowList.Add(row);
                area += room.Area;
            }
            _sortedRooms.Clear();
            string level = _shown >= 0 && _shown < _titles.Count ? _titles[_shown] : "";
            _roomsTitle.text = string.IsNullOrEmpty(level) ? "Комнаты"
                : n > 0 ? level + " · " + Ui.Plural(n, "комната", "комнаты", "комнат") : level;
            _levelArea.text = n > 0 ? Ui.Area(area) : "";
            string empty = n > 0 ? null
                : plan == null ? "Комнат пока нет"
                : plan.Walls.Count > 0 ? "Комнаты на этом этаже ещё не размечены"
                : "На этом этаже пока ничего нет";
            if (empty != null) _listEmpty.text = empty;
            Ui.Show(_listEmpty, empty != null);
            Ui.Show(_roomList, n > 0);
            _roomList.scrollOffset = Vector2.zero;
            SyncRowStates();
        }

        static int ByAreaDesc(PlanGeometry.Room a, PlanGeometry.Room b)
        {
            int c = b.Area.CompareTo(a.Area);
            return c != 0 ? c : string.CompareOrdinal(FloorPlanView.RoomTitle(a), FloorPlanView.RoomTitle(b));
        }

        VisualElement BuildRow(PlanGeometry plan, PlanGeometry.Room room)
        {
            string title = FloorPlanView.RoomTitle(room);
            string area = Ui.Area(room.Area);
            var icon = RoomIcons.Create(room.Type, 16);
            icon.AddToClassList("plan-row-icon");
            // the row the viewer stands in is `selected` (.plan-current) with an accent icon, as in the views popover
            var row = Ui.El("plan-row", icon, Ui.Text(title, "plan-row-name"), Ui.Text(area, "plan-row-area"));
            Ui.OnClick(row, () => { if (LargeOpen) GoRoom(plan, room); });
            row.RegisterCallback<PointerEnterEvent>(_ => { if (LargeOpen) _largeView.Highlighted = room; });
            row.RegisterCallback<PointerLeaveEvent>(_ => { if (_largeView.Highlighted == room) _largeView.Highlighted = null; });
            // the full name, even when the row ellipsises it
            string type = PlanGeometry.TypeName(room.Type);
            Tooltips.Tip(row, title + " · " + area, null, type != title ? type : null);
            return row;
        }

        void OnLargeHover(PlanGeometry.Room room)
        {
            foreach (var kv in _rows) kv.Value.EnableInClassList("plan-hl", kv.Key == room);
            if (room != null && _rows.TryGetValue(room, out var row)) _roomList.ScrollTo(row);
        }

        void SyncRowStates()
        {
            var cur = _largeView.CurrentRoom;
            foreach (var kv in _rows) kv.Value.EnableInClassList("plan-current", kv.Key == cur);
        }

        void UpdateTotals()
        {
            float area = 0f;
            int n = 0;
            foreach (var p in _plans)
                foreach (var r in p.Rooms) { area += r.Area; n++; }
            _totals.text = n == 0 ? "Комнат пока нет" : "Весь дом: " + Ui.Area(area) + " · " + Ui.Plural(n, "комната", "комнаты", "комнат");
        }

        /// <summary>Scale bar: the largest round length (0,5 … 50 м) that stays within 120 px.</summary>
        void UpdateScaleBar()
        {
            float ppm = _largeView.PixelsPerMeter;
            bool on = _largeView.HasContent && ppm > 0f && !float.IsNaN(ppm);
            Ui.Show(_scale, on);
            Ui.Show(_north, on);
            if (!on) return;
            float m = ScaleSteps[0];
            foreach (float step in ScaleSteps)
                if (step * ppm <= 120f) m = step;
            _scaleBar.style.width = Mathf.Round(m * ppm);
            _scaleLabel.text = Ui.Number(m) + " м";
        }

        // ================================================================== parts
        /// <summary>Level tabs: a small segmented control; digits only when the names do not fit; a caption for one level.</summary>
        sealed class LevelTabs
        {
            public readonly VisualElement Element;
            readonly Action<int> _onPick;
            readonly string _segClasses;
            readonly List<string> _compactLabels = new List<string>();
            Segmented _seg;
            string _key;
            bool _compact;

            public LevelTabs(Action<int> onPick, string classes, bool boxed)
            {
                _onPick = onPick;
                _segClasses = boxed ? "sm boxed" : "sm";
                Element = Ui.El(classes);
                Element.RegisterCallback<GeometryChangedEvent>(_ => CheckFit());
            }

            /// <param name="compact">short labels (digits) used when the titles do not fit</param>
            /// <param name="fallback">caption when there are no levels (null = nothing)</param>
            public void Build(string key, List<string> titles, List<string> compact, List<string> tips, int selected, string fallback)
            {
                if (key != _key)
                {
                    _key = key;
                    if (_seg != null)
                        for (int i = 0; i < _seg.Items.Count; i++) Tooltips.Untip(_seg.Items[i]);
                    _seg = null;
                    _compact = false;
                    _compactLabels.Clear();
                    _compactLabels.AddRange(compact);
                    Element.Clear();
                    if (titles.Count <= 1)
                    {
                        string caption = titles.Count == 1 ? titles[0] : fallback;
                        if (!string.IsNullOrEmpty(caption)) Element.Add(Ui.Text(caption, "plan-level-single ellipsis"));
                        return;
                    }
                    var items = new List<(string label, IconKind? icon, string tooltip, string keys)>(titles.Count);
                    for (int i = 0; i < titles.Count; i++) items.Add((titles[i], (IconKind?)null, tips[i], LevelKeys));
                    _seg = new Segmented(items, _onPick, _segClasses);
                    _seg.Element.style.flexShrink = 0;
                    _seg.Element.RegisterCallback<GeometryChangedEvent>(_ => CheckFit());
                    Element.Add(_seg.Element);
                }
                else if (_seg != null)
                {
                    // same levels: only the tooltips (areas, room counts) change
                    for (int i = 0; i < _seg.Items.Count && i < tips.Count; i++) Tooltips.Tip(_seg.Items[i], tips[i], LevelKeys);
                }
                Select(selected);
            }

            public void Select(int index)
            {
                if (_seg != null && index >= 0 && index < _seg.Items.Count && _seg.Selected != index) _seg.Select(index);
            }

            /// <summary>Names wider than the header: switch to digits (the tooltips keep the full names).</summary>
            void CheckFit()
            {
                if (_seg == null || _compact) return;
                float avail = Element.layout.width, need = _seg.Element.layout.width;
                if (float.IsNaN(avail) || float.IsNaN(need) || avail <= 0f || need <= 0f) return;
                if (need <= avail + 0.5f) return;
                _compact = true;
                for (int i = 0; i < _seg.Items.Count; i++)
                    _seg.SetLabel(i, i < _compactLabels.Count ? _compactLabels[i] : (i + 1).ToString());
            }
        }

        /// <summary>
        /// North indicator of the large plan (top left of the stage): a 24 px ring (border-strong) with a filled text-2
        /// arrowhead, «С» in Micro text-3 under it. Only the ring takes the pointer, for its «Север» tooltip.
        /// </summary>
        static class NorthBadge
        {
            public static VisualElement Create()
            {
                var dial = new NorthDial();
                Tooltips.Tip(dial, "Север");
                var badge = Ui.El("plan-north", dial, Ui.Text("С", "t-micro plan-north-label"));
                badge.pickingMode = PickingMode.Ignore;
                return badge;
            }
        }

        sealed class NorthDial : VisualElement
        {
            public NorthDial()
            {
                AddToClassList("plan-north-dial");
                generateVisualContent += Draw;
            }

            void Draw(MeshGenerationContext ctx)
            {
                // the ring is the element's USS border; the arrowhead is drawn on its 24 grid in the text colour
                var r = layout;
                if (float.IsNaN(r.width) || float.IsNaN(r.height) || r.width <= 0f || r.height <= 0f) return;
                float s = Mathf.Min(r.width, r.height) / 24f;
                var o = new Vector2((r.width - 24f * s) * 0.5f, (r.height - 24f * s) * 0.5f);
                var p = ctx.painter2D;
                p.fillColor = resolvedStyle.color;
                p.BeginPath();
                p.MoveTo(o + new Vector2(12f, 6f) * s);
                p.LineTo(o + new Vector2(15.5f, 14f) * s);
                p.LineTo(o + new Vector2(8.5f, 14f) * s);
                p.ClosePath();
                p.Fill();
            }
        }

        /// <summary>Centred message over an empty canvas.</summary>
        sealed class EmptyState
        {
            public readonly VisualElement Element;
            readonly Label _title, _text;

            public EmptyState(int iconSize, string classes)
            {
                _title = Ui.Text("", "plan-empty-title");
                _text = Ui.Text("", "plan-empty-text");
                Element = Ui.El("plan-empty " + classes, Ui.Icon(IconKind.Plan, iconSize, "plan-empty-icon"), _title, _text);
                Element.pickingMode = PickingMode.Ignore;
                Ui.Show(Element, false);
            }

            public void Set(string title, string text)
            {
                bool on = !string.IsNullOrEmpty(title);
                Ui.Show(Element, on);
                if (!on) return;
                _title.text = title;
                _text.text = text ?? "";
                Ui.Show(_text, !string.IsNullOrEmpty(text));
            }
        }

        /// <summary>
        /// Room hover tooltip «Гостиная · 24,6 м² — перейти» that follows the pointer (a room is a target inside one
        /// canvas, so the anchor-based <see cref="Tooltips"/> cannot place it). Same look and timing family: 350 ms
        /// rest, at once within 800 ms of the last one; hidden on press, on leave and while the cursor is captured.
        /// </summary>
        sealed class RoomTip
        {
            const long Delay = 350;
            const float Warm = 0.8f;

            readonly VisualElement _el;
            readonly Label _name;
            VisualElement _layer;
            PlanGeometry.Room _room, _pressed;
            Vector2 _pos;
            IVisualElementScheduledItem _pending;
            bool _shown;
            float _hiddenAt = -10f;

            public RoomTip()
            {
                _name = Ui.Text("", "tip-text");
                _el = Ui.El("tip plan-tip", _name, Ui.Text("— перейти", "tip-text plan-tip-go"));
                _el.pickingMode = PickingMode.Ignore;
                _el.RegisterCallback<GeometryChangedEvent>(_ => Place());
            }

            public void Track(VisualElement layer, PlanGeometry.Room room, Vector2 panelPos)
            {
                _pos = panelPos;
                if (room == null || Tooltips.Suppressed) { Hide(); return; }
                if (room == _pressed) return;
                _pressed = null;
                if (_el.parent != layer)
                {
                    Hide();
                    layer.Add(_el);
                }
                _layer = layer;
                if (room != _room)
                {
                    _room = room;
                    _name.text = FloorPlanView.RoomTitle(room) + " · " + Ui.Area(room.Area);
                    if (!_shown)
                    {
                        _pending?.Pause();
                        bool warm = Time.unscaledTime - _hiddenAt < Warm;
                        _pending = _el.schedule.Execute(ShowNow);
                        _pending.ExecuteLater(warm ? 0 : Delay);
                    }
                }
                if (_shown) Place();
            }

            public void Press()
            {
                var r = _room;
                Hide();
                _pressed = r;
            }

            public void Leave()
            {
                Hide();
                _pressed = null;
            }

            public void Hide()
            {
                if (_pending != null) { _pending.Pause(); _pending = null; }
                if (_shown)
                {
                    _shown = false;
                    _hiddenAt = Time.unscaledTime;
                    _el.RemoveFromClassList("show");
                }
                _room = null;
            }

            void ShowNow()
            {
                _pending = null;
                if (_room == null || _layer == null || _el.panel == null || Tooltips.Suppressed) return;
                _shown = true;
                Place();
                _el.AddToClassList("show");
            }

            void Place()
            {
                if (_layer == null || _layer.panel == null) return;
                float w = _el.resolvedStyle.width, h = _el.resolvedStyle.height;
                if (float.IsNaN(w) || float.IsNaN(h)) return;
                var root = _layer.worldBound;
                float x = Mathf.Clamp(_pos.x - w * 0.5f, root.xMin + 8f, Mathf.Max(root.xMin + 8f, root.xMax - w - 8f));
                float y = _pos.y - h - 14f;
                if (y < root.yMin + 8f) y = _pos.y + 24f;
                _el.style.left = x - root.xMin;
                _el.style.top = y - root.yMin;
            }
        }

        /// <summary>Room type → 16 px icon: the kit's icons where they exist, the rest drawn here in the same style.</summary>
        static class RoomIcons
        {
            public static VisualElement Create(RoomType type, int size)
            {
                IconKind? kind = type switch
                {
                    RoomType.Living => (IconKind?)IconKind.Sofa,
                    RoomType.Kitchen => IconKind.Kitchen,
                    RoomType.Bedroom => IconKind.Bed,
                    RoomType.Bathroom => IconKind.Bath,
                    RoomType.Hall => IconKind.Door,
                    RoomType.Stair => IconKind.Stairs,
                    RoomType.Terrace => IconKind.Sun,
                    RoomType.Other => IconKind.Plan,
                    _ => null,
                };
                if (kind.HasValue) return Ui.Icon(kind.Value, size);
                var glyph = new RoomGlyph(type);
                glyph.AddToClassList("icon-" + size);
                return glyph;
            }
        }

        /// <summary>
        /// Room icons the kit lacks (dining, corridor, wardrobe, utility, office, garage): Painter2D on a 24 grid,
        /// stroke 1.6, round caps — the kit's <see cref="Icon"/> style; the colour follows the element's text colour.
        /// </summary>
        sealed class RoomGlyph : VisualElement
        {
            readonly RoomType _type;
            Color _drawn;

            public RoomGlyph(RoomType type)
            {
                _type = type;
                AddToClassList("icon");
                pickingMode = PickingMode.Ignore;
                generateVisualContent += Draw;
                // hover/current styles recolour the row; generated content does not follow by itself
                schedule.Execute(() => { if (resolvedStyle.color != _drawn) MarkDirtyRepaint(); }).Every(60);
            }

            void Draw(MeshGenerationContext ctx)
            {
                var r = contentRect;
                if (float.IsNaN(r.width) || float.IsNaN(r.height)) return;
                float s = Mathf.Min(r.width, r.height) / 24f;
                if (s <= 0f) return;
                var o = new Vector2(r.x + (r.width - 24f * s) * 0.5f, r.y + (r.height - 24f * s) * 0.5f);
                var p = ctx.painter2D;
                var c = _drawn = resolvedStyle.color;
                p.strokeColor = c;
                p.fillColor = c;
                p.lineWidth = Mathf.Max(1.1f, 1.6f * s);
                p.lineCap = LineCap.Round;
                p.lineJoin = LineJoin.Round;
                Vector2 P(float x, float y) => o + new Vector2(x, y) * s;

                void Line(params float[] xy)
                {
                    p.BeginPath();
                    p.MoveTo(P(xy[0], xy[1]));
                    for (int i = 2; i < xy.Length; i += 2) p.LineTo(P(xy[i], xy[i + 1]));
                    p.Stroke();
                }
                void Poly(params float[] xy)
                {
                    p.BeginPath();
                    p.MoveTo(P(xy[0], xy[1]));
                    for (int i = 2; i < xy.Length; i += 2) p.LineTo(P(xy[i], xy[i + 1]));
                    p.ClosePath();
                    p.Stroke();
                }
                void Circle(float x, float y, float rad, bool fill = false)
                {
                    p.BeginPath();
                    p.Arc(P(x, y), rad * s, Angle.Degrees(0f), Angle.Degrees(360f));
                    p.ClosePath();
                    if (fill) p.Fill(); else p.Stroke();
                }
                void RoundRect(float x, float y, float w, float h, float rad)
                {
                    p.BeginPath();
                    p.MoveTo(P(x + rad, y));
                    p.ArcTo(P(x + w, y), P(x + w, y + h), rad * s);
                    p.ArcTo(P(x + w, y + h), P(x, y + h), rad * s);
                    p.ArcTo(P(x, y + h), P(x, y), rad * s);
                    p.ArcTo(P(x, y), P(x + w, y), rad * s);
                    p.ClosePath();
                    p.Stroke();
                }

                switch (_type)
                {
                    case RoomType.Dining:            // plate between fork and knife
                        Circle(12, 12, 5f);
                        Line(3.5f, 4, 3.5f, 7.5f, 5, 9, 6.5f, 7.5f, 6.5f, 4);
                        Line(5, 9, 5, 20);
                        Line(19.5f, 20, 19.5f, 4, 21, 6.5f, 21, 11.5f, 19.5f, 11.5f);
                        break;
                    case RoomType.Corridor:          // a hall in perspective with a centre line
                        Line(3.5f, 20.5f, 9, 3.5f);
                        Line(20.5f, 20.5f, 15, 3.5f);
                        Line(12, 18.5f, 12, 16);
                        Line(12, 12.5f, 12, 10.5f);
                        Line(12, 7.5f, 12, 6.5f);
                        break;
                    case RoomType.Wardrobe:          // coat hanger
                        p.BeginPath();
                        p.Arc(P(12, 6.2f), 2.2f * s, Angle.Degrees(-180f), Angle.Degrees(90f));
                        p.Stroke();
                        Line(12, 8.4f, 12, 10);
                        Poly(12, 10, 21, 17, 3, 17);
                        break;
                    case RoomType.Utility:           // washing machine
                        RoundRect(4.5f, 3, 15, 18, 2f);
                        Line(4.5f, 7, 19.5f, 7);
                        Circle(12, 14, 4f);
                        Circle(7.8f, 5, 0.8f, true);
                        break;
                    case RoomType.Office:            // monitor on a stand
                        RoundRect(3, 4.5f, 18, 11.5f, 1.5f);
                        Line(12, 16, 12, 19.5f);
                        Line(8, 19.5f, 16, 19.5f);
                        break;
                    case RoomType.Garage:            // car, front view
                        Poly(4.5f, 17.5f, 4.5f, 12.5f, 6.5f, 7.5f, 17.5f, 7.5f, 19.5f, 12.5f, 19.5f, 17.5f);
                        Line(4.5f, 12.5f, 19.5f, 12.5f);
                        Line(7, 17.5f, 7, 20);
                        Line(17, 17.5f, 17, 20);
                        Circle(8, 15, 0.9f, true);
                        Circle(16, 15, 0.9f, true);
                        break;
                    default:
                        RoundRect(3.5f, 3.5f, 17, 17, 2f);
                        break;
                }
            }
        }
    }
}
