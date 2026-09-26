using UnityEditor;
using UnityEngine;

namespace House4696.Setup
{
    /// <summary>
    /// Keeps the house out of the garden reflection probe (the facade glazing must not reflect the house
    /// itself) while letting the per-room interior probes capture the rooms: the house lives on its own
    /// layer, is flagged reflection-probe static, and the garden probe's culling mask skips that layer.
    /// </summary>
    public static class ReflectionSetup
    {
        public const string HouseLayerName = "House";
        const int PreferredLayer = 8;

        public static void Apply(GameObject house, ReflectionProbe gardenProbe)
        {
            int layer = EnsureLayer(HouseLayerName);
            foreach (var t in house.GetComponentsInChildren<Transform>(true))
            {
                t.gameObject.layer = layer;
                var flags = GameObjectUtility.GetStaticEditorFlags(t.gameObject);
                if ((flags & StaticEditorFlags.BatchingStatic) != 0)
                    GameObjectUtility.SetStaticEditorFlags(t.gameObject, flags | StaticEditorFlags.ReflectionProbeStatic);
            }
            if (gardenProbe != null) gardenProbe.cullingMask = ~(1 << layer);
        }

        /// <summary>
        /// Realtime reflection probes on every quality level. The app captures its probes from script; with the option
        /// off (the PC level had it off) they are never rendered and glossy surfaces reflect the sky. The player also
        /// switches it on at start (<c>ReflectionCapture.EnableRealtimeProbes</c>); this makes it stick for the editor.
        /// </summary>
        [MenuItem("House 46-96/App/Enable realtime reflection probes", priority = 48)]
        public static void EnableRealtimeProbes()
        {
            var assets = AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/QualitySettings.asset");
            if (assets == null || assets.Length == 0) { Debug.LogError("[ReflectionSetup] QualitySettings.asset not found"); return; }
            var qs = new SerializedObject(assets[0]);
            var levels = qs.FindProperty("m_QualitySettings");
            int changed = 0;
            for (int i = 0; levels != null && i < levels.arraySize; i++)
            {
                var p = levels.GetArrayElementAtIndex(i).FindPropertyRelative("realtimeReflectionProbes");
                if (p == null) continue;
                if (p.propertyType == SerializedPropertyType.Boolean)
                {
                    if (!p.boolValue) { p.boolValue = true; changed++; }
                }
                else if (p.intValue == 0) { p.intValue = 1; changed++; }
            }
            qs.ApplyModifiedPropertiesWithoutUndo();
            AssetDatabase.SaveAssets();
            Debug.Log($"[ReflectionSetup] realtime reflection probes on ({changed} quality level(s) changed)");
        }

        static int EnsureLayer(string name)
        {
            int existing = LayerMask.NameToLayer(name);
            if (existing >= 0) return existing;
            var tm = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            var layers = tm.FindProperty("layers");
            int slot = -1;
            if (string.IsNullOrEmpty(layers.GetArrayElementAtIndex(PreferredLayer).stringValue)) slot = PreferredLayer;
            for (int i = 8; slot < 0 && i < 32; i++)
                if (string.IsNullOrEmpty(layers.GetArrayElementAtIndex(i).stringValue)) slot = i;
            if (slot < 0) throw new System.InvalidOperationException("no free user layer for " + name);
            layers.GetArrayElementAtIndex(slot).stringValue = name;
            tm.ApplyModifiedPropertiesWithoutUndo();
            return slot;
        }
    }
}
