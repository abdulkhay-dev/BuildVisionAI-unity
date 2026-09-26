using System;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Dialog: scrim + surface-2 card (radius 16, padding 24, e3 shadow) with title, optional subtitle, ✕ (Esc),
    /// body and a right-aligned footer. ↩ runs <see cref="Primary"/> unless the dialog is destructive.
    /// Subclasses fill <see cref="Body"/> and <see cref="Foot"/> in their constructor and call <see cref="Show"/>.
    /// </summary>
    public class Modal
    {
        public readonly VisualElement Host, Scrim, Shell, Card, Head, Body, Foot;
        protected readonly AppUI Ui_;
        readonly Label _title, _subtitle;

        /// <summary>Esc / ✕ / scrim click close the dialog.</summary>
        public bool Dismissable = true;
        /// <summary>↩ runs this (null = nothing). Destructive dialogs leave it null.</summary>
        public Action Primary;
        public event Action Closed;

        public Modal(AppUI ui, string title, string subtitle, float width, bool closeButton = true)
        {
            Ui_ = ui;
            Host = Ui.El("modal-host");
            Scrim = Ui.El("scrim");
            Scrim.RegisterCallback<PointerDownEvent>(_ => Dismiss());
            Card = Ui.El("modal");
            Card.style.width = width;
            _title = Ui.Text(title, "t-title");
            _subtitle = Ui.Text(NoOrphan(subtitle), "modal-subtitle");
            Ui.Show(_subtitle, !string.IsNullOrEmpty(subtitle));
            Head = Ui.El("modal-head", Ui.El("modal-titles", _title, _subtitle));
            Body = Ui.El("modal-body");
            Foot = Ui.El("modal-foot");
            Card.Add(Head);
            Card.Add(Body);
            Card.Add(Foot);
            // ✕ sits in the corner, outside the title row, so the subtitle gets the full width
            if (closeButton) Card.Add(Ui.IconButton(IconKind.Close, Dismiss, "Закрыть", "Esc", classes: "btn-xs modal-close", iconSize: 16));
            Shell = Elevation.Wrap(Card, 16, 48, 20, 0.6f, "modal-shell");
            Host.Add(Scrim);
            Host.Add(Shell);
        }

        public string Title { get => _title.text; set => _title.text = value; }
        public string Subtitle
        {
            get => _subtitle.text;
            set { _subtitle.text = NoOrphan(value); Ui.Show(_subtitle, !string.IsNullOrEmpty(value)); }
        }

        /// <summary>Joins the last two words with a no-break space, so a paragraph never ends on a lone word.</summary>
        public static string NoOrphan(string text)
        {
            if (string.IsNullOrEmpty(text)) return text ?? "";
            int i = text.TrimEnd().LastIndexOf(' ');
            return i > 0 ? text.Substring(0, i) + "\u00A0" + text.Substring(i + 1) : text;
        }

        public void Show() => Ui_.ShowModal(this);
        public void Close() => Ui_.CloseModal(this);
        public virtual void Dismiss() { if (Dismissable) Close(); }
        /// <summary>After the dialog is on screen (focus a field here).</summary>
        public virtual void OnShown() { }
        public virtual void OnClosed() => Closed?.Invoke();
        /// <summary>Every frame while open.</summary>
        public virtual void Tick() { }
    }
}
