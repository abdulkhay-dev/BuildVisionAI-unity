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
    public enum RenderMode { Orbit, Walk, Plan }

    /// <summary>What to render: an orbit angle around the house, a standing point inside, or a floor plan from above.</summary>
    public sealed class RenderRequest
    {
        public RenderMode Mode = RenderMode.Orbit;
        public float Yaw = 30f, Pitch = 12f, Distance;          // orbit: distance 0 = fit the house
        public Vector3 Position;                                 // walk: feet position (absolute)
        public string Level;                                     // plan: which level (default: lowest)
        public int Width = 1280, Height = 800;
        public float Fov = 60f;
        public int Frames = 48;                                  // realtime GI accumulation
    }

    /// <summary>
    /// Renders views of the current house into PNGs for the AI (so it can see what it built). Perspective views go
    /// through the GI renderer: with baked lighting a few frames suffice, with the realtime fallback they accumulate
    /// a few dozen frames, a few per app frame with GPU syncs so neither the app nor the GPU queue stalls. Plans are orthographic from above, without GI, with everything
    /// above the cut height (ceilings, upper floors, roofs) hidden.
    /// </summary>
    public sealed class ViewRenderer
    {
        const int FramesPerTick = 3;
        readonly HouseSession _session;
        readonly int _giRenderer;

        public ViewRenderer(HouseSession session, int giRendererIndex)
        {
            _session = session; _giRenderer = giRendererIndex;
        }

        public IEnumerator Render(RenderRequest q, Action<byte[]> done, Action<string> fail)
        {
            var result = _session.Result;
            if (result == null) { fail("нет открытого проекта"); yield break; }
            int w = Mathf.Clamp(q.Width, 256, 2048), h = Mathf.Clamp(q.Height, 256, 2048);

            var main = Camera.main;
            var go = new GameObject("ApiRenderCamera") { hideFlags = HideFlags.HideAndDontSave };
            var cam = go.AddComponent<Camera>();
            if (main != null) cam.CopyFrom(main);
            cam.usePhysicalProperties = false;
            cam.lensShift = Vector2.zero;
            cam.enabled = false;
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            cam.targetTexture = rt;
            var hidden = new List<Renderer>();
            // the surface-cache GI volume follows the camera being rendered; with the viewer camera rendering in
            // between, its centre would jump every frame and the lighting would never converge — pause it meanwhile
            bool mainWasEnabled = main != null && main.enabled;
            if (q.Mode != RenderMode.Plan && main != null) main.enabled = false;
            // stills for the AI can afford the full sample count the interactive view saves
            SurfaceCacheGIVolumeOverride gi = null;
            House4696.Core.HouseContent.Load().RealtimeGIProfile?.TryGet(out gi);
            int samples = gi != null ? gi.sampleCount.value : 0;
            if (gi != null && q.Mode != RenderMode.Plan) gi.sampleCount.Override(Mathf.Max(samples, 8));
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
                    cam.Render();
                    if (f % FramesPerTick == FramesPerTick - 1)
                    {
                        AsyncGPUReadback.Request(rt, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                        yield return null;
                    }
                }
                var prev = RenderTexture.active;
                RenderTexture.active = rt;
                var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                var png = tex.EncodeToPNG();
                Object.Destroy(tex);
                done(png);
            }
            finally
            {
                if (main != null) main.enabled = mainWasEnabled;
                if (gi != null) gi.sampleCount.Override(samples);
                foreach (var r in hidden) if (r != null) r.forceRenderingOff = false;
                cam.targetTexture = null;
                rt.Release();
                Object.Destroy(rt);
                Object.Destroy(go);
            }
        }

        /// <summary>Plan cut: 1.2 m above the level's floor (lowest level when none is given).</summary>
        float CutHeight(string levelId)
        {
            var doc = _session.Doc;
            float elev = 0f;
            if (doc.Levels.Count > 0)
            {
                var l = doc.Levels.Find(x => x.Id == levelId);
                if (l == null) { l = doc.Levels[0]; foreach (var x in doc.Levels) if (x.Elevation < l.Elevation) l = x; }
                elev = l.Elevation;
            }
            return elev + 1.2f;
        }
    }
}
