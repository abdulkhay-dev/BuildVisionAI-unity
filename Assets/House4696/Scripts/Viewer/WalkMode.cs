using System;
using UnityEngine;

namespace House4696.Runtime
{
    /// <summary>
    /// First-person walking: CharacterController with acceleration, sprint, crouch, jump, head bob,
    /// sprint FOV kick and door interaction by looking at a door and pressing E.
    /// </summary>
    [Serializable]
    public sealed class WalkMode : ViewMode
    {
        [Header("Movement")]
        [SerializeField] float walkSpeed = 1.9f;
        [SerializeField] float runSpeed = 4.6f;
        [SerializeField] float crouchSpeed = 1.0f;
        [SerializeField] float acceleration = 14f;
        [SerializeField] float jumpHeight = 0.9f;
        [SerializeField] float gravity = 19.6f;

        [Header("Body")]
        [SerializeField] float height = 1.8f;
        [SerializeField] float crouchHeight = 1.2f;
        [SerializeField] float radius = 0.28f;
        [SerializeField] float eyeBelowTop = 0.14f;

        [Header("View")]
        [SerializeField] float lookSensitivity = 0.1f;
        [SerializeField] float fov = 70f;
        [SerializeField] float runFovBoost = 6f;
        [SerializeField] float bobAmplitude = 0.035f;
        [SerializeField] float interactDistance = 2.6f;

        CharacterController _cc;
        float _yaw, _pitch, _vy, _eye, _bobPhase, _bobWeight;
        Vector3 _vel;
        bool _crouched;
        Door _lookDoor;
        WalkPoint _spawn;

        public override string Title => "Прогулка";
        public override string[] Help => new[]
        {
            "WASD — идти, Shift — бег, Space — прыжок, C — присесть",
            "Мышь — осмотреться, E — открыть/закрыть дверь",
            "Esc — освободить курсор, клик — вернуть",
        };
        public override string Prompt => _lookDoor == null ? null : _lookDoor.IsOpen ? "E — закрыть дверь" : "E — открыть дверь";
        public override bool CapturesCursor => true;

        public Vector3 Feet => _cc != null ? _cc.transform.position : Vector3.zero;

        public void SetSpawn(WalkPoint p) => _spawn = p;

        public override void Enter()
        {
            EnsureBody();
            UseGameLens(fov);
            _eye = height - eyeBelowTop;
        }

        public override void Exit() => _lookDoor = null;

        public override void GoTo(WalkPoint p)
        {
            EnsureBody();
            _cc.enabled = false;
            _cc.transform.position = p.Feet;
            _cc.enabled = true;
            _yaw = p.Yaw;
            _pitch = p.Pitch;
            _vel = Vector3.zero;
            _vy = 0f;
        }

        void EnsureBody()
        {
            if (_cc != null) return;
            var go = new GameObject("Player") { layer = 2 }; // Ignore Raycast: the interaction ray never hits the body
            go.transform.SetParent(Owner.parent, false);
            _cc = go.AddComponent<CharacterController>();
            _cc.radius = radius;
            _cc.skinWidth = 0.02f;
            _cc.stepOffset = 0.4f;
            _cc.slopeLimit = 50f;
            _cc.minMoveDistance = 0f;
            SetHeight(height);
            GoTo(_spawn);
        }

        void SetHeight(float h)
        {
            _cc.height = h;
            _cc.center = new Vector3(0f, h * 0.5f + _cc.skinWidth, 0f);
        }

        public override void Tick(float dt)
        {
            var kb = ViewerInput.Kb;
            if (kb == null) return;

            if (Cursor.lockState == CursorLockMode.Locked)
            {
                Vector2 d = ViewerInput.MouseDelta * lookSensitivity;
                _yaw += d.x;
                _pitch = Mathf.Clamp(_pitch - d.y, -85f, 85f);
            }

            UpdateCrouch(kb.cKey.isPressed || kb.leftCtrlKey.isPressed);

            // horizontal velocity with acceleration (air control is weaker)
            Vector2 input = ViewerInput.Move();
            bool running = kb.leftShiftKey.isPressed && !_crouched && input.y > 0.1f;
            float speed = _crouched ? crouchSpeed : running ? runSpeed : walkSpeed;
            Vector3 wish = Quaternion.Euler(0f, _yaw, 0f) * new Vector3(input.x, 0f, input.y) * speed;
            float accel = _cc.isGrounded ? acceleration : acceleration * 0.25f;
            _vel = Vector3.MoveTowards(_vel, wish, accel * speed * dt);

            if (_cc.isGrounded)
            {
                if (_vy < 0f) _vy = -2f; // keeps the controller glued to steps and slopes
                if (kb.spaceKey.wasPressedThisFrame && !_crouched) _vy = Mathf.Sqrt(2f * gravity * jumpHeight);
            }
            _vy -= gravity * dt;

            var flags = _cc.Move((_vel + Vector3.up * _vy) * dt);
            if ((flags & CollisionFlags.Above) != 0 && _vy > 0f) _vy = 0f;
            if (_cc.transform.position.y < -20f) GoTo(_spawn); // fell out of the world

            UpdateCamera(dt, running);
            UpdateInteraction(kb.eKey.wasPressedThisFrame);
        }

        void UpdateCrouch(bool wantCrouch)
        {
            if (wantCrouch == _crouched) return;
            if (!wantCrouch)
            {
                // stand up only if there is head room
                Vector3 p = _cc.transform.position;
                Vector3 bottom = p + Vector3.up * (crouchHeight - radius + 0.05f);
                Vector3 top = p + Vector3.up * (height - radius);
                if (Physics.CheckCapsule(bottom, top, radius * 0.95f, ~(1 << 2), QueryTriggerInteraction.Ignore)) return;
            }
            _crouched = wantCrouch;
            SetHeight(_crouched ? crouchHeight : height);
        }

        void UpdateCamera(float dt, bool running)
        {
            float targetEye = (_crouched ? crouchHeight : height) - eyeBelowTop;
            _eye = Mathf.Lerp(_eye, targetEye, Damp(12f, dt));

            // head bob: one vertical cycle per step, one lateral cycle per two steps
            float planar = new Vector2(_vel.x, _vel.z).magnitude;
            bool moving = _cc.isGrounded && planar > 0.3f;
            _bobWeight = Mathf.Lerp(_bobWeight, moving ? Mathf.Clamp01(planar / runSpeed) + 0.3f : 0f, Damp(8f, dt));
            if (moving) _bobPhase += dt * planar / 0.75f * Mathf.PI; // ~0.75 m stride
            float bobY = Mathf.Abs(Mathf.Sin(_bobPhase)) * bobAmplitude * _bobWeight;
            float bobX = Mathf.Cos(_bobPhase) * bobAmplitude * 0.5f * _bobWeight;

            var rot = Quaternion.Euler(_pitch, _yaw, 0f);
            Cam.transform.SetPositionAndRotation(_cc.transform.position + Vector3.up * (_eye + bobY) + rot * Vector3.right * bobX, rot);
            Cam.fieldOfView = Mathf.Lerp(Cam.fieldOfView, fov + (running && planar > walkSpeed ? runFovBoost : 0f), Damp(6f, dt));
        }

        void UpdateInteraction(bool pressed)
        {
            _lookDoor = null;
            var t = Cam.transform;
            if (Physics.Raycast(t.position, t.forward, out var hit, interactDistance, ~(1 << 2), QueryTriggerInteraction.Ignore))
                _lookDoor = hit.collider.GetComponentInParent<Door>();
            if (pressed && _lookDoor != null) _lookDoor.Toggle();
        }
    }
}
