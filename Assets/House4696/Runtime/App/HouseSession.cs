using System;
using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using House4696.Setup;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace House4696.App
{
    /// <summary>
    /// The open project: its document, the generated house in the scene and an undo history. Every change goes
    /// through <see cref="Apply"/>: validate → save → rebuild (a house regenerates in well under a second).
    /// </summary>
    public sealed class HouseSession
    {
        const int UndoDepth = 30;
        public const uint HouseRenderingLayer = 1u, SiteRenderingLayer = 2u;

        public readonly ProjectStore Store;
        public string ProjectId { get; private set; }
        public HouseDocument Doc { get; private set; }
        public HouseBuildResult Result { get; private set; }
        public List<Issue> Issues { get; private set; } = new List<Issue>();
        public long LastBuildMs { get; private set; }
        /// <summary>Set after a rebuild: the reflection probes should be re-captured once the GI has settled.</summary>
        public bool ProbesDirty { get; set; }
        public event Action Rebuilt;
        /// <summary>Raised after a project was opened, created or closed (by the UI or by the AI).</summary>
        public event Action ProjectChanged;
        public const string LastProjectPref = "house.lastProject";

        readonly MaterialLibrary _mats;
        readonly List<string> _undo = new List<string>();
        SceneWriter _writer;

        public HouseSession(ProjectStore store, MaterialLibrary mats)
        {
            Store = store; _mats = mats;
        }

        public bool HasProject => Doc != null;
        public MaterialLibrary Mats => _mats;
        public int UndoCount => _undo.Count;

        public void Open(string id)
        {
            var doc = Store.Load(id);
            ProjectId = id;
            Doc = doc;
            _undo.Clear();
            PlayerPrefs.SetString(LastProjectPref, id);
            Rebuild();
            ProjectChanged?.Invoke();
        }

        public void Close()
        {
            Teardown();
            ProjectId = null; Doc = null; Result = null; _undo.Clear();
            ProjectChanged?.Invoke();
        }

        /// <summary>
        /// Creates a project from a template (<c>empty</c> or a bundled sample) and opens it.
        /// </summary>
        public string Create(string name, string description, string template, string author)
        {
            HouseDocument doc;
            template = string.IsNullOrEmpty(template) ? "empty" : template;
            if (template == "empty")
            {
                doc = new HouseDocument();
                doc.Levels.Add(new LevelDef { Id = "ground", Name = "1 этаж", Elevation = 0.3f, Height = 2.8f, Slab = 0.3f });
            }
            else
            {
                if (!ProjectStore.Samples().TryGetValue(template, out var path))
                    throw new ArgumentException($"нет шаблона '{template}'. Есть: empty, {string.Join(", ", ProjectStore.Samples().Keys)}");
                doc = HouseJson.Deserialize(System.IO.File.ReadAllText(path));
            }
            doc.Meta = new HouseMeta
            {
                Name = string.IsNullOrWhiteSpace(name) ? "Новый дом" : name.Trim(),
                Description = string.IsNullOrWhiteSpace(description) ? doc.Meta?.Description : description.Trim(),
                Author = author, Created = DateTime.UtcNow.ToString("yyyy-MM-dd"),
            };
            string id = Store.Create(doc);
            Open(id);
            return id;
        }

        /// <summary>Renames a project (metadata only: the open house is not rebuilt).</summary>
        public void Rename(string id, string name)
        {
            if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("пустое название");
            if (id == ProjectId && HasProject)
            {
                Doc.Meta ??= new HouseMeta();
                Doc.Meta.Name = name.Trim();
                Store.Save(id, Doc);
                ProjectChanged?.Invoke();
                return;
            }
            var doc = Store.Load(id);
            doc.Meta ??= new HouseMeta();
            doc.Meta.Name = name.Trim();
            Store.Save(id, doc);
        }

        /// <summary>Moves a project to the trash; the open one is closed first.</summary>
        public void Delete(string id)
        {
            bool current = id == ProjectId;
            Store.Delete(id);
            if (current) Close();
        }

        /// <summary>Makes <paramref name="next"/> the current document (saved, rebuilt); the old one goes to the undo stack.</summary>
        public List<Issue> Apply(HouseDocument next)
        {
            if (!HasProject) throw new InvalidOperationException("нет открытого проекта — открой или создай проект");
            _undo.Add(HouseJson.Serialize(Doc));
            if (_undo.Count > UndoDepth) _undo.RemoveAt(0);
            Doc = next;
            Store.Save(ProjectId, Doc);
            Rebuild();
            return Issues;
        }

        public bool Undo()
        {
            if (_undo.Count == 0) return false;
            Doc = HouseJson.Deserialize(_undo[_undo.Count - 1]);
            _undo.RemoveAt(_undo.Count - 1);
            Store.Save(ProjectId, Doc);
            Rebuild();
            return true;
        }

        public void Rebuild()
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            Teardown();
            Issues = HouseValidator.Validate(Doc);
            _writer = new SceneWriter();
            // generation works on a copy: the builder normalises some fields (level order) in place
            Result = HouseBuilder.Build(HouseJson.Clone(Doc), _mats, _writer);
            Issues.AddRange(Result.Checks);
            PrepareScene();
            LastBuildMs = sw.ElapsedMilliseconds;
            ProbesDirty = true;
            Rebuilt?.Invoke();
        }

        void PrepareScene()
        {
            int layer = LayerMask.NameToLayer("House");
            if (layer >= 0)
                foreach (var t in Result.House.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            foreach (var p in Result.House.GetComponentsInChildren<ReflectionProbe>(true))
            {
                p.mode = ReflectionProbeMode.Realtime;
                p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
                p.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            }
            AssignExteriorShellLayer(Result.House, Doc);   // perf plan step 8 / R3: lamps stop lighting the outer shell
            // realtime GI only for the house: the garden (grass blades, trees) would double its cost for no
            // visible gain — the GI volume's rendering-layer mask takes layer 1, the garden moves to layer 2
            if (Result.Site != null)
            {
                foreach (var r in Result.Site.GetComponentsInChildren<Renderer>(true)) r.renderingLayerMask = SiteRenderingLayer;
                foreach (var t in Result.Site.GetComponentsInChildren<Terrain>(true)) t.renderingLayerMask = SiteRenderingLayer;
                ReduceGardenShadows(Result.Site, Result.Footprint);
            }
            var site = Doc.Site ?? new SiteDef();
            if (RenderSettings.sun != null)
                RenderSettings.sun.transform.rotation = Quaternion.Euler(EnvironmentBuilder.SunFrom(site.SunAzimuth, site.SunElevation));

            var cam = Camera.main;
            var viewer = cam != null ? cam.GetComponent<HouseViewer>() : null;
            if (viewer != null)
            {
                var walk = Result.Walk.Length > 0 ? Result.Walk
                    : new[] { new WalkPoint { Name = "Вход", Feet = new Vector3(Result.Footprint.center.x, 0.05f, Result.Footprint.yMin - 3f) } };
                viewer.Configure(Result.Pivot, walk, Result.Orbit);
            }
        }

        /// <summary>Trees farther from the house than this cast no shadows (their shadows fall on lawn nobody looks at).</summary>
        const float TreeShadowReach = 30f;

        /// <summary>
        /// The garden is most of the frame cost (1.4 M triangles drawn again into every shadow cascade): grass and small
        /// plants cast no shadows (the boulder and the dwarf pines do: <see cref="House4696.Landscape.GardenPerf.PlantShadows"/>),
        /// trees only near the house. A near tree whose shadow falls away from the house casts it from a ShadowsOnly proxy
        /// (its LOD1 mesh, <see cref="House4696.Landscape.GardenPerf.TreeShadowProxies"/>); trees that shade the house or the
        /// front lawn keep their full crown. A tree is an object under "Trees" (its LOD0 renderer) with its children (LOD1, proxy).
        /// </summary>
        void ReduceGardenShadows(GameObject site, Rect footprint)
        {
            var near = footprint;
            near.xMin -= TreeShadowReach; near.yMin -= TreeShadowReach; near.xMax += TreeShadowReach; near.yMax += TreeShadowReach;
            // direction the sunlight travels, on the ground (PrepareScene points the sun from the same site data)
            var sun = Doc?.Site ?? new SiteDef();
            Vector3 light = Quaternion.Euler(EnvironmentBuilder.SunFrom(sun.SunAzimuth, sun.SunElevation)) * Vector3.forward;
            var lightXZ = new Vector2(light.x, light.z);
            bool proxies = House4696.Landscape.GardenPerf.TreeShadowProxies && lightXZ.sqrMagnitude > 1e-4f;
            lightXZ = proxies ? lightXZ.normalized : Vector2.zero;
            var proxied = new List<Transform>();
            foreach (var r in site.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (r.shadowCastingMode == ShadowCastingMode.ShadowsOnly) continue;   // shadow proxies made by the generator (hedges)
                string name = r.gameObject.name, parent = r.transform.parent != null ? r.transform.parent.name : "";
                var mat = r.sharedMaterial != null ? r.sharedMaterial.name : "";
                bool caster = House4696.Landscape.GardenPerf.PlantShadows && parent == "Plants"
                              && (name.StartsWith("Boulder") || name.StartsWith("Plant_mugo_"));
                bool grass = !caster && (name.StartsWith("Lawn_Blades") || name.StartsWith("Pot_Grass") || mat.Contains("Grass") || mat.Contains("Blades") || parent == "Plants");
                if (grass) { r.shadowCastingMode = ShadowCastingMode.Off; continue; }
                var tree = TreeRoot(r.transform);
                if (tree == null) continue;
                // the tree's own (LOD0) bounds decide for all its renderers, as before for the single renderer
                var body = tree.GetComponent<Renderer>();
                Vector3 c = body != null ? body.bounds.center : tree.position;
                var p = new Vector2(c.x, c.z);
                if (!near.Contains(p)) { r.shadowCastingMode = ShadowCastingMode.Off; continue; }
                if (proxies && Vector2.Dot(lightXZ, (footprint.center - p).normalized) < House4696.Landscape.GardenPerf.TreeProxyAwayCos
                    && Lod1Of(tree) != null)
                {
                    r.shadowCastingMode = ShadowCastingMode.Off;
                    if (!proxied.Contains(tree)) proxied.Add(tree);
                }
            }
            foreach (var tree in proxied) AddShadowProxy(Lod1Of(tree));
        }

        /// <summary>The tree a site renderer belongs to: the object under "Trees" (LOD0), or its parent for LOD1 / proxy children.</summary>
        static Transform TreeRoot(Transform t)
        {
            var p = t.parent;
            if (p != null && p.name == "Trees") return t;
            if (p != null && p.parent != null && p.parent.name == "Trees") return p;
            string n = t.name;
            return n.StartsWith("Spruce") || n.StartsWith("Birch") || n.StartsWith("Broadleaf") ? t : null;
        }

        /// <summary>The LOD1 renderer of a tree's LODGroup (with a mesh), or null.</summary>
        static MeshRenderer Lod1Of(Transform tree)
        {
            var group = tree.GetComponent<LODGroup>();
            if (group == null || group.lodCount < 2) return null;
            var lods = group.GetLODs();
            var rs = lods[lods.Length - 1].renderers;
            var mr = rs.Length > 0 ? rs[0] as MeshRenderer : null;
            var mf = mr != null ? mr.GetComponent<MeshFilter>() : null;
            return mf != null && mf.sharedMesh != null ? mr : null;
        }

        /// <summary>A ShadowsOnly copy of the LOD1 renderer next to it, outside the LODGroup (it casts at every distance; still in the GI bake as a shadow-ray blocker).</summary>
        static void AddShadowProxy(MeshRenderer lod1)
        {
            if (lod1 == null) return;
            var go = new GameObject("ShadowProxy") { layer = lod1.gameObject.layer };
            go.transform.SetParent(lod1.transform.parent, false);
            go.transform.localPosition = lod1.transform.localPosition;
            go.transform.localRotation = lod1.transform.localRotation;
            go.transform.localScale = lod1.transform.localScale;
            go.AddComponent<MeshFilter>().sharedMesh = lod1.GetComponent<MeshFilter>().sharedMesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterials = lod1.sharedMaterials;
            mr.shadowCastingMode = ShadowCastingMode.ShadowsOnly;
            mr.receiveShadows = false;
            mr.renderingLayerMask = lod1.renderingLayerMask;
        }

        void Teardown()
        {
            if (Result != null)
            {
                if (Result.House != null) Object.Destroy(Result.House);
                if (Result.Site != null) Object.Destroy(Result.Site);
                foreach (var m in Result.CreatedMaterials) if (m != null) Object.Destroy(m);
            }
            if (_writer != null)
                foreach (var m in _writer.RuntimeMeshes) if (m != null) Object.Destroy(m);
            _writer = null;
            Result = null;
        }

        // ------------------------------------------------------------------ exterior shell rendering layer (perf plan step 8, R3)
        /// <summary>
        /// Rendering layer of the exterior shell (roofs, wall battens, exterior elements and railings): the sun lights
        /// every layer, the lamps only layer 1 (<see cref="HouseRenderingLayer"/>), so lamps without shadows stop
        /// lighting battens, belt caps and soffits through the walls. The realtime-GI mask must include it (1 | 4).
        /// </summary>
        public const uint HouseExteriorRenderingLayer = 4u;

        /// <summary>A/B switch for <see cref="HouseExteriorRenderingLayer"/> (takes effect on the next rebuild).</summary>
        public static bool ExteriorShellLayer = true;

        /// <summary>
        /// Moves the exterior shell to <see cref="HouseExteriorRenderingLayer"/>: every Roof_* (incl. Roof_Coping_*)
        /// and Battens_* (only exterior walls have battens), and element / railing renderers that are exterior: they
        /// start at or above the highest ceiling (canopies, parapets), or neither their bounds centre in plan lies in
        /// a non-terrace room outline nor any of their faces looks into a room (a point just outside the face inside
        /// a room prism). The face test keeps interior pieces that sit in the wall zone between room outlines on
        /// layer 1 (46-96: beam_left / beam_right, the lintels at the living room corners, seen lit by the
        /// chandelier); the gallery rail, nosing and LED cove stay on layer 1 as well. When unsure it keeps layer 1,
        /// i.e. today's lighting.
        /// Lamps outside every room (porch, terrace, facade lights) light layer 4 as well: the shell they stand next
        /// to stays lit by them.
        /// </summary>
        static void AssignExteriorShellLayer(GameObject house, HouseDocument doc)
        {
            if (!ExteriorShellLayer || house == null || doc == null) return;
            LevelDef lowest = null;
            var levels = new Dictionary<string, LevelDef>();
            float top = float.MinValue;
            foreach (var l in doc.Levels)
            {
                if (l == null) continue;
                if (!string.IsNullOrEmpty(l.Id)) levels[l.Id] = l;
                if (lowest == null || l.Elevation < lowest.Elevation) lowest = l;
                top = Mathf.Max(top, l.Elevation + l.Height);
            }
            var rooms = new List<ShellRoom>();                 // non-terrace room prisms
            foreach (var r in doc.Rooms)
            {
                if (r == null || r.Outline == null || r.Outline.Count < 3) continue;
                var level = r.Level != null && levels.TryGetValue(r.Level, out var lv) ? lv : lowest;
                float y0 = float.MinValue, y1 = float.MaxValue;  // no levels: the plan decides
                if (level != null)
                {
                    y0 = level.Elevation;
                    y1 = level.Elevation + (r.Height ?? level.Height);
                    top = Mathf.Max(top, y1);
                }
                if (r.Type != RoomType.Terrace) rooms.Add(new ShellRoom { Outline = r.Outline, Y0 = y0, Y1 = y1 });
            }
            if (top == float.MinValue) top = float.MaxValue;   // no levels: only the plan and face tests decide

            foreach (var mr in house.GetComponentsInChildren<Renderer>(true))
            {
                string n = mr.gameObject.name;
                bool shell = n.StartsWith("Roof_", StringComparison.Ordinal) || n.StartsWith("Battens_", StringComparison.Ordinal);
                if (!shell && IsElementOrRailing(n))
                {
                    var b = mr.bounds;
                    shell = b.min.y >= top - 0.01f || !TouchesRoom(b, rooms);
                }
                if (shell) mr.renderingLayerMask = HouseExteriorRenderingLayer;
            }

            foreach (var light in house.GetComponentsInChildren<Light>(true))
            {
                if (light.type == LightType.Directional || InRoom(light.transform.position, rooms, ExteriorLampTolerance, 0f)) continue;
                if (light.TryGetComponent<UnityEngine.Rendering.Universal.UniversalAdditionalLightData>(out var data))
                    data.renderingLayers = HouseRenderingLayer | HouseExteriorRenderingLayer;
            }
        }

        struct ShellRoom { public List<Vector2> Outline; public float Y0, Y1; }

        /// <summary>Samples sit this far outside an element face when testing whether the face looks into a room.</summary>
        const float FaceProbe = 0.1f;
        /// <summary>
        /// A face sample counts only this deep inside a room (from its outline and from its floor / ceiling): belt caps
        /// overhang the wall's inner face by ~1 cm and the upper floor by ~1.5 cm, which must not make them interior.
        /// </summary>
        const float FaceMargin = 0.05f;
        /// <summary>A lamp counts as inside a room within this height of its floor / ceiling (as HouseBuilder's room-light test).</summary>
        const float ExteriorLampTolerance = 0.05f;

        static bool IsElementOrRailing(string n) =>
            n.StartsWith("Element_", StringComparison.Ordinal) || n.StartsWith("Railing_", StringComparison.Ordinal) ||
            n.StartsWith("Decor_Element_", StringComparison.Ordinal) || n.StartsWith("Decor_Railing_", StringComparison.Ordinal);

        /// <summary>
        /// Interior piece: its bounds centre in plan lies in a room outline, or one of its six faces looks into a room
        /// (5 points per face — centre and four inner corners — <see cref="FaceProbe"/> outside the face and at least
        /// <see cref="FaceMargin"/> deep inside a room prism).
        /// </summary>
        static bool TouchesRoom(Bounds b, List<ShellRoom> rooms)
        {
            var c = b.center;
            var pc = new Vector2(c.x, c.z);
            foreach (var r in rooms)
                if (Polygon.Contains(r.Outline, pc)) return true;
            var ext = b.extents;
            for (int axis = 0; axis < 3; axis++)
            for (int sign = -1; sign <= 1; sign += 2)
            {
                var n = Vector3.zero;
                n[axis] = sign;
                int ua = (axis + 1) % 3, va = (axis + 2) % 3;
                var u = Vector3.zero; u[ua] = ext[ua] * 0.7f;
                var v = Vector3.zero; v[va] = ext[va] * 0.7f;
                var face = c + n * (ext[axis] + FaceProbe);
                if (DeepInRoom(face, rooms) || DeepInRoom(face + u + v, rooms) || DeepInRoom(face + u - v, rooms)
                    || DeepInRoom(face - u + v, rooms) || DeepInRoom(face - u - v, rooms))
                    return true;
            }
            return false;
        }

        static bool DeepInRoom(Vector3 p, List<ShellRoom> rooms) => InRoom(p, rooms, -FaceMargin, FaceMargin);

        /// <summary>
        /// p inside a room prism: its height range widened by <paramref name="yPad"/> (negative narrows), and in plan
        /// inside the outline at least <paramref name="planMargin"/> from it.
        /// </summary>
        static bool InRoom(Vector3 p, List<ShellRoom> rooms, float yPad, float planMargin)
        {
            var q = new Vector2(p.x, p.z);
            foreach (var r in rooms)
            {
                if (p.y < r.Y0 - yPad || p.y > r.Y1 + yPad || !Polygon.Contains(r.Outline, q)) continue;
                if (planMargin <= 0f || DistanceToOutline(r.Outline, q) >= planMargin) return true;
            }
            return false;
        }

        static float DistanceToOutline(List<Vector2> poly, Vector2 p)
        {
            float best = float.MaxValue;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                Vector2 a = poly[j], ab = poly[i] - a;
                float len2 = ab.sqrMagnitude;
                float t = len2 > 1e-8f ? Mathf.Clamp01(Vector2.Dot(p - a, ab) / len2) : 0f;
                best = Mathf.Min(best, (a + ab * t - p).sqrMagnitude);
            }
            return Mathf.Sqrt(best);
        }
    }
}
