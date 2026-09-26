using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Top-right status pill (spec §3.2): one surface with segments separated by 1×20 dividers —
    /// light (only while baking, for 1.5 s after it is ready, and while it has failed; its width collapses to 0),
    /// AI (four states: connect CTA, connected, online, working with a verb phrase) and the settings gear.
    /// Both popovers hang from the pill's surface, not from the item: right edge at W − 16, 8 px below the pill.
    /// Styles: Resources/UI/Chrome.uss (sp-*).
    /// </summary>
    public sealed class StatusPill
    {
        const float ReadyHold = 1.5f, TextEvery = 0.25f, SampleEvery = 0.5f, AiTipEvery = 2f;
        /// <summary>Same copy as the AI popover's hint in this state.</summary>
        const string WaitingHint = "ИИ-ассистент настроен. Напишите ему — он найдёт House сам.";

        enum LightShown { None, Baking, Ready, Failed }

        /// <summary>"0 %" … "99 %", built once (no per-frame strings).</summary>
        static readonly string[] PctText = new string[100];

        readonly AppUI _ui;
        public VisualElement Element { get; }

        readonly VisualElement _light, _ai, _gear;
        readonly SurfaceAnchor _aiPop, _settingsPop;
        readonly ProgressRing _ring;
        readonly Icon _lightIcon, _aiIcon;
        readonly Label _lightLabel, _lightPct, _aiLabel;
        readonly PulseDot _aiDot;
        readonly ChromeMorph _lightMorph;

        LightShown _shown;
        float _readyUntil, _nextText, _nextSample, _bakeT0, _bakeP0, _eta = -1f, _nextAiTip;
        int _pct = -1, _samples, _etaShown = -1;
        string _lightTip, _aiTip, _aiSub, _aiText;
        AiState _aiState;
        bool _aiInit;

        public StatusPill(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("sp-root");
            Element.pickingMode = PickingMode.Ignore;

            // light: ring / check / warning + label; its divider sits inside the collapsing part
            _ring = new ProgressRing();
            _lightIcon = Ui.Icon(IconKind.Check, 16);
            _lightLabel = Ui.Text("Свет", "sp-light-label t-ui sp-fade");
            _lightPct = Ui.Text("", "sp-light-pct t-ui");
            _light = Ui.El("sp-light", _ring, _lightIcon, _lightLabel, _lightPct);
            Ui.OnClick(_light, OnLightClick);
            Tooltips.Tip(_light, "Рассчитываем освещение");
            var lightIn = Ui.El("sp-light-in", _light, Ui.DividerV());
            lightIn.pickingMode = PickingMode.Ignore;
            var lightClip = Ui.El("sp-light-clip", lightIn);
            lightClip.pickingMode = PickingMode.Ignore;
            _lightMorph = new ChromeMorph(lightClip, lightIn, false);

            // AI: the segment itself clips and animates its width when the label changes
            _aiIcon = Ui.Icon(IconKind.Sparkle, 16);
            _aiDot = new PulseDot();
            _aiLabel = Ui.Text("", "sp-ai-label t-ui sp-fade");
            var aiIn = Ui.El("sp-ai-in", _aiIcon, _aiDot, _aiLabel);
            aiIn.pickingMode = PickingMode.Ignore;
            _ai = Ui.El("sp-ai", aiIn);
            Ui.OnClick(_ai, ToggleAi);
            _ = new ChromeMorph(_ai, aiIn, true);      // lives on through its geometry callback

            // settings
            _gear = Ui.Tool(IconKind.Sliders, null, ToggleSettings, "Настройки", "⌘ ,");
            _gear.AddToClassList("sp-gear");

            var pill = Ui.El("sp-pill", lightClip, _ai, Ui.DividerV(), _gear);
            Element.Add(Elevation.Wrap(pill, 12, 16, 4f, 0.45f));

            // popovers anchor to the surface (Element has exactly the pill's bounds); the items keep the pressed look
            _aiPop = new SurfaceAnchor(_ui, Element, _ai);
            _settingsPop = new SurfaceAnchor(_ui, Element, _gear);

            if (_ui.Ai != null) _ui.Ai.Changed += UpdateAi;
            UpdateAi();
            UpdateLight();
        }

        // ------------------------------------------------------------------ public
        public void Refresh()
        {
            UpdateAi();
            UpdateLight();
        }

        public void Tick()
        {
            _aiPop.Tick();
            _settingsPop.Tick();
            UpdateLight();
            // «Последний запрос: 2 мин назад» ages; the waiting / connect tooltips are fixed
            if (Time.unscaledTime >= _nextAiTip && (_aiState == AiState.Online || _aiState == AiState.Working)) UpdateAiTip();
        }

        /// <summary>Opens/closes the settings popover under the gear (⌘,).</summary>
        public void ToggleSettings() => TogglePop(_settingsPop, () => SettingsPopover.Build(_ui), 320f);

        /// <summary>Opens/closes the AI popover (or the Connect AI dialog when not connected).</summary>
        public void ToggleAi()
        {
            if (_ui.S == null || _ui.Ai == null) return;
            if (_ui.Ai.State == AiState.NotConnected)
            {
                _ui.ShowConnectAi();
                return;
            }
            TogglePop(_aiPop, () => AiPopover.Build(_ui), 340f);
        }

        /// <summary>Both popovers are right-aligned to the pill (W − 16), 8 px below it.</summary>
        void TogglePop(SurfaceAnchor pop, Func<VisualElement> build, float width)
        {
            if (pop.IsOpen) { pop.Close(); return; }
            if (_ui.HomeOpen || _ui.VeilVisible || _ui.S?.Session?.HasProject != true) return;
            if (_ui.CleanView)
            {
                // a popover never floats over hidden chrome: bring the chrome back, open once it is laid out
                _ui.SetCleanView(false);
                pop.Proxy.schedule.Execute(() =>
                {
                    if (!_ui.CleanView && !pop.IsOpen) pop.Toggle(build, width, PopPlacement.BelowRight);
                }).ExecuteLater(40);
                return;
            }
            pop.Toggle(build, width, PopPlacement.BelowRight);
        }

        // ------------------------------------------------------------------ AI segment
        void UpdateAi()
        {
            var ai = _ui.Ai;
            if (ai == null) return;
            var st = ai.State;
            if (!_aiInit || st != _aiState)
            {
                _aiInit = true;
                _aiState = st;
                bool connect = st == AiState.NotConnected;
                _ai.EnableInClassList("sp-ai-connect", connect);
                Ui.Show(_aiIcon, connect);
                Ui.Show(_aiDot, !connect);
                _aiDot.SetStyle(AiDotStyle(st), st == AiState.Working);
                if (connect) _aiPop.Close();
            }
            string label = AiLabel(ai);
            if (label != _aiText)
            {
                bool fade = _aiText != null;
                _aiText = label;
                ChromeMorph.SwapText(_aiLabel, label, fade);
            }
            UpdateAiTip();
        }

        void UpdateAiTip()
        {
            _nextAiTip = Time.unscaledTime + AiTipEvery;
            string text, sub = null;
            switch (_aiState)
            {
                case AiState.NotConnected:
                    text = "Подключите ИИ-ассистента";
                    sub = "Claude, Cursor или другой клиент";
                    break;
                case AiState.Waiting:
                    text = WaitingHint;
                    break;
                default:
                    text = _ui.Ai.LastCallText;
                    break;
            }
            if (text == _aiTip && sub == _aiSub) return;
            _aiTip = text;
            _aiSub = sub;
            Tooltips.Tip(_ai, text, null, sub);
        }

        // The AI state's wording and dot, the same wherever the state is shown (Home pill, AI popover, empty-site card,
        // Connect AI footer): kept here until AiStatus carries them (Label / DotStyle).

        /// <summary>«Подключить ИИ» (a call to action) · «ИИ подключён» (ready, not used yet) · «ИИ на связи» · verb phrase.</summary>
        static string AiLabel(AiStatus ai) => ai.State switch
        {
            AiState.NotConnected => "Подключить ИИ",
            AiState.Waiting => "ИИ подключён",
            AiState.Online => "ИИ на связи",
            _ => string.IsNullOrEmpty(ai.Phrase) ? "ИИ работает" : ai.Phrase,
        };

        /// <summary>Waiting: an 8 px success ring (ready but unused); online: a filled success dot; working: the ai dot (pulsing).</summary>
        static string AiDotStyle(AiState state) => state switch
        {
            AiState.Waiting => "dot-ring",
            AiState.Online => "dot-success",
            AiState.Working => "dot-ai",
            _ => null,
        };

        // ------------------------------------------------------------------ light segment
        void UpdateLight()
        {
            var s = _ui.S;
            var lighting = s?.Lighting;
            var state = lighting != null && s.Session != null && s.Session.HasProject ? lighting.Current : HouseLighting.State.Idle;
            float now = Time.unscaledTime;
            switch (state)
            {
                case HouseLighting.State.Baking:
                    if (_shown != LightShown.Baking) EnterBaking(lighting.Progress, now);
                    _ring.Value = lighting.Progress;
                    if (now >= _nextText) UpdateBaking(lighting.Progress, now);
                    break;
                case HouseLighting.State.Ready:
                    if (_shown == LightShown.Baking)
                    {
                        if (_ui.VeilVisible) HideLight(false);        // the veil already showed the progress: no flash behind it
                        else EnterReady(lighting, now);
                    }
                    else if (_shown == LightShown.Ready && now >= _readyUntil) HideLight(true);
                    else if (_shown == LightShown.Failed) HideLight(true);
                    break;
                case HouseLighting.State.Failed:
                    if (_shown != LightShown.Failed) EnterFailed();
                    break;
                default:
                    if (_shown != LightShown.None) HideLight(true);
                    break;
            }
        }

        void EnterBaking(float progress, float now)
        {
            bool swap = _shown != LightShown.None;
            _shown = LightShown.Baking;
            _ring.Snap(progress);
            Ui.Show(_ring, true);
            Ui.Show(_lightIcon, false);
            Ui.Show(_lightPct, true);
            _light.RemoveFromClassList("sp-clickable");
            ChromeMorph.SwapText(_lightLabel, "Свет", swap);
            _bakeT0 = now;
            _bakeP0 = progress;
            _samples = 0;
            _eta = -1f;
            _etaShown = -1;
            _pct = -1;
            _lightTip = null;
            _nextSample = now + SampleEvery;
            UpdateBaking(progress, now);
            _lightMorph.Set(true, !_ui.VeilVisible);
        }

        /// <summary>«Свет 53 %» and the ETA tooltip (from the progress slope, shown after two samples); 4×/s.</summary>
        void UpdateBaking(float progress, float now)
        {
            _nextText = now + TextEvery;
            int pct = Mathf.Clamp(Mathf.FloorToInt(progress * 100f), 0, 99);
            if (pct != _pct)
            {
                _pct = pct;
                _lightPct.text = PctText[pct] ??= pct + " %";
            }

            if (now >= _nextSample)
            {
                _nextSample = now + SampleEvery;
                float dt = now - _bakeT0, dp = progress - _bakeP0;
                if (dt > 0.2f && dp > 0.002f)
                {
                    _samples++;
                    float eta = (1f - progress) * dt / dp;
                    _eta = _eta < 0f ? eta : Mathf.Lerp(_eta, eta, 0.5f);
                }
            }

            int secs = _samples >= 2 && _eta >= 0f ? Mathf.Max(1, Mathf.CeilToInt(_eta)) : 0;
            if (secs == _etaShown && _lightTip != null) return;
            _etaShown = secs;
            string etaText = secs < 60 ? "~" + secs + " с" : "~" + Mathf.CeilToInt(secs / 60f) + " мин";
            SetLightTip(secs == 0
                ? "Рассчитываем освещение — картинка скоро уточнится"
                : "Рассчитываем освещение — картинка уточнится через " + etaText);
        }

        void EnterReady(HouseLighting lighting, float now)
        {
            _shown = LightShown.Ready;
            _readyUntil = now + ReadyHold;
            Ui.Show(_ring, false);
            SetLightIcon(IconKind.Check, "c-success");
            Ui.Show(_lightPct, false);
            _light.RemoveFromClassList("sp-clickable");
            ChromeMorph.SwapText(_lightLabel, "Свет готов", true);
            var volume = lighting.Volume;
            SetLightTip(volume != null && volume.BakeSeconds > 0f
                ? "Освещение рассчитано за " + Ui.Number(volume.BakeSeconds) + " с"
                : "Освещение рассчитано");
            _lightMorph.Set(true);
        }

        void EnterFailed()
        {
            bool swap = _shown != LightShown.None;
            _shown = LightShown.Failed;
            Ui.Show(_ring, false);
            SetLightIcon(IconKind.Warning, "c-warning");
            Ui.Show(_lightPct, false);
            _light.AddToClassList("sp-clickable");
            ChromeMorph.SwapText(_lightLabel, "Упрощённый свет", swap);
            SetLightTip("Не удалось рассчитать освещение. Щёлкните, чтобы повторить.");
            _lightMorph.Set(true, !_ui.VeilVisible);
        }

        void HideLight(bool animate)
        {
            _shown = LightShown.None;
            _light.RemoveFromClassList("sp-clickable");
            if (_lightMorph.IsOpen && _light.worldBound.Contains(_ui.PointerPanelPosition())) Tooltips.HideNow();
            _lightMorph.Set(false, animate && !_ui.VeilVisible);
        }

        void SetLightIcon(IconKind kind, string colour)
        {
            _lightIcon.Kind = kind;
            _lightIcon.EnableInClassList("c-success", colour == "c-success");
            _lightIcon.EnableInClassList("c-warning", colour == "c-warning");
            Ui.Show(_lightIcon, true);
        }

        void SetLightTip(string text)
        {
            if (text == _lightTip) return;
            _lightTip = text;
            Tooltips.Tip(_light, text);
        }

        void OnLightClick()
        {
            if (_shown == LightShown.Failed) _ui.RetryLighting();
        }
    }
}
