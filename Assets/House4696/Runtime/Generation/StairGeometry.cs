using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Plan geometry of a stair, shared by the builder (floor openings, guards), the checks and the inspector: riser
    /// count, the footprint of flights and landing, the stairwell (where the upper floor must be open for 2 m of
    /// headroom) and the arrival edge (where the last flight steps onto the upper floor). Plan polygons are world
    /// (x, z), counter-clockwise, convex (rectangles).
    /// </summary>
    public sealed class StairGeometry
    {
        public const float Headroom = 2.0f;

        public StairDef Def;
        public LevelDef From, To;
        public float H, Rise;
        public int Risers, FirstFlight;
        public readonly List<Vector2[]> Footprint = new List<Vector2[]>();
        public readonly List<Vector2[]> Well = new List<Vector2[]>();
        public Vector2 ArrivalA, ArrivalB;
        /// <summary>Walking direction off the last tread onto the upper floor (unit, plan).</summary>
        public Vector2 ArrivalDir;

        /// <summary>Null when the upper level is missing or not above the lower one.</summary>
        public static StairGeometry Compute(StairDef s, LevelDef from, LevelDef to)
        {
            if (from == null || to == null) return null;
            float H = to.Elevation - from.Elevation;
            if (H <= 0.2f) return null;
            var g = new StairGeometry { Def = s, From = from, To = to, H = H };
            int n = Mathf.Max(3, s.Risers ?? Mathf.RoundToInt(H / 0.175f));
            g.Risers = n;
            g.Rise = H / n;
            int k = s.Type == StairType.Straight ? n : Mathf.Clamp(s.FirstFlight ?? n / 2 + 1, 2, n - 2);
            g.FirstFlight = k;
            float go = s.Going, w = s.Width, hw = w * 0.5f;
            float side = s.Turn != "right" ? -1f : 1f;
            // first tread whose top has less than 2 m under the upper slab
            float clear = H - to.Slab - Headroom;
            int i0 = 1;
            while (i0 < n && i0 * g.Rise <= clear) i0++;
            float zs = (i0 - 1) * go;

            switch (s.Type)
            {
                case StairType.Straight:
                {
                    float zEnd = (n - 1) * go;
                    g.Footprint.Add(g.Rect(-hw, hw, 0, zEnd));
                    if (i0 < n) g.Well.Add(g.Rect(-hw, hw, zs, zEnd));
                    g.SetArrival(new Vector2(-hw, zEnd), new Vector2(hw, zEnd), new Vector2(0, 1));
                    break;
                }
                case StairType.U:
                {
                    float zl = (k - 1) * go, depth = s.Landing ?? w;
                    int rest = n - k;
                    float x2 = side * (w + s.Gap);
                    float lx0 = Mathf.Min(-hw, x2 - hw), lx1 = Mathf.Max(hw, x2 + hw);
                    float zt = zl - (rest - 1) * go;
                    g.Footprint.Add(g.Rect(-hw, hw, 0, zl));
                    g.Footprint.Add(g.Rect(lx0, lx1, zl, zl + depth));
                    g.Footprint.Add(g.Rect(x2 - hw, x2 + hw, zt, zl));
                    // the standard U well: the whole rectangle from the arrival line to the far side of the landing
                    float wz = Mathf.Max(0f, zt);
                    g.Well.Add(g.Rect(lx0, lx1, wz, zl + depth));
                    g.SetArrival(new Vector2(x2 - hw, zt), new Vector2(x2 + hw, zt), new Vector2(0, -1));
                    break;
                }
                default: // L: square landing, the second flight runs sideways
                {
                    float zl = (k - 1) * go, depth = s.Landing ?? w;
                    int rest = n - k;
                    float edge = side * hw, xEnd = edge + side * (rest - 1) * go;
                    g.Footprint.Add(g.Rect(-hw, hw, 0, zl + depth));
                    g.Footprint.Add(g.Rect(Mathf.Min(edge, xEnd), Mathf.Max(edge, xEnd), zl, zl + depth));
                    g.Well.Add(g.Rect(-hw, hw, Mathf.Min(zs, zl), zl + depth));
                    g.Well.Add(g.Rect(Mathf.Min(edge, xEnd), Mathf.Max(edge, xEnd), zl, zl + depth));
                    g.SetArrival(new Vector2(xEnd, zl), new Vector2(xEnd, zl + depth), new Vector2(side, 0));
                    break;
                }
            }
            if (s.Well == "none") g.Well.Clear();
            return g;
        }

        /// <summary>
        /// A strip of slab narrower than this between the well and a wall is not a floor but a floating beam in the
        /// stair hall (and a shelf across a window): the well is extended to the wall's face instead.
        /// </summary>
        public const float SliverMax = 0.6f;

        /// <summary>Extends well edges that run parallel to a wall less than <see cref="SliverMax"/> away up to its face.</summary>
        public void SnapWell(IEnumerable<WallFrame> allWalls)
        {
            var walls = new List<WallFrame>();
            foreach (var f in allWalls) if (f.Spans(To.Elevation + 0.5f)) walls.Add(f);
            if (walls.Count == 0) return;
            for (int r = 0; r < Well.Count; r++)
            {
                var q = Well[r];
                for (int i = 0; i < 4; i++)
                {
                    Vector2 a = q[i], b = q[(i + 1) % 4], d = b - a;
                    float len = d.magnitude;
                    if (len < 0.2f) continue;
                    var outward = new Vector2(d.y, -d.x) / len;
                    if (DistanceToSegment((ArrivalA + ArrivalB) * 0.5f, a, b) < 0.05f) continue;   // people step off here
                    // the whole edge must face the wall at about the same distance (5 probes, ends excluded)
                    float lo = float.MaxValue, hi = 0f;
                    for (int k = 0; k < 5; k++)
                    {
                        var p = a + d * (0.1f + 0.8f * k / 4f) + outward * 0.005f;
                        float? t = WallFrame.Cast(walls, p, outward, SliverMax, out _);
                        if (t == null) { lo = float.MaxValue; hi = float.MaxValue; break; }
                        lo = Mathf.Min(lo, t.Value); hi = Mathf.Max(hi, t.Value);
                    }
                    if (hi >= float.MaxValue || lo < 0.02f || hi - lo > 0.05f) continue;
                    var shift = outward * (lo + 0.005f);
                    q[i] += shift; q[(i + 1) % 4] += shift;
                }
            }
        }

        Vector2 W(float x, float z)
        {
            var p = Quaternion.Euler(0, Def.Direction, 0) * new Vector3(x, 0, z);
            return Def.Start + new Vector2(p.x, p.z);
        }

        Vector2[] Rect(float x0, float x1, float z0, float z1)
        {
            // counter-clockwise in local space stays counter-clockwise after a rotation
            return new[] { W(x0, z0), W(x1, z0), W(x1, z1), W(x0, z1) };
        }

        void SetArrival(Vector2 a, Vector2 b, Vector2 dir)
        {
            ArrivalA = W(a.x, a.y);
            ArrivalB = W(b.x, b.y);
            var d = Quaternion.Euler(0, Def.Direction, 0) * new Vector3(dir.x, 0, dir.y);
            ArrivalDir = new Vector2(d.x, d.z).normalized;
        }

        public bool InFootprint(Vector2 p)
        {
            foreach (var r in Footprint) if (Polygon.Contains(r, p)) return true;
            return false;
        }

        /// <summary>Plan distance from a point to the flights and landings (0 on them).</summary>
        public float DistanceToFootprint(Vector2 p)
        {
            float best = float.MaxValue;
            foreach (var r in Footprint)
            {
                if (Polygon.Contains(r, p)) return 0f;
                for (int i = 0; i < r.Length; i++) best = Mathf.Min(best, DistanceToSegment(p, r[i], r[(i + 1) % r.Length]));
            }
            return best;
        }

        public bool InWell(Vector2 p)
        {
            foreach (var r in Well) if (Polygon.Contains(r, p)) return true;
            return false;
        }

        /// <summary>Is the point on the arrival edge (within <paramref name="tol"/>)?</summary>
        public bool OnArrival(Vector2 p, float tol = 0.05f) => DistanceToSegment(p, ArrivalA, ArrivalB) < tol;

        public static float DistanceToSegment(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            float t = ab.sqrMagnitude < 1e-8f ? 0f : Mathf.Clamp01(Vector2.Dot(p - a, ab) / ab.sqrMagnitude);
            return (a + ab * t - p).magnitude;
        }
    }
}
