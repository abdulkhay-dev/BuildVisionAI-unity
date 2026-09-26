using System.Collections.Generic;
using House4696.Generation;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// What the furniture mode draws over the 3D view: the box of the item under the pointer (thin, neutral), of the selected
    /// one (accent) and of the model being placed or dragged (accent, or red where it cannot stand); a bar of actions above
    /// the selected item (name and size, turn ↺ ↻, duplicate, delete, a warning from the checks); and a hint next to the
    /// pointer while a spot is wrong («Мешает стена», «Наведите на стену»).
    /// </summary>
    public sealed class FurnitureOverlay
    {
        const float BarGap = 14f, Edge = 8f;

        static readonly Color HoverColor = new Color32(0xA3, 0xA8, 0xB1, 0xFF);
        static readonly Color SelectColor = new Color32(0x5A, 0x6A, 0xF7, 0xFF);
        static readonly Color GhostColor = new Color32(0x93, 0xA2, 0xFF, 0xFF);
        static readonly Color BadColor = new Color32(0xF8, 0x71, 0x71, 0xFF);

        readonly AppUI _ui;
        readonly FurnitureEditor _editor;
        readonly Boxes _boxes;
        readonly VisualElement _barWrap, _warn;
        readonly Label _name, _size, _hintText;
        readonly VisualElement _hint, _rotateL, _rotateR;
        readonly Icon _hintIcon;
        ItemBox _barFor;
        bool _barShown, _hintShown;
        string _warnText;

        public VisualElement Element { get; }

        public FurnitureOverlay(AppUI ui, FurnitureEditor editor)
        {
            _ui = ui;
            _editor = editor;
            Element = Ui.El("layer fo-layer");
            Element.pickingMode = PickingMode.Ignore;
            _boxes = new Boxes();
            Element.Add(_boxes);

            // ---- action bar
            _name = Ui.Text("", "fo-name");
            _size = Ui.Text("", "fo-size");
            var titles = Ui.El("fo-titles", _name, _size);
            _warn = Ui.El("fo-warn", Ui.Icon(IconKind.Warning, 16));
            _rotateL = Ui.IconButton(IconKind.RotateCcw, () => _editor.Rotate(-90f), "Повернуть против часовой", "⇧ R", ButtonKind.Ghost, "btn-sm fo-btn", 18);
            _rotateR = Ui.IconButton(IconKind.RotateCw, () => _editor.Rotate(90f), "Повернуть по часовой", "R", ButtonKind.Ghost, "btn-sm fo-btn", 18);
            var dup = Ui.IconButton(IconKind.Duplicate, _editor.DuplicateSelected, "Дублировать", "⌘ D", ButtonKind.Ghost, "btn-sm fo-btn", 18);
            var del = Ui.IconButton(IconKind.Trash, _editor.DeleteSelected, "Удалить", "⌫", ButtonKind.Ghost, "btn-sm fo-btn fo-danger", 18);
            var bar = Ui.El("fo-bar", titles, _warn, Ui.DividerV(), _rotateL, _rotateR, Ui.DividerV(), dup, del);
            _barWrap = Elevation.Wrap(bar, 12, 16, 4f, 0.45f, "fo-bar-wrap");
            _barWrap.style.position = Position.Absolute;
            Ui.Show(_barWrap, false);
            Element.Add(_barWrap);

            // ---- hint at the pointer
            _hintText = Ui.Text("", "fo-hint-text");
            _hintIcon = Ui.Icon(IconKind.Warning, 14, "fo-hint-icon");
            _hint = Ui.El("fo-hint", _hintIcon, _hintText);
            _hint.pickingMode = PickingMode.Ignore;
            _hint.style.position = Position.Absolute;
            Ui.Show(_hint, false);
            Element.Add(_hint);
        }

        public void Tick()
        {
            var cam = Camera.main;
            bool on = _editor.Active && cam != null && Element.panel != null && _ui.S.Session.HasProject && !_ui.CleanView
                      && !_ui.HomeOpen && !_ui.VeilVisible && (_ui.Plan == null || !_ui.Plan.LargeOpen);
            if (!on)
            {
                ShowBar(false);
                ShowHint(null, false);
                if (_boxes.LineCount > 0) { _boxes.ClearLines(); _boxes.MarkDirtyRepaint(); }
                return;
            }
            _boxes.ClearLines();
            var st = _editor.Current;
            var sel = _editor.Selected;
            Rect selRect = default;
            bool selVisible = false;

            if (st == FurnitureEditor.State.Placing)
            {
                var g = _editor.Ghost;
                if (g != null) AddBox(cam, g.transform.localToWorldMatrix, _editor.GhostShape.Local, _editor.Target.Valid ? GhostColor : BadColor, 2f, out _);
            }
            else
            {
                var hover = _editor.Hover;
                if (hover != null && hover != sel && hover.Object != null)
                    AddBox(cam, hover.Object.transform.localToWorldMatrix, hover.Local, HoverColor, 1.25f, out _);
                if (sel?.Object != null)
                {
                    bool bad = st == FurnitureEditor.State.Dragging && !_editor.Target.Valid;
                    selVisible = AddBox(cam, sel.Object.transform.localToWorldMatrix, sel.Local, bad ? BadColor : SelectColor, 2f, out selRect);
                }
            }
            _boxes.MarkDirtyRepaint();

            // the bar: above the selected item while nothing is being moved or placed
            bool bar = selVisible && st == FurnitureEditor.State.Idle && !_ui.CleanView;
            if (bar) PlaceBar(sel, selRect);
            ShowBar(bar);

            // the hint follows the pointer while the spot is wrong (red) or the pointer is not over a place for the model (neutral)
            string hint = st == FurnitureEditor.State.Idle ? null : _editor.Hint;
            ShowHint(hint, _editor.Target.Found);
        }

        // ------------------------------------------------------------------ boxes
        /// <summary>Adds the 12 edges of a box (clipped at the near plane); returns false when it is all behind the camera.</summary>
        bool AddBox(Camera cam, Matrix4x4 toWorld, Bounds b, Color color, float width, out Rect screenRect)
        {
            screenRect = default;
            var corners = new Vector3[8];
            for (int i = 0; i < 8; i++)
            {
                var c = new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y, (i & 4) == 0 ? b.min.z : b.max.z);
                corners[i] = toWorld.MultiplyPoint3x4(c);
            }
            var camPos = cam.transform.position;
            var fwd = cam.transform.forward;
            float near = cam.nearClipPlane + 0.02f;
            float Depth(Vector3 p) => Vector3.Dot(p - camPos, fwd) - near;
            bool any = false;
            float x0 = float.MaxValue, y0 = float.MaxValue, x1 = float.MinValue, y1 = float.MinValue;
            for (int i = 0; i < 8; i++)
            for (int bit = 1; bit < 8; bit <<= 1)
            {
                int j = i | bit;
                if (j == i) continue;
                Vector3 a = corners[i], c = corners[j];
                float da = Depth(a), dc = Depth(c);
                if (da < 0f && dc < 0f) continue;
                if (da < 0f) a = Vector3.Lerp(a, c, da / (da - dc));
                else if (dc < 0f) c = Vector3.Lerp(c, a, dc / (dc - da));
                var pa = ToPanel(cam, a);
                var pc = ToPanel(cam, c);
                _boxes.Add(pa, pc, color, width);
                x0 = Mathf.Min(x0, Mathf.Min(pa.x, pc.x)); x1 = Mathf.Max(x1, Mathf.Max(pa.x, pc.x));
                y0 = Mathf.Min(y0, Mathf.Min(pa.y, pc.y)); y1 = Mathf.Max(y1, Mathf.Max(pa.y, pc.y));
                any = true;
            }
            if (any) screenRect = Rect.MinMaxRect(x0, y0, x1, y1);
            return any;
        }

        Vector2 ToPanel(Camera cam, Vector3 world)
        {
            var s = cam.WorldToScreenPoint(world);
            var p = RuntimePanelUtils.ScreenToPanel(Element.panel, new Vector2(s.x, Screen.height - s.y));
            var origin = Element.worldBound.position;
            return p - origin;
        }

        // ------------------------------------------------------------------ action bar
        void PlaceBar(ItemBox sel, Rect r)
        {
            if (_barFor != sel)
            {
                _barFor = sel;
                _name.text = _editor.NameOf(sel);
                var shape = _editor.ShapeOf(sel);
                _size.text = FurnitureCatalog.SizeText(sel.Local, shape.Mount);
                bool wall = shape.Mount == ItemMount.Wall;
                _rotateL.SetEnabled(!wall);
                _rotateR.SetEnabled(!wall);
            }
            var issues = _editor.SelectedIssues();
            string warn = issues.Count > 0 ? string.Join("\n", issues) : null;
            if (warn != _warnText)
            {
                _warnText = warn;
                Ui.Show(_warn, warn != null);
                if (warn != null) Tooltips.Tip(_warn, issues.Count == 1 ? "Проверка расстановки" : "Проверка расстановки: " + issues.Count, null, warn);
            }
            var area = Element.layout;
            float w = _barWrap.resolvedStyle.width, h = _barWrap.resolvedStyle.height;
            if (float.IsNaN(w) || float.IsNaN(h) || w <= 0f) { w = 360f; h = 44f; }
            float x = Mathf.Clamp(r.center.x - w * 0.5f, Edge, Mathf.Max(Edge, area.width - w - Edge));
            float y = r.yMin - BarGap - h;
            if (y < Edge + 60f) y = Mathf.Min(r.yMax + BarGap, area.height - h - 80f);   // no room above: below the item
            y = Mathf.Clamp(y, Edge, Mathf.Max(Edge, area.height - h - Edge));
            _barWrap.style.left = Mathf.Round(x);
            _barWrap.style.top = Mathf.Round(y);
        }

        void ShowBar(bool on)
        {
            if (on == _barShown) return;
            _barShown = on;
            if (!on) _barFor = null;
            Motion.Fade(_barWrap, on, 120, 100);
        }

        // ------------------------------------------------------------------ hint
        void ShowHint(string text, bool error)
        {
            var pointer = _editor.PointerScreen;
            bool on = !string.IsNullOrEmpty(text) && !_ui.PointerOverUI(pointer);
            if (on)
            {
                if (_hintText.text != text) _hintText.text = text;
                _hint.EnableInClassList("fo-hint-info", !error);
                _hintIcon.Kind = error ? IconKind.Warning : IconKind.Info;
                var p = RuntimePanelUtils.ScreenToPanel(Element.panel, new Vector2(pointer.x, Screen.height - pointer.y)) - Element.worldBound.position;
                _hint.style.left = Mathf.Round(p.x + 18f);
                _hint.style.top = Mathf.Round(p.y + 20f);
            }
            if (on == _hintShown) return;
            _hintShown = on;
            Ui.Show(_hint, on);
        }

        // ================================================================== boxes element
        /// <summary>Line segments in the layer's coordinates, redrawn every frame (Painter2D, one stroke per segment).</summary>
        sealed class Boxes : VisualElement
        {
            readonly List<(Vector2 a, Vector2 b, Color c, float w)> _lines = new List<(Vector2, Vector2, Color, float)>();

            public Boxes()
            {
                pickingMode = PickingMode.Ignore;
                style.position = Position.Absolute;
                style.left = 0; style.top = 0; style.right = 0; style.bottom = 0;
                generateVisualContent += Draw;
            }

            public int LineCount => _lines.Count;
            public void ClearLines() => _lines.Clear();
            public void Add(Vector2 a, Vector2 b, Color c, float w) => _lines.Add((a, b, c, w));

            void Draw(MeshGenerationContext ctx)
            {
                if (_lines.Count == 0) return;
                var p = ctx.painter2D;
                p.lineCap = LineCap.Round;
                p.lineJoin = LineJoin.Round;
                foreach (var (a, b, c, w) in _lines)
                {
                    p.strokeColor = c;
                    p.lineWidth = w;
                    p.BeginPath();
                    p.MoveTo(a);
                    p.LineTo(b);
                    p.Stroke();
                }
            }
        }
    }
}
