using System.Linq;
using System.Collections.Generic;
using System.IO;
using House4696.Core;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.Rendering.Universal.ShaderGUI;
using UnityEngine;

namespace House4696.Setup
{
    /// <summary>
    /// Turns Assets/House4696/External (prepared by tools/assets: Poly Haven scans and Blender models) into what the
    /// player uses: texture import settings, URP/Lit materials, one prefab per model with its materials by slot, and
    /// the <see cref="ExternalCatalog"/> referenced from HouseContent. Re-running updates everything in place.
    /// </summary>
    public static class ExternalCatalogImporter
    {
        const string Source = AssetPaths.Root + "/External";
        const string Out = AssetPaths.Generated + "/External";
        const string CatalogPath = Out + "/ExternalCatalog.asset";
        /// <summary>Materials and prefabs: under Resources, loaded by path on first use (see <see cref="ExternalCatalog"/>).</summary>
        const string Lib = Out + "/Resources/ExternalLibrary";
        /// <summary>Blender models face -Y; after the FBX axis conversion that is Unity +Z, the catalogue wants -Z.</summary>
        const float FrontYaw = 180f;

        [MenuItem("House 46-96/External/Import Catalog", priority = 70)]
        public static void ImportMenu() => Debug.Log(Import());

        public static string Import()
        {
            string manifestPath = Source + "/external.json";
            if (!File.Exists(manifestPath)) return "[External] no " + manifestPath + " — run tools/assets first";
            var manifest = JObject.Parse(File.ReadAllText(manifestPath));
            AssetPaths.Ensure(Lib + "/Materials");
            AssetPaths.Ensure(Lib + "/Prefabs");
            AssetDatabase.Refresh();

            var catalog = AssetDatabase.LoadAssetAtPath<ExternalCatalog>(CatalogPath);
            if (catalog == null)
            {
                catalog = ScriptableObject.CreateInstance<ExternalCatalog>();
                AssetDatabase.CreateAsset(catalog, CatalogPath);
            }
            catalog.Materials.Clear();
            catalog.Models.Clear();
            ConfigureAllTextures(manifest);

            foreach (JObject m in manifest["materials"])
            {
                string folder = Source + "/" + (string)m["folder"];
                var tex = (JObject)m["textures"];
                var tile = (JArray)m["metersPerTile"];
                // 1K everywhere: at walk-through distances 2K floors were indistinguishable and cost ~80 MB; door
                // finishes ask for 2K along the grain (a 2 m stile is one tile)
                // door glass with a picture or pattern: transparent where the texture's alpha says so
                bool see = (bool?)m["transparent"] ?? false;
                // art glass keeps the faint glow of the palette's satin glass (M_DoorGlassSatin), so a picture's frosted
                // areas read like the plain Magic Fog next to them
                bool glass = see && (string)m["category"] == "doorglass";
                var mat = LitMaterial((string)m["id"], folder, tex, (int?)m["maxSize"] ?? 1024,
                    new Vector2(1f / (float)tile[0], 1f / (float)tile[1]), cutout: false, transparent: see,
                    emission: glass ? new Color(0.11f, 0.104f, 0.094f) : Color.black,
                    factors: m["factors"] as JObject, opacity: see ? 1f : 0.25f, maskMax: MaskMax(m));
                catalog.Materials.Add(new ExternalCatalog.MaterialEntry
                {
                    Id = (string)m["id"], Name = (string)m["name"], Category = (string)m["category"], Material = mat, MaterialPath = ResourcePath(mat), Neutral = (bool?)m["neutral"] ?? false,
                });
            }

            foreach (JObject m in manifest["models"])
                catalog.Models.Add(ImportModel(m, catalog));

            // materials of renamed slots / removed entries
            foreach (var guid in AssetDatabase.FindAssets("t:Material", new[] { Lib + "/Materials" }))
            {
                string p = AssetDatabase.GUIDToAssetPath(guid);
                if (!_written.Contains(p)) AssetDatabase.DeleteAsset(p);
            }
            _written.Clear();

            EditorUtility.SetDirty(catalog);
            var content = AssetDatabase.LoadAssetAtPath<HouseContent>(AssetPaths.Root + "/Resources/" + HouseContent.ResourceName + ".asset");
            if (content != null)
            {
                content.External = catalog;
                EditorUtility.SetDirty(content);
            }
            AssetDatabase.SaveAssets();
            ExternalCatalog.Reset();
            return $"[External] {catalog.Materials.Count} materials, {catalog.Models.Count} models → {CatalogPath}";
        }

        static ExternalCatalog.ModelEntry ImportModel(JObject m, ExternalCatalog catalog)
        {
            string id = (string)m["id"];
            string folder = Source + "/" + (string)m["folder"];
            string fbxPath = folder + "/" + (string)m["fbx"];
            var importer = (ModelImporter)AssetImporter.GetAtPath(fbxPath);
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
            importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.isReadable = true;            // the runtime GI bake reads emissive meshes
            importer.meshCompression = ModelImporterMeshCompression.Medium;   // ~75 models: keeps the app small
            importer.optimizeMeshPolygons = importer.optimizeMeshVertices = true;
            importer.addCollider = false;
            importer.importCameras = importer.importLights = false;
            importer.SaveAndReimport();
            var fbx = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);

            var entry = new ExternalCatalog.ModelEntry
            {
                Id = id, Name = (string)m["name"], Category = (string)m["category"], Source = (string)m["source"],
                Hanging = (bool?)m["hanging"] ?? false, Triangles = (int?)m["triangles"] ?? 0,
            };
            var size = (JArray)m["size"];
            entry.Size = new Vector3((float)size[0], (float)size[2], (float)size[1]);   // Blender x, y (depth), z (height)

            // own materials per slot, keyed by the slot (= material) name the FBX carries
            var own = new Dictionary<string, ExternalCatalog.Slot>();
            foreach (JObject s in m["slots"])
            {
                string slot = (string)s["slot"];
                var tex = (JObject)s["textures"] ?? new JObject();
                Material mat = null;
                if (tex.Count > 0 || s["baseColor"] != null)
                {
                    bool textured = tex["albedo"] != null;
                    // glass is see-through; a textured part is at most cut out by its alpha (the glTF often marks whole
                    // lamps as BLEND because of their glass)
                    bool transparent = slot.Contains("glass") || (!textured && (bool?)s["transparent"] == true);
                    bool cutout = !transparent && (bool?)s["cutout"] == true;
                    // Poly Haven drives glow with an emission texture we do not import: the factor alone would light the
                    // whole body, so it only lights untextured parts (bulbs, flames, opal globes). Our Blender models' own
                    // textured slots (screens, backlit pictures) glow with their albedo as the emission map.
                    bool ownModel = ((string)m["source"] ?? "").StartsWith("blender:");
                    var em = (!textured || ownModel) && s["emissive"] is JArray e ? new Color((float)e[0], (float)e[1], (float)e[2]) * 1.5f : Color.black;
                    mat = LitMaterial($"{id}_{slot}", folder, tex, 1024, Vector2.one, cutout, transparent, em, s);
                }
                own[slot] = new ExternalCatalog.Slot
                {
                    Name = slot, Own = mat, OwnPath = ResourcePath(mat), Default = (string)s["default"], UvMeters = (bool?)s["uvMeters"] ?? false,
                };
            }

            // prefab: pivot object → model turned to face -Z, materials in sub-mesh order
            var root = new GameObject(id);
            var model = (GameObject)PrefabUtility.InstantiatePrefab(fbx);
            PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            model.transform.SetParent(root.transform, false);
            model.transform.localRotation = Quaternion.Euler(0f, FrontYaw, 0f) * model.transform.localRotation;
            var renderer = model.GetComponentInChildren<MeshRenderer>();
            var imported = renderer.sharedMaterials;
            var mats = new Material[imported.Length];
            for (int i = 0; i < imported.Length; i++)
            {
                string slotName = imported[i] != null ? imported[i].name : "slot" + i;
                if (!own.TryGetValue(slotName, out var slot))
                    slot = own[slotName] = new ExternalCatalog.Slot { Name = slotName };
                entry.Slots.Add(slot);
                mats[i] = slot.Own != null ? slot.Own : DefaultMaterial(catalog, slot.Default) ?? Fallback();
            }
            renderer.sharedMaterials = mats;
            string prefabPath = $"{Lib}/Prefabs/{id}.prefab";
            entry.Prefab = PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            entry.PrefabPath = ResourcePath(entry.Prefab);
            Object.DestroyImmediate(root);
            return entry;
        }

        /// <summary>Resources.Load path of an asset under <see cref="Lib"/> (no extension), or null.</summary>
        static string ResourcePath(Object asset)
        {
            if (asset == null) return null;
            string p = AssetDatabase.GetAssetPath(asset);
            const string marker = "/Resources/";
            int i = p.IndexOf(marker, System.StringComparison.Ordinal);
            if (i < 0) throw new System.InvalidOperationException($"[External] {p} is not under a Resources folder");
            p = p.Substring(i + marker.Length);
            return p.Substring(0, p.Length - Path.GetExtension(p).Length);
        }

        /// <summary>
        /// Largest mask (metallic / smoothness) texture of a library material: 512 is plenty for tiling surfaces; pictures
        /// (art glass, painted ornaments) keep their masks as sharp as their albedo — a print's metal edges must not blur.
        /// </summary>
        static int MaskMax(JObject m)
        {
            string cat = (string)m["category"];
            return (int?)m["maskSize"] ?? (cat == "doorglass" || cat == "doorart" ? (int?)m["maxSize"] ?? 1024 : 512);
        }

        static Material LitMaterial(string name, string folder, JObject tex, int maxSize, Vector2 tiling, bool cutout, bool transparent,
            Color emission, JObject factors = null, float opacity = 0.25f, int maskMax = 512)
        {
            string path = $"{Lib}/Materials/M_{name}.mat";
            _written.Add(path);
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(shader);
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = shader;
            m.shaderKeywords = new string[0];
            // an albedo with alpha drives cutouts and (door glass) transparency
            var albedo = Texture(folder, (string)tex["albedo"], TextureKind.Albedo, maxSize, cutout || transparent && opacity >= 0.99f);
            var normal = Texture(folder, (string)tex["normal"], TextureKind.Normal, maxSize, false);
            var mask = Texture(folder, (string)tex["mask"], TextureKind.Mask, maxSize, false, maskMax);

            var color = Color.white;
            if (albedo == null && factors?["baseColor"] is JArray bc) color = new Color((float)bc[0], (float)bc[1], (float)bc[2], 1f).gamma;
            if (transparent) color.a = opacity;
            m.SetFloat("_WorkflowMode", 1f);
            m.SetColor("_BaseColor", color);
            m.SetTexture("_BaseMap", albedo);
            m.SetTextureScale("_BaseMap", tiling);
            m.SetTexture("_BumpMap", normal);
            m.SetFloat("_BumpScale", 1f);
            m.SetTexture("_MetallicGlossMap", mask);
            m.SetTexture("_OcclusionMap", mask);
            m.SetFloat("_OcclusionStrength", 1f);
            m.SetFloat("_SmoothnessTextureChannel", 0f);   // smoothness in the mask's alpha
            if (mask != null)
            {
                m.SetFloat("_Smoothness", 1f);
                m.SetFloat("_Metallic", 1f);
            }
            else
            {
                float rough = factors?["roughness"] != null ? (float)factors["roughness"] : 0.6f;
                m.SetFloat("_Smoothness", transparent ? 0.95f : 1f - rough);
                m.SetFloat("_Metallic", transparent ? 0f : factors?["metallic"] != null ? Mathf.Clamp01((float)factors["metallic"]) : 0f);
            }
            m.SetFloat("_AlphaClip", cutout ? 1f : 0f);
            m.SetFloat("_Cutoff", 0.5f);
            m.SetFloat("_Cull", cutout ? 0f : 2f);
            m.SetFloat("_Surface", transparent ? 1f : 0f);
            m.SetFloat("_Blend", 0f);
            m.SetFloat("_BlendModePreserveSpecular", 1f);
            m.SetFloat("_ReceiveShadows", 1f);
            m.SetFloat("_EnvironmentReflections", 1f);
            m.SetFloat("_SpecularHighlights", 1f);
            if (emission.maxColorComponent > 0f)
            {
                m.SetColor("_EmissionColor", emission);
                m.SetTexture("_EmissionMap", albedo);   // null for untextured parts: plain colour glow
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
                m.EnableKeyword("_EMISSION");
            }
            else
            {
                m.SetTexture("_EmissionMap", null);
                m.SetColor("_EmissionColor", Color.black);
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            }
            BaseShaderGUI.SetMaterialKeywords(m, LitGUI.SetMaterialKeywords);
            if (cutout) m.renderQueue = (int)UnityEngine.Rendering.RenderQueue.AlphaTest;
            if (transparent) m.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Transparent;
            EditorUtility.SetDirty(m);
            return m;
        }

        static readonly HashSet<string> _written = new HashSet<string>();

        internal enum TextureKind { Albedo, Normal, Mask }

        static Texture2D Texture(string folder, string file, TextureKind kind, int maxSize, bool alpha, int maskMax = 512)
        {
            if (string.IsNullOrEmpty(file)) return null;
            string path = folder + "/" + file;
            var ti = (TextureImporter)AssetImporter.GetAtPath(path);
            if (ti == null) { Debug.LogWarning("[External] missing texture " + path); return null; }
            if (Configure(ti, kind, maxSize, alpha, maskMax)) ti.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        /// <summary>Import settings of a library texture; true when something changed (a reimport is needed).</summary>
        internal static bool Configure(TextureImporter ti, TextureKind kind, int maxSize, bool alpha, int maskMax = 512)
        {
            var type = kind == TextureKind.Normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            bool srgb = kind == TextureKind.Albedo;
            var alphaSource = kind == TextureKind.Mask || alpha ? TextureImporterAlphaSource.FromInput : TextureImporterAlphaSource.None;
            int aniso = kind == TextureKind.Albedo ? 4 : 2;
            int size = kind == TextureKind.Mask ? Mathf.Min(maxSize, maskMax) : maxSize;
            int quality = kind == TextureKind.Normal ? 80 : 65;
            if (ti.textureType == type && ti.sRGBTexture == srgb && ti.alphaSource == alphaSource && ti.alphaIsTransparency == alpha &&
                ti.mipmapEnabled && ti.wrapMode == TextureWrapMode.Repeat && ti.anisoLevel == aniso && ti.maxTextureSize == size &&
                ti.textureCompression == TextureImporterCompression.Compressed && ti.crunchedCompression && ti.compressionQuality == quality)
                return false;
            ti.textureType = type;
            ti.sRGBTexture = srgb;
            ti.alphaSource = alphaSource;
            ti.alphaIsTransparency = alpha;
            ti.mipmapEnabled = true;
            ti.wrapMode = TextureWrapMode.Repeat;
            ti.anisoLevel = aniso;
            ti.maxTextureSize = size;
            // crunched DXT: 4–6× smaller in the build (the library has ~180 materials) at a barely visible cost
            ti.textureCompression = TextureImporterCompression.Compressed;
            ti.crunchedCompression = true;
            ti.compressionQuality = quality;
            return true;
        }

        /// <summary>
        /// Sets the import settings of every texture of the manifest in one batch, so the ~500 textures are
        /// reimported once (in parallel import workers) instead of one by one.
        /// </summary>
        static void ConfigureAllTextures(JObject manifest)
        {
            var files = new List<(string path, int max, int maskMax)>();
            foreach (JObject m in manifest["materials"])
                foreach (var t in (JObject)m["textures"])
                    files.Add((Source + "/" + (string)m["folder"] + "/" + (string)t.Value, (int?)m["maxSize"] ?? 1024, MaskMax(m)));
            foreach (JObject m in manifest["models"])
                foreach (JObject s in m["slots"])
                    if (s["textures"] is JObject tex)
                        foreach (var t in tex) files.Add((Source + "/" + (string)m["folder"] + "/" + (string)t.Value, 1024, 512));
            int changed = 0;
            AssetDatabase.StartAssetEditing();
            try
            {
                foreach (var (path, max, maskMax) in files)
                {
                    if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) continue;
                    var kind = path.Contains("_normal.") ? TextureKind.Normal : path.Contains("_mask.") ? TextureKind.Mask : TextureKind.Albedo;
                    if (Configure(ti, kind, max, kind == TextureKind.Albedo && path.EndsWith(".png"), maskMax)) { ti.SaveAndReimport(); changed++; }
                }
            }
            finally { AssetDatabase.StopAssetEditing(); }
            Debug.Log($"[External] texture settings: {changed} of {files.Count} reimported");
        }

        /// <summary>Library (or palette) material named by a slot default such as "linen_rough#c8c0b3" — untinted; the tint is applied at runtime.</summary>
        static Material DefaultMaterial(ExternalCatalog catalog, string spec)
        {
            if (string.IsNullOrEmpty(spec)) return null;
            string id = spec.Split('#')[0];
            var lib = catalog.Materials.Find(e => e.Id == id);
            if (lib != null) return lib.Material;
            string palette = "M_" + string.Concat(id.Split('_').Select(w => w.Length > 0 ? char.ToUpperInvariant(w[0]) + w.Substring(1) : w));
            return AssetDatabase.LoadAssetAtPath<Material>(AssetPaths.Materials + "/" + palette + ".mat")
                ?? AssetDatabase.LoadAssetAtPath<Material>(AssetPaths.Materials + "/M_Int" + palette.Substring(2) + ".mat");
        }

        static Material _fallback;
        static Material Fallback() => _fallback != null ? _fallback : _fallback = AssetDatabase.LoadAssetAtPath<Material>(AssetPaths.Materials + "/M_InteriorWall.mat");
    }
}
