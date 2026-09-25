using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace House4696.App
{
    /// <summary>
    /// Frame-time diagnostics in the running app: measures the viewer with one cost switched off at a time
    /// (realtime GI, render scale, SSAO, extra shadows, garden, MSAA) so the expensive parts show up.
    /// </summary>
    public static class PerfProbe
    {
        public static IEnumerator Sweep(HouseSession session, int giRenderer, int frames, Action<JObject> done)
        {
            var cam = Camera.main;
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var data = cam.GetUniversalAdditionalCameraData();
            var result = new JObject
            {
                ["screen"] = $"{Screen.width}×{Screen.height} (window), dpi {Screen.dpi:0}",
                ["gpu"] = SystemInfo.graphicsDeviceName, ["vsync"] = QualitySettings.vSyncCount, ["targetFps"] = Application.targetFrameRate,
                ["renderers"] = Object.FindObjectsByType<Renderer>().Length,
                ["lights"] = Object.FindObjectsByType<Light>().Length,
                ["shadowLights"] = Object.FindObjectsByType<Light>().Count(l => l.shadows != LightShadows.None),
            };
            var ssao = FindFeatures("ScreenSpaceAmbientOcclusion");
            var runs = new JArray();
            result["runs"] = runs;

            IEnumerator Measure(string name, Action apply, Action undo)
            {
                apply?.Invoke();
                for (int i = 0; i < 20; i++) yield return null;
                FrameTimingManager.CaptureFrameTimings();
                float sum = 0f, gpu = 0f; int gpuN = 0;
                var timings = new FrameTiming[1];
                for (int i = 0; i < frames; i++)
                {
                    yield return null;
                    sum += Time.unscaledDeltaTime;
                    FrameTimingManager.CaptureFrameTimings();
                    if (FrameTimingManager.GetLatestTimings(1, timings) > 0 && timings[0].gpuFrameTime > 0) { gpu += (float)timings[0].gpuFrameTime; gpuN++; }
                }
                float ms = sum / frames * 1000f;
                runs.Add(new JObject { ["config"] = name, ["frameMs"] = Math.Round(ms, 1), ["fps"] = Math.Round(1000f / ms, 1), ["gpuMs"] = gpuN > 0 ? Math.Round(gpu / gpuN, 1) : (double?)null });
                undo?.Invoke();
            }

            float scale = urp.renderScale;
            int msaa = urp.msaaSampleCount;
            var profile = House4696.Core.HouseContent.Load().RealtimeGIProfile;
            SurfaceCacheGIVolumeOverride gi = null;
            profile?.TryGet(out gi);
            yield return Measure("baseline", null, null);
            yield return Measure("render scale 0.5", () => urp.renderScale = 0.5f, () => urp.renderScale = scale);
            yield return Measure("render scale 0.7", () => urp.renderScale = 0.7f, () => urp.renderScale = scale);
            if (ssao.Count > 0) yield return Measure("no SSAO", () => ssao.ForEach(f => f.SetActive(false)), () => ssao.ForEach(f => f.SetActive(true)));
            yield return Measure("MSAA off", () => urp.msaaSampleCount = 1, () => urp.msaaSampleCount = msaa);
            var site = session.Result?.Site;
            if (site != null)
            {
                yield return Measure("no garden", () => site.SetActive(false), () => site.SetActive(true));
                var siteRenderers = site.GetComponentsInChildren<Renderer>().ToList();
                var casting = siteRenderers.Select(r => r.shadowCastingMode).ToList();
                yield return Measure("garden casts no shadows", () => siteRenderers.ForEach(r => r.shadowCastingMode = ShadowCastingMode.Off),
                    () => { for (int i = 0; i < siteRenderers.Count; i++) siteRenderers[i].shadowCastingMode = casting[i]; });
                var grass = siteRenderers.Where(r => r.sharedMaterial != null && r.sharedMaterial.name.Contains("Grass")).ToList();
                if (grass.Count > 0)
                    yield return Measure($"no grass blades ({grass.Count})", () => grass.ForEach(r => r.enabled = false), () => grass.ForEach(r => r.enabled = true));
                var trees = siteRenderers.Where(r => r.transform.parent != null && r.transform.parent.name == "Trees").ToList();
                if (trees.Count > 0)
                    yield return Measure($"no trees ({trees.Count})", () => trees.ForEach(r => r.enabled = false), () => trees.ForEach(r => r.enabled = true));
            }
            var baked = House4696.Lighting.BakedGIVolume.Active;
            if (baked != null)
                yield return Measure("no baked GI (resolve pass off)", () => House4696.Lighting.BakedGIVolume.Active = null, () => House4696.Lighting.BakedGIVolume.Active = baked);
            var punctual = Object.FindObjectsByType<Light>().Where(l => l.type != LightType.Directional && l.shadows != LightShadows.None).ToList();
            if (punctual.Count > 0)
            {
                var modes = punctual.Select(l => l.shadows).ToList();
                yield return Measure($"no lamp shadows ({punctual.Count})", () => punctual.ForEach(l => l.shadows = LightShadows.None),
                    () => { for (int i = 0; i < punctual.Count; i++) punctual[i].shadows = modes[i]; });
            }
            var lamps = Object.FindObjectsByType<Light>().Where(l => l.type != LightType.Directional && l.enabled).ToList();
            if (lamps.Count > 0)
                yield return Measure($"no lamps ({lamps.Count})", () => lamps.ForEach(l => l.enabled = false), () => lamps.ForEach(l => l.enabled = true));
            if (gi != null && gi.enabled.value)
            {
                int sc = gi.sampleCount.value;
                result["gi"] = $"surface cache on: samples {sc}, resolution {gi.volumeResolution.value}, cascades {gi.volumeCascadeCount.value}";
                yield return Measure("surface cache GI samples 2", () => gi.sampleCount.Override(2), () => gi.sampleCount.Override(sc));
            }
            // no renderer switching: taking the camera off its renderer and back stops it rendering
            done(result);
        }

        /// <summary>Average frame and GPU time of the viewer over <paramref name="frames"/> after a warm-up.</summary>
        public static IEnumerator Measure(int warmup, int frames, Action<JObject> done)
        {
            for (int i = 0; i < warmup; i++) yield return null;
            FrameTimingManager.CaptureFrameTimings();
            float sum = 0f, gpu = 0f; int gpuN = 0;
            var timings = new FrameTiming[1];
            for (int i = 0; i < frames; i++)
            {
                yield return null;
                sum += Time.unscaledDeltaTime;
                FrameTimingManager.CaptureFrameTimings();
                if (FrameTimingManager.GetLatestTimings(1, timings) > 0 && timings[0].gpuFrameTime > 0) { gpu += (float)timings[0].gpuFrameTime; gpuN++; }
            }
            float ms = sum / frames * 1000f;
            done(new JObject { ["frameMs"] = Math.Round(ms, 1), ["fps"] = Math.Round(1000f / ms, 1), ["gpuMs"] = gpuN > 0 ? Math.Round(gpu / gpuN, 1) : (double?)null });
        }

        /// <summary>
        /// Live tuning for diagnostics: render scale, MSAA, SSAO, realtime-GI parameters and whether the garden
        /// takes part in the GI (rendering layer 1 = house, 2 = site; the GI mask decides who gets cache patches).
        /// </summary>
        public static JObject Tune(JObject a, HouseSession session)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            if (a["renderScale"] != null) urp.renderScale = (float)a["renderScale"];
            if (a["msaa"] != null) urp.msaaSampleCount = (int)a["msaa"];
            if (a["ssao"] != null) FindFeatures("ScreenSpaceAmbientOcclusion").ForEach(f => f.SetActive((bool)a["ssao"]));
            SurfaceCacheGIVolumeOverride gi = null;
            House4696.Core.HouseContent.Load().RealtimeGIProfile?.TryGet(out gi);
            if (gi != null && a["gi"] is JObject g)
            {
                if (g["samples"] != null) gi.sampleCount.Override((int)g["samples"]);
                if (g["resolution"] != null) gi.volumeResolution.Override((int)g["resolution"]);
                if (g["cascades"] != null) gi.volumeCascadeCount.Override((int)g["cascades"]);
                if (g["size"] != null) gi.volumeSize.Override((float)g["size"]);
                if (g["multiBounce"] != null) gi.multiBounce.Override((bool)g["multiBounce"]);
                if (g["lookup"] != null) gi.lookupSampleCount.Override((int)g["lookup"]);
                if (g["upsampling"] != null) gi.upsamplingSampleCount.Override((int)g["upsampling"]);
                if (g["spatial"] != null) gi.spatialFilterEnabled.Override((bool)g["spatial"]);
                if (g["temporal"] != null) gi.temporalSmoothing.Override((float)g["temporal"]);
                if (g["siteInGI"] != null)
                {
                    bool siteIn = (bool)g["siteInGI"];
                    var site = session.Result?.Site;
                    if (site != null) foreach (var r in site.GetComponentsInChildren<Renderer>(true)) r.renderingLayerMask = 2u;
                    gi.renderingLayerMask.Override(siteIn ? (RenderingLayerMask)0xFFFFFFFF : (RenderingLayerMask)1u);
                }
            }
            return new JObject
            {
                ["renderScale"] = urp.renderScale, ["msaa"] = urp.msaaSampleCount,
                ["gi"] = gi == null ? null : $"samples {gi.sampleCount.value}, resolution {gi.volumeResolution.value}, cascades {gi.volumeCascadeCount.value}, size {gi.volumeSize.value}, multiBounce {gi.multiBounce.value}, lookup {gi.lookupSampleCount.value}, upsampling {gi.upsamplingSampleCount.value}, spatial {gi.spatialFilterEnabled.value}, mask {(uint)gi.renderingLayerMask.value}",
            };
        }

        static List<ScriptableRendererFeature> FindFeatures(string typeName)
        {
            var found = new List<ScriptableRendererFeature>();
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var list = typeof(UniversalRenderPipelineAsset).GetField("m_RendererDataList", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.GetValue(urp) as ScriptableRendererData[];
            if (list == null) return found;
            foreach (var rd in list)
                if (rd != null)
                    foreach (var f in rd.rendererFeatures)
                        if (f != null && f.GetType().Name == typeName) found.Add(f);
            return found;
        }
    }
}
