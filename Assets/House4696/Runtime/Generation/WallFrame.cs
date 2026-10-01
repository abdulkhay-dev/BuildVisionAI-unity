using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Resolved geometry of a wall. Wall space: s along the wall (A→B), y up (absolute), d outward from the outer
    /// face (the body spans d ∈ [-T, 0]). <see cref="ToWorld"/> maps local (s, y, -d) to world, so boxes built in
    /// local space are axis aligned there and get the same metric planar UVs as world-aligned walls.
    /// "Outer" is the right side of A→B seen from above (the outside of counter-clockwise exterior walls).
    /// </summary>
    public sealed class WallFrame
    {
        public readonly WallDef Def;
        public readonly LevelDef Level;
        public readonly Vector3 N, A, O;
        public readonly Matrix4x4 ToWorld;
        public readonly float T, Y0, Y1;
        /// <summary>Wall-space s of the ends (may be extended past A/B, see <see cref="Extend"/>).</summary>
        public float S0 { get; private set; }
        public float S1 { get; private set; }
        readonly float _origin;   // s of point A: openings and zones are measured from it
        public bool WrapStart, WrapEnd;

        public bool Exterior => Def.Kind == WallKind.Exterior;
        public float Length => S1 - S0;

        public WallFrame(WallDef w, HouseContext ctx)
        {
            Def = w;
            Level = ctx.Level(w.Level);
            bool ext = w.Kind == WallKind.Exterior;
            T = w.Thickness ?? (ext ? 0.4f : 0.12f);
            var align = w.Align ?? (ext ? WallAlign.Outer : WallAlign.Center);

            Vector2 d2 = w.B - w.A;
            if (d2.sqrMagnitude < 1e-8f) d2 = Vector2.right;
            d2.Normalize();
            A = new Vector3(d2.x, 0, d2.y);
            N = new Vector3(d2.y, 0, -d2.x);                       // right of A→B
            float off = align == WallAlign.Outer ? 0f : align == WallAlign.Center ? T * 0.5f : T;
            Vector3 a = new Vector3(w.A.x, 0, w.A.y) + N * off, b = new Vector3(w.B.x, 0, w.B.y) + N * off;
            O = N * Vector3.Dot(a, N);                              // foot of the world origin on the outer face line
            S0 = Vector3.Dot(a, A);
            S1 = Vector3.Dot(b, A);
            _origin = S0;
            ToWorld = Matrix4x4.TRS(O, Quaternion.LookRotation(-N, Vector3.up), Vector3.one);

            var above = ctx.Above(Level);
            if (ext)
            {
                // the lowest storey's walls reach the ground (a plinth) — or go down to its slab when it is a basement
                Y0 = w.Bottom ?? (ctx.IsLowest(Level) ? Mathf.Min(0f, Level.Elevation - Level.Slab) : Level.Elevation - Level.Slab);
                Y1 = w.Top ?? (above != null ? above.Elevation - above.Slab : Level.Elevation + Level.Height + 0.3f);
            }
            else
            {
                Y0 = w.Bottom ?? Level.Elevation;
                Y1 = w.Top ?? Level.Elevation + Level.Height;
            }
            WrapStart = w.WrapStart ?? false;
            WrapEnd = w.WrapEnd ?? false;
        }

        /// <summary>World point of wall-space (s, y, d).</summary>
        public Vector3 P(float s, float y, float d) => O + A * s + Vector3.up * y + N * d;

        /// <summary>Local (builder) coordinates of wall-space (s, y, d).</summary>
        public static Vector3 L(float s, float y, float d) => new Vector3(s, y, -d);

        /// <summary>Wall-space s of a distance measured from A along the wall.</summary>
        public float SAt(float fromA) => _origin + fromA;

        public Vector3 WorldA => P(S0, 0, 0);
        public Vector3 WorldB => P(S1, 0, 0);

        /// <summary>Lengthens the wall at an end (openings stay where they are: they are measured from A).</summary>
        public void Extend(bool atB, float by) { if (atB) S1 += by; else S0 -= by; }

        /// <summary>Do the two walls stand in the same storey (overlap in height by more than 0.3 m)?</summary>
        public bool SameStorey(WallFrame o) => Y0 < o.Y1 - 0.3f && o.Y0 < Y1 - 0.3f;

        /// <summary>Plan point of wall-space (s, d).</summary>
        public Vector2 Plan(float s, float d) { var p = P(s, 0, d); return new Vector2(p.x, p.z); }

        /// <summary>Does the wall stand at this height (absolute)?</summary>
        public bool Spans(float y) => Y0 < y && Y1 > y;

        /// <summary>Plan rectangle of the wall body (counter-clockwise), grown by <paramref name="grow"/>.</summary>
        public Vector2[] PlanBody(float grow = 0f)
        {
            var r = new[] { Plan(S0 - grow, grow), Plan(S1 + grow, grow), Plan(S1 + grow, -T - grow), Plan(S0 - grow, -T - grow) };
            return Polygon.SignedArea(r) < 0 ? new[] { r[3], r[2], r[1], r[0] } : r;
        }

        /// <summary>Plan distance from a point to the wall body (0 inside).</summary>
        public float DistanceTo(Vector2 p)
        {
            var body = PlanBody();
            if (Polygon.Contains(body, p)) return 0f;
            float best = float.MaxValue;
            for (int i = 0; i < 4; i++) best = Mathf.Min(best, StairGeometry.DistanceToSegment(p, body[i], body[(i + 1) % 4]));
            return best;
        }

        /// <summary>
        /// Distance along a plan ray to the first wall body among <paramref name="walls"/> (null when none within
        /// <paramref name="max"/>). Marches in 1 cm steps: walls are thicker than that.
        /// </summary>
        public static float? Cast(IEnumerable<WallFrame> walls, Vector2 from, Vector2 dir, float max, out WallFrame hit)
        {
            hit = null;
            float? best = null;
            foreach (var f in walls)
            {
                var body = f.PlanBody();
                for (float t = 0f; t <= max && (best == null || t < best.Value); t += 0.01f)
                    if (Polygon.Contains(body, from + dir * t)) { best = t; hit = f; break; }
            }
            return best;
        }
    }
}
