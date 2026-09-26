using System;
using System.Collections.Generic;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Frame pacing and heat. While the window has focus the viewer runs at the focused policy (uncapped, VSync off:
    /// on the 60 Hz panel VSync would alternate 16.7 / 33.3 ms frames as long as a frame takes ~26 ms). In the
    /// background — the user works in their AI client — the app drops to <see cref="UnfocusedFrameRate"/> so the
    /// fanless MacBook Air stays cool and does not throttle, except while something needs full speed: an API call
    /// (until its result is set, and a short grace after it: an AI sends calls in bursts), a GI bake, a still render,
    /// a reflection capture or a diagnostics run. Player only: in the editor Game-view focus means nothing and quality
    /// changes would stick.
    /// </summary>
    public sealed class FramePacing
    {
        // ---- tuning / A-B / rollback -------------------------------------------------------------------------
        /// <summary>Throttle while the window is not focused (false = the old behaviour: always uncapped).</summary>
        public static bool ThrottleWhenUnfocused = true;
        /// <summary>Frame cap while throttled.</summary>
        public static int UnfocusedFrameRate = 30;
        /// <summary>Full speed for this long after the last API call was answered.</summary>
        public static float ApiGraceSeconds = 3f;
        /// <summary>
        /// A tracked API call whose result is never set stops holding full speed after this long (a handler bug must
        /// not disable the throttle for the rest of the session). Longer than any bench or sweep.
        /// </summary>
        public static float CallMaxSeconds = 900f;
        /// <summary>
        /// VSync while focused, applied once at start (player only): 0 = off, as the PC quality level has it today.
        /// Switch to 1 (60 FPS on this panel) only once the p95 frame is below ~15 ms. -1 = leave the quality level.
        /// </summary>
        public static int FocusedVSyncCount = 0;
        /// <summary>
        /// Frame cap while focused, applied once at start: 0 = the display's refresh rate (60 on the Air, 120 with
        /// ProMotion), -1 = none; ignored while VSync is on. Frames beyond the panel's rate were never shown and only
        /// heated the fanless MacBook Air (the house views ran at 80–110 FPS), which then throttled by 40–50 % in the
        /// heavy views; unlike VSync the cap does not quantise slower frames to 33 ms.
        /// </summary>
        public static int FocusedFrameRate = 0;

        /// <summary>The frame cap <see cref="FocusedFrameRate"/> stands for.</summary>
        public static int FocusedCap()
        {
            if (FocusedFrameRate != 0) return FocusedFrameRate;
            double hz = Screen.currentResolution.refreshRateRatio.value;
            return hz >= 30 ? (int)Math.Round(hz) : 60;
        }
        /// <summary>
        /// Diagnostics may set this while they measure: never throttle meanwhile. PerfProbe sweep / bench / measure
        /// run as API calls, which <see cref="Track"/> already covers until their result is set (also past the API's
        /// 180 s reply timeout), so this is only for runs started some other way.
        /// </summary>
        public static bool DiagnosticsRunning;

        /// <summary>True while the background frame cap is applied.</summary>
        public bool Throttled { get; private set; }

        int _savedVSync, _savedFrameRate;
        readonly List<(LocalApi.Call call, float since)> _calls = new List<(LocalApi.Call, float)>();

        /// <summary>Applies the focused policy (call once at start).</summary>
        public void ApplyFocusedPolicy()
        {
            if (Application.isEditor) return;
            if (FocusedVSyncCount >= 0) QualitySettings.vSyncCount = FocusedVSyncCount;
            Application.targetFrameRate = FocusedCap();
        }

        /// <summary>
        /// An API call is being executed: hold full speed until its result is set. <see cref="LocalApi.InFlight"/>
        /// drops when the HTTP reply times out (180 s), a long bench keeps running after that.
        /// </summary>
        public void Track(LocalApi.Call call)
        {
            if (call != null) _calls.Add((call, Time.realtimeSinceStartup));
        }

        /// <summary>Once per frame: throttles in the background when nothing needs full speed, restores otherwise.</summary>
        public void Tick(LocalApi api, HouseLighting lighting)
        {
            bool callsRunning = PruneCalls();
            bool throttle = ThrottleWhenUnfocused && !Application.isEditor && !Application.isFocused
                            && !callsRunning && !NeedsFullSpeed(api, lighting);
            if (throttle == Throttled) return;
            Throttled = throttle;
            if (throttle)
            {
                // keep whatever is live now (diagnostics may have tuned it) and bring it back on focus
                _savedVSync = QualitySettings.vSyncCount;
                _savedFrameRate = Application.targetFrameRate;
                QualitySettings.vSyncCount = 0;                 // targetFrameRate is ignored while VSync is on
                Application.targetFrameRate = Mathf.Max(1, UnfocusedFrameRate);
            }
            else
            {
                QualitySettings.vSyncCount = _savedVSync;
                Application.targetFrameRate = _savedFrameRate;
            }
        }

        /// <summary>Drops finished (or hopelessly old) calls; true while any tracked call still runs.</summary>
        bool PruneCalls()
        {
            float now = Time.realtimeSinceStartup;
            for (int i = _calls.Count - 1; i >= 0; i--)
            {
                var c = _calls[i];
                if (c.call.Done.Task.IsCompleted || now - c.since > CallMaxSeconds) _calls.RemoveAt(i);
            }
            return _calls.Count > 0;
        }

        static bool NeedsFullSpeed(LocalApi api, HouseLighting lighting)
        {
            if (DiagnosticsRunning || HouseBootstrap.PinRenderScale) return true;   // pinned = someone is measuring
            if (ViewRenderer.Busy || ReflectionCapture.Busy) return true;
            if (lighting != null && lighting.IsBaking) return true;
            if (api != null)
            {
                if (api.InFlight > 0) return true;
                if ((DateTime.UtcNow - api.LastFinishedUtc).TotalSeconds < ApiGraceSeconds) return true;
            }
            return false;
        }
    }
}
