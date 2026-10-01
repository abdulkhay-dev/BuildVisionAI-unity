using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// The natural preset: a landscaped plot on relief built from the site's intent (streams, paths, planting
    /// style, placed objects). A detailed Unity terrain covers the plot (heights with the stream beds, four ground
    /// layers, grass and ground cover as instanced details, perennials and shrubs as tree instances with LODs),
    /// rocks are objects with colliders, a coarse terrain with hills and a forest reaches the horizon.
    /// </summary>
    public sealed class NaturalSiteBuilder
    {
        public const string RootName = "Landscape";
        const float TargetCell = 0.2f;

        readonly SiteDef _def;
        readonly LandscapeKit _kit;
        readonly SceneWriter _w;
        readonly VegetationFactory _veg;
        readonly MaterialLibrary _lib;
        readonly Generation.MaterialResolver _mats;
        SiteModel _m;
        PlantingPlan _plan;
        /// <summary>Zone per splat cell (the detail layers use the same grid).</summary>
        Zone[] _zones;
        int _zoneRes;
        Transform _root;
        Rng _rng;
        readonly List<string> _warnings;

        public SiteModel Model => _m;

        /// <summary>Plan outlines (convex) of pools dug into the ground: holes in the terrain, nothing planted there.</summary>
        public List<Vector2[]> Holes = new List<Vector2[]>();
        /// <summary>Footprints of built things standing on the ground (terraces, porches, steps): nothing grows there.</summary>
        public List<Vector2[]> Solids = new List<Vector2[]>();
        /// <summary>Paths the generator adds itself (the approach to the entrance).</summary>
        public List<SitePathDef> ExtraPaths = new List<SitePathDef>();

        public NaturalSiteBuilder(SiteDef def, LandscapeKit kit, SceneWriter w, VegetationFactory veg, MaterialLibrary lib,
            Generation.MaterialResolver mats, List<string> warnings)
        {
            _def = def; _kit = kit; _w = w; _veg = veg; _lib = lib; _mats = mats; _warnings = warnings;
        }

        public GameObject Build(Rect footprint)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            _m = new SiteModel(_def, footprint, extraPaths: ExtraPaths);
            _m.Hard.AddRange(Holes);
            _m.Hard.AddRange(Solids);
            _plan = new PlantingPlan(_m.Planting, _m.Terrain.Seed);
            _rng = new Rng(_m.Terrain.Seed + 31);
            var root = new GameObject(RootName);
            _root = root.transform;
            if (_kit == null)
            {
                _warnings.Add("участок: набор ландшафта не импортирован (House 46-96 → External → Import Landscape Kit)");
                return root;
            }

            var terrain = InnerTerrain();
            long tTerrain = sw.ElapsedMilliseconds;
            var plantsGo = new GameObject("Plants");
            plantsGo.transform.SetParent(_root, false);
            var plants = plantsGo.AddComponent<PlantField>();
            PlantBeds(plants);
            long tPlants = sw.ElapsedMilliseconds;
            Rocks(plants);
            Details(terrain);
            new WaterBuilder(_m, _kit, _w).Build(_root);
            new SitePropsBuilder(_m, _lib, _mats, _w, _veg).Build(_root);
            long tDetails = sw.ElapsedMilliseconds;
            OuterTerrain();
            if (_def.Trees != "none") Forest();
            Debug.Log($"[Site] natural: terrain {tTerrain} ms, plants+stones {plants.Count} in {tPlants - tTerrain} ms, " +
                      $"details {tDetails - tPlants} ms, total {sw.ElapsedMilliseconds} ms");
            return root;
        }

        // ------------------------------------------------------------------ terrain

        static int Resolution(float side)
        {
            int res = 129;
            while ((res - 1) * TargetCell < side && res < 1025) res = (res - 1) * 2 + 1;
            return res;
        }

        Terrain InnerTerrain()
        {
            var area = _m.Area;
            int res = Resolution(area.width);
            var heights = new float[res, res];
            float minH = float.MaxValue, maxH = float.MinValue;
            float step = area.width / (res - 1);
            var raw = new float[res * res];
            for (int j = 0; j < res; j++)
            for (int i = 0; i < res; i++)
            {
                float h = _m.Height(area.xMin + i * step, area.yMin + j * step);
                raw[j * res + i] = h;
                if (h < minH) minH = h;
                if (h > maxH) maxH = h;
            }
            float range = Mathf.Max(0.5f, maxH - minH);
            for (int j = 0; j < res; j++)
            for (int i = 0; i < res; i++)
                heights[j, i] = (raw[j * res + i] - minH) / range;

            var data = new TerrainData { heightmapResolution = res };
            data.size = new Vector3(area.width, range, area.height);
            data.SetHeights(0, 0, heights);
            data.alphamapResolution = res - 1;
            data.terrainLayers = new[] { _kit.TerrainLayer("soil"), _kit.TerrainLayer("grass"), _kit.TerrainLayer("pebbles"), _kit.TerrainLayer("mud") };
            Splat(data, res - 1);
            CutHoles(data, res, step);
            data.name = "SiteTerrain";

            var go = Terrain.CreateTerrainGameObject(data);
            go.name = "Terrain";
            go.transform.SetParent(_root, false);
            go.transform.position = new Vector3(area.xMin, minH, area.yMin);
            var t = go.GetComponent<Terrain>();
            Configure(t, detailed: true);
            return t;
        }

        /// <summary>Terrain holes where pools are dug in: cells whose centre is inside a pool cut (the coping hides the jagged edge).</summary>
        void CutHoles(TerrainData data, int res, float step)
        {
            if (Holes.Count == 0) return;
            int n = res - 1;
            var solid = new bool[n, n];
            var area = _m.Area;
            bool any = false;
            for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                var p = new Vector2(area.xMin + (i + 0.5f) * step, area.yMin + (j + 0.5f) * step);
                bool hole = Holes.Exists(h => Generation.Polygon.Contains(h, p));
                solid[j, i] = !hole;
                any |= hole;
            }
            if (any) data.SetHoles(0, 0, solid);
        }

        void Configure(Terrain t, bool detailed)
        {
            t.materialTemplate = _kit.TerrainMaterial;
            // not instanced: in the player the instanced path drew the ground with no sunlight (its per-pixel normals
            // come from a normal map the engine generates with a hidden shader the build does not carry); the editor
            // looked right. Patch meshes cost at most ~1 ms here
            t.drawInstanced = false;
            t.heightmapPixelError = detailed ? 3f : 8f;
            t.basemapDistance = detailed ? 120f : 60f;
            // one-sided: the ground only has to shade from above (two-sided doubled its shadow-map cost)
            t.shadowCastingMode = ShadowCastingMode.On;
            t.treeDistance = 160f;
            t.treeBillboardDistance = 2000f;          // LODGroup prefabs, no billboards
            t.treeMaximumFullLODCount = 10000;
            // grass clumps beyond ~45 m are a few pixels: the lawn layer carries the colour there (-2 ms)
            t.detailObjectDistance = 45f;
            t.detailObjectDensity = 1f;
            t.allowAutoConnect = false;
            t.groupingID = detailed ? 1 : 2;
        }

        /// <summary>Ground layers: 0 soil (beds), 1 grass (lawn and outside), 2 pebbles (stream bed), 3 mud (banks).</summary>
        void Splat(TerrainData data, int res)
        {
            var area = _m.Area;
            var maps = new float[res, res, 4];
            _zones = new Zone[res * res];
            _zoneRes = res;
            float cell = area.width / res;
            for (int j = 0; j < res; j++)
            for (int i = 0; i < res; i++)
            {
                float x = area.xMin + (i + 0.5f) * cell, z = area.yMin + (j + 0.5f) * cell;
                float n = Mathf.PerlinNoise(x * 0.35f + 3.3f, z * 0.35f + 1.1f);
                var zone = _m.ZoneAt(x, z, n);
                _zones[j * res + i] = zone;
                float grass;
                switch (zone)
                {
                    case Zone.Lawn: case Zone.Path: case Zone.House: case Zone.Outside: grass = 1f; break;
                    default: grass = 0f; break;
                }
                // soft lawn edge towards the beds (open lawn of the garden/lawn styles stays lawn)
                if ((zone == Zone.Bed || zone == Zone.Back || zone == Zone.Lawn && !_m.LawnGround) && _m.BedAt(x, z) < 0)
                {
                    float edge = _m.Planting.Lawn * (0.7f + 0.6f * n);
                    grass = 1f - SiteModel.Smooth(edge - 0.3f, edge + 0.3f, _m.PathDistance(x, z));
                    if (_m.InHouse(x, z, 2.2f) || !_m.InPlot(x, z, 0.3f)) grass = 1f;
                }
                float pebble = 0f, mud = 0f;
                if (_m.StreamAt(x, z, out float d, out _, out float hw, out _, out _))
                {
                    pebble = 1f - SiteModel.Smooth(hw - 0.2f, hw + 0.45f, d);
                    mud = (1f - SiteModel.Smooth(hw + 0.2f, hw + 1.3f, d)) * (1f - pebble);
                    grass *= SiteModel.Smooth(hw + 0.5f, hw + 1.5f, d);
                }
                float rest = 1f - pebble - mud;
                maps[j, i, 0] = rest * (1f - grass);
                maps[j, i, 1] = rest * grass;
                maps[j, i, 2] = pebble;
                maps[j, i, 3] = mud;
            }
            data.SetAlphamaps(0, 0, maps);
        }

        // ------------------------------------------------------------------ plants (instanced, PlantField)

        /// <summary>Groups whose plants cast shadows (the tall, dense ones); flowers and ground cover do not.</summary>
        const float RealtimeDensity = 0.75f;

        static bool Shadowed(string group) => group == "shrub" || group == "grass_tuft" || group == "fern";

        LandscapeKit.Variant Pick(string group)
        {
            var g = _kit.Find(group);
            if (g == null || g.Variants.Count == 0) return null;
            return g.Variants[_rng.Range(0, g.Variants.Count)];
        }

        void PlantBeds(PlantField field)
        {
            const float step = 0.24f;
            var plot = _m.Plot;
            void Place(string species, float x, float z)
            {
                var sp = PlantingPlan.All[species];
                var v = Pick(sp.Group);
                if (v == null) return;
                float y = _m.Height(x, z) - sp.Sink;
                float scale = _rng.Range(sp.ScaleMin, sp.ScaleMax) / Mathf.Sqrt(RealtimeDensity);
                field.Add(v.Prefab, new Vector3(x, y, z), _rng.Range(0f, Mathf.PI * 2f), scale, Shadowed(sp.Group));
            }
            for (float z = plot.yMin; z < plot.yMax; z += step)
            for (float x = plot.xMin; x < plot.xMax; x += step)
            {
                float px = x + _rng.Range(0f, step), pz = z + _rng.Range(0f, step);
                float n = Mathf.PerlinNoise(px * 0.35f + 3.3f, pz * 0.35f + 1.1f);
                var zone = _m.ZoneAt(px, pz, n);
                int bed = zone == Zone.Bed ? _m.BedAt(px, pz) : -1;
                var plan = bed >= 0 ? BedPlan(bed) : _plan;
                if (!plan.Plants(zone)) continue;
                string s0 = plan.SpeciesAt(zone, px, pz, 0);
                // realtime density: ~¾ of the Blender look-dev, the clumps a little larger (Place scales by 1/√ of it)
                if (s0 != null && _rng.Value() < RealtimeDensity * 1.35f * plan.Density * Sq(step / PlantingPlan.All[s0].Spacing)) Place(s0, px, pz);
                string s1 = plan.SpeciesAt(zone, px, pz, 1);
                if (s1 != null && _rng.Value() < RealtimeDensity * 1.1f * plan.Density * Sq(step / PlantingPlan.All[s1].Spacing)) Place(s1, px, pz);
            }
        }

        readonly Dictionary<int, PlantingPlan> _bedPlans = new Dictionary<int, PlantingPlan>();

        /// <summary>Planting of an explicit bed: the plot's settings with the bed's own style and flowers.</summary>
        PlantingPlan BedPlan(int i)
        {
            if (_bedPlans.TryGetValue(i, out var p)) return p;
            var b = _def.Beds[i];
            var d = new PlantingDef
            {
                Style = string.IsNullOrEmpty(b.Style) ? _m.Planting.Style : b.Style,
                Flowers = b.Flowers != null && b.Flowers.Count > 0 ? b.Flowers : _m.Planting.Flowers,
                Density = _m.Planting.Density, Lawn = _m.Planting.Lawn,
            };
            return _bedPlans[i] = new PlantingPlan(d, _m.Terrain.Seed + 7 * (i + 1));
        }

        static float Sq(float v) => v * v;

        // ------------------------------------------------------------------ rocks

        void Rocks(PlantField field)
        {
            var g = _w.Group("Rocks", _root);
            void Rock(string group, Vector2 p, float y, float size, bool tilt = true, float squash = 1f)
            {
                var v = Pick(group);
                if (v == null) return;
                float s = size / Mathf.Max(0.1f, Mathf.Max(v.Size.x, v.Size.z));
                var go = Object.Instantiate(v.Prefab, g);
                go.name = "Rock_" + v.Id;
                go.transform.SetPositionAndRotation(new Vector3(p.x, y, p.y),
                    Quaternion.Euler(tilt ? _rng.Range(-12f, 12f) : 0f, _rng.Range(0f, 360f), tilt ? _rng.Range(-12f, 12f) : 0f));
                go.transform.localScale = new Vector3(s, s * squash, s);
            }
            void Stone(Vector2 p, float scale)
            {
                var v = Pick("rock_small");
                if (v == null) return;
                field.Add(v.Prefab, new Vector3(p.x, _m.Height(p.x, p.y) - 0.01f, p.y), _rng.Range(0f, 6.28f), scale, false);
            }

            foreach (var st in _m.Streams)
            {
                var line = st.Line;
                for (float s = 0f; s < line.Length; s += _rng.Range(0.45f, 0.8f))
                {
                    var p = line.At(s, out var tan);
                    var n = new Vector2(-tan.y, tan.x);
                    float hw = st.HalfWidth(s);
                    var pool = st.PoolAt(s);
                    for (int k = 0; k < 4; k++)
                    {
                        int side = k % 2 == 0 ? -1 : 1, row = k / 2;
                        if (_rng.Value() > (row == 0 ? 0.9f : 0.35f)) continue;
                        float off = hw + _rng.Range(-0.3f, 0.3f) + row * _rng.Range(0.5f, 0.9f);
                        var q = p + n * side * off;
                        if (!_m.Area.Contains(q)) continue;
                        float size = row == 0 ? _rng.Range(0.5f, 1.2f) : _rng.Range(0.4f, 0.9f);
                        float y = Mathf.Max(_m.Height(q.x, q.y), pool.Level - 0.1f) - size * 0.2f;
                        Rock(_rng.Value() < 0.6f ? "rock_moss" : "rock_boulder", q, y, size, true, _rng.Range(0.6f, 1f));
                    }
                    for (int k = 0; k < 3; k++) Stone(p + n * _rng.Range(-hw, hw) * 0.9f, _rng.Range(1.5f, 4f));
                }
                foreach (var c in st.Cascades)
                {
                    var p = line.At(c.S, out var tan);
                    var n = new Vector2(-tan.y, tan.x);
                    float hw = st.HalfWidth(c.S);
                    // a weir of stones across the lip, the tongues pouring between them
                    for (float u = -1.15f; u < 1.15f;)
                    {
                        var gap = c.Tongues.Find(tg => Mathf.Abs(u - tg.x) < tg.y + 0.07f);
                        if (gap != default) { u = gap.x + gap.y + 0.08f; continue; }
                        float size = _rng.Range(0.45f, 0.75f);
                        Rock("rock_boulder", p + n * hw * u + tan * _rng.Range(-0.05f, 0.1f), c.Top - size * 0.28f, size, true, _rng.Range(0.7f, 1f));
                        u += size * 0.65f / hw;
                    }
                    // a jumble at the foot of the step, smaller under the tongues
                    for (float u = -1f; u < 1f;)
                    {
                        bool under = c.Tongues.Exists(tg => Mathf.Abs(u - tg.x) < tg.y);
                        float size = under ? _rng.Range(0.2f, 0.36f) : _rng.Range(0.4f, 0.68f);
                        Rock("rock_boulder", p + n * hw * u + tan * _rng.Range(0.12f, 0.3f), c.Bottom - size * (under ? 0.3f : 0.18f), size, true, _rng.Range(0.6f, 0.9f));
                        u += size * 0.55f / hw;
                    }
                    for (int side = -1; side <= 1; side += 2)
                        Rock("rock_moss", p + n * side * (hw + 0.25f), c.Bottom - 0.1f, _rng.Range(1.1f, 1.7f), false, _rng.Range(0.8f, 1f));
                }
            }
            // stones scattered in the beds
            var plot = _m.Plot;
            int count = Mathf.RoundToInt(plot.width * plot.height * 0.1f);
            for (int i = 0; i < count; i++)
            {
                var p = new Vector2(_rng.Range(plot.xMin, plot.xMax), _rng.Range(plot.yMin, plot.yMax));
                var zone = _m.ZoneAt(p.x, p.y);
                if (zone != Zone.Bed && zone != Zone.Bank && zone != Zone.Rim) continue;
                if (_rng.Value() < 0.8f) Stone(p, _rng.Range(3f, 7f));
                else Rock("rock_moss", p, _m.Height(p.x, p.y) - 0.1f, _rng.Range(0.3f, 0.6f));
            }
            // placed boulders and shrubs
            foreach (var o in SiteObjectDef.Expand(_def.Objects))
            {
                if (o.Type == "boulder")
                    Rock(string.IsNullOrEmpty(o.Species) ? "rock_boulder" : o.Species, o.At, _m.Height(o.At.x, o.At.y) - 0.2f * o.Scale, 1.2f * o.Scale, false);
                else if (o.Type == "shrub")
                {
                    var v = Pick("shrub");
                    if (v != null) field.Add(v.Prefab, new Vector3(o.At.x, _m.Height(o.At.x, o.At.y) - 0.05f, o.At.y), o.Rotation * Mathf.Deg2Rad, 1.3f * o.Scale, true);
                }
            }
        }

        // ------------------------------------------------------------------ details (grass and ground cover)

        void Details(Terrain t)
        {
            var data = t.terrainData;
            int res = data.heightmapResolution - 1;
            data.SetDetailResolution(res, 32);
            data.SetDetailScatterMode(DetailScatterMode.InstanceCountMode);
            // prototypes: lawn clumps, short grass, moss, low ground cover (the lighter variants only)
            var picks = new List<(LandscapeKit.Variant v, int layer)>();
            void Take(string group, int layer, int max, int maxTris)
            {
                var g = _kit.Find(group);
                if (g == null) return;
                int n = 0;
                foreach (var v in g.Variants)
                    if (v.TrianglesLod0 <= maxTris && n < max) { picks.Add((v, layer)); n++; }
            }
            // light meshes: a detail is a hand-sized clump, hundreds of them per square metre of view
            Take("grass_short", 0, 4, 300);
            Take("grass_lawn", 1, 3, 400);
            Take("moss", 2, 3, 100);
            Take("groundcover", 3, 6, 300);
            var protos = new DetailPrototype[picks.Count];
            for (int i = 0; i < picks.Count; i++)
            {
                protos[i] = new DetailPrototype
                {
                    prototype = picks[i].v.Prefab, usePrototypeMesh = true, useInstancing = true, renderMode = DetailRenderMode.VertexLit,
                    minWidth = 1.1f, maxWidth = 1.9f, minHeight = 1.1f, maxHeight = 2.0f, noiseSpread = 0.3f,
                    healthyColor = Color.white, dryColor = new Color(0.85f, 0.82f, 0.7f), alignToGround = 0.3f,
                    density = 1f, useDensityScaling = true,
                };
                if (picks[i].layer == 1) { protos[i].minWidth = 1.0f; protos[i].maxWidth = 1.5f; protos[i].minHeight = 1.0f; protos[i].maxHeight = 1.6f; }
                if (picks[i].layer == 2) { protos[i].minWidth = protos[i].minHeight = 3f; protos[i].maxWidth = protos[i].maxHeight = 6f; }
            }
            data.detailPrototypes = protos;
            var layers = new int[picks.Count][,];
            for (int i = 0; i < picks.Count; i++) layers[i] = new int[res, res];
            var byLayer = new List<int>[4];
            for (int l = 0; l < 4; l++) { byLayer[l] = new List<int>(); for (int i = 0; i < picks.Count; i++) if (picks[i].layer == l) byLayer[l].Add(i); }
            var area = _m.Area;
            float cell = area.width / res;
            float cellArea = cell * cell;
            void Put(int layer, int i, int j, float perSquareMetre)
            {
                if (byLayer[layer].Count == 0) return;
                float expect = perSquareMetre * cellArea;
                int n = Mathf.FloorToInt(expect) + (_rng.Value() < expect - Mathf.Floor(expect) ? 1 : 0);
                for (int k = 0; k < n; k++) layers[byLayer[layer][_rng.Range(0, byLayer[layer].Count)]][j, i]++;
            }
            for (int j = 0; j < res; j++)
            for (int i = 0; i < res; i++)
            {
                Zone zone;
                if (_zones != null && _zoneRes == res) zone = _zones[j * res + i];
                else
                {
                    float x = area.xMin + (i + 0.5f) * cell, z = area.yMin + (j + 0.5f) * cell;
                    zone = _m.ZoneAt(x, z, Mathf.PerlinNoise(x * 0.35f + 3.3f, z * 0.35f + 1.1f));
                }
                switch (zone)
                {
                    // the ground layers carry the colour; details add the texture near the eye (≈40k instances in a plot)
                    case Zone.Lawn:
                        Put(0, i, j, 22f); Put(1, i, j, 3f); break;
                    case Zone.Outside:
                        Put(0, i, j, 5f); Put(1, i, j, 1f); break;
                    case Zone.Rim: case Zone.Bank:
                        Put(2, i, j, 6f); Put(3, i, j, 2f); Put(0, i, j, 5f); break;
                    case Zone.Bed: case Zone.Back:
                        Put(0, i, j, 7f); Put(2, i, j, 4f); Put(3, i, j, 1f); break;
                }
            }
            for (int i = 0; i < picks.Count; i++) data.SetDetailLayer(0, 0, i, layers[i]);
        }

        // ------------------------------------------------------------------ far land and forest

        float FarHeight(float x, float z)
        {
            float h = _m.Natural(x, z);
            float r = Vector2.Distance(new Vector2(x, z), _m.Plot.center);
            float hills = 22f * SiteModel.Smooth(90f, 600f, r) * (0.55f + 0.45f * Mathf.PerlinNoise(x / 380f + 5.1f, z / 380f + 2.7f));
            return h + hills;
        }

        void OuterTerrain()
        {
            const float side = 1600f;
            const int res = 257;
            var c = _m.Plot.center;
            float x0 = c.x - side / 2f, z0 = c.y - side / 2f, step = side / (res - 1);
            var raw = new float[res * res];
            float minH = float.MaxValue, maxH = float.MinValue;
            var inner = _m.Area;
            for (int j = 0; j < res; j++)
            for (int i = 0; i < res; i++)
            {
                float x = x0 + i * step, z = z0 + j * step;
                float h = FarHeight(x, z);
                // under the detailed terrain: sink so it never pokes through
                float inside = Mathf.Min(Mathf.Min(x - inner.xMin, inner.xMax - x), Mathf.Min(z - inner.yMin, inner.yMax - z));
                if (inside > 0f) h -= 3f * SiteModel.Smooth(0f, step, inside);
                raw[j * res + i] = h;
                minH = Mathf.Min(minH, h); maxH = Mathf.Max(maxH, h);
            }
            float range = Mathf.Max(1f, maxH - minH);
            var heights = new float[res, res];
            for (int j = 0; j < res; j++)
            for (int i = 0; i < res; i++) heights[j, i] = (raw[j * res + i] - minH) / range;
            var data = new TerrainData { heightmapResolution = res, name = "FarTerrain" };
            data.size = new Vector3(side, range, side);
            data.SetHeights(0, 0, heights);
            data.alphamapResolution = 128;
            data.terrainLayers = new[] { _kit.TerrainLayer("grass"), _kit.TerrainLayer("soil") };
            var maps = new float[128, 128, 2];
            for (int j = 0; j < 128; j++)
            for (int i = 0; i < 128; i++)
            {
                float n = Mathf.PerlinNoise(i * 0.09f, j * 0.09f);
                maps[j, i, 0] = 0.75f + 0.25f * n;
                maps[j, i, 1] = 1f - maps[j, i, 0];
            }
            data.SetAlphamaps(0, 0, maps);
            var go = Terrain.CreateTerrainGameObject(data);
            go.name = "FarTerrain";
            go.transform.SetParent(_root, false);
            go.transform.position = new Vector3(x0, minH, z0);
            Configure(go.GetComponent<Terrain>(), detailed: false);
        }

        void Forest()
        {
            var g = _w.Group("Trees", _root);
            bool lod = GardenPerf.TreeLod;
            float[] spruceH = { 14f, 18f }; int[] spruceSeed = { 7, 8 };
            float[] birchH = { 11f, 13f }; int[] birchSeed = { 31, 32 };
            var spruce = new TreeProto[spruceH.Length];
            for (int i = 0; i < spruce.Length; i++)
                spruce[i] = new TreeProto(_w, "Spruce_" + i, _veg.Spruce(spruceH[i], spruceSeed[i]), lod ? _veg.Spruce(spruceH[i], spruceSeed[i], 1) : null);
            var birch = new TreeProto[birchH.Length];
            for (int i = 0; i < birch.Length; i++)
                birch[i] = new TreeProto(_w, "Birch_" + i, _veg.Birch(birchH[i], birchSeed[i]), lod ? _veg.Birch(birchH[i], birchSeed[i], 1) : null);

            // towards the sun only trees too short to shade the garden (shadow = height / tan(elevation))
            float sunAz = _def.SunAzimuth * Mathf.Deg2Rad, tanEl = Mathf.Tan(Mathf.Max(3f, _def.SunElevation) * Mathf.Deg2Rad);
            var rng = new Rng(_m.Terrain.Seed + 41);
            var plot = _m.Plot;
            var c = plot.center;
            for (int i = 0; i < 420; i++)
            {
                float a = rng.Range(0f, Mathf.PI * 2f);
                float r = Mathf.Max(plot.width, plot.height) * 0.5f + 6f + Mathf.Pow(rng.Value(), 1.4f) * 240f;
                float x = c.x + Mathf.Sin(a) * r, z = c.y + Mathf.Cos(a) * r;
                if (_m.InPlot(x, z, -4f)) continue;
                bool isBirch = rng.Value() < 0.35f;
                float h = isBirch ? rng.Range(10f, 14f) : rng.Range(13f, 21f);
                float da = Mathf.Abs(Mathf.DeltaAngle(a * Mathf.Rad2Deg, sunAz * Mathf.Rad2Deg));
                float edge = Mathf.Sqrt(Sq(Mathf.Max(plot.xMin - x, 0f, x - plot.xMax)) + Sq(Mathf.Max(plot.yMin - z, 0f, z - plot.yMax)));
                if (da < 35f && h > 0.8f * edge * tanEl) continue;
                var pos = new Vector3(x, FarHeight(x, z) - 0.1f, z);
                var rot = Quaternion.Euler(0f, rng.Range(0f, 360f), 0f);
                if (isBirch) { int k = rng.Range(0, birch.Length); GardenLod.Tree(_w, "Birch", g, birch[k], pos, rot, h / birchH[k]); }
                else { int k = rng.Range(0, spruce.Length); GardenLod.Tree(_w, "Spruce", g, spruce[k], pos, rot, h / spruceH[k]); }
            }
        }
    }
}
