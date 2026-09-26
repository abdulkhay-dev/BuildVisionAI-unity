using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// Draws the site's plants and small stones with GPU instancing. Instances are bucketed into 4 m chunks; per camera
    /// every chunk in the view picks a LOD by its distance and the variant's size (the kit's LODGroup screen heights)
    /// and the matrices of each (variant, LOD) are drawn in batches of 1023 with tight world bounds.
    /// Shadows are a separate shadow-only draw of the coarsest mesh (LOD1: the same silhouette, a third of the
    /// triangles) of the shadow-casting plants within <see cref="ShadowDistance"/> of the camera — in view or not, so
    /// plants just outside the frame still shade it — and with bounds that keep them out of the far cascades.
    /// One mesh per variant in memory; ~1 ms of CPU for tens of thousands of plants.
    /// </summary>
    public sealed class PlantField : MonoBehaviour
    {
        /// <summary>Diagnostics (API tune): draw the plants at all.</summary>
        public static bool Enabled = true;
        /// <summary>Diagnostics (API tune): plants cast shadows.</summary>
        public static bool Shadows = true;
        /// <summary>Shadow casters are the plants within this distance of the camera (small plants further away give sub-texel shadows).</summary>
        public static float ShadowDistance = 15f;
        /// <summary>Diagnostics (API tune): LODs above this index are not drawn.</summary>
        public static int MaxLod = 99;
        /// <summary>Diagnostics (API tune): multiplies the LOD transition heights (&gt;1 = coarser LODs sooner).</summary>
        public static float LodScale = 1f;
        /// <summary>Instances drawn per LOD in the last main-camera frame (diagnostics).</summary>
        public static readonly int[] Drawn = new int[4];

        const float ChunkSize = 4f;
        const int Batch = 1023;

        sealed class Lod
        {
            public Mesh Mesh;
            public Material[] Materials;
            public readonly List<Matrix4x4> Visible = new List<Matrix4x4>();
            public Bounds Bounds;
        }

        sealed class Proto
        {
            public string Name;
            public readonly int[] Drawn = new int[4];
            public Lod[] Lods;
            public float[] Heights;       // screen-relative transition heights (LODGroup)
            public float Size;            // LODGroup size (metres)
            public bool CastsShadows;
            public readonly List<Matrix4x4> ShadowCasters = new List<Matrix4x4>();
            public Bounds ShadowBounds;
        }

        sealed class Chunk
        {
            public Bounds Bounds;
            public readonly List<int> Protos = new List<int>();
            public readonly List<List<Matrix4x4>> Instances = new List<List<Matrix4x4>>();
            /// <summary>Largest instance scale per proto: big clumps keep their detail further out.</summary>
            public readonly List<float> MaxScale = new List<float>();
        }

        readonly List<Proto> _protos = new List<Proto>();
        readonly Dictionary<GameObject, int> _protoIndex = new Dictionary<GameObject, int>();
        readonly Dictionary<long, Chunk> _chunks = new Dictionary<long, Chunk>();
        readonly List<Chunk> _chunkList = new List<Chunk>();
        readonly Plane[] _planes = new Plane[6];
        readonly Matrix4x4[] _buffer = new Matrix4x4[Batch];
        public uint RenderingLayer = 2u;
        public int Count { get; private set; }

        /// <summary>Adds one instance of a kit prefab (LODGroup or single renderer).</summary>
        public void Add(GameObject prefab, Vector3 position, float yawRadians, float scale, bool shadows)
        {
            int p = ProtoOf(prefab, shadows);
            if (p < 0) return;
            var m = Matrix4x4.TRS(position, Quaternion.Euler(0f, yawRadians * Mathf.Rad2Deg, 0f), Vector3.one * scale);
            long key = ((long)Mathf.FloorToInt(position.x / ChunkSize) << 32) ^ (uint)Mathf.FloorToInt(position.z / ChunkSize);
            if (!_chunks.TryGetValue(key, out var c))
            {
                c = new Chunk { Bounds = new Bounds(position, Vector3.zero) };
                _chunks[key] = c;
                _chunkList.Add(c);
            }
            int slot = c.Protos.IndexOf(p);
            if (slot < 0)
            {
                c.Protos.Add(p);
                c.Instances.Add(new List<Matrix4x4>());
                c.MaxScale.Add(0f);
                slot = c.Protos.Count - 1;
            }
            c.Instances[slot].Add(m);
            c.MaxScale[slot] = Mathf.Max(c.MaxScale[slot], scale);
            float r = _protos[p].Size * scale;
            c.Bounds.Encapsulate(new Bounds(position + Vector3.up * r * 0.5f, new Vector3(r, r, r)));
            Count++;
        }

        int ProtoOf(GameObject prefab, bool shadows)
        {
            if (_protoIndex.TryGetValue(prefab, out int i)) return i;
            var proto = new Proto { CastsShadows = shadows, Name = prefab.name };
            var group = prefab.GetComponent<LODGroup>();
            if (group != null)
            {
                var lods = group.GetLODs();
                proto.Lods = new Lod[lods.Length];
                proto.Heights = new float[lods.Length];
                for (int k = 0; k < lods.Length; k++)
                {
                    var r = lods[k].renderers.Length > 0 ? lods[k].renderers[0] as MeshRenderer : null;
                    var f = r != null ? r.GetComponent<MeshFilter>() : null;
                    proto.Lods[k] = new Lod { Mesh = f != null ? f.sharedMesh : null, Materials = r != null ? r.sharedMaterials : null };
                    proto.Heights[k] = lods[k].screenRelativeTransitionHeight;
                }
                proto.Size = group.size;
            }
            else
            {
                var r = prefab.GetComponentInChildren<MeshRenderer>();
                var f = r != null ? r.GetComponent<MeshFilter>() : null;
                if (f == null) return _protoIndex[prefab] = -1;
                // a single mesh without LODs (a terrain-detail asset): drawn only while it is reasonably large
                proto.Lods = new[] { new Lod { Mesh = f.sharedMesh, Materials = r.sharedMaterials } };
                proto.Heights = new[] { 0.02f };
                proto.Size = f.sharedMesh.bounds.size.magnitude;
            }
            _protos.Add(proto);
            return _protoIndex[prefab] = _protos.Count - 1;
        }

        float _lastK;

        /// <summary>Diagnostics: per variant its LODGroup size, transition heights and instances drawn per LOD (main camera).</summary>
        public string Report()
        {
            var sb = new System.Text.StringBuilder($"k {_lastK:0.###}\n");
            foreach (var p in _protos)
                sb.Append($"{p.Name} size {p.Size:0.##} h [{string.Join(", ", System.Array.ConvertAll(p.Heights, x => x.ToString("0.####")))}] drawn [{string.Join(", ", p.Drawn)}]\n");
            return sb.ToString();
        }

        void OnEnable() => RenderPipelineManager.beginCameraRendering += Draw;
        void OnDisable() => RenderPipelineManager.beginCameraRendering -= Draw;

        static void Grow(ref Bounds b, List<Matrix4x4> list, in Bounds add)
        {
            if (list.Count == 0) b = add; else b.Encapsulate(add);
        }

        void Draw(ScriptableRenderContext ctx, Camera cam)
        {
            if (!Enabled || (cam.cameraType != CameraType.Game && cam.cameraType != CameraType.SceneView)) return;
            GeometryUtility.CalculateFrustumPlanes(cam, _planes);
            var camPos = cam.transform.position;
            // screen-relative height of an object of size s at distance d: s / (2 d tan(fov/2)). Deliberately without
            // QualitySettings.lodBias: the app raises it for its trees (GardenLod compensates the same way); the plant
            // thresholds are real screen fractions
            float k = 1f / (2f * Mathf.Tan(0.5f * cam.fieldOfView * Mathf.Deg2Rad));
            float shadowDist2 = Shadows ? ShadowDistance * ShadowDistance : -1f;
            foreach (var p in _protos)
            {
                p.ShadowCasters.Clear();
                foreach (var l in p.Lods) l.Visible.Clear();
            }
            bool main = cam == Camera.main;
            if (main)
            {
                System.Array.Clear(Drawn, 0, Drawn.Length);
                foreach (var p in _protos) System.Array.Clear(p.Drawn, 0, p.Drawn.Length);
                _lastK = k;
            }
            foreach (var c in _chunkList)
            {
                float d2 = c.Bounds.SqrDistance(camPos);
                bool inView = GeometryUtility.TestPlanesAABB(_planes, c.Bounds);
                bool shadowNear = d2 < shadowDist2;
                if (!inView && !shadowNear) continue;
                float d = Mathf.Max(0.5f, Mathf.Sqrt(d2));
                for (int s = 0; s < c.Protos.Count; s++)
                {
                    var proto = _protos[c.Protos[s]];
                    var list = c.Instances[s];
                    if (inView)
                    {
                        // the LOD at the chunk's nearest and farthest point: one pick for the whole chunk when they agree,
                        // otherwise per instance (a 4 m chunk spans several metres of the LOD bands)
                        float sizeK = proto.Size * c.MaxScale[s] * k;
                        int near = PickLod(proto, sizeK / d);
                        int far = PickLod(proto, sizeK / Mathf.Max(0.5f, Mathf.Sqrt(MaxSqrDistance(c.Bounds, camPos))));
                        if (near == far)
                        {
                            if (near >= 0) AddAll(proto, near, list, c.Bounds, main);
                        }
                        else
                        {
                            for (int j = 0; j < list.Count; j++)
                            {
                                var m = list[j];
                                float dx = m.m03 - camPos.x, dy = m.m13 - camPos.y, dz = m.m23 - camPos.z;
                                float scale = Mathf.Sqrt(m.m00 * m.m00 + m.m10 * m.m10 + m.m20 * m.m20);
                                int lod = PickLod(proto, proto.Size * scale * k / Mathf.Max(0.5f, Mathf.Sqrt(dx * dx + dy * dy + dz * dz)));
                                if (lod < 0) continue;
                                var l = proto.Lods[lod];
                                Grow(ref l.Bounds, l.Visible, c.Bounds);
                                l.Visible.Add(m);
                                if (main) { Drawn[Mathf.Min(lod, 3)]++; proto.Drawn[Mathf.Min(lod, 3)]++; }
                            }
                        }
                    }
                    if (shadowNear && proto.CastsShadows)
                    {
                        Grow(ref proto.ShadowBounds, proto.ShadowCasters, c.Bounds);
                        proto.ShadowCasters.AddRange(list);
                    }
                }
            }
            foreach (var proto in _protos)
            {
                for (int li = 0; li < proto.Lods.Length; li++)
                {
                    var l = proto.Lods[li];
                    if (l.Visible.Count > 0) Submit(cam, l.Mesh, l.Materials, l.Visible, l.Bounds, ShadowCastingMode.Off);
                }
                if (proto.ShadowCasters.Count > 0)
                {
                    // the coarsest mesh with a real silhouette: LOD1 (the impostor cards of a LOD2 would cast flat shadows)
                    var l = proto.Lods[Mathf.Min(1, proto.Lods.Length - 1)];
                    Submit(cam, l.Mesh, l.Materials, proto.ShadowCasters, proto.ShadowBounds, ShadowCastingMode.ShadowsOnly);
                }
            }
        }

        /// <summary>LOD index for a screen-relative height, -1 = culled (or above <see cref="MaxLod"/>).</summary>
        static int PickLod(Proto proto, float h)
        {
            for (int i = 0; i < proto.Heights.Length; i++)
                if (h >= proto.Heights[i] * LodScale) return i > MaxLod ? -1 : i;
            return -1;
        }

        static float MaxSqrDistance(Bounds b, Vector3 p)
        {
            float dx = Mathf.Max(Mathf.Abs(p.x - b.min.x), Mathf.Abs(p.x - b.max.x));
            float dy = Mathf.Max(Mathf.Abs(p.y - b.min.y), Mathf.Abs(p.y - b.max.y));
            float dz = Mathf.Max(Mathf.Abs(p.z - b.min.z), Mathf.Abs(p.z - b.max.z));
            return dx * dx + dy * dy + dz * dz;
        }

        void AddAll(Proto proto, int lod, List<Matrix4x4> list, Bounds bounds, bool main)
        {
            var l = proto.Lods[lod];
            Grow(ref l.Bounds, l.Visible, bounds);
            l.Visible.AddRange(list);
            if (main) { Drawn[Mathf.Min(lod, 3)] += list.Count; proto.Drawn[Mathf.Min(lod, 3)] += list.Count; }
        }

        void Submit(Camera cam, Mesh mesh, Material[] materials, List<Matrix4x4> instances, Bounds bounds, ShadowCastingMode shadows)
        {
            if (mesh == null || materials == null) return;
            var rp = new RenderParams
            {
                camera = cam, layer = gameObject.layer, renderingLayerMask = RenderingLayer, receiveShadows = true,
                shadowCastingMode = shadows, lightProbeUsage = LightProbeUsage.Off,
                reflectionProbeUsage = ReflectionProbeUsage.BlendProbes, motionVectorMode = MotionVectorGenerationMode.Camera,
                worldBounds = bounds,
            };
            for (int s = 0; s < mesh.subMeshCount && s < materials.Length; s++)
            {
                rp.material = materials[s];
                if (rp.material == null) continue;
                for (int start = 0; start < instances.Count; start += Batch)
                {
                    int n = Mathf.Min(Batch, instances.Count - start);
                    instances.CopyTo(start, _buffer, 0, n);
                    Graphics.RenderMeshInstanced(rp, mesh, s, _buffer, n);
                }
            }
        }
    }
}
