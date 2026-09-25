using System;
using UnityEngine;

namespace House4696.Runtime
{
    /// <summary>Named standing position for walking tours (feet on the floor, view direction).</summary>
    [Serializable]
    public struct WalkPoint
    {
        public string Name;
        public Vector3 Feet;
        public float Yaw, Pitch;
    }

    /// <summary>Named orbit angle around the house pivot.</summary>
    [Serializable]
    public struct OrbitPoint
    {
        public string Name;
        public float Yaw, Pitch, Distance;
    }

    /// <summary>
    /// Play-mode camera controller for touring the house. Owns the view modes (walk, orbit, fly), switches
    /// between them with Tab, jumps to viewpoints with 1–9, restores the calibrated reference shot with R
    /// and draws a small help overlay (H hides it). In a player build F11 toggles fullscreen and F10 quits.
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public sealed class HouseViewer : MonoBehaviour
    {
        public enum Mode { Walk, Orbit, Fly }

        [SerializeField] Mode startMode = Mode.Walk;
        [SerializeField] WalkMode walk = new WalkMode();
        [SerializeField] OrbitMode orbit = new OrbitMode();
        [SerializeField] FlyMode fly = new FlyMode();
        [SerializeField] WalkPoint[] walkPoints = new WalkPoint[0];
        [SerializeField] OrbitPoint[] orbitPoints = new OrbitPoint[0];
        [SerializeField] bool showHelp = true;

        Camera _cam;
        ViewMode _current;
        Mode _mode;
        LensState _reference;
        string _toast;
        float _toastUntil;
        GUIStyle _panel, _title, _text, _center;

        /// <summary>Called by the scene generator with house-specific data.</summary>
        public void Configure(Vector3 orbitPivot, WalkPoint[] walkTour, OrbitPoint[] orbitPresets)
        {
            orbit.Pivot = orbitPivot;
            walkPoints = walkTour;
            orbitPoints = orbitPresets;
        }

        void Awake()
        {
            _cam = GetComponent<Camera>();
            _reference = LensState.Capture(_cam);
            walk.Bind(_cam, transform);
            orbit.Bind(_cam, transform);
            fly.Bind(_cam, transform);

            // the walk starts where the reference camera stands, looking the same way
            var t = _cam.transform;
            walk.SetSpawn(new WalkPoint { Name = "Старт", Feet = GroundBelow(t.position), Yaw = t.eulerAngles.y, Pitch = 0f });
        }

        void Start() => SwitchTo(startMode);

        void OnDisable()
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }

        void Update()
        {
            var kb = ViewerInput.Kb;
            if (kb != null)
            {
                if (kb.tabKey.wasPressedThisFrame) SwitchTo((Mode)(((int)_mode + 1) % 3));
                if (kb.rKey.wasPressedThisFrame) ShowReference();
                if (kb.hKey.wasPressedThisFrame) showHelp = !showHelp;
                if (kb.f11Key.wasPressedThisFrame) Screen.fullScreen = !Screen.fullScreen;
                if (kb.f10Key.wasPressedThisFrame && !Application.isEditor) Application.Quit();
                for (int i = 0; i < 9; i++)
                    if (kb[UnityEngine.InputSystem.Key.Digit1 + i].wasPressedThisFrame) GoToPoint(i);
            }
            UpdateCursor();
            _current?.Tick(Time.deltaTime);
        }

        public void SwitchTo(Mode mode)
        {
            _current?.Exit();
            _mode = mode;
            _current = mode == Mode.Walk ? walk : mode == Mode.Orbit ? (ViewMode)orbit : fly;
            _current.Enter();
            Toast(_current.Title);
        }

        /// <summary>Calibrated reference shot: physical lens with vertical shift; stays in fly mode.</summary>
        void ShowReference()
        {
            _current?.Exit();
            _mode = Mode.Fly;
            _current = fly;
            _reference.Apply(_cam);
            fly.Enter(keepLens: true);
            Toast("Ракурс референса");
        }

        void GoToPoint(int i)
        {
            if (_mode == Mode.Orbit)
            {
                if (i >= orbitPoints.Length) return;
                orbit.GoTo(orbitPoints[i]);
                Toast(orbitPoints[i].Name);
            }
            else
            {
                if (i >= walkPoints.Length) return;
                _current.GoTo(walkPoints[i]);
                Toast(walkPoints[i].Name);
            }
        }

        void UpdateCursor()
        {
            if (!_current.CapturesCursor)
            {
                if (Cursor.lockState != CursorLockMode.None) { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
                return;
            }
            var kb = ViewerInput.Kb;
            var mouse = ViewerInput.Mouse;
            if (kb != null && kb.escapeKey.wasPressedThisFrame) { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
            else if (mouse != null && mouse.leftButton.wasPressedThisFrame && Cursor.lockState != CursorLockMode.Locked)
            {
                Cursor.lockState = CursorLockMode.Locked;
                Cursor.visible = false;
            }
        }

        static Vector3 GroundBelow(Vector3 p)
        {
            return Physics.Raycast(p + Vector3.up * 2f, Vector3.down, out var hit, 50f, ~(1 << 2), QueryTriggerInteraction.Ignore)
                ? hit.point : new Vector3(p.x, 0f, p.z);
        }

        void Toast(string text) { _toast = text; _toastUntil = Time.unscaledTime + 1.6f; }

        // ------------------------------------------------------------------ overlay
        void OnGUI()
        {
            if (_current == null) return;
            EnsureStyles();
            float scale = Mathf.Max(0.75f, Screen.height / 1080f);
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1f));
            float w = Screen.width / scale, h = Screen.height / scale;

            bool locked = Cursor.lockState == CursorLockMode.Locked;
            if (_mode == Mode.Walk && locked) GUI.Label(new Rect(w * 0.5f - 10, h * 0.5f - 12, 20, 24), "·", _center);
            if (_mode == Mode.Walk && !locked) GUI.Label(new Rect(0, h * 0.5f - 20, w, 40), "Кликните, чтобы управлять взглядом", _center);

            string prompt = _current.Prompt;
            if (prompt != null) GUI.Label(new Rect(0, h * 0.62f, w, 40), prompt, _center);
            if (Time.unscaledTime < _toastUntil) GUI.Label(new Rect(0, 40, w, 40), _toast, _center);

            if (!showHelp) { GUI.Label(new Rect(16, h - 40, 400, 30), "H — подсказки", _text); return; }

            var lines = new System.Collections.Generic.List<string>(_current.Help);
            lines.Add("");
            if (_mode == Mode.Orbit)
                for (int i = 0; i < orbitPoints.Length && i < 9; i++) lines.Add((i + 1) + " — " + orbitPoints[i].Name);
            else
                for (int i = 0; i < walkPoints.Length && i < 9; i++) lines.Add((i + 1) + " — " + walkPoints[i].Name);
            lines.Add("");
            lines.Add("Tab — сменить режим, R — ракурс референса, H — скрыть");
            if (!Application.isEditor) lines.Add("F11 — полный экран / окно, F10 — выход");

            const float lineH = 24f, pad = 14f;
            var box = new Rect(16, 16, 560, pad * 2 + 34 + lines.Count * lineH);
            GUI.Box(box, GUIContent.none, _panel);
            GUI.Label(new Rect(box.x + pad, box.y + pad, box.width, 30), _current.Title, _title);
            for (int i = 0; i < lines.Count; i++)
                GUI.Label(new Rect(box.x + pad, box.y + pad + 34 + i * lineH, box.width - pad * 2, lineH), lines[i], _text);
        }

        void EnsureStyles()
        {
            if (_panel != null) return;
            var bg = new Texture2D(1, 1) { hideFlags = HideFlags.HideAndDontSave };
            bg.SetPixel(0, 0, new Color(0.06f, 0.07f, 0.08f, 0.62f));
            bg.Apply();
            _panel = new GUIStyle { normal = { background = bg } };
            _title = new GUIStyle { fontSize = 22, fontStyle = FontStyle.Bold, normal = { textColor = Color.white } };
            _text = new GUIStyle { fontSize = 16, normal = { textColor = new Color(0.9f, 0.92f, 0.94f) } };
            _center = new GUIStyle
            {
                fontSize = 22, fontStyle = FontStyle.Bold, alignment = TextAnchor.MiddleCenter,
                normal = { textColor = Color.white },
            };
        }

        /// <summary>Snapshot of the camera pose and lens, so the calibrated physical camera can be restored.</summary>
        struct LensState
        {
            Vector3 _pos;
            Quaternion _rot;
            bool _physical;
            float _focal, _fov, _near;
            Vector2 _sensor, _shift;
            Camera.GateFitMode _gate;

            public static LensState Capture(Camera c) => new LensState
            {
                _pos = c.transform.position, _rot = c.transform.rotation, _physical = c.usePhysicalProperties,
                _focal = c.focalLength, _fov = c.fieldOfView, _near = c.nearClipPlane,
                _sensor = c.sensorSize, _shift = c.lensShift, _gate = c.gateFit,
            };

            public void Apply(Camera c)
            {
                c.transform.SetPositionAndRotation(_pos, _rot);
                c.usePhysicalProperties = _physical;
                c.nearClipPlane = _near;
                if (_physical)
                {
                    c.sensorSize = _sensor;
                    c.gateFit = _gate;
                    c.focalLength = _focal;
                    c.lensShift = _shift;
                }
                else c.fieldOfView = _fov;
            }
        }
    }
}
