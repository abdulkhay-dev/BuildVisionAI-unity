using System.IO;
using UnityEditor;
using UnityEngine;

namespace House4696.Core
{
    public static class AssetPaths
    {
        public const string Root = "Assets/House4696";
        public const string Generated = Root + "/Generated";
        public const string Textures = Generated + "/Textures";
        public const string Materials = Generated + "/Materials";
        public const string Meshes = Generated + "/Meshes";
        public const string Settings = Generated + "/Settings";
        public const string Scenes = Root + "/Scenes";
        public const string ScenePath = Scenes + "/House_46-96.unity";

        /// <summary>Creates a nested project folder (e.g. Assets/A/B/C) if it does not exist.</summary>
        public static void Ensure(string folder)
        {
            if (AssetDatabase.IsValidFolder(folder)) return;
            string parent = Path.GetDirectoryName(folder)?.Replace('\\', '/');
            if (!string.IsNullOrEmpty(parent) && !AssetDatabase.IsValidFolder(parent)) Ensure(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(folder));
        }

        /// <summary>Deletes and recreates a folder of generated assets (used for meshes on rebuild).</summary>
        public static void Recreate(string folder)
        {
            if (AssetDatabase.IsValidFolder(folder)) AssetDatabase.DeleteAsset(folder);
            Ensure(folder);
        }

        public static T SaveOrReplace<T>(T obj, string path) where T : Object
        {
            var existing = AssetDatabase.LoadAssetAtPath<T>(path);
            if (existing != null)
            {
                EditorUtility.CopySerialized(obj, existing);
                EditorUtility.SetDirty(existing);
                return existing;
            }
            AssetDatabase.CreateAsset(obj, path);
            return obj;
        }
    }
}
