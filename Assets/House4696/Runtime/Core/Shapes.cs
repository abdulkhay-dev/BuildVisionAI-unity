using System;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Soft primitives on top of <see cref="MeshBuilder"/>: rounded boxes (upholstery), lathes (lamps, vases,
    /// basins), cylinders and ellipsoids. All shapes are emitted in the builder's current local frame, so
    /// <see cref="Place"/> positions and rotates whole pieces of furniture.
    /// </summary>
    public static class Shapes
    {
        /// <summary>Restores the builder's previous transform when disposed.</summary>
        public readonly struct Scope : IDisposable
        {
            readonly MeshBuilder _mb; readonly Matrix4x4 _prev;
            public Scope(MeshBuilder mb, Matrix4x4 local) { _mb = mb; _prev = mb.Transform; mb.Transform = _prev * local; }
            public void Dispose() => _mb.Transform = _prev;
        }

        /// <summary>Local frame at <paramref name="pos"/> rotated by <paramref name="yaw"/> degrees about Y.</summary>
        public static Scope Place(this MeshBuilder mb, Vector3 pos, float yaw = 0f) =>
            new Scope(mb, Matrix4x4.TRS(pos, Quaternion.Euler(0, yaw, 0), Vector3.one));

        public static Scope Place(this MeshBuilder mb, Vector3 pos, Quaternion rot) =>
            new Scope(mb, Matrix4x4.TRS(pos, rot, Vector3.one));

        /// <summary>Yaw that turns the local "front" (-Z) towards <paramref name="dir"/>.</summary>
        public static float Facing(Vector3 dir) => Mathf.Atan2(-dir.x, -dir.z) * Mathf.Rad2Deg;

        // ------------------------------------------------------------------ rounded box
        /// <summary>
        /// Box with rounded edges. <paramref name="puff"/> bulges every flat face outward (upholstery, cushions),
        /// <paramref name="wrinkle"/> adds soft creases (metres of displacement); both need <paramref name="inner"/>
        /// subdivisions across the flat part of each face.
        /// </summary>
        public static void RoundBox(this MeshBuilder mb, Vector3 min, Vector3 max, float r, Material m, int seg = 3,
                                    int inner = 0, float puff = 0f, float wrinkle = 0f, int seed = 0)
        {
            Vector3 size = max - min;
            r = Mathf.Min(r, size.x * 0.5f, Mathf.Min(size.y * 0.5f, size.z * 0.5f));
            if (r < 1e-4f) { mb.Box(min, max, m); return; }
            Vector3 imin = min + Vector3.one * r, imax = max - Vector3.one * r, center = (min + max) * 0.5f, half = size * 0.5f;
            float[] ax = Axis(min.x, max.x, r, seg, inner), ay = Axis(min.y, max.y, r, seg, inner), az = Axis(min.z, max.z, r, seg, inner);
            bool soft = puff != 0f || wrinkle != 0f;

            Vector3 Project(Vector3 p, Vector3 faceN, out Vector3 n)
            {
                var c = new Vector3(Mathf.Clamp(p.x, imin.x, imax.x), Mathf.Clamp(p.y, imin.y, imax.y), Mathf.Clamp(p.z, imin.z, imax.z));
                Vector3 d = p - c;
                n = d.sqrMagnitude > 1e-10f ? d.normalized : faceN;
                Vector3 q = c + n * r;
                if (!soft) return q;
                // face-local coordinates in [-1, 1] on the two in-plane axes
                Vector3 t = new Vector3((p.x - center.x) / half.x, (p.y - center.y) / half.y, (p.z - center.z) / half.z);
                float bump = 1f;
                if (Mathf.Abs(faceN.x) < 0.5f) bump *= Mathf.Max(0f, 1f - t.x * t.x);
                if (Mathf.Abs(faceN.y) < 0.5f) bump *= Mathf.Max(0f, 1f - t.y * t.y);
                if (Mathf.Abs(faceN.z) < 0.5f) bump *= Mathf.Max(0f, 1f - t.z * t.z);
                float crease = 0f;
                if (wrinkle > 0f)
                {
                    Vector3 w = q * 9f;
                    float nz = Noise.Perlin(w.x + w.y * 0.7f + seed * 3.1f, w.z + w.y * 0.4f, 0, 0, seed + 7);
                    crease = (1f - Mathf.Abs(nz)); crease = crease * crease * crease - 0.35f;
                }
                return q + n * (puff * bump + wrinkle * crease * (0.4f + 0.6f * Mathf.Sqrt(bump)));
            }

            void Face(Vector3 n, float[] ru, float[] rv, Func<float, float, Vector3> pos)
            {
                int nu = ru.Length, nv = rv.Length;
                var P = new Vector3[nu, nv]; var N = new Vector3[nu, nv];
                for (int i = 0; i < nu; i++)
                for (int j = 0; j < nv; j++)
                    P[i, j] = Project(pos(ru[i], rv[j]), n, out N[i, j]);
                if (soft)
                    for (int i = 0; i < nu; i++)
                    for (int j = 0; j < nv; j++)
                    {
                        Vector3 du = P[Mathf.Min(nu - 1, i + 1), j] - P[Mathf.Max(0, i - 1), j];
                        Vector3 dv = P[i, Mathf.Min(nv - 1, j + 1)] - P[i, Mathf.Max(0, j - 1)];
                        Vector3 fn = Vector3.Cross(dv, du);
                        if (fn.sqrMagnitude > 1e-12f && Vector3.Dot(fn, N[i, j]) > 0f) N[i, j] = fn.normalized;
                    }
                for (int i = 0; i + 1 < nu; i++)
                for (int j = 0; j + 1 < nv; j++)
                {
                    Vector3 a = P[i, j], b = P[i + 1, j], c = P[i + 1, j + 1], d = P[i, j + 1];
                    Vector2 ua = MeshBuilder.PlanarUV(a, n), ub = MeshBuilder.PlanarUV(b, n), uc = MeshBuilder.PlanarUV(c, n), ud = MeshBuilder.PlanarUV(d, n);
                    mb.Triangle(a, d, c, N[i, j], N[i, j + 1], N[i + 1, j + 1], ua, ud, uc, m);
                    mb.Triangle(a, c, b, N[i, j], N[i + 1, j + 1], N[i + 1, j], ua, uc, ub, m);
                }
            }

            float[] rx = ax, rxr = Reverse(ax), rz = az, rzr = Reverse(az);
            // right = Cross(n, up) must increase along the first list
            Face(Vector3.back, rx, ay, (s, t) => new Vector3(s, t, min.z));
            Face(Vector3.forward, rxr, ay, (s, t) => new Vector3(s, t, max.z));
            Face(Vector3.left, rzr, ay, (s, t) => new Vector3(min.x, t, s));
            Face(Vector3.right, rz, ay, (s, t) => new Vector3(max.x, t, s));
            Face(Vector3.up, rx, az, (s, t) => new Vector3(s, max.y, t));
            Face(Vector3.down, rx, rzr, (s, t) => new Vector3(s, min.y, t));
        }

        /// <summary>Box with a small 45° chamfer on every edge: catches a highlight like real machined or veneered edges.</summary>
        public static void Bevel(this MeshBuilder mb, Vector3 min, Vector3 max, Material m, float r = 0.003f) =>
            mb.RoundBox(min, max, r, m, 1);

        static float[] Axis(float lo, float hi, float r, int seg, int inner)
        {
            var a = new float[seg * 2 + 2 + inner];
            for (int i = 0; i <= seg; i++)
            {
                // samples across the rounded band; the spherical projection bends them onto the arc
                a[i] = lo + r * (i / (float)seg);
                a[seg * 2 + 1 + inner - i] = hi - r * (i / (float)seg);
            }
            for (int k = 1; k <= inner; k++) a[seg + k] = Mathf.Lerp(lo + r, hi - r, k / (float)(inner + 1));
            return a;
        }

        static float[] Reverse(float[] a)
        {
            var b = (float[])a.Clone();
            Array.Reverse(b);
            return b;
        }

        // ------------------------------------------------------------------ lathe (surface of revolution about local Y)
        /// <summary>Profile points are (radius, height) from bottom to top; normals come from the profile slope.</summary>
        public static void Lathe(this MeshBuilder mb, Vector3 baseCenter, Vector2[] profile, int sides, Material m, bool capTop = false, bool capBottom = false)
        {
            int n = profile.Length;
            var pn = new Vector2[n];
            for (int k = 0; k < n; k++)
            {
                Vector2 a = profile[Mathf.Max(0, k - 1)], b = profile[Mathf.Min(n - 1, k + 1)];
                Vector2 t = (b - a).normalized;
                pn[k] = new Vector2(t.y, -t.x); // outward for a profile running upward
            }
            float vAcc = 0;
            var vs = new float[n];
            for (int k = 1; k < n; k++) { vAcc += (profile[k] - profile[k - 1]).magnitude; vs[k] = vAcc; }
            for (int i = 0; i < sides; i++)
            {
                float a0 = i * Mathf.PI * 2 / sides, a1 = (i + 1) * Mathf.PI * 2 / sides;
                Vector3 d0 = new Vector3(Mathf.Cos(a0), 0, Mathf.Sin(a0)), d1 = new Vector3(Mathf.Cos(a1), 0, Mathf.Sin(a1));
                for (int k = 0; k + 1 < n; k++)
                {
                    Vector2 p = profile[k], q = profile[k + 1];
                    Vector3 p0 = baseCenter + d0 * p.x + Vector3.up * p.y, p1 = baseCenter + d1 * p.x + Vector3.up * p.y;
                    Vector3 q0 = baseCenter + d0 * q.x + Vector3.up * q.y, q1 = baseCenter + d1 * q.x + Vector3.up * q.y;
                    Vector3 np0 = d0 * pn[k].x + Vector3.up * pn[k].y, np1 = d1 * pn[k].x + Vector3.up * pn[k].y;
                    Vector3 nq0 = d0 * pn[k + 1].x + Vector3.up * pn[k + 1].y, nq1 = d1 * pn[k + 1].x + Vector3.up * pn[k + 1].y;
                    float u0 = a0 * 0.3f, u1 = a1 * 0.3f;
                    // seen from outside p0 is on the left and p1 on the right: clockwise = p0, q0, q1
                    mb.Triangle(p0, q0, q1, np0, nq0, nq1, new Vector2(u0, vs[k]), new Vector2(u0, vs[k + 1]), new Vector2(u1, vs[k + 1]), m);
                    mb.Triangle(p0, q1, p1, np0, nq1, np1, new Vector2(u0, vs[k]), new Vector2(u1, vs[k + 1]), new Vector2(u1, vs[k]), m);
                }
                if (capTop && profile[n - 1].x > 1e-4f)
                {
                    Vector3 c = baseCenter + Vector3.up * profile[n - 1].y;
                    float r = profile[n - 1].x;
                    mb.Triangle(c, c + d1 * r, c + d0 * r, Vector3.up, Vector3.up, Vector3.up,
                        Vector2.zero, new Vector2(d1.x, d1.z) * r, new Vector2(d0.x, d0.z) * r, m);
                }
                if (capBottom && profile[0].x > 1e-4f)
                {
                    Vector3 c = baseCenter + Vector3.up * profile[0].y;
                    float r = profile[0].x;
                    mb.Triangle(c, c + d0 * r, c + d1 * r, Vector3.down, Vector3.down, Vector3.down,
                        Vector2.zero, new Vector2(d0.x, d0.z) * r, new Vector2(d1.x, d1.z) * r, m);
                }
            }
        }

        public static void Cylinder(this MeshBuilder mb, Vector3 baseCenter, float r, float h, Material m, int sides = 24, bool caps = true) =>
            mb.Lathe(baseCenter, new[] { new Vector2(r, 0), new Vector2(r, h) }, sides, m, caps, caps);

        /// <summary>Cylinder between two arbitrary points (rods, cables, frames).</summary>
        public static void Rod(this MeshBuilder mb, Vector3 a, Vector3 b, float r, Material m, int sides = 8)
        {
            Vector3 d = b - a;
            float len = d.magnitude;
            if (len < 1e-5f) return;
            using (mb.Place(a, Quaternion.FromToRotation(Vector3.up, d / len)))
                mb.Lathe(Vector3.zero, new[] { new Vector2(r, 0), new Vector2(r, len) }, sides, m, true, true);
        }

        /// <summary>Flat disk facing +Y (or -Y when <paramref name="down"/>).</summary>
        public static void Disk(this MeshBuilder mb, Vector3 c, float r, Material m, bool down = false, int sides = 24)
        {
            for (int i = 0; i < sides; i++)
            {
                float a0 = i * Mathf.PI * 2 / sides, a1 = (i + 1) * Mathf.PI * 2 / sides;
                Vector3 d0 = new Vector3(Mathf.Cos(a0), 0, Mathf.Sin(a0)) * r, d1 = new Vector3(Mathf.Cos(a1), 0, Mathf.Sin(a1)) * r;
                Vector3 n = down ? Vector3.down : Vector3.up;
                if (down) mb.Triangle(c, c + d0, c + d1, n, n, n, new Vector2(0.5f, 0.5f), new Vector2(0.5f + d0.x, 0.5f + d0.z), new Vector2(0.5f + d1.x, 0.5f + d1.z), m);
                else mb.Triangle(c, c + d1, c + d0, n, n, n, new Vector2(0.5f, 0.5f), new Vector2(0.5f + d1.x, 0.5f + d1.z), new Vector2(0.5f + d0.x, 0.5f + d0.z), m);
            }
        }

        public static void Sphere(this MeshBuilder mb, Vector3 c, Vector3 radii, Material m, int sides = 20, int rings = 12)
        {
            var prof = new Vector2[rings + 1];
            for (int k = 0; k <= rings; k++)
            {
                float t = -Mathf.PI * 0.5f + Mathf.PI * k / rings;
                prof[k] = new Vector2(Mathf.Cos(t), Mathf.Sin(t));
            }
            using (new Scope(mb, Matrix4x4.TRS(c, Quaternion.identity, radii)))
                mb.Lathe(Vector3.zero, prof, sides, m);
        }

        public static void Sphere(this MeshBuilder mb, Vector3 c, float r, Material m, int sides = 20, int rings = 12) =>
            mb.Sphere(c, Vector3.one * r, m, sides, rings);

        /// <summary>Quad on the plane with normal <paramref name="n"/> and explicit UV rectangle (pictures, screens).</summary>
        public static void Picture(this MeshBuilder mb, Vector3 center, Vector3 n, float w, float h, Rect uv, Material m)
        {
            Vector3 up = Mathf.Abs(n.y) > 0.9f ? Vector3.forward : Vector3.up;
            Vector3 right = Vector3.Cross(n, up).normalized;
            Vector3 a = center - right * w * 0.5f - up * h * 0.5f, b = center + right * w * 0.5f - up * h * 0.5f;
            Vector3 c = center + right * w * 0.5f + up * h * 0.5f, d = center - right * w * 0.5f + up * h * 0.5f;
            mb.Quad(a, b, c, d, n, new Vector2(uv.xMin, uv.yMin), new Vector2(uv.xMax, uv.yMin), new Vector2(uv.xMax, uv.yMax), new Vector2(uv.xMin, uv.yMax), m);
        }
    }
}
