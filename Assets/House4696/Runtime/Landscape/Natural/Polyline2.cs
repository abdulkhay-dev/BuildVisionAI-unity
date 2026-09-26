using System.Collections.Generic;
using UnityEngine;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// A plan curve (Catmull-Rom through the control points) resampled every <c>step</c> metres, with arclength
    /// and a grid index for nearest-point queries.
    /// </summary>
    public sealed class Polyline2
    {
        public readonly List<Vector2> Points = new List<Vector2>();
        public readonly List<float> S = new List<float>();
        public float Length => S.Count > 0 ? S[S.Count - 1] : 0f;

        const float Cell = 2f;
        readonly Dictionary<long, List<int>> _grid = new Dictionary<long, List<int>>();

        public Polyline2(IList<Vector2> ctrl, float step = 0.1f)
        {
            if (ctrl.Count == 1) Points.Add(ctrl[0]);
            for (int i = 0; i < ctrl.Count - 1; i++)
            {
                Vector2 p0 = ctrl[Mathf.Max(i - 1, 0)], p1 = ctrl[i], p2 = ctrl[i + 1], p3 = ctrl[Mathf.Min(i + 2, ctrl.Count - 1)];
                int n = Mathf.Max(2, Mathf.CeilToInt((p2 - p1).magnitude / step));
                for (int k = 0; k < n; k++)
                {
                    float t = k / (float)n, t2 = t * t, t3 = t2 * t;
                    Points.Add(0.5f * (2f * p1 + (-p0 + p2) * t + (2f * p0 - 5f * p1 + 4f * p2 - p3) * t2 + (-p0 + 3f * p1 - 3f * p2 + p3) * t3));
                }
            }
            if (ctrl.Count > 1) Points.Add(ctrl[ctrl.Count - 1]);
            S.Add(0f);
            for (int i = 1; i < Points.Count; i++) S.Add(S[i - 1] + (Points[i] - Points[i - 1]).magnitude);
            for (int i = 0; i < Points.Count; i++)
            {
                long key = Key(Mathf.FloorToInt(Points[i].x / Cell), Mathf.FloorToInt(Points[i].y / Cell));
                if (!_grid.TryGetValue(key, out var list)) _grid[key] = list = new List<int>();
                list.Add(i);
            }
        }

        static long Key(int x, int y) => ((long)x << 32) ^ (uint)y;

        public Vector2 Tangent(int i)
        {
            var d = Points[Mathf.Min(i + 1, Points.Count - 1)] - Points[Mathf.Max(i - 1, 0)];
            return d.sqrMagnitude > 1e-12f ? d.normalized : Vector2.up;
        }

        /// <summary>Index of the nearest resampled point; <paramref name="dist"/> its distance (∞ beyond <paramref name="maxDist"/>).</summary>
        public int Nearest(Vector2 p, out float dist, float maxDist = 60f)
        {
            int cx = Mathf.FloorToInt(p.x / Cell), cy = Mathf.FloorToInt(p.y / Cell);
            int best = -1;
            float bestD2 = maxDist * maxDist;
            int maxRing = Mathf.CeilToInt(maxDist / Cell) + 1;
            for (int ring = 0; ring <= maxRing; ring++)
            {
                // a point in ring r is at least (r - 1) cells away
                float minD = (ring - 1) * Cell;
                if (ring > 0 && best >= 0 && minD * minD > bestD2) break;
                if (ring > 0 && minD > maxDist) break;
                // perimeter cells of the ring only
                int count = ring == 0 ? 1 : 8 * ring;
                for (int k = 0; k < count; k++)
                {
                    int dx, dy;
                    if (ring == 0) { dx = 0; dy = 0; }
                    else if (k < 2 * ring + 1) { dx = -ring + k; dy = -ring; }
                    else if (k < 4 * ring + 2) { dx = -ring + (k - 2 * ring - 1); dy = ring; }
                    else if (k < 6 * ring + 1) { dx = -ring; dy = -ring + 1 + (k - 4 * ring - 2); }
                    else { dx = ring; dy = -ring + 1 + (k - 6 * ring - 1); }
                    if (!_grid.TryGetValue(Key(cx + dx, cy + dy), out var list)) continue;
                    foreach (int i in list)
                    {
                        float d2 = (Points[i] - p).sqrMagnitude;
                        if (d2 < bestD2) { bestD2 = d2; best = i; }
                    }
                }
            }
            dist = best >= 0 ? Mathf.Sqrt(bestD2) : float.PositiveInfinity;
            return best;
        }

        /// <summary>Point and tangent at arclength <paramref name="s"/>.</summary>
        public Vector2 At(float s, out Vector2 tangent)
        {
            s = Mathf.Clamp(s, 0f, Length);
            int lo = 0, hi = S.Count - 1;
            while (hi - lo > 1)
            {
                int mid = (lo + hi) / 2;
                if (S[mid] <= s) lo = mid; else hi = mid;
            }
            float seg = S[hi] - S[lo];
            float t = seg > 0 ? (s - S[lo]) / seg : 0f;
            tangent = Tangent(lo);
            return Vector2.Lerp(Points[lo], Points[hi], t);
        }

        /// <summary>Arclength of the resampled point nearest to <paramref name="p"/>.</summary>
        public float Project(Vector2 p)
        {
            int i = Nearest(p, out _, 1000f);
            return i >= 0 ? S[i] : 0f;
        }
    }
}
