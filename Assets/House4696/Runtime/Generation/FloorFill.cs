using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// The part of a level's floor slab that no room covers: under partitions and door openings (rooms usually stop at
    /// wall faces), in passages between rooms and in enclosed areas the author left without a room. Without it the
    /// ground shows through every doorway and an upper floor has holes wherever a room is missing.
    /// <para>
    /// Works on a 5 cm raster of the level: the exterior walls (grown by <see cref="HouseContext.SlitMax"/>/2 so small
    /// gaps between them do not leak) separate outside from inside; a region they enclose is indoors unless its
    /// walls face it with their outer side (a courtyard). Filled: indoor cells and cells under interior walls standing on
    /// this floor or under exterior glass screens, not wholly inside a room, not over a stairwell, a double-height room or a pool. The cells are merged
    /// into rectangles: the top is the default floor at the level's floor height, upper levels get a ceiling underside
    /// just above the ceiling plates of the rooms below (so they never share a plane).
    /// </para>
    /// </summary>
    public sealed class FloorFill
    {
        const float Cell = 0.05f;
        /// <summary>Underside of the fill above the rooms' ceiling plates (<see cref="RoomBuilder"/>): no coplanar faces.</summary>
        const float UndersideGap = 0.11f;

        readonly HouseContext _c;
        public FloorFill(HouseContext c) { _c = c; }

        /// <summary>Plan rectangles (x0, z0, x1, z1) of the fill of a level.</summary>
        public List<Rect> Rects(LevelDef L)
        {
            float floorY = L.Elevation;
            var rooms = _c.Doc.Rooms.FindAll(r => _c.Level(r.Level) == L && r.Outline != null && r.Outline.Count >= 3);
            var ext = new List<WallFrame>();
            var inner = new List<WallFrame>();
            foreach (var f in _c.Walls)
            {
                if (f.Exterior && f.Spans(floorY + 0.5f)) ext.Add(f);
                else if (!f.Exterior && Mathf.Abs(f.Y0 - floorY) < 0.05f && f.Y1 > floorY + 0.5f) inner.Add(f);
            }
            var res = new List<Rect>();
            if (ext.Count == 0 && inner.Count == 0) return res;

            // raster frame: everything that may matter, plus a margin for the outside flood
            float grow = HouseContext.SlitMax * 0.5f;
            bool any = false;
            Rect b = default;
            void Add(Rect r) { b = any ? Rect.MinMaxRect(Mathf.Min(b.xMin, r.xMin), Mathf.Min(b.yMin, r.yMin), Mathf.Max(b.xMax, r.xMax), Mathf.Max(b.yMax, r.yMax)) : r; any = true; }
            foreach (var f in ext) Add(Polygon.Bounds(f.PlanBody(grow)));
            foreach (var f in inner) Add(Polygon.Bounds(f.PlanBody()));
            foreach (var r in rooms) Add(Polygon.Bounds(r.Outline));
            // an odd offset keeps grid lines off the (usually round) coordinates of walls and rooms
            float x0 = Mathf.Floor(b.xMin) - 1f + 0.0173f, z0 = Mathf.Floor(b.yMin) - 1f + 0.0137f;
            int nx = Mathf.CeilToInt((b.xMax + 1f - x0) / Cell) + 1, nz = Mathf.CeilToInt((b.yMax + 1f - z0) / Cell) + 1;
            if ((long)nx * nz > 4_000_000) { _c.Warn($"level '{L.Id}': floor fill skipped, the level is too large for its raster"); return res; }
            int N = nx * nz;

            // cell centres: exterior wall bodies, their grown barrier, interior wall bodies
            var extWall = new bool[N];
            var barrier = new bool[N];
            var innerWall = new bool[N];
            var glassWall = new bool[N];
            foreach (var f in ext)
            {
                MarkCentres(f.PlanBody(grow), barrier, x0, z0, nx, nz);
                MarkCentres(f.PlanBody(), extWall, x0, z0, nx, nz);
                // a glass screen is a thin frame in the middle of its band: the floor runs under it
                if (f.Def.System == WallSystem.SteelGlass) MarkCentres(f.PlanBody(), glassWall, x0, z0, nx, nz);
            }
            foreach (var f in inner) MarkCentres(f.PlanBody(), innerWall, x0, z0, nx, nz);

            // outside = flood from the raster border through non-barrier cells, then back over the grown ring (not
            // into walls) so the closing does not push the floor out past the facade
            var outside = new bool[N];
            var q = new Queue<int>();
            for (int i = 0; i < nx; i++) { Seed(i, 0); Seed(i, nz - 1); }
            for (int j = 0; j < nz; j++) { Seed(0, j); Seed(nx - 1, j); }
            void Seed(int i, int j) { int k = j * nx + i; if (!barrier[k] && !outside[k]) { outside[k] = true; q.Enqueue(k); } }
            Flood(q, outside, nx, nz, k => !barrier[k]);
            var ring = new List<int>();
            for (int k = 0; k < N; k++) if (outside[k]) ring.Add(k);
            int steps = Mathf.CeilToInt(grow / Cell) + 1;
            for (int s = 0; s < steps && ring.Count > 0; s++)
            {
                var next = new List<int>();
                foreach (int k in ring)
                    foreach (int n in Neighbours(k, nx, nz))
                        if (!outside[n] && barrier[n] && !extWall[n]) { outside[n] = true; next.Add(n); }
                ring = next;
            }

            // enclosed regions: indoors unless the exterior walls around them face in with their outer side
            var label = new int[N];
            var votes = new List<int> { 0 };
            for (int k = 0; k < N; k++)
            {
                if (outside[k] || extWall[k] || label[k] != 0) continue;
                votes.Add(0);
                int id = votes.Count - 1;
                label[k] = id; q.Enqueue(k);
                Flood(q, null, nx, nz, n => !outside[n] && !extWall[n] && label[n] == 0, n => label[n] = id);
            }
            foreach (var f in ext)
                for (int i = 0; i < 5; i++)
                {
                    float s = Mathf.Lerp(f.S0, f.S1, (i + 0.5f) / 5f);
                    int inIdx = Index(f.Plan(s, -f.T - 0.15f), x0, z0, nx, nz), outIdx = Index(f.Plan(s, 0.15f), x0, z0, nx, nz);
                    if (inIdx >= 0 && label[inIdx] > 0) votes[label[inIdx]]++;
                    if (outIdx >= 0 && label[outIdx] > 0) votes[label[outIdx]]--;
                }

            // cells wholly inside ONE room or wall body need no fill (a cell across two of them may hide a hairline
            // gap between them: it is filled); cells touching a cut-out get none
            var covered = new bool[N];
            var cut = new bool[(nx + 1) * (nz + 1)];
            foreach (var r in rooms) MarkInside(Polygon.CounterClockwise(r.Outline), covered, x0, z0, nx, nz);
            foreach (var f in ext) if (f.Def.System != WallSystem.SteelGlass) MarkInside(f.PlanBody(), covered, x0, z0, nx, nz);
            foreach (var f in inner) MarkInside(f.PlanBody(), covered, x0, z0, nx, nz);
            foreach (var h in _c.FloorCuts(L)) MarkCorners(h, cut, x0, z0, nx, nz);

            var fill = new bool[N];
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                int k = j * nx + i;
                // masonry exterior walls run down through the slab: a cell under one would only poke out of the facade
                bool want = innerWall[k] || glassWall[k] || (!outside[k] && !extWall[k] && label[k] > 0 && votes[label[k]] >= 0);
                if (!want) continue;
                if (covered[k]) continue;
                int c00 = j * (nx + 1) + i, c10 = c00 + 1, c01 = c00 + nx + 1, c11 = c01 + 1;
                if (cut[c00] || cut[c10] || cut[c01] || cut[c11]) continue;
                fill[k] = true;
            }

            // greedy merge: runs along x, stacked along z while the run repeats
            var open = new Dictionary<long, int>();   // (i0, i1) → index in res of the rectangle growing upwards
            for (int j = 0; j <= nz; j++)
            {
                var seen = new Dictionary<long, int>();
                if (j < nz)
                    for (int i = 0; i < nx; i++)
                    {
                        if (!fill[j * nx + i]) continue;
                        int i0 = i;
                        while (i < nx && fill[j * nx + i]) i++;
                        long key = (long)i0 << 32 | (uint)i;
                        if (open.TryGetValue(key, out int ri))
                        {
                            var r = res[ri];
                            r.yMax = z0 + (j + 1) * Cell;
                            res[ri] = r;
                            seen[key] = ri;
                        }
                        else
                        {
                            res.Add(Rect.MinMaxRect(x0 + i0 * Cell, z0 + j * Cell, x0 + i * Cell, z0 + (j + 1) * Cell));
                            seen[key] = res.Count - 1;
                        }
                    }
                open = seen;
            }
            return res;
        }

        /// <summary>Emits the fill of a level into <paramref name="mb"/>.</summary>
        public void Build(LevelDef L, MeshBuilder mb)
        {
            bool lowest = _c.IsLowest(L);
            float top = L.Elevation, bottom = lowest ? L.Elevation - L.Slab + 0.02f : L.Elevation - L.Slab + UndersideGap;
            var mats = BoxMats.All(_c.M.Plaster).With(yp: _c.M.Oak, yn: _c.M.Ceiling);
            if (lowest) mats = mats.Without(yn: true);
            foreach (var r in Rects(L))
                mb.Box(new Vector3(r.xMin, bottom, r.yMin), new Vector3(r.xMax, top, r.yMax), mats);
        }

        static int Index(Vector2 p, float x0, float z0, int nx, int nz)
        {
            int i = Mathf.FloorToInt((p.x - x0) / Cell), j = Mathf.FloorToInt((p.y - z0) / Cell);
            return i < 0 || j < 0 || i >= nx || j >= nz ? -1 : j * nx + i;
        }

        static IEnumerable<int> Neighbours(int k, int nx, int nz)
        {
            int i = k % nx, j = k / nx;
            if (i > 0) yield return k - 1;
            if (i + 1 < nx) yield return k + 1;
            if (j > 0) yield return k - nx;
            if (j + 1 < nz) yield return k + nx;
        }

        static void Flood(Queue<int> q, bool[] mark, int nx, int nz, System.Func<int, bool> pass, System.Action<int> visit = null)
        {
            while (q.Count > 0)
            {
                int k = q.Dequeue();
                foreach (int n in Neighbours(k, nx, nz))
                {
                    if (!pass(n)) continue;
                    if (mark != null) { if (mark[n]) continue; mark[n] = true; }
                    visit?.Invoke(n);
                    q.Enqueue(n);
                }
            }
        }

        /// <summary>Cells whose centre is inside the polygon.</summary>
        static void MarkCentres(IList<Vector2> poly, bool[] a, float x0, float z0, int nx, int nz)
        {
            var bb = Polygon.Bounds(poly);
            int i0 = Mathf.Max(0, Mathf.FloorToInt((bb.xMin - x0) / Cell) - 1), i1 = Mathf.Min(nx - 1, Mathf.CeilToInt((bb.xMax - x0) / Cell));
            int j0 = Mathf.Max(0, Mathf.FloorToInt((bb.yMin - z0) / Cell) - 1), j1 = Mathf.Min(nz - 1, Mathf.CeilToInt((bb.yMax - z0) / Cell));
            for (int j = j0; j <= j1; j++)
            for (int i = i0; i <= i1; i++)
                if (Polygon.Contains(poly, new Vector2(x0 + (i + 0.5f) * Cell, z0 + (j + 0.5f) * Cell))) a[j * nx + i] = true;
        }

        /// <summary>Cells with all four corners inside the polygon.</summary>
        static void MarkInside(IList<Vector2> poly, bool[] a, float x0, float z0, int nx, int nz)
        {
            var bb = Polygon.Bounds(poly);
            int i0 = Mathf.Max(0, Mathf.FloorToInt((bb.xMin - x0) / Cell)), i1 = Mathf.Min(nx, Mathf.CeilToInt((bb.xMax - x0) / Cell));
            int j0 = Mathf.Max(0, Mathf.FloorToInt((bb.yMin - z0) / Cell)), j1 = Mathf.Min(nz, Mathf.CeilToInt((bb.yMax - z0) / Cell));
            int w = i1 - i0 + 1, h = j1 - j0 + 1;
            if (w < 2 || h < 2) return;
            var c = new bool[w * h];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
                c[j * w + i] = Polygon.Contains(poly, new Vector2(x0 + (i0 + i) * Cell, z0 + (j0 + j) * Cell));
            for (int j = 0; j + 1 < h; j++)
            for (int i = 0; i + 1 < w; i++)
                if (c[j * w + i] && c[j * w + i + 1] && c[(j + 1) * w + i] && c[(j + 1) * w + i + 1]) a[(j0 + j) * nx + i0 + i] = true;
        }

        /// <summary>Cell corners inside the polygon (a corner lattice of (nx+1)×(nz+1)).</summary>
        static void MarkCorners(IList<Vector2> poly, bool[] a, float x0, float z0, int nx, int nz)
        {
            var bb = Polygon.Bounds(poly);
            int i0 = Mathf.Max(0, Mathf.FloorToInt((bb.xMin - x0) / Cell)), i1 = Mathf.Min(nx, Mathf.CeilToInt((bb.xMax - x0) / Cell));
            int j0 = Mathf.Max(0, Mathf.FloorToInt((bb.yMin - z0) / Cell)), j1 = Mathf.Min(nz, Mathf.CeilToInt((bb.yMax - z0) / Cell));
            for (int j = j0; j <= j1; j++)
            for (int i = i0; i <= i1; i++)
                if (Polygon.Contains(poly, new Vector2(x0 + i * Cell, z0 + j * Cell))) a[j * (nx + 1) + i] = true;
        }
    }
}
