using House4696.Core;
using House4696.Runtime;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Setup
{
    /// <summary>Sun, sky, ambient, fog, post-processing, reflection probe, camera and pipeline quality.</summary>
    public static class EnvironmentSetup
    {
        public static void ConfigurePipeline()
        {
            if (!(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)) return;
            GlobalIlluminationSetup.ConfigurePipeline();
            urp.msaaSampleCount = 4;
            urp.shadowDistance = 95f;
            urp.shadowCascadeCount = 4;
            urp.cascade4Split = new Vector3(0.07f, 0.2f, 0.46f);
            urp.mainLightShadowmapResolution = 4096;
            var so = new SerializedObject(urp);
            so.FindProperty("m_SoftShadowsSupported").boolValue = true;
            var q = so.FindProperty("m_SoftShadowQuality"); if (q != null) q.intValue = 3;
            var hdr = so.FindProperty("m_SupportsHDR"); if (hdr != null) hdr.boolValue = true;
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(urp);

            // stronger, wider SSAO for soffits, reveals and batten gaps
            var rendererData = so.FindProperty("m_RendererDataList").GetArrayElementAtIndex(0).objectReferenceValue as ScriptableRendererData;
            if (rendererData != null)
            {
                foreach (var feature in rendererData.rendererFeatures)
                {
                    if (feature == null || feature.GetType().Name != "ScreenSpaceAmbientOcclusion") continue;
                    var fso = new SerializedObject(feature);
                    void F(string p, float v) { var sp = fso.FindProperty("m_Settings." + p); if (sp != null) sp.floatValue = v; }
                    void I(string p, int v) { var sp = fso.FindProperty("m_Settings." + p); if (sp != null) sp.intValue = v; }
                    void B(string p, bool v) { var sp = fso.FindProperty("m_Settings." + p); if (sp != null) sp.boolValue = v; }
                    F("Intensity", 0.55f); F("Radius", 0.22f); // soft enough for interiors (larger radii smudge wall/ceiling joints) F("DirectLightingStrength", 0.2f); F("Falloff", 60f);
                    B("Downsample", false); B("AfterOpaque", false);
                    I("Samples", 0); // High
                    I("BlurQuality", 0); // High
                    fso.ApplyModifiedPropertiesWithoutUndo();
                    EditorUtility.SetDirty(feature);
                }
            }
            AssetDatabase.SaveAssets();
        }

        public static GameObject Build(MaterialLibrary m, Vector3? sunEuler = null) => EnvironmentBuilder.Build(m, CreateProfile(), sunEuler);

        public static void ApplyCamera(Camera cam) => EnvironmentBuilder.ApplyCamera(cam);

        public static VolumeProfile CreateProfile()
        {
            AssetPaths.Ensure(AssetPaths.Settings);
            string path = AssetPaths.Settings + "/HouseVolumeProfile.asset";
            if (AssetDatabase.LoadAssetAtPath<VolumeProfile>(path) != null) AssetDatabase.DeleteAsset(path);
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(profile, path);
            T Add<T>() where T : VolumeComponent
            {
                var c = profile.Add<T>(true);
                c.name = typeof(T).Name;
                AssetDatabase.AddObjectToAsset(c, profile);
                return c;
            }
            var tm = Add<Tonemapping>(); tm.mode.Override(TonemappingMode.Neutral);
            var bloom = Add<Bloom>(); bloom.intensity.Override(0.22f); bloom.threshold.Override(1.15f); bloom.scatter.Override(0.62f);
            var ca = Add<ColorAdjustments>(); ca.postExposure.Override(0.55f); ca.contrast.Override(10f); ca.saturation.Override(4f);
            var wb = Add<WhiteBalance>(); wb.temperature.Override(2f);
            var vig = Add<Vignette>(); vig.intensity.Override(0.14f); vig.smoothness.Override(0.5f);
            // probe-volume sampling: push samples off surfaces so thin partitions do not leak or blotch
            var apv = Add<ProbeVolumesOptions>();
            apv.normalBias.Override(0.22f); apv.viewBias.Override(0.15f);
            apv.samplingNoise.Override(0.04f); apv.animateSamplingNoise.Override(false);
            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        /// <summary>
        /// Bakes the adaptive probe volume (indirect light of the sun, sky and Mixed interior lights), the
        /// ambient probe and the reflection probes. Direct lighting stays realtime.
        /// </summary>
        public static string BakeEnvironment()
        {
            var ls = GlobalIlluminationSetup.CreateLightingSettings();
            string path = AssetPaths.Settings + "/HouseLighting.lighting";
            if (AssetDatabase.LoadAssetAtPath<LightingSettings>(path) != null) AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(ls, path);
            Lightmapping.lightingSettings = ls;
            bool ok = Lightmapping.Bake();
            return ok ? "environment baked" : "environment bake FAILED";
        }
    }
}
