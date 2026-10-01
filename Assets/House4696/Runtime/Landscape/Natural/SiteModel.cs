using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Landscape.Natural
{
    /// <summary>Zones of the natural site: where lawn, beds, the stream banks and the plot edge are.</summary>
    public enum Zone { Outside, House, Water, Path, Lawn, Rim, Bank, Bed, Back }

    /// <summary>
    /// Height model of the natural preset (port of tools/landscape/garden/site.py): a slope with a soft undulation,
    /// the house on a level pad at grade 0, streams carved in as level pools stepping down in cascades, paths.
    /// Distances to streams and paths are precomputed on a 0.25 m grid over <see cref="Area"/>.
    /// </summary>
    public sealed class SiteModel
    {
        public sealed class Pool { public float S0, S1, Level; }

        public sealed class Cascade
        {
            public float S, Top, Bottom;
            /// <summary>Tongues of water between the lip stones: lateral position -1..1 and half width (fractions of the half width).</summary>
            public readonly List<Vector2> Tongues = new List<Vector2>();
        }

        public sealed class Stream
        {
            public StreamDef Def;
            public Polyline2 Line;
            public readonly List<Pool> Pools = new List<Pool>();
            public readonly List<Cascade> Cascades = new List<Cascade>();
            internal float Seed;

            public float HalfWidth(float s)
            {
                float w = Def.Width * (1f + 0.3f * (Mathf.PerlinNoise(s / 7f + Seed, 0.5f) * 2f - 1f));
                foreach (var c in Cascades)
                {
                    float k = s - c.S;
                    if (k > 0f && k < 3.5f) w *= 1f + 0.2f * Mathf.Sin(Mathf.PI * k / 3.5f);
                }
                return 0.5f * Mathf.Max(0.4f, w);
            }

            public Pool PoolAt(float s)
            {
                foreach (var p in Pools) if (s <= p.S1) return p;
                return Pools[Pools.Count - 1];
            }
        }

        public sealed class Path
        {
            public SitePathDef Def;
            public Polyline2 Line;
        }

        /// <summary>
        /// A hard surface graded into the ground: a plane fitted to the ground under it (a drive follows the slope, a
        /// patio by the house sits at its floor), or level at <see cref="SiteAreaDef.Y"/>.
        /// </summary>
        public sealed class HardArea
        {
            public SiteAreaDef Def;
            public Vector2[] Outline;
            public Rect Bounds;
            public Vector2 Centre;
            /// <summary>Surface height at the centre and its slope along x and z (m per m).</summary>
            public float Level, SlopeX, SlopeZ;
            public float HeightAt(float x, float z) => Level + SlopeX * (x - Centre.x) + SlopeZ * (z - Centre.y);
        }

        public sealed class Hedge
        {
            public SiteHedgeDef Def;
            public Rect Bounds;
        }

        public readonly SiteDef Def;
        public readonly TerrainDef Terrain;
        public readonly PlantingDef Planting;
        /// <summary>House footprint (plan x, z).</summary>
        public readonly Rect House;
        /// <summary>Plot = fence line.</summary>
        public readonly Rect Plot;
        /// <summary>Area of the detailed terrain (plot + margin).</summary>
        public readonly Rect Area;
        public readonly List<Stream> Streams = new List<Stream>();
        public readonly List<Path> Paths = new List<Path>();
        public readonly List<HardArea> Areas = new List<HardArea>();
        public readonly List<Hedge> Hedges = new List<Hedge>();
        /// <summary>Styles that keep the open ground as lawn (flowers only in explicit beds and borders).</summary>
        readonly bool _lawnGround, _border;
        public bool LawnGround => _lawnGround;

        readonly Vector2 _slopeDir;
        readonly float _slopeLo, _slopeHi;
        readonly int _seed;

        // distance fields over Area
        public const float FieldCell = 0.25f;
        const float StreamReach = 14f, PathReach = 8f;
        readonly int _fw, _fh;
        readonly float[] _streamDist;
        readonly int[] _streamIdx;         // stream index * 1e6 + point index
        readonly float[] _pathDist;

        /// <summary>The plot of a site: its <c>plot</c>, or the house footprint plus 18 m.</summary>
        public static Rect PlotOf(SiteDef def, Rect house) =>
            def.Plot != null && def.Plot.Length == 4
                ? Rect.MinMaxRect(def.Plot[0], def.Plot[1], def.Plot[2], def.Plot[3])
                : Rect.MinMaxRect(house.xMin - 18f, house.yMin - 18f, house.xMax + 18f, house.yMax + 18f);

        /// <param name="extraPaths">Paths the generator adds itself (the approach to the entrance).</param>
        public SiteModel(SiteDef def, Rect house, float margin = 16f, IEnumerable<SitePathDef> extraPaths = null)
        {
            Def = def;
            Terrain = def.Terrain ?? new TerrainDef();
            Planting = def.Planting ?? new PlantingDef();
            string style = string.IsNullOrEmpty(Planting.Style) ? "perennial" : Planting.Style;
            _lawnGround = style == "garden" || style == "lawn" || style == "none";
            _border = style == "garden";
            House = house;
            Plot = PlotOf(def, house);
            // square (the terrain heightmap is square), centred on the plot
            float side = Mathf.Max(Plot.width, Plot.height) + 2f * margin;
            Area = new Rect(Plot.center.x - side / 2f, Plot.center.y - side / 2f, side, side);
            _seed = Terrain.Seed;
            float a = Terrain.SlopeAzimuth * Mathf.Deg2Rad;
            _slopeDir = new Vector2(Mathf.Sin(a), Mathf.Cos(a));
            // the slope levels off a little beyond the plot so the far land does not climb forever
            float lo = float.MaxValue, hi = float.MinValue;
            foreach (var c in new[] { new Vector2(Plot.xMin, Plot.yMin), new Vector2(Plot.xMax, Plot.yMin), new Vector2(Plot.xMin, Plot.yMax), new Vector2(Plot.xMax, Plot.yMax) })
            {
                float d = Vector2.Dot(c - house.center, _slopeDir);
                lo = Mathf.Min(lo, d); hi = Mathf.Max(hi, d);
            }
            _slopeLo = lo - margin; _slopeHi = hi + margin;

            _fw = Mathf.CeilToInt(Area.width / FieldCell) + 1;
            _fh = Mathf.CeilToInt(Area.height / FieldCell) + 1;
            _streamDist = Fill(new float[_fw * _fh], float.PositiveInfinity);
            _streamIdx = new int[_fw * _fh];
            _pathDist = Fill(new float[_fw * _fh], float.PositiveInfinity);

            int si = 0;
            foreach (var sd in def.Streams)
            {
                if (sd.Path == null || sd.Path.Count < 2) continue;
                var st = new Stream { Def = sd, Line = new Polyline2(sd.Path, 0.08f), Seed = 13.7f * (si + 1) };
                Streams.Add(st);
                Stamp(st.Line, StreamReach, _streamDist, _streamIdx, si * 1000000);
                si++;
            }
            var allPaths = new List<SitePathDef>(def.Paths);
            if (extraPaths != null) allPaths.AddRange(extraPaths);
            foreach (var pd in allPaths)
            {
                if (pd.Path == null || pd.Path.Count < 2) continue;
                var p = new Path { Def = pd, Line = new Polyline2(pd.Path, 0.1f) };
                Paths.Add(p);
                StampPath(p);
            }
            foreach (var ad in def.Areas)
            {
                if (ad.Outline == null || ad.Outline.Count < 3) continue;
                var o = Generation.Polygon.CounterClockwise(ad.Outline).ToArray();
                var b = Generation.Polygon.Bounds(o);
                var area = new HardArea { Def = ad, Outline = o, Bounds = b, Centre = Generation.Polygon.Centroid(o) };
                if (ad.Y.HasValue) area.Level = ad.Y.Value;
                else FitPlane(area);
                Areas.Add(area);
            }
            foreach (var hd in def.Hedges)
            {
                if (hd.Path == null || hd.Path.Count < 2) continue;
                var b = Generation.Polygon.Bounds(hd.Path);
                float g = hd.Width * 0.5f + 0.3f;
                Hedges.Add(new Hedge { Def = hd, Bounds = Rect.MinMaxRect(b.xMin - g, b.yMin - g, b.xMax + g, b.yMax + g) });
            }
            for (int i = 0; i < Streams.Count; i++) BuildPools(Streams[i], i);
        }

        /// <summary>Plan distance from a point to a polygon (0 inside).</summary>
        public static float DistanceToPolygon(IList<Vector2> poly, Vector2 p)
        {
            if (Generation.Polygon.Contains(poly, p)) return 0f;
            float best = float.MaxValue;
            for (int i = 0; i < poly.Count; i++)
                best = Mathf.Min(best, Generation.StairGeometry.DistanceToSegment(p, poly[i], poly[(i + 1) % poly.Count]));
            return best;
        }

        /// <summary>The area at a point (null: none).</summary>
        public HardArea AreaAt(float x, float z, float margin = 0f)
        {
            var p = new Vector2(x, z);
            foreach (var a in Areas)
            {
                if (x < a.Bounds.xMin - margin || x > a.Bounds.xMax + margin || z < a.Bounds.yMin - margin || z > a.Bounds.yMax + margin) continue;
                if (margin <= 0f ? Generation.Polygon.Contains(a.Outline, p) : DistanceToPolygon(a.Outline, p) <= margin) return a;
            }
            return null;
        }

        /// <summary>Is the point within <paramref name="margin"/> of a hedge's body?</summary>
        public bool NearHedge(float x, float z, float margin)
        {
            var p = new Vector2(x, z);
            foreach (var h in Hedges)
            {
                if (!h.Bounds.Contains(p)) continue;
                var path = h.Def.Path;
                for (int i = 0; i + 1 < path.Count; i++)
                    if (Generation.StairGeometry.DistanceToSegment(p, path[i], path[i + 1]) < h.Def.Width * 0.5f + margin) return true;
            }
            return false;
        }

        static float[] Fill(float[] a, float v) { for (int i = 0; i < a.Length; i++) a[i] = v; return a; }

        void Stamp(Polyline2 line, float reach, float[] dist, int[] idx, int tag)
        {
            int r = Mathf.CeilToInt(reach / FieldCell);
            for (int i = 0; i < line.Points.Count; i += 2)
            {
                var p = line.Points[i];
                int cx = Mathf.RoundToInt((p.x - Area.xMin) / FieldCell), cy = Mathf.RoundToInt((p.y - Area.yMin) / FieldCell);
                for (int y = Mathf.Max(0, cy - r); y <= Mathf.Min(_fh - 1, cy + r); y++)
                for (int x = Mathf.Max(0, cx - r); x <= Mathf.Min(_fw - 1, cx + r); x++)
                {
                    float dx = Area.xMin + x * FieldCell - p.x, dy = Area.yMin + y * FieldCell - p.y;
                    float d = dx * dx + dy * dy;
                    int k = y * _fw + x;
                    if (d < dist[k] * dist[k]) { dist[k] = Mathf.Sqrt(d); if (idx != null) idx[k] = tag + i; }
                }
            }
        }

        void StampPath(Path p)
        {
            var tmp = Fill(new float[_fw * _fh], float.PositiveInfinity);
            Stamp(p.Line, PathReach, tmp, null, 0);
            float half = p.Def.Width * 0.5f;
            for (int k = 0; k < tmp.Length; k++)
                _pathDist[k] = Mathf.Min(_pathDist[k], tmp[k] - half);
        }

        int FieldIndex(float x, float z)
        {
            int fx = Mathf.RoundToInt((x - Area.xMin) / FieldCell), fy = Mathf.RoundToInt((z - Area.yMin) / FieldCell);
            if (fx < 0 || fy < 0 || fx >= _fw || fy >= _fh) return -1;
            return fy * _fw + fx;
        }

        // ------------------------------------------------------------------ natural ground

        float Fbm(float x, float z, int octaves, float offset)
        {
            float amp = 1f, freq = 1f, sum = 0f, norm = 0f;
            for (int o = 0; o < octaves; o++)
            {
                sum += amp * (Mathf.PerlinNoise(x * freq + offset + _seed * 0.137f, z * freq - offset + _seed * 0.071f) * 2f - 1f);
                norm += amp; amp *= 0.5f; freq *= 2f;
            }
            return sum / norm;
        }

        /// <summary>Ground without the pad and the streams: slope (levelling off beyond the plot) and undulation.</summary>
        public float Natural(float x, float z)
        {
            float d = Vector2.Dot(new Vector2(x, z) - House.center, _slopeDir);
            // soft clamp of the slope coordinate to the plot range (+ margin)
            if (d > _slopeHi) d = _slopeHi + 8f * (1f - Mathf.Exp(-(d - _slopeHi) / 8f));
            if (d < _slopeLo) d = _slopeLo - 8f * (1f - Mathf.Exp(-(_slopeLo - d) / 8f));
            float h = Terrain.Grade * d;
            h += Terrain.Relief * (Fbm(x / 16f, z / 16f, 3, 3.1f) + 0.2f * Fbm(x / 3.5f, z / 3.5f, 2, 7.7f));
            return h;
        }

        /// <summary>Natural ground with the house pad levelled at grade 0.</summary>
        float PadGround(float x, float z)
        {
            float h = Natural(x, z);
            float dx = Mathf.Max(House.xMin - 1.5f - x, 0f, x - House.xMax - 1.5f);
            float dz = Mathf.Max(House.yMin - 1.5f - z, 0f, z - House.yMax - 1.5f);
            float t = Smooth(0f, 5f, Mathf.Sqrt(dx * dx + dz * dz));
            return Mathf.Lerp(0f, h, t);
        }

        /// <summary>Least-squares plane through the ground under an area (sampled on a grid inside it).</summary>
        void FitPlane(HardArea a)
        {
            var b = a.Bounds;
            float step = Mathf.Max(0.5f, Mathf.Max(b.width, b.height) / 16f);
            double n = 0, sx = 0, sz = 0, sh = 0, sxx = 0, szz = 0, sxz = 0, sxh = 0, szh = 0;
            for (float x = b.xMin + step * 0.5f; x < b.xMax; x += step)
            for (float z = b.yMin + step * 0.5f; z < b.yMax; z += step)
            {
                if (!Generation.Polygon.Contains(a.Outline, new Vector2(x, z))) continue;
                double u = x - a.Centre.x, v = z - a.Centre.y, h = PadGround(x, z);
                n++; sx += u; sz += v; sh += h; sxx += u * u; szz += v * v; sxz += u * v; sxh += u * h; szh += v * h;
            }
            if (n < 3) { a.Level = PadGround(a.Centre.x, a.Centre.y); return; }
            // normal equations of h = c + p·u + q·v
            double[,] m = { { n, sx, sz }, { sx, sxx, sxz }, { sz, sxz, szz } };
            double[] r = { sh, sxh, szh };
            double det = Det(m);
            if (System.Math.Abs(det) < 1e-9) { a.Level = (float)(sh / n); return; }
            double Solve(int col)
            {
                var k = (double[,])m.Clone();
                for (int i = 0; i < 3; i++) k[i, col] = r[i];
                return Det(k) / det;
            }
            a.Level = (float)Solve(0); a.SlopeX = (float)Solve(1); a.SlopeZ = (float)Solve(2);
        }

        static double Det(double[,] m) =>
            m[0, 0] * (m[1, 1] * m[2, 2] - m[1, 2] * m[2, 1]) - m[0, 1] * (m[1, 0] * m[2, 2] - m[1, 2] * m[2, 0]) + m[0, 2] * (m[1, 0] * m[2, 1] - m[1, 1] * m[2, 0]);

        /// <summary>Natural ground with the house pad levelled at grade 0 and the hard areas graded in.</summary>
        public float Ground(float x, float z)
        {
            float h = PadGround(x, z);
            const float blend = 3f;   // the ground eases into a paved area over this distance
            HardArea nearest = null;
            float nd = blend;
            var p = new Vector2(x, z);
            foreach (var a in Areas)
            {
                if (x < a.Bounds.xMin - blend || x > a.Bounds.xMax + blend || z < a.Bounds.yMin - blend || z > a.Bounds.yMax + blend) continue;
                float d = DistanceToPolygon(a.Outline, p);
                if (d <= 0f) return a.HeightAt(x, z);          // on the area: its surface (adjacent areas do not fight)
                if (d < nd) { nd = d; nearest = a; }
            }
            return nearest == null ? h : Mathf.Lerp(nearest.HeightAt(x, z), h, Smooth(0.3f, blend, nd));
        }

        // ------------------------------------------------------------------ streams

        void BuildPools(Stream st, int index)
        {
            var line = st.Line;
            var cuts = new List<float>();
            if (st.Def.Cascades != null && st.Def.Cascades.Count > 0)
                foreach (var c in st.Def.Cascades) cuts.Add(line.Project(c));
            else
            {
                // a cascade wherever the ground along the stream has dropped ~0.55 m since the last one
                float refH = Ground(line.Points[0].x, line.Points[0].y), last = -10f;
                for (int i = 0; i < line.Points.Count; i += 4)
                {
                    float g = Ground(line.Points[i].x, line.Points[i].y);
                    if (refH - g > 0.55f && line.S[i] - last > 3f && line.S[i] > 1f && line.S[i] < line.Length - 1f)
                    {
                        cuts.Add(line.S[i]); last = line.S[i]; refH = g;
                    }
                }
            }
            cuts.Sort();
            var bounds = new List<float> { 0f };
            bounds.AddRange(cuts);
            bounds.Add(line.Length);
            for (int i = 0; i < bounds.Count - 1; i++)
            {
                // level at the lowest ground along the pool, a little below it
                float low = float.MaxValue;
                for (int k = 0; k < line.Points.Count; k++)
                    if (line.S[k] >= bounds[i] && line.S[k] <= bounds[i + 1])
                        low = Mathf.Min(low, Ground(line.Points[k].x, line.Points[k].y));
                if (st.Pools.Count > 0) low = Mathf.Min(low, st.Pools[st.Pools.Count - 1].Level + 0.2f - 0.05f);
                st.Pools.Add(new Pool { S0 = bounds[i], S1 = bounds[i + 1], Level = low - 0.2f });
            }
            var rng = new Core.Rng(_seed + 5 + index * 17);
            for (int i = 0; i < st.Pools.Count - 1; i++)
            {
                var c = new Cascade { S = st.Pools[i].S1, Top = st.Pools[i].Level, Bottom = st.Pools[i + 1].Level };
                int n = rng.Value() < 0.35f ? 2 : 3;
                var slots = new List<float>();
                for (int k = 0; k < n; k++) slots.Add(rng.Range(-0.55f, 0.55f));
                slots.Sort();
                foreach (float u in slots)
                    if (c.Tongues.TrueForAll(t => Mathf.Abs(u - t.x) > 0.34f)) c.Tongues.Add(new Vector2(u, rng.Range(0.1f, 0.19f)));
                if (c.Tongues.Count == 0) c.Tongues.Add(new Vector2(0f, 0.18f));
                st.Cascades.Add(c);
            }
        }

        /// <summary>Nearest stream at a point: distance to its centre line, arclength, half width, water level.</summary>
        public bool StreamAt(float x, float z, out float dist, out float s, out float halfWidth, out float level, out Stream stream)
        {
            dist = float.PositiveInfinity; s = 0; halfWidth = 0; level = 0; stream = null;
            if (Streams.Count == 0) return false;
            int k = FieldIndex(x, z);
            if (k >= 0)
            {
                dist = _streamDist[k];
                if (float.IsInfinity(dist)) return false;
                int tag = _streamIdx[k];
                stream = Streams[tag / 1000000];
                s = stream.Line.S[tag % 1000000];
            }
            else
            {
                // outside the field: direct query (rare: far land, props)
                foreach (var st in Streams)
                {
                    int i = st.Line.Nearest(new Vector2(x, z), out float d, StreamReach);
                    if (i >= 0 && d < dist) { dist = d; stream = st; s = st.Line.S[i]; }
                }
                if (stream == null) return false;
            }
            halfWidth = stream.HalfWidth(s);
            level = stream.PoolAt(s).Level;
            return true;
        }

        /// <summary>Distance to the nearest path edge (negative on the path).</summary>
        public float PathDistance(float x, float z)
        {
            int k = FieldIndex(x, z);
            if (k >= 0) return _pathDist[k];
            float best = float.PositiveInfinity;
            foreach (var p in Paths)
            {
                if (p.Line.Nearest(new Vector2(x, z), out float d, PathReach) >= 0) best = Mathf.Min(best, d - p.Def.Width / 2);
            }
            return best;
        }

        /// <summary>Final height: ground with the stream beds and banks carved in.</summary>
        public float Height(float x, float z)
        {
            float nat = Ground(x, z);
            if (!StreamAt(x, z, out float d, out _, out float hw, out float w, out var st)) return nat;
            if (d < hw)
            {
                float t = d / hw;
                float depth = st.Def.Depth;
                float bed = w - depth * (1f - t * t) - 0.03f + 0.05f * (Mathf.PerlinNoise(x * 1.7f, z * 1.7f) * 2f - 1f);
                return Mathf.Min(nat, bed);
            }
            float cut = w + 0.04f + (d - hw) * 0.55f;                   // banks at most ~29°
            float floor = w + 0.06f - Mathf.Max(0f, d - hw - 1.2f) * 0.35f;   // levee where the ground dips under the water
            return Mathf.Min(Mathf.Max(nat, floor), cut);
        }

        // ------------------------------------------------------------------ zones

        public bool InPlot(float x, float z, float margin = 0f) =>
            x >= Plot.xMin + margin && x <= Plot.xMax - margin && z >= Plot.yMin + margin && z <= Plot.yMax - margin;

        /// <summary>Built-over ground outside the house rectangle (pools): nothing grows there.</summary>
        public readonly List<Vector2[]> Hard = new List<Vector2[]>();

        public bool InHouse(float x, float z, float margin = 0f) =>
            x >= House.xMin - margin && x <= House.xMax + margin && z >= House.yMin - margin && z <= House.yMax + margin || InHard(x, z, margin);

        /// <summary>Inside a pool with its coping and a strip around it (plus <paramref name="margin"/>)?</summary>
        public bool InHard(float x, float z, float margin = 0f)
        {
            foreach (var h in Hard)
            {
                var b = Generation.Polygon.Bounds(h);
                float m = margin + 0.5f;   // the coping and a strip of paving around the pool
                if (x >= b.xMin - m && x <= b.xMax + m && z >= b.yMin - m && z <= b.yMax + m) return true;
            }
            return false;
        }

        /// <summary>What grows at a point (lawnNoise 0..1 wobbles the lawn edge).</summary>
        public Zone ZoneAt(float x, float z, float lawnNoise = 0.5f)
        {
            if (InHouse(x, z)) return Zone.House;
            bool stream = StreamAt(x, z, out float d, out _, out float hw, out _, out _);
            if (stream && d < hw + 0.15f) return Zone.Water;
            float pd = PathDistance(x, z);
            if (pd < 0f) return Zone.Path;
            var area = AreaAt(x, z);
            if (area != null) return area.Def.Type == "lawn" ? Zone.Lawn : Zone.Path;
            if (NearHedge(x, z, 0.15f)) return Zone.Path;
            if (!InPlot(x, z, 0.3f)) return Zone.Outside;
            if (BedAt(x, z) >= 0) return stream && d < hw + 0.75f ? Zone.Rim : Zone.Bed;
            float lawn = Planting.Lawn * (0.7f + 0.6f * lawnNoise);
            if (pd < lawn || InHouse(x, z, 2.2f) || AreaAt(x, z, 1.2f) != null) return Zone.Lawn;
            if (stream && d < hw + 0.75f) return Zone.Rim;
            if (stream && d < hw + 2.4f) return Zone.Bank;
            bool back = Mathf.Min(Plot.xMax - x, Plot.yMax - z, Mathf.Min(x - Plot.xMin, z - Plot.yMin)) < 3f;
            if (_lawnGround) return back && _border ? Zone.Back : Zone.Lawn;
            if (back) return Zone.Back;
            return Zone.Bed;
        }

        /// <summary>Index of the explicit bed (<see cref="SiteDef.Beds"/>) containing the point, or -1.</summary>
        public int BedAt(float x, float z)
        {
            for (int b = 0; b < Def.Beds.Count; b++)
            {
                var o = Def.Beds[b].Outline;
                if (o == null || o.Count < 3) continue;
                bool inside = false;
                for (int i = 0, j = o.Count - 1; i < o.Count; j = i++)
                    if ((o[i].y > z) != (o[j].y > z) && x < (o[j].x - o[i].x) * (z - o[i].y) / (o[j].y - o[i].y) + o[i].x)
                        inside = !inside;
                if (inside) return b;
            }
            return -1;
        }

        public static float Smooth(float e0, float e1, float x)
        {
            float t = Mathf.Clamp01((x - e0) / (e1 - e0));
            return t * t * (3f - 2f * t);
        }
    }
}
