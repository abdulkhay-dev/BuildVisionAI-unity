using System.Collections.Generic;
using House4696.Core;
using House4696.House;
using UnityEngine;

namespace House4696.Landscape
{
    /// <summary>
    /// Garden around the house as seen in the reference render: lawn, white gravel bands, large concrete
    /// stepping slabs, clipped boxwood hedges, a steel-edged bed with grasses / dwarf pines / boulder,
    /// timber bollards, porch planters and the spruce / birch backdrop.
    /// Positions of reference features were back-projected through the calibrated camera.
    /// </summary>
    public sealed class LandscapeGenerator
    {
        readonly MaterialLibrary _m;
        readonly SceneWriter _w;
        readonly VegetationFactory _veg;
        readonly Vector3 _cameraPos;
        readonly Vector3 _cameraFwd;
        Transform _root;
        readonly List<(Vector2 p, float r)> _keepOut = new List<(Vector2, float)>();

        public LandscapeGenerator(MaterialLibrary m, SceneWriter w, Vector3 cameraPos, Vector3 cameraForward)
        {
            _m = m; _w = w; _veg = new VegetationFactory(m);
            _cameraPos = cameraPos; _cameraFwd = new Vector3(cameraForward.x, 0, cameraForward.z).normalized;
        }

        public GameObject Build()
        {
            var root = new GameObject("Landscape");
            _root = root.transform;
            Ground();
            Hardscape();
            Hedges();
            BedAndForegroundPlants();
            PorchPlanters();
            Bollards();
            Trees();
            LawnBlades();
            return root;
        }

        // ------------------------------------------------------------------ ground
        void Ground()
        {
            var mb = new MeshBuilder();
            mb.Box(new Vector3(-900, -0.3f, -900), new Vector3(900, 0f, 900), BoxMats.All(null).With(yp: _m.Lawn));
            _w.Emit("Lawn", _root, mb, castShadows: false, probeStatic: true);
        }

        // ------------------------------------------------------------------ gravel, slabs, edging, bed
        void Hardscape()
        {
            var gravel = new MeshBuilder();
            var top = BoxMats.All(_m.Gravel).Without(yn: true);
            const float gy = 0.022f;
            gravel.Box(new Vector3(-1.4f, 0, -3.35f), new Vector3(26f, gy, 0f), top);            // front band incl. path bed
            gravel.Box(new Vector3(-1.0f, 0, 0f), new Vector3(0f, gy, 10.9f), top);             // left side
            gravel.Box(new Vector3(HouseSpec.Width, 0, 0f), new Vector3(15.6f, gy, 10.9f), top); // right side
            gravel.Box(new Vector3(-1.0f, 0, 10.35f), new Vector3(15.6f, gy, 12.1f), top);      // rear
            gravel.Box(new Vector3(1.7f, 0, -19f), new Vector3(3.8f, gy, -3.35f), top);          // strip of the entrance walk
            _w.Emit("Gravel", _root, gravel, castShadows: false, probeStatic: true);

            var slabs = new MeshBuilder();
            var slab = BoxMats.All(_m.Paver).Without(yn: true);
            // stepping slabs parallel to the facade
            float x = -12f;
            var rng = new Rng(21);
            while (x < 25f)
            {
                float len = 1.45f + rng.Range(-0.05f, 0.05f);
                slabs.Box(new Vector3(x, 0, -3.18f), new Vector3(x + len, 0.05f, -2.02f), slab);
                x += len + 0.14f;
            }
            // entrance walk towards the viewer: slabs across the walk
            for (float z = -3.9f; z > -19f; z -= 0.92f)
                slabs.Box(new Vector3(2.08f, 0, z - 0.62f), new Vector3(3.42f, 0.05f, z), slab);
            // slabs leading to the porch steps
            slabs.Box(new Vector3(10.2f, 0, -1.86f), new Vector3(14.3f, 0.05f, -1.22f), slab);
            slabs.Box(new Vector3(10.2f, 0, -1.10f), new Vector3(14.3f, 0.05f, -0.52f), slab);
            _w.Emit("Paving_Slabs", _root, slabs, probeStatic: true);

            // steel edging along the walk and around the bed
            var edge = new MeshBuilder();
            var em = BoxMats.All(_m.Edging).Without(yn: true);
            edge.Box(new Vector3(1.69f, 0, -19f), new Vector3(1.705f, 0.06f, -3.35f), em);
            edge.Box(new Vector3(3.80f, 0, -19f), new Vector3(3.815f, 0.06f, -3.35f), em);
            edge.Box(new Vector3(3.80f, 0, -9.6f), new Vector3(11.6f, 0.06f, -9.585f), em);
            edge.Box(new Vector3(11.585f, 0, -9.6f), new Vector3(11.6f, 0.06f, -3.35f), em);
            edge.Box(new Vector3(-12f, 0, -3.365f), new Vector3(1.7f, 0.05f, -3.35f), em);
            _w.Emit("Steel_Edging", _root, edge, probeStatic: true);

            var bed = new MeshBuilder();
            bed.Box(new Vector3(3.815f, 0, -9.585f), new Vector3(11.585f, 0.035f, -3.35f), BoxMats.All(_m.Mulch).Without(yn: true));
            _w.Emit("Planting_Bed", _root, bed, castShadows: false, probeStatic: true);
            _keepOut.Add((new Vector2(2.75f, -11f), 1.2f));
        }

        // ------------------------------------------------------------------ boxwood hedges
        void Hedges()
        {
            var g = _w.Group("Hedges", _root);
            void H(string name, float x0, float x1, float z0, float z1, float h, int seed)
            {
                var mb = _veg.Hedge(new Vector3(x1 - x0, h, z1 - z0), 0.12f, seed);
                var go = _w.Emit(name, g, mb, probeStatic: true);
                if (go != null) go.transform.position = new Vector3((x0 + x1) * 0.5f, 0.02f, (z0 + z1) * 0.5f);
            }
            H("Hedge_LivingRoom", 4.85f, 9.25f, -1.42f, -0.82f, 0.56f, 11);
            H("Hedge_Left", -11.5f, -1.05f, 0.32f, 1.02f, 0.68f, 12);
            H("Hedge_Right", 15.25f, 34f, 1.15f, 1.85f, 0.78f, 13);
            H("Hedge_Rear", -1.2f, 16f, 12.4f, 13.1f, 0.9f, 14);
        }

        // ------------------------------------------------------------------ planting bed + foreground plants
        void BedAndForegroundPlants()
        {
            var g = _w.Group("Plants", _root);
            var protos = new Dictionary<string, Mesh>();
            var protoMats = new Dictionary<string, Material[]>();
            void Proto(string key, MeshBuilder mb)
            {
                protos[key] = _w.Store(mb.Build("Plant_" + key));
                protoMats[key] = mb.Materials;
            }
            Proto("pennisetum", _veg.GrassClump(0.42f, 0.55f, 160, 4, 0, 0, 101));
            Proto("pennisetum_grey", _veg.GrassClump(0.40f, 0.5f, 170, 7, 0, 0, 102, arch: 1.3f));
            Proto("plumes_tall", _veg.GrassClump(0.45f, 0.7f, 150, 3, 30, 1.2f, 103, plumeSize: 0.24f));
            Proto("plumes_short", _veg.GrassClump(0.35f, 0.45f, 110, 5, 18, 0.8f, 104, plumeSize: 0.2f));
            Proto("pampas", _veg.GrassClump(0.6f, 0.75f, 220, 7, 42, 1.3f, 105, plumeSize: 0.27f));
            Proto("mugo_s", _veg.RoundConifer(0.55f, 0.6f, 106));
            Proto("mugo_m", _veg.RoundConifer(0.75f, 0.75f, 107));
            Proto("mugo_l", _veg.RoundConifer(1.1f, 1.6f, 108));

            void Put(string key, float x, float z, float scale = 1f, float rot = 0f, float keep = 0.5f)
            {
                var go = _w.Instance("Plant_" + key, g, protos[key], protoMats[key], true, true);
                go.transform.position = new Vector3(x, 0.03f, z);
                go.transform.rotation = Quaternion.Euler(0, rot, 0);
                go.transform.localScale = Vector3.one * scale;
                _keepOut.Add((new Vector2(x, z), keep * scale));
            }
            // bed right of the entrance walk (reference: boulder, mounds, white plumes, mugo pines)
            Put("pennisetum", 4.35f, -6.7f, 1.0f, 10);
            Put("plumes_short", 5.25f, -7.75f, 1.1f, 40);
            Put("mugo_s", 5.45f, -8.55f, 1.0f, 0);
            Put("pennisetum_grey", 6.2f, -5.1f, 1.1f, 70);
            Put("plumes_tall", 6.95f, -6.4f, 1.0f, 120);
            Put("mugo_m", 8.2f, -7.6f, 1.0f, 30);
            Put("pennisetum", 8.9f, -5.0f, 1.2f, 200);
            Put("plumes_short", 9.8f, -6.4f, 1.0f, 250);
            Put("pennisetum_grey", 10.6f, -8.4f, 1.0f, 300);
            Put("mugo_s", 10.7f, -4.4f, 1.1f, 60);
            Put("pennisetum", 7.4f, -8.9f, 0.9f, 15);
            Put("plumes_tall", 11.0f, -3.95f, 0.9f, 90);
            Put("pennisetum_grey", 4.6f, -4.3f, 1.0f, 33);
            Put("mugo_s", 6.0f, -3.9f, 0.9f, 80);
            Put("pennisetum", 5.9f, -9.1f, 1.1f, 120);
            Put("plumes_short", 7.8f, -4.6f, 1.0f, 200);
            Put("pennisetum_grey", 9.4f, -9.0f, 1.0f, 10);
            Put("mugo_m", 10.4f, -6.0f, 0.95f, 140);
            Put("pennisetum", 11.1f, -7.6f, 0.9f, 260);
            Put("plumes_tall", 8.9f, -8.2f, 0.95f, 300);
            // foreground left (bottom-left of the reference frame)
            Put("pampas", -4.45f, -10.1f, 1.05f, 20, 0.8f);
            Put("mugo_m", -3.35f, -11.35f, 0.82f, 45, 0.8f);
            Put("pennisetum_grey", -2.2f, -11.85f, 1.2f, 80, 0.7f);
            Put("pennisetum", -1.2f, -12.9f, 1.1f, 140, 0.7f);
            Put("mugo_l", -6.9f, 4.8f, 1.0f, 10, 1.2f);   // pine beside the house, left
            Put("mugo_m", 20.2f, 2.6f, 1.2f, 70, 1.2f);   // pines beside the house, right
            Put("mugo_s", 23.8f, 4.2f, 1.1f, 20);
            Put("mugo_l", 31f, 9.5f, 1.4f, 110);
            Put("mugo_l", 44f, 22f, 2.2f, 10);

            // boulder
            var rock = new MeshBuilder();
            Boulder(rock, new Vector3(5.12f, 0f, -6.65f), new Vector3(0.95f, 0.5f, 0.62f), 17);
            _w.Emit("Boulder", g, rock, probeStatic: true);
        }

        void Boulder(MeshBuilder mb, Vector3 c, Vector3 size, int seed)
        {
            const int seg = 18, rings = 10;
            Vector3 P(float a, float t)
            {
                var d = new Vector3(Mathf.Cos(a) * Mathf.Cos(t), Mathf.Sin(t), Mathf.Sin(a) * Mathf.Cos(t));
                float n = 1f + Noise.Fbm3(d * 1.7f, 4, seed) * 0.35f;
                var p = Vector3.Scale(d * n, size * 0.5f);
                if (p.y < -0.05f) p.y = -0.05f;
                return c + p + Vector3.up * size.y * 0.35f;
            }
            for (int j = 0; j < rings; j++)
            {
                float t0 = Mathf.PI * j / rings - Mathf.PI / 2, t1 = Mathf.PI * (j + 1) / rings - Mathf.PI / 2;
                for (int i = 0; i < seg; i++)
                {
                    float a0 = Mathf.PI * 2 * i / seg, a1 = Mathf.PI * 2 * (i + 1) / seg;
                    Vector3 p00 = P(a0, t0), p10 = P(a1, t0), p01 = P(a0, t1), p11 = P(a1, t1);
                    Vector3 n = Vector3.Cross(p01 - p00, p11 - p00).normalized;
                    if (Vector3.Dot(n, (p00 + p11) * 0.5f - c) < 0) n = -n;
                    Vector2 U(Vector3 p) => new Vector2(p.x + p.z, p.y);
                    mb.Triangle(p00, p01, p11, n, n, n, U(p00), U(p01), U(p11), _m.Boulder);
                    mb.Triangle(p00, p11, p10, n, n, n, U(p00), U(p11), U(p10), _m.Boulder);
                }
            }
        }

        // ------------------------------------------------------------------ porch planters (reference: two pots with grasses)
        void PorchPlanters()
        {
            var g = _w.Group("Porch_Planters", _root);
            var pots = new MeshBuilder();
            HouseGenerator.Cylinder(pots, new Vector3(12.75f, HouseSpec.FloorY, 1.12f), 0.21f, 0.5f, 24, _m.FurnitureDark);
            HouseGenerator.Cylinder(pots, new Vector3(13.28f, HouseSpec.FloorY, 1.16f), 0.16f, 0.24f, 24, _m.Pot);
            HouseGenerator.Cylinder(pots, new Vector3(13.28f, HouseSpec.FloorY + 0.24f, 1.16f), 0.165f, 0.2f, 24, _m.FurnitureDark);
            _w.Emit("Pots", g, pots);
            var a = _w.Emit("Pot_Grass_A", g, _veg.GrassClump(0.18f, 0.42f, 90, 4, 9, 0.75f, 301, plumeSize: 0.2f));
            if (a != null) a.transform.position = new Vector3(12.75f, HouseSpec.FloorY + 0.48f, 1.12f);
            var b = _w.Emit("Pot_Grass_B", g, _veg.GrassClump(0.14f, 0.34f, 80, 5, 0, 0, 302));
            if (b != null) b.transform.position = new Vector3(13.28f, HouseSpec.FloorY + 0.42f, 1.16f);
        }

        // ------------------------------------------------------------------ timber bollard lights
        void Bollards()
        {
            var mb = new MeshBuilder();
            foreach (var p in new[] { new Vector2(1.9f, -3.45f), new Vector2(5.8f, -3.45f), new Vector2(15.82f, -1.95f), new Vector2(-4.2f, -3.45f), new Vector2(10.0f, -3.45f) })
            {
                Vector3 b = new Vector3(p.x, 0, p.y);
                mb.Box(b + new Vector3(-0.05f, 0, -0.05f), b + new Vector3(0.05f, 0.5f, 0.05f), BoxMats.All(_m.BollardWood).Without(yn: true));
                mb.Box(b + new Vector3(-0.056f, 0.5f, -0.056f), b + new Vector3(0.056f, 0.56f, 0.056f), BoxMats.All(_m.BollardCap).Without(yn: true));
                mb.Box(b + new Vector3(-0.03f, 0.43f, -0.052f), b + new Vector3(0.03f, 0.47f, -0.049f), BoxMats.All(_m.BollardLight));
            }
            _w.Emit("Bollards", _root, mb, probeStatic: true);
        }

        // ------------------------------------------------------------------ trees
        void Trees()
        {
            var g = _w.Group("Trees", _root);
            var spruce = new[] { _veg.Spruce(14f, 7), _veg.Spruce(17f, 8), _veg.Spruce(20f, 9) };
            var spruceMeshes = new Mesh[spruce.Length];
            for (int i = 0; i < spruce.Length; i++) spruceMeshes[i] = _w.Store(spruce[i].Build("Spruce_" + i));
            var birch = new[] { _veg.Birch(11f, 31), _veg.Birch(13f, 32) };
            var birchMeshes = new Mesh[birch.Length];
            for (int i = 0; i < birch.Length; i++) birchMeshes[i] = _w.Store(birch[i].Build("Birch_" + i));
            var broad = _veg.BroadleafTree(7f, 2.6f, 41);
            var broadMesh = _w.Store(broad.Build("Broadleaf"));

            void Spruce(float x, float z, float h, float rot)
            {
                int idx = h < 15.5f ? 0 : h < 18.5f ? 1 : 2;
                float native = idx == 0 ? 14f : idx == 1 ? 17f : 20f;
                var go = _w.Instance("Spruce", g, spruceMeshes[idx], spruce[idx].Materials, true, true);
                go.transform.position = new Vector3(x, 0, z);
                go.transform.rotation = Quaternion.Euler(0, rot, 0);
                go.transform.localScale = Vector3.one * (h / native);
            }
            void Birch(float x, float z, float h, float rot)
            {
                int idx = h < 12f ? 0 : 1;
                var go = _w.Instance("Birch", g, birchMeshes[idx], birch[idx].Materials, true, true);
                go.transform.position = new Vector3(x, 0, z);
                go.transform.rotation = Quaternion.Euler(0, rot, 0);
                go.transform.localScale = Vector3.one * (h / (idx == 0 ? 11f : 13f));
            }
            void Broad(float x, float z, float s, float rot)
            {
                var go = _w.Instance("Broadleaf", g, broadMesh, broad.Materials, true, true);
                go.transform.position = new Vector3(x, 0, z);
                go.transform.rotation = Quaternion.Euler(0, rot, 0);
                go.transform.localScale = Vector3.one * s;
            }

            // left backdrop (behind the house's left end)
            Birch(1.8f, 32f, 12f, 0);
            Birch(-2.5f, 27f, 10.5f, 140);
            Spruce(-0.8f, 30f, 12.5f, 30);
            Spruce(5.7f, 40f, 15f, 200);
            Spruce(-4.5f, 38f, 16f, 90);
            Spruce(-9f, 22f, 17f, 10);
            Broad(-5.5f, 16f, 1.0f, 0);
            // right backdrop
            Spruce(46.2f, 24f, 17f, 45);
            Spruce(62f, 32f, 20f, 120);
            Spruce(45.5f, 18f, 14.5f, 300);
            Spruce(61f, 38f, 17f, 10);
            Spruce(53f, 44f, 19f, 200);
            Birch(58f, 30f, 12f, 60);
            Birch(66f, 36f, 13f, 200);
            Birch(37f, 15f, 12.5f, 40);
            Birch(33f, 21f, 11f, 150);
            Spruce(41f, 11f, 13f, 70);
            Spruce(30f, 26f, 16f, 250);
            // behind the camera: reflected in the glazing, and the shade on the foreground lawn
            Spruce(-12f, -27f, 18f, 0);
            Spruce(-3.5f, -31f, 20f, 60);
            Spruce(6f, -29f, 17f, 120);
            Spruce(15f, -25f, 19f, 180);
            Spruce(24f, -17f, 16f, 240);
            Spruce(-17f, -13f, 15f, 300);
            Spruce(3.2f, -22.5f, 15f, 20);
            Broad(-9f, -19f, 1.2f, 0);
            Broad(0.8f, -21.5f, 1.45f, 30);
            Broad(-2.5f, -24f, 1.3f, 200);
            // distant ring of forest
            var rng = new Rng(404);
            for (int i = 0; i < 160; i++)
            {
                float a = rng.Range(0, Mathf.PI * 2);
                float r = i < 70 ? rng.Range(70f, 115f) : rng.Range(130f, 220f);
                float x = 7f + Mathf.Cos(a) * r, z = 5f + Mathf.Sin(a) * r;
                if (rng.Value() < 0.75f) Spruce(x, z, rng.Range(16f, 24f), rng.Range(0, 360));
                else Birch(x, z, rng.Range(11f, 15f), rng.Range(0, 360));
            }
        }

        // ------------------------------------------------------------------ grass blades in the camera foreground
        void LawnBlades()
        {
            var area = new Rect(-10f, -17f, 20f, 13.6f);
            float Density(Vector2 p)
            {
                // exclusions: gravel walk, bed, front gravel band, paths
                if (p.y > -3.4f) return 0f;
                if (p.x > 1.65f && p.x < 3.85f) return 0f;
                if (p.x > 3.8f && p.x < 11.6f && p.y > -9.6f) return 0f;
                foreach (var k in _keepOut) if ((p - k.p).sqrMagnitude < k.r * k.r) return 0f;
                Vector3 d = new Vector3(p.x, 0, p.y) - _cameraPos; d.y = 0;
                float dist = d.magnitude;
                if (dist < 1.5f || dist > 17f) return 0f;
                float ang = Vector3.Angle(d, _cameraFwd);
                if (ang > 30f) return 0f;
                return Mathf.Clamp01((17f - dist) / 6f);
            }
            var mb = _veg.LawnBlades(Density, area, 77, 230000);
            _w.Emit("Lawn_Blades", _root, mb, castShadows: false);
        }
    }
}
