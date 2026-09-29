using System.Collections.Generic;
using System.IO;
using System.Linq;
using House4696.Casegoods;
using House4696.Core;
using House4696.Doors;
using House4696.Generation;
using House4696.Model;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.CasegoodsEditor
{
    /// <summary>
    /// Renders a case furniture model alone in the door preview's calibrated studio (a face square to the camera shows
    /// its albedo, so a render and a catalogue photo compare colour for colour): "front" = orthographic, "angle" = from the
    /// front left and above, "side" = orthographic from the left, "top"; open = doors and drawers open.
    /// </summary>
    public static class CasePreview
    {
        static readonly Vector3 Studio = new Vector3(0f, 0f, -600f);

        public static string Render(string model, string finish, string outPath, string view = "front", bool open = false, float pxPerM = 500f)
        {
            // designs edited outside the editor (the 2D tools, a cloud session) reach Resources only after an import
            UnityEditor.AssetDatabase.Refresh();
            CaseCatalog.Reload();
            var cm = CaseCatalog.Model(model);
            if (cm == null) return "[CasePreview] no model " + model;
            var lib = MaterialLibrary.Create();
            var writer = new SceneWriter();
            var doc = new HouseDocument();
            doc.Meta.Name = "case-preview";
            doc.Site.Landscape = LandscapePreset.None;
            doc.Levels.Add(new LevelDef { Id = "ground", Elevation = 0f, Height = 3f, Slab = 0.2f });
            var ps = new JObject { ["open"] = open };
            if (!string.IsNullOrEmpty(finish)) ps["finish"] = finish;
            bool wall = cm.Mount == "wall";
            float H = cm.Size != null && cm.Size.Length > 2 ? cm.Size[2] / 1000f : 1f;
            doc.Items.Add(new ItemDef { Id = "piece", Model = cm.Id, Level = "ground", Position = new Vector3(0f, wall ? H * 0.5f : 0f, 0f), Rotation = 0f, Params = ps });

            var saved = (RenderSettings.ambientMode, RenderSettings.ambientLight, RenderSettings.ambientProbe, RenderSettings.defaultReflectionMode,
                RenderSettings.customReflectionTexture);
            var lights = new List<Light>();
            foreach (var l in Object.FindObjectsByType<Light>()) if (l.enabled) { lights.Add(l); l.enabled = false; }
            GameObject studio = null;
            Cubemap sky = null;
            RenderTexture rt = null;
            Texture2D read = null;
            HouseBuildResult built = null;
            try
            {
                built = HouseBuilder.Build(doc, lib, writer);
                built.House.transform.position = Studio;
                if (built.Site != null) Object.DestroyImmediate(built.Site);
                foreach (var w in built.Warnings ?? new List<string>()) Debug.LogWarning("[CasePreview] " + w);
                var item = built.House.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == "Item_piece");
                if (item == null) return "[CasePreview] the item did not build (see the console)";
                foreach (var r in built.House.GetComponentsInChildren<Renderer>(true))
                    if (!r.transform.IsChildOf(item)) r.enabled = false;
                foreach (var l in built.House.GetComponentsInChildren<Light>(true)) l.enabled = false;
                var b = Bounds(item.gameObject);

                studio = new GameObject("CasePreviewStudio") { hideFlags = HideFlags.HideAndDontSave };
                DoorPreview.AddLight(studio, new Vector3(40f, 215f, 0f), 0.64f, Color.white, true);
                RenderSettings.ambientMode = AmbientMode.Flat;
                float ambLin = 0.6f, ambGamma = Mathf.LinearToGammaSpace(ambLin);
                RenderSettings.ambientLight = new Color(ambGamma, ambGamma, ambGamma);
                var sh = new SphericalHarmonicsL2();
                sh.AddAmbientLight(new Color(ambLin, ambLin, ambLin));
                RenderSettings.ambientProbe = sh;
                sky = DoorPreview.GreySky();
                RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
                RenderSettings.customReflectionTexture = sky;
                // a pale floor under floor pieces (shadows, legs)
                if (!wall)
                {
                    var floor = GameObject.CreatePrimitive(PrimitiveType.Quad);
                    floor.hideFlags = HideFlags.HideAndDontSave;
                    floor.transform.SetParent(studio.transform, false);
                    floor.transform.SetPositionAndRotation(new Vector3(b.center.x, Studio.y + 0.0005f, b.center.z), Quaternion.Euler(90f, 0f, 0f));
                    floor.transform.localScale = new Vector3(8f, 8f, 1f);
                    var fm = new Material(Shader.Find("Universal Render Pipeline/Lit")) { hideFlags = HideFlags.HideAndDontSave, color = new Color(0.93f, 0.93f, 0.92f) };
                    fm.SetFloat("_Smoothness", 0.2f);
                    floor.GetComponent<Renderer>().sharedMaterial = fm;
                    Object.DestroyImmediate(floor.GetComponent<Collider>());
                }

                var camGo = new GameObject("CasePreviewCam") { hideFlags = HideFlags.HideAndDontSave };
                camGo.transform.SetParent(studio.transform, false);
                var cam = camGo.AddComponent<Camera>();
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = Color.white;
                cam.allowHDR = false;
                cam.allowMSAA = false;
                cam.enabled = false;
                var data = cam.GetUniversalAdditionalCameraData();
                data.renderPostProcessing = false;
                data.antialiasing = AntialiasingMode.None;
                data.renderShadows = true;
                data.SetRenderer(0);
                int ss = 2, W, Hpx;
                const float margin = 0.06f;
                if (view == "front" || view == "side" || view == "top")
                {
                    cam.orthographic = true;
                    Vector3 dir; float fw, fh;
                    if (view == "front") { dir = Vector3.back; fw = b.size.x; fh = b.size.y; }
                    else if (view == "side") { dir = Vector3.right; fw = b.size.z; fh = b.size.y; }
                    else { dir = Vector3.down; fw = b.size.x; fh = b.size.z; }
                    fw += 2f * margin; fh += 2f * margin;
                    W = Mathf.RoundToInt(fw * pxPerM); Hpx = Mathf.RoundToInt(fh * pxPerM);
                    cam.orthographicSize = fh * 0.5f;
                    var eye = b.center - dir * 6f;
                    camGo.transform.SetPositionAndRotation(eye, Quaternion.LookRotation(dir, view == "top" ? Vector3.forward : Vector3.up));
                    cam.nearClipPlane = 0.5f; cam.farClipPlane = 20f;
                }
                else
                {
                    W = 1000; Hpx = 1100;
                    cam.orthographic = false;
                    cam.fieldOfView = 32f;
                    float r = b.extents.magnitude;
                    // the front faces +Z: from the front left, a little above eye level
                    var eye = b.center + new Vector3(-0.55f, 0.35f, 1f).normalized * (r / Mathf.Sin(cam.fieldOfView * 0.5f * Mathf.Deg2Rad) * 1.05f);
                    camGo.transform.SetPositionAndRotation(eye, Quaternion.LookRotation(b.center - eye));
                    cam.nearClipPlane = 0.05f; cam.farClipPlane = 60f;
                }
                rt = new RenderTexture(W * ss, Hpx * ss, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
                cam.targetTexture = rt;
                cam.Render();
                AsyncGPUReadback.Request(rt, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                read = new Texture2D(rt.width, rt.height, TextureFormat.RGBA32, false);
                var prev = RenderTexture.active;
                RenderTexture.active = rt;
                read.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
                read.Apply(false);
                RenderTexture.active = prev;
                cam.targetTexture = null;
                var png = DoorPreview.Downsample(read, ss);
                Directory.CreateDirectory(Path.GetDirectoryName(outPath));
                File.WriteAllBytes(outPath, png.EncodeToPNG());
                Object.DestroyImmediate(png);
                return $"[CasePreview] {model} {view}{(open ? " open" : "")} {W}×{Hpx} → {outPath}";
            }
            finally
            {
                foreach (var l in lights) if (l != null) l.enabled = true;
                RenderSettings.ambientMode = saved.Item1;
                RenderSettings.ambientLight = saved.Item2;
                RenderSettings.ambientProbe = saved.Item3;
                RenderSettings.defaultReflectionMode = saved.Item4;
                RenderSettings.customReflectionTexture = saved.Item5;
                if (studio != null) Object.DestroyImmediate(studio);
                if (sky != null) Object.DestroyImmediate(sky);
                if (rt != null) { rt.Release(); Object.DestroyImmediate(rt); }
                if (read != null) Object.DestroyImmediate(read);
                if (built != null)
                {
                    if (built.House != null) Object.DestroyImmediate(built.House);
                    if (built.Site != null) Object.DestroyImmediate(built.Site);
                    foreach (var m in built.CreatedMaterials) if (m != null) Object.DestroyImmediate(m);
                }
                foreach (var m in writer.RuntimeMeshes) if (m != null) Object.DestroyImmediate(m);
            }
        }

        static Bounds Bounds(GameObject go)
        {
            var rs = go.GetComponentsInChildren<Renderer>(true);
            var b = rs.Length > 0 ? rs[0].bounds : new Bounds(go.transform.position, Vector3.one);
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }
    }
}
