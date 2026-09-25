using System;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Soft goods and bent metal: parametric surfaces with finite-difference normals, sewn pillows, draped cloth
    /// (duvets, throws) that falls over the edge of what it lies on, and swept tubes along smooth paths.
    /// </summary>
    public static class SoftShapes
    {
        /// <summary>
        /// Grid surface P(u, v), u and v in [0, 1]. Increasing u runs to the viewer's right and increasing v up,
        /// seen from the front side. UVs are the grid coordinates scaled by <paramref name="uvScale"/> (metres).
        /// </summary>
        public static void Surface(this MeshBuilder mb, int nu, int nv, Func<float, float, Vector3> P, Material m, Vector2 uvScale)
        {
            var pos = new Vector3[nu + 1, nv + 1];
            for (int i = 0; i <= nu; i++)
            for (int j = 0; j <= nv; j++)
                pos[i, j] = P(i / (float)nu, j / (float)nv);
            var nrm = new Vector3[nu + 1, nv + 1];
            for (int i = 0; i <= nu; i++)
            for (int j = 0; j <= nv; j++)
            {
                Vector3 du = pos[Mathf.Min(nu, i + 1), j] - pos[Mathf.Max(0, i - 1), j];
                Vector3 dv = pos[i, Mathf.Min(nv, j + 1)] - pos[i, Mathf.Max(0, j - 1)];
                Vector3 n = Vector3.Cross(dv, du);
                nrm[i, j] = n.sqrMagnitude > 1e-14f ? n.normalized : Vector3.up;
            }
            for (int i = 0; i < nu; i++)
            for (int j = 0; j < nv; j++)
            {
                Vector3 a = pos[i, j], b = pos[i + 1, j], c = pos[i + 1, j + 1], d = pos[i, j + 1];
                Vector2 ua = new Vector2(i / (float)nu * uvScale.x, j / (float)nv * uvScale.y);
                Vector2 ub = new Vector2((i + 1) / (float)nu * uvScale.x, ua.y);
                Vector2 uc = new Vector2(ub.x, (j + 1) / (float)nv * uvScale.y);
                Vector2 ud = new Vector2(ua.x, uc.y);
                mb.Triangle(a, d, c, nrm[i, j], nrm[i, j + 1], nrm[i + 1, j + 1], ua, ud, uc, m);
                mb.Triangle(a, c, b, nrm[i, j], nrm[i + 1, j + 1], nrm[i + 1, j], ua, uc, ub, m);
            }
        }

        static float Crease(float x, float y, int seed)
        {
            float n = Noise.Perlin(x, y, 0, 0, seed);
            float c = 1f - Mathf.Abs(n);
            return c * c * c;
        }

        /// <summary>
        /// Sewn pillow standing in the local XY plane, front facing -Z: puffed centre, thin seam at the rim,
        /// corners pulled into points and sides drawn in, soft creases radiating from the corners.
        /// </summary>
        public static void Pillow(this MeshBuilder mb, float width, float height, float thickness, Material m, int seed, float squash = 0f)
        {
            float W = width * 0.5f, H = height * 0.5f, T = thickness * 0.5f;
            Vector3 Pt(float u, float v, float side)
            {
                float x = u * 2f - 1f, y = v * 2f - 1f;
                // outline: sides pulled in at the middle, corners stay out
                float px = x * W * (1f - 0.07f * (1f - y * y));
                float py = y * H * (1f - 0.07f * (1f - x * x));
                float fill = Mathf.Pow(Mathf.Max(0f, 1f - x * x), 0.55f) * Mathf.Pow(Mathf.Max(0f, 1f - y * y), 0.55f);
                // creases concentrate towards the corners where the fabric bunches
                float corner = Mathf.Abs(x * y);
                float cr = Crease(x * 3.1f + seed, y * 2.7f - seed * 0.37f, seed) * 0.5f
                         + Crease((x + y) * 4.3f, (x - y) * 1.3f + seed, seed + 3) * corner;
                float z = T * fill * (1f - squash * 0.5f * (1f - y)) + thickness * 0.09f * (cr - 0.3f) * fill * (0.4f + corner);
                return new Vector3(px, py, -side * z);
            }
            // front (seen from -Z): u right = +X, v up = +Y ; back mirrored so it faces +Z
            mb.Surface(22, 22, (u, v) => Pt(u, v, 1f), m, new Vector2(width, height));
            mb.Surface(22, 22, (u, v) => Pt(1f - u, v, -1f), m, new Vector2(width, height));
        }

        /// <summary>
        /// Cloth lying on a rectangle (top at <paramref name="topY"/>) that rolls over the chosen edges around
        /// radius <paramref name="r"/> and hangs <paramref name="drop"/> metres, with folds in the hanging part.
        /// Hang flags: -X, +X, -Z, +Z edges.
        /// </summary>
        public static void Drape(this MeshBuilder mb, Rect xz, float topY, float r, float drop, bool hx0, bool hx1, bool hz0, bool hz1,
                                 float wrinkle, Material m, int seed)
        {
            float ext = r * Mathf.PI * 0.5f + drop;
            float x0 = xz.xMin - (hx0 ? ext : 0f), x1 = xz.xMax + (hx1 ? ext : 0f);
            float z0 = xz.yMin - (hz0 ? ext : 0f), z1 = xz.yMax + (hz1 ? ext : 0f);
            int nu = Mathf.Clamp(Mathf.RoundToInt((x1 - x0) / 0.035f), 8, 120);
            int nv = Mathf.Clamp(Mathf.RoundToInt((z1 - z0) / 0.035f), 8, 120);
            Vector3 P(float u, float v)
            {
                float x = Mathf.Lerp(x0, x1, u), z = Mathf.Lerp(z0, z1, v);
                float ex = Mathf.Clamp(x, xz.xMin, xz.xMax), ez = Mathf.Clamp(z, xz.yMin, xz.yMax);
                Vector2 off = new Vector2(x - ex, z - ez);
                float e = off.magnitude;
                float top = Crease(x * 5f + seed, z * 3.5f, seed) * wrinkle * 0.5f + Noise.Perlin(x * 2.1f, z * 2.1f + seed, 0, 0, seed + 1) * wrinkle * 0.6f;
                if (e < 1e-5f) return new Vector3(x, topY + top, z);
                Vector2 dir = off / e;
                float h, y;
                float arc = r * Mathf.PI * 0.5f;
                if (e < arc) { float th = e / r; h = r * Mathf.Sin(th); y = topY - r * (1f - Mathf.Cos(th)); }
                else { float hang = e - arc; h = r + hang * 0.06f; y = topY - r - hang; }
                // vertical folds: stronger towards the hem
                float along = ex * Mathf.Abs(dir.y) + ez * Mathf.Abs(dir.x) + (ex + ez) * 0.3f;
                float k = Mathf.Clamp01((e - arc * 0.5f) / Mathf.Max(0.01f, drop));
                // irregular folds: a few broad soft ones plus finer ripples, widening towards the hem
                float fold = (Noise.Perlin(along * 5.5f + seed, e * 1.5f, 0, 0, seed + 2) * 1.2f
                            + Noise.Perlin(along * 13f, e * 4f + seed, 0, 0, seed + 5) * 0.35f) * wrinkle * 2.4f * k;
                h += fold;
                // the hem is not a straight line: hang length varies a little along the edge
                float hem = Noise.Perlin(along * 3.3f, seed * 0.7f, 0, 0, seed + 9) * 0.025f * k;
                return new Vector3(ex + dir.x * h, y + top * (1f - k) + hem, ez + dir.y * h);
            }
            mb.Surface(nu, nv, P, m, new Vector2(x1 - x0, z1 - z0));
        }

        /// <summary>Round tube swept along a smooth path (parallel-transport frames): chrome frames, rails.</summary>
        public static void Tube(this MeshBuilder mb, Vector3[] path, float radius, Material m, int sides = 12)
        {
            int n = path.Length;
            if (n < 2) return;
            var tang = new Vector3[n];
            for (int i = 0; i < n; i++) tang[i] = (path[Mathf.Min(n - 1, i + 1)] - path[Mathf.Max(0, i - 1)]).normalized;
            Vector3 normal = Vector3.Cross(tang[0], Mathf.Abs(tang[0].y) < 0.9f ? Vector3.up : Vector3.right).normalized;
            var ring = new Vector3[n, sides + 1]; var rn = new Vector3[n, sides + 1];
            float[] len = new float[n];
            for (int i = 0; i < n; i++)
            {
                if (i > 0)
                {
                    normal = Quaternion.FromToRotation(tang[i - 1], tang[i]) * normal;
                    len[i] = len[i - 1] + (path[i] - path[i - 1]).magnitude;
                }
                Vector3 bin = Vector3.Cross(normal, tang[i]); // counter-clockwise around the tangent, like Lathe
                for (int k = 0; k <= sides; k++)
                {
                    float a = k * Mathf.PI * 2f / sides;
                    Vector3 d = normal * Mathf.Cos(a) + bin * Mathf.Sin(a);
                    rn[i, k] = d; ring[i, k] = path[i] + d * radius;
                }
            }
            for (int i = 0; i + 1 < n; i++)
            for (int k = 0; k < sides; k++)
            {
                Vector2 ua = new Vector2(k / (float)sides * 0.1f, len[i]), ub = new Vector2((k + 1) / (float)sides * 0.1f, len[i]);
                Vector2 uc = new Vector2(ub.x, len[i + 1]), ud = new Vector2(ua.x, len[i + 1]);
                // winding chosen so faces point along rn (outward)
                mb.Triangle(ring[i, k], ring[i + 1, k], ring[i + 1, k + 1], rn[i, k], rn[i + 1, k], rn[i + 1, k + 1], ua, ud, uc, m);
                mb.Triangle(ring[i, k], ring[i + 1, k + 1], ring[i, k + 1], rn[i, k], rn[i + 1, k + 1], rn[i, k + 1], ua, uc, ub, m);
            }
        }

        /// <summary>Points of a Catmull-Rom spline through the control points (for tubes and cushions following a curve).</summary>
        public static Vector3[] Spline(Vector3[] ctrl, int perSegment)
        {
            var list = new System.Collections.Generic.List<Vector3>();
            for (int i = 0; i + 1 < ctrl.Length; i++)
            {
                Vector3 p0 = ctrl[Mathf.Max(0, i - 1)], p1 = ctrl[i], p2 = ctrl[i + 1], p3 = ctrl[Mathf.Min(ctrl.Length - 1, i + 2)];
                for (int s = 0; s < perSegment; s++)
                {
                    float t = s / (float)perSegment, t2 = t * t, t3 = t2 * t;
                    list.Add(0.5f * (2f * p1 + (-p0 + p2) * t + (2f * p0 - 5f * p1 + 4f * p2 - p3) * t2 + (-p0 + 3f * p1 - 3f * p2 + p3) * t3));
                }
            }
            list.Add(ctrl[ctrl.Length - 1]);
            return list.ToArray();
        }
    }
}
