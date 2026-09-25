using House4696.Core;
using House4696.Runtime;
using UnityEngine;
using static House4696.House.HouseSpec;

namespace House4696.House
{
    /// <summary>
    /// Builds the complete house (walls, openings, belts, canopies, parapets, terraces, railings,
    /// furnished interior and balcony furniture) under one root object.
    /// </summary>
    public sealed class HouseGenerator
    {
        readonly MaterialLibrary _m;
        readonly SceneWriter _w;

        public HouseGenerator(MaterialLibrary m, SceneWriter w) { _m = m; _w = w; }

        public GameObject Build()
        {
            var root = new GameObject("House_46-96");
            var facade = new FacadeBuilder(_m);

            var walls = _w.Group("Walls", root.transform);
            var openings = _w.Group("Windows & Doors", root.transform);
            var glassGroup = _w.Group("Glass", root.transform);
            var curtainGroup = _w.Group("Curtains", root.transform);
            var doorGroup = _w.Group("Doors", root.transform);

            foreach (var w in Walls())
            {
                var core = new MeshBuilder();
                var slats = new MeshBuilder();
                facade.BuildWall(w, core, slats);
                var wallGo = _w.Emit("Wall_" + w.Name, walls, core);
                if (!slats.IsEmpty) _w.Emit("Battens_" + w.Name, wallGo != null ? wallGo.transform : walls, slats);

                var frames = new MeshBuilder();
                var glass = new MeshBuilder();
                var curtains = new MeshBuilder();
                foreach (var o in w.Openings)
                {
                    var leaf = new MeshBuilder();
                    facade.BuildOpening(w, o, frames, glass, curtains, leaf);
                    if (!leaf.IsEmpty) BuildDoor("Door_" + w.Name, doorGroup, w, o, leaf);
                }
                _w.Emit("Frames_" + w.Name, openings, frames);
                _w.Emit("Glass_" + w.Name, glassGroup, glass, castShadows: false);
                _w.Emit("Curtains_" + w.Name, curtainGroup, curtains, castShadows: false);
            }

            BuildBand(root.transform);
            BuildRoof(root.transform);
            BuildColumnsAndPlatforms(root.transform);
            BuildRailings(root.transform);
            new Interior.InteriorBuilder(_m, _w).Build(root.transform);
            BuildBalconyFurniture(root.transform);
            return root;
        }

        // ------------------------------------------------------------------ openable door leaves
        /// <summary>
        /// Door leaf on a pivot at its hinge: the leaf mesh keeps world-space vertices, so the child is offset
        /// by -hinge. The leaf moves at runtime, so it is not static and gets a kinematic body for its collider.
        /// </summary>
        void BuildDoor(string name, Transform parent, WallSpec w, Opening o, MeshBuilder leaf)
        {
            FacadeBuilder.DoorHinge(w, o, out var hinge, out var inward);
            var pivot = new GameObject(name);
            pivot.transform.SetParent(parent, false);
            pivot.transform.position = hinge;

            var leafGo = _w.Emit("Leaf", pivot.transform, leaf);
            leafGo.transform.localPosition = -hinge;
            _w.MarkDynamic(leafGo);

            // swing into the house: the leaf extends from the hinge along the wall axis
            float angle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * w.Axis, inward) > 0 ? 95f : -95f;
            pivot.AddComponent<Door>().OpenAngle = angle;
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
        }

        // ------------------------------------------------------------------ inter-floor belt & balcony slabs
        void BuildBand(Transform parent)
        {
            const float o = 0.07f; // projection past the structural face (clears cladding)
            float y0 = BandBottom, y1 = BandTop;
            var mb = new MeshBuilder();
            var cop = new MeshBuilder();
            var boxes = new (float x0, float x1, float z0, float z1)[]
            {
                (-o, FinLeftX0, -o, LeftFrontZ + WallThickness),       // left balcony slab (stops at the fin; interior beam fills the rest)
                (FinRightX1, Width + o, -o, RightFrontZ + WallThickness), // right balcony slab
                (-o, WallThickness, LeftFrontZ, BackZ + o),            // left side belt
                (Width - WallThickness, Width + o, RightFrontZ, BackZ + o), // right side belt
                (-o, BumpX0, BackZ - WallThickness, BackZ + o),        // rear belt, left block
                (BumpX1, Width + o, BackZ - WallThickness, BackZ + o), // rear belt, right block
                (BumpX0 - o, 4.79f, BackZ, BumpBackZ + o),             // bay: left side
                (9.35f, BumpX1 + o, BackZ, BumpBackZ + o),             // bay: right side (right of stair window)
                (BumpX0 - o, 7.09f, BumpBackZ - WallThickness, BumpBackZ + o), // bay rear, left of stair window
            };
            foreach (var b in boxes)
            {
                mb.Box(new Vector3(b.x0, y0, b.z0), new Vector3(b.x1, y1, b.z1), BoxMats.All(_m.Stucco).With(yn: _m.Soffit).Without(yp: true));
                cop.Box(new Vector3(b.x0 - 0.012f, y1, b.z0 - 0.012f), new Vector3(b.x1 + 0.012f, y1 + 0.035f, b.z1 + 0.012f), BoxMats.All(_m.Coping));
            }
            // balcony decking (inset porcelain on the slabs)
            cop.Box(new Vector3(0.1f, y1 + 0.035f, 0.1f), new Vector3(FinLeftX0, y1 + 0.05f, LeftFrontZ), BoxMats.All(_m.Porcelain).Without(yn: true));
            cop.Box(new Vector3(FinRightX1, y1 + 0.035f, 0.1f), new Vector3(Width - 0.1f, y1 + 0.05f, RightFrontZ), BoxMats.All(_m.Porcelain).Without(yn: true));
            _w.Emit("Belt", parent, mb);
            _w.Emit("Belt_Coping", parent, cop);
        }

        // ------------------------------------------------------------------ canopies & parapets
        void BuildRoof(Transform parent)
        {
            var roof = _w.Group("Roof", parent);
            var mb = new MeshBuilder();
            var cop = new MeshBuilder();
            foreach (var c in Canopies)
            {
                mb.Box(new Vector3(c.x0, SoffitY, c.z0), new Vector3(c.x1, CanopyTop, c.z1), BoxMats.All(_m.Stucco).With(yn: _m.Soffit).Without(yp: true));
                cop.Box(new Vector3(c.x0 - 0.02f, CanopyTop, c.z0 - 0.02f), new Vector3(c.x1 + 0.02f, CanopyTop + CanopyCoping, c.z1 + 0.02f),
                    BoxMats.All(_m.Coping).Without(yn: true));
            }
            _w.Emit("Canopies", roof, mb);
            _w.Emit("Canopy_Coping", roof, cop);

            var par = new MeshBuilder();
            var pcop = new MeshBuilder();
            foreach (var p in Parapets)
            {
                par.Box(new Vector3(p.x0, CanopyTop, p.z0), new Vector3(p.x1, ParapetTop, p.z1), BoxMats.All(_m.Stucco).Without(yp: true, yn: true));
                pcop.Box(new Vector3(p.x0 - 0.025f, ParapetTop, p.z0 - 0.025f), new Vector3(p.x1 + 0.025f, ParapetTop + 0.03f, p.z1 + 0.025f),
                    BoxMats.All(_m.Coping).Without(yn: true));
            }
            _w.Emit("Parapets", roof, par);
            _w.Emit("Parapet_Coping", roof, pcop);
        }

        // ------------------------------------------------------------------ columns, terrace, porch, steps
        void BuildColumnsAndPlatforms(Transform parent)
        {
            var mb = new MeshBuilder();
            foreach (var c in Columns)
                mb.Box(new Vector3(c.x0 - 0.02f, FloorY, c.z0 - 0.02f), new Vector3(c.x1 + 0.02f, BandBottom, c.z1 + 0.02f),
                    BoxMats.All(_m.Stone).Without(yp: true, yn: true));
            _w.Emit("Columns", parent, mb);

            var plat = new MeshBuilder();
            void Platform(float x0, float x1, float zFront, float zBack)
            {
                var top = BoxMats.All(_m.StepRiser).With(yp: _m.Porcelain).Without(yn: true);
                plat.Box(new Vector3(x0, 0f, zFront), new Vector3(x1, FloorY, zBack), top);
                plat.Box(new Vector3(x0, 0f, zFront - 0.42f), new Vector3(x1, StepY, zFront), top);
            }
            Platform(-0.03f, FinLeftX0, -0.05f, LeftFrontZ);
            Platform(FinRightX1, Width + 0.03f, -0.05f, RightFrontZ);
            _w.Emit("Terrace_Porch_Steps", parent, plat);
        }

        // ------------------------------------------------------------------ frameless glass balustrades
        void BuildRailings(Transform parent)
        {
            var glass = new MeshBuilder();
            var metal = new MeshBuilder();
            const float gy0 = BandTop + 0.04f, gy1 = 5.0f, gt = 0.012f, zf = 0.012f;

            void Run(Vector3 a, Vector3 b)
            {
                Vector3 d = b - a; float len = d.magnitude; d /= len;
                bool alongX = Mathf.Abs(d.x) > 0.5f;
                int panels = Mathf.Max(1, Mathf.RoundToInt(len / 1.15f));
                for (int i = 0; i < panels; i++)
                {
                    Vector3 p0 = a + d * (len * i / panels + 0.005f), p1 = a + d * (len * (i + 1) / panels - 0.005f);
                    Vector3 mn = Vector3.Min(p0, p1), mx = Vector3.Max(p0, p1);
                    if (alongX) { mn.z -= gt * 0.5f; mx.z += gt * 0.5f; } else { mn.x -= gt * 0.5f; mx.x += gt * 0.5f; }
                    mn.y = gy0; mx.y = gy1;
                    glass.Box(mn, mx, BoxMats.All(_m.GlassRailing));
                }
                Vector3 cmn = Vector3.Min(a, b), cmx = Vector3.Max(a, b);
                Vector3 pad = alongX ? new Vector3(0.012f, 0, 0.022f) : new Vector3(0.022f, 0, 0.012f);
                // top cap and base shoe
                metal.Box(new Vector3(cmn.x - pad.x, gy1 - 0.01f, cmn.z - pad.z), new Vector3(cmx.x + pad.x, gy1 + 0.03f, cmx.z + pad.z), BoxMats.All(_m.Frame));
                metal.Box(new Vector3(cmn.x - pad.x * 1.5f, BandTop, cmn.z - pad.z * 1.6f), new Vector3(cmx.x + pad.x * 1.5f, gy0 + 0.02f, cmx.z + pad.z * 1.6f), BoxMats.All(_m.Frame));
            }
            // left balcony: front and return along the left edge
            Run(new Vector3(0.03f, 0, zf), new Vector3(FinLeftX0, 0, zf));
            Run(new Vector3(0.03f, 0, zf), new Vector3(0.03f, 0, LeftFrontZ));
            // right balcony
            Run(new Vector3(FinRightX1, 0, zf), new Vector3(Width - 0.03f, 0, zf));
            Run(new Vector3(Width - 0.03f, 0, zf), new Vector3(Width - 0.03f, 0, RightFrontZ));
            _w.Emit("Railing_Glass", parent, glass, castShadows: false);
            _w.Emit("Railing_Profiles", parent, metal);
        }

        // ------------------------------------------------------------------ left balcony furniture (visible in the reference)
        void BuildBalconyFurniture(Transform parent)
        {
            var mb = new MeshBuilder();
            float y = BandTop + 0.05f;
            // rattan lounge chair
            Vector3 c = new Vector3(0.62f, y, 1.25f);
            mb.Box(c + new Vector3(-0.36f, 0, -0.36f), c + new Vector3(0.36f, 0.42f, 0.36f), BoxMats.All(_m.Rattan));
            mb.Box(c + new Vector3(-0.36f, 0.42f, 0.22f), c + new Vector3(0.36f, 0.86f, 0.36f), BoxMats.All(_m.Rattan));
            mb.Box(c + new Vector3(-0.36f, 0.42f, -0.36f), c + new Vector3(-0.26f, 0.64f, 0.36f), BoxMats.All(_m.Rattan));
            mb.Box(c + new Vector3(0.26f, 0.42f, -0.36f), c + new Vector3(0.36f, 0.64f, 0.36f), BoxMats.All(_m.Rattan));
            mb.Box(c + new Vector3(-0.26f, 0.42f, -0.3f), c + new Vector3(0.26f, 0.52f, 0.22f), BoxMats.All(_m.Cushion));
            // round table + two dark dining chairs
            Vector3 t = new Vector3(2.45f, y, 1.25f);
            mb.Box(t + new Vector3(-0.04f, 0, -0.04f), t + new Vector3(0.04f, 0.72f, 0.04f), BoxMats.All(_m.FurnitureDark));
            Cylinder(mb, t + new Vector3(0, 0.72f, 0), 0.45f, 0.03f, 20, _m.FurnitureDark);
            foreach (float dx in new[] { -0.75f, 0.75f })
            {
                Vector3 ch = t + new Vector3(dx, 0, -0.1f);
                mb.Box(ch + new Vector3(-0.23f, 0.44f, -0.23f), ch + new Vector3(0.23f, 0.5f, 0.23f), BoxMats.All(_m.FurnitureDark));
                float back = dx < 0 ? -0.23f : 0.19f;
                mb.Box(ch + new Vector3(back, 0.5f, -0.23f), ch + new Vector3(back + 0.04f, 0.92f, 0.23f), BoxMats.All(_m.FurnitureDark));
                foreach (var lx in new[] { -0.2f, 0.18f })
                foreach (var lz in new[] { -0.2f, 0.18f })
                    mb.Box(ch + new Vector3(lx, 0, lz), ch + new Vector3(lx + 0.025f, 0.44f, lz + 0.025f), BoxMats.All(_m.FurnitureDark));
            }
            _w.Emit("Balcony_Furniture", parent, mb);
        }

        public static void Cylinder(MeshBuilder mb, Vector3 baseCenter, float r, float h, int sides, Material m, bool caps = true)
        {
            for (int i = 0; i < sides; i++)
            {
                float a0 = i * Mathf.PI * 2 / sides, a1 = (i + 1) * Mathf.PI * 2 / sides;
                Vector3 d0 = new Vector3(Mathf.Cos(a0), 0, Mathf.Sin(a0)), d1 = new Vector3(Mathf.Cos(a1), 0, Mathf.Sin(a1));
                Vector3 p0 = baseCenter + d0 * r, p1 = baseCenter + d1 * r;
                Vector3 up = Vector3.up * h;
                float u0 = a0 * r, u1 = a1 * r;
                // seen from outside p0 is on the left and p1 on the right: clockwise = p0, p0+up, p1+up
                mb.Triangle(p0, p0 + up, p1 + up, d0, d0, d1, new Vector2(u0, 0), new Vector2(u0, h), new Vector2(u1, h), m);
                mb.Triangle(p0, p1 + up, p1, d0, d1, d1, new Vector2(u0, 0), new Vector2(u1, h), new Vector2(u1, 0), m);
                if (caps)
                {
                    Vector3 top = baseCenter + up;
                    mb.Triangle(top, p1 + up, p0 + up, Vector3.up, Vector3.up, Vector3.up,
                        new Vector2(top.x, top.z), new Vector2(p1.x, p1.z), new Vector2(p0.x, p0.z), m);
                }
            }
        }
    }
}
