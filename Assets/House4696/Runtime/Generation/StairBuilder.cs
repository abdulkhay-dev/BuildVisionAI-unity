using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Stairs in their own frame: origin = bottom of the first flight on its centre line (at the lower floor), local
    /// +Z = walking direction of the first flight, +X = its right. Floating oak treads (or solid concrete), a
    /// landing slab for L/U stairs, handrails, glass guards and step lights.
    /// </summary>
    public sealed class StairBuilder
    {
        const float Tread = 0.06f;
        const float Waist = 0.2f;   // concrete under the treads of a solid flight that has nothing below it
        readonly HouseContext _c;
        public StairBuilder(HouseContext c) { _c = c; }

        public void Build(StairDef s)
        {
            var from = _c.Level(s.From);
            var to = _c.Level(s.To ?? _c.Above(from)?.Id);
            float H = to.Elevation - from.Elevation;
            if (H <= 0.2f) { _c.Warn($"stair '{s.Id}': level '{s.To}' is not above '{s.From}'"); return; }
            int n = Mathf.Max(3, s.Risers ?? Mathf.RoundToInt(H / 0.175f));
            float rise = H / n, g = s.Going, w = s.Width, hw = w * 0.5f;
            bool left = s.Turn != "right";
            float side = left ? -1f : 1f;                 // direction of the second flight / return

            var m = Matrix4x4.TRS(new Vector3(s.Start.x, from.Elevation, s.Start.y), Quaternion.Euler(0, s.Direction, 0), Vector3.one);
            var mb = new MeshBuilder { Transform = m };
            var glass = new MeshBuilder { Transform = m };
            var rails = new MeshBuilder { Transform = m };
            var lights = new MeshBuilder { Transform = m };
            var oak = BoxMats.All(_c.M.OakLight);
            bool solid = s.Style == "solid" || s.Style == "concrete";
            var treadMats = solid ? BoxMats.All(_c.M.Plaster).With(yp: _c.M.OakLight) : oak;
            float slabBottom = H - to.Slab;               // underside of the upper floor

            // a solid stair is a mass down to its floor — except over a stairwell (stairs stacked storey on storey):
            // there it keeps a waist under the treads, or it would fill the headroom of the flight below
            var below = new List<Vector2[]>();
            foreach (var sg in _c.StairGeometries) if (sg.To == from && sg.Def != s) below.AddRange(sg.Well);
            bool OverVoid(float x, float z)
            {
                var w = m.MultiplyPoint(new Vector3(x, 0, z));
                var p = new Vector2(w.x, w.z);
                return below.Exists(h => Polygon.Contains(h, p));
            }
            // over a void the step only reaches down to the soffit plate under the flight (see Soffit)
            void TreadZ(float x0, float x1, float z0, float z1, float top)
            {
                float y0 = !solid ? top - Tread : OverVoid((x0 + x1) * 0.5f, (z0 + z1) * 0.5f) ? top - rise - 0.02f : 0f;
                mb.Box(new Vector3(x0, y0, z0), new Vector3(x1, top, z1), treadMats);
            }
            // smooth concrete waist under a solid flight over a void: its top runs through the inner corners of the steps
            void Soffit(float x0, float x1, float za, float ya, float zb, float yb)
            {
                if (!solid || !OverVoid((x0 + x1) * 0.5f, (za + zb) * 0.5f) || Mathf.Abs(zb - za) < 0.1f) return;
                float slope = (yb - ya) / (zb - za), t = Waist * Mathf.Sqrt(1f + slope * slope);
                PlateX(mb, x0, x1, new List<Vector2> { new Vector2(za, ya), new Vector2(zb, yb), new Vector2(zb, yb - t), new Vector2(za, ya - t) }, _c.M.Plaster);
            }
            void TreadX(float x0, float x1, float z0, float z1, float top) => TreadZ(x0, x1, z0, z1, top);

            int k = s.Type == StairType.Straight ? n : Mathf.Clamp(s.FirstFlight ?? n / 2 + 1, 2, n - 2);
            float wallX = side > 0 ? -hw : hw;           // flight 1 usually runs along a wall on the outer side
            float landY1 = k * rise, zl1 = (k - 1) * g;   // top of flight 1: the landing (or the upper floor)
            float zEnd1 = s.Type == StairType.Straight ? (n - 1) * g : zl1;
            // a side with no wall along it gets a steel stringer under the tread ends and a glass guard: floating treads
            // need a wall to hang on, and a handrail needs something to be fixed to
            bool walled1 = Walled(m, new Vector3(wallX, 0, 0), new Vector3(wallX, 0, zEnd1), Vector3.right * Mathf.Sign(wallX), landY1 * 0.5f + 1f);
            // flight 1
            for (int i = 1; i < k; i++)
            {
                float top = i * rise, z0 = (i - 1) * g;
                TreadZ(-hw, hw, z0, z0 + g + 0.02f, top);
                if (!solid && walled1 && i % 2 == 1) StepLight(lights, side > 0 ? -hw + 0.004f : hw - 0.004f, top + 0.22f, z0 + g * 0.5f, side < 0);
            }
            Soffit(-hw, hw, 0f, 0f, zEnd1, zEnd1 * rise / g);
            Vector3 r0 = new Vector3(wallX - Mathf.Sign(wallX) * 0.07f, 0.9f + rise, 0f);
            var flight1 = FlightZ(0f, zEnd1, 0f, rise, s.Type == StairType.Straight ? H : landY1, sl: rise / g);
            if (walled1) Handrail(rails, r0, new Vector3(r0.x, (s.Type == StairType.Straight ? H : landY1) + 0.9f, zEnd1), wallX);
            else OpenSide(mb, glass, rails, wallX, Mathf.Sign(wallX), flight1, solid);
            // the other side of a straight or L flight (a U has the glass between its flights there)
            if (s.Type != StairType.U &&
                !Walled(m, new Vector3(-wallX, 0, 0), new Vector3(-wallX, 0, s.Type == StairType.L ? zl1 : zEnd1), Vector3.right * -Mathf.Sign(wallX), landY1 * 0.5f + 1f))
                OpenSide(mb, glass, rails, -wallX, -Mathf.Sign(wallX), s.Type == StairType.L ? FlightZ(0f, zl1, 0f, rise, landY1, rise / g) : flight1, solid);

            if (s.Type != StairType.Straight)
            {
                float landY = k * rise, zl = (k - 1) * g, depth = s.Landing ?? w;
                int rest = n - k;
                if (s.Type == StairType.U)
                {
                    float x2 = side * (w + s.Gap);           // centre of flight 2
                    float lx0 = Mathf.Min(-hw, x2 - hw), lx1 = Mathf.Max(hw, x2 + hw);
                    mb.Box(new Vector3(lx0, landY - 0.2f, zl), new Vector3(lx1, landY, zl + depth),
                        BoxMats.All(_c.M.Plaster).With(yp: _c.M.OakLight, yn: _c.M.Ceiling));
                    for (int j = 1; j < rest; j++)
                    {
                        float top = landY + j * rise, z1 = zl - (j - 1) * g;
                        TreadZ(x2 - hw, x2 + hw, z1 - g - 0.02f, z1, top);
                        float outer = x2 + side * hw;
                        if (!solid && j % 2 == 1) StepLight(lights, outer - side * 0.004f, top + 0.22f, z1 - g * 0.5f, side > 0);
                    }
                    float zt = zl - (rest - 1) * g;              // where flight 2 arrives on the upper floor
                    Soffit(x2 - hw, x2 + hw, zt, landY + (zl - zt) * rise / g, zl, landY);
                    float xm = side * (hw + s.Gap * 0.5f);         // plane between the flights
                    if (!solid)
                    {
                        GlassPanel(glass, xm, new[] { new Vector2(0f, 0f), new Vector2(zl, landY - 0.05f), new Vector2(zt, slabBottom), new Vector2(0f, slabBottom) });
                        GlassPanel(glass, xm, new[] { new Vector2(zl, landY - 0.05f), new Vector2(zl, landY + 0.95f), new Vector2(zt, H + 0.95f), new Vector2(zt, slabBottom) });
                        rails.Rod(new Vector3(xm, landY + 0.95f, zl), new Vector3(xm, H + 0.95f, zt), 0.022f, _c.M.BlackMetal, 12);
                        // guard at the top of flight 1 (between the wall and the inner edge of flight 2); with an
                        // automatic well the well guards cover this edge
                        if (s.Well != "auto" || _c.Stair(s) == null || _c.Stair(s).Well.Count == 0)
                        {
                            float guardA = Mathf.Min(side > 0 ? -hw : x2 + hw, side > 0 ? x2 - hw : hw);
                            float guardB = Mathf.Max(side > 0 ? -hw : x2 + hw, side > 0 ? x2 - hw : hw);
                            glass.Box(new Vector3(guardA, H, zt - 0.006f), new Vector3(guardB, H + 1.0f, zt + 0.006f), _c.M.Glass);
                            rails.Rod(new Vector3(guardA, H + 1.0f, zt), new Vector3(guardB, H + 1.0f, zt), 0.022f, _c.M.BlackMetal, 12);
                        }
                    }
                    // outer side of flight 2 and the free edges of the landing
                    float x2o = x2 + side * hw;
                    var flight2 = FlightZ(zl, zt, landY, rise, H, rise / g);
                    if (Walled(m, new Vector3(x2o, 0, zt), new Vector3(x2o, 0, zl), Vector3.right * side, (landY + H) * 0.5f + 1f))
                        Handrail(rails, new Vector3(x2o - side * 0.07f, landY + rise + 0.9f, zl), new Vector3(x2o - side * 0.07f, H + 0.9f, zt), x2o);
                    else OpenSide(mb, glass, rails, x2o, side, flight2, solid);
                    LandingEdges(m, mb, glass, rails, lx0, lx1, zl, zl + depth, landY, skipSide: 0f);
                }
                else // L: square landing, second flight runs sideways
                {
                    mb.Box(new Vector3(-hw, landY - 0.2f, zl), new Vector3(hw, landY, zl + depth),
                        BoxMats.All(_c.M.Plaster).With(yp: _c.M.OakLight, yn: _c.M.Ceiling));
                    float edge = side * hw;
                    for (int j = 1; j < rest; j++)
                    {
                        float top = landY + j * rise, x1 = edge + side * (j - 1) * g;
                        float xa = Mathf.Min(x1, x1 + side * (g + 0.02f)), xb = Mathf.Max(x1, x1 + side * (g + 0.02f));
                        TreadX(xa, xb, zl, zl + depth, top);
                    }
                    // flight 2 runs sideways: its sides are handled in a frame where it runs along +z'
                    var turn = m * Matrix4x4.TRS(new Vector3(edge, 0, zl + depth * 0.5f), Quaternion.Euler(0, side > 0 ? 90f : -90f, 0), Vector3.one);
                    mb.Transform = glass.Transform = rails.Transform = turn;
                    var flight2 = FlightZ(0f, (rest - 1) * g, landY, rise, H, rise / g);
                    float hd = depth * 0.5f;
                    foreach (float sx in new[] { -1f, 1f })
                        if (!Walled(turn, new Vector3(sx * hd, 0, 0), new Vector3(sx * hd, 0, flight2.Z1), Vector3.right * sx, (landY + H) * 0.5f + 1f))
                            OpenSide(mb, glass, rails, sx * hd, sx, flight2, solid);
                    mb.Transform = glass.Transform = rails.Transform = m;
                    LandingEdges(m, mb, glass, rails, -hw, hw, zl, zl + depth, landY, skipSide: side);
                }
            }

            string id = s.Id ?? "stair";
            _c.W.Emit("Stair_" + id, _c.Interior, mb);
            _c.W.Emit("Stair_Glass_" + id, _c.Interior, glass, castShadows: false);
            _c.W.Emit("Stair_Rails_" + id, _c.Interior, rails);
            _c.W.Emit("Decor_StepLights_" + id, _c.Interior, lights, castShadows: false);
        }

        /// <summary>A flight in the stair frame running along z: from (<see cref="Z0"/>, first tread top <see cref="Y0"/>) to (<see cref="Z1"/>, <see cref="Y1"/>).</summary>
        struct Flight
        {
            public float Z0, Z1, Y0, Y1;
            /// <summary>What the flight starts from: the floor (0) or the landing top.</summary>
            public float Base;
        }

        static Flight FlightZ(float z0, float z1, float baseY, float rise, float topY, float sl) =>
            new Flight { Z0 = z0, Z1 = z1, Base = baseY, Y0 = baseY + rise, Y1 = topY };

        /// <summary>
        /// Is there a solid wall (not glass) within 15 cm beyond the stair edge la→lb (stair frame <paramref name="m"/>)
        /// along most of its length, at a height <paramref name="yLocal"/> above the lower floor?
        /// </summary>
        bool Walled(Matrix4x4 m, Vector3 la, Vector3 lb, Vector3 outLocal, float yLocal)
        {
            float y = m.MultiplyPoint(new Vector3(0, yLocal, 0)).y;
            var walls = new List<WallFrame>();
            foreach (var f in _c.Walls) if (f.Def.System != WallSystem.SteelGlass && f.Spans(y)) walls.Add(f);
            var dir3 = m.MultiplyVector(outLocal);
            var dir = new Vector2(dir3.x, dir3.z).normalized;
            int hits = 0;
            foreach (float t in new[] { 0.2f, 0.5f, 0.8f })
            {
                var p3 = m.MultiplyPoint(Vector3.Lerp(la, lb, t));
                if (WallFrame.Cast(walls, new Vector2(p3.x, p3.z) + dir * 0.005f, dir, 0.15f, out _) != null) hits++;
            }
            return hits >= 2;
        }

        /// <summary>
        /// Open side of a flight at x (tread ends; <paramref name="sgn"/> points away from the treads): a black steel
        /// stringer under the tread ends (not for solid stairs) and a glass guard with a walnut handrail on top.
        /// </summary>
        void OpenSide(MeshBuilder mb, MeshBuilder glass, MeshBuilder rails, float x, float sgn, Flight f, bool solid)
        {
            const float Plate = 0.012f, Depth = 0.28f, Guard = 0.9f;
            float yA = f.Y0 + 0.03f, yB = f.Y1;
            if (!solid && Mathf.Abs(f.Z1 - f.Z0) > 0.05f)
            {
                float slope = (yB - yA) / (f.Z1 - f.Z0);
                // the plate's lower edge runs parallel to the nosing line and meets the floor/landing it starts from
                float foot = f.Base > 0.01f ? f.Base - 0.2f : 0f;
                float zf = f.Z0 + (foot - (yA - Depth)) / slope;
                var pts = new List<Vector2> { new Vector2(f.Z0, foot), new Vector2(f.Z0, yA), new Vector2(f.Z1, yB), new Vector2(f.Z1, yB - Depth) };
                if ((zf - f.Z0) * (f.Z1 - f.Z0) > 0f && Mathf.Abs(zf - f.Z0) < Mathf.Abs(f.Z1 - f.Z0)) pts.Add(new Vector2(zf, foot));
                PlateX(mb, x, x + sgn * Plate, pts, _c.M.BlackMetal);
            }
            float xg = x + sgn * (Plate + 0.02f);
            GlassPanel(glass, xg, new[] { new Vector2(f.Z0, yA), new Vector2(f.Z1, yB + 0.03f), new Vector2(f.Z1, yB + Guard), new Vector2(f.Z0, yA + Guard) });
            rails.Rod(new Vector3(xg, yA + Guard, f.Z0), new Vector3(xg, yB + Guard, f.Z1), 0.022f, _c.M.Walnut, 12);
        }

        /// <summary>
        /// Guards on the free edges of a landing (x0..x1 × z0..z1, top at y) and steel posts under its far corners
        /// when nothing carries them. The near edge (where flight 1 arrives) is skipped; <paramref name="skipSide"/>
        /// ±1 skips the side edge a sideways second flight leaves from.
        /// </summary>
        void LandingEdges(Matrix4x4 m, MeshBuilder mb, MeshBuilder glass, MeshBuilder rails, float x0, float x1, float z0, float z1, float y, float skipSide)
        {
            const float Guard = 1.0f, In = 0.02f;
            var edges = new List<(Vector3 a, Vector3 b, Vector3 o)>
            {
                (new Vector3(x0, 0, z1), new Vector3(x1, 0, z1), Vector3.forward),
            };
            if (skipSide >= 0f) edges.Add((new Vector3(x0, 0, z0), new Vector3(x0, 0, z1), Vector3.left));
            if (skipSide <= 0f) edges.Add((new Vector3(x1, 0, z0), new Vector3(x1, 0, z1), Vector3.right));
            bool farOpen = false;
            foreach (var (a, b, o) in edges)
            {
                if (Walled(m, a, b, o, y + 1f)) continue;
                if (o == Vector3.forward) farOpen = true;
                var lo = Vector3.Min(a, b) - o * In; var hi = Vector3.Max(a, b) - o * In;
                var pad = new Vector3(o.x == 0 ? 0 : 0.006f, 0, o.z == 0 ? 0 : 0.006f);
                glass.Box(new Vector3(lo.x, y, lo.z) - pad, new Vector3(hi.x, y + Guard, hi.z) + pad, _c.M.Glass);
                rails.Rod(new Vector3(lo.x, y + Guard, lo.z), new Vector3(hi.x, y + Guard, hi.z), 0.022f, _c.M.Walnut, 12);
            }
            if (!farOpen) return;
            foreach (float px in new[] { x0 + 0.06f, x1 - 0.06f })
            {
                var w = m.MultiplyPoint(new Vector3(px, 0, z1 - 0.06f));
                var p = new Vector2(w.x, w.z);
                bool carried = false;
                foreach (var f in _c.Walls) if (f.Spans(w.y + 1f) && f.DistanceTo(p) < 0.15f) { carried = true; break; }
                if (!carried) mb.Box(new Vector3(px - 0.03f, 0f, z1 - 0.09f), new Vector3(px + 0.03f, y - 0.2f, z1 - 0.03f), _c.M.BlackMetal);
            }
        }

        /// <summary>Convex plate between the planes x = xa and x = xb; outline points (z, y) in any order around it.</summary>
        static void PlateX(MeshBuilder mb, float xa, float xb, List<Vector2> zy, Material mat)
        {
            var c = Vector2.zero; foreach (var p in zy) c += p; c /= zy.Count;
            zy.Sort((p, q) => Mathf.Atan2(p.y - c.y, p.x - c.x).CompareTo(Mathf.Atan2(q.y - c.y, q.x - c.x)));
            float lo = Mathf.Min(xa, xb), hi = Mathf.Max(xa, xb);
            Vector3 P(float x, Vector2 v) => new Vector3(x, v.y, v.x);
            // same winding rule as GlassPanel: the face shows towards n
            void Tri(Vector3 a, Vector3 b, Vector3 d, Vector3 n)
            {
                Vector2 U(Vector3 v) => Mathf.Abs(n.x) > 0.5f ? new Vector2(v.z, v.y) : new Vector2(v.x + v.z, v.y);
                if (Vector3.Dot(Vector3.Cross(b - a, d - a), n) > 0) mb.Triangle(a, b, d, n, n, n, U(a), U(b), U(d), mat);
                else mb.Triangle(a, d, b, n, n, n, U(a), U(d), U(b), mat);
            }
            for (int i = 1; i + 1 < zy.Count; i++)
            {
                Tri(P(hi, zy[0]), P(hi, zy[i]), P(hi, zy[i + 1]), Vector3.right);
                Tri(P(lo, zy[0]), P(lo, zy[i]), P(lo, zy[i + 1]), Vector3.left);
            }
            for (int i = 0; i < zy.Count; i++)
            {
                Vector2 a = zy[i], b = zy[(i + 1) % zy.Count], e = b - a;
                if (e.sqrMagnitude < 1e-8f) continue;
                // outward normal of the edge in the (z, y) plane
                var mid = (a + b) * 0.5f - c;
                var n2 = new Vector2(e.y, -e.x);
                if (Vector2.Dot(n2, mid) < 0) n2 = -n2;
                var n = new Vector3(0, n2.y, n2.x).normalized;
                Tri(P(lo, a), P(lo, b), P(hi, b), n);
                Tri(P(lo, a), P(hi, b), P(hi, a), n);
            }
        }

        /// <summary>Wall-mounted walnut handrail with black brackets towards the wall at <paramref name="wallX"/>.</summary>
        void Handrail(MeshBuilder mb, Vector3 a, Vector3 b, float wallX)
        {
            mb.Rod(a, b, 0.022f, _c.M.Walnut, 12);
            var toWall = Vector3.right * Mathf.Sign(wallX) * 0.07f;
            for (int i = 0; i <= 3; i++)
            {
                Vector3 p = Vector3.Lerp(a, b, 0.1f + i * 0.27f);
                mb.Rod(p, p + toWall, 0.008f, _c.M.BlackMetal);
            }
        }

        void StepLight(MeshBuilder mb, float x, float y, float z, bool facingNegX)
        {
            float d = facingNegX ? -0.006f : 0.006f;
            Vector3 a = new Vector3(x, y - 0.025f, z - 0.09f), b = new Vector3(x + d, y + 0.025f, z + 0.09f);
            mb.Box(Vector3.Min(a, b), Vector3.Max(a, b), BoxMats.All(_c.M.BlackMetal).With(yn: _c.M.Led));
        }

        /// <summary>Glass polygon in the plane x = const; points (z, y) counter-clockwise, convex.</summary>
        void GlassPanel(MeshBuilder mb, float x, Vector2[] zy)
        {
            const float h = 0.006f;
            for (int side = -1; side <= 1; side += 2)
            {
                Vector3 n = Vector3.right * side;
                Vector3 P(int i) => new Vector3(x + side * h, zy[i].y, zy[i].x);
                for (int i = 1; i + 1 < zy.Length; i++)
                {
                    Vector3 a = P(0), b = P(i), c = P(i + 1);
                    Vector2 ua = new Vector2(a.z, a.y), ub = new Vector2(b.z, b.y), uc = new Vector2(c.z, c.y);
                    if (Vector3.Dot(Vector3.Cross(b - a, c - a), n) > 0) mb.Triangle(a, b, c, n, n, n, ua, ub, uc, _c.M.Glass);
                    else mb.Triangle(a, c, b, n, n, n, ua, uc, ub, _c.M.Glass);
                }
            }
        }
    }
}
