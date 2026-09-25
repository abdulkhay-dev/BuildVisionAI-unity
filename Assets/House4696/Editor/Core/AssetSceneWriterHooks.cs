using UnityEditor;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Editor persistence for <see cref="SceneWriter"/>: meshes become sub-assets of one container asset (one
    /// file instead of hundreds, and scenes stay small); scene objects get static editor flags for batching and baking.
    /// </summary>
    public sealed class AssetSceneWriterHooks : ISceneWriterHooks
    {
        readonly Object _container;

        public AssetSceneWriterHooks(string containerPath)
        {
            AssetPaths.Ensure(System.IO.Path.GetDirectoryName(containerPath)?.Replace('\\', '/'));
            if (AssetDatabase.LoadMainAssetAtPath(containerPath) != null) AssetDatabase.DeleteAsset(containerPath);
            var root = new Mesh { name = "GeneratedMeshes" };
            AssetDatabase.CreateAsset(root, containerPath);
            _container = root;
        }

        public void StoreMesh(Mesh mesh) => AssetDatabase.AddObjectToAsset(mesh, _container);

        public void MarkStatic(GameObject go, bool probeStatic)
        {
            var flags = StaticEditorFlags.BatchingStatic | StaticEditorFlags.OccludeeStatic;
            if (probeStatic) flags |= StaticEditorFlags.ReflectionProbeStatic;
            GameObjectUtility.SetStaticEditorFlags(go, flags);
        }

        public void MarkDynamic(GameObject go) => GameObjectUtility.SetStaticEditorFlags(go, 0);
    }
}
