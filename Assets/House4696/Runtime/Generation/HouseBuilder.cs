using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using House4696.Runtime;
using House4696.Setup;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace House4696.Generation
{
    public sealed class HouseBuildResult
    {
        public GameObject House, Site;
        public List<string> Warnings;
        public Rect Footprint;
        public Vector3 Pivot;
        public WalkPoint[] Walk;
        public OrbitPoint[] Orbit;
        public int Colliders;
    }

    /// <summary>
    /// Generates a house from a <see cref="HouseDocument"/>: walls and openings, rooms (slabs, ceilings, downlights,
    /// probes), roofs, stairs, elements, catalogue items, lights, the site and colliders. Works in the editor and
    /// in a player (with <see cref="SceneWriter"/> hooks deciding whether meshes become assets).
    /// </summary>
    public static class HouseBuilder
    {
        static readonly Color Warm = new Color(1f, 0.86f, 0.71f);
        static readonly Color Neutral = new Color(1f, 0.93f, 0.85f);

        public static HouseBuildResult Build(HouseDocument doc, MaterialLibrary lib, SceneWriter w)
        {
            var c = new HouseContext(doc, lib, w);
            var root = new GameObject("House_" + Sanitize(doc.Meta?.Name));
            c.Root = root.transform;
            c.Shell = w.Group("Shell", c.Root);
            c.Interior = w.Group("Interior", c.Root);
            c.Doors = w.Group("Doors", c.Root);
            c.Furniture = w.Group("Items", c.Root);
            c.Lights = w.Group("Lights", c.Root);
            c.Probes = w.Group("ReflectionProbes", c.Root);

            var walls = new WallBuilder(c);
            foreach (var f in c.Walls) walls.Build(f);
            new RoomBuilder(c).BuildAll();
            var roofs = new RoofBuilder(c);
            foreach (var r in doc.Roofs) roofs.Build(r);
            var stairs = new StairBuilder(c);
            foreach (var s in doc.Stairs) stairs.Build(s);
            var elements = new ElementBuilder(c);
            foreach (var e in doc.Elements) elements.Build(e);
            foreach (var it in doc.Items) Item(c, it);
            Lights(c);

            var footprint = Footprint(c);
            var site = new SiteBuilder(c).Build(footprint);
            int colliders = CollisionSetup.Apply(site != null ? new[] { root, site } : new[] { root });
            return new HouseBuildResult
            {
                House = root, Site = site, Warnings = c.Warnings, Footprint = footprint, Colliders = colliders,
                Pivot = new Vector3(footprint.center.x, TopHeight(c) * 0.45f, footprint.center.y),
                Walk = WalkViews(doc), Orbit = OrbitViews(doc),
            };
        }

        static string Sanitize(string s) => string.IsNullOrEmpty(s) ? "Project" : s.Replace('/', '_').Replace('\\', '_');

        // ------------------------------------------------------------------ items
        /// <summary>Builds a catalogue item in its local space and places it with its transform (so it can move later).</summary>
        static void Item(HouseContext c, ItemDef it)
        {
            var model = ItemCatalog.Get(it.Model);
            if (model == null) { c.Warn($"item '{it.Id}': unknown model '{it.Model}'"); return; }
            string levelId = it.Level;
            if (levelId == null && it.Room != null) levelId = c.Doc.Rooms.Find(r => r.Id == it.Room)?.Level;
            float baseY = levelId != null ? c.Elevation(levelId) : 0f;
            string id = it.Id ?? model.Id;
            var go = new GameObject("Item_" + id);
            go.transform.SetParent(c.Furniture, false);
            // rotation = compass direction the item's front faces (0 = +Z); catalogue models are built facing -Z
            go.transform.SetPositionAndRotation(new Vector3(it.Position.x, baseY + it.Position.y, it.Position.z), Quaternion.Euler(0, it.Rotation + 180f, 0));

            var b = new ItemBuild { C = c, P = new ItemParams(it.Params, c.Mats) };
            try { model.Build(b); }
            catch (System.Exception ex) { c.Warn($"item '{id}' ({model.Id}) failed: {ex.Message}"); return; }
            c.W.Emit("Furniture_" + id, go.transform, b.F);
            c.W.Emit("Decor_" + id, go.transform, b.D, castShadows: true);
            for (int i = 0; i < b.Plants.Count; i++)
            {
                var p = c.W.Emit("Plant_" + id + (i > 0 ? "_" + i : ""), go.transform, b.Plants[i].mb);
                if (p != null) p.transform.localPosition = b.Plants[i].pos;
            }
        }

        // ------------------------------------------------------------------ lights
        static void Lights(HouseContext c)
        {
            foreach (var l in c.Doc.Lights)
            {
                float baseY = l.Level != null ? c.Elevation(l.Level) : 0f;
                var pos = l.Position + Vector3.up * baseY;
                var light = Make(c, l.Id ?? "light", pos, l.Type == LightKind.Spot ? LightType.Spot : LightType.Point,
                    ColorOf(l.Color), l.Intensity, l.Range, l.Shadows);
                if (l.Type == LightKind.Spot)
                {
                    var target = (l.Target ?? (l.Position + Vector3.down)) + Vector3.up * baseY;
                    light.transform.rotation = Quaternion.LookRotation(target - pos, Vector3.forward);
                    light.spotAngle = l.Angle;
                    light.innerSpotAngle = l.Angle * 0.45f;
                }
            }
            // rooms without an explicit light get a soft ceiling light at their centroid
            foreach (var r in c.Doc.Rooms)
            {
                if (r.Type == RoomType.Terrace || r.Outline.Count < 3) continue;
                var L = c.Level(r.Level);
                float y0 = L.Elevation, y1 = y0 + (r.Height ?? L.Height);
                bool lit = c.Doc.Lights.Exists(l =>
                {
                    float by = l.Level != null ? c.Elevation(l.Level) : 0f;
                    var p = l.Position + Vector3.up * by;
                    return p.y >= y0 - 0.05f && p.y <= y1 + 0.05f && Polygon.Contains(r.Outline, new Vector2(p.x, p.z));
                });
                if (lit) continue;
                float area = Mathf.Abs(Polygon.SignedArea(r.Outline));
                var cen = Polygon.Centroid(r.Outline);
                // low enough not to burn a hot spot into the ceiling, soft enough to read as ambient room light
                Make(c, "Room_" + r.Id, new Vector3(cen.x, Mathf.Max(y0 + 1.6f, y1 - 1.1f), cen.y), LightType.Point, Warm,
                    0.45f + area * 0.012f, Mathf.Sqrt(area) * 1.3f + 2f, false);
            }
        }

        static Light Make(HouseContext c, string name, Vector3 pos, LightType type, Color col, float intensity, float range, bool shadows)
        {
            var go = new GameObject("Light_" + name);
            go.transform.SetParent(c.Lights, false);
            go.transform.position = pos;
            var l = go.AddComponent<Light>();
            l.type = type;
            l.color = col;
            l.intensity = intensity;
            l.range = range;
            l.shadows = shadows ? LightShadows.Soft : LightShadows.None;
            l.shadowBias = 0.02f;
            l.shadowNormalBias = 0.3f;
            l.shadowNearPlane = 0.1f;
#if UNITY_EDITOR
            l.lightmapBakeType = LightmapBakeType.Mixed; // editor bake only; a player lights everything in realtime
#endif
            l.bounceIntensity = 1f;
            go.AddComponent<UniversalAdditionalLightData>().usePipelineSettings = true;
            return l;
        }

        public static Color ColorOf(string s)
        {
            if (string.IsNullOrEmpty(s) || s == "warm") return Warm;
            if (s == "neutral") return Neutral;
            if (s == "cool") return new Color(0.9f, 0.95f, 1f);
            if (s == "fire") return new Color(1f, 0.55f, 0.25f);
            return ColorUtility.TryParseHtmlString(s, out var col) ? col : Warm;
        }

        // ------------------------------------------------------------------ extents and views
        static Rect Footprint(HouseContext c)
        {
            bool any = false;
            Vector2 mn = default, mx = default;
            void Add(Vector3 p)
            {
                var q = new Vector2(p.x, p.z);
                if (!any) { mn = mx = q; any = true; } else { mn = Vector2.Min(mn, q); mx = Vector2.Max(mx, q); }
            }
            foreach (var f in c.Walls) if (f.Exterior) { Add(f.WorldA); Add(f.WorldB); }
            if (!any) foreach (var r in c.Doc.Rooms) foreach (var p in r.Outline) Add(new Vector3(p.x, 0, p.y));
            return any ? Rect.MinMaxRect(mn.x, mn.y, mx.x, mx.y) : new Rect(-5, -5, 10, 10);
        }

        static float TopHeight(HouseContext c)
        {
            float top = 3f;
            foreach (var f in c.Walls) top = Mathf.Max(top, f.Y1);
            return top;
        }

        static WalkPoint[] WalkViews(HouseDocument doc)
        {
            var list = new List<WalkPoint>();
            foreach (var v in doc.Views)
                if (v.Type == ViewKind.Walk) list.Add(new WalkPoint { Name = v.Name, Feet = v.Position, Yaw = v.Yaw, Pitch = v.Pitch });
            return list.ToArray();
        }

        static OrbitPoint[] OrbitViews(HouseDocument doc)
        {
            var list = new List<OrbitPoint>();
            foreach (var v in doc.Views)
                if (v.Type == ViewKind.Orbit) list.Add(new OrbitPoint { Name = v.Name, Yaw = v.Yaw, Pitch = v.Pitch, Distance = v.Distance });
            if (list.Count == 0)
            {
                list.Add(new OrbitPoint { Name = "Фасад 3/4", Yaw = 30f, Pitch = 10f, Distance = 26f });
                list.Add(new OrbitPoint { Name = "Главный фасад", Yaw = 0f, Pitch = 5f, Distance = 24f });
                list.Add(new OrbitPoint { Name = "Задний фасад", Yaw = 180f, Pitch = 6f, Distance = 24f });
                list.Add(new OrbitPoint { Name = "Вид сверху", Yaw = 20f, Pitch = 70f, Distance = 34f });
            }
            return list.ToArray();
        }
    }
}
