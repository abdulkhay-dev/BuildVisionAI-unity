using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using House4696.Core;
using House4696.Catalog;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Resolves material names used in house documents ("stone", "oak", "boucle", "black_metal", …) to palette
    /// materials. Names are case- and underscore-insensitive and match the public members of
    /// <see cref="InteriorMaterials"/> and <see cref="MaterialLibrary"/> (interior names win), plus a few aliases.
    /// </summary>
    public sealed class MaterialResolver
    {
        static readonly Dictionary<string, string> Aliases = new Dictionary<string, string>
        {
            { "wood", "slatbacking" },       // wood cladding: battens are added by the wall builder
            { "battens", "slatbacking" },
            { "concrete", "pot" },
            { "metal", "blackmetal" },
            { "flashing", "coping" },
            { "paint", "plaster" },
            { "white", "plaster" },
            { "parquet", "oak" },
            { "tiles", "tile" },
            { "membrane", "coping" },
            { "roofmetal", "coping" },
            { "render", "plaster" },          // light exterior render (tint it: "render#e8e2d6")
            { "facadeplaster", "plaster" },
        };

        public readonly MaterialLibrary Lib;
        public readonly InteriorMaterials Interior;
        readonly Dictionary<string, Material> _map = new Dictionary<string, Material>();
        readonly Dictionary<string, ExternalCatalog.MaterialEntry> _library = new Dictionary<string, ExternalCatalog.MaterialEntry>();
        readonly HashSet<string> _missing = new HashSet<string>();

        public MaterialResolver(MaterialLibrary lib, InteriorMaterials interior)
        {
            Lib = lib; Interior = interior;
            Collect(lib);
            Collect(interior); // interior names override (e.g. "glass", "soil")
            // library materials (PBR scans) by their catalogue ids; built-in names keep priority
            // (entries, not materials: a library material loads when a house first asks for it)
            var external = ExternalCatalog.Load();
            if (external != null)
                foreach (var e in external.Materials)
                {
                    if (string.IsNullOrEmpty(e.MaterialPath)) continue;
                    string k = Key(e.Id);
                    if (_map.ContainsKey(k)) Debug.LogWarning($"[House] library material '{e.Id}' clashes with a built-in name and is hidden");
                    else _library[k] = e;
                }
        }

        void Collect(object src)
        {
            const BindingFlags F = BindingFlags.Public | BindingFlags.Instance;
            foreach (var f in src.GetType().GetFields(F))
                if (f.FieldType == typeof(Material) && f.GetValue(src) is Material m) _map[Key(f.Name)] = m;
            foreach (var p in src.GetType().GetProperties(F))
                if (p.PropertyType == typeof(Material) && p.GetValue(src) is Material m) _map[Key(p.Name)] = m;
        }

        public static string Key(string name) => name?.Replace("_", "").Replace("-", "").Replace(" ", "").ToLowerInvariant() ?? "";

        /// <summary>Material name without a colour suffix: "plaster#e8e2d6" → "plaster".</summary>
        public static string BaseName(string name)
        {
            int i = name?.IndexOf('#') ?? -1;
            return i > 0 ? name.Substring(0, i) : name;
        }

        readonly Dictionary<string, Material> _tinted = new Dictionary<string, Material>();

        public bool Has(string name) => !string.IsNullOrEmpty(name) && Lookup(Key(BaseName(name))) != null;

        /// <summary>
        /// Material by name, or <paramref name="fallback"/> (with a one-time warning) when unknown or empty.
        /// "name#rrggbb" gives a copy of the material with that base colour (the texture keeps its pattern).
        /// </summary>
        public Material Get(string name, Material fallback)
        {
            if (string.IsNullOrEmpty(name)) return fallback;
            string baseName = BaseName(name);
            var m = Lookup(Key(baseName)) ?? (baseName != name ? fallback : null);
            if (m == null)
            {
                if (_missing.Add(name)) Debug.LogWarning($"[House] unknown material '{name}', using {fallback?.name}");
                return fallback;
            }
            if (baseName == name) return m;
            if (_tinted.TryGetValue(name, out var t)) return t;
            if (!ColorUtility.TryParseHtmlString(name.Substring(baseName.Length), out var col))
            {
                if (_missing.Add(name)) Debug.LogWarning($"[House] bad colour in '{name}' (expected #rrggbb)");
                return m;
            }
            t = new Material(m) { name = m.name + "_" + name.Substring(baseName.Length + 1) };
            t.SetColor("_BaseColor", col);
            _tinted[name] = t;
            return t;
        }

        /// <summary>Copy of <paramref name="m"/> with the base colour "#rrggbb" (for a model's own scanned materials).</summary>
        public Material Tint(Material m, string hex)
        {
            if (m == null || !ColorUtility.TryParseHtmlString(hex, out var col)) return m;
            string key = m.name + hex;
            if (_tinted.TryGetValue(key, out var t)) return t;
            t = new Material(m) { name = m.name + "_" + hex.TrimStart('#') };
            t.SetColor("_BaseColor", col);
            _tinted[key] = t;
            return t;
        }

        /// <summary>Tinted copies created for this house (destroyed with it).</summary>
        public IEnumerable<Material> Created => _tinted.Values;

        Material Lookup(string key)
        {
            if (_map.TryGetValue(key, out var m)) return m;
            if (_library.TryGetValue(key, out var e)) return _map[key] = e.Material;
            if (Aliases.TryGetValue(key, out var alias))
            {
                if (_map.TryGetValue(alias, out m)) return m;
                if (_library.TryGetValue(alias, out e)) return _map[alias] = e.Material;
            }
            return null;
        }

        public IEnumerable<string> Names => _map.Keys.Concat(_library.Keys).Distinct();
    }
}
