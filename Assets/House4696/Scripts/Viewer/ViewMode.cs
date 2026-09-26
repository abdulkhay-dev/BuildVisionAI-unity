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

    /// <summary>
    /// Thin wrapper over the Input System devices shared by all modes. The app UI blocks the pointer while it is over
    /// a panel and the keyboard while a text field or a dialog has focus, so the camera never reacts to UI input.
    /// </summary>
    public static class ViewerInput
    {
        /// <summary>Pointer is over the UI (set by the app UI every frame): no clicks, drags, wheel for the camera.</summary>
        public static bool PointerBlocked;
        /// <summary>A text field or a dialog owns the keyboard.</summary>
        public static bool KeyboardBlocked;

        public static Keyboard Kb => Keyboard.current;
        public static Mouse Mouse => Mouse.current;

        /// <summary>⌘ / Ctrl / Alt is held: letters are app shortcuts then (⌘S is not "walk back").</summary>
        public static bool Modified => Kb != null && (Kb.leftMetaKey.isPressed || Kb.rightMetaKey.isPressed || Kb.leftCtrlKey.isPressed
                                                     || Kb.rightCtrlKey.isPressed || Kb.leftAltKey.isPressed || Kb.rightAltKey.isPressed);

        static bool Usable(Key k) => !KeyboardBlocked && Kb != null && (k == Key.LeftShift || k == Key.RightShift || !Modified);

        /// <summary>Key held (false while the UI owns the keyboard or a modifier makes it a shortcut).</summary>
        public static bool Held(Key k) => Usable(k) && Kb[k].isPressed;
        /// <summary>Key went down this frame (false while the UI owns the keyboard or a modifier makes it a shortcut).</summary>
        public static bool Down(Key k) => Usable(k) && Kb[k].wasPressedThisFrame;

        public static bool LeftHeld => !PointerBlocked && Mouse != null && Mouse.leftButton.isPressed;
        public static bool LeftDown => !PointerBlocked && Mouse != null && Mouse.leftButton.wasPressedThisFrame;
        public static bool RightHeld => !PointerBlocked && Mouse != null && Mouse.rightButton.isPressed;
        public static bool MiddleHeld => !PointerBlocked && Mouse != null && Mouse.middleButton.isPressed;

        /// <summary>WASD / arrows as a vector (x = strafe, y = forward).</summary>
        public static Vector2 Move()
        {
            if (KeyboardBlocked || Kb == null || Modified) return Vector2.zero;
            var v = Vector2.zero;
            if (Held(Key.W) || Held(Key.UpArrow)) v.y += 1;
            if (Held(Key.S) || Held(Key.DownArrow)) v.y -= 1;
            if (Held(Key.D) || Held(Key.RightArrow)) v.x += 1;
            if (Held(Key.A) || Held(Key.LeftArrow)) v.x -= 1;
            return Vector2.ClampMagnitude(v, 1f);
        }

        public static Vector2 MouseDelta => Mouse != null && !PointerBlocked ? Mouse.delta.ReadValue() : Vector2.zero;

        /// <summary>Wheel direction: +1, -1 or 0 (raw values differ per platform).</summary>
        public static float ScrollSign
        {
            get
            {
                float y = Mouse != null && !PointerBlocked ? Mouse.scroll.ReadValue().y : 0f;
                return Mathf.Abs(y) < 0.01f ? 0f : Mathf.Sign(y);
            }
        }
    }
}
