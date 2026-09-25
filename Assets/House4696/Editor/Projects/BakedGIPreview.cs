using System.Collections;
using System.Linq;
using House4696.Core;
using House4696.Lighting;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Projects
{
    /// <summary>
    /// Edit-mode check of the runtime GI baker on the scene built by <see cref="ProjectPreview"/>: bakes the probe
    /// volume exactly as the app does (<see cref="HouseLightBake"/>), activates it and switches Surface Cache GI off, so
    /// RenderJob renders compare the two. Progress and completion go to the console as "[BakedGI]" lines.
    /// </summary>
    public static class BakedGIPreview
    {
        static IEnumerator _job;

        public static bool Busy => _job != null;

        [MenuItem("House 46-96/Projects/Bake GI of the preview (runtime baker)", priority = 62)]
        public static void BakeMenu() => Debug.Log(Start());

        public static string Start(ProbeBakeSettings settings = null)
        {
            if (Busy) return "[BakedGI] a bake is already running";
            var last = ProjectPreview.Last;
            if (last == null || last.House == null) return "[BakedGI] build a project preview first";
            var content = HouseContent.Load();
            float lastReport = -1f;
            _job = HouseLightBake.Bake(content.BakedGI, last.House, last.Site, settings,
                v =>
                {
                    BakedGIVolume.Active?.Dispose();
                    BakedGIVolume.Active = v;
                    SetSurfaceCache(content, false);
                    Debug.Log($"[BakedGI] done: {v.Size.x}×{v.Size.y}×{v.Size.z} probes ({v.ProbeCount}), spacing {v.Spacing:0.00} m, {v.BakeSeconds:0.0} s — {v.Stats}");
                },
                e => Debug.LogError("[BakedGI] failed: " + e),
                null,
                p => { if (p - lastReport >= 0.25f || p >= 1f) { lastReport = p; Debug.Log($"[BakedGI] {p:P0}"); } });
            EditorApplication.update += Tick;
            return "[BakedGI] started";
        }

        [MenuItem("House 46-96/Projects/Clear baked GI (back to Surface Cache)", priority = 63)]
        public static void Clear()
        {
            BakedGIVolume.Active?.Dispose();
            BakedGIVolume.Active = null;
            SetSurfaceCache(HouseContent.Load(), true);
        }

        public static void SetSurfaceCache(HouseContent content, bool on)
        {
            if (content.RealtimeGIProfile != null && content.RealtimeGIProfile.TryGet(out SurfaceCacheGIVolumeOverride gi))
                gi.enabled.Override(on);
        }

        static void Tick()
        {
            if (_job == null) { EditorApplication.update -= Tick; return; }
            bool more;
            try { more = _job.MoveNext(); }
            catch (System.Exception e) { Debug.LogException(e); more = false; }
            if (!more)
            {
                _job = null;
                EditorApplication.update -= Tick;
            }
            SceneView.RepaintAll();
        }
    }
}
