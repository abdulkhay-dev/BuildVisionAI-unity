using House4696.Core;
using House4696.Lighting;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace House4696.Setup
{
    /// <summary>
    /// Runtime-baked GI for the player: the resource asset the probe baker needs (path tracing shaders and sampling
    /// textures that the package loads through the AssetDatabase in the editor) and the <see cref="BakedGIFeature"/>
    /// on the app's renderer — the one that also carries Surface Cache GI, so the camera never switches renderers.
    /// </summary>
    public static class BakedGISetup
    {
        const string Dir = AssetPaths.Settings + "/RuntimeGI";
        const string ResourcesPath = Dir + "/ProbeBakeResources.asset";
        const string Core = "Packages/com.unity.render-pipelines.core/Runtime/";
        const string Shaders = Core + "PathTracing/Shaders/";
        const string ResolvePath = AssetPaths.Root + "/Runtime/Lighting/BakedGI/BakedGIResolve.compute";

        [MenuItem("House 46-96/App/Setup baked GI", priority = 47)]
        public static void SetupMenu()
        {
            var res = EnsureResources();
            EnsureFeature(res);
            Debug.Log($"[BakedGI] resources {(res.IsComplete ? "complete" : "INCOMPLETE")}, feature on the app renderer");
        }

        public static ProbeBakeResources EnsureResources()
        {
            var res = AssetDatabase.LoadAssetAtPath<ProbeBakeResources>(ResourcesPath);
            if (res == null)
            {
                AssetPaths.Ensure(Dir);
                res = ScriptableObject.CreateInstance<ProbeBakeResources>();
                AssetDatabase.CreateAsset(res, ResourcesPath);
            }
            res.IndirectRadiance = Compute(Shaders + "ProbeIntegrationIndirect.urtshader");
            res.DirectStochasticLight = Compute(Shaders + "ProbeIntegrationDirectStochasticLight.urtshader");
            res.DirectDirectionalAndEnvironment = Compute(Shaders + "ProbeIntegrationDirectDirectionalAndEnvironment.urtshader");
            res.Validity = Compute(Shaders + "ProbeIntegrationValidity.urtshader");
            res.SegmentedReduction = Compute(Shaders + "SegmentedReduction.compute");
            res.ProbePostProcessing = Compute(Shaders + "ProbePostProcessing.compute");
            res.SobolScramblingTile = AssetDatabase.LoadAssetAtPath<Texture2D>(Core + "Sampling/Textures/SobolBlueNoise/ScramblingTile256SPP.png");
            res.SobolRankingTile = AssetDatabase.LoadAssetAtPath<Texture2D>(Core + "Sampling/Textures/SobolBlueNoise/RankingTile256SPP.png");
            res.SobolOwenScrambled256 = AssetDatabase.LoadAssetAtPath<Texture2D>(Core + "Sampling/Textures/SobolBlueNoise/SobolOwenScrambled256.png");
            res.PassthroughSkybox = AssetDatabase.LoadAssetAtPath<Shader>(Shaders + "PassthroughSkybox.shader");
            res.Resolve = AssetDatabase.LoadAssetAtPath<ComputeShader>(ResolvePath);
            EditorUtility.SetDirty(res);
            AssetDatabase.SaveAssets();
            if (!res.IsComplete) Debug.LogError("[BakedGI] some bake resources were not found — check the package paths in BakedGISetup");
            return res;
        }

        /// <summary>Adds (or updates) the resolve feature on the renderer the app camera uses.</summary>
        public static void EnsureFeature(ProbeBakeResources res)
        {
            int index = RealtimeGISetup.EnsureRenderer();
            var urp = (UniversalRenderPipelineAsset)UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline;
            var list = new SerializedObject(urp).FindProperty("m_RendererDataList");
            var rd = (ScriptableRendererData)list.GetArrayElementAtIndex(index).objectReferenceValue;

            BakedGIFeature feature = null;
            foreach (var f in rd.rendererFeatures)
                if (f is BakedGIFeature b) feature = b;
            if (feature == null)
            {
                feature = ScriptableObject.CreateInstance<BakedGIFeature>();
                feature.name = "BakedGI";
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
            }
            feature.resolveShader = res.Resolve;
            EditorUtility.SetDirty(feature);
            EditorUtility.SetDirty(rd);
            AssetDatabase.SaveAssets();
        }

        static ComputeShader Compute(string path) => AssetDatabase.LoadAssetAtPath<ComputeShader>(path);
    }
}
