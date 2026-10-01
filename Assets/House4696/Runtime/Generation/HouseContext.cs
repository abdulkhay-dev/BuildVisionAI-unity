using System.Collections.Generic;
using House4696.Core;
using House4696.Catalog;
using House4696.Landscape;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>Shared state of one generation run: the document with lookups, materials, writer and output groups.</summary>
    public sealed class HouseContext
    {
        public readonly HouseDocument Doc;
        public readonly MaterialResolver Mats;
        public readonly InteriorMaterials M;
        public readonly MaterialLibrary Lib;
        public readonly FurnitureKit Kit;
        public readonly VegetationFactory Veg;
        public readonly SceneWriter W;
        public readonly List<string> Warnings = new List<string>();
        /// <summary>Catalogue items as built (filled by the builder).</summary>
        public readonly List<ItemBox> ItemBoxes = new List<ItemBox>();
        /// <summary>The natural site as built (null for the other presets): entrances, street, approach paths; heights and zones.</summary>
        public SiteLayout Layout;
        public House4696.Landscape.Natural.SiteModel SiteModel;
        /// <summary>Findings of <see cref="HousePhysicsChecks"/> on the last full build (the checks repeat them).</summary>
        public readonly List<Issue> PhysicalIssues = new List<Issue>();

        readonly Dictionary<string, LevelDef> _levels = new Dictionary<string, LevelDef>();
        readonly Dictionary<string, WallFrame> _walls = new Dictionary<string, WallFrame>();
        readonly Dictionary<StairDef, StairGeometry> _stairs = new Dictionary<StairDef, StairGeometry>();

        public Transform Root, Shell, Interior, Doors, Furniture, Plants, Lights, Probes;

        public HouseContext(HouseDocument doc, MaterialLibrary lib, SceneWriter w)
        {
            Doc = doc; Lib = lib; W = w;
            M = new InteriorMaterials(lib);
            Mats = new MaterialResolver(lib, M);
            Kit = new FurnitureKit(M);
            Veg = new VegetationFactory(lib);
            var sorted = new List<LevelDef>(doc.Levels);
            sorted.Sort((a, b) => a.Elevation.CompareTo(b.Elevation));
            doc.Levels.Clear();
            doc.Levels.AddRange(sorted);
            foreach (var l in doc.Levels) if (!string.IsNullOrEmpty(l.Id)) _levels[l.Id] = l;
            foreach (var wd in doc.Walls) _walls[wd.Id ?? ("wall" + _walls.Count)] = new WallFrame(wd, this);
            DetectCorners();
            SnapPartitionEnds();
            foreach (var e in doc.Elements)
                if (e.Type == ElementType.Pool && PoolShape.From(e, out _) is PoolShape pool) Pools.Add(pool);
            foreach (var s in doc.Stairs)
            {
                var from = Level(s.From);
                var to = s.To != null ? (_levels.TryGetValue(s.To, out var t) ? t : null) : Above(from);
                var g = StairGeometry.Compute(s, from, to);
                if (g == null) continue;
                g.SnapWell(_walls.Values);
                _stairs[s] = g;
            }
            foreach (var l in doc.Lifts)
            {
                var spec = House4696.Lifts.LiftCatalog.Resolve(l, out _);
                if (spec != null) Lifts.Add(new House4696.Lifts.LiftGeometry(l, spec, doc.Levels));
            }
        }

        /// <summary>Lifts of the document that resolve against the catalogue (the validator reports the others).</summary>
        public readonly List<House4696.Lifts.LiftGeometry> Lifts = new List<House4696.Lifts.LiftGeometry>();

        /// <summary>Clear shafts of the lifts that run through a floor or ceiling plane at <paramref name="y"/>.</summary>
        public List<Vector2[]> LiftCuts(float y)
        {
            var list = new List<Vector2[]>();
            foreach (var g in Lifts) if (g.Crosses(y)) list.Add(g.Clear);
            return list;
        }

        /// <summary>Pools of the document that resolve (invalid ones are reported by the builder/validator).</summary>
        public readonly List<PoolShape> Pools = new List<PoolShape>();

        /// <summary>
        /// Plan outlines (basin + walls, convex) of the pools that sink into a solid whose top is at <paramref name="y"/>:
        /// the ground (0), a deck/platform, a room floor. Their builders cut these out.
        /// </summary>
        public List<Vector2[]> PoolCuts(float y)
        {
            var list = new List<Vector2[]>();
            foreach (var p in Pools) if (p.Cuts(y)) list.Add(p.Cut);
            return list;
        }

        /// <summary>
        /// Where a level's floor must stay open (convex or simple plan polygons): stairwells arriving on it, rooms below
        /// rising through it (second light), pools sunk into it.
        /// </summary>
        public List<Vector2[]> FloorCuts(LevelDef L)
        {
            var list = new List<Vector2[]>();
            foreach (var g in StairGeometries) if (g.To == L) list.AddRange(g.Well);
            foreach (var r in Doc.Rooms)
            {
                if (r.Outline == null || r.Outline.Count < 3) continue;
                var R = Level(r.Level);
                if (R.Elevation >= L.Elevation - 0.01f) continue;
                if (R.Elevation + (r.Height ?? R.Height) > L.Elevation - L.Slab + 0.05f) list.Add(Polygon.CounterClockwise(r.Outline).ToArray());
            }
            list.AddRange(PoolCuts(L.Elevation));
            list.AddRange(LiftCuts(L.Elevation));
            return list;
        }

        /// <summary>Plan geometry of a stair (null when its levels do not make a stair).</summary>
        public StairGeometry Stair(StairDef s) => s != null && _stairs.TryGetValue(s, out var g) ? g : null;
        public IEnumerable<StairGeometry> StairGeometries => _stairs.Values;

        /// <summary>
        /// Exterior walls the roof covers: most of the wall (3 of 5 points along it) inside the outline grown by 0.3 m
        /// (walls run along the outline with their outer face on it). A porch roof next to a house wall does not cover it.
        /// </summary>
        public List<WallFrame> WallsUnder(RoofDef r)
        {
            var list = new List<WallFrame>();
            if (r.Outline == null || r.Outline.Count < 3) return list;
            var grown = RoofBuilder.Offset(Polygon.CounterClockwise(r.Outline), 0.3f);
            foreach (var f in _walls.Values)
            {
                if (!f.Exterior) continue;
                int inside = 0;
                for (int i = 0; i < 5; i++)
                {
                    var p = Vector3.Lerp(f.WorldA, f.WorldB, (i + 0.5f) / 5f);
                    if (Polygon.Contains(grown, new Vector2(p.x, p.z))) inside++;
                }
                if (inside >= 3) list.Add(f);
            }
            return list;
        }

        /// <summary>
        /// Height the roof bears at: its <see cref="RoofDef.Base"/>, or the highest top of the exterior walls under its
        /// outline, or the top of the highest level + 0.3 m when no wall is under it.
        /// </summary>
        public float RoofBase(RoofDef r)
        {
            if (r.Base.HasValue) return r.Base.Value;
            float best = float.MinValue;
            foreach (var f in WallsUnder(r)) best = Mathf.Max(best, f.Y1);
            if (best > float.MinValue) return best;
            var top = Doc.Levels.Count > 0 ? Doc.Levels[Doc.Levels.Count - 1] : new LevelDef();
            return top.Elevation + top.Height + 0.3f;
        }

        /// <summary>
        /// Height above which an exterior wall of the top level is outdoors on its inner side too — a parapet: the top
        /// of the flat roof that covers the room behind it. Null when the wall has a level above, stands under a pitched
        /// roof, or no flat roof reaches it. The roof may be outlined along the walls' outer or inner faces, so the test
        /// looks just inside the inner face.
        /// </summary>
        public float? ParapetFrom(WallFrame f)
        {
            if (!f.Exterior || Above(f.Level) != null) return null;
            float? best = null;
            foreach (var r in Doc.Roofs)
            {
                if (r.Type != RoofType.Flat || r.Outline == null || r.Outline.Count < 3) continue;
                var grown = RoofBuilder.Offset(Polygon.CounterClockwise(r.Outline), 0.05f);
                int inside = 0;
                for (int i = 0; i < 5; i++)
                    if (Polygon.Contains(grown, f.Plan(Mathf.Lerp(f.S0, f.S1, (i + 0.5f) / 5f), -f.T - 0.1f))) inside++;
                if (inside < 3) continue;
                float top = RoofBase(r) + r.Thickness;
                if (best == null || top > best.Value) best = top;
            }
            return best;
        }

        /// <summary>A gap narrower than this between a partition's end and a wall is a see-through slit, not a passage.</summary>
        public const float SlitMax = 0.6f;

        /// <summary>
        /// Partitions that stop short of a wall by less than <see cref="SlitMax"/> run on to its face. The usual cause is
        /// measuring to an axis instead of the wall's face (e.g. a partition ends on the line of the inner faces, but the
        /// exterior wall there is set back); the slit left behind shows through between rooms.
        /// </summary>
        void SnapPartitionEnds()
        {
            var all = new List<WallFrame>(_walls.Values);
            // twice: a wall extended in the first pass may be what another end runs into
            for (int pass = 0; pass < 2; pass++)
            foreach (var f in all)
            {
                if (f.Exterior) continue;
                var others = all.FindAll(g => g != f && g.SameStorey(f));
                foreach (bool atB in new[] { false, true })
                {
                    var p = f.Plan(atB ? f.S1 : f.S0, -f.T * 0.5f);
                    if (others.Exists(g => g.DistanceTo(p) < 0.03f)) continue;
                    var dir = new Vector2(f.A.x, f.A.z) * (atB ? 1f : -1f);
                    float? t = WallFrame.Cast(others, p, dir, SlitMax, out _);
                    if (t != null && t.Value >= 0.03f) f.Extend(atB, t.Value);
                }
            }
            JoinCorners(all);
        }

        /// <summary>
        /// Two walls meeting at an angle whose ends both stop short of the corner (each measured to a column, an axis or a
        /// face of the other) leave a diagonal slit that the straight-ahead snap above does not see. Free ends closer than
        /// <see cref="SlitMax"/> run on to the crossing of the centre lines, each into the far face of the other wall.
        /// Exterior walls are not moved: a partition runs into them.
        /// </summary>
        void JoinCorners(List<WallFrame> all)
        {
            bool Free(WallFrame f, bool atB, List<WallFrame> others)
            {
                var p = f.Plan(atB ? f.S1 : f.S0, -f.T * 0.5f);
                return !others.Exists(g => g.DistanceTo(p) < 0.03f);
            }
            var ends = new List<(WallFrame f, bool atB)>();
            foreach (var f in all)
            {
                var others = all.FindAll(g => g != f && g.SameStorey(f));
                foreach (bool atB in new[] { false, true }) if (Free(f, atB, others)) ends.Add((f, atB));
            }
            for (int i = 0; i < ends.Count; i++)
            for (int j = i + 1; j < ends.Count; j++)
            {
                var (f, fb) = ends[i];
                var (g, gb) = ends[j];
                if (f == g || !f.SameStorey(g) || (f.Exterior && g.Exterior)) continue;
                if (Mathf.Abs(Vector3.Dot(f.A, g.A)) > 0.87f) continue;               // (nearly) parallel: not a corner
                Vector2 pf = f.Plan(fb ? f.S1 : f.S0, -f.T * 0.5f), pg = g.Plan(gb ? g.S1 : g.S0, -g.T * 0.5f);
                if ((pf - pg).magnitude > SlitMax) continue;
                // crossing of the centre lines, as distances ahead of each end
                Vector2 df = new Vector2(f.A.x, f.A.z) * (fb ? 1f : -1f), dg = new Vector2(g.A.x, g.A.z) * (gb ? 1f : -1f);
                float den = df.x * dg.y - df.y * dg.x;
                if (Mathf.Abs(den) < 1e-4f) continue;
                Vector2 w = pg - pf;
                float tf = (w.x * dg.y - w.y * dg.x) / den, tg = (w.x * df.y - w.y * df.x) / den;
                if (tf < -0.05f || tg < -0.05f || tf > SlitMax || tg > SlitMax) continue;
                // 1 cm short of the far face: an end flush with it would share its plane
                if (!f.Exterior) { float by = tf + g.T * 0.5f - 0.01f; if (by > 0.005f) f.Extend(fb, by); }
                if (!g.Exterior) { float by = tg + f.T * 0.5f - 0.01f; if (by > 0.005f) g.Extend(gb, by); }
            }
        }

        /// <summary>
        /// Outside corners of exterior walls (end of one wall meets the start of the next with a left turn, i.e. a
        /// convex corner of a counter-clockwise outline): the cladding wraps around them unless set explicitly.
        /// </summary>
        void DetectCorners()
        {
            foreach (var f in _walls.Values)
            foreach (var g in _walls.Values)
            {
                if (f == g || !f.Exterior || !g.Exterior) continue;
                if ((f.WorldB - g.WorldA).sqrMagnitude > 0.0004f) continue;
                bool convex = Vector3.Cross(f.A, g.A).y < -1e-4f;
                if (!convex) continue;
                if (f.Def.WrapEnd == null) f.WrapEnd = true;
                if (g.Def.WrapStart == null) g.WrapStart = true;
            }
        }

        public void Warn(string msg) { Warnings.Add(msg); Debug.LogWarning("[House] " + msg); }

        public LevelDef Level(string id)
        {
            if (id != null && _levels.TryGetValue(id, out var l)) return l;
            return Doc.Levels.Count > 0 ? Doc.Levels[0] : new LevelDef { Id = "ground" };
        }

        public float Elevation(string levelId) => string.IsNullOrEmpty(levelId) ? 0f : Level(levelId).Elevation;

        /// <summary>The level directly above, or null for the top level.</summary>
        public LevelDef Above(LevelDef l)
        {
            int i = Doc.Levels.IndexOf(l);
            return i >= 0 && i + 1 < Doc.Levels.Count ? Doc.Levels[i + 1] : null;
        }

        public bool IsLowest(LevelDef l) => Doc.Levels.Count == 0 || Doc.Levels[0] == l;

        /// <summary>A storey whose floor is this far below grade is a basement (its walls are earth-retaining).</summary>
        public const float BasementDepth = 0.3f;

        public static bool IsBelowGrade(LevelDef l) => l != null && l.Elevation < -BasementDepth;

        /// <summary>The storey at grade — where the entrance is: the lowest one not below ground (basements are under it).</summary>
        public LevelDef GroundLevel
        {
            get
            {
                foreach (var l in Doc.Levels) if (!IsBelowGrade(l)) return l;
                return Doc.Levels.Count > 0 ? Doc.Levels[Doc.Levels.Count - 1] : null;
            }
        }

        /// <summary>
        /// Plan outline (outer faces, counter-clockwise) of a storey's exterior walls when they close into a ring; else the
        /// rectangle around them; null without exterior walls.
        /// </summary>
        public List<Vector2> Outline(LevelDef level)
        {
            var walls = new List<WallFrame>();
            foreach (var f in _walls.Values) if (f.Exterior && f.Level == level) walls.Add(f);
            if (walls.Count == 0) return null;
            var ring = new List<Vector2>();
            var used = new HashSet<WallFrame>();
            WallFrame cur = walls[0], last = null;
            while (cur != null && used.Add(cur))
            {
                ring.Add(new Vector2(cur.WorldA.x, cur.WorldA.z));
                last = cur;
                var end = cur.WorldB;
                cur = walls.Find(g => !used.Contains(g) && (g.WorldA - end).sqrMagnitude < 0.0025f);
            }
            bool closed = used.Count == walls.Count && ring.Count >= 3 && (last.WorldB - walls[0].WorldA).sqrMagnitude < 0.0025f;
            if (closed) return Polygon.CounterClockwise(ring);
            float x0 = float.MaxValue, z0 = float.MaxValue, x1 = float.MinValue, z1 = float.MinValue;
            foreach (var f in walls)
                foreach (var p in new[] { f.WorldA, f.WorldB })
                { x0 = Mathf.Min(x0, p.x); x1 = Mathf.Max(x1, p.x); z0 = Mathf.Min(z0, p.z); z1 = Mathf.Max(z1, p.z); }
            return new List<Vector2> { new Vector2(x0, z0), new Vector2(x1, z0), new Vector2(x1, z1), new Vector2(x0, z1) };
        }

        /// <summary>Light wells and stair pits dug in front of below-grade openings (filled by <see cref="BasementBuilder"/>).</summary>
        public readonly List<BasementBuilder.Pit> Pits = new List<BasementBuilder.Pit>();

        /// <summary>
        /// Where the ground surface must be cut away (convex plan polygons): pools, the footprints of basements (as
        /// triangles) and the pits in front of their openings. The lawn, the gravel apron and the natural terrain use it.
        /// </summary>
        public List<Vector2[]> GroundCuts()
        {
            var list = PoolCuts(0f);
            foreach (var l in Doc.Levels)
            {
                if (!IsBelowGrade(l)) continue;
                var o = Outline(l);
                if (o == null) continue;
                // pulled 5 cm inside the outer faces: the walls hide the cut edge
                var inner = RoofBuilder.Offset(o, -0.05f);
                var tris = Polygon.Triangulate(inner);
                for (int t = 0; t + 2 < tris.Count; t += 3) list.Add(new[] { inner[tris[t]], inner[tris[t + 1]], inner[tris[t + 2]] });
            }
            foreach (var p in Pits) list.Add(p.Cut);
            return list;
        }

        /// <summary>Height of the underside of the structure above a level's ceiling (next floor's slab bottom or roof).</summary>
        public float TopOfLevel(LevelDef l)
        {
            var up = Above(l);
            return up != null ? up.Elevation : l.Elevation + l.Height + 0.3f;
        }

        public WallFrame Wall(string id) => id != null && _walls.TryGetValue(id, out var f) ? f : null;
        public IEnumerable<WallFrame> Walls => _walls.Values;
    }
}
