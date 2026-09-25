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
