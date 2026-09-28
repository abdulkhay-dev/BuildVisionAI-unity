using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Glass guards on the open edges of upper floors: around stairwells (<c>well: auto</c>) and along floor edges over a
    /// double-height room. An edge is open where there is no floor across it, no wall on it and no author's railing
    /// along it; the arrival edge of a stair stays open. Coverage is exact at the ends: a railing covers only what it
    /// runs alongside (not 25 cm past its end), a wall only its own body — so a gap between a railing and a wall
    /// gets its own short guard instead of being left as a hole to fall through.
    /// </summary>
    public sealed class EdgeGuards
    {
        const float Step = 0.05f, MinRun = 0.1f;
        readonly HouseContext _c;
        public EdgeGuards(HouseContext c) { _c = c; }

        /// <summary>An open stretch of floor edge: on the slab, at floor height <see cref="Y"/>.</summary>
        public struct Run { public Vector2 A, B; public float Y; public string Owner; }

        public void Build()
        {
            var elements = new ElementBuilder(_c);
            int n = 0;
            foreach (var r in Find(_c))
                elements.Build(new ElementDef
                {
                    Id = $"{r.Owner}_guard{++n}", Type = ElementType.Railing, Y = r.Y, Height = 1.0f, Style = "glass",
                    Path = new List<Vector2> { r.A, r.B },
                });
        }

        /// <summary>All open edge runs of the house (shared by the builder and the inspector).</summary>
        public static List<Run> Find(HouseContext c)
        {
            var runs = new List<Run>();
            // stairwells: every edge of the well polygon, floor on the outside of the hole
            foreach (var g in c.StairGeometries)
            {
                if (g.Well.Count == 0 || g.Def.Well != "auto") continue;
                float y = g.To.Elevation;
                var cov = new Coverage(c, y);
                var rooms = c.Doc.Rooms.FindAll(r => r.Level == g.To.Id && r.Outline != null && r.Outline.Count >= 3);
                foreach (var h in g.Well)
                    for (int i = 0; i < h.Length; i++)
                    {
                        Vector2 a = h[i], b = h[(i + 1) % h.Length];
                        // outward of the hole = onto the floor; the guard stands on the floor just outside the hole
                        Scan(a, b, y, "stair_" + (g.Def.Id ?? "stair"), runs, towardsFloor: true, (p, onFloor) =>
                            !g.InWell(onFloor) && !g.OnArrival(p, 0.08f) && rooms.Exists(r => Polygon.Contains(r.Outline, onFloor)) && !cov.Covered(p, b - a));
                    }
            }
            // floor edges over a double-height room
            foreach (var low in c.Doc.Rooms)
            {
                if (low.Outline == null || low.Outline.Count < 3 || low.Type == RoomType.Terrace) continue;
                var L = c.Level(low.Level);
                var up = c.Above(L);
                if (up == null || (low.Height ?? L.Height) < up.Elevation - L.Elevation + 0.1f) continue;
                float y = up.Elevation;
                var cov = new Coverage(c, y);
                var upper = c.Doc.Rooms.FindAll(r => r.Level == up.Id && r.Outline != null && r.Outline.Count >= 3);
                foreach (var room in upper)
                {
                    var o = Polygon.CounterClockwise(room.Outline);
                    for (int i = 0; i < o.Count; i++)
                    {
                        Vector2 a = o[i], b = o[(i + 1) % o.Count];
                        // outward of a room outline = into the void; the guard stands just inside the room
                        Scan(a, b, y, "void_" + room.Id, runs, towardsFloor: false, (p, inVoid) =>
                            Polygon.Contains(low.Outline, inVoid) && !upper.Exists(r => Polygon.Contains(r.Outline, inVoid)) &&
                            !InAnyWell(c, up, inVoid) && !OnAnyArrival(c, up, p) && !cov.Covered(p, b - a));
                    }
                }
            }
            return runs;
        }

        /// <summary>
        /// Walks the edge a→b in 5 cm steps; <paramref name="open"/>(point on the edge, probe 15 cm to its outer side).
        /// Open runs become guards set 3 cm onto the floor.
        /// </summary>
        static void Scan(Vector2 a, Vector2 b, float y, string owner, List<Run> runs, bool towardsFloor, System.Func<Vector2, Vector2, bool> open)
        {
            var d = b - a;
            float len = d.magnitude;
            if (len < MinRun) return;
            d /= len;
            var outward = new Vector2(d.y, -d.x);
            var floorSide = towardsFloor ? outward : -outward;
            int steps = Mathf.Max(1, Mathf.RoundToInt(len / Step));
            int start = -1;
            for (int k = 0; k <= steps; k++)
            {
                bool isOpen = false;
                if (k < steps)
                {
                    var p = a + d * (len * (k + 0.5f) / steps);
                    isOpen = open(p, p + outward * 0.15f);
                }
                if (isOpen && start < 0) start = k;
                if (isOpen || start < 0) continue;
                float t0 = len * start / steps, t1 = len * k / steps;
                start = -1;
                if (t1 - t0 < MinRun) continue;
                var off = floorSide * 0.03f;
                runs.Add(new Run { A = a + d * t0 + off, B = a + d * t1 + off, Y = y, Owner = owner });
            }
        }

        static bool InAnyWell(HouseContext c, LevelDef level, Vector2 p)
        {
            foreach (var g in c.StairGeometries) if (g.To == level && g.InWell(p)) return true;
            return false;
        }

        static bool OnAnyArrival(HouseContext c, LevelDef level, Vector2 p)
        {
            foreach (var g in c.StairGeometries) if (g.To == level && g.OnArrival(p, 0.3f)) return true;
            return false;
        }

        /// <summary>Walls and author's railings standing on a floor at height y.</summary>
        sealed class Coverage
        {
            readonly List<WallFrame> _walls = new List<WallFrame>();
            readonly List<ElementDef> _rails;

            public Coverage(HouseContext c, float y)
            {
                foreach (var f in c.Walls) if (f.Spans(y + 0.5f)) _walls.Add(f);
                _rails = c.Doc.Elements.FindAll(e => e.Type == ElementType.Railing && Mathf.Abs(e.Y - y) < 0.4f && e.Path != null && e.Path.Count >= 2);
            }

            /// <summary>Is the edge point p (edge direction <paramref name="dir"/>) on a wall or alongside a railing?</summary>
            public bool Covered(Vector2 p, Vector2 dir)
            {
                foreach (var f in _walls) if (f.DistanceTo(p) < 0.05f) return true;
                dir = dir.normalized;
                foreach (var e in _rails)
                    for (int j = 0; j + 1 < e.Path.Count; j++)
                    {
                        Vector2 a = e.Path[j], ab = e.Path[j + 1] - a;
                        float l2 = ab.sqrMagnitude;
                        if (l2 < 1e-6f || Mathf.Abs(Vector2.Dot(ab / Mathf.Sqrt(l2), dir)) < 0.9f) continue;   // only a parallel railing
                        float t = Vector2.Dot(p - a, ab) / l2;
                        if (t < -0.02f || t > 1.02f) continue;                                              // not past its ends
                        if ((a + ab * Mathf.Clamp01(t) - p).magnitude < 0.25f) return true;
                    }
                return false;
            }
        }
    }
}
