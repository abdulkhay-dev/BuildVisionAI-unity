using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Experiments
{
    /// <summary>
    /// Renders the views of a generated house in the background, a few frames per editor tick, so no single call blocks the editor
    /// (long synchronous render bursts time out the MCP bridge, whose retries re-run them). Realtime GI converges
    /// over <c>frames</c> renders per view; progress and completion go to the console as "[RenderJob]" lines.
    /// </summary>
    public static class RenderJob
    {
        const int FramesPerTick = 3;
        struct View { public string Name; public Vector3 Pos; public Quaternion Rot; public float Fov; }
        static Queue<View> _stops;
        static View _view;
        static string _tag, _dir;
        static int _frames, _frame, _width, _height, _current = -1;
        static Camera _cam;
        static RenderTexture _rt;
        static System.Diagnostics.Stopwatch _sw;

        public static bool Busy => _stops != null;

        /// <summary>Renders the walk stops and orbit presets of a generated house (names 00.., o00..).</summary>
        public static string StartViews(string tag, House4696.Generation.HouseBuildResult r, int frames, int width = 1280, int height = 800)
        {
            var views = new List<View>();
            for (int i = 0; i < r.Walk.Length; i++)
                views.Add(new View { Name = i.ToString("00"), Pos = r.Walk[i].Feet + Vector3.up * 1.66f, Rot = Quaternion.Euler(r.Walk[i].Pitch, r.Walk[i].Yaw, 0f), Fov = 70f });
            for (int i = 0; i < r.Orbit.Length; i++)
            {
                var o = r.Orbit[i];
                var rot = Quaternion.Euler(o.Pitch, o.Yaw, 0f);
                views.Add(new View { Name = "o" + i.ToString("00"), Pos = r.Pivot + rot * new Vector3(0, 0, -o.Distance), Rot = rot, Fov = 45f });
            }
            return Run(tag, views, frames, width, height);
        }

        static string Run(string tag, List<View> views, int frames, int width, int height)
        {
            if (Busy) return "[RenderJob] busy with " + _tag;
            _stops = new Queue<View>(views);
            _tag = tag; _frames = frames; _width = width; _height = height;
            _dir = Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? "", "Renders", "gi");
            Directory.CreateDirectory(_dir);

            var main = Camera.main;
            var go = new GameObject("RenderJobCamera") { hideFlags = HideFlags.HideAndDontSave };
            _cam = go.AddComponent<Camera>();
            if (main != null) _cam.CopyFrom(main);
            var data = _cam.GetUniversalAdditionalCameraData();
            if (main != null) data.SetRenderer(RendererIndex(main));
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            _cam.usePhysicalProperties = false;
            _cam.lensShift = Vector2.zero;
            _cam.nearClipPlane = 0.05f;
            _rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            _cam.targetTexture = _rt;
            _current = -1;
            _sw = System.Diagnostics.Stopwatch.StartNew();
            int count = _stops.Count;
            EditorApplication.update += Tick;
            return $"[RenderJob] started {tag}: {count} views × {frames} frames";
        }

        static void Tick()
        {
            if (_stops == null) return;
            try
            {
                if (_current < 0)
                {
                    if (_stops.Count == 0) { Finish(); return; }
                    _view = _stops.Dequeue();
                    _current = 0;
                    _cam.transform.SetPositionAndRotation(_view.Pos, _view.Rot);
                    _cam.fieldOfView = _view.Fov;
                    _frame = 0;
                }
                for (int i = 0; i < FramesPerTick && _frame < _frames; i++, _frame++) _cam.Render();
                AsyncGPUReadback.Request(_rt, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                if (_frame < _frames) return;

                var prev = RenderTexture.active;
                RenderTexture.active = _rt;
                var tex = new Texture2D(_width, _height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, _width, _height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                File.WriteAllBytes(Path.Combine(_dir, $"{_view.Name}_{_tag}.png"), tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
                Debug.Log($"[RenderJob] {_tag} view {_view.Name} done at {_sw.ElapsedMilliseconds} ms");
                _current = -1;
            }
            catch (System.Exception e)
            {
                Debug.LogError("[RenderJob] failed: " + e);
                Finish();
            }
        }

        static void Finish()
        {
            EditorApplication.update -= Tick;
            Debug.Log($"[RenderJob] {_tag} finished in {_sw.ElapsedMilliseconds} ms");
            if (_cam != null) { _cam.targetTexture = null; Object.DestroyImmediate(_cam.gameObject); }
            if (_rt != null) { _rt.Release(); Object.DestroyImmediate(_rt); }
            _stops = null;
        }

        static int RendererIndex(Camera cam)
        {
            var f = typeof(UniversalAdditionalCameraData).GetField("m_RendererIndex",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            int idx = f != null ? (int)f.GetValue(cam.GetUniversalAdditionalCameraData()) : -1;
            return idx < 0 ? 0 : idx;
        }
    }
}
