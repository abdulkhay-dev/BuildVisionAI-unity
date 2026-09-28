using System.Collections.Generic;
using House4696.Core;
using House4696.Landscape;
using House4696.Model;
using House4696.Setup;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Surroundings of a generated house. <c>catalog4696</c> is the hand-placed garden of project 46-96;
    /// <c>garden</c> fits any house: lawn, a gravel apron around the footprint, a paved path to the entrance
    /// side and a loose ring of spruces and birches; <c>lawn</c> is the ground only.
    /// </summary>
    public sealed class SiteBuilder
    {
        readonly HouseContext _c;
        public SiteBuilder(HouseContext c) { _c = c; }

        public GameObject Build(Rect footprint)
        {
            switch (_c.Doc.Site.Landscape)
            {
                case LandscapePreset.None: return null;
                case LandscapePreset.Catalog4696:
                    return new LandscapeGenerator(_c.Lib, _c.W, CameraSpec.Position, CameraSpec.Forward).Build();
                case LandscapePreset.Natural:
                    return new House4696.Landscape.Natural.NaturalSiteBuilder(_c.Doc.Site, LandscapeKit.Load(), _c.W, _c.Veg, _c.Lib, _c.Mats, _c.Warnings)
                        { Holes = _c.PoolCuts(0f) }.Build(footprint);
            }
            var root = new GameObject("Landscape");
            var ground = new MeshBuilder();
            // pools dug into the ground cut it (and the gravel apron)
            var pools = _c.PoolCuts(0f);
            Polygon.Prism(ground, new[] { new Vector2(-900, -900), new Vector2(900, -900), new Vector2(900, 900), new Vector2(-900, 900) },
                pools, -0.3f, 0f, _c.Lib.Lawn, null, null);
            _c.W.Emit("Lawn", root.transform, ground, castShadows: false, probeStatic: true);
            if (_c.Doc.Site.Landscape == LandscapePreset.Lawn) return root;

            // gravel apron and a path of slabs from the front (-Z) side
            var gravel = new MeshBuilder();
            var top = BoxMats.All(_c.Lib.Gravel).Without(yn: true);
            const float apron = 0.8f, gy = 0.022f;
            var r = footprint;
            var apronRect = new[] { new Vector2(r.xMin - apron, r.yMin - apron), new Vector2(r.xMax + apron, r.yMin - apron), new Vector2(r.xMax + apron, r.yMax + apron), new Vector2(r.xMin - apron, r.yMax + apron) };
            Polygon.Prism(gravel, apronRect, pools, 0f, gy, _c.Lib.Gravel, null, _c.Lib.Gravel);
            _c.W.Emit("Gravel", root.transform, gravel, castShadows: false, probeStatic: true);
            var site = _c.Doc.Site;
            if (site.Path != "none")
            {
                var slabs = new MeshBuilder();
                var slab = BoxMats.All(_c.Lib.Paver).Without(yn: true);
                float px = r.center.x;
                for (float z = r.yMin - apron - 0.2f; z > r.yMin - 14f; z -= 0.92f)
                    slabs.Box(new Vector3(px - 0.67f, 0, z - 0.62f), new Vector3(px + 0.67f, 0.05f, z), slab);
                _c.W.Emit("Path_Slabs", root.transform, slabs, castShadows: false, probeStatic: true);
            }

            if (site.Trees != "none") Trees(root.transform, r);
            return root;
        }

        void Trees(Transform root, Rect house)
        {
            var veg = _c.Veg;
            var g = _c.W.Group("Trees", root);
            bool lod = GardenPerf.TreeLod;
            float[] spruceH = { 11f, 14f, 9f }; int[] spruceSeed = { 1, 2, 3 };
            float[] birchH = { 10f, 12f }; int[] birchSeed = { 4, 5 };
            var spruce = new TreeProto[spruceH.Length];
            var birch = new TreeProto[birchH.Length];
            for (int i = 0; i < spruce.Length; i++)
                spruce[i] = new TreeProto(_c.W, "Spruce_" + i, veg.Spruce(spruceH[i], spruceSeed[i]), lod ? veg.Spruce(spruceH[i], spruceSeed[i], 1) : null);
            for (int i = 0; i < birch.Length; i++)
                birch[i] = new TreeProto(_c.W, "Birch_" + i, veg.Birch(birchH[i], birchSeed[i]), lod ? veg.Birch(birchH[i], birchSeed[i], 1) : null);

            var rng = new Rng(4696);
            float radius = Mathf.Max(house.width, house.height) * 0.5f;
            var c = house.center;
            var placed = new List<Vector2>();
            for (int i = 0; i < 40; i++)
            {
                float a = rng.Range(0f, Mathf.PI * 2f);
                // keep the front (-Z) view open: fewer trees in a 100° sector in front of the house
                float deg = Mathf.Repeat(a * Mathf.Rad2Deg, 360f);
                if (deg > 220f && deg < 320f && rng.Value() < 0.8f) continue;
                float dist = radius + rng.Range(9f, 26f);
                var p = c + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * dist;
                if (placed.Exists(q => (q - p).sqrMagnitude < 16f)) continue;
                placed.Add(p);
                bool isBirch = rng.Value() < 0.35f;
                int idx = isBirch ? rng.Range(0, birch.Length) : rng.Range(0, spruce.Length);
                // same random draws in the same order as before: rotation, then scale
                var rot = Quaternion.Euler(0, rng.Range(0f, 360f), 0);
                float s = rng.Range(0.85f, 1.2f);
                GardenLod.Tree(_c.W, isBirch ? "Birch" : "Spruce", g, isBirch ? birch[idx] : spruce[idx], new Vector3(p.x, 0, p.y), rot, s);
            }
        }
    }
}
