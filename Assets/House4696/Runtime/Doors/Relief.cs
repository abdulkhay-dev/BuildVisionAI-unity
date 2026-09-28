using System;
using System.Collections.Generic;
using Clipper2Lib;
using House4696.Core;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>
    /// Relief of leaf faces: regions with holes (Clipper2 booleans and triangulation) and profiles swept along polylines —
    /// grooves, glass beads, raised panels, applied mouldings. Input in millimetres (leaf space), output in metres.
    /// A face is +1 (front, z up) or -1 (back, mirrored in z).
    /// </summary>
    public static class Relief
    {
        const int Dec = 3;   // Clipper precision: micrometres

        public static PathD Path(IList<Vector2> pts)
        {
            var p = new PathD(pts.Count);
            foreach (var v in pts) p.Add(new PointD(v.x, v.y));
            return p;
        }

        public static List<Vector2> Points(PathD p)
        {
            var l = new List<Vector2>(p.Count);
            foreach (var q in p) l.Add(new Vector2((float)q.x, (float)q.y));
            return l;
        }

        public static PathsD Rect(Rect r) => new PathsD { Clipper.MakePath(new double[] { r.xMin, r.yMin, r.xMax, r.yMin, r.xMax, r.yMax, r.xMin, r.yMax }) };

        public static PathsD Union(PathsD a) => a.Count == 0 ? a : Clipper.Union(a, new PathsD(), FillRule.NonZero, Dec);
        public static PathsD Difference(PathsD a, PathsD b) => b.Count == 0 ? a : Clipper.Difference(a, b, FillRule.NonZero, Dec);
        public static PathsD Intersect(PathsD a, PathsD b) => Clipper.Intersect(a, b, FillRule.NonZero, Dec);

        /// <summary>Grows (d > 0) or shrinks a region, mitred corners.</summary>
        public static PathsD Inflate(PathsD a, float d) => Clipper.InflatePaths(a, d, JoinType.Miter, EndType.Polygon, 4.0, Dec);

        public static double Area(PathsD a)
        {
            double s = 0;
            foreach (var p in a) s += Clipper.Area(p);
            return s;
        }

        /// <summary>Flat region at height z (mm) of one face, triangulated; UVs from <paramref name="uv"/> (mm in, metres out).</summary>
        public static void Fill(MeshBuilder mb, PathsD region, float zMm, float face, Material m, Func<Vector2, Vector2> uv)
        {
            if (m == null || region == null || region.Count == 0) return;
            if (Clipper.Triangulate(region, Dec, out PathsD tris) != TriangulateResult.success || tris == null) return;
            var n = new Vector3(0f, 0f, face);
            float z = face * zMm / 1000f;
            foreach (var t in tris)
            {
                if (t.Count < 3) continue;
                Vector2 a = new Vector2((float)t[0].x, (float)t[0].y), b = new Vector2((float)t[1].x, (float)t[1].y), c = new Vector2((float)t[2].x, (float)t[2].y);
                DoorGeo.Tri(mb, new Vector3(a.x / 1000f, a.y / 1000f, z), new Vector3(b.x / 1000f, b.y / 1000f, z), new Vector3(c.x / 1000f, c.y / 1000f, z),
                    n, n, n, uv(a), uv(b), uv(c), m);
            }
        }

        /// <summary>
        /// Polyline moved by <paramref name="d"/> mm along its left normal (d > 0 = into a counter-clockwise ring), mitred at
        /// the corners; point i stays point i, so swept strips close watertight with the rings they start from.
        /// </summary>
        public static List<Vector2> Offset(IList<Vector2> p, float d, bool closed, float miterLimit = 4f)
        {
            int n = p.Count;
            var r = new List<Vector2>(n);
            for (int i = 0; i < n; i++) r.Add(p[i] + Miter(p, i, closed, miterLimit) * d);
            return r;
        }

        /// <summary>Unit left normals of the segments meeting at point i, and the mitre vector (length 1/cos of the half turn).</summary>
        static Vector2 Miter(IList<Vector2> p, int i, bool closed, float miterLimit)
        {
            Normals(p, i, closed, out var n0, out var n1);
            Vector2 m = n0 + n1;
            float len = m.magnitude;
            if (len < 1e-4f) return n1;
            m /= len;
            float c = Vector2.Dot(m, n1);
            return m / Mathf.Max(c, 1f / miterLimit);
        }

        static void Normals(IList<Vector2> p, int i, bool closed, out Vector2 n0, out Vector2 n1)
        {
            int n = p.Count;
            Vector2 cur = p[i];
            Vector2 prev = closed ? p[(i - 1 + n) % n] : p[Mathf.Max(0, i - 1)];
            Vector2 next = closed ? p[(i + 1) % n] : p[Mathf.Min(n - 1, i + 1)];
            Vector2 t0 = cur - prev, t1 = next - cur;
            if (t0.sqrMagnitude < 1e-10f) t0 = t1;
            if (t1.sqrMagnitude < 1e-10f) t1 = t0;
            t0.Normalize(); t1.Normalize();
            n0 = new Vector2(-t0.y, t0.x);
            n1 = new Vector2(-t1.y, t1.x);
        }

        /// <summary>
        /// Sweeps a profile along a polyline of the face plane. Profile points (u, v) in mm: u across the path (positive to the
        /// left of travel), v above <paramref name="zBase"/>; they run along the visible surface so that turning the tangent
        /// by +90° points out of the material. Sharp corners of the path split the normals, gentle ones stay smooth.
        /// UVs: along the path (the grain follows it) and along the profile, metres. <paramref name="capSign"/>: end caps of an
        /// open path (+1 facing out along the path — a moulding's end; -1 facing back into it — the end wall of a groove; 0 none).
        /// </summary>
        public static void Sweep(MeshBuilder mb, IList<Vector2> path, bool closed, IList<Vector2> profile, float zBase, float face,
                                 Material m, float uOffset = 0f, int capSign = 0, float sharpDeg = 40f, Func<int, Material> segment = null)
        {
            int n = path.Count, k = profile.Count;
            if (m == null || n < 2 || k < 2) return;
            var miter = new Vector2[n];
            var nIn = new Vector2[n];   // in-plane normal used for shading at a vertex (per side of a sharp corner below)
            var n0s = new Vector2[n];
            var n1s = new Vector2[n];
            var sharp = new bool[n];
            float cosSharp = Mathf.Cos(sharpDeg * Mathf.Deg2Rad);
            for (int i = 0; i < n; i++)
            {
                miter[i] = Miter(path, i, closed, 4f);
                Normals(path, i, closed, out n0s[i], out n1s[i]);
                sharp[i] = Vector2.Dot(n0s[i], n1s[i]) < cosSharp;
                nIn[i] = (n0s[i] + n1s[i]).normalized;
                if (nIn[i].sqrMagnitude < 0.5f) nIn[i] = n1s[i];
            }
            // profile normals (u, v) and lengths: smooth at gentle bends, per segment where the profile turns sharply
            // (a milled edge stays crisp without doubling its point)
            var pn = new Vector2[k];
            var pv = new float[k];
            for (int j = 0; j < k; j++)
            {
                Vector2 a = profile[Mathf.Max(0, j - 1)], b = profile[Mathf.Min(k - 1, j + 1)];
                Vector2 t = (b - a).normalized;
                pn[j] = new Vector2(-t.y, t.x);
                if (j > 0) pv[j] = pv[j - 1] + (profile[j] - profile[j - 1]).magnitude / 1000f;
            }
            var sn = new Vector2[Mathf.Max(1, k - 1)];
            for (int j = 0; j + 1 < k; j++)
            {
                Vector2 t = (profile[j + 1] - profile[j]).normalized;
                sn[j] = new Vector2(-t.y, t.x);
            }
            const float cosProfileSharp = 0.8f;   // 37°
            // normal of segment j at its start (end = false) or end (end = true)
            Vector2 SegN(int j, bool end)
            {
                int v = end ? j + 1 : j;
                if (v <= 0 || v >= k - 1) return pn[v];
                return Vector2.Dot(sn[v - 1], sn[v]) < cosProfileSharp ? sn[j] : pn[v];
            }
            var along = new float[n + 1];
            for (int i = 1; i <= n; i++) along[i] = along[i - 1] + (path[i % n] - path[i - 1]).magnitude / 1000f;

            Vector3 Pos(int i, int j) => new Vector3((path[i].x + miter[i].x * profile[j].x) / 1000f, (path[i].y + miter[i].y * profile[j].x) / 1000f,
                                                     face * (zBase + profile[j].y) / 1000f);
            Vector3 Nrm(Vector2 inPlane, Vector2 p2) => new Vector3(inPlane.x * p2.x, inPlane.y * p2.x, face * p2.y).normalized;
            int segs = closed ? n : n - 1;
            for (int s = 0; s < segs; s++)
            {
                int i0 = s, i1 = (s + 1) % n;
                // the segment's own normal where a corner is sharp, the averaged one where it is smooth
                Vector2 seg = n1s[i0];
                Vector2 a0 = sharp[i0] ? seg : nIn[i0], a1 = sharp[i1] ? seg : nIn[i1];
                if (!closed && i0 == 0) a0 = seg;
                if (!closed && i1 == n - 1) a1 = seg;
                float u0 = along[s] + uOffset, u1 = along[s + 1] + uOffset;
                for (int j = 0; j + 1 < k; j++)
                    DoorGeo.Quad(mb, Pos(i0, j), Pos(i1, j), Pos(i1, j + 1), Pos(i0, j + 1),
                        Nrm(a0, SegN(j, false)), Nrm(a1, SegN(j, false)), Nrm(a1, SegN(j, true)), Nrm(a0, SegN(j, true)),
                        new Vector2(u0, pv[j]), new Vector2(u1, pv[j]), new Vector2(u1, pv[j + 1]), new Vector2(u0, pv[j + 1]),
                        segment?.Invoke(j) ?? m);
            }
            if (!closed && capSign != 0)
            {
                Cap(mb, path, profile, 0, zBase, face, m, capSign, true, miter);
                Cap(mb, path, profile, n - 1, zBase, face, m, capSign, false, miter);
            }
        }

        static void Cap(MeshBuilder mb, IList<Vector2> path, IList<Vector2> profile, int i, float zBase, float face, Material m, int sign, bool start,
                        Vector2[] miter)
        {
            int n = path.Count;
            Vector2 t = start ? path[1] - path[0] : path[n - 1] - path[n - 2];
            t.Normalize();
            // out along the path at the end, back along it at the start; a groove's end wall faces the other way
            Vector2 dir = (start ? -t : t) * sign;
            var nrm = new Vector3(dir.x, dir.y, 0f);
            var pts = new List<Vector3>();
            foreach (var q in profile)
                pts.Add(new Vector3((path[i].x + miter[i].x * q.x) / 1000f, (path[i].y + miter[i].y * q.x) / 1000f, face * (zBase + q.y) / 1000f));
            var c = Vector3.zero;
            foreach (var p in pts) c += p;
            c /= pts.Count;
            // fan from the centre, closed by the base line between the first and last profile points
            for (int j = 0; j < pts.Count; j++)
            {
                var p = pts[j];
                var q = pts[(j + 1) % pts.Count];
                if ((p - q).sqrMagnitude < 1e-12f) continue;
                DoorGeo.Tri(mb, c, p, q, nrm, nrm, nrm, Vector2.zero, new Vector2(0.01f, 0f), new Vector2(0f, 0.01f), m);
            }
        }

        /// <summary>
        /// The band a path sweeps between offsets u0 and u1 (u0 &lt; u1): for a closed path the ring between the two offset
        /// rings, for an open one the strip joined at its ends. Built from the same mitred offsets as <see cref="Sweep"/>.
        /// </summary>
        public static PathsD Band(IList<Vector2> path, bool closed, float u0, float u1)
        {
            var a = Offset(path, u0, closed);
            var b = Offset(path, u1, closed);
            if (closed)
            {
                // two rings of opposite winding: NonZero fill leaves the band
                var outer = Path(a);
                var inner = Path(b);
                if (Clipper.Area(outer) < 0) outer.Reverse();
                if (Clipper.Area(inner) > 0) inner.Reverse();
                return Union(new PathsD { outer, inner });
            }
            var strip = new List<Vector2>(a);
            for (int i = b.Count - 1; i >= 0; i--) strip.Add(b[i]);
            var ps = Path(strip);
            if (Clipper.Area(ps) < 0) ps.Reverse();
            return Union(new PathsD { ps });
        }
    }
}
