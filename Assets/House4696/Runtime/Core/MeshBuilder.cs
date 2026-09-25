using System.Collections.Generic;
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
        public Vector2 UvOffset = Vector2.zero;
        public Color VertexColor = Color.white;

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

        int AddVertex(Vector3 p, Vector3 n, Vector2 uv)
        {
            _v.Add(Transform.MultiplyPoint3x4(p));
            _n.Add(Transform.MultiplyVector(n).normalized);
            _uv.Add(uv + UvOffset);
            _c.Add(VertexColor);
            return _v.Count - 1;
        }

        /// <summary>Quad a-b-c-d given counter-clockwise when looking at its front (normal side).</summary>
        public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 n, Vector2 ua, Vector2 ub, Vector2 uc, Vector2 ud, Material m)
        {
            if (m == null) return;
            var t = _tris[Sub(m)];
            int ia = AddVertex(a, n, ua), ib = AddVertex(b, n, ub), ic = AddVertex(c, n, uc), id = AddVertex(d, n, ud);
            // Unity front faces are clockwise when viewed from the front.
            t.Add(ia); t.Add(id); t.Add(ic);
            t.Add(ia); t.Add(ic); t.Add(ib);
        }

        public void Triangle(Vector3 a, Vector3 b, Vector3 c, Vector3 na, Vector3 nb, Vector3 nc, Vector2 ua, Vector2 ub, Vector2 uc, Material m)
        {
            if (m == null) return;
            var t = _tris[Sub(m)];
            int ia = AddVertex(a, na, ua), ib = AddVertex(b, nb, ub), ic = AddVertex(c, nc, uc);
            t.Add(ia); t.Add(ib); t.Add(ic);
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
            for (int i = 0; i < idx.Length; i++) t.Add(baseIndex + idx[i]);
        }

        public Material[] Materials => _mats.ToArray();

        public Mesh Build(string name, bool tangents = true)
        {
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
    }
}
