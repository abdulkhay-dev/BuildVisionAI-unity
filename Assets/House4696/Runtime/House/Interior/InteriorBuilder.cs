using House4696.Core;
using House4696.Landscape;
using House4696.Runtime;
using UnityEngine;
using static House4696.House.HouseSpec;
using static House4696.House.Interior.InteriorPlan;

namespace House4696.House.Interior
{
    /// <summary>
    /// Builds the interior: slabs and ceilings, partitions with openable doors, the floating U-stair with glass
    /// balustrades, furnished rooms (<c>InteriorBuilder.Rooms.cs</c>) and lighting (<see cref="InteriorLighting"/>).
    /// Everything is emitted under one "Interior" object; soft decor and plants carry prefixes that
    /// <c>CollisionSetup</c> leaves without colliders.
    /// </summary>
    public sealed partial class InteriorBuilder
    {
        readonly MaterialLibrary _lib;
        readonly InteriorMaterials _m;
        readonly FurnitureKit _k;
        readonly VegetationFactory _veg;
        readonly SceneWriter _w;
        Transform _root, _doors, _furniture, _plants;

        public InteriorBuilder(MaterialLibrary lib, SceneWriter w)
        {
            _lib = lib; _w = w;
            _m = new InteriorMaterials(lib);
            _k = new FurnitureKit(_m);
            _veg = new VegetationFactory(lib);
        }

        public GameObject Build(Transform parent)
        {
            _root = _w.Group("Interior", parent);
            _doors = _w.Group("Interior_Doors", _root);
            _furniture = _w.Group("Furniture", _root);
            _plants = _w.Group("Plants", _root);

            BuildSlabs();
            BuildPartitions();
            BuildStair();
            BuildGalleryRail();
            BuildSteelPartition();
            FurnishRooms();
            new InteriorLighting(_m, _k, _w).Build(_root);
            return _root.gameObject;
        }

        // ------------------------------------------------------------------ slabs, ceilings, floor finishes
        void BuildSlabs()
        {
            var mb = new MeshBuilder();
            var ground = BoxMats.All(_m.Plaster).With(yp: _m.Oak).Without(yn: true);
            var ceiling = BoxMats.All(_m.Plaster).With(yn: _m.Ceiling).Without(yp: true);
            var upper = BoxMats.All(_m.Plaster).With(yp: _m.Oak, yn: _m.Ceiling);
            foreach (var a in GroundAreas)
            {
                mb.Box(new Vector3(a.X0, 0.02f, a.Z0), new Vector3(a.X1, FloorY, a.Z1), ground);
                mb.Box(new Vector3(a.X0, UpperCeil, a.Z0), new Vector3(a.X1, SoffitY - 0.01f, a.Z1), ceiling);
            }
            foreach (var a in UpperSlab())
                mb.Box(new Vector3(a.X0, BandBottom, a.Z0), new Vector3(a.X1, UpperFloorY, a.Z1), upper);

            var tile = BoxMats.All(_m.Tile).Without(yn: true);
            foreach (var a in TiledGround) mb.Box(new Vector3(a.X0, FloorY, a.Z0), new Vector3(a.X1, FloorY + 0.004f, a.Z1), tile);
            foreach (var a in TiledUpper) mb.Box(new Vector3(a.X0, UpperFloorY, a.Z0), new Vector3(a.X1, UpperFloorY + 0.004f, a.Z1), tile);

            // plaster beams between the floors where the fin walls meet the side blocks (seen from the living room)
            mb.Box(new Vector3(FinLeftX0, BandBottom, LeftFrontZ), new Vector3(FinLeftX1, UpperFloorY, LeftIn), BoxMats.All(_m.Plaster).With(yn: _m.Ceiling));
            mb.Box(new Vector3(FinRightX0, BandBottom, RightFrontZ), new Vector3(FinRightX1, UpperFloorY, RightIn), BoxMats.All(_m.Plaster).With(yn: _m.Ceiling));

            // oak nosing on the gallery edge and a shadow-gap LED cove under it (lights the living-room ceiling edge)
            mb.Box(new Vector3(FinLeftX1, UpperFloorY - 0.03f, VoidZ - 0.012f), new Vector3(FinRightX0, UpperFloorY + 0.004f, VoidZ + 0.02f), _m.OakLight);
            mb.Box(new Vector3(FinLeftX1, BandBottom - 0.02f, VoidZ + 0.02f), new Vector3(FinRightX0, BandBottom, VoidZ + 0.05f), BoxMats.All(_m.Led).Without(yp: true));
            _w.Emit("Interior_Shell", _root, mb);
        }

        // ------------------------------------------------------------------ partitions and doors
        void BuildPartitions()
        {
            var mb = new MeshBuilder();
            var wall = BoxMats.All(_m.Plaster);
            foreach (var p in Partitions())
            {
                bool ax = p.AlongX;
                float a0 = ax ? p.X0 : p.Z0, a1 = ax ? p.X1 : p.Z1;
                Vector3 Min(float s0, float s1, float y0) => ax ? new Vector3(s0, y0, p.Z0) : new Vector3(p.X0, y0, s0);
                Vector3 Max(float s0, float s1, float y1) => ax ? new Vector3(s1, y1, p.Z1) : new Vector3(p.X1, y1, s1);

                float s = a0;
                foreach (var d in Sorted(p.Doors))
                {
                    if (d.From > s) mb.Box(Min(s, d.From, p.Y0), Max(s, d.From, p.Y1), wall);
                    float top = p.Y0 + d.Height;
                    if (top < p.Y1 - 0.01f) mb.Box(Min(d.From, d.To, top), Max(d.From, d.To, p.Y1), wall);
                    BuildDoorLeaf(p, d);
                    s = d.To;
                }
                if (s < a1) mb.Box(Min(s, a1, p.Y0), Max(s, a1, p.Y1), wall);
            }
            _w.Emit("Interior_Partitions", _root, mb);
        }

        static DoorSpec[] Sorted(DoorSpec[] doors)
        {
            var d = (DoorSpec[])doors.Clone();
            System.Array.Sort(d, (x, y) => x.From.CompareTo(y.From));
            return d;
        }

        /// <summary>Flush oak leaf on a pivot at its hinge (same scheme as the exterior doors), black levers both sides.</summary>
        void BuildDoorLeaf(PartitionSpec p, DoorSpec d)
        {
            bool ax = p.AlongX;
            float c = ax ? (p.Z0 + p.Z1) * 0.5f : (p.X0 + p.X1) * 0.5f;
            const float t = 0.04f, gap = 0.004f;
            float s0 = d.From + gap, s1 = d.To - gap, y0 = p.Y0 + 0.008f, y1 = p.Y0 + d.Height - gap;
            Vector3 P(float s, float y, float o) => ax ? new Vector3(s, y, c + o) : new Vector3(c + o, y, s);

            var leaf = new MeshBuilder();
            Vector3 a = P(s0, y0, -t * 0.5f), b = P(s1, y1, t * 0.5f);
            leaf.Box(Vector3.Min(a, b), Vector3.Max(a, b), _m.OakLight);
            float hs = d.HingeAtFrom ? s1 - 0.08f : s0 + 0.08f, dir = d.HingeAtFrom ? -1f : 1f;
            foreach (float side in new[] { -1f, 1f })
            {
                float o0 = side * t * 0.5f, o1 = side * (t * 0.5f + 0.055f);
                Vector3 r0 = P(hs, p.Y0 + 1.0f, o0), r1 = P(hs, p.Y0 + 1.0f, o1);
                leaf.Rod(r0, r1, 0.009f, _m.BlackMetal);
                leaf.Rod(r1, P(hs + dir * 0.13f, p.Y0 + 1.0f, o1), 0.008f, _m.BlackMetal);
            }

            Vector3 hinge = P(d.HingeAtFrom ? s0 : s1, y0, 0f);
            Vector3 along = (ax ? Vector3.right : Vector3.forward) * (d.HingeAtFrom ? 1f : -1f);
            Vector3 inward = (ax ? Vector3.forward : Vector3.right) * d.Swing;
            var pivot = new GameObject("Door_" + p.Name);
            pivot.transform.SetParent(_doors, false);
            pivot.transform.position = hinge;
            var leafGo = _w.Emit("Leaf", pivot.transform, leaf);
            leafGo.transform.localPosition = -hinge;
            _w.MarkDynamic(leafGo);
            float angle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * along, inward) > 0 ? 100f : -100f;
            pivot.AddComponent<Door>().OpenAngle = angle;
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
        }

        // ------------------------------------------------------------------ floating U-stair
        void BuildStair()
        {
            var mb = new MeshBuilder();
            var glass = new MeshBuilder();
            const float tread = 0.06f;
            var treadMats = BoxMats.All(_m.OakLight);
            var steps = new MeshBuilder();

            // flight 1: along the right wall, going +Z
            for (int i = 1; i < Flight1Risers; i++)
            {
                float top = FloorY + i * Rise, z0 = StairZ0 + (i - 1) * Going;
                mb.Box(new Vector3(StairMid1, top - tread, z0), new Vector3(StairX1, top, z0 + Going + 0.02f), treadMats);
                if (i % 2 == 1) StepLight(steps, StairX1 - 0.004f, top + 0.22f, z0 + Going * 0.5f, true);
            }
            // landing slab
            mb.Box(new Vector3(StairX0, LandingY - 0.2f, LandingZ), new Vector3(StairX1, LandingY, BayIn),
                BoxMats.All(_m.Plaster).With(yp: _m.OakLight, yn: _m.Ceiling));
            // flight 2: along the boiler/bath wall, returning -Z to the upper floor
            for (int j = 1; j < Risers - Flight1Risers; j++)
            {
                float top = LandingY + j * Rise, z1 = LandingZ - (j - 1) * Going;
                mb.Box(new Vector3(StairX0, top - tread, z1 - Going - 0.02f), new Vector3(StairMid0, top, z1), treadMats);
                if (j % 2 == 1) StepLight(steps, StairX0 + 0.004f, top + 0.22f, z1 - Going * 0.5f, false);
            }

            // glass fin between the flights (two convex pieces) and the guard at the top of flight 1
            float xm = (StairMid0 + StairMid1) * 0.5f, zt = StairTopZ, zl = LandingZ;
            GlassPanel(glass, xm, new[] { new Vector2(StairZ0, FloorY), new Vector2(zl, LandingY - 0.05f), new Vector2(zt, BandBottom), new Vector2(StairZ0, BandBottom) });
            GlassPanel(glass, xm, new[] { new Vector2(zl, LandingY - 0.05f), new Vector2(zl, LandingY + 0.95f), new Vector2(zt, UpperFloorY + 0.95f), new Vector2(zt, BandBottom) });
            glass.Box(new Vector3(StairMid0, UpperFloorY, zt - 0.006f), new Vector3(StairX1, UpperFloorY + 1.0f, zt + 0.006f), _m.Glass);
            _w.Emit("Stair_Glass", _root, glass, castShadows: false);

            // handrails: on the glass top of flight 2 and wall-mounted along flight 1
            var rails = new MeshBuilder();
            rails.Rod(new Vector3(xm, LandingY + 0.95f, zl), new Vector3(xm, UpperFloorY + 0.95f, zt), 0.022f, _m.BlackMetal, 12);
            rails.Rod(new Vector3(StairMid0, UpperFloorY + 1.0f, zt), new Vector3(StairX1, UpperFloorY + 1.0f, zt), 0.022f, _m.BlackMetal, 12);
            Vector3 r0 = new Vector3(StairX1 - 0.07f, FloorY + 0.9f + Rise, StairZ0), r1 = new Vector3(StairX1 - 0.07f, LandingY + 0.9f, zl);
            rails.Rod(r0, r1, 0.022f, _m.Walnut, 12);
            for (int i = 0; i <= 3; i++)
            {
                Vector3 p = Vector3.Lerp(r0, r1, 0.1f + i * 0.27f);
                rails.Rod(p, p + Vector3.right * 0.07f, 0.008f, _m.BlackMetal);
            }
            _w.Emit("Stair", _root, mb);
            _w.Emit("Stair_Rails", _root, rails);
            _w.Emit("Decor_StepLights", _root, steps, castShadows: false);
        }

        void StepLight(MeshBuilder mb, float x, float y, float z, bool facingNegX)
        {
            float d = facingNegX ? -0.006f : 0.006f;
            Vector3 a = new Vector3(x, y - 0.025f, z - 0.09f), b = new Vector3(x + d, y + 0.025f, z + 0.09f);
            mb.Box(Vector3.Min(a, b), Vector3.Max(a, b), BoxMats.All(_m.BlackMetal).With(yn: _m.Led));
        }

        /// <summary>Glass polygon in the plane x = const; points (z, y) counter-clockwise, convex.</summary>
        void GlassPanel(MeshBuilder mb, float x, Vector2[] zy)
        {
            const float h = 0.006f;
            for (int side = -1; side <= 1; side += 2)
            {
                Vector3 n = Vector3.right * side;
                Vector3 P(int i) => new Vector3(x + side * h, zy[i].y, zy[i].x);
                for (int i = 1; i + 1 < zy.Length; i++)
                {
                    Vector3 a = P(0), b = P(i), c = P(i + 1);
                    Vector2 ua = new Vector2(a.z, a.y), ub = new Vector2(b.z, b.y), uc = new Vector2(c.z, c.y);
                    // (z, y) is counter-clockwise seen from +X: clockwise front order is a, c, b
                    if (side > 0) mb.Triangle(a, c, b, n, n, n, ua, uc, ub, _m.Glass);
                    else mb.Triangle(a, b, c, n, n, n, ua, ub, uc, _m.Glass);
                }
            }
        }

        // ------------------------------------------------------------------ gallery balustrade over the living room
        void BuildGalleryRail()
        {
            var g = new MeshBuilder();
            g.Box(new Vector3(FinLeftX1, UpperFloorY + 0.004f, VoidZ + 0.02f), new Vector3(FinRightX0, UpperFloorY + 1.05f, VoidZ + 0.032f), _m.Glass);
            _w.Emit("Gallery_Glass", _root, g, castShadows: false);
            var r = new MeshBuilder();
            r.Box(new Vector3(FinLeftX1, UpperFloorY + 0.004f, VoidZ + 0.01f), new Vector3(FinRightX0, UpperFloorY + 0.05f, VoidZ + 0.045f), _m.BlackMetal);
            r.Rod(new Vector3(FinLeftX1, UpperFloorY + 1.07f, VoidZ + 0.026f), new Vector3(FinRightX0, UpperFloorY + 1.07f, VoidZ + 0.026f), 0.022f, _m.OakLight, 12);
            _w.Emit("Gallery_Rail", _root, r);
        }

        // ------------------------------------------------------------------ steel-framed glass screen between hall and living room
        /// <summary>
        /// Crittall-style screen in the hall opening (thin black steel profiles, clear glass, a glazed swing door
        /// with a horizontal bar at hand height and a transom above the door).
        /// </summary>
        void BuildSteelPartition()
        {
            const float x = (FinRightX0 + FinRightX1) * 0.5f, t = 0.045f, w = 0.035f;
            const float z0 = 4.16f, z1 = 6.7f, dz0 = 5.0f, dz1 = 5.9f, y0 = FloorY, y1 = GroundCeil;
            float bar = y0 + 0.95f, head = y0 + 2.4f;
            var frame = new MeshBuilder();
            var glass = new MeshBuilder();
            void Profile(MeshBuilder mb, float za, float zb, float ya, float yb) =>
                mb.Bevel(new Vector3(x - t * 0.5f, ya, za), new Vector3(x + t * 0.5f, yb, zb), _m.BlackMetal, 0.002f);
            void Pane(MeshBuilder mb, float za, float zb, float ya, float yb) =>
                mb.Box(new Vector3(x - 0.004f, ya, za), new Vector3(x + 0.004f, yb, zb), _m.Glass);

            // outer frame, door posts, head and bars on the fixed panes
            Profile(frame, z0, z0 + w, y0, y1); Profile(frame, z1 - w, z1, y0, y1);
            Profile(frame, z0, z1, y1 - w, y1); Profile(frame, z0, dz0, y0, y0 + w); Profile(frame, dz1, z1, y0, y0 + w);
            Profile(frame, dz0 - w, dz0, y0, y1); Profile(frame, dz1, dz1 + w, y0, y1);
            Profile(frame, dz0, dz1, head - w * 0.5f, head + w * 0.5f);
            foreach (var (za, zb) in new[] { (z0 + w, dz0 - w), (dz1 + w, z1 - w) })
            {
                Profile(frame, za, zb, bar - w * 0.5f, bar + w * 0.5f);
                Profile(frame, za, zb, head - w * 0.5f, head + w * 0.5f);
                Pane(glass, za, zb, y0 + w, y1 - w);
            }
            Pane(glass, dz0, dz1, head + w * 0.5f, y1 - w);
            _w.Emit("Steel_Partition", _root, frame);
            _w.Emit("Steel_Glass", _root, glass, castShadows: false);

            // glazed door leaf on a pivot at the hinge, swinging into the living room
            var leaf = new MeshBuilder();
            float la = dz0 + 0.004f, lb = dz1 - 0.004f, lt = head - w * 0.5f - 0.004f, lbm = y0 + 0.01f;
            Profile(leaf, la, la + w, lbm, lt); Profile(leaf, lb - w, lb, lbm, lt);
            Profile(leaf, la, lb, lt - w, lt); Profile(leaf, la, lb, lbm, lbm + w * 1.6f);
            Profile(leaf, la, lb, bar - w * 0.5f, bar + w * 0.5f);
            Pane(leaf, la + w, lb - w, lbm + w, lt - w);
            foreach (float side in new[] { -1f, 1f })
                leaf.Rod(new Vector3(x + side * 0.03f, y0 + 0.75f, lb - 0.09f), new Vector3(x + side * 0.03f, y0 + 1.35f, lb - 0.09f), 0.01f, _m.BlackMetal);
            var hinge = new Vector3(x, lbm, la);
            var pivot = new GameObject("Door_SteelGlass");
            pivot.transform.SetParent(_doors, false);
            pivot.transform.position = hinge;
            var leafGo = _w.Emit("Leaf", pivot.transform, leaf);
            leafGo.transform.localPosition = -hinge;
            _w.MarkDynamic(leafGo);
            float angle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * Vector3.forward, Vector3.left) > 0 ? 100f : -100f;
            pivot.AddComponent<Door>().OpenAngle = angle;
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
        }

        // ------------------------------------------------------------------ helpers for the room layouts
        /// <summary>Emits a room's furniture as one object and its soft decor (no colliders) as another.</summary>
        void Emit(string room, MeshBuilder furniture, MeshBuilder decor)
        {
            _w.Emit("Furniture_" + room, _furniture, furniture);
            if (decor != null) _w.Emit("Decor_" + room, _furniture, decor);
        }

        void Plant(string name, Vector3 floor, float height, float radius, int seed, float potR = 0.28f, float potH = 0.5f, Material pot = null)
        {
            var mb = new MeshBuilder();
            _k.Planter(mb, floor, potR, potH, pot ?? _m.Stoneware);
            _w.Emit("Furniture_Pot_" + name, _furniture, mb);
            var tree = _veg.BroadleafTree(height, radius, seed);
            var go = _w.Emit("Plant_" + name, _plants, tree);
            go.transform.position = floor + Vector3.up * (potH * 0.85f);
        }

        void Grass(string name, Vector3 floor, int seed, float potR = 0.2f, float potH = 0.36f)
        {
            var mb = new MeshBuilder();
            _k.Planter(mb, floor, potR, potH, _m.Charcoal);
            _w.Emit("Furniture_Pot_" + name, _furniture, mb);
            var g = _veg.GrassClump(potR * 1.3f, 0.7f, 70, 2, 0, 0f, seed);
            var go = _w.Emit("Plant_" + name, _plants, g);
            go.transform.position = floor + Vector3.up * (potH * 0.88f);
        }
    }
}
