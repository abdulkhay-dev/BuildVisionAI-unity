using System;
using System.Collections.Generic;
using System.Linq;
using Clipper2Lib;
using House4696.Core;
using House4696.Generation;
using House4696.Runtime;
using UnityEngine;

namespace House4696.Casegoods
{
    /// <summary>
    /// Builds a catalogue module (<see cref="CaseDesign"/>) as an item: every part of the design in the item's local space
    /// (front towards -Z, back at z = 0, x centred, floor at y = 0; wall pieces centred on their wall point), doors and
    /// drawers on their own pivots. Item parameters: finish (a finish id of the model), open (build the doors / drawers open).
    /// </summary>
    public sealed class CaseBuilder
    {
        readonly ItemBuild _b;
        readonly CaseDesign _d;
        readonly CaseFinish _fin;
        readonly CaseCollection _col;
        readonly CaseGeo _g;
        readonly Dictionary<string, ItemMover> _moverOf = new Dictionary<string, ItemMover>(StringComparer.OrdinalIgnoreCase);
        readonly Dictionary<string, Material> _mats = new Dictionary<string, Material>(StringComparer.OrdinalIgnoreCase);

        public static void Build(ItemBuild b, CaseModel model)
        {
            var d = CaseCatalog.Design(model.Design ?? model.Id);
            if (d == null) throw new Exception($"нет чертежа Casegoods/Designs/{model.Design ?? model.Id}.json");
            if (d.Size == null || d.Size.Length < 3) throw new Exception("у чертежа нет size [L, B, H]");
            var fin = CaseCatalog.FinishFor(model, b.P.S("finish", null));
            new CaseBuilder(b, d, fin, CaseCatalog.Collection(model.Collection), model.Mount == "wall").Run();
        }

        CaseBuilder(ItemBuild b, CaseDesign d, CaseFinish fin, CaseCollection col, bool wall)
        {
            _b = b; _d = d; _fin = fin; _col = col;
            _g = new CaseGeo(d.Size[0], wall ? d.Size[2] * 0.5f : 0f);
        }

        void Run()
        {
            foreach (var mv in _d.Moves ?? new List<CaseMove>()) Mover(mv);
            foreach (var p in _d.Parts)
            {
                try { Part(p); }
                catch (Exception e) { throw new Exception($"деталь '{p.Id ?? p.N}' ({p.Kind}): {e.Message}"); }
            }
            // the item opens as built when asked to (previews of the interior)
            if (_b.P.B("open", false))
                foreach (var mv in _b.Movers) mv.Open = true;
        }

        string IdOf(CasePart p) => p.Id ?? p.N;

        // ------------------------------------------------------------------ moving groups
        void Mover(CaseMove mv)
        {
            var parts = _d.Parts.Where(p => mv.Parts.Contains(IdOf(p), StringComparer.OrdinalIgnoreCase)).ToList();
            if (parts.Count == 0) return;
            var box = Bounds(parts);   // x0 y0 z0 x1 y1 z1
            var m = new ItemMover { Name = mv.Name ?? (mv.Type + "_" + _b.Movers.Count) };
            string type = (mv.Type ?? "door").ToLowerInvariant();
            var front = parts.Where(p => p.Kind == "front" && p.Box != null).OrderByDescending(p => Math.Abs(p.Box[3] - p.Box[0]) * Math.Abs(p.Box[4] - p.Box[1]))
                .FirstOrDefault()?.Box ?? box;
            if (type == "drawer" || type == "slide")
            {
                m.Motion = DoorMotion.Slide;
                m.Pivot = _g.P(new Vector3((box[0] + box[3]) * 0.5f, (box[1] + box[4]) * 0.5f, box[5]));
                var by = type == "drawer" || mv.By == null || mv.By.Length < 3 ? new[] { 0f, 0f, mv.Travel } : mv.By;
                m.Slide = new Vector3(by[0], by[1], -by[2]) / 1000f;
            }
            else if (type == "flap")
            {
                // a horizontal hinge line along x: the pivot's local Y is turned onto +X, the door turns about it
                bool bottom = !string.Equals(mv.Hinge, "top", StringComparison.OrdinalIgnoreCase);
                float ay = mv.Axis != null && mv.Axis.Length >= 2 ? mv.Axis[0] : bottom ? front[1] : front[4];
                float az = mv.Axis != null && mv.Axis.Length >= 2 ? mv.Axis[1] : front[5];
                m.Motion = DoorMotion.Swing;
                m.Pivot = _g.P(new Vector3((front[0] + front[3]) * 0.5f, ay, az));
                m.Frame = Quaternion.FromToRotation(Vector3.up, Vector3.right);
                // about +X a positive turn takes +Y towards +Z (the back): a dropping flap turns negative
                m.Angle = bottom ? -Mathf.Min(mv.Angle, 90f) : Mathf.Min(mv.Angle, 100f);
            }
            else
            {
                // the front part (the biggest) gives the hinge edge; hinge line at its front outer corner unless given
                bool left = !string.Equals(mv.Hinge, "right", StringComparison.OrdinalIgnoreCase);
                float ax = mv.Axis != null && mv.Axis.Length >= 2 ? mv.Axis[0] : left ? front[0] : front[3];
                float az = mv.Axis != null && mv.Axis.Length >= 2 ? mv.Axis[1] : front[5];
                m.Motion = DoorMotion.Swing;
                m.Pivot = _g.P(new Vector3(ax, 0f, az));
                // local front is -Z: a left hinge swings the free (+x) edge towards -Z by turning +Y
                m.Angle = left ? mv.Angle : -mv.Angle;
            }
            _b.Movers.Add(m);
            foreach (var p in parts) _moverOf[IdOf(p)] = m;
        }

        static float[] Bounds(IEnumerable<CasePart> parts)
        {
            var r = new[] { float.MaxValue, float.MaxValue, float.MaxValue, float.MinValue, float.MinValue, float.MinValue };
            foreach (var p in parts)
            {
                var b = PartBox(p);
                if (b == null) continue;
                for (int i = 0; i < 3; i++) { r[i] = Mathf.Min(r[i], Mathf.Min(b[i], b[i + 3])); r[i + 3] = Mathf.Max(r[i + 3], Mathf.Max(b[i], b[i + 3])); }
            }
            return r;
        }

        /// <summary>The box a part occupies (handles: round their point).</summary>
        static float[] PartBox(CasePart p)
        {
            if (p.Box != null && p.Box.Length >= 6) return p.Box;
            if (p.From != null && p.To != null && p.From.Length >= 3 && p.To.Length >= 3)
            {
                float r = Mathf.Max(p.D, p.D2, 1f) * 0.5f;
                var a = new Vector3(p.From[0], p.From[1], p.From[2]); var b = new Vector3(p.To[0], p.To[1], p.To[2]);
                var ax = (b - a).normalized;
                // the ends are cut square to the axis: the radius pads each axis by r·sin(angle to the rod)
                var pad = new Vector3(Mathf.Sqrt(Mathf.Max(0f, 1f - ax.x * ax.x)), Mathf.Sqrt(Mathf.Max(0f, 1f - ax.y * ax.y)), Mathf.Sqrt(Mathf.Max(0f, 1f - ax.z * ax.z))) * r;
                var lo = Vector3.Min(a, b) - pad; var hi = Vector3.Max(a, b) + pad;
                return new[] { lo.x, lo.y, lo.z, hi.x, hi.y, hi.z };
            }
            if (p.At != null && p.At.Length >= 2)
            {
                float r = Mathf.Max(p.D, 10f) * 0.5f;
                return new[] { p.At[0] - r, p.At[1] - r, p.Z, p.At[0] + r, p.At[1] + r, p.Z + p.Standoff + p.T };
            }
            return null;
        }

        ItemMover MoverOf(CasePart p) => IdOf(p) is string id && _moverOf.TryGetValue(id, out var m) ? m : null;
        MeshBuilder Solid(CasePart p) => MoverOf(p)?.Solid ?? _b.F;
        MeshBuilder Glass(CasePart p) => MoverOf(p)?.Glass ?? _b.G;

        // ------------------------------------------------------------------ parts
        void Part(CasePart p)
        {
            string kind = (p.Kind ?? "panel").ToLowerInvariant();
            // decors run along the part's longest side unless the design says otherwise (metal and glass: planar)
            _g.Grain = kind == "panel" || kind == "back" || kind == "front"
                ? AxisOf(p.Grain) ?? (p.Box != null && p.Box.Length >= 6 ? CaseGeo.LongestAxis(p.Box) : -1)
                : -1;
            var turned = TurnOn(p);
            try { Build(p, kind); }
            finally { foreach (var mb in turned) mb.Transform = Matrix4x4.identity; }
        }

        /// <summary>A turned part: every mesh builder it may write to gets the turn in the item's local space.</summary>
        List<MeshBuilder> TurnOn(CasePart p)
        {
            var list = new List<MeshBuilder>();
            if (p.Rot == null || Mathf.Abs(p.Rot.Deg) < 1e-4f) return list;
            var about = p.Rot.About != null && p.Rot.About.Length >= 3 ? new Vector3(p.Rot.About[0], p.Rot.About[1], p.Rot.About[2])
                : p.Box != null && p.Box.Length >= 6 ? new Vector3((p.Box[0] + p.Box[3]) * 0.5f, (p.Box[1] + p.Box[4]) * 0.5f, (p.Box[2] + p.Box[5]) * 0.5f)
                : Vector3.zero;
            float d = p.Rot.Deg;
            // design space is right-handed with z to the front, local space has z to the back (see CaseGeo.P)
            var q = (p.Rot.Axis ?? "x").ToLowerInvariant() == "y" ? Quaternion.Euler(0f, -d, 0f)
                  : (p.Rot.Axis ?? "x").ToLowerInvariant() == "z" ? Quaternion.Euler(0f, 0f, d)
                  : Quaternion.Euler(-d, 0f, 0f);
            var c = _g.P(about);
            var m = Matrix4x4.Translate(c) * Matrix4x4.Rotate(q) * Matrix4x4.Translate(-c);
            foreach (var mb in new[] { Solid(p), Glass(p), _b.D })
                if (!list.Contains(mb)) { mb.Transform = m; list.Add(mb); }
            return list;
        }

        void Build(CasePart p, string kind)
        {
            switch (kind)
            {
                case "panel":
                case "back":
                case "front":
                    if (p.Glass != null && kind == "front") GlazedFront(p);
                    else FacedBoard(p, Solid(p), Mat(p.Mat ?? (kind == "panel" ? "body" : kind)), p.Edge ?? (kind == "front" ? 1.5f : kind == "back" ? 0.3f : 1f));
                    if (!string.IsNullOrEmpty(p.Print)) Print(p);
                    break;
                case "rod":
                    Rod(p);
                    break;
                case "soft":
                    Soft(p);
                    break;
                case "glass":
                    Slab(p, Glass(p), Mat(p.Mat ?? "glass"), p.Edge ?? 0.5f);
                    break;
                case "mirror":
                    Slab(p, Solid(p), Mat(p.Mat ?? "mirror"), p.Edge ?? 0.5f);
                    break;
                case "moulding":
                    Moulding(p);
                    break;
                case "tube":
                    Tube(p);
                    break;
                case "handle":
                    Handle(p);
                    break;
                case "light":
                    Slab(p, _b.D, Mat(p.Mat ?? "led"), 0.5f);
                    break;
                case "mattress":
                    Mattress(p);
                    break;
                default:
                    throw new Exception("неизвестный вид детали");
            }
        }

        /// <summary>A board, or a disc / ring / shaped slab when the part's shape says so (cut through its thinnest axis).</summary>
        void Slab(CasePart p, MeshBuilder mb, Material m, float edge)
        {
            if (p.Box == null || p.Box.Length < 6) throw new Exception("нет box");
            var (pl, a0, b0, a1, b1, w0, w1) = CaseGeo.Thin(p.Box);
            _g.Slab(mb, pl, Region(p, a0, b0, a1, b1), w0, w1, edge, m);
        }

        /// <summary>The outline of a part in the plane across its thinnest axis.</summary>
        static PathsD Region(CasePart p, float a0, float b0, float a1, float b1)
        {
            string shape = (p.Shape ?? "rect").ToLowerInvariant();
            float ca = (a0 + a1) * 0.5f, cb = (b0 + b1) * 0.5f, ra = (a1 - a0) * 0.5f, rb = (b1 - b0) * 0.5f;
            switch (shape)
            {
                case "circle":
                case "ring":
                    var region = new PathsD { CaseGeo.Ellipse(ca, cb, ra, rb) };
                    if (shape == "ring" && p.Inner is float inner && inner > 0f)
                        region.Add(CaseGeo.Reversed(CaseGeo.Ellipse(ca, cb, inner * 0.5f * ra / Mathf.Max(ra, rb), inner * 0.5f * rb / Mathf.Max(ra, rb))));
                    return region;
                case "path":
                    if (string.IsNullOrEmpty(p.Outline)) throw new Exception("shape path без outline");
                    var paths = new PathsD();
                    foreach (var poly in House4696.Doors.Shape2D.ParsePath(p.Outline, 0.5f))
                    {
                        if (!poly.Closed || poly.P.Count < 3) continue;
                        var q = new PathD(poly.P.Count);
                        foreach (var v in poly.P) q.Add(new PointD(v.x, v.y));
                        paths.Add(q);
                    }
                    if (paths.Count == 0) throw new Exception("outline не даёт замкнутого контура");
                    // the outline is clipped to the box (a path drawn a little outside still gives the listed size)
                    return Clipper.Intersect(paths, new PathsD { CaseGeo.Rect(a0, b0, a1, b1) }, FillRule.EvenOdd, 3);
                default:
                    return new PathsD { CaseGeo.RoundRect(a0, b0, a1, b1, p.Radius) };
            }
        }

        // ------------------------------------------------------------------ faces
        /// <summary>A board whose +W face (a front's face) is flat, fluted, a milled frame round a sunk panel, grooved or diamond.</summary>
        void FacedBoard(CasePart p, MeshBuilder mb, Material m, float edge)
        {
            var f = p.Face;
            string type = (f?.Type ?? "flat").ToLowerInvariant();
            if (type == "flat" || p.Box == null) { Slab(p, mb, m, edge); return; }
            var (pl, a0, b0, a1, b1, w0, w1) = CaseGeo.Thin(p.Box);
            if (string.Equals(f.Side, "-", StringComparison.Ordinal) || string.Equals(f.Side, "back", StringComparison.OrdinalIgnoreCase))
            {
                // the face on the −W side: the same plane looking the other way (depths negate)
                pl = new CasePlane(pl.Origin, pl.U, pl.V, -pl.W);
                (w0, w1) = (-w1, -w0);
            }
            var region = Region(p, a0, b0, a1, b1);
            float depth = Mathf.Clamp(f.Depth, 0.2f, (w1 - w0) * 0.8f);
            switch (type)
            {
                case "fluted":
                {
                    bool alongA = string.Equals(f.Dir, "x", StringComparison.OrdinalIgnoreCase);
                    // ribs run along b: swap the plane's axes for ribs along a
                    var fp = alongA ? new CasePlane(pl.Origin, pl.V, pl.U, pl.W) : pl;
                    float s0 = alongA ? b0 : a0, s1 = alongA ? b1 : a1, t0 = alongA ? a0 : b0, t1 = alongA ? a1 : b1;
                    // a part of the face only: the ribs stand on the flat face (applied reeds)
                    bool part = f.Area != null && f.Area.Length >= 4;
                    float wb = part ? w1 : w1 - depth;
                    if (part)
                    {
                        s0 = alongA ? f.Area[1] : f.Area[0]; s1 = alongA ? f.Area[3] : f.Area[2];
                        t0 = alongA ? f.Area[0] : f.Area[1]; t1 = alongA ? f.Area[2] : f.Area[3];
                    }
                    _g.Slab(mb, pl, region, w0, wb, edge, m);
                    float pitch = Mathf.Max(f.Pitch, 2f), rib = Mathf.Max(pitch - Mathf.Max(f.Gap, 0f), 1f);
                    int n = Mathf.Max(1, Mathf.FloorToInt((s1 - s0 - 2f * f.Margin + f.Gap) / pitch));
                    float start = s0 + ((s1 - s0) - (n * pitch - f.Gap)) * 0.5f;
                    bool reed = !string.Equals(f.Flute, "groove", StringComparison.OrdinalIgnoreCase);
                    float H(float s)
                    {
                        float x = s - start;
                        if (x < 0f || x > n * pitch - f.Gap) return reed ? 0f : depth;
                        float t = x % pitch;
                        if (t > rib) return reed ? 0f : depth;
                        float u = 2f * t / rib - 1f, c = Mathf.Sqrt(Mathf.Max(0f, 1f - u * u));
                        return reed ? depth * c : depth * (1f - c);
                    }
                    float inset = part ? 0f : edge;   // the rounded edge of the base stays visible round the ribs
                    _g.Corrugated(mb, fp, s0 + inset, s1 - inset, t0 + inset, t1 - inset, wb, H, n * 14, m);
                    break;
                }
                case "frame":
                {
                    float bw = Mathf.Max(f.Border, 5f);
                    var inner = CaseGeo.Rect(a0 + bw, b0 + bw, a1 - bw, b1 - bw);
                    var ring = new PathsD(region) { CaseGeo.Reversed(inner) };
                    _g.Slab(mb, pl, ring, w0, w1, edge, m);
                    // the sunk panel; its milled edge (R) rounds into the frame
                    _g.Slab(mb, pl, new PathsD { inner }, w0, w1 - depth, Mathf.Min(f.R, depth * 0.9f), m, back: false);
                    var prof = CaseCatalog.Profile(f.Profile);
                    if (prof != null)
                    {
                        var pts = prof.Pts.Select(q => new Vector2(q[0], q[1])).ToList();
                        if ((pts[0] - pts[pts.Count - 1]).sqrMagnitude > 1e-6f) pts.Add(pts[0]);
                        var path = inner.Select(q => new Vector2((float)q.x, (float)q.y)).ToList();
                        _g.Sweep(mb, pl, path, true, pts, w1 - depth, m);
                    }
                    break;
                }
                case "grooves":
                {
                    float w = Mathf.Max(f.W, 1f);
                    var lines = new PathsD();
                    foreach (var l in f.Lines ?? new List<float[]>())
                        if (l != null && l.Length >= 4) lines.Add(new PathD { new PointD(l[0], l[1]), new PointD(l[2], l[3]) });
                    var bands = Clipper.InflatePaths(lines, w * 0.5f, JoinType.Miter, EndType.Butt, 2.0, 3);
                    _g.Slab(mb, pl, region, w0, w1, edge, m, faceCut: bands);
                    bool u = string.Equals(f.Flute, "u", StringComparison.OrdinalIgnoreCase) || string.Equals(f.Flute, "groove", StringComparison.OrdinalIgnoreCase);
                    var prof = new List<Vector2>();
                    if (u)
                        for (int i = 0; i <= 8; i++)
                        {
                            float t = Mathf.PI + Mathf.PI * i / 8f;
                            prof.Add(new Vector2(w * 0.5f * Mathf.Cos(t), depth * Mathf.Sin(t)));
                        }
                    else { prof.Add(new Vector2(-w * 0.5f, 0f)); prof.Add(new Vector2(0f, -depth)); prof.Add(new Vector2(w * 0.5f, 0f)); }
                    foreach (var l in lines)
                        _g.Sweep(mb, pl, new List<Vector2> { new Vector2((float)l[0].x, (float)l[0].y), new Vector2((float)l[1].x, (float)l[1].y) },
                            false, prof, w1, m, caps: -1);
                    break;
                }
                case "diamond":
                {
                    var cell = f.Cell != null && f.Cell.Length >= 2 ? f.Cell : new[] { 100f, 100f };
                    _g.Slab(mb, pl, region, w0, w1 - depth, edge, m);
                    float mg = Mathf.Max(f.Margin, edge);
                    _g.Pyramids(mb, pl, a0 + mg, a1 - mg, b0 + mg, b1 - mg, cell[0], cell[1], w1 - depth, depth, m);
                    break;
                }
                default:
                    throw new Exception($"неизвестная поверхность '{f.Type}'");
            }
        }

        /// <summary>A printed picture over the +W face of a front, fitted to its box (drawn a hair above the face).</summary>
        void Print(CasePart p)
        {
            var (pl, a0, b0, a1, b1, w0, w1) = CaseGeo.Thin(p.Box);
            var m = _b.C.Mats.Get(p.Print, null);
            if (m == null) throw new Exception($"нет материала печати '{p.Print}'");
            float e = p.Edge ?? 1.5f;
            var face = Clipper.InflatePaths(Region(p, a0, b0, a1, b1), -e, JoinType.Round, EndType.Polygon, 2.0, 3);
            float w = Mathf.Max(a1 - a0, 1f), h = Mathf.Max(b1 - b0, 1f);
            _g.Fill(Solid(p), pl, face, w1 + 0.25f, 1f, m, (a, b) => new Vector2((a - a0) / w, (b - b0) / h));
        }

        /// <summary>A front with a glass panel: the frame (one milled piece) round an opening, the glass in its rebate.</summary>
        void GlazedFront(CasePart p)
        {
            var (pl, a0, b0, a1, b1, w0, w1) = CaseGeo.Thin(p.Box);
            var g = p.Glass;
            float open = g.Frame + g.Rebate;
            var region = new PathsD { CaseGeo.Rect(a0, b0, a1, b1), CaseGeo.Reversed(CaseGeo.Rect(a0 + open, b0 + open, a1 - open, b1 - open)) };
            var mat = Mat(p.Mat ?? "front");
            _g.Slab(Solid(p), pl, region, w0, w1, p.Edge ?? 1.5f, mat);
            float mid = (w0 + w1) * 0.5f, t = Mathf.Clamp(g.T, 2f, w1 - w0 - 1f);
            var pane = new PathsD { CaseGeo.Rect(a0 + g.Frame, b0 + g.Frame, a1 - g.Frame, b1 - g.Frame) };
            var gm = GlassTint(g.Tint);
            _g.Slab(g.Tint == "mirror" ? Solid(p) : Glass(p), pl, pane, mid - t * 0.5f, mid + t * 0.5f, 0.3f, gm);
            // glazing bars across the opening, through the glass, a little below the frame's face
            float bw = Mathf.Max(g.BarW, 4f), bz0 = mid - t * 0.5f - 4f, bz1 = w1 - 1.5f;
            foreach (var x in g.BarsX ?? new float[0])
                _g.Slab(Solid(p), pl, new PathsD { CaseGeo.Rect(x - bw * 0.5f, b0 + open - 1f, x + bw * 0.5f, b1 - open + 1f) }, bz0, bz1, 1f, mat);
            foreach (var y in g.BarsY ?? new float[0])
                _g.Slab(Solid(p), pl, new PathsD { CaseGeo.Rect(a0 + open - 1f, y - bw * 0.5f, a1 - open + 1f, y + bw * 0.5f) }, bz0, bz1, 1f, mat);
        }

        /// <summary>A bar between two points (legs, frames, rails, hairpins): round or square, tapering from D to D2.</summary>
        void Rod(CasePart p)
        {
            if (p.From == null || p.To == null || p.From.Length < 3 || p.To.Length < 3) throw new Exception("rod без from / to");
            float d0 = p.D > 0 ? p.D : 25f, d1 = p.D2 > 0 ? p.D2 : d0;
            _g.Rod(Solid(p), new Vector3(p.From[0], p.From[1], p.From[2]), new Vector3(p.To[0], p.To[1], p.To[2]), d0 * 0.5f, d1 * 0.5f,
                Mat(p.Mat ?? "metal"), string.Equals(p.Section, "square", StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>An upholstered panel (headboards, bench seats): one pad, vertical channels or buttoned tufts.</summary>
        void Soft(CasePart p)
        {
            var b = p.Box ?? throw new Exception("нет box");
            var m = Mat(p.Mat ?? "fabric");
            var mb = Solid(p);
            float x0 = Mathf.Min(b[0], b[3]), x1 = Mathf.Max(b[0], b[3]), y0 = Mathf.Min(b[1], b[4]), y1 = Mathf.Max(b[1], b[4]);
            float z0 = Mathf.Min(b[2], b[5]), z1 = Mathf.Max(b[2], b[5]);
            float t = z1 - z0, r = Mathf.Min(p.Edge ?? t * 0.35f, t * 0.45f);
            void Pad(float a0, float a1, float c0, float c1, int seed)
            {
                var lo = _g.P(new Vector3(a0, c0, z0)); var hi = _g.P(new Vector3(a1, c1, z1));
                mb.RoundBox(Vector3.Min(lo, hi), Vector3.Max(lo, hi), r / 1000f, m, 3, 4, t * 0.12f / 1000f, 0.0015f, seed);
            }
            if (p.Tufts != null && p.Tufts.Length >= 2 && p.Tufts[0] > 0 && p.Tufts[1] > 0)
            {
                int nx = p.Tufts[0], ny = p.Tufts[1];
                float cw = (x1 - x0) / nx, ch = (y1 - y0) / ny;
                for (int i = 0; i < nx; i++)
                for (int j = 0; j < ny; j++) Pad(x0 + i * cw + 0.5f, x0 + (i + 1) * cw - 0.5f, y0 + j * ch + 0.5f, y0 + (j + 1) * ch - 0.5f, i * 31 + j);
                var bm = m;
                for (int i = 1; i < nx; i++)
                for (int j = 1; j < ny; j++)
                    mb.Sphere(_g.P(new Vector3(x0 + i * cw, y0 + j * ch, z1 - t * 0.35f)), 0.008f, bm, 10, 6);
            }
            else if (p.Channels > 0)
            {
                float cw = (x1 - x0) / p.Channels;
                for (int i = 0; i < p.Channels; i++) Pad(x0 + i * cw + 0.5f, x0 + (i + 1) * cw - 0.5f, y0, y1, i * 17);
            }
            else Pad(x0, x1, y0, y1, 3);
        }

        void Moulding(CasePart p)
        {
            var prof = CaseCatalog.Profile(p.Profile) ?? throw new Exception($"нет профиля '{p.Profile}'");
            if (p.Path == null || p.Path.Count < 2) throw new Exception("нет path");
            var pts = prof.Pts.Select(q => new Vector2(q[0], q[1])).ToList();
            // close the section along its back (it lies on the carcass): the overhang into an opening shows its back too
            if ((pts[0] - pts[pts.Count - 1]).sqrMagnitude > 1e-6f) pts.Add(pts[0]);
            var path = p.Path.Select(q => new Vector2(q[0], q[1])).ToList();
            bool closed = p.Closed;
            if (closed && Area(path) < 0f) path.Reverse();              // counter-clockwise: the profile lies inside
            if (!closed && p.Side < 0) pts = pts.Select(q => new Vector2(-q.x, q.y)).Reverse().ToList();
            var pl = PlaneOf(p.Plane);
            _g.Sweep(Solid(p), pl, path, closed, pts, p.Z, Mat(p.Mat ?? "front"), caps: closed ? 0 : 1);
        }

        CasePlane PlaneOf(string plane)
        {
            switch ((plane ?? "front").ToLowerInvariant())
            {
                case "top": return CasePlane.Top;
                case "left": return CasePlane.Left;
                case "right": return CasePlane.Right(_d.Size[1]);
                default: return CasePlane.Front;
            }
        }

        static float Area(List<Vector2> p)
        {
            float s = 0f;
            for (int i = 0; i < p.Count; i++) { var a = p[i]; var b = p[(i + 1) % p.Count]; s += a.x * b.y - b.x * a.y; }
            return s * 0.5f;
        }

        /// <summary>A round bar along the box's longest axis (legs, hanger rails), as thick as the box's smaller side.</summary>
        void Tube(CasePart p)
        {
            var b = p.Box ?? throw new Exception("нет box");
            float x0 = Mathf.Min(b[0], b[3]), x1 = Mathf.Max(b[0], b[3]), y0 = Mathf.Min(b[1], b[4]), y1 = Mathf.Max(b[1], b[4]);
            float z0 = Mathf.Min(b[2], b[5]), z1 = Mathf.Max(b[2], b[5]);
            float dx = x1 - x0, dy = y1 - y0, dz = z1 - z0;
            CasePlane pl; float ca, cb, d, w0, w1;
            if (dy >= dx && dy >= dz) { pl = CasePlane.Top; ca = (x0 + x1) * 0.5f; cb = (z0 + z1) * 0.5f; d = Mathf.Min(dx, dz); w0 = y0; w1 = y1; }
            else if (dx >= dz) { pl = new CasePlane(Vector3.zero, Vector3.forward, Vector3.up, Vector3.right); ca = (z0 + z1) * 0.5f; cb = (y0 + y1) * 0.5f; d = Mathf.Min(dy, dz); w0 = x0; w1 = x1; }
            else { pl = CasePlane.Front; ca = (x0 + x1) * 0.5f; cb = (y0 + y1) * 0.5f; d = Mathf.Min(dx, dy); w0 = z0; w1 = z1; }
            var region = new PathsD { CaseGeo.Ellipse(ca, cb, d * 0.5f, d * 0.5f, 28) };
            _g.Slab(Solid(p), pl, region, w0, w1, p.Edge ?? 1f, Mat(p.Mat ?? "metal"));
        }

        /// <summary>Handles on a front face (z = <see cref="CasePart.Z"/>): ring-half (a flat half ring on two posts), knob, bar.</summary>
        void Handle(CasePart p)
        {
            if (p.At == null || p.At.Length < 2) throw new Exception("нет at");
            var mb = Solid(p);
            var m = Mat(p.Mat ?? "metal");
            float x = p.At[0], y = p.At[1];
            float d = p.D > 0 ? p.D : 80f, band = p.Band > 0 ? p.Band : 10f, t = p.T > 0 ? p.T : 6f, off = p.Standoff > 0 ? p.Standoff : 8f;
            bool back = string.Equals(p.On, "back", StringComparison.OrdinalIgnoreCase);
            // a back face looks towards −z: the front plane turned round, its depths negated
            var pl = back ? new CasePlane(Vector3.zero, Vector3.right, Vector3.up, Vector3.back) : CasePlane.Front;
            float z = back ? -p.Z : p.Z;
            bool squarePosts = string.Equals(p.Section, "square", StringComparison.OrdinalIgnoreCase);
            float post = p.Post > 0 ? p.Post : band * 0.7f;
            PathD Post(float cx, float cy) => squarePosts ? CaseGeo.Rect(cx - post * 0.5f, cy - post * 0.5f, cx + post * 0.5f, cy + post * 0.5f)
                                                          : CaseGeo.Ellipse(cx, cy, post * 0.5f, post * 0.5f, 14);
            string model = (p.Model ?? "ring-half").ToLowerInvariant();
            if (model == "ring-half")
            {
                var dir = Dir(p.Dir);
                float ro = d * 0.5f, ri = ro - band;
                _g.Slab(mb, pl, new PathsD { CaseGeo.HalfRing(x, y, ro, ri, dir) }, z + off, z + off + t, 0.8f, m);
                // posts near both ends of the arc, into the front
                float rm = (ro + ri) * 0.5f, a0 = Mathf.Atan2(dir.y, dir.x);
                foreach (float a in new[] { a0 - Mathf.PI * 0.5f + 0.35f, a0 + Mathf.PI * 0.5f - 0.35f })
                {
                    var c = CaseGeo.Ellipse(x + rm * Mathf.Cos(a), y + rm * Mathf.Sin(a), band * 0.3f, band * 0.3f, 14);
                    _g.Slab(mb, pl, new PathsD { c }, z, z + off + 0.5f, 0.3f, m, back: false);
                }
            }
            else if (model == "knob")
            {
                _g.Slab(mb, pl, new PathsD { CaseGeo.Ellipse(x, y, d * 0.5f, d * 0.5f) }, z + off, z + off + t, Mathf.Min(t * 0.4f, 3f), m);
                _g.Slab(mb, pl, new PathsD { CaseGeo.Ellipse(x, y, d * 0.22f, d * 0.22f, 16) }, z, z + off + 0.5f, 0.3f, m, back: false);
            }
            else if (model == "bar")
            {
                var dir = Dir(p.Dir ?? "right");
                float hl = d * 0.5f;
                var a = new Vector2(x, y) - dir * hl; var b = new Vector2(x, y) + dir * hl;
                var perp = new Vector2(-dir.y, dir.x) * band * 0.5f;
                var bar = new PathD { new PointD(a.x - perp.x, a.y - perp.y), new PointD(b.x - perp.x, b.y - perp.y), new PointD(b.x + perp.x, b.y + perp.y), new PointD(a.x + perp.x, a.y + perp.y) };
                if (Clipper.Area(bar) < 0) bar.Reverse();
                _g.Slab(mb, pl, new PathsD { bar }, z + off, z + off + t, Mathf.Min(band, t) * 0.4f, m);
                foreach (float s in new[] { -0.4f, 0.4f })
                {
                    var c = new Vector2(x, y) + dir * (hl * 2f * s);
                    _g.Slab(mb, pl, new PathsD { Post(c.x, c.y) }, z, z + off + 0.5f, 0.3f, m, back: false);
                }
            }
            else if (model == "edge")
            {
                // an edge pull: an L profile over the front's top edge — a leg `band` high on the face and a lip over the
                // edge `standoff` deep (the front's thickness + the metal); at = [the middle, the top edge], d = length
                float hl = d * 0.5f, mt = p.T > 0 ? p.T : 2f, lip = p.Standoff > 0 ? p.Standoff : 18f;
                _g.Slab(mb, pl, new PathsD { CaseGeo.Rect(x - hl, y - band, x + hl, y) }, z, z + mt, 0.4f, m);
                var top = new CasePlane(Vector3.zero, Vector3.right, back ? Vector3.back : Vector3.forward, Vector3.up);
                _g.Slab(mb, top, new PathsD { CaseGeo.Rect(x - hl, z + mt - lip, x + hl, z + mt) }, y, y + mt, 0.4f, m);
            }
            else throw new Exception($"нет модели ручки '{p.Model}'");
        }

        static int? AxisOf(string g)
        {
            switch ((g ?? "").ToLowerInvariant())
            {
                case "x": return 0;
                case "y": return 1;
                case "z": return 2;
                default: return null;
            }
        }

        static Vector2 Dir(string d)
        {
            switch ((d ?? "up").ToLowerInvariant())
            {
                case "down": return Vector2.down;
                case "left": return Vector2.left;
                case "right": return Vector2.right;
                default: return Vector2.up;
            }
        }

        void Mattress(CasePart p)
        {
            var b = p.Box ?? throw new Exception("нет box");
            var a = _g.P(new Vector3(b[0], b[1], b[2]));
            var c = _g.P(new Vector3(b[3], b[4], b[5]));
            _b.D.RoundBox(Vector3.Min(a, c), Vector3.Max(a, c), (p.Edge ?? 40f) / 1000f, Mat(p.Mat ?? "bedding"), 3, 4, 0.006f);
        }

        // ------------------------------------------------------------------ materials
        /// <summary>
        /// A material role: body / front / back (the finish), metal (the collection's handles and legs), gold, chrome, black,
        /// white, glass, mirror, led, bedding; anything else is a library material ("name#rrggbb").
        /// </summary>
        Material Mat(string role)
        {
            if (_mats.TryGetValue(role, out var m)) return m;
            var M = _b.M;
            var body = _b.C.Mats.Get(_fin?.Body ?? "door_enamel_whitey#e8e6e0", M.GlossWhite);
            if (_fin?.Roles != null && _fin.Roles.TryGetValue(role, out var named) && !string.IsNullOrEmpty(named))
            {
                m = named.StartsWith("gloss") || named.StartsWith("gold") || named.StartsWith("chrome") || named.StartsWith("black")
                    ? Special(named) : _b.C.Mats.Get(named, body);
                _mats[role] = m;
                return m;
            }
            switch (role.ToLowerInvariant())
            {
                case "body": m = body; break;
                case "fabric": m = M.Linen; break;
                case "front": m = _fin?.Front != null ? _b.C.Mats.Get(_fin.Front, body) : body; break;
                case "back": m = _fin?.Back != null ? _b.C.Mats.Get(_fin.Back, body) : body; break;
                case "metal": m = Metal(_col?.Metal ?? "chrome"); break;
                case "glass": m = M.Glass; break;
                case "mirror": m = M.Mirror; break;
                case "led": m = M.Led; break;
                case "bedding": m = M.Bedding; break;
                case "white": m = _b.C.Mats.Get("door_enamel_whitey#f1f0ec", M.GlossWhite); break;
                default:
                    m = role.StartsWith("gold") || role.StartsWith("brass") || role.StartsWith("chrome") || role.StartsWith("black") || role.StartsWith("gloss")
                        ? Special(role) : _b.C.Mats.Get(role, body);
                    break;
            }
            _mats[role] = m;
            return m;
        }

        /// <summary>Metals and high gloss: "gold#d9c189", "chrome", "black", "gloss#f2f2ef" (lacquered high-gloss fronts).</summary>
        Material Special(string spec)
        {
            if (spec.StartsWith("gloss"))
            {
                int i = spec.IndexOf('#');
                return i >= 0 ? _b.C.Mats.Tint(_b.M.GlossWhite, spec.Substring(i)) : _b.M.GlossWhite;
            }
            return Metal(spec);
        }

        /// <summary>gold / brass / chrome / black, optionally tinted: "gold#d9c189".</summary>
        Material Metal(string spec)
        {
            var M = _b.M;
            int i = spec.IndexOf('#');
            string kind = (i >= 0 ? spec.Substring(0, i) : spec).ToLowerInvariant();
            string hex = i >= 0 ? spec.Substring(i) : null;
            var baseM = kind == "gold" || kind == "brass" ? M.Brass : kind == "black" ? M.BlackMetal : M.Chrome;
            return hex != null ? _b.C.Mats.Tint(baseM, hex) : baseM;
        }

        Material GlassTint(string tint)
        {
            switch ((tint ?? "clear").ToLowerInvariant())
            {
                case "satin": case "frosted": return _b.M.DoorSatin ?? _b.M.Glass;
                case "mirror": return _b.M.Mirror;
                case "bronze": return _b.C.Mats.Tint(_b.M.Glass, "#8c6b4a40");
                case "grey": case "gray": return _b.C.Mats.Tint(_b.M.Glass, "#5a5e6040");
                case "black": case "smoke": return _b.C.Mats.Tint(_b.M.Glass, "#1c1d1f70");
                default: return _b.M.Glass;
            }
        }
    }
}
