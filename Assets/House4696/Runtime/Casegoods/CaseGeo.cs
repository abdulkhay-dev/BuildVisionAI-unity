using System;
using System.Collections.Generic;
using Clipper2Lib;
using House4696.Core;
using House4696.Doors;
using UnityEngine;

namespace House4696.Casegoods
{
    /// <summary>
    /// A plane of a module in design millimetres: 2D points (a, b) and a depth w along its normal map to
    /// Origin + a·U + b·V + w·W. Geometry is emitted into the item's local space (metres, x centred, front towards -Z).
    /// </summary>
    public readonly struct CasePlane
    {
        public readonly Vector3 Origin, U, V, W;
        public CasePlane(Vector3 origin, Vector3 u, Vector3 v, Vector3 w) { Origin = origin; U = u; V = v; W = w; }
        public Vector3 At(float a, float b, float w) => Origin + U * a + V * b + W * w;
        public Vector3 Dir(float a, float b, float w) => U * a + V * b + W * w;

        /// <summary>The front plane: a = x, b = y, w = z (out of the front at z = depth).</summary>
        public static CasePlane Front => new CasePlane(Vector3.zero, Vector3.right, Vector3.up, Vector3.forward);
        /// <summary>The top plane seen from above: a = x, b = z (back to front), w = y.</summary>
        public static CasePlane Top => new CasePlane(Vector3.zero, Vector3.right, Vector3.forward, Vector3.up);
        /// <summary>The left side seen from the left: a = z (back to front), b = y, w = -x (out of the left side at x = 0).</summary>
        public static CasePlane Left => new CasePlane(Vector3.zero, Vector3.forward, Vector3.up, Vector3.left);
        /// <summary>The right side seen from the right: a = depth - z, b = y, w = x.</summary>
        public static CasePlane Right(float depth) => new CasePlane(new Vector3(0, 0, depth), Vector3.back, Vector3.up, Vector3.right);
    }

    /// <summary>Geometry of case furniture: boards, shaped slabs with rounded edges, swept mouldings.</summary>
    public sealed class CaseGeo
    {
        const int Dec = 3;
        readonly float _halfL, _y0;

        /// <param name="lengthMm">The module's width: x is centred on the item's origin.</param>
        /// <param name="yOriginMm">Height of the item's origin in the design (wall pieces: their middle).</param>
        public CaseGeo(float lengthMm, float yOriginMm = 0f) { _halfL = lengthMm * 0.5f; _y0 = yOriginMm; }

        /// <summary>Design mm (x right, y up, z from the back) to local metres (x centred, front towards -Z).</summary>
        public Vector3 P(Vector3 mm) => new Vector3((mm.x - _halfL) / 1000f, (mm.y - _y0) / 1000f, -mm.z / 1000f);
        public static Vector3 N(Vector3 n) => new Vector3(n.x, n.y, -n.z).normalized;

        // ------------------------------------------------------------------ boards
        /// <summary>
        /// Texture direction of what is built next: the design axis (0 = x, 1 = y, 2 = z) the texture's U (a wood decor's
        /// grain) runs along on every face that contains it; -1 = the default planar mapping.
        /// </summary>
        public int Grain = -1;

        /// <summary>The longest side of a box: the grain of a board unless the design says otherwise.</summary>
        public static int LongestAxis(float[] box)
        {
            float dx = Mathf.Abs(box[3] - box[0]), dy = Mathf.Abs(box[4] - box[1]), dz = Mathf.Abs(box[5] - box[2]);
            return dy >= dx && dy >= dz ? 1 : dx >= dz ? 0 : 2;
        }

        /// <summary>
        /// An axis-aligned board [x0, y0, z0, x1, y1, z1] mm: its two big faces and their edges rounded by <paramref name="r"/>
        /// mm (the corners across the thickness stay square, like a cut and edge-banded panel).
        /// </summary>
        public void Board(MeshBuilder mb, float[] box, float r, Material m, Material edgeM = null)
        {
            if (m == null || box == null || box.Length < 6) return;
            var (pl, a0, b0, a1, b1, w0, w1) = Thin(box);
            if (a1 - a0 < 1e-3f || b1 - b0 < 1e-3f || w1 - w0 < 1e-3f) return;
            Slab(mb, pl, new PathsD { Rect(a0, b0, a1, b1) }, w0, w1, r, m, edgeM: edgeM);
        }

        /// <summary>The plane across a box's thinnest axis and the box's extent in it.</summary>
        public static (CasePlane pl, float a0, float b0, float a1, float b1, float w0, float w1) Thin(float[] box)
        {
            float x0 = Mathf.Min(box[0], box[3]), x1 = Mathf.Max(box[0], box[3]);
            float y0 = Mathf.Min(box[1], box[4]), y1 = Mathf.Max(box[1], box[4]);
            float z0 = Mathf.Min(box[2], box[5]), z1 = Mathf.Max(box[2], box[5]);
            float dx = x1 - x0, dy = y1 - y0, dz = z1 - z0;
            if (dz <= dx && dz <= dy) return (CasePlane.Front, x0, y0, x1, y1, z0, z1);
            if (dy <= dx) return (CasePlane.Top, x0, z0, x1, z1, y0, y1);
            return (new CasePlane(Vector3.zero, Vector3.forward, Vector3.up, Vector3.right), z0, y0, z1, y1, x0, x1);
        }

        // ------------------------------------------------------------------ shaped slabs
        /// <summary>
        /// A slab of <paramref name="region"/> (plane mm; outer rings counter-clockwise, holes clockwise) between depths
        /// <paramref name="w0"/> and <paramref name="w1"/>, its face edges rounded with <paramref name="r"/> mm; the back face
        /// only when <paramref name="back"/>.
        /// </summary>
        public void Slab(MeshBuilder mb, CasePlane pl, PathsD region, float w0, float w1, float r, Material m, bool back = true,
                         PathsD faceCut = null, Material edgeM = null)
        {
            if (m == null || region == null || region.Count == 0 || w1 - w0 < 1e-3f) return;
            // outer rings counter-clockwise, holes clockwise: the edge normals follow the rings' left side
            region = Clipper.Union(region, new PathsD(), FillRule.NonZero, Dec);
            r = Mathf.Clamp(r, 0f, (w1 - w0) * 0.49f);
            var face = r > 0.05f ? Clipper.InflatePaths(region, -r, JoinType.Round, EndType.Polygon, 2.0, Dec) : region;
            Fill(mb, pl, faceCut != null && faceCut.Count > 0 ? Clipper.Difference(face, faceCut, FillRule.NonZero, Dec) : face, w1, 1f, m);
            if (back) Fill(mb, pl, face, w0, -1f, m);
            // edge: from the front face over the rounding, down the side, round onto the back face
            var prof = new List<Vector2>();
            const int seg = 3;
            if (r > 0.05f)
                for (int i = 0; i <= seg; i++)
                {
                    float t = i / (float)seg * Mathf.PI * 0.5f;
                    prof.Add(new Vector2(r - r * Mathf.Sin(t), w1 - r + r * Mathf.Cos(t)));
                }
            else prof.Add(new Vector2(0f, w1));
            if (r > 0.05f)
                for (int i = 0; i <= seg; i++)
                {
                    float t = i / (float)seg * Mathf.PI * 0.5f;
                    prof.Add(new Vector2(r - r * Mathf.Cos(t), w0 + r - r * Mathf.Sin(t)));
                }
            else prof.Add(new Vector2(0f, w0));
            if (!back) prof[prof.Count - 1] = new Vector2(prof[prof.Count - 1].x, w0);
            foreach (var ring in region)
            {
                var path = new List<Vector2>(ring.Count);
                foreach (var p in ring) path.Add(new Vector2((float)p.x, (float)p.y));
                // walk the profile from the back face to the front one: (u, v) → (-v, u) then points out of the material
                var rev = new List<Vector2>(prof);
                rev.Reverse();
                Sweep(mb, pl, path, true, rev, 0f, edgeM ?? m, planarUv: true);
            }
        }

        /// <summary>Flat region at depth <paramref name="w"/>, facing +W (<paramref name="dir"/> = 1) or -W.</summary>
        public void Fill(MeshBuilder mb, CasePlane pl, PathsD region, float w, float dir, Material m, Func<float, float, Vector2> uvAB = null)
        {
            if (m == null || region == null || region.Count == 0) return;
            if (Clipper.Triangulate(region, Dec, out PathsD tris) != TriangulateResult.success || tris == null) return;
            var n = N(pl.W * dir);
            foreach (var t in tris)
            {
                if (t.Count < 3) continue;
                Vector3 da = pl.At((float)t[0].x, (float)t[0].y, w), db = pl.At((float)t[1].x, (float)t[1].y, w), dc = pl.At((float)t[2].x, (float)t[2].y, w);
                Vector3 a = P(da), b = P(db), c = P(dc);
                var dn = pl.W * dir;
                if (uvAB != null)
                    DoorGeo.Tri(mb, a, b, c, n, n, n, uvAB((float)t[0].x, (float)t[0].y), uvAB((float)t[1].x, (float)t[1].y), uvAB((float)t[2].x, (float)t[2].y), m);
                else
                    DoorGeo.Tri(mb, a, b, c, n, n, n, UV(da, dn, a, n), UV(db, dn, b, n), UV(dc, dn, c, n), m);
            }
        }

        /// <summary>UV of a point (design mm <paramref name="d"/>, normal <paramref name="dn"/>; local <paramref name="p"/>, <paramref name="n"/>): along <see cref="Grain"/> in metres, else planar.</summary>
        Vector2 UV(Vector3 d, Vector3 dn, Vector3 p, Vector3 n)
        {
            if (Grain < 0) return MeshBuilder.PlanarUV(p, n);
            float ax = Mathf.Abs(dn.x), ay = Mathf.Abs(dn.y), az = Mathf.Abs(dn.z);
            int k = ay >= ax && ay >= az ? 1 : ax >= az ? 0 : 2;       // the axis the face looks along
            int i = k == 0 ? 1 : 0, j = k == 2 ? 1 : 2;                // the two in the face
            if (Grain == k) return new Vector2(d[i], d[j]) / 1000f;    // end grain: anything
            int other = Grain == i ? j : i;
            return new Vector2(d[Grain], d[other]) / 1000f;
        }

        // ------------------------------------------------------------------ swept profiles
        /// <summary>
        /// Sweeps a profile along a path in the plane. Profile points (u, v) mm: u along the path's left normal (into a
        /// counter-clockwise ring), v = depth along W above <paramref name="wBase"/>. The visible surface's normal is the
        /// profile tangent turned by +90° (u, v) → (-v, u) when <paramref name="outward"/> is false (a moulding drawn from its
        /// outer edge inwards over its top), else the opposite. Sharp path corners are mitred with split normals.
        /// </summary>
        public void Sweep(MeshBuilder mb, CasePlane pl, IList<Vector2> path, bool closed, IList<Vector2> profile, float wBase, Material m,
                          bool outward = false, int caps = 0, bool planarUv = false)
        {
            int n = path.Count, k = profile.Count;
            if (m == null || n < 2 || k < 2) return;
            var miter = new Vector2[n];
            var segN = new Vector2[n];   // left normal of the segment starting at i
            for (int i = 0; i < n; i++)
            {
                Vector2 prev = closed ? path[(i - 1 + n) % n] : path[Mathf.Max(0, i - 1)];
                Vector2 next = closed ? path[(i + 1) % n] : path[Mathf.Min(n - 1, i + 1)];
                Vector2 t0 = path[i] - prev, t1 = next - path[i];
                if (t0.sqrMagnitude < 1e-10f) t0 = t1;
                if (t1.sqrMagnitude < 1e-10f) t1 = t0;
                t0.Normalize(); t1.Normalize();
                Vector2 n0 = new Vector2(-t0.y, t0.x), n1 = new Vector2(-t1.y, t1.x);
                segN[i] = n1;
                Vector2 mm = n0 + n1;
                float len = mm.magnitude;
                if (len < 1e-4f) { miter[i] = n1; continue; }
                mm /= len;
                miter[i] = mm / Mathf.Max(Vector2.Dot(mm, n1), 0.25f);
            }
            // per profile segment normals in (u, v)
            var pn = new Vector2[k - 1];
            for (int j = 0; j + 1 < k; j++)
            {
                Vector2 t = (profile[j + 1] - profile[j]).normalized;
                pn[j] = outward ? new Vector2(t.y, -t.x) : new Vector2(-t.y, t.x);
            }
            // smooth the profile normals across gentle bends (a rounded edge), keep sharp ones crisp
            Vector2 PN(int j, bool end)
            {
                int v = end ? j + 1 : j;
                if (v <= 0 || v >= k - 1) return pn[j];
                int other = end ? j + 1 : j - 1;
                return Vector2.Dot(pn[j], pn[other]) > 0.8f ? (pn[j] + pn[other]).normalized : pn[j];
            }
            // texture v runs along the profile's own length (a tall profile — a corner wardrobe's door drawn as a 16 × 1996
            // moulding — must not smear its face into streaks); the grain follows the longer of path and profile
            var arc = new float[k];
            for (int j = 1; j < k; j++) arc[j] = arc[j - 1] + (profile[j] - profile[j - 1]).magnitude;
            float pathLen = 0f;
            for (int s = 0; s < (closed ? n : n - 1); s++) pathLen += (path[(s + 1) % n] - path[s]).magnitude;
            bool swap = arc[k - 1] > pathLen;
            Vector2 Uv(float a, float b) => swap ? new Vector2(b / 1000f, a / 1000f) : new Vector2(a / 1000f, b / 1000f);
            float along = 0f;
            int segs = closed ? n : n - 1;
            for (int s = 0; s < segs; s++)
            {
                int i0 = s, i1 = (s + 1) % n;
                Vector2 sn = segN[i0];
                float seglen = (path[i1] - path[i0]).magnitude;
                for (int j = 0; j + 1 < k; j++)
                {
                    Vector3 D(int i, int jj) => pl.At(path[i].x + miter[i].x * profile[jj].x, path[i].y + miter[i].y * profile[jj].x, wBase + profile[jj].y);
                    Vector3 Dn(Vector2 q) => pl.Dir(sn.x * q.x, sn.y * q.x, q.y);
                    Vector2 qa = PN(j, false), qb = PN(j, true);
                    Vector3 na = N(Dn(qa)), nb = N(Dn(qb));
                    Vector3 d00 = D(i0, j), d10 = D(i1, j), d11 = D(i1, j + 1), d01 = D(i0, j + 1);
                    Vector3 p00 = P(d00), p10 = P(d10), p11 = P(d11), p01 = P(d01);
                    Vector2 u00, u10, u11, u01;
                    if (planarUv && Grain >= 0)
                    {
                        // a slab's edge continues the faces' grain (edge banding printed like the decor)
                        Vector3 sd = pl.Dir(sn.x, sn.y, 0f);
                        u00 = UV(d00, sd, p00, na); u10 = UV(d10, sd, p10, na); u11 = UV(d11, sd, p11, nb); u01 = UV(d01, sd, p01, nb);
                    }
                    else
                    {
                        u00 = Uv(along, arc[j]); u10 = Uv(along + seglen, arc[j]);
                        u11 = Uv(along + seglen, arc[j + 1]); u01 = Uv(along, arc[j + 1]);
                    }
                    DoorGeo.Quad(mb, p00, p10, p11, p01, na, na, nb, nb, u00, u10, u11, u01, m);
                }
                along += seglen;
            }
            // caps of an open path: +1 facing out along the path (a moulding's end), -1 facing back into it (a groove's end wall)
            if (!closed && caps != 0)
            {
                Cap(mb, pl, path, profile, wBase, m, 0, miter, caps);
                Cap(mb, pl, path, profile, wBase, m, n - 1, miter, caps);
            }
        }

        void Cap(MeshBuilder mb, CasePlane pl, IList<Vector2> path, IList<Vector2> profile, float wBase, Material m, int i, Vector2[] miter, int sign)
        {
            int n = path.Count;
            Vector2 t = i == 0 ? path[0] - path[1] : path[n - 1] - path[n - 2];
            t = t.normalized * sign;
            var nrm = N(pl.Dir(t.x, t.y, 0f));
            var region = new PathD();
            foreach (var q in profile) region.Add(new PointD(q.x, q.y));
            var pts = new PathsD { region };
            if (Clipper.Triangulate(pts, Dec, out PathsD tris) != TriangulateResult.success || tris == null) return;
            foreach (var tr in tris)
            {
                if (tr.Count < 3) continue;
                Vector3 Q(PointD q) => P(pl.At(path[i].x + miter[i].x * (float)q.x, path[i].y + miter[i].y * (float)q.x, wBase + (float)q.y));
                DoorGeo.Tri(mb, Q(tr[0]), Q(tr[1]), Q(tr[2]), nrm, nrm, nrm, Vector2.zero, new Vector2(0.01f, 0f), new Vector2(0f, 0.01f), m);
            }
        }

        // ------------------------------------------------------------------ faces
        /// <summary>
        /// A corrugated surface over [a0, a1] × [b0, b1] of the plane: height <paramref name="h"/>(a) above <paramref name="wBase"/>
        /// (ribs running along b), with its end caps at b0 / b1 and side walls at a0 / a1 down to the base.
        /// </summary>
        public void Corrugated(MeshBuilder mb, CasePlane pl, float a0, float a1, float b0, float b1, float wBase, Func<float, float> h,
                               int samples, Material m)
        {
            if (m == null || samples < 2 || a1 - a0 < 1e-3f) return;
            var a = new float[samples + 1];
            var z = new float[samples + 1];
            for (int i = 0; i <= samples; i++) { a[i] = Mathf.Lerp(a0, a1, i / (float)samples); z[i] = wBase + Mathf.Max(0f, h(a[i])); }
            // normals from the slope (central differences), split where the slope jumps (a rib meets the flat)
            Vector3 NormAt(int i, int seg)
            {
                float da = a[seg + 1] - a[seg], dz = z[seg + 1] - z[seg];
                float slope = dz / Mathf.Max(da, 1e-4f);
                // average with the neighbour segment when the surface bends gently
                int other = i == seg ? seg - 1 : seg + 1;
                if (other >= 0 && other < samples)
                {
                    float s2 = (z[other + 1] - z[other]) / Mathf.Max(a[other + 1] - a[other], 1e-4f);
                    if (Mathf.Abs(Mathf.Atan(s2) - Mathf.Atan(slope)) < 0.6f) slope = (slope + s2) * 0.5f;
                }
                return N(pl.Dir(-slope, 0f, 1f));
            }
            for (int s = 0; s < samples; s++)
            {
                Vector3 p00 = P(pl.At(a[s], b0, z[s])), p10 = P(pl.At(a[s + 1], b0, z[s + 1]));
                Vector3 p11 = P(pl.At(a[s + 1], b1, z[s + 1])), p01 = P(pl.At(a[s], b1, z[s]));
                Vector3 n0 = NormAt(s, s), n1 = NormAt(s + 1, s);
                Vector2 u00 = new Vector2(b0, a[s]) / 1000f, u10 = new Vector2(b0, a[s + 1]) / 1000f;
                Vector2 u11 = new Vector2(b1, a[s + 1]) / 1000f, u01 = new Vector2(b1, a[s]) / 1000f;
                DoorGeo.Quad(mb, p00, p10, p11, p01, n0, n1, n1, n0, u00, u10, u11, u01, m);
            }
            // end caps: the section under the profile, at both ends
            var sec = new PathD();
            sec.Add(new PointD(a0, wBase));
            for (int i = 0; i <= samples; i++) sec.Add(new PointD(a[i], z[i]));
            sec.Add(new PointD(a1, wBase));
            if (Clipper.Area(sec) < 0) sec.Reverse();
            var secs = Clipper.Union(new PathsD { sec }, new PathsD(), FillRule.NonZero, Dec);
            if (Clipper.Triangulate(secs, Dec, out PathsD tris) == TriangulateResult.success && tris != null)
                foreach (float bb in new[] { b0, b1 })
                {
                    var nrm = N(pl.Dir(0f, bb == b0 ? -1f : 1f, 0f));
                    foreach (var t in tris)
                    {
                        if (t.Count < 3) continue;
                        Vector3 Q(PointD q) => P(pl.At((float)q.x, bb, (float)q.y));
                        DoorGeo.Tri(mb, Q(t[0]), Q(t[1]), Q(t[2]), nrm, nrm, nrm, new Vector2((float)t[0].x, (float)t[0].y) / 1000f,
                            new Vector2((float)t[1].x, (float)t[1].y) / 1000f, new Vector2((float)t[2].x, (float)t[2].y) / 1000f, m);
                    }
                }
            // side walls where the profile stands above the base at the ends
            foreach (int i in new[] { 0, samples })
            {
                if (z[i] - wBase < 0.05f) continue;
                var nrm = N(pl.Dir(i == 0 ? -1f : 1f, 0f, 0f));
                DoorGeo.Quad(mb, P(pl.At(a[i], b0, wBase)), P(pl.At(a[i], b1, wBase)), P(pl.At(a[i], b1, z[i])), P(pl.At(a[i], b0, z[i])),
                    nrm, Vector2.zero, new Vector2(0.01f, 0f), new Vector2(0.01f, 0.01f), new Vector2(0f, 0.01f), m);
            }
        }

        /// <summary>Pyramids over [a0, a1] × [b0, b1]: cells <paramref name="cw"/> × <paramref name="ch"/> mm, apex <paramref name="depth"/> above <paramref name="wBase"/>.</summary>
        public void Pyramids(MeshBuilder mb, CasePlane pl, float a0, float a1, float b0, float b1, float cw, float ch, float wBase, float depth, Material m)
        {
            if (m == null || cw < 1f || ch < 1f) return;
            int nx = Mathf.Max(1, Mathf.RoundToInt((a1 - a0) / cw)), ny = Mathf.Max(1, Mathf.RoundToInt((b1 - b0) / ch));
            float sw = (a1 - a0) / nx, sh = (b1 - b0) / ny;
            for (int i = 0; i < nx; i++)
            for (int j = 0; j < ny; j++)
            {
                float x0 = a0 + i * sw, x1 = x0 + sw, y0 = b0 + j * sh, y1 = y0 + sh;
                var apex = pl.At((x0 + x1) * 0.5f, (y0 + y1) * 0.5f, wBase + depth);
                var c = new[] { pl.At(x0, y0, wBase), pl.At(x1, y0, wBase), pl.At(x1, y1, wBase), pl.At(x0, y1, wBase) };
                for (int k = 0; k < 4; k++)
                {
                    Vector3 d0 = c[k], d1 = c[(k + 1) % 4];
                    var n = Vector3.Cross(d1 - d0, apex - d0).normalized;
                    if (Vector3.Dot(n, pl.W) < 0) n = -n;
                    var nn = N(n);
                    Vector3 q0 = P(d0), q1 = P(d1), qa = P(apex);
                    DoorGeo.Tri(mb, q0, q1, qa, nn, nn, nn, UV(d0, n, q0, nn), UV(d1, n, q1, nn), UV(apex, n, qa, nn), m);
                }
            }
        }

        // ------------------------------------------------------------------ rods
        /// <summary>A bar from <paramref name="a"/> to <paramref name="b"/> (design mm): round or square, radius r0 at a tapering to r1 at b, capped.</summary>
        public void Rod(MeshBuilder mb, Vector3 a, Vector3 b, float r0, float r1, Material m, bool square = false, int sides = 20)
        {
            if (m == null) return;
            var axis = b - a;
            float len = axis.magnitude;
            if (len < 0.1f) return;
            axis /= len;
            var side = Mathf.Abs(Vector3.Dot(axis, Vector3.up)) > 0.9f ? Vector3.right : Vector3.up;
            var u = Vector3.Cross(axis, side).normalized;
            var v = Vector3.Cross(axis, u).normalized;
            if (square) sides = 4;
            float slope = (r0 - r1) / len;
            Vector3 Ring(int i, float r)
            {
                float t = (i + (square ? 0.5f : 0f)) / sides * Mathf.PI * 2f;
                float k = square ? Mathf.Sqrt(2f) : 1f;
                return (u * Mathf.Cos(t) + v * Mathf.Sin(t)) * r * k;
            }
            for (int i = 0; i < sides; i++)
            {
                Vector3 e0 = Ring(i, 1f), e1 = Ring(i + 1, 1f);
                Vector3 n0 = (e0.normalized + axis * slope).normalized, n1 = (e1.normalized + axis * slope).normalized;
                if (square) { var f = ((e0 + e1) * 0.5f).normalized; n0 = n1 = (f + axis * slope).normalized; }
                Vector3 p00 = a + e0 * r0, p10 = a + e1 * r0, p11 = b + e1 * r1, p01 = b + e0 * r1;
                float c0 = i / (float)sides, c1 = (i + 1) / (float)sides;
                DoorGeo.Quad(mb, P(p00), P(p10), P(p11), P(p01), N(n0), N(n1), N(n1), N(n0),
                    new Vector2(c0 * 0.1f, 0f), new Vector2(c1 * 0.1f, 0f), new Vector2(c1 * 0.1f, len / 1000f), new Vector2(c0 * 0.1f, len / 1000f), m);
            }
            foreach (var (c, r, dir) in new[] { (a, r0, -axis), (b, r1, axis) })
            {
                if (r < 0.05f) continue;
                var nn = N(dir);
                for (int i = 0; i < sides; i++)
                    DoorGeo.Tri(mb, P(c), P(c + Ring(i, r)), P(c + Ring(i + 1, r)), nn, nn, nn, Vector2.zero, new Vector2(0.01f, 0f), new Vector2(0f, 0.01f), m);
            }
        }

        // ------------------------------------------------------------------ shapes
        public static PathD Rect(float a0, float b0, float a1, float b1) =>
            new PathD { new PointD(a0, b0), new PointD(a1, b0), new PointD(a1, b1), new PointD(a0, b1) };

        /// <summary>Ellipse in the box, counter-clockwise (reverse it for a hole).</summary>
        public static PathD Ellipse(float ca, float cb, float ra, float rb, int seg = 0)
        {
            if (seg <= 0) seg = Mathf.Clamp(Mathf.CeilToInt(Mathf.Max(ra, rb) * 0.35f), 12, 96);
            var p = new PathD(seg);
            for (int i = 0; i < seg; i++)
            {
                float t = i / (float)seg * Mathf.PI * 2f;
                p.Add(new PointD(ca + ra * Mathf.Cos(t), cb + rb * Mathf.Sin(t)));
            }
            return p;
        }

        /// <summary>Half of a ring (outer radius <paramref name="ro"/>, inner <paramref name="ri"/>) whose arc bulges along <paramref name="dir"/> from the cut line through (ca, cb).</summary>
        public static PathD HalfRing(float ca, float cb, float ro, float ri, Vector2 dir, int seg = 24)
        {
            float a0 = Mathf.Atan2(dir.y, dir.x) - Mathf.PI * 0.5f;
            var p = new PathD();
            for (int i = 0; i <= seg; i++)
            {
                float t = a0 + Mathf.PI * i / seg;
                p.Add(new PointD(ca + ro * Mathf.Cos(t), cb + ro * Mathf.Sin(t)));
            }
            for (int i = seg; i >= 0; i--)
            {
                float t = a0 + Mathf.PI * i / seg;
                p.Add(new PointD(ca + ri * Mathf.Cos(t), cb + ri * Mathf.Sin(t)));
            }
            return p;
        }

        /// <summary>A rectangle with its corners rounded by <paramref name="r"/>, counter-clockwise.</summary>
        public static PathD RoundRect(float a0, float b0, float a1, float b1, float r)
        {
            r = Mathf.Min(r, (a1 - a0) * 0.5f, (b1 - b0) * 0.5f);
            if (r < 0.05f) return Rect(a0, b0, a1, b1);
            var p = new PathD();
            const int seg = 8;
            void Arc(float cx, float cy, float t0)
            {
                for (int i = 0; i <= seg; i++)
                {
                    float t = t0 + i / (float)seg * Mathf.PI * 0.5f;
                    p.Add(new PointD(cx + r * Mathf.Cos(t), cy + r * Mathf.Sin(t)));
                }
            }
            Arc(a1 - r, b0 + r, -Mathf.PI * 0.5f);
            Arc(a1 - r, b1 - r, 0f);
            Arc(a0 + r, b1 - r, Mathf.PI * 0.5f);
            Arc(a0 + r, b0 + r, Mathf.PI);
            return p;
        }

        public static PathD Reversed(PathD p)
        {
            var r = new PathD(p);
            r.Reverse();
            return r;
        }
    }
}
