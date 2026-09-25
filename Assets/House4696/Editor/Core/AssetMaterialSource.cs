using UnityEditor;
using UnityEditor.Rendering.Universal.ShaderGUI;
using UnityEngine;

namespace House4696.Core
{
    /// <summary>
    /// Editor material source: creates or updates URP/Lit material assets under Generated/Materials from
    /// <see cref="LitOptions"/> (textures come from <see cref="TextureFactory"/>). These assets are what
    /// <see cref="HouseContent"/> later ships to the player.
    /// </summary>
    public sealed class AssetMaterialSource : IMaterialSource
    {
        public AssetMaterialSource() => AssetPaths.Ensure(AssetPaths.Materials);

        public Material Lit(string name, LitOptions o)
        {
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            string path = $"{AssetPaths.Materials}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(shader);
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = shader;
            m.shaderKeywords = new string[0];

            m.SetFloat("_WorkflowMode", 1f);
            m.SetColor("_BaseColor", o.Color);
            var alb = string.IsNullOrEmpty(o.Albedo) ? null : TextureFactory.Get(o.Albedo);
            m.SetTexture("_BaseMap", alb);
            var nrm = string.IsNullOrEmpty(o.Normal) ? null : TextureFactory.Get(o.Normal);
            m.SetTexture("_BumpMap", nrm);
            m.SetFloat("_BumpScale", o.NormalScale <= 0 ? 1f : o.NormalScale);
            Vector2 tiling = o.Tiling != Vector2.zero ? o.Tiling
                : Vector2.one / Mathf.Max(0.001f, o.MetersPerTile <= 0 ? 1f : o.MetersPerTile);
            m.SetTextureScale("_BaseMap", tiling);
            m.SetFloat("_Smoothness", o.Smoothness);
            m.SetFloat("_Metallic", o.Metallic);
            m.SetFloat("_AlphaClip", o.Cutout ? 1f : 0f);
            m.SetFloat("_Cutoff", o.Cutoff <= 0 ? 0.5f : o.Cutoff);
            m.SetFloat("_Cull", o.TwoSided ? 0f : 2f);
            m.SetFloat("_Surface", o.Transparent ? 1f : 0f);
            m.SetFloat("_Blend", 0f);
            m.SetFloat("_BlendModePreserveSpecular", 1f);
            m.SetFloat("_ReceiveShadows", 1f);
            m.SetFloat("_EnvironmentReflections", 1f);
            m.SetFloat("_SpecularHighlights", 1f);
            if (o.Emission.maxColorComponent > 0f)
            {
                m.SetColor("_EmissionColor", o.Emission);
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
                m.EnableKeyword("_EMISSION");
            }
            else
            {
                m.SetColor("_EmissionColor", Color.black);
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            }
            BaseShaderGUI.SetMaterialKeywords(m, LitGUI.SetMaterialKeywords);
            if (o.Cutout) m.renderQueue = (int)UnityEngine.Rendering.RenderQueue.AlphaTest;
            EditorUtility.SetDirty(m);
            return m;
        }

        public Material Sky()
        {
            var skyShader = Shader.Find("Skybox/Panoramic");
            string skyPath = $"{AssetPaths.Materials}/{HouseContent.SkyMaterial}.mat";
            var sky = AssetDatabase.LoadAssetAtPath<Material>(skyPath);
            if (sky == null) { sky = new Material(skyShader); AssetDatabase.CreateAsset(sky, skyPath); }
            sky.shader = skyShader;
            sky.SetTexture("_MainTex", TextureFactory.Get("T_Sky"));
            sky.SetFloat("_Mapping", 1f);      // latitude-longitude
            sky.SetFloat("_ImageType", 0f);    // 360
            sky.SetFloat("_Exposure", 1.45f);
            sky.SetFloat("_Rotation", 0f);
            sky.SetColor("_Tint", new Color(0.48f, 0.44f, 0.5f, 0.5f));
            EditorUtility.SetDirty(sky);
            AssetDatabase.SaveAssets();
            return sky;
        }
    }
}
