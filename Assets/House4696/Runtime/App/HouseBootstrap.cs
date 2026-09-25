using System.Collections;
using House4696.Core;
using House4696.Setup;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.App
{
    /// <summary>
    /// App composition root: project store, the open-project session, the environment (sun, sky, post, viewer
    /// camera), the lighting (GI baked on the GPU after every rebuild, realtime GI as the fallback) and the local API
    /// the MCP server drives. Opens the last project on start and re-captures reflection probes once the lighting of
    /// a rebuild is ready.
    /// </summary>
    public sealed class HouseBootstrap : MonoBehaviour
    {
        public const string Version = "0.3.0";

        [SerializeField] Camera loadingCamera;
        [Tooltip("Project opened when nothing was opened before (id in the project store).")]
        [SerializeField] string defaultProject = "46-96";
        [Tooltip("Frames to let the realtime GI converge before the reflection probes are captured.")]
        [SerializeField] int giWarmupFrames = 60;
        [SerializeField] bool showStats = true;
        [SerializeField] bool enableApi = true;

        public HouseSession Session { get; private set; }
        public LocalApi Api { get; private set; }
        public HouseLighting Lighting { get; private set; }

        ApiHandlers _handlers;
        string _status = "Загрузка…";
        float _fps;
        int _probeCountdown = -1;

        IEnumerator Start()
        {
            Application.runInBackground = true;      // the AI edits the house while another window has focus
            yield return null;                       // show the loading frame first

            var content = HouseContent.Load();
            var mats = MaterialLibrary.Create();
            EnvironmentBuilder.Build(mats, content.PostProcessProfile);
            SetupRealtimeGI(content);
            var garden = GameObject.Find("ReflectionProbe_Garden")?.GetComponent<ReflectionProbe>();
            int layer = LayerMask.NameToLayer("House");
            if (garden != null)
            {
                garden.mode = ReflectionProbeMode.Realtime;
                garden.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
                if (layer >= 0) garden.cullingMask = ~(1 << layer);
            }
            DynamicGI.UpdateEnvironment();

            Session = new HouseSession(new ProjectStore(), mats);
            Lighting = new HouseLighting(this, Session, content);
            // reflections are captured with the finished lighting: after the bake, or after the realtime GI settled
            Lighting.Baked += () => _probeCountdown = 2;
            Session.Rebuilt += () =>
            {
                Lighting.Rebake();
                if (!Lighting.CanBake) _probeCountdown = giWarmupFrames;
            };
            string last = PlayerPrefs.GetString("house.lastProject", defaultProject);
            if (!Session.Store.Exists(last)) last = Session.Store.Exists(defaultProject) ? defaultProject : Session.Store.List().Find(p => p.Id != null)?.Id;
            if (last != null)
            {
                try { Session.Open(last); }
                catch (System.Exception e) { Debug.LogError("[App] open failed: " + e); }
            }
            if (loadingCamera != null) Destroy(loadingCamera.gameObject);

            if (enableApi)
            {
                Api = new LocalApi();
                Api.Start(Version);
                _handlers = new ApiHandlers(Session, new ViewRenderer(Session, content.RealtimeGIRendererIndex), Lighting, this, Version);
            }
            _status = null;
            Debug.Log($"[App] ready: project '{Session.ProjectId}', built in {Session.LastBuildMs} ms, api port {Api?.Port}");
        }

        static void SetupRealtimeGI(HouseContent content)
        {
            if (content.RealtimeGIProfile != null)
            {
                var vol = new GameObject("RealtimeGI_Volume").AddComponent<Volume>();
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
            Api?.Pump(_handlers.Execute);
            if (_probeCountdown > 0 && --_probeCountdown == 0)
                foreach (var p in FindObjectsByType<ReflectionProbe>()) p.RenderProbe();
        }

        void OnDestroy() => Api?.Dispose();
        void OnApplicationQuit() => Api?.Dispose();

        void OnGUI()
        {
            if (_status != null)
            {
                var style = new GUIStyle(GUI.skin.label) { fontSize = 28, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(0, 0, Screen.width, Screen.height), _status, style);
            }
            else if (showStats && Session != null)
            {
                string project = Session.HasProject ? $"{Session.Doc.Meta?.Name} ({Session.ProjectId})" : "проект не открыт";
                string api = Api != null ? $" · MCP API :{Api.Port}" : "";
                GUI.Label(new Rect(12, Screen.height - 28, 1200, 24), $"{_fps:F0} FPS · {project} · сборка {Session.LastBuildMs} мс · {Lighting?.StatusText()}{api}");
            }
        }
    }
}
