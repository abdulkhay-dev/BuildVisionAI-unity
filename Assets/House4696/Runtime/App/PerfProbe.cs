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
            // GI stays on until the last run: switching its renderer off and back stops the camera rendering
            yield return Measure("baseline", null, null);
            yield return Measure("render scale 0.5", () => urp.renderScale = 0.5f, () => urp.renderScale = scale);
            yield return Measure("render scale 0.7", () => urp.renderScale = 0.7f, () => urp.renderScale = scale);
            if (ssao.Count > 0) yield return Measure("no SSAO", () => ssao.ForEach(f => f.SetActive(false)), () => ssao.ForEach(f => f.SetActive(true)));
            yield return Measure("MSAA off", () => urp.msaaSampleCount = 1, () => urp.msaaSampleCount = msaa);
            var site = session.Result?.Site;
            if (site != null) yield return Measure("no garden", () => site.SetActive(false), () => site.SetActive(true));
            if (gi != null)
            {
                int sc = gi.sampleCount.value, res = gi.volumeResolution.value, cas = gi.volumeCascadeCount.value, look = gi.lookupSampleCount.value, up = gi.upsamplingSampleCount.value;
                bool mb = gi.multiBounce.value, sf = gi.spatialFilterEnabled.value;
                result["gi"] = $"samples {sc}, resolution {res}, cascades {cas}, lookup {look}, upsampling {up}, multiBounce {mb}, spatial {sf}";
                yield return Measure("GI samples 2", () => gi.sampleCount.Override(2), () => gi.sampleCount.Override(sc));
                yield return Measure("GI resolution 32", () => gi.volumeResolution.Override(32), () => gi.volumeResolution.Override(res));
                yield return Measure("GI cascades 2", () => gi.volumeCascadeCount.Override(2), () => gi.volumeCascadeCount.Override(cas));
                yield return Measure("GI single bounce", () => gi.multiBounce.Override(false), () => gi.multiBounce.Override(mb));
                yield return Measure("GI lookup 1 + upsampling 2", () => { gi.lookupSampleCount.Override(1); gi.upsamplingSampleCount.Override(2); },
                    () => { gi.lookupSampleCount.Override(look); gi.upsamplingSampleCount.Override(up); });
                yield return Measure("GI cheap: samples 2, res 32, cascades 2, lookup 1, up 2 + scale 0.7", () =>
                {
                    gi.sampleCount.Override(2); gi.volumeResolution.Override(32); gi.volumeCascadeCount.Override(2);
                    gi.lookupSampleCount.Override(1); gi.upsamplingSampleCount.Override(2); urp.renderScale = 0.7f;
                }, () =>
                {
                    gi.sampleCount.Override(sc); gi.volumeResolution.Override(res); gi.volumeCascadeCount.Override(cas);
                    gi.lookupSampleCount.Override(look); gi.upsamplingSampleCount.Override(up); urp.renderScale = scale;
                });
            }
            yield return Measure("no realtime GI", () => data.SetRenderer(0), () => data.SetRenderer(giRenderer));
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
