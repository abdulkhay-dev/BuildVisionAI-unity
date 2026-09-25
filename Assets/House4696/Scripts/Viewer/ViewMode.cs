using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace House4696.Runtime
{
    /// <summary>
    /// One way of driving the camera. Modes are plain serializable objects owned by <see cref="HouseViewer"/>,
    /// so their tuning shows up in its inspector; the viewer calls Enter/Exit on switches and Tick every frame.
    /// </summary>
    [Serializable]
    public abstract class ViewMode
    {
        protected Camera Cam;
        protected Transform Owner;

        public abstract string Title { get; }
        public abstract string[] Help { get; }
        /// <summary>Context hint shown at the bottom of the screen (e.g. "E — открыть дверь"), or null.</summary>
        public virtual string Prompt => null;
        /// <summary>Whether the mode wants the cursor captured for mouse look.</summary>
        public virtual bool CapturesCursor => false;

        public void Bind(Camera cam, Transform owner) { Cam = cam; Owner = owner; }

        /// <summary>Called when the mode becomes active; the camera still holds the previous mode's pose.</summary>
        public virtual void Enter() { }
        public virtual void Exit() { }
        public abstract void Tick(float dt);

        /// <summary>Moves the view to a named walk point.</summary>
        public abstract void GoTo(WalkPoint p);

        /// <summary>Plain perspective lens (the reference view uses a shifted physical lens).</summary>
        protected void UseGameLens(float fov)
        {
            Cam.usePhysicalProperties = false;
            Cam.lensShift = Vector2.zero;
            Cam.fieldOfView = fov;
            Cam.nearClipPlane = 0.05f;
        }

        /// <summary>Frame-rate independent exponential smoothing factor.</summary>
        protected static float Damp(float sharpness, float dt) => 1f - Mathf.Exp(-sharpness * dt);
    }

    /// <summary>Thin wrapper over the Input System devices shared by all modes.</summary>
    public static class ViewerInput
    {
        public static Keyboard Kb => Keyboard.current;
        public static Mouse Mouse => Mouse.current;

        /// <summary>WASD / arrows as a vector (x = strafe, y = forward).</summary>
        public static Vector2 Move()
        {
            var kb = Kb;
            if (kb == null) return Vector2.zero;
            var v = Vector2.zero;
            if (kb.wKey.isPressed || kb.upArrowKey.isPressed) v.y += 1;
            if (kb.sKey.isPressed || kb.downArrowKey.isPressed) v.y -= 1;
            if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) v.x += 1;
            if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) v.x -= 1;
            return Vector2.ClampMagnitude(v, 1f);
        }

        public static Vector2 MouseDelta => Mouse != null ? Mouse.delta.ReadValue() : Vector2.zero;

        /// <summary>Wheel direction: +1, -1 or 0 (raw values differ per platform).</summary>
        public static float ScrollSign
        {
            get
            {
                float y = Mouse != null ? Mouse.scroll.ReadValue().y : 0f;
                return Mathf.Abs(y) < 0.01f ? 0f : Mathf.Sign(y);
            }
        }
    }
}
