using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using UnityEngine.LightTransport;
using UnityEngine.PathTracing.Core;
using UnityEngine.PathTracing.Integration;
using UnityEngine.PathTracing.PostProcessing;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Sampling;
using UnityEngine.Rendering.UnifiedRayTracing;
using LightSamplingMode = UnityEngine.PathTracing.Core.LightSamplingMode;
using EmissiveSamplingMode = UnityEngine.PathTracing.Core.EmissiveSamplingMode;
using MaterialHandle = UnityEngine.PathTracing.Core.Handle<UnityEngine.PathTracing.Core.MaterialPool.MaterialDescriptor>;

namespace House4696.Lighting
{
    /// <summary>What to bake and how well.</summary>
    public sealed class ProbeBakeSettings
    {
        /// <summary>Region covered by the probe grid (the house plus a margin around it).</summary>
        public Bounds Bounds;
        /// <summary>Probe spacing in metres; grown automatically when the grid would exceed <see cref="MaxProbes"/>.</summary>
        public float Spacing = 0.5f;
        public int MaxProbes = 48000;
        public int Bounces = 3;
        public int IndirectSamples = 512;
        public int EnvironmentSamples = 128;
        public int ValiditySamples = 64;
        /// <summary>Probes integrated per step; smaller steps keep the app responsive while baking.</summary>
        public int ProbesPerStep = 1024;
        /// <summary>
        /// Multiplier of the lights' bounced contribution. URP's realtime lighting has no 1/π in its diffuse term, so a
        /// light of intensity I lights like a physical irradiance of π·I; the path tracer is physical, hence π.
        /// </summary>
        public float LightIndirectScale = Mathf.PI;
        /// <summary>Probes whose rays hit back faces more often than this are inside geometry.</summary>
        public float InvalidBackfaceRatio = 0.25f;
    }

    /// <summary>
    /// Bakes indirect lighting into a probe grid inside the player, with the GPU path tracer the editor uses for
    /// its own probe bakes: sky light (direct + bounced) and the bounced light of every scene light. Direct light of
    /// the lights stays realtime (URP draws it), so they only enter the bake as indirect sources.
    /// Run as a coroutine; the work is split in steps of <see cref="ProbeBakeSettings.ProbesPerStep"/> probes.
    /// </summary>
    public static class ProbeVolumeBaker
    {
        public static IEnumerator Bake(ProbeBakeResources resources, ProbeBakeSettings settings, IReadOnlyList<Renderer> renderers,
            IReadOnlyList<Light> lights, Action<BakedGIVolume> done, Action<string> failed, Func<bool> cancelled = null, Action<float> progress = null)
        {
            if (resources == null || !resources.IsComplete) { failed?.Invoke("bake resources are missing — run House 46-96 → App → Setup baked GI"); yield break; }
            var job = new Job(resources, settings, cancelled, progress);
            var steps = job.Run(renderers, lights);
            while (true)
            {
                object current;
                try
                {
                    if (!steps.MoveNext()) break;
                    current = steps.Current;
                }
                catch (Exception e)
                {
                    job.Dispose();
                    failed?.Invoke(e.Message);
                    Debug.LogException(e);
                    yield break;
                }
                yield return current;
            }
            job.Dispose();
            if (job.Result != null) done?.Invoke(job.Result);
        }

        sealed class Job : IDisposable
        {
            const int FloatsPerSh = 27;
            const int RisCandidates = 8;
            const int EnvCubemapResolution = 64;
            const int LightGridCells = 64;

            readonly ProbeBakeResources _res;
            readonly ProbeBakeSettings _s;
            readonly Func<bool> _cancelled;
            readonly Action<float> _progress;
            readonly List<UnityEngine.Object> _temp = new List<UnityEngine.Object>();
            readonly List<GraphicsBuffer> _buffers = new List<GraphicsBuffer>();
            readonly List<MaterialPool.MaterialDescriptor> _descriptors = new List<MaterialPool.MaterialDescriptor>();

            RayTracingContext _ctx;
            World _world;
            SamplingResources _sampling;
            ProbeIntegrator _integrator;
            GraphicsBuffer _scratch;
            CommandBuffer _cmd;

            public BakedGIVolume Result;

            public Job(ProbeBakeResources res, ProbeBakeSettings s, Func<bool> cancelled, Action<float> progress)
            {
                _res = res; _s = s; _cancelled = cancelled; _progress = progress;
            }

            bool Cancelled => _cancelled != null && _cancelled();

            public IEnumerator Run(IReadOnlyList<Renderer> renderers, IReadOnlyList<Light> lights)
            {
                var clock = System.Diagnostics.Stopwatch.StartNew();
                _progress?.Invoke(0f);

                // --- probe grid
                float spacing = Mathf.Max(0.1f, _s.Spacing);
                Vector3Int size;
                while (true)
                {
                    var cells = _s.Bounds.size / spacing;
                    size = new Vector3Int(Mathf.CeilToInt(cells.x) + 1, Mathf.CeilToInt(cells.y) + 1, Mathf.CeilToInt(cells.z) + 1);
                    if ((long)size.x * size.y * size.z <= _s.MaxProbes) break;
                    spacing *= 1.15f;
                }
                var origin = _s.Bounds.center - (Vector3)(size - Vector3Int.one) * (spacing * 0.5f);
                int count = size.x * size.y * size.z;
                var positions = new Vector3[count];
                for (int z = 0, i = 0; z < size.z; z++)
                    for (int y = 0; y < size.y; y++)
                        for (int x = 0; x < size.x; x++, i++)
                            positions[i] = origin + new Vector3(x, y, z) * spacing;

                // --- world: geometry, materials, lights, environment
                _cmd = new CommandBuffer { name = "House probe bake" };
                CreateContexts();
                var sceneBounds = AddGeometry(renderers, out int instances);
                sceneBounds.Encapsulate(_s.Bounds);
                int lightCount = AddLights(lights);
                SetEnvironment();
                _world.lightPickingMethod = LightPickingMethod.LightGrid;
                _world.Build(sceneBounds, _cmd, ref _scratch, _sampling, true, EnvCubemapResolution, LightGridCells);
                Graphics.ExecuteCommandBuffer(_cmd);
                _cmd.Clear();
                yield return null;
                if (Cancelled) yield break;
                double worldMs = clock.Elapsed.TotalMilliseconds;

                // --- integrator
                var positionsBuffer = Buffer(count, sizeof(float) * 3);
                positionsBuffer.SetData(positions);
                _integrator = new ProbeIntegrator();
                _integrator.Prepare(positionsBuffer, new ProbeIntegratorResources
                {
                    IndirectShader = _ctx.CreateRayTracingShader(_res.IndirectRadiance),
                    DirectStochasticLightShader = _ctx.CreateRayTracingShader(_res.DirectStochasticLight),
                    DirectDirectionalAndEnviromentShader = _ctx.CreateRayTracingShader(_res.DirectDirectionalAndEnvironment),
                    ValidityShader = _ctx.CreateRayTracingShader(_res.Validity),
                    GatherKernel = new SegmentedReduction(_res.SegmentedReduction),
                }, _sampling);
                _integrator.SetProgressReporter(new BakeProgressState());
                var post = new ProbePostProcessor();
                post.Prepare(_res.ProbePostProcessing);

                int step = Mathf.Max(64, _s.ProbesPerStep);
                uint maxSamples = (uint)Mathf.Max(_s.IndirectSamples, _s.EnvironmentSamples);
                ProbeIntegrator.GetRadianceScratchBufferSizesInDwords((uint)step, maxSamples, out uint expRad, out uint redRad);
                ProbeIntegrator.GetValidityScratchBufferSizesInDwords((uint)step, (uint)_s.ValiditySamples, out uint expVal, out uint redVal);
                var expansion = Buffer((int)Math.Max(expRad, expVal), sizeof(float));
                var reduction = Buffer((int)Math.Max(redRad, redVal), sizeof(float));
                var indirect = Buffer(step * FloatsPerSh, sizeof(float));
                var direct = Buffer(step * FloatsPerSh, sizeof(float));
                var sum = Buffer(step * FloatsPerSh, sizeof(float));
                var irradiance = Buffer(step * FloatsPerSh, sizeof(float));
                var unity = Buffer(step * FloatsPerSh, sizeof(float));
                var validityBuffer = Buffer(step, sizeof(float));

                var zeros = new float[step];
                var sh = new float[count * FloatsPerSh];
                var backface = new float[count];
                uint maxLights = (uint)Mathf.Max(1, _world.MaxLightsInAnyCell);

                for (int offset = 0; offset < count; offset += step)
                {
                    if (Cancelled) yield break;
                    int n = Mathf.Min(step, count - offset);
                    _cmd.SetBufferData(validityBuffer, zeros);   // unlike the radiance passes, validity accumulates into its output
                    _integrator.EstimateValidity(_cmd, _world, (uint)offset, (uint)n, 0, (uint)_s.ValiditySamples,
                        validityBuffer, 0, expansion, reduction, false);
                    _integrator.EstimateIndirectRadianceShl2(_cmd, _world, (uint)offset, (uint)n, (uint)_s.Bounces, 0, (uint)_s.IndirectSamples,
                        LightSamplingMode.RIS, RisCandidates, maxLights, EmissiveSamplingMode.MIS, false, indirect, 0, expansion, reduction, false);
                    _integrator.EstimateDirectRadianceShl2(_cmd, _world, (uint)offset, (uint)n, 0, (uint)_s.EnvironmentSamples,
                        LightSamplingMode.RIS, RisCandidates, maxLights, false, direct, 0, expansion, reduction, false);
                    post.AddSphericalHarmonicsL2(_cmd, indirect, direct, sum, 0, 0, 0, (uint)n);
                    post.ConvolveRadianceToIrradiance(_cmd, sum, irradiance, 0, 0, (uint)n);
                    post.ConvertToUnityFormat(_cmd, irradiance, unity, 0, 0, (uint)n);
                    Graphics.ExecuteCommandBuffer(_cmd);
                    _cmd.Clear();

                    var shRead = AsyncGPUReadback.Request(unity, n * FloatsPerSh * sizeof(float), 0);
                    var valRead = AsyncGPUReadback.Request(validityBuffer, n * sizeof(float), 0);
                    while (!shRead.done || !valRead.done) yield return null;
                    if (shRead.hasError || valRead.hasError) throw new InvalidOperationException("GPU readback of the probe bake failed");
                    Unity.Collections.NativeArray<float>.Copy(shRead.GetData<float>(), 0, sh, offset * FloatsPerSh, n * FloatsPerSh);
                    Unity.Collections.NativeArray<float>.Copy(valRead.GetData<float>(), 0, backface, offset, n);
                    _progress?.Invoke((offset + n) / (float)count);
                }

                // --- probes inside walls take their neighbours' light, then pack for the shaders
                var validity = new float[count];
                for (int i = 0; i < count; i++) validity[i] = backface[i] > _s.InvalidBackfaceRatio ? 0f : 1f;
                Dilate(sh, validity, size);
                double integrateMs = clock.Elapsed.TotalMilliseconds - worldMs;
                int invalid = 0;
                foreach (float v in validity) if (v < 0.5f) invalid++;
                Result = new BakedGIVolume(origin, spacing, size, Pack(sh, count), validity, (float)clock.Elapsed.TotalSeconds)
                {
                    BackfaceRatio = backface,
                    Stats = $"{instances} instances, {lightCount} lights, world {worldMs:0} ms, integration {integrateMs:0} ms, " +
                            $"{count} probes ({invalid} inside geometry), samples {_s.IndirectSamples}/{_s.EnvironmentSamples}/{_s.ValiditySamples}, {_s.Bounces} bounces",
                };
                _progress?.Invoke(1f);
            }

            void CreateContexts()
            {
                var rt = new RayTracingResources();
#if UNITY_EDITOR
                rt.Load();
#else
                if (!rt.LoadFromRenderPipelineResources()) throw new InvalidOperationException("ray tracing resources are missing from the build");
#endif
                _ctx = new RayTracingContext(RayTracingBackend.Compute, rt);
                var worldRes = new WorldResourceSet();
                if (!worldRes.LoadFromRenderPipelineResources()) throw new InvalidOperationException("path tracing world resources are missing from the build");
                _world = new World();
                _world.Init(_ctx, worldRes);

                // SamplingResources.Load() is editor-only (AssetDatabase): fill the same fields from the shipped asset
                _sampling = new SamplingResources();
                const BindingFlags f = BindingFlags.NonPublic | BindingFlags.Instance;
                var t = typeof(SamplingResources);
                t.GetField("m_SobolScramblingTile", f).SetValue(_sampling, _res.SobolScramblingTile);
                t.GetField("m_SobolRankingTile", f).SetValue(_sampling, _res.SobolRankingTile);
                t.GetField("m_SobolOwenScrambled256Samples", f).SetValue(_sampling, _res.SobolOwenScrambled256);
                var sobol = new GraphicsBuffer(GraphicsBuffer.Target.Structured, (int)(SobolData.SobolDims * SobolData.SobolSize), sizeof(uint));
                sobol.SetData(SobolData.SobolMatrices);
                t.GetField("m_SobolBuffer", f).SetValue(_sampling, sobol);
            }

            Bounds AddGeometry(IReadOnlyList<Renderer> renderers, out int instances)
            {
                instances = 0;
                var materials = new Dictionary<Material, MaterialHandle>();
                MaterialHandle fallback = MaterialHandle.Invalid;
                var bounds = new Bounds();
                bool any = false;
                var shared = new List<Material>();
                foreach (var r in renderers)
                {
                    if (r == null || !r.enabled || !r.gameObject.activeInHierarchy || !(r is MeshRenderer)) continue;
                    var mesh = r.GetComponent<MeshFilter>()?.sharedMesh;
                    if (mesh == null || mesh.subMeshCount == 0) continue;
                    r.GetSharedMaterials(shared);

                    int subs = mesh.subMeshCount;
                    var handles = new MaterialHandle[subs];
                    var masks = new uint[subs];
                    uint mask = World.GetInstanceMask(r.shadowCastingMode, true, RenderedGameObjectsFilter.OnlyStatic);
                    bool visible = false;
                    for (int s = 0; s < subs; s++)
                    {
                        var m = shared.Count > 0 ? shared[Mathf.Min(s, shared.Count - 1)] : null;
                        // glass and other transparent surfaces let the light through: rays ignore them
                        bool transparent = m == null || m.renderQueue >= (int)RenderQueue.GeometryLast + 1;
                        if (transparent)
                        {
                            if (fallback == MaterialHandle.Invalid) fallback = AddMaterial(FallbackMaterial(null));
                            handles[s] = fallback;
                            masks[s] = 0u;
                            continue;
                        }
                        if (!materials.TryGetValue(m, out var h))
                        {
                            h = AddMaterial(m.FindPass("Meta") >= 0 ? m : FallbackMaterial(m));
                            materials[m] = h;
                        }
                        handles[s] = h;
                        masks[s] = mask;
                        visible |= mask != 0u;
                    }
                    if (!visible) continue;
                    _world.AddInstance(mesh, handles, masks, UnityComputeWorld.RenderingObjectLayer, r.localToWorldMatrix, r.bounds,
                        true, RenderedGameObjectsFilter.OnlyStatic, true);
                    instances++;
                    if (any) bounds.Encapsulate(r.bounds); else { bounds = r.bounds; any = true; }
                }
                return bounds;
            }

            MaterialHandle AddMaterial(Material m)
            {
                var d = MaterialPool.ConvertUnityMaterialToMaterialDescriptor(m, EmissionMode.Baked);
                _descriptors.Add(d);
                return _world.AddMaterial(d, UVChannel.UV0);
            }

            Material FallbackMaterial(Material source)
            {
                var m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { hideFlags = HideFlags.HideAndDontSave };
                var c = source != null && source.HasColor("_BaseColor") ? source.GetColor("_BaseColor")
                      : source != null && source.HasColor("_Color") ? source.GetColor("_Color") : new Color(0.5f, 0.5f, 0.5f);
                m.SetColor("_BaseColor", c);
                _temp.Add(m);
                return m;
            }

            int AddLights(IReadOnlyList<Light> lights)
            {
                var list = new List<World.LightDescriptor>();
                foreach (var l in lights)
                {
                    if (l == null || !l.isActiveAndEnabled || l.intensity <= 0f) continue;
                    if (l.type != LightType.Directional && l.type != LightType.Point && l.type != LightType.Spot) continue;
                    var d = new World.LightDescriptor
                    {
                        Type = l.type,
                        LinearLightColor = Util.GetLinearLightColor(l),
                        Shadows = LightShadows.Hard,   // bounced light must not leak through walls even if the realtime light has no shadows
                        Transform = Matrix4x4.TRS(l.transform.position, l.transform.rotation, Vector3.one),
                        LightmapBakeType = LightmapBakeType.Realtime,   // indirect only: URP draws the direct light
                        FalloffType = UnityEngine.Experimental.GlobalIllumination.FalloffType.InverseSquared,
                        AreaSize = l.type == LightType.Directional ? new Vector2(0.5f * Mathf.Deg2Rad, 0f) : Vector2.one,
                        SpotAngle = l.spotAngle,
                        InnerSpotAngle = l.innerSpotAngle,
                        CullingMask = uint.MaxValue,
                        BounceIntensity = l.bounceIntensity * _s.LightIndirectScale,
                        Range = Mathf.Max(0.01f, l.range),
                        ShadowMaskChannel = -1,
                        ShadowRadius = l.type == LightType.Directional ? 0f : 0.05f,
                    };
                    list.Add(d);
                }
                if (list.Count > 0)
                    _world.AddLights(list.ToArray(), false, true, MixedLightingMode.IndirectOnly);
                return list.Count;
            }

            /// <summary>The environment the realtime renderer lights with: skybox, trilight gradient or flat colour.</summary>
            void SetEnvironment()
            {
                if (RenderSettings.ambientMode == AmbientMode.Skybox && RenderSettings.skybox != null)
                {
                    _world.SetEnvironmentMaterial(RenderSettings.skybox);
                    return;
                }
                const int res = 32;
                float k = RenderSettings.ambientIntensity;
                Color sky = RenderSettings.ambientSkyColor.linear * k, equator = RenderSettings.ambientEquatorColor.linear * k,
                      ground = RenderSettings.ambientGroundColor.linear * k;
                bool flat = RenderSettings.ambientMode == AmbientMode.Flat;
                var cube = new Cubemap(res, TextureFormat.RGBAFloat, false) { hideFlags = HideFlags.HideAndDontSave };
                var px = new Color[res * res];
                for (int f = 0; f < 6; f++)
                {
                    for (int y = 0; y < res; y++)
                        for (int x = 0; x < res; x++)
                        {
                            float u = (x + 0.5f) / res * 2f - 1f, v = (y + 0.5f) / res * 2f - 1f;
                            float dirY = CubeDirection((CubemapFace)f, u, v).y;
                            px[y * res + x] = flat ? sky : dirY >= 0f ? Color.Lerp(equator, sky, dirY) : Color.Lerp(equator, ground, -dirY);
                        }
                    cube.SetPixels(px, (CubemapFace)f);
                }
                cube.Apply(false);
                _temp.Add(cube);
                var mat = new Material(_res.PassthroughSkybox) { hideFlags = HideFlags.HideAndDontSave };
                mat.SetTexture("_Tex", cube);
                _temp.Add(mat);
                _world.SetEnvironmentMaterial(mat);
            }

            static Vector3 CubeDirection(CubemapFace face, float u, float v)
            {
                // Unity cubemap face orientation (v grows downwards on every face)
                switch (face)
                {
                    case CubemapFace.PositiveX: return new Vector3(1f, -v, -u).normalized;
                    case CubemapFace.NegativeX: return new Vector3(-1f, -v, u).normalized;
                    case CubemapFace.PositiveY: return new Vector3(u, 1f, v).normalized;
                    case CubemapFace.NegativeY: return new Vector3(u, -1f, -v).normalized;
                    case CubemapFace.PositiveZ: return new Vector3(u, -v, 1f).normalized;
                    default: return new Vector3(-u, -v, -1f).normalized;
                }
            }

            /// <summary>Invalid probes (inside geometry) get the average of their valid neighbours, growing outwards.</summary>
            static void Dilate(float[] sh, float[] validity, Vector3Int size)
            {
                int count = validity.Length;
                var filled = new bool[count];
                for (int i = 0; i < count; i++) filled[i] = validity[i] > 0.5f;
                var acc = new float[FloatsPerSh];
                for (int pass = 0; pass < 4; pass++)
                {
                    var newly = new List<int>();
                    for (int z = 0; z < size.z; z++)
                        for (int y = 0; y < size.y; y++)
                            for (int x = 0; x < size.x; x++)
                            {
                                int i = x + size.x * (y + size.y * z);
                                if (filled[i]) continue;
                                Array.Clear(acc, 0, acc.Length);
                                int n = 0;
                                for (int dz = -1; dz <= 1; dz++)
                                    for (int dy = -1; dy <= 1; dy++)
                                        for (int dx = -1; dx <= 1; dx++)
                                        {
                                            int nx = x + dx, ny = y + dy, nz = z + dz;
                                            if (nx < 0 || ny < 0 || nz < 0 || nx >= size.x || ny >= size.y || nz >= size.z) continue;
                                            int j = nx + size.x * (ny + size.y * nz);
                                            if (!filled[j]) continue;
                                            for (int c = 0; c < FloatsPerSh; c++) acc[c] += sh[j * FloatsPerSh + c];
                                            n++;
                                        }
                                if (n == 0) continue;
                                for (int c = 0; c < FloatsPerSh; c++) sh[i * FloatsPerSh + c] = acc[c] / n;
                                newly.Add(i);
                            }
                    if (newly.Count == 0) break;
                    foreach (int i in newly) filled[i] = true;
                }
            }

            /// <summary>Unity SH L2 (channel-major, 9 coefficients) → the 7 shader vectors SHAr/g/b, SHBr/g/b, SHC.</summary>
            static Vector4[] Pack(float[] sh, int count)
            {
                var o = new Vector4[count * BakedGIVolume.ShTextureCount];
                for (int i = 0; i < count; i++)
                {
                    int b = i * FloatsPerSh;
                    for (int c = 0; c < 3; c++)
                    {
                        int k = b + c * 9;
                        o[i * 7 + c] = new Vector4(sh[k + 3], sh[k + 1], sh[k + 2], sh[k + 0] - sh[k + 6]);
                        o[i * 7 + 3 + c] = new Vector4(sh[k + 4], sh[k + 5], sh[k + 6] * 3f, sh[k + 7]);
                    }
                    o[i * 7 + 6] = new Vector4(sh[b + 8], sh[b + 9 + 8], sh[b + 18 + 8], 1f);
                }
                return o;
            }

            GraphicsBuffer Buffer(int count, int stride)
            {
                var b = new GraphicsBuffer(GraphicsBuffer.Target.Structured, Mathf.Max(1, count), stride);
                _buffers.Add(b);
                return b;
            }

            public void Dispose()
            {
                _integrator?.Dispose();
                _world?.Dispose();
                _sampling?.Dispose();
                _ctx?.Dispose();
                _scratch?.Dispose();
                _cmd?.Release();
                foreach (var b in _buffers) b.Dispose();
                _buffers.Clear();
                foreach (var d in _descriptors)
                {
                    DestroyRenderTexture(d.Albedo);
                    DestroyRenderTexture(d.Emission);
                    DestroyRenderTexture(d.Transmission);
                }
                _descriptors.Clear();
                foreach (var o in _temp) BakedGIVolume.Release(o);
                _temp.Clear();
            }

            static void DestroyRenderTexture(Texture t)
            {
                if (t is RenderTexture rt) { rt.Release(); BakedGIVolume.Release(rt); }
            }
        }
    }
}
