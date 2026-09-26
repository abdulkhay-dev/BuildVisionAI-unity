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
        /// <summary>Measurements run uncapped (the focused frame cap would floor every result at the panel rate).</summary>
        sealed class Uncapped : IDisposable
        {
            readonly int _rate = Application.targetFrameRate, _vsync = QualitySettings.vSyncCount;
            public Uncapped() { Application.targetFrameRate = -1; QualitySettings.vSyncCount = 0; }
            public void Dispose() { Application.targetFrameRate = _rate; QualitySettings.vSyncCount = _vsync; }
        }

        public static IEnumerator Sweep(HouseSession session, int giRenderer, int frames, Action<JObject> done)
        {
            using var uncapped = new Uncapped();
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
            bool budget = LampShadowBudget.Enabled;
            LampShadowBudget.Enabled = false;               // one cost at a time: every lamp keeps its shadow
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
                var shown = siteRenderers.Select(r => r.enabled).ToList();
                yield return Measure("garden casts no shadows", () => siteRenderers.ForEach(CastNoShadow),
                    () => { for (int i = 0; i < siteRenderers.Count; i++) { siteRenderers[i].shadowCastingMode = casting[i]; siteRenderers[i].enabled = shown[i]; } });
                var grass = siteRenderers.Where(r => r.sharedMaterial != null && r.sharedMaterial.name.Contains("Grass")).ToList();
                if (grass.Count > 0)
                    yield return Measure($"no grass blades ({grass.Count})", () => grass.ForEach(r => r.enabled = false), () => grass.ForEach(r => r.enabled = true));
                var trees = siteRenderers.Where(r => IsTreeRenderer(r.transform)).ToList();
                if (trees.Count > 0)
                    yield return Measure($"no trees ({trees.Count})", () => trees.ForEach(r => r.enabled = false), () => trees.ForEach(r => r.enabled = true));
                // natural site: its parts one at a time
                var field = site.GetComponentInChildren<House4696.Landscape.Natural.PlantField>();
                if (field != null)
                {
                    yield return Measure($"no plants ({field.Count})", () => House4696.Landscape.Natural.PlantField.Enabled = false, () => House4696.Landscape.Natural.PlantField.Enabled = true);
                    yield return Measure("plants cast no shadows", () => House4696.Landscape.Natural.PlantField.Shadows = false, () => House4696.Landscape.Natural.PlantField.Shadows = true);
                    var terrains = site.GetComponentsInChildren<Terrain>(true);
                    var inner = terrains.FirstOrDefault(t => t.name == "Terrain");
                    if (inner != null)
                    {
                        float density = inner.detailObjectDensity;
                        yield return Measure("no grass details", () => inner.detailObjectDensity = 0f, () => inner.detailObjectDensity = density);
                        var mode = inner.shadowCastingMode;
                        yield return Measure("terrain casts no shadows", () => { foreach (var t in terrains) t.shadowCastingMode = ShadowCastingMode.Off; },
                            () => { foreach (var t in terrains) t.shadowCastingMode = mode; });
                    }
                    foreach (var part in new[] { "Water", "Rocks", "FarTerrain", "Built" })
                    {
                        var go = site.transform.Find(part);
                        if (go != null) yield return Measure($"no {part}", () => go.gameObject.SetActive(false), () => go.gameObject.SetActive(true));
                    }
                }
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
            LampShadowBudget.Enabled = budget;
            done(result);
        }

        /// <summary>
        /// Repeatable benchmark: fixed views (exterior orbit preset 0, the largest ground-floor room from inside, the
        /// top orbit view), each warmed up then measured — median / p95 frame time, average GPU time. With
        /// <paramref name="shotsDir"/> each view is also saved as a PNG (the viewer's own picture) for A/B comparison.
        /// </summary>
        public static IEnumerator Bench(HouseSession session, ViewRenderer renderer, int frames, string shotsDir, Action<JObject> done)
        {
            using var uncapped = new Uncapped();
            var cam = Camera.main;
            var viewer = cam != null ? cam.GetComponent<House4696.Runtime.HouseViewer>() : null;
            var result = new JObject
            {
                ["screen"] = $"{Screen.width}×{Screen.height}", ["gpu"] = SystemInfo.graphicsDeviceName,
                ["renderScale"] = (GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset)?.renderScale,
            };
            var views = new JArray();
            result["views"] = views;
            if (viewer == null || session.Result == null) { done(result); yield break; }

            var steps = new List<(string name, Action go)>
            {
                ("exterior", () => { viewer.SwitchTo(House4696.Runtime.HouseViewer.Mode.Orbit); viewer.GoToPoint(0); }),
                ("interior", () =>
                {
                    var level = session.Doc.Levels.OrderBy(l => l.Elevation).FirstOrDefault();
                    if (level == null) return;
                    var plan = PlanGeometry.Build(session.Doc, level);
                    var room = plan.Rooms.OrderByDescending(r => r.Area).FirstOrDefault();
                    if (room == null) return;
                    PlanGeometry.ViewSpot(room.Outline, plan.Elevation, out var feet, out float yaw);
                    viewer.TeleportWalk(new House4696.Runtime.WalkPoint { Name = room.Name, Feet = feet, Yaw = yaw, Pitch = 3f });
                }),
                ("top", () =>
                {
                    viewer.SwitchTo(House4696.Runtime.HouseViewer.Mode.Orbit);
                    int top = Array.FindIndex(viewer.OrbitPoints, o => o.Pitch > 45f);
                    viewer.GoToPoint(top >= 0 ? top : viewer.OrbitPoints.Length - 1);
                }),
            };
            var timings = new FrameTiming[1];
            foreach (var st in steps)
            {
                st.go();
                for (int i = 0; i < 90; i++) yield return null;       // camera glide + GPU clocks settle
                var ms = new List<float>(frames);
                float gpu = 0f, cpuMain = 0f, cpuRender = 0f; int gpuN = 0, cpuN = 0;
                FrameTimingManager.CaptureFrameTimings();
                for (int i = 0; i < frames; i++)
                {
                    yield return null;
                    ms.Add(Time.unscaledDeltaTime * 1000f);
                    FrameTimingManager.CaptureFrameTimings();
                    if (FrameTimingManager.GetLatestTimings(1, timings) > 0)
                    {
                        if (timings[0].gpuFrameTime > 0) { gpu += (float)timings[0].gpuFrameTime; gpuN++; }
                        if (timings[0].cpuMainThreadFrameTime > 0) { cpuMain += (float)timings[0].cpuMainThreadFrameTime; cpuRender += (float)timings[0].cpuRenderThreadFrameTime; cpuN++; }
                    }
                }
                ms.Sort();
                float median = ms[ms.Count / 2], p95 = ms[Mathf.Min(ms.Count - 1, (int)(ms.Count * 0.95f))];
                var v = new JObject
                {
                    ["view"] = st.name, ["medianMs"] = Math.Round(median, 1), ["p95Ms"] = Math.Round(p95, 1),
                    ["fps"] = Math.Round(1000f / median, 1), ["gpuMs"] = gpuN > 0 ? Math.Round(gpu / gpuN, 1) : (double?)null,
                    ["cpuMainMs"] = cpuN > 0 ? Math.Round(cpuMain / cpuN, 1) : (double?)null,
                    ["cpuRenderMs"] = cpuN > 0 ? Math.Round(cpuRender / cpuN, 1) : (double?)null,
                };
                views.Add(v);
                if (!string.IsNullOrEmpty(shotsDir))
                {
                    // the real viewer output (render scale, upscaler, AA) without the UI
                    System.IO.Directory.CreateDirectory(shotsDir);
                    var doc = Object.FindAnyObjectByType<UnityEngine.UIElements.UIDocument>();
                    var ui = doc != null ? doc.rootVisualElement : null;
                    if (ui != null) ui.style.display = UnityEngine.UIElements.DisplayStyle.None;
                    yield return null;
                    yield return new WaitForEndOfFrame();
                    var tex = ScreenCapture.CaptureScreenshotAsTexture();
                    string path = System.IO.Path.Combine(shotsDir, st.name + ".png");
                    System.IO.File.WriteAllBytes(path, tex.EncodeToPNG());
                    Object.Destroy(tex);
                    if (ui != null) ui.style.display = UnityEngine.UIElements.DisplayStyle.Flex;
                    v["shot"] = path;
                }
            }
            done(result);
        }

        /// <summary>
        /// Interleaved A/B measurement on one fixed view (the fanless MacBook throttles within a minute, so sequential
        /// sweeps drift by several ms): applies tune <c>a</c>, measures, applies <c>b</c>, measures, for
        /// <paramref name="rounds"/> rounds, and reports the median of each side.
        /// </summary>
        public static IEnumerator AB(HouseSession session, JObject args, Action<JObject> done)
        {
            using var uncapped = new Uncapped();
            var cam = Camera.main;
            var viewer = cam != null ? cam.GetComponent<House4696.Runtime.HouseViewer>() : null;
            var a = args["a"] as JObject ?? new JObject();
            var b = args["b"] as JObject ?? new JObject();
            int rounds = args["rounds"] != null ? (int)args["rounds"] : 4, frames = args["frames"] != null ? (int)args["frames"] : 90;
            string view = (string)args["view"] ?? "exterior";
            if (viewer != null && session.Result != null) GoTo(session, viewer, view);
            for (int i = 0; i < 90; i++) yield return null;
            var msA = new List<float>(); var msB = new List<float>();
            IEnumerator Run(JObject tune, List<float> into)
            {
                Tune(tune, session);
                for (int i = 0; i < 20; i++) yield return null;
                var ms = new List<float>(frames);
                for (int i = 0; i < frames; i++) { yield return null; ms.Add(Time.unscaledDeltaTime * 1000f); }
                ms.Sort();
                into.Add(ms[ms.Count / 2]);
            }
            for (int r = 0; r < rounds; r++)
            {
                yield return Run(a, msA);
                yield return Run(b, msB);
            }
            Tune(args["restore"] as JObject ?? a, session);
            msA.Sort(); msB.Sort();
            float ma = msA[msA.Count / 2], mb = msB[msB.Count / 2];
            done(new JObject
            {
                ["view"] = view, ["a"] = a, ["b"] = b,
                ["aMs"] = Math.Round(ma, 2), ["bMs"] = Math.Round(mb, 2), ["deltaMs"] = Math.Round(mb - ma, 2),
                ["aRuns"] = new JArray(msA.Select(x => Math.Round(x, 1))), ["bRuns"] = new JArray(msB.Select(x => Math.Round(x, 1))),
            });
        }

        /// <summary>Puts the viewer on one of the benchmark views.</summary>
        static void GoTo(HouseSession session, House4696.Runtime.HouseViewer viewer, string view)
        {
            switch (view)
            {
                case "interior":
                    var level = session.Doc.Levels.OrderBy(l => l.Elevation).FirstOrDefault();
                    if (level == null) return;
                    var plan = PlanGeometry.Build(session.Doc, level);
                    var room = plan.Rooms.OrderByDescending(r => r.Area).FirstOrDefault();
                    if (room == null) return;
                    PlanGeometry.ViewSpot(room.Outline, plan.Elevation, out var feet, out float yaw);
                    viewer.TeleportWalk(new House4696.Runtime.WalkPoint { Name = room.Name, Feet = feet, Yaw = yaw, Pitch = 3f });
                    break;
                case "top":
                    viewer.SwitchTo(House4696.Runtime.HouseViewer.Mode.Orbit);
                    int top = Array.FindIndex(viewer.OrbitPoints, o => o.Pitch > 45f);
                    viewer.GoToPoint(top >= 0 ? top : viewer.OrbitPoints.Length - 1);
                    break;
                default:
                    viewer.SwitchTo(House4696.Runtime.HouseViewer.Mode.Orbit);
                    viewer.GoToPoint(0);
                    break;
            }
        }

        /// <summary>Average frame and GPU time of the viewer over <paramref name="frames"/> after a warm-up.</summary>
        public static IEnumerator Measure(int warmup, int frames, Action<JObject> done)
        {
            using var uncapped = new Uncapped();
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
            if (a["pin"] != null) HouseBootstrap.PinRenderScale = (bool)a["pin"];
            if (a["renderScale"] != null) { HouseBootstrap.PinRenderScale = true; urp.renderScale = (float)a["renderScale"]; }
            if (a["upscaler"] != null)
            {
                HouseBootstrap.PinRenderScale = true;
                urp.upscalingFilter = (string)a["upscaler"] switch
                {
                    "stp" => UpscalingFilterSelection.STP, "fsr" => UpscalingFilterSelection.FSR,
                    "linear" => UpscalingFilterSelection.Linear, "point" => UpscalingFilterSelection.Point, _ => UpscalingFilterSelection.Auto,
                };
            }
            if (a["fsrSharpness"] != null) { urp.fsrOverrideSharpness = true; urp.fsrSharpness = (float)a["fsrSharpness"]; }
            if (a["msaa"] != null) urp.msaaSampleCount = (int)a["msaa"];
            if (a["ssao"] != null) FindFeatures("ScreenSpaceAmbientOcclusion").ForEach(f => f.SetActive((bool)a["ssao"]));
            if (a["opaqueTexture"] != null) urp.supportsCameraOpaqueTexture = (bool)a["opaqueTexture"];
            if (a["occlusion"] != null) urp.gpuResidentDrawerEnableOcclusionCullingInCameras = (bool)a["occlusion"];
            if (a["shadowDistance"] != null) urp.shadowDistance = (float)a["shadowDistance"];
            if (a["cascades"] != null) urp.shadowCascadeCount = (int)a["cascades"];
            if (a["mainShadowRes"] != null) urp.mainLightShadowmapResolution = (int)a["mainShadowRes"];
            if (a["addShadowRes"] != null) urp.additionalLightsShadowmapResolution = (int)a["addShadowRes"];
            if (a["softShadows"] != null)
                typeof(UniversalRenderPipelineAsset).GetField("m_SoftShadowsSupported", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(urp, (bool)a["softShadows"]);
            if (a["hdr"] != null) urp.supportsHDR = (bool)a["hdr"];
            if (a["depthPriming"] != null)
            {
                // 0 disabled, 1 auto, 2 forced: the colour pass shades each pixel once (ZTest Equal) after the depth prepass
                var list = typeof(UniversalRenderPipelineAsset).GetField("m_RendererDataList", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.GetValue(urp) as ScriptableRendererData[];
                if (list != null)
                    foreach (var rd in list)
                        if (rd is UniversalRendererData ur) { ur.depthPrimingMode = (DepthPrimingMode)(int)a["depthPriming"]; ur.SetDirty(); }
            }
            if (a["lodBias"] != null) QualitySettings.lodBias = (float)a["lodBias"];
            if (a["vsync"] != null) QualitySettings.vSyncCount = (int)a["vsync"];
            if (a["targetFps"] != null) Application.targetFrameRate = (int)a["targetFps"];
            var cam = Camera.main;
            var camData = cam != null ? cam.GetUniversalAdditionalCameraData() : null;
            if (camData != null && a["aa"] != null)
                camData.antialiasing = (string)a["aa"] switch
                {
                    "smaa" => AntialiasingMode.SubpixelMorphologicalAntiAliasing, "taa" => AntialiasingMode.TemporalAntiAliasing,
                    "fxaa" => AntialiasingMode.FastApproximateAntialiasing, _ => AntialiasingMode.None,
                };
            if (a["lampShadows"] != null)
            {
                bool on = (bool)a["lampShadows"];
                foreach (var l in Object.FindObjectsByType<Light>())
                    if (l.type != LightType.Directional && (l.shadows != LightShadows.None || on))
                    {
                        if (!on) { l.shadows = LightShadows.None; }
                    }
            }
            if (a["garden"] != null && session.Result?.Site != null) session.Result.Site.SetActive((bool)a["garden"]);
            if (a["trees"] != null && session.Result?.Site != null)
                foreach (var r in session.Result.Site.GetComponentsInChildren<Renderer>(true))
                    if (IsTreeRenderer(r.transform)) r.enabled = (bool)a["trees"];
            if (a["grass"] != null && session.Result?.Site != null)
                foreach (var r in session.Result.Site.GetComponentsInChildren<Renderer>(true))
                    if (r.sharedMaterial != null && r.sharedMaterial.name.Contains("Grass")) r.enabled = (bool)a["grass"];
            if (a["plants"] != null) House4696.Landscape.Natural.PlantField.Enabled = (bool)a["plants"];
            if (a["plantShadows"] != null) House4696.Landscape.Natural.PlantField.Shadows = (bool)a["plantShadows"];
            if (a["plantShadowDistance"] != null) House4696.Landscape.Natural.PlantField.ShadowDistance = (float)a["plantShadowDistance"];
            if (a["plantMaxLod"] != null) House4696.Landscape.Natural.PlantField.MaxLod = (int)a["plantMaxLod"];
            if (a["plantLodScale"] != null) House4696.Landscape.Natural.PlantField.LodScale = (float)a["plantLodScale"];
            if (session.Result?.Site != null)
            {
                foreach (var t in session.Result.Site.GetComponentsInChildren<Terrain>(true))
                {
                    if (a["detailDensity"] != null) t.detailObjectDensity = (float)a["detailDensity"];
                    if (a["detailDistance"] != null) t.detailObjectDistance = (float)a["detailDistance"];
                    if (a["terrainError"] != null) t.heightmapPixelError = (float)a["terrainError"];
                    if (a["terrainShadows"] != null) t.shadowCastingMode = (bool)a["terrainShadows"] ? ShadowCastingMode.On : ShadowCastingMode.Off;
                    if (a["terrainInstanced"] != null) t.drawInstanced = (bool)a["terrainInstanced"];
                }
                foreach (var part in new[] { "Water", "Rocks", "FarTerrain", "Built" })
                {
                    var key = char.ToLowerInvariant(part[0]) + part.Substring(1);
                    var go = session.Result.Site.transform.Find(part);
                    if (a[key] != null && go != null) go.gameObject.SetActive((bool)a[key]);
                }
                var built = session.Result.Site.transform.Find("Built");
                if (built != null)
                {
                    foreach (Transform t in built)
                    {
                        bool isTree = t.name.StartsWith("Broadleaf") || t.name.StartsWith("Spruce") || t.name.StartsWith("Birch");
                        if (a["builtTrees"] != null && isTree) t.gameObject.SetActive((bool)a["builtTrees"]);
                        if (a["fence"] != null && t.name == "Fence") t.gameObject.SetActive((bool)a["fence"]);
                    }
                }
                if (a["siteLights"] != null)
                    foreach (var l in session.Result.Site.GetComponentsInChildren<Light>(true)) l.enabled = (bool)a["siteLights"];
            }
            if (a["gardenShadows"] != null && session.Result?.Site != null && !(bool)a["gardenShadows"])
                foreach (var r in session.Result.Site.GetComponentsInChildren<Renderer>(true)) CastNoShadow(r);
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
                    gi.renderingLayerMask.Override(siteIn ? (RenderingLayerMask)0xFFFFFFFF : (RenderingLayerMask)5u);
                }
            }
            return new JObject
            {
                ["renderScale"] = urp.renderScale, ["msaa"] = urp.msaaSampleCount, ["upscaler"] = urp.upscalingFilter.ToString(),
                ["pinned"] = HouseBootstrap.PinRenderScale, ["aa"] = camData?.antialiasing.ToString(), ["opaqueTexture"] = urp.supportsCameraOpaqueTexture,
                ["occlusion"] = urp.gpuResidentDrawerEnableOcclusionCullingInCameras, ["shadowDistance"] = urp.shadowDistance,
                ["cascades"] = urp.shadowCascadeCount, ["softShadows"] = urp.supportsSoftShadows, ["lodBias"] = QualitySettings.lodBias,
                ["plantsDrawn"] = new JArray(House4696.Landscape.Natural.PlantField.Drawn),
                ["depthPriming"] = (typeof(UniversalRenderPipelineAsset).GetField("m_RendererDataList", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.GetValue(urp) as ScriptableRendererData[])?.OfType<UniversalRendererData>().FirstOrDefault()?.depthPrimingMode.ToString(),
                ["plants"] = session.Result?.Site != null && a["report"] != null
                    ? session.Result.Site.GetComponentInChildren<House4696.Landscape.Natural.PlantField>()?.Report() : null,
                ["gi"] = gi == null ? null : $"samples {gi.sampleCount.value}, resolution {gi.volumeResolution.value}, cascades {gi.volumeCascadeCount.value}, size {gi.volumeSize.value}, multiBounce {gi.multiBounce.value}, lookup {gi.lookupSampleCount.value}, upsampling {gi.upsamplingSampleCount.value}, spatial {gi.spatialFilterEnabled.value}, mask {(uint)gi.renderingLayerMask.value}",
            };
        }

        /// <summary>
        /// Stops a garden renderer casting. Shadow proxies (ShadowsOnly: tree "ShadowProxy", "&lt;hedge&gt;_Shadow") are
        /// switched off instead: set to Off they would start drawing in the colour passes (a second crown / hedge).
        /// </summary>
        static void CastNoShadow(Renderer r)
        {
            if (r.shadowCastingMode == ShadowCastingMode.ShadowsOnly) r.enabled = false;
            else r.shadowCastingMode = ShadowCastingMode.Off;
        }

        /// <summary>A tree's renderer: the tree object under "Trees" (LOD0) or its children (LOD1, shadow proxy).</summary>
        static bool IsTreeRenderer(Transform t)
        {
            var p = t.parent;
            return p != null && (p.name == "Trees" || (p.parent != null && p.parent.name == "Trees"));
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
