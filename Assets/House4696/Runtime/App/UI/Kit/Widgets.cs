using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Segmented control with one sliding thumb under the selected item (toolbar modes, graphics quality, level tabs).
    /// The selected item is neutral (selected surface + text-1), never accent.
    /// </summary>
    public sealed class Segmented
    {
        public readonly VisualElement Element;
        readonly VisualElement _thumb;
        readonly List<VisualElement> _items = new List<VisualElement>();
        readonly Action<int> _onSelect;
        int _selected = -1;
        bool _placed;

        /// <param name="classes">extra classes: "sm" (h 28), "boxed" (field background).</param>
        public Segmented(IList<(string label, IconKind? icon, string tooltip, string keys)> items, Action<int> onSelect, string classes = null)
        {
            _onSelect = onSelect;
            Element = Ui.El("segmented " + (classes ?? ""));
            _thumb = Ui.El("seg-thumb");
            _thumb.pickingMode = PickingMode.Ignore;
            Element.Add(_thumb);
            for (int i = 0; i < items.Count; i++)
            {
                int index = i;
                var it = items[i];
                var seg = Ui.El("seg");
                if (it.icon.HasValue) seg.Add(Ui.Icon(it.icon.Value, 18));
                else seg.AddToClassList("no-icon");
                if (!string.IsNullOrEmpty(it.label)) seg.Add(Ui.Text(it.label, "seg-label"));
                Ui.OnClick(seg, () => { Select(index, true); });
                if (it.tooltip != null) Tooltips.Tip(seg, it.tooltip, it.keys);
                seg.RegisterCallback<GeometryChangedEvent>(_ => { if (index == _selected) PlaceThumb(); });
                _items.Add(seg);
                Element.Add(seg);
            }
            Ui.Show(_thumb, false);
        }

        public int Selected => _selected;
        public IReadOnlyList<VisualElement> Items => _items;

        /// <summary>Selects an item (the thumb slides); <paramref name="notify"/> raises the callback.</summary>
        public void Select(int index, bool notify = false)
        {
            if (index < -1 || index >= _items.Count) return;
            bool changed = index != _selected;
            _selected = index;
            for (int i = 0; i < _items.Count; i++) _items[i].EnableInClassList("selected", i == index);
            Ui.Show(_thumb, index >= 0);
            PlaceThumb();
            if (notify && changed) _onSelect?.Invoke(index);
            else if (notify) _onSelect?.Invoke(index);
        }

        public void SetLabel(int index, string text)
        {
            var l = _items[index].Q<Label>(className: "seg-label");
            if (l != null) l.text = text;
        }

        void PlaceThumb()
        {
            if (_selected < 0) return;
            var r = _items[_selected].layout;
            if (float.IsNaN(r.width) || r.width <= 0f) return;
            // first placement jumps, later ones slide
            _thumb.EnableInClassList("instant", !_placed);
            _thumb.style.width = r.width;
            _thumb.style.translate = new Translate(r.x, 0);
            _thumb.style.left = 0;
            if (!_placed) _thumb.schedule.Execute(() => _thumb.RemoveFromClassList("instant")).ExecuteLater(30);
            _placed = true;
        }
    }

    /// <summary>
    /// 16 px progress ring (Painter2D): track + arc. <see cref="Value"/> 0–1 is eased at 8/s; <see cref="Spinning"/>
    /// shows an indeterminate rotating arc. Colours: USS --ring-track / --ring-fill.
    /// </summary>
    public sealed class ProgressRing : VisualElement
    {
        static readonly CustomStyleProperty<Color> Track = new CustomStyleProperty<Color>("--ring-track");
        static readonly CustomStyleProperty<Color> Fill = new CustomStyleProperty<Color>("--ring-fill");
        Color _track = new Color(0.18f, 0.19f, 0.22f), _fill = new Color(0.29f, 0.36f, 0.94f);
        float _shown, _target, _spin;
        bool _spinning;
        IVisualElementScheduledItem _loop;

        public ProgressRing()
        {
            AddToClassList("ring");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(e =>
            {
                if (e.customStyle.TryGetValue(Track, out var t)) _track = t;
                if (e.customStyle.TryGetValue(Fill, out var f)) _fill = f;
                MarkDirtyRepaint();
            });
            RegisterCallback<AttachToPanelEvent>(_ => _loop = schedule.Execute(Step).Every(16));
            RegisterCallback<DetachFromPanelEvent>(_ => _loop?.Pause());
        }

        public float Value { get => _target; set => _target = Mathf.Clamp01(value); }

        /// <summary>Neither the element nor an ancestor is display:none.</summary>
        public static bool VisibleInHierarchy(VisualElement e)
        {
            if (e.panel == null) return false;
            for (var p = e; p != null; p = p.parent)
                if (p.resolvedStyle.display == DisplayStyle.None) return false;
            return true;
        }
        public bool Spinning { get => _spinning; set { _spinning = value; MarkDirtyRepaint(); } }
        /// <summary>Jumps to the value without easing.</summary>
        public void Snap(float v) { _target = _shown = Mathf.Clamp01(v); MarkDirtyRepaint(); }

        void Step()
        {
            if (!VisibleInHierarchy(this)) return;
            float dt = Mathf.Min(Time.unscaledDeltaTime, 0.1f);
            if (_spinning) { _spin = (_spin + dt * 450f) % 360f; MarkDirtyRepaint(); return; }
            if (Mathf.Abs(_shown - _target) > 0.001f)
            {
                _shown = Mathf.MoveTowards(_shown, _target, Mathf.Max(0.02f, Mathf.Abs(_target - _shown) * 8f * dt));
                MarkDirtyRepaint();
            }
        }

        void Draw(MeshGenerationContext ctx)
        {
            var r = contentRect;
            float rad = Mathf.Min(r.width, r.height) * 0.5f - 1.5f;
            if (rad <= 0f) return;
            var c = r.center;
            var p = ctx.painter2D;
            p.lineWidth = 2f;
            p.lineCap = LineCap.Round;
            p.strokeColor = _track;
            p.BeginPath();
            p.Arc(c, rad, Angle.Degrees(0f), Angle.Degrees(360f));
            p.Stroke();
            p.strokeColor = _fill;
            float start = _spinning ? _spin - 90f : -90f;
            float sweep = _spinning ? 100f : _shown * 360f;
            if (sweep < 1f) return;
            p.BeginPath();
            p.Arc(c, rad, Angle.Degrees(start), Angle.Degrees(start + sweep));
            p.Stroke();
        }
    }

    /// <summary>8 px status dot; with <see cref="Pulsing"/> an expanding ring breathes around it (the AI is working).</summary>
    public sealed class PulseDot : VisualElement
    {
        readonly VisualElement _ring, _dot;
        IVisualElementScheduledItem _loop;
        float _t;
        bool _pulsing;

        public PulseDot()
        {
            AddToClassList("pulse");
            pickingMode = PickingMode.Ignore;
            _ring = Ui.El("pulse-ring");
            _dot = Ui.El("dot");
            Add(_ring);
            Add(_dot);
            _ring.style.opacity = 0f;
            RegisterCallback<AttachToPanelEvent>(_ => _loop = schedule.Execute(Step).Every(16));
            RegisterCallback<DetachFromPanelEvent>(_ => _loop?.Pause());
        }

        /// <summary>Dot style: "dot-success", "dot-ai", "dot-warning", "dot-ring" (hollow) or null (grey).</summary>
        public void SetStyle(string dotClass, bool pulsing)
        {
            _dot.RemoveFromClassList("dot-success");
            _dot.RemoveFromClassList("dot-ai");
            _dot.RemoveFromClassList("dot-warning");
            _dot.RemoveFromClassList("dot-ring");
            if (!string.IsNullOrEmpty(dotClass)) _dot.AddToClassList(dotClass);
            _pulsing = pulsing;
            if (!pulsing) _ring.style.opacity = 0f;
        }

        void Step()
        {
            if (!_pulsing || !ProgressRing.VisibleInHierarchy(this)) return;
            _t = (_t + Mathf.Min(Time.unscaledDeltaTime, 0.1f) / 1.2f) % 1f;
            float e = Mathf.Sin(_t * Mathf.PI * 0.5f);          // ease-out sine
            _ring.style.scale = new Scale(Vector3.one * Mathf.Lerp(1f, 1.8f, e));
            _ring.style.opacity = Mathf.Lerp(0.6f, 0f, e);
        }
    }

    /// <summary>Show/hide with a fade: display comes first when showing, last when hiding (hidden elements take no clicks).</summary>
    public static class Motion
    {
        static readonly Dictionary<VisualElement, IVisualElementScheduledItem> Pending = new Dictionary<VisualElement, IVisualElementScheduledItem>();

        public static void Fade(VisualElement e, bool show, int inMs = 160, int outMs = 240, float yOffset = 0f)
        {
            if (Pending.TryGetValue(e, out var p)) { p.Pause(); Pending.Remove(e); }
            e.style.transitionProperty = new List<StylePropertyName> { new StylePropertyName("opacity"), new StylePropertyName("translate") };
            e.style.transitionTimingFunction = new List<EasingFunction> { new EasingFunction(EasingMode.EaseOutCubic), new EasingFunction(EasingMode.EaseOutCubic) };
            if (show)
            {
                bool wasHidden = !Ui.IsShown(e) || e.resolvedStyle.opacity < 0.01f;
                Ui.Show(e, true);
                if (wasHidden)
                {
                    e.style.transitionDuration = new List<TimeValue> { new TimeValue(0), new TimeValue(0) };
                    e.style.opacity = 0f;
                    e.style.translate = new Translate(0, yOffset);
                }
                var item = e.schedule.Execute(() =>
                {
                    e.style.transitionDuration = new List<TimeValue> { new TimeValue(inMs, TimeUnit.Millisecond), new TimeValue(inMs, TimeUnit.Millisecond) };
                    e.style.opacity = 1f;
                    e.style.translate = new Translate(0, 0);
                    Pending.Remove(e);
                });
                item.ExecuteLater(16);
                Pending[e] = item;
            }
            else
            {
                if (!Ui.IsShown(e)) return;
                e.style.transitionDuration = new List<TimeValue> { new TimeValue(outMs, TimeUnit.Millisecond), new TimeValue(outMs, TimeUnit.Millisecond) };
                e.style.opacity = 0f;
                e.style.translate = new Translate(0, yOffset);
                var item = e.schedule.Execute(() => { Ui.Show(e, false); Pending.Remove(e); });
                item.ExecuteLater(outMs + 20);
                Pending[e] = item;
            }
        }
    }

    /// <summary>One entry of a menu (context menu, project menu, sort menu).</summary>
    public sealed class MenuItem
    {
        public string Label, Shortcut, Header;
        public IconKind? Icon;
        public Action Action;
        public bool Danger, Separator, Disabled, Checked;
        /// <summary>Custom row content (e.g. a recent-project row with a thumbnail); Action still runs on click.</summary>
        public VisualElement Custom;
        /// <summary>Extra classes for the menu row (e.g. a taller row for custom content).</summary>
        public string RowClass;

        public static MenuItem Sep() => new MenuItem { Separator = true };
        public static MenuItem Title(string text) => new MenuItem { Header = text };
    }
}
