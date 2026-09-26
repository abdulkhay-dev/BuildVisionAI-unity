using System;
using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>How a model attaches: stands on a floor (or a table top), hangs on a wall, hangs from the ceiling.</summary>
    public enum ItemMount { Floor, Wall, Ceiling }

    /// <summary>
    /// The item catalogue as the furniture library shows it: categories in a fixed order with Russian names, and every model
    /// with its picture and extent (both made in the editor: House 46-96 → External → Render Catalog Thumbnails writes
    /// Resources/CatalogThumbs/&lt;id&gt;.png and catalog.json) and the way it is placed. A model added after the last render
    /// has no picture and gets its extent from its first preview (<see cref="Measure"/>).
    /// </summary>
    public sealed class FurnitureCatalog
    {
        public const string ThumbFolder = "CatalogThumbs";
        public const string ManifestName = "catalog";

        public sealed class Category
        {
            public string Id, Title;
            public readonly List<Entry> Entries = new List<Entry>();
        }

        public sealed class Entry
        {
            public ItemModel Model;
            public Category Category;
            public string Id => Model.Id;
            public string Name => Model.Name;
            /// <summary>Extent with default parameters in the model's frame (front faces -Z, origin = placement point); null until measured.</summary>
            public Bounds? Local;
            public ItemMount Mount;
            /// <summary>The origin is at the back: the model stands with its back to a wall (wardrobes, beds, kitchen units, vanities).</summary>
            public bool AgainstWall;
            /// <summary>Small things that may stand on tables, shelves and sofas, not only on the floor.</summary>
            public bool OnSurfaces;
            internal string SearchText;
            Texture2D _thumb;
            bool _thumbTried;

            /// <summary>The picture from Resources (null when the editor has not rendered one).</summary>
            public Texture2D Thumbnail
            {
                get
                {
                    if (_thumbTried) return _thumb;
                    _thumbTried = true;
                    _thumb = Resources.Load<Texture2D>(ThumbFolder + "/" + Id);
                    return _thumb;
                }
            }

            /// <summary>"210 × 90 × 85 см": width across the front × depth × height (wall pieces: width × height).</summary>
            public string SizeText => Local.HasValue ? FurnitureCatalog.SizeText(Local.Value, Mount) : "";
        }

        /// <summary>Library order and names (the catalogue's own ids are English, for the AI).</summary>
        static readonly (string id, string title)[] Order =
        {
            ("seating", "Диваны и кресла"),
            ("tables", "Столы"),
            ("storage", "Шкафы и комоды"),
            ("bedroom", "Спальня"),
            ("kitchen", "Кухня"),
            ("bath", "Ванная"),
            ("lighting", "Свет"),
            ("decor", "Декор"),
            ("textiles", "Текстиль"),
            ("walls", "Отделка стен"),
            ("plants", "Растения"),
            ("utility", "Техника"),
            ("outdoor", "Сад и терраса"),
        };

        /// <summary>Categories whose small pieces may stand on other furniture (a vase on a table, a lamp on a nightstand).</summary>
        static readonly HashSet<string> SurfaceCategories = new HashSet<string> { "decor", "kitchen", "lighting", "plants" };

        public readonly List<Category> Categories = new List<Category>();
        public readonly List<Entry> All = new List<Entry>();
        readonly Dictionary<string, Entry> _byId = new Dictionary<string, Entry>(StringComparer.OrdinalIgnoreCase);

        static FurnitureCatalog _instance;

        /// <summary>The catalogue (built on first use; the item catalogue does not change while the app runs).</summary>
        public static FurnitureCatalog Instance => _instance ??= new FurnitureCatalog();

        FurnitureCatalog()
        {
            var bounds = LoadManifest();
            var cats = new Dictionary<string, Category>();
            foreach (var (id, title) in Order)
            {
                var c = new Category { Id = id, Title = title };
                cats[id] = c;
                Categories.Add(c);
            }
            foreach (var m in ItemCatalog.All)
            {
                if (!cats.TryGetValue(m.Category ?? "", out var cat))
                {
                    // a category the library does not know yet: shown last under its own id
                    cat = new Category { Id = m.Category ?? "other", Title = m.Category ?? "Разное" };
                    cats[cat.Id] = cat;
                    Categories.Add(cat);
                }
                var e = new Entry { Model = m, Category = cat };
                if (bounds.TryGetValue(m.Id, out var b)) SetExtent(e, b);
                e.SearchText = (m.Name + " " + m.Id.Replace('_', ' ') + " " + cat.Title).ToLowerInvariant();
                cat.Entries.Add(e);
                All.Add(e);
                _byId[m.Id] = e;
            }
            // Cyrillic code points are in alphabetical order (no culture data needed in the player)
            foreach (var c in Categories) c.Entries.Sort((a, b) => string.Compare(a.Name, b.Name, StringComparison.OrdinalIgnoreCase));
            Categories.RemoveAll(c => c.Entries.Count == 0);
        }

        public Entry Get(string id) => id != null && _byId.TryGetValue(id, out var e) ? e : null;

        /// <summary>Models whose name, id or category contain every word of the query (case-insensitive), in library order.</summary>
        public List<Entry> Search(string query)
        {
            var list = new List<Entry>();
            var words = (query ?? "").Trim().ToLowerInvariant().Split(new[] { ' ', ',' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var c in Categories)
            foreach (var e in c.Entries)
            {
                bool all = true;
                foreach (var w in words)
                    if (e.SearchText.IndexOf(w, StringComparison.Ordinal) < 0) { all = false; break; }
                if (all) list.Add(e);
            }
            return list;
        }

        /// <summary>Takes the extent of a built preview for a model the editor has not measured.</summary>
        public static void Measure(Entry e, GameObject built)
        {
            if (e == null || e.Local.HasValue || built == null) return;
            SetExtent(e, ItemBox.LocalBounds(built));
        }

        static void SetExtent(Entry e, Bounds b)
        {
            e.Local = b;
            var ext = ExternalCatalog.Load()?.Model(e.Id);
            if ((ext != null && ext.Hanging) || (b.max.y <= 0.02f && (b.min.y < -0.05f || e.Model.Category == "lighting")))
                e.Mount = ItemMount.Ceiling;                       // pendants, chandeliers, downlights: origin = ceiling point
            else if (b.max.z <= 0.03f && b.min.y < -0.05f && b.max.y > 0.05f)
                e.Mount = ItemMount.Wall;                          // pictures, mirrors, sconces: origin = their centre on the wall
            else
                e.Mount = ItemMount.Floor;
            e.AgainstWall = e.Mount == ItemMount.Floor && b.max.z <= 0.05f;
            e.OnSurfaces = e.Mount == ItemMount.Floor && !e.AgainstWall && SurfaceCategories.Contains(e.Model.Category)
                           && b.size.y <= 0.9f && Mathf.Max(b.size.x, b.size.z) <= 1.1f;
        }

        public static string SizeText(Bounds b, ItemMount mount)
        {
            int Cm(float m) => Mathf.Max(1, Mathf.RoundToInt(m * 100f));
            var s = b.size;
            return mount == ItemMount.Wall ? $"{Cm(s.x)} × {Cm(s.y)} см" : $"{Cm(s.x)} × {Cm(s.z)} × {Cm(s.y)} см";
        }

        /// <summary>catalog.json: {"models": {"sofa": {"min": [x, y, z], "max": [x, y, z]}, …}}.</summary>
        static Dictionary<string, Bounds> LoadManifest()
        {
            var map = new Dictionary<string, Bounds>(StringComparer.OrdinalIgnoreCase);
            var text = Resources.Load<TextAsset>(ThumbFolder + "/" + ManifestName);
            if (text == null) return map;
            try
            {
                var models = JObject.Parse(text.text)["models"] as JObject;
                if (models == null) return map;
                foreach (var p in models.Properties())
                {
                    if (!(p.Value["min"] is JArray mn) || !(p.Value["max"] is JArray mx) || mn.Count != 3 || mx.Count != 3) continue;
                    var b = new Bounds();
                    b.SetMinMax(new Vector3((float)mn[0], (float)mn[1], (float)mn[2]), new Vector3((float)mx[0], (float)mx[1], (float)mx[2]));
                    map[p.Name] = b;
                }
            }
            catch (Exception e) { Debug.LogWarning("[Furniture] catalog.json: " + e.Message); }
            return map;
        }
    }
}
