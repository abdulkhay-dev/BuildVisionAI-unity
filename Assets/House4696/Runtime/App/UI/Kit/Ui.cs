using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    public enum ButtonKind { Primary, Secondary, Ghost, Danger, AccentGhost }

    /// <summary>
    /// Builders of the code-built UI (UiKit): elements, text, buttons, keycaps, inputs, switches — styled by
    /// Resources/UI/Tokens.uss + Components.uss — and Russian text helpers.
    /// Buttons are plain elements with a <see cref="Clickable"/> (not UI Toolkit Buttons): they take no keyboard focus,
    /// so Space/Tab keep driving the 3D view, and no theme styles leak in.
    /// </summary>
    public static class Ui
    {
        // ------------------------------------------------------------------ elements & text
        public static VisualElement El(string classes = null, params VisualElement[] children)
        {
            var e = new VisualElement();
            AddClasses(e, classes);
            foreach (var c in children) if (c != null) e.Add(c);
            return e;
        }

        /// <summary>Label (not pickable). Typical classes: "t-ui c-2", "t-headline ellipsis".</summary>
        public static Label Text(string text, string classes = null)
        {
            var l = new Label(text) { pickingMode = PickingMode.Ignore };
            AddClasses(l, classes);
            return l;
        }

        public static Icon Icon(IconKind kind, int size = 18, string classes = null)
        {
            var i = new Icon(kind);
            i.AddToClassList("icon-" + size);
            AddClasses(i, classes);
            return i;
        }

        public static void AddClasses(VisualElement e, string classes)
        {
            if (string.IsNullOrEmpty(classes)) return;
            foreach (var c in classes.Split(' ')) if (c.Length > 0) e.AddToClassList(c);
        }

        /// <summary>display: none / flex.</summary>
        public static void Show(VisualElement e, bool on) => e.EnableInClassList("hidden", !on);
        public static bool IsShown(VisualElement e) => !e.ClassListContains("hidden");

        /// <summary>Makes any element clickable (left button, press/active states).</summary>
        public static T OnClick<T>(T e, Action onClick) where T : VisualElement
        {
            e.focusable = false;
            e.AddManipulator(new Clickable(() => onClick?.Invoke()));
            return e;
        }

        public static VisualElement DividerV() => El("divider-v");
        public static VisualElement DividerH() => El("divider-h");

        // ------------------------------------------------------------------ buttons
        /// <summary>Text button (h 36, radius 8): primary / secondary / ghost / danger. Optional leading icon.</summary>
        public static VisualElement Button(ButtonKind kind, string label, Action onClick, IconKind? icon = null, string classes = null)
        {
            var b = El("btn " + KindClass(kind));
            AddClasses(b, classes);
            if (icon.HasValue) b.Add(Icon(icon.Value, 16));
            if (!string.IsNullOrEmpty(label))
            {
                var l = Text(label, "btn-label");
                if (icon.HasValue) l.AddToClassList("after-icon");
                b.Add(l);
            }
            return OnClick(b, onClick);
        }

        /// <summary>Square icon button with a tooltip (and shortcut keycaps in the tooltip).</summary>
        public static VisualElement IconButton(IconKind icon, Action onClick, string tooltip, string keys = null, ButtonKind kind = ButtonKind.Ghost, string classes = null, int iconSize = 18)
        {
            var b = El("btn btn-icon " + KindClass(kind));
            AddClasses(b, classes);
            b.Add(Icon(icon, iconSize));
            OnClick(b, onClick);
            if (tooltip != null) Tooltips.Tip(b, tooltip, keys);
            return b;
        }

        /// <summary>Chrome/toolbar item: neutral text-2 → text-1 on hover, "selected" when on.</summary>
        public static VisualElement Tool(IconKind icon, string label, Action onClick, string tooltip = null, string keys = null)
        {
            var t = El("tool");
            t.Add(Icon(icon, 18));
            if (!string.IsNullOrEmpty(label)) t.Add(Text(label, "tool-label"));
            else t.AddToClassList("icon-only");
            OnClick(t, onClick);
            if (tooltip != null) Tooltips.Tip(t, tooltip, keys);
            return t;
        }

        /// <summary>Replaces a button's label text (first .btn-label / .tool-label / .seg-label child).</summary>
        public static void SetLabel(VisualElement button, string text)
        {
            var l = button.Q<Label>(className: "btn-label") ?? button.Q<Label>(className: "tool-label") ?? button.Q<Label>(className: "seg-label");
            if (l != null) l.text = text;
        }

        static string KindClass(ButtonKind k) => k switch
        {
            ButtonKind.Primary => "btn-primary",
            ButtonKind.Secondary => "btn-secondary",
            ButtonKind.Danger => "btn-danger",
            ButtonKind.AccentGhost => "btn-accent-ghost",
            _ => "btn-ghost",
        };

        // ------------------------------------------------------------------ keycaps
        /// <summary>
        /// One keycap: text ("⌘", "Esc", "W") or a mouse glyph ("MouseLeft", "MouseRight", "MouseWheel").
        /// </summary>
        public static VisualElement Kbd(string key, bool small = false)
        {
            VisualElement k;
            IconKind? mouse = key == "MouseLeft" ? IconKind.MouseLeft : key == "MouseRight" ? IconKind.MouseRight : key == "MouseWheel" ? IconKind.MouseWheel : (IconKind?)null;
            if (mouse.HasValue) k = El("kbd", Icon(mouse.Value, 14));
            else if (key == "⌃")
            {
                // the Control glyph is a thin ASCII-like caret in Inter: draw a chevron instead
                var i = Icon(IconKind.ChevronUp, 12);
                i.style.translate = new Translate(0, 1);
                k = El("kbd", i);
            }
            else k = Text(key, "kbd");
            if (small) k.AddToClassList("kbd-sm");
            return k;
        }

        /// <summary>
        /// Keycaps from a spec: space-separated keys ("⌘ ⇧ S", "W A S D"); "/" and "·" become separators;
        /// "MouseLeft" etc. become mouse glyphs.
        /// </summary>
        public static VisualElement Keys(string spec, bool small = false)
        {
            var row = El("keys");
            foreach (var t in spec.Split(' '))
            {
                if (t.Length == 0) continue;
                if (t == "/" || t == "·" || t == "или") row.Add(Text(t, "keys-sep"));
                else row.Add(Kbd(t, small));
            }
            return row;
        }

        // ------------------------------------------------------------------ inputs
        /// <summary>
        /// Text input (h 36, field colour, accent border + 3 px halo when focused). Returns the wrapper to add;
        /// <paramref name="field"/> is the TextField. Optional leading icon and a trailing keycap hint.
        /// </summary>
        public static VisualElement Input(string placeholder, out TextField field, bool multiline = false, IconKind? icon = null, string kbd = null)
        {
            var f = new TextField { multiline = multiline };
            f.AddToClassList("field");
            if (multiline) f.AddToClassList("field-multiline");
            var ph = Text(placeholder ?? "", "field-placeholder");
            f.Add(ph);
            if (icon.HasValue)
            {
                f.AddToClassList("with-icon");
                var i = Icon(icon.Value, 16, "field-icon");
                f.Add(i);
            }
            VisualElement hint = null;
            if (kbd != null)
            {
                hint = Keys(kbd, true);
                hint.AddToClassList("field-kbd");
                hint.pickingMode = PickingMode.Ignore;
                f.Add(hint);
            }
            f.RegisterValueChangedCallback(e =>
            {
                Show(ph, string.IsNullOrEmpty(e.newValue));
                if (hint != null) Show(hint, string.IsNullOrEmpty(e.newValue));
            });
            var wrap = El("field-wrap", f);
            f.RegisterCallback<FocusInEvent>(_ => wrap.AddToClassList("focused"));
            f.RegisterCallback<FocusOutEvent>(_ => wrap.RemoveFromClassList("focused"));
            field = f;
            return wrap;
        }

        /// <summary>Sets a field's value and its placeholder visibility.</summary>
        public static void SetValue(TextField f, string value)
        {
            f.SetValueWithoutNotify(value ?? "");
            var ph = f.Q<Label>(className: "field-placeholder");
            if (ph != null) Show(ph, string.IsNullOrEmpty(value));
            var hint = f.Q(className: "field-kbd");
            if (hint != null) Show(hint, string.IsNullOrEmpty(value));
        }

        /// <summary>Label + switch row (h 36). Call the returned refresh after changing the value elsewhere.</summary>
        public static VisualElement Switch(string label, Func<bool> get, Action<bool> set, out Action refresh)
        {
            var sw = El("switch", El("switch-knob"));
            var row = El("switch-row", Text(label, "switch-label"), sw);
            Action r = () => sw.EnableInClassList("on", get());
            OnClick(row, () => { set(!get()); r(); });
            r();
            refresh = r;
            return row;
        }

        // ------------------------------------------------------------------ Russian text
        static readonly NumberFormatInfo Ru = new NumberFormatInfo { NumberDecimalSeparator = ",", NumberGroupSeparator = " " };
        static readonly string[] Months = { "янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек" };

        /// <summary>1 этаж, 2 этажа, 5 этажей.</summary>
        public static string Plural(int n, string one, string few, string many)
        {
            int m10 = n % 10, m100 = n % 100;
            string w = m10 == 1 && m100 != 11 ? one : m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14) ? few : many;
            return n + " " + w;
        }

        public static string Number(float v, string format = "0.#") => v.ToString(format, Ru);

        /// <summary>"212 м²".</summary>
        public static string Area(float m2) => Number(m2, m2 >= 100f ? "0" : "0.#") + " м²";

        /// <summary>"только что", "5 мин назад", "3 ч назад", "вчера", "25 сен", "25 сен 2024".</summary>
        public static string Ago(string isoUtc)
        {
            if (string.IsNullOrEmpty(isoUtc) || !DateTime.TryParse(isoUtc, CultureInfo.InvariantCulture,
                    DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out var t)) return "";
            return Ago(t);
        }

        public static string Ago(DateTime utc)
        {
            var d = DateTime.UtcNow - utc;
            if (d.TotalSeconds < 50) return "только что";
            if (d.TotalMinutes < 60) return $"{Mathf.Max(1, (int)d.TotalMinutes)} мин назад";
            var local = utc.ToLocalTime();
            var today = DateTime.Now.Date;
            if (local.Date == today) return $"{(int)d.TotalHours} ч назад";
            if (local.Date == today.AddDays(-1)) return "вчера";
            string s = local.Day + " " + Months[local.Month - 1];
            return local.Year == today.Year ? s : s + " " + local.Year;
        }

        /// <summary>Text width in panel px for a label style (for animated widths; USS cannot animate to auto).</summary>
        public static float Measure(Label reference, string text)
        {
            var size = reference.MeasureTextSize(text, 0, VisualElement.MeasureMode.Undefined, 0, VisualElement.MeasureMode.Undefined);
            return Mathf.Ceil(size.x);
        }

        /// <summary>Sorted copy helper for lists shown in the UI.</summary>
        public static List<T> Sorted<T>(IEnumerable<T> items, Comparison<T> cmp)
        {
            var l = new List<T>(items);
            l.Sort(cmp);
            return l;
        }
    }
}
