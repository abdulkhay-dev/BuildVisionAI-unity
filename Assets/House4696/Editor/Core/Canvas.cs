using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Minimal software raster used to paint procedural textures (strokes, ellipses) with wrap-around,
    /// so painted textures tile seamlessly. Colors are stored in sRGB space (0..1), plus a height channel
    /// used to derive normal maps.
    /// </summary>
    public sealed class Canvas
    {
        public readonly int W, H;
        public readonly Color[] Px;
        public readonly float[] Height;
        public bool Wrap = true;

        public Canvas(int w, int h, Color fill, float height = 0f)
        {
            W = w; H = h;
            Px = new Color[w * h];
            Height = new float[w * h];
            for (int i = 0; i < Px.Length; i++) { Px[i] = fill; Height[i] = height; }
        }

        int Index(int x, int y)
        {
            if (Wrap) { x = ((x % W) + W) % W; y = ((y % H) + H) % H; }
            else if (x < 0 || y < 0 || x >= W || y >= H) return -1;
            return y * W + x;
        }

        public void Blend(int x, int y, Color c, float a, float h = float.NaN, bool maxHeight = false)
        {
            int i = Index(x, y);
            if (i < 0 || a <= 0f) return;
            var d = Px[i];
            float outA = a + d.a * (1 - a);
            Px[i] = new Color(Mathf.Lerp(d.r, c.r, a), Mathf.Lerp(d.g, c.g, a), Mathf.Lerp(d.b, c.b, a), outA);
            if (!float.IsNaN(h))
                Height[i] = maxHeight ? Mathf.Max(Height[i], h) : Mathf.Lerp(Height[i], h, a);
        }

        /// <summary>Thick line with soft edges; width and color can taper from start to end.</summary>
        public void Stroke(float x0, float y0, float x1, float y1, float w0, float w1, Color c0, Color c1,
                           float h0 = float.NaN, float h1 = float.NaN, float alpha = 1f)
        {
            float dx = x1 - x0, dy = y1 - y0;
            float len = Mathf.Sqrt(dx * dx + dy * dy);
            int steps = Mathf.Max(1, Mathf.CeilToInt(len * 1.5f));
            for (int s = 0; s <= steps; s++)
            {
                float t = s / (float)steps;
                float cx = x0 + dx * t, cy = y0 + dy * t;
                float r = Mathf.Lerp(w0, w1, t) * 0.5f;
                Color col = Color.Lerp(c0, c1, t);
                float hh = float.IsNaN(h0) ? float.NaN : Mathf.Lerp(h0, h1, t);
                int ix0 = Mathf.FloorToInt(cx - r - 1), ix1 = Mathf.CeilToInt(cx + r + 1);
                int iy0 = Mathf.FloorToInt(cy - r - 1), iy1 = Mathf.CeilToInt(cy + r + 1);
                for (int y = iy0; y <= iy1; y++)
                for (int x = ix0; x <= ix1; x++)
                {
                    float ddx = x + 0.5f - cx, ddy = y + 0.5f - cy;
                    float d = Mathf.Sqrt(ddx * ddx + ddy * ddy);
                    float a = Mathf.Clamp01(r + 0.5f - d) * alpha;
                    if (a > 0) Blend(x, y, col, a, hh, true);
                }
            }
        }

        /// <summary>Filled rotated ellipse with radial shading (leaf / pebble primitive).</summary>
        public void Ellipse(float cx, float cy, float rx, float ry, float angle, Color c, float shade, float height)
        {
            float ca = Mathf.Cos(angle), sa = Mathf.Sin(angle);
            float r = Mathf.Max(rx, ry);
            int x0 = Mathf.FloorToInt(cx - r - 1), x1 = Mathf.CeilToInt(cx + r + 1);
            int y0 = Mathf.FloorToInt(cy - r - 1), y1 = Mathf.CeilToInt(cy + r + 1);
            for (int y = y0; y <= y1; y++)
            for (int x = x0; x <= x1; x++)
            {
                float px = x + 0.5f - cx, py = y + 0.5f - cy;
                float lx = (px * ca + py * sa) / rx, ly = (-px * sa + py * ca) / ry;
                float d = lx * lx + ly * ly;
                if (d > 1.15f) continue;
                float a = Mathf.Clamp01((1.15f - d) / 0.3f);
                float k = 1f - shade * d;
                // mid-rib highlight
                float rib = Mathf.Clamp01(1f - Mathf.Abs(ly) * 6f) * 0.08f;
                var col = new Color(c.r * k + rib, c.g * k + rib, c.b * k + rib, 1f);
                Blend(x, y, col, a, height * (1f - 0.5f * d), false);
            }
        }

        public Color[] Normals(float strength)
        {
            var n = new Color[W * H];
            for (int y = 0; y < H; y++)
            for (int x = 0; x < W; x++)
            {
                float hl = Height[Index(x - 1, y) < 0 ? y * W + x : Index(x - 1, y)];
                float hr = Height[Index(x + 1, y) < 0 ? y * W + x : Index(x + 1, y)];
                float hd = Height[Index(x, y - 1) < 0 ? y * W + x : Index(x, y - 1)];
                float hu = Height[Index(x, y + 1) < 0 ? y * W + x : Index(x, y + 1)];
                var v = new Vector3((hl - hr) * strength, (hd - hu) * strength, 1f).normalized;
                n[y * W + x] = new Color(v.x * 0.5f + 0.5f, v.y * 0.5f + 0.5f, v.z * 0.5f + 0.5f, 1f);
            }
            return n;
        }
    }
}
