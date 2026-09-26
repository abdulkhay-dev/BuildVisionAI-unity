using System.Collections.Generic;
using System.IO;
using House4696.App;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Setup
{
    /// <summary>
    /// Pictures of every catalogue model for the furniture library: each model is built as the app builds it (default
    /// parameters), lit in a small studio far from the scene (key, fill and rim lights, soft ambient, a grey sky to reflect)
    /// and rendered at 2× on a transparent background, then halved to <see cref="Width"/>×<see cref="Height"/> PNGs in
    /// Resources/CatalogThumbs, with catalog.json holding every model's measured extent (the library's sizes and placement
    /// rules). Runs in the background, a few models per editor tick; "[Thumbs] done" in the console when finished.
    /// Re-run after importing new models (House 46-96 → External → Import Catalog).
    /// </summary>
    public static class CatalogThumbnails
    {
        public const int Width = 320, Height = 240, Supersample = 2;
        const string Folder = AssetPaths.Root + "/Resources/" + FurnitureCatalog.ThumbFolder;
        static readonly Vector3 Studio = new Vector3(5000f, 0f, 5000f);
        const float Fov = 24f;

        static Queue<ItemModel> _queue;
        static JObject _manifest;
        static MaterialLibrary _lib;
        static HouseContext _ctx;
        static SceneWriter _writer;
        static GameObject _studio;
        static Camera _cam;
        static RenderTexture _rt;
        static Texture2D _read;
        static List<(Light light, bool enabled)> _otherLights;
        static (AmbientMode mode, Color color, SphericalHarmonicsL2 probe, DefaultReflectionMode refl, Texture custom) _env;
        static Cubemap _sky;
        static int _done, _total;
        static System.Diagnostics.Stopwatch _sw;

        public static bool Busy => _queue != null;

        [MenuItem("House 46-96/External/Render Catalog Thumbnails", priority = 72)]
        public static void Menu() => Debug.Log(Start());

        /// <summary>Starts rendering all models (or only <paramref name="ids"/>); returns at once.</summary>
        public static string Start(IEnumerable<string> ids = null)
        {
            if (Busy) return "[Thumbs] busy";
            if (EditorApplication.isPlaying) return "[Thumbs] exit play mode first";
            var only = ids != null ? new HashSet<string>(ids) : null;
            _queue = new Queue<ItemModel>();
            foreach (var m in ItemCatalog.All)
                if (only == null || only.Contains(m.Id)) _queue.Enqueue(m);
            _total = _queue.Count;
            _done = 0;
            _sw = System.Diagnostics.Stopwatch.StartNew();
            AssetPaths.Ensure(Folder);
            string manifestPath = Folder + "/" + FurnitureCatalog.ManifestName + ".json";
            _manifest = File.Exists(manifestPath) ? JObject.Parse(File.ReadAllText(manifestPath)) : new JObject();
            if (!(_manifest["models"] is JObject)) _manifest["models"] = new JObject();
            try { SetUp(); }
            catch (System.Exception e)
            {
                TearDown();
                return "[Thumbs] set-up failed: " + e;
            }
            EditorApplication.update += Tick;
            return $"[Thumbs] started: {_total} models";
        }

        static void Tick()
        {
            if (_queue == null) return;
            try
            {
                // a few per tick: each is a build, one render and a read-back
                for (int i = 0; i < 3 && _queue.Count > 0; i++) Render(_queue.Dequeue());
                if (_queue.Count > 0) return;
                Finish();
            }
            catch (System.Exception e)
            {
                Debug.LogError("[Thumbs] failed: " + e);
                EditorApplication.update -= Tick;
                TearDown();
            }
        }

        static void Finish()
        {
            EditorApplication.update -= Tick;
            File.WriteAllText(Folder + "/" + FurnitureCatalog.ManifestName + ".json", _manifest.ToString(Newtonsoft.Json.Formatting.Indented));
            TearDown();
            AssetDatabase.Refresh();
            Debug.Log($"[Thumbs] done: {_done}/{_total} models in {_sw.ElapsedMilliseconds} ms → {Folder}");
        }

        // ------------------------------------------------------------------ studio
        static void SetUp()
        {
            _lib = MaterialLibrary.Create();
            _writer = new SceneWriter();
            var doc = new HouseDocument();
            doc.Levels.Add(new LevelDef { Id = "ground" });
            _ctx = new HouseContext(doc, _lib, _writer);

            // only the studio's lights: the open scene's are switched off for the job
            _otherLights = new List<(Light, bool)>();
            foreach (var l in Object.FindObjectsByType<Light>())
                if (l.enabled) { _otherLights.Add((l, true)); l.enabled = false; }

            _studio = new GameObject("CatalogThumbStudio") { hideFlags = HideFlags.HideAndDontSave };
            _studio.transform.position = Studio;
            AddLight("Key", new Vector3(38f, -142f, 0f), 2.1f, new Color(1f, 0.97f, 0.92f), true);
            AddLight("Fill", new Vector3(18f, 125f, 0f), 0.7f, new Color(0.88f, 0.92f, 1f), false);
            AddLight("Rim", new Vector3(28f, 10f, 0f), 1.0f, Color.white, false);

            _env = (RenderSettings.ambientMode, RenderSettings.ambientLight, RenderSettings.ambientProbe, RenderSettings.defaultReflectionMode,
                RenderSettings.customReflectionTexture);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.42f, 0.43f, 0.45f);
            var sh = new SphericalHarmonicsL2();
            sh.AddAmbientLight(new Color(0.42f, 0.43f, 0.45f));
            RenderSettings.ambientProbe = sh;
            _sky = GreySky();
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = _sky;

            var go = new GameObject("ThumbCamera") { hideFlags = HideFlags.HideAndDontSave };
            go.transform.SetParent(_studio.transform, false);
            _cam = go.AddComponent<Camera>();
            _cam.clearFlags = CameraClearFlags.SolidColor;
            _cam.backgroundColor = new Color(0f, 0f, 0f, 0f);
            _cam.allowHDR = false;                 // an 8-bit target keeps the alpha
            _cam.allowMSAA = false;                // supersampled instead
            _cam.fieldOfView = Fov;
            _cam.nearClipPlane = 0.02f;
            _cam.farClipPlane = 80f;
            _cam.enabled = false;
            var data = _cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = false;
            data.antialiasing = AntialiasingMode.None;
            data.renderShadows = true;
            data.SetRenderer(0);
            _rt = new RenderTexture(Width * Supersample, Height * Supersample, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            _cam.targetTexture = _rt;
            _read = new Texture2D(_rt.width, _rt.height, TextureFormat.RGBA32, false);
        }

        static void AddLight(string name, Vector3 euler, float intensity, Color color, bool shadows)
        {
            var go = new GameObject("Studio" + name) { hideFlags = HideFlags.HideAndDontSave };
            go.transform.SetParent(_studio.transform, false);
            go.transform.rotation = Quaternion.Euler(euler);
            var l = go.AddComponent<Light>();
            l.type = LightType.Directional;
            l.intensity = intensity;
            l.color = color;
            l.shadows = shadows ? LightShadows.Soft : LightShadows.None;
            l.shadowStrength = 0.6f;
        }

        /// <summary>A tiny cubemap: light above, mid grey at the horizon, dark below — something for metal and gloss to reflect.</summary>
        static Cubemap GreySky()
        {
            const int n = 16;
            var cube = new Cubemap(n, TextureFormat.RGBA32, false) { hideFlags = HideFlags.HideAndDontSave };
            var faces = new[] { CubemapFace.PositiveX, CubemapFace.NegativeX, CubemapFace.PositiveY, CubemapFace.NegativeY, CubemapFace.PositiveZ, CubemapFace.NegativeZ };
            foreach (var f in faces)
            {
                var px = new Color[n * n];
                for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float u = (x + 0.5f) / n * 2f - 1f, v = (y + 0.5f) / n * 2f - 1f;
                    Vector3 d = f switch
                    {
                        CubemapFace.PositiveX => new Vector3(1f, -v, -u),
                        CubemapFace.NegativeX => new Vector3(-1f, -v, u),
                        CubemapFace.PositiveY => new Vector3(u, 1f, v),
                        CubemapFace.NegativeY => new Vector3(u, -1f, -v),
                        CubemapFace.PositiveZ => new Vector3(u, -v, 1f),
                        _ => new Vector3(-u, -v, -1f),
                    };
                    float h = d.normalized.y;
                    float g = h > 0f ? Mathf.Lerp(0.55f, 0.9f, h) : Mathf.Lerp(0.55f, 0.18f, -h);
                    px[y * n + x] = new Color(g, g, g * 1.02f, 1f);
                }
                cube.SetPixels(px, f);
            }
            cube.Apply();
            return cube;
        }

        static void TearDown()
        {
            if (_otherLights != null)
                foreach (var (light, enabled) in _otherLights)
                    if (light != null) light.enabled = enabled;
            _otherLights = null;
            if (_studio != null)
            {
                RenderSettings.ambientMode = _env.mode;
                RenderSettings.ambientLight = _env.color;
                RenderSettings.ambientProbe = _env.probe;
                RenderSettings.defaultReflectionMode = _env.refl;
                RenderSettings.customReflectionTexture = _env.custom;
            }
            if (_cam != null) _cam.targetTexture = null;
            if (_studio != null) Object.DestroyImmediate(_studio);
            if (_rt != null) { _rt.Release(); Object.DestroyImmediate(_rt); }
            if (_read != null) Object.DestroyImmediate(_read);
            if (_sky != null) Object.DestroyImmediate(_sky);
            if (_ctx != null) foreach (var m in _ctx.Mats.Created) if (m != null) Object.DestroyImmediate(m);
            _studio = null; _cam = null; _rt = null; _read = null; _sky = null; _ctx = null; _writer = null;
            _queue = null;
        }

        // ------------------------------------------------------------------ one model
        static void Render(ItemModel m)
        {
            var def = new ItemDef { Id = "thumb", Model = m.Id };
            var go = HouseBuilder.BuildItemObject(_ctx, def, _studio.transform, _writer);
            if (go == null) { Debug.LogWarning("[Thumbs] " + m.Id + ": the model did not build"); return; }
            try
            {
                // front towards +Z, the model's origin at the studio
                go.transform.SetPositionAndRotation(Studio, FurnitureGeometry.ItemRotation(0f));
                var local = ItemBox.LocalBounds(go);
                _manifest["models"][m.Id] = new JObject
                {
                    ["min"] = new JArray(R(local.min.x), R(local.min.y), R(local.min.z)),
                    ["max"] = new JArray(R(local.max.x), R(local.max.y), R(local.max.z)),
                };
                Frame(go, local, m);
                _cam.Render();
                AsyncGPUReadback.Request(_rt, 0, 0, 1, 0, 1, 0, 1).WaitForCompletion();
                var prev = RenderTexture.active;
                RenderTexture.active = _rt;
                _read.ReadPixels(new Rect(0, 0, _rt.width, _rt.height), 0, 0);
                _read.Apply(false);
                RenderTexture.active = prev;
                var png = Downsample(_read);
                File.WriteAllBytes(Folder + "/" + m.Id + ".png", png.EncodeToPNG());
                Object.DestroyImmediate(png);
                _done++;
            }
            finally
            {
                _writer.Release(go);
                Object.DestroyImmediate(go);
            }
        }

        /// <summary>
        /// A three-quarter view from the front-left and a little above, fitted to the model's box with a margin. Wall pieces are
        /// seen almost frontally, ceiling pieces from slightly below.
        /// </summary>
        static void Frame(GameObject go, Bounds local, ItemModel m)
        {
            var b = local;
            // the same classes as the library's placement (FurnitureCatalog): ceiling, wall, floor; flat ones seen more from above / below
            bool ceiling = b.max.y <= 0.02f && (b.min.y < -0.05f || m.Category == "lighting");
            bool wall = !ceiling && b.max.z <= 0.03f && b.min.y < -0.05f && b.max.y > 0.05f;
            bool flat = b.size.y < 0.05f;
            float yaw = wall ? 18f : 32f;
            float pitch = wall ? 6f : ceiling ? (flat ? -60f : -8f) : flat ? 55f : b.size.y < 0.25f ? 38f : 20f;
            // the direction from the model to the camera: in front (+Z) turned by yaw, raised by pitch
            var dir = Quaternion.Euler(-pitch, yaw, 0f) * Vector3.forward;
            var rot = Quaternion.LookRotation(-dir, Vector3.up);
            var toWorld = go.transform.localToWorldMatrix;
            var centre = toWorld.MultiplyPoint3x4(b.center);
            float tanV = Mathf.Tan(Fov * 0.5f * Mathf.Deg2Rad) * 0.84f;
            float tanH = tanV * Width / Height;
            var inv = Quaternion.Inverse(rot);
            float d = 0.3f;
            for (int i = 0; i < 8; i++)
            {
                var c = new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y, (i & 4) == 0 ? b.min.z : b.max.z);
                var v = inv * (toWorld.MultiplyPoint3x4(c) - centre);
                d = Mathf.Max(d, Mathf.Abs(v.x) / tanH - v.z, Mathf.Abs(v.y) / tanV - v.z);
            }
            _cam.transform.SetPositionAndRotation(centre - rot * Vector3.forward * d, rot);
            _cam.nearClipPlane = Mathf.Max(0.01f, d * 0.02f);
            _cam.farClipPlane = d * 4f + b.size.magnitude * 2f;
            // the lights follow the view (a light's yaw = where it shines = its side + 180°): the key from the camera's upper
            // left, the fill from its right, the rim from behind the model
            var key = _studio.transform.Find("StudioKey");
            if (key != null) key.rotation = Quaternion.Euler(40f, yaw + 225f, 0f);
            var fill = _studio.transform.Find("StudioFill");
            if (fill != null) fill.rotation = Quaternion.Euler(15f, yaw + 110f, 0f);
            var rim = _studio.transform.Find("StudioRim");
            if (rim != null) rim.rotation = Quaternion.Euler(35f, yaw + 15f, 0f);
        }

        /// <summary>2×2 box filter with premultiplied alpha (no dark fringes on the transparent edge).</summary>
        static Texture2D Downsample(Texture2D src)
        {
            var px = src.GetPixels32();
            int w = src.width, h = src.height, ow = w / Supersample, oh = h / Supersample;
            var outPx = new Color32[ow * oh];
            for (int y = 0; y < oh; y++)
            for (int x = 0; x < ow; x++)
            {
                float r = 0, g = 0, bl = 0, a = 0;
                for (int sy = 0; sy < Supersample; sy++)
                for (int sx = 0; sx < Supersample; sx++)
                {
                    var c = px[(y * Supersample + sy) * w + x * Supersample + sx];
                    float ca = c.a / 255f;
                    r += c.r * ca; g += c.g * ca; bl += c.b * ca; a += ca;
                }
                int n = Supersample * Supersample;
                outPx[y * ow + x] = a > 1e-4f
                    ? new Color32((byte)Mathf.Clamp(Mathf.RoundToInt(r / a), 0, 255), (byte)Mathf.Clamp(Mathf.RoundToInt(g / a), 0, 255),
                        (byte)Mathf.Clamp(Mathf.RoundToInt(bl / a), 0, 255), (byte)Mathf.Clamp(Mathf.RoundToInt(a / n * 255f), 0, 255))
                    : new Color32(0, 0, 0, 0);
            }
            var tex = new Texture2D(ow, oh, TextureFormat.RGBA32, false);
            tex.SetPixels32(outPx);
            tex.Apply(false);
            return tex;
        }

        static double R(float v) => System.Math.Round(v, 3);
    }

    /// <summary>Import settings of the library pictures: UI textures with alpha, no mipmaps, clamped.</summary>
    public sealed class CatalogThumbImport : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if (!assetPath.Replace('\\', '/').Contains("/Resources/" + FurnitureCatalog.ThumbFolder + "/")) return;
            var ti = (TextureImporter)assetImporter;
            ti.textureType = TextureImporterType.Default;
            ti.sRGBTexture = true;
            ti.alphaSource = TextureImporterAlphaSource.FromInput;
            ti.alphaIsTransparency = true;
            ti.mipmapEnabled = false;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.maxTextureSize = 512;
            ti.textureCompression = TextureImporterCompression.CompressedHQ;
        }
    }
}
