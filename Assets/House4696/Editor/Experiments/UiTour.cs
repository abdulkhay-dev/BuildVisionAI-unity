using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using House4696.App.UI;
using House4696.Runtime;
using UnityEditor;
using UnityEngine;

namespace House4696.Experiments
{
    /// <summary>
    /// Screenshot tour of the app UI in Play mode: puts the interface into a list of states (viewer modes, popovers,
    /// dialogs, Home, plan…) and saves a PNG of each (camera + UI) to Renders/ui2/. Driven by EditorApplication.update,
    /// so one call starts it; it logs "[UiTour] done" at the end.
    /// </summary>
    public static class UiTour
    {
        static IEnumerator _run;
        static double _until;
        static int _untilFrame = -1;

        public static string Start(string outDir, string only = null)
        {
            if (!EditorApplication.isPlaying) return "enter play mode first";
            var ui = UnityEngine.Object.FindAnyObjectByType<AppUI>();
            if (ui == null || ui.S == null) return "app not ready";
            _run = Tour(ui, outDir, only);
            EditorApplication.update -= Step;
            EditorApplication.update += Step;
            return "started";
        }

        static void Step()
        {
            if (!EditorApplication.isPlaying || _run == null) { EditorApplication.update -= Step; return; }
            if (EditorApplication.timeSinceStartup < _until) return;
            if (_untilFrame >= 0 && Time.frameCount < _untilFrame) return;
            _untilFrame = -1;
            try
            {
                if (!_run.MoveNext()) { _run = null; EditorApplication.update -= Step; Debug.Log("[UiTour] done"); return; }
                // yield return N = N/60 s of real time (editor ticks run faster than game frames in the background)
                if (_run.Current is string s && s == "frame") { _untilFrame = Time.frameCount + 1; _until = 0; }
                else _until = EditorApplication.timeSinceStartup + (_run.Current is int n ? n : 1) / 60.0;
            }
            catch (Exception e)
            {
                Debug.LogException(e);
                _run = null;
                EditorApplication.update -= Step;
                Debug.Log("[UiTour] done (error)");
            }
        }

        /// <summary>Waits: yield return N = N/60 s.</summary>
        static IEnumerator Tour(AppUI ui, string dir, string only)
        {
            Directory.CreateDirectory(dir);
            var states = new List<(string name, Action<AppUI> set, int settle)>
            {
                ("01-orbit", u => { Reset(u); u.SwitchMode(HouseViewer.Mode.Orbit); u.GoToView(HouseViewer.Mode.Orbit, 0); }, 120),
                ("02-orbit-views", u => { Reset(u); u.Toolbar.ToggleViews(); }, 30),
                ("03-settings", u => { Reset(u); u.StatusPill.ToggleSettings(); }, 30),
                ("04-ai-popover", u => { Reset(u); u.StatusPill.ToggleAi(); }, 30),
                ("05-walk-plan", u => { Reset(u); u.SwitchMode(HouseViewer.Mode.Walk); GoToFirstRoom(u); }, 140),
                ("06-large-plan", u => { Reset(u); u.Plan.ToggleLarge(); }, 40),
                ("07-clean", u => { Reset(u); u.SetCleanView(true); }, 40),
                ("08-toast-ai", ToastDemo, 30),
                ("09-home", u => { Reset(u); u.ShowHome(); }, 50),
                ("10-new-project", u => { Reset(u); u.ShowHome(); u.ShowNewProject(); }, 40),
                ("11-connect-ai", u => { Reset(u); u.ShowConnectAi(); }, 40),
                ("12-shortcuts", u => { Reset(u); u.ShowShortcuts(); }, 40),
                ("13-delete", u => { Reset(u); u.ConfirmDelete("barnhouse"); }, 40),
                ("14-veil", u => { Reset(u); u.Veil.ShowOpening("barnhouse", "Барнхаус 120"); }, 40),
            };
            foreach (var st in states)
            {
                if (only != null && !st.name.Contains(only)) continue;
                try { st.set(ui); }
                catch (Exception e) { Debug.LogWarning($"[UiTour] {st.name}: {e.Message}"); }
                yield return st.settle;
                UiShot.Begin(Path.Combine(dir, st.name + ".png"));
                yield return "frame";    // exactly one panel draw over the camera image (more would stack the shadows)
                UiShot.End();
                Debug.Log($"[UiTour] {st.name}");
            }
            try { Reset(ui); } catch (Exception) { }
        }

        static void ToastDemo(AppUI u)
        {
            Reset(u);
            Action none = () => { };
            u.Toast("ИИ построил наружные стены", House4696.App.UI.IconKind.Sparkle, ToastKind.Ai, "Отменить последнюю", none);
        }

        static void GoToFirstRoom(AppUI u)
        {
            foreach (var plan in u.Plans)
                foreach (var r in plan.Rooms)
                    if (r.Type == House4696.Model.RoomType.Living) { u.GoToRoom(plan, r); return; }
            if (u.Plans.Count > 0 && u.Plans[0].Rooms.Count > 0) u.GoToRoom(u.Plans[0], u.Plans[0].Rooms[0]);
        }

        /// <summary>Closes popovers, dialogs, the large plan, clean view, Home and the veil.</summary>
        public static void Reset(AppUI u)
        {
            u.ClosePopover();
            var f = typeof(AppUI).GetField("_modals", BindingFlags.NonPublic | BindingFlags.Instance);
            if (f?.GetValue(u) is IList list)
                while (list.Count > 0) u.CloseModal((Modal)list[list.Count - 1]);
            if (u.Plan.LargeOpen) u.Plan.CloseLarge();
            u.SetCleanView(false);
            if (u.HomeOpen) u.CloseHome();
            if (u.VeilVisible) u.Veil.Hide();
        }
    }
}
