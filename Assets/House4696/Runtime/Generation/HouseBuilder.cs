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
        /// <summary>Resolved geometry of this build (walls, stairs, roofs) for the checks and the inspector.</summary>
        public HouseContext Context;
        /// <summary>Built catalogue items with their real bounds.</summary>
        public List<ItemBox> Items = new List<ItemBox>();
        /// <summary>Geometric checks of the built house (<see cref="HouseChecks"/>).</summary>
        public List<Issue> Checks = new List<Issue>();
        /// <summary>Materials created for this house (tinted variants); the owner destroys them with the house.</summary>
        public List<Material> CreatedMaterials = new List<Material>();
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
            House4696.Doors.DoorSizing.Normalize(doc);
            var c = new HouseContext(doc, lib, w);
            var root = new GameObject("House_" + Sanitize(doc.Meta?.Name));
            c.Root = root.transform;
            c.Shell = w.Group("Shell", c.Root);
            c.Interior = w.Group("Interior", c.Root);
            c.Doors = w.Group("Doors", c.Root);
            c.Furniture = w.Group("Items", c.Root);
            c.Lights = w.Group("Lights", c.Root);
            c.Probes = w.Group("ReflectionProbes", c.Root);

            var basements = new BasementBuilder(c);
            basements.Plan();
            var walls = new WallBuilder(c);
            foreach (var f in c.Walls) walls.Build(f);
            basements.Build();
            new RoomBuilder(c).BuildAll();
            var roofs = new RoofBuilder(c);
            foreach (var r in doc.Roofs) roofs.Build(r);
            var stairs = new StairBuilder(c);
            foreach (var s in doc.Stairs) stairs.Build(s);
            var lifts = new House4696.Lifts.LiftBuilder(c);
            foreach (var g in c.Lifts) lifts.Build(g);
            new EdgeGuards(c).Build();
            var elements = new ElementBuilder(c);
            foreach (var e in doc.Elements) elements.Build(e);
            foreach (var it in doc.Items) BuildItem(c, it);
            Lights(c);

            var footprint = Footprint(c);
            var site = new SiteBuilder(c).Build(footprint);
            int colliders = CollisionSetup.Apply(site != null ? new[] { root, site } : new[] { root });
            var result = new HouseBuildResult
            {
                House = root, Site = site, Warnings = c.Warnings, Footprint = footprint, Colliders = colliders,
                Pivot = new Vector3(footprint.center.x, TopHeight(c) * 0.45f, footprint.center.y),
                Walk = WalkViews(doc), Orbit = OrbitViews(doc), CreatedMaterials = new List<Material>(c.Mats.Created),
                Context = c, Items = c.ItemBoxes,
            };
            try { HousePhysicsChecks.Run(c, root); }
            catch (System.Exception e) { Debug.LogException(e); c.Warn("walk-through checks failed: " + e.Message); }
            try { result.Checks = HouseChecks.Run(c, c.ItemBoxes); }
            catch (System.Exception e) { Debug.LogException(e); c.Warn("geometry checks failed: " + e.Message); }
            return result;
        }

        static Dictionary<string, Bounds> _measured;

        /// <summary>True once <see cref="MeasureCatalog"/> has built (and loaded) every model.</summary>
        public static bool CatalogMeasured => _measured != null;

        /// <summary>
        /// Real extent of every catalogue model with default parameters, in the model's frame (front faces -Z, origin =
        /// its placement point): built once in a throwaway house and cached.
        /// </summary>
        public static Dictionary<string, Bounds> MeasureCatalog(MaterialLibrary lib)
        {
            if (_measured != null) return _measured;
            var doc = new HouseDocument();
            doc.Site.Landscape = LandscapePreset.None;
            doc.Levels.Add(new LevelDef { Id = "ground" });
            int i = 0;
            foreach (var m in ItemCatalog.Listed)
            {
                doc.Items.Add(new ItemDef { Id = m.Id, Model = m.Id, Level = "ground", Position = new Vector3(i % 12 * 15f, 0, i / 12 * 15f) });
                i++;
            }
            var w = new SceneWriter();
            var r = Build(doc, lib, w);
            _measured = new Dictionary<string, Bounds>(System.StringComparer.OrdinalIgnoreCase);
            foreach (var it in r.Items) _measured[it.Model] = it.Local;
            // immediately: the probe objects must not render (or reach the lighting bake) even for one frame
            void Kill(Object o) { if (o != null) Object.DestroyImmediate(o); }
            Kill(r.House); Kill(r.Site);
            foreach (var m in r.CreatedMaterials) Kill(m);
            foreach (var m in w.RuntimeMeshes) Kill(m);
            return _measured;
        }

        static string Sanitize(string s) => string.IsNullOrEmpty(s) ? "Project" : s.Replace('/', '_').Replace('\\', '_');

        // ------------------------------------------------------------------ items
        /// <summary>
        /// Builds a catalogue item under the house's items group and registers its real extent (<see cref="HouseContext.ItemBoxes"/>);
        /// null when the model is unknown or failed. The item is built in its local space and placed by its transform, so it can
        /// move later. <paramref name="writer"/> overrides the context's writer (an item rebuilt on its own).
        /// </summary>
        public static ItemBox BuildItem(HouseContext c, ItemDef it, SceneWriter writer = null)
        {
            var go = CreateItem(c, it, c.Furniture, writer ?? c.W, out var model, out float baseY);
            if (go == null) return null;
            var box = ItemBox.Of(it, model, go, baseY);
            c.ItemBoxes.Add(box);
            return box;
        }

        /// <summary>
        /// The item's object exactly as the house builds it, under <paramref name="parent"/>, without registering it: a preview
        /// that follows the pointer. Its generated meshes belong to <paramref name="writer"/> (release them with the preview).
        /// </summary>
        public static GameObject BuildItemObject(HouseContext c, ItemDef it, Transform parent, SceneWriter writer) =>
            CreateItem(c, it, parent, writer, out _, out _);

        static GameObject CreateItem(HouseContext c, ItemDef it, Transform parent, SceneWriter w, out ItemModel model, out float baseY)
        {
            baseY = 0f;
            model = ItemCatalog.Get(it.Model);
            if (model == null) { c.Warn($"item '{it.Id}': unknown model '{it.Model}'"); return null; }
            string levelId = it.Level;
            if (levelId == null && it.Room != null) levelId = c.Doc.Rooms.Find(r => r.Id == it.Room)?.Level;
            baseY = levelId != null ? c.Elevation(levelId) : 0f;
            string id = it.Id ?? model.Id;
            var go = new GameObject("Item_" + id);
            go.transform.SetParent(parent, false);
            // rotation = compass direction the item's front faces (0 = +Z); catalogue models are built facing -Z
            go.transform.SetPositionAndRotation(new Vector3(it.Position.x, baseY + it.Position.y, it.Position.z), Quaternion.Euler(0, it.Rotation + 180f, 0));

            var b = new ItemBuild { C = c, P = new ItemParams(it.Params, c.Mats) };
            try { model.Build(b); }
            catch (System.Exception ex)
            {
                c.Warn($"item '{id}' ({model.Id}) failed: {ex.Message}");
                if (Application.isPlaying) Object.Destroy(go); else Object.DestroyImmediate(go);
                return null;
            }
            if (b.External != null) { PlaceModel(c, go, id, b); return go; }
            w.Emit("Furniture_" + id, go.transform, b.F);
            // light fittings glow themselves: their globes and shades casting shadows of the lamps' own lights put
            // dark discs on the ceiling (a chandelier's globes shadow each other's bulbs)
            w.Emit("Decor_" + id, go.transform, b.D, castShadows: model.Category != "lighting");
            w.Emit("Decor_" + id + "_Glass", go.transform, b.G, castShadows: false);
            foreach (var mv in b.Movers) EmitMover(w, go.transform, id, mv);
            for (int i = 0; i < b.Plants.Count; i++)
            {
                var p = w.Emit("Plant_" + id + (i > 0 ? "_" + i : ""), go.transform, b.Plants[i].mb);
                if (p != null) p.transform.localPosition = b.Plants[i].pos;
            }
            return go;
        }

        /// <summary>
        /// A moving part of an item on its own pivot: "Furniture_…" so it collides (a click opens it) and counts in the
        /// item's extent; the glass of a glazed door too, so a click on the glass opens the door.
        /// </summary>
        static void EmitMover(SceneWriter w, Transform parent, string id, ItemMover mv)
        {
            if (mv.Solid.IsEmpty && mv.Glass.IsEmpty) return;
            var pivot = new GameObject("Furniture_" + id + "_" + mv.Name);
            pivot.transform.SetParent(parent, false);
            pivot.transform.localPosition = mv.Pivot;
            pivot.transform.localRotation = mv.Frame;
            var back = Quaternion.Inverse(mv.Frame);
            foreach (var (mb, part, shadows) in new[] { (mv.Solid, "", true), (mv.Glass, "_Glass", false) })
            {
                var o = w.Emit("Furniture_" + id + "_" + mv.Name + part, pivot.transform, mb, castShadows: shadows);
                if (o == null) continue;
                // the meshes are in the item's space: undo the pivot's turn and offset
                o.transform.localRotation = back;
                o.transform.localPosition = back * -mv.Pivot;
                w.MarkDynamic(o);
            }
            w.MarkDynamic(pivot);
            var door = pivot.AddComponent<House4696.Runtime.Door>();
            door.Motion = mv.Motion;
            door.OpenAngle = mv.Angle;
            door.SlideBy = mv.Slide;
            if (mv.Open) door.SetOpen(true, instant: true);
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
        }

        /// <summary>
        /// Library model: the prefab under the item's transform; every slot takes the item parameter of the same name
        /// (a library material, "#rrggbb" to tint the model's own material, or "original"), else the slot's default.
        /// </summary>
        static void PlaceModel(HouseContext c, GameObject go, string id, ItemBuild b)
        {
            var e = b.External;
            var inst = Object.Instantiate(e.Prefab, go.transform, false);
            // collider rules go by name: plants and light fittings get none, other models a box
            string prefix = e.Category == "plants" ? "Plant_" : e.Category == "lighting" ? "Decor_" : "Model_";
            inst.name = prefix + id;
            var r = inst.GetComponentInChildren<MeshRenderer>();
            if (r == null) return;
            r.gameObject.name = prefix + id + "_mesh";
            var mats = r.sharedMaterials;
            for (int i = 0; i < mats.Length && i < e.Slots.Count; i++)
            {
                var slot = e.Slots[i];
                string want = b.P.S(e.SlotKey(i), null) ?? b.P.S(slot.Name, null) ?? slot.Default;
                if (string.IsNullOrEmpty(want) || want == "original") continue;
                mats[i] = want.StartsWith("#") ? c.Mats.Tint(slot.Own != null ? slot.Own : mats[i], want) : c.Mats.Get(want, mats[i]);
            }
            r.sharedMaterials = mats;
            // light fittings glow themselves (see Decor_ above)
            if (e.Category == "lighting") r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
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

        /// <summary>
        /// Perf plan step 4a. Every lamp gets a fixed shadow-resolution tier of the pipeline asset (spots High =
        /// 1024, points Medium = 512 per cube face) instead of the default High for all. With High everywhere, 5
        /// shadowed lamps request 20 slices of 1024² that do not fit the 4096² atlas, so URP halves all of them to 512,
        /// and the resolution pops between 512 and 1024 as lamps enter and leave the view. Fixed tiers always fit
        /// (no squeeze, no popping). Set to false (then rebuild) to go back to URP's default tier.
        /// </summary>
        public static bool FixedLampShadowTiers = true;

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
            // no shadowBias / shadowNormalBias: URP ignores them while usePipelineSettings = true (asset 0.1 / 0.5)
            l.shadowNearPlane = 0.1f;
#if UNITY_EDITOR
            l.lightmapBakeType = LightmapBakeType.Mixed; // editor bake only; a player lights everything in realtime
#endif
            l.bounceIntensity = 1f;
            var data = go.AddComponent<UniversalAdditionalLightData>();
            data.usePipelineSettings = true;
            if (FixedLampShadowTiers)
                SetShadowTier(data, type == LightType.Spot
                    ? UniversalAdditionalLightData.AdditionalLightsShadowResolutionTierHigh
                    : UniversalAdditionalLightData.AdditionalLightsShadowResolutionTierMedium);
            return l;
        }

        /// <summary>
        /// The tier setter throws outside play mode, so editor previews write the serialized field instead
        /// (same result: the editor preview matches the app).
        /// </summary>
        static void SetShadowTier(UniversalAdditionalLightData data, int tier)
        {
            if (Application.isPlaying)
            {
                data.additionalLightsShadowResolutionTier = tier;
                return;
            }
#if UNITY_EDITOR
            var so = new UnityEditor.SerializedObject(data);
            var p = so.FindProperty("m_AdditionalLightsShadowResolutionTier");
            if (p == null) return;
            p.intValue = tier;
            so.ApplyModifiedPropertiesWithoutUndo();
#endif
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
