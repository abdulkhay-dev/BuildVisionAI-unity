using System;
using System.Reflection;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;

namespace House4696.Lighting
{
    /// <summary>
    /// Shows <see cref="BakedGIVolume.Active"/>: after the depth-normals prepass a compute pass resolves the probe
    /// volume per pixel and hands the result to URP as the screen-space irradiance texture (the same path the
    /// Surface Cache GI feature uses), so every Lit material gets it as baked GI without shader changes. Costs one
    /// full-screen compute dispatch; does nothing while no volume is active.
    /// </summary>
    public sealed class BakedGIFeature : ScriptableRendererFeature
    {
        public ComputeShader resolveShader;
        [Tooltip("Sample point offset along the surface normal, in probe spacings.")]
        public float normalBias = 0.35f;
        [Tooltip("Sample point offset towards the camera, in probe spacings.")]
        public float viewBias = 0.1f;
        [Tooltip("Distance over which the volume fades to the ambient probe at its border, metres.")]
        public float fadeDistance = 1.5f;

        ResolvePass _pass;

        public override void Create()
        {
            _pass = new ResolvePass(this) { renderPassEvent = RenderPassEvent.AfterRenderingPrePasses + 2 };
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            if (resolveShader == null || BakedGIVolume.Active == null) return;
            var type = renderingData.cameraData.cameraType;
            if (type != CameraType.Game && type != CameraType.SceneView && type != CameraType.Reflection) return;
            _pass.ConfigureInput(ScriptableRenderPassInput.Depth | ScriptableRenderPassInput.Normal);
            renderer.EnqueuePass(_pass);
        }

        sealed class ResolvePass : ScriptableRenderPass
        {
            static readonly PropertyInfo IrradianceProperty =
                typeof(UniversalResourceData).GetProperty("irradianceTexture", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            static readonly int[] ShIds =
            {
                Shader.PropertyToID("_SH0"), Shader.PropertyToID("_SH1"), Shader.PropertyToID("_SH2"), Shader.PropertyToID("_SH3"),
                Shader.PropertyToID("_SH4"), Shader.PropertyToID("_SH5"), Shader.PropertyToID("_SH6"),
            };
            static readonly int DepthsId = Shader.PropertyToID("_Depths"), NormalsId = Shader.PropertyToID("_Normals"),
                OutputId = Shader.PropertyToID("_Output"), ValidityId = Shader.PropertyToID("_Validity"),
                ClipToWorldId = Shader.PropertyToID("_ClipToWorld"), OriginId = Shader.PropertyToID("_VolumeOrigin"),
                SpacingId = Shader.PropertyToID("_VolumeSpacing"), SizeId = Shader.PropertyToID("_VolumeSize"),
                NormalBiasId = Shader.PropertyToID("_NormalBias"), ViewBiasId = Shader.PropertyToID("_ViewBias"),
                FadeId = Shader.PropertyToID("_FadeDistance"), CameraPosId = Shader.PropertyToID("_CameraPos"),
                AmbientId = Shader.PropertyToID("_Ambient");

            readonly BakedGIFeature _owner;
            readonly Vector4[] _ambient = new Vector4[7];

            class PassData
            {
                public ComputeShader Shader;
                public int Kernel;
                public TextureHandle Depths, Normals, Output;
                public BakedGIVolume Volume;
                public Matrix4x4 ClipToWorld;
                public Vector3 CameraPos;
                public Vector4[] Ambient;
                public float NormalBias, ViewBias, Fade;
                public int Width, Height;
            }

            public ResolvePass(BakedGIFeature owner) { _owner = owner; }

            public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
            {
                var volume = BakedGIVolume.Active;
                if (volume == null || IrradianceProperty == null) return;
                var resources = frameData.Get<UniversalResourceData>();
                var cameraData = frameData.Get<UniversalCameraData>();
                if (!resources.cameraDepthTexture.IsValid() || !resources.cameraNormalsTexture.IsValid()) return;

                var depthDesc = renderGraph.GetTextureDesc(resources.cameraDepthTexture);
                int width = depthDesc.width, height = depthDesc.height;   // the resolve covers exactly the depth texture
                var desc = new TextureDesc(width, height)
                {
                    colorFormat = GraphicsFormat.R16G16B16A16_SFloat, enableRandomWrite = true, name = "_BakedGIIrradiance",
                    filterMode = FilterMode.Point,
                };
                var output = renderGraph.CreateTexture(desc);
                var clipToWorld = (GL.GetGPUProjectionMatrix(cameraData.GetProjectionMatrix(), true) * cameraData.GetViewMatrix()).inverse;
                PackAmbient(RenderSettings.ambientProbe, _ambient);

                using (var builder = renderGraph.AddUnsafePass("Baked GI Resolve", out PassData data))
                {
                    data.Shader = _owner.resolveShader;
                    data.Kernel = _owner.resolveShader.FindKernel("Resolve");
                    data.Depths = resources.cameraDepthTexture;
                    data.Normals = resources.cameraNormalsTexture;
                    data.Output = output;
                    data.Volume = volume;
                    data.ClipToWorld = clipToWorld;
                    data.CameraPos = cameraData.worldSpaceCameraPos;
                    data.Ambient = _ambient;
                    data.NormalBias = _owner.normalBias * volume.Spacing;
                    data.ViewBias = _owner.viewBias * volume.Spacing;
                    data.Fade = Mathf.Max(0.01f, _owner.fadeDistance);
                    data.Width = width; data.Height = height;
                    builder.UseTexture(data.Depths, AccessFlags.Read);
                    builder.UseTexture(data.Normals, AccessFlags.Read);
                    builder.UseTexture(data.Output, AccessFlags.Write);
                    builder.SetRenderFunc((PassData d, UnsafeGraphContext ctx) =>
                    {
                        var cmd = CommandBufferHelpers.GetNativeCommandBuffer(ctx.cmd);
                        var v = d.Volume;
                        cmd.SetComputeTextureParam(d.Shader, d.Kernel, DepthsId, d.Depths);
                        cmd.SetComputeTextureParam(d.Shader, d.Kernel, NormalsId, d.Normals);
                        cmd.SetComputeTextureParam(d.Shader, d.Kernel, OutputId, d.Output);
                        for (int i = 0; i < ShIds.Length; i++) cmd.SetComputeTextureParam(d.Shader, d.Kernel, ShIds[i], v.Sh[i]);
                        cmd.SetComputeTextureParam(d.Shader, d.Kernel, ValidityId, v.Validity);
                        cmd.SetComputeMatrixParam(d.Shader, ClipToWorldId, d.ClipToWorld);
                        cmd.SetComputeVectorParam(d.Shader, OriginId, v.Origin);
                        cmd.SetComputeFloatParam(d.Shader, SpacingId, v.Spacing);
                        cmd.SetComputeIntParams(d.Shader, SizeId, v.Size.x, v.Size.y, v.Size.z);
                        cmd.SetComputeFloatParam(d.Shader, NormalBiasId, d.NormalBias);
                        cmd.SetComputeFloatParam(d.Shader, ViewBiasId, d.ViewBias);
                        cmd.SetComputeFloatParam(d.Shader, FadeId, d.Fade);
                        cmd.SetComputeVectorParam(d.Shader, CameraPosId, d.CameraPos);
                        cmd.SetComputeVectorArrayParam(d.Shader, AmbientId, d.Ambient);
                        cmd.DispatchCompute(d.Shader, d.Kernel, (d.Width + 7) / 8, (d.Height + 7) / 8, 1);
                    });
                }
                IrradianceProperty.SetValue(resources, output);
            }

            /// <summary>SphericalHarmonicsL2 → SHAr/g/b, SHBr/g/b, SHC (the unity_SH* layout).</summary>
            static void PackAmbient(SphericalHarmonicsL2 sh, Vector4[] o)
            {
                for (int c = 0; c < 3; c++)
                {
                    o[c] = new Vector4(sh[c, 3], sh[c, 1], sh[c, 2], sh[c, 0] - sh[c, 6]);
                    o[3 + c] = new Vector4(sh[c, 4], sh[c, 5], sh[c, 6] * 3f, sh[c, 7]);
                }
                o[6] = new Vector4(sh[0, 8], sh[1, 8], sh[2, 8], 1f);
            }
        }
    }
}
