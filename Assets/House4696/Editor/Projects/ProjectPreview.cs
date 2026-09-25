using System.IO;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using House4696.Setup;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Projects
{
    /// <summary>
    /// Edit-mode preview of a house document exactly as the app builds it: palette materials, meshes in memory,
    /// no bake, realtime Surface Cache GI. Used to compare generated projects with the hand-coded original.
    /// </summary>
    public static class ProjectPreview
    {
        [MenuItem("House 46-96/Projects/Preview Project (realtime GI)…", priority = 61)]
        public static void PreviewMenu()
        {
            string path = EditorUtility.OpenFilePanel("House project", Path.Combine(Application.streamingAssetsPath, "Samples"), "json");
            if (!string.IsNullOrEmpty(path)) Debug.Log(Build(path));
        }

        public static House4696.Generation.HouseBuildResult Last { get; private set; }

        public static string Build(string jsonPath)
        {
            if (EditorApplication.isPlaying) return "exit play mode first";
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var doc = HouseJson.Deserialize(File.ReadAllText(jsonPath));
            var issues = HouseValidator.Validate(doc);
            var content = HouseContent.Load();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var lib = MaterialLibrary.Create();
            var result = HouseBuilder.Build(doc, lib, new SceneWriter());
            Last = result;
            var env = EnvironmentBuilder.Build(lib, content.PostProcessProfile, EnvironmentBuilder.SunFrom(doc.Site.SunAzimuth, doc.Site.SunElevation));

            int layer = LayerMask.NameToLayer("House");
            if (layer >= 0) foreach (var t in result.House.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            var garden = env.GetComponentInChildren<ReflectionProbe>();
            if (garden != null && layer >= 0) garden.cullingMask = ~(1 << layer);
            foreach (var p in Object.FindObjectsByType<ReflectionProbe>())
            {
                p.mode = ReflectionProbeMode.Realtime;
                p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
            }
            var vol = new GameObject("RealtimeGI_Volume").AddComponent<Volume>();
            vol.isGlobal = true; vol.priority = 10; vol.sharedProfile = content.RealtimeGIProfile;
            Camera.main.GetUniversalAdditionalCameraData().SetRenderer(content.RealtimeGIRendererIndex);
            return $"[ProjectPreview] {doc.Meta.Name}: built in {sw.ElapsedMilliseconds} ms, {result.Colliders} colliders, " +
                   $"{issues.Count} validation issues{(issues.Count > 0 ? ":\n  " + string.Join("\n  ", issues) : "")}, " +
                   $"{result.Warnings.Count} build warnings{(result.Warnings.Count > 0 ? ": " + string.Join(" | ", result.Warnings) : "")}";
        }
    }
}
