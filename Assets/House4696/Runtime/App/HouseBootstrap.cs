using System.Collections;
using System.Diagnostics;
using House4696.Core;
using House4696.House;
using House4696.Landscape;
using House4696.Setup;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Debug = UnityEngine.Debug;

namespace House4696.App
{
    /// <summary>
    /// Stage-0 prototype entry point: generates the house, garden and environment inside the player (no editor,
    /// no baked data) and lights them with realtime Surface Cache GI. Reflection probes are captured once the GI
    /// has had time to converge.
    /// </summary>
    public sealed class HouseBootstrap : MonoBehaviour
    {
        [SerializeField] Camera loadingCamera;
        [Tooltip("Frames to let the realtime GI converge before the reflection probes are captured.")]
        [SerializeField] int giWarmupFrames = 90;
        [SerializeField] bool showStats = true;

        public GameObject House { get; private set; }
        public bool IsReady { get; private set; }
        public string BuildReport { get; private set; } = "";

        string _status = "Сборка дома…";
        float _fps;

        IEnumerator Start()
        {
            yield return null; // show the loading frame before the main thread is busy
            var sw = Stopwatch.StartNew();
            var content = HouseContent.Load();
            var mats = MaterialLibrary.Create();
            long tMats = sw.ElapsedMilliseconds;

            var writer = new SceneWriter();
            House = new HouseGenerator(mats, writer).Build();
            long tHouse = sw.ElapsedMilliseconds;
            var landscape = new LandscapeGenerator(mats, writer, CameraSpec.Position, CameraSpec.Forward).Build();
            long tLand = sw.ElapsedMilliseconds;
            int colliders = CollisionSetup.Apply(House, landscape);
            var env = EnvironmentBuilder.Build(mats, content.PostProcessProfile);
            long tEnv = sw.ElapsedMilliseconds;

            SetupReflections(House, env);
            SetupRealtimeGI(content);
            if (loadingCamera != null) Destroy(loadingCamera.gameObject);

            BuildReport = $"materials {tMats} ms, house {tHouse - tMats} ms, garden {tLand - tHouse} ms, " +
                          $"colliders+env {tEnv - tLand} ms ({colliders} colliders)";
            Debug.Log("[HouseBootstrap] built: " + BuildReport);

            _status = "Расчёт освещения…";
            for (int i = 0; i < giWarmupFrames; i++) yield return null;
            foreach (var p in FindObjectsByType<ReflectionProbe>()) p.RenderProbe();
            yield return null;
            _status = null;
            IsReady = true;
            Debug.Log($"[HouseBootstrap] ready in {sw.ElapsedMilliseconds} ms");
        }

        /// <summary>
        /// Same split as the editor build: the house lives on its own layer that the garden probe skips (the
        /// glazing must not reflect the house itself). Probes render in realtime, on demand.
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
