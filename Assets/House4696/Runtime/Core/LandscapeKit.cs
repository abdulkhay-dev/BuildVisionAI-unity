using System;
using System.Collections.Generic;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Landscape kit: rocks, grasses, ground cover, perennials and shrubs (Poly Haven scans and procedural plants
    /// made in Blender, tools/landscape) plus the ground layers of the terrain. The site generator scatters its
    /// variants. Built by the editor from Assets/House4696/External/Landscape/landscape.json
    /// (House 46-96 → External → Import Landscape Kit).
    /// </summary>
    public sealed class LandscapeKit : ScriptableObject
    {
        public enum Kind
        {
            /// <summary>Boulder: collider, casts shadows, LOD0/LOD1.</summary>
            Rock,
            /// <summary>Small stone or pebble: no collider, no shadow, one LOD.</summary>
            Stone,
            /// <summary>Perennial, fern, grass tuft, shrub: mesh instance with LOD0/LOD1, no collider.</summary>
            Plant,
            /// <summary>Grass and ground cover drawn instanced by the terrain's detail system.</summary>
            Detail,
        }

        [Serializable]
        public sealed class Variant
        {
            public string Id, Source;
            [Tooltip("Rocks, stones and plants: the prefab (LODGroup when it has two LODs). Details: a single mesh renderer.")]
            public GameObject Prefab;
            [Tooltip("Size of LOD0 in metres (x, height, z).")]
            public Vector3 Size;
            public int TrianglesLod0, TrianglesLod1;
        }

        [Serializable]
        public sealed class Group
        {
            public string Id;
            public Kind Kind;
            public List<Variant> Variants = new List<Variant>();
        }

        [Serializable]
        public sealed class Layer
        {
            public string Id;
            public TerrainLayer TerrainLayer;
        }

        [Tooltip("URP Terrain/Lit material of the site terrains.")]
        public Material TerrainMaterial;
        [Tooltip("Stream pools (flowing water with refraction).")]
        public Material WaterMaterial;
        [Tooltip("Cascade tongues (white water).")]
        public Material FallsMaterial;
        public List<Group> Groups = new List<Group>();
        public List<Layer> Layers = new List<Layer>();

        public Group Find(string id) => Groups.Find(g => string.Equals(g.Id, id, StringComparison.OrdinalIgnoreCase));
        public TerrainLayer TerrainLayer(string id) => Layers.Find(l => l.Id == id)?.TerrainLayer;

        /// <summary>
        /// Resources name of the kit. It is not referenced from <see cref="HouseContent"/>: its rocks, plants and terrain
        /// layers (~160 MB of textures and meshes) load only when a natural site or a pool needs them.
        /// </summary>
        public const string ResourceName = "LandscapeKit";

        static LandscapeKit _loaded;
        static bool _tried;

        /// <summary>The kit shipped with the app, or null.</summary>
        public static LandscapeKit Load()
        {
            if (_tried) return _loaded;
            _tried = true;
            _loaded = Resources.Load<LandscapeKit>(ResourceName);
            return _loaded;
        }

        /// <summary>Forget the cached kit (the editor re-imported it, or the app frees what the scene does not use).</summary>
        public static void Reset() { _tried = false; _loaded = null; }
    }
}
