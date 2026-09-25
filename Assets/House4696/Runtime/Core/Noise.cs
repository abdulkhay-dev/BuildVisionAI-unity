using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Deterministic, tileable noise helpers used by the procedural texture generators.
    /// All functions are pure; periods are expressed in lattice cells.
    /// </summary>
    public static class Noise
    {
        public static uint Hash(int x, int y, int seed)
        {
            unchecked
            {
                uint h = (uint)(x * 374761393 + y * 668265263 + seed * 144665);
                h = (h ^ (h >> 13)) * 1274126177u;
                return h ^ (h >> 16);
            }
        }

        public static float Hash01(int x, int y, int seed) => (Hash(x, y, seed) & 0xFFFFFF) / 16777215f;

        static int Wrap(int v, int period) => period <= 0 ? v : ((v % period) + period) % period;

        static Vector2 Grad(int x, int y, int seed)
        {
            float a = Hash01(x, y, seed) * Mathf.PI * 2f;
            return new Vector2(Mathf.Cos(a), Mathf.Sin(a));
        }

        static float Fade(float t) => t * t * t * (t * (t * 6f - 15f) + 10f);

        /// <summary>Periodic gradient noise in [-1, 1] (approximately).</summary>
        public static float Perlin(float x, float y, int px, int py, int seed)
        {
            int x0 = Mathf.FloorToInt(x), y0 = Mathf.FloorToInt(y);
            float fx = x - x0, fy = y - y0;
            int ax = Wrap(x0, px), bx = Wrap(x0 + 1, px), ay = Wrap(y0, py), by = Wrap(y0 + 1, py);
            float n00 = Vector2.Dot(Grad(ax, ay, seed), new Vector2(fx, fy));
            float n10 = Vector2.Dot(Grad(bx, ay, seed), new Vector2(fx - 1, fy));
            float n01 = Vector2.Dot(Grad(ax, by, seed), new Vector2(fx, fy - 1));
            float n11 = Vector2.Dot(Grad(bx, by, seed), new Vector2(fx - 1, fy - 1));
            float u = Fade(fx), v = Fade(fy);
            return Mathf.Lerp(Mathf.Lerp(n00, n10, u), Mathf.Lerp(n01, n11, u), v) * 1.41421f;
        }

        /// <summary>Tileable fractal noise; (u,v) in [0,1) maps once over the tile.</summary>
        public static float Fbm(float u, float v, int baseFreqX, int baseFreqY, int octaves, int seed, float gain = 0.5f)
        {
            float sum = 0, amp = 1, norm = 0;
            int fx = baseFreqX, fy = baseFreqY;
            for (int o = 0; o < octaves; o++)
            {
                sum += amp * Perlin(u * fx, v * fy, fx, fy, seed + o * 1013);
                norm += amp;
                amp *= gain;
                fx *= 2; fy *= 2;
            }
            return sum / norm;
        }

        /// <summary>Non-periodic fbm for meshes (world space).</summary>
        public static float Fbm3(Vector3 p, int octaves, int seed)
        {
            float sum = 0, amp = 1, norm = 0, f = 1;
            for (int o = 0; o < octaves; o++)
            {
                sum += amp * Perlin(p.x * f + p.y * 0.37f * f, p.z * f - p.y * 0.61f * f, 0, 0, seed + o * 31);
                norm += amp; amp *= 0.5f; f *= 2.03f;
            }
            return sum / norm;
        }

        /// <summary>Periodic Worley (cellular) noise. Returns F1 distance and the id of the nearest cell.</summary>
        public static float Worley(float u, float v, int cells, int seed, out int cellId, out float f2)
        {
            float x = u * cells, y = v * cells;
            int cx = Mathf.FloorToInt(x), cy = Mathf.FloorToInt(y);
            float best = 9f, second = 9f; cellId = 0;
            for (int j = -1; j <= 1; j++)
            for (int i = -1; i <= 1; i++)
            {
                int gx = cx + i, gy = cy + j;
                int wx = Wrap(gx, cells), wy = Wrap(gy, cells);
                float ox = Hash01(wx, wy, seed), oy = Hash01(wx, wy, seed + 7);
                float dx = gx + ox - x, dy = gy + oy - y;
                float d = Mathf.Sqrt(dx * dx + dy * dy);
                if (d < best) { second = best; best = d; cellId = wx + wy * 7919; }
                else if (d < second) second = d;
            }
            f2 = second;
            return best;
        }
    }

    /// <summary>Small deterministic PRNG so every rebuild produces the same scene.</summary>
    public sealed class Rng
    {
        uint _s;
        public Rng(int seed) { _s = (uint)seed * 2654435761u + 1013904223u; if (_s == 0) _s = 1; }
        public uint NextUInt() { _s ^= _s << 13; _s ^= _s >> 17; _s ^= _s << 5; return _s; }
        public float Value() => (NextUInt() & 0xFFFFFF) / 16777216f;
        public float Range(float a, float b) => a + (b - a) * Value();
        public int Range(int a, int bExclusive) => a + (int)(Value() * (bExclusive - a));
        public float Gaussian() { float u1 = Mathf.Max(1e-6f, Value()), u2 = Value(); return Mathf.Sqrt(-2f * Mathf.Log(u1)) * Mathf.Cos(2f * Mathf.PI * u2); }
        public Vector2 InsideUnitCircle() { float a = Value() * Mathf.PI * 2, r = Mathf.Sqrt(Value()); return new Vector2(Mathf.Cos(a) * r, Mathf.Sin(a) * r); }
        public Vector3 OnUnitSphere()
        {
            float y = Range(-1f, 1f), a = Range(0f, Mathf.PI * 2f), r = Mathf.Sqrt(Mathf.Max(0f, 1f - y * y));
            return new Vector3(r * Mathf.Cos(a), y, r * Mathf.Sin(a));
        }
        public Vector3 InsideUnitSphere() => OnUnitSphere() * Mathf.Pow(Value(), 1f / 3f);
    }
}
