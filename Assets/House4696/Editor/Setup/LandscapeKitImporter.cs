using System.Collections.Generic;
using System.IO;
using System.Linq;
using House4696.Core;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.Rendering.Universal.ShaderGUI;
using UnityEngine;
using UnityEngine.Rendering;
using TextureKind = House4696.Setup.ExternalCatalogImporter.TextureKind;

namespace House4696.Setup
{
    /// <summary>
    /// Turns Assets/House4696/External/Landscape (tools/landscape/export_kit.py) into the <see cref="LandscapeKit"/>:
    /// URP/Lit materials (foliage cut out, two-sided, instanced), one prefab per variant with a LODGroup built from its
    /// _LOD0/_LOD1 meshes, single-renderer prefabs for terrain details, and TerrainLayers for the ground.
    /// Re-running updates everything in place.
    /// </summary>
    public static class LandscapeKitImporter
    {
        const string Source = AssetPaths.Root + "/External/Landscape";
        const string Out = AssetPaths.Generated + "/Landscape";
        const string KitPath = Out + "/LandscapeKit.asset";

        /// <summary>
        /// LODGroup screen heights (fraction of the screen height where each LOD ends) by kind and LOD count. Plants:
        /// full mesh up close, LOD1 in the middle distance, from ~20 m the impostor cards (4 triangles) out to ~200 m,
        /// so distant beds stay planted.
        /// </summary>
        static float[] LodHeights(LandscapeKit.Kind kind, int lods)
        {
            switch (kind)
            {
                case LandscapeKit.Kind.Rock: return lods > 1 ? new[] { 0.10f, 0.006f } : new[] { 0.006f };
                case LandscapeKit.Kind.Stone: return new[] { 0.004f };
                // plants (real screen fractions, PlantField ignores the lodBias): the full mesh while the plant is taller
                // than 12 % of the screen (~4–5 m for a 0.7 m clump), LOD1 down to 4 % (~13 m), impostor cards to 0.3 %
                // (~170 m). Measured in the app: the plants were vertex-bound (render scale did not change their cost),
                // and side-by-side renders showed no difference against 8 % / 2.2 %
                default: return lods > 2 ? new[] { 0.12f, 0.04f, 0.003f } : lods > 1 ? new[] { 0.12f, 0.013f } : new[] { 0.013f };
            }
        }

        [MenuItem("House 46-96/External/Import Landscape Kit", priority = 71)]
        public static void ImportMenu() => Debug.Log(Import());

        public static string Import()
        {
            string manifestPath = Source + "/landscape.json";
            if (!File.Exists(manifestPath)) return "[Landscape] no " + manifestPath + " — run tools/landscape/export_kit.py first";
            var manifest = JObject.Parse(File.ReadAllText(manifestPath));
            AssetPaths.Ensure(Out + "/Materials");
            AssetPaths.Ensure(Out + "/Prefabs");
            AssetPaths.Ensure(Out + "/TerrainLayers");
            AssetDatabase.Refresh();
            ConfigureTextures(manifest);
            ConfigureModels(manifest);

            var kit = AssetDatabase.LoadAssetAtPath<LandscapeKit>(KitPath);
            if (kit == null)
            {
                kit = ScriptableObject.CreateInstance<LandscapeKit>();
                AssetDatabase.CreateAsset(kit, KitPath);
            }
            kit.Groups.Clear();
            kit.Layers.Clear();

            var materials = new Dictionary<string, Material>();
            foreach (JObject m in manifest["materials"])
                materials[(string)m["name"]] = LitMaterial(m);

            int variants = 0;
            foreach (JObject g in manifest["groups"])
            {
                var kind = ParseKind((string)g["kind"]);
                var group = new LandscapeKit.Group { Id = (string)g["id"], Kind = kind };
                foreach (JObject v in g["variants"])
                {
                    group.Variants.Add(ImportVariant(v, kind, materials));
                    variants++;
                }
                kit.Groups.Add(group);
            }

            foreach (JObject l in manifest["terrainLayers"])
                kit.Layers.Add(new LandscapeKit.Layer { Id = (string)l["id"], TerrainLayer = TerrainLayerAsset(l) });
            kit.TerrainMaterial = TerrainMaterial();
            // stream water: transparent URP/Lit, near-mirror smooth with a scrolling ripple normal (WaterFlow)
            kit.WaterMaterial = WaterMaterial("M_StreamWater", null, new Color(0.07f, 0.11f, 0.09f, 0.72f), 0.88f, 0.8f, new Vector2(3f, 3f), 0.42f);
            kit.FallsMaterial = WaterMaterial("M_StreamFalls", null, new Color(0.86f, 0.9f, 0.9f, 0.78f), 0.6f, 1.0f, new Vector2(2f, 0.5f), 0.7f);

            EditorUtility.SetDirty(kit);
            var content = AssetDatabase.LoadAssetAtPath<HouseContent>(AssetPaths.Root + "/Resources/" + HouseContent.ResourceName + ".asset");
            if (content != null)
            {
                content.Landscape = kit;
                EditorUtility.SetDirty(content);
            }
            AssetDatabase.SaveAssets();
            LandscapeKit.Reset();
            return $"[Landscape] {kit.Groups.Count} groups, {variants} variants, {materials.Count} materials, {kit.Layers.Count} terrain layers → {KitPath}";
        }

        static LandscapeKit.Kind ParseKind(string kind)
        {
            switch (kind)
            {
                case "rock": return LandscapeKit.Kind.Rock;
                case "stone": return LandscapeKit.Kind.Stone;
                case "detail": return LandscapeKit.Kind.Detail;
                default: return LandscapeKit.Kind.Plant;
            }
        }

        // ------------------------------------------------------------------ import settings

        static void ConfigureTextures(JObject manifest)
        {
            var jobs = new List<(string path, TextureKind kind, int size, bool alpha)>();
            foreach (JObject m in manifest["materials"])
            {
                if ((bool?)m["point"] == true || (bool?)m["impostor"] == true) continue;   // palette / atlas: set up separately
                foreach (var t in (JObject)m["textures"])
                {
                    string path = Source + "/" + (string)m["folder"] + "/" + (string)t.Value;
                    var kind = Kind(path);
                    jobs.Add((path, kind, 1024, kind == TextureKind.Albedo && path.EndsWith(".png")));
                }
            }
            foreach (JObject l in manifest["terrainLayers"])
                foreach (var t in (JObject)l["textures"])
                {
                    string path = Source + "/" + (string)l["folder"] + "/" + (string)t.Value;
                    jobs.Add((path, Kind(path), 2048, false));
                }
            int changed = 0;
            AssetDatabase.StartAssetEditing();
            try
            {
                foreach (var (path, kind, size, alpha) in jobs)
                    if (AssetImporter.GetAtPath(path) is TextureImporter ti && ExternalCatalogImporter.Configure(ti, kind, size, alpha))
                    {
                        ti.SaveAndReimport();
                        changed++;
                    }
                foreach (JObject m in manifest["materials"])
                    if ((bool?)m["impostor"] == true)
                        foreach (var t in (JObject)m["textures"])
                            if (AssetImporter.GetAtPath(Source + "/" + (string)m["folder"] + "/" + (string)t.Value) is TextureImporter ti && ConfigureImpostor(ti))
                            {
                                ti.SaveAndReimport();
                                changed++;
                            }
                foreach (JObject m in manifest["materials"])
                    if ((bool?)m["point"] == true)
                        foreach (var t in (JObject)m["textures"])
                            if (AssetImporter.GetAtPath(Source + "/" + (string)m["folder"] + "/" + (string)t.Value) is TextureImporter ti && ConfigurePalette(ti))
                            {
                                ti.SaveAndReimport();
                                changed++;
                            }
            }
            finally { AssetDatabase.StopAssetEditing(); }
            Debug.Log($"[Landscape] texture settings: {changed} of {jobs.Count} reimported");
        }

        static TextureKind Kind(string path) =>
            path.Contains("_normal.") ? TextureKind.Normal : path.Contains("_mask.") ? TextureKind.Mask : TextureKind.Albedo;

        /// <summary>
        /// The impostor atlas: mipmaps that keep the alpha-tested coverage (plain mips thin the cards out into nothing
        /// at a distance), no crunch (its blocks smear the cut-out edges).
        /// </summary>
        static bool ConfigureImpostor(TextureImporter ti)
        {
            if (ti.mipmapEnabled && ti.mipMapsPreserveCoverage && Mathf.Approximately(ti.alphaTestReferenceValue, 0.4f) && !ti.crunchedCompression &&
                ti.maxTextureSize == 2048 && ti.sRGBTexture && ti.alphaSource == TextureImporterAlphaSource.FromInput && ti.wrapMode == TextureWrapMode.Clamp)
                return false;
            ti.textureType = TextureImporterType.Default;
            ti.sRGBTexture = true;
            ti.alphaSource = TextureImporterAlphaSource.FromInput;
            ti.alphaIsTransparency = true;
            ti.mipmapEnabled = true;
            ti.mipMapsPreserveCoverage = true;
            ti.alphaTestReferenceValue = 0.4f;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.maxTextureSize = 2048;
            ti.anisoLevel = 2;
            ti.textureCompression = TextureImporterCompression.Compressed;
            ti.crunchedCompression = false;
            return true;
        }

        /// <summary>Palette textures: every texel is one colour, so no filtering, mipmaps or compression.</summary>
        static bool ConfigurePalette(TextureImporter ti)
        {
            bool srgb = !ti.assetPath.Contains("_mask.");
            if (ti.filterMode == FilterMode.Point && !ti.mipmapEnabled && ti.textureCompression == TextureImporterCompression.Uncompressed &&
                ti.sRGBTexture == srgb && ti.wrapMode == TextureWrapMode.Clamp)
                return false;
            ti.textureType = TextureImporterType.Default;
            ti.sRGBTexture = srgb;
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            ti.alphaSource = TextureImporterAlphaSource.FromInput;
            return true;
        }

        static void ConfigureModels(JObject manifest)
        {
            AssetDatabase.StartAssetEditing();
            try
            {
                foreach (JObject g in manifest["groups"])
                    foreach (JObject v in g["variants"])
                    {
                        var importer = (ModelImporter)AssetImporter.GetAtPath(Source + "/" + (string)v["fbx"]);
                        if (importer == null) continue;
                        importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                        importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
                        importer.importAnimation = false;
                        importer.animationType = ModelImporterAnimationType.None;
                        importer.isReadable = true;          // the runtime GI bake reads meshes; the terrain reads detail meshes
                        importer.meshCompression = ModelImporterMeshCompression.Medium;
                        importer.optimizeMeshPolygons = importer.optimizeMeshVertices = true;
                        importer.addCollider = false;
                        importer.importCameras = importer.importLights = false;
                        importer.importBlendShapes = false;
                        importer.SaveAndReimport();
                    }
            }
            finally { AssetDatabase.StopAssetEditing(); }
        }

        // ------------------------------------------------------------------ materials

        static Material LitMaterial(JObject m)
        {
            string name = (string)m["name"];
            string folder = Source + "/" + (string)m["folder"];
            var tex = (JObject)m["textures"];
            bool cutout = (bool?)m["cutout"] == true;
            bool twoSided = (bool?)m["twoSided"] == true;
            string path = $"{Out}/Materials/M_{name}.mat";
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.shader = shader;
            mat.shaderKeywords = new string[0];
            Texture2D Load(string key) => tex[key] != null ? AssetDatabase.LoadAssetAtPath<Texture2D>(folder + "/" + (string)tex[key]) : null;
            var mask = Load("mask");
            mat.SetFloat("_WorkflowMode", 1f);
            mat.SetColor("_BaseColor", Color.white);
            mat.SetTexture("_BaseMap", Load("albedo"));
            mat.SetTexture("_BumpMap", Load("normal"));
            mat.SetFloat("_BumpScale", 1f);
            mat.SetTexture("_MetallicGlossMap", mask);
            mat.SetTexture("_OcclusionMap", mask);
            mat.SetFloat("_OcclusionStrength", 1f);
            mat.SetFloat("_SmoothnessTextureChannel", 0f);
            mat.SetFloat("_Smoothness", mask != null ? 1f : (float?)m["smoothness"] ?? 0.3f);
            mat.SetFloat("_Metallic", mask != null ? 1f : 0f);
            mat.SetFloat("_AlphaClip", cutout ? 1f : 0f);
            mat.SetFloat("_Cutoff", 0.4f);
            mat.SetFloat("_Cull", twoSided ? 0f : 2f);
            mat.SetFloat("_Surface", 0f);
            mat.SetFloat("_ReceiveShadows", 1f);
            mat.SetFloat("_EnvironmentReflections", 1f);
            mat.SetFloat("_SpecularHighlights", 1f);
            mat.SetColor("_EmissionColor", Color.black);
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            BaseShaderGUI.SetMaterialKeywords(mat, LitGUI.SetMaterialKeywords);
            mat.renderQueue = cutout ? (int)RenderQueue.AlphaTest : (int)RenderQueue.Geometry;
            mat.enableInstancing = true;           // terrain details draw instanced
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ------------------------------------------------------------------ prefabs

        static LandscapeKit.Variant ImportVariant(JObject v, LandscapeKit.Kind kind, Dictionary<string, Material> materials)
        {
            string id = (string)v["id"];
            string fbxPath = Source + "/" + (string)v["fbx"];
            var meshes = AssetDatabase.LoadAllAssetsAtPath(fbxPath).OfType<Mesh>().ToDictionary(m => m.name);
            // material names per mesh: the imported FBX renderers carry them in sub-mesh order
            var fbx = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);
            var slotNames = new Dictionary<string, string[]>();
            foreach (var r in fbx.GetComponentsInChildren<MeshRenderer>(true))
            {
                var mf = r.GetComponent<MeshFilter>();
                if (mf != null && mf.sharedMesh != null)
                    slotNames[mf.sharedMesh.name] = r.sharedMaterials.Select(x => x != null ? x.name : "").ToArray();
            }

            Material[] Mats(Mesh mesh)
            {
                var names = slotNames.TryGetValue(mesh.name, out var n) ? n : new string[mesh.subMeshCount];
                return names.Select(x => materials.TryGetValue(x ?? "", out var mat) ? mat : materials.Values.First()).ToArray();
            }

            var levels = new List<Mesh>();
            for (int i = 0; i < 3 && meshes.TryGetValue(id + "_LOD" + i, out var mesh); i++) levels.Add(mesh);
            if (levels.Count == 0) levels.Add(meshes.Values.First());
            var lod0 = levels[0];

            var root = new GameObject(id);
            bool shadows = kind == LandscapeKit.Kind.Rock || kind == LandscapeKit.Kind.Plant;
            if (kind == LandscapeKit.Kind.Detail)
            {
                // terrain details want one renderer on the prefab root
                root.AddComponent<MeshFilter>().sharedMesh = lod0;
                var r = root.AddComponent<MeshRenderer>();
                r.sharedMaterials = Mats(lod0);
                r.shadowCastingMode = ShadowCastingMode.Off;
            }
            else
            {
                var lods = new List<LOD>();
                var heights = LodHeights(kind, levels.Count);
                for (int i = 0; i < heights.Length && i < levels.Count; i++)
                {
                    var child = new GameObject(i == 0 ? id : id + "_LOD" + i);
                    child.transform.SetParent(root.transform, false);
                    child.AddComponent<MeshFilter>().sharedMesh = levels[i];
                    var r = child.AddComponent<MeshRenderer>();
                    r.sharedMaterials = Mats(levels[i]);
                    // impostor cards cast no shadows (a flat card casts a flat shadow)
                    r.shadowCastingMode = shadows && i < 2 ? ShadowCastingMode.On : ShadowCastingMode.Off;
                    lods.Add(new LOD(heights[i], new Renderer[] { r }));
                }
                var group = root.AddComponent<LODGroup>();
                group.SetLODs(lods.ToArray());
                group.RecalculateBounds();
            }

            string prefabPath = $"{Out}/Prefabs/{id}.prefab";
            var prefab = PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            Object.DestroyImmediate(root);
            var size = (JArray)v["size"];
            var tris = (JArray)v["tris"];
            return new LandscapeKit.Variant
            {
                Id = id, Source = (string)v["source"], Prefab = prefab,
                Size = new Vector3((float)size[0], (float)size[2], (float)size[1]),
                TrianglesLod0 = (int)tris[0], TrianglesLod1 = tris.Count > 1 ? (int)tris[1] : 0,
            };
        }

        // ------------------------------------------------------------------ terrain layers

        /// <param name="reflection">Scales the sky/probe reflection (as occlusion): at grazing angles a smooth surface
        /// reflects nearly all of a bright sky, which turned the whole stream white.</param>
        static Material WaterMaterial(string name, string albedo, Color color, float smoothness, float bump, Vector2 tiling, float reflection)
        {
            string folder = Source + "/Water";
            var normalTi = (TextureImporter)AssetImporter.GetAtPath(folder + "/ripples_normal.png");
            if (normalTi != null && normalTi.textureType != TextureImporterType.NormalMap)
            {
                normalTi.textureType = TextureImporterType.NormalMap;
                normalTi.SaveAndReimport();
            }
            string path = $"{Out}/Materials/{name}.mat";
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.shader = shader;
            mat.shaderKeywords = new string[0];
            mat.SetFloat("_WorkflowMode", 1f);
            mat.SetColor("_BaseColor", color);
            mat.SetTexture("_BaseMap", albedo != null ? AssetDatabase.LoadAssetAtPath<Texture2D>(folder + "/" + albedo) : null);
            mat.SetTextureScale("_BaseMap", tiling);
            mat.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>(folder + "/ripples_normal.png"));
            mat.SetFloat("_BumpScale", bump);
            mat.SetFloat("_Smoothness", smoothness);
            mat.SetFloat("_Metallic", 0f);
            mat.SetTexture("_OcclusionMap", FlatTexture("T_WaterReflection", new Color32(0, (byte)(reflection * 255), 0, 255)));
            mat.SetFloat("_OcclusionStrength", 1f);
            mat.SetColor("_EmissionColor", Color.black);   // a new material defaults to white emission: the stream glowed
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            mat.SetFloat("_Surface", 1f);            // transparent
            mat.SetFloat("_Blend", 0f);              // alpha
            mat.SetFloat("_BlendModePreserveSpecular", 1f);   // reflections stay at full strength over the see-through body
            mat.SetFloat("_Cull", 2f);
            mat.SetFloat("_ZWrite", 0f);
            mat.SetFloat("_ReceiveShadows", 1f);
            mat.SetFloat("_EnvironmentReflections", 1f);
            mat.SetFloat("_SpecularHighlights", 1f);
            BaseShaderGUI.SetMaterialKeywords(mat, LitGUI.SetMaterialKeywords);
            mat.renderQueue = (int)RenderQueue.Transparent;
            EditorUtility.SetDirty(mat);
            return mat;
        }

        /// <summary>A flat terrain mask map (no metal, full occlusion, low smoothness) for layers without their own.</summary>
        static Texture2D MatteMask() => FlatTexture("T_MatteMask", new Color32(0, 255, 0, 12));

        /// <summary>A 4×4 linear texture of one value (written once to Generated/Landscape/TerrainLayers).</summary>
        static Texture2D FlatTexture(string name, Color32 value)
        {
            string path = $"{Out}/TerrainLayers/{name}_{value.r}_{value.g}_{value.b}_{value.a}.png";
            if (!File.Exists(path))
            {
                var t = new Texture2D(4, 4, TextureFormat.RGBA32, false, true);
                var px = new Color32[16];
                for (int i = 0; i < 16; i++) px[i] = value;
                t.SetPixels32(px);
                File.WriteAllBytes(path, t.EncodeToPNG());
                Object.DestroyImmediate(t);
                AssetDatabase.ImportAsset(path);
                var ti = (TextureImporter)AssetImporter.GetAtPath(path);
                ti.sRGBTexture = false;
                ti.mipmapEnabled = false;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static Material TerrainMaterial()
        {
            string path = $"{Out}/Materials/M_SiteTerrain.mat";
            var shader = Shader.Find("Universal Render Pipeline/Terrain/Lit");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.shader = shader;
            mat.enableInstancing = true;
            // the layers carry mask maps (occlusion, smoothness)
            mat.EnableKeyword("_MASKMAP");
            mat.EnableKeyword("_NORMALMAP");
            // the site terrains are not instanced (NaturalSiteBuilder.Configure explains why)
            mat.DisableKeyword("_TERRAIN_INSTANCED_PERPIXEL_NORMAL");
            EditorUtility.SetDirty(mat);
            return mat;
        }

        static TerrainLayer TerrainLayerAsset(JObject l)
        {
            string id = (string)l["id"];
            string folder = Source + "/" + (string)l["folder"];
            var tex = (JObject)l["textures"];
            var tile = (JArray)l["metersPerTile"];
            string path = $"{Out}/TerrainLayers/TL_{id}.terrainlayer";
            var layer = AssetDatabase.LoadAssetAtPath<TerrainLayer>(path);
            if (layer == null)
            {
                layer = new TerrainLayer();
                AssetDatabase.CreateAsset(layer, path);
            }
            layer.diffuseTexture = AssetDatabase.LoadAssetAtPath<Texture2D>(folder + "/" + (string)tex["albedo"]);
            layer.normalMapTexture = tex["normal"] != null ? AssetDatabase.LoadAssetAtPath<Texture2D>(folder + "/" + (string)tex["normal"]) : null;
            // our mask (R metallic, G occlusion, A smoothness) matches the terrain mask map (B = height, unused)
            layer.maskMapTexture = tex["mask"] != null ? AssetDatabase.LoadAssetAtPath<Texture2D>(folder + "/" + (string)tex["mask"]) : null;
            layer.normalScale = 1f;
            layer.tileSize = new Vector2((float)tile[0], (float)tile[1]);
            layer.diffuseRemapMax = Vector4.one;
            // the scanned lawns read brown from a distance; the app's own lawn (the one of every other site) stays green
            var lawn = AssetDatabase.LoadAssetAtPath<Texture2D>(AssetPaths.Textures + "/T_Lawn.png");
            if (id == "grass" && lawn != null)
            {
                layer.diffuseTexture = lawn;
                layer.normalMapTexture = AssetDatabase.LoadAssetAtPath<Texture2D>(AssetPaths.Textures + "/T_Lawn_N.png");
                layer.maskMapTexture = MatteMask();     // the terrain material reads mask maps: without one it was a mirror
                layer.normalScale = 0.8f;
                layer.tileSize = new Vector2(3f, 3f);
                layer.diffuseRemapMax = new Vector4(1f, 1f, 0.78f, 1f);    // the tint of M_Lawn
            }
            layer.metallic = 0f;
            layer.smoothness = 0.2f;
            EditorUtility.SetDirty(layer);
            return layer;
        }
    }
}
