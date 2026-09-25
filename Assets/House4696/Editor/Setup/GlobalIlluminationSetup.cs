using House4696.Core;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace House4696.Setup
{
    /// <summary>
    /// Baked indirect lighting through Adaptive Probe Volumes: one local volume around the house, sampled per
    /// pixel, so rooms get sun and lamp bounce light instead of the flat realtime ambient. No lightmaps are
    /// used (every renderer receives GI from probes), so meshes need no second UV set. Direct light stays
    /// realtime (Mixed lights, Baked Indirect mode). Objects outside the volume keep the ambient probe.
    /// </summary>
    public static class GlobalIlluminationSetup
    {
        const string BakingSetPath = AssetPaths.Settings + "/HouseBakingSet.asset";
        static readonly Bounds HouseVolume = new Bounds(new Vector3(7.31f, 4.1f, 5.6f), new Vector3(16.8f, 8.6f, 13.6f));

        /// <summary>Switches the pipeline to probe volumes (idempotent).</summary>
        public static void ConfigurePipeline()
        {
            if (!(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)) return;
            var so = new SerializedObject(urp);
            so.FindProperty("m_LightProbeSystem").intValue = 1;      // Adaptive Probe Volumes
            so.FindProperty("m_ProbeVolumeSHBands").intValue = 2;    // L2
            so.FindProperty("m_AdditionalLightsShadowmapResolution").intValue = 4096;
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(urp);
        }

        /// <summary>Adds the volume, flags GI contributors and registers the scene in the baking set.</summary>
        public static void Prepare(Scene scene, Light sun, params GameObject[] roots)
        {
            var go = new GameObject("ProbeVolume_House");
            go.transform.position = HouseVolume.center;
            var pv = go.AddComponent<ProbeVolume>();
            pv.mode = ProbeVolume.Mode.Local;
            pv.size = HouseVolume.size;

            int contributors = 0;
            foreach (var root in roots)
            foreach (var r in root.GetComponentsInChildren<MeshRenderer>(true))
            {
                r.receiveGI = ReceiveGI.LightProbes;
                r.lightProbeUsage = LightProbeUsage.BlendProbes;
                var flags = GameObjectUtility.GetStaticEditorFlags(r.gameObject);
                bool contributes = Contributes(r) && (flags & StaticEditorFlags.BatchingStatic) != 0;
                flags = contributes ? flags | StaticEditorFlags.ContributeGI : flags & ~StaticEditorFlags.ContributeGI;
                GameObjectUtility.SetStaticEditorFlags(r.gameObject, flags);
                if (contributes) contributors++;
            }
            if (sun != null) sun.lightmapBakeType = LightmapBakeType.Mixed;

            var set = AssetDatabase.LoadAssetAtPath<ProbeVolumeBakingSet>(BakingSetPath);
            if (set == null)
            {
                set = ScriptableObject.CreateInstance<ProbeVolumeBakingSet>();
                set.name = "HouseBakingSet";
                AssetDatabase.CreateAsset(set, BakingSetPath);
            }
            set.minDistanceBetweenProbes = 0.3f;   // dense enough for 0.12 m partitions
            set.simplificationLevels = 4;          // up to ~24 m spacing in empty space
            // a set created from code starts with probe adjustment off: push probes out of walls (virtual
            // offset) and replace the remaining invalid ones by their valid neighbours (dilation)
            var so = new SerializedObject(set);
            void F(string p, float v) => so.FindProperty("settings." + p).floatValue = v;
            void B(string p, bool v) => so.FindProperty("settings." + p).boolValue = v;
            void I(string p, int v) => so.FindProperty("settings." + p).intValue = v;
            B("dilationSettings.enableDilation", true);
            F("dilationSettings.dilationDistance", 1f);
            F("dilationSettings.dilationValidityThreshold", 0.25f);
            I("dilationSettings.dilationIterations", 1);
            B("dilationSettings.squaredDistWeighting", true);
            B("virtualOffsetSettings.useVirtualOffset", true);
            F("virtualOffsetSettings.validityThreshold", 0.25f);
            F("virtualOffsetSettings.outOfGeoOffset", 0.01f);
            F("virtualOffsetSettings.searchMultiplier", 0.2f);
            F("virtualOffsetSettings.rayOriginBias", -0.001f);
            so.ApplyModifiedPropertiesWithoutUndo();
            string guid = AssetDatabase.AssetPathToGUID(scene.path);
            if (!string.IsNullOrEmpty(guid)) set.TryAddScene(guid);
            EditorUtility.SetDirty(set);
            AssetDatabase.SaveAssets();
            Debug.Log($"[House4696] GI: {contributors} contributing renderers, probe volume {HouseVolume.size}");
        }

        /// <summary>Opaque, non-foliage surfaces bounce light; glass, curtains, cutout leaves and emissive trims do not.</summary>
        static bool Contributes(MeshRenderer r)
        {
            string n = r.name;
            if (n.StartsWith("Plant_") || n.StartsWith("Lawn_Blades") || n.StartsWith("Pot_Grass")) return false;
            foreach (var m in r.sharedMaterials)
            {
                if (m == null) continue;
                if (m.renderQueue >= (int)RenderQueue.AlphaTest) return false;
            }
            return true;
        }

        public static LightingSettings CreateLightingSettings()
        {
            return new LightingSettings
            {
                name = "HouseLighting",
                bakedGI = true,
                realtimeGI = false,
                mixedBakeMode = MixedLightingMode.IndirectOnly,
                lightmapper = LightingSettings.Lightmapper.ProgressiveGPU,
                maxBounces = 3,
                directSampleCount = 32,
                indirectSampleCount = 256,
                environmentSampleCount = 256,
                autoGenerate = false,
            };
        }
    }
}
