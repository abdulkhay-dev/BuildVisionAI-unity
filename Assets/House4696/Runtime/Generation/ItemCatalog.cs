using System;
using System.Collections.Generic;
using House4696.Core;
using House4696.Catalog;
using House4696.Landscape;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>Typed access to an item's JSON parameters with defaults; materials resolve by name.</summary>
    public sealed class ItemParams
    {
        readonly JObject _o;
        readonly MaterialResolver _mats;
        public ItemParams(JObject o, MaterialResolver mats) { _o = o ?? new JObject(); _mats = mats; }

        JToken T(string k) => _o.TryGetValue(k, StringComparison.OrdinalIgnoreCase, out var t) ? t : null;
        public bool Has(string k) => T(k) != null;
        public float F(string k, float d) { var t = T(k); return t != null && (t.Type == JTokenType.Float || t.Type == JTokenType.Integer) ? t.Value<float>() : d; }
        public int I(string k, int d) { var t = T(k); return t != null && (t.Type == JTokenType.Integer || t.Type == JTokenType.Float) ? (int)t.Value<float>() : d; }
        public bool B(string k, bool d) { var t = T(k); return t != null && t.Type == JTokenType.Boolean ? t.Value<bool>() : d; }
        public string S(string k, string d) { var t = T(k); return t != null && t.Type == JTokenType.String ? t.Value<string>() : d; }
        public Material M(string k, Material d) { var s = S(k, null); return s == null ? d : _mats.Get(s, d); }
        /// <summary>Material or null when the parameter is "none"/missing and no default is given.</summary>
        public Material MOpt(string k, Material d) { var s = S(k, null); return s == "none" ? null : s == null ? d : _mats.Get(s, d); }
        public Vector3 V3(string k, Vector3 d)
        {
            var t = T(k) as JArray;
            return t != null && t.Count == 3 ? new Vector3(t[0].Value<float>(), t[1].Value<float>(), t[2].Value<float>()) : d;
        }
    }

    /// <summary>Everything an item model needs while building in its own local space (front faces -Z, floor at y = 0; the placement turns -Z to the item's rotation).</summary>
    public sealed class ItemBuild
    {
        /// <summary>Solid furniture (gets colliders) and soft decor (no colliders).</summary>
        public readonly MeshBuilder F = new MeshBuilder(), D = new MeshBuilder();
        /// <summary>Glass of the body (vitrine shelves): no shadows, no collider.</summary>
        public readonly MeshBuilder G = new MeshBuilder();
        /// <summary>Parts that move (furniture doors, drawers): each on its own pivot with a <see cref="House4696.Runtime.Door"/>.</summary>
        public readonly List<ItemMover> Movers = new List<ItemMover>();
        public readonly List<(MeshBuilder mb, Vector3 pos)> Plants = new List<(MeshBuilder, Vector3)>();
        public ItemParams P;
        public HouseContext C;
        /// <summary>Set by library models: the builder places this prefab instead of generated meshes.</summary>
        public ExternalCatalog.ModelEntry External;
        public InteriorMaterials M => C.M;
        public FurnitureKit K => C.Kit;
        public VegetationFactory Veg => C.Veg;
    }

    /// <summary>
    /// A moving part of an item, built in the item's local space like the rest: the builder puts it on a pivot at
    /// <see cref="Pivot"/> that turns about Y by <see cref="Angle"/> (a door) or slides by <see cref="Slide"/> (a drawer).
    /// </summary>
    public sealed class ItemMover
    {
        public string Name;
        public readonly MeshBuilder Solid = new MeshBuilder(), Glass = new MeshBuilder();
        public Vector3 Pivot;
        /// <summary>Orientation of the pivot: its local Y is the hinge line (identity = vertical; a flap turns it onto X).</summary>
        public Quaternion Frame = Quaternion.identity;
        public House4696.Runtime.DoorMotion Motion = House4696.Runtime.DoorMotion.Swing;
        public float Angle = 95f;
        public Vector3 Slide;
        /// <summary>Built open (a preview of the interior).</summary>
        public bool Open;
    }

    public sealed class ItemModel
    {
        public string Id, Name, Category;
        public string Params;   // human/AI readable parameter list with defaults
        public Action<ItemBuild> Build;
    }

    /// <summary>
    /// Catalogue of placeable objects (furniture, fixtures, decor, plants). Ids are stable snake_case names used by
    /// house documents and the MCP tools; each entry documents its parameters.
    /// </summary>
    public static class ItemCatalog
    {
        static readonly Dictionary<string, ItemModel> Models = new Dictionary<string, ItemModel>(StringComparer.OrdinalIgnoreCase);
        public static IEnumerable<ItemModel> All { get { EnsureExternal(); return Models.Values; } }
        /// <summary>Models offered to people and the AI: all but "_…" test pieces (they build, for previews, but are not listed).</summary>
        public static IEnumerable<ItemModel> Listed { get { foreach (var m in All) if (!m.Id.StartsWith("_")) yield return m; } }
        public static ItemModel Get(string id) { EnsureExternal(); return id != null && Models.TryGetValue(id, out var m) ? m : null; }

        static bool _external;
        static readonly HashSet<string> _caseIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        /// <summary>
        /// Re-reads the case furniture catalogue (Resources/Casegoods) into the item catalogue: designs and models added or
        /// changed since the first use (the editor previews call it after importing new designs).
        /// </summary>
        public static void ReloadCasegoods()
        {
            House4696.Casegoods.CaseCatalog.Reload();
            foreach (var id in _caseIds) Models.Remove(id);
            _caseIds.Clear();
            if (_external) AddCasegoods();
            House4696.Medical.MedCatalog.Reload();
            foreach (var id in _medIds) Models.Remove(id);
            _medIds.Clear();
            if (_external) AddMedical();
        }

        /// <summary>Library models (scans, Blender models) join the catalogue under their ids once the content is loaded.</summary>
        static void EnsureExternal()
        {
            if (_external) return;
            _external = true;
            AddCasegoods();
            AddMedical();
            var ext = ExternalCatalog.Load();
            if (ext == null) return;
            foreach (var e in ext.Models)
            {
                if (string.IsNullOrEmpty(e.PrefabPath) || Models.ContainsKey(e.Id)) continue;
                var entry = e;
                Models[e.Id] = new ItemModel { Id = e.Id, Name = e.Name, Category = e.Category, Params = e.ParamsText(), Build = b => b.External = entry };
            }
        }

        static readonly List<string> _medIds = new List<string>();

        /// <summary>Medical equipment of the manufacturers' catalogues (Resources/Medical): parametric, built from their designs.</summary>
        static void AddMedical()
        {
            foreach (var mm in House4696.Medical.MedCatalog.File.Models)
            {
                if (string.IsNullOrEmpty(mm.Id) || Models.ContainsKey(mm.Id)) continue;
                // listed with the whole inventory: only devices whose design is drawn join the library
                if (House4696.Medical.MedCatalog.Design(mm.Design ?? mm.Id) == null) continue;
                var entry = mm;
                Models[mm.Id] = new ItemModel
                {
                    Id = mm.Id, Name = $"{mm.NameRu ?? mm.Name} {mm.Code}".Trim(), Category = "med_" + (mm.Category ?? "other"), Params = "",
                    Build = b => House4696.Medical.MedBuilder.Build(b, entry),
                };
                _medIds.Add(mm.Id);
            }
        }

        /// <summary>Case furniture of the manufacturers' catalogues (Resources/Casegoods): parametric, built from their designs.</summary>
        static void AddCasegoods()
        {
            foreach (var cm in House4696.Casegoods.CaseCatalog.File.Models)
            {
                if (string.IsNullOrEmpty(cm.Id) || Models.ContainsKey(cm.Id)) continue;
                var entry = cm;
                var fins = House4696.Casegoods.CaseCatalog.FinishesOf(cm);
                string ps = $"finish={cm.Finish ?? (fins.Count > 0 ? fins[0] : "")}" + (fins.Count > 1 ? $" ({string.Join(" | ", fins)})" : "") + " open=false";
                Models[cm.Id] = new ItemModel
                {
                    Id = cm.Id, Name = $"{cm.Name} {cm.Code}".Trim(), Category = cm.Category ?? "storage", Params = ps,
                    Build = b => House4696.Casegoods.CaseBuilder.Build(b, entry),
                };
                _caseIds.Add(cm.Id);
            }
        }

        static void R(string id, string name, string category, string ps, Action<ItemBuild> build) =>
            Models[id] = new ItemModel { Id = id, Name = name, Category = category, Params = ps, Build = build };

        static ItemCatalog()
        {
            // ------------------------------------------------------------ seating
            R("sofa", "Диван", "seating", "length=3.2 depth=1.0 fabric=boucle accent=terracotta chaise=false",
                b => b.K.Sofa(b.F, b.P.F("length", 3.2f), b.P.F("depth", 1f), b.P.M("fabric", b.M.Boucle), b.P.M("accent", b.M.Terracotta), b.P.B("chaise", false)));
            R("armchair", "Кресло", "seating", "fabric=linen wood=walnut",
                b => b.K.Armchair(b.F, b.P.M("fabric", b.M.Linen), b.P.M("wood", b.M.Walnut)));
            R("lounge_chair", "Лаунж-кресло", "seating", "", b => b.K.LoungeChair(b.F));
            R("chaise_longue", "Шезлонг", "seating", "leather=leather_white pillow=charcoal",
                b => b.K.Chaise(b.F, b.P.M("leather", b.M.LeatherWhite), b.P.M("pillow", b.M.Charcoal)));
            R("dining_chair", "Стул обеденный", "seating", "fabric=linen", b => b.K.DiningChair(b.F, b.P.M("fabric", b.M.Linen)));
            R("bar_stool", "Барный стул", "seating", "", b => b.K.BarStool(b.F));
            R("bench", "Скамья с подушкой", "seating", "length=1.4 wood=oak_light cushion=boucle", Bench);

            // ------------------------------------------------------------ tables & storage
            R("round_table", "Круглый столик", "tables", "radius=0.5 height=0.34 material=travertine",
                b => b.K.RoundTable(b.F, b.P.F("radius", 0.5f), b.P.F("height", 0.34f), b.P.M("material", b.M.Travertine)));
            R("wire_table", "Проволочный столик", "tables", "radius=0.22 height=0.42", b => b.K.WireTable(b.F, b.P.F("radius", 0.22f), b.P.F("height", 0.42f)));
            R("dining_table", "Обеденный стол", "tables", "length=2.3 width=1.0", b => b.K.DiningTable(b.F, b.P.F("length", 2.3f), b.P.F("width", 1f)));
            R("desk", "Письменный стол", "tables", "length=1.4", b => b.K.Desk(b.F, b.P.F("length", 1.4f)));
            R("wardrobe", "Шкаф", "storage", "length=2.0 height=2.6 depth=0.6 front=gloss_white door_width=0.5 handles=true",
                b => b.K.Wardrobe(b.F, b.P.F("length", 2f), b.P.F("height", 2.6f), b.P.F("depth", 0.6f), b.P.M("front", b.M.GlossWhite),
                    b.P.F("door_width", 0.5f), b.P.B("handles", true)));
            R("fluted_cabinet", "Комод с рифлёными фасадами", "storage", "length=1.6 height=0.7 depth=0.45 lift=0.12",
                b => b.K.FlutedCabinet(b.F, b.P.F("length", 1.6f), b.P.F("height", 0.7f), b.P.F("depth", 0.45f), b.P.F("lift", 0.12f)));
            R("cubby_shelf", "Стеллаж", "storage", "width=0.9 height=2.4 depth=0.32 seed=1",
                b => b.K.CubbyShelf(b.F, b.D, b.P.F("width", 0.9f), b.P.F("height", 2.4f), b.P.F("depth", 0.32f), b.P.I("seed", 1)));
            R("tv_console", "ТВ-консоль с телевизором", "storage", "length=1.6 lift=0.36 tv_width=1.1",
                b => b.K.TvConsole(b.F, b.D, b.P.F("length", 1.6f), b.P.F("lift", 0.36f), b.P.F("tv_width", 1.1f)));
            R("media_wall", "Медиастена с камином", "storage", "length=3.7 height=6.4",
                b => b.K.MediaWall(b.F, b.P.F("length", 3.7f), b.P.F("height", 6.4f)));
            R("nightstand", "Прикроватная тумба", "bedroom", "lamp=true", b => b.K.Nightstand(b.F, b.P.B("lamp", true)));
            R("bed", "Кровать", "bedroom", "width=1.6 length=2.0 headboard=linen throw=sage seed=1",
                b => b.K.Bed(b.F, b.P.F("width", 1.6f), b.P.F("length", 2f), b.P.M("headboard", b.M.Linen), b.P.M("throw", b.M.Sage), b.P.I("seed", 1)));

            // ------------------------------------------------------------ kitchen & bath
            R("kitchen_base", "Кухня: нижние модули", "kitchen", "length=3.0 sink_at=NaN hob_at=NaN (from the centre)",
                b => b.K.KitchenBase(b.F, b.P.F("length", 3f), b.P.F("sink_at", float.NaN), b.P.F("hob_at", float.NaN)));
            R("tall_units", "Кухня: пенал с техникой", "kitchen", "length=2.1 height=3.0 front=gloss_white",
                b => b.K.TallUnits(b.F, b.P.F("length", 2.1f), b.P.F("height", 3f), b.P.M("front", b.M.GlossWhite)));
            R("kitchen_island", "Кухонный остров", "kitchen", "length=2.0 width=1.0", b => b.K.Island(b.F, b.P.F("length", 2f), b.P.F("width", 1f)));
            R("vanity", "Тумба с раковиной и зеркалом", "bath", "length=1.1 basins=1 mirror_height=0.7",
                b => b.K.Vanity(b.F, b.P.F("length", 1.1f), b.P.I("basins", 1), b.P.F("mirror_height", 0.7f)));
            R("toilet", "Унитаз подвесной", "bath", "", b => b.K.Toilet(b.F));
            R("bathtub", "Ванна отдельностоящая", "bath", "length=1.6 width=0.76", b => b.K.Bathtub(b.F, b.P.F("length", 1.6f), b.P.F("width", 0.76f)));
            R("shower", "Душевая с перегородкой", "bath", "width=1.3 depth=1.0 screen_from=0 screen_to=width height=2.4 (origin = corner)",
                b =>
                {
                    float w = b.P.F("width", 1.3f), d = b.P.F("depth", 1f);
                    b.K.Shower(b.F, 0, w, 0, d, b.P.F("screen_from", 0f), b.P.F("screen_to", w), b.P.F("height", 2.4f));
                });
            R("towel_rail", "Полотенцесушитель", "bath", "width=0.5 height=1.3", b => b.K.TowelRail(b.F, b.P.F("width", 0.5f), b.P.F("height", 1.3f)));

            // ------------------------------------------------------------ lighting fixtures (geometry; light sources are separate)
            R("pendant_globe", "Подвес-шар", "lighting", "drop=1.0 radius=0.13 (position = ceiling point)",
                b => b.K.PendantGlobe(b.D, Vector3.zero, b.P.F("drop", 1f), b.P.F("radius", 0.13f)));
            R("linear_pendant", "Линейный подвес", "lighting", "drop=1.45 length=1.8 (position = ceiling point, runs along local X)",
                b => b.K.LinearPendant(b.D, Vector3.zero, b.P.F("drop", 1.45f), b.P.F("length", 1.8f), false));
            R("chandelier", "Люстра из шаров", "lighting", "spread=2.1 min_drop=0.9 max_drop=2.6 count=21 seed=11 (position = ceiling point)",
                b => b.K.Chandelier(b.D, Vector3.zero, b.P.F("spread", 2.1f), b.P.F("min_drop", 0.9f), b.P.F("max_drop", 2.6f), b.P.I("count", 21), b.P.I("seed", 11)));
            R("table_lamp", "Настольная лампа", "lighting", "radius=0.16", b => b.K.TableLamp(b.D, Vector3.zero, b.P.F("radius", 0.16f)));
            R("floor_lamp", "Торшер", "lighting", "", b => b.K.FloorLamp(b.F));
            R("downlight", "Встроенный светильник", "lighting", "(position = ceiling point)", b => b.K.Downlight(b.D, Vector3.zero));
            R("led_slot", "Линейный LED-профиль", "lighting", "length=3.0 (position = ceiling point at the start, runs along local X)",
                b => b.K.LedSlot(b.D, Vector3.zero, Vector3.right * b.P.F("length", 3f)));

            // ------------------------------------------------------------ walls & textiles
            R("slat_panel", "Реечная панель на стену", "walls", "width=3.2 height=2.8 (back against the wall, faces the rotation)",
                b => { float w = b.P.F("width", 3.2f); b.K.SlatPanel(b.F, -w * 0.5f, w * 0.5f, 0, b.P.F("height", 2.8f), 0f); });
            R("artwork", "Картина", "decor", "width=1.0 height=1.2 cell=0 (position = canvas centre on the wall, faces the rotation)",
                b => b.K.Artwork(b.F, Vector3.zero, Vector3.back, b.P.F("width", 1f), b.P.F("height", 1.2f), b.P.I("cell", 0)));
            R("mirror_round", "Круглое зеркало", "decor", "radius=0.45 (position = centre on the wall, faces the rotation)", MirrorRound);
            R("rug", "Ковёр", "textiles", "width=2.4 depth=1.7 material=rug border=none",
                b => b.K.Rug(b.D, b.P.F("width", 2.4f), b.P.F("depth", 1.7f), b.P.M("material", b.M.Rug), b.P.MOpt("border", null)));
            R("drapes", "Портьеры", "textiles", "width=0.4 height=2.7 material=linen (runs along local X)", Drapes);
            R("panel", "Панель / плитка / полка", "walls", "size=[1,1,0.02] material=travertine round=0 decor=false (position = bottom centre)", Panel);

            // ------------------------------------------------------------ decor
            R("vase", "Ваза", "decor", "height=0.3 material=stoneware kind=0", b => b.K.Vase(b.D, Vector3.zero, b.P.F("height", 0.3f), b.P.M("material", b.M.Stoneware), b.P.I("kind", 0)));
            R("books", "Книги", "decor", "span=0.2 thickness=0.035 count=3 lying=true",
                b => b.K.Books(b.D, Vector3.zero, b.P.F("span", 0.2f), b.P.F("thickness", 0.035f), b.P.I("count", 3), b.P.B("lying", true)));
            R("twigs", "Ветки в вазе", "decor", "height=0.8 seed=1", b => b.K.Twigs(b.D, Vector3.zero, b.P.F("height", 0.8f), b.P.I("seed", 1)));

            // ------------------------------------------------------------ plants
            R("plant_tree", "Дерево в кашпо", "plants", "height=2.0 radius=0.6 seed=1 pot_radius=0.28 pot_height=0.5 pot=stoneware", PlantTree);
            R("plant_grass", "Злаки в кашпо", "plants", "seed=1 pot_radius=0.2 pot_height=0.36", PlantGrass);

            // ------------------------------------------------------------ utility & outdoor
            R("boiler", "Котёл и бойлер", "utility", "", Boiler);
            R("washer_stack", "Стиральная и сушильная машины", "utility", "", WasherStack);
            R("rattan_lounge_chair", "Плетёное кресло", "outdoor", "", RattanChair);
            R("bistro_set", "Столик с двумя стульями", "outdoor", "", BistroSet);
            R("sun_lounger", "Шезлонг у бассейна", "outdoor", "cushion=cushion frame=furniture_dark back=45 (изголовье к +Z, ноги к фасаду -Z)", SunLounger);
        }

        // ------------------------------------------------------------------ composite models
        static void Bench(ItemBuild b)
        {
            float l = b.P.F("length", 1.4f) * 0.5f;
            var wood = b.P.M("wood", b.M.OakLight);
            b.F.RoundBox(new Vector3(-l, 0.36f, -0.42f), new Vector3(l, 0.42f, 0f), 0.008f, wood);
            b.F.Box(new Vector3(-l + 0.05f, 0, -0.38f), new Vector3(-l + 0.09f, 0.36f, -0.04f), wood);
            b.F.Box(new Vector3(l - 0.09f, 0, -0.38f), new Vector3(l - 0.05f, 0.36f, -0.04f), wood);
            b.F.RoundBox(new Vector3(-l + 0.02f, 0.42f, -0.4f), new Vector3(l - 0.02f, 0.5f, -0.02f), 0.03f, b.P.M("cushion", b.M.Boucle));
        }

        static void MirrorRound(ItemBuild b)
        {
            float r = b.P.F("radius", 0.45f);
            using (b.F.Place(Vector3.zero, Quaternion.FromToRotation(Vector3.down, Vector3.back)))
            {
                b.F.Disk(Vector3.zero, r, b.M.Mirror, true, 48);
                b.F.Lathe(Vector3.zero, new[] { new Vector2(r + 0.012f, 0.012f), new Vector2(r + 0.012f, -0.006f), new Vector2(r, -0.006f) }, 48, b.M.Brass);
            }
        }

        /// <summary>Heavy linen drape: soft vertical folds along local X, hanging from a black rod.</summary>
        static void Drapes(ItemBuild b)
        {
            float w = b.P.F("width", 0.4f), h = b.P.F("height", 2.7f);
            var m = b.P.M("material", b.M.Linen);
            int n = Mathf.Max(3, Mathf.RoundToInt(w / 0.065f));
            for (int i = 0; i < n; i++)
            {
                float x = Mathf.Lerp(0, w, (i + 0.5f) / n);
                float dz = i % 2 == 0 ? 0.025f : -0.01f;
                b.D.Lathe(new Vector3(x, 0.01f, dz), new[] { new Vector2(0.042f, 0), new Vector2(0.04f, h - 0.01f) }, 10, m);
            }
            b.D.Rod(new Vector3(-0.1f, h - 0.03f, 0), new Vector3(w + 0.1f, h - 0.03f, 0), 0.012f, b.M.BlackMetal);
        }

        static void Panel(ItemBuild b)
        {
            var s = b.P.V3("size", new Vector3(1, 1, 0.02f));
            var m = b.P.M("material", b.M.Travertine);
            var mb = b.P.B("decor", false) ? b.D : b.F;
            var mn = new Vector3(-s.x * 0.5f, 0, -s.z * 0.5f);
            var mx = new Vector3(s.x * 0.5f, s.y, s.z * 0.5f);
            float r = b.P.F("round", 0f);
            if (r > 0f) mb.RoundBox(mn, mx, r, m); else mb.Box(mn, mx, m);
        }

        static void PlantTree(ItemBuild b)
        {
            float potR = b.P.F("pot_radius", 0.28f), potH = b.P.F("pot_height", 0.5f);
            b.K.Planter(b.F, Vector3.zero, potR, potH, b.P.M("pot", b.M.Stoneware));
            b.Plants.Add((b.Veg.BroadleafTree(b.P.F("height", 2f), b.P.F("radius", 0.6f), b.P.I("seed", 1)), Vector3.up * (potH * 0.85f)));
        }

        static void PlantGrass(ItemBuild b)
        {
            float potR = b.P.F("pot_radius", 0.2f), potH = b.P.F("pot_height", 0.36f);
            b.K.Planter(b.F, Vector3.zero, potR, potH, b.P.M("pot", b.M.Charcoal));
            b.Plants.Add((b.Veg.GrassClump(potR * 1.3f, 0.7f, 70, 2, 0, 0f, b.P.I("seed", 1)), Vector3.up * (potH * 0.88f)));
        }

        /// <summary>Wall boiler with pipes and a floor-standing cylinder; origin = wall point, faces -Z.</summary>
        static void Boiler(ItemBuild b)
        {
            b.F.RoundBox(new Vector3(-0.225f, 1.3f, -0.36f), new Vector3(0.225f, 2.05f, 0f), 0.02f, b.M.Ceramic);
            for (int i = 0; i < 3; i++)
                b.F.Rod(new Vector3(-0.125f + i * 0.12f, 1.3f, -0.18f), new Vector3(-0.125f + i * 0.12f, 0.2f, -0.18f), 0.014f, b.M.Chrome);
            b.F.Cylinder(new Vector3(0.825f, 0, -0.31f), 0.28f, 1.7f, b.M.Ceramic, 28);
        }

        /// <summary>Washer/dryer stack with round doors on the front (-Z) and a shelf above.</summary>
        static void WasherStack(ItemBuild b)
        {
            b.F.RoundBox(new Vector3(-0.31f, 0, -0.315f), new Vector3(0.31f, 0.85f, 0.315f), 0.02f, b.M.Ceramic);
            b.F.RoundBox(new Vector3(-0.31f, 0.86f, -0.315f), new Vector3(0.31f, 1.71f, 0.315f), 0.02f, b.M.Ceramic);
            foreach (var y in new[] { 0.42f, 1.28f })
                using (b.F.Place(new Vector3(0, y, -0.315f), Quaternion.Euler(-90f, 0, 0)))
                    b.F.Cylinder(new Vector3(0, -0.01f, 0), 0.2f, 0.012f, b.M.BlackGlass, 28);
        }

        static void RattanChair(ItemBuild b)
        {
            var rattan = b.C.Lib.Rattan; var cushion = b.C.Lib.Cushion;
            b.F.Box(new Vector3(-0.36f, 0, -0.36f), new Vector3(0.36f, 0.42f, 0.36f), BoxMats.All(rattan));
            b.F.Box(new Vector3(-0.36f, 0.42f, 0.22f), new Vector3(0.36f, 0.86f, 0.36f), BoxMats.All(rattan));
            b.F.Box(new Vector3(-0.36f, 0.42f, -0.36f), new Vector3(-0.26f, 0.64f, 0.36f), BoxMats.All(rattan));
            b.F.Box(new Vector3(0.26f, 0.42f, -0.36f), new Vector3(0.36f, 0.64f, 0.36f), BoxMats.All(rattan));
            b.F.Box(new Vector3(-0.26f, 0.42f, -0.3f), new Vector3(0.26f, 0.52f, 0.22f), BoxMats.All(cushion));
        }

        /// <summary>Pool sun lounger, 0.7 × 2.0 m: dark aluminium frame, a thick cushion, the backrest raised at the +Z end.</summary>
        static void SunLounger(ItemBuild b)
        {
            var frame = b.P.M("frame", b.C.Lib.FurnitureDark);
            var cushion = b.P.M("cushion", b.C.Lib.Cushion);
            float back = Mathf.Clamp(b.P.F("back", 45f), 0f, 80f);
            const float hw = 0.34f, z0 = -1.0f, z1 = 1.0f, hinge = 0.3f, bedY = 0.26f;
            // side rails and legs
            foreach (float x in new[] { -hw, hw - 0.03f })
            {
                b.F.Box(new Vector3(x, bedY - 0.06f, z0), new Vector3(x + 0.03f, bedY, z1), frame);
                b.F.Box(new Vector3(x, 0f, z0 + 0.05f), new Vector3(x + 0.03f, bedY - 0.06f, z0 + 0.09f), frame);
                b.F.Box(new Vector3(x, 0f, z1 - 0.12f), new Vector3(x + 0.03f, bedY - 0.06f, z1 - 0.08f), frame);
            }
            b.F.Box(new Vector3(-hw, bedY - 0.06f, z0), new Vector3(hw, bedY - 0.02f, z0 + 0.03f), frame);
            // flat part of the cushion
            b.D.RoundBox(new Vector3(-hw + 0.02f, bedY - 0.02f, z0 + 0.02f), new Vector3(hw - 0.02f, bedY + 0.07f, hinge), 0.03f, cushion);
            // backrest: frame plate and cushion tilted about the hinge line
            using (b.F.Place(new Vector3(0, bedY, hinge), Quaternion.Euler(-back, 0, 0)))
                b.F.Box(new Vector3(-hw, -0.04f, 0f), new Vector3(hw, -0.01f, z1 - hinge), frame);
            using (b.D.Place(new Vector3(0, bedY, hinge), Quaternion.Euler(-back, 0, 0)))
                b.D.RoundBox(new Vector3(-hw + 0.02f, -0.02f, 0.01f), new Vector3(hw - 0.02f, 0.07f, z1 - hinge - 0.02f), 0.03f, cushion);
        }

        static void BistroSet(ItemBuild b)
        {
            var dark = b.C.Lib.FurnitureDark;
            b.F.Box(new Vector3(-0.04f, 0, -0.04f), new Vector3(0.04f, 0.72f, 0.04f), BoxMats.All(dark));
            b.F.Cylinder(new Vector3(0, 0.72f, 0), 0.45f, 0.03f, dark, 20);
            foreach (float dx in new[] { -0.75f, 0.75f })
            {
                Vector3 ch = new Vector3(dx, 0, -0.1f);
                b.F.Box(ch + new Vector3(-0.23f, 0.44f, -0.23f), ch + new Vector3(0.23f, 0.5f, 0.23f), BoxMats.All(dark));
                float back = dx < 0 ? -0.23f : 0.19f;
                b.F.Box(ch + new Vector3(back, 0.5f, -0.23f), ch + new Vector3(back + 0.04f, 0.92f, 0.23f), BoxMats.All(dark));
                foreach (var lx in new[] { -0.2f, 0.18f })
                foreach (var lz in new[] { -0.2f, 0.18f })
                    b.F.Box(ch + new Vector3(lx, 0, lz), ch + new Vector3(lx + 0.025f, 0.44f, lz + 0.025f), BoxMats.All(dark));
            }
        }
    }
}
