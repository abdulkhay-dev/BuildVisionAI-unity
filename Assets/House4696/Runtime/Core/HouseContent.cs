using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Core
{
    /// <summary>
    /// Everything the player needs to generate a house without the editor: the material palette (prebuilt
    /// URP/Lit assets, so their textures and shader variants are included in the build), the post-processing
    /// profile and the realtime-GI setup. Built by the editor (House 46-96 → Rebuild), loaded from Resources.
    /// </summary>
    [CreateAssetMenu(menuName = "House 46-96/House Content")]
    public sealed class HouseContent : ScriptableObject
    {
        public const string ResourceName = "HouseContent";
        public const string SkyMaterial = "M_Sky";

        [Serializable]
        public struct Entry
        {
            public string Name;
            public Material Material;
        }

        public List<Entry> Materials = new List<Entry>();
        public VolumeProfile PostProcessProfile;
        public VolumeProfile RealtimeGIProfile;
        [Tooltip("Index of the renderer (in the pipeline asset) that has the Surface Cache GI feature.")]
        public int RealtimeGIRendererIndex = -1;
        [Tooltip("Shaders and textures of the runtime GI baker (the lighting of a house is baked in the player).")]
        public House4696.Lighting.ProbeBakeResources BakedGI;
        [Tooltip("External PBR materials and furniture models (Poly Haven scans, Blender models).")]
        public ExternalCatalog External;
        [Tooltip("Landscape kit: rocks, plants, ground cover and terrain layers of the site generator.")]
        public LandscapeKit Landscape;

        Dictionary<string, Material> _byName;

        public Material Material(string name)
        {
            if (_byName == null)
            {
                _byName = new Dictionary<string, Material>(Materials.Count);
                foreach (var e in Materials)
                    if (e.Material != null) _byName[e.Name] = e.Material;
            }
            if (_byName.TryGetValue(name, out var m)) return m;
            Debug.LogError($"[HouseContent] material '{name}' is missing — rebuild content in the editor");
            return null;
        }

        public static HouseContent Load()
        {
            var c = Resources.Load<HouseContent>(ResourceName);
            if (c == null) throw new InvalidOperationException($"Resources/{ResourceName} not found — run House 46-96 → Rebuild in the editor");
            return c;
        }
    }
}
