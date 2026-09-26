using System;
using System.Collections.Generic;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Library of external assets (CC0 scans from Poly Haven and models made in Blender): PBR materials that house
    /// documents name by id ("oak_planks", "velvet#6b4f3a") and furniture models placed as catalogue items. Built by the
    /// editor from Assets/House4696/External/external.json (House 46-96 → External → Import Catalog).
    /// </summary>
    public sealed class ExternalCatalog : ScriptableObject
    {
        [Serializable]
        public sealed class MaterialEntry
        {
            public string Id, Name, Category;
            public Material Material;
            [Tooltip("Grey albedo: meant to be tinted with #rrggbb.")]
            public bool Neutral;
        }

        [Serializable]
        public sealed class Slot
        {
            [Tooltip("Role of the sub-mesh: upholstery, legs, frame…; item parameters use it as the key.")]
            public string Name;
            [Tooltip("Material of the scan (textures made for this model's UVs).")]
            public Material Own;
            [Tooltip("Library material used when the item does not say otherwise (\"linen_rough#c8c0b3\").")]
            public string Default;
            [Tooltip("UVs are in metres, so any library material keeps its real scale.")]
            public bool UvMeters;
        }

        [Serializable]
        public sealed class ModelEntry
        {
            public string Id, Name, Category, Source;
            public GameObject Prefab;
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

        /// <summary>Forget the cached catalogue (the editor re-imported it).</summary>
        public static void Reset() { _tried = false; _loaded = null; }
    }
}
