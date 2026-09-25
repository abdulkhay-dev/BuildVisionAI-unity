using System.Collections.Generic;
using House4696.Core;
using UnityEngine;

namespace House4696.House
{
    /// <summary>
    /// Turns a <see cref="WallSpec"/> into geometry: a structural core split around openings, an exterior
    /// cladding layer (stone slabs, honed plinth, anthracite stucco or vertical battens on a black backing)
    /// and dark metal reveals. Walls are axis aligned, so every piece is emitted as a world-space box with
    /// metric planar UVs; wood battens get per-slat UVs into the plank atlas.
    /// </summary>
    public sealed class FacadeBuilder
    {
        // cladding build-up in front of the structural face (meters)
        public const float StoneT = 0.03f, PlinthT = 0.036f, StuccoT = 0.015f;
        public const float BackingD = 0.006f, SlatD = 0.045f, SlatW = 0.083f, SlatPitch = 0.10f;
        public const float RevealDepth = 0.12f;   // structural face → outer face of window frames

        readonly MaterialLibrary _m;
        public FacadeBuilder(MaterialLibrary m) { _m = m; }

        struct Frame
        {
            public Vector3 O, N, A;
            public Vector3 P(float s, float y, float d) => O + A * s + Vector3.up * y + N * d;

            /// <summary>World AABB of a wall-space box.</summary>
            public void Box(float s0, float s1, float y0, float y1, float d0, float d1, out Vector3 min, out Vector3 max)
            {
                Vector3 a = P(s0, y0, d0), b = P(s1, y1, d1);
                min = Vector3.Min(a, b); max = Vector3.Max(a, b);
            }
        }

        static Frame FrameOf(WallSpec w) => new Frame { O = w.Origin, N = w.Normal, A = w.Axis };

        /// <summary>Maps wall-relative faces (outer, inner, s-, s+, bottom, top) onto world box faces.</summary>
        static BoxMats FaceMats(WallSpec w, Material outer, Material inner, Material sNeg, Material sPos, Material yNeg, Material yPos)
        {
            var b = new BoxMats { YNeg = yNeg, YPos = yPos };
            Vector3 n = w.Normal, a = w.Axis;
            void Put(Vector3 dir, Material m)
            {
                if (dir == Vector3.left) b.XNeg = m; else if (dir == Vector3.right) b.XPos = m;
                else if (dir == Vector3.back) b.ZNeg = m; else if (dir == Vector3.forward) b.ZPos = m;
            }
            Put(Round(n), outer); Put(Round(-n), inner); Put(Round(-a), sNeg); Put(Round(a), sPos);
            return b;
        }

        static Vector3 Round(Vector3 v) => new Vector3(Mathf.Round(v.x), Mathf.Round(v.y), Mathf.Round(v.z));

        Material FinishMat(Finish f) => f == Finish.Stone ? _m.Stone : f == Finish.Plinth ? _m.Plinth : f == Finish.Stucco ? _m.Stucco : _m.SlatBacking;
        static float FinishT(Finish f) => f == Finish.Stone ? StoneT : f == Finish.Plinth ? PlinthT : f == Finish.Stucco ? StuccoT : BackingD;

        public void BuildWall(WallSpec w, MeshBuilder mb, MeshBuilder slats)
        {
            var fr = FrameOf(w);
            float s0 = Mathf.Min(w.ToS(w.From), w.ToS(w.To)), s1 = Mathf.Max(w.ToS(w.From), w.ToS(w.To));
            bool cornerNeg = w.ToS(w.From) < w.ToS(w.To) ? w.CornerAtFrom : w.CornerAtTo;
            bool cornerPos = w.ToS(w.From) < w.ToS(w.To) ? w.CornerAtTo : w.CornerAtFrom;

            var openings = new List<Rect>();
            foreach (var o in w.Openings)
            {
                float a = w.ToS(o.From), b = w.ToS(o.To);
                openings.Add(Rect.MinMaxRect(Mathf.Min(a, b), o.Y0, Mathf.Max(a, b), o.Y1));
            }
            var zones = new List<(Rect r, Finish f)>();
            foreach (var z in w.Zones)
            {
                float a = w.ToS(z.From), b = w.ToS(z.To);
                zones.Add((Rect.MinMaxRect(Mathf.Min(a, b), z.Y0, Mathf.Max(a, b), z.Y1), z.Finish));
            }

            var sBreaks = Breaks(s0, s1, openings, zones, true);
            var yBreaks = Breaks(w.Y0, w.Y1, openings, zones, false);
            int ns = sBreaks.Count - 1, ny = yBreaks.Count - 1;
            var hole = new bool[ns, ny];
            var fin = new Finish[ns, ny];
            for (int i = 0; i < ns; i++)
            for (int j = 0; j < ny; j++)
            {
                var c = new Vector2((sBreaks[i] + sBreaks[i + 1]) * 0.5f, (yBreaks[j] + yBreaks[j + 1]) * 0.5f);
                hole[i, j] = openings.Exists(r => r.Contains(c));
                var f = w.Default;
                foreach (var z in zones) if (z.r.Contains(c)) f = z.f;
                fin[i, j] = f;
            }
            bool Hole(int i, int j) => i >= 0 && j >= 0 && i < ns && j < ny && hole[i, j];

            float T = w.Thickness;
            for (int i = 0; i < ns; i++)
            for (int j = 0; j < ny; j++)
            {
                if (hole[i, j]) continue;
                float sa = sBreaks[i], sb = sBreaks[i + 1], ya = yBreaks[j], yb = yBreaks[j + 1];
                bool hl = Hole(i - 1, j), hr = Hole(i + 1, j), hd = Hole(i, j - 1), hu = Hole(i, j + 1);

                // structural core: outer part (dark reveal faces) and inner part (plaster reveal faces)
                fr.Box(sa, sb, ya, yb, -RevealDepth, 0f, out var mn, out var mx);
                mb.Box(mn, mx, FaceMats(w, null, null, hl ? _m.Frame : null, hr ? _m.Frame : null, hd ? _m.Frame : null, hu ? _m.Frame : null));
                fr.Box(sa, sb, ya, yb, -T, -RevealDepth, out mn, out mx);
                mb.Box(mn, mx, FaceMats(w, null, _m.InteriorWall, hl ? _m.InteriorWall : null, hr ? _m.InteriorWall : null,
                    hd ? _m.InteriorWall : null, hu ? _m.InteriorWall : null));

                // cladding
                var f = fin[i, j];
                float ca = sa, cb = sb;
                float t = FinishT(f) + (f == Finish.Wood ? SlatD - BackingD : 0f);
                if (i == 0 && cornerNeg) ca -= t;
                if (i == ns - 1 && cornerPos) cb += t;
                if (f == Finish.Wood)
                {
                    fr.Box(ca, cb, ya, yb, 0f, BackingD, out mn, out mx);
                    mb.Box(mn, mx, FaceMats(w, _m.SlatBacking, null, hl ? _m.Frame : null, hr ? _m.Frame : null, hd ? _m.Frame : null, hu ? _m.Frame : null));
                }
                else
                {
                    var mat = FinishMat(f);
                    fr.Box(ca, cb, ya, yb, 0f, FinishT(f), out mn, out mx);
                    bool topExposed = hu || (j == ny - 1 && f == Finish.Plinth);
                    bool plinthTop = j + 1 < ny && fin[i, j + 1] != Finish.Plinth && f == Finish.Plinth && !hole[i, j + 1];
                    mb.Box(mn, mx, FaceMats(w, mat, null, hl ? mat : null, hr ? mat : null, hd ? mat : null,
                        (topExposed || plinthTop) ? mat : null));
                }
            }

            // battens: vertical runs of wood cells per column, on a world-aligned slat grid
            for (int i = 0; i < ns; i++)
            {
                int j = 0;
                while (j < ny)
                {
                    if (hole[i, j] || fin[i, j] != Finish.Wood) { j++; continue; }
                    int j0 = j;
                    while (j < ny && !hole[i, j] && fin[i, j] == Finish.Wood) j++;
                    float ya = yBreaks[j0], yb = yBreaks[j];
                    float sa = sBreaks[i], sb = sBreaks[i + 1];
                    if (i == 0 && cornerNeg) sa -= SlatD;
                    if (i == ns - 1 && cornerPos) sb += SlatD;
                    EmitSlats(fr, slats, sa, sb, ya, yb, StableHash(w.Name));
                }
            }
        }

        void EmitSlats(Frame fr, MeshBuilder mb, float sa, float sb, float ya, float yb, int seed)
        {
            int k0 = Mathf.FloorToInt(sa / SlatPitch) - 1, k1 = Mathf.CeilToInt(sb / SlatPitch) + 1;
            float gap = (SlatPitch - SlatW) * 0.5f;
            for (int k = k0; k <= k1; k++)
            {
                float a = k * SlatPitch + gap, b = a + SlatW;
                a = Mathf.Max(a, sa); b = Mathf.Min(b, sb);
                if (b - a < SlatW * 0.3f) continue;
                int plank = (int)(Noise.Hash(k, seed & 0xffff, 7) % 8);
                float u0 = plank / 8f + 0.01f, u1 = (plank + 1) / 8f - 0.01f;
                float v = Noise.Hash01(k, 3, seed & 0xffff) * 2f;
                mb.Slat(fr.O, fr.N, a, b, ya, yb, BackingD, SlatD, _m.Wood, u0, u1, v);
            }
        }

        static int StableHash(string s)
        {
            unchecked
            {
                uint h = 2166136261;
                foreach (char c in s) { h ^= c; h *= 16777619; }
                return (int)(h & 0x7fffffff);
            }
        }

        static List<float> Breaks(float lo, float hi, List<Rect> openings, List<(Rect r, Finish f)> zones, bool horizontal)
        {
            var list = new List<float> { lo, hi };
            void Add(float v) { if (v > lo + 1e-4f && v < hi - 1e-4f) list.Add(v); }
            foreach (var r in openings) { Add(horizontal ? r.xMin : r.yMin); Add(horizontal ? r.xMax : r.yMax); }
            foreach (var z in zones) { Add(horizontal ? z.r.xMin : z.r.yMin); Add(horizontal ? z.r.xMax : z.r.yMax); }
            list.Sort();
            var outList = new List<float>();
            foreach (var v in list) if (outList.Count == 0 || v - outList[outList.Count - 1] > 1e-4f) outList.Add(v);
            return outList;
        }

        // ------------------------------------------------------------------ windows & doors

        /// <summary>Frame, mullions/transoms and glass for one opening. Glass goes to its own builder (transparent sorting).</summary>
        static bool IsDoor(Opening o) => o.Kind == OpeningKind.EntryDoor || o.Kind == OpeningKind.SolidDoor;

        /// <summary>Frame profile of an opening: frame width, mullion width and the depth range of the frame.</summary>
        static void Profile(Opening o, out float fw, out float mw, out float d0, out float d1)
        {
            bool big = o.Kind == OpeningKind.Glazing || o.Columns > 1 && (o.Y1 - o.Y0) > 3f;
            fw = o.Kind == OpeningKind.Glazing ? 0.085f : 0.065f;
            mw = o.Kind == OpeningKind.Glazing ? 0.075f : 0.055f;
            d0 = -RevealDepth;
            d1 = -RevealDepth - (big ? 0.11f : 0.08f);
        }

        /// <summary>
        /// Hinge of a door leaf built by <see cref="BuildOpening"/>: bottom point of the hinge line (on the frame
        /// jamb at the lower "s" end) and the horizontal direction into the house.
        /// </summary>
        public static void DoorHinge(WallSpec w, Opening o, out Vector3 hinge, out Vector3 inward)
        {
            var fr = FrameOf(w);
            float sa = Mathf.Min(w.ToS(o.From), w.ToS(o.To));
            Profile(o, out float fw, out _, out float d0, out float d1);
            hinge = fr.P(sa + fw, o.Y0, (d0 + d1) * 0.5f);
            inward = -fr.N;
        }

        /// <param name="leaf">Receives the movable door leaf (doors only); null puts it into <paramref name="frames"/>.</param>
        public void BuildOpening(WallSpec w, Opening o, MeshBuilder frames, MeshBuilder glass, MeshBuilder curtains, MeshBuilder leaf = null)
        {
            var fr = FrameOf(w);
            float sa = Mathf.Min(w.ToS(o.From), w.ToS(o.To)), sb = Mathf.Max(w.ToS(o.From), w.ToS(o.To));
            float ya = o.Y0, yb = o.Y1;
            Profile(o, out float fw, out float mw, out float d0, out float d1);
            var fm = _m.Frame;

            void BarTo(MeshBuilder target, float s0, float s1, float y0, float y1, float dd0, float dd1, Material m)
            {
                fr.Box(s0, s1, y0, y1, dd1, dd0, out var mn, out var mx);
                target.Box(mn, mx, BoxMats.All(m));
            }
            void Bar(float s0, float s1, float y0, float y1, float dd0, float dd1, Material m) => BarTo(frames, s0, s1, y0, y1, dd0, dd1, m);

            // outer frame
            Bar(sa, sa + fw, ya, yb, d0, d1, fm);
            Bar(sb - fw, sb, ya, yb, d0, d1, fm);
            Bar(sa, sb, yb - fw, yb, d0, d1, fm);
            Bar(sa, sb, ya, ya + fw, d0, d1, fm);

            float gd = (d0 + d1) * 0.5f;
            if (IsDoor(o))
            {
                var lb = leaf ?? frames;
                // door leaf (bottom profile sits 5 mm above the sill so the leaf can swing)
                var leafMat = o.Kind == OpeningKind.EntryDoor ? _m.GlassDoor : _m.FurnitureDark;
                BarTo(lb, sa + fw, sb - fw, ya + fw + 0.005f, yb - fw, gd + 0.02f, gd - 0.03f, leafMat);
                // leaf profile
                float lw = 0.05f;
                BarTo(lb, sa + fw, sa + fw + lw, ya + fw, yb - fw, d0 - 0.005f, gd - 0.02f, fm);
                BarTo(lb, sb - fw - lw, sb - fw, ya + fw, yb - fw, d0 - 0.005f, gd - 0.02f, fm);
                BarTo(lb, sa + fw, sb - fw, yb - fw - lw, yb - fw, d0 - 0.005f, gd - 0.02f, fm);
                BarTo(lb, sa + fw, sb - fw, ya + fw + 0.005f, ya + fw + 0.005f + lw * 1.5f, d0 - 0.005f, gd - 0.02f, fm);
                if (o.Kind == OpeningKind.EntryDoor)
                {
                    // long vertical pull handle on the lock side
                    float hs = sb - fw - 0.12f;
                    BarTo(lb, hs - 0.015f, hs + 0.015f, ya + 0.7f, ya + 1.9f, d0 + 0.06f, d0 + 0.03f, _m.Steel);
                    BarTo(lb, hs - 0.012f, hs + 0.012f, ya + 0.75f, ya + 0.78f, d0 + 0.03f, d0 - 0.01f, _m.Steel);
                    BarTo(lb, hs - 0.012f, hs + 0.012f, ya + 1.82f, ya + 1.85f, d0 + 0.03f, d0 - 0.01f, _m.Steel);
                }
                return;
            }

            // mullions
            var paneS = new List<float> { sa + fw };
            for (int c = 1; c < o.Columns; c++)
            {
                float sc = Mathf.Lerp(sa, sb, c / (float)o.Columns);
                Bar(sc - mw * 0.5f, sc + mw * 0.5f, ya + fw, yb - fw, d0, d1, fm);
                paneS.Add(sc - mw * 0.5f); paneS.Add(sc + mw * 0.5f);
            }
            paneS.Add(sb - fw);
            // transoms
            var paneY = new List<float> { ya + fw };
            foreach (var ty in o.Transoms)
            {
                if (ty <= ya || ty >= yb) continue;
                Bar(sa + fw, sb - fw, ty - mw * 0.5f, ty + mw * 0.5f, d0, d1, fm);
                paneY.Add(ty - mw * 0.5f); paneY.Add(ty + mw * 0.5f);
            }
            paneY.Add(yb - fw);

            // glass panes (two faces, so interiors look right too)
            for (int pi = 0; pi + 1 < paneS.Count; pi += 2)
            for (int pj = 0; pj + 1 < paneY.Count; pj += 2)
            {
                fr.Box(paneS[pi], paneS[pi + 1], paneY[pj], paneY[pj + 1], gd - 0.006f, gd + 0.006f, out var mn, out var mx);
                glass.Box(mn, mx, FaceMats(w, _m.Glass, _m.GlassInner, null, null, null, null));
            }

            if (o.Curtain != CurtainSide.None)
            {
                float width = sb - sa - 2 * fw;
                float cw = o.Curtain == CurtainSide.Full ? width : width * o.CurtainFraction;
                float cs0 = o.Curtain == CurtainSide.Right ? sb - fw - cw : sa + fw;
                Curtain(fr, curtains, cs0, cs0 + cw, ya + fw + 0.01f, yb - fw - 0.02f, d1 - 0.28f, o.Curtain == CurtainSide.Full ? 0.045f : 0.05f);
            }
        }

        /// <summary>Sheer curtain with vertical pleats: sinusoidal offset along the wall normal.</summary>
        void Curtain(Frame fr, MeshBuilder mb, float s0, float s1, float y0, float y1, float d, float amp)
        {
            const float period = 0.13f;
            int cols = Mathf.Max(4, Mathf.CeilToInt((s1 - s0) / (period / 8f)));
            var rng = new Rng(Mathf.RoundToInt(s0 * 1000));
            float phase = rng.Range(0, 6.28f);
            float Off(float s) => amp * (0.75f * Mathf.Sin(s / period * Mathf.PI * 2 + phase) + 0.25f * Mathf.Sin(s / period * 2.7f * Mathf.PI + phase * 1.7f));
            for (int c = 0; c < cols; c++)
            {
                float sa = Mathf.Lerp(s0, s1, c / (float)cols), sb = Mathf.Lerp(s0, s1, (c + 1) / (float)cols);
                float da = d + Off(sa), db = d + Off(sb);
                // normal from slope of the pleat
                Vector3 na = PleatNormal(fr, sa, amp, period, phase), nb = PleatNormal(fr, sb, amp, period, phase);
                Vector3 p0 = fr.P(sa, y0, da), p1 = fr.P(sb, y0, db), p2 = fr.P(sb, y1, db), p3 = fr.P(sa, y1, da);
                float u0 = sa / 0.5f, u1 = sb / 0.5f;
                mb.Triangle(p0, p3, p2, na, na, nb, new Vector2(u0, 0), new Vector2(u0, 1), new Vector2(u1, 1), _m.Curtain);
                mb.Triangle(p0, p2, p1, na, nb, nb, new Vector2(u0, 0), new Vector2(u1, 1), new Vector2(u1, 0), _m.Curtain);
            }
        }

        static Vector3 PleatNormal(Frame fr, float s, float amp, float period, float phase)
        {
            float k = Mathf.PI * 2 / period;
            float slope = amp * (0.75f * k * Mathf.Cos(s * k + phase) + 0.25f * 1.35f * k * Mathf.Cos(s * k * 1.35f + phase * 1.7f));
            return (fr.N - fr.A * slope).normalized;
        }
    }
}
