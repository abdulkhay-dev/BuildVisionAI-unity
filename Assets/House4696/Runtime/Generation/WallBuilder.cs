using System.Collections.Generic;
using House4696.Core;
using House4696.Doors;
using House4696.Model;
using House4696.Runtime;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Walls with their openings. Exterior walls: structural core split around openings, cladding layer by finish
    /// zones (stone slabs, honed plinth, stucco, vertical battens on a black backing), dark metal reveals, window
    /// frames with mullions/transoms, glass, sheer curtains and openable door leaves. Interior walls: plastered
    /// partitions with flush oak doors, or steel-framed glass screens. Everything is built in wall space
    /// (<see cref="WallFrame"/>) and transformed, so walls may run at any angle.
    /// </summary>
    public sealed class WallBuilder
    {
        // cladding build-up in front of the structural face (meters)
        public const float StoneT = 0.03f, PlinthT = 0.036f, StuccoT = 0.015f, PaintT = 0.004f;
        public const float BackingD = 0.006f, SlatD = 0.045f, SlatW = 0.083f, SlatPitch = 0.10f;
        public const float RevealDepth = 0.12f;   // structural face → outer face of window frames

        readonly HouseContext _c;
        readonly DoorBlockBuilder _doors;
        public WallBuilder(HouseContext c) { _c = c; _doors = new DoorBlockBuilder(c); }

        /// <summary>The catalogue door of an opening (model, finish, glass, design), or null for the built-in door.</summary>
        static ResolvedDoor Catalogue(OpeningRect o) => DoorSizing.IsCatalogueDoor(o.Def) ? DoorCatalog.Resolve(o.Def) : null;

        struct OpeningRect
        {
            public OpeningDef Def;
            public float S0, S1, Y0, Y1;
            public Rect Rect => Rect.MinMaxRect(S0, Y0, S1, Y1);
        }

        List<OpeningRect> OpeningsOf(WallFrame f)
        {
            var list = new List<OpeningRect>();
            foreach (var o in _c.Doc.Openings)
            {
                if (o.Wall != f.Def.Id) continue;
                float baseY = f.Level.Elevation;
                float sa = f.SAt(o.At), sb = f.SAt(o.At + o.Width);
                float ya = baseY + (o.Type == OpeningType.Door || o.Type == OpeningType.EntryDoor || o.Type == OpeningType.SolidDoor ? Mathf.Max(0f, o.Sill) : o.Sill);
                var r = new OpeningRect { Def = o, S0 = Mathf.Max(sa, f.S0), S1 = Mathf.Min(sb, f.S1), Y0 = Mathf.Max(ya, f.Y0), Y1 = Mathf.Min(ya + o.Height, f.Y1) };
                if (r.S1 - r.S0 < 0.05f || r.Y1 - r.Y0 < 0.05f)
                {
                    _c.Warn($"opening '{o.Id}' lies outside wall '{f.Def.Id}' (at {o.At:0.##}, width {o.Width:0.##}, wall length {f.Length:0.##})");
                    continue;
                }
                list.Add(r);
            }
            return list;
        }

        public void Build(WallFrame f)
        {
            if (f.Def.System == WallSystem.SteelGlass) { SteelGlass(f); return; }
            if (f.Exterior) Exterior(f); else Interior(f);
        }

        // ================================================================== exterior walls
        enum Clad { Stone, Plinth, Stucco, Wood, Paint }

        Clad CladOf(string finish)
        {
            switch (MaterialResolver.Key(MaterialResolver.BaseName(finish)))
            {
                case "stone": case "stonecladding": return Clad.Stone;
                case "plinth": return Clad.Plinth;
                case "stucco": case "render": return Clad.Stucco;
                case "wood": case "battens": case "woodbattens": return Clad.Wood;
                default: return Clad.Paint;
            }
        }

        static float CladT(Clad c) => c == Clad.Stone ? StoneT : c == Clad.Plinth ? PlinthT : c == Clad.Stucco ? StuccoT : c == Clad.Wood ? BackingD : PaintT;

        Material CladMat(Clad c, string finish)
        {
            var L = _c.Lib;
            if (finish != null && finish.IndexOf('#') > 0 && c != Clad.Wood) return _c.Mats.Get(finish, L.Stucco);
            switch (c)
            {
                case Clad.Stone: return L.Stone;
                case Clad.Plinth: return L.Plinth;
                case Clad.Stucco: return L.Stucco;
                case Clad.Wood: return L.SlatBacking;
                default: return _c.Mats.Get(finish, L.Stucco);
            }
        }

        /// <summary>Box in wall space: s, y ranges and d (outward) range; faces: outer, inner, s-, s+, bottom, top.</summary>
        static void WBox(MeshBuilder mb, float s0, float s1, float y0, float y1, float d0, float d1,
                         Material outer, Material inner, Material sNeg, Material sPos, Material yNeg, Material yPos)
        {
            mb.Box(new Vector3(s0, y0, -d1), new Vector3(s1, y1, -d0),
                new BoxMats { ZNeg = outer, ZPos = inner, XNeg = sNeg, XPos = sPos, YNeg = yNeg, YPos = yPos });
        }

        static void WBox(MeshBuilder mb, float s0, float s1, float y0, float y1, float d0, float d1, Material all) =>
            WBox(mb, s0, s1, y0, y1, Mathf.Min(d0, d1), Mathf.Max(d0, d1), all, all, all, all, all, all);

        void Exterior(WallFrame f)
        {
            var L = _c.Lib;
            var core = new MeshBuilder { Transform = f.ToWorld };
            var slats = new MeshBuilder { Transform = f.ToWorld };
            var openings = OpeningsOf(f);
            string defFinish = f.Def.Outside ?? "stucco";
            var zones = new List<(Rect r, string f)>();
            if ((f.Def.Plinth ?? 0f) > 0f) zones.Add((Rect.MinMaxRect(f.S0, f.Y0, f.S1, f.Y0 + f.Def.Plinth.Value), "plinth"));
            foreach (var z in f.Def.Zones)
                zones.Add((Rect.MinMaxRect(f.SAt(Mathf.Min(z.From, z.To)), z.Bottom, f.SAt(Mathf.Max(z.From, z.To)), z.Top), z.Finish));

            // a wall rising above the flat roof behind it is a parapet: outdoors on both sides from the roof top up
            float? parapet = _c.ParapetFrom(f);
            if (parapet.HasValue && parapet.Value > f.Y1 - 0.05f) parapet = null;
            var sBreaks = Breaks(f.S0, f.S1, openings, zones, true);
            var yBreaks = Breaks(f.Y0, f.Y1, openings, zones, false);
            if (parapet.HasValue && parapet.Value > f.Y0 + 0.05f && !yBreaks.Exists(y => Mathf.Abs(y - parapet.Value) < 1e-3f))
            {
                yBreaks.Add(parapet.Value);
                yBreaks.Sort();
            }
            int ns = sBreaks.Count - 1, ny = yBreaks.Count - 1;
            var hole = new bool[ns, ny];
            var fin = new string[ns, ny];
            for (int i = 0; i < ns; i++)
            for (int j = 0; j < ny; j++)
            {
                var c = new Vector2((sBreaks[i] + sBreaks[i + 1]) * 0.5f, (yBreaks[j] + yBreaks[j + 1]) * 0.5f);
                hole[i, j] = openings.Exists(o => o.Rect.Contains(c));
                string fn = defFinish;
                foreach (var z in zones) if (z.r.Contains(c)) fn = z.f;
                fin[i, j] = fn;
            }
            bool Hole(int i, int j) => i >= 0 && j >= 0 && i < ns && j < ny && hole[i, j];
            var plaster = _c.Mats.Get(f.Def.Inside, _c.M.Plaster);
            var frame = L.Frame;

            float T = f.T;
            for (int i = 0; i < ns; i++)
            for (int j = 0; j < ny; j++)
            {
                if (hole[i, j]) continue;
                float sa = sBreaks[i], sb = sBreaks[i + 1], ya = yBreaks[j], yb = yBreaks[j + 1];
                bool hl = Hole(i - 1, j), hr = Hole(i + 1, j), hd = Hole(i, j - 1), hu = Hole(i, j + 1);
                var clad = CladOf(fin[i, j]);
                // the top and the ends are closed too: seen from above (a lower roof, a terrace, an orbit view) or at a
                // free end an open box shows the room through the wall; hidden faces under slabs and in corners cost nothing
                bool top = j == ny - 1, s0 = i == 0, s1 = i == ns - 1;
                bool outdoors = parapet.HasValue && ya >= parapet.Value - 1e-3f;
                var inner = outdoors ? (clad == Clad.Wood ? L.Wood : CladMat(clad, fin[i, j])) : plaster;
                var cap = top ? L.Coping : null;
                var end = clad == Clad.Wood ? L.SlatBacking : CladMat(clad, fin[i, j]);

                // structural core: outer part (dark reveal faces) and inner part (plaster reveal faces)
                WBox(core, sa, sb, ya, yb, -RevealDepth, 0f, null, null, hl ? frame : s0 ? end : null, hr ? frame : s1 ? end : null,
                    hd ? frame : null, hu ? frame : cap);
                WBox(core, sa, sb, ya, yb, -T, -RevealDepth, null, inner, hl || s0 ? inner : null, hr || s1 ? inner : null,
                    hd ? plaster : null, hu ? plaster : cap);

                // cladding
                float ca = sa, cb = sb;
                float t = CladT(clad) + (clad == Clad.Wood ? SlatD - BackingD : 0f);
                if (i == 0 && f.WrapStart) ca -= t;
                if (i == ns - 1 && f.WrapEnd) cb += t;
                if (clad == Clad.Wood)
                {
                    WBox(core, ca, cb, ya, yb, 0f, BackingD, L.SlatBacking, null, hl ? frame : null, hr ? frame : null, hd ? frame : null, hu ? frame : cap);
                }
                else
                {
                    var mat = CladMat(clad, fin[i, j]);
                    bool topExposed = hu || (j == ny - 1 && clad == Clad.Plinth);
                    bool plinthTop = j + 1 < ny && clad == Clad.Plinth && CladOf(fin[i, j + 1]) != Clad.Plinth && !hole[i, j + 1];
                    WBox(core, ca, cb, ya, yb, 0f, CladT(clad), mat, null, hl ? mat : null, hr ? mat : null, hd ? mat : null,
                        (topExposed || plinthTop || top) ? mat : null);
                }
            }

            // metal coping over a parapet (a wall top level with the roof is flashed by the roof's own coping)
            if (parapet.HasValue)
                WBox(core, f.S0 - (f.WrapStart ? 0.05f : 0f), f.S1 + (f.WrapEnd ? 0.05f : 0f), f.Y1, f.Y1 + 0.04f, -T - 0.03f, 0.05f, L.Coping);

            // battens: vertical runs of wood cells per column, on a slat grid aligned with s = 0
            int seed = StableHash(f.Def.Id ?? "wall");
            for (int i = 0; i < ns; i++)
            {
                int j = 0;
                while (j < ny)
                {
                    if (hole[i, j] || CladOf(fin[i, j]) != Clad.Wood) { j++; continue; }
                    int j0 = j;
                    while (j < ny && !hole[i, j] && CladOf(fin[i, j]) == Clad.Wood) j++;
                    float ya = yBreaks[j0], yb = yBreaks[j];
                    float sa = sBreaks[i], sb = sBreaks[i + 1];
                    if (i == 0 && f.WrapStart) sa -= SlatD;
                    if (i == ns - 1 && f.WrapEnd) sb += SlatD;
                    EmitSlats(slats, sa, sb, ya, yb, seed);
                }
            }

            string id = f.Def.Id;
            var wallGo = _c.W.Emit("Wall_" + id, _c.Shell, core);
            if (!slats.IsEmpty) _c.W.Emit("Battens_" + id, wallGo != null ? wallGo.transform : _c.Shell, slats);

            var frames = new MeshBuilder { Transform = f.ToWorld };
            var glass = new MeshBuilder { Transform = f.ToWorld };
            var curtains = new MeshBuilder { Transform = f.ToWorld };
            foreach (var o in openings)
            {
                if (o.Def.Type == OpeningType.Hole) continue;
                var door = Catalogue(o);
                if (door != null)
                {
                    // a catalogue door in a facade wall: casing indoors only, the facade keeps its reveal
                    _doors.Build(f, o.Def, door, o.S0, o.S1, o.Y0, o.Y1, casingOut: false, casingIn: true);
                    Threshold(frames, f, o);
                    continue;
                }
                var leaf = new MeshBuilder { Transform = f.ToWorld };
                ExteriorOpening(o, frames, glass, curtains, leaf);
                if (!leaf.IsEmpty) DoorPivot("Door_" + (o.Def.Id ?? id), f, o, leaf, ExteriorHinge(f, o), -f.N);
            }
            _c.W.Emit("Frames_" + id, _c.Shell, frames);
            _c.W.Emit("Glass_" + id, _c.Shell, glass, castShadows: false);
            _c.W.Emit("Curtains_" + id, _c.Shell, curtains, castShadows: false);
        }

        /// <summary>Height bands of a wall that are structure, not room: slabs of upper levels and the build-up above the top ceiling.</summary>
        List<(float, float)> Spandrels(WallFrame f)
        {
            var bands = new List<(float, float)>();
            void Add(float a, float b)
            {
                a = Mathf.Max(a, f.Y0); b = Mathf.Min(b, f.Y1);
                if (b - a > 0.05f) bands.Add((a, b));
            }
            LevelDef top = null;
            foreach (var l in _c.Doc.Levels)
            {
                if (!_c.IsLowest(l)) Add(l.Elevation - l.Slab, l.Elevation);
                top = l;
            }
            if (top != null) Add(top.Elevation + top.Height, f.Y1);
            return bands;
        }

        void EmitSlats(MeshBuilder mb, float sa, float sb, float ya, float yb, int seed)
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
                mb.Slat(Vector3.zero, Vector3.back, a, b, ya, yb, BackingD, SlatD, _c.Lib.Wood, u0, u1, v);
            }
        }

        public static int StableHash(string s)
        {
            unchecked
            {
                uint h = 2166136261;
                foreach (char ch in s) { h ^= ch; h *= 16777619; }
                return (int)(h & 0x7fffffff);
            }
        }

        static List<float> Breaks(float lo, float hi, List<OpeningRect> openings, List<(Rect r, string f)> zones, bool horizontal)
        {
            var list = new List<float> { lo, hi };
            void Add(float v) { if (v > lo + 1e-4f && v < hi - 1e-4f) list.Add(v); }
            foreach (var o in openings) { Add(horizontal ? o.S0 : o.Y0); Add(horizontal ? o.S1 : o.Y1); }
            if (zones != null)
                foreach (var z in zones) { Add(horizontal ? z.r.xMin : z.r.yMin); Add(horizontal ? z.r.xMax : z.r.yMax); }
            list.Sort();
            var outList = new List<float>();
            foreach (var v in list) if (outList.Count == 0 || v - outList[outList.Count - 1] > 1e-4f) outList.Add(v);
            return outList;
        }

        // ------------------------------------------------------------------ exterior windows & doors
        static bool IsDoor(OpeningType t) => t == OpeningType.EntryDoor || t == OpeningType.SolidDoor || t == OpeningType.Door;

        static void Profile(OpeningRect o, out float fw, out float mw, out float d0, out float d1)
        {
            var t = o.Def.Type;
            bool big = t == OpeningType.Glazing || o.Def.Columns > 1 && (o.Y1 - o.Y0) > 3f;
            fw = t == OpeningType.Glazing ? 0.085f : 0.065f;
            mw = t == OpeningType.Glazing ? 0.075f : 0.055f;
            d0 = -RevealDepth;
            d1 = -RevealDepth - (big ? 0.11f : 0.08f);
        }

        /// <summary>Bottom point of the hinge line of an exterior door leaf (on the jamb at the hinge side).</summary>
        static Vector3 ExteriorHinge(WallFrame f, OpeningRect o)
        {
            Profile(o, out float fw, out _, out float d0, out float d1);
            bool atStart = o.Def.Hinge == Hinge.Start;
            return f.P(atStart ? o.S0 + fw : o.S1 - fw, o.Y0, (d0 + d1) * 0.5f);
        }

        void ExteriorOpening(OpeningRect o, MeshBuilder frames, MeshBuilder glass, MeshBuilder curtains, MeshBuilder leaf)
        {
            var L = _c.Lib;
            float sa = o.S0, sb = o.S1, ya = o.Y0, yb = o.Y1;
            Profile(o, out float fw, out float mw, out float d0, out float d1);
            var fm = L.Frame;

            void BarTo(MeshBuilder target, float s0, float s1, float y0, float y1, float dd0, float dd1, Material m) =>
                WBox(target, s0, s1, y0, y1, dd0, dd1, m);
            void Bar(float s0, float s1, float y0, float y1, float dd0, float dd1, Material m) => BarTo(frames, s0, s1, y0, y1, dd0, dd1, m);

            // outer frame
            Bar(sa, sa + fw, ya, yb, d0, d1, fm);
            Bar(sb - fw, sb, ya, yb, d0, d1, fm);
            Bar(sa, sb, yb - fw, yb, d0, d1, fm);
            Bar(sa, sb, ya, ya + fw, d0, d1, fm);

            float gd = (d0 + d1) * 0.5f;
            if (IsDoor(o.Def.Type))
            {
                var leafMat = o.Def.Type == OpeningType.SolidDoor ? L.FurnitureDark : L.GlassDoor;
                BarTo(leaf, sa + fw, sb - fw, ya + fw + 0.005f, yb - fw, gd + 0.02f, gd - 0.03f, leafMat);
                float lw = 0.05f;
                BarTo(leaf, sa + fw, sa + fw + lw, ya + fw, yb - fw, d0 - 0.005f, gd - 0.02f, fm);
                BarTo(leaf, sb - fw - lw, sb - fw, ya + fw, yb - fw, d0 - 0.005f, gd - 0.02f, fm);
                BarTo(leaf, sa + fw, sb - fw, yb - fw - lw, yb - fw, d0 - 0.005f, gd - 0.02f, fm);
                BarTo(leaf, sa + fw, sb - fw, ya + fw + 0.005f, ya + fw + 0.005f + lw * 1.5f, d0 - 0.005f, gd - 0.02f, fm);
                if (o.Def.Type != OpeningType.SolidDoor)
                {
                    // long vertical pull handle on the lock side
                    float hs = o.Def.Hinge == Hinge.Start ? sb - fw - 0.12f : sa + fw + 0.12f;
                    BarTo(leaf, hs - 0.015f, hs + 0.015f, ya + 0.7f, ya + 1.9f, d0 + 0.06f, d0 + 0.03f, L.Steel);
                    BarTo(leaf, hs - 0.012f, hs + 0.012f, ya + 0.75f, ya + 0.78f, d0 + 0.03f, d0 - 0.01f, L.Steel);
                    BarTo(leaf, hs - 0.012f, hs + 0.012f, ya + 1.82f, ya + 1.85f, d0 + 0.03f, d0 - 0.01f, L.Steel);
                }
                return;
            }

            // mullions
            var paneS = new List<float> { sa + fw };
            for (int c = 1; c < o.Def.Columns; c++)
            {
                float sc = Mathf.Lerp(sa, sb, c / (float)o.Def.Columns);
                Bar(sc - mw * 0.5f, sc + mw * 0.5f, ya + fw, yb - fw, d0, d1, fm);
                paneS.Add(sc - mw * 0.5f); paneS.Add(sc + mw * 0.5f);
            }
            paneS.Add(sb - fw);
            // transoms (heights above the sill)
            var paneY = new List<float> { ya + fw };
            foreach (var th in o.Def.Transoms)
            {
                float ty = ya + th;
                if (ty <= ya || ty >= yb) continue;
                Bar(sa + fw, sb - fw, ty - mw * 0.5f, ty + mw * 0.5f, d0, d1, fm);
                paneY.Add(ty - mw * 0.5f); paneY.Add(ty + mw * 0.5f);
            }
            paneY.Add(yb - fw);

            // glass panes (two faces, so interiors look right too)
            for (int pi = 0; pi + 1 < paneS.Count; pi += 2)
            for (int pj = 0; pj + 1 < paneY.Count; pj += 2)
                WBox(glass, paneS[pi], paneS[pi + 1], paneY[pj], paneY[pj + 1], gd - 0.006f, gd + 0.006f, L.Glass, L.GlassInner, null, null, null, null);

            if (o.Def.Curtain != CurtainType.None)
            {
                float width = sb - sa - 2 * fw;
                float cw = o.Def.Curtain == CurtainType.Full ? width : width * o.Def.CurtainFraction;
                float cs0 = o.Def.Curtain == CurtainType.Right ? sb - fw - cw : sa + fw;
                Curtain(curtains, cs0, cs0 + cw, ya + fw + 0.01f, yb - fw - 0.02f, d1 - 0.28f, o.Def.Curtain == CurtainType.Full ? 0.045f : 0.05f);
            }
        }

        /// <summary>Sheer curtain with vertical pleats: sinusoidal offset along the wall normal (wall space).</summary>
        void Curtain(MeshBuilder mb, float s0, float s1, float y0, float y1, float d, float amp)
        {
            const float period = 0.13f;
            int cols = Mathf.Max(4, Mathf.CeilToInt((s1 - s0) / (period / 8f)));
            var rng = new Rng(Mathf.RoundToInt(s0 * 1000));
            float phase = rng.Range(0, 6.28f);
            float Off(float s) => amp * (0.75f * Mathf.Sin(s / period * Mathf.PI * 2 + phase) + 0.25f * Mathf.Sin(s / period * 2.7f * Mathf.PI + phase * 1.7f));
            Vector3 Nrm(float s)
            {
                float k = Mathf.PI * 2 / period;
                float slope = amp * (0.75f * k * Mathf.Cos(s * k + phase) + 0.25f * 1.35f * k * Mathf.Cos(s * k * 1.35f + phase * 1.7f));
                return (Vector3.back - Vector3.right * slope).normalized;
            }
            var mat = _c.Lib.Curtain;
            for (int c = 0; c < cols; c++)
            {
                float sa = Mathf.Lerp(s0, s1, c / (float)cols), sb = Mathf.Lerp(s0, s1, (c + 1) / (float)cols);
                float da = d + Off(sa), db = d + Off(sb);
                Vector3 na = Nrm(sa), nb = Nrm(sb);
                Vector3 p0 = WallFrame.L(sa, y0, da), p1 = WallFrame.L(sb, y0, db), p2 = WallFrame.L(sb, y1, db), p3 = WallFrame.L(sa, y1, da);
                float u0 = sa / 0.5f, u1 = sb / 0.5f;
                mb.Triangle(p0, p3, p2, na, na, nb, new Vector2(u0, 0), new Vector2(u0, 1), new Vector2(u1, 1), mat);
                mb.Triangle(p0, p2, p1, na, nb, nb, new Vector2(u0, 0), new Vector2(u1, 1), new Vector2(u1, 0), mat);
            }
        }

        /// <summary>
        /// Door leaf on a pivot at its hinge: the leaf mesh keeps world-space vertices, so the child is offset by
        /// -hinge. The leaf moves at runtime, so it is dynamic and gets a kinematic body for its collider.
        /// </summary>
        void DoorPivot(string name, WallFrame f, OpeningRect o, MeshBuilder leaf, Vector3 hinge, Vector3 swingSide, float maxAngle = 95f)
        {
            var pivot = new GameObject(name);
            pivot.transform.SetParent(_c.Doors, false);
            pivot.transform.position = hinge;
            var leafGo = _c.W.Emit("Leaf", pivot.transform, leaf);
            if (leafGo == null) return;
            leafGo.transform.localPosition = -hinge;
            _c.W.MarkDynamic(leafGo);
            Vector3 along = o.Def.Hinge == Hinge.Start ? f.A : -f.A;           // from the hinge towards the lock side
            Vector3 side = o.Def.Swing >= 0 ? swingSide : -swingSide;
            float angle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * along, side) > 0 ? maxAngle : -maxAngle;
            pivot.AddComponent<Door>().OpenAngle = angle;
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
        }

        // ================================================================== interior partitions
        void Interior(WallFrame f)
        {
            var mb = new MeshBuilder { Transform = f.ToWorld };
            var glass = new MeshBuilder { Transform = f.ToWorld };
            var openings = OpeningsOf(f);
            var right = _c.Mats.Get(f.Def.Outside, _c.M.Plaster);   // outer = right side of A→B
            var left = _c.Mats.Get(f.Def.Inside, _c.M.Plaster);
            var sBreaks = Breaks(f.S0, f.S1, openings, null, true);
            var yBreaks = Breaks(f.Y0, f.Y1, openings, null, false);
            int ns = sBreaks.Count - 1, ny = yBreaks.Count - 1;
            bool Hole(int i, int j)
            {
                if (i < 0 || j < 0 || i >= ns || j >= ny) return false;
                var c = new Vector2((sBreaks[i] + sBreaks[i + 1]) * 0.5f, (yBreaks[j] + yBreaks[j + 1]) * 0.5f);
                return openings.Exists(o => o.Rect.Contains(c));
            }
            for (int i = 0; i < ns; i++)
            for (int j = 0; j < ny; j++)
            {
                if (Hole(i, j)) continue;
                // ends, top and bottom are closed too: a partition may stand over a void or next to an open slab edge
                bool hl = Hole(i - 1, j) || i == 0, hr = Hole(i + 1, j) || i == ns - 1, hd = Hole(i, j - 1) || j == 0, hu = Hole(i, j + 1) || j == ny - 1;
                WBox(mb, sBreaks[i], sBreaks[i + 1], yBreaks[j], yBreaks[j + 1], -f.T, 0f, right, left,
                    hl ? left : null, hr ? left : null, hd ? left : null, hu ? left : null);
            }
            foreach (var o in openings)
            {
                if (IsDoor(o.Def.Type) || o.Def.Type == OpeningType.Hole) Threshold(mb, f, o);
                if (IsDoor(o.Def.Type))
                {
                    var door = Catalogue(o);
                    if (door != null) _doors.Build(f, o.Def, door, o.S0, o.S1, o.Y0, o.Y1);
                    else InteriorDoor(f, o);
                }
                else if (o.Def.Type == OpeningType.Window || o.Def.Type == OpeningType.Glazing)
                    WBox(glass, o.S0, o.S1, o.Y0, o.Y1, -f.T * 0.5f - 0.005f, -f.T * 0.5f + 0.005f, _c.M.Glass);
            }
            _c.W.Emit("Partition_" + f.Def.Id, _c.Interior, mb);
            _c.W.Emit("Partition_Glass_" + f.Def.Id, _c.Interior, glass, castShadows: false);
        }

        /// <summary>
        /// Floor under a door in a partition: room slabs stop at the wall faces, so the threshold is filled with a
        /// slab piece (oak top) as deep as the wall and as thick as the level's floor build-up.
        /// </summary>
        void Threshold(MeshBuilder mb, WallFrame f, OpeningRect o)
        {
            float floor = f.Level.Elevation;
            if (o.Y0 > floor + 0.05f) return;
            // 2 mm below the floor: where a room slab already runs under the wall, the room floor wins (no z-fighting)
            WBox(mb, o.S0, o.S1, floor - f.Level.Slab, floor - 0.002f, -f.T, 0f, null, null, null, null, null, _c.M.Oak);
        }

        /// <summary>Flush oak leaf on a pivot at its hinge, black levers on both sides.</summary>
        void InteriorDoor(WallFrame f, OpeningRect o)
        {
            const float t = 0.04f, gap = 0.004f;
            float c = -f.T * 0.5f;
            float s0 = o.S0 + gap, s1 = o.S1 - gap, y0 = o.Y0 + 0.008f, y1 = o.Y1 - gap;
            var leaf = new MeshBuilder { Transform = f.ToWorld };
            WBox(leaf, s0, s1, y0, y1, c - t * 0.5f, c + t * 0.5f, _c.M.OakLight);
            bool atStart = o.Def.Hinge == Hinge.Start;
            float hs = atStart ? s1 - 0.08f : s0 + 0.08f, dir = atStart ? -1f : 1f;
            foreach (float side in new[] { -1f, 1f })
            {
                float o0 = c + side * t * 0.5f, o1 = c + side * (t * 0.5f + 0.055f);
                Vector3 r0 = WallFrame.L(hs, o.Y0 + 1.0f, o0), r1 = WallFrame.L(hs, o.Y0 + 1.0f, o1);
                leaf.Rod(r0, r1, 0.009f, _c.M.BlackMetal);
                leaf.Rod(r1, WallFrame.L(hs + dir * 0.13f, o.Y0 + 1.0f, o1), 0.008f, _c.M.BlackMetal);
            }
            var hinge = f.P(atStart ? s0 : s1, y0, c);
            DoorPivot("Door_" + (o.Def.Id ?? f.Def.Id), f, o, leaf, hinge, -f.N, 100f);
        }

        // ================================================================== steel-framed glass screen
        /// <summary>
        /// Crittall-style screen along the whole wall: thin black steel profiles, clear glass, bars at hand height
        /// and at door-head height, glazed swing doors (openings of a door type) with a transom above.
        /// </summary>
        void SteelGlass(WallFrame f)
        {
            const float t = 0.045f, w = 0.035f;
            float z0 = f.S0, z1 = f.S1, y0 = f.Y0, y1 = f.Y1;
            // transoms from the floor of the wall's level (an upper wall starts under its slab)
            float floorY = Mathf.Max(y0, f.Level.Elevation);
            float bar = floorY + 0.95f, head = floorY + 2.4f;
            float c = -f.T * 0.5f;
            var frame = new MeshBuilder { Transform = f.ToWorld };
            var glass = new MeshBuilder { Transform = f.ToWorld };
            var bm = _c.M.BlackMetal;
            void Prof(MeshBuilder mb, float za, float zb, float ya, float yb) =>
                mb.Bevel(new Vector3(za, ya, -(c + t * 0.5f)), new Vector3(zb, yb, -(c - t * 0.5f)), bm, 0.002f);
            void Pane(MeshBuilder mb, float za, float zb, float ya, float yb) =>
                WBox(mb, za, zb, ya, yb, c - 0.004f, c + 0.004f, _c.M.Glass);

            var doors = OpeningsOf(f).FindAll(o => IsDoor(o.Def.Type));
            doors.Sort((a, b) => a.S0.CompareTo(b.S0));
            Prof(frame, z0, z0 + w, y0, y1); Prof(frame, z1 - w, z1, y0, y1);
            Prof(frame, z0, z1, y1 - w, y1);
            float s = z0 + w;
            void Fixed(float za, float zb)
            {
                if (zb - za < 0.05f) return;
                Prof(frame, za, zb, y0, y0 + w);
                Prof(frame, za, zb, bar - w * 0.5f, bar + w * 0.5f);
                Prof(frame, za, zb, head - w * 0.5f, head + w * 0.5f);
                Pane(glass, za, zb, y0 + w, y1 - w);
            }
            var sill = new MeshBuilder { Transform = f.ToWorld };
            foreach (var d in doors)
            {
                Threshold(sill, f, d);
                float dz0 = d.S0, dz1 = d.S1;
                Fixed(s, dz0 - w);
                Prof(frame, dz0 - w, dz0, y0, y1); Prof(frame, dz1, dz1 + w, y0, y1);
                Prof(frame, dz0, dz1, head - w * 0.5f, head + w * 0.5f);
                Pane(glass, dz0, dz1, head + w * 0.5f, y1 - w);

                // glazed door leaf
                var leaf = new MeshBuilder { Transform = f.ToWorld };
                float la = dz0 + 0.004f, lb = dz1 - 0.004f, lt = head - w * 0.5f - 0.004f, lbm = y0 + 0.01f;
                Prof(leaf, la, la + w, lbm, lt); Prof(leaf, lb - w, lb, lbm, lt);
                Prof(leaf, la, lb, lt - w, lt); Prof(leaf, la, lb, lbm, lbm + w * 1.6f);
                Prof(leaf, la, lb, bar - w * 0.5f, bar + w * 0.5f);
                Pane(leaf, la + w, lb - w, lbm + w, lt - w);
                bool atStart = d.Def.Hinge == Hinge.Start;
                float hz = atStart ? lb - 0.09f : la + 0.09f;
                foreach (float side in new[] { -1f, 1f })
                    leaf.Rod(WallFrame.L(hz, y0 + 0.75f, c + side * 0.03f), WallFrame.L(hz, y0 + 1.35f, c + side * 0.03f), 0.01f, bm);
                DoorPivot("Door_" + (d.Def.Id ?? f.Def.Id), f, d, leaf, f.P(atStart ? la : lb, lbm, c), -f.N, 100f);
                s = dz1 + w;
            }
            Fixed(s, z1 - w);
            // an exterior glass wall passing a floor slab or the roof build-up gets an opaque spandrel there: otherwise
            // the slab edge (and the void above the top ceiling) shows through the glass as a floating white band
            if (f.Exterior)
                foreach (var (ya, yb) in Spandrels(f)) Prof(frame, z0, z1, ya, yb);
            _c.W.Emit("Steel_Partition_" + f.Def.Id, _c.Interior, frame);
            _c.W.Emit("Threshold_" + f.Def.Id, _c.Interior, sill);
            _c.W.Emit("Steel_Glass_" + f.Def.Id, _c.Interior, glass, castShadows: false);
        }
    }
}
