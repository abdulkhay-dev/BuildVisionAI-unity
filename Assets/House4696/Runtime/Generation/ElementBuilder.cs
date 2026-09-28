using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Architectural elements: boxes (belts, canopies, parapets, beams, columns, terraces and steps) with separate
    /// top/underside materials and an optional coping cap, and railings (frameless glass or metal bars) along a path.
    /// </summary>
    public sealed class ElementBuilder
    {
        readonly HouseContext _c;
        public ElementBuilder(HouseContext c) { _c = c; }

        public void Build(ElementDef e)
        {
            string id = e.Id ?? e.Type.ToString().ToLowerInvariant();
            string prefix = e.Collide ? "Element_" : "Decor_Element_";
            if (e.Type == ElementType.Railing) { Railing(e, prefix + id); return; }
            if (e.Type == ElementType.Pool) { new PoolBuilder(_c).Build(e, "Pool_" + id); return; }

            var mb = new MeshBuilder();
            var capMb = new MeshBuilder();
            var def = e.Type == ElementType.Column ? _c.Lib.Stone : _c.Lib.Stucco;
            var side = _c.Mats.Get(e.Material, def);
            Material Face(string name, Material fallback) => name == "none" ? null : _c.Mats.Get(name, fallback);
            bool capped = !string.IsNullOrEmpty(e.Cap) && e.Cap != "none";
            var top = e.Top != null ? Face(e.Top, side) : capped ? null : side;
            var bottom = Face(e.Bottom, side);
            Vector3 mn = Vector3.Min(e.Min, e.Max), mx = Vector3.Max(e.Min, e.Max);
            // a pool sunk into a deck/terrace cuts its basin out of it
            var cuts = e.Type == ElementType.Column ? null : _c.PoolCuts(mx.y);
            var rect = new List<Vector2> { new Vector2(mn.x, mn.z), new Vector2(mx.x, mn.z), new Vector2(mx.x, mx.z), new Vector2(mn.x, mx.z) };
            if (cuts != null && cuts.Exists(h => Polygon.BoundsOverlap(rect, h)))
                Polygon.Prism(mb, rect, cuts, mn.y, mx.y, top, bottom, side);
            else
                mb.Box(mn, mx, new BoxMats { XNeg = side, XPos = side, ZNeg = side, ZPos = side, YPos = top, YNeg = bottom });
            if (capped)
            {
                float o = e.CapOverhang;
                capMb.Box(new Vector3(mn.x - o, mx.y, mn.z - o), new Vector3(mx.x + o, mx.y + e.CapHeight, mx.z + o),
                    BoxMats.All(_c.Mats.Get(e.Cap, _c.Lib.Coping)).Without(yn: true));
            }
            _c.W.Emit(prefix + id, _c.Shell, mb);
            _c.W.Emit(prefix + id + "_Cap", _c.Shell, capMb);
        }

        /// <summary>Glass: panels of ~1.15 m between a base shoe and a top cap; metal: top rail, bottom rail and balusters.</summary>
        void Railing(ElementDef e, string name)
        {
            if (e.Path == null || e.Path.Count < 2) { _c.Warn($"railing '{e.Id}' needs a path of 2+ points"); return; }
            var glass = new MeshBuilder();
            var metal = new MeshBuilder();
            bool isGlass = e.Style != "metal";
            bool sheet = e.Style == "glass_oak";             // one continuous sheet with an oak handrail on top
            float y = e.Y, gy0 = y + 0.04f, gy1 = y + e.Height;
            const float gt = 0.012f;
            var frame = _c.Mats.Get(e.Material, _c.Lib.Frame);
            for (int i = 0; i + 1 < e.Path.Count; i++)
            {
                Vector2 a = e.Path[i], b = e.Path[i + 1];
                var d = b - a; float len = d.magnitude;
                if (len < 1e-3f) continue;
                d /= len;
                var n = new Vector3(d.y, 0, -d.x);
                var m = Matrix4x4.TRS(new Vector3(a.x, 0, a.y), Quaternion.LookRotation(-n, Vector3.up), Vector3.one);
                glass.Transform = m; metal.Transform = m;
                if (sheet)
                {
                    glass.Box(new Vector3(0, y + 0.004f, -0.006f), new Vector3(len, gy1 - 0.02f, 0.006f), BoxMats.All(_c.M.Glass));
                    metal.Box(new Vector3(0, y + 0.004f, -0.0175f), new Vector3(len, y + 0.05f, 0.0175f), BoxMats.All(_c.M.BlackMetal));
                    metal.Rod(new Vector3(0, gy1, 0), new Vector3(len, gy1, 0), 0.022f, _c.M.OakLight, 12);
                }
                else if (isGlass)
                {
                    int panels = Mathf.Max(1, Mathf.RoundToInt(len / 1.15f));
                    for (int p = 0; p < panels; p++)
                    {
                        float s0 = len * p / panels + 0.005f, s1 = len * (p + 1) / panels - 0.005f;
                        glass.Box(new Vector3(s0, gy0, -gt * 0.5f), new Vector3(s1, gy1, gt * 0.5f), BoxMats.All(_c.Lib.GlassRailing));
                    }
                    const float pa = 0.012f, pc = 0.022f;
                    metal.Box(new Vector3(-pa, gy1 - 0.01f, -pc), new Vector3(len + pa, gy1 + 0.03f, pc), BoxMats.All(frame));
                    metal.Box(new Vector3(-pa * 1.5f, y, -pc * 1.6f), new Vector3(len + pa * 1.5f, gy0 + 0.02f, pc * 1.6f), BoxMats.All(frame));
                }
                else
                {
                    metal.Box(new Vector3(0, gy1 - 0.04f, -0.025f), new Vector3(len, gy1, 0.025f), BoxMats.All(frame));
                    metal.Box(new Vector3(0, y + 0.08f, -0.012f), new Vector3(len, y + 0.11f, 0.012f), BoxMats.All(frame));
                    int bars = Mathf.Max(2, Mathf.CeilToInt(len / 0.11f));
                    for (int k = 0; k <= bars; k++)
                    {
                        float s = len * k / bars;
                        metal.Box(new Vector3(s - 0.008f, y, -0.008f), new Vector3(s + 0.008f, gy1 - 0.04f, 0.008f), BoxMats.All(frame));
                    }
                }
            }
            _c.W.Emit(name.Replace("Element_", "Railing_Glass_"), _c.Shell, glass, castShadows: false);
            _c.W.Emit(name.Replace("Element_", "Railing_"), _c.Shell, metal);
        }
    }
}
