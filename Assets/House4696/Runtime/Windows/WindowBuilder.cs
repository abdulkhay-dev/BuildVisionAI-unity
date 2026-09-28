using System;
using System.Collections.Generic;
using Clipper2Lib;
using House4696.Core;
using House4696.Doors;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.Windows
{
    /// <summary>
    /// Builds a catalogue window in its wall opening. Window space (mm): x from the opening's left edge seen from outside,
    /// y up from the opening's bottom, z into the wall from its structural outer face (the facade's cladding is at z &lt; 0,
    /// the inside face at z = wall thickness). The frame, mullions and sashes are prisms of 2D regions (Clipper), so any
    /// outline works: rectangles, arches, circles, gables. A shaped window fills the rest of its rectangular wall hole.
    /// Turn sashes swing inwards, sliding sashes slide (Door component); fixed glass and tilt sashes stay.
    /// </summary>
    public sealed class WindowBuilder
    {
        readonly HouseContext _c;

        public WindowBuilder(HouseContext c) { _c = c; }

        /// <summary>Materials of the wall round the opening: its facade finish, the inside finish and the facade's cladding thickness (m).</summary>
        public struct WallSide
        {
            public Material Outside, Inside;
            public float CladT;
        }

        sealed class Cell
        {
            public WindowNode Node;
            public Rect R;
        }

        public void Build(WallFrame f, OpeningDef o, ResolvedWindow w, float s0, float s1, float y0, float y1, WallSide wall)
        {
            var d = w.Design;
            float W = (s1 - s0) * 1000f, H = (y1 - y0) * 1000f, T = f.T * 1000f;
            var mx = new ResizeMap(d.RefW, W, d.FixX);
            var my = new ResizeMap(d.RefH, H, d.FixY);
            var toWorld = f.ToWorld * Matrix4x4.Translate(new Vector3(s0, y0, 0f));
            var solid = new MeshBuilder { Transform = toWorld };
            var glass = new MeshBuilder { Transform = toWorld };
            var L = _c.Lib;
            var frameMat = w.Finish != null ? _c.Mats.Get(w.Finish.Material, L.Frame) : L.Frame;

            // outline of the frame and its inside
            var outline = d.Shape != null ? Shape2D.Parse(d.Shape) : new List<Poly> { Shape2D.RoundRect(0f, 0f, d.RefW, d.RefH, 0f, 0.5f) };
            Shape2D.Map(outline, mx, my);
            var O = Relief.Union(Rings(outline));
            if (O.Count == 0) O = Relief.Rect(Rect.MinMaxRect(0f, 0f, W, H));
            float fw = Mathf.Max(10f, d.Frame.Width), fd = Mathf.Max(20f, d.Frame.Depth);
            var I = Relief.Inflate(O, -fw);
            float fz0 = Mathf.Clamp(d.Frame.Inset, 0f, Mathf.Max(0f, T - fd)), fz1 = fz0 + fd;

            // a shaped window: the wall fills its rectangular hole round the outline
            // (a millimetre larger than the hole, so an outline touching its edges — a circle — leaves one ring with a hole)
            var hole = Relief.Rect(Rect.MinMaxRect(-1f, -1f, W + 1f, H + 1f));
            var infill = Relief.Difference(hole, O);
            if (Relief.Area(infill) > 100f + 2f * (W + H) + 4f)
            {
                float zc = -wall.CladT * 1000f;
                Relief.Fill(solid, infill, -zc, -1f, wall.Outside, mm => mm / 1000f);
                Relief.Fill(solid, infill, T, 1f, wall.Inside, mm => mm / 1000f);
                foreach (var p in O) Walls(solid, p, zc, T, wall.Outside, inward: true);
            }

            // frame ring and mullions
            Prism(solid, Relief.Difference(O, I), fz0, fz1, frameMat, frameMat, frameMat);
            var cells = new List<Cell>();
            var bounds = Clipper.GetBounds(I);
            Walk(d.Layout, Rect.MinMaxRect((float)bounds.left, (float)bounds.top, (float)bounds.right, (float)bounds.bottom), mx, my, I, cells,
                 band => Prism(solid, band, fz0, fz1, frameMat, frameMat, frameMat));

            // cells: fixed glass or sashes
            int slideIndex = 0;
            var doors = new List<Door>();
            foreach (var cell in cells)
            {
                var C = Relief.Intersect(Relief.Rect(cell.R), I);
                if (Relief.Area(C) < 100f) continue;
                string kind = (cell.Node.Sash ?? "fixed").ToLowerInvariant();
                string role = cell.Node.Glass ?? d.Glass;
                if (kind == "fixed")
                {
                    float pz = (fz0 + fz1) * 0.5f;
                    Pane(glass, C, pz, role, cell.Node.Frosted, cell.R);
                    Bars(solid, C, cell, pz, mx, my, frameMat);
                    continue;
                }
                // a sash: its own frame inside the cell, its glass and bars; it moves as one piece
                var sashSolid = new MeshBuilder { Transform = toWorld };
                var sashGlass = new MeshBuilder { Transform = toWorld };
                var so = C;
                float track = 0f;
                if (kind == "slide")
                {
                    // sliding sashes overlap their neighbours (interlock) and run in alternate tracks
                    var wide = cell.R;
                    wide.xMin -= d.Sash.Overlap * 0.5f;
                    wide.xMax += d.Sash.Overlap * 0.5f;
                    so = Relief.Intersect(Relief.Rect(wide), I);
                    track = (slideIndex++ % 2) * d.Sash.Depth * 0.55f;
                }
                float sw = Mathf.Max(10f, d.Sash.Width);
                var si = Relief.Inflate(so, -sw);
                float sz0 = fz0 + d.Sash.Offset + track, sz1 = sz0 + d.Sash.Depth;
                Prism(sashSolid, Relief.Difference(so, si), sz0, sz1, frameMat, frameMat, frameMat);
                float spz = (sz0 + sz1) * 0.5f;
                Pane(sashGlass, si, spz, role, cell.Node.Frosted, cell.R);
                Bars(sashSolid, si, cell, spz, mx, my, frameMat);

                var sb = Clipper.GetBounds(so);
                float x0 = (float)sb.left, x1 = (float)sb.right, yb = (float)sb.top;
                string hinge = (cell.Node.Hinge ?? "left").ToLowerInvariant();
                Vector3 World(float x, float y, float z) => toWorld.MultiplyPoint3x4(new Vector3(x, y, z) / 1000f);
                Vector3 inside = toWorld.MultiplyVector(Vector3.forward).normalized;
                if (kind == "turn" || kind == "tilt-turn")
                {
                    // hinge side as seen from outside; the sash swings into the room
                    float hx = hinge.StartsWith("r") ? x1 : x0;
                    var at = World(hx, yb, sz1);
                    var along = (World(hinge.StartsWith("r") ? x0 : x1, yb, sz1) - at).normalized;
                    var door = Pivot("Window_" + o.Id + "_" + doors.Count, at, sashSolid, sashGlass);
                    door.OpenAngle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * along, inside) > 0f ? 80f : -80f;
                    doors.Add(door);
                }
                else if (kind == "slide")
                {
                    var at = World((x0 + x1) * 0.5f, yb, sz0);
                    var door = Pivot("Window_" + o.Id + "_" + doors.Count, at, sashSolid, sashGlass);
                    door.Motion = DoorMotion.Slide;
                    float dist = (x1 - x0) - d.Sash.Overlap;
                    door.SlideBy = toWorld.MultiplyVector(new Vector3(hinge.StartsWith("r") ? dist : -dist, 0f, 0f) / 1000f);
                    doors.Add(door);
                }
                else
                {
                    // tilt (and anything else): part of the fixed frame
                    Emit("WindowSash_" + o.Id, sashSolid, sashGlass);
                }
            }
            foreach (var door in doors) if (o.Open == true) door.SetOpen(true, instant: true);

            Sill(solid, d, W, T, fz0, fz1, wall, frameMat);
            if (d.Surround != null) Surround(solid, d.Surround, O, W, H, wall, frameMat);
            Emit("Window_" + o.Id, solid, glass);
        }

        // ------------------------------------------------------------------ layout
        void Walk(WindowNode n, Rect r, ResizeMap mx, ResizeMap my, PathsD inside, List<Cell> cells, Action<PathsD> mullion)
        {
            if (n == null) { cells.Add(new Cell { Node = new WindowNode(), R = r }); return; }
            bool split = (n.Split == "x" || n.Split == "y") && n.At != null && n.Cells != null && n.Cells.Count == n.At.Length + 1;
            if (!split) { cells.Add(new Cell { Node = n, R = r }); return; }
            bool alongX = n.Split == "x";
            var map = alongX ? mx : my;
            float lo = alongX ? r.xMin : r.yMin;
            for (int i = 0; i <= n.At.Length; i++)
            {
                float hi = i < n.At.Length ? map.Map(n.At[i]) : (alongX ? r.xMax : r.yMax);
                float wNext = i < n.At.Length ? MullionWidth(n, i) : 0f;
                float cellHi = i < n.At.Length ? hi - wNext * 0.5f : hi;
                var cr = alongX ? Rect.MinMaxRect(lo, r.yMin, cellHi, r.yMax) : Rect.MinMaxRect(r.xMin, lo, r.xMax, cellHi);
                Walk(n.Cells[i], cr, mx, my, inside, cells, mullion);
                if (i < n.At.Length && wNext > 0.5f)
                {
                    var band = alongX ? Rect.MinMaxRect(hi - wNext * 0.5f, r.yMin - 1f, hi + wNext * 0.5f, r.yMax + 1f)
                                      : Rect.MinMaxRect(r.xMin - 1f, hi - wNext * 0.5f, r.xMax + 1f, hi + wNext * 0.5f);
                    var region = Relief.Intersect(Relief.Rect(band), inside);
                    if (region.Count > 0) mullion(region);
                }
                lo = hi + wNext * 0.5f;
            }
        }

        static float MullionWidth(WindowNode n, int i)
        {
            var t = n.Mullion;
            if (t == null || t.Type == JTokenType.Null) return 80f;
            if (t is JArray a) return i < a.Count ? (float)a[i] : 80f;
            return (float)t;
        }

        // ------------------------------------------------------------------ parts
        /// <summary>Glass over a region (it runs 8 mm under the frame round it); a frosted band from the cell's bottom when asked.</summary>
        void Pane(MeshBuilder mb, PathsD region, float z, string role, float? frosted, Rect cell)
        {
            var pane = Relief.Inflate(region, 8f);
            if (frosted.HasValue && frosted.Value > 1f)
            {
                var band = Relief.Rect(Rect.MinMaxRect(cell.xMin - 20f, cell.yMin - 20f, cell.xMax + 20f, cell.yMin + frosted.Value));
                Glass(mb, Relief.Intersect(pane, band), z, "frosted");
                Glass(mb, Relief.Difference(pane, band), z, role);
            }
            else Glass(mb, pane, z, role);
        }

        void Glass(MeshBuilder mb, PathsD pane, float z, string role)
        {
            if (pane == null || pane.Count == 0) return;
            var L = _c.Lib;
            var M = _c.M;
            Material outer, inner;
            switch ((role ?? "clear").ToLowerInvariant())
            {
                case "frosted": case "satin": outer = inner = M.DoorSatin; break;
                case "tinted": case "black": outer = inner = M.BlackGlass; break;
                case "mirror": outer = M.Mirror; inner = L.GlassInner; break;
                default: outer = L.Glass; inner = L.GlassInner; break;
            }
            Relief.Fill(mb, pane, -(z - 2f), -1f, outer, mm => mm / 1000f);
            Relief.Fill(mb, pane, z + 2f, 1f, inner, mm => mm / 1000f);
        }

        /// <summary>Glazing bars across a glass region: at reference positions (their centres move with the size) or a regular grid.</summary>
        void Bars(MeshBuilder mb, PathsD region, Cell cell, float z, ResizeMap mx, ResizeMap my, Material m)
        {
            var b = cell.Node.Bars;
            if (b == null || region.Count == 0) return;
            var rb = Clipper.GetBounds(region);
            float x0 = (float)rb.left, x1 = (float)rb.right, y0 = (float)rb.top, y1 = (float)rb.bottom, w = Mathf.Max(8f, b.Width);
            var xs = new List<float>();
            var ys = new List<float>();
            if (b.X != null) foreach (var x in b.X) xs.Add(mx.Map(x));
            if (b.Y != null) foreach (var y in b.Y) ys.Add(my.Map(y));
            if (b.Cols.HasValue) for (int i = 1; i < b.Cols.Value; i++) xs.Add(Mathf.Lerp(x0, x1, i / (float)b.Cols.Value));
            if (b.Rows.HasValue) for (int i = 1; i < b.Rows.Value; i++) ys.Add(Mathf.Lerp(y0, y1, i / (float)b.Rows.Value));
            float depth = 22f;
            foreach (var x in xs)
                Prism(mb, Relief.Intersect(Relief.Rect(Rect.MinMaxRect(x - w * 0.5f, y0 - 1f, x + w * 0.5f, y1 + 1f)), region), z - depth, z + depth, m, m, m);
            foreach (var y in ys)
                Prism(mb, Relief.Intersect(Relief.Rect(Rect.MinMaxRect(x0 - 1f, y - w * 0.5f, x1 + 1f, y + w * 0.5f)), region), z - depth, z + depth, m, m, m);
        }

        /// <summary>Outside: a metal drip or a stone sill under the frame; inside: a window board.</summary>
        void Sill(MeshBuilder mb, WindowDesign d, float W, float T, float fz0, float fz1, WallSide wall, Material frame)
        {
            var s = d.Sill ?? new SillSpec();
            float face = -wall.CladT * 1000f;
            string outside = (s.Outside ?? "metal").ToLowerInvariant();
            if (outside == "metal")
            {
                var m = s.Material != null ? _c.Mats.Get(s.Material, _c.Lib.Coping) : _c.Lib.Coping;
                Box(mb, 0f, W, 2f, 5f, face - s.Overhang, fz0, m);
                Box(mb, 0f, W, -28f, 5f, face - s.Overhang - 2f, face - s.Overhang, m);
            }
            else if (outside == "stone")
            {
                var m = _c.Mats.Get(s.Material ?? "sandstone_light", _c.Lib.Stone);
                Box(mb, -s.Ears, W + s.Ears, 5f - s.Thickness, 5f, face - s.Overhang, fz0, m);
            }
            if ((s.Inside ?? "board").ToLowerInvariant() == "board")
            {
                var m = s.InsideMaterial != null ? _c.Mats.Get(s.InsideMaterial, frame) : _c.Mats.Get("door_enamel_whitey#f4f3ef", frame);
                Box(mb, -s.InsideOverhang, W + s.InsideOverhang, 0f, 20f, fz1, T + s.InsideOverhang, m);
            }
        }

        /// <summary>A band round the window on the facade (stone architrave, wooden portal), following its outline.</summary>
        void Surround(MeshBuilder mb, SurroundSpec s, PathsD outline, float W, float H, WallSide wall, Material frame)
        {
            var m = string.Equals(s.Material, "frame", StringComparison.OrdinalIgnoreCase) ? frame : _c.Mats.Get(s.Material, _c.Lib.Stone);
            var outer = Relief.Inflate(outline, s.Width);
            if (s.Head > 0.5f)
            {
                var hb = Clipper.GetBounds(outer);
                outer = Relief.Union(new PathsD(outer) { Relief.Rect(Rect.MinMaxRect((float)hb.left - 15f, H, (float)hb.right + 15f, (float)hb.bottom + s.Head))[0] });
            }
            var ring = Relief.Difference(outer, outline);
            float face = -wall.CladT * 1000f;
            Prism(mb, ring, face - s.Depth, face + 5f, m, m, m);
        }

        // ------------------------------------------------------------------ geometry
        /// <summary>A prism of a 2D region between depths z0 (outside face, normal −z) and z1 (inside face, normal +z), with its side walls.</summary>
        static void Prism(MeshBuilder mb, PathsD region, float z0, float z1, Material outside, Material inside, Material side)
        {
            if (region == null || region.Count == 0) return;
            Relief.Fill(mb, region, -z0, -1f, outside, mm => new Vector2(mm.y, mm.x) / 1000f);
            Relief.Fill(mb, region, z1, 1f, inside, mm => new Vector2(mm.y, mm.x) / 1000f);
            foreach (var p in region) Walls(mb, p, z0, z1, side, inward: false);
        }

        /// <summary>
        /// Side walls along a contour between z0 and z1. Clipper keeps the region on the left of every contour (outer rings
        /// counter-clockwise, holes clockwise), so the outward normal is the right-hand one; <paramref name="inward"/> flips it.
        /// Normals are smoothed across gentle bends (arches, circles) and kept sharp at corners.
        /// </summary>
        static void Walls(MeshBuilder mb, PathD p, float z0, float z1, Material m, bool inward)
        {
            int n = p.Count;
            if (n < 2 || m == null) return;
            var pts = new Vector2[n];
            for (int i = 0; i < n; i++) pts[i] = new Vector2((float)p[i].x, (float)p[i].y);
            float sign = inward ? -1f : 1f;
            Vector2 EdgeN(int i)
            {
                Vector2 a = pts[i], b = pts[(i + 1) % n], t = (b - a).normalized;
                return new Vector2(t.y, -t.x) * sign;
            }
            const float cosSmooth = 0.94f;   // ~20°
            float along = 0f;
            for (int i = 0; i < n; i++)
            {
                Vector2 a = pts[i], b = pts[(i + 1) % n];
                float len = (b - a).magnitude;
                if (len < 1e-3f) continue;
                Vector2 ne = EdgeN(i), np = EdgeN((i - 1 + n) % n), nn = EdgeN((i + 1) % n);
                Vector2 na = Vector2.Dot(ne, np) > cosSmooth ? (ne + np).normalized : ne;
                Vector2 nb = Vector2.Dot(ne, nn) > cosSmooth ? (ne + nn).normalized : ne;
                Vector3 A0 = new Vector3(a.x, a.y, z0) / 1000f, B0 = new Vector3(b.x, b.y, z0) / 1000f;
                Vector3 A1 = new Vector3(a.x, a.y, z1) / 1000f, B1 = new Vector3(b.x, b.y, z1) / 1000f;
                float u0 = along / 1000f, u1 = (along + len) / 1000f, v0 = z0 / 1000f, v1 = z1 / 1000f;
                DoorGeo.Quad(mb, A0, B0, B1, A1, new Vector3(na.x, na.y, 0f), new Vector3(nb.x, nb.y, 0f), new Vector3(nb.x, nb.y, 0f), new Vector3(na.x, na.y, 0f),
                    new Vector2(u0, v0), new Vector2(u1, v0), new Vector2(u1, v1), new Vector2(u0, v1), m);
                along += len;
            }
        }

        static void Box(MeshBuilder mb, float x0, float x1, float y0, float y1, float z0, float z1, Material m)
        {
            if (m == null) return;
            mb.Box(new Vector3(Mathf.Min(x0, x1), Mathf.Min(y0, y1), Mathf.Min(z0, z1)) / 1000f,
                   new Vector3(Mathf.Max(x0, x1), Mathf.Max(y0, y1), Mathf.Max(z0, z1)) / 1000f, m);
        }

        static PathsD Rings(List<Poly> shape)
        {
            var paths = new PathsD();
            foreach (var p in shape) if (p.Closed && p.P.Count >= 3) paths.Add(Relief.Path(p.P));
            return paths;
        }

        void Emit(string name, MeshBuilder solid, MeshBuilder glass)
        {
            _c.W.Emit(name, _c.Shell, solid);
            _c.W.Emit(name + "_Glass", _c.Shell, glass, castShadows: false);
        }

        Door Pivot(string name, Vector3 at, MeshBuilder solid, MeshBuilder glass)
        {
            var pivot = new GameObject(name);
            pivot.transform.SetParent(_c.Doors, false);
            pivot.transform.position = at;
            foreach (var (mb, part, shadows) in new[] { (solid, "Sash", true), (glass, "Sash_Glass", false) })
            {
                var go = _c.W.Emit(part, pivot.transform, mb, castShadows: shadows);
                if (go == null) continue;
                go.transform.localPosition = -at;
                _c.W.MarkDynamic(go);
            }
            var door = pivot.AddComponent<Door>();
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
            return door;
        }
    }
}
