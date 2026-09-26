using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Project previews for the project list: once the lighting of the open house is ready and its reflection probes
    /// are captured (HouseBootstrap calls <see cref="Capture"/> when <see cref="ReflectionCapture"/> is done), a small exterior view is rendered
    /// to <c>thumb.jpg</c> in the project folder. Loaded pictures are cached per file time.
    /// </summary>
    public sealed class Thumbnails
    {
        public const int Width = 640, Height = 400;

        readonly HouseSession _session;
        readonly ViewRenderer _renderer;
        readonly MonoBehaviour _host;
        readonly Dictionary<string, (DateTime time, Texture2D tex)> _cache = new Dictionary<string, (DateTime, Texture2D)>();
        int _generation;

        /// <summary>Raised with the project id after its preview was written.</summary>
        public event Action<string> Updated;

        public Thumbnails(HouseSession session, ViewRenderer renderer, MonoBehaviour host)
        {
            _session = session; _renderer = renderer; _host = host;
        }

        /// <summary>Renders the preview of the open project (a newer request supersedes a pending one).</summary>
        public void Capture(float delaySeconds = 0f)
        {
            if (!_session.HasProject) return;
            _host.StartCoroutine(CaptureRoutine(++_generation, _session.ProjectId, delaySeconds));
        }

        IEnumerator CaptureRoutine(int generation, string id, float delay)
        {
            if (delay > 0f) yield return new WaitForSecondsRealtime(delay);
            if (generation != _generation || id != _session.ProjectId || _session.Result == null) yield break;
            var q = new RenderRequest { Width = Width, Height = Height, Jpeg = true, Yaw = 32f, Pitch = 14f, Fov = 50f };
            var orbit = _session.Result.Orbit;
            if (orbit != null && orbit.Length > 0)
            {
                q.Yaw = orbit[0].Yaw; q.Pitch = orbit[0].Pitch; q.Distance = orbit[0].Distance;
            }
            byte[] jpg = null;
            yield return _renderer.Render(q, bytes => jpg = bytes, err => Debug.LogWarning("[Thumbnails] " + err));
            if (jpg == null || id != _session.ProjectId || !_session.Store.Exists(id)) yield break;
            try
            {
                File.WriteAllBytes(_session.Store.ThumbPath(id), jpg);
                Updated?.Invoke(id);
            }
            catch (Exception e) { Debug.LogWarning("[Thumbnails] " + e.Message); }
        }

        /// <summary>The preview of a project, or null when it has none yet.</summary>
        public Texture2D Get(string id)
        {
            string path = _session.Store.ThumbPath(id);
            if (!File.Exists(path)) return null;
            var time = File.GetLastWriteTimeUtc(path);
            if (_cache.TryGetValue(id, out var hit) && hit.time == time && hit.tex != null) return hit.tex;
            if (hit.tex != null) UnityEngine.Object.Destroy(hit.tex);
            var tex = new Texture2D(2, 2, TextureFormat.RGB24, false) { name = "thumb_" + id, wrapMode = TextureWrapMode.Clamp };
            try
            {
                if (!tex.LoadImage(File.ReadAllBytes(path), true)) { UnityEngine.Object.Destroy(tex); return null; }
            }
            catch (Exception) { UnityEngine.Object.Destroy(tex); return null; }
            _cache[id] = (time, tex);
            return tex;
        }
    }
}
