using System.Collections.Generic;
using House4696.Core;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>Plan-polygon helpers (points are (x, z)): orientation, containment, ear-clipping triangulation, prisms.</summary>
    public static class Polygon
    {
        /// <summary>Signed area; positive when the points run counter-clockwise seen from above (X right, Z up).</summary>
        public static float SignedArea(IList<Vector2> p)
        {
            float a = 0f;
            for (int i = 0; i < p.Count; i++)
            {
                Vector2 u = p[i], v = p[(i + 1) % p.Count];
                a += u.x * v.y - v.x * u.y;
            }
            return a * 0.5f;
        }

        public static List<Vector2> CounterClockwise(IList<Vector2> p)
        {
            var list = new List<Vector2>(p);
            if (SignedArea(list) < 0) list.Reverse();
            return list;
        }

        public static bool Contains(IList<Vector2> poly, Vector2 pt)
        {
            bool inside = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                Vector2 a = poly[i], b = poly[j];
                if ((a.y > pt.y) != (b.y > pt.y) && pt.x < (b.x - a.x) * (pt.y - a.y) / (b.y - a.y) + a.x) inside = !inside;
            }
            return inside;
        }

        public static Rect Bounds(IList<Vector2> p)
        {
            Vector2 mn = p[0], mx = p[0];
            foreach (var v in p) { mn = Vector2.Min(mn, v); mx = Vector2.Max(mx, v); }
            return Rect.MinMaxRect(mn.x, mn.y, mx.x, mx.y);
        }

        public static Vector2 Centroid(IList<Vector2> p)
        {
            float a = SignedArea(p);
            if (Mathf.Abs(a) < 1e-6f) return Bounds(p).center;
            float cx = 0, cz = 0;
            for (int i = 0; i < p.Count; i++)
            {
                Vector2 u = p[i], v = p[(i + 1) % p.Count];
                float c = u.x * v.y - v.x * u.y;
                cx += (u.x + v.x) * c; cz += (u.y + v.y) * c;
            }
            return new Vector2(cx, cz) / (6f * a);
        }

        /// <summary>Ear clipping of a simple polygon; returns index triples into the counter-clockwise point list.</summary>
        public static List<int> Triangulate(IList<Vector2> ccw)
        {
            var tris = new List<int>();
            var idx = new List<int>();
            for (int i = 0; i < ccw.Count; i++) idx.Add(i);
            int guard = 0;
            while (idx.Count > 3 && guard++ < 10000)
            {
                bool clipped = false;
                for (int k = 0; k < idx.Count; k++)
                {
                    int ip = idx[(k + idx.Count - 1) % idx.Count], ic = idx[k], inx = idx[(k + 1) % idx.Count];
                    Vector2 a = ccw[ip], b = ccw[ic], c = ccw[inx];
                    if (Cross(b - a, c - b) <= 1e-7f) continue; // reflex or collinear
                    bool empty = true;
                    foreach (int j in idx)
                    {
                        if (j == ip || j == ic || j == inx) continue;
                        if (InTriangle(ccw[j], a, b, c)) { empty = false; break; }
                    }
                    if (!empty) continue;
                    tris.Add(ip); tris.Add(ic); tris.Add(inx);
                    idx.RemoveAt(k);
                    clipped = true;
                    break;
                }
                if (!clipped) idx.RemoveAt(0); // degenerate input: drop a vertex rather than loop forever
            }
            if (idx.Count == 3) { tris.Add(idx[0]); tris.Add(idx[1]); tris.Add(idx[2]); }
            return tris;
        }

        static float Cross(Vector2 u, Vector2 v) => u.x * v.y - u.y * v.x;

        static bool InTriangle(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
        {
            float d1 = Cross(b - a, p - a), d2 = Cross(c - b, p - b), d3 = Cross(a - c, p - c);
            return d1 >= 0 && d2 >= 0 && d3 >= 0;
        }

        /// <summary>
        /// Vertical prism over a plan polygon between y0 and y1 with planar metric UVs. Null materials skip that part.
        /// </summary>
        public static void Prism(MeshBuilder mb, IList<Vector2> outline, float y0, float y1, Material top, Material bottom, Material sides)
        {
            var p = CounterClockwise(outline);
            var tris = Triangulate(p);
            Vector3 P(int i, float y) => new Vector3(p[i].x, y, p[i].y);
            for (int t = 0; t < tris.Count; t += 3)
            {
                int a = tris[t], b = tris[t + 1], c = tris[t + 2];
                if (top != null)
                {
                    // CCW seen from above = counter-clockwise; Unity front faces are clockwise → a, c, b
                    Vector3 pa = P(a, y1), pb = P(b, y1), pc = P(c, y1);
                    mb.Triangle(pa, pc, pb, Vector3.up, Vector3.up, Vector3.up, UV(pa), UV(pc), UV(pb), top);
                }
                if (bottom != null)
                {
                    Vector3 pa = P(a, y0), pb = P(b, y0), pc = P(c, y0);
                    mb.Triangle(pa, pb, pc, Vector3.down, Vector3.down, Vector3.down, UVd(pa), UVd(pb), UVd(pc), bottom);
                }
            }
            if (sides == null) return;
            float along = 0f;
            for (int i = 0; i < p.Count; i++)
            {
                Vector2 u = p[i], v = p[(i + 1) % p.Count];
                Vector2 d = v - u;
                float len = d.magnitude;
                if (len < 1e-5f) continue;
                Vector3 n = new Vector3(d.y, 0, -d.x) / len; // outward for a CCW outline
                Vector3 a = new Vector3(u.x, y0, u.y), b = new Vector3(v.x, y0, v.y);
                mb.Quad(a, b, b + Vector3.up * (y1 - y0), a + Vector3.up * (y1 - y0), n,
                    new Vector2(along, y0), new Vector2(along + len, y0), new Vector2(along + len, y1), new Vector2(along, y1), sides);
                along += len;
            }
        }

        // ------------------------------------------------------------------ openings in slabs
        /// <summary>Part of a convex polygon on the left of the directed line a→b (Sutherland–Hodgman against one half-plane).</summary>
        public static List<Vector2> ClipLeft(IList<Vector2> poly, Vector2 a, Vector2 b)
        {
            var res = new List<Vector2>();
            Vector2 d = b - a;
            float Side(Vector2 p) => Cross(d, p - a);
            for (int i = 0; i < poly.Count; i++)
            {
                Vector2 p = poly[i], q = poly[(i + 1) % poly.Count];
                float sp = Side(p), sq = Side(q);
                if (sp >= 0) res.Add(p);
                if ((sp >= 0) != (sq >= 0)) res.Add(p + (q - p) * (sp / (sp - sq)));
            }
            return res;
        }

        /// <summary>
        /// Convex polygon minus a convex counter-clockwise hole, as convex pieces: the part outside hole edge i and inside
        /// edges 0..i-1, for every i (the pieces do not overlap).
        /// </summary>
        public static List<List<Vector2>> SubtractConvex(List<Vector2> piece, IList<Vector2> hole)
        {
            var res = new List<List<Vector2>>();
            var rest = piece;
            for (int i = 0; i < hole.Count && rest.Count >= 3; i++)
            {
                Vector2 a = hole[i], b = hole[(i + 1) % hole.Count];
                var outside = ClipLeft(rest, b, a);      // right of a→b = outside a CCW hole
                if (outside.Count >= 3 && Mathf.Abs(SignedArea(outside)) > 1e-5f) res.Add(outside);
                rest = ClipLeft(rest, a, b);
            }
            return res;
        }

        /// <summary>Do two polygons' bounding boxes overlap?</summary>
        public static bool BoundsOverlap(IList<Vector2> a, IList<Vector2> b)
        {
            var ra = Bounds(a); var rb = Bounds(b);
            return ra.xMin < rb.xMax && rb.xMin < ra.xMax && ra.yMin < rb.yMax && rb.yMin < ra.yMax;
        }

        /// <summary>
        /// Parameter intervals [t0, t1] of segment a→b where <paramref name="keep"/> holds, split exactly at the crossings
        /// with the edges of <paramref name="polys"/> (the predicate is tested at each interval's midpoint).
        /// </summary>
        public static List<Vector2> Intervals(Vector2 a, Vector2 b, IEnumerable<IList<Vector2>> polys, System.Func<Vector2, bool> keep)
        {
            var ts = new List<float> { 0f, 1f };
            Vector2 d = b - a;
            foreach (var poly in polys)
                for (int i = 0; i < poly.Count; i++)
                {
                    Vector2 c = poly[i], e = poly[(i + 1) % poly.Count], f = e - c;
                    float den = Cross(d, f);
                    if (Mathf.Abs(den) < 1e-9f) continue;
                    float t = Cross(c - a, f) / den, u = Cross(c - a, d) / den;
                    if (t > 1e-4f && t < 1 - 1e-4f && u >= -1e-4f && u <= 1 + 1e-4f) ts.Add(t);
                }
            ts.Sort();
            var res = new List<Vector2>();
            for (int i = 0; i + 1 < ts.Count; i++)
            {
                float t0 = ts[i], t1 = ts[i + 1];
                if (t1 - t0 < 1e-4f || !keep(a + d * ((t0 + t1) * 0.5f))) continue;
                if (res.Count > 0 && Mathf.Abs(res[res.Count - 1].y - t0) < 1e-4f) res[res.Count - 1] = new Vector2(res[res.Count - 1].x, t1);
                else res.Add(new Vector2(t0, t1));
            }
            return res;
        }

        static bool InAny(IList<Vector2[]> holes, Vector2 p, Vector2[] except = null)
        {
            foreach (var h in holes) if (h != except && Contains(h, p)) return true;
            return false;
        }

        /// <summary>
        /// <see cref="Prism"/> with convex holes (stairwells): the outline is triangulated and every triangle loses the
        /// holes as convex pieces; side faces run along the outline outside the holes and around the holes inside the
        /// outline (facing into the opening).
        /// </summary>
        public static void Prism(MeshBuilder mb, IList<Vector2> outline, IList<Vector2[]> holes, float y0, float y1, Material top, Material bottom, Material sides)
        {
            var p = CounterClockwise(outline);
            var cut = new List<Vector2[]>();
            if (holes != null)
                foreach (var h in holes) if (h != null && h.Length >= 3 && BoundsOverlap(p, h)) cut.Add(CounterClockwise(h).ToArray());
            if (cut.Count == 0) { Prism(mb, outline, y0, y1, top, bottom, sides); return; }

            var tris = Triangulate(p);
            for (int t = 0; t < tris.Count; t += 3)
            {
                var pieces = new List<List<Vector2>> { new List<Vector2> { p[tris[t]], p[tris[t + 1]], p[tris[t + 2]] } };
                foreach (var h in cut)
                {
                    var next = new List<List<Vector2>>();
                    foreach (var piece in pieces) next.AddRange(SubtractConvex(piece, h));
                    pieces = next;
                }
                foreach (var piece in pieces)
                    for (int i = 1; i + 1 < piece.Count; i++)
                    {
                        Vector3 a = new Vector3(piece[0].x, 0, piece[0].y), b = new Vector3(piece[i].x, 0, piece[i].y), c = new Vector3(piece[i + 1].x, 0, piece[i + 1].y);
                        if (top != null)
                        {
                            Vector3 pa = a + Vector3.up * y1, pb = b + Vector3.up * y1, pc = c + Vector3.up * y1;
                            mb.Triangle(pa, pc, pb, Vector3.up, Vector3.up, Vector3.up, UV(pa), UV(pc), UV(pb), top);
                        }
                        if (bottom != null)
                        {
                            Vector3 pa = a + Vector3.up * y0, pb = b + Vector3.up * y0, pc = c + Vector3.up * y0;
                            mb.Triangle(pa, pb, pc, Vector3.down, Vector3.down, Vector3.down, UVd(pa), UVd(pb), UVd(pc), bottom);
                        }
                    }
            }
            if (sides == null) return;
            var all = new List<IList<Vector2>> { p };
            foreach (var h in cut) all.Add(h);
            void Side(Vector2 u, Vector2 v, Vector3 n)
            {
                Vector3 a = new Vector3(u.x, y0, u.y), b = new Vector3(v.x, y0, v.y);
                float len = (v - u).magnitude, s0 = u.x + u.y;
                mb.Quad(a, b, b + Vector3.up * (y1 - y0), a + Vector3.up * (y1 - y0), n,
                    new Vector2(s0, y0), new Vector2(s0 + len, y0), new Vector2(s0 + len, y1), new Vector2(s0, y1), sides);
            }
            for (int i = 0; i < p.Count; i++)
            {
                Vector2 u = p[i], v = p[(i + 1) % p.Count], d = v - u;
                if (d.sqrMagnitude < 1e-10f) continue;
                var n = new Vector3(d.y, 0, -d.x).normalized;
                foreach (var iv in Intervals(u, v, all, q => !InAny(cut, q))) Side(u + d * iv.x, u + d * iv.y, n);
            }
            foreach (var h in cut)
                for (int i = 0; i < h.Length; i++)
                {
                    // walk the hole edge backwards: the face looks into the opening
                    Vector2 u = h[(i + 1) % h.Length], v = h[i], d = v - u;
                    if (d.sqrMagnitude < 1e-10f) continue;
                    var n = new Vector3(d.y, 0, -d.x).normalized;
                    foreach (var iv in Intervals(u, v, all, q => Contains(p, q) && !InAny(cut, q, h))) Side(u + d * iv.x, u + d * iv.y, n);
                }
        }

        static Vector2 UV(Vector3 p) => new Vector2(p.x, p.z);
        static Vector2 UVd(Vector3 p) => new Vector2(p.x, -p.z);
    }
}
