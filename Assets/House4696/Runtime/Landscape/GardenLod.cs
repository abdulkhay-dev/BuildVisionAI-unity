using House4696.Core;
using UnityEngine;

namespace House4696.Landscape
{
    /// <summary>A tree prototype: the LOD0 mesh and, with <see cref="GardenPerf.TreeLod"/>, the LOD1 mesh, with their materials.</summary>
    public readonly struct TreeProto
    {
        public readonly Mesh Mesh, Lod1;
        public readonly Material[] Mats, Lod1Mats;

        /// <param name="lod1">null = no LOD1 (the tree stays a single renderer).</param>
        public TreeProto(SceneWriter w, string name, MeshBuilder lod0, MeshBuilder lod1)
        {
            Mesh = w.Store(lod0.Build(name));
            Mats = lod0.Materials;
            Lod1 = lod1 != null ? w.Store(lod1.Build(name + GardenLod.Lod1Suffix)) : null;
            Lod1Mats = lod1?.Materials;
        }
    }

    /// <summary>
    /// LODGroups of the garden. Built for the GPU Resident Drawer: dithered cross-fade from
    /// <see cref="LOD.fadeTransitionWidth"/> (the drawer ignores <see cref="LODGroup.animateCrossFading"/>), no
    /// MaterialPropertyBlocks, the last level never culled.
    /// </summary>
    public static class GardenLod
    {
        /// <summary>Name suffix of a tree's LOD1 child.</summary>
        public const string Lod1Suffix = "_LOD1";

        /// <summary>Places a tree of a prototype (see the other overload).</summary>
        public static GameObject Tree(SceneWriter w, string name, Transform parent, TreeProto p, Vector3 position, Quaternion rotation, float scale) =>
            Tree(w, name, parent, p.Mesh, p.Mats, p.Lod1, p.Lod1Mats, position, rotation, scale);

        /// <summary>
        /// Places a tree. The LOD0 renderer is the tree object itself (same name, parent and collider rules as before);
        /// with <see cref="GardenPerf.TreeLod"/> the LOD1 mesh becomes a child "&lt;name&gt;_LOD1" and a LODGroup on the tree
        /// switches between them at <see cref="GardenPerf.TreeLodScreenHeight"/>.
        /// </summary>
        /// <param name="position">World position of the trunk base (the "Trees" group sits at the origin).</param>
        public static GameObject Tree(SceneWriter w, string name, Transform parent, Mesh lod0, Material[] mats0, Mesh lod1, Material[] mats1,
                                      Vector3 position, Quaternion rotation, float scale)
        {
            var go = w.Instance(name, parent, lod0, mats0, true, true);
            go.transform.position = position;
            go.transform.rotation = rotation;
            go.transform.localScale = Vector3.one * scale;
            if (!GardenPerf.TreeLod || lod1 == null) return go;

            var low = w.Instance(name + Lod1Suffix, go.transform, lod1, mats1, true, true);
            var group = go.AddComponent<LODGroup>();
            group.fadeMode = LODFadeMode.CrossFade;
            group.animateCrossFading = false;
            group.SetLODs(new[]
            {
                new LOD(Threshold(GardenPerf.TreeLodScreenHeight), new Renderer[] { go.GetComponent<MeshRenderer>() })
                    { fadeTransitionWidth = Mathf.Clamp01(GardenPerf.TreeLodFadeWidth) },
                new LOD(0f, new Renderer[] { low.GetComponent<MeshRenderer>() }),     // 0 = never culled
            });
            group.RecalculateBounds();
            return go;
        }

        /// <summary>
        /// LODGroup of a lawn chunk: LOD0 (every blade) within about <see cref="GardenPerf.LawnLodDistance"/> of the camera,
        /// LOD1 (fewer, wider blades; may be null) beyond. The group's size is set so that the switch lands at that
        /// distance for the walk lens whatever the chunk's extent; the distance is measured to <paramref name="centre"/>.
        /// </summary>
        public static void LawnChunk(GameObject lod0, GameObject lod1, Vector3 centre)
        {
            const float height = 0.5f;   // any value in (0, 1): the size below is derived from it
            var group = lod0.AddComponent<LODGroup>();
            group.fadeMode = LODFadeMode.CrossFade;
            group.animateCrossFading = false;
            var far = lod1 != null ? new Renderer[] { lod1.GetComponent<MeshRenderer>() } : new Renderer[0];
            group.SetLODs(new[]
            {
                new LOD(height, new Renderer[] { lod0.GetComponent<MeshRenderer>() }) { fadeTransitionWidth = Mathf.Clamp01(GardenPerf.LawnLodFadeWidth) },
                new LOD(0f, far),
            });
            // LOD0 while |camera − centre| · 2·tan(fov/2) / lodBias < size / height  →  switch distance = size·lodBias / (height · 2·tan(fov/2))
            float tan = Mathf.Tan(Mathf.Clamp(GardenPerf.LawnLodReferenceFov, 1f, 179f) * 0.5f * Mathf.Deg2Rad);
            group.localReferencePoint = lod0.transform.InverseTransformPoint(centre);
            group.size = Mathf.Max(0.01f, GardenPerf.LawnLodDistance) * height * 2f * tan / LodBias;
        }

        /// <summary>LOD threshold that switches at <paramref name="realScreenHeight"/> whatever QualitySettings.lodBias is.</summary>
        static float Threshold(float realScreenHeight) => Mathf.Clamp(realScreenHeight * LodBias, 0.001f, 0.999f);

        static float LodBias => Mathf.Max(0.01f, QualitySettings.lodBias);
    }
}
