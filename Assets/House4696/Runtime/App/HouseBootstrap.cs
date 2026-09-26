using System.Collections;
using House4696.App.UI;
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
    /// the MCP server drives, and the interface (<see cref="AppUI"/>). Opens the last project on start, re-captures
    /// reflection probes once the lighting of a rebuild is ready and renders the project preview for the list.
    /// </summary>
    public sealed class HouseBootstrap : MonoBehaviour
    {
        public const string Version = "0.4.0";

        [SerializeField] Camera loadingCamera;
        [Tooltip("Project opened when nothing was opened before (id in the project store).")]
        [SerializeField] string defaultProject = "46-96";
        [Tooltip("Frames to let the realtime GI converge before the reflection probes are captured.")]
        [SerializeField] int giWarmupFrames = 60;
        [SerializeField] bool enableApi = true;

        public HouseSession Session { get; private set; }
        public LocalApi Api { get; private set; }
        public HouseLighting Lighting { get; private set; }
        public AppSettings Settings { get; } = new AppSettings();

        ApiHandlers _handlers;
        AppUI _ui;
        ReflectionCapture _reflections;
        Thumbnails _thumbs;
        HouseLighting.State _lightingState;
        System.Action<LocalApi.Call> _execute;
        readonly FramePacing _pacing = new FramePacing();

        void Awake()
        {
            _ui = gameObject.AddComponent<AppUI>();                 // the splash is up from the first frame
            _execute = Execute;
        }

        IEnumerator Start()
        {
            Application.runInBackground = true;      // the AI edits the house while another window has focus
            _pacing.ApplyFocusedPolicy();
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
            // ---- perf plan step 8: lamp shadow budget for the viewer camera (LampShadowBudget.Enabled = false turns it off)
            gameObject.AddComponent<LampShadowBudget>().Init(Session);
            // ---- end lamp shadow budget
            var renderer = new ViewRenderer(Session, content.RealtimeGIRendererIndex);
            var thumbs = _thumbs = new Thumbnails(Session, renderer, this);
            // reflections are captured with the finished lighting: after the bake, or after the realtime GI settled,
            // one probe per frame; the preview for the project list once they are all done
            _reflections = new ReflectionCapture(this, Session, garden, content);
            Lighting.Baked += () => _reflections.Schedule(2, () => thumbs.Capture());
            Session.Rebuilt += () =>
            {
                _reflections.Cancel();               // the old house's probes are gone; the new ones wait for the new lighting
                Lighting.Rebake();
                _lightingState = Lighting.Current;   // a bake failing later is caught by WatchBakeFailure
                if (!Lighting.CanBake || Lighting.Current == HouseLighting.State.Failed)
                    _reflections.Schedule(giWarmupFrames, () => thumbs.Capture());
            };
            string last = PlayerPrefs.GetString(HouseSession.LastProjectPref, defaultProject);
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
                _handlers = new ApiHandlers(Session, renderer, Lighting, this, Version);
            }
            _ui.Bind(new AppServices
            {
                Session = Session, Lighting = Lighting, Api = Api, Thumbs = thumbs, Settings = Settings, Version = Version,
                Snapshots = new Snapshots(Session, renderer, Lighting),
                Viewer = Camera.main != null ? Camera.main.GetComponent<House4696.Runtime.HouseViewer>() : null,
            });
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
            UpdateRenderScale();
            Api?.Pump(_execute);
            WatchBakeFailure();
            _pacing.Tick(Api, Lighting);
        }

        /// <summary>Every API call runs through here: the frame pacing holds full speed until its result is set.</summary>
        void Execute(LocalApi.Call call)
        {
            _pacing.Track(call);
            _handlers.Execute(call);
        }

        /// <summary>
        /// A failed bake falls back to the realtime GI and raises no <see cref="HouseLighting.Baked"/>, while the
        /// rebuild already dropped the pending capture: capture once the realtime GI settled, as without a bake.
        /// </summary>
        void WatchBakeFailure()
        {
            if (Lighting == null || _reflections == null) return;
            var state = Lighting.Current;
            if (state == _lightingState) return;
            _lightingState = state;
            if (state == HouseLighting.State.Failed) _reflections.Schedule(giWarmupFrames, () => _thumbs?.Capture());
        }

        /// <summary>Diagnostics (PerfProbe tune/bench) pin the render scale and upscaler; the automatic choice stays off meanwhile.</summary>
        public static bool PinRenderScale;

        /// <summary>
        /// A fullscreen Retina window has 4× the pixels of the same window at 1×: render about the quality setting's
        /// megapixels and let FSR upscale (with sharpening) to the screen. Player only — in the editor the pipeline
        /// asset would keep the change. Left alone while a still renders (it sets its own scale per frame).
        /// </summary>
        void UpdateRenderScale()
        {
            if (Application.isEditor || PinRenderScale || ViewRenderer.Busy) return;
            if (!(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)) return;
            float pixels = (float)Screen.width * Screen.height;
            if (pixels <= 0f) return;
            float scale = Mathf.Clamp(Mathf.Sqrt(Settings.TargetMegapixels * 1e6f / pixels), 0.4f, 1f);
            scale = Mathf.Round(scale * 20f) / 20f;
            bool stp = Settings.UseStp;
            var filter = stp ? UpscalingFilterSelection.STP : scale < 0.99f ? UpscalingFilterSelection.FSR : UpscalingFilterSelection.Auto;
            if (urp.msaaSampleCount != 1) urp.msaaSampleCount = 1;
            var cam = Camera.main;
            var data = cam != null ? cam.GetUniversalAdditionalCameraData() : null;
            var aa = stp ? AntialiasingMode.None : AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            if (data != null && data.antialiasing != aa) data.antialiasing = aa;
            if (Mathf.Abs(urp.renderScale - scale) < 0.01f && urp.upscalingFilter == filter) return;
            urp.renderScale = scale;
            urp.upscalingFilter = filter;
        }

        Vector3 _lastCamPos;
        Quaternion _lastCamRot;

        /// <summary>
        /// Temporal upscaling keeps a history of past frames: after a jump (teleport to a room, viewpoint, project
        /// switch) the old history would ghost into the new view, so it is dropped.
        /// </summary>
        void LateUpdate()
        {
            var cam = Camera.main;
            if (cam == null) return;
            var t = cam.transform;
            bool jump = (t.position - _lastCamPos).sqrMagnitude > 1f || Quaternion.Angle(t.rotation, _lastCamRot) > 30f;
            if (jump) cam.GetUniversalAdditionalCameraData().resetHistory = true;
            _lastCamPos = t.position;
            _lastCamRot = t.rotation;
        }

        void OnDestroy()
        {
            Api?.Dispose();
            _reflections?.Dispose();
        }

        void OnApplicationQuit() => Api?.Dispose();
    }
}
