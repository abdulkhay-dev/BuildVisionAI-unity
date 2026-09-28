using House4696.Core;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>
    /// Geometry primitives of doors, in a builder's local space (metres). Triangles orient themselves by the normals
    /// they are given, so callers list corners in either direction; a builder whose transform mirrors sets
    /// <see cref="MeshBuilder.FlipWinding"/>.
    /// </summary>
    public static class DoorGeo
    {
        /// <summary>Triangle facing along the average of its normals.</summary>
        public static void Tri(MeshBuilder mb, Vector3 a, Vector3 b, Vector3 c, Vector3 na, Vector3 nb, Vector3 nc,
                               Vector2 ua, Vector2 ub, Vector2 uc, Material m)
        {
            if (m == null) return;
            // Unity front faces: (b - a) × (c - a) points at the viewer
            if (Vector3.Dot(Vector3.Cross(b - a, c - a), na + nb + nc) >= 0f) mb.Triangle(a, b, c, na, nb, nc, ua, ub, uc, m);
            else mb.Triangle(a, c, b, na, nc, nb, ua, uc, ub, m);
        }

        /// <summary>Quad a-b-c-d (corners in order around it, either direction) with per-corner normals.</summary>
        public static void Quad(MeshBuilder mb, Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 na, Vector3 nb, Vector3 nc, Vector3 nd,
                                Vector2 ua, Vector2 ub, Vector2 uc, Vector2 ud, Material m)
        {
            Tri(mb, a, b, c, na, nb, nc, ua, ub, uc, m);
            Tri(mb, a, c, d, na, nc, nd, ua, uc, ud, m);
        }

        public static void Quad(MeshBuilder mb, Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 n,
                                Vector2 ua, Vector2 ub, Vector2 uc, Vector2 ud, Material m) =>
            Quad(mb, a, b, c, d, n, n, n, n, ua, ub, uc, ud, m);

        /// <summary>
        /// A board of a leaf: rectangle <paramref name="r"/> in XY with faces at z = ±<paramref name="h"/>, every face edge
        /// rounded with radius <paramref name="rad"/> (the vertical corners stay square: boards meet there). Wood grain
        /// runs along y when <paramref name="grainV"/>, else along x. UVs are metres, and the film wraps round the edges:
        /// the texture of the face continues over the rounding and down the sides, like the real foil.
        /// </summary>
        public static void Slab(MeshBuilder mb, Rect r, float h, float rad, Material m, bool grainV, Vector2 uvOffset, int seg = 3,
                                Clipper2Lib.PathsD cutFront = null, Clipper2Lib.PathsD cutBack = null)
        {
            if (m == null || r.width < 1e-4f || r.height < 1e-4f || h < 1e-5f) return;
            rad = Mathf.Min(rad, h * 0.95f, r.width * 0.45f, r.height * 0.45f);
            if (rad < 2e-4f) { rad = 0f; seg = 0; }
            Vector2 Uv(float x, float y) => (grainV ? new Vector2(y, x) : new Vector2(x, y)) + uvOffset;

            int n = seg;
            var inset = new float[n + 1];
            var zz = new float[n + 1];
            var sn = new float[n + 1];
            var cs = new float[n + 1];
            var arc = new float[n + 1];
            for (int k = 0; k <= n; k++)
            {
                float th = n == 0 ? 0f : k / (float)n * Mathf.PI * 0.5f;
                inset[k] = rad * (1f - Mathf.Sin(th));
                zz[k] = h - rad * (1f - Mathf.Cos(th));
                sn[k] = Mathf.Sin(th);
                cs[k] = Mathf.Cos(th);
                arc[k] = rad * th;
            }
            float wall = rad * Mathf.PI * 0.5f;   // unrolled length of the rounding

            // sides: 0 bottom (-y), 1 right (+x), 2 top (+y), 3 left (-x); edge point p(t) with t 0..1 along the side
            Vector3 SidePoint(int side, float t, float ins, float z)
            {
                float x0 = r.xMin + ins, x1 = r.xMax - ins, y0 = r.yMin + ins, y1 = r.yMax - ins;
                switch (side)
                {
                    case 0: return new Vector3(Mathf.Lerp(x0, x1, t), y0, z);
                    case 1: return new Vector3(x1, Mathf.Lerp(y0, y1, t), z);
                    case 2: return new Vector3(Mathf.Lerp(x1, x0, t), y1, z);
                    default: return new Vector3(x0, Mathf.Lerp(y1, y0, t), z);
                }
            }
            Vector2 Out(int side) => side == 0 ? Vector2.down : side == 1 ? Vector2.right : side == 2 ? Vector2.up : Vector2.left;
            // film unrolled outward from the face edge by distance d
            Vector2 WrapUv(int side, Vector3 p, float d)
            {
                switch (side)
                {
                    case 0: return Uv(p.x, r.yMin + rad - d);
                    case 1: return Uv(r.xMax - rad + d, p.y);
                    case 2: return Uv(p.x, r.yMax - rad + d);
                    default: return Uv(r.xMin + rad - d, p.y);
                }
            }

            foreach (float s in new[] { 1f, -1f })
            {
                var nz = new Vector3(0f, 0f, s);
                float i0 = inset[0], z0 = s * h;
                Vector3 a = new Vector3(r.xMin + i0, r.yMin + i0, z0), b = new Vector3(r.xMax - i0, r.yMin + i0, z0),
                        c = new Vector3(r.xMax - i0, r.yMax - i0, z0), d = new Vector3(r.xMin + i0, r.yMax - i0, z0);
                // features cut into this face (grooves, glass, panels): the face is the rectangle minus them (millimetres)
                var cut = s > 0f ? cutFront : cutBack;
                var faceMm = new Rect(a.x * 1000f, a.y * 1000f, (b.x - a.x) * 1000f, (d.y - a.y) * 1000f);
                Clipper2Lib.PathsD inside = null;
                if (cut != null && cut.Count > 0)
                {
                    inside = Relief.Intersect(cut, Relief.Rect(faceMm));
                    if (Relief.Area(inside) < 0.5) inside = null;
                }
                if (inside == null) Quad(mb, a, b, c, d, nz, Uv(a.x, a.y), Uv(b.x, b.y), Uv(c.x, c.y), Uv(d.x, d.y), m);
                else Relief.Fill(mb, Relief.Difference(Relief.Rect(faceMm), inside), h * 1000f, s, m, p => Uv(p.x / 1000f, p.y / 1000f));

                for (int side = 0; side < 4; side++)
                {
                    Vector2 o = Out(side);
                    for (int k = 0; k < n; k++)
                    {
                        Vector3 p0 = SidePoint(side, 0f, inset[k], s * zz[k]), p1 = SidePoint(side, 1f, inset[k], s * zz[k]);
                        Vector3 q0 = SidePoint(side, 0f, inset[k + 1], s * zz[k + 1]), q1 = SidePoint(side, 1f, inset[k + 1], s * zz[k + 1]);
                        Vector3 np = new Vector3(o.x * sn[k], o.y * sn[k], s * cs[k]);
                        Vector3 nq = new Vector3(o.x * sn[k + 1], o.y * sn[k + 1], s * cs[k + 1]);
                        Quad(mb, p0, p1, q1, q0, np, np, nq, nq,
                            WrapUv(side, p0, arc[k]), WrapUv(side, p1, arc[k]), WrapUv(side, q1, arc[k + 1]), WrapUv(side, q0, arc[k + 1]), m);
                    }
                    // side wall: from the rounding down to the middle of the edge (the back half continues from the back face)
                    float zTop = s * (h - rad);
                    Vector3 w0 = SidePoint(side, 0f, 0f, zTop), w1 = SidePoint(side, 1f, 0f, zTop);
                    Vector3 m0 = SidePoint(side, 0f, 0f, 0f), m1 = SidePoint(side, 1f, 0f, 0f);
                    var nw = new Vector3(o.x, o.y, 0f);
                    float dTop = wall, dMid = wall + (h - rad);
                    Quad(mb, w0, w1, m1, m0, nw, WrapUv(side, w0, dTop), WrapUv(side, w1, dTop), WrapUv(side, m1, dMid), WrapUv(side, m0, dMid), m);
                }
            }
        }

        /// <summary>Glass pane over <paramref name="r"/>, faces at z = ±<paramref name="halfT"/>; its edges sit in the boards and stay hidden.</summary>
        public static void Pane(MeshBuilder mb, Rect r, float halfT, Material m, Rect? fit = null)
        {
            if (m == null || r.width < 1e-4f || r.height < 1e-4f) return;
            // UVs: metres (a tiled pattern), or 0…1 over the visible glass (a picture)
            Vector2 Uv(Vector3 p) => fit.HasValue
                ? new Vector2((p.x - fit.Value.xMin) / Mathf.Max(1e-4f, fit.Value.width), (p.y - fit.Value.yMin) / Mathf.Max(1e-4f, fit.Value.height))
                : new Vector2(p.x, p.y);
            foreach (float s in new[] { 1f, -1f })
            {
                var n = new Vector3(0f, 0f, s);
                Vector3 a = new Vector3(r.xMin, r.yMin, s * halfT), b = new Vector3(r.xMax, r.yMin, s * halfT),
                        c = new Vector3(r.xMax, r.yMax, s * halfT), d = new Vector3(r.xMin, r.yMax, s * halfT);
                Quad(mb, a, b, c, d, n, Uv(a), Uv(b), Uv(c), Uv(d), m);
            }
        }

        /// <summary>
        /// Straight moulding: a 2D profile (x across the moulding, y its height above the base plane, listed along the
        /// visible surface) extruded from <paramref name="a"/> to <paramref name="b"/>. <paramref name="across"/> and
        /// <paramref name="up"/> give the profile's axes in space. Each end is cut square, or along a 45° mitre when
        /// <c>miterA</c>/<c>miterB</c> is set: the end then moves along the axis by the profile x (so two mouldings meeting
        /// at a corner close the joint). UVs: u along the moulding, v along the profile (metres) — the grain runs lengthwise.
        /// </summary>
        public static void Moulding(MeshBuilder mb, Vector2[] profile, Vector3 a, Vector3 b, Vector3 across, Vector3 up, Material m,
                                    bool miterA, bool miterB, bool capA = true, bool capB = true, float uOffset = 0f, int materialSide = 0)
        {
            if (m == null || profile == null || profile.Length < 2) return;
            Vector3 axis = b - a;
            float len = axis.magnitude;
            if (len < 1e-5f) return;
            axis /= len;
            int n = profile.Length;
            // profile normals (in the across/up plane), smooth unless the turn is sharp
            var segN = new Vector2[n - 1];
            for (int k = 0; k + 1 < n; k++)
            {
                Vector2 t = (profile[k + 1] - profile[k]).normalized;
                segN[k] = new Vector2(t.y, -t.x);
            }
            // outward = to the right of travel when the material is on the left (materialSide > 0), to the left when it is on
            // the right (< 0); unspecified: whichever makes the surface face up on average (bars, casings)
            float sum = 0f;
            foreach (var sN in segN) sum += sN.y;
            if (materialSide < 0 || materialSide == 0 && sum < 0f) for (int k = 0; k < segN.Length; k++) segN[k] = -segN[k];
            var vAcc = new float[n];
            for (int k = 1; k < n; k++) vAcc[k] = vAcc[k - 1] + (profile[k] - profile[k - 1]).magnitude;

            Vector3 P(Vector2 pr, bool atB)
            {
                Vector3 basePt = atB ? b : a;
                // mitre: the end slides along the axis by the across offset (outer edge longer)
                float slide = (atB ? (miterB ? pr.x : 0f) : (miterA ? -pr.x : 0f));
                return basePt + axis * slide + across * pr.x + up * pr.y;
            }
            Vector3 N3(Vector2 nn) => (across * nn.x + up * nn.y).normalized;
            for (int k = 0; k + 1 < n; k++)
            {
                Vector2 p0 = profile[k], p1 = profile[k + 1];
                bool sharpA = k > 0 && Vector2.Dot(segN[k - 1], segN[k]) < 0.7f;
                bool sharpB = k + 2 < n && Vector2.Dot(segN[k], segN[k + 1]) < 0.7f;
                Vector2 n0 = k == 0 || sharpA ? segN[k] : (segN[k - 1] + segN[k]).normalized;
                Vector2 n1 = k + 2 >= n || sharpB ? segN[k] : (segN[k] + segN[k + 1]).normalized;
                Vector3 A0 = P(p0, false), A1 = P(p1, false), B0 = P(p0, true), B1 = P(p1, true);
                float ua0 = Vector3.Dot(A0 - a, axis) + uOffset, ua1 = Vector3.Dot(A1 - a, axis) + uOffset;
                float ub0 = Vector3.Dot(B0 - a, axis) + uOffset, ub1 = Vector3.Dot(B1 - a, axis) + uOffset;
                Quad(mb, A0, B0, B1, A1, N3(n0), N3(n0), N3(n1), N3(n1),
                    new Vector2(ua0, vAcc[k]), new Vector2(ub0, vAcc[k]), new Vector2(ub1, vAcc[k + 1]), new Vector2(ua1, vAcc[k + 1]), m);
            }
            // end caps: fan over the profile polygon (closed by the base line)
            void Cap(bool atB)
            {
                // outward along the axis (a mitred cap is hidden by its partner anyway)
                Vector3 capN = atB ? axis : -axis;
                Vector3 c0 = P(new Vector2(profile[0].x, 0f), atB), c1 = P(new Vector2(profile[n - 1].x, 0f), atB);
                var center = (c0 + c1) * 0.5f;
                for (int k = 0; k + 1 < n; k++)
                {
                    Vector3 p = P(profile[k], atB), q = P(profile[k + 1], atB);
                    Vector3 fn = Vector3.Cross(q - p, center - p);
                    if (fn.sqrMagnitude < 1e-14f) continue;
                    fn = fn.normalized;
                    if (Vector3.Dot(fn, capN) < 0f) fn = -fn;
                    Tri(mb, center, p, q, fn, fn, fn, Vector2.zero, new Vector2(profile[k].x, profile[k].y), new Vector2(profile[k + 1].x, profile[k + 1].y), m);
                }
            }
            if (capA) Cap(false);
            if (capB) Cap(true);
        }

        /// <summary>Flat bar profile with rounded top edges: width × thickness, radii at the start and end edges (x = 0 / x = width).</summary>
        public static Vector2[] BarProfile(float width, float thickness, float r0, float r1, int seg = 4)
        {
            var pts = new System.Collections.Generic.List<Vector2> { new Vector2(0f, 0f) };
            r0 = Mathf.Min(r0, thickness, width * 0.5f);
            r1 = Mathf.Min(r1, thickness, width * 0.5f);
            if (r0 > 1e-5f)
                for (int k = 0; k <= seg; k++)
                {
                    float th = k / (float)seg * Mathf.PI * 0.5f;   // from the side up to the top
                    pts.Add(new Vector2(r0 - r0 * Mathf.Cos(th), thickness - r0 + r0 * Mathf.Sin(th)));
                }
            else pts.Add(new Vector2(0f, thickness));
            if (r1 > 1e-5f)
                for (int k = 0; k <= seg; k++)
                {
                    float th = k / (float)seg * Mathf.PI * 0.5f;
                    pts.Add(new Vector2(width - r1 + r1 * Mathf.Sin(th), thickness - r1 + r1 * Mathf.Cos(th)));
                }
            else pts.Add(new Vector2(width, thickness));
            pts.Add(new Vector2(width, 0f));
            return pts.ToArray();
        }
    }
}
