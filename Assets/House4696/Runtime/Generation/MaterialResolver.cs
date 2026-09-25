using System;
using System.Collections.Generic;
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
        };

        public readonly MaterialLibrary Lib;
        public readonly InteriorMaterials Interior;
        readonly Dictionary<string, Material> _map = new Dictionary<string, Material>();
        readonly HashSet<string> _missing = new HashSet<string>();

        public MaterialResolver(MaterialLibrary lib, InteriorMaterials interior)
        {
            Lib = lib; Interior = interior;
            Collect(lib);
            Collect(interior); // interior names override (e.g. "glass", "soil")
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

        public bool Has(string name) => !string.IsNullOrEmpty(name) && Lookup(Key(name)) != null;

        /// <summary>Material by name, or <paramref name="fallback"/> (with a one-time warning) when unknown or empty.</summary>
        public Material Get(string name, Material fallback)
        {
            if (string.IsNullOrEmpty(name)) return fallback;
            var m = Lookup(Key(name));
            if (m != null) return m;
            if (_missing.Add(name)) Debug.LogWarning($"[House] unknown material '{name}', using {fallback?.name}");
            return fallback;
        }

        Material Lookup(string key)
        {
            if (_map.TryGetValue(key, out var m)) return m;
            if (Aliases.TryGetValue(key, out var alias) && _map.TryGetValue(alias, out m)) return m;
            return null;
        }

        public IEnumerable<string> Names => _map.Keys;
    }
}
