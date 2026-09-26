using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Soft shadows and gradients for UI Toolkit, which has neither: textures generated once at runtime. A shadow is a
    /// blurred rounded rectangle drawn as a 9-slice behind a panel, so one small texture serves any panel size.
    /// </summary>
    public static class Elevation
    {
        static readonly Dictionary<(int, int), Texture2D> Shadows = new Dictionary<(int, int), Texture2D>();
        static readonly Dictionary<string, Texture2D> Ramps = new Dictionary<string, Texture2D>();

        /// <summary>
        /// Shadow texture: a rounded rect of corner <paramref name="radius"/> blurred by <paramref name="blur"/> px
        /// (Gaussian sigma = blur / 2), black with alpha. Slice = blur + radius on every side.
        /// </summary>
        public static Texture2D ShadowTexture(int radius, int blur)
        {
            if (Shadows.TryGetValue((radius, blur), out var cached) && cached != null) return cached;
            int pad = blur * 2, inner = radius * 2 + 4, size = inner + pad * 2;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false, true)
            {
                name = $"shadow_{radius}_{blur}", wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear,
                hideFlags = HideFlags.HideAndDontSave,
            };
            float sigma = Mathf.Max(0.5f, blur * 0.5f);
            var px = new Color32[size * size];
            float half = inner * 0.5f, c = size * 0.5f;
            for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
            {
                // signed distance to the rounded rectangle centred in the texture
                float qx = Mathf.Abs(x + 0.5f - c) - (half - radius), qy = Mathf.Abs(y + 0.5f - c) - (half - radius);
                float outside = new Vector2(Mathf.Max(qx, 0f), Mathf.Max(qy, 0f)).magnitude;
                float d = outside + Mathf.Min(Mathf.Max(qx, qy), 0f) - radius;
                float a = 0.5f * (1f - Erf(d / (sigma * 1.41421356f)));
                px[y * size + x] = new Color32(0, 0, 0, (byte)Mathf.RoundToInt(Mathf.Clamp01(a) * 255f));
            }
            tex.SetPixels32(px);
            tex.Apply(false, true);
            Shadows[(radius, blur)] = tex;
            return tex;
        }

        /// <summary>
        /// Adds a shadow behind <paramref name="panel"/>: returns a host that takes the panel's place in the layout
        /// (move the panel's positioning styles to the host). The shadow is offset down by <paramref name="offsetY"/>.
        /// </summary>
        public static VisualElement Wrap(VisualElement panel, int radius, int blur, float offsetY = 6f, float opacity = 0.55f, string hostClasses = null)
        {
            var host = Ui.El(hostClasses);
            host.pickingMode = PickingMode.Ignore;
            host.Add(Shadow(radius, blur, offsetY, opacity));
            host.Add(panel);
            return host;
        }

        /// <summary>An absolutely positioned shadow element sized to its parent (add it as the parent's first child).</summary>
        public static VisualElement Shadow(int radius, int blur, float offsetY = 6f, float opacity = 0.55f)
        {
            int pad = blur * 2, slice = pad + radius + 2;
            var s = new VisualElement { name = "shadow", pickingMode = PickingMode.Ignore };
            s.style.position = Position.Absolute;
            s.style.left = -pad; s.style.right = -pad;
            s.style.top = -pad + offsetY; s.style.bottom = -pad - offsetY;
            s.style.backgroundImage = new StyleBackground(ShadowTexture(radius, blur));
            s.style.unitySliceLeft = slice; s.style.unitySliceRight = slice;
            s.style.unitySliceTop = slice; s.style.unitySliceBottom = slice;
            s.style.opacity = opacity;
            s.AddToClassList("shadow");
            return s;
        }

        /// <summary>Vertical gradient texture (top → bottom), for image scrims and backgrounds.</summary>
        public static Texture2D VerticalRamp(Color top, Color bottom, int height = 64)
        {
            string key = ColorUtility.ToHtmlStringRGBA(top) + ColorUtility.ToHtmlStringRGBA(bottom) + height;
            if (Ramps.TryGetValue(key, out var cached) && cached != null) return cached;
            var tex = new Texture2D(1, height, TextureFormat.RGBA32, false, true)
            {
                name = "ramp_" + key, wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear,
                hideFlags = HideFlags.HideAndDontSave,
            };
            for (int y = 0; y < height; y++)
            {
                // texture rows go bottom-up; smoothstep keeps the ends soft
                float t = Mathf.SmoothStep(0f, 1f, y / (float)(height - 1));
                tex.SetPixel(0, y, Color.Lerp(bottom, top, t));
            }
            tex.Apply(false, true);
            Ramps[key] = tex;
            return tex;
        }

        /// <summary>Error function (Abramowitz–Stegun 7.1.26, |ε| &lt; 1.5e-7).</summary>
        static float Erf(float x)
        {
            float s = Mathf.Sign(x);
            x = Mathf.Abs(x);
            float t = 1f / (1f + 0.3275911f * x);
            float y = 1f - (((((1.061405429f * t - 1.453152027f) * t) + 1.421413741f) * t - 0.284496736f) * t + 0.254829592f) * t * Mathf.Exp(-x * x);
            return s * y;
        }
    }
}
