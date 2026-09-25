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

            void TreadZ(float x0, float x1, float z0, float z1, float top)
            {
                float y0 = solid ? 0f : top - Tread;
                mb.Box(new Vector3(x0, y0, z0), new Vector3(x1, top, z1), treadMats);
            }
            void TreadX(float x0, float x1, float z0, float z1, float top) => TreadZ(x0, x1, z0, z1, top);

            int k = s.Type == StairType.Straight ? n : Mathf.Clamp(s.FirstFlight ?? n / 2 + 1, 2, n - 2);
            // flight 1 (the last riser of a straight stair lands on the upper floor)
            for (int i = 1; i < k; i++)
            {
                float top = i * rise, z0 = (i - 1) * g;
                TreadZ(-hw, hw, z0, z0 + g + 0.02f, top);
                if (!solid && i % 2 == 1) StepLight(lights, side > 0 ? -hw + 0.004f : hw - 0.004f, top + 0.22f, z0 + g * 0.5f, side < 0);
            }
            float wallX = side > 0 ? -hw : hw;           // flight 1 runs along a wall on the outer side
            Vector3 r0 = new Vector3(wallX - Mathf.Sign(wallX) * 0.07f, 0.9f + rise, 0f);

            if (s.Type == StairType.Straight)
            {
                Vector3 r1 = new Vector3(r0.x, H + 0.9f, (n - 1) * g);
                Handrail(rails, r0, r1, wallX);
            }
            else
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
                    float xm = side * (hw + s.Gap * 0.5f);         // plane between the flights
                    if (!solid)
                    {
                        GlassPanel(glass, xm, new[] { new Vector2(0f, 0f), new Vector2(zl, landY - 0.05f), new Vector2(zt, slabBottom), new Vector2(0f, slabBottom) });
                        GlassPanel(glass, xm, new[] { new Vector2(zl, landY - 0.05f), new Vector2(zl, landY + 0.95f), new Vector2(zt, H + 0.95f), new Vector2(zt, slabBottom) });
                        // guard at the top of flight 1 (between the wall and the inner edge of flight 2)
                        float guardA = Mathf.Min(side > 0 ? -hw : x2 + hw, side > 0 ? x2 - hw : hw);
                        float guardB = Mathf.Max(side > 0 ? -hw : x2 + hw, side > 0 ? x2 - hw : hw);
                        glass.Box(new Vector3(guardA, H, zt - 0.006f), new Vector3(guardB, H + 1.0f, zt + 0.006f), _c.M.Glass);
                        rails.Rod(new Vector3(xm, landY + 0.95f, zl), new Vector3(xm, H + 0.95f, zt), 0.022f, _c.M.BlackMetal, 12);
                        rails.Rod(new Vector3(guardA, H + 1.0f, zt), new Vector3(guardB, H + 1.0f, zt), 0.022f, _c.M.BlackMetal, 12);
                    }
                    Handrail(rails, r0, new Vector3(r0.x, landY + 0.9f, zl), wallX);
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
                    Handrail(rails, r0, new Vector3(r0.x, landY + 0.9f, zl), wallX);
                }
            }

            string id = s.Id ?? "stair";
            _c.W.Emit("Stair_" + id, _c.Interior, mb);
            _c.W.Emit("Stair_Glass_" + id, _c.Interior, glass, castShadows: false);
            _c.W.Emit("Stair_Rails_" + id, _c.Interior, rails);
            _c.W.Emit("Decor_StepLights_" + id, _c.Interior, lights, castShadows: false);
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
