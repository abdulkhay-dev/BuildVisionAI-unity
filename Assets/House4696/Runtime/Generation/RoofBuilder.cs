using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Roofs. Flat: slab over the outline grown by the overhang (soffit underneath, fascia edges, metal coping) and
    /// an optional parapet on the outline. Shed/gable/hip: sloped slabs over the outline's bounding rectangle in
    /// the roof frame (ridge along local X), eaves dropping with the overhang, gable/shed end walls filled in.
    /// </summary>
    public sealed class RoofBuilder
    {
        const float ParapetT = 0.25f;
        const float WallSeat = 0.4f;   // typical exterior wall thickness: where the roof bears on the walls
        readonly HouseContext _c;
        public RoofBuilder(HouseContext c) { _c = c; }

        public void Build(RoofDef r)
        {
            if (r.Outline == null || r.Outline.Count < 3) { _c.Warn($"roof '{r.Id}' needs an outline"); return; }
            var mb = new MeshBuilder();
            var cap = new MeshBuilder();
            var top = _c.Mats.Get(r.Material, _c.Lib.Coping);
            var soffit = _c.Mats.Get(r.Soffit, _c.Lib.Soffit);
            var fascia = _c.Lib.Stucco;
            // gable/shed end walls have no battens: "wood" means vertical boards (plank atlas), not the backing
            var gable = MaterialResolver.Key(r.Gable) == "wood" ? _c.Lib.Wood : _c.Mats.Get(r.Gable, _c.Lib.Stucco);
            if (r.Type == RoofType.Flat) Flat(r, mb, cap, top, soffit, fascia);
            else Pitched(r, mb, top, soffit, fascia, gable);
            string id = r.Id ?? "roof";
            _c.W.Emit("Roof_" + id, _c.Shell, mb);
            _c.W.Emit("Roof_Coping_" + id, _c.Shell, cap);
        }

        // ------------------------------------------------------------------ flat
        void Flat(RoofDef r, MeshBuilder mb, MeshBuilder cap, Material top, Material soffit, Material fascia)
        {
            var outline = Polygon.CounterClockwise(r.Outline);
            var slab = Offset(outline, r.Overhang);
            float y0 = r.Base, y1 = r.Base + r.Thickness;
            Polygon.Prism(mb, slab, y0, y1, r.Parapet > 0 ? top : null, soffit, fascia);
            if (r.Parapet <= 0f)
            {
                Polygon.Prism(cap, Offset(slab, 0.02f), y1, y1 + 0.075f, _c.Lib.Coping, null, _c.Lib.Coping);
                return;
            }
            // parapet ring on the outline, with a coping cap
            float p0 = y1, p1 = y1 + r.Parapet;
            for (int i = 0; i < outline.Count; i++)
            {
                Vector2 a = outline[i], b = outline[(i + 1) % outline.Count];
                var d = b - a; float len = d.magnitude;
                if (len < 1e-4f) continue;
                d /= len;
                var n = new Vector3(d.y, 0, -d.x); // outward of a CCW outline
                var m = Matrix4x4.TRS(new Vector3(a.x, 0, a.y), Quaternion.LookRotation(-n, Vector3.up), Vector3.one);
                mb.Transform = m; cap.Transform = m;
                mb.Box(new Vector3(0, p0, 0), new Vector3(len, p1, ParapetT), BoxMats.All(fascia).Without(yp: true, yn: true));
                cap.Box(new Vector3(-0.025f, p1, -0.025f), new Vector3(len + 0.025f, p1 + 0.03f, ParapetT + 0.025f), BoxMats.All(_c.Lib.Coping).Without(yn: true));
            }
            mb.Transform = Matrix4x4.identity; cap.Transform = Matrix4x4.identity;
        }

        /// <summary>Grows a (mostly convex / orthogonal) CCW polygon by moving each edge outward and intersecting neighbours.</summary>
        public static List<Vector2> Offset(IList<Vector2> ccw, float dist)
        {
            if (Mathf.Abs(dist) < 1e-5f) return new List<Vector2>(ccw);
            int n = ccw.Count;
            var res = new List<Vector2>(n);
            for (int i = 0; i < n; i++)
            {
                Vector2 p = ccw[(i + n - 1) % n], c = ccw[i], nx = ccw[(i + 1) % n];
                Vector2 d0 = (c - p).normalized, d1 = (nx - c).normalized;
                Vector2 n0 = new Vector2(d0.y, -d0.x), n1 = new Vector2(d1.y, -d1.x);
                Vector2 bis = n0 + n1;
                float cos = Vector2.Dot(bis.normalized, n0);
                if (bis.sqrMagnitude < 1e-8f || cos < 0.2f) { res.Add(c + n0 * dist); continue; }
                res.Add(c + bis.normalized * (dist / cos));
            }
            return res;
        }

        // ------------------------------------------------------------------ pitched
        void Pitched(RoofDef r, MeshBuilder mb, Material top, Material soffit, Material fascia, Material gable)
        {
            var rot = Quaternion.Euler(0, r.Rotation, 0);
            var inv = Quaternion.Inverse(rot);
            float x0 = float.MaxValue, x1 = float.MinValue, z0 = float.MaxValue, z1 = float.MinValue;
            foreach (var p in r.Outline)
            {
                var l = inv * new Vector3(p.x, 0, p.y);
                x0 = Mathf.Min(x0, l.x); x1 = Mathf.Max(x1, l.x); z0 = Mathf.Min(z0, l.z); z1 = Mathf.Max(z1, l.z);
            }
            mb.Transform = Matrix4x4.TRS(Vector3.zero, rot, Vector3.one);
            float pitch = Mathf.Clamp(r.Pitch, 3f, 70f) * Mathf.Deg2Rad;
            float tan = Mathf.Tan(pitch);
            float oh = r.Overhang, t = r.Thickness;
            float X0 = x0 - oh, X1 = x1 + oh, Z0 = z0 - oh, Z1 = z1 + oh;
            // the roof rests on the walls: its underside passes through the wall tops (Base) on the outer wall
            // line, so the top surface is one vertical slab thickness higher; the eave drops with the overhang
            float lift = t / Mathf.Cos(pitch);
            // the underside meets the wall top on the wall's inner face (~0.4 m in), so the outer part of the wall
            // and its cladding run into the roof slab instead of leaving a slit under it
            float seat = WallSeat * tan;
            lift -= seat;
            float ye = r.Base - oh * tan + lift;          // top surface at the overhang edge
            float wallTop = r.Base;
            float zc = (z0 + z1) * 0.5f;

            switch (r.Type)
            {
                case RoofType.Gable:
                {
                    float yr = r.Base + (zc - z0) * tan + lift;
                    Slab(mb, new[] { V(X0, ye, Z0), V(X1, ye, Z0), V(X1, yr, zc), V(X0, yr, zc) }, t, top, soffit, fascia);
                    Slab(mb, new[] { V(X1, ye, Z1), V(X0, ye, Z1), V(X0, yr, zc), V(X1, yr, zc) }, t, top, soffit, fascia);
                    foreach (float x in new[] { x0, x1 })
                        EndWall(mb, x, x == x0 ? 1 : -1, new[] { new Vector2(z0, wallTop), new Vector2(z1, wallTop), new Vector2(zc, yr - lift - seat) }, gable);
                    break;
                }
                case RoofType.Shed:
                {
                    float yh = r.Base + (z1 - z0) * tan, yH = yh + oh * tan + lift;
                    Slab(mb, new[] { V(X0, ye, Z0), V(X1, ye, Z0), V(X1, yH, Z1), V(X0, yH, Z1) }, t, top, soffit, fascia);
                    foreach (float x in new[] { x0, x1 })
                        EndWall(mb, x, x == x0 ? 1 : -1, new[] { new Vector2(z0, wallTop), new Vector2(z1, wallTop), new Vector2(z1, yh) }, gable);
                    // high wall under the upper eave
                    var hw = BoxMats.All(gable).Without(yn: true);
                    mb.Box(new Vector3(x0, wallTop, z1 - 0.3f), new Vector3(x1, yh, z1), hw);
                    break;
                }
                default: // hip
                {
                    float halfW = (Z1 - Z0) * 0.5f;
                    float h = Mathf.Min(halfW, (X1 - X0) * 0.5f);
                    float yr = ye + h * tan;                   // ye already includes the lift
                    float zm = (Z0 + Z1) * 0.5f;
                    float ra = X0 + h, rb = X1 - h;            // ridge ends (equal when the plan is square)
                    Slab(mb, new[] { V(X0, ye, Z0), V(X1, ye, Z0), V(rb, yr, zm), V(ra, yr, zm) }, t, top, soffit, fascia);
                    Slab(mb, new[] { V(X1, ye, Z1), V(X0, ye, Z1), V(ra, yr, zm), V(rb, yr, zm) }, t, top, soffit, fascia);
                    Slab(mb, new[] { V(X0, ye, Z1), V(X0, ye, Z0), V(ra, yr, zm) }, t, top, soffit, fascia);
                    Slab(mb, new[] { V(X1, ye, Z0), V(X1, ye, Z1), V(rb, yr, zm) }, t, top, soffit, fascia);
                    break;
                }
            }
            mb.Transform = Matrix4x4.identity;
        }

        static Vector3 V(float x, float y, float z) => new Vector3(x, y, z);

        /// <summary>
        /// Sloped slab: <paramref name="topPoly"/> is the (convex) top surface, counter-clockwise seen from above; the
        /// underside is the same outline lowered by the vertical thickness. UVs follow the slope (u across, v down-slope).
        /// </summary>
        static void Slab(MeshBuilder mb, Vector3[] topPoly, float thickness, Material top, Material bottom, Material edge)
        {
            Vector3 n = Vector3.Cross(topPoly[2] - topPoly[0], topPoly[1] - topPoly[0]).normalized;
            if (n.y < 0) n = -n;
            float dy = thickness / Mathf.Max(0.2f, n.y);
            Vector3 u = Vector3.Cross(Vector3.up, n);
            u = u.sqrMagnitude < 1e-6f ? Vector3.right : u.normalized;
            Vector3 v = Vector3.Cross(n, u).normalized;
            Vector2 UV(Vector3 p) => new Vector2(Vector3.Dot(p, u), Vector3.Dot(p, v));
            int k = topPoly.Length;
            for (int i = 1; i + 1 < k; i++)
            {
                Vector3 a = topPoly[0], b = topPoly[i], c = topPoly[i + 1];
                // CCW seen from above → clockwise front order a, c, b
                mb.Triangle(a, c, b, n, n, n, UV(a), UV(c), UV(b), top);
                Vector3 ad = a + Vector3.down * dy, bd = b + Vector3.down * dy, cd = c + Vector3.down * dy;
                mb.Triangle(ad, bd, cd, -n, -n, -n, UV(ad), UV(bd), UV(cd), bottom);
            }
            for (int i = 0; i < k; i++)
            {
                Vector3 a = topPoly[i], b = topPoly[(i + 1) % k];
                Vector3 e = b - a;
                if (new Vector2(e.x, e.z).sqrMagnitude < 1e-8f) continue;
                Vector3 en = new Vector3(e.z, 0, -e.x).normalized; // outward of a CCW polygon: right of the edge
                Vector3 ad = a + Vector3.down * dy, bd = b + Vector3.down * dy;
                float len = e.magnitude;
                mb.Quad(ad, bd, b, a, en, new Vector2(0, 0), new Vector2(len, 0), new Vector2(len, dy), new Vector2(0, dy), edge);
            }
        }

        /// <summary>Gable/shed end wall at local x (inward direction <paramref name="inward"/>): a (z, y) polygon extruded 0.3 m.</summary>
        static void EndWall(MeshBuilder mb, float x, int inward, Vector2[] zy, Material m)
        {
            const float t = 0.3f;
            float xa = x, xb = x + inward * t;
            for (int side = 0; side < 2; side++)
            {
                float px = side == 0 ? xa : xb;
                Vector3 n = side == 0 ? Vector3.right * -inward : Vector3.right * inward;
                for (int i = 1; i + 1 < zy.Length; i++)
                {
                    Vector3 a = new Vector3(px, zy[0].y, zy[0].x), b = new Vector3(px, zy[i].y, zy[i].x), c = new Vector3(px, zy[i + 1].y, zy[i + 1].x);
                    Vector2 ua = new Vector2(a.z, a.y), ub = new Vector2(b.z, b.y), uc = new Vector2(c.z, c.y);
                    // Unity front faces: Cross(b - a, c - a) points along the normal
                    if (Vector3.Dot(Vector3.Cross(b - a, c - a), n) > 0) mb.Triangle(a, b, c, n, n, n, ua, ub, uc, m);
                    else mb.Triangle(a, c, b, n, n, n, ua, uc, ub, m);
                }
            }
        }
    }
}
