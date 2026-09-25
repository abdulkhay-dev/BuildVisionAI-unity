using System.Diagnostics;
using System.IO;
using System.Linq;
using House4696.Core;
using House4696.House;
using House4696.Landscape;
using House4696.Setup;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Debug = UnityEngine.Debug;

namespace House4696
{
    /// <summary>
    /// Entry points: rebuild the whole scene from code (house + garden + lighting) and render the
    /// calibrated reference view to a PNG for side-by-side comparison with the source image.
    /// </summary>
    public static class HouseMenu
    {
        [MenuItem("House 46-96/Rebuild Scene", priority = 0)]
        public static void RebuildMenu() => Debug.Log(Build(false));

        [MenuItem("House 46-96/Regenerate Textures and Rebuild", priority = 1)]
        public static void RebuildAllMenu() => Debug.Log(Build(true));

        [MenuItem("House 46-96/Render Reference View (1600x1195)", priority = 20)]
        public static void RenderMenu()
        {
            string dir = Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? "", "Renders");
            Directory.CreateDirectory(dir);
            string path = Path.Combine(dir, "reference_view.png");
            Debug.Log(Render(path, CameraSpec.RefWidth, CameraSpec.RefHeight));
            EditorUtility.RevealInFinder(path);
        }

        [MenuItem("House 46-96/Reset Camera to Reference View", priority = 21)]
        public static void ResetCamera()
        {
            var cam = Camera.main;
            if (cam != null) { EnvironmentSetup.ApplyCamera(cam); EditorUtility.SetDirty(cam); }
        }

        public static string Build(bool forceTextures)
        {
            var sw = Stopwatch.StartNew();
            EnvironmentSetup.ConfigurePipeline();
            TextureFactory.GenerateAll(forceTextures);
            long tTex = sw.ElapsedMilliseconds;
            MaterialLibrary.Source = new AssetMaterialSource();
            var mats = MaterialLibrary.Create();

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var writer = new SceneWriter(new AssetSceneWriterHooks(AssetPaths.Meshes + "/SceneMeshes.asset"));
            var house = new HouseGenerator(mats, writer).Build();
            var landscape = new LandscapeGenerator(mats, writer, CameraSpec.Position, CameraSpec.Forward).Build();
            int colliders = CollisionSetup.Apply(house, landscape);
            var env = EnvironmentSetup.Build(mats);
            ReflectionSetup.Apply(house, env.GetComponentInChildren<ReflectionProbe>());
            AssetDatabase.SaveAssets();
            AssetPaths.Ensure(AssetPaths.Scenes);
            EditorSceneManager.SaveScene(scene, AssetPaths.ScenePath);
            GlobalIlluminationSetup.Prepare(scene, RenderSettings.sun, house, landscape);
            EditorSceneManager.SaveScene(scene);
            long tGeo = sw.ElapsedMilliseconds;

            string bake = EnvironmentSetup.BakeEnvironment();
            EditorSceneManager.SaveScene(scene);
            AddToBuildSettings(AssetPaths.ScenePath);
            string content = HouseContentBuilder.Rebuild();

            int verts = Object.FindObjectsByType<MeshFilter>().Sum(f => f.sharedMesh != null ? f.sharedMesh.vertexCount : 0);
            return $"[House4696] built in {sw.ElapsedMilliseconds} ms (textures {tTex} ms, geometry {tGeo - tTex} ms); {bake}; colliders: {colliders}; vertices in scene: {verts:N0}; {content}";
        }

        static void AddToBuildSettings(string scenePath)
        {
            var list = EditorBuildSettings.scenes.ToList();
            if (list.Any(s => s.path == scenePath)) return;
            list.Insert(0, new EditorBuildSettingsScene(scenePath, true));
            EditorBuildSettings.scenes = list.ToArray();
        }

        /// <summary>Renders an arbitrary viewpoint with a temporary camera (inspection of the sides not in the reference).</summary>
        public static string RenderFrom(string absPath, Vector3 position, Vector3 lookAt, float fov = 50f, int width = 1400, int height = 900)
        {
            var main = Camera.main;
            var go = new GameObject("TempRenderCamera") { hideFlags = HideFlags.HideAndDontSave };
            var cam = go.AddComponent<Camera>();
            if (main != null) cam.CopyFrom(main);
            cam.usePhysicalProperties = false;
            cam.fieldOfView = fov;
            cam.lensShift = Vector2.zero;
            go.transform.position = position;
            go.transform.LookAt(lookAt);
            var data = UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam);
            data.renderPostProcessing = true;
            data.antialiasing = UnityEngine.Rendering.Universal.AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            cam.targetTexture = rt;
            cam.Render();
            var prevActive = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            RenderTexture.active = prevActive;
            cam.targetTexture = null;
            File.WriteAllBytes(absPath, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            rt.Release();
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(go);
            return "rendered " + absPath;
        }

        /// <summary>Renders the main camera to a PNG (absolute path). Used for comparison with the reference image.</summary>
        public static string Render(string absPath, int width, int height)
        {
            var cam = Camera.main;
            if (cam == null) return "no main camera";
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = 1 };
            var prev = cam.targetTexture;
            cam.targetTexture = rt;
            cam.Render();
            var prevActive = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            RenderTexture.active = prevActive;
            cam.targetTexture = prev;
            Directory.CreateDirectory(Path.GetDirectoryName(absPath) ?? ".");
            File.WriteAllBytes(absPath, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            rt.Release();
            Object.DestroyImmediate(rt);
            return "rendered " + absPath;
        }
    }
}
