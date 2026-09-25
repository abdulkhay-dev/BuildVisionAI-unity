using System;
using System.IO;
using System.Threading.Tasks;
using UnityEditor;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Procedural texture generators for every surface of the scene. Textures are written once as PNG
    /// assets (import settings are applied by <see cref="GeneratedTexturePostprocessor"/> from the name suffix):
    ///   *_N  → normal map, *_A → albedo with alpha (cutout), *_Sky → clamped panorama, others → sRGB albedo.
    /// Physical scale of each texture is documented next to its generator (meters per tile).
    /// </summary>
    public static partial class TextureFactory
    {
        public const string Dir = AssetPaths.Textures;

        static string PathOf(string name) => $"{Dir}/{name}.png";
        static string FullPath(string assetPath) => Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? "", assetPath);

        public static Texture2D Get(string name) => AssetDatabase.LoadAssetAtPath<Texture2D>(PathOf(name));

        static bool Has(string name, bool force) => !force && File.Exists(FullPath(PathOf(name)));

        static void Write(string name, Color[] px, int w, int h)
        {
            var tex = new Texture2D(w, h, TextureFormat.RGBA32, false, true);
            tex.SetPixels(px);
            tex.Apply(false);
            File.WriteAllBytes(FullPath(PathOf(name)), tex.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(tex);
        }

        static float Smooth(float e0, float e1, float x)
        {
            float t = Mathf.Clamp01((x - e0) / (e1 - e0));
            return t * t * (3 - 2 * t);
        }

        static Color Mul(Color c, float k) => new Color(c.r * k, c.g * k, c.b * k, c.a);

        static float Blob(float u, float elDeg, float uc, float elc, float wu, float wel)
        {
            float du = Mathf.Repeat(u - uc + 0.5f, 1f) - 0.5f;
            float a = du / wu, b = (elDeg - elc) / wel;
            return Mathf.Exp(-(a * a + b * b));
        }

        /// <summary>Generates all textures that are missing (or all of them when forced) and imports them.</summary>
        public static void GenerateAll(bool force)
        {
            AssetPaths.Ensure(Dir);
            var jobs = new (string name, Action gen)[]
            {
                ("T_Stone", () => Stone(force)),
                ("T_Plinth", () => Plinth(force)),
                ("T_Wood", () => Wood(force)),
                ("T_Stucco", () => Stucco(force)),
                ("T_Porcelain", () => Porcelain(force)),
                ("T_Paver", () => Paver(force)),
                ("T_Gravel", () => Gravel(force)),
                ("T_Lawn", () => Lawn(force)),
                ("T_Mulch", () => Mulch(force)),
                ("T_Hedge", () => Hedge(force)),
                ("T_SpruceBranch_A", () => SpruceBranch(force)),
                ("T_PineTuft_A", () => PineTuft(force)),
                ("T_BirchLeaves_A", () => BirchLeaves(force)),
                ("T_DeciduousLeaves_A", () => DeciduousLeaves(force)),
                ("T_BoxTuft_A", () => BoxTuft(force)),
                ("T_Bark", () => Bark(force)),
                ("T_BirchBark", () => BirchBark(force)),
                ("T_Blades", () => Blades(force)),
                ("T_Plume_A", () => Plume(force)),
                ("T_Boulder", () => Boulder(force)),
                ("T_Sky", () => Sky(force)),
                ("T_OakFloor", () => OakFloor(force)),
                ("T_Grain", () => Grain(force)),
                ("T_Marble", () => Marble(force)),
                ("T_Travertine", () => Travertine(force)),
                ("T_Fabric", () => Fabric(force)),
                ("T_Plaster", () => Plaster(force)),
                ("T_Tile", () => Tile(force)),
                ("T_Art", () => Art(force)),
            };
            foreach (var j in jobs)
            {
                try { j.gen(); }
                catch (Exception e) { Debug.LogError($"[House4696] texture {j.name} failed: {e}"); }
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        // ------------------------------------------------------------------ stone cladding
        // 3.6 m tile: 4 x 12 slabs of 0.9 x 0.3 m, running bond, dark slate with light veins.
        public static void Stone(bool force)
        {
            if (Has("T_Stone", force)) return;
            const int N = 2048; const float M = 3.6f, TW = 0.9f, TH = 0.3f, JOINT = 0.005f;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float mu = u * M, mv = v * M;
                    int row = Mathf.FloorToInt(mv / TH);
                    float off = (row % 2 == 1 ? TW * 0.5f : 0f) + (Noise.Hash01(row % 12, 3, 91) - 0.5f) * 0.18f;
                    float su = mu + off;
                    int col = Mathf.FloorToInt(su / TW);
                    float lu = su - col * TW, lv = mv - row * TH;
                    int id = (row % 12) * 16 + ((col % 4) + 4) % 4;
                    float edge = Mathf.Min(Mathf.Min(lu, TW - lu), Mathf.Min(lv, TH - lv));
                    float tone = 0.86f + 0.28f * Noise.Hash01(id, 1, 5);
                    float cloudy = Noise.Fbm(u, v, 6, 6, 5, 11 + id % 3);
                    float warp = Noise.Fbm(u, v, 4, 4, 3, 23);
                    float vein = Mathf.Abs(Noise.Fbm(u + warp * 0.08f, v + warp * 0.05f, 10, 5, 5, 37 + id % 5));
                    float veinMask = Smooth(0.07f, 0.0f, vein) * (0.35f + 0.65f * Noise.Hash01(id, 2, 7));
                    float speck = (Noise.Hash01(x, y, 3) - 0.5f) * 0.05f;
                    var dark = new Color(0.175f, 0.182f, 0.196f);
                    var mid = new Color(0.30f, 0.31f, 0.33f);
                    float grain = Noise.Fbm(u, v, 96, 96, 3, 19 + id % 7);
                    var c = Color.Lerp(dark, mid, 0.5f + 0.9f * cloudy + 0.35f * grain) * tone;
                    c = Color.Lerp(c, new Color(0.44f, 0.45f, 0.47f), veinMask * 0.3f);
                    c += new Color(speck, speck, speck);
                    float h = 0.6f + cloudy * 0.08f + (Noise.Hash01(id, 4, 1) - 0.5f) * 0.05f;
                    float bevel = Smooth(JOINT * 0.5f, JOINT * 0.5f + 0.004f, edge);
                    if (edge < JOINT * 0.5f) { c = new Color(0.07f, 0.072f, 0.078f); h = 0f; }
                    else { h *= bevel; c = Color.Lerp(c * 1.12f, c, bevel); }
                    c.a = 1;
                    alb[y * N + x] = c; hgt[y * N + x] = h;
                }
            });
            WriteWithNormal("T_Stone", alb, hgt, N, N, 6f);
        }

        // Plinth: smoother, darker honed stone, 2 m tile.
        public static void Plinth(bool force)
        {
            if (Has("T_Plinth", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float n = Noise.Fbm(u, v, 5, 5, 5, 71);
                    float s = (Noise.Hash01(x, y, 9) - 0.5f) * 0.04f;
                    float k = 0.16f + 0.03f * n + s;
                    alb[y * N + x] = new Color(k, k * 1.02f, k * 1.07f, 1);
                    hgt[y * N + x] = Noise.Fbm(u, v, 48, 48, 3, 3) * 0.3f;
                }
            });
            WriteWithNormal("T_Plinth", alb, hgt, N, N, 2f);
        }

        // ------------------------------------------------------------------ wood battens atlas
        // u: 8 plank variants side by side (each slat samples one column), v: 2 m of length.
        public static void Wood(bool force)
        {
            if (Has("T_Wood", force)) return;
            const int W = 1024, H = 2048, P = 8;
            var alb = new Color[W * H]; var hgt = new float[W * H];
            Parallel.For(0, H, y =>
            {
                for (int x = 0; x < W; x++)
                {
                    float u = (x + 0.5f) / W, v = (y + 0.5f) / H;
                    int k = Mathf.Min(P - 1, Mathf.FloorToInt(u * P));
                    float lu = u * P - k;
                    float tone = 0.82f + 0.32f * Noise.Hash01(k, 0, 17);
                    float hue = (Noise.Hash01(k, 1, 17) - 0.5f) * 0.08f;
                    float warp = Noise.Fbm(u, v, 16, 3, 3, 40 + k) * 0.6f;
                    float grain = Noise.Perlin((u + warp * 0.02f) * 512f, v * 6f, 512, 6, 101 + k);
                    float rings = Mathf.Sin((lu * 9f + warp * 2.5f + Noise.Hash01(k, 2, 3) * 10f) * Mathf.PI * 2f);
                    rings = Mathf.Pow(Mathf.Abs(rings), 6f);
                    float streak = Noise.Fbm(u, v, 64, 2, 3, 200 + k);
                    var light = new Color(0.82f + hue, 0.63f, 0.43f - hue);
                    var dark = new Color(0.58f + hue, 0.41f, 0.26f);
                    float t = 0.55f + 0.22f * grain + 0.25f * streak - 0.35f * rings;
                    var c = Color.Lerp(dark, light, Mathf.Clamp01(t)) * tone;
                    float edgeDark = Smooth(0.0f, 0.06f, Mathf.Min(lu, 1 - lu));
                    c = Color.Lerp(c * 0.7f, c, edgeDark);
                    c.a = 1;
                    alb[y * W + x] = c;
                    hgt[y * W + x] = 0.5f + grain * 0.15f - rings * 0.2f + edgeDark * 0.3f;
                }
            });
            WriteWithNormal("T_Wood", alb, hgt, W, H, 3f);
        }

        // ------------------------------------------------------------------ anthracite stucco (2 m)
        public static void Stucco(bool force)
        {
            if (Has("T_Stucco", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float lo = Noise.Fbm(u, v, 4, 4, 4, 5);
                    float hi = Noise.Fbm(u, v, 96, 96, 3, 6);
                    float s = (Noise.Hash01(x, y, 2) - 0.5f) * 0.03f;
                    float k = 0.255f + lo * 0.018f + hi * 0.02f + s;
                    alb[y * N + x] = new Color(k, k, k * 1.03f, 1);
                    hgt[y * N + x] = hi * 0.6f + Noise.Hash01(x, y, 8) * 0.25f;
                }
            });
            WriteWithNormal("T_Stucco", alb, hgt, N, N, 1.6f);
        }

        // ------------------------------------------------------------------ light porcelain floor (2.4 m, 1.2 x 0.6 slabs)
        public static void Porcelain(bool force)
        {
            if (Has("T_Porcelain", force)) return;
            const int N = 1024; const float M = 2.4f;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float mu = u * M, mv = v * M;
                    int row = Mathf.FloorToInt(mv / 0.6f);
                    float su = mu + (row % 2) * 0.6f;
                    int col = Mathf.FloorToInt(su / 1.2f);
                    float lu = su - col * 1.2f, lv = mv - row * 0.6f;
                    float edge = Mathf.Min(Mathf.Min(lu, 1.2f - lu), Mathf.Min(lv, 0.6f - lv));
                    int id = (row % 4) * 8 + ((col % 2) + 2) % 2;
                    float n = Noise.Fbm(u, v, 6, 6, 4, 13);
                    float k = 0.64f + n * 0.025f + (Noise.Hash01(id, 0, 3) - 0.5f) * 0.03f + (Noise.Hash01(x, y, 5) - 0.5f) * 0.035f;
                    var c = new Color(k, k, k * 0.985f, 1);
                    float h = 0.5f;
                    if (edge < 0.0022f) { c = new Color(0.36f, 0.36f, 0.35f, 1); h = 0.0f; }
                    alb[y * N + x] = c; hgt[y * N + x] = h;
                }
            });
            WriteWithNormal("T_Porcelain", alb, hgt, N, N, 3f);
        }

        // ------------------------------------------------------------------ concrete paving slab (2 m)
        public static void Paver(bool force)
        {
            if (Has("T_Paver", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float lo = Noise.Fbm(u, v, 3, 3, 5, 19);
                    float hi = Noise.Fbm(u, v, 64, 64, 3, 20);
                    float speck = Noise.Hash01(x, y, 21);
                    float k = 0.50f + lo * 0.04f + hi * 0.015f + (speck > 0.985f ? -0.12f : 0f) + (speck - 0.5f) * 0.03f;
                    alb[y * N + x] = new Color(k, k * 1.005f, k * 1.02f, 1);
                    hgt[y * N + x] = hi * 0.4f + (speck > 0.985f ? -0.3f : 0f);
                }
            });
            WriteWithNormal("T_Paver", alb, hgt, N, N, 2f);
        }

        // ------------------------------------------------------------------ white gravel (0.6 m)
        public static void Gravel(bool force)
        {
            if (Has("T_Gravel", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float best = -1; Color bc = Color.black;
                    for (int layer = 0; layer < 2; layer++)
                    {
                        int cells = layer == 0 ? 44 : 70;
                        float f1 = Noise.Worley(u, v, cells, 300 + layer * 17, out int id, out float f2);
                        float gap = f2 - f1;
                        float dome = Mathf.Sqrt(Mathf.Max(0, 1 - (f1 / 0.62f) * (f1 / 0.62f)));
                        float hgtv = dome * Smooth(0.0f, 0.12f, gap) * (layer == 0 ? 1f : 0.8f);
                        if (hgtv > best)
                        {
                            best = hgtv;
                            float tone = 0.62f + 0.33f * Noise.Hash01(id, layer, 44);
                            float warm = (Noise.Hash01(id, layer, 45) - 0.5f) * 0.06f;
                            bc = new Color(tone + warm, tone, tone - warm * 0.5f, 1) * (0.72f + 0.28f * dome);
                        }
                    }
                    if (best < 0.05f) bc = new Color(0.22f, 0.21f, 0.2f, 1);
                    bc.a = 1;
                    alb[y * N + x] = bc; hgt[y * N + x] = best;
                }
            });
            WriteWithNormal("T_Gravel", alb, hgt, N, N, 5f);
        }

        // ------------------------------------------------------------------ lawn (3 m), painted grass blades
        public static void Lawn(bool force)
        {
            if (Has("T_Lawn", force)) return;
            const int N = 2048;
            var cv = new Canvas(N, N, new Color(0.085f, 0.15f, 0.04f), 0f);
            var rng = new Rng(777);
            int count = 220000;
            for (int i = 0; i < count; i++)
            {
                float x = rng.Value() * N, y = rng.Value() * N;
                float u = x / N, v = y / N;
                float patch = Noise.Fbm(u, v, 5, 5, 4, 88);
                float dry = Mathf.Clamp01(Noise.Fbm(u, v, 9, 9, 3, 89) * 1.5f + 0.1f);
                float ang = rng.Range(0, Mathf.PI * 2);
                float len = rng.Range(7f, 22f);
                float hueT = rng.Value();
                var baseC = Color.Lerp(new Color(0.12f, 0.22f, 0.03f), new Color(0.31f, 0.43f, 0.07f), hueT);
                baseC = Color.Lerp(baseC, new Color(0.47f, 0.49f, 0.14f), dry * 0.4f * rng.Value());
                float bright = 0.75f + 0.5f * rng.Value() + patch * 0.25f;
                var c0 = Mul(baseC, bright * 0.7f);
                var c1 = Mul(baseC, bright * 1.15f);
                float hh = 0.3f + 0.7f * (i / (float)count);
                cv.Stroke(x, y, x + Mathf.Cos(ang) * len, y + Mathf.Sin(ang) * len, 2.2f, 0.8f, c0, c1, hh * 0.6f, hh);
            }
            Write("T_Lawn", cv.Px, N, N);
            Write("T_Lawn_N", cv.Normals(3f), N, N);
        }

        // ------------------------------------------------------------------ bark mulch (1.5 m)
        public static void Mulch(bool force)
        {
            if (Has("T_Mulch", force)) return;
            const int N = 1024;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float f1 = Noise.Worley(u * 1f, v, 60, 501, out int id, out float f2);
                    float gap = f2 - f1;
                    float tone = 0.14f + 0.12f * Noise.Hash01(id, 0, 55);
                    float streak = Noise.Perlin(u * 900f, v * 300f, 900, 300, 56) * 0.03f;
                    var c = new Color(tone * 1.5f + streak, tone * 1.05f + streak, tone * 0.72f, 1);
                    if (gap < 0.08f) c = Mul(c, 0.45f);
                    c.a = 1;
                    alb[y * N + x] = c; hgt[y * N + x] = Smooth(0, 0.2f, gap);
                }
            });
            WriteWithNormal("T_Mulch", alb, hgt, N, N, 4f);
        }

        // ------------------------------------------------------------------ boxwood hedge leaves (0.8 m)
        public static void Hedge(bool force)
        {
            if (Has("T_Hedge", force)) return;
            const int N = 1024;
            var cv = new Canvas(N, N, new Color(0.035f, 0.06f, 0.025f), 0f);
            var rng = new Rng(4242);
            for (int i = 0; i < 26000; i++)
            {
                float x = rng.Value() * N, y = rng.Value() * N;
                float rx = rng.Range(7f, 10f), ry = rx * rng.Range(0.48f, 0.6f);
                float t = rng.Value();
                var c = Color.Lerp(new Color(0.15f, 0.21f, 0.06f), new Color(0.40f, 0.47f, 0.14f), t * t);
                if (rng.Value() < 0.14f) c = Color.Lerp(c, new Color(0.55f, 0.58f, 0.22f), 0.5f);
                cv.Ellipse(x, y, rx, ry, rng.Range(0, Mathf.PI), c, 0.35f, 0.3f + 0.7f * (i / 26000f));
            }
            Write("T_Hedge", cv.Px, N, N);
            Write("T_Hedge_N", cv.Normals(4f), N, N);
        }

        // ------------------------------------------------------------------ spruce branch card (RGBA)
        // v = 0 at the trunk attachment, v = 1 at the tip. Width spans the branch spread.
        public static void SpruceBranch(bool force)
        {
            if (Has("T_SpruceBranch_A", force)) return;
            const int W = 512, H = 1024;
            var cv = new Canvas(W, H, new Color(0.08f, 0.14f, 0.07f, 0f), 0f) { Wrap = false };
            var rng = new Rng(99);
            var stem = new Color(0.25f, 0.19f, 0.12f);
            float cx = W * 0.5f;
            // main axis with slight wobble
            var axis = new Vector2[41];
            for (int i = 0; i <= 40; i++)
            {
                float t = i / 40f;
                axis[i] = new Vector2(cx + Mathf.Sin(t * 3.1f) * 10f, 8 + t * (H - 30));
            }
            void Needles(Vector2 a, Vector2 b, float spread, float lenMin, float lenMax, float density, float youth)
            {
                Vector2 d = (b - a); float L = d.magnitude; if (L < 1) return; d /= L;
                Vector2 nrm = new Vector2(-d.y, d.x);
                int count = Mathf.CeilToInt(L * density);
                for (int k = 0; k < count; k++)
                {
                    float t = (k + rng.Value()) / count;
                    Vector2 p = a + d * (L * t);
                    float side = rng.Value() < 0.5f ? -1f : 1f;
                    float ang = spread * rng.Range(0.6f, 1.1f);
                    Vector2 dir = (d * Mathf.Cos(ang) + nrm * side * Mathf.Sin(ang)).normalized;
                    float len = rng.Range(lenMin, lenMax) * (1f - 0.35f * t);
                    float g = rng.Value();
                    var c0 = Color.Lerp(new Color(0.09f, 0.17f, 0.08f), new Color(0.17f, 0.29f, 0.13f), g);
                    var c1 = Color.Lerp(c0, new Color(0.32f, 0.45f, 0.19f), youth * t * rng.Value());
                    cv.Stroke(p.x, p.y, p.x + dir.x * len, p.y + dir.y * len, 3.2f, 1.6f, c0, c1, 0.5f, 0.8f);
                }
            }
            for (int i = 0; i < 40; i++)
            {
                float t = i / 40f;
                cv.Stroke(axis[i].x, axis[i].y, axis[i + 1].x, axis[i + 1].y, 7f - 4f * t, 7f - 4f * (t + 0.025f), stem, stem, 0.4f, 0.4f);
            }
            // side shoots, alternating, longer near the base
            int shoots = 22;
            for (int s = 0; s < shoots; s++)
            {
                float t = (s + 0.5f) / shoots;
                int ai = Mathf.Clamp(Mathf.RoundToInt(t * 40), 0, 40);
                Vector2 p = axis[ai];
                float side = (s % 2 == 0) ? -1f : 1f;
                float len = Mathf.Lerp(215f, 45f, t) * rng.Range(0.85f, 1.1f);
                float ang = Mathf.Deg2Rad * rng.Range(38f, 52f);
                Vector2 dir = new Vector2(side * Mathf.Sin(ang), Mathf.Cos(ang));
                Vector2 q = p + dir * len;
                cv.Stroke(p.x, p.y, q.x, q.y, 3.5f, 1.5f, stem, stem, 0.45f, 0.45f);
                // secondary shoots
                int sec = Mathf.Max(2, Mathf.RoundToInt(len / 45f));
                for (int k = 1; k <= sec; k++)
                {
                    Vector2 sp = Vector2.Lerp(p, q, k / (sec + 1f));
                    float sside = (k % 2 == 0) ? -1f : 1f;
                    Vector2 sdir = (dir * 0.75f + new Vector2(-dir.y, dir.x) * sside * 0.65f).normalized;
                    float sl = len * 0.35f * (1f - k / (sec + 2f));
                    Vector2 sq = sp + sdir * sl;
                    Needles(sp, sq, 0.95f, 10f, 17f, 2.2f, 0.8f);
                }
                Needles(p, q, 1.0f, 12f, 20f, 2.6f, 1f);
            }
            Needles(axis[0], axis[40], 1.05f, 12f, 20f, 1.1f, 1f);
            for (int i = 0; i < cv.Px.Length; i++) { var c = cv.Px[i]; c.a = c.a > 0.35f ? 1f : 0f; cv.Px[i] = c; }
            DilateColors(cv.Px, W, H, 4);
            Write("T_SpruceBranch_A", cv.Px, W, H);
        }

        // ------------------------------------------------------------------ pine needle tuft (RGBA)
        public static void PineTuft(bool force)
        {
            if (Has("T_PineTuft_A", force)) return;
            const int N = 512;
            var cv = new Canvas(N, N, new Color(0.1f, 0.18f, 0.08f, 0f), 0f) { Wrap = false };
            var rng = new Rng(314);
            for (int i = 0; i < 420; i++)
            {
                float ang = Mathf.Deg2Rad * (90f + rng.Gaussian() * 38f);
                float len = rng.Range(120f, 240f);
                float bend = rng.Range(-0.35f, 0.35f);
                var c0 = new Color(0.07f, 0.14f, 0.06f);
                var c1 = Color.Lerp(new Color(0.16f, 0.29f, 0.11f), new Color(0.30f, 0.43f, 0.17f), rng.Value());
                Vector2 p = new Vector2(N * 0.5f + rng.Range(-14f, 14f), 10f);
                Vector2 dir = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang));
                int segs = 6;
                for (int s = 0; s < segs; s++)
                {
                    float t0 = s / (float)segs, t1 = (s + 1) / (float)segs;
                    Vector2 d = Quaternion.Euler(0, 0, bend * 30f * t0) * dir;
                    Vector2 q = p + d * (len / segs);
                    cv.Stroke(p.x, p.y, q.x, q.y, 3f, 2.2f, Color.Lerp(c0, c1, t0), Color.Lerp(c0, c1, t1), 0.5f, 0.9f);
                    p = q;
                }
            }
            for (int i = 0; i < cv.Px.Length; i++) { var c = cv.Px[i]; c.a = c.a > 0.35f ? 1f : 0f; cv.Px[i] = c; }
            DilateColors(cv.Px, N, N, 4);
            Write("T_PineTuft_A", cv.Px, N, N);
        }

        // ------------------------------------------------------------------ birch leaf cluster (RGBA)
        public static void BirchLeaves(bool force)
        {
            if (Has("T_BirchLeaves_A", force)) return;
            LeafCluster("T_BirchLeaves_A", 515, 110, 13f, 20f, new Color(0.26f, 0.44f, 0.12f), new Color(0.52f, 0.66f, 0.24f));
        }

        public static void BoxTuft(bool force)
        {
            if (Has("T_BoxTuft_A", force)) return;
            LeafCluster("T_BoxTuft_A", 717, 150, 9f, 14f, new Color(0.12f, 0.18f, 0.05f), new Color(0.40f, 0.46f, 0.14f));
        }

        public static void DeciduousLeaves(bool force)
        {
            if (Has("T_DeciduousLeaves_A", force)) return;
            LeafCluster("T_DeciduousLeaves_A", 616, 85, 16f, 26f, new Color(0.14f, 0.28f, 0.08f), new Color(0.36f, 0.52f, 0.16f));
        }

        static void LeafCluster(string name, int seed, int leaves, float rMin, float rMax, Color dark, Color light)
        {
            const int N = 512;
            var cv = new Canvas(N, N, Color.Lerp(dark, light, 0.4f) * new Color(1, 1, 1, 0), 0f) { Wrap = false };
            var rng = new Rng(seed);
            var twig = new Color(0.22f, 0.18f, 0.12f);
            Vector2 root = new Vector2(N * 0.5f, 12);
            for (int b = 0; b < 7; b++)
            {
                float ang = Mathf.Deg2Rad * (90f + (b - 3) * 22f + rng.Range(-8f, 8f));
                Vector2 end = root + new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * rng.Range(170f, 230f);
                cv.Stroke(root.x, root.y, end.x, end.y, 3f, 1.2f, twig, twig);
            }
            for (int i = 0; i < leaves; i++)
            {
                Vector2 c = new Vector2(N * 0.5f, N * 0.52f) + rng.InsideUnitCircle() * (N * 0.38f);
                float rx = rng.Range(rMin, rMax), ry = rx * rng.Range(0.55f, 0.7f);
                var col = Color.Lerp(dark, light, rng.Value());
                cv.Ellipse(c.x, c.y, rx, ry, rng.Range(0, Mathf.PI), col, 0.3f, 1f);
            }
            for (int i = 0; i < cv.Px.Length; i++) { var c = cv.Px[i]; c.a = c.a > 0.4f ? 1f : 0f; cv.Px[i] = c; }
            DilateColors(cv.Px, N, N, 4);
            Write(name, cv.Px, N, N);
        }

        // ------------------------------------------------------------------ spruce bark (0.5 x 1 m)
        public static void Bark(bool force)
        {
            if (Has("T_Bark", force)) return;
            const int W = 512, H = 1024;
            var alb = new Color[W * H]; var hgt = new float[W * H];
            Parallel.For(0, H, y =>
            {
                for (int x = 0; x < W; x++)
                {
                    float u = (x + 0.5f) / W, v = (y + 0.5f) / H;
                    float f1 = Noise.Worley(u, v * 0.5f, 18, 71, out int id, out float f2);
                    float plate = Smooth(0.0f, 0.15f, f2 - f1);
                    float n = Noise.Fbm(u, v, 8, 16, 4, 72);
                    float k = 0.20f + 0.10f * Noise.Hash01(id, 0, 3) + n * 0.04f;
                    var c = new Color(k * 1.25f, k * 1.02f, k * 0.82f, 1) * (0.55f + 0.45f * plate);
                    c.a = 1;
                    alb[y * W + x] = c; hgt[y * W + x] = plate * 0.8f + n * 0.2f;
                }
            });
            WriteWithNormal("T_Bark", alb, hgt, W, H, 4f);
        }

        public static void BirchBark(bool force)
        {
            if (Has("T_BirchBark", force)) return;
            const int W = 512, H = 1024;
            var alb = new Color[W * H]; var hgt = new float[W * H];
            Parallel.For(0, H, y =>
            {
                for (int x = 0; x < W; x++)
                {
                    float u = (x + 0.5f) / W, v = (y + 0.5f) / H;
                    float n = Noise.Fbm(u, v, 4, 8, 4, 81);
                    float patches = Noise.Fbm(u, v, 3, 10, 4, 82);
                    float lent = Mathf.Abs(Noise.Perlin(u * 24f, v * 160f, 24, 160, 83));
                    float k = 0.84f + n * 0.05f;
                    var c = new Color(k, k * 0.99f, k * 0.95f, 1);
                    if (patches > 0.32f) c = Color.Lerp(c, new Color(0.10f, 0.09f, 0.08f), Smooth(0.32f, 0.38f, patches));
                    if (lent < 0.05f && Noise.Hash01(x / 20, y, 84) > 0.5f) c = Color.Lerp(c, new Color(0.2f, 0.18f, 0.16f), 0.8f);
                    c.a = 1;
                    alb[y * W + x] = c; hgt[y * W + x] = 0.5f + n * 0.2f - (patches > 0.32f ? 0.2f : 0f);
                }
            });
            WriteWithNormal("T_BirchBark", alb, hgt, W, H, 2f);
        }

        // ------------------------------------------------------------------ grass blade atlas
        // u: 8 colour variants; v: base (0) → tip (1).
        public static void Blades(bool force)
        {
            if (Has("T_Blades", force)) return;
            const int N = 256;
            var px = new Color[N * N];
            var rng = new Rng(55);
            var variants = new Color[8];
            for (int i = 0; i < 8; i++)
            {
                float t = i / 7f;
                variants[i] = Color.Lerp(new Color(0.12f, 0.26f, 0.05f), new Color(0.34f, 0.50f, 0.12f), t);
                if (i == 6) variants[i] = new Color(0.44f, 0.52f, 0.20f);
                if (i == 7) variants[i] = new Color(0.52f, 0.56f, 0.44f); // grey-green (ornamental grass)
            }
            for (int y = 0; y < N; y++)
            for (int x = 0; x < N; x++)
            {
                int k = x * 8 / N;
                float v = (y + 0.5f) / N;
                var c = Color.Lerp(Mul(variants[k], 0.55f), Mul(variants[k], 1.12f), Mathf.Pow(v, 0.7f));
                c = Color.Lerp(c, new Color(0.62f, 0.60f, 0.40f), Smooth(0.85f, 1f, v) * 0.35f);
                c.a = 1;
                px[y * N + x] = c;
            }
            Write("T_Blades", px, N, N);
        }

        // ------------------------------------------------------------------ feathery plume (RGBA)
        public static void Plume(bool force)
        {
            if (Has("T_Plume_A", force)) return;
            const int W = 256, H = 512;
            var cv = new Canvas(W, H, new Color(0.92f, 0.9f, 0.84f, 0f), 0f) { Wrap = false };
            var rng = new Rng(808);
            for (int i = 0; i < 5200; i++)
            {
                float t = rng.Value();
                float y = 16 + t * (H - 32);
                float envelope = Mathf.Pow(Mathf.Sin(Mathf.Clamp01(t) * Mathf.PI), 0.6f) * (0.7f + 0.3f * (1 - t));
                float reach = W * 0.46f * envelope * rng.Range(0.35f, 1.05f);
                float ang = rng.Range(0f, Mathf.PI * 2f);
                float x0 = W * 0.5f + rng.Range(-3f, 3f);
                float x1 = x0 + Mathf.Cos(ang) * reach, y1 = y + Mathf.Abs(Mathf.Sin(ang)) * reach * 0.35f + reach * 0.25f;
                float tone = rng.Range(0.84f, 1.0f);
                var c = new Color(0.95f * tone, 0.93f * tone, 0.87f * tone);
                cv.Stroke(x0, y, x1, y1, 1.3f, 0.7f, c, c, float.NaN, float.NaN, rng.Range(0.6f, 1f));
            }
            for (int i = 0; i < cv.Px.Length; i++) { var c = cv.Px[i]; c.a = c.a > 0.3f ? 1f : 0f; cv.Px[i] = c; }
            DilateColors(cv.Px, W, H, 3);
            Write("T_Plume_A", cv.Px, W, H);
        }

        // ------------------------------------------------------------------ boulder (1 m)
        public static void Boulder(bool force)
        {
            if (Has("T_Boulder", force)) return;
            const int N = 512;
            var alb = new Color[N * N]; var hgt = new float[N * N];
            Parallel.For(0, N, y =>
            {
                for (int x = 0; x < N; x++)
                {
                    float u = (x + 0.5f) / N, v = (y + 0.5f) / N;
                    float n = Noise.Fbm(u, v, 4, 4, 6, 91);
                    float m = Noise.Fbm(u, v, 12, 12, 3, 92);
                    float k = 0.55f + n * 0.12f + m * 0.05f;
                    alb[y * N + x] = new Color(k * 1.02f, k * 0.97f, k * 0.88f, 1);
                    hgt[y * N + x] = n * 0.8f + m * 0.3f;
                }
            });
            WriteWithNormal("T_Boulder", alb, hgt, N, N, 3f);
        }

        // ------------------------------------------------------------------ sky panorama (lat-long)
        // u = azimuth (0..1), v = elevation (-90..90 deg). Clouds cluster near the horizon like the reference.
        public static void Sky(bool force)
        {
            if (Has("T_Sky", force)) return;
            const int W = 4096, H = 2048;
            var px = new Color[W * H];
            var zenith = new Color(0.24f, 0.44f, 0.76f);
            var mid = new Color(0.43f, 0.63f, 0.87f);
            var horizon = new Color(0.78f, 0.85f, 0.91f);
            Parallel.For(0, H, y =>
            {
                float el = ((y + 0.5f) / H - 0.5f) * Mathf.PI; // -pi/2..pi/2
                float elDeg = el * Mathf.Rad2Deg;
                for (int x = 0; x < W; x++)
                {
                    float u = (x + 0.5f) / W, v = (y + 0.5f) / H;
                    Color c;
                    if (elDeg >= 0)
                    {
                        float t = Mathf.Pow(Mathf.Clamp01(elDeg / 90f), 0.55f);
                        c = t < 0.35f ? Color.Lerp(horizon, mid, t / 0.35f) : Color.Lerp(mid, zenith, (t - 0.35f) / 0.65f);
                        // cumulus: noise shaped by explicit cloud groups (u 0.27..0.40 is the camera's field of view)
                        float groups = Blob(u, elDeg, 0.397f, 13.5f, 0.018f, 2.8f) * 1.2f + Blob(u, elDeg, 0.386f, 12f, 0.009f, 2f)
                                     + Blob(u, elDeg, 0.404f, 16f, 0.006f, 1.3f) * 0.8f
                                     + Blob(u, elDeg, 0.272f, 11f, 0.007f, 1.5f) + Blob(u, elDeg, 0.286f, 20f, 0.01f, 1.4f) * 0.4f
                                     + Blob(u, elDeg, 0.33f, 6f, 0.02f, 1.8f) * 0.5f
                                     + Blob(u, elDeg, 0.62f, 12f, 0.05f, 6f) + Blob(u, elDeg, 0.83f, 9f, 0.06f, 5f) + Blob(u, elDeg, 0.05f, 15f, 0.05f, 7f);
                        float band = Smooth(1.5f, 5f, elDeg) * Smooth(30f, 10f, elDeg);
                        float mask = Mathf.Clamp01(groups * 1.1f + band * 0.25f);
                        if (mask > 0.01f)
                        {
                            float cloud = Noise.Fbm(u, v * 3f, 18, 9, 6, 1234) + 0.18f;
                            float detail = Noise.Fbm(u, v * 3f, 72, 36, 3, 1240) * 0.15f;
                            float cov = Smooth(0.22f, 0.45f, (cloud + detail + 0.22f) * mask);
                            float shade = Mathf.Clamp01(0.62f + (cloud + detail) * 0.8f + (elDeg - 10f) * 0.01f);
                            var cloudCol = Color.Lerp(new Color(0.74f, 0.78f, 0.86f), new Color(1.0f, 1.0f, 1.0f), shade);
                            c = Color.Lerp(c, cloudCol, Mathf.Clamp01(cov));
                        }
                        // a few high wisps
                        float wband = Smooth(18f, 30f, elDeg) * Smooth(70f, 40f, elDeg);
                        if (wband > 0f)
                        {
                            float wisp = Smooth(0.26f, 0.5f, Noise.Fbm(u, v, 10, 22, 5, 1300)) * wband * 0.35f;
                            c = Color.Lerp(c, new Color(0.93f, 0.95f, 0.98f), wisp);
                        }
                    }
                    else
                    {
                        float t = Mathf.Clamp01(-elDeg / 25f);
                        c = Color.Lerp(new Color(0.46f, 0.50f, 0.44f), new Color(0.20f, 0.22f, 0.16f), t);
                    }
                    c.a = 1;
                    px[y * W + x] = c;
                }
            });
            Write("T_Sky", px, W, H);
        }

        // ------------------------------------------------------------------ helpers
        static void WriteWithNormal(string name, Color[] alb, float[] hgt, int w, int h, float strength)
        {
            Write(name, alb, w, h);
            var n = new Color[w * h];
            Parallel.For(0, h, y =>
            {
                for (int x = 0; x < w; x++)
                {
                    int xl = (x - 1 + w) % w, xr = (x + 1) % w, yd = (y - 1 + h) % h, yu = (y + 1) % h;
                    float dx = hgt[y * w + xl] - hgt[y * w + xr];
                    float dy = hgt[yd * w + x] - hgt[yu * w + x];
                    var v = new Vector3(dx * strength, dy * strength, 1f).normalized;
                    n[y * w + x] = new Color(v.x * 0.5f + 0.5f, v.y * 0.5f + 0.5f, v.z * 0.5f + 0.5f, 1);
                }
            });
            Write(name + "_N", n, w, h);
        }

        /// <summary>Bleeds opaque colors into transparent texels so mip levels of cutout textures do not halo.</summary>
        static void DilateColors(Color[] px, int w, int h, int passes)
        {
            var src = (Color[])px.Clone();
            var filled = new bool[px.Length];
            for (int i = 0; i < px.Length; i++) filled[i] = px[i].a > 0.5f;
            for (int p = 0; p < passes * 8; p++)
            {
                bool any = false;
                var next = (bool[])filled.Clone();
                for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                {
                    int i = y * w + x;
                    if (filled[i]) continue;
                    Color acc = Color.clear; int cnt = 0;
                    for (int dy = -1; dy <= 1; dy++)
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        int xx = x + dx, yy = y + dy;
                        if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
                        int j = yy * w + xx;
                        if (filled[j]) { acc += src[j]; cnt++; }
                    }
                    if (cnt > 0) { var c = acc / cnt; c.a = 0; src[i] = c; next[i] = true; any = true; }
                }
                filled = next;
                if (!any) break;
            }
            for (int i = 0; i < px.Length; i++) { var a = px[i].a; px[i] = src[i]; px[i].a = a; }
        }
    }

    /// <summary>Applies import settings to generated textures based on their name suffix.</summary>
    public class GeneratedTexturePostprocessor : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(AssetPaths.Textures)) return;
            var ti = (TextureImporter)assetImporter;
            string file = Path.GetFileNameWithoutExtension(assetPath);
            ti.maxTextureSize = 4096;
            ti.anisoLevel = 8;
            ti.mipmapEnabled = true;
            ti.textureCompression = TextureImporterCompression.CompressedHQ;
            ti.wrapMode = TextureWrapMode.Repeat;
            if (file.EndsWith("_N"))
            {
                ti.textureType = TextureImporterType.NormalMap;
                ti.sRGBTexture = false;
            }
            else
            {
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = true;
                if (file.EndsWith("_A"))
                {
                    ti.alphaSource = TextureImporterAlphaSource.FromInput;
                    ti.alphaIsTransparency = true;
                    ti.mipMapsPreserveCoverage = true;
                    ti.alphaTestReferenceValue = 0.5f;
                    ti.wrapMode = TextureWrapMode.Clamp;
                }
                else ti.alphaSource = TextureImporterAlphaSource.None;
                if (file == "T_Sky")
                {
                    ti.wrapModeU = TextureWrapMode.Repeat;
                    ti.wrapModeV = TextureWrapMode.Clamp;
                    ti.mipmapEnabled = false;
                    ti.textureCompression = TextureImporterCompression.Uncompressed;
                }
            }
        }
    }
}
