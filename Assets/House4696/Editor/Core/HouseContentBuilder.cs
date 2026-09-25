using System.Linq;
using House4696.Setup;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Core
{
    /// <summary>
    /// Writes Resources/HouseContent: the generated material assets plus the volume profiles and renderer the
    /// player needs to build and light a house on its own.
    /// </summary>
    public static class HouseContentBuilder
    {
        const string ResourcesDir = AssetPaths.Root + "/Resources";
        const string ContentPath = ResourcesDir + "/" + HouseContent.ResourceName + ".asset";
        const string PostProfilePath = AssetPaths.Settings + "/HouseVolumeProfile.asset";

        /// <summary>Creates textures, materials and the post profile without touching the scene, then the content asset.</summary>
        [MenuItem("House 46-96/Rebuild Runtime Content", priority = 2)]
        public static void RebuildMenu()
        {
            TextureFactory.GenerateAll(false);
            MaterialLibrary.Source = new AssetMaterialSource();
            new Catalog.InteriorMaterials(MaterialLibrary.Create());
            if (AssetDatabase.LoadAssetAtPath<VolumeProfile>(PostProfilePath) == null) EnvironmentSetup.CreateProfile();
            Debug.Log(Rebuild());
        }

        public static string Rebuild()
        {
            AssetPaths.Ensure(ResourcesDir);
            var content = AssetDatabase.LoadAssetAtPath<HouseContent>(ContentPath);
            if (content == null)
            {
                content = ScriptableObject.CreateInstance<HouseContent>();
                AssetDatabase.CreateAsset(content, ContentPath);
            }

            content.Materials = AssetDatabase.FindAssets("t:Material", new[] { AssetPaths.Materials })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Select(AssetDatabase.LoadAssetAtPath<Material>)
                .Where(m => m != null)
                .OrderBy(m => m.name)
                .Select(m => new HouseContent.Entry { Name = m.name, Material = m })
                .ToList();
            content.PostProcessProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(PostProfilePath);
            content.RealtimeGIProfile = RealtimeGISetup.EnsureProfile();
            content.RealtimeGIRendererIndex = RealtimeGISetup.EnsureRenderer();
            content.BakedGI = BakedGISetup.EnsureResources();
            BakedGISetup.EnsureFeature(content.BakedGI);
            EditorUtility.SetDirty(content);
            AssetDatabase.SaveAssets();
            return $"[House4696] runtime content: {content.Materials.Count} materials, GI renderer #{content.RealtimeGIRendererIndex}";
        }
    }
}
