using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using UnityEngine;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// Built things of the natural site (port of tools/landscape/garden/props.py): stepping-stone paths, the arched
    /// timber bridge, stone lanterns (tōrō), post lanterns, the board fence and single trees.
    /// </summary>
    public sealed class SitePropsBuilder
    {
        readonly SiteModel _m;
        readonly MaterialLibrary _lib;
        readonly MaterialResolver _mats;
        readonly SceneWriter _w;
        readonly VegetationFactory _veg;
        readonly Rng _rng;
        Material _wood, _slab, _stone, _fence, _metal, _glow;

        public SitePropsBuilder(SiteModel m, MaterialLibrary lib, MaterialResolver mats, SceneWriter w, VegetationFactory veg)
        {
            _m = m; _lib = lib; _mats = mats; _w = w; _veg = veg;
            _rng = new Rng(m.Terrain.Seed + 11);
        }

        public void Build(Transform parent)
        {
            _wood = _mats.Get("deck_boards#8a6a55", _lib.Wood);
            _slab = _mats.Get("flagstone_grey", _lib.Paver);
            _stone = _mats.Get("granite_dark#9a968e", _lib.Stone);
            _fence = _mats.Get("deck_boards#6e5646", _lib.Wood);
            _metal = _lib.FurnitureDark;
            _glow = _lib.BollardLight;
            var g = _w.Group("Built", parent);
            SteppingStones(g);
            foreach (var o in _m.Def.Objects)
            {
                switch (o.Type)
                {
                    case "bridge": Bridge(g, o); break;
                    case "stone_lantern": Lantern(g, o, stone: true); break;
                    case "garden_lamp": Lantern(g, o, stone: false); break;
                    case "tree": Tree(g, o); break;
                }
            }
            Fence(g);
        }

        // ------------------------------------------------------------------ helpers

        /// <summary>Box of <paramref name="size"/> centred at <paramref name="c"/>, turned by yaw (degrees) and pitch about its X axis.</summary>
        static void Box(MeshBuilder mb, Vector3 c, Vector3 size, float yaw, Material m, float pitch = 0f)
        {
            var saved = mb.Transform;
            mb.Transform = saved * Matrix4x4.TRS(c, Quaternion.Euler(0f, yaw, 0f) * Quaternion.Euler(0f, 0f, pitch), Vector3.one);
            mb.Box(-size * 0.5f, size * 0.5f, m);
            mb.Transform = saved;
        }

        /// <summary>n-sided frustum standing on <paramref name="baseY"/> (flat shaded, capped).</summary>
        static void Frustum(MeshBuilder mb, Vector3 c, float r0, float r1, float h, int sides, Material m, float yaw = 0f)
        {
            var ring0 = new Vector3[sides];
            var ring1 = new Vector3[sides];
            for (int i = 0; i < sides; i++)
            {
                float a = (i + 0.5f) * Mathf.PI * 2f / sides + yaw * Mathf.Deg2Rad;
                ring0[i] = c + new Vector3(Mathf.Cos(a) * r0, 0f, Mathf.Sin(a) * r0);
                ring1[i] = c + new Vector3(Mathf.Cos(a) * r1, h, Mathf.Sin(a) * r1);
            }
            var top = c + Vector3.up * h;
            for (int i = 0; i < sides; i++)
            {
                int j = (i + 1) % sides;
                var n = Vector3.Cross(ring1[i] - ring0[i], ring0[j] - ring0[i]).normalized;
                // counter-clockwise seen from outside: the larger angle is on the viewer's right
                mb.Quad(ring0[j], ring1[j], ring1[i], ring0[i], n, UV(ring0[j], n), UV(ring1[j], n), UV(ring1[i], n), UV(ring0[i], n), m);
                if (r1 > 0.001f) mb.Triangle(top, ring1[j], ring1[i], Vector3.up, Vector3.up, Vector3.up, UV(top, Vector3.up), UV(ring1[j], Vector3.up), UV(ring1[i], Vector3.up), m);
                mb.Triangle(c, ring0[i], ring0[j], Vector3.down, Vector3.down, Vector3.down, UV(c, Vector3.down), UV(ring0[i], Vector3.down), UV(ring0[j], Vector3.down), m);
            }
        }

        static Vector2 UV(Vector3 p, Vector3 n) => MeshBuilder.PlanarUV(p, n);

        // ------------------------------------------------------------------ stepping stones

        void SteppingStones(Transform parent)
        {
            var mb = new MeshBuilder();
            foreach (var path in _m.Paths)
            {
                if (path.Def.Style != "stepping" && !string.IsNullOrEmpty(path.Def.Style)) continue;
                var line = path.Line;
                float width = path.Def.Width;
                for (float s = 0.3f; s < line.Length - 0.2f;)
                {
                    var p = line.At(s, out var t);
                    var n = new Vector2(-t.y, t.x);
                    float size = _rng.Range(0.55f, 0.8f) * Mathf.Sqrt(width / 1.1f);
                    var offsets = new List<float> { _rng.Range(-0.12f, 0.12f) };
                    if (width > 1f && _rng.Value() < 0.35f) { offsets = new List<float> { -0.28f, 0.3f }; size *= 0.72f; }
                    foreach (float off in offsets)
                    {
                        var c = p + n * off * width;
                        if (_m.StreamAt(c.x, c.y, out float d, out _, out float hw, out _, out _) && d < hw + 0.3f) continue;
                        if (!_m.Area.Contains(c)) continue;
                        Slab(mb, c, size);
                    }
                    s += size * _rng.Range(1.05f, 1.25f);
                }
            }
            if (!mb.IsEmpty) _w.Emit("SteppingStones", parent, mb, castShadows: false, probeStatic: true);
        }

        void Slab(MeshBuilder mb, Vector2 c, float size)
        {
            const int seg = 12;
            float rot = _rng.Range(0f, Mathf.PI);
            float sx = size * _rng.Range(0.85f, 1.15f), sy = size * _rng.Range(0.65f, 0.9f);
            float z0 = _m.Height(c.x, c.y);
            var top = new Vector3[seg];
            var bot = new Vector3[seg];
            float seed = _rng.Range(0f, 100f);
            for (int k = 0; k < seg; k++)
            {
                float a = Mathf.PI * 2f * k / seg;
                float r = 1f + 0.16f * (Mathf.PerlinNoise(Mathf.Cos(a) * 2f + seed, Mathf.Sin(a) * 2f + seed) * 2f - 1f);
                float lx = Mathf.Cos(a) * sx / 2f * r, ly = Mathf.Sin(a) * sy / 2f * r;
                float x = c.x + lx * Mathf.Cos(rot) - ly * Mathf.Sin(rot), z = c.y + lx * Mathf.Sin(rot) + ly * Mathf.Cos(rot);
                float h = _m.Height(x, z);
                top[k] = new Vector3(x, Mathf.Max(z0, h) + 0.035f, z);
                bot[k] = new Vector3(x, Mathf.Min(z0, h) - 0.08f, z);
            }
            var ctr = new Vector3(c.x, z0 + 0.04f, c.y);
            for (int k = 0; k < seg; k++)
            {
                int j = (k + 1) % seg;
                mb.Triangle(ctr, top[j], top[k], Vector3.up, Vector3.up, Vector3.up, UV(ctr, Vector3.up), UV(top[j], Vector3.up), UV(top[k], Vector3.up), _slab);
                var n = Vector3.Cross(top[j] - top[k], bot[k] - top[k]).normalized;
                mb.Quad(bot[k], bot[j], top[j], top[k], n, UV(bot[k], n), UV(bot[j], n), UV(top[j], n), UV(top[k], n), _slab);
            }
        }

        // ------------------------------------------------------------------ bridge

        void Bridge(Transform parent, SiteObjectDef o)
        {
            if (o.To == null) return;
            var a = o.At; var b = o.To.Value;
            float span = (b - a).magnitude, width = 1.5f * o.Scale, rise = 0.55f;
            var mid = (a + b) * 0.5f;
            float yaw = -Mathf.Atan2(b.y - a.y, b.x - a.x) * Mathf.Rad2Deg;
            float baseY = Mathf.Max(_m.Height(a.x, a.y), _m.Height(b.x, b.y));
            float Arch(float x) => rise * (1f - Sq(2f * x / span));
            float Slope(float x) => Mathf.Atan(-8f * rise * x / (span * span)) * Mathf.Rad2Deg;
            var mb = new MeshBuilder();
            mb.Transform = Matrix4x4.TRS(new Vector3(mid.x, baseY, mid.y), Quaternion.Euler(0f, yaw, 0f), Vector3.one);
            int n = Mathf.Max(8, Mathf.RoundToInt(span / 0.16f));
            for (int i = 0; i < n; i++)
            {
                float x = -span / 2f + (i + 0.5f) * span / n;
                Box(mb, new Vector3(x, Arch(x) - 0.03f, 0f), new Vector3(span / n * 0.9f, 0.05f, width), 0f, _wood, Slope(x));
            }
            for (int side = -1; side <= 1; side += 2)
            {
                for (int i = 0; i < 24; i++)
                {
                    float xm = -span / 2f + (i + 0.5f) * span / 24f;
                    Box(mb, new Vector3(xm, Arch(xm) - 0.14f, side * (width / 2f - 0.08f)), new Vector3(span / 24f * 1.02f, 0.2f, 0.1f), 0f, _wood, Slope(xm));
                }
                float z = side * (width / 2f + 0.02f);
                const int posts = 6;
                for (int i = 0; i <= posts; i++)
                {
                    float x = -span / 2f + 0.15f + i * (span - 0.3f) / posts;
                    Box(mb, new Vector3(x, Arch(x) + 0.42f, z), new Vector3(0.09f, 0.9f, 0.09f), 0f, _wood);
                }
                foreach (var (h, th) in new[] { (0.86f, 0.07f), (0.45f, 0.045f) })
                    for (int i = 0; i < 24; i++)
                    {
                        float x0 = -span / 2f + 0.15f + i * (span - 0.3f) / 24f, x1 = x0 + (span - 0.3f) / 24f, xm = (x0 + x1) / 2f;
                        Box(mb, new Vector3(xm, Arch(xm) + h, z), new Vector3((x1 - x0) * 1.03f, th, th + 0.02f), 0f, _wood, Slope(xm));
                    }
            }
            _w.Emit("Bridge_" + o.Id, parent, mb, castShadows: true, probeStatic: true);
        }

        static float Sq(float v) => v * v;

        // ------------------------------------------------------------------ lanterns

        void Lantern(Transform parent, SiteObjectDef o, bool stone)
        {
            float s = o.Scale;
            var pos = new Vector3(o.At.x, _m.Height(o.At.x, o.At.y) - 0.03f, o.At.y);
            var mb = new MeshBuilder();
            mb.Transform = Matrix4x4.TRS(pos, Quaternion.Euler(0f, o.Rotation, 0f), Vector3.one * s);
            float lightY;
            if (stone)
            {
                Frustum(mb, new Vector3(0, 0, 0), 0.3f, 0.26f, 0.12f, 6, _stone);
                Frustum(mb, new Vector3(0, 0.12f, 0), 0.09f, 0.08f, 0.56f, 10, _stone);
                Frustum(mb, new Vector3(0, 0.67f, 0), 0.2f, 0.24f, 0.1f, 6, _stone);
                for (int k = 0; k < 4; k++)
                {
                    float a = k * 90f + 45f;
                    var p = Quaternion.Euler(0, a, 0) * new Vector3(0.14f, 0, 0);
                    Box(mb, p + new Vector3(0, 0.88f, 0), new Vector3(0.07f, 0.22f, 0.07f), a, _stone);
                }
                Box(mb, new Vector3(0, 0.88f, 0), new Vector3(0.16f, 0.2f, 0.16f), 0f, _glow);
                Frustum(mb, new Vector3(0, 0.98f, 0), 0.36f, 0.36f, 0.04f, 6, _stone);
                Frustum(mb, new Vector3(0, 1.02f, 0), 0.36f, 0.1f, 0.16f, 6, _stone);
                Frustum(mb, new Vector3(0, 1.17f, 0), 0.05f, 0.02f, 0.12f, 8, _stone);
                lightY = 0.88f;
            }
            else
            {
                Box(mb, new Vector3(0, 0.05f, 0), new Vector3(0.18f, 0.1f, 0.18f), 0f, _metal);
                Box(mb, new Vector3(0, 0.5f, 0), new Vector3(0.07f, 0.85f, 0.07f), 0f, _metal);
                Box(mb, new Vector3(0, 0.94f, 0), new Vector3(0.2f, 0.03f, 0.2f), 0f, _metal);
                for (int k = 0; k < 4; k++)
                {
                    var p = Quaternion.Euler(0, k * 90f + 45f, 0) * new Vector3(0.12f, 0, 0);
                    Box(mb, p + new Vector3(0, 1.06f, 0), new Vector3(0.02f, 0.22f, 0.02f), 0f, _metal);
                }
                Box(mb, new Vector3(0, 1.06f, 0), new Vector3(0.15f, 0.2f, 0.15f), 0f, _glow);
                Frustum(mb, new Vector3(0, 1.17f, 0), 0.16f, 0.03f, 0.1f, 4, _metal, 45f);
                lightY = 1.06f;
            }
            var go = _w.Emit((stone ? "StoneLantern_" : "GardenLamp_") + o.Id, parent, mb, castShadows: true, probeStatic: true);
            var lightGo = new GameObject(go.name + "_Light");
            lightGo.transform.SetParent(go.transform, false);
            lightGo.transform.position = pos + Vector3.up * lightY * s;
            var l = lightGo.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = new Color(1f, 0.7f, 0.42f);
            l.intensity = stone ? 1.2f : 2f;
            l.range = stone ? 3f : 4.5f;
            l.shadows = LightShadows.None;
        }

        // ------------------------------------------------------------------ fence

        void Fence(Transform parent)
        {
            var sides = _m.Def.Fence;
            if (sides == null || sides.Count == 0) return;
            var p = _m.Plot;
            var runs = new List<(Vector2 a, Vector2 b)>();
            if (sides.Contains("north")) runs.Add((new Vector2(p.xMax, p.yMax), new Vector2(p.xMin, p.yMax)));
            if (sides.Contains("east")) runs.Add((new Vector2(p.xMax, p.yMin), new Vector2(p.xMax, p.yMax)));
            if (sides.Contains("south")) runs.Add((new Vector2(p.xMin, p.yMin), new Vector2(p.xMax, p.yMin)));
            if (sides.Contains("west")) runs.Add((new Vector2(p.xMin, p.yMax), new Vector2(p.xMin, p.yMin)));
            var mb = new MeshBuilder();
            foreach (var (a, b) in runs)
            {
                float length = (b - a).magnitude;
                var t = (b - a) / length;
                float yaw = -Mathf.Atan2(t.y, t.x) * Mathf.Rad2Deg;
                int n = Mathf.RoundToInt(length / 0.15f);
                for (int i = 0; i < n; i++)
                {
                    var q = a + t * (i + 0.5f) * length / n;
                    if (_m.InHouse(q.x, q.y, 0.5f)) continue;
                    float z = _m.Height(q.x, q.y);
                    if (_m.StreamAt(q.x, q.y, out float d, out _, out float hw, out float w, out _) && d < hw + 0.2f) z = Mathf.Max(z, w + 0.05f);
                    float h = 1.85f + _rng.Range(-0.01f, 0.01f);
                    Box(mb, new Vector3(q.x, z + h / 2f - 0.05f, q.y), new Vector3(length / n * 0.94f, h, 0.025f), yaw, _fence);
                }
                for (float s = 0f; s <= length; s += 2.4f)
                {
                    var q = a + t * s;
                    if (_m.InHouse(q.x, q.y, 0.5f)) continue;
                    Box(mb, new Vector3(q.x, _m.Height(q.x, q.y) + 0.9f, q.y), new Vector3(0.1f, 1.9f, 0.1f), yaw, _fence);
                }
            }
            if (!mb.IsEmpty) _w.Emit("Fence", parent, mb, castShadows: true, probeStatic: true);
        }

        // ------------------------------------------------------------------ single trees

        void Tree(Transform parent, SiteObjectDef o)
        {
            string sp = string.IsNullOrEmpty(o.Species) ? "oak" : o.Species;
            var pos = new Vector3(o.At.x, _m.Height(o.At.x, o.At.y) - 0.05f, o.At.y);
            var rot = Quaternion.Euler(0f, o.Rotation, 0f);
            bool lod = GardenPerf.TreeLod;
            int seed = Mathf.Abs((o.Id ?? "t").GetHashCode()) % 1000;
            switch (sp)
            {
                case "spruce":
                {
                    var p = new TreeProto(_w, "Spruce_" + o.Id, _veg.Spruce(16f, seed), lod ? _veg.Spruce(16f, seed, 1) : null);
                    GardenLod.Tree(_w, "Spruce", parent, p, pos, rot, o.Scale);
                    break;
                }
                case "birch":
                {
                    var p = new TreeProto(_w, "Birch_" + o.Id, _veg.Birch(12f, seed), lod ? _veg.Birch(12f, seed, 1) : null);
                    GardenLod.Tree(_w, "Birch", parent, p, pos, rot, o.Scale);
                    break;
                }
                default:
                {
                    bool maple = sp == "maple_red";
                    var p = new TreeProto(_w, "Broadleaf_" + o.Id, _veg.BroadleafTree(maple ? 5f : 8f, maple ? 2.4f : 3.2f, seed),
                        lod ? _veg.BroadleafTree(maple ? 5f : 8f, maple ? 2.4f : 3.2f, seed, true, 1) : null);
                    var go = GardenLod.Tree(_w, "Broadleaf", parent, p, pos, rot, o.Scale);
                    if (maple) Redden(go);
                    break;
                }
            }
        }

        Material _red;

        /// <summary>Japanese maple: the deciduous leaf material with a red base colour.</summary>
        void Redden(GameObject tree)
        {
            foreach (var r in tree.GetComponentsInChildren<MeshRenderer>(true))
            {
                var mats = r.sharedMaterials;
                for (int i = 0; i < mats.Length; i++)
                    if (mats[i] == _lib.DeciduousLeaves)
                    {
                        if (_red == null) { _red = new Material(_lib.DeciduousLeaves) { name = "M_MapleLeaves" }; _red.SetColor("_BaseColor", new Color(1.7f, 0.5f, 0.42f)); }
                        mats[i] = _red;
                    }
                r.sharedMaterials = mats;
            }
        }
    }
}
