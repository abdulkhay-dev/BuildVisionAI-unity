using System.Threading.Tasks;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Interior surfaces: oak flooring, neutral wood grain (tinted per species by the material), marble,
    /// travertine, woven fabric, wall plaster, large-format tile and an atlas of four abstract paintings.
    /// </summary>
    public static partial class TextureFactory
    {
        // ------------------------------------------------------------------ oak plank floor
        // 2.4 m tile, 12 planks of 0.2 m running along v, one or two butt joints per column, micro-bevel edges.
        public static void OakFloor(bool force)
        {
            if (Has("T_OakFloor", force)) return;
            const int N = 2048, P = 12;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    int k = Mathf.Min(P - 1, Mathf.FloorToInt(u * P));
                    float lu = u * P - k;
                    float o = Noise.Hash01(k, 0, 71);
                    bool two = Noise.Hash01(k, 1, 71) > 0.45f;
                    float split = 0.42f + 0.16f * Noise.Hash01(k, 2, 71);
                    float t = Mathf.Repeat(v - o, 1f);
                    int seg = two && t >= split ? 1 : 0;
                    int id = k * 2 + seg;
                    float dj = two ? Mathf.Min(Mathf.Min(t, 1f - t), Mathf.Abs(t - split)) : Mathf.Min(t, 1f - t);

                    float tone = 0.9f + 0.2f * Noise.Hash01(id, 3, 71);
                    float warm = (Noise.Hash01(id, 4, 71) - 0.5f) * 0.06f;
                    float shift = Noise.Hash01(id, 5, 71) * 7f;
                    float warp = Noise.Fbm(u, v, 8, 2, 3, 300 + id) * 0.8f;
                    float grain = Noise.Fbm(u + shift / P + warp * 0.004f, v, 220, 3, 3, 310);
                    float figure = Mathf.Pow(Mathf.Abs(Mathf.Sin((lu * 3.5f + warp * 1.6f + shift) * Mathf.PI)), 10f);
                    float cloud = Noise.Fbm(u, v, 12, 4, 3, 320 + id % 5);
                    var light = new Color(0.80f + warm, 0.67f, 0.51f - warm);
                    var dark = new Color(0.62f + warm, 0.49f, 0.35f - warm);
                    var c = Color.Lerp(dark, light, Mathf.Clamp01(0.62f + 0.35f * grain + 0.25f * cloud - 0.3f * figure)) * tone;
                    // occasional small knot
                    float kx = (Noise.Hash01(id, 6, 71) * 0.6f + 0.2f), ky = Noise.Hash01(id, 7, 71);
                    float kd = new Vector2((lu - kx) * 0.2f * 5f, (Mathf.Repeat(v - ky + 0.5f, 1f) - 0.5f) * 2.4f * 2.2f).magnitude;
                    if (Noise.Hash01(id, 8, 71) > 0.72f) c = Color.Lerp(c * 0.45f, c, Smooth(0.0f, 0.03f, kd));
                    float edge = Mathf.Min(Mathf.Min(lu, 1f - lu) * 0.2f, dj * 2.4f);
                    float bevel = Smooth(0.0f, 0.0025f, edge);
                    c = Color.Lerp(c * 0.55f, c, bevel);
                    c.a = 1;
                    alb[y * N + x] = c;
                    hgt[y * N + x] = 0.5f + grain * 0.08f - figure * 0.05f + bevel * 0.45f;
                }
            });
            WriteWithNormal("T_OakFloor", alb, hgt, N, N, 4f);
        }

        // ------------------------------------------------------------------ neutral wood grain (1 m), tinted by materials
        public static void Grain(bool force)
        {
            if (Has("T_Grain", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    // straight-cut veneer: fine dense lines, soft long streaks, faint cathedral figure
                    float warp = Noise.Fbm(u, v, 4, 1, 3, 400);
                    float fine = Noise.Fbm(u + warp * 0.004f, v, 256, 2, 3, 410);
                    float streak = Noise.Fbm(u + warp * 0.01f, v, 40, 1, 3, 415);
                    float cath = Mathf.Pow(Mathf.Abs(Mathf.Sin((u * 24f + warp * 0.6f + Noise.Fbm(u, v, 3, 1, 2, 420) * 0.3f) * Mathf.PI)), 16f);
                    float cloud = Noise.Fbm(u, v, 6, 3, 3, 430);
                    float k = Mathf.Clamp01(0.86f + 0.07f * fine + 0.07f * streak + 0.04f * cloud - 0.08f * cath);
                    alb[y * N + x] = new Color(k, k * 0.94f, k * 0.87f, 1);
                    hgt[y * N + x] = 0.5f + fine * 0.2f - cath * 0.05f;
                }
            });
            WriteWithNormal("T_Grain", alb, hgt, N, N, 1.5f);
        }

        // ------------------------------------------------------------------ calacatta-style marble (2 m slab)
        public static void Marble(bool force)
        {
            if (Has("T_Marble", force)) return;
            const int N = 2048;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float wx = Noise.Fbm(u, v, 3, 3, 5, 500), wy = Noise.Fbm(u, v, 3, 3, 5, 501);
                    float main = Mathf.Abs(Noise.Fbm(u + wx * 0.12f, v + wy * 0.12f, 2, 3, 6, 510));
                    float second = Mathf.Abs(Noise.Fbm(u + wx * 0.2f, v + wy * 0.08f, 5, 5, 5, 520));
                    float cloud = Noise.Fbm(u, v, 4, 4, 5, 530);
                    float veinA = Smooth(0.045f, 0.0f, main);
                    float veinHalo = Smooth(0.16f, 0.0f, main);
                    float veinB = Smooth(0.018f, 0.0f, second) * 0.55f;
                    var c = new Color(0.93f, 0.925f, 0.91f) * (0.975f + cloud * 0.04f);
                    c = Color.Lerp(c, new Color(0.80f, 0.78f, 0.75f), veinHalo * 0.35f);
                    c = Color.Lerp(c, new Color(0.62f, 0.58f, 0.52f), veinB);
                    c = Color.Lerp(c, new Color(0.40f, 0.37f, 0.33f), veinA * 0.85f);
                    c.a = 1;
                    alb[y * N + x] = c;
                    hgt[y * N + x] = 0.5f;
                }
            });
            Write("T_Marble", alb, N, N);
        }

        // ------------------------------------------------------------------ vein-cut travertine (1.2 m)
        public static void Travertine(bool force)
        {
            if (Has("T_Travertine", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float warp = Noise.Fbm(u, v, 2, 4, 3, 600);
                    float band = Noise.Fbm(u * 0.25f + warp * 0.05f, v + warp * 0.03f, 1, 14, 4, 610);
                    float cloud = Noise.Fbm(u, v, 5, 5, 3, 620);
                    float pore = Noise.Fbm(u, v, 90, 360, 2, 630);
                    var c = Color.Lerp(new Color(0.70f, 0.61f, 0.49f), new Color(0.86f, 0.79f, 0.68f), Mathf.Clamp01(0.55f + band * 0.9f + cloud * 0.2f));
                    float p = Smooth(-0.35f, -0.55f, pore);
                    c = Color.Lerp(c, new Color(0.46f, 0.39f, 0.30f), p * 0.8f);
                    c.a = 1;
                    alb[y * N + x] = c;
                    hgt[y * N + x] = 0.6f - p * 0.5f + band * 0.05f;
                }
            });
            WriteWithNormal("T_Travertine", alb, hgt, N, N, 3f);
        }

        // ------------------------------------------------------------------ woven fabric (0.25 m), neutral light, tinted
        public static void Fabric(bool force)
        {
            if (Has("T_Fabric", force)) return;
            const int N = 1024, Threads = 128;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float tu = u * Threads, tv = v * Threads;
                    int iu = Mathf.FloorToInt(tu), iv = Mathf.FloorToInt(tv);
                    bool over = ((iu + iv) & 1) == 0;
                    float fu = tu - iu, fv = tv - iv;
                    float warp = Mathf.Sin(fu * Mathf.PI), weft = Mathf.Sin(fv * Mathf.PI);
                    float h = over ? warp * (0.6f + 0.4f * weft) : weft * (0.6f + 0.4f * warp);
                    float slub = Noise.Fbm(u, v, 4, 64, 3, 700) * 0.5f + Noise.Fbm(u, v, 64, 4, 3, 701) * 0.5f;
                    float mel = (Noise.Hash01(iu, iv, 702) - 0.5f) * 0.08f;
                    float k = 0.86f + 0.07f * h + 0.06f * slub + mel;
                    alb[y * N + x] = new Color(k, k * 0.99f, k * 0.97f, 1);
                    hgt[y * N + x] = h * 0.8f + slub * 0.2f;
                }
            });
            WriteWithNormal("T_Fabric", alb, hgt, N, N, 2.2f);
        }

        // ------------------------------------------------------------------ warm white wall plaster (2 m)
        public static void Plaster(bool force)
        {
            if (Has("T_Plaster", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float lo = Noise.Fbm(u, v, 3, 3, 4, 800);
                    float trowel = Noise.Fbm(u, v, 12, 8, 3, 810);
                    float hi = Noise.Fbm(u, v, 128, 128, 2, 820);
                    float k = 0.95f + lo * 0.02f + trowel * 0.012f;
                    alb[y * N + x] = new Color(k, k, k, 1);
                    hgt[y * N + x] = trowel * 0.4f + hi * 0.25f;
                }
            });
            WriteWithNormal("T_Plaster", alb, hgt, N, N, 0.8f);
        }

        // ------------------------------------------------------------------ large-format stone-look tile, 1.2 m tile of 0.6 x 1.2 slabs
        public static void Tile(bool force)
        {
            if (Has("T_Tile", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float mu = u * 1.2f, mv = v * 1.2f;
                    int col = Mathf.FloorToInt(mu / 0.6f);
                    float lu = mu - col * 0.6f;
                    float edge = Mathf.Min(Mathf.Min(lu, 0.6f - lu), Mathf.Min(mv, 1.2f - mv));
                    float cloud = Noise.Fbm(u, v, 3, 3, 5, 900 + col);
                    float speck = Noise.Fbm(u, v, 120, 120, 2, 910);
                    float k = 0.86f + cloud * 0.06f + speck * 0.025f;
                    var c = new Color(k, k * 0.985f, k * 0.965f, 1);
                    float h = 0.5f;
                    if (edge < 0.0015f) { c = new Color(0.62f, 0.61f, 0.59f, 1); h = 0f; }
                    alb[y * N + x] = c; hgt[y * N + x] = h;
                }
            });
            WriteWithNormal("T_Tile", alb, hgt, N, N, 3f);
        }

        // ------------------------------------------------------------------ 2 x 2 atlas of abstract paintings on canvas
        public static void Art(bool force)
        {
            if (Has("T_Art", force)) return;
            const int N = 1024, H = N / 2;
            var px = new Color[N * N];
            var cream = new Color(0.90f, 0.86f, 0.78f);
            var sand = new Color(0.82f, 0.70f, 0.55f);
            var terracotta = new Color(0.66f, 0.34f, 0.22f);
            var ochre = new Color(0.78f, 0.58f, 0.28f);
            var sage = new Color(0.55f, 0.60f, 0.50f);
            var charcoal = new Color(0.16f, 0.15f, 0.14f);
            var rust = new Color(0.55f, 0.24f, 0.14f);
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    int panel = (x / H) + 2 * (y / H);
                    float u = (x % H + 0.5f) / H, v = (y % H + 0.5f) / H;
                    float brush = Noise.Fbm(u, v, 6, 40, 3, 1000 + panel) * 0.5f + 0.5f;
                    Color c;
                    switch (panel)
                    {
                        case 0: // stacked arches
                        {
                            c = cream;
                            float d1 = new Vector2(u - 0.38f, (v - 0.18f) * 0.9f).magnitude;
                            float d2 = new Vector2(u - 0.64f, (v - 0.18f) * 0.9f).magnitude;
                            if (v > 0.18f && d1 < 0.30f) c = d1 > 0.2f ? terracotta : sand;
                            if (v > 0.18f && d2 < 0.22f && d2 > 0.12f) c = ochre;
                            if (v < 0.18f) c = Color.Lerp(sand, terracotta, 0.25f);
                            if (new Vector2(u - 0.72f, v - 0.74f).magnitude < 0.09f) c = rust;
                            break;
                        }
                        case 1: // horizon bands
                        {
                            float w = Noise.Fbm(u, v, 3, 1, 3, 1100) * 0.05f;
                            c = v < 0.34f + w ? charcoal : v < 0.52f + w ? sage : v < 0.58f + w ? sand : cream;
                            c = Color.Lerp(c, c * 0.85f, brush * 0.5f);
                            break;
                        }
                        case 2: // sun and line
                        {
                            c = Color.Lerp(sand, cream, 0.55f);
                            float d = new Vector2(u - 0.5f, v - 0.58f).magnitude;
                            if (d < 0.24f) c = rust;
                            if (Mathf.Abs(v - 0.3f) < 0.006f && u > 0.12f && u < 0.88f) c = charcoal;
                            if (v < 0.3f) c = Color.Lerp(c, sand, 0.4f);
                            break;
                        }
                        default: // textured monochrome with gold line
                        {
                            float t = Noise.Fbm(u, v, 4, 4, 5, 1200);
                            c = Color.Lerp(new Color(0.24f, 0.23f, 0.22f), new Color(0.38f, 0.36f, 0.33f), t * 0.8f + 0.5f);
                            float line = Mathf.Abs(u - 0.62f - Noise.Fbm(u, v, 1, 3, 3, 1210) * 0.12f);
                            if (line < 0.006f) c = new Color(0.80f, 0.64f, 0.34f);
                            break;
                        }
                    }
                    float canvas = (Noise.Hash01(x, y, 1300) - 0.5f) * 0.04f + (Mathf.Sin(x * 1.9f) * Mathf.Sin(y * 1.9f)) * 0.012f;
                    c = Mul(c, 0.94f + brush * 0.08f) + new Color(canvas, canvas, canvas);
                    c.a = 1;
                    px[y * N + x] = c;
                }
            });
            Write("T_Art", px, N, N);
        }
    }
}
