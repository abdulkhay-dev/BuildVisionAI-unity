using System.Collections;
using System.Diagnostics;
using System.IO;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using House4696.Setup;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Debug = UnityEngine.Debug;

namespace House4696.App
{
    /// <summary>
    /// App entry point (prototype): loads a house document, generates the house, site and environment inside the
    /// player (no editor, no baked data) and lights them with realtime Surface Cache GI. Reflection probes are
    /// captured once the GI has had time to converge.
    /// </summary>
    public sealed class HouseBootstrap : MonoBehaviour
    {
        [SerializeField] Camera loadingCamera;
        [Tooltip("House document, relative to StreamingAssets (or an absolute path).")]
        [SerializeField] string project = "Samples/46-96.house.json";
        [Tooltip("Frames to let the realtime GI converge before the reflection probes are captured.")]
        [SerializeField] int giWarmupFrames = 90;
        [SerializeField] bool showStats = true;

        public HouseDocument Document { get; private set; }
        public HouseBuildResult Result { get; private set; }
        public bool IsReady { get; private set; }
        public string BuildReport { get; private set; } = "";

        string _status = "Сборка дома…";
        float _fps;

        IEnumerator Start()
        {
            yield return null; // show the loading frame before the main thread is busy
            var sw = Stopwatch.StartNew();
            string path = Path.IsPathRooted(project) ? project : Path.Combine(Application.streamingAssetsPath, project);
            try { Document = HouseJson.Deserialize(File.ReadAllText(path)); }
            catch (System.Exception e)
            {
                _status = "Не удалось открыть проект: " + e.Message;
                Debug.LogError("[HouseBootstrap] " + e);
                yield break;
            }
            var content = HouseContent.Load();
            var mats = MaterialLibrary.Create();
            long tLoad = sw.ElapsedMilliseconds;

            Result = HouseBuilder.Build(Document, mats, new SceneWriter());
            long tHouse = sw.ElapsedMilliseconds;
            var site = Document.Site;
            var env = EnvironmentBuilder.Build(mats, content.PostProcessProfile, EnvironmentBuilder.SunFrom(site.SunAzimuth, site.SunElevation));
            ConfigureViewer();
            SetupReflections(Result.House, env);
            SetupRealtimeGI(content);
            if (loadingCamera != null) Destroy(loadingCamera.gameObject);

            BuildReport = $"{Document.Meta.Name}: load {tLoad} ms, build {tHouse - tLoad} ms, {Result.Colliders} colliders" +
                          (Result.Warnings.Count > 0 ? $", {Result.Warnings.Count} warnings" : "");
            Debug.Log("[HouseBootstrap] built: " + BuildReport);

            _status = "Расчёт освещения…";
            for (int i = 0; i < giWarmupFrames; i++) yield return null;
            foreach (var p in FindObjectsByType<ReflectionProbe>()) p.RenderProbe();
            yield return null;
            _status = null;
            IsReady = true;
            Debug.Log($"[HouseBootstrap] ready in {sw.ElapsedMilliseconds} ms");
        }

        /// <summary>Tour stops and orbit presets of the document (the viewer keeps its defaults when there are none).</summary>
        void ConfigureViewer()
        {
            var cam = Camera.main;
            var viewer = cam != null ? cam.GetComponent<HouseViewer>() : null;
            if (viewer == null) return;
            var walk = Result.Walk.Length > 0 ? Result.Walk : new[] { new WalkPoint { Name = "Вход", Feet = new Vector3(Result.Footprint.center.x, 0.05f, Result.Footprint.yMin - 3f) } };
            viewer.Configure(Result.Pivot, walk, Result.Orbit);
        }

        /// <summary>
        /// The house lives on its own layer that the garden probe skips (the glazing must not reflect the house
        /// itself). Probes render in realtime, on demand.
        /// </summary>
        static void SetupReflections(GameObject house, GameObject env)
        {
            int layer = LayerMask.NameToLayer("House");
            if (layer >= 0)
                foreach (var t in house.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            foreach (var p in FindObjectsByType<ReflectionProbe>())
            {
                p.mode = ReflectionProbeMode.Realtime;
                p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
                p.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            }
            var garden = env.GetComponentInChildren<ReflectionProbe>();
            if (garden != null && layer >= 0) garden.cullingMask = ~(1 << layer);
            DynamicGI.UpdateEnvironment();
        }

        static void SetupRealtimeGI(HouseContent content)
        {
            if (content.RealtimeGIProfile != null)
            {
                var go = new GameObject("RealtimeGI_Volume");
                var vol = go.AddComponent<Volume>();
                vol.isGlobal = true;
                vol.priority = 10;
                vol.sharedProfile = content.RealtimeGIProfile;
            }
            var cam = Camera.main;
            if (cam != null && content.RealtimeGIRendererIndex >= 0)
                cam.GetUniversalAdditionalCameraData().SetRenderer(content.RealtimeGIRendererIndex);
        }

        void Update()
        {
            if (Time.unscaledDeltaTime > 0f) _fps = Mathf.Lerp(_fps, 1f / Time.unscaledDeltaTime, 0.05f);
        }

        void OnGUI()
        {
            if (_status != null)
            {
                var style = new GUIStyle(GUI.skin.label) { fontSize = 28, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(0, 0, Screen.width, Screen.height), _status, style);
            }
            else if (showStats)
            {
                GUI.Label(new Rect(12, Screen.height - 28, 900, 24), $"{_fps:F0} FPS · {BuildReport}");
            }
        }
    }
}
