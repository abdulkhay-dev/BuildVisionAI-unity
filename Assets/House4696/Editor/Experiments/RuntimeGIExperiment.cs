using System.IO;
using House4696.Core;
using House4696.Setup;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Experiments
{
    /// <summary>
    /// Stage-0 prototype: can the house look right without an editor bake? Copies the baked scene, strips all
    /// baked lighting (APV, baked reflection probes) and lights it with URP's realtime Surface Cache GI, then
    /// renders the same tour viewpoints from both scenes for side-by-side comparison.
    /// </summary>
    public static class RuntimeGIExperiment
    {
        const string RtScenePath = AssetPaths.Scenes + "/Experiments/House_46-96_RT.unity";
        const float EyeHeight = 1.66f, Fov = 70f;

        [MenuItem("House 46-96/Experiments/Prepare Runtime-GI Scene")]
        public static void PrepareMenu() => Debug.Log(Prepare());

        public static string Prepare()
        {
            if (EditorApplication.isPlaying) return "exit play mode first";
            int rendererIndex = RealtimeGISetup.EnsureRenderer();
            var profile = RealtimeGISetup.EnsureProfile();

            var src = EditorSceneManager.OpenScene(AssetPaths.ScenePath, OpenSceneMode.Single);
            AssetPaths.Ensure(Path.GetDirectoryName(RtScenePath)?.Replace('\\', '/'));
            EditorSceneManager.SaveScene(src, RtScenePath, true);
            var scene = EditorSceneManager.OpenScene(RtScenePath, OpenSceneMode.Single);

            // no baked data at all: this is what the app will have for a house built at runtime
            Lightmapping.lightingDataAsset = null;
            foreach (var pv in Object.FindObjectsByType<ProbeVolume>()) Object.DestroyImmediate(pv.gameObject);
            foreach (var l in Object.FindObjectsByType<Light>()) l.lightmapBakeType = LightmapBakeType.Realtime;
            foreach (var p in Object.FindObjectsByType<ReflectionProbe>())
            {
                p.mode = ReflectionProbeMode.Realtime;
                p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
                p.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            }

            var volGo = new GameObject("SurfaceCacheGI_Volume");
            var vol = volGo.AddComponent<Volume>();
            vol.isGlobal = true;
            vol.priority = 10;
            vol.sharedProfile = profile;

            var cam = Camera.main;
            if (cam != null) cam.GetUniversalAdditionalCameraData().SetRenderer(rendererIndex);

            EditorSceneManager.SaveScene(scene);
            return $"[RuntimeGI] prepared {RtScenePath} (renderer #{rendererIndex})";
        }

        /// <summary>
        /// Renders tour stops [from, to) of the currently open scene into Renders/gi/{index}_{tag}.png.
        /// Realtime GI accumulates over frames, so each view is rendered <paramref name="frames"/> times first.
        /// </summary>
        public static string RenderStops(string tag, int from, int to, int frames, int width = 1280, int height = 800)
        {
            string dir = Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? "", "Renders", "gi");
            Directory.CreateDirectory(dir);
            var stops = TourSpec.Walk();
            foreach (var p in Object.FindObjectsByType<ReflectionProbe>())
                if (p.mode == ReflectionProbeMode.Realtime) p.RenderProbe();

            var main = Camera.main;
            var go = new GameObject("GIRenderCamera") { hideFlags = HideFlags.HideAndDontSave };
            var cam = go.AddComponent<Camera>();
            if (main != null) cam.CopyFrom(main);
            var data = cam.GetUniversalAdditionalCameraData();
            var mainData = main != null ? main.GetUniversalAdditionalCameraData() : null;
            if (mainData != null) data.SetRenderer(RendererIndexOf(main));
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            cam.usePhysicalProperties = false;
            cam.lensShift = Vector2.zero;
            cam.fieldOfView = Fov;
            cam.nearClipPlane = 0.05f;
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            cam.targetTexture = rt;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var names = new System.Collections.Generic.List<string>();
            for (int i = from; i < Mathf.Min(to, stops.Length); i++)
            {
                var s = stops[i];
                go.transform.SetPositionAndRotation(s.Feet + Vector3.up * EyeHeight, Quaternion.Euler(s.Pitch, s.Yaw, 0f));
                for (int f = 0; f < frames; f++) cam.Render();
                var prev = RenderTexture.active;
                RenderTexture.active = rt;
                var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                File.WriteAllBytes(Path.Combine(dir, $"{i:00}_{tag}.png"), tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
                names.Add(s.Name);
            }
            cam.targetTexture = null;
            rt.Release();
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(go);
            return $"[RuntimeGI] {tag}: {string.Join(", ", names)} in {sw.ElapsedMilliseconds} ms";
        }

        /// <summary>
        /// Realtime probes do not render outside play mode, so each probe is captured by a regular game camera
        /// (which also gets Surface Cache GI) into a cubemap and assigned as the probe's custom texture.
        /// Run after the GI has converged (e.g. after <see cref="RenderStops"/>).
        /// </summary>
        public static string CaptureProbes(int maxSize = 256)
        {
            var main = Camera.main;
            var go = new GameObject("ProbeCaptureCamera") { hideFlags = HideFlags.HideAndDontSave };
            var cam = go.AddComponent<Camera>();
            if (main != null) cam.CopyFrom(main);
            cam.usePhysicalProperties = false;
            cam.lensShift = Vector2.zero;
            var data = cam.GetUniversalAdditionalCameraData();
            if (main != null) data.SetRenderer(RendererIndexOf(main));
            data.renderPostProcessing = false;
            int n = 0;
            foreach (var p in Object.FindObjectsByType<ReflectionProbe>())
            {
                int size = Mathf.Min(p.resolution, maxSize);
                var rt = new RenderTexture(size, size, 24, RenderTextureFormat.ARGBHalf)
                {
                    dimension = TextureDimension.Cube, useMipMap = true, autoGenerateMips = true,
                    name = "Probe_" + p.name, hideFlags = HideFlags.DontSave
                };
                rt.Create();
                go.transform.SetPositionAndRotation(p.transform.position, Quaternion.identity);
                cam.cullingMask = p.cullingMask;
                cam.nearClipPlane = p.nearClipPlane;
                cam.farClipPlane = p.farClipPlane;
                cam.clearFlags = CameraClearFlags.Skybox;
                cam.RenderToCubemap(rt, 63);
                p.mode = ReflectionProbeMode.Custom;
                p.customBakedTexture = rt;
                n++;
            }
            Object.DestroyImmediate(go);
            return $"[RuntimeGI] captured {n} probes";
        }

        /// <summary>Index of the renderer the camera uses (reflection: the field is not exposed publicly).</summary>
        static int RendererIndexOf(Camera cam)
        {
            var data = cam.GetUniversalAdditionalCameraData();
            var f = typeof(UniversalAdditionalCameraData).GetField("m_RendererIndex",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            int idx = f != null ? (int)f.GetValue(data) : -1;
            return idx < 0 ? 0 : idx;
        }
    }
}
