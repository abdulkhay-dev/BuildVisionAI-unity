using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace House4696.Runtime
{
    /// <summary>
    /// Showroom inspection: the camera orbits a pivot on the house. LMB rotates, RMB/MMB pans, the wheel
    /// zooms; presets fly smoothly to fixed angles; after a pause without input the view slowly turns.
    /// </summary>
    [Serializable]
    public sealed class OrbitMode : ViewMode
    {
        [SerializeField] Vector3 pivot = new Vector3(7.3f, 3.2f, 5.6f);
        [SerializeField] float minDistance = 3f;
        [SerializeField] float maxDistance = 90f;
        [SerializeField] float minPitch = -10f, maxPitch = 85f;
        [SerializeField] float rotateSensitivity = 0.25f;
        [SerializeField] float keyRotateSpeed = 70f;
        [SerializeField] float panSensitivity = 0.0012f;
        [SerializeField] float fov = 45f;
        [SerializeField] float smoothing = 10f;
        [SerializeField, Tooltip("Seconds without input before the slow turntable starts (0 = off)")] float idleSpin = 12f;
        [SerializeField] float spinSpeed = 5f;

        // desired (target) and current (smoothed) orbit state
        float _yaw, _pitch, _dist, _cYaw, _cPitch, _cDist;
        Vector3 _target, _cTarget;
        float _idle;

        public override string Title => "Осмотр дома";
        public override string[] Help => new[]
        {
            "ЛКМ — вращать, ПКМ / колесо (зажать) — сдвиг, колесо — зум",
            "WASD / стрелки — вращать, F — вернуться к центру дома",
        };

        public Vector3 Pivot { get => pivot; set => pivot = value; }

        public override void Enter()
        {
            UseGameLens(fov);
            // start from the current camera position so the switch has no jump in position
            _target = pivot;
            Vector3 dir = Cam.transform.position - _target;
            _dist = Mathf.Clamp(dir.magnitude, 12f, maxDistance);
            _yaw = Mathf.Atan2(-dir.x, -dir.z) * Mathf.Rad2Deg;
            _pitch = Mathf.Clamp(Mathf.Asin(Mathf.Clamp(dir.y / Mathf.Max(dir.magnitude, 0.01f), -1f, 1f)) * Mathf.Rad2Deg, 5f, maxPitch);
            Snap();
            _idle = 0f;
        }

        /// <summary>Animates to a preset angle around the pivot.</summary>
        public void GoTo(OrbitPoint p)
        {
            _target = pivot;
            _yaw = _cYaw + Mathf.DeltaAngle(_cYaw, p.Yaw); // shortest way round
            _pitch = Mathf.Clamp(p.Pitch, minPitch, maxPitch);
            _dist = Mathf.Clamp(p.Distance, minDistance, maxDistance);
            _idle = 0f;
        }

        /// <summary>Walk points are not orbit presets: orbit around the pivot from that side instead.</summary>
        public override void GoTo(WalkPoint p)
        {
            Vector3 d = p.Feet - pivot;
            GoTo(new OrbitPoint { Yaw = Mathf.Atan2(-d.x, -d.z) * Mathf.Rad2Deg, Pitch = 15f, Distance = Mathf.Max(d.magnitude, 12f) });
        }

        void Snap()
        {
            _cYaw = _yaw; _cPitch = _pitch; _cDist = _dist; _cTarget = _target;
            Apply();
        }

        public override void Tick(float dt)
        {
            bool input = false;

            Vector2 delta = ViewerInput.MouseDelta;
            if (ViewerInput.LeftHeld)
            {
                _yaw += delta.x * rotateSensitivity;
                _pitch -= delta.y * rotateSensitivity;
                input = true;
            }
            else if (ViewerInput.RightHeld || ViewerInput.MiddleHeld)
            {
                var t = Cam.transform;
                _target -= (t.right * delta.x + t.up * delta.y) * (panSensitivity * _cDist);
                input = true;
            }

            Vector2 keys = ViewerInput.Move();
            if (keys != Vector2.zero)
            {
                _yaw -= keys.x * keyRotateSpeed * dt;
                _pitch += keys.y * keyRotateSpeed * 0.5f * dt;
                input = true;
            }

            float scroll = ViewerInput.ScrollSign;
            if (scroll != 0f) { _dist *= scroll > 0 ? 0.88f : 1.14f; input = true; }
            if (ViewerInput.Down(Key.F)) { _target = pivot; input = true; }

            _idle = input ? 0f : _idle + dt;
            if (idleSpin > 0f && _idle > idleSpin) _yaw += spinSpeed * dt;

            _pitch = Mathf.Clamp(_pitch, minPitch, maxPitch);
            _dist = Mathf.Clamp(_dist, minDistance, maxDistance);

            float k = Damp(smoothing, dt);
            _cYaw = Mathf.Lerp(_cYaw, _yaw, k);
            _cPitch = Mathf.Lerp(_cPitch, _pitch, k);
            _cDist = Mathf.Lerp(_cDist, _dist, k);
            _cTarget = Vector3.Lerp(_cTarget, _target, k);
            Apply();
        }

        void Apply()
        {
            var rot = Quaternion.Euler(_cPitch, _cYaw, 0f);
            Vector3 pos = _cTarget - rot * Vector3.forward * _cDist;
            pos.y = Mathf.Max(pos.y, 0.4f); // never below the lawn
            Cam.transform.position = pos;
            Cam.transform.rotation = Quaternion.LookRotation(_cTarget - pos);
        }
    }
}
