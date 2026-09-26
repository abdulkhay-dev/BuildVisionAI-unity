using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// A built catalogue item with its real extent: the bounds of everything it rendered, in the item's own frame
    /// (front faces -Z, floor at y = 0), and the placement. Items only turn about the vertical, so the plan footprint is
    /// an oriented rectangle and the height range is the local one shifted by the placement.
    /// </summary>
    public sealed class ItemBox
    {
        public ItemDef Def;
        public string Model, Category;
        /// <summary>The built object ("Item_…"): its transform places the item, its meshes are what it renders.</summary>
        public GameObject Object;
        /// <summary>Everything the item renders (canopies, throws, lamp shades included) — its visual size.</summary>
        public Bounds Local;
        /// <summary>The solid body only (furniture meshes and library models, no soft decor or foliage) — what collides with walls and doorways.</summary>
        public Bounds Solid;
        /// <summary>Plan cells (<see cref="Cell"/> m, world grid) the solid body covers: its real footprint, not a bounding box.</summary>
        public HashSet<long> Cells;
        public const float Cell = 0.1f;
        public Vector3 Position;
        public float Yaw;
        public float FloorY;

        public string Id => Def.Id ?? Model;
        public float Y0 => Position.y + Solid.min.y;
        public float Y1 => Position.y + Solid.max.y;
        /// <summary>Width across the front (local X) × depth front-to-back (local Z) × height.</summary>
        public Vector3 Size => Local.size;

        public static ItemBox Of(ItemDef def, ItemModel model, GameObject go, float floorY)
        {
            var solid = SolidFilters(go);
            var b = new ItemBox
            {
                Def = def, Model = model.Id, Category = model.Category, Local = LocalBounds(go, null), Object = go,
                Position = go.transform.position, Yaw = go.transform.eulerAngles.y, FloorY = floorY,
            };
            b.Solid = solid.Count > 0 ? LocalBounds(go, solid) : b.Local;
            if (model.Category == "plants" && solid.Count == 0)
            {
                // foliage spreads freely (and brushes walls in real rooms); what stands on the floor is the pot and trunk
                var sz = b.Solid.size;
                b.Solid = new Bounds(new Vector3(b.Solid.center.x, b.Solid.center.y, b.Solid.center.z), new Vector3(sz.x * 0.4f, sz.y, sz.z * 0.4f));
                var fp = b.Footprint();
                var r = Polygon.Bounds(fp);
                b.Cells = new HashSet<long>();
                for (float x = r.xMin; x <= r.xMax; x += Cell * 0.5f)
                for (float z = r.yMin; z <= r.yMax; z += Cell * 0.5f)
                    if (Polygon.Contains(fp, new Vector2(x, z))) b.Cells.Add(Key(x, z));
            }
            b.Cells = Rasterize(solid.Count > 0 ? solid : new List<MeshFilter>(go.GetComponentsInChildren<MeshFilter>(true)));
            return b;
        }

        /// <summary>Meshes of the solid body: generated furniture ("Furniture_…") and library models ("Model_…", except plants and fittings).</summary>
        static List<MeshFilter> SolidFilters(GameObject go)
        {
            var list = new List<MeshFilter>();
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
            {
                for (var t = mf.transform; t != null && t != go.transform; t = t.parent)
                    if (t.name.StartsWith("Furniture_") || t.name.StartsWith("Model_")) { list.Add(mf); break; }
            }
            return list;
        }

        /// <summary>World plan cells touched by the triangles of the meshes (vertices, edges every 5 cm, faces on a 5 cm lattice).</summary>
        static HashSet<long> Rasterize(List<MeshFilter> filters)
        {
            var cells = new HashSet<long>();
            const float step = Cell * 0.5f;
            void Mark(Vector3 p) => cells.Add(Key(p.x, p.z));
            foreach (var mf in filters)
            {
                var mesh = mf.sharedMesh;
                if (mesh == null || !mesh.isReadable) continue;
                var m = mf.transform.localToWorldMatrix;
                var v = mesh.vertices;
                var w = new Vector3[v.Length];
                for (int i = 0; i < v.Length; i++) { w[i] = m.MultiplyPoint3x4(v[i]); Mark(w[i]); }
                var tris = mesh.triangles;
                for (int t = 0; t + 2 < tris.Length; t += 3)
                {
                    Vector3 a = w[tris[t]], b = w[tris[t + 1]], c = w[tris[t + 2]];
                    float ab = Plan(a, b), bc = Plan(b, c), ca = Plan(c, a);
                    // edges
                    foreach (var e in new[] { (a, b, ab), (b, c, bc), (c, a, ca) })
                    {
                        int n = Mathf.CeilToInt(e.Item3 / step);
                        for (int k = 1; k < n; k++) Mark(Vector3.Lerp(e.Item1, e.Item2, k / (float)n));
                    }
                    // faces with a plan area (tops of boxes, seats): a lattice of barycentric samples
                    float area = Mathf.Abs((b.x - a.x) * (c.z - a.z) - (c.x - a.x) * (b.z - a.z)) * 0.5f;
                    if (area < step * step) continue;
                    int nu = Mathf.CeilToInt(Mathf.Max(ab, ca) / step);
                    for (int i = 1; i < nu; i++)
                    for (int j = 1; i + j < nu; j++)
                        Mark(a + (b - a) * (i / (float)nu) + (c - a) * (j / (float)nu));
                }
            }
            return cells;
        }

        static float Plan(Vector3 a, Vector3 b) => new Vector2(b.x - a.x, b.z - a.z).magnitude;

        public static long Key(float x, float z) =>
            ((long)Mathf.FloorToInt(x / Cell) << 32) ^ (uint)Mathf.FloorToInt(z / Cell);

        /// <summary>Plan area (m²) both items cover.</summary>
        public float SharedArea(ItemBox o)
        {
            if (Cells == null || o.Cells == null) return 0f;
            var small = Cells.Count <= o.Cells.Count ? Cells : o.Cells;
            var big = small == Cells ? o.Cells : Cells;
            int n = 0;
            foreach (var k in small) if (big.Contains(k)) n++;
            return n * Cell * Cell;
        }

        public float CellArea => Cells == null ? 0f : Cells.Count * Cell * Cell;

        HashSet<long> _core;

        /// <summary>
        /// Cells whose four neighbours are covered too: the body without its 10 cm rim. Thin things (wall panels, a
        /// headboard, a nightstand's back touching it) have no core, so they never "collide" by a sliver.
        /// </summary>
        public HashSet<long> Core
        {
            get
            {
                if (_core != null || Cells == null) return _core;
                _core = new HashSet<long>();
                foreach (var k in Cells)
                {
                    long x = k >> 32, z = (int)(uint)(k & 0xffffffffL);
                    if (Cells.Contains(K(x + 1, z)) && Cells.Contains(K(x - 1, z)) && Cells.Contains(K(x, z + 1)) && Cells.Contains(K(x, z - 1))) _core.Add(k);
                }
                return _core;
            }
        }

        static long K(long x, long z) => (x << 32) ^ (uint)(int)z;

        /// <summary>Plan area (m²) of the cores both items share.</summary>
        public float SharedCore(ItemBox o)
        {
            var a = Core; var b = o.Core;
            if (a == null || b == null) return 0f;
            var small = a.Count <= b.Count ? a : b;
            var big = small == a ? b : a;
            int n = 0;
            foreach (var k in small) if (big.Contains(k)) n++;
            return n * Cell * Cell;
        }

        public float CoreArea => Core == null ? 0f : Core.Count * Cell * Cell;

        /// <summary>Number of covered cells whose centres fall inside a convex counter-clockwise plan polygon.</summary>
        public int CellsIn(IList<Vector2> poly)
        {
            if (Cells == null) return 0;
            int n = 0;
            foreach (var k in Cells)
            {
                long x = k >> 32, z = (int)(uint)(k & 0xffffffffL);
                if (Polygon.Contains(poly, new Vector2((x + 0.5f) * Cell, (z + 0.5f) * Cell))) n++;
            }
            return n;
        }

        /// <summary>Plan corners of the footprint (world x, z), counter-clockwise, optionally shrunk by <paramref name="inset"/>.</summary>
        public Vector2[] Footprint(float inset = 0f)
        {
            var rot = Quaternion.Euler(0, Yaw, 0);
            float x0 = Solid.min.x + inset, x1 = Solid.max.x - inset, z0 = Solid.min.z + inset, z1 = Solid.max.z - inset;
            if (x1 < x0) x0 = x1 = Solid.center.x;
            if (z1 < z0) z0 = z1 = Solid.center.z;
            Vector2 W(float x, float z) { var p = Position + rot * new Vector3(x, 0, z); return new Vector2(p.x, p.z); }
            var c = new[] { W(x0, z0), W(x1, z0), W(x1, z1), W(x0, z1) };
            return Polygon.SignedArea(c) < 0 ? new[] { c[3], c[2], c[1], c[0] } : c;
        }

        public Vector2 PlanCenter
        {
            get { var p = Position + Quaternion.Euler(0, Yaw, 0) * Solid.center; return new Vector2(p.x, p.z); }
        }

        public float PlanArea => Mathf.Max(1e-4f, Solid.size.x * Solid.size.z);

        /// <summary>Bounds of all meshes under <paramref name="root"/>, in its local frame (empty object → zero box at the origin).</summary>
        public static Bounds LocalBounds(GameObject root, List<MeshFilter> only = null)
        {
            var toLocal = root.transform.worldToLocalMatrix;
            bool any = false;
            var b = new Bounds();
            foreach (var mf in only ?? new List<MeshFilter>(root.GetComponentsInChildren<MeshFilter>(true)))
            {
                var mesh = mf.sharedMesh;
                if (mesh == null) continue;
                var mb = mesh.bounds;
                var m = toLocal * mf.transform.localToWorldMatrix;
                for (int i = 0; i < 8; i++)
                {
                    var corner = mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = m.MultiplyPoint3x4(corner);
                    if (!any) { b = new Bounds(p, Vector3.zero); any = true; }
                    else b.Encapsulate(p);
                }
            }
            return b;
        }
    }
}
