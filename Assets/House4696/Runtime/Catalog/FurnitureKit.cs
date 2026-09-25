using House4696.Core;
using UnityEngine;

namespace House4696.Catalog
{
    /// <summary>
    /// Parametric furniture. Every piece is emitted in the builder's local frame (see <see cref="Shapes.Place"/>):
    /// the local "front" is -Z. Free-standing pieces are centred on the origin at floor level; wall pieces
    /// (beds, cabinets, vanities) have their back against the wall at z = 0 and extend towards -Z.
    /// </summary>
    public sealed class FurnitureKit
    {
        readonly InteriorMaterials _m;
        public FurnitureKit(InteriorMaterials m) { _m = m; }

        static Vector3 V(float x, float y, float z) => new Vector3(x, y, z);

        // ================================================================== seating
        /// <summary>Low modular sofa, <paramref name="length"/> along X; optional chaise at +X end.</summary>
        public void Sofa(MeshBuilder mb, float length, float depth, Material fabric, Material accent, bool chaise = false)
        {
            float L = length * 0.5f, D = depth * 0.5f;
            mb.Box(V(-L + 0.06f, 0, -D + 0.06f), V(L - 0.06f, 0.08f, D - 0.06f), _m.BlackMetal);
            mb.RoundBox(V(-L, 0.08f, -D), V(L, 0.40f, D), 0.04f, fabric, 3, 3, 0.004f);
            mb.RoundBox(V(-L, 0.38f, D - 0.24f), V(L, 0.80f, D), 0.07f, fabric, 3, 4, 0.01f, 0.002f, 11);
            mb.RoundBox(V(-L, 0.38f, -D), V(-L + 0.2f, 0.62f, D - 0.18f), 0.07f, fabric, 3, 3, 0.01f);
            if (!chaise) mb.RoundBox(V(L - 0.2f, 0.38f, -D), V(L, 0.62f, D - 0.18f), 0.07f, fabric, 3, 3, 0.01f);

            float inner0 = -L + 0.2f, inner1 = chaise ? L : L - 0.2f;
            int n = Mathf.Max(1, Mathf.RoundToInt((inner1 - inner0) / 0.95f));
            for (int i = 0; i < n; i++)
            {
                float a = Mathf.Lerp(inner0, inner1, i / (float)n) + 0.006f, b = Mathf.Lerp(inner0, inner1, (i + 1) / (float)n) - 0.006f;
                mb.RoundBox(V(a, 0.39f, -D + 0.02f), V(b, 0.55f, D - 0.24f), 0.06f, fabric, 3, 6, 0.022f, 0.004f, 20 + i);
                using (mb.Place(V(0, 0.52f, D - 0.3f), Quaternion.Euler(12f + i * 2f, 0, (i % 2 == 0 ? 1f : -1f))))
                    mb.RoundBox(V(a, 0f, -0.1f), V(b, 0.42f, 0.1f), 0.08f, fabric, 3, 6, 0.03f, 0.005f, 30 + i);
            }
            if (chaise)
            {
                mb.Box(V(L - 0.9f, 0, -D - 0.7f), V(L - 0.06f, 0.08f, -D + 0.06f), _m.BlackMetal);
                mb.RoundBox(V(L - 0.95f, 0.08f, -D - 0.75f), V(L, 0.40f, -D + 0.04f), 0.04f, fabric, 3, 3, 0.004f);
                mb.RoundBox(V(L - 0.95f + 0.006f, 0.39f, -D - 0.73f), V(L - 0.006f, 0.55f, -D + 0.02f), 0.06f, fabric, 3, 6, 0.022f, 0.004f, 40);
            }
            // sewn throw pillows leaning on the back cushions
            using (mb.Place(V(-L + 0.45f, 0.78f, D - 0.4f), Quaternion.Euler(16f, 22f, 4f))) mb.Pillow(0.5f, 0.5f, 0.17f, accent, 3);
            using (mb.Place(V(-L + 0.92f, 0.76f, D - 0.38f), Quaternion.Euler(14f, -6f, -5f))) mb.Pillow(0.45f, 0.45f, 0.15f, _m.Linen, 5);
            using (mb.Place(V(inner1 - 0.45f, 0.78f, D - 0.4f), Quaternion.Euler(18f, -18f, 3f))) mb.Pillow(0.5f, 0.5f, 0.17f, accent, 7);
        }

        /// <summary>Rounded lounge armchair on short wooden legs.</summary>
        public void Armchair(MeshBuilder mb, Material fabric, Material wood)
        {
            foreach (var x in new[] { -0.32f, 0.32f })
            foreach (var z in new[] { -0.3f, 0.3f })
                mb.Lathe(V(x, 0, z), new[] { new Vector2(0.018f, 0), new Vector2(0.024f, 0.14f) }, 10, wood, true);
            mb.RoundBox(V(-0.4f, 0.14f, -0.4f), V(0.4f, 0.40f, 0.4f), 0.12f, fabric, 4, 2, 0.01f);
            mb.RoundBox(V(-0.4f, 0.3f, 0.12f), V(0.4f, 0.82f, 0.4f), 0.13f, fabric, 4, 3, 0.015f, 0.003f, 51);
            mb.RoundBox(V(-0.4f, 0.3f, -0.36f), V(-0.24f, 0.62f, 0.36f), 0.08f, fabric, 3, 3, 0.008f);
            mb.RoundBox(V(0.24f, 0.3f, -0.36f), V(0.4f, 0.62f, 0.36f), 0.08f, fabric, 3, 3, 0.008f);
            mb.RoundBox(V(-0.25f, 0.38f, -0.37f), V(0.25f, 0.52f, 0.14f), 0.06f, fabric, 3, 5, 0.02f, 0.004f, 53);
        }

        /// <summary>Leather lounge chair in a walnut frame (side slabs) with reclined back.</summary>
        public void LoungeChair(MeshBuilder mb)
        {
            foreach (var x in new[] { -0.38f, 0.34f })
                mb.RoundBox(V(x, 0, -0.42f), V(x + 0.04f, 0.55f, 0.42f), 0.012f, _m.Walnut);
            mb.Bevel(V(-0.34f, 0.12f, -0.36f), V(0.34f, 0.16f, 0.36f), _m.Walnut);
            mb.RoundBox(V(-0.34f, 0.16f, -0.4f), V(0.34f, 0.34f, 0.3f), 0.06f, _m.Leather, 3, 5, 0.018f, 0.003f, 61);
            using (mb.Place(V(0, 0.3f, 0.26f), Quaternion.Euler(18f, 0, 0)))
                mb.RoundBox(V(-0.34f, 0, -0.08f), V(0.34f, 0.6f, 0.1f), 0.07f, _m.Leather, 3, 5, 0.02f, 0.003f, 62);
        }

        /// <summary>
        /// Chaise longue on a bent chrome frame with a channel-tufted leather cushion (head at +Z, sitting
        /// facing -Z), curved armrest hoops and a sled base.
        /// </summary>
        public void Chaise(MeshBuilder mb, Material leather, Material pillow)
        {
            var line = SoftShapes.Spline(new[]
            {
                V(0, 0.44f, -0.8f), V(0, 0.41f, -0.45f), V(0, 0.38f, -0.05f), V(0, 0.42f, 0.2f), V(0, 0.56f, 0.38f), V(0, 0.8f, 0.52f), V(0, 1.02f, 0.6f)
            }, 8);
            // cushion: tufted rolls following the curve
            const float seg = 0.105f;
            int from = 0, roll = 0;
            float acc = 0f;
            for (int i = 1; i < line.Length; i++)
            {
                acc += (line[i] - line[i - 1]).magnitude;
                if (acc < seg && i < line.Length - 1) continue;
                Vector3 a = line[from], b = line[i];
                Vector3 c = (a + b) * 0.5f, t = (b - a).normalized;
                Vector3 up = Vector3.Cross(t, Vector3.right).normalized;
                float len = (b - a).magnitude * 0.5f + 0.004f;
                using (mb.Place(c + up * 0.045f, Quaternion.LookRotation(t, up)))
                    mb.RoundBox(V(-0.28f, -0.045f, -len), V(0.28f, 0.045f, len), 0.044f, leather, 3, 3, 0.006f, 0.0015f, 70 + roll++);
                acc = 0f; from = i;
            }
            Vector3 top = line[line.Length - 1];
            using (mb.Place(top + V(0, 0.02f, -0.02f), Quaternion.Euler(0, 0, 90f)))
                mb.Lathe(V(0, -0.29f, 0), new[] { new Vector2(0.055f, 0), new Vector2(0.075f, 0.03f), new Vector2(0.075f, 0.55f), new Vector2(0.055f, 0.58f) }, 20, leather, true, true);
            // frame: seat rails under the cushion, sled runners, hoops, cross bars
            foreach (float x in new[] { -0.3f, 0.3f })
            {
                var rail = new Vector3[line.Length];
                for (int i = 0; i < line.Length; i++) rail[i] = line[i] + V(x, -0.015f, 0);
                mb.Tube(rail, 0.011f, _m.Chrome);
                mb.Tube(SoftShapes.Spline(new[]
                {
                    V(x, 0.43f, -0.8f), V(x, 0.3f, -0.9f), V(x, 0.1f, -0.82f), V(x, 0.02f, -0.6f), V(x, 0.02f, 0.25f), V(x, 0.12f, 0.6f), V(x, 0.45f, 0.62f), V(x, 0.62f, 0.54f)
                }, 8), 0.011f, _m.Chrome);
                mb.Tube(SoftShapes.Spline(new[]
                {
                    V(x * 1.12f, 0.4f, -0.15f), V(x * 1.14f, 0.62f, -0.05f), V(x * 1.14f, 0.66f, 0.15f), V(x * 1.12f, 0.46f, 0.3f)
                }, 8), 0.01f, _m.Chrome);
            }
            foreach (float z in new[] { -0.6f, 0.25f })
                mb.Rod(V(-0.3f, 0.02f, z), V(0.3f, 0.02f, z), 0.009f, _m.Chrome);
            mb.Rod(V(-0.3f, 0.38f, -0.1f), V(0.3f, 0.38f, -0.1f), 0.009f, _m.Chrome);
            using (mb.Place(top + V(0.02f, -0.18f, -0.1f), Quaternion.Euler(55f, 8f, -6f))) mb.Pillow(0.42f, 0.36f, 0.15f, pillow, 9);
        }

        /// <summary>Hexagonal wire side table (powder-coated), top at <paramref name="h"/>.</summary>
        public void WireTable(MeshBuilder mb, float r, float h)
        {
            var ring = new Vector3[7];
            for (int i = 0; i <= 6; i++) { float a = i * Mathf.PI / 3f; ring[i] = V(Mathf.Cos(a) * r, h, Mathf.Sin(a) * r); }
            mb.Tube(ring, 0.006f, _m.WhiteMetal, 8);
            float zMax = r * 0.866f;
            for (float z = -zMax + 0.025f; z < zMax; z += 0.028f)
            {
                float w = r - Mathf.Abs(z) / 1.732f;
                mb.Rod(V(-w, h - 0.004f, z), V(w, h - 0.004f, z), 0.0025f, _m.WhiteMetal, 5);
            }
            for (int i = 0; i < 6; i += 2)
            {
                Vector3 c = ring[i];
                mb.Rod(c, V(c.x * 0.75f, 0f, c.z * 0.75f), 0.005f, _m.WhiteMetal, 6);
            }
        }

        public void DiningChair(MeshBuilder mb, Material fabric)
        {
            foreach (var x in new[] { -0.2f, 0.2f })
            foreach (var z in new[] { -0.2f, 0.2f })
                mb.Rod(V(x, 0, z), V(x * 0.93f, 0.44f, z * 0.93f), 0.013f, _m.OakLight, 8);
            mb.RoundBox(V(-0.235f, 0.42f, -0.24f), V(0.235f, 0.5f, 0.23f), 0.035f, fabric);
            using (mb.Place(V(0, 0.48f, 0.21f), Quaternion.Euler(9f, 0, 0)))
                mb.RoundBox(V(-0.22f, 0.08f, -0.03f), V(0.22f, 0.4f, 0.035f), 0.03f, fabric);
        }

        public void BarStool(MeshBuilder mb)
        {
            for (int i = 0; i < 4; i++)
            {
                float a = i * Mathf.PI * 0.5f + Mathf.PI * 0.25f;
                Vector3 d = V(Mathf.Cos(a), 0, Mathf.Sin(a));
                mb.Rod(d * 0.21f, d * 0.14f + Vector3.up * 0.7f, 0.011f, _m.BlackMetal);
            }
            mb.Lathe(V(0, 0.28f, 0), new[] { new Vector2(0.175f, 0), new Vector2(0.175f, 0.012f) }, 20, _m.Brass, true, true);
            mb.Lathe(V(0, 0.7f, 0), new[] { new Vector2(0.17f, 0), new Vector2(0.19f, 0.03f), new Vector2(0.19f, 0.06f), new Vector2(0.17f, 0.075f), new Vector2(0f, 0.08f) }, 24, _m.Leather);
        }

        // ================================================================== tables
        public void RoundTable(MeshBuilder mb, float r, float h, Material m)
        {
            mb.Lathe(Vector3.zero, new[]
            {
                new Vector2(r * 0.92f, 0), new Vector2(r, 0.03f), new Vector2(r, h - 0.02f), new Vector2(r - 0.02f, h)
            }, 40, m, capTop: true);
        }

        public void DiningTable(MeshBuilder mb, float length, float width)
        {
            float L = length * 0.5f, W = width * 0.5f;
            mb.RoundBox(V(-W, 0.71f, -L), V(W, 0.76f, L), 0.012f, _m.OakLight);
            foreach (var z in new[] { -L + 0.35f, L - 0.43f })
                mb.Bevel(V(-W + 0.12f, 0, z), V(W - 0.12f, 0.71f, z + 0.08f), _m.OakLight);
            mb.Bevel(V(-0.04f, 0.5f, -L + 0.43f), V(0.04f, 0.58f, L - 0.43f), _m.OakLight);
        }

        public void Rug(MeshBuilder mb, float w, float d, Material m, Material border)
        {
            mb.Box(V(-w * 0.5f, 0.002f, -d * 0.5f), V(w * 0.5f, 0.014f, d * 0.5f), BoxMats.All(m).Without(yn: true));
            if (border == null) return;
            const float b = 0.07f, i = 0.12f;
            float x0 = -w * 0.5f + i, x1 = w * 0.5f - i, z0 = -d * 0.5f + i, z1 = d * 0.5f - i;
            var bm = BoxMats.All(border).Without(yn: true);
            mb.Box(V(x0, 0.014f, z0), V(x1, 0.0152f, z0 + b), bm);
            mb.Box(V(x0, 0.014f, z1 - b), V(x1, 0.0152f, z1), bm);
            mb.Box(V(x0, 0.014f, z0 + b), V(x0 + b, 0.0152f, z1 - b), bm);
            mb.Box(V(x1 - b, 0.014f, z0 + b), V(x1, 0.0152f, z1 - b), bm);
        }

        // ================================================================== bedroom
        /// <summary>
        /// Bed with the head against the wall at z = 0; the foot points to -Z. The duvet is draped cloth that rolls
        /// over the mattress edge and hangs in folds, pillows are sewn shapes, the throw hangs over both sides.
        /// </summary>
        public void Bed(MeshBuilder mb, float width, float length, Material headboard, Material throwMat, int seed = 1)
        {
            float W = width * 0.5f;
            mb.Box(V(-W + 0.1f, 0, -length + 0.1f), V(W - 0.1f, 0.1f, -0.2f), _m.BlackMetal);
            mb.RoundBox(V(-W - 0.04f, 0.1f, -length - 0.04f), V(W + 0.04f, 0.3f, -0.08f), 0.006f, _m.Walnut, 2);
            // mattress in a fitted sheet
            mb.RoundBox(V(-W + 0.01f, 0.29f, -length + 0.01f), V(W - 0.01f, 0.52f, -0.1f), 0.06f, _m.Cloth, 3, 6, 0.01f, 0.002f, seed);
            // duvet: turned down below the pillows, falling over both sides and the foot
            float duvetTop = 0.56f;
            mb.Drape(new Rect(-W + 0.02f, -length + 0.02f, width - 0.04f, length - 0.62f), duvetTop, 0.07f, 0.2f,
                     true, true, true, false, 0.007f, _m.Cloth, seed + 2);
            // the turned-back band
            mb.RoundBox(V(-W - 0.03f, duvetTop - 0.02f, -0.86f), V(W + 0.03f, duvetTop + 0.035f, -0.58f), 0.025f, _m.Cloth, 3, 8, 0.012f, 0.004f, seed + 3);
            // throw across the foot, hanging over the sides
            mb.Drape(new Rect(-W + 0.02f, -length + 0.1f, width - 0.04f, 0.55f), duvetTop + 0.022f, 0.1f, 0.3f,
                     true, true, false, false, 0.006f, throwMat, seed + 4);
            // pillows: two sleeping pillows against the headboard, two in front, one accent cushion
            for (int s = -1; s <= 1; s += 2)
            {
                using (mb.Place(V(s * W * 0.48f, 0.76f, -0.23f), Quaternion.Euler(22f, s * 4f, s * 2f)))
                    mb.Pillow(W * 0.9f, 0.5f, 0.2f, _m.Cloth, seed * 10 + s + 1, 0.3f);
                using (mb.Place(V(s * W * 0.46f, 0.72f, -0.44f), Quaternion.Euler(30f, -s * 6f, -s * 3f)))
                    mb.Pillow(W * 0.82f, 0.45f, 0.17f, _m.SoftWhite, seed * 10 + s + 5, 0.4f);
            }
            using (mb.Place(V(W * 0.12f, 0.77f, -0.66f), Quaternion.Euler(28f, -12f, 8f)))
                mb.Pillow(0.45f, 0.42f, 0.17f, throwMat == _m.Terracotta ? _m.Charcoal : throwMat, seed * 10 + 9, 0.2f);
            // upholstered headboard spanning the nightstands
            mb.RoundBox(V(-W - 0.62f, 0.2f, -0.1f), V(W + 0.62f, 1.3f, 0f), 0.04f, headboard, 3, 6, 0.012f, 0.002f, seed + 6);
        }

        /// <summary>Floating nightstand against the wall (z = 0) with a table lamp.</summary>
        public void Nightstand(MeshBuilder mb, bool lamp = true)
        {
            mb.RoundBox(V(-0.25f, 0.28f, -0.42f), V(0.25f, 0.56f, 0f), 0.01f, _m.Walnut);
            mb.Box(V(-0.24f, 0.418f, -0.4205f), V(0.24f, 0.422f, -0.415f), _m.BlackMetal);
            mb.Box(V(-0.06f, 0.44f, -0.435f), V(0.06f, 0.452f, -0.42f), _m.Brass);
            if (lamp) TableLamp(mb, V(0.06f, 0.56f, -0.2f), 0.2f);
            Books(mb, V(-0.18f, 0.56f, -0.3f), 0.2f, 0.035f, 3, true);
        }

        public void TableLamp(MeshBuilder mb, Vector3 p, float r)
        {
            mb.Lathe(p, new[]
            {
                new Vector2(0.05f, 0), new Vector2(0.09f, 0.04f), new Vector2(0.11f, 0.13f), new Vector2(0.08f, 0.24f),
                new Vector2(0.025f, 0.3f), new Vector2(0.012f, 0.36f), new Vector2(0f, 0.37f)
            }, 20, _m.Stoneware);
            Shade(mb, p + Vector3.up * 0.3f, r, r * 0.85f, 0.24f);
        }

        /// <summary>Two-sided open drum shade (emissive fabric).</summary>
        void Shade(MeshBuilder mb, Vector3 p, float rBottom, float rTop, float h)
        {
            mb.Lathe(p, new[] { new Vector2(rBottom, 0), new Vector2(rTop, h) }, 28, _m.LampShade);
            mb.Lathe(p, new[] { new Vector2(rTop - 0.003f, h), new Vector2(rBottom - 0.003f, 0) }, 28, _m.LampShade);
        }

        public void FloorLamp(MeshBuilder mb)
        {
            mb.Lathe(Vector3.zero, new[] { new Vector2(0.17f, 0), new Vector2(0.17f, 0.025f), new Vector2(0.03f, 0.03f), new Vector2(0f, 0.03f) }, 28, _m.Travertine);
            mb.Rod(V(0, 0.02f, 0), V(0, 1.42f, 0), 0.011f, _m.Brass);
            Shade(mb, V(0, 1.2f, 0), 0.24f, 0.2f, 0.34f);
        }

        /// <summary>
        /// Floor-to-ceiling cabinetry run against the wall: flush doors with thin dark seams (the carcass face behind
        /// the gaps is dark), push-to-open when <paramref name="handles"/> is false.
        /// </summary>
        public void Wardrobe(MeshBuilder mb, float length, float height, float depth, Material front, float doorWidth = 0.5f, bool handles = true)
        {
            float L = length * 0.5f;
            mb.Box(V(-L, 0, -depth + 0.02f), V(L, 0.06f, 0f), _m.BlackMetal);
            mb.Box(V(-L, 0.06f, -depth + 0.02f), V(L, height, 0f), BoxMats.All(front).With(zn: _m.Felt));
            int n = Mathf.Max(1, Mathf.RoundToInt(length / doorWidth));
            for (int i = 0; i < n; i++)
            {
                float a = Mathf.Lerp(-L, L, i / (float)n) + 0.0015f, b = Mathf.Lerp(-L, L, (i + 1) / (float)n) - 0.0015f;
                mb.Bevel(V(a, 0.062f, -depth), V(b, height - 0.003f, -depth + 0.02f), front, 0.0015f);
                if (!handles) continue;
                float hx = (i % 2 == 0) ? b - 0.05f : a + 0.04f;
                mb.Bevel(V(hx, 0.9f, -depth - 0.03f), V(hx + 0.012f, 1.5f, -depth), _m.BlackMetal, 0.002f);
            }
        }

        public void Desk(MeshBuilder mb, float length)
        {
            float L = length * 0.5f;
            mb.RoundBox(V(-L, 0.72f, -0.6f), V(L, 0.75f, 0f), 0.004f, _m.OakLight, 1);
            foreach (var x in new[] { -L + 0.04f, L - 0.06f })
                mb.Box(V(x, 0, -0.56f), V(x + 0.025f, 0.72f, -0.04f), _m.BlackMetal);
            TableLamp(mb, V(-L + 0.25f, 0.75f, -0.2f), 0.15f);
            Books(mb, V(L - 0.35f, 0.75f, -0.2f), 0.28f, 0.03f, 2, true);
        }

        // ================================================================== storage & decor
        /// <summary>Floating fluted walnut cabinet against the wall at height <paramref name="lift"/>.</summary>
        public void FlutedCabinet(MeshBuilder mb, float length, float height, float depth, float lift)
        {
            float L = length * 0.5f;
            mb.Bevel(V(-L, lift, -depth + 0.02f), V(L, lift + height, 0), _m.Walnut, 0.002f);
            FlutedPanel(mb, -L, L, lift, lift + height, -depth + 0.02f, _m.Walnut, 0.03f);
            mb.Bevel(V(-L - 0.005f, lift + height, -depth - 0.005f), V(L + 0.005f, lift + height + 0.025f, 0), _m.Travertine, 0.003f);
        }

        /// <summary>Vertical half-round-ish ribs along X at depth z (facing -Z).</summary>
        public void FlutedPanel(MeshBuilder mb, float x0, float x1, float y0, float y1, float z, Material m, float pitch)
        {
            int n = Mathf.Max(1, Mathf.FloorToInt((x1 - x0) / pitch));
            float w = (x1 - x0) / n;
            for (int i = 0; i < n; i++)
            {
                float a = x0 + i * w, b = a + w;
                mb.RoundBox(V(a + 0.0015f, y0, z - w * 0.45f), V(b - 0.0015f, y1, z + 0.001f), w * 0.4f, m, 2);
            }
        }

        /// <summary>
        /// Acoustic slat panel against the wall at depth z (facing -Z): solid-wood slats, each cut from a different
        /// plank of the atlas, on a black felt backing so the gaps read as deep shadow lines.
        /// </summary>
        public void SlatPanel(MeshBuilder mb, float x0, float x1, float y0, float y1, float z, float slat = 0.027f, float gap = 0.014f, float depth = 0.021f)
        {
            mb.Box(V(x0, y0, z - 0.004f), V(x1, y1, z), BoxMats.All(_m.Felt).Without(zp: true));
            float pitch = slat + gap;
            int n = Mathf.Max(1, Mathf.FloorToInt((x1 - x0 + gap) / pitch));
            float start = x0 + (x1 - x0 - (n * pitch - gap)) * 0.5f;
            for (int i = 0; i < n; i++)
            {
                float a = start + i * pitch;
                int plank = (int)(Noise.Hash((int)(a * 1000f), 3, 17) % 8);
                float u0 = plank / 8f + 0.01f, u1 = (plank + 1) / 8f - 0.01f;
                mb.Slat(V(0, 0, z - 0.004f), Vector3.back, a, a + slat, y0, y1, 0f, depth, _m.SlatWood, u0, u1, Noise.Hash01(i, 5, 9) * 2f);
            }
        }

        /// <summary>
        /// Oak open shelving with an irregular grid of cubbies (back at z = 0), styled with books, ceramics and a
        /// small plant on the decor builder.
        /// </summary>
        public void CubbyShelf(MeshBuilder mb, MeshBuilder decor, float width, float height, float depth, int seed)
        {
            const float t = 0.02f;
            float W = width * 0.5f;
            var wood = _m.OakLight;
            mb.Bevel(V(-W, 0, -depth), V(-W + t, height, 0), wood, 0.002f);
            mb.Bevel(V(W - t, 0, -depth), V(W, height, 0), wood, 0.002f);
            mb.Bevel(V(-W, height - t, -depth), V(W, height, 0), wood, 0.002f);
            mb.Box(V(-W + t, 0, -0.012f), V(W - t, height - t, 0), wood);
            var rng = new Rng(seed);
            float y = 0f;
            int row = 0;
            while (y < height - 0.3f)
            {
                float rowH = Mathf.Min(height - t - y, rng.Range(0.3f, 0.42f));
                mb.Bevel(V(-W + t, y, -depth), V(W - t, y + t, 0), wood, 0.002f);
                // 1-3 vertical dividers, staggered row to row
                int cells = 2 + rng.Range(0, 2);
                float x = -W + t;
                for (int c = 0; c < cells; c++)
                {
                    float cw = c == cells - 1 ? W - t - x : (width - 2 * t) / cells * rng.Range(0.7f, 1.3f);
                    float xe = Mathf.Min(W - t, x + cw);
                    if (c < cells - 1) mb.Bevel(V(xe - t * 0.5f, y + t, -depth), V(xe + t * 0.5f, y + rowH, 0), wood, 0.002f);
                    // styling per cell
                    float cellW = xe - x - t;
                    int kind = rng.Range(0, 5);
                    Vector3 floor = V(x + t, y + t, -depth * 0.5f);
                    if (kind <= 1) Books(decor, floor + V(0.02f, 0, 0), Mathf.Min(cellW - 0.05f, rng.Range(0.12f, 0.25f)), 0.035f, 0);
                    else if (kind == 2) Books(decor, floor + V(cellW * 0.5f, 0, 0), 0.2f, 0.04f, rng.Range(2, 5), true);
                    else if (kind == 3) Vase(decor, floor + V(cellW * 0.5f, 0, 0), rng.Range(0.14f, 0.22f), row % 2 == 0 ? _m.Stoneware : _m.Charcoal, rng.Range(0, 2));
                    x = xe;
                }
                y += rowH;
                row++;
            }
        }

        /// <summary>Floating high-gloss TV console with an open niche, soundbar and TV above (against the wall).</summary>
        public void TvConsole(MeshBuilder mb, MeshBuilder decor, float length, float lift, float tvWidth)
        {
            float L = length * 0.5f, h = 0.22f, D = 0.42f, t = 0.035f, nx = L * 0.55f;
            var g = _m.GlossWhite;
            mb.Bevel(V(-L, lift, -D), V(L, lift + t, 0), g, 0.003f);                 // bottom
            mb.Bevel(V(-L, lift + h - t, -D), V(L, lift + h, 0), g, 0.003f);         // top
            mb.Bevel(V(-L, lift + t, -D), V(-nx, lift + h - t, 0), g, 0.003f);       // closed left
            mb.Bevel(V(nx, lift + t, -D), V(L, lift + h - t, 0), g, 0.003f);         // closed right
            mb.Box(V(-nx, lift + t, -0.012f), V(nx, lift + h - t, 0), g);            // niche back
            mb.RoundBox(V(-0.4f, lift + t, -D + 0.08f), V(0.4f, lift + t + 0.07f, -D + 0.17f), 0.02f, _m.BlackGlass, 2);
            float tvW = tvWidth * 0.5f, tvH = tvWidth * 0.5625f;
            float ty = lift + h + 0.35f;
            mb.Bevel(V(-tvW, ty, -0.05f), V(tvW, ty + tvH, -0.02f), _m.BlackMetal, 0.003f);
            mb.Box(V(-tvW + 0.006f, ty + 0.006f, -0.0505f), V(tvW - 0.006f, ty + tvH - 0.006f, -0.049f), _m.Screen);
            Vase(decor, V(L - 0.2f, lift + h, -0.2f), 0.3f, _m.Ceramic, 0);
            Twigs(decor, V(L - 0.2f, lift + h + 0.26f, -0.2f), 0.45f, 11);
            Books(decor, V(-L + 0.25f, lift + h, -0.22f), 0.2f, 0.035f, 3, true);
        }

        /// <summary>Bare branches for a vase: thin dark tubes that fork upward.</summary>
        public void Twigs(MeshBuilder mb, Vector3 p, float h, int seed)
        {
            var rng = new Rng(seed);
            for (int i = 0; i < 4; i++)
            {
                Vector3 dir = V(rng.Range(-0.35f, 0.35f), 1f, rng.Range(-0.35f, 0.35f)).normalized;
                Vector3 a = p, b = p + dir * h * rng.Range(0.6f, 1f);
                Vector3 mid = Vector3.Lerp(a, b, 0.5f) + V(rng.Range(-0.03f, 0.03f), 0, rng.Range(-0.03f, 0.03f));
                mb.Tube(SoftShapes.Spline(new[] { a, mid, b }, 4), 0.004f, _m.Walnut, 5);
                Vector3 fork = Vector3.Lerp(a, b, rng.Range(0.45f, 0.7f));
                mb.Tube(new[] { fork, fork + (dir + V(rng.Range(-0.6f, 0.6f), 0.3f, rng.Range(-0.6f, 0.6f))).normalized * h * 0.25f }, 0.0025f, _m.Walnut, 4);
            }
        }

        public void Books(MeshBuilder mb, Vector3 p, float span, float t, int count, bool lying = false)
        {
            var mats = new[] { _m.Terracotta, _m.Linen, _m.Charcoal, _m.Sage, _m.Boucle };
            var rng = new Rng(Mathf.RoundToInt(p.x * 131 + p.z * 71 + p.y * 17));
            if (lying)
            {
                float y = p.y;
                for (int i = 0; i < count; i++)
                {
                    float w = rng.Range(0.16f, 0.22f), d = rng.Range(0.22f, 0.28f), th = rng.Range(0.02f, t);
                    using (mb.Place(V(p.x, y, p.z), rng.Range(-8f, 8f)))
                        mb.Box(V(-w * 0.5f, 0, -d * 0.5f), V(w * 0.5f, th, d * 0.5f), mats[rng.Range(0, mats.Length)]);
                    y += th;
                }
                return;
            }
            float x = p.x;
            while (x < p.x + span)
            {
                float w = rng.Range(0.02f, t), h = rng.Range(0.18f, 0.26f), d = rng.Range(0.15f, 0.2f);
                mb.Box(V(x, p.y, p.z - d * 0.5f), V(x + w, p.y + h, p.z + d * 0.5f), mats[rng.Range(0, mats.Length)]);
                x += w + 0.002f;
            }
        }

        public void Vase(MeshBuilder mb, Vector3 p, float h, Material m, int kind = 0)
        {
            Vector2[] prof = kind == 0
                ? new[] { new Vector2(0.05f, 0), new Vector2(0.09f, 0.1f), new Vector2(0.1f, 0.35f), new Vector2(0.06f, 0.75f), new Vector2(0.035f, 0.9f), new Vector2(0.045f, 1f), new Vector2(0.03f, 0.98f), new Vector2(0.02f, 0.8f) }
                : kind == 1
                    ? new[] { new Vector2(0.08f, 0), new Vector2(0.17f, 0.2f), new Vector2(0.2f, 0.45f), new Vector2(0.14f, 0.8f), new Vector2(0.1f, 0.9f), new Vector2(0.12f, 1f), new Vector2(0.09f, 0.97f), new Vector2(0.05f, 0.7f) }
                    : new[] { new Vector2(0.14f, 0), new Vector2(0.3f, 0.12f), new Vector2(0.32f, 0.2f), new Vector2(0.3f, 0.24f), new Vector2(0.26f, 0.2f), new Vector2(0.1f, 0.08f), new Vector2(0f, 0.06f) };
            for (int i = 0; i < prof.Length; i++) prof[i] *= h;
            mb.Lathe(p, prof, 24, m);
        }

        /// <summary>Framed canvas on a wall with normal <paramref name="n"/>; atlas cell 0..3.</summary>
        public void Artwork(MeshBuilder mb, Vector3 center, Vector3 n, float w, float h, int cell, Material frame = null)
        {
            Vector3 right = Vector3.Cross(n, Vector3.up).normalized;
            Vector3 half = right * (w * 0.5f + 0.025f) + Vector3.up * (h * 0.5f + 0.025f);
            Vector3 a = center - half, b = center + half + n * 0.04f;
            mb.Bevel(Vector3.Min(a, b), Vector3.Max(a, b), frame ?? _m.BlackMetal, 0.004f);
            var uv = new Rect((cell % 2) * 0.5f + 0.01f, (cell / 2) * 0.5f + 0.01f, 0.48f, 0.48f);
            mb.Picture(center + n * 0.0405f, n, w, h, uv, _m.Art);
        }

        // ================================================================== lighting fixtures (geometry only)
        public void PendantGlobe(MeshBuilder mb, Vector3 ceiling, float drop, float r)
        {
            Vector3 c = ceiling + Vector3.down * drop;
            mb.Rod(ceiling, c + Vector3.up * r, 0.003f, _m.BlackMetal, 5);
            mb.Lathe(ceiling + Vector3.down * 0.02f, new[] { new Vector2(0.05f, 0), new Vector2(0.05f, 0.02f) }, 16, _m.Brass, false, true);
            mb.Lathe(c + Vector3.up * r * 0.92f, new[] { new Vector2(0.03f, 0), new Vector2(0.025f, 0.06f) }, 12, _m.Brass, true);
            mb.Sphere(c, r, _m.Globe, 24, 14);
        }

        public void LinearPendant(MeshBuilder mb, Vector3 ceiling, float drop, float length, bool alongZ)
        {
            Vector3 ax = alongZ ? Vector3.forward : Vector3.right, side = alongZ ? Vector3.right : Vector3.forward;
            Vector3 c = ceiling + Vector3.down * drop;
            foreach (var s in new[] { -0.4f, 0.4f })
                mb.Rod(ceiling + ax * length * s, c + ax * length * s, 0.002f, _m.BlackMetal, 4);
            Vector3 mn = c - ax * length * 0.5f - side * 0.03f - Vector3.up * 0.04f, mx = c + ax * length * 0.5f + side * 0.03f;
            mb.Box(mn, mx, BoxMats.All(_m.BlackMetal).With(yn: _m.Led));
        }

        /// <summary>Square trimless downlight: a shallow recess with the diffuser set slightly back.</summary>
        public void Downlight(MeshBuilder mb, Vector3 ceiling)
        {
            const float a = 0.045f;
            mb.Box(ceiling + V(-a, -0.0015f, -a), ceiling + V(a, -0.001f, a), BoxMats.All(_m.Downlight).Without(yp: true));
        }

        /// <summary>Recessed linear LED profile in the ceiling between two points.</summary>
        public void LedSlot(MeshBuilder mb, Vector3 a, Vector3 b, float width = 0.03f)
        {
            Vector3 d = (b - a).normalized, side = Vector3.Cross(Vector3.up, d) * (width * 0.5f);
            Vector3 mn = Vector3.Min(a - side, b + side), mx = Vector3.Max(a - side, b + side);
            mb.Box(new Vector3(mn.x, a.y - 0.0015f, mn.z), new Vector3(mx.x, a.y - 0.001f, mx.z), BoxMats.All(_m.Led).Without(yp: true));
        }

        // ================================================================== kitchen
        /// <summary>Base run against the wall: recessed plinth, walnut fronts with a J-groove, marble worktop.</summary>
        public void KitchenBase(MeshBuilder mb, float length, float sinkAt = float.NaN, float hobAt = float.NaN)
        {
            float L = length * 0.5f, D = 0.62f, top = 0.9f;
            mb.Box(V(-L, 0, -D + 0.07f), V(L, 0.1f, 0), _m.BlackMetal);
            mb.Box(V(-L, 0.1f, -D + 0.02f), V(L, top - 0.03f, 0), _m.Walnut);
            int n = Mathf.Max(1, Mathf.RoundToInt(length / 0.6f));
            for (int i = 0; i < n; i++)
            {
                float a = Mathf.Lerp(-L, L, i / (float)n) + 0.002f, b = Mathf.Lerp(-L, L, (i + 1) / (float)n) - 0.002f;
                mb.Bevel(V(a, 0.102f, -D), V(b, top - 0.075f, -D + 0.02f), _m.Walnut, 0.002f);
                mb.Box(V(a, top - 0.071f, -D + 0.005f), V(b, top - 0.03f, -D + 0.02f), _m.BlackMetal); // grip groove
            }
            mb.Bevel(V(-L, top - 0.03f, -D - 0.02f), V(L, top, 0), _m.Marble, 0.003f);
            if (!float.IsNaN(sinkAt))
            {
                mb.Box(V(sinkAt - 0.38f, top + 0.0005f, -0.5f), V(sinkAt + 0.38f, top + 0.001f, -0.1f), BoxMats.All(_m.BlackMetal).Without(yn: true));
                Vector3 tap = V(sinkAt, top, -0.06f);
                mb.Lathe(tap, new[] { new Vector2(0.022f, 0), new Vector2(0.018f, 0.04f), new Vector2(0.012f, 0.3f), new Vector2(0f, 0.3f) }, 12, _m.Brass);
                mb.Rod(tap + Vector3.up * 0.29f, tap + V(0, 0.3f, -0.22f), 0.011f, _m.Brass);
                mb.Rod(tap + V(0, 0.3f, -0.22f), tap + V(0, 0.22f, -0.24f), 0.011f, _m.Brass);
            }
            if (!float.IsNaN(hobAt)) Hob(mb, V(hobAt, top, -0.31f));
        }

        void Hob(MeshBuilder mb, Vector3 c)
        {
            mb.Box(c + V(-0.4f, 0.0005f, -0.26f), c + V(0.4f, 0.004f, 0.26f), BoxMats.All(_m.BlackGlass).Without(yn: true));
            foreach (var x in new[] { -0.2f, 0.2f })
            foreach (var z in new[] { -0.12f, 0.12f })
                mb.Disk(c + V(x, 0.0045f, z), 0.1f, _m.Charcoal, false, 24);
        }

        /// <summary>Full-height column bank: fridge, two ovens, pantry. Against the wall at z = 0.</summary>
        public void TallUnits(MeshBuilder mb, float length, float height, Material front)
        {
            float L = length * 0.5f, D = 0.64f;
            mb.Box(V(-L, 0, -D + 0.07f), V(L, 0.1f, 0), _m.BlackMetal);
            mb.Box(V(-L, 0.1f, -D + 0.02f), V(L, height, 0), BoxMats.All(front).With(zn: _m.Felt));
            int n = Mathf.Max(1, Mathf.RoundToInt(length / 0.6f));
            for (int i = 0; i < n; i++)
            {
                float a = Mathf.Lerp(-L, L, i / (float)n) + 0.002f, b = Mathf.Lerp(-L, L, (i + 1) / (float)n) - 0.002f;
                bool ovens = i == n / 2;
                if (ovens)
                {
                    mb.Bevel(V(a, 0.102f, -D), V(b, 0.9f, -D + 0.02f), front, 0.002f);
                    mb.Box(V(a, 0.9f, -D - 0.005f), V(b, 1.5f, -D + 0.02f), _m.BlackGlass);
                    mb.Box(V(a, 1.502f, -D - 0.005f), V(b, 1.95f, -D + 0.02f), _m.BlackGlass);
                    mb.Box(V(a + 0.05f, 1.42f, -D - 0.03f), V(b - 0.05f, 1.44f, -D - 0.005f), _m.Brass);
                    mb.Box(V(a + 0.05f, 1.87f, -D - 0.03f), V(b - 0.05f, 1.89f, -D - 0.005f), _m.Brass);
                    mb.Bevel(V(a, 1.954f, -D), V(b, height - 0.004f, -D + 0.02f), front, 0.002f);
                }
                else mb.Bevel(V(a, 0.102f, -D), V(b, height - 0.004f, -D + 0.02f), front, 0.002f);
                float hx = i % 2 == 0 ? b - 0.05f : a + 0.04f;
                mb.Bevel(V(hx, 0.95f, -D - 0.03f), V(hx + 0.012f, 1.75f, -D), _m.BlackMetal, 0.002f);
            }
        }

        /// <summary>Waterfall island centred on the origin, long side along X; hob on top, seating overhang on -Z.</summary>
        public void Island(MeshBuilder mb, float length, float width)
        {
            float L = length * 0.5f, W = width * 0.5f, top = 0.92f;
            mb.Bevel(V(-L, top - 0.04f, -W), V(L, top, W), _m.Marble, 0.004f);
            mb.Bevel(V(-L, 0, -W), V(-L + 0.04f, top - 0.04f, W), _m.Marble, 0.004f);
            mb.Bevel(V(L - 0.04f, 0, -W), V(L, top - 0.04f, W), _m.Marble, 0.004f);
            mb.Box(V(-L + 0.04f, 0, -W + 0.3f), V(L - 0.04f, top - 0.04f, W - 0.02f), _m.Walnut);
            mb.Box(V(-L + 0.04f, 0, -W + 0.3f), V(L - 0.04f, 0.1f, -W + 0.34f), _m.BlackMetal);
            int n = Mathf.RoundToInt((length - 0.08f) / 0.6f);
            for (int i = 1; i < n; i++)
            {
                float x = Mathf.Lerp(-L + 0.04f, L - 0.04f, i / (float)n);
                mb.Box(V(x - 0.002f, 0.1f, W - 0.021f), V(x + 0.002f, top - 0.04f, W - 0.019f), _m.BlackMetal);
            }
            Hob(mb, V(0.1f, top, 0.12f));
        }

        // ================================================================== bathroom
        public void Vanity(MeshBuilder mb, float length, int basins, float mirrorH)
        {
            float L = length * 0.5f;
            mb.RoundBox(V(-L, 0.45f, -0.5f), V(L, 0.83f, 0), 0.008f, _m.Walnut);
            mb.Box(V(-L + 0.01f, 0.64f, -0.502f), V(L - 0.01f, 0.645f, -0.495f), _m.BlackMetal);
            mb.Box(V(-L - 0.01f, 0.83f, -0.52f), V(L + 0.01f, 0.855f, 0), _m.Marble);
            for (int i = 0; i < basins; i++)
            {
                float x = basins == 1 ? 0 : Mathf.Lerp(-L * 0.5f, L * 0.5f, i / (float)(basins - 1));
                // vessel basin: outer wall up to the rim, then down inside to the bowl floor
                mb.Lathe(V(x, 0.855f, -0.27f), new[]
                {
                    new Vector2(0.1f, 0), new Vector2(0.19f, 0.05f), new Vector2(0.21f, 0.12f), new Vector2(0.205f, 0.135f),
                    new Vector2(0.19f, 0.125f), new Vector2(0.16f, 0.05f), new Vector2(0f, 0.035f)
                }, 32, _m.Ceramic);
                Vector3 tap = V(x, 1.12f, -0.01f);
                mb.Rod(tap, tap + V(0, 0, -0.17f), 0.01f, _m.Brass);
                mb.Disk(tap + V(0, 0, 0.005f), 0.03f, _m.Brass, false, 12);
                // round backlit mirror
                Vector3 mc = V(x, 0.95f + mirrorH * 0.5f + 0.3f, -0.012f);
                using (mb.Place(mc, Quaternion.Euler(90f, 0, 0)))
                {
                    mb.Lathe(Vector3.zero, new[] { new Vector2(mirrorH * 0.5f + 0.008f, 0), new Vector2(mirrorH * 0.5f + 0.008f, 0.008f) }, 48, _m.Led);
                    mb.Disk(V(0, -0.012f, 0), mirrorH * 0.5f, _m.Mirror, true, 48);
                    mb.Lathe(V(0, -0.012f, 0), new[] { new Vector2(mirrorH * 0.5f, 0), new Vector2(mirrorH * 0.5f, 0.004f) }, 48, _m.Brass);
                }
            }
            mb.Box(V(-0.3f, 0.3f, -0.06f), V(-0.12f, 0.302f, -0.02f), _m.Brass);
        }

        public void Toilet(MeshBuilder mb)
        {
            mb.RoundBox(V(-0.18f, 0.2f, -0.55f), V(0.18f, 0.42f, 0f), 0.1f, _m.Ceramic, 4);
            mb.RoundBox(V(-0.185f, 0.42f, -0.56f), V(0.185f, 0.44f, -0.02f), 0.01f, _m.Ceramic);
            mb.Box(V(-0.12f, 1.0f, -0.012f), V(0.12f, 1.16f, 0f), _m.Brass);
        }

        /// <summary>Freestanding oval bathtub centred on the origin (long axis X).</summary>
        public void Bathtub(MeshBuilder mb, float length, float width)
        {
            using (new Shapes.Scope(mb, Matrix4x4.Scale(V(length / width, 1f, 1f))))
                mb.Lathe(Vector3.zero, new[]
                {
                    new Vector2(0f, 0.004f), new Vector2(width * 0.36f, 0f), new Vector2(width * 0.45f, 0.1f), new Vector2(width * 0.5f, 0.4f),
                    new Vector2(width * 0.5f, 0.58f), new Vector2(width * 0.47f, 0.6f), new Vector2(width * 0.44f, 0.56f),
                    new Vector2(width * 0.4f, 0.3f), new Vector2(width * 0.3f, 0.12f), new Vector2(0f, 0.1f)
                }, 48, _m.Ceramic);
            // floor-mounted mixer
            Vector3 p = V(length * 0.5f + 0.15f, 0, 0);
            mb.Lathe(p, new[] { new Vector2(0.025f, 0), new Vector2(0.02f, 0.02f), new Vector2(0.016f, 0.9f), new Vector2(0, 0.9f) }, 12, _m.Brass);
            mb.Rod(p + V(0, 0.88f, 0), p + V(-0.22f, 0.88f, 0), 0.012f, _m.Brass);
            mb.Rod(p + V(-0.22f, 0.88f, 0), p + V(-0.24f, 0.8f, 0), 0.012f, _m.Brass);
        }

        /// <summary>Walk-in shower: tray, frameless glass screen along X at z = <paramref name="screenZ"/>, rain head.</summary>
        public void Shower(MeshBuilder mb, float x0, float x1, float z0, float z1, float screenX0, float screenX1, float ceilingH)
        {
            mb.Box(V(x0, 0, z0), V(x1, 0.02f, z1), BoxMats.All(_m.TileDark).Without(yn: true));
            mb.Box(V((x0 + x1) * 0.5f - 0.3f, 0.0205f, z1 - 0.12f), V((x0 + x1) * 0.5f + 0.3f, 0.021f, z1 - 0.08f), _m.Brass);
            mb.Box(V(screenX0, 0.02f, z0 - 0.005f), V(screenX1, 2.05f, z0 + 0.005f), _m.Glass);
            mb.Box(V(screenX0, 2.05f, z0 - 0.012f), V(screenX1, 2.07f, z0 + 0.012f), _m.BlackMetal);
            Vector3 head = V((x0 + x1) * 0.5f, 0, (z0 + z1) * 0.5f + 0.1f);
            mb.Rod(head + Vector3.up * ceilingH, head + Vector3.up * 2.15f, 0.012f, _m.BlackMetal);
            mb.Lathe(head + Vector3.up * 2.12f, new[] { new Vector2(0.15f, 0), new Vector2(0.15f, 0.012f) }, 32, _m.BlackMetal, true, true);
            Vector3 mixer = V(x1 - 0.01f, 1.1f, (z0 + z1) * 0.5f);
            mb.Box(mixer + V(-0.02f, -0.1f, -0.06f), mixer + V(0.01f, 0.1f, 0.06f), _m.BlackMetal);
        }

        public void TowelRail(MeshBuilder mb, float width, float height)
        {
            float W = width * 0.5f;
            mb.Rod(V(-W, 0.15f, -0.05f), V(-W, height, -0.05f), 0.012f, _m.BlackMetal);
            mb.Rod(V(W, 0.15f, -0.05f), V(W, height, -0.05f), 0.012f, _m.BlackMetal);
            for (float y = 0.35f; y < height; y += 0.22f)
                mb.Rod(V(-W, y, -0.05f), V(W, y, -0.05f), 0.008f, _m.BlackMetal);
            mb.RoundBox(V(-W + 0.03f, height - 0.6f, -0.075f), V(W - 0.03f, height - 0.02f, -0.03f), 0.015f, _m.Towel);
        }

        // ================================================================== living room
        /// <summary>
        /// Double-height media wall against the wall at z = 0: full-height fluted walnut, travertine slab,
        /// floating travertine bench with a linear bio-fireplace, TV.
        /// </summary>
        public void MediaWall(MeshBuilder mb, float length, float height)
        {
            float L = length * 0.5f;
            SlatPanel(mb, -L, L, 0f, height, 0f, 0.032f, 0.016f, 0.024f);
            // travertine slab behind the TV
            mb.Box(V(-1.15f, 0.55f, -0.075f), V(1.15f, 2.55f, -0.03f), _m.Travertine);
            // bench with the fire slot
            mb.Box(V(-L + 0.2f, 0.12f, -0.5f), V(L - 0.2f, 0.52f, -0.03f), BoxMats.All(_m.Travertine));
            mb.Box(V(-0.9f, 0.2f, -0.505f), V(0.9f, 0.44f, -0.2f), _m.BlackGlass);
            mb.Box(V(-0.82f, 0.22f, -0.3f), V(0.82f, 0.25f, -0.24f), _m.Fire);
            for (int i = 0; i < 14; i++)
            {
                float x = -0.78f + i * 0.12f, h = 0.06f + 0.06f * Mathf.Abs(Mathf.Sin(i * 1.7f));
                mb.Box(V(x, 0.25f, -0.28f), V(x + 0.07f, 0.25f + h, -0.26f), _m.Fire);
            }
            mb.Box(V(-0.9f, 0.2f, -0.506f), V(0.9f, 0.44f, -0.5055f), _m.Glass);
            // TV
            mb.Box(V(-0.73f, 1.2f, -0.105f), V(0.73f, 2.03f, -0.075f), _m.BlackMetal);
            mb.Box(V(-0.72f, 1.21f, -0.106f), V(0.72f, 2.02f, -0.104f), _m.Screen);
            // decor on the bench
            Vase(mb, V(L - 0.55f, 0.52f, -0.25f), 0.45f, _m.Stoneware, 0);
            Vase(mb, V(L - 0.8f, 0.52f, -0.22f), 0.28f, _m.Charcoal, 1);
            Books(mb, V(-L + 0.5f, 0.52f, -0.25f), 0.2f, 0.04f, 3, true);
        }

        /// <summary>Cluster chandelier: opal globes on cables of staggered length.</summary>
        public void Chandelier(MeshBuilder mb, Vector3 ceiling, float spread, float minDrop, float maxDrop, int count, int seed)
        {
            var rng = new Rng(seed);
            for (int i = 0; i < count; i++)
            {
                float a = i * 2.39996f, r = spread * 0.42f * Mathf.Sqrt((i + 0.5f) / count);
                Vector3 top = ceiling + V(Mathf.Cos(a) * r, -0.03f, Mathf.Sin(a) * r);
                float drop = Mathf.Lerp(minDrop, maxDrop, rng.Value());
                PendantGlobe(mb, top, drop, rng.Range(0.11f, 0.19f));
            }
        }

        /// <summary>Planter (hollow lathe with a soil disk).</summary>
        public void Planter(MeshBuilder mb, Vector3 p, float r, float h, Material m)
        {
            mb.Lathe(p, new[]
            {
                new Vector2(r * 0.75f, 0), new Vector2(r * 0.95f, h * 0.3f), new Vector2(r, h), new Vector2(r * 0.93f, h),
                new Vector2(r * 0.88f, h * 0.9f), new Vector2(0, h * 0.9f)
            }, 32, m);
            mb.Disk(p + Vector3.up * (h * 0.9f + 0.003f), r * 0.9f, _m.Soil, false, 24);
        }
    }
}
