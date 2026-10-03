using System.Collections.Generic;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Core
{
    /// <summary>Per-face material assignment for axis-aligned boxes (null = face is skipped).</summary>
    public struct BoxMats
    {
        public Material XNeg, XPos, YNeg, YPos, ZNeg, ZPos;

        public static BoxMats All(Material m) => new BoxMats { XNeg = m, XPos = m, YNeg = m, YPos = m, ZNeg = m, ZPos = m };

        public BoxMats With(Material xn = null, Material xp = null, Material yn = null, Material yp = null, Material zn = null, Material zp = null)
        {
            var b = this;
            if (xn != null) b.XNeg = xn; if (xp != null) b.XPos = xp;
            if (yn != null) b.YNeg = yn; if (yp != null) b.YPos = yp;
            if (zn != null) b.ZNeg = zn; if (zp != null) b.ZPos = zp;
            return b;
        }

        public BoxMats Without(bool xn = false, bool xp = false, bool yn = false, bool yp = false, bool zn = false, bool zp = false)
        {
            var b = this;
            if (xn) b.XNeg = null; if (xp) b.XPos = null;
            if (yn) b.YNeg = null; if (yp) b.YPos = null;
            if (zn) b.ZNeg = null; if (zp) b.ZPos = null;
            return b;
        }
    }

    /// <summary>
    /// Accumulates geometry into one multi-material mesh.
    /// Box faces get planar UVs in meters (world/local space) so tiling textures keep a constant scale
    /// across every element of the building.
    /// </summary>
    public sealed class MeshBuilder
    {
        readonly List<Vector3> _v = new List<Vector3>();
        readonly List<Vector3> _n = new List<Vector3>();
        readonly List<Vector2> _uv = new List<Vector2>();
        readonly List<Color> _c = new List<Color>();
        readonly List<List<int>> _tris = new List<List<int>>();
        readonly List<Material> _mats = new List<Material>();

        public Matrix4x4 Transform = Matrix4x4.identity;
        /// <summary>
        /// Reverse the winding of every triangle: set it when <see cref="Transform"/> mirrors (negative determinant), so
        /// front faces stay front faces (a left-hand door built from the right-hand design).
        /// </summary>
        public bool FlipWinding;
        public Vector2 UvOffset = Vector2.zero;
        public Color VertexColor = Color.white;

        /// <summary>
        /// Indexed emission for <see cref="Triangle"/>: a corner exactly equal (position, normal, uv, colour) to one of
        /// the last <see cref="WeldWindow"/> vertices reuses it instead of adding a vertex, so cards, strips and grid rows
        /// emitted corner by corner share their vertices (a quad becomes 4 vertices instead of 6). Grids can use
        /// <see cref="V"/> + <see cref="Tri"/> directly. Off by default: other builders keep one vertex per corner.
        /// </summary>
        public bool Weld;
        /// <summary>How many of the most recent vertices a welded corner is compared with.</summary>
        public const int WeldWindow = 8;
        /// <summary>
        /// Compact vertex layout in <see cref="Build"/>: position, normal and UV0 stay Float32 (UVs are in metres on bark and
        /// hedges, and the GPU probe baker's geometry pool reads normal / UV0 as float3 / float2), the tangent is Float16×4
        /// and only present when a material has a normal map, no vertex colour (URP/Lit ignores it): 32 or 40 bytes per
        /// vertex instead of 64. Off by default.
        /// </summary>
        public bool Compact;

        public int VertexCount => _v.Count;
        public bool IsEmpty => _v.Count == 0;

        int Sub(Material m)
        {
            int i = _mats.IndexOf(m);
            if (i >= 0) return i;
            _mats.Add(m);
            _tris.Add(new List<int>());
            return _mats.Count - 1;
        }

        int AddVertex(Vector3 p, Vector3 n, Vector2 uv) =>
            Push(Transform.MultiplyPoint3x4(p), Transform.MultiplyVector(n).normalized, uv + UvOffset);

        int Push(Vector3 p, Vector3 n, Vector2 uv)
        {
            // a zero normal (degenerate part) becomes NaN in the shader's normalize and blackens the whole frame through
            // bloom, TAA and the GI cache
            if (!(n.sqrMagnitude > 1e-6f)) n = Vector3.up;
            _v.Add(p);
            _n.Add(n);
            _uv.Add(uv);
            _c.Add(VertexColor);
            return _v.Count - 1;
        }

        /// <summary>A triangle corner: with <see cref="Weld"/> an identical recent vertex is reused.</summary>
        int Corner(Vector3 p, Vector3 n, Vector2 uv)
        {
            if (!Weld) return AddVertex(p, n, uv);
            Vector3 wp = Transform.MultiplyPoint3x4(p), wn = Transform.MultiplyVector(n).normalized;
            Vector2 wuv = uv + UvOffset;
            int stop = Mathf.Max(0, _v.Count - WeldWindow);
            for (int i = _v.Count - 1; i >= stop; i--)
                if (_v[i].Equals(wp) && _n[i].Equals(wn) && _uv[i].Equals(wuv) && _c[i].Equals(VertexColor)) return i;
            return Push(wp, wn, wuv);
        }

        /// <summary>Adds one vertex for indexed emission and returns its index (connect vertices with <see cref="Tri"/>).</summary>
        public int V(Vector3 p, Vector3 n, Vector2 uv) => AddVertex(p, n, uv);

        /// <summary>Triangle over vertices added with <see cref="V"/>; winding as in <see cref="Triangle"/>.</summary>
        public void Tri(int i0, int i1, int i2, Material m)
        {
            if (m == null) return;
            var t = _tris[Sub(m)];
            if (FlipWinding) { t.Add(i0); t.Add(i2); t.Add(i1); }
            else { t.Add(i0); t.Add(i1); t.Add(i2); }
        }

        /// <summary>Quad a-b-c-d given counter-clockwise when looking at its front (normal side).</summary>
        public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 n, Vector2 ua, Vector2 ub, Vector2 uc, Vector2 ud, Material m)
        {
            if (m == null) return;
            var t = _tris[Sub(m)];
            int ia = AddVertex(a, n, ua), ib = AddVertex(b, n, ub), ic = AddVertex(c, n, uc), id = AddVertex(d, n, ud);
            // Unity front faces are clockwise when viewed from the front.
            if (FlipWinding) { t.Add(ia); t.Add(ic); t.Add(id); t.Add(ia); t.Add(ib); t.Add(ic); }
            else { t.Add(ia); t.Add(id); t.Add(ic); t.Add(ia); t.Add(ic); t.Add(ib); }
        }

        public void Triangle(Vector3 a, Vector3 b, Vector3 c, Vector3 na, Vector3 nb, Vector3 nc, Vector2 ua, Vector2 ub, Vector2 uc, Material m)
        {
            if (m == null) return;
            var t = _tris[Sub(m)];
            int ia = Corner(a, na, ua), ib = Corner(b, nb, ub), ic = Corner(c, nc, uc);
            if (FlipWinding) { t.Add(ia); t.Add(ic); t.Add(ib); }
            else { t.Add(ia); t.Add(ib); t.Add(ic); }
        }

        /// <summary>Planar UV in meters for a point on a face with the given axis-aligned normal.</summary>
        public static Vector2 PlanarUV(Vector3 p, Vector3 n)
        {
            if (Mathf.Abs(n.x) > 0.5f) return new Vector2(n.x > 0 ? -p.z : p.z, p.y);
            if (Mathf.Abs(n.z) > 0.5f) return new Vector2(n.z > 0 ? -p.x : p.x, p.y);
            return n.y > 0 ? new Vector2(p.x, p.z) : new Vector2(p.x, -p.z);
        }

        void PlanarQuad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 n, Material m)
        {
            Quad(a, b, c, d, n, PlanarUV(a, n), PlanarUV(b, n), PlanarUV(c, n), PlanarUV(d, n), m);
        }

        public void Box(Vector3 min, Vector3 max, BoxMats mats)
        {
            float x0 = min.x, y0 = min.y, z0 = min.z, x1 = max.x, y1 = max.y, z1 = max.z;
            // -Z face (front, seen from -Z): counter-clockwise from viewer = x0->x1 bottom, then top
            PlanarQuad(new Vector3(x0, y0, z0), new Vector3(x1, y0, z0), new Vector3(x1, y1, z0), new Vector3(x0, y1, z0), Vector3.back, mats.ZNeg);
            PlanarQuad(new Vector3(x1, y0, z1), new Vector3(x0, y0, z1), new Vector3(x0, y1, z1), new Vector3(x1, y1, z1), Vector3.forward, mats.ZPos);
            PlanarQuad(new Vector3(x0, y0, z1), new Vector3(x0, y0, z0), new Vector3(x0, y1, z0), new Vector3(x0, y1, z1), Vector3.left, mats.XNeg);
            PlanarQuad(new Vector3(x1, y0, z0), new Vector3(x1, y0, z1), new Vector3(x1, y1, z1), new Vector3(x1, y1, z0), Vector3.right, mats.XPos);
            PlanarQuad(new Vector3(x0, y1, z0), new Vector3(x1, y1, z0), new Vector3(x1, y1, z1), new Vector3(x0, y1, z1), Vector3.up, mats.YPos);
            PlanarQuad(new Vector3(x0, y0, z1), new Vector3(x1, y0, z1), new Vector3(x1, y0, z0), new Vector3(x0, y0, z0), Vector3.down, mats.YNeg);
        }

        public void Box(Vector3 min, Vector3 max, Material m) => Box(min, max, BoxMats.All(m));

        /// <summary>
        /// Vertical slat (batten) on a wall with outward normal <paramref name="n"/>.
        /// (s, y, d) are wall coordinates: s along the wall (viewer's right), y up, d outward from the wall plane.
        /// u0..u1 selects a plank column of the wood atlas; v runs along the slat length in meters.
        /// </summary>
        public void Slat(Vector3 origin, Vector3 n, float s0, float s1, float y0, float y1, float d0, float d1,
                         Material m, float u0, float u1, float vOffset)
        {
            Vector3 a = Vector3.Cross(Vector3.up, -n).normalized;
            Vector3 P(float s, float y, float d) => origin + a * s + Vector3.up * y + n * d;
            float va = y0 + vOffset, vb = y1 + vOffset, us = (u1 - u0) * 0.35f;
            Quad(P(s0, y0, d1), P(s1, y0, d1), P(s1, y1, d1), P(s0, y1, d1), n,
                new Vector2(u0, va), new Vector2(u1, va), new Vector2(u1, vb), new Vector2(u0, vb), m);
            Quad(P(s0, y0, d0), P(s0, y0, d1), P(s0, y1, d1), P(s0, y1, d0), -a,
                new Vector2(u0, va), new Vector2(u0 + us, va), new Vector2(u0 + us, vb), new Vector2(u0, vb), m);
            Quad(P(s1, y0, d1), P(s1, y0, d0), P(s1, y1, d0), P(s1, y1, d1), a,
                new Vector2(u1 - us, va), new Vector2(u1, va), new Vector2(u1, vb), new Vector2(u1 - us, vb), m);
            Quad(P(s0, y1, d1), P(s1, y1, d1), P(s1, y1, d0), P(s0, y1, d0), Vector3.up,
                new Vector2(u0, vb), new Vector2(u1, vb), new Vector2(u1, vb + 0.02f), new Vector2(u0, vb + 0.02f), m);
            Quad(P(s0, y0, d0), P(s1, y0, d0), P(s1, y0, d1), P(s0, y0, d1), Vector3.down,
                new Vector2(u0, va), new Vector2(u1, va), new Vector2(u1, va + 0.02f), new Vector2(u0, va + 0.02f), m);
        }

        /// <summary>Generic quad from 4 corners (CCW seen from the front) with planar world UVs.</summary>
        public void PlanarFace(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 n, Material m) => PlanarQuad(a, b, c, d, n, m);

        /// <summary>Appends another mesh (all submeshes) with a transform, mapping every submesh to one material.</summary>
        public void AppendMesh(Mesh mesh, Matrix4x4 m, Material mat)
        {
            var verts = mesh.vertices; var norms = mesh.normals; var uvs = mesh.uv;
            var t = _tris[Sub(mat)];
            int baseIndex = _v.Count;
            var full = Transform * m;
            for (int i = 0; i < verts.Length; i++)
            {
                _v.Add(full.MultiplyPoint3x4(verts[i]));
                _n.Add(full.MultiplyVector(norms.Length > 0 ? norms[i] : Vector3.up).normalized);
                _uv.Add((uvs.Length > 0 ? uvs[i] : Vector2.zero) + UvOffset);
                _c.Add(VertexColor);
            }
            var idx = mesh.triangles;
            // FlipWinding compensates a mirroring builder Transform; a mirroring m needs its own flip
            bool flip = FlipWinding ^ (m.determinant < 0f);
            for (int i = 0; i + 2 < idx.Length; i += 3)
            {
                t.Add(baseIndex + idx[i]);
                t.Add(baseIndex + idx[flip ? i + 2 : i + 1]);
                t.Add(baseIndex + idx[flip ? i + 1 : i + 2]);
            }
        }

        public Material[] Materials => _mats.ToArray();

        public Mesh Build(string name, bool tangents = true)
        {
            if (Compact && _v.Count > 0)
            {
                var compact = BuildCompact(name, tangents);
                if (compact != null) return compact;
            }
            var mesh = new Mesh { name = name };
            if (_v.Count > 65000) mesh.indexFormat = IndexFormat.UInt32;
            mesh.SetVertices(_v);
            mesh.SetNormals(_n);
            mesh.SetUVs(0, _uv);
            mesh.SetColors(_c);
            mesh.subMeshCount = _tris.Count;
            for (int i = 0; i < _tris.Count; i++) mesh.SetTriangles(_tris[i], i, false);
            mesh.RecalculateBounds();
            if (tangents) mesh.RecalculateTangents();
            return mesh;
        }

        // ------------------------------------------------------------------ compact layout
        // Interleaved stream 0; Unity orders attributes Position, Normal, Tangent, Color, TexCoord0 inside a stream.
        [StructLayout(LayoutKind.Sequential)]
        struct VertexPNU { public Vector3 P, N; public Vector2 Uv; }                                       // 32 B

        [StructLayout(LayoutKind.Sequential)]
        struct VertexPNTU { public Vector3 P, N; public ushort Tx, Ty, Tz, Tw; public Vector2 Uv; }       // 40 B

        /// <summary>The <see cref="Compact"/> layout; null when the device cannot take Float16 tangents (the caller falls back to the classic layout).</summary>
        Mesh BuildCompact(string name, bool tangents)
        {
            bool withTangents = tangents && HasNormalMap();
            if (withTangents && !SystemInfo.SupportsVertexAttributeFormat(VertexAttributeFormat.Float16, 4)) return null;
            int count = _v.Count;
            var mesh = new Mesh { name = name };
            if (count > 65000) mesh.indexFormat = IndexFormat.UInt32;
            if (withTangents)
            {
                mesh.SetVertexBufferParams(count,
                    new VertexAttributeDescriptor(VertexAttribute.Position, VertexAttributeFormat.Float32, 3),
                    new VertexAttributeDescriptor(VertexAttribute.Normal, VertexAttributeFormat.Float32, 3),
                    new VertexAttributeDescriptor(VertexAttribute.Tangent, VertexAttributeFormat.Float16, 4),
                    new VertexAttributeDescriptor(VertexAttribute.TexCoord0, VertexAttributeFormat.Float32, 2));
                var tan = Tangents();
                var data = new VertexPNTU[count];
                for (int i = 0; i < count; i++)
                {
                    var t = tan[i];
                    data[i] = new VertexPNTU
                    {
                        P = _v[i], N = _n[i], Uv = _uv[i],
                        Tx = Mathf.FloatToHalf(t.x), Ty = Mathf.FloatToHalf(t.y), Tz = Mathf.FloatToHalf(t.z), Tw = Mathf.FloatToHalf(t.w),
                    };
                }
                mesh.SetVertexBufferData(data, 0, 0, count, 0, MeshUpdateFlags.Default);
            }
            else
            {
                mesh.SetVertexBufferParams(count,
                    new VertexAttributeDescriptor(VertexAttribute.Position, VertexAttributeFormat.Float32, 3),
                    new VertexAttributeDescriptor(VertexAttribute.Normal, VertexAttributeFormat.Float32, 3),
                    new VertexAttributeDescriptor(VertexAttribute.TexCoord0, VertexAttributeFormat.Float32, 2));
                var data = new VertexPNU[count];
                for (int i = 0; i < count; i++) data[i] = new VertexPNU { P = _v[i], N = _n[i], Uv = _uv[i] };
                mesh.SetVertexBufferData(data, 0, 0, count, 0, MeshUpdateFlags.Default);
            }
            mesh.subMeshCount = _tris.Count;
            for (int i = 0; i < _tris.Count; i++) mesh.SetTriangles(_tris[i], i, false);
            mesh.RecalculateBounds();
            return mesh;
        }

        bool HasNormalMap()
        {
            foreach (var m in _mats)
                if (m != null && (m.IsKeywordEnabled("_NORMALMAP") || (m.HasProperty("_BumpMap") && m.GetTexture("_BumpMap") != null)))
                    return true;
            return false;
        }

        /// <summary>
        /// Per-vertex tangents from positions, normals and UV0 (accumulated over the triangles that share a vertex,
        /// orthogonalised to the normal, w = bitangent sign) — the same construction as Mesh.RecalculateTangents, which
        /// cannot be used here because it rewrites the layout to Float32.
        /// </summary>
        Vector4[] Tangents()
        {
            int count = _v.Count;
            var sdir = new Vector3[count];
            var tdir = new Vector3[count];
            foreach (var t in _tris)
                for (int k = 0; k + 2 < t.Count; k += 3)
                {
                    int i0 = t[k], i1 = t[k + 1], i2 = t[k + 2];
                    Vector3 e1 = _v[i1] - _v[i0], e2 = _v[i2] - _v[i0];
                    Vector2 d1 = _uv[i1] - _uv[i0], d2 = _uv[i2] - _uv[i0];
                    float det = d1.x * d2.y - d2.x * d1.y;
                    if (Mathf.Abs(det) < 1e-12f) continue;
                    float r = 1f / det;
                    Vector3 s = (e1 * d2.y - e2 * d1.y) * r;
                    Vector3 u = (e2 * d1.x - e1 * d2.x) * r;
                    sdir[i0] += s; sdir[i1] += s; sdir[i2] += s;
                    tdir[i0] += u; tdir[i1] += u; tdir[i2] += u;
                }
            var result = new Vector4[count];
            for (int i = 0; i < count; i++)
            {
                Vector3 n = _n[i], s = sdir[i];
                Vector3 o = s - n * Vector3.Dot(n, s);
                if (o.sqrMagnitude < 1e-20f)
                {
                    // no usable UV gradient: any unit vector perpendicular to the normal
                    o = Vector3.Cross(n, Mathf.Abs(n.y) < 0.99f ? Vector3.up : Vector3.right);
                    if (o.sqrMagnitude < 1e-20f) o = Vector3.right;
                }
                o.Normalize();
                float w = Vector3.Dot(Vector3.Cross(n, s), tdir[i]) < 0f ? -1f : 1f;
                result[i] = new Vector4(o.x, o.y, o.z, w);
            }
            return result;
        }
    }
}
