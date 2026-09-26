using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using House4696.Core;
using House4696.Lighting;
using House4696.Model;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace House4696.App
{
    /// <summary>
    /// Captures the reflection probes once the lighting of a rebuild is ready, spread over frames instead of all in
    /// one: one probe per frame (a room probe renders its six faces at once), the probe nearest the viewer first; the
    /// big garden probe one face per frame and only when the site changed (it does not see the house, so a new house
    /// leaves it as it was). Stills for the AI and thumbnails wait for it (<see cref="Busy"/>).
    /// <para>Realtime probes are switched on in the quality settings at start: the PC level had them off, so the
    /// probes were never captured and mirrors, chrome and glossy floors reflected the sky.</para>
    /// <para>Probe cameras render with the default renderer, which has no baked-GI resolve: the captured rooms had
    /// direct light and the flat ambient only. The resolve pass is injected into probe cameras
    /// (<see cref="BakedGIInReflections"/>), so reflections carry the same bounce light as the view.</para>
    /// </summary>
    public sealed class ReflectionCapture : IDisposable
    {
        // ---- tuning / A-B / rollback -------------------------------------------------------------------------
        /// <summary>Turn QualitySettings.realtimeReflectionProbes on at start (player only; editor: see ReflectionSetup).</summary>
        public static bool EnableRealtimeProbes = true;
        /// <summary>One probe per frame, nearest first (false = the old loop: every probe in one frame).</summary>
        public static bool Staggered = true;
        /// <summary>Room probes one face per frame (~9 frames each) instead of six faces in one frame.</summary>
        public static bool RoomProbesOneFacePerFrame = false;
        /// <summary>The 1024² garden probe one face per frame.</summary>
        public static bool GardenOneFacePerFrame = true;
        /// <summary>Capture the garden probe only when the site (landscape, sun, footprint) changed.</summary>
        public static bool GardenOnlyWhenSiteChanges = true;
        /// <summary>A time-sliced probe that never reports finished is left after this many frames.</summary>
        public static int MaxFramesPerSlicedProbe = 30;
        /// <summary>Resolve the baked GI in probe captures too (read when the capture is set up).</summary>
        public static bool BakedGIInReflections = true;

        /// <summary>True from the moment a capture is scheduled until every probe is done.</summary>
        public static bool Busy { get; private set; }

        readonly MonoBehaviour _host;
        readonly HouseSession _session;
        readonly ReflectionProbe _garden;
        int _generation;
        string _gardenKey;

        BakedGIFeature _giFeature;
        ScriptableRenderPass _giPass;
        ScriptableRenderer _giRenderer;

        public ReflectionCapture(MonoBehaviour host, HouseSession session, ReflectionProbe garden, HouseContent content)
        {
            _host = host; _session = session; _garden = garden;
            if (EnableRealtimeProbes && !Application.isEditor && !QualitySettings.realtimeReflectionProbes)
            {
                QualitySettings.realtimeReflectionProbes = true;
                Debug.Log("[Reflections] realtime reflection probes switched on");
            }
            if (BakedGIInReflections) InstallReflectionGI(content);
        }

        /// <summary>
        /// Captures after <paramref name="delayFrames"/> frames and then calls <paramref name="finished"/>; a newer
        /// call supersedes a pending one.
        /// </summary>
        public void Schedule(int delayFrames, Action finished)
        {
            int generation = ++_generation;
            Busy = true;
            _host.StartCoroutine(Run(generation, Mathf.Max(0, delayFrames), finished));
        }

        /// <summary>Drops a pending capture (the house it was for is being replaced).</summary>
        public void Cancel()
        {
            _generation++;
            Busy = false;
        }

        IEnumerator Run(int generation, int delayFrames, Action finished)
        {
            try
            {
                for (int i = 0; i < delayFrames; i++)
                {
                    yield return null;
                    if (generation != _generation) yield break;
                }
                float start = Time.realtimeSinceStartup;
                int frames = 0, count = 0;
                if (!Staggered)
                {
                    foreach (var p in Object.FindObjectsByType<ReflectionProbe>()) { p.RenderProbe(); count++; }
                    yield return null;
                    frames = 1;
                }
                else
                {
                    var probes = Collect(out string gardenKey);
                    foreach (var p in probes)
                    {
                        if (generation != _generation) yield break;
                        if (p == null || !p.isActiveAndEnabled) continue;
                        bool sliced = p.timeSlicingMode != ReflectionProbeTimeSlicingMode.NoTimeSlicing;
                        int id = p.RenderProbe();
                        count++;
                        int waited = 0;
                        // a probe that is not time-sliced is rendered with this frame; a sliced one reports when done
                        do { yield return null; waited++; }
                        while (sliced && generation == _generation && p != null && !p.IsFinishedRendering(id) && waited < MaxFramesPerSlicedProbe);
                        frames += waited;
                        if (p == _garden && generation == _generation) _gardenKey = gardenKey;
                    }
                }
                if (generation != _generation) yield break;
                Debug.Log($"[Reflections] {count} probe(s) captured over {frames} frame(s), {Time.realtimeSinceStartup - start:0.00} s");
                Busy = false;
                finished?.Invoke();
            }
            finally
            {
                if (generation == _generation) Busy = false;
            }
        }

        /// <summary>The probes to capture, nearest the viewer first (inside several: the smallest, i.e. the room, first).</summary>
        List<ReflectionProbe> Collect(out string gardenKey)
        {
            gardenKey = GardenKey();
            var list = new List<ReflectionProbe>();
            foreach (var p in Object.FindObjectsByType<ReflectionProbe>())
            {
                if (p == _garden || p.mode != ReflectionProbeMode.Realtime) continue;
                if (RoomProbesOneFacePerFrame) p.timeSlicingMode = ReflectionProbeTimeSlicingMode.IndividualFaces;
                list.Add(p);
            }
            if (_garden != null && _garden.isActiveAndEnabled && _garden.mode == ReflectionProbeMode.Realtime
                && (!GardenOnlyWhenSiteChanges || gardenKey != _gardenKey))
            {
                _garden.timeSlicingMode = GardenOneFacePerFrame ? ReflectionProbeTimeSlicingMode.IndividualFaces : ReflectionProbeTimeSlicingMode.NoTimeSlicing;
                list.Add(_garden);
            }
            var cam = Camera.main;
            var eye = cam != null ? cam.transform.position : Vector3.zero;
            var keys = new Dictionary<ReflectionProbe, (float distance, float volume)>(list.Count);
            foreach (var p in list)
            {
                var b = p.bounds;
                keys[p] = (b.SqrDistance(eye), b.size.x * b.size.y * b.size.z);
            }
            list.Sort((a, b) =>
            {
                var ka = keys[a]; var kb = keys[b];
                int c = ka.distance.CompareTo(kb.distance);
                return c != 0 ? c : ka.volume.CompareTo(kb.volume);
            });
            return list;
        }

        /// <summary>What the garden probe depends on: the site preset, the sun and the house footprint (paths, apron, trees).</summary>
        string GardenKey()
        {
            var site = _session.Doc?.Site ?? new SiteDef();
            var fp = _session.Result != null ? _session.Result.Footprint : default;
            return string.Format(CultureInfo.InvariantCulture, "{0}|{1:0.##}|{2:0.##}|{3:0.##}|{4:0.##}|{5:0.##}|{6:0.##}",
                site.Landscape, site.SunAzimuth, site.SunElevation, fp.xMin, fp.yMin, fp.xMax, fp.yMax);
        }

        // ---- baked GI in probe captures ------------------------------------------------------------------------

        /// <summary>
        /// A private copy of the viewer's <see cref="BakedGIFeature"/> whose resolve pass is enqueued into the renderer
        /// of every reflection-probe camera (they have no camera data, so URP gives them the default renderer). The
        /// wrapper records nothing for other cameras, so the plan stills on the same renderer stay unchanged.
        /// </summary>
        void InstallReflectionGI(HouseContent content)
        {
            if (!(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)) return;
            var source = FindViewerFeature(urp, out int giRendererIndex);
            var shader = source != null && source.resolveShader != null ? source.resolveShader : content != null && content.BakedGI != null ? content.BakedGI.Resolve : null;
            if (shader == null) return;
            var feature = ScriptableObject.CreateInstance<BakedGIFeature>();
            feature.name = "BakedGI (reflection probes)";
            feature.hideFlags = HideFlags.HideAndDontSave;
            feature.resolveShader = shader;
            if (source != null)
            {
                feature.normalBias = source.normalBias;
                feature.viewBias = source.viewBias;
                feature.fadeDistance = source.fadeDistance;
            }
            feature.Create();
            var inner = typeof(BakedGIFeature).GetField("_pass", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(feature) as ScriptableRenderPass;
            if (inner == null)
            {
                Debug.LogWarning("[Reflections] BakedGIFeature has no _pass field any more: probe captures stay without baked GI");
                Object.Destroy(feature);
                return;
            }
            _giFeature = feature;
            _giPass = new ReflectionOnlyPass(inner);
            _giRenderer = giRendererIndex >= 0 ? urp.GetRenderer(giRendererIndex) : null;
            RenderPipelineManager.beginCameraRendering += OnBeginCamera;
        }

        static BakedGIFeature FindViewerFeature(UniversalRenderPipelineAsset urp, out int rendererIndex)
        {
            var list = urp.rendererDataList;
            for (int i = 0; i < list.Length; i++)
            {
                var rd = list[i];
                if (rd == null) continue;
                foreach (var f in rd.rendererFeatures)
                    if (f is BakedGIFeature b) { rendererIndex = i; return b; }
            }
            rendererIndex = -1;
            return null;
        }

        void OnBeginCamera(ScriptableRenderContext context, Camera camera)
        {
            if (camera.cameraType != CameraType.Reflection || _giPass == null || !BakedGIInReflections || BakedGIVolume.Active == null) return;
            if (!(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)) return;
            // URP renders non-game cameras without camera data, i.e. with the default renderer (GetRenderer)
            var renderer = urp.scriptableRenderer;
            if (renderer == null || renderer == _giRenderer) return;   // the GI renderer resolves reflection cameras itself
            renderer.EnqueuePass(_giPass);
        }

        /// <summary>Runs the baked-GI resolve for reflection-probe cameras only.</summary>
        sealed class ReflectionOnlyPass : ScriptableRenderPass
        {
            readonly ScriptableRenderPass _inner;

            public ReflectionOnlyPass(ScriptableRenderPass inner)
            {
                _inner = inner;
                renderPassEvent = inner.renderPassEvent;
                ConfigureInput(ScriptableRenderPassInput.Depth | ScriptableRenderPassInput.Normal);
            }

            public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
            {
                if (frameData.Get<UniversalCameraData>().cameraType != CameraType.Reflection) return;
                _inner.RecordRenderGraph(renderGraph, frameData);
            }
        }

        public void Dispose()
        {
            _generation++;
            Busy = false;
            if (_giPass != null) RenderPipelineManager.beginCameraRendering -= OnBeginCamera;
            _giPass = null;
            if (_giFeature != null)
            {
                _giFeature.Dispose();
                Object.Destroy(_giFeature);
                _giFeature = null;
            }
        }
    }
}
