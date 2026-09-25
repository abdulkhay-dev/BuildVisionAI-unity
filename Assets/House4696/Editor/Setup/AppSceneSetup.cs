using House4696.App;
using House4696.Core;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace House4696.Setup
{
    /// <summary>
    /// The app scene is (almost) empty: a loading camera and <see cref="HouseBootstrap"/>, which generates the
    /// house at runtime. Nothing baked or generated in the editor is referenced except Resources/HouseContent.
    /// </summary>
    public static class AppSceneSetup
    {
        public const string ScenePath = AssetPaths.Scenes + "/App.unity";

        [MenuItem("House 46-96/App/Create App Scene", priority = 40)]
        public static void CreateMenu() => Debug.Log(Create());

        public static string Create()
        {
            if (EditorApplication.isPlaying) return "exit play mode first";
            if (RealtimeGISetup.ConfigurePlayer()) Debug.Log("[House4696] SURFACE_CACHE define added — scripts will recompile");
            HouseContentBuilder.Rebuild();

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var camGo = new GameObject("LoadingCamera");
            var cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.93f, 0.92f, 0.9f);

            var boot = new GameObject("HouseBootstrap").AddComponent<HouseBootstrap>();
            var so = new SerializedObject(boot);
            so.FindProperty("loadingCamera").objectReferenceValue = cam;
            so.ApplyModifiedPropertiesWithoutUndo();

            AssetPaths.Ensure(AssetPaths.Scenes);
            EditorSceneManager.SaveScene(scene, ScenePath);
            return "[House4696] app scene: " + ScenePath;
        }
    }
}
