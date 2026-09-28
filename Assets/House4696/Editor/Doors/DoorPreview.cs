using System.Collections.Generic;
using System.IO;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Doors
{
    /// <summary>
    /// Renders catalogue doors in a studio for checking them against the catalogue: a door block standing in a short
    /// partition, lit evenly like the manufacturer's renders. "front" is orthographic and square-on from the side the door
    /// opens to (the catalogue's view: handle on the left, hinges on the right) at 0.4 px/mm — the scale of the big
    /// catalogue photos — with the wall hidden; "angle" is a 3/4 perspective with the wall.
    /// Call from the editor (MCP execute_code): DoorPreview.Render(new DoorPreview.Shot { Model = "porta-22" }, path).
    /// </summary>
    public static class DoorPreview
    {
        public sealed class Shot
        {
            public string Model, Finish, Glass;
            /// <summary>Entrance doors: finish of the inner panel.</summary>
            public string FinishIn;
            public Vector2 Leaf = new Vector2(0.8f, 2.0f);
            public bool HingeStart = true;
            public int Swing = 1;
            public bool Open;
            /// <summary>front · back · angle · angleBack</summary>
            public string View = "front";
            public float Wall = 0.12f;
            /// <summary>swing · sliding · folding · portal; leaves 1–2 (4 panels for a folding door).</summary>
            public string Kind;
            public int? Leaves;
            /// <summary>Pixels per metre of a front view.</summary>
            public float PxPerM = 400f;
            public bool HideWall = true;
            /// <summary>A ready document instead of the door test wall (window previews); its first opening is framed.</summary>
            public HouseDocument Doc;
            /// <summary>Front view: the framed size (m) and the height of its centre, when not the door's.</summary>
            public Vector2? FrontSize;
            public float? FrontCenterY;
        }

        static readonly Vector3 Studio = new Vector3(0f, 0f, -600f);

        /// <summary>Renders the shot into <paramref name="path"/> (PNG); returns a line about what was written.</summary>
        public static string Render(Shot s, string path)
        {
            var lib = MaterialLibrary.Create();
            var writer = new SceneWriter();
            var doc = s.Doc ?? Document(s);
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
                foreach (var r in built.House.GetComponentsInChildren<Renderer>(true))
                    if (r.name.StartsWith("DownLight") || r.name.StartsWith("Room")) r.enabled = false;
                bool front = s.View == "front" || s.View == "back";
                if (s.HideWall || front)
                    foreach (var r in built.House.GetComponentsInChildren<Renderer>(true))
                        if (r.name.StartsWith("Partition_") || r.name.StartsWith("Wall_")) r.enabled = false;
                foreach (var l in built.House.GetComponentsInChildren<Light>(true)) l.enabled = false;

                // calibrated like the manufacturer's renders: a face square to the camera shows its albedo (ambient 0.6 + a soft
                // key from the upper left ≈ 1.0), so a render and a catalogue photo compare colour for colour
                studio = new GameObject("DoorPreviewStudio") { hideFlags = HideFlags.HideAndDontSave };
                float sideZ0 = (s.View == "back" || s.View == "angleBack" ? -1f : 1f) * (s.Swing < 0 ? -1f : 1f);
                // from the upper left of the camera (it looks along -Z·sideZ, its left is +X·sideZ), raking like the
                // catalogue's renders so mouldings and bevels read: 40° up, 35° aside; a face square to the camera still gets
                // ambient 0.6 + 0.64 · cos 40° · cos 35° = 1.0
                AddLight(studio, new Vector3(40f, sideZ0 > 0 ? 215f : 35f, 0f), 0.64f, Color.white, true);
                RenderSettings.ambientMode = AmbientMode.Flat;
                // 0.6 in linear light (a Color here is gamma-space: 0.6 would give only 0.32 linear and a render ~25 % darker
                // than the catalogue); the probe takes linear values
                float ambLin = 0.6f, ambGamma = Mathf.LinearToGammaSpace(ambLin);
                RenderSettings.ambientLight = new Color(ambGamma, ambGamma, ambGamma);
                var sh = new SphericalHarmonicsL2();
                sh.AddAmbientLight(new Color(ambLin, ambLin, ambLin));
                RenderSettings.ambientProbe = sh;
                sky = GreySky();
                RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
                RenderSettings.customReflectionTexture = sky;

                // frame: the opening in wall "w" (along +X at z = 0); the swing side is +Z
                var o = doc.Openings[0];
                float ow = o.Width, oh = o.Height;
                var center = Studio + new Vector3(0f, s.FrontCenterY ?? oh * 0.5f + 0.03f, 0f);
                var camGo = new GameObject("DoorPreviewCam") { hideFlags = HideFlags.HideAndDontSave };
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
                int ss = 2, W, H;
                float sideZ = s.View == "back" || s.View == "angleBack" ? -1f : 1f;
                if (s.Swing < 0) sideZ = -sideZ;
                if (front)
                {
                    // classic blocks (pilasters, cornice) stand wider and taller than plain casings
                    bool wide = DoorCatalog.Resolve(o)?.Block?.StartsWith("classic") == true;
                    float fw = ow + 2f * (wide ? 0.15f : 0.08f), fh = oh + (wide ? 0.2f : 0.1f);
                    if (s.FrontSize.HasValue) { fw = s.FrontSize.Value.x; fh = s.FrontSize.Value.y; }
                    float cy = s.FrontCenterY ?? fh * 0.5f;
                    W = Mathf.RoundToInt(fw * s.PxPerM); H = Mathf.RoundToInt(fh * s.PxPerM);
                    cam.orthographic = true;
                    cam.orthographicSize = fh * 0.5f;
                    camGo.transform.SetPositionAndRotation(Studio + new Vector3(0f, cy, sideZ * 4f), Quaternion.LookRotation(new Vector3(0f, 0f, -sideZ)));
                    cam.nearClipPlane = 0.5f; cam.farClipPlane = 10f;
                }
                else if (s.View.StartsWith("detail"))
                {
                    // close-ups: "detailTop" = head corner on the hinge side, "detailFloor" = casing foot and threshold,
                    // "detailFar" = the far side's extension and casing
                    W = 900; H = 900;
                    cam.orthographic = false;
                    cam.fieldOfView = 32f;
                    float hx = s.HingeStart ? -ow * 0.5f : ow * 0.5f;
                    Vector3 target, eye;
                    if (s.View == "detailFloor") { target = Studio + new Vector3(hx, 0.08f, 0f); eye = target + new Vector3(hx * 0.9f, 0.35f, sideZ * 0.75f); }
                    else if (s.View == "detailFar") { target = Studio + new Vector3(-hx, 1.2f, 0f); eye = target + new Vector3(hx * 1.1f, 0.15f, -sideZ * 0.9f); }
                    else { target = Studio + new Vector3(hx, oh - 0.03f, 0f); eye = target + new Vector3(hx * 0.9f, 0.25f, sideZ * 0.8f); }
                    camGo.transform.SetPositionAndRotation(eye, Quaternion.LookRotation(target - eye));
                    cam.nearClipPlane = 0.02f; cam.farClipPlane = 20f;
                }
                else
                {
                    W = 900; H = 1100;
                    cam.orthographic = false;
                    cam.fieldOfView = 40f;
                    // big subjects (window panoramas) are seen from further away
                    float far = s.FrontSize.HasValue ? Mathf.Max(1f, Mathf.Max(s.FrontSize.Value.x, s.FrontSize.Value.y) / 2.2f) : 1f;
                    var eye = center + new Vector3(-1.6f, 0.2f, sideZ * 2.6f) * far;
                    camGo.transform.SetPositionAndRotation(eye, Quaternion.LookRotation(center - eye));
                    cam.nearClipPlane = 0.05f; cam.farClipPlane = 60f;
                }
                rt = new RenderTexture(W * ss, H * ss, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
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
                var png = Downsample(read, ss);
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllBytes(path, png.EncodeToPNG());
                Object.DestroyImmediate(png);
                return $"[DoorPreview] {s.Model} {s.View} {W}×{H} → {path}";
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

        /// <summary>
        /// Renders a design file as it is — no catalogue entry needed (design authors check their work with it): any
        /// finish and glass id of the shipped catalogue. One call, so parallel callers do not disturb each other.
        /// </summary>
        public static string RenderDesign(string designPath, string finish, string glass, string outPath, string view = "front",
                                          float leafW = 0.8f, float leafH = 2.0f, bool open = false, string kind = null, int leaves = 0,
                                          string block = null)
        {
            if (!File.Exists(designPath)) return "[DoorPreview] no file " + designPath;
            DoorDesign d;
            try { d = DoorCatalog.ParseDesign(File.ReadAllText(designPath)); }
            catch (System.Exception e) { return "[DoorPreview] the design does not parse: " + e.Message; }
            if (d == null) return "[DoorPreview] empty design";
            if (string.IsNullOrEmpty(d.Id)) d.Id = Path.GetFileNameWithoutExtension(designPath);
            DoorCatalog.Reload();
            var file = DoorCatalog.File;
            var tmp = new SeriesDef { Id = "_preview", Name = "preview", Finishes = file.Finishes.ConvertAll(f => f.Id), Glass = file.Glass.ConvertAll(g => g.Id) };
            if (!string.IsNullOrEmpty(block)) tmp.Block = block;
            string model = "_preview-" + d.Id;
            tmp.Models.Add(new ModelDef { Id = model, Name = d.Name, Design = d.Id });
            file.Series.Insert(0, tmp);
            DoorCatalog.Use(file, new[] { d });
            try
            {
                return Render(new Shot
                {
                    Model = model, Finish = finish, Glass = glass, View = view, Leaf = new Vector2(leafW, leafH), Open = open,
                    HideWall = view == "front" || view == "back", Kind = kind, Leaves = leaves > 0 ? leaves : (int?)null,
                }, outPath);
            }
            finally { DoorCatalog.Reload(); }
        }

        /// <summary>
        /// Renders an entrance door from its two design files (outer face and inner panel) — no catalogue entry needed:
        /// outer finish, inner finish and the inner panel's glass by catalogue ids; <paramref name="blockW"/> 0.86 or 0.96
        /// (block height 2.05). View "front" = the street side, "back" = the inside.
        /// </summary>
        public static string RenderEntrance(string outerPath, string innerPath, string finish, string finishIn, string glass, string outPath,
                                            string view = "front", float blockW = 0.86f, bool open = false)
        {
            DoorDesign Parse(string path)
            {
                if (string.IsNullOrEmpty(path) || !File.Exists(path)) return null;
                var d = DoorCatalog.ParseDesign(File.ReadAllText(path));
                if (d != null && string.IsNullOrEmpty(d.Id)) d.Id = Path.GetFileNameWithoutExtension(path);
                return d;
            }
            DoorDesign outer, inner;
            try { outer = Parse(outerPath); inner = Parse(innerPath); }
            catch (System.Exception e) { return "[DoorPreview] a design does not parse: " + e.Message; }
            if (outer == null) return "[DoorPreview] no outer design " + outerPath;
            DoorCatalog.Reload();
            var file = DoorCatalog.File;
            var all = file.Finishes.ConvertAll(f => f.Id);
            var tmp = new SeriesDef { Id = "_preview", Name = "preview", Kind = "entrance", Finishes = all, FinishesIn = all, Glass = file.Glass.ConvertAll(g => g.Id) };
            string model = "_preview-" + outer.Id;
            tmp.Models.Add(new ModelDef { Id = model, Name = outer.Name, Design = outer.Id, Inner = inner?.Id });
            file.Series.Insert(0, tmp);
            DoorCatalog.Use(file, inner != null ? new[] { outer, inner } : new[] { outer });
            try
            {
                return Render(new Shot
                {
                    Model = model, Finish = finish, FinishIn = finishIn, Glass = glass, View = view, Leaf = new Vector2(blockW, DoorSizing.EntranceHeight),
                    Open = open, Wall = 0.25f, HideWall = view == "front" || view == "back",
                }, outPath);
            }
            finally { DoorCatalog.Reload(); }
        }

        /// <summary>
        /// The finish id of a photo's finish slug ("l-12" → "l-12-milanoreh", "whitey" → "veneer-whitey",
        /// "silver-ash-silver-rift" → "silver-ash"); the model's first finish when nothing matches.
        /// </summary>
        static string PhotoFinish(string slug, IList<string> finishes)
        {
            if (finishes == null || finishes.Count == 0) return DoorCatalog.Finish(slug) != null ? slug : null;
            if (!string.IsNullOrEmpty(slug))
            {
                foreach (var f in finishes) if (f == slug) return f;
                foreach (var f in finishes) if (f.StartsWith(slug + "-") || f.EndsWith("-" + slug)) return f;
                foreach (var f in finishes) if (slug.StartsWith(f + "-")) return f;
                // the photo names the colour in Russian ("shimo-svetlyy" = "П-34 Шимо Светлый")
                foreach (var f in finishes)
                {
                    var name = Slug(DoorCatalog.Finish(f)?.Name);
                    if (name.Length > 0 && (name == slug || name.EndsWith("-" + slug) || name.Contains(slug))) return f;
                }
            }
            return finishes[0];
        }

        /// <summary>Latin kebab-case of a name, transliterated like the photo index ("П-34 Шимо Светлый" → "p-34-shimo-svetlyy").</summary>
        static string Slug(string name)
        {
            if (string.IsNullOrEmpty(name)) return "";
            const string ru = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя";
            string[] la = { "a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "c", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya" };
            var sb = new System.Text.StringBuilder();
            foreach (char c0 in name.ToLowerInvariant())
            {
                int k = ru.IndexOf(c0);
                if (k >= 0) sb.Append(la[k]);
                else if ((c0 >= 'a' && c0 <= 'z') || (c0 >= '0' && c0 <= '9')) sb.Append(c0);
                else if (sb.Length > 0 && sb[sb.Length - 1] != '-') sb.Append('-');
            }
            return sb.ToString().Trim('-');
        }

        /// <summary>A partition 3 m long with the door in its middle, nothing else.</summary>
        static HouseDocument Document(Shot s)
        {
            var doc = new HouseDocument();
            doc.Meta.Name = "door-preview";
            doc.Site.Landscape = LandscapePreset.None;
            doc.Levels.Add(new LevelDef { Id = "ground", Elevation = 0f, Height = 2.8f, Slab = 0.2f });
            doc.Walls.Add(new WallDef { Id = "w", Level = "ground", Kind = WallKind.Interior, A = new Vector2(-2.5f, 0f), B = new Vector2(2.5f, 0f), Thickness = s.Wall });
            var o = new OpeningDef
            {
                Id = "d", Wall = "w", Type = OpeningType.Door, Model = s.Model, Finish = s.Finish, Glass = s.Glass, Leaf = s.Leaf,
                Hinge = s.HingeStart ? Hinge.Start : Hinge.End, Swing = s.Swing, Open = s.Open ? true : (bool?)null,
                Kind = s.Kind, Leaves = s.Leaves, FinishIn = s.FinishIn,
            };
            var size = DoorSizing.OpeningFor(o, s.Leaf);
            o.Width = size.x; o.Height = size.y; o.At = 2.5f - size.x * 0.5f;
            doc.Openings.Add(o);
            return doc;
        }

        /// <summary>
        /// Renders every model of a series in the finish (and glass) of its catalogue photo and writes [photo | render] pairs
        /// to <paramref name="outDir"/>/&lt;model&gt;.png — the check "one to one". Photos: tools/doors/.cache/photos.
        /// </summary>
        public static string CompareSeries(string seriesId, string outDir, string photosDir)
        {
            DoorCatalog.Reload();
            var series = DoorCatalog.File.Series.Find(x => x.Id == seriesId);
            if (series == null) return "[DoorPreview] no series " + seriesId;
            Directory.CreateDirectory(outDir);
            var log = new System.Text.StringBuilder();
            foreach (var m in series.Models)
            {
                string photo = m.Photo != null ? Path.Combine(photosDir, m.Photo) : null;
                // the photo's finish and glass: "p021_porta-22-mf__grey-veralinga.jpg"
                string finish = null, glass = null;
                if (m.Photo != null)
                {
                    var stem = Path.GetFileNameWithoutExtension(m.Photo);
                    int k = stem.IndexOf("__", System.StringComparison.Ordinal);
                    if (k > 0)
                    {
                        finish = stem.Substring(k + 2);
                        foreach (var g in DoorCatalog.GlassOf(series, m))
                            if (stem.Substring(0, k).EndsWith("-" + g) || stem.Substring(0, k).Contains("-" + g + "-")) glass = g;
                    }
                }
                finish = PhotoFinish(finish, DoorCatalog.FinishesOf(series, m));
                string render = Path.Combine(outDir, m.Id + "_render.png");
                // the series' own kind (a folding series shows its book of two 400 mm panels, a sliding one its coupe)
                var kind = DoorSizing.SeriesKind(series);
                var shot = new Shot { Model = m.Id, Finish = finish, Glass = glass };
                if (kind == DoorKind.Folding) { shot.Kind = "folding"; shot.Leaf = new Vector2(0.4f, 2.0f); }
                else if (kind == DoorKind.Sliding) shot.Kind = "sliding";
                if (series.IsEntrance)
                {
                    var sz = (m.Sizes ?? series.Sizes)?.Find(x => x != null && x.Length >= 2);
                    shot.Leaf = sz != null ? new Vector2(sz[0], sz[1]) : new Vector2(DoorSizing.EntranceWidths[0], DoorSizing.EntranceHeight);
                    shot.Wall = 0.25f;
                }
                log.AppendLine(Render(shot, render));
                if (photo != null && File.Exists(photo))
                {
                    // the photo scaled to the render's height, then side by side
                    var ph = Load(photo);
                    var rd = Load(render);
                    int h = rd.height, w = Mathf.RoundToInt(ph.width * (float)h / ph.height);
                    var scaled = Scale(ph, w, h);
                    File.WriteAllBytes(Path.Combine(outDir, m.Id + "_photo.png"), scaled.EncodeToPNG());
                    Object.DestroyImmediate(ph); Object.DestroyImmediate(rd); Object.DestroyImmediate(scaled);
                    log.AppendLine(Compare(Path.Combine(outDir, m.Id + "_photo.png"), render, Path.Combine(outDir, m.Id + ".png")));
                }
            }
            return log.ToString();
        }

        static Texture2D Scale(Texture2D src, int w, int h)
        {
            var rt = RenderTexture.GetTemporary(w, h, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            Graphics.Blit(src, rt);
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var dst = new Texture2D(w, h, TextureFormat.RGBA32, false);
            dst.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            dst.Apply(false);
            RenderTexture.active = prev;
            RenderTexture.ReleaseTemporary(rt);
            return dst;
        }

        /// <summary>Puts a render next to a catalogue photo at the same leaf height: [photo | render].</summary>
        public static string Compare(string photoPath, string renderPath, string outPath)
        {
            var photo = Load(photoPath);
            var render = Load(renderPath);
            if (photo == null || render == null) return "[DoorPreview] missing " + (photo == null ? photoPath : renderPath);
            int h = Mathf.Max(photo.height, render.height);
            var sheet = new Texture2D(photo.width + render.width + 12, h, TextureFormat.RGBA32, false);
            var white = new Color32[sheet.width * sheet.height];
            for (int i = 0; i < white.Length; i++) white[i] = new Color32(255, 255, 255, 255);
            sheet.SetPixels32(white);
            sheet.SetPixels(0, h - photo.height, photo.width, photo.height, photo.GetPixels());
            sheet.SetPixels(photo.width + 12, h - render.height, render.width, render.height, render.GetPixels());
            sheet.Apply(false);
            File.WriteAllBytes(outPath, sheet.EncodeToPNG());
            Object.DestroyImmediate(photo); Object.DestroyImmediate(render); Object.DestroyImmediate(sheet);
            return "[DoorPreview] " + outPath;
        }

        static Texture2D Load(string path)
        {
            if (!File.Exists(path)) return null;
            var t = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            return t.LoadImage(File.ReadAllBytes(path)) ? t : null;
        }

        static void AddLight(GameObject parent, Vector3 euler, float intensity, Color color, bool shadows)
        {
            var go = new GameObject("DoorPreviewLight") { hideFlags = HideFlags.HideAndDontSave };
            go.transform.SetParent(parent.transform, false);
            go.transform.rotation = Quaternion.Euler(euler);
            var l = go.AddComponent<Light>();
            l.type = LightType.Directional;
            l.intensity = intensity;
            l.color = color;
            l.shadows = shadows ? LightShadows.Soft : LightShadows.None;
            l.shadowStrength = 0.5f;
        }

        static Texture2D Downsample(Texture2D src, int k)
        {
            int w = src.width / k, h = src.height / k;
            var dst = new Texture2D(w, h, TextureFormat.RGBA32, false);
            var s = src.GetPixels32();
            var d = new Color32[w * h];
            for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                int r = 0, g = 0, b = 0, a = 0;
                for (int j = 0; j < k; j++)
                for (int i = 0; i < k; i++)
                {
                    var c = s[(y * k + j) * src.width + x * k + i];
                    r += c.r; g += c.g; b += c.b; a += c.a;
                }
                int n = k * k;
                d[y * w + x] = new Color32((byte)(r / n), (byte)(g / n), (byte)(b / n), (byte)(a / n));
            }
            dst.SetPixels32(d);
            dst.Apply(false);
            return dst;
        }

        /// <summary>A tiny cubemap: light above, mid grey at the horizon, darker below.</summary>
        static Cubemap GreySky()
        {
            const int n = 16;
            var cube = new Cubemap(n, TextureFormat.RGBA32, false) { hideFlags = HideFlags.HideAndDontSave };
            foreach (CubemapFace f in new[] { CubemapFace.PositiveX, CubemapFace.NegativeX, CubemapFace.PositiveY, CubemapFace.NegativeY, CubemapFace.PositiveZ, CubemapFace.NegativeZ })
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
                    float g = h > 0f ? Mathf.Lerp(0.6f, 0.95f, h) : Mathf.Lerp(0.6f, 0.3f, -h);
                    px[y * n + x] = new Color(g, g, g, 1f);
                }
                cube.SetPixels(px, f);
            }
            cube.Apply();
            return cube;
        }
    }
}
