using System;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    public enum ToastKind { Info, Success, Error, Ai }

    /// <summary>
    /// One toast at a time, top-centre: icon, text (with inline keycaps: "{H}", "{Esc}"), optional action. A new toast
    /// replaces the old one with a quick content crossfade (the surface stays up); toasts with the same merge key update
    /// in place ("ИИ внёс 4 правки"). 3.5 s, 6 s with an action, 8 s for errors; hover pauses.
    /// </summary>
    public sealed class Toasts
    {
        static readonly Regex KeyToken = new Regex(@"\{([^}]+)\}");

        readonly VisualElement _host, _toast, _content, _textRow;
        readonly Icon _icon;
        readonly VisualElement _actionSlot;
        float _hideAt = -1f;
        bool _hover;
        string _mergeKey;
        int _mergeCount;
        IVisualElementScheduledItem _pendingHide, _pendingShow;

        public Toasts(VisualElement layer)
        {
            _icon = new Icon(IconKind.Info);
            _textRow = Ui.El("toast-text-row");
            _actionSlot = Ui.El("toast-action");
            _content = Ui.El("toast-content", _icon, _textRow, _actionSlot);
            _toast = Ui.El("toast", _content);
            _toast.RegisterCallback<PointerEnterEvent>(_ => _hover = true);
            _toast.RegisterCallback<PointerLeaveEvent>(_ => _hover = false);
            _host = Ui.El("toast-host", Elevation.Wrap(_toast, 12, 24, 10, 0.55f));
            _host.pickingMode = PickingMode.Ignore;
            layer.Add(_host);
            Ui.Show(_host, false);
        }

        /// <param name="mergeKey">toasts with the same key count up: <paramref name="mergeText"/>(count) replaces the text.</param>
        public void Show(string text, IconKind icon = IconKind.Info, ToastKind kind = ToastKind.Info, string action = null, Action onAction = null,
            string mergeKey = null, Func<int, string> mergeText = null)
        {
            _pendingHide?.Pause();
            _pendingShow?.Pause();
            bool visible = Ui.IsShown(_host) && _toast.ClassListContains("show");
            bool merge = mergeKey != null && visible && mergeKey == _mergeKey;
            _mergeCount = merge ? _mergeCount + 1 : 1;
            if (merge && mergeText != null) text = mergeText(_mergeCount);
            _mergeKey = mergeKey;

            bool hasAction = action != null && onAction != null;
            _hideAt = Time.unscaledTime + (kind == ToastKind.Error ? 8f : hasAction ? 6f : 3.5f);

            void Fill()
            {
                SetText(text);
                _icon.Kind = icon;
                _toast.EnableInClassList("success", kind == ToastKind.Success);
                _toast.EnableInClassList("error", kind == ToastKind.Error);
                _toast.EnableInClassList("ai", kind == ToastKind.Ai);
                _actionSlot.Clear();
                if (hasAction) _actionSlot.Add(Ui.Button(ButtonKind.AccentGhost, action, () => { onAction(); Hide(); }));
                _toast.EnableInClassList("no-action", !hasAction);
            }

            if (merge)
            {
                // same series: update in place, no blink
                SetText(text);
                return;
            }
            Ui.Show(_host, true);
            if (visible)
            {
                // replace: the surface stays, the content crossfades
                _content.style.opacity = 0f;
                _pendingShow = _content.schedule.Execute(() => { Fill(); _content.style.opacity = 1f; });
                _pendingShow.ExecuteLater(90);
            }
            else
            {
                Fill();
                _content.style.opacity = 1f;
                _pendingShow = _toast.schedule.Execute(() => _toast.AddToClassList("show"));
                _pendingShow.ExecuteLater(16);
            }
        }

        /// <summary>Text with "{Key}" tokens rendered as small keycaps between labels.</summary>
        void SetText(string text)
        {
            _textRow.Clear();
            int at = 0;
            foreach (Match m in KeyToken.Matches(text ?? ""))
            {
                if (m.Index > at) _textRow.Add(Ui.Text(text.Substring(at, m.Index - at), "toast-text"));
                var k = Ui.Kbd(m.Groups[1].Value, true);
                k.AddToClassList("toast-kbd");
                _textRow.Add(k);
                at = m.Index + m.Length;
            }
            if (at < (text ?? "").Length) _textRow.Add(Ui.Text(text.Substring(at), "toast-text"));
        }

        public void Hide()
        {
            _hideAt = -1f;
            _pendingShow?.Pause();
            _toast.RemoveFromClassList("show");
            _mergeKey = null;
            _pendingHide?.Pause();
            _pendingHide = _toast.schedule.Execute(() => { if (!_toast.ClassListContains("show")) Ui.Show(_host, false); });
            _pendingHide.ExecuteLater(200);
        }

        public void Tick()
        {
            if (_hideAt < 0f) return;
            if (_hover) { _hideAt = Mathf.Max(_hideAt, Time.unscaledTime + 1.5f); return; }
            if (Time.unscaledTime > _hideAt) Hide();
        }
    }
}
