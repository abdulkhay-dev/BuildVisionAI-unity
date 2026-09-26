using System;
using System.Collections.Generic;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Overlay of the 3D view (spec §3.6, §3.2, §2). <see cref="Element"/> sits in the chrome layer (hidden by clean view
    /// and the veil): the AI activity line, the coach slot (look hint / mode hint strip), the empty-site card and the FPS
    /// chip. <see cref="HudElement"/> stays in clean view: the door prompt, the crosshair and the clean-view restore pill
    /// (the way back for mouse users: it appears when the pointer moves and leaves after 1.5 s of stillness).
    /// </summary>
    public sealed class ViewerOverlay
    {
        enum Coach { None, LookWalk, LookFly, StripOrbit, StripWalk, StripFly, StripFurniture, StripPlacing }

        const float LookDelay = 0.6f, StripSeconds = 6f, StripMinSeconds = 1.5f;
        const float AiLoopSeconds = 1.1f, AiSegmentShare = 0.3f, FpsEvery = 0.25f, PickEvery = 0.1f;
        const int CoachFadeMs = 180;
        /// <summary>Restore pill: leaves after this much pointer stillness; motion right after entering is ignored.</summary>
        const float RestoreIdle = 1.5f, RestoreArm = 0.3f;
        const int RestoreInMs = 160, RestoreOutMs = 240;

        static readonly List<EasingFunction> HideEasing = new List<EasingFunction>
            { new EasingFunction(EasingMode.EaseInOutSine), new EasingFunction(EasingMode.EaseInOutSine) };

        /// <summary>The example request of the empty-site card (spec §3.6).</summary>
        public const string EmptySitePrompt =
            "Спроектируй одноэтажный дом 10×12 м: гостиная с кухней, две спальни, санузел и терраса. Расставь мебель.";

        static readonly string[] FpsText = new string[241];

        readonly AppUI _ui;

        // chrome part
        readonly VisualElement _aiLine, _aiSeg;
        readonly VisualElement _coachHost, _coachWrap;
        readonly VisualElement[] _coachItems = new VisualElement[8];
        readonly VisualElement _emptyHost, _emptyConnect, _emptyStatus;
        readonly PulseDot _emptyDot;
        readonly Label _emptyStatusText;
        readonly VisualElement _fps;
        readonly Label _fpsText;

        // hud part
        readonly VisualElement _doorWrap, _crosshair, _restoreWrap;
        readonly Label _doorKey, _doorText;

        // clean-view restore pill
        bool _restoreShown, _restoreHover, _wasClean, _pointerKnown;
        float _cleanSince, _lastMove = -10f;
        Vector2 _lastPointer;

        bool _aiOn, _emptyShown, _hudShown = true, _crossShown, _doorShown, _showFps, _showHints = true;
        float _aiT, _fpsAcc, _coachShift;
        int _fpsFrames, _fpsValue = -1;
        string _prompt;

        Coach _coachShown = Coach.None, _stripOverride = Coach.None;
        float _coachFreeAt, _stripAt, _stripUntil, _sceneSince = -1f, _nextPick;
        HouseViewer.Mode _stripMode;
        bool _pointerOnScene, _flyLooked;

        public VisualElement Element { get; }
        public VisualElement HudElement { get; }

        public ViewerOverlay(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("layer");
            Element.pickingMode = PickingMode.Ignore;
            HudElement = Ui.El("layer");
            HudElement.pickingMode = PickingMode.Ignore;

            // ---- AI line: a 2 px violet segment running across the top while the AI works
            _aiSeg = Ui.El("ov-ai-seg");
            _aiSeg.usageHints = UsageHints.DynamicTransform;
            _aiLine = Ui.El("ov-ai-line", _aiSeg);
            NoPick(_aiLine);
            Ui.Show(_aiLine, false);

            // ---- coach slot: one pill, one message at a time
            var coach = Ui.El("ov-coach");
            _coachItems[(int)Coach.LookWalk] = Strip(("MouseLeft", "Щёлкните по сцене, чтобы осмотреться"));
            // the fly camera looks with the right button (it never captures the cursor)
            _coachItems[(int)Coach.LookFly] = Strip(("MouseRight", "Зажмите правую кнопку, чтобы осмотреться"));
            _coachItems[(int)Coach.StripOrbit] = Strip(("MouseLeft", "вращать"), ("MouseRight", "сдвиг"), ("MouseWheel", "масштаб"), ("F", "к дому"));
            _coachItems[(int)Coach.StripWalk] = Strip(("W A S D", "идти"), ("Shift", "бег"), ("E", "дверь"), ("C", "присесть"), ("Esc", "отпустить мышь"));
            _coachItems[(int)Coach.StripFly] = Strip(("W A S D", "лететь"), ("E Q", "вверх/вниз"), ("Shift", "быстрее"));
            _coachItems[(int)Coach.StripFurniture] = Strip(("MouseLeft", "выбрать и двигать"), ("R", "повернуть"), ("⌫", "удалить"), ("MouseRight", "осмотреться"));
            _coachItems[(int)Coach.StripPlacing] = Strip(("MouseLeft", "поставить"), ("R", "повернуть"), ("MouseWheel", "точнее"), ("Esc", "отмена"));
            for (int i = 1; i < _coachItems.Length; i++)
            {
                coach.Add(_coachItems[i]);
                Ui.Show(_coachItems[i], false);
            }
            _coachWrap = Elevation.Wrap(coach, 12, 16, 4f, 0.45f, "ov-coach-wrap");
            _coachHost = Ui.El("ov-coach-host", _coachWrap);
            NoPick(_coachHost);                  // information only: the look hint must not hide itself
            Ui.Show(_coachWrap, false);

            // ---- empty-site card
            var card = Ui.El("ov-empty");
            card.Add(Ui.El("ov-empty-tile", Ui.Icon(IconKind.Sparkle, 24)));
            card.Add(Ui.Text("Участок готов", "t-title ov-empty-title"));
            card.Add(Ui.Text("Попросите ИИ-ассистента построить дом — изменения появятся здесь сразу.", "ov-empty-text"));
            var copy = Ui.Button(ButtonKind.Ghost, "Скопировать", () => _ui.Copy(EmptySitePrompt), IconKind.Copy, "btn-sm ov-empty-copy");
            Tooltips.Tip(copy, "Скопировать запрос и вставить его в чат с ИИ");
            card.Add(Ui.El("ov-empty-prompt",
                Ui.Text(EmptySitePrompt, "ov-empty-prompt-text"),
                Ui.El("ov-empty-prompt-foot", copy)));
            _emptyDot = new PulseDot();
            _emptyStatusText = Ui.Text("", "ov-empty-status-text");
            _emptyStatus = Ui.El("ov-empty-status", _emptyDot, _emptyStatusText);
            _emptyStatus.pickingMode = PickingMode.Ignore;
            _emptyConnect = Ui.Button(ButtonKind.Primary, "Подключить ИИ", () => _ui.ShowConnectAi(), IconKind.Sparkle);
            Tooltips.Tip(_emptyConnect, "Настроить ИИ-ассистента для работы с House");
            card.Add(Ui.El("ov-empty-foot", _emptyStatus, _emptyConnect));
            _emptyHost = Ui.El("ov-empty-host", Elevation.Wrap(card, 16, 24, 10f, 0.55f, "ov-empty-wrap"));
            _emptyHost.pickingMode = PickingMode.Ignore;
            Ui.Show(_emptyHost, false);

            // ---- FPS chip
            _fpsText = Ui.Text("", "ov-fps-text");
            _fps = Ui.El("ov-fps", _fpsText);
            NoPick(_fps);
            Ui.Show(_fps, false);

            Element.Add(_emptyHost);
            Element.Add(_coachHost);
            Element.Add(_fps);
            Element.Add(_aiLine);

            // ---- HUD: door prompt (top 60 %) and the crosshair (only while the cursor is captured)
            _doorKey = Ui.Text("E", "kbd");
            _doorText = Ui.Text("", "ov-door-text");
            var door = Ui.El("ov-door", _doorKey, _doorText);
            _doorWrap = Elevation.Wrap(door, 12, 16, 4f, 0.45f, "ov-door-wrap");
            var doorHost = Ui.El("ov-door-host", _doorWrap);
            NoPick(doorHost);
            Ui.Show(_doorWrap, false);
            // an opaque 1 px dark ring around a 6 px text-1 dot at 70 % (only the dot is translucent)
            _crosshair = Ui.El("ov-crosshair", Ui.El("ov-crosshair-dot"));
            NoPick(_crosshair);
            Ui.Show(_crosshair, false);
            HudElement.Add(doorHost);
            HudElement.Add(_crosshair);

            // ---- clean view (H): «Показать интерфейс» [H], bottom-centre where the toolbar was
            var restore = Ui.El("ov-restore");
            restore.Add(Ui.Icon(IconKind.Eye, 16, "ov-restore-icon"));
            restore.Add(Ui.Text("Показать интерфейс", "ov-restore-text"));
            restore.Add(Ui.Kbd("H"));
            Ui.OnClick(restore, () => _ui.SetCleanView(false));
            Tooltips.Tip(restore, "Вернуть панели и кнопки", "H / Esc");
            restore.RegisterCallback<PointerEnterEvent>(_ => _restoreHover = true);
            restore.RegisterCallback<PointerLeaveEvent>(_ => _restoreHover = false);
            _restoreWrap = Elevation.Wrap(restore, 12, 16, 4f, 0.45f, "ov-restore-wrap");
            var restoreHost = Ui.El("ov-restore-host", _restoreWrap);
            restoreHost.pickingMode = PickingMode.Ignore;
            Ui.Show(_restoreWrap, false);
            HudElement.Add(restoreHost);

            // ---- events
            var s = _ui.S;
            if (s?.Viewer != null) s.Viewer.ModeChanged += OnModeChanged;
            if (s?.Settings != null) s.Settings.Changed += OnSettings;
            if (_ui.Ai != null) _ui.Ai.Changed += SyncAiStatus;
            OnSettings();
            Refresh();
        }

        // ------------------------------------------------------------------ state
        public void Refresh()
        {
            var session = _ui.S?.Session;
            bool empty = session != null && session.HasProject && session.Doc.Walls.Count == 0 && session.Doc.Rooms.Count == 0;
            if (empty != _emptyShown)
            {
                _emptyShown = empty;
                // fades out on the first rebuild that has walls or rooms
                Motion.Fade(_emptyHost, empty, 180, 240, 8f);
            }
            SyncAiStatus();
        }

        public void Tick()
        {
            if (_ui.S == null) return;
            float now = Time.unscaledTime, dt = Mathf.Min(Time.unscaledDeltaTime, 0.1f);
            TickHud();
            TickRestore(now);
            TickAiLine(dt);
            TickFps();
            TickCoach(now);
        }

        void OnSettings()
        {
            var st = _ui.S?.Settings;
            if (st == null) return;
            _showHints = st.ShowHints;
            if (!_showHints) _stripUntil = 0f;
            bool fps = st.ShowStats;
            if (fps == _showFps) return;
            _showFps = fps;
            _fpsFrames = 0;
            _fpsAcc = 0f;
            _fpsValue = -1;
            _fpsText.text = "— FPS";
            Ui.Show(_fps, fps);
        }

        /// <summary>The furniture library opened: its controls show in the coach slot (as after a mode switch).</summary>
        public void ShowFurnitureHints()
        {
            if (!_showHints) return;
            _stripOverride = Coach.StripFurniture;
            _stripAt = Time.unscaledTime;
            _stripUntil = _stripAt + StripSeconds;
        }

        void OnModeChanged(HouseViewer.Mode mode)
        {
            _flyLooked = false;
            _sceneSince = -1f;
            _stripOverride = Coach.None;
            if (!_showHints) return;
            _stripMode = mode;
            _stripAt = Time.unscaledTime;
            _stripUntil = _stripAt + StripSeconds;
        }

        // ------------------------------------------------------------------ empty-site card
        void SyncAiStatus()
        {
            var ai = _ui.Ai;
            if (ai == null) return;
            bool connect = ai.State == AiState.NotConnected;
            Ui.Show(_emptyConnect, connect);
            Ui.Show(_emptyStatus, !connect);
            switch (ai.State)
            {
                case AiState.Waiting:
                    _emptyDot.SetStyle("dot-ring", false);
                    _emptyStatusText.text = "ИИ подключён";
                    break;
                case AiState.Online:
                    _emptyDot.SetStyle("dot-success", false);
                    _emptyStatusText.text = "ИИ на связи";
                    break;
                case AiState.Working:
                    _emptyDot.SetStyle("dot-ai", true);
                    _emptyStatusText.text = ai.Phrase;
                    break;
            }
        }

        // ------------------------------------------------------------------ HUD
        void TickHud()
        {
            var v = _ui.S.Viewer;
            bool hud = !_ui.VeilVisible && !_ui.HomeOpen;
            if (hud != _hudShown)
            {
                _hudShown = hud;
                Ui.Show(HudElement, hud);
            }

            // the HUD layer sits above the chrome layer: keep it off the large plan card (it lives in the chrome layer)
            bool large = _ui.Plan != null && _ui.Plan.LargeOpen;
            bool cross = hud && !large && v != null && v.CursorCaptured;
            if (cross != _crossShown)
            {
                _crossShown = cross;
                Ui.Show(_crosshair, cross);
            }

            string prompt = hud && !large && !_ui.ModalOpen && v != null && v.Current != null ? v.Current.Prompt : null;
            if (string.Equals(prompt, _prompt)) return;
            _prompt = prompt;
            if (prompt == null)
            {
                if (_doorShown) Motion.Fade(_doorWrap, false, 140, 120, 4f);
                _doorShown = false;
                return;
            }
            // "E — открыть дверь" → keycap E + «Открыть дверь»
            ParsePrompt(prompt, out string key, out string text);
            _doorKey.text = key ?? "";
            Ui.Show(_doorKey, !string.IsNullOrEmpty(key));
            _doorText.EnableInClassList("ov-no-key", string.IsNullOrEmpty(key));
            _doorText.text = text;
            if (!_doorShown) Motion.Fade(_doorWrap, true, 140, 120, 4f);
            _doorShown = true;
        }

        /// <summary>
        /// Clean view's way back for the mouse: the pill fades in (160 ms) when the pointer moves over the viewer and
        /// fades out (240 ms) after 1.5 s of stillness — it stays while hovered. Never while the cursor is captured, a
        /// popover or dialog is open, or a snapshot is being rendered (and snapshots render the camera only, no UI).
        /// </summary>
        void TickRestore(float now)
        {
            bool clean = _ui.CleanView;
            if (clean != _wasClean)
            {
                _wasClean = clean;
                _cleanSince = now;
                _lastMove = -10f;         // the motion that led to the H key / the button click does not count
            }

            // pointer motion is polled: over the bare 3D view no element is picked, so no PointerMoveEvent arrives
            bool moved = false;
            var m = Mouse.current;
            if (m != null)
            {
                var p = m.position.ReadValue();
                bool inside = p.x >= 0f && p.y >= 0f && p.x <= Screen.width && p.y <= Screen.height;
                moved = _pointerKnown && inside && (p - _lastPointer).sqrMagnitude > 1f;
                _lastPointer = p;
                _pointerKnown = true;
            }

            var s = _ui.S;
            bool eligible = clean && _hudShown && !_ui.PopoverOpen && !_ui.ModalOpen
                            && (s.Viewer == null || !s.Viewer.CursorCaptured)
                            && (s.Snapshots == null || !s.Snapshots.Busy);
            if (!eligible) _lastMove = -10f;
            else if (moved && now - _cleanSince >= RestoreArm) _lastMove = now;

            bool want = eligible && (_restoreHover || now - _lastMove < RestoreIdle);
            if (want == _restoreShown) return;
            _restoreShown = want;
            if (!want) _restoreHover = false;         // a hidden element gets no PointerLeave
            Motion.Fade(_restoreWrap, want, RestoreInMs, RestoreOutMs);
            // chrome hide eases in-out-sine (spec §7); Motion eases out-cubic both ways
            if (!want) _restoreWrap.style.transitionTimingFunction = HideEasing;
        }

        static void ParsePrompt(string prompt, out string key, out string text)
        {
            key = null;
            text = prompt.Trim();
            int dash = prompt.IndexOf(" — ", StringComparison.Ordinal);
            if (dash > 0 && dash <= 8)
            {
                key = prompt.Substring(0, dash).Trim();
                text = prompt.Substring(dash + 3).Trim();
            }
            if (text.Length > 0) text = char.ToUpperInvariant(text[0]) + text.Substring(1);
        }

        // ------------------------------------------------------------------ AI line
        void TickAiLine(float dt)
        {
            bool working = _ui.Ai != null && _ui.Ai.State == AiState.Working;
            if (working != _aiOn)
            {
                _aiOn = working;
                if (working) _aiT = 0f;
                Motion.Fade(_aiLine, working, 240, 160);
            }
            if (!_aiOn && !Ui.IsShown(_aiLine)) return;
            float w = _aiLine.layout.width;
            if (float.IsNaN(w) || w <= 0f) return;
            // one pass left → right per 1.1 s, eased (in-out sine) so it glides in and out of the edges
            _aiT = (_aiT + dt / AiLoopSeconds) % 1f;
            float e = 0.5f - 0.5f * Mathf.Cos(_aiT * Mathf.PI);
            float seg = w * AiSegmentShare;
            _aiSeg.style.translate = new Translate(Mathf.Lerp(-seg, w, e), 0);
        }

        // ------------------------------------------------------------------ FPS
        void TickFps()
        {
            if (!_showFps) return;
            _fpsFrames++;
            _fpsAcc += Time.unscaledDeltaTime;
            if (_fpsAcc < FpsEvery) return;
            int fps = Mathf.Clamp(Mathf.RoundToInt(_fpsFrames / _fpsAcc), 0, FpsText.Length - 1);
            _fpsFrames = 0;
            _fpsAcc = 0f;
            if (fps == _fpsValue) return;
            _fpsValue = fps;
            _fpsText.text = FpsText[fps] ??= fps + " FPS";
        }

        // ------------------------------------------------------------------ coach slot
        void TickCoach(float now)
        {
            var s = _ui.S;
            var v = s.Viewer;

            // follow the toolbar when it makes room for the plan panel
            float shift = _ui.Toolbar != null ? _ui.Toolbar.ShiftX : 0f;
            if (Mathf.Abs(shift - _coachShift) > 0.5f)
            {
                _coachShift = shift;
                _coachHost.style.translate = new Translate(shift, 0);
            }

            bool can = v != null && s.Session.HasProject && !_ui.ModalOpen && !_ui.PopoverOpen && !_ui.HomeOpen && !_ui.VeilVisible
                       && (_ui.Plan == null || !_ui.Plan.LargeOpen);
            Coach want = Coach.None;
            if (v != null)
            {
                if (v.CurrentMode == HouseViewer.Mode.Fly && ViewerInput.RightHeld && ViewerInput.MouseDelta.sqrMagnitude > 4f)
                    _flyLooked = true;
                // the hint strip stays at least 1.5 s, then leaves on the first camera input
                if (_stripUntil > now && now - _stripAt >= StripMinSeconds && CameraInput(v)) _stripUntil = 0f;
                // placing a model: its keys stay while the model follows the pointer
                var fe = _ui.Furniture;
                bool placing = fe != null && fe.Current == FurnitureEditor.State.Placing && !fe.PlacingByDrag;
                if (can && placing && _showHints) want = Coach.StripPlacing;
                else if (can && _stripUntil > now) want = _stripOverride != Coach.None ? _stripOverride : StripFor(_stripMode);
                // arranging furniture: the look hint would nag while the pointer works on the items
                else if (can && !ViewerInput.PointerTool && LookWanted(v, now)) want = v.CurrentMode == HouseViewer.Mode.Walk ? Coach.LookWalk : Coach.LookFly;
                else if (!can) _sceneSince = -1f;
            }
            ApplyCoach(want, now);
        }

        static Coach StripFor(HouseViewer.Mode mode) => mode switch
        {
            HouseViewer.Mode.Orbit => Coach.StripOrbit,
            HouseViewer.Mode.Walk => Coach.StripWalk,
            _ => Coach.StripFly,
        };

        /// <summary>Walk/fly, cursor free, the pointer has stayed over the bare 3D view for 600 ms.</summary>
        bool LookWanted(HouseViewer v, float now)
        {
            bool eligible = v.CurrentMode != HouseViewer.Mode.Orbit && !v.CursorCaptured && Application.isFocused
                            && !(v.CurrentMode == HouseViewer.Mode.Fly && _flyLooked);
            if (!eligible) { _sceneSince = -1f; return false; }
            if (now >= _nextPick)
            {
                _nextPick = now + PickEvery;
                _pointerOnScene = PointerOnScene();
            }
            if (!_pointerOnScene) { _sceneSince = -1f; return false; }
            if (_sceneSince < 0f) _sceneSince = now;
            return now - _sceneSince >= LookDelay;
        }

        bool PointerOnScene()
        {
            var m = Mouse.current;
            if (m == null || m.leftButton.isPressed || m.rightButton.isPressed || m.middleButton.isPressed) return false;
            var p = m.position.ReadValue();
            if (p.x < 0f || p.y < 0f || p.x > Screen.width || p.y > Screen.height) return false;
            return !_ui.PointerOverUI();
        }

        static bool CameraInput(HouseViewer v) =>
            ViewerInput.Move() != Vector2.zero || ViewerInput.ScrollSign != 0f
            || ((ViewerInput.LeftHeld || ViewerInput.RightHeld || ViewerInput.MiddleHeld || v.CursorCaptured)
                && ViewerInput.MouseDelta.sqrMagnitude > 4f);

        /// <summary>One message at a time: the old one fades out (180 ms), then the new one fades in (opacity + y 8→0).</summary>
        void ApplyCoach(Coach want, float now)
        {
            if (want == _coachShown) return;
            if (_coachShown != Coach.None)
            {
                Motion.Fade(_coachWrap, false, CoachFadeMs, CoachFadeMs, 8f);
                _coachShown = Coach.None;
                _coachFreeAt = now + (CoachFadeMs + 20) / 1000f;
                return;
            }
            if (now < _coachFreeAt) return;
            for (int i = 1; i < _coachItems.Length; i++) Ui.Show(_coachItems[i], i == (int)want);
            Motion.Fade(_coachWrap, true, CoachFadeMs, CoachFadeMs, 8f);
            _coachShown = want;
        }

        /// <summary>Keycaps + captions: [W][A][S][D] идти · [Shift] бег …</summary>
        static VisualElement Strip(params (string keys, string text)[] parts)
        {
            var row = Ui.El("ov-coach-row");
            for (int i = 0; i < parts.Length; i++)
            {
                if (i > 0) row.Add(Ui.Text("·", "ov-coach-sep"));
                var keys = parts[i].keys.Split(' ');
                for (int k = 0; k < keys.Length; k++)
                {
                    if (keys[k].Length == 0) continue;
                    var cap = Ui.Kbd(keys[k]);
                    if (k > 0) cap.AddToClassList("ov-kbd-next");
                    row.Add(cap);
                }
                row.Add(Ui.Text(parts[i].text, "ov-coach-text"));
            }
            return row;
        }

        static void NoPick(VisualElement e)
        {
            e.pickingMode = PickingMode.Ignore;
            for (int i = 0; i < e.hierarchy.childCount; i++) NoPick(e.hierarchy[i]);
        }
    }
}
