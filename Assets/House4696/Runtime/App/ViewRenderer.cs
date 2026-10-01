using System;
using System.Collections;
using System.Collections.Generic;
using House4696.Core;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace House4696.App
{
    public enum RenderMode { Orbit, Walk, Plan, Current, Site }

    /// <summary>What to render: an orbit angle around the house, a standing point inside, a floor plan from above, or the viewer's current view (snapshots).</summary>
    public sealed class RenderRequest
    {
        public RenderMode Mode = RenderMode.Orbit;
        public float Yaw = 30f, Pitch = 12f, Distance;          // orbit: distance 0 = fit the house
        public Vector3 Position;                                 // walk: feet position (absolute)
        public string Level;                                     // plan: which level (default: lowest)
        public int Width = 1280, Height = 800;
        public float Fov = 60f;
        public int Frames = 48;                                  // realtime GI accumulation
        public bool Jpeg;                                        // JPG (thumbnails) instead of PNG
    }

    /// <summary>
    /// Renders views of the current house into PNGs for the AI (so it can see what it built). Perspective views go
    /// through the GI renderer: with baked lighting a few frames suffice, with the realtime fallback they accumulate
    /// a few dozen frames, a few per app frame with GPU syncs so neither the app nor the GPU queue stalls. Plans are orthographic from above, without GI, with everything
    /// above the cut height (ceilings, upper floors, roofs) hidden.
    /// <para>Stills render like the live view but at full resolution: an HDR target (lighting above 1 reaches the
    /// tonemapper, bloom fires) with MSAA (foliage alpha-to-coverage, thin edges) plus SMAA, at render scale 1 without
    /// an upscaler — set for the still camera's own frames only, the viewer keeps its scale in between. The result is
    /// resolved into an 8-bit sRGB copy for the PNG.</para>
    /// </summary>
    public sealed class ViewRenderer
    {
        const int FramesPerTick = 3;

        // ---- tuning / A-B / rollback -------------------------------------------------------------------------
        /// <summary>Half-float target like the live view (false = the old 8-bit sRGB target: clipped highlights, no bloom).</summary>
        public static bool HdrStills = true;
        /// <summary>MSAA samples for stills up to <see cref="MsaaLargePixels"/> (1 = off, the old behaviour).</summary>
        public static int StillMsaa = 4;
        /// <summary>MSAA samples for larger stills (4K snapshots) — memory: each MSAA colour/depth buffer is ~150 MB at 4K ×2.</summary>
        public static int StillMsaaLarge = 2;
        public static int MsaaLargePixels = 2048 * 2048;
        /// <summary>Above this pixel count stills get no MSAA.</summary>
        public static int MsaaMaxPixels = 4096 * 2560;
        /// <summary>Scale 1 + Auto filter around each still frame only (false = the old way: scale 1 for the whole render).</summary>
        public static bool NativeScaleStills = true;
        /// <summary>Longest wait for a running reflection capture before a perspective still renders.</summary>
        public static float ProbeWaitSeconds = 8f;

        static bool s_busy;
        static float s_busySince;

        /// <summary>True while a still renders (the viewer's automatic render scale holds meanwhile).</summary>
        public static bool Busy => s_busy && Time.realtimeSinceStartup - s_busySince < 60f;

        readonly HouseSession _session;
        readonly int _giRenderer;

        public ViewRenderer(HouseSession session, int giRendererIndex)
        {
            _session = session; _giRenderer = giRendererIndex;
        }

        bool _busy;
        float _busySince;

        /// <summary>
        /// Renders one view; requests are serialised (two renders would fight over the viewer camera). A render
        /// abandoned by an exception without disposal releases the queue after a minute.
        /// </summary>
        public IEnumerator Render(RenderRequest q, Action<byte[]> done, Action<string> fail)
        {
            while (_busy && Time.realtimeSinceStartup - _busySince < 60f) yield return null;
            _busy = true;
            _busySince = Time.realtimeSinceStartup;
            s_busy = true;
            s_busySince = _busySince;
            try { yield return RenderNow(q, done, fail); }
            finally { _busy = false; s_busy = false; }
        }

        IEnumerator RenderNow(RenderRequest q, Action<byte[]> done, Action<string> fail)
        {
            var result = _session.Result;
            if (result == null) { fail("нет открытого проекта"); yield break; }
            // after a rebuild the reflections are captured probe by probe: perspective stills wait for them
            if (q.Mode != RenderMode.Plan && ReflectionCapture.Busy)
            {
                float until = Time.realtimeSinceStartup + ProbeWaitSeconds;
                while (ReflectionCapture.Busy && Time.realtimeSinceStartup < until) yield return null;
                result = _session.Result;
                if (result == null) { fail("нет открытого проекта"); yield break; }
            }
            int max = q.Mode == RenderMode.Current ? 4096 : 2048;
            int w = Mathf.Clamp(q.Width, 256, max), h = Mathf.Clamp(q.Height, 256, max);

            var main = Camera.main;
            var go = new GameObject("ApiRenderCamera") { hideFlags = HideFlags.HideAndDontSave };
            var cam = go.AddComponent<Camera>();
            if (main != null) cam.CopyFrom(main);
            if (q.Mode != RenderMode.Current)
            {
                cam.usePhysicalProperties = false;
                cam.lensShift = Vector2.zero;
            }
            cam.enabled = false;
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            // URP takes the camera's MSAA and its intermediate colour format from the target texture
            int msaa = StillMsaaFor(w, h);
            bool hdr = HdrStills;
            var rt = new RenderTexture(w, h, 24, hdr ? RenderTextureFormat.DefaultHDR : RenderTextureFormat.ARGB32,
                hdr ? RenderTextureReadWrite.Linear : RenderTextureReadWrite.sRGB) { antiAliasing = msaa, name = "ApiRenderTarget" };
            // what the PNG reads: the target resolved (MSAA) and encoded to 8-bit sRGB by a blit
            var readback = hdr || msaa > 1
                ? new RenderTexture(w, h, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { name = "ApiRenderReadback" }
                : rt;
            cam.targetTexture = rt;
            var hidden = new List<Renderer>();
            // the surface-cache GI volume follows the camera being rendered; with the viewer camera rendering in
            // between, its centre would jump every frame and the lighting would never converge — pause it meanwhile
            // (the baked lighting has no such state: the viewer keeps rendering, the screen does not blink)
            bool mainWasEnabled = main != null && main.enabled;
            bool pauseMain = q.Mode != RenderMode.Plan && main != null && House4696.Lighting.BakedGIVolume.Active == null;
            if (pauseMain) main.enabled = false;
            // stills for the AI can afford the full sample count the interactive view saves
            SurfaceCacheGIVolumeOverride gi = null;
            House4696.Core.HouseContent.Load().RealtimeGIProfile?.TryGet(out gi);
            int samples = gi != null ? gi.sampleCount.value : 0;
            if (gi != null && q.Mode != RenderMode.Plan) gi.sampleCount.Override(Mathf.Max(samples, 8));
            // stills for the AI always at full resolution (the viewer may render smaller on dense screens)
            var urp = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            float viewerScale = urp != null ? urp.renderScale : 1f;
            var viewerFilter = urp != null ? urp.upscalingFilter : UpscalingFilterSelection.Auto;
            bool perFrameScale = NativeScaleStills;
            if (urp != null && !perFrameScale)
            {
                urp.renderScale = 1f;
                urp.upscalingFilter = UpscalingFilterSelection.Auto;   // no FSR, no STP on an empty history
            }
            try
            {
                int frames = Mathf.Clamp(q.Frames, 1, 240), hideWait = 0;
                // baked lighting needs no accumulation: a few frames settle shadows and exposure
                if (House4696.Lighting.BakedGIVolume.Active != null) frames = Mathf.Min(frames, 4);
                switch (q.Mode)
                {
                    case RenderMode.Plan:
                    {
                        data.SetRenderer(0);                 // plain lighting: a plan must be readable, not moody
                        var fp = result.Footprint;
                        float cut = CutHeight(q.Level);
                        foreach (var r in Object.FindObjectsByType<Renderer>())
                            if (r.enabled && !r.forceRenderingOff && r.bounds.min.y > cut) { r.forceRenderingOff = true; hidden.Add(r); }
                        cam.orthographic = true;
                        float aspect = (float)w / h;
                        cam.orthographicSize = Mathf.Max(fp.height * 0.5f, fp.width * 0.5f / aspect) + 1.5f;
                        cam.nearClipPlane = 0.1f; cam.farClipPlane = 200f;
                        go.transform.SetPositionAndRotation(new Vector3(fp.center.x, cut + 50f, fp.center.y), Quaternion.Euler(90f, 0f, 0f));
                        frames = 2;
                        hideWait = 2;                        // the GPU resident drawer applies visibility changes a frame later
                        break;
                    }
                    case RenderMode.Site:
                    {
                        // the site plan: the whole plot from straight above, plain lighting, nothing hidden
                        data.SetRenderer(0);
                        var plot = House4696.Landscape.Natural.SiteModel.PlotOf(_session.Doc.Site, result.Footprint);
                        cam.orthographic = true;
                        float aspect = (float)w / h;
                        cam.orthographicSize = Mathf.Max(plot.height * 0.5f, plot.width * 0.5f / aspect) + 2f;
                        cam.nearClipPlane = 1f; cam.farClipPlane = 600f;
                        go.transform.SetPositionAndRotation(new Vector3(plot.center.x, 250f, plot.center.y), Quaternion.Euler(90f, 0f, 0f));
                        frames = 4;
                        break;
                    }
                    case RenderMode.Current:
                        // CopyFrom took the viewer's pose and lens
                        data.SetRenderer(_giRenderer);
                        break;
                    case RenderMode.Walk:
                        data.SetRenderer(_giRenderer);
                        cam.fieldOfView = q.Fov;
                        cam.nearClipPlane = 0.05f;
                        go.transform.SetPositionAndRotation(q.Position + Vector3.up * 1.66f, Quaternion.Euler(q.Pitch, q.Yaw, 0f));
                        break;
                    default:
                    {
                        data.SetRenderer(_giRenderer);
                        cam.fieldOfView = q.Fov;
                        var fp = result.Footprint;
                        float fit = Mathf.Max(fp.width, fp.height, 6f) * 1.35f / Mathf.Tan(q.Fov * 0.5f * Mathf.Deg2Rad) * 0.5f + 4f;
                        float dist = q.Distance > 0f ? q.Distance : fit;
                        var rot = Quaternion.Euler(q.Pitch, q.Yaw, 0f);
                        go.transform.SetPositionAndRotation(result.Pivot + rot * new Vector3(0, 0, -dist), rot);
                        break;
                    }
                }

                for (int i = 0; i < hideWait; i++) yield return null;
                for (int f = 0; f < frames; f++)
                {
                    if (perFrameScale) RenderAtFullScale(cam, urp); else cam.Render();
                    if (f % FramesPerTick == FramesPerTick - 1)
                    {
                        Resolve(rt, readback);
                        AsyncGPUReadback.Request(readback, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                        yield return null;
                    }
                }
                Resolve(rt, readback);
                var prev = RenderTexture.active;
                RenderTexture.active = readback;
                var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                var png = q.Jpeg ? tex.EncodeToJPG(88) : tex.EncodeToPNG();
                Object.Destroy(tex);
                done(png);
            }
            finally
            {
                if (pauseMain) main.enabled = mainWasEnabled;
                if (gi != null) gi.sampleCount.Override(samples);
                if (urp != null && !perFrameScale)
                {
                    urp.renderScale = viewerScale;
                    urp.upscalingFilter = viewerFilter;
                }
                foreach (var r in hidden) if (r != null) r.forceRenderingOff = false;
                cam.targetTexture = null;
                rt.Release();
                Object.Destroy(rt);
                if (readback != rt)
                {
                    readback.Release();
                    Object.Destroy(readback);
                }
                Object.Destroy(go);
            }
        }

        /// <summary>
        /// One still frame at render scale 1 with the Auto filter (no FSR, no STP — STP would run as TAA on an empty
        /// history). URP reads both per camera render and <see cref="Camera.Render"/> is synchronous, so the viewer's
        /// scale and upscaler are back before its next frame.
        /// </summary>
        static void RenderAtFullScale(Camera cam, UniversalRenderPipelineAsset urp)
        {
            if (urp == null) { cam.Render(); return; }
            float scale = urp.renderScale;
            var filter = urp.upscalingFilter;
            urp.renderScale = 1f;
            urp.upscalingFilter = UpscalingFilterSelection.Auto;
            try { cam.Render(); }
            finally
            {
                urp.renderScale = scale;
                urp.upscalingFilter = filter;
            }
        }

        /// <summary>Resolves MSAA and encodes the HDR target to 8-bit sRGB (linear colour space: the blit writes sRGB).</summary>
        static void Resolve(RenderTexture target, RenderTexture readback)
        {
            if (readback == target) return;
            var active = RenderTexture.active;
            Graphics.Blit(target, readback);
            RenderTexture.active = active;
        }

        /// <summary>MSAA sample count for a still of this size (a valid count: 1, 2, 4 or 8).</summary>
        static int StillMsaaFor(int w, int h)
        {
            long pixels = (long)w * h;
            int samples = pixels <= MsaaLargePixels ? StillMsaa : pixels <= MsaaMaxPixels ? StillMsaaLarge : 1;
            return samples >= 8 ? 8 : samples >= 4 ? 4 : samples >= 2 ? 2 : 1;
        }

        /// <summary>Plan cut: 1.2 m above the level's floor (the storey at grade when none is given, not a basement).</summary>
        float CutHeight(string levelId)
        {
            var doc = _session.Doc;
            float elev = 0f;
            if (doc.Levels.Count > 0)
            {
                var l = doc.Levels.Find(x => x.Id == levelId);
                if (l == null)
                {
                    foreach (var x in doc.Levels)
                        if (!House4696.Generation.HouseContext.IsBelowGrade(x) && (l == null || x.Elevation < l.Elevation)) l = x;
                    if (l == null) { l = doc.Levels[0]; foreach (var x in doc.Levels) if (x.Elevation > l.Elevation) l = x; }
                }
                elev = l.Elevation;
            }
            return elev + 1.2f;
        }
    }
}
