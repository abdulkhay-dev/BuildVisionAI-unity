using System;
using System.Collections.Generic;
using UnityEngine;
using Object = UnityEngine.Object;

namespace House4696.Core
{
    /// <summary>
    /// Library of external assets (CC0 scans from Poly Haven and models made in Blender): PBR materials that house
    /// documents name by id ("oak_planks", "velvet#6b4f3a") and furniture models placed as catalogue items. Built by the
    /// editor from Assets/House4696/External/external.json (House 46-96 → External → Import Catalog).
    /// <para>Materials and prefabs live under Resources/ExternalLibrary and are referenced by path, not by object: a direct
    /// reference loads every texture of the library (~1.2 GB of GPU memory) with HouseContent at start, though a house
    /// uses a few dozen. They load on first use; <see cref="Release"/> + Resources.UnloadUnusedAssets frees the rest.</para>
    /// </summary>
    public sealed class ExternalCatalog : ScriptableObject
    {
        [Serializable]
        public sealed class MaterialEntry
        {
            public string Id, Name, Category;
            [Tooltip("Resources path of the material (loaded on first use).")]
            public string MaterialPath;
            [NonSerialized] Material _material;
            public Material Material { get => _material != null ? _material : _material = Load<Material>(MaterialPath); set => _material = value; }
            internal void Release() => _material = null;
            [Tooltip("Grey albedo: meant to be tinted with #rrggbb.")]
            public bool Neutral;
        }

        [Serializable]
        public sealed class Slot
        {
            [Tooltip("Role of the sub-mesh: upholstery, legs, frame…; item parameters use it as the key.")]
            public string Name;
            [Tooltip("Resources path of the scan's own material (textures made for this model's UVs), loaded on first use; empty when the slot has none.")]
            public string OwnPath;
            [NonSerialized] Material _own;
            public Material Own { get => _own != null ? _own : _own = Load<Material>(OwnPath); set => _own = value; }
            internal void Release() => _own = null;
            [Tooltip("Library material used when the item does not say otherwise (\"linen_rough#c8c0b3\").")]
            public string Default;
            [Tooltip("UVs are in metres, so any library material keeps its real scale.")]
            public bool UvMeters;
        }

        [Serializable]
        public sealed class ModelEntry
        {
            public string Id, Name, Category, Source;
            [Tooltip("Resources path of the prefab (loaded on first use).")]
            public string PrefabPath;
            [NonSerialized] GameObject _prefab;
            public GameObject Prefab { get => _prefab != null ? _prefab : _prefab = Load<GameObject>(PrefabPath); set => _prefab = value; }
            internal void Release() { _prefab = null; foreach (var s in Slots) s.Release(); }
            public Vector3 Size;
            [Tooltip("Pivot at the ceiling point (pendants) instead of the floor.")]
            public bool Hanging;
            public int Triangles;
            [Tooltip("In the order of the model's sub-meshes.")]
            public List<Slot> Slots = new List<Slot>();

            /// <summary>Parameter list for the catalogue: every slot with its default ("upholstery=linen_rough#c8c0b3 …").</summary>
            public string ParamsText()
            {
                var parts = new List<string>();
                for (int i = 0; i < Slots.Count; i++)
                    parts.Add($"{SlotKey(i)}={(string.IsNullOrEmpty(Slots[i].Default) ? "original" : Slots[i].Default)}");
                return string.Join(" ", parts);
            }

            /// <summary>
            /// Parameter name of slot <paramref name="i"/>: its role ("upholstery"), or "main"/"partN" when the scan kept an
            /// internal material name ("Material.008", "Armchair_01") that an author could not guess.
            /// </summary>
            public string SlotKey(int i)
            {
                string n = Slots[i].Name;
                if (!string.IsNullOrEmpty(n) && System.Text.RegularExpressions.Regex.IsMatch(n, "^[a-z][a-z0-9_]*$")) return n;
                return i == 0 && !Slots.Exists(s => s.Name == "main") ? "main" : "part" + (i + 1);
            }
        }

        public List<MaterialEntry> Materials = new List<MaterialEntry>();
        public List<ModelEntry> Models = new List<ModelEntry>();

        public ModelEntry Model(string id) => Models.Find(m => string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase));

        static ExternalCatalog _loaded;
        static bool _tried;

        /// <summary>The catalogue shipped with the app (via <see cref="HouseContent"/>), or null.</summary>
        public static ExternalCatalog Load()
        {
            if (_tried) return _loaded;
            _tried = true;
            var content = Resources.Load<HouseContent>(HouseContent.ResourceName);
            _loaded = content != null ? content.External : null;
            return _loaded;
        }

        static T Load<T>(string path) where T : Object => string.IsNullOrEmpty(path) ? null : Resources.Load<T>(path);

        /// <summary>
        /// Drops the cached materials and prefabs, so Resources.UnloadUnusedAssets can free what the scene no longer uses
        /// (the next use loads them again).
        /// </summary>
        public static void Release()
        {
            if (_loaded == null) return;
            foreach (var m in _loaded.Materials) m.Release();
            foreach (var m in _loaded.Models) m.Release();
        }

        /// <summary>Forget the cached catalogue (the editor re-imported it).</summary>
        public static void Reset() { _tried = false; _loaded = null; }
    }
}
