using System;
using UnityEngine;

namespace House4696.Runtime
{
    /// <summary>Free "noclip" camera: RMB to look, WASD/QE to move, Shift to speed up, wheel changes speed.</summary>
    [Serializable]
    public sealed class FlyMode : ViewMode
    {
        [SerializeField] float speed = 4f;
        [SerializeField] float lookSensitivity = 0.12f;
        [SerializeField] float fov = 60f;

        float _yaw, _pitch;

        public override string Title => "Свободный полёт";
        public override string[] Help => new[]
        {
            "ПКМ + мышь — обзор, WASD — полёт, Q/E — вниз/вверх",
            "Shift — быстрее, колесо — скорость (" + speed.ToString("0.#") + " м/с)",
        };

        /// <param name="keepLens">true keeps the camera's current lens (used for the calibrated reference view).</param>
        public void Enter(bool keepLens)
        {
            if (!keepLens) UseGameLens(fov);
            var e = Cam.transform.eulerAngles;
            _yaw = e.y;
            _pitch = e.x > 180f ? e.x - 360f : e.x;
        }

        public override void Enter() => Enter(false);

        public override void GoTo(WalkPoint p)
        {
            Cam.transform.SetPositionAndRotation(p.Feet + Vector3.up * 1.65f, Quaternion.Euler(p.Pitch, p.Yaw, 0f));
            _yaw = p.Yaw;
            _pitch = p.Pitch;
        }

        public override void Tick(float dt)
        {
            var kb = ViewerInput.Kb;
            var mouse = ViewerInput.Mouse;
            if (kb == null || mouse == null) return;

            var t = Cam.transform;
            if (mouse.rightButton.isPressed)
            {
                Vector2 d = ViewerInput.MouseDelta * lookSensitivity;
                _yaw += d.x;
                _pitch = Mathf.Clamp(_pitch - d.y, -85f, 85f);
                t.rotation = Quaternion.Euler(_pitch, _yaw, 0f);
            }

            float scroll = ViewerInput.ScrollSign;
            if (scroll != 0f) speed = Mathf.Clamp(speed * (scroll > 0 ? 1.15f : 0.87f), 0.5f, 40f);

            Vector2 m = ViewerInput.Move();
            Vector3 move = new Vector3(m.x, 0f, m.y);
            if (kb.eKey.isPressed) move += Vector3.up;
            if (kb.qKey.isPressed) move += Vector3.down;
            float s = speed * (kb.leftShiftKey.isPressed ? 3f : 1f);
            t.Translate(move * (s * dt), Space.Self);
        }
    }
}
