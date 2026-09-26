using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Hover tooltips (UI Toolkit shows none at runtime): text, optional second line and shortcut keycaps. Shown after
    /// 500 ms (at once within 800 ms of the previous tooltip, like native apps), 8 px below top-half anchors and above
    /// bottom-half ones, clamped to the window. Hidden on pointer down, while the cursor is captured and while the
    /// anchor's own popover is open.
    /// </summary>
    public sealed class Tooltips
    {
        const long Delay = 500;
        const float Warm = 0.8f;

        static Tooltips _instance;
        static readonly List<(VisualElement e, string text, string keys, string sub)> Early = new List<(VisualElement, string, string, string)>();

        readonly VisualElement _layer, _tip, _keys;
        readonly Label _text, _sub;
        sealed class Content { public string Text, Keys, Sub; }
        // weak keys: rebuilt popover/dialog content does not pile up
        readonly System.Runtime.CompilerServices.ConditionalWeakTable<VisualElement, Content> _content = new System.Runtime.CompilerServices.ConditionalWeakTable<VisualElement, Content>();
        VisualElement _target;
        IVisualElementScheduledItem _pending;
        float _hiddenAt = -10f;

        /// <summary>While true no tooltip shows (cursor captured, dragging the camera).</summary>
        public static bool Suppressed;

        public Tooltips(VisualElement layer)
        {
            _instance = this;
            _layer = layer;
            _text = Ui.Text("", "tip-text");
            _sub = Ui.Text("", "tip-sub");
            _text.enableRichText = false;       // project names are shown as typed
            _sub.enableRichText = false;
            _keys = Ui.El("tip-keys");
            _tip = Ui.El("tip", Ui.El("tip-body", _text, _sub), _keys);
            _tip.pickingMode = PickingMode.Ignore;
            _tip.RegisterCallback<GeometryChangedEvent>(_ => Place());
            _layer.Add(_tip);
            foreach (var t in Early) Tip(t.e, t.text, t.keys, t.sub);
            Early.Clear();
        }

        /// <summary>
        /// Gives <paramref name="e"/> a tooltip: text, optional shortcut ("⌘ O", "Tab" — space-separated keycaps) and an
        /// optional second line. Calling again updates the content.
        /// </summary>
        public static T Tip<T>(T e, string text, string keys = null, string sub = null) where T : VisualElement
        {
            if (_instance == null) { Early.Add((e, text, keys, sub)); return e; }
            var t = _instance;
            bool first = !t._content.TryGetValue(e, out var c);
            if (first) { c = new Content(); t._content.Add(e, c); }
            c.Text = text; c.Keys = keys; c.Sub = sub;
            if (first)
            {
                e.RegisterCallback<PointerEnterEvent>(_ => t.Enter(e));
                e.RegisterCallback<PointerLeaveEvent>(_ => t.Leave(e));
                e.RegisterCallback<PointerDownEvent>(_ => t.Hide(), TrickleDown.TrickleDown);
                e.RegisterCallback<DetachFromPanelEvent>(_ => { if (t._target == e) t.Hide(); });
            }
            if (t._target == e) t.Fill(e);
            return e;
        }

        /// <summary>Removes the tooltip of an element.</summary>
        public static void Untip(VisualElement e)
        {
            if (_instance == null) return;
            _instance._content.Remove(e);
            if (_instance._target == e) _instance.Hide();
        }

        public static void HideNow() => _instance?.Hide();

        void Enter(VisualElement e)
        {
            _target = e;
            _pending?.Pause();
            bool warm = Time.unscaledTime - _hiddenAt < Warm || _tip.ClassListContains("show");
            _pending = _tip.schedule.Execute(() => Show(e));
            _pending.ExecuteLater(warm ? 0 : Delay);
        }

        void Leave(VisualElement e)
        {
            if (_target == e) Hide();
        }

        void Hide()
        {
            _pending?.Pause();
            if (_tip.ClassListContains("show")) _hiddenAt = Time.unscaledTime;
            _tip.RemoveFromClassList("show");
            _target = null;
        }

        void Show(VisualElement e)
        {
            if (_target != e || e.panel == null || Suppressed || e.ClassListContains("popover-open") || !_content.TryGetValue(e, out _)) return;
            Fill(e);
            Place();
            _tip.AddToClassList("show");
        }

        void Fill(VisualElement e)
        {
            if (!_content.TryGetValue(e, out var c)) return;
            _text.text = c.Text;
            _sub.text = c.Sub ?? "";
            Ui.Show(_sub, !string.IsNullOrEmpty(c.Sub));
            _keys.Clear();
            if (!string.IsNullOrEmpty(c.Keys))
                foreach (var k in c.Keys.Split(' '))
                    if (k.Length > 0) _keys.Add(k == "/" || k == "·" ? Ui.Text(k, "tip-sub") : Ui.Text(k, "tip-kbd"));
            Ui.Show(_keys, _keys.childCount > 0);
        }

        void Place()
        {
            if (_target == null || _target.panel == null) return;
            var root = _layer.worldBound;
            var a = _target.worldBound;
            float w = _tip.resolvedStyle.width, h = _tip.resolvedStyle.height;
            if (float.IsNaN(w) || float.IsNaN(h)) return;
            bool above = a.center.y > root.center.y;
            float x = Mathf.Clamp(a.center.x - w * 0.5f, root.xMin + 8f, root.xMax - w - 8f);
            float y = above ? a.yMin - h - 8f : a.yMax + 8f;
            _tip.style.left = x - root.xMin;
            _tip.style.top = y - root.yMin;
        }

        public void Tick()
        {
            if (Suppressed && _target != null) Hide();
        }
    }
}
