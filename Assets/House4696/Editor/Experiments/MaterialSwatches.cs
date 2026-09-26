using System.IO;
using House4696.Core;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Experiments
{
    /// <summary>
    /// Swatches of the library materials for review: a 1 × 1 m quad per material (real scale) under a low sun, so
    /// relief, roughness and tiling show. Renders in batches (keep each call short: long synchronous renders time out the
    /// MCP bridge) into PNG files named by material id.
    /// </summary>
    public static class MaterialSwatches
    {
        public static string Render(string dir, int start, int count, int size = 256)
        {
            var catalog = ExternalCatalog.Load();
            if (catalog == null) return "no external catalog";
            if (start == 0) Setup();
            var quad = GameObject.Find("SwatchQuad");
            var cam = GameObject.Find("SwatchCamera")?.GetComponent<Camera>();
            if (quad == null || cam == null) return "run with start = 0 first";
            Directory.CreateDirectory(dir);
            var rt = new RenderTexture(size, size, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            cam.targetTexture = rt;
            var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
            var r = quad.GetComponent<MeshRenderer>();
            int done = 0;
            for (int i = start; i < Mathf.Min(catalog.Materials.Count, start + count); i++, done++)
            {
                var e = catalog.Materials[i];
                r.sharedMaterial = e.Material;
                cam.Render();
                cam.Render();
                AsyncGPUReadback.Request(rt, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, size, size), 0, 0);
                tex.Apply();
                RenderTexture.active = null;
                File.WriteAllBytes(Path.Combine(dir, $"{i:000}_{e.Id}.png"), tex.EncodeToPNG());
            }
            cam.targetTexture = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
            return $"rendered {done} swatches ({start}..{start + done - 1} of {catalog.Materials.Count})";
        }

        /// <summary>Library models from a 3/4 front view, framed by their bounds (front = -Z, as placed in houses).</summary>
        public static string RenderModels(string dir, int start, int count, int size = 320)
        {
            var catalog = ExternalCatalog.Load();
            if (catalog == null) return "no external catalog";
            if (start == 0) Setup();
            var cam = GameObject.Find("SwatchCamera")?.GetComponent<Camera>();
            var quad = GameObject.Find("SwatchQuad");
            if (cam == null) return "run with start = 0 first";
            if (quad != null) quad.SetActive(false);
            cam.orthographic = false;
            cam.fieldOfView = 30f;
            Directory.CreateDirectory(dir);
            var rt = new RenderTexture(size, size, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = 4 };
            cam.targetTexture = rt;
            var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
            int done = 0;
            for (int i = start; i < Mathf.Min(catalog.Models.Count, start + count); i++, done++)
            {
                var e = catalog.Models[i];
                var go = (GameObject)Object.Instantiate(e.Prefab);
                var b = new Bounds(go.transform.position, Vector3.zero);
                foreach (var r in go.GetComponentsInChildren<Renderer>()) b.Encapsulate(r.bounds);
                float radius = b.extents.magnitude;
                var dirToCam = Quaternion.Euler(22f, 35f, 0f) * Vector3.back;   // front (-Z), from the right, above
                cam.transform.position = b.center + dirToCam * (radius / Mathf.Sin(cam.fieldOfView * 0.5f * Mathf.Deg2Rad));
                cam.transform.LookAt(b.center);
                cam.nearClipPlane = 0.01f;
                cam.farClipPlane = radius * 10f + 10f;
                cam.Render();
                cam.Render();
                AsyncGPUReadback.Request(rt, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, size, size), 0, 0);
                tex.Apply();
                RenderTexture.active = null;
                File.WriteAllBytes(Path.Combine(dir, $"{i:000}_{e.Id}.png"), tex.EncodeToPNG());
                Object.DestroyImmediate(go);
            }
            cam.targetTexture = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
            return $"rendered {done} models ({start}..{start + done - 1} of {catalog.Models.Count})";
        }

        static void Setup()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.63f, 0.63f, 0.64f);
            RenderSettings.ambientEquatorColor = new Color(0.45f, 0.44f, 0.42f);
            RenderSettings.ambientGroundColor = new Color(0.2f, 0.2f, 0.2f);
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 2.2f;
            sun.color = new Color(1f, 0.97f, 0.92f);
            sun.shadows = LightShadows.None;
            sun.transform.rotation = Quaternion.Euler(35f, -40f, 0f);   // low, from the side: relief shows
            var quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
            quad.name = "SwatchQuad";
            Object.DestroyImmediate(quad.GetComponent<Collider>());
            quad.transform.rotation = Quaternion.Euler(90f, 0f, 0f);    // lying flat, UV 0..1 = 1 m
            var cam = new GameObject("SwatchCamera").AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 0.5f;
            cam.transform.SetPositionAndRotation(new Vector3(0f, 2f, 0f), Quaternion.Euler(90f, 0f, 0f));
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.white;
        }
    }
}
