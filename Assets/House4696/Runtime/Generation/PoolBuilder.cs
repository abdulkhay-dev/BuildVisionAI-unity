using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Resolved plan and heights of a pool element: a convex counter-clockwise outline (the inner face of the basin),
    /// the rim (top of the coping) and the floor. The builder, the cut-outs in the ground/decks/floors, the checks and
    /// the inspector all read the pool through this.
    /// </summary>
    public sealed class PoolShape
    {
        public ElementDef Def;
        public List<Vector2> Outline;
        public float Top, Floor;
        public readonly HashSet<int> GlassEdges = new HashSet<int>();

        public const float Coping = 0.3f;       // stone band around the water
        public const float Freeboard = 0.08f;   // rim → water (skimmer pool); overflow pools brim over
        public float Water => Top - (Def.Style == "overflow" ? 0.012f : Freeboard);

        /// <summary>Null (and a Russian error) when the element does not describe a pool.</summary>
        public static PoolShape From(ElementDef e, out string error)
        {
            error = null;
            var s = new PoolShape { Def = e };
            if (e.Path != null && e.Path.Count >= 3)
            {
                s.Outline = Polygon.CounterClockwise(e.Path);
                s.Top = e.Y;
                s.Floor = e.Y - e.Height;
            }
            else
            {
                Vector3 mn = Vector3.Min(e.Min, e.Max), mx = Vector3.Max(e.Min, e.Max);
                s.Outline = new List<Vector2> { new Vector2(mn.x, mn.z), new Vector2(mx.x, mn.z), new Vector2(mx.x, mx.z), new Vector2(mn.x, mx.z) };
                s.Top = mx.y;
                s.Floor = mn.y;
            }
            var b = Polygon.Bounds(s.Outline);
            if (b.width < 1f || b.height < 1f) { error = "бассейн меньше 1 м по стороне: задай min/max (или path) по внутренней грани чаши"; return null; }
            float depth = s.Top - s.Floor;
            if (depth < 0.3f || depth > 4f) { error = $"глубина бассейна {depth:0.##} м: min.y — дно, max.y — борт (обычно 1.2–1.6 м)"; return null; }
            if (!Convex(s.Outline)) { error = "контур бассейна должен быть выпуклым (прямоугольник, трапеция…); Г-образный — два бассейна встык"; return null; }
            foreach (var g in e.Glass ?? new List<string>())
            {
                var idx = s.EdgesOf(g);
                if (idx.Count == 0) { error = $"glass: '{g}' — нужна сторона north/east/south/west или номер ребра 0…{s.Outline.Count - 1}"; return null; }
                foreach (int i in idx) s.GlassEdges.Add(i);
            }
            return s;
        }

        /// <summary>Edges named by a compass side (outward normal within 45°) or an index of the outline.</summary>
        public List<int> EdgesOf(string side)
        {
            var list = new List<int>();
            if (int.TryParse(side, out int k)) { if (k >= 0 && k < Outline.Count) list.Add(k); return list; }
            Vector2 dir;
            switch ((side ?? "").ToLowerInvariant())
            {
                case "north": case "n": case "север": dir = Vector2.up; break;
                case "south": case "s": case "юг": dir = Vector2.down; break;
                case "east": case "e": case "восток": dir = Vector2.right; break;
                case "west": case "w": case "запад": dir = Vector2.left; break;
                default: return list;
            }
            for (int i = 0; i < Outline.Count; i++)
                if (Vector2.Dot(Outward(i), dir) > 0.7f) list.Add(i);
            return list;
        }

        public Vector2 Outward(int i)
        {
            var d = (Outline[(i + 1) % Outline.Count] - Outline[i]).normalized;
            return new Vector2(d.y, -d.x);
        }

        /// <summary>Plan area cut out of solids around the basin: the basin plus its walls (only the pane on glass sides).</summary>
        public Vector2[] Cut => Grown(PoolBuilder.Wall, PoolBuilder.Pane + 0.005f).ToArray();   // clears a deck edge flush with the glass

        /// <summary>The outline grown by <paramref name="solid"/> on masonry sides and <paramref name="glass"/> on glass sides.</summary>
        public List<Vector2> Grown(float solid, float glass)
        {
            var d = new float[Outline.Count];
            for (int i = 0; i < d.Length; i++) d[i] = GlassEdges.Contains(i) ? glass : solid;
            return OffsetEdges(Outline, d);
        }

        /// <summary>Convex CCW polygon with each edge i moved outward by d[i] (neighbouring offset lines intersected).</summary>
        public static List<Vector2> OffsetEdges(IList<Vector2> p, float[] d)
        {
            int n = p.Count;
            var res = new List<Vector2>(n);
            for (int i = 0; i < n; i++)
            {
                int h = (i + n - 1) % n;
                Vector2 a0 = p[h], a1 = p[i], b0 = p[i], b1 = p[(i + 1) % n];
                Vector2 da = (a1 - a0).normalized, db = (b1 - b0).normalized;
                Vector2 na = new Vector2(da.y, -da.x), nb = new Vector2(db.y, -db.x);
                Vector2 pa = a1 + na * d[h], pb = b0 + nb * d[i];
                float den = da.x * db.y - da.y * db.x;
                if (Mathf.Abs(den) < 1e-5f) { res.Add(pb); continue; }
                float t = ((pb.x - pa.x) * db.y - (pb.y - pa.y) * db.x) / den;
                res.Add(pa + da * t);
            }
            return res;
        }

        /// <summary>Does a solid whose top is at <paramref name="y"/> lie within the basin's height (so the basin must cut it)?</summary>
        public bool Cuts(float y) => y > Floor + 0.01f && y <= Top + 0.05f;

        public bool Contains(Vector2 p) => Polygon.Contains(Outline, p);

        static bool Convex(IList<Vector2> p)
        {
            for (int i = 0; i < p.Count; i++)
            {
                Vector2 a = p[i], b = p[(i + 1) % p.Count], c = p[(i + 2) % p.Count];
                float cross = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x);
                if (cross < -1e-4f) return false;
            }
            return true;
        }
    }

    /// <summary>
    /// Swimming pool: a basin lined with mosaic (floor and walls), a water surface a few centimetres under the coping
    /// (brimming for <c>style: overflow</c>), a stone coping band around it, glass sides where asked (with a sheet of
    /// water behind the glass so the side reads as water, not air) and plain outer walls/underside wherever the basin
    /// stands above what surrounds it. The ground, decks and room floors it sinks into are cut by their builders
    /// (<see cref="HouseContext.PoolCuts"/>).
    /// </summary>
    public sealed class PoolBuilder
    {
        public const float Wall = 0.2f;          // basin wall thickness (outside the lining)
        public const float Pane = 0.04f;         // glass side thickness
        readonly HouseContext _c;
        public PoolBuilder(HouseContext c) { _c = c; }

        public void Build(ElementDef e, string name)
        {
            var s = PoolShape.From(e, out var error);
            if (s == null) { _c.Warn($"pool '{e.Id}': {error}"); return; }
            var o = s.Outline;
            float top = s.Top, floor = s.Floor, water = s.Water;
            var lining = _c.Mats.Get(e.Material ?? DefaultLining, _c.Lib.Porcelain);
            var coping = _c.Mats.Get(e.Top ?? DefaultCoping, _c.Lib.Paver);
            var outside = _c.Mats.Get(e.Outside, _c.Lib.Stucco);

            var basin = new MeshBuilder();
            var shell = new MeshBuilder();
            var glass = new MeshBuilder();
            var cap = new MeshBuilder();
            const float capTop = 0.02f, capT = 0.05f;   // coping 2 cm proud of the rim level, 5 cm thick

            // floor and walls of the lining (faces look into the basin)
            Polygon.Prism(basin, o, floor - 0.02f, floor, lining, null, null);
            for (int i = 0; i < o.Count; i++)
            {
                if (s.GlassEdges.Contains(i)) continue;
                Vector2 a = o[i], b = o[(i + 1) % o.Count];
                Face(basin, b, a, floor, top - capT + capTop, lining);
            }
            // basin shell: walls and underside, visible only where the pool stands above the ground or a deck
            var outer = s.Grown(Wall, Pane);
            Polygon.Prism(shell, outer, floor - 0.25f, floor - 0.02f, null, outside, null);
            for (int i = 0; i < o.Count; i++)
            {
                if (s.GlassEdges.Contains(i)) continue;
                Face(shell, outer[i], outer[(i + 1) % o.Count], floor - 0.25f, top - capT + capTop, outside);
            }
            // glass sides: a pane on the lining line (it replaces that wall), running on over the neighbouring walls'
            // ends, whose end faces close the corners behind it; a water sheet just inside so the side reads as water
            var waterMat = WaterMaterial(e.Water);
            var sheets = new MeshBuilder();
            foreach (int i in s.GlassEdges)
            {
                Vector2 a = o[i], b = o[(i + 1) % o.Count], n = s.Outward(i), d = (b - a).normalized;
                Vector2 ga = a - d * Wall, gb = b + d * Wall;
                Polygon.Prism(glass, new List<Vector2> { ga, gb, gb + n * Pane, ga + n * Pane }, floor - 0.25f, top - capT + capTop, _c.M.Glass, _c.M.Glass, _c.M.Glass);
                Face(shell, ga, a, floor - 0.25f, top - capT + capTop, outside);
                Face(shell, b, gb, floor - 0.25f, top - capT + capTop, outside);
                Face(sheets, a - n * 0.005f, b - n * 0.005f, floor, water, waterMat);
            }
            // coping ring: overhangs the water by 2 cm and covers the cut edge of the deck/ground around the basin
            // (flush with the pane on glass sides)
            Polygon.Prism(cap, s.Grown(PoolShape.Coping, Pane), new[] { RoofBuilder.Offset(o, -0.02f).ToArray() },
                top - capT + capTop, top + capTop, coping, coping, coping);

            // water surface (UV in metres / 3 for the ripple normal)
            var surf = new MeshBuilder();
            var tris = Polygon.Triangulate(o);
            for (int t = 0; t < tris.Count; t += 3)
            {
                Vector3 P(int k) => new Vector3(o[tris[t + k]].x, water, o[tris[t + k]].y);
                Vector2 U(Vector3 p) => new Vector2(p.x, p.z);
                Vector3 a = P(0), b = P(1), c2 = P(2);
                surf.Triangle(a, c2, b, Vector3.up, Vector3.up, Vector3.up, U(a), U(c2), U(b), waterMat);
            }

            _c.W.Emit(name + "_Basin", _c.Shell, basin);
            _c.W.Emit(name + "_Shell", _c.Shell, shell);
            _c.W.Emit(name + "_Coping", _c.Shell, cap);
            _c.W.Emit("Decor_" + name + "_Glass", _c.Shell, glass, castShadows: false);
            _c.W.Emit("Decor_" + name + "_WaterSide", _c.Shell, sheets, castShadows: false);
            // the water surface keeps a collider: walking over the pool beats falling in and being stuck
            var go = _c.W.Emit(name + "_Water", _c.Shell, surf, castShadows: false);
            // gentle ripples; the flow component owns (and destroys) this pool's water material
            if (go != null && waterMat != _c.M.Glass)
            {
                var flow = go.AddComponent<House4696.Landscape.Natural.WaterFlow>();
                flow.Pools = waterMat; flow.PoolSpeed = 0.015f;
            }
        }

        public const string DefaultLining = "tiles_mosaic_wall#8fd0ee", DefaultCoping = "travertine_tiles";

        /// <summary>Vertical quad from a to b (plan), facing right of a→b, between heights y0 and y1.</summary>
        static void Face(MeshBuilder mb, Vector2 a, Vector2 b, float y0, float y1, Material m)
        {
            var d = b - a; float len = d.magnitude;
            if (len < 1e-4f || m == null) return;
            var n = new Vector3(d.y, 0, -d.x) / len;
            Vector3 A = new Vector3(a.x, y0, a.y), B = new Vector3(b.x, y0, b.y), up = Vector3.up * (y1 - y0);
            float s0 = a.x + a.y;
            mb.Quad(A, B, B + up, A + up, n, new Vector2(s0, y0), new Vector2(s0 + len, y0), new Vector2(s0 + len, y1), new Vector2(s0, y1), m);
        }

        /// <summary>Clear pool water: a copy of the stream water (transparent URP Lit with a ripple normal), tinted.</summary>
        Material WaterMaterial(string hex)
        {
            var src = LandscapeKit.Load()?.WaterMaterial;
            if (src == null) return _c.M.Glass;
            var m = new Material(src) { name = "M_PoolWater" };
            var col = new Color(0.36f, 0.74f, 0.80f, 0.42f);
            if (hex != null && ColorUtility.TryParseHtmlString(hex, out var c)) col = new Color(c.r, c.g, c.b, col.a);
            m.SetColor("_BaseColor", col);
            m.SetFloat("_Smoothness", 0.94f);
            m.SetFloat("_BumpScale", 0.3f);
            m.mainTextureScale = new Vector2(0.6f, 0.6f);
            return m;
        }
    }
}
