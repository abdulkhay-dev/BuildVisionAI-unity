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
        public readonly float S0, S1, T, Y0, Y1;
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
            ToWorld = Matrix4x4.TRS(O, Quaternion.LookRotation(-N, Vector3.up), Vector3.one);

            var above = ctx.Above(Level);
            if (ext)
            {
                Y0 = w.Bottom ?? (ctx.IsLowest(Level) ? 0f : Level.Elevation - Level.Slab);
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
        public float SAt(float fromA) => S0 + fromA;

        public Vector3 WorldA => P(S0, 0, 0);
        public Vector3 WorldB => P(S1, 0, 0);
    }
}
