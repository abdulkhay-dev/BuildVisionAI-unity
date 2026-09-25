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
            }
            var root = new GameObject("Landscape");
            var ground = new MeshBuilder();
            ground.Box(new Vector3(-900, -0.3f, -900), new Vector3(900, 0f, 900), BoxMats.All(null).With(yp: _c.Lib.Lawn));
            _c.W.Emit("Lawn", root.transform, ground, castShadows: false, probeStatic: true);
            if (_c.Doc.Site.Landscape == LandscapePreset.Lawn) return root;

            // gravel apron and a path of slabs from the front (-Z) side
            var gravel = new MeshBuilder();
            var top = BoxMats.All(_c.Lib.Gravel).Without(yn: true);
            const float apron = 0.8f, gy = 0.022f;
            var r = footprint;
            gravel.Box(new Vector3(r.xMin - apron, 0, r.yMin - apron), new Vector3(r.xMax + apron, gy, r.yMax + apron), top);
            _c.W.Emit("Gravel", root.transform, gravel, castShadows: false, probeStatic: true);
            var slabs = new MeshBuilder();
            var slab = BoxMats.All(_c.Lib.Paver).Without(yn: true);
            float px = r.center.x;
            for (float z = r.yMin - apron - 0.2f; z > r.yMin - 14f; z -= 0.92f)
                slabs.Box(new Vector3(px - 0.67f, 0, z - 0.62f), new Vector3(px + 0.67f, 0.05f, z), slab);
            _c.W.Emit("Path_Slabs", root.transform, slabs, castShadows: false, probeStatic: true);

            Trees(root.transform, r);
            return root;
        }

        void Trees(Transform root, Rect house)
        {
            var veg = _c.Veg;
            var g = _c.W.Group("Trees", root);
            var spruce = new[] { veg.Spruce(11f, 1), veg.Spruce(14f, 2), veg.Spruce(9f, 3) };
            var birch = new[] { veg.Birch(10f, 4), veg.Birch(12f, 5) };
            var spruceMeshes = new Mesh[spruce.Length];
            var birchMeshes = new Mesh[birch.Length];
            for (int i = 0; i < spruce.Length; i++) spruceMeshes[i] = _c.W.Store(spruce[i].Build("Spruce_" + i));
            for (int i = 0; i < birch.Length; i++) birchMeshes[i] = _c.W.Store(birch[i].Build("Birch_" + i));

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
                var go = isBirch
                    ? _c.W.Instance("Birch", g, birchMeshes[idx], birch[idx].Materials, true, true)
                    : _c.W.Instance("Spruce", g, spruceMeshes[idx], spruce[idx].Materials, true, true);
                go.transform.position = new Vector3(p.x, 0, p.y);
                go.transform.rotation = Quaternion.Euler(0, rng.Range(0f, 360f), 0);
                float s = rng.Range(0.85f, 1.2f);
                go.transform.localScale = Vector3.one * s;
            }
        }
    }
}
