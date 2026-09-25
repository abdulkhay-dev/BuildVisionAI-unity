using House4696.Core;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Setup
{
    /// <summary>
    /// Realtime global illumination for houses generated in the player (no editor bake is possible there):
    /// URP's Surface Cache GI (experimental, compiled with the SURFACE_CACHE define) on a separate renderer, so
    /// the baked editor scene keeps the default renderer unchanged. The feature is incompatible with static
    /// batching, which is therefore disabled in the player settings.
    /// </summary>
    public static class RealtimeGISetup
    {
        public const string Define = "SURFACE_CACHE";
        const string Dir = AssetPaths.Settings + "/RuntimeGI";
        const string RendererPath = Dir + "/PC_Renderer_SurfaceCache.asset";
        const string ProfilePath = Dir + "/SurfaceCacheProfile.asset";

        /// <summary>Adds the define and turns static batching off; returns true when a recompile is needed.</summary>
        public static bool ConfigurePlayer()
        {
            var t = UnityEditor.Build.NamedBuildTarget.Standalone;
            string d = PlayerSettings.GetScriptingDefineSymbols(t);
            PlayerSettings.SetStaticBatchingForPlatform(BuildTarget.StandaloneOSX, false);
            PlayerSettings.SetStaticBatchingForPlatform(BuildTarget.StandaloneWindows64, false);
            if (d.Contains(Define)) return false;
            PlayerSettings.SetScriptingDefineSymbols(t, string.IsNullOrEmpty(d) ? Define : d + ";" + Define);
            return true;
        }

        /// <summary>Copy of the default renderer with the Surface Cache GI feature, registered in the pipeline asset.</summary>
        public static int EnsureRenderer()
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var urpSo = new SerializedObject(urp);
            var list = urpSo.FindProperty("m_RendererDataList");
            var baseData = (ScriptableRendererData)list.GetArrayElementAtIndex(0).objectReferenceValue;

            var rd = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
            if (rd == null)
            {
                AssetPaths.Ensure(Dir);
                AssetDatabase.CopyAsset(AssetDatabase.GetAssetPath(baseData), RendererPath);
                rd = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
                var feature = ScriptableObject.CreateInstance<SurfaceCacheGIRendererFeature>();
                feature.name = "SurfaceCacheGI";
                AssetDatabase.AddObjectToAsset(feature, rd);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(feature, out _, out long localId);
                var so = new SerializedObject(rd);
                var features = so.FindProperty("m_RendererFeatures");
                var map = so.FindProperty("m_RendererFeatureMap");
                features.arraySize++;
                features.GetArrayElementAtIndex(features.arraySize - 1).objectReferenceValue = feature;
                map.arraySize++;
                map.GetArrayElementAtIndex(map.arraySize - 1).longValue = localId;
                so.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(rd);
                AssetDatabase.SaveAssets();
            }

            for (int i = 0; i < list.arraySize; i++)
                if (list.GetArrayElementAtIndex(i).objectReferenceValue == rd) return i;
            list.arraySize++;
            list.GetArrayElementAtIndex(list.arraySize - 1).objectReferenceValue = rd;
            urpSo.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(urp);
            AssetDatabase.SaveAssets();
            return list.arraySize - 1;
        }

        /// <summary>
        /// Interactive defaults measured on an Apple M4 in the player (house 10×10 m, 1470×816 window): 8 samples and
        /// the garden in the GI cost ~125 ms GPU; garden excluded ~57 ms; + 4 samples ~29 ms; 2 samples ~20 ms with
        /// visibly the same converged result. Renders for the AI temporarily raise the samples (ViewRenderer).
        /// </summary>
        static void ApplyDefaults(SurfaceCacheGIVolumeOverride gi)
        {
            gi.multiBounce.Override(true);
            gi.sampleCount.Override(4);
            gi.volumeSize.Override(48f);
            gi.volumeResolution.Override(64);
            gi.volumeCascadeCount.Override(4);
            gi.renderingLayerMask.Override((RenderingLayerMask)1u);   // house only (garden = layer 2)
        }

        public static VolumeProfile EnsureProfile()
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profile != null)
            {
                if (profile.TryGet<SurfaceCacheGIVolumeOverride>(out var existing)) ApplyDefaults(existing);
                EditorUtility.SetDirty(profile);
                return profile;
            }
            AssetPaths.Ensure(Dir);
            profile = ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(profile, ProfilePath);
            var gi = profile.Add<SurfaceCacheGIVolumeOverride>(true);
            gi.name = nameof(SurfaceCacheGIVolumeOverride);
            ApplyDefaults(gi);
            AssetDatabase.AddObjectToAsset(gi, profile);
            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }
    }
}
