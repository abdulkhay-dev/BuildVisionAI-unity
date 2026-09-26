using System;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// «Начало работы» on Home (spec §5): surface-1 card with three steps in columns — connect the AI, ask it to build a
    /// house, take a walk. Each step has a 24 px circle (border-strong ring → success fill with a check), a title, a
    /// caption and a secondary action (h 32) that turns into «Готово» once the step is done.
    /// </summary>
    internal sealed class HomeChecklist
    {
        public readonly VisualElement Element;
        readonly Label _progress;
        readonly Step _connect, _prompt, _walk;

        public HomeChecklist(Action connect, Action copyPrompt, Action walk, Action dismiss)
        {
            _progress = Ui.Text("0 из 3", "t-caption c-3 home-check-progress");
            // spec §5: ✕ «Скрыть» — a small ghost button with the label, not an icon-only one
            var close = Ui.Button(ButtonKind.Ghost, "Скрыть", dismiss, IconKind.Close, "btn-xs home-check-close");
            Tooltips.Tip(close, "Скрыть «Начало работы»", null, "Список больше не появится");
            var head = Ui.El("home-check-head", Ui.Text("Начало работы", "t-headline"), _progress, Ui.El("grow"), close);

            _connect = new Step(1, "Подключите ИИ-ассистента", "Claude, Cursor или другой клиент", "Подключить", connect,
                "Подключить ИИ-ассистента", "Выберите приложение, в котором вы общаетесь с ИИ");
            _prompt = new Step(2, "Попросите ИИ построить дом", "Например: «одноэтажный дом 10×12 м с террасой»", "Скопировать запрос", copyPrompt,
                "Скопировать пример запроса", "Вставьте его в чат с ИИ-ассистентом");
            _walk = new Step(3, "Прогуляйтесь по дому", "Режим «Прогулка» — ⌘2", "Перейти", walk,
                "Открыть проект в режиме «Прогулка»", null);

            var steps = Ui.El("home-check-steps", _connect.Root, Divider(), _prompt.Root, Divider(), _walk.Root);
            Element = Ui.El("home-check on-surface-1", head, steps);
        }

        static VisualElement Divider()
        {
            var d = Ui.El("home-check-divider");
            d.pickingMode = PickingMode.Ignore;
            return d;
        }

        /// <summary>
        /// Applies the progress. <paramref name="walkName"/> is the project «Перейти» opens (null = there is no project yet,
        /// the action is disabled with a caption saying why). Returns the number of finished steps.
        /// </summary>
        public int Set(bool connected, bool built, bool walked, string walkName)
        {
            _connect.SetDone(connected);
            _prompt.SetDone(built);
            _walk.SetDone(walked);
            bool canWalk = walkName != null;
            _walk.SetAvailable(canWalk, canWalk ? null : "Сначала создайте проект");
            if (canWalk) _walk.SetTip("Открыть «" + walkName + "» в режиме «Прогулка»");
            int done = (connected ? 1 : 0) + (built ? 1 : 0) + (walked ? 1 : 0);
            _progress.text = done + " из 3";
            return done;
        }

        sealed class Step
        {
            public readonly VisualElement Root;
            readonly VisualElement _button, _done;
            readonly Label _number, _caption;
            readonly Icon _check;
            readonly string _defaultCaption, _tipSub;

            public Step(int n, string title, string caption, string action, Action onClick, string tip, string tipSub)
            {
                _defaultCaption = caption;
                _tipSub = tipSub;
                _number = Ui.Text(n.ToString(), "home-step-num");
                _check = Ui.Icon(IconKind.Check, 14, "home-step-check");
                Ui.Show(_check, false);
                var circle = Ui.El("home-step-circle", _number, _check);
                circle.pickingMode = PickingMode.Ignore;

                _caption = Ui.Text(caption, "t-caption c-3 home-step-caption");
                _button = Ui.Button(ButtonKind.Secondary, action, onClick, null, "btn-sm home-step-action");
                Tooltips.Tip(_button, tip, null, tipSub);
                _done = Ui.El("home-step-done", Ui.Icon(IconKind.Check, 14), Ui.Text("Готово", "t-caption-m"));
                _done.pickingMode = PickingMode.Ignore;
                Ui.Show(_done, false);
                var text = Ui.El("home-step-text", Ui.Text(title, "t-ui home-step-title"), _caption, _button, _done);
                Root = Ui.El("home-step", circle, text);
            }

            public void SetDone(bool done)
            {
                Root.EnableInClassList("done", done);
                Ui.Show(_number, !done);
                Ui.Show(_check, done);
                Ui.Show(_button, !done);
                Ui.Show(_done, done);
            }

            /// <summary>Disables the action with a caption that says why (spec: a disabled button always has one).</summary>
            public void SetAvailable(bool on, string why)
            {
                _button.SetEnabled(on);
                string caption = on || string.IsNullOrEmpty(why) ? _defaultCaption : why;
                if (_caption.text != caption) _caption.text = caption;
            }

            public void SetTip(string tip) => Tooltips.Tip(_button, tip, null, _tipSub);
        }
    }
}
