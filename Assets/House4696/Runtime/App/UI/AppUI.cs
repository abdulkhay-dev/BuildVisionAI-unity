using System;
using System.Collections.Generic;
using House4696.Model;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>Services the UI works with (set up by <see cref="HouseBootstrap"/>).</summary>
    public sealed class AppServices
    {
        public HouseSession Session;
        public HouseLighting Lighting;
        public LocalApi Api;
        public Thumbnails Thumbs;
        public AppSettings Settings;
        public HouseViewer Viewer;
        public Snapshots Snapshots;
        public string Version;
    }

    public enum PopPlacement { BelowLeft, BelowRight, BelowCenter, AboveLeft, AboveRight, AboveCenter }

    /// <summary>Where the viewer stands (walk/fly): level, its plan and the room (null outside / in orbit).</summary>
    public struct ViewerLocation
    {
        public LevelDef Level;
        public PlanGeometry Plan;
        public PlanGeometry.Room Room;
    }

    /// <summary>
    /// The app's interface root (UI Toolkit, built in code, styled by Resources/UI/*.uss). Owns the layers, the
    /// screens (<see cref="ProjectPill"/>, <see cref="StatusPill"/>, <see cref="Toolbar"/>, <see cref="ViewerOverlay"/>,
    /// <see cref="PlanPanel"/>, <see cref="HomeScreen"/>, <see cref="Veil"/>), dialogs, popovers/menus, toasts,
    /// tooltips, keyboard shortcuts with the Esc chain, and the app actions screens call (open/create/delete
    /// projects, go to a room, snapshot, undo…). Every frame it tells the camera whether the pointer and keyboard
    /// belong to the UI (<see cref="ViewerInput"/>); it runs before the viewer for that reason.
    /// </summary>
    [DefaultExecutionOrder(-100)]
    public sealed class AppUI : MonoBehaviour
    {
        static readonly string[] Sheets = { "UI/Tokens", "UI/Components", "UI/Chrome", "UI/Viewer", "UI/Plan", "UI/Home", "UI/Dialogs", "UI/Furniture" };

        public AppServices S { get; private set; }
        public AiStatus Ai { get; private set; }
        public VisualElement Root { get; private set; }
        public Toasts Toasts { get; private set; }

        public ProjectPill ProjectPill { get; private set; }
        public StatusPill StatusPill { get; private set; }
        public Toolbar Toolbar { get; private set; }
        public ViewerOverlay Overlay { get; private set; }
        public PlanPanel Plan { get; private set; }
        public HomeScreen Home { get; private set; }
        public Veil Veil { get; private set; }
        /// <summary>The furniture library (B): open = the 3D view arranges furniture (<see cref="Furniture"/>).</summary>
        public LibraryPanel Library { get; private set; }
        public FurnitureEditor Furniture { get; private set; }
        FurnitureOverlay _furnitureOverlay;

        /// <summary>Plans of the open house, one per level, lowest first (rebuilt after every change).</summary>
        public IReadOnlyList<PlanGeometry> Plans => _plans;
        /// <summary>Where the viewer stands (walk/fly; updated 4×/s).</summary>
        public ViewerLocation Location { get; private set; }
        public event Action LocationChanged;
        /// <summary>Raised after <see cref="Plans"/> were rebuilt (project opened or changed).</summary>
        public event Action PlansChanged;
        /// <summary>Chrome hidden (H): only toasts, the door prompt and the crosshair stay.</summary>
        public bool CleanView { get; private set; }

        UIDocument _doc;
        VisualElement _chromeLayer, _hudLayer, _homeLayer, _veilLayer, _modalLayer, _popLayer, _toastLayer, _tipLayer, _fade, _shutter;
        Tooltips _tips;
        readonly List<Modal> _modals = new List<Modal>();
        readonly List<PlanGeometry> _plans = new List<PlanGeometry>();
        VisualElement _popHost, _popAnchor;
        readonly List<(VisualElement row, MenuItem item)> _menuRows = new List<(VisualElement, MenuItem)>();
        int _menuHighlight = -1;
        bool _sceneDrag;
        float _nextLocation;
        HouseLighting.State _lastLightState;

        public bool ModalOpen => _modals.Count > 0;
        public bool PopoverOpen => _popHost != null;
        /// <summary>This frame's click only closed a popover (it must not also select or deselect in the view).</summary>
        public bool PopoverClosedThisFrame => _popClosedFrame == Time.frameCount;
        int _popClosedFrame = -1;
        public bool HomeOpen => Home != null && Home.IsOpen;
        public bool VeilVisible => Veil != null && Veil.Visible;
        public bool Typing { get; private set; }
        /// <summary>The 3D view owns the keyboard (no dialog, popover, Home, veil or text field).</summary>
        public bool ViewerFocused => !ModalOpen && !PopoverOpen && !HomeOpen && !VeilVisible && !Typing;

        // ------------------------------------------------------------------ setup
        void Awake()
        {
            // UI Toolkit reads the Input System through an EventSystem with its UI module
            if (FindAnyObjectByType<UnityEngine.EventSystems.EventSystem>() == null)
            {
                var es = new GameObject("EventSystem", typeof(UnityEngine.EventSystems.EventSystem),
                    typeof(UnityEngine.InputSystem.UI.InputSystemUIInputModule));
                es.transform.SetParent(transform, false);
            }

            var settings = ScriptableObject.CreateInstance<PanelSettings>();
            settings.name = "HousePanel";
            settings.themeStyleSheet = Resources.Load<ThemeStyleSheet>("UI/HouseTheme");
            settings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            settings.referenceResolution = new Vector2Int(1600, 940);
            settings.screenMatchMode = PanelScreenMatchMode.MatchWidthOrHeight;
            settings.match = 1f;
            settings.sortingOrder = 10;
            _doc = gameObject.AddComponent<UIDocument>();
            _doc.panelSettings = settings;

            Root = Ui.El("app");
            Root.pickingMode = PickingMode.Ignore;
            foreach (var path in Sheets)
            {
                var sheet = Resources.Load<StyleSheet>(path);
                if (sheet != null) Root.styleSheets.Add(sheet);
                else Debug.LogWarning($"[AppUI] Resources/{path}.uss missing");
            }
            var tree = _doc.rootVisualElement;
            tree.pickingMode = PickingMode.Ignore;
            tree.Add(Root);

            _chromeLayer = Layer("chrome");
            _hudLayer = Layer("hud");
            _homeLayer = Layer("home");
            _veilLayer = Layer("veil");
            _modalLayer = Layer("modals");
            _popLayer = Layer("popovers");
            _toastLayer = Layer("toasts");
            _tipLayer = Layer("tooltips");
            _fade = Ui.El("fade-overlay");
            _fade.pickingMode = PickingMode.Ignore;
            Root.Add(_fade);
            _shutter = Ui.El("shutter");
            _shutter.pickingMode = PickingMode.Ignore;
            Root.Add(_shutter);

            // nothing reaches the camera before the UI is bound
            ViewerInput.PointerBlocked = true;
            ViewerInput.KeyboardBlocked = true;
            _tips = new Tooltips(_tipLayer);
            Toasts = new Toasts(_toastLayer);
            Veil = new Veil(this);
            _veilLayer.Add(Veil.Element);
            Veil.ShowStartup();
        }

        VisualElement Layer(string name)
        {
            var l = Ui.El("layer");
            l.name = name;
            l.pickingMode = PickingMode.Ignore;
            Root.Add(l);
            return l;
        }

        /// <summary>Called once the app is ready: builds the interface around the services.</summary>
        public void Bind(AppServices services)
        {
            S = services;
            Ai = new AiStatus(S.Api, S.Settings);
            AiActivityLog.Attach(this);
            if (S.Viewer != null)
            {
                S.Viewer.DrawOverlay = false;
                S.Viewer.HandleHotkeys = false;
                S.Viewer.ModeChanged += OnModeChanged;
            }
            RebuildPlans();

            Furniture = new FurnitureEditor(this);
            _furnitureOverlay = new FurnitureOverlay(this, Furniture);
            Library = new LibraryPanel(this, Furniture);
            Overlay = new ViewerOverlay(this);
            Plan = new PlanPanel(this);
            Toolbar = new Toolbar(this);
            ProjectPill = new ProjectPill(this);
            StatusPill = new StatusPill(this);
            _chromeLayer.Add(_furnitureOverlay.Element);
            _chromeLayer.Add(Overlay.Element);
            _chromeLayer.Add(Library.Element);
            _chromeLayer.Add(Plan.Element);
            _chromeLayer.Add(Toolbar.Element);
            _chromeLayer.Add(ProjectPill.Element);
            _chromeLayer.Add(StatusPill.Element);
            _hudLayer.Add(Overlay.HudElement);
            Home = new HomeScreen(this);
            _homeLayer.Add(Home.Element);

            S.Session.ProjectChanged += OnProjectChanged;
            S.Session.Rebuilt += OnRebuilt;
            S.Session.ItemsChanged += Refresh;
            Ai.CallFinished += OnAiCallFinished;
            Ai.FirstCallEver += () => Toast("ИИ-ассистент подключился", IconKind.Sparkle, ToastKind.Ai);

            if (S.Session.HasProject) Veil.WaitForLighting();
            else
            {
                Veil.Hide();
                Home.Open();
            }
            Refresh();
        }

        void OnModeChanged(HouseViewer.Mode mode)
        {
            if (mode == HouseViewer.Mode.Walk) S.Settings.WalkedOnce = true;
            _nextLocation = 0f;
            Refresh();
        }

        void OnProjectChanged()
        {
            RebuildPlans();
            Refresh();
            if (!S.Session.HasProject && !HomeOpen) Home.Open();
            if (AiJustCalled() && S.Session.HasProject)
                Toast($"ИИ открыл «{S.Session.Doc.Meta?.Name}»", IconKind.Sparkle, ToastKind.Ai);
        }

        void OnRebuilt()
        {
            RebuildPlans();
            if (S.Session.HasProject && (S.Session.Doc.Walls.Count > 0 || S.Session.Doc.Rooms.Count > 0) && AiJustCalled())
                S.Settings.AiBuiltOnce = true;
            Refresh();
        }

        void OnAiCallFinished(string command, bool ok)
        {
            if (!ok) return;
            if (AiStatus.IsEdit(command))
                Toast(AiStatus.EditToast(command), IconKind.Sparkle, ToastKind.Ai, "Отменить последнюю", Undo,
                    "ai-edit", n => "ИИ внёс " + Ui.Plural(n, "правку", "правки", "правок"));
            else if (command == "undo") Toast("ИИ отменил правку", IconKind.Undo, ToastKind.Ai);
        }

        bool AiJustCalled() => S.Api != null && (DateTime.UtcNow - S.Api.LastCallUtc).TotalSeconds < 3.0;

        void RebuildPlans()
        {
            _plans.Clear();
            if (S?.Session?.HasProject == true)
            {
                var levels = new List<LevelDef>(S.Session.Doc.Levels);
                levels.Sort((a, b) => a.Elevation.CompareTo(b.Elevation));
                foreach (var l in levels)
                {
                    try { _plans.Add(PlanGeometry.Build(S.Session.Doc, l)); }
                    catch (Exception e) { Debug.LogWarning("[AppUI] plan " + l.Id + ": " + e.Message); }
                }
            }
            _nextLocation = 0f;
            PlansChanged?.Invoke();
        }

        /// <summary>Re-reads the session into every part of the interface.</summary>
        public void Refresh()
        {
            if (S == null) return;
            ProjectPill?.Refresh();
            StatusPill?.Refresh();
            Toolbar?.Refresh();
            Overlay?.Refresh();
            Plan?.Refresh();
            Library?.Refresh();
            if (HomeOpen) Home.Refresh();
        }

        public PlanGeometry PlanOf(string levelId) => _plans.Find(p => p.LevelId == levelId);

        // ------------------------------------------------------------------ projects
        public void ShowHome() { ClosePopover(); Home.Open(); }
        public void CloseHome() { if (S.Session.HasProject) Home.Close(); }

        /// <summary>Opens a project behind the veil (its preview, name and the lighting progress).</summary>
        public void OpenProject(string id)
        {
            ClosePopover();
            if (id == S.Session.ProjectId && S.Session.HasProject) { Home.Close(); return; }
            Veil.ShowOpening(id, NameOf(id));
            RunNextFrames(() =>
            {
                try
                {
                    S.Session.Open(id);
                    Home.Close();
                    Veil.WaitForLighting();
                }
                catch (Exception e)
                {
                    Debug.LogException(e);
                    Veil.Hide();
                    Toast("Не удалось открыть проект: " + e.Message, IconKind.Error, ToastKind.Error);
                }
            });
        }

        /// <summary>Creates and opens a project (template "empty" or a bundled sample id).</summary>
        public void CreateProject(string name, string description, string template)
        {
            ClosePopover();
            string shown = string.IsNullOrWhiteSpace(name) ? "Новый проект" : name.Trim();
            Veil.ShowOpening(null, shown);
            RunNextFrames(() =>
            {
                try
                {
                    S.Session.Create(shown, description, template, "Пользователь");
                    Home.Close();
                    Veil.WaitForLighting();
                    if (Ai.State == AiState.NotConnected) Toast("Проект создан", IconKind.Check, ToastKind.Success, "Подключить ИИ", ShowConnectAi);
                    else Toast("Проект создан", IconKind.Check, ToastKind.Success);
                }
                catch (Exception e)
                {
                    Debug.LogException(e);
                    Veil.Hide();
                    Toast("Не удалось создать проект: " + e.Message, IconKind.Error, ToastKind.Error);
                }
            });
        }

        /// <summary>Lets the veil paint before the main thread blocks (open/create rebuild the house).</summary>
        void RunNextFrames(Action action) => Root.schedule.Execute(action).ExecuteLater(60);

        /// <summary>Asks, then moves the project to the trash.</summary>
        public void ConfirmDelete(string id) { ClosePopover(); new DeleteProjectDialog(this, id).Show(); }

        public void DeleteProject(string id)
        {
            string name = NameOf(id);
            try
            {
                bool current = id == S.Session.ProjectId;
                S.Session.Delete(id);
                Toast($"Проект «{name}» удалён", IconKind.Trash);
                if (HomeOpen && !current) Home.Refresh();
            }
            catch (Exception e) { Toast("Не удалось удалить: " + e.Message, IconKind.Error, ToastKind.Error); }
        }

        public void RenameProject(string id, string name)
        {
            if (string.IsNullOrWhiteSpace(name)) return;
            try
            {
                S.Session.Rename(id, name);
                if (id != S.Session.ProjectId) { Refresh(); if (HomeOpen) Home.Refresh(); }      // the open one refreshes via ProjectChanged
            }
            catch (Exception e) { Toast("Не удалось переименовать: " + e.Message, IconKind.Error, ToastKind.Error); }
        }

        public void DuplicateProject(string id)
        {
            try
            {
                string copy = S.Session.Store.Duplicate(id);
                Toast($"Создана копия «{NameOf(copy)}»", IconKind.Duplicate, ToastKind.Success);
                if (HomeOpen) Home.Refresh();
            }
            catch (Exception e) { Toast("Не удалось скопировать: " + e.Message, IconKind.Error, ToastKind.Error); }
        }

        public string NameOf(string id)
        {
            if (string.IsNullOrEmpty(id)) return "";
            if (id == S.Session.ProjectId && S.Session.HasProject) return S.Session.Doc.Meta?.Name ?? id;
            try { return S.Session.Store.Load(id).Meta?.Name ?? id; }
            catch (Exception) { return id; }
        }

        /// <summary>Shows a file or folder in Finder (Explorer on Windows).</summary>
        public void RevealInFinder(string path)
        {
            try
            {
                if (Application.platform == RuntimePlatform.OSXPlayer || Application.platform == RuntimePlatform.OSXEditor)
                    System.Diagnostics.Process.Start("open", (System.IO.File.Exists(path) ? "-R " : "") + "\"" + path + "\"");
                else Application.OpenURL(new Uri(System.IO.Directory.Exists(path) ? path : System.IO.Path.GetDirectoryName(path)).AbsoluteUri);
            }
            catch (Exception e) { Debug.LogWarning("[AppUI] reveal: " + e.Message); }
        }

        // ------------------------------------------------------------------ dialogs
        public void ShowNewProject() { ClosePopover(); new NewProjectDialog(this).Show(); }
        public void ShowConnectAi() { ClosePopover(); new ConnectAiDialog(this).Show(); }
        public void ShowShortcuts() { ClosePopover(); new ShortcutsDialog(this).Show(); }

        public void ShowModal(Modal m)
        {
            ClosePopover();
            Tooltips.HideNow();
            _modals.Add(m);
            _modalLayer.Add(m.Host);
            m.Host.schedule.Execute(() => { m.Scrim.AddToClassList("open"); m.Shell.AddToClassList("open"); m.OnShown(); }).ExecuteLater(16);
        }

        public void CloseModal(Modal m)
        {
            if (!_modals.Remove(m)) return;
            m.Scrim.RemoveFromClassList("open");
            m.Shell.RemoveFromClassList("open");
            m.Host.pickingMode = PickingMode.Ignore;
            m.Host.schedule.Execute(() => m.Host.RemoveFromHierarchy()).ExecuteLater(200);
            m.OnClosed();
        }

        // ------------------------------------------------------------------ popovers & menus
        /// <summary>
        /// Shows a popover (surface-2, e2 shadow) at <paramref name="anchor"/>; clicking the same anchor again closes
        /// it. The anchor gets the class "popover-open" while it is open (use it for the pressed look).
        /// </summary>
        public void TogglePopover(VisualElement anchor, Func<VisualElement> build, float width, PopPlacement placement)
        {
            if (_popHost != null && _popAnchor == anchor) { ClosePopover(); return; }
            ClosePopover();
            var pop = Ui.El("popover");
            if (width > 0) pop.style.width = width;
            pop.Add(build());
            OpenPopover(pop, anchor, anchor.worldBound, placement);
        }

        /// <summary>Menu under/over an anchor (↑↓ ↩ Esc work); clicking the anchor again closes it.</summary>
        public void ShowMenu(VisualElement anchor, IList<MenuItem> items, PopPlacement placement = PopPlacement.BelowLeft, float minWidth = 220)
        {
            if (_popHost != null && _popAnchor == anchor) { ClosePopover(); return; }
            ClosePopover();
            OpenPopover(BuildMenu(items, minWidth), anchor, anchor.worldBound, placement);
        }

        /// <summary>Context menu at a panel position (right click).</summary>
        public void ShowMenuAt(Vector2 panelPos, IList<MenuItem> items, float minWidth = 220)
        {
            ClosePopover();
            OpenPopover(BuildMenu(items, minWidth), null, new Rect(panelPos, Vector2.zero), PopPlacement.BelowLeft);
        }

        public bool IsPopoverAnchor(VisualElement e) => _popHost != null && _popAnchor == e;

        VisualElement BuildMenu(IList<MenuItem> items, float minWidth)
        {
            var menu = Ui.El("popover menu");
            menu.style.minWidth = minWidth;
            _menuRows.Clear();
            _menuHighlight = -1;
            foreach (var it in items)
            {
                if (it.Separator) { menu.Add(Ui.El("menu-sep")); continue; }
                if (it.Header != null) { menu.Add(Ui.Text(it.Header, "menu-header")); continue; }
                var row = Ui.El("menu-item");
                if (it.Custom != null) row.Add(it.Custom);
                else
                {
                    if (it.Icon.HasValue) row.Add(Ui.Icon(it.Icon.Value, 16));
                    row.Add(Ui.Text(it.Label, "menu-label"));
                    if (it.Checked) row.Add(Ui.Icon(IconKind.Check, 16, "c-accent"));
                    if (!string.IsNullOrEmpty(it.Shortcut)) row.Add(Ui.Text(it.Shortcut, "menu-shortcut"));
                }
                if (it.Custom != null) row.AddToClassList("menu-item-custom");
                if (!string.IsNullOrEmpty(it.RowClass)) Ui.AddClasses(row, it.RowClass);
                if (it.Danger) row.AddToClassList("danger");
                if (it.Disabled) row.SetEnabled(false);
                var item = it;
                Ui.OnClick(row, () => RunMenuItem(item));
                int index = _menuRows.Count;
                row.RegisterCallback<PointerEnterEvent>(_ => HighlightMenu(index));
                _menuRows.Add((row, it));
                menu.Add(row);
            }
            return menu;
        }

        void RunMenuItem(MenuItem item)
        {
            if (item.Disabled) return;
            ClosePopover();
            item.Action?.Invoke();
        }

        void HighlightMenu(int index)
        {
            for (int i = 0; i < _menuRows.Count; i++) _menuRows[i].row.EnableInClassList("highlight", i == index);
            _menuHighlight = index;
        }

        void OpenPopover(VisualElement pop, VisualElement anchor, Rect a, PopPlacement placement)
        {
            bool up = placement >= PopPlacement.AboveLeft;
            if (up) pop.AddToClassList("up");
            var host = Elevation.Wrap(pop, 12, 24, 10, 0.55f, "popover-host");
            host.style.position = Position.Absolute;
            host.style.visibility = Visibility.Hidden;          // measured first, then placed
            _popLayer.Add(host);
            _popHost = host;
            _popAnchor = anchor;
            anchor?.AddToClassList("popover-open");
            Tooltips.HideNow();
            void Place()
            {
                var root = Root.worldBound;
                float w = pop.resolvedStyle.width, h = pop.resolvedStyle.height;
                if (float.IsNaN(w) || float.IsNaN(h)) return;
                bool left = placement == PopPlacement.BelowLeft || placement == PopPlacement.AboveLeft;
                bool right = placement == PopPlacement.BelowRight || placement == PopPlacement.AboveRight;
                float x = left ? a.xMin : right ? a.xMax - w : a.center.x - w * 0.5f;
                float y = up ? a.yMin - 8f - h : a.yMax + 8f;
                // flip at the edges
                if (!up && y + h > root.yMax - 8f && a.yMin - 8f - h > root.yMin) y = a.yMin - 8f - h;
                if (up && y < root.yMin + 8f) y = a.yMax + 8f;
                x = Mathf.Clamp(x, root.xMin + 8f, Mathf.Max(root.xMin + 8f, root.xMax - w - 8f));
                y = Mathf.Clamp(y, root.yMin + 8f, Mathf.Max(root.yMin + 8f, root.yMax - h - 8f));
                host.style.left = x - root.xMin;
                host.style.top = y - root.yMin;
                host.style.visibility = Visibility.Visible;
            }
            pop.RegisterCallback<GeometryChangedEvent>(_ => Place());
            pop.schedule.Execute(() => pop.AddToClassList("open")).ExecuteLater(16);
        }

        public void ClosePopover()
        {
            if (_popHost == null) return;
            var host = _popHost;
            _popAnchor?.RemoveFromClassList("popover-open");
            _popHost = null;
            _popAnchor = null;
            _menuRows.Clear();
            _menuHighlight = -1;
            var pop = host.Q(className: "popover");
            pop?.RemoveFromClassList("open");
            host.pickingMode = PickingMode.Ignore;
            if (pop != null) pop.pickingMode = PickingMode.Ignore;
            host.schedule.Execute(() => host.RemoveFromHierarchy()).ExecuteLater(120);
        }

        // ------------------------------------------------------------------ feedback
        public void Toast(string text, IconKind icon = IconKind.Info, ToastKind kind = ToastKind.Info, string action = null, Action onAction = null,
            string mergeKey = null, Func<int, string> mergeText = null)
            => Toasts.Show(text, icon, kind, action, onAction, mergeKey, mergeText);

        /// <summary>Copies to the clipboard with a toast.</summary>
        public void Copy(string text, string toast = "Скопировано — вставьте в чат с ИИ")
        {
            GUIUtility.systemCopyBuffer = text;
            Toast(toast, IconKind.Check, ToastKind.Success);
        }

        // ------------------------------------------------------------------ viewer actions
        public void SwitchMode(HouseViewer.Mode mode)
        {
            if (S.Viewer == null || !S.Session.HasProject) return;
            if (S.Viewer.CurrentMode != mode) S.Viewer.SwitchTo(mode);
        }

        /// <summary>Goes to a viewpoint of a mode (switching mode first when needed).</summary>
        public void GoToView(HouseViewer.Mode mode, int index)
        {
            if (S.Viewer == null) return;
            if (S.Viewer.CurrentMode != mode) S.Viewer.SwitchTo(mode);
            S.Viewer.GoToPoint(index);
        }

        /// <summary>
        /// Walks into a room: a named walk view inside it if there is one, else the photographer's spot
        /// (<see cref="PlanGeometry.ViewSpot"/>), else its interior point — through a short fade.
        /// </summary>
        public void GoToRoom(PlanGeometry plan, PlanGeometry.Room room)
        {
            if (S.Viewer == null || plan == null || room == null) return;
            WalkPoint target = default;
            bool found = false;
            foreach (var w in S.Viewer.WalkPoints)
                if (Mathf.Abs(w.Feet.y - plan.Elevation) < 1f && PlanGeometry.Contains(room.Outline, new Vector2(w.Feet.x, w.Feet.z)))
                {
                    target = w; found = true; break;
                }
            if (!found)
            {
                if (PlanGeometry.ViewSpot(room.Outline, plan.Elevation, out var feet, out float yaw))
                    target = new WalkPoint { Feet = feet, Yaw = yaw, Pitch = 5f };
                else
                {
                    var p = PlanGeometry.InteriorPoint(room.Outline, out _);
                    target = new WalkPoint { Feet = new Vector3(p.x, plan.Elevation + 0.02f, p.y), Yaw = 0f, Pitch = 0f };
                }
            }
            target.Name = room.Name;
            FadeThrough(() => S.Viewer.TeleportWalk(target));
        }

        /// <summary>Fades to bg-app (120 ms), runs <paramref name="mid"/>, fades back (180 ms).</summary>
        public void FadeThrough(Action mid)
        {
            _fade.style.transitionProperty = new List<StylePropertyName> { new StylePropertyName("opacity") };
            _fade.style.transitionDuration = new List<TimeValue> { new TimeValue(120, TimeUnit.Millisecond) };
            _fade.style.transitionTimingFunction = new List<EasingFunction> { new EasingFunction(EasingMode.EaseIn) };
            _fade.style.opacity = 1f;
            _fade.schedule.Execute(() =>
            {
                try { mid(); }
                catch (Exception e) { Debug.LogException(e); }
                _fade.style.transitionDuration = new List<TimeValue> { new TimeValue(180, TimeUnit.Millisecond) };
                _fade.style.transitionTimingFunction = new List<EasingFunction> { new EasingFunction(EasingMode.EaseOut) };
                _fade.style.opacity = 0f;
            }).ExecuteLater(140);
        }

        public void TakeSnapshot()
        {
            if (S.Snapshots == null || S.Snapshots.Busy || !S.Session.HasProject) return;
            StartCoroutine(S.Snapshots.Capture(path =>
            {
                Shutter();
                Toast("Снимок сохранён", IconKind.Camera, ToastKind.Success, "Показать в Finder", () => RevealInFinder(path));
            }, err => Toast("Не удалось сохранить снимок: " + err, IconKind.Error, ToastKind.Error)));
        }

        void Shutter()
        {
            _shutter.style.transitionProperty = new List<StylePropertyName> { new StylePropertyName("opacity") };
            _shutter.style.transitionTimingFunction = new List<EasingFunction> { new EasingFunction(EasingMode.Linear) };
            _shutter.style.transitionDuration = new List<TimeValue> { new TimeValue(60, TimeUnit.Millisecond) };
            _shutter.style.opacity = 0.2f;
            _shutter.schedule.Execute(() =>
            {
                _shutter.style.transitionDuration = new List<TimeValue> { new TimeValue(140, TimeUnit.Millisecond) };
                _shutter.style.opacity = 0f;
            }).ExecuteLater(70);
        }

        /// <summary>One step back in the project history (the last change, the AI's or the user's).</summary>
        public void Undo()
        {
            if (!S.Session.HasProject) return;
            if (S.Session.Undo()) Toast("Правка отменена", IconKind.Undo);
            else Toast("Отменять больше нечего", IconKind.Info);
        }

        /// <param name="fromClick">entered from the toolbar button: always explain how to return (the H key only once).</param>
        public void SetCleanView(bool on, bool fromClick = false)
        {
            if (CleanView == on) return;
            CleanView = on;
            ClosePopover();
            if (on && (fromClick || !S.Settings.CleanViewHintShown))
            {
                S.Settings.CleanViewHintShown = true;
                Toast("Интерфейс скрыт — {H} или {Esc}, чтобы вернуть", IconKind.EyeOff);
            }
            Motion.Fade(_chromeLayer, !on && S.Session.HasProject, 160, 240);
        }

        public void ToggleFullscreen() => Screen.fullScreen = !Screen.fullScreen;

        // ------------------------------------------------------------------ furniture
        /// <summary>
        /// The library just opened: the hints for arranging furniture show under the view; from outside (orbit) a toast offers
        /// to walk in — furniture is arranged from the inside.
        /// </summary>
        public void OnLibraryOpened()
        {
            Overlay?.ShowFurnitureHints();
            if (S.Viewer == null || S.Viewer.CurrentMode != HouseViewer.Mode.Orbit) return;
            var room = MainRoom(out var plan);
            if (room == null) return;
            Toast("Мебель удобнее расставлять изнутри", IconKind.Walk, ToastKind.Info, "Войти в дом", () => GoToRoom(plan, room));
        }

        /// <summary>The largest room of the lowest floor that has rooms (not a terrace).</summary>
        PlanGeometry.Room MainRoom(out PlanGeometry plan)
        {
            plan = null;
            PlanGeometry.Room best = null;
            foreach (var p in _plans)
            {
                if (p.Elevation < -0.5f) continue;          // basements
                foreach (var r in p.Rooms)
                    if (r.Type != RoomType.Terrace && (best == null || r.Area > best.Area)) { best = r; plan = p; }
                if (best != null) break;
            }
            return best;
        }

        /// <summary>Retries a failed lighting bake.</summary>
        public void RetryLighting() => S.Lighting?.Rebake();

        // ------------------------------------------------------------------ frame
        void Update()
        {
            if (S == null || Root.panel == null)
            {
                Veil?.Tick();
                return;
            }
            Ai.Tick();
            UpdateInputOwnership();
            Furniture.Tick();           // before the camera: it claims the left button, the wheel and the arrows it uses
            HandleKeys();
            UpdateLocation();
            WatchLighting();
            foreach (var m in _modals.ToArray()) m.Tick();
            ProjectPill.Tick();
            StatusPill.Tick();
            Toolbar.Tick();
            Overlay.Tick();
            Plan.Tick();
            Library.Tick();
            _furnitureOverlay.Tick();
            if (HomeOpen) Home.Tick();
            Veil.Tick();
            Toasts.Tick();
            _toastLayer.EnableInClassList("under-header", HomeOpen);     // Home's header owns the top edge
            _tips.Tick();
            bool chrome = S.Session.HasProject && !VeilVisible;
            if (!chrome && Ui.IsShown(_chromeLayer)) Ui.Show(_chromeLayer, false);
            else if (chrome && !CleanView && !Ui.IsShown(_chromeLayer)) Motion.Fade(_chromeLayer, true);
        }

        void WatchLighting()
        {
            var l = S.Lighting;
            if (l == null) return;
            if (l.Current == HouseLighting.State.Failed && _lastLightState != HouseLighting.State.Failed)
                Toast("Не удалось рассчитать освещение", IconKind.Warning, ToastKind.Error, "Повторить", RetryLighting);
            _lastLightState = l.Current;
        }

        void UpdateLocation()
        {
            if (Time.unscaledTime < _nextLocation) return;
            _nextLocation = Time.unscaledTime + 0.25f;
            var v = S.Viewer;
            var loc = new ViewerLocation();
            if (v != null && S.Session.HasProject && _plans.Count > 0 && v.CurrentMode != HouseViewer.Mode.Orbit)
            {
                Vector3 feet = v.CurrentMode == HouseViewer.Mode.Walk ? v.WalkFeet : v.transform.position - Vector3.up * 1.65f;
                PlanGeometry plan = _plans[0];
                foreach (var p in _plans) if (feet.y >= p.Elevation - 0.4f) plan = p;
                loc.Plan = plan;
                loc.Level = S.Session.Doc.Levels.Find(l => l.Id == plan.LevelId);
                loc.Room = plan.RoomAt(new Vector2(feet.x, feet.z));
            }
            bool changed = loc.Plan != Location.Plan || loc.Room != Location.Room;
            Location = loc;
            if (changed) LocationChanged?.Invoke();
        }

        /// <summary>Decides whether the pointer and the keyboard belong to the UI or to the 3D view this frame.</summary>
        void UpdateInputOwnership()
        {
            bool blocking = ModalOpen || HomeOpen || VeilVisible;
            var mouse = Mouse.current;
            bool anyHeld = mouse != null && (mouse.leftButton.isPressed || mouse.rightButton.isPressed || mouse.middleButton.isPressed);
            bool anyDown = mouse != null && (mouse.leftButton.wasPressedThisFrame || mouse.rightButton.wasPressedThisFrame || mouse.middleButton.wasPressedThisFrame);
            bool locked = UnityEngine.Cursor.lockState == CursorLockMode.Locked;
            bool over = !locked && PointerOverUI();

            // a drag that started on the 3D view keeps the camera even when the pointer crosses a panel
            if (anyDown) _sceneDrag = !over && !blocking && !PopoverOpen;
            else if (!anyHeld) _sceneDrag = false;
            if (anyDown && _popHost != null && !OverPopover())
            {
                ClosePopover();
                _popClosedFrame = Time.frameCount;
            }

            ViewerInput.PointerBlocked = blocking || PopoverOpen || (over && !_sceneDrag);
            var focused = Root.panel.focusController?.focusedElement as VisualElement;
            Typing = focused is TextField || focused?.GetFirstAncestorOfType<TextField>() != null;
            ViewerInput.KeyboardBlocked = blocking || Typing || PopoverOpen;
            Tooltips.Suppressed = locked || _sceneDrag;
        }

        /// <summary>Pointer position in panel coordinates.</summary>
        public Vector2 PointerPanelPosition()
        {
            var mouse = Mouse.current;
            if (mouse == null || Root.panel == null) return Vector2.zero;
            var screen = mouse.position.ReadValue();
            return RuntimePanelUtils.ScreenToPanel(Root.panel, new Vector2(screen.x, Screen.height - screen.y));
        }

        /// <summary>The pointer is over a pickable UI element (not the bare 3D view).</summary>
        public bool PointerOverUI()
        {
            if (Root.panel == null) return false;
            return PickedUI(PointerPanelPosition());
        }

        /// <summary>A screen point (px, origin at the bottom left) is over a pickable UI element.</summary>
        public bool PointerOverUI(Vector2 screen)
        {
            if (Root.panel == null) return false;
            return PickedUI(RuntimePanelUtils.ScreenToPanel(Root.panel, new Vector2(screen.x, Screen.height - screen.y)));
        }

        bool PickedUI(Vector2 panelPos)
        {
            var picked = Root.panel.Pick(panelPos);
            return picked != null && picked != Root && picked != _doc.rootVisualElement;
        }

        bool OverPopover()
        {
            if (_popHost == null) return false;
            var pos = PointerPanelPosition();
            var pop = _popHost.Q(className: "popover");
            return (pop != null && pop.worldBound.Contains(pos)) || (_popAnchor != null && _popAnchor.worldBound.Contains(pos));
        }

        // ------------------------------------------------------------------ keyboard
        void HandleKeys()
        {
            var kb = Keyboard.current;
            if (kb == null) return;
            bool meta = kb.leftMetaKey.isPressed || kb.rightMetaKey.isPressed;
            bool ctrl = kb.leftCtrlKey.isPressed || kb.rightCtrlKey.isPressed;
            bool cmd = meta || ctrl;
            bool shift = kb.leftShiftKey.isPressed || kb.rightShiftKey.isPressed;
            bool Down(Key k) => kb[k].wasPressedThisFrame;

            if (Down(Key.Escape)) { Escape(); return; }

            // menus: ↑↓ ↩
            if (_menuRows.Count > 0)
            {
                if (Down(Key.DownArrow)) { HighlightMenu(NextMenuRow(_menuHighlight, 1)); return; }
                if (Down(Key.UpArrow)) { HighlightMenu(NextMenuRow(_menuHighlight, -1)); return; }
                if ((Down(Key.Enter) || Down(Key.NumpadEnter)) && _menuHighlight >= 0) { RunMenuItem(_menuRows[_menuHighlight].item); return; }
            }

            if (ModalOpen)
            {
                var top = _modals[_modals.Count - 1];
                if ((Down(Key.Enter) || Down(Key.NumpadEnter)) && top.Primary != null && !IsMultilineFocused()) top.Primary();
                return;
            }
            if (VeilVisible)
            {
                if (Down(Key.Enter) || Down(Key.NumpadEnter)) Veil.Skip();
                return;
            }

            // global (⌘) shortcuts
            if (cmd)
            {
                if (meta && ctrl && Down(Key.F)) { ToggleFullscreen(); return; }
                if (Down(Key.O)) { if (HomeOpen) CloseHome(); else ShowHome(); return; }
                if (Down(Key.N)) { ShowNewProject(); return; }
                if (HomeOpen) { Home.OnKey(kb, true, shift); return; }
                if (Down(Key.Comma)) { StatusPill.ToggleSettings(); return; }
                if (Down(Key.Z) && !Typing) { Undo(); return; }
                if (!Typing && Furniture.OnCommandKey(kb)) return;
                if (Down(Key.S) && shift) { TakeSnapshot(); return; }
                if (Down(Key.Digit1)) { SwitchMode(HouseViewer.Mode.Orbit); return; }
                if (Down(Key.Digit2)) { SwitchMode(HouseViewer.Mode.Walk); return; }
                if (Down(Key.Digit3)) { SwitchMode(HouseViewer.Mode.Fly); return; }
                return;
            }
            if (Down(Key.F11)) { ToggleFullscreen(); return; }
            if (!Typing && (Down(Key.F1) || (Down(Key.Slash) && shift))) { ShowShortcuts(); return; }
            if (HomeOpen) { Home.OnKey(kb, false, shift); return; }
            if (PopoverOpen && !Typing && Down(Key.V) && IsPopoverAnchor(Toolbar.ViewsButton)) { ClosePopover(); return; }
            if (Typing || PopoverOpen || !S.Session.HasProject || S.Viewer == null) return;
            if (Plan.LargeOpen)
            {
                // behind the large plan only the plan keys work
                if (Down(Key.M)) Plan.Toggle();
                else if (Down(Key.P)) Plan.ToggleLarge();
                else if (Down(Key.PageUp)) Plan.LevelStep(1);
                else if (Down(Key.PageDown)) Plan.LevelStep(-1);
                return;
            }

            // furniture: B opens the library; while it is open R, ⌫ and the arrows edit the selected item
            bool alt = kb.leftAltKey.isPressed || kb.rightAltKey.isPressed;
            if (Down(Key.B)) { Library.Toggle(); return; }
            if (Library.IsOpen && Furniture.OnKey(kb, shift, alt)) return;

            // viewer shortcuts (need viewer focus)
            var v = S.Viewer;
            if (Down(Key.Tab)) { v.SwitchTo((HouseViewer.Mode)(((int)v.CurrentMode + (shift ? 2 : 1)) % 3)); return; }
            for (int i = 0; i < 9; i++)
                if (Down(Key.Digit1 + i)) { v.GoToPoint(i); return; }
            if (Down(Key.LeftBracket)) { StepPoint(-1); return; }
            if (Down(Key.RightBracket)) { StepPoint(1); return; }
            if (Down(Key.V)) { Toolbar.ToggleViews(); return; }
            if (Down(Key.M)) { Plan.Toggle(); return; }
            if (Down(Key.P)) { Plan.ToggleLarge(); return; }
            if (Down(Key.PageUp)) { Plan.LevelStep(1); return; }
            if (Down(Key.PageDown)) { Plan.LevelStep(-1); return; }
            if (Down(Key.H)) { SetCleanView(!CleanView); return; }
        }

        void StepPoint(int dir)
        {
            var v = S.Viewer;
            int n = v.PointCount;
            if (n == 0) return;
            int i = v.CurrentPoint < 0 ? (dir > 0 ? 0 : n - 1) : ((v.CurrentPoint + dir) % n + n) % n;
            v.GoToPoint(i);
        }

        bool IsMultilineFocused()
        {
            var f = Root.panel.focusController?.focusedElement as VisualElement;
            var tf = f as TextField ?? f?.GetFirstAncestorOfType<TextField>();
            return tf != null && tf.multiline;
        }

        int NextMenuRow(int from, int dir)
        {
            int n = _menuRows.Count;
            int i = from < 0 ? (dir > 0 ? -1 : n) : from;
            for (int step = 0; step < n; step++)
            {
                i = (i + dir + n) % n;
                if (!_menuRows[i].item.Disabled) return i;
            }
            return from;
        }

        /// <summary>
        /// Esc: menu/popover → dialog/large plan → veil → text field → placing/dragging/selection → library → release cursor
        /// → leave clean view → close Home.
        /// </summary>
        void Escape()
        {
            if (_popHost != null) { ClosePopover(); return; }
            if (_modals.Count > 0) { _modals[_modals.Count - 1].Dismiss(); return; }
            if (Plan != null && Plan.LargeOpen) { Plan.CloseLarge(); return; }
            if (VeilVisible) { Veil.Skip(); return; }
            if (Typing) { Root.panel.focusController?.focusedElement?.Blur(); return; }
            if (Furniture != null && Furniture.Escape()) return;
            if (Library != null && Library.IsOpen) { Library.Close(); return; }
            if (UnityEngine.Cursor.lockState == CursorLockMode.Locked) return;   // the viewer releases it this frame
            if (CleanView) { SetCleanView(false); return; }
            if (HomeOpen) { CloseHome(); return; }
        }

        void OnDestroy()
        {
            ViewerInput.PointerBlocked = false;
            ViewerInput.KeyboardBlocked = false;
            Tooltips.Suppressed = false;
            ViewerInput.PointerTool = false;
            ViewerInput.LeftClaimed = false;
            ViewerInput.ArrowsClaimed = false;
            ViewerInput.WheelClaimed = false;
            if (S?.Session != null)
            {
                S.Session.ProjectChanged -= OnProjectChanged;
                S.Session.Rebuilt -= OnRebuilt;
                S.Session.ItemsChanged -= Refresh;
            }
        }
    }
}
