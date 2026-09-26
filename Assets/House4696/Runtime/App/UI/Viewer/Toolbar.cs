using System.Collections.Generic;
using System.Text.RegularExpressions;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Bottom-centre toolbar (spec §3.3): camera modes on one sliding thumb in a recessed track · «Виды» with the views
    /// popover (§3.4, V) · «План» toggle (M) · snapshot (spinner while it waits for the light) · clean view (H) · help (?).
    /// Its width never changes (the «Виды» button is fixed, its label ellipsised), so nothing slides under the pointer.
    /// Fades out 800 ms after the cursor is captured for mouse look and slides left when the plan panel would crowd it.
    /// </summary>
    public sealed class Toolbar
    {
        const float HideAfterCapture = 0.8f;
        /// <summary>The toolbar's right edge stays at or left of W − 320 while the plan panel (288 at right 16) is open.</summary>
        const float PlanReserve = 320f;
        const float SideGutter = 16f;
        const string ViewsTitle = "Виды", ViewsKeys = "V · 1–9 · [ ]";

        // views popover geometry (fixed heights so the list can decide to scroll before it is laid out)
        const float PopoverMaxHeight = 480f, PopoverChrome = 10f;   // padding 4 + 4, border 1 + 1
        const float CaptionH = 30f, RowH = 40f, SepH = 9f, EmptyH = 64f;

        static readonly HouseViewer.Mode[] SegModes = { HouseViewer.Mode.Orbit, HouseViewer.Mode.Walk, HouseViewer.Mode.Fly };
        static readonly string[] ModeLabels = { "Осмотр", "Прогулка", "Полёт" };
        static readonly IconKind[] ModeIcons = { IconKind.Orbit, IconKind.Walk, IconKind.Fly };
        static readonly string[] ModeTips =
            { "Осмотр — вращайте дом мышью", "Прогулка — от первого лица", "Полёт — свободная камера сквозь стены" };
        static readonly string[] ModeKeys = { "⌘ 1", "⌘ 2", "⌘ 3" };
        /// <summary>A trailing parenthetical of a view name: «Фасад 3/4 (как на фото)» → «Фасад 3/4».</summary>
        static readonly Regex TrailingNote = new Regex(@"\s*\([^)]*\)\s*$", RegexOptions.CultureInvariant);

        readonly AppUI _ui;
        readonly VisualElement _wrap, _bar, _views, _plan, _snap, _snapIcon;
        readonly Label _viewsLabel;
        readonly ProgressRing _spinner;
        readonly Segmented _modes;

        string _viewsFull;
        bool _planShown, _snapBusy, _snapWaitsLight, _hidden;
        float _capturedAt = -1f, _shift;
        IVisualElementScheduledItem _openWhenReady;
        int _openTries;

        public VisualElement Element { get; }
        /// <summary>The «Виды» button (anchor of the views popover).</summary>
        public VisualElement ViewsButton => _views;
        /// <summary>Horizontal offset of the toolbar in panel px (≤ 0 while it makes room for the plan panel).</summary>
        public float ShiftX => _shift;

        public Toolbar(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("tb-host");
            Element.pickingMode = PickingMode.Ignore;
            _bar = Ui.El("tb-bar");

            // ---- modes: one thumb slides under the active segment, inside a recessed track (a choice within a group,
            // unlike the standalone «План» toggle)
            var items = new (string, IconKind?, string, string)[SegModes.Length];
            for (int i = 0; i < items.Length; i++) items[i] = (ModeLabels[i], ModeIcons[i], null, null);
            _modes = new Segmented(items, i => _ui.SwitchMode(SegModes[i]), "tb-modes");
            for (int i = 0; i < _modes.Items.Count; i++)
            {
                Tooltips.Tip(_modes.Items[i], ModeTips[i], ModeKeys[i], "Tab — следующий режим");
                if (i > 0) _modes.Items[i].AddToClassList("tb-gap");
            }
            _bar.Add(_modes.Element);
            _bar.Add(Ui.DividerV());

            // ---- views: fixed 208 px — pin + short view name (or «Виды», ellipsised) + chevron pinned right
            _views = Ui.El("tool tb-views");
            _views.Add(Ui.Icon(IconKind.Pin, 18));
            _viewsLabel = Ui.Text(ViewsTitle, "tool-label tb-views-label");
            _views.Add(_viewsLabel);
            _views.Add(Ui.Icon(IconKind.ChevronUp, 12, "tb-chevron"));
            Ui.OnClick(_views, ToggleViews);
            Tooltips.Tip(_views, ViewsTitle, ViewsKeys);
            _bar.Add(_views);

            // ---- plan toggle (neutral «selected» when on, never accent)
            _plan = Ui.Tool(IconKind.Plan, "План", TogglePlan, "План этажа", "M");
            _plan.AddToClassList("tb-gap");
            _bar.Add(_plan);
            _bar.Add(Ui.DividerV());

            // ---- snapshot (spinner while busy)
            _snap = Ui.El("tool icon-only tb-snap");
            _snapIcon = Ui.Icon(IconKind.Camera, 18);
            _spinner = new ProgressRing { Spinning = true };
            _spinner.AddToClassList("tb-spinner");
            Ui.Show(_spinner, false);
            _snap.Add(_snapIcon);
            _snap.Add(_spinner);
            Ui.OnClick(_snap, () => _ui.TakeSnapshot());
            Tooltips.Tip(_snap, "Сохранить снимок", "⌘ ⇧ S");
            _bar.Add(_snap);

            // fromClick: the hint toast shows on every click entry (the H key shows it only once)
            var clean = Ui.Tool(IconKind.EyeOff, null, () => _ui.SetCleanView(true, fromClick: true), "Скрыть интерфейс", "H");
            clean.AddToClassList("tb-gap");
            _bar.Add(clean);

            var help = Ui.Tool(IconKind.Help, null, () => _ui.ShowShortcuts(), "Управление и клавиши", "?");
            help.AddToClassList("tb-gap");
            _bar.Add(help);
            // the right end is kept free for «Мебель» and «Презентация» (spec §2, reserved space)

            _wrap = Elevation.Wrap(_bar, 12, 16, 4f, 0.45f, "tb-wrap");
            Element.Add(_wrap);

            var v = _ui.S?.Viewer;
            if (v != null)
            {
                v.PointChanged += (m, i) => UpdateViewsLabel();
                v.Configured += OnConfigured;
            }
            else
            {
                _modes.Element.SetEnabled(false);
                _views.SetEnabled(false);
            }
            Refresh();
        }

        // ------------------------------------------------------------------ state
        public void Refresh()
        {
            var v = _ui.S?.Viewer;
            if (v != null) _modes.Select(SegIndex(v.CurrentMode));
            UpdateViewsLabel();
            SyncPlan(true);
            SyncSnapshot(true);
        }

        public void Tick()
        {
            if (_ui.S == null) return;
            SyncPlan(false);
            SyncSnapshot(false);
            SyncVisibility();
            SyncShift();
        }

        static int SegIndex(HouseViewer.Mode mode) => mode switch
        {
            HouseViewer.Mode.Orbit => 0,
            HouseViewer.Mode.Walk => 1,
            _ => 2,
        };

        void TogglePlan()
        {
            if (_ui.Plan == null) return;
            _ui.Plan.Toggle();
            SyncPlan(true);
        }

        void SyncPlan(bool force)
        {
            bool on = _ui.Plan != null && _ui.Plan.IsOpen;
            if (on == _planShown && !force) return;
            _planShown = on;
            _plan.EnableInClassList("selected", on);
        }

        void SyncSnapshot(bool force)
        {
            var s = _ui.S;
            bool busy = s?.Snapshots != null && s.Snapshots.Busy;
            bool light = busy && s.Lighting != null && s.Lighting.IsBaking;
            if (!force && busy == _snapBusy && light == _snapWaitsLight) return;
            _snapBusy = busy;
            _snapWaitsLight = light;
            Ui.Show(_snapIcon, !busy);
            Ui.Show(_spinner, busy);
            _snap.EnableInClassList("tb-busy", busy);
            if (!busy) Tooltips.Tip(_snap, "Сохранить снимок", "⌘ ⇧ S");
            else Tooltips.Tip(_snap, light ? "Ждём расчёт света…" : "Сохраняем снимок…");
        }

        /// <summary>Mouse look: the toolbar steps aside 800 ms after the cursor is captured and returns on release.</summary>
        void SyncVisibility()
        {
            var v = _ui.S.Viewer;
            bool captured = v != null && v.CursorCaptured;
            float now = Time.unscaledTime;
            if (!captured) _capturedAt = -1f;
            else if (_capturedAt < 0f) _capturedAt = now;
            bool hide = captured && now - _capturedAt >= HideAfterCapture && !_ui.IsPopoverAnchor(_views);
            if (hide == _hidden) return;
            _hidden = hide;
            FadeBar(!hide);
        }

        static readonly List<EasingFunction> HideEasing = new List<EasingFunction>
            { new EasingFunction(EasingMode.EaseInOutSine), new EasingFunction(EasingMode.EaseInOutSine) };

        /// <summary>Chrome show 160 ms ease-out-cubic / hide 240 ms ease-in-out-sine (spec §7).</summary>
        void FadeBar(bool show)
        {
            Motion.Fade(_wrap, show, 160, 240);
            // Motion eases both ways out-cubic; the hide transition starts with this frame's styles, so override it
            if (!show) _wrap.style.transitionTimingFunction = HideEasing;
        }

        /// <summary>Keeps the toolbar clear of the plan panel: its right edge at or left of W − 320 (220 ms slide).</summary>
        void SyncShift()
        {
            float w = Element.layout.width, tw = _wrap.layout.width;
            if (float.IsNaN(w) || float.IsNaN(tw) || w <= 0f || tw <= 0f) return;
            float target = 0f;
            var plan = _ui.Plan;
            // PanelVisible: the small panel is really on screen (open, a project, the large plan closed)
            if (plan != null && plan.PanelVisible)
            {
                float right = (w + tw) * 0.5f, limit = w - PlanReserve;
                if (right > limit) target = limit - right;
                // never past the left gutter (a very narrow window): overlap the plan rather than the edge
                float minShift = SideGutter - (w - tw) * 0.5f;
                if (target < minShift) target = Mathf.Min(0f, minShift);
            }
            if (Mathf.Abs(target - _shift) < 0.5f) return;
            _shift = target;
            Element.style.translate = new Translate(target, 0);
        }

        // ------------------------------------------------------------------ «Виды» label
        void OnConfigured()
        {
            UpdateViewsLabel();
            // a rebuilt house brings new viewpoints: an open list is rebuilt in place
            if (_ui.IsPopoverAnchor(_views))
            {
                _ui.ClosePopover();
                OpenViews();
            }
        }

        /// <summary>
        /// The button shows the short name of the current view (or «Виды»); the tooltip carries the full one. The button
        /// is a fixed 208 px, so a view being picked or left (the first camera drag) never re-centres the toolbar.
        /// </summary>
        void UpdateViewsLabel()
        {
            var v = _ui.S?.Viewer;
            string full = null;
            if (v != null && v.CurrentPoint >= 0 && v.CurrentPoint < v.PointCount)
                full = ViewName(v.PointName(v.CurrentPoint), v.CurrentPoint);
            if (full == _viewsFull) return;                 // null = no view: the constructor's «Виды» stands
            _viewsFull = full;
            _viewsLabel.text = full == null ? ViewsTitle : ShortViewName(full);
            Tooltips.Tip(_views, full == null ? ViewsTitle : ViewsTitle + " · " + full, ViewsKeys);
        }

        static string ViewName(string name, int index) =>
            string.IsNullOrWhiteSpace(name) ? "Вид " + (index + 1) : name.Trim();

        /// <summary>
        /// Toolbar label of a view: the name without a trailing parenthetical («Фасад 3/4 (как на фото)» → «Фасад 3/4»).
        /// The views popover and the tooltip keep the full name.
        /// </summary>
        public static string ShortViewName(string name)
        {
            if (string.IsNullOrEmpty(name)) return name;
            string s = TrailingNote.Replace(name, "");
            return s.Length > 0 ? s : name;
        }

        // ------------------------------------------------------------------ views popover (§3.4)
        /// <summary>Opens/closes the views popover (V).</summary>
        public void ToggleViews()
        {
            if (_ui.S?.Session == null || !_ui.S.Session.HasProject || _ui.S.Viewer == null) return;
            if (_ui.IsPopoverAnchor(_views)) { _ui.ClosePopover(); return; }

            // the popover is placed at the button, so a hidden toolbar comes back first
            bool relayout = false;
            if (_ui.CleanView) { _ui.SetCleanView(false); relayout = true; }
            if (_hidden || !Ui.IsShown(_wrap))
            {
                _hidden = false;
                _capturedAt = -1f;
                FadeBar(true);
                relayout = true;
            }
            if (!relayout && _views.worldBound.width > 0f) { OpenViews(); return; }

            _openWhenReady?.Pause();
            _openTries = 0;
            _openWhenReady = _views.schedule.Execute(() =>
            {
                _openTries++;
                float bw = _views.worldBound.width;
                bool ready = !float.IsNaN(bw) && bw > 0f;
                if (!ready && _openTries < 30) return;
                _openWhenReady.Pause();
                if (ready && !_ui.PopoverOpen) OpenViews();
            }).Every(16);
        }

        void OpenViews() => _ui.TogglePopover(_views, BuildViews, 320f, PopPlacement.AboveCenter);

        VisualElement BuildViews()
        {
            var content = Ui.El("tb-views-pop");
            var v = _ui.S?.Viewer;
            var orbit = v != null ? v.OrbitPoints : null;
            var walk = v != null ? v.WalkPoints : null;
            int no = orbit?.Length ?? 0, nw = walk?.Length ?? 0;
            if (v == null || (no == 0 && nw == 0))
            {
                content.Add(Empty(true));
                return content;
            }

            var mode = v.CurrentMode;
            bool inOrbit = mode == HouseViewer.Mode.Orbit;
            // walk points are shown by the walk and the fly modes alike: fly stays in fly
            var walkMode = mode == HouseViewer.Mode.Fly ? HouseViewer.Mode.Fly : HouseViewer.Mode.Walk;
            var list = Ui.El("tb-views-list");
            float height = 0f;

            // groups are by camera mode (not by place: a walk can start outdoors), captioned with the toolbar's mode
            // names; the other mode's group says that a click there switches the mode
            list.Add(Caption(ModeName(HouseViewer.Mode.Orbit), !inOrbit));
            height += CaptionH;
            if (no == 0) { list.Add(Empty(false)); height += EmptyH; }
            for (int i = 0; i < no; i++)
            {
                list.Add(Row(IconKind.Orbit, ViewName(orbit[i].Name, i), i, HouseViewer.Mode.Orbit, inOrbit,
                    inOrbit && v.CurrentPoint == i));
                height += RowH;
            }

            list.Add(Ui.El("tb-views-sep"));
            height += SepH;
            list.Add(Caption(ModeName(walkMode), inOrbit));
            height += CaptionH;
            if (nw == 0) { list.Add(Empty(false)); height += EmptyH; }
            for (int i = 0; i < nw; i++)
            {
                list.Add(Row(IconKind.Walk, ViewName(walk[i].Name, i), i, walkMode, !inOrbit,
                    !inOrbit && v.CurrentPoint == i));
                height += RowH;
            }

            float max = PopoverMaxHeight - PopoverChrome;
            if (height <= max)
            {
                content.Add(list);
                return content;
            }
            var scroll = new ScrollView(ScrollViewMode.Vertical)
            {
                horizontalScrollerVisibility = ScrollerVisibility.Hidden,
                verticalScrollerVisibility = ScrollerVisibility.Auto,
                mouseWheelScrollSize = RowH,
            };
            scroll.AddToClassList("tb-views-scroll");
            scroll.style.height = max;
            scroll.Add(list);
            content.Add(scroll);
            return content;
        }

        static string ModeName(HouseViewer.Mode mode) => ModeLabels[SegIndex(mode)];

        /// <summary>
        /// Group caption (Caption Medium text-3). The group of the other mode gets «переключит режим» on the right:
        /// its keycaps are gone, and a click there changes the camera mode.
        /// </summary>
        static VisualElement Caption(string text, bool switchesMode)
        {
            if (!switchesMode) return Ui.Text(text, "tb-views-caption");
            var row = Ui.El("tb-views-caption tb-views-caption-row");
            row.pickingMode = PickingMode.Ignore;
            row.Add(Ui.Text(text, "tb-views-caption-text"));
            row.Add(Ui.Text("переключит режим", "tb-views-caption-hint"));
            return row;
        }

        VisualElement Row(IconKind icon, string name, int index, HouseViewer.Mode target, bool currentGroup, bool selected)
        {
            var row = Ui.El("tb-view-row");
            row.Add(Ui.Icon(icon, 16, "tb-view-icon"));
            row.Add(Ui.Text(name, "tb-view-name"));
            // keycaps 1–9 only in the current mode's group: that is what the digits do right now
            bool keyed = currentGroup && index < 9;
            if (keyed) row.Add(Ui.Kbd((index + 1).ToString()));
            if (selected) row.AddToClassList("selected");
            Ui.OnClick(row, () =>
            {
                _ui.ClosePopover();
                _ui.GoToView(target, index);
            });
            if (currentGroup)
                Tooltips.Tip(row, selected ? "Вы здесь" : "Показать этот вид", keyed ? (index + 1).ToString() : null);
            else
                Tooltips.Tip(row, target == HouseViewer.Mode.Orbit
                    ? "Откроется в режиме «Осмотр»"
                    : "Откроется в режиме «Прогулка»");
            return row;
        }

        static VisualElement Empty(bool all)
        {
            var box = Ui.El(all ? "tb-views-empty tb-views-empty-all" : "tb-views-empty");
            if (all) box.Add(Ui.Icon(IconKind.Pin, 24, "tb-views-empty-icon"));
            box.Add(Ui.Text("Видов пока нет", "tb-views-empty-title"));
            box.Add(Ui.Text("Попросите ИИ: «добавь вид из гостиной на террасу»", "tb-views-empty-hint"));
            return box;
        }
    }
}
