using System;
using System.Collections.Generic;
using House4696.Generation;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Top-left project pill (spec §3.1): the House mark (→ all projects, ⌘O), the project name with its menu (recent
    /// projects, all projects, new, inline rename, reveal in Finder, delete), the walk/fly breadcrumb
    /// («| 1 этаж › Гостиная» after a divider, from <see cref="AppUI.Location"/>) and the check-issues badge (→ issues
    /// popover). Both popovers hang from the pill's surface: left edge at 16, 8 px below the pill.
    /// Styles: Resources/UI/Chrome.uss (pp-*).
    /// </summary>
    public sealed class ProjectPill
    {
        const int RecentCount = 5;
        const int LevelNameMax = 12;
        const float RenameMinWidth = 160f, RenameMaxWidth = 320f;

        readonly AppUI _ui;
        public VisualElement Element { get; }

        readonly VisualElement _mark, _nameBtn, _renameWrap, _levelSep, _issues;
        readonly Label _name, _level, _room, _issueCount;
        readonly TextField _rename;
        readonly ChromeMorph _crumbs;
        readonly SurfaceAnchor _menuPop, _issuesPop;

        string _shownName = "", _measuredName, _nameSub, _renameId, _issuesProject;
        float _nameWidth;
        int _issueTotal = -1, _issueErrors = -1, _renameFrame = -1;
        bool _renaming;

        public ProjectPill(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("pp-root");
            Element.pickingMode = PickingMode.Ignore;

            // mark: white House on an accent tile → Home
            var tile = Ui.El("pp-tile", Ui.Icon(IconKind.House, 16));
            tile.pickingMode = PickingMode.Ignore;
            _mark = Ui.El("pp-mark", tile);
            Ui.OnClick(_mark, () => _ui.ShowHome());
            Tooltips.Tip(_mark, "Все проекты", "⌘ O");

            // name + chevron → project menu
            _name = Ui.Text("", "pp-name-label t-headline");
            _nameBtn = Ui.El("pp-name", _name, Ui.Icon(IconKind.ChevronDown, 12, "pp-chev"));
            Ui.OnClick(_nameBtn, ToggleMenu);
            Tooltips.Tip(_nameBtn, "Меню проекта");
            _name.RegisterCallback<GeometryChangedEvent>(_ => UpdateNameTip());

            // inline rename in place of the name: ↩ saves, Esc cancels, clicking away saves
            _rename = new TextField { maxLength = 80 };
            _rename.AddToClassList("pp-rename");
            _rename.RegisterCallback<KeyDownEvent>(OnRenameKey, TrickleDown.TrickleDown);
            _rename.RegisterCallback<FocusOutEvent>(OnRenameFocusOut);
            _rename.RegisterValueChangedCallback(e => FitRename(e.newValue));
            Tooltips.Tip(_rename, "Сохранить название", "↩", "Esc — отменить");
            _renameWrap = Ui.El("pp-rename-wrap", _rename);
            Ui.Show(_renameWrap, false);

            // breadcrumb (walk / fly only): | level › room; its width animates. A 1×20 divider, not a chevron, separates it
            // from the name: «46-96 ⌄ › 1 этаж» read as a doubled chevron and tied the crumbs to the project menu
            _level = Ui.Text("", "pp-crumb pp-crumb-level t-ui sp-fade");
            _levelSep = Ui.Icon(IconKind.ChevronRight, 12, "pp-sep");
            _room = Ui.Text("", "pp-crumb pp-crumb-room t-ui sp-fade");
            var crumbsDiv = Ui.DividerV();
            crumbsDiv.AddToClassList("pp-crumbs-div");
            var crumbsIn = Ui.El("pp-crumbs-in", crumbsDiv, _level, _levelSep, _room);
            crumbsIn.pickingMode = PickingMode.Ignore;
            var crumbs = Ui.El("pp-crumbs", crumbsIn);
            crumbs.pickingMode = PickingMode.Ignore;
            _crumbs = new ChromeMorph(crumbs, crumbsIn, false);

            // issues badge → issues popover
            _issueCount = Ui.Text("", "pp-issues-count t-micro");
            _issues = Ui.El("pp-issues", Ui.Icon(IconKind.Warning, 14), _issueCount);
            Ui.OnClick(_issues, ToggleIssues);
            Tooltips.Tip(_issues, "Замечания — открыть список");
            Ui.Show(_issues, false);

            var pill = Ui.El("pp-pill", _mark, _nameBtn, _renameWrap, crumbs, _issues);
            Element.Add(Elevation.Wrap(pill, 12, 16, 4f, 0.45f));

            // popovers anchor to the surface (Element has exactly the pill's bounds); the items keep the pressed look
            _menuPop = new SurfaceAnchor(_ui, Element, _nameBtn);
            _issuesPop = new SurfaceAnchor(_ui, Element, _issues);

            _ui.LocationChanged += UpdateCrumbs;
            Refresh();
        }

        // ------------------------------------------------------------------ public
        public void Refresh()
        {
            var s = _ui.S?.Session;
            if (s == null) return;
            if (_renaming && (!s.HasProject || s.ProjectId != _renameId)) EndRename(false);

            string name = "";
            if (s.HasProject) name = string.IsNullOrWhiteSpace(s.Doc.Meta?.Name) ? s.ProjectId ?? "" : s.Doc.Meta.Name.Trim();
            if (name != _shownName)
            {
                _shownName = name;
                _name.text = name;
                _name.schedule.Execute(UpdateNameTip).ExecuteLater(30);
            }
            UpdateIssues(s);
            UpdateCrumbs();
        }

        public void Tick()
        {
            _menuPop.Tick();
            _issuesPop.Tick();
            if (_renaming)
            {
                TickRename();
                return;
            }
            // F2 renames the open project (the viewer's key handler has no F2; Home handles its own)
            var kb = Keyboard.current;
            if (kb == null || !kb.f2Key.wasPressedThisFrame) return;
            if (kb.leftMetaKey.isPressed || kb.rightMetaKey.isPressed || kb.leftCtrlKey.isPressed || kb.rightCtrlKey.isPressed
                || kb.leftAltKey.isPressed || kb.rightAltKey.isPressed) return;
            if (_ui.ViewerFocused && !_ui.CleanView && _ui.S.Session.HasProject) BeginRename();
        }

        /// <summary>Polled backups for the inline rename (the device is read directly, no allocations).</summary>
        void TickRename()
        {
            // the field lives in the chrome: Home, the veil, a dialog or clean view over it ends the edit (saving, like a
            // click away) — otherwise keys typed on Home would land in the hidden field
            if (_ui.HomeOpen || _ui.VeilVisible || _ui.ModalOpen || _ui.CleanView)
            {
                EndRename(true);
                return;
            }
            // the ↩ / click that picked «Переименовать» in the menu this frame is not a save
            if (Time.frameCount == _renameFrame) return;
            // ↩ saves even if the text field's own key event does not arrive
            var kb = Keyboard.current;
            if (kb != null && (kb.enterKey.wasPressedThisFrame || kb.numpadEnterKey.wasPressedThisFrame))
            {
                EndRename(true);
                return;
            }
            // a press outside the field saves (the panel may keep the focus when the click lands on the bare 3D view)
            var mouse = Mouse.current;
            if (mouse != null && (mouse.leftButton.wasPressedThisFrame || mouse.rightButton.wasPressedThisFrame || mouse.middleButton.wasPressedThisFrame)
                && !_renameWrap.worldBound.Contains(_ui.PointerPanelPosition()))
                EndRename(true);
        }

        /// <summary>Inline rename of the open project (F2 / project menu).</summary>
        public void BeginRename()
        {
            var s = _ui.S?.Session;
            if (s == null || !s.HasProject || _renaming || _ui.HomeOpen || _ui.VeilVisible) return;
            if (_ui.CleanView) _ui.SetCleanView(false);
            _ui.ClosePopover();
            Tooltips.HideNow();
            _renaming = true;
            _renameId = s.ProjectId;
            _renameFrame = Time.frameCount;
            _rename.SetValueWithoutNotify(_shownName);
            FitRename(_shownName);
            Ui.Show(_nameBtn, false);
            Ui.Show(_renameWrap, true);
            _rename.schedule.Execute(() =>
            {
                if (!_renaming) return;
                _rename.Focus();
                _rename.SelectAll();
            }).ExecuteLater(30);
        }

        /// <summary>True while the name is being edited in place.</summary>
        public bool Renaming => _renaming;

        // ------------------------------------------------------------------ name & menu
        void UpdateNameTip()
        {
            // a truncated name shows in full as the tooltip's second line; the text is measured once per name (the label's
            // geometry changes on every frame of a breadcrumb width animation)
            if (_name.panel == null) return;
            float w = _name.layout.width;
            if (_measuredName != _shownName)
            {
                _measuredName = _shownName;
                _nameWidth = string.IsNullOrEmpty(_shownName) ? 0f : Ui.Measure(_name, _shownName);
            }
            string sub = null;
            if (!float.IsNaN(w) && w > 1f && _nameWidth > w + 1f) sub = _shownName;
            if (sub == _nameSub) return;
            _nameSub = sub;
            Tooltips.Tip(_nameBtn, "Меню проекта", null, sub);
        }

        void ToggleMenu()
        {
            var s = _ui.S.Session;
            if (!s.HasProject || _renaming) return;
            if (_menuPop.IsOpen) { _menuPop.Close(); return; }

            string id = s.ProjectId;
            var items = new List<MenuItem>();
            var recent = Recent(id);
            if (recent.Count > 0)
            {
                items.Add(MenuItem.Title("Недавние"));
                foreach (var p in recent)
                {
                    string pid = p.Id;
                    items.Add(new MenuItem { Custom = RecentRow(p), Action = () => _ui.OpenProject(pid) });
                }
                items.Add(MenuItem.Sep());
            }
            items.Add(new MenuItem { Label = "Все проекты", Icon = IconKind.Grid, Shortcut = "⌘O", Action = _ui.ShowHome });
            items.Add(new MenuItem { Label = "Новый проект…", Icon = IconKind.Plus, Shortcut = "⌘N", Action = _ui.ShowNewProject });
            items.Add(MenuItem.Sep());
            items.Add(new MenuItem { Label = "Переименовать", Icon = IconKind.Pencil, Shortcut = "F2", Action = BeginRename });
            items.Add(new MenuItem { Label = "Показать в Finder", Icon = IconKind.Folder, Action = () => Reveal(id) });
            items.Add(MenuItem.Sep());
            items.Add(new MenuItem { Label = "Удалить проект…", Icon = IconKind.Trash, Danger = true, Action = () => _ui.ConfirmDelete(id) });
            _menuPop.Menu(items, PopPlacement.BelowLeft, 280f);
        }

        void Reveal(string id)
        {
            var store = _ui.S?.Session?.Store;
            if (store == null || !store.Exists(id)) return;
            _ui.RevealInFinder(store.FolderOf(id));
        }

        /// <summary>Up to five other projects, most recently changed first.</summary>
        List<ProjectInfo> Recent(string currentId)
        {
            var result = new List<ProjectInfo>(RecentCount);
            List<ProjectInfo> all;
            try { all = _ui.S.Session.Store.List(); }
            catch (Exception e)
            {
                Debug.LogWarning("[ProjectPill] recent projects: " + e.Message);
                return result;
            }
            foreach (var p in all)
            {
                if (p.Id == currentId) continue;
                result.Add(p);
                if (result.Count == RecentCount) break;
            }
            return result;
        }

        /// <summary>Recent-project row: 48×30 preview, name, «9 ч назад» (the menu row itself becomes h 44).</summary>
        VisualElement RecentRow(ProjectInfo p)
        {
            var thumb = Ui.El("pp-recent-thumb");
            thumb.pickingMode = PickingMode.Ignore;
            Texture2D tex = null;
            try { tex = _ui.S.Thumbs?.Get(p.Id); }
            catch (Exception) { /* no preview: the placeholder stays */ }
            if (tex != null) thumb.style.backgroundImage = new StyleBackground(tex);
            else thumb.Add(Ui.Icon(IconKind.House, 14, "pp-recent-ph"));

            var text = Ui.El("pp-recent-text", Ui.Text(string.IsNullOrWhiteSpace(p.Name) ? p.Id : p.Name, "pp-recent-name"));
            text.pickingMode = PickingMode.Ignore;
            string ago = Ui.Ago(p.Modified);
            if (!string.IsNullOrEmpty(ago)) text.Add(Ui.Text(ago, "pp-recent-ago"));

            var row = Ui.El("pp-recent", thumb, text);
            row.pickingMode = PickingMode.Ignore;
            row.RegisterCallback<AttachToPanelEvent>(_ => row.parent?.AddToClassList("pp-recent-item"));
            return row;
        }

        // ------------------------------------------------------------------ inline rename
        void OnRenameKey(KeyDownEvent e)
        {
            if (!_renaming) return;
            if (e.keyCode == KeyCode.Return || e.keyCode == KeyCode.KeypadEnter)
            {
                e.StopPropagation();
                EndRename(true);
            }
            else if (e.keyCode == KeyCode.Escape)
            {
                e.StopPropagation();
                EndRename(false);
            }
        }

        void OnRenameFocusOut(FocusOutEvent e)
        {
            if (!_renaming) return;
            // focus moving inside the field (to its text input) is not leaving it
            if (e.relatedTarget is VisualElement next && (next == _rename || _rename.Contains(next))) return;
            // AppUI's Esc chain blurs the field: that is a cancel; any other blur (click away) saves
            var kb = Keyboard.current;
            bool esc = kb != null && (kb.escapeKey.isPressed || kb.escapeKey.wasPressedThisFrame);
            EndRename(!esc);
        }

        void EndRename(bool commit)
        {
            if (!_renaming) return;
            _renaming = false;
            string id = _renameId;
            string text = (_rename.value ?? "").Trim();
            _renameId = null;
            var focused = _rename.focusController?.focusedElement as VisualElement;
            if (focused != null && (focused == _rename || _rename.Contains(focused))) focused.Blur();
            Ui.Show(_renameWrap, false);
            Ui.Show(_nameBtn, true);
            var s = _ui.S?.Session;
            if (commit && text.Length > 0 && text != _shownName && s != null && s.HasProject && id == s.ProjectId)
                _ui.RenameProject(id, text);
        }

        /// <summary>The field grows with the text (Headline metrics), 160…320.</summary>
        void FitRename(string text)
        {
            float w = Ui.Measure(_name, string.IsNullOrEmpty(text) ? "Название" : text);
            _rename.style.width = Mathf.Clamp(w + 24f, RenameMinWidth, RenameMaxWidth);
        }

        // ------------------------------------------------------------------ breadcrumb
        void UpdateCrumbs()
        {
            var s = _ui.S;
            if (s == null) return;
            var loc = _ui.Location;
            bool walkOrFly = s.Viewer != null && s.Session.HasProject && s.Viewer.CurrentMode != HouseViewer.Mode.Orbit;
            if (!walkOrFly || loc.Plan == null)
            {
                _crumbs.Set(false);
                return;
            }
            int index = IndexOfPlan(loc.Plan);
            if (index < 0) return;          // stale location right after a rebuild: a fresh one follows within 0.25 s

            var plans = _ui.Plans;
            bool outside = loc.Room == null;
            // one-storey houses need no level; on the plot around the house the level says nothing either
            bool showLevel = plans.Count > 1 && !(outside && index == 0);
            bool visible = _crumbs.IsOpen;
            if (showLevel) ChromeMorph.SwapText(_level, LevelLabel(loc, index), visible && Ui.IsShown(_level));
            Ui.Show(_level, showLevel);
            Ui.Show(_levelSep, showLevel);
            ChromeMorph.SwapText(_room, outside ? "Участок" : RoomLabel(loc.Room), visible);
            _crumbs.Set(true);
        }

        int IndexOfPlan(PlanGeometry plan)
        {
            var plans = _ui.Plans;
            for (int i = 0; i < plans.Count; i++)
                if (plans[i] == plan) return i;
            return -1;
        }

        /// <summary>The level's own name, or «N этаж» when it has none or it is longer than 12 characters.</summary>
        string LevelLabel(ViewerLocation loc, int index)
        {
            // same names as the plan's level tabs («Цоколь» below the ground floor)
            string title = _ui.Plan?.LevelTitle(loc.Plan.LevelId);
            if (!string.IsNullOrEmpty(title)) return title;
            string name = loc.Level?.Name;
            return string.IsNullOrWhiteSpace(name) || name.Trim().Length > LevelNameMax ? (index + 1) + " этаж" : name.Trim();
        }

        /// <summary>The room's name, or its type («Гостиная») when it has none (the plan falls back to the id).</summary>
        static string RoomLabel(PlanGeometry.Room room) =>
            string.IsNullOrWhiteSpace(room.Name) || room.Name == room.Id ? PlanGeometry.TypeName(room.Type) : room.Name;

        // ------------------------------------------------------------------ issues
        void UpdateIssues(HouseSession s)
        {
            int errors = 0, warnings = 0;
            if (s.HasProject)
            {
                foreach (var issue in s.Issues)
                {
                    if (issue.Level == IssueLevel.Error) errors++;
                    else warnings++;
                }
                var built = s.Result?.Warnings;
                if (built != null) warnings += built.Count;
            }
            int total = errors + warnings;
            bool sameProject = _issuesProject == s.ProjectId;
            if (total == _issueTotal && errors == _issueErrors && sameProject) return;
            bool grew = sameProject && _issueTotal >= 0 && total > _issueTotal;
            _issueTotal = total;
            _issueErrors = errors;
            _issuesProject = s.ProjectId;

            if (total == 0)
            {
                _issuesPop.Close();
                Ui.Show(_issues, false);
                return;
            }
            _issueCount.text = total.ToString();
            _issues.EnableInClassList("pp-err", errors > 0);
            string tip = Ui.Plural(total, "замечание", "замечания", "замечаний") + " — открыть список";
            string sub = errors > 0 && warnings > 0
                ? Ui.Plural(errors, "ошибка", "ошибки", "ошибок") + " · " + Ui.Plural(warnings, "предупреждение", "предупреждения", "предупреждений")
                : null;
            Tooltips.Tip(_issues, tip, null, sub);
            Ui.Show(_issues, true);
            if (grew) Bump();
        }

        void ToggleIssues() => _issuesPop.Toggle(() => IssuesPopover.Build(_ui), 400f, PopPlacement.BelowLeft);

        /// <summary>Badge bump when the count grows: scale 1 → 1.15 → 1 (120 + 120 ms).</summary>
        void Bump()
        {
            _issues.AddToClassList("pp-bump");
            _issues.schedule.Execute(() => _issues.RemoveFromClassList("pp-bump")).ExecuteLater(130);
        }
    }

    /// <summary>
    /// Animated auto width for chrome segments (USS cannot animate to or from <c>auto</c>): the outer element clips and
    /// carries the width transition, the inner one is absolutely positioned so it keeps its natural width. The outer
    /// width follows the inner one (240 ms, ease-in-out-cubic, set in USS), collapses to 0 and then leaves the layout
    /// (display:none, so it takes no clicks). The class <c>sp-instant</c> (0 s transition) is used for jumps.
    /// </summary>
    internal sealed class ChromeMorph
    {
        const string Instant = "sp-instant";
        const long CollapseMs = 260;

        readonly VisualElement _outer, _inner;
        IVisualElementScheduledItem _pending;
        bool _open, _jump;

        public ChromeMorph(VisualElement outer, VisualElement inner, bool open)
        {
            _outer = outer;
            _inner = inner;
            _open = open;
            _jump = open;                    // a segment that starts visible takes its width without animating
            _outer.style.width = 0f;
            Ui.Show(_outer, open);
            _inner.RegisterCallback<GeometryChangedEvent>(_ => Fit());
        }

        public bool IsOpen => _open;

        public void Set(bool open, bool animate = true)
        {
            if (open)
            {
                _pending?.Pause();
                _pending = null;
                _open = true;
                if (!animate) _jump = true;
                if (!Ui.IsShown(_outer))
                {
                    _outer.style.width = 0f;
                    Ui.Show(_outer, true);
                    // the inner row is measured on the next layout; this is a fallback if no geometry event comes
                    _outer.schedule.Execute(Fit).ExecuteLater(20);
                }
                Fit();
                return;
            }

            if (!_open) return;
            _open = false;
            _pending?.Pause();
            _pending = null;
            if (!animate || !Ui.IsShown(_outer))
            {
                _outer.AddToClassList(Instant);
                _outer.style.width = 0f;
                Ui.Show(_outer, false);
                return;
            }
            _outer.RemoveFromClassList(Instant);
            _outer.style.width = 0f;
            _pending = _outer.schedule.Execute(() =>
            {
                if (!_open) Ui.Show(_outer, false);
            });
            _pending.ExecuteLater(CollapseMs);
        }

        void Fit()
        {
            if (!_open || !Ui.IsShown(_outer)) return;
            float w = _inner.layout.width;
            if (float.IsNaN(w) || w < 1f) return;
            _outer.EnableInClassList(Instant, _jump);
            _jump = false;
            _outer.style.width = w;
        }

        /// <summary>Replaces a label's text; with <paramref name="fade"/> the new text fades in (160 ms).</summary>
        public static void SwapText(Label label, string text, bool fade)
        {
            if (label.text == text) return;
            label.text = text;
            if (!fade) return;
            label.AddToClassList("sp-fresh");
            label.schedule.Execute(() => label.RemoveFromClassList("sp-fresh")).ExecuteLater(30);
        }
    }

    /// <summary>
    /// Hangs a pill item's popover from the pill's floating surface instead of from the item, so every popover of one
    /// pill shares the pill's edge and keeps an 8 px gap below it (spec §6: separate shadows). AppUI places a popover
    /// 8 px from its anchor's worldBound, so the anchor is an invisible proxy covering the surface; the item mirrors the
    /// proxy's <c>popover-open</c> class (pressed look, tooltip suppression), and a press elsewhere on the surface closes
    /// the popover, as a press outside an item anchor does.
    /// </summary>
    internal sealed class SurfaceAnchor
    {
        const string OpenClass = "popover-open";

        readonly AppUI _ui;
        readonly VisualElement _item;
        bool _open;

        /// <param name="surface">An element with exactly the surface's bounds; the proxy is added to it (absolute, 0/0/0/0).</param>
        /// <param name="item">The control that opens the popover (gets <c>popover-open</c> while it is open).</param>
        public SurfaceAnchor(AppUI ui, VisualElement surface, VisualElement item)
        {
            _ui = ui;
            _item = item;
            Proxy = Ui.El("sp-anchor");
            Proxy.pickingMode = PickingMode.Ignore;
            surface.Add(Proxy);
        }

        /// <summary>The popover anchor (also usable for scheduling: it lives as long as the pill).</summary>
        public VisualElement Proxy { get; }

        public bool IsOpen => _ui.IsPopoverAnchor(Proxy);

        /// <summary>Opens the popover (closing any other); closes it if it is this one's.</summary>
        public void Toggle(Func<VisualElement> build, float width, PopPlacement placement)
        {
            _ui.TogglePopover(Proxy, build, width, placement);
            Sync();
        }

        /// <summary>Opens a menu (closing any other popover); closes it if it is this one's.</summary>
        public void Menu(IList<MenuItem> items, PopPlacement placement, float minWidth)
        {
            _ui.ShowMenu(Proxy, items, placement, minWidth);
            Sync();
        }

        public void Close()
        {
            if (IsOpen) _ui.ClosePopover();
            Sync();
        }

        /// <summary>Per frame; no allocations.</summary>
        public void Tick()
        {
            if (IsOpen)
            {
                var mouse = Mouse.current;
                if (mouse != null && (mouse.leftButton.wasPressedThisFrame || mouse.rightButton.wasPressedThisFrame || mouse.middleButton.wasPressedThisFrame))
                {
                    // AppUI keeps a popover open while the press is over its anchor, which is now the whole surface
                    var p = _ui.PointerPanelPosition();
                    if (Proxy.worldBound.Contains(p) && !_item.worldBound.Contains(p)) _ui.ClosePopover();
                }
            }
            Sync();
        }

        void Sync()
        {
            bool open = IsOpen;
            if (open == _open) return;
            _open = open;
            _item.EnableInClassList(OpenClass, open);
        }
    }
}
