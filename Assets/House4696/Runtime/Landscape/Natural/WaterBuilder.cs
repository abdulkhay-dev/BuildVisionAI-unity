using House4696.Core;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// Stream water (port of tools/landscape/garden/water.py): a level ribbon per pool slightly wider than the channel
    /// so it meets the banks, and per cascade a curved sheet for every tongue pouring between the lip stones.
    /// UVs: u across (0..1), v along the flow in metres / 4 (the stream shaders scroll along v).
    /// </summary>
    public sealed class WaterBuilder
    {
        readonly SiteModel _m;
        readonly LandscapeKit _kit;
        readonly SceneWriter _w;

        public WaterBuilder(SiteModel m, LandscapeKit kit, SceneWriter w) { _m = m; _kit = kit; _w = w; }

        public void Build(Transform parent)
        {
            if (_m.Streams.Count == 0 || _kit.WaterMaterial == null) return;
            var g = _w.Group("Water", parent);
            // per-site copies: the flow scrolls their texture offset
            var flow = g.gameObject.AddComponent<WaterFlow>();
            flow.Pools = new Material(_kit.WaterMaterial) { name = _kit.WaterMaterial.name };
            flow.Falls = new Material(_kit.FallsMaterial != null ? _kit.FallsMaterial : _kit.WaterMaterial) { name = "M_StreamFalls" };
            int si = 0;
            foreach (var st in _m.Streams)
            {
                int k = 0;
                foreach (var pool in st.Pools) Emit($"Water_Pool_{si}_{k++}", g, Pool(st, pool), flow.Pools);
                k = 0;
                foreach (var c in st.Cascades) Emit($"Water_Fall_{si}_{k++}", g, Fall(st, c), flow.Falls);
                si++;
            }
        }

        void Emit(string name, Transform parent, Mesh mesh, Material mat)
        {
            var go = _w.Instance(name, parent, _w.Store(mesh), new[] { mat }, castShadows: false);
            var r = go.GetComponent<MeshRenderer>();
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = true;
        }

        static Mesh Pool(SiteModel.Stream st, SiteModel.Pool pool)
        {
            const int across = 10;
            int steps = Mathf.Max(2, Mathf.CeilToInt((pool.S1 - pool.S0) / 0.25f));
            var verts = new Vector3[(steps + 1) * (across + 1)];
            var uvs = new Vector2[verts.Length];
            var tris = new int[steps * across * 6];
            for (int i = 0; i <= steps; i++)
            {
                float s = Mathf.Lerp(pool.S0, pool.S1, i / (float)steps);
                var p = st.Line.At(s, out var t);
                var n = new Vector2(-t.y, t.x);
                float hw = st.HalfWidth(s) + 0.45f;
                for (int j = 0; j <= across; j++)
                {
                    float u = -1f + 2f * j / across;
                    var q = p + n * hw * u;
                    verts[i * (across + 1) + j] = new Vector3(q.x, pool.Level, q.y);
                    uvs[i * (across + 1) + j] = new Vector2(j / (float)across, s * 0.25f);
                }
            }
            int ti = 0;
            for (int i = 0; i < steps; i++)
            for (int j = 0; j < across; j++)
            {
                int a = i * (across + 1) + j;
                // cross(n, t) points up: the surface faces the sky (n is to the left of the flow)
                tris[ti++] = a; tris[ti++] = a + 1; tris[ti++] = a + across + 1;
                tris[ti++] = a + 1; tris[ti++] = a + across + 2; tris[ti++] = a + across + 1;
            }
            return Finish("WaterPool", verts, uvs, tris);
        }

        static Mesh Fall(SiteModel.Stream st, SiteModel.Cascade c)
        {
            const int rows = 12, across = 6;
            var p0 = st.Line.At(c.S, out var t);
            var n = new Vector2(-t.y, t.x);
            float drop = c.Top - c.Bottom;
            float hwLip = st.HalfWidth(c.S);
            float run = 0.2f + drop * 0.4f;
            int per = (rows + 1) * (across + 1);
            var verts = new Vector3[per * c.Tongues.Count];
            var uvs = new Vector2[verts.Length];
            var tris = new int[rows * across * 6 * c.Tongues.Count];
            int ti = 0;
            for (int k = 0; k < c.Tongues.Count; k++)
            {
                var tg = c.Tongues[k];
                var p = p0 + n * hwLip * tg.x;
                float hw = hwLip * tg.y;
                int b = k * per;
                for (int i = 0; i <= rows; i++)
                {
                    float v = i / (float)rows;
                    float fwd = run * v - 0.1f;
                    float y = c.Top + 0.01f - drop * Mathf.Pow(v, 1.7f);
                    for (int j = 0; j <= across; j++)
                    {
                        float u = -1f + 2f * j / across;
                        var q = p + t * fwd + n * hw * u * (1f + 0.5f * v);
                        verts[b + i * (across + 1) + j] = new Vector3(q.x, y, q.y);
                        uvs[b + i * (across + 1) + j] = new Vector2(j / (float)across + k * 0.37f, v * (drop + run) * 0.8f);
                    }
                }
                for (int i = 0; i < rows; i++)
                for (int j = 0; j < across; j++)
                {
                    int a = b + i * (across + 1) + j;
                    tris[ti++] = a; tris[ti++] = a + 1; tris[ti++] = a + across + 1;
                    tris[ti++] = a + 1; tris[ti++] = a + across + 2; tris[ti++] = a + across + 1;
                }
            }
            return Finish("WaterFall", verts, uvs, tris);
        }

        static Mesh Finish(string name, Vector3[] verts, Vector2[] uvs, int[] tris)
        {
            var m = new Mesh { name = name, indexFormat = verts.Length > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
            m.vertices = verts;
            m.uv = uvs;
            m.triangles = tris;
            m.RecalculateNormals();
            m.RecalculateTangents();
            m.RecalculateBounds();
            return m;
        }
    }
}
