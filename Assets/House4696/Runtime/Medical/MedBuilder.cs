using System;
using System.Collections.Generic;
using Clipper2Lib;
using House4696.Casegoods;
using House4696.Core;
using House4696.Generation;
using UnityEngine;

namespace House4696.Medical
{
    /// <summary>
    /// Builds a medical device from its <see cref="MedDesign"/> into an item: every part in the design's millimetres,
    /// mapped like the case furniture (x from the left, y up, z from the back; the item's front faces −Z, origin at the
    /// middle of the back on the floor). Solid parts collide, soft ones (cables, lamps) do not, glass goes to the glass
    /// mesh. See Docs/medical-designs.md.
    /// </summary>
    public sealed class MedBuilder
    {
        readonly ItemBuild _b;
        readonly MedDesign _d;
        readonly CaseGeo _g;
        readonly float _halfW;
        readonly Dictionary<string, Material> _mats = new Dictionary<string, Material>(StringComparer.OrdinalIgnoreCase);

        public static void Build(ItemBuild b, MedModel model)
        {
            var d = MedCatalog.Design(model.Design ?? model.Id);
            if (d == null) throw new Exception($"нет чертежа Medical/Designs/{model.Design ?? model.Id}.json");
            if (d.Size == null || d.Size.Length < 3) throw new Exception("у чертежа нет size [W, D, H]");
            new MedBuilder(b, d, model.Mount).Run();
        }

        MedBuilder(ItemBuild b, MedDesign d, string mount)
        {
            _b = b; _d = d;
            _halfW = d.Size[0] * 0.5f;
            // a wall device hangs from its middle (like wall casegoods); others stand on the floor
            _g = new CaseGeo(d.Size[0], mount == "wall" ? d.Size[2] * 0.5f : mount == "ceiling" ? d.Size[2] : 0f);
        }

        void Run()
        {
            foreach (var p in _d.Parts)
            {
                try
                {
                    // (shift in design axes, shift in the part's turned frame) of every copy
                    var offs = new List<(Vector3 world, Vector3 local)> { (Vector3.zero, Vector3.zero) };
                    if (p.Copies != null)
                        foreach (var c in p.Copies) if (c != null && c.Length >= 3) offs.Add((new Vector3(c[0], c[1], c[2]), Vector3.zero));
                    if (p.Repeat != null && p.Repeat.Step != null && p.Repeat.Step.Length >= 3)
                    {
                        var step = new Vector3(p.Repeat.Step[0], p.Repeat.Step[1], p.Repeat.Step[2]);
                        int count = offs.Count;
                        for (int k = 1; k < Mathf.Clamp(p.Repeat.N, 1, 200); k++)
                            for (int i = 0; i < count; i++)
                                offs.Add(p.Repeat.Local ? (offs[i].world, offs[i].local + step * k) : (offs[i].world + step * k, offs[i].local));
                    }
                    bool mir = string.Equals(p.Mirror, "x", StringComparison.OrdinalIgnoreCase);
                    foreach (var o in offs) { Placed(p, o.world, o.local, false); if (mir) Placed(p, o.world, o.local, true); }
                }
                catch (Exception e) { throw new Exception($"деталь '{p.Id}' ({p.Kind}): {e.Message}"); }
            }
        }

        /// <summary>One copy of a part: shifted by <paramref name="offMm"/>, turned by its Rot, mirrored about the width's middle.</summary>
        void Placed(MedPart p, Vector3 offMm, Vector3 localMm, bool mirror)
        {
            var mb = Target(p);
            var keep = mb.Transform;
            bool flip = mb.FlipWinding;
            var m = Matrix4x4.identity;
            if (mirror) m = Matrix4x4.Scale(new Vector3(-1f, 1f, 1f));        // x = 0 is the width's middle after P()
            if (offMm != Vector3.zero) m = m * Matrix4x4.Translate(new Vector3(offMm.x, offMm.y, -offMm.z) / 1000f);
            // Rot, then each of Rots: every turn about its own line in design coordinates
            var turn = Matrix4x4.identity;
            if (p.Rot != null) turn = Turn(p.Rot) * turn;
            if (p.Rots != null) foreach (var r in p.Rots) if (r != null) turn = Turn(r) * turn;
            m = m * turn;
            // a local shift moves the part before it turns: along the tilted face
            if (localMm != Vector3.zero) m = m * Matrix4x4.Translate(new Vector3(localMm.x, localMm.y, -localMm.z) / 1000f);
            mb.Transform = keep * m;
            if (mirror) mb.FlipWinding = !flip;
            try { Part(p, mb); }
            finally { mb.Transform = keep; mb.FlipWinding = flip; }
        }

        /// <summary>The turn of one rotation (casegoods convention: +deg about x turns y towards z; design z = −item z).</summary>
        Matrix4x4 Turn(MedRot r)
        {
            if (Mathf.Abs(r.Deg) <= 1e-3f) return Matrix4x4.identity;
            var about = r.About != null && r.About.Length >= 3 ? _g.P(V(r.About)) : Vector3.zero;
            Quaternion q;
            switch ((r.Axis ?? "x").ToLowerInvariant())
            {
                case "y": q = Quaternion.Euler(0f, -r.Deg, 0f); break;
                case "z": q = Quaternion.Euler(0f, 0f, r.Deg); break;
                default: q = Quaternion.Euler(-r.Deg, 0f, 0f); break;
            }
            return Matrix4x4.Translate(about) * Matrix4x4.Rotate(q) * Matrix4x4.Translate(-about);
        }

        MeshBuilder Target(MedPart p)
        {
            string mat = (p.Mat ?? "").ToLowerInvariant();
            if (mat == "glass" || mat.StartsWith("glass#") || mat.StartsWith("acrylic")) return _b.G;
            // a role mapped to glass or acrylic
            if (_d.Mats != null && p.Mat != null && _d.Mats.TryGetValue(p.Mat, out var role))
            {
                role = role.ToLowerInvariant();
                if (role == "glass" || role.StartsWith("glass#") || role.StartsWith("acrylic")) return _b.G;
            }
            // decals (pictures on faces) always go to the decal mesh: no collider, no shadow
            return p.Soft || string.Equals(p.Kind, "decal", StringComparison.OrdinalIgnoreCase) ? _b.D : _b.F;
        }

        static Vector3 V(float[] a, int i = 0) => new Vector3(a[i], a[i + 1], a[i + 2]);

        // ------------------------------------------------------------------ parts
        void Part(MedPart p, MeshBuilder mb)
        {
            var mat = Mat(p.Mat);
            switch ((p.Kind ?? "box").ToLowerInvariant())
            {
                case "box": Box(p, mb, mat); break;
                case "cyl": case "cylinder": case "rod": Cyl(p, mb, mat); break;
                case "tube": Tube(p, mb, mat); break;
                case "lathe": Lathe(p, mb, mat); break;
                case "sphere": Sphere(p, mb, mat); break;
                case "slab": Slab(p, mb, mat); break;
                case "loft": Loft(p, mb, mat); break;
                case "screen": Screen(p, mb, mat); break;
                case "caster": Caster(p, mb); break;
                case "wheel": Wheel(p, mb, mat); break;
                case "bar": Bar(p, mb, mat); break;
                case "sweep": Sweep(p, mb, mat); break;
                case "strap": Strap(p, mb, mat); break;
                case "coil": Coil(p, mb, mat); break;
                case "decal": Decal(p, mb, mat); break;
                default: throw new Exception($"неизвестный вид детали '{p.Kind}'");
            }
        }

        (Vector3 min, Vector3 max) Bounds(float[] box)
        {
            if (box == null || box.Length < 6) throw new Exception("нужен box [x0, y0, z0, x1, y1, z1]");
            Vector3 a = _g.P(V(box)), b = _g.P(V(box, 3));
            return (Vector3.Min(a, b), Vector3.Max(a, b));
        }

        void Box(MedPart p, MeshBuilder mb, Material m)
        {
            var (min, max) = Bounds(p.Box);
            float r = p.R / 1000f;
            int inner = p.Puff > 0f ? 4 : 0;
            if (r <= 0.0005f && p.Puff <= 0f) mb.Box(min, max, m);
            else mb.RoundBox(min, max, Mathf.Max(r, 0.001f), m, r > 0.02f ? 5 : 3, inner, p.Puff / 1000f);
        }

        void Cyl(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.From == null || p.To == null) throw new Exception("нужны from и to");
            float r0 = (p.D > 0 ? p.D : 20f) * 0.5f, r1 = (p.D2 > 0 ? p.D2 : p.D > 0 ? p.D : 20f) * 0.5f;
            _g.Rod(mb, V(p.From), V(p.To), r0, r1, m, false, p.Sides > 0 ? p.Sides : r0 > 40f ? 32 : 20);
        }

        /// <summary>A bent tube: the path's corners rounded with <see cref="MedPart.Bend"/>, swept with a round section.</summary>
        void Tube(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.Path == null || p.Path.Count < 2) throw new Exception("трубе нужен path из 2+ точек");
            if (p.Rib > 0f) { Sweep(p, mb, m); return; }
            var pts = new List<Vector3>();
            foreach (var q in p.Path) pts.Add(_g.P(V(q)));
            var path = p.Bend > 0f ? Rounded(pts, p.Bend / 1000f) : pts;
            mb.Tube(path.ToArray(), (p.D > 0 ? p.D : 25f) * 0.0005f, m, p.Sides > 0 ? p.Sides : 14);
            if (p.Caps != false)
            {
                // flat ends
                foreach (var (a, b) in new[] { (path[0], path[1]), (path[path.Count - 1], path[path.Count - 2]) })
                    using (mb.Place(a, Quaternion.FromToRotation(Vector3.up, (a - b).normalized)))
                        mb.Disk(Vector3.zero, (p.D > 0 ? p.D : 25f) * 0.0005f, m, false, p.Sides > 0 ? p.Sides : 14);
            }
        }

        /// <summary>Polyline with every inner corner replaced by an arc of radius <paramref name="r"/> (metres).</summary>
        static List<Vector3> Rounded(List<Vector3> pts, float r)
        {
            var res = new List<Vector3> { pts[0] };
            for (int i = 1; i + 1 < pts.Count; i++)
            {
                Vector3 a = pts[i - 1], c = pts[i], b = pts[i + 1];
                Vector3 da = (a - c).normalized, db = (b - c).normalized;
                float ang = Vector3.Angle(da, db) * Mathf.Deg2Rad;
                if (ang < 1e-3f || ang > Mathf.PI - 1e-3f) { res.Add(c); continue; }
                float t = Mathf.Min(r / Mathf.Tan(ang * 0.5f), (a - c).magnitude * 0.49f, (b - c).magnitude * 0.49f);
                Vector3 p0 = c + da * t, p1 = c + db * t;
                const int n = 8;
                for (int k = 0; k <= n; k++)
                {
                    float s = k / (float)n;
                    // quadratic Bézier through the corner: close to a circular arc for these angles
                    var q = (1 - s) * (1 - s) * p0 + 2 * (1 - s) * s * c + s * s * p1;
                    res.Add(q);
                }
            }
            res.Add(pts[pts.Count - 1]);
            return res;
        }

        Quaternion AxisRot(string axis)
        {
            switch ((axis ?? "y").ToLowerInvariant())
            {
                case "x": return Quaternion.Euler(0f, 0f, -90f);   // local up → +x
                case "z": return Quaternion.Euler(-90f, 0f, 0f);   // local up → −z item = +z design
                default: return Quaternion.identity;
            }
        }

        void Lathe(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.At == null || p.Profile == null || p.Profile.Count < 2) throw new Exception("нужны at и profile [[r, h], …]");
            var prof = new Vector2[p.Profile.Count];
            for (int i = 0; i < prof.Length; i++) prof[i] = new Vector2(p.Profile[i][0], p.Profile[i][1]) / 1000f;
            using (mb.Place(_g.P(V(p.At)), AxisRot(p.Axis)))
                mb.Lathe(Vector3.zero, prof, p.Sides > 0 ? p.Sides : 32, m, p.Caps != false, p.Caps != false);
        }

        void Sphere(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.At == null) throw new Exception("нужен at");
            var r = p.Radii != null && p.Radii.Length >= 3 ? new Vector3(p.Radii[0], p.Radii[1], p.Radii[2]) / 1000f : Vector3.one * (p.D > 0 ? p.D : 50f) * 0.0005f;
            mb.Sphere(_g.P(V(p.At)), r, m, p.Sides > 0 ? p.Sides : 28, 16);
        }

        /// <summary>An outline (SVG path or the box's rectangle with rounded corners) extruded across its plane, edges rounded.</summary>
        void Slab(MedPart p, MeshBuilder mb, Material m)
        {
            string plane = (p.Plane ?? "front").ToLowerInvariant();
            CasePlane pl = plane == "top" ? CasePlane.Top : plane == "side" ? new CasePlane(Vector3.zero, Vector3.forward, Vector3.up, Vector3.right) : CasePlane.Front;
            PathsD region;
            float w0, w1;
            if (p.Outline != null)
            {
                region = new PathsD();
                foreach (var poly in House4696.Doors.Shape2D.ParsePath(p.Outline, 0.5f))
                {
                    if (!poly.Closed || poly.P.Count < 3) continue;
                    var path = new PathD();
                    foreach (var q in poly.P) path.Add(new PointD(q.x, q.y));
                    if (Clipper.Area(path) < 0) path.Reverse();
                    region.Add(path);
                }
                if (region.Count == 0) throw new Exception("outline не даёт замкнутого контура");
                region = Clipper.Union(region, new PathsD(), FillRule.EvenOdd, 3);
                if (p.W == null || p.W.Length < 2) throw new Exception("slab с outline: нужен w [от, до]");
                w0 = p.W[0]; w1 = p.W[1];
            }
            else
            {
                var bx = p.Box ?? throw new Exception("slab: нужен outline или box");
                float x0 = Mathf.Min(bx[0], bx[3]), x1 = Mathf.Max(bx[0], bx[3]), y0 = Mathf.Min(bx[1], bx[4]), y1 = Mathf.Max(bx[1], bx[4]);
                float z0 = Mathf.Min(bx[2], bx[5]), z1 = Mathf.Max(bx[2], bx[5]);
                float a0, b0, a1, b1;
                if (plane == "top") { a0 = x0; b0 = z0; a1 = x1; b1 = z1; w0 = y0; w1 = y1; }
                else if (plane == "side") { a0 = z0; b0 = y0; a1 = z1; b1 = y1; w0 = x0; w1 = x1; }
                else { a0 = x0; b0 = y0; a1 = x1; b1 = y1; w0 = z0; w1 = z1; }
                float cr = p.Radii != null && p.Radii.Length > 0 ? p.Radii[0] : 0f;     // corner radius of the outline
                region = new PathsD { cr > 0 ? CaseGeo.RoundRect(a0, b0, a1, b1, cr) : CaseGeo.Rect(a0, b0, a1, b1) };
            }
            _g.Slab(mb, pl, region, w0, w1, Mathf.Max(p.R, 0.5f), m);
        }

        /// <summary>
        /// Rounded-rectangle sections along an axis (y by default) joined into one smooth shell, capped: tapered columns,
        /// curved housings of carts and robots, shells of capsules.
        /// </summary>
        void Loft(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.Sections == null || p.Sections.Count < 2) throw new Exception("loft: нужно 2+ sections");
            const int perCorner = 6;
            int ring = perCorner * 4 + 4;
            string axis = (p.Axis ?? "y").ToLowerInvariant();
            // a section point (u across x, v across z) at position t along the axis → design mm
            Vector3 Pt(MedSection s, float u, float v)
            {
                switch (axis)
                {
                    case "x": return new Vector3(s.At, s.Cx + v, s.Cz + u);       // u → z, v → y
                    case "z": return new Vector3(s.Cx + u, s.Cz + v, s.At);       // u → x, v → y
                    default: return new Vector3(s.Cx + u, s.At, s.Cz + v);        // u → x, v → z
                }
            }
            List<Vector2> Outline(MedSection s)
            {
                float hw = s.W * 0.5f, hd = s.D * 0.5f, r = Mathf.Clamp(s.R, 0f, Mathf.Min(hw, hd));
                var pts = new List<Vector2>(ring);
                var corners = new[] { new Vector2(hw - r, hd - r), new Vector2(-hw + r, hd - r), new Vector2(-hw + r, -hd + r), new Vector2(hw - r, -hd + r) };
                for (int c = 0; c < 4; c++)
                    for (int k = 0; k <= perCorner; k++)
                    {
                        float a = (c * 90f + 90f * k / perCorner) * Mathf.Deg2Rad;
                        pts.Add(corners[c] + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * r);
                    }
                return pts;
            }
            var secs = new List<MedSection>(p.Sections);
            string dome = (p.Dome ?? "").ToLowerInvariant();
            List<MedSection> DomeOf(MedSection s, MedSection inner, bool atEnd)
            {
                // the end section shrinks over an elliptic quarter to a point, continuing away from the shell
                float dir = Mathf.Sign(s.At - inner.At); if (dir == 0) dir = 1f;
                float h = p.DomeH > 0 ? p.DomeH : Mathf.Min(s.W, s.D) * 0.5f;
                var list = new List<MedSection>();
                const int n = 6;
                for (int k = 1; k <= n; k++)
                {
                    float a = k / (float)n * Mathf.PI * 0.5f, sc = Mathf.Max(Mathf.Cos(a), 0.02f);
                    list.Add(new MedSection { At = s.At + dir * h * Mathf.Sin(a), W = s.W * sc, D = s.D * sc, R = s.R * sc, Cx = s.Cx, Cz = s.Cz });
                }
                if (!atEnd) list.Reverse();
                return list;
            }
            if (dome == "start" || dome == "both") secs.InsertRange(0, DomeOf(p.Sections[0], p.Sections[1], false));
            if (dome == "end" || dome == "both") secs.AddRange(DomeOf(p.Sections[p.Sections.Count - 1], p.Sections[p.Sections.Count - 2], true));
            var rings = new List<Vector3[]>();
            foreach (var s in secs)
            {
                var o = Outline(s);
                var r = new Vector3[o.Count];
                for (int i = 0; i < o.Count; i++) r[i] = _g.P(Pt(s, o[i].x, o[i].y));
                rings.Add(r);
            }
            int n = rings[0].Length;
            var centres = new Vector3[rings.Count];
            for (int k = 0; k < rings.Count; k++) { var c = Vector3.zero; foreach (var q in rings[k]) c += q; centres[k] = c / n; }
            // normals by finite differences over the grid, turned to point away from the section's centre
            var N = new Vector3[rings.Count, n];
            for (int k = 0; k < rings.Count; k++)
                for (int i = 0; i < n; i++)
                {
                    var du = rings[k][(i + 1) % n] - rings[k][(i - 1 + n) % n];
                    var dv = rings[Mathf.Min(k + 1, rings.Count - 1)][i] - rings[Mathf.Max(k - 1, 0)][i];
                    var nn = Vector3.Cross(dv, du);
                    if (nn.sqrMagnitude < 1e-14f) nn = rings[k][i] - centres[k];
                    nn.Normalize();
                    if (Vector3.Dot(nn, rings[k][i] - centres[k]) < 0f) nn = -nn;
                    N[k, i] = nn;
                }
            float vAcc = 0f;
            for (int k = 0; k + 1 < rings.Count; k++)
            {
                float len = (centres[k + 1] - centres[k]).magnitude;
                float uAcc = 0f;
                for (int i = 0; i < n; i++)
                {
                    int j = (i + 1) % n;
                    float seg = (rings[k][j] - rings[k][i]).magnitude;
                    Tri(mb, rings[k][i], rings[k][j], rings[k + 1][j], N[k, i], N[k, j], N[k + 1, j],
                        new Vector2(uAcc, vAcc), new Vector2(uAcc + seg, vAcc), new Vector2(uAcc + seg, vAcc + len), m);
                    Tri(mb, rings[k][i], rings[k + 1][j], rings[k + 1][i], N[k, i], N[k + 1, j], N[k + 1, i],
                        new Vector2(uAcc, vAcc), new Vector2(uAcc + seg, vAcc + len), new Vector2(uAcc, vAcc + len), m);
                    uAcc += seg;
                }
                vAcc += len;
            }
            if (p.Caps != false)
            {
                var dir = (centres[rings.Count - 1] - centres[0]).normalized;
                Cap(mb, rings[0], centres[0], -dir, m);
                Cap(mb, rings[rings.Count - 1], centres[rings.Count - 1], dir, m);
            }
        }

        /// <summary>A triangle wound so that it faces the side its normals point to (Unity: clockwise seen from the front).</summary>
        static void Tri(MeshBuilder mb, Vector3 a, Vector3 b, Vector3 c, Vector3 na, Vector3 nb, Vector3 nc, Vector2 ua, Vector2 ub, Vector2 uc, Material m)
        {
            var avg = na + nb + nc;
            if (Vector3.Dot(Vector3.Cross(b - a, c - a), avg) >= 0f) mb.Triangle(a, b, c, na, nb, nc, ua, ub, uc, m);
            else mb.Triangle(a, c, b, na, nc, nb, ua, uc, ub, m);
        }

        /// <summary>A flat fan over a ring facing <paramref name="nrm"/>.</summary>
        static void Cap(MeshBuilder mb, Vector3[] ring, Vector3 c, Vector3 nrm, Material m)
        {
            for (int i = 0; i < ring.Length; i++)
            {
                int j = (i + 1) % ring.Length;
                if (Vector3.Cross(ring[i] - c, ring[j] - c).sqrMagnitude < 1e-14f) continue;
                Tri(mb, c, ring[i], ring[j], nrm, nrm, nrm, Vector2.zero, Vector2.right, Vector2.up, m);
            }
        }

        /// <summary>A straight bar between two points with a rounded-rectangle section [w, h] (roll about its axis).</summary>
        void Bar(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.From == null || p.To == null) throw new Exception("bar: нужны from и to");
            Vector3 a = _g.P(V(p.From)), b = _g.P(V(p.To));
            var d = b - a; float len = d.magnitude;
            if (len < 1e-4f) return;
            float w = (p.Section != null && p.Section.Length > 0 ? p.Section[0] : 30f) / 1000f;
            float h = (p.Section != null && p.Section.Length > 1 ? p.Section[1] : w * 1000f) / 1000f;
            var dir = d / len;
            var up = Mathf.Abs(Vector3.Dot(dir, Vector3.up)) > 0.95f ? Vector3.forward : Vector3.up;
            var rot = Quaternion.LookRotation(dir, up) * Quaternion.Euler(0f, 0f, p.Roll);
            using (mb.Place(a, rot))
                mb.RoundBox(new Vector3(-w * 0.5f, -h * 0.5f, 0f), new Vector3(w * 0.5f, h * 0.5f, len), Mathf.Clamp(p.R / 1000f, 0.0005f, Mathf.Min(w, h) * 0.5f), m, 3);
        }

        /// <summary>A section (rect with corner radius R, oval, round) swept along the path, its corners bent with Bend; ribs optional.</summary>
        void Sweep(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.Path == null || p.Path.Count < 2) throw new Exception("sweep: нужен path из 2+ точек");
            var pts = new List<Vector3>();
            foreach (var q in p.Path) pts.Add(_g.P(V(q)));
            if (p.Bend > 0f) pts = Rounded(pts, p.Bend / 1000f);
            string shape = (p.Shape ?? (p.Section != null ? "rect" : "round")).ToLowerInvariant();
            float w = (p.Section != null && p.Section.Length > 0 ? p.Section[0] : p.D > 0 ? p.D : 25f) / 1000f;
            float h = (p.Section != null && p.Section.Length > 1 ? p.Section[1] : w * 1000f) / 1000f;
            if (shape == "round") w = h = (p.D > 0 ? p.D : w * 1000f) / 1000f;
            SweepSection(mb, pts, Section(shape, w, h, p.R / 1000f), m, p.Roll, p.Rib / 1000f, p.Pitch > 0 ? p.Pitch / 1000f : 0.025f, p.Caps != false);
        }

        /// <summary>A flat strap: a thin rect section [w, t] along a path (harness straps, belts).</summary>
        void Strap(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.Path == null || p.Path.Count < 2) throw new Exception("strap: нужен path из 2+ точек");
            var pts = new List<Vector3>();
            foreach (var q in p.Path) pts.Add(_g.P(V(q)));
            if (p.Bend > 0f) pts = Rounded(pts, p.Bend / 1000f);
            float w = (p.Section != null && p.Section.Length > 0 ? p.Section[0] : 40f) / 1000f;
            float t = (p.Section != null && p.Section.Length > 1 ? p.Section[1] : 3f) / 1000f;
            SweepSection(mb, pts, Section("rect", w, t, t * 0.4f), m ?? Mat("fabric#2a2c30"), p.Roll, 0f, 0f, true);
        }

        /// <summary>A coiled cable from → to: <see cref="MedPart.Turns"/> turns of coil diameter D, wire D2.</summary>
        void Coil(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.From == null || p.To == null) throw new Exception("coil: нужны from и to");
            Vector3 a = _g.P(V(p.From)), b = _g.P(V(p.To));
            var axis = b - a; float len = axis.magnitude;
            if (len < 1e-4f) return;
            var dir = axis / len;
            var u = Vector3.Cross(dir, Mathf.Abs(dir.y) < 0.9f ? Vector3.up : Vector3.right).normalized;
            var v = Vector3.Cross(dir, u);
            float rc = (p.D > 0 ? p.D : 30f) * 0.0005f, rw = (p.D2 > 0 ? p.D2 : 5f) * 0.0005f;
            float turns = p.Turns > 0 ? p.Turns : len / (rw * 2.6f);
            int n = Mathf.Clamp(Mathf.CeilToInt(turns * 12f), 12, 2000);
            var pts = new List<Vector3>(n + 1);
            for (int i = 0; i <= n; i++)
            {
                float t = i / (float)n, ang = t * turns * Mathf.PI * 2f;
                pts.Add(a + dir * (len * t) + (u * Mathf.Cos(ang) + v * Mathf.Sin(ang)) * rc);
            }
            SweepSection(mb, pts, Section("round", rw * 2f, rw * 2f, 0f), m, 0f, 0f, 0f, true, 8);
        }

        /// <summary>A flat picture or colour plate on a face: centred at At, Size [w, h], facing Face (front/back/left/right/top).</summary>
        void Decal(MedPart p, MeshBuilder dmb, Material m)
        {
            if (p.At == null || p.Size == null || p.Size.Length < 2) throw new Exception("decal: нужны at и size [w, h]");
            var pic = p.Print != null ? _b.C.Mats.Get(p.Print, m) : m;
            var c = _g.P(V(p.At));
            float w = p.Size[0] / 1000f, h = p.Size[1] / 1000f;
            var face = (p.Face ?? "front").ToLowerInvariant();
            Vector3 n = face == "back" ? Vector3.forward : face == "left" ? Vector3.left : face == "right" ? Vector3.right : face == "top" ? Vector3.up : Vector3.back;
            dmb.Picture(c + n * 0.0012f, n, w, h, face == "back" ? new Rect(1, 0, -1, 1) : new Rect(0, 0, 1, 1), pic);
        }

        /// <summary>Section outline (metres, counter-clockwise) of the given shape.</summary>
        static List<Vector2> Section(string shape, float w, float h, float r)
        {
            var pts = new List<Vector2>();
            if (shape == "round" || shape == "oval")
            {
                const int n = 20;
                for (int i = 0; i < n; i++) { float a = i * Mathf.PI * 2f / n; pts.Add(new Vector2(Mathf.Cos(a) * w * 0.5f, Mathf.Sin(a) * h * 0.5f)); }
                return pts;
            }
            r = Mathf.Clamp(r, 0f, Mathf.Min(w, h) * 0.5f);
            float hw = w * 0.5f - r, hh = h * 0.5f - r;
            var corners = new[] { new Vector2(hw, hh), new Vector2(-hw, hh), new Vector2(-hw, -hh), new Vector2(hw, -hh) };
            int per = r > 1e-4f ? 4 : 0;
            for (int c = 0; c < 4; c++)
                for (int k = 0; k <= per; k++)
                {
                    float a = (c * 90f + (per == 0 ? 45f : 90f * k / per)) * Mathf.Deg2Rad;
                    pts.Add(corners[c] + (per == 0 ? Vector2.zero : new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * r));
                }
            if (per == 0) { pts.Clear(); pts.Add(new Vector2(w * .5f, h * .5f)); pts.Add(new Vector2(-w * .5f, h * .5f)); pts.Add(new Vector2(-w * .5f, -h * .5f)); pts.Add(new Vector2(w * .5f, -h * .5f)); }
            return pts;
        }

        /// <summary>
        /// Sweeps a section along a path with parallel-transported frames (the section's "up" starts as world up, or
        /// forward for a vertical start), optional roll and ribs; ends capped.
        /// </summary>
        static void SweepSection(MeshBuilder mb, List<Vector3> path, List<Vector2> sec, Material m, float rollDeg, float rib, float pitch, bool caps, int maxSegPerMetre = 0)
        {
            int n = path.Count, k = sec.Count;
            if (n < 2 || k < 3) return;
            var T = new Vector3[n];
            for (int i = 0; i < n; i++)
            {
                var d = path[Mathf.Min(i + 1, n - 1)] - path[Mathf.Max(i - 1, 0)];
                T[i] = d.sqrMagnitude > 1e-12f ? d.normalized : (i > 0 ? T[i - 1] : Vector3.forward);
            }
            var up0 = Mathf.Abs(Vector3.Dot(T[0], Vector3.up)) > 0.95f ? Vector3.forward : Vector3.up;
            var U = new Vector3[n];
            U[0] = Vector3.ProjectOnPlane(up0, T[0]).normalized;
            for (int i = 1; i < n; i++)
            {
                var q = Quaternion.FromToRotation(T[i - 1], T[i]);
                U[i] = Vector3.ProjectOnPlane(q * U[i - 1], T[i]).normalized;
            }
            float roll = rollDeg * Mathf.Deg2Rad;
            var rings = new Vector3[n, k]; var norms = new Vector3[n, k];
            float along = 0f;
            for (int i = 0; i < n; i++)
            {
                if (i > 0) along += (path[i] - path[i - 1]).magnitude;
                var u = U[i]; var r = Vector3.Cross(T[i], u);   // section x → r, y → u
                float bulge = rib > 0f ? 1f + rib / Mathf.Max(1e-4f, 0.5f * (sec[0].magnitude)) * (0.5f + 0.5f * Mathf.Cos(along / pitch * Mathf.PI * 2f)) : 1f;
                for (int j = 0; j < k; j++)
                {
                    var s2 = sec[j];
                    float cx = s2.x * Mathf.Cos(roll) - s2.y * Mathf.Sin(roll), cy = s2.x * Mathf.Sin(roll) + s2.y * Mathf.Cos(roll);
                    var off = (r * cx + u * cy) * bulge;
                    rings[i, j] = path[i] + off;
                    norms[i, j] = off.sqrMagnitude > 1e-14f ? off.normalized : u;
                }
            }
            float v0 = 0f;
            for (int i = 0; i + 1 < n; i++)
            {
                float seg = (path[i + 1] - path[i]).magnitude, u0 = 0f;
                for (int j = 0; j < k; j++)
                {
                    int jn = (j + 1) % k;
                    float e = (rings[i, jn] - rings[i, j]).magnitude;
                    Tri(mb, rings[i, j], rings[i, jn], rings[i + 1, jn], norms[i, j], norms[i, jn], norms[i + 1, jn],
                        new Vector2(u0, v0), new Vector2(u0 + e, v0), new Vector2(u0 + e, v0 + seg), m);
                    Tri(mb, rings[i, j], rings[i + 1, jn], rings[i + 1, j], norms[i, j], norms[i + 1, jn], norms[i + 1, j],
                        new Vector2(u0, v0), new Vector2(u0 + e, v0 + seg), new Vector2(u0, v0 + seg), m);
                    u0 += e;
                }
                v0 += seg;
            }
            if (!caps) return;
            for (int end = 0; end < 2; end++)
            {
                int i = end == 0 ? 0 : n - 1;
                var ring = new Vector3[k];
                for (int j = 0; j < k; j++) ring[j] = rings[i, j];
                Cap(mb, ring, path[i], end == 0 ? -T[0] : T[n - 1], m);
            }
        }

        /// <summary>A rounded box whose <see cref="MedPart.Face"/> shows a screen: the picture (or a dark screen) inside a bezel.</summary>
        void Screen(MedPart p, MeshBuilder mb, Material m)
        {
            var (min, max) = Bounds(p.Box);
            float r = Mathf.Max(p.R, 1f) / 1000f;
            mb.RoundBox(min, max, r, m, 3);
            var pic = p.Print != null ? _b.C.Mats.Get(p.Print, null) : null;
            pic ??= _b.M.Screen ?? _b.M.BlackGlass;
            float bez = (p.Bezel > 0 ? p.Bezel : 12f) / 1000f, off = 0.0015f;
            var face = (p.Face ?? "front").ToLowerInvariant();
            Vector3 c = (min + max) * 0.5f, s = max - min;
            var dmb = _b.D;   // the picture is a decal: no collider of its own
            var keep = dmb.Transform; dmb.Transform = mb.Transform;
            bool flip = dmb.FlipWinding; dmb.FlipWinding = mb.FlipWinding;
            switch (face)
            {
                case "back": dmb.Picture(new Vector3(c.x, c.y, max.z + off), Vector3.forward, s.x - 2 * bez, s.y - 2 * bez, new Rect(1, 0, -1, 1), pic); break;
                case "left": dmb.Picture(new Vector3(min.x - off, c.y, c.z), Vector3.left, s.z - 2 * bez, s.y - 2 * bez, new Rect(0, 0, 1, 1), pic); break;
                case "right": dmb.Picture(new Vector3(max.x + off, c.y, c.z), Vector3.right, s.z - 2 * bez, s.y - 2 * bez, new Rect(0, 0, 1, 1), pic); break;
                case "top": dmb.Picture(new Vector3(c.x, max.y + off, c.z), Vector3.up, s.x - 2 * bez, s.z - 2 * bez, new Rect(0, 0, 1, 1), pic); break;
                default: dmb.Picture(new Vector3(c.x, c.y, min.z - off), Vector3.back, s.x - 2 * bez, s.y - 2 * bez, new Rect(0, 0, 1, 1), pic); break;
            }
            dmb.Transform = keep; dmb.FlipWinding = flip;
        }

        /// <summary>A swivel castor: wheel <see cref="MedPart.D"/> (default 75 mm) under a fork and a stem up to y = d + 25.</summary>
        void Caster(MedPart p, MeshBuilder mb)
        {
            if (p.At == null) throw new Exception("нужен at (точка опоры колеса на полу)");
            float d = p.D > 0 ? p.D : 75f, w = d * 0.32f;
            var at = V(p.At);
            var tyre = Mat(p.Mat ?? "rubber");
            var fork = Mat("chrome");
            var top = at + new Vector3(0, d + 25f, 0);
            // wheel axis along x, offset back from the stem (trailing castor)
            var hub = at + new Vector3(0, d * 0.5f, -d * 0.3f);
            _g.Rod(mb, hub - new Vector3(w * 0.5f, 0, 0), hub + new Vector3(w * 0.5f, 0, 0), d * 0.5f, d * 0.5f, tyre, false, 24);
            _g.Rod(mb, hub - new Vector3(w * 0.5f + 2f, 0, 0), hub + new Vector3(w * 0.5f + 2f, 0, 0), d * 0.22f, d * 0.22f, Mat("plastic#9aa3ad"), false, 16);
            foreach (float sx in new[] { -1f, 1f })
                _g.Rod(mb, hub + new Vector3(sx * (w * 0.5f + 4f), 0, 0), top + new Vector3(sx * (w * 0.5f + 4f), -12f, 0), 5f, 5f, fork, true, 4);
            _g.Rod(mb, top - new Vector3(0, 14f, 0), top, d * 0.3f, d * 0.3f, fork, false, 16);
        }

        /// <summary>A plain wheel: axis along x through <see cref="MedPart.At"/> (its centre), diameter D, width D2 (default D/4).</summary>
        void Wheel(MedPart p, MeshBuilder mb, Material m)
        {
            if (p.At == null) throw new Exception("нужен at (центр колеса)");
            float d = p.D > 0 ? p.D : 100f, w = p.D2 > 0 ? p.D2 : d * 0.25f;
            var c = V(p.At);
            string ax = (p.Axis ?? "x").ToLowerInvariant();
            var dir = ax == "z" ? new Vector3(0, 0, w * 0.5f) : ax == "y" ? new Vector3(0, w * 0.5f, 0) : new Vector3(w * 0.5f, 0, 0);
            _g.Rod(mb, c - dir, c + dir, d * 0.5f, d * 0.5f, m ?? Mat("rubber"), false, 28);
        }

        // ------------------------------------------------------------------ materials
        /// <summary>
        /// A role of the design ("shell") → its material; or a material spec: plastic#hex (satin plastic), gloss#hex (glossy
        /// plastic or lacquer), metal#hex (brushed steel), chrome, black (black metal), rubber, leather#hex (upholstery),
        /// screen, led, glass, or any library material (with an optional #hex tint).
        /// </summary>
        Material Mat(string spec)
        {
            if (string.IsNullOrEmpty(spec)) spec = "shell";
            if (_mats.TryGetValue(spec, out var cached)) return cached;
            string resolved = _d.Mats != null && _d.Mats.TryGetValue(spec, out var role) ? role : spec;
            var m = Resolve(resolved) ?? Resolve("plastic#eef0f2");
            _mats[spec] = m;
            return m;
        }

        Material Resolve(string spec)
        {
            var M = _b.M; var mats = _b.C.Mats;
            int hash = spec.IndexOf('#');
            string kind = (hash >= 0 ? spec.Substring(0, hash) : spec).ToLowerInvariant();
            string hex = hash >= 0 ? spec.Substring(hash) : null;
            Material Tinted(Material baseM, string libName, int mean)
            {
                if (hex == null) return mats.Has(libName) ? mats.Get(libName, baseM) : baseM;
                return mats.Has(libName) ? mats.Get(libName + Over(hex, mean), baseM) : mats.Tint(baseM, hex);
            }
            switch (kind)
            {
                case "plastic": return Tinted(M.WhiteMetal, "lift_painted", 0xe6);
                case "gloss": return hex != null ? mats.Tint(M.GlossWhite, hex) : M.GlossWhite;
                case "metal": case "steel": return Tinted(M.Chrome, "lift_brushed", 0xd8);
                case "chrome": return M.Chrome;
                case "black": return hex != null ? mats.Tint(M.BlackMetal, hex) : M.BlackMetal;
                case "rubber": return mats.Tint(M.BlackMetal, hex ?? "#1d1e20");
                case "leather": return hex != null ? mats.Tint(M.LeatherWhite ?? M.Leather, hex) : M.Leather;
                case "fabric": return Tinted(M.Linen, "cgfab_velur", 0xe0);
                case "screen": return M.Screen ?? M.BlackGlass;
                case "led": return M.Led;
                case "glass": return M.Glass;
                case "acrylic": return mats.Tint(M.Glass, hex ?? "#eef4ff80");
                case "mirror": return M.Mirror;
                case "wood": return hex != null ? mats.Tint(M.OakLight, hex) : M.OakLight;
            }
            return mats.Has(spec) ? mats.Get(spec, null) : null;
        }

        /// <summary>"#rrggbb" that turns a neutral texture of mean grey <paramref name="mean"/> into <paramref name="target"/> (linear).</summary>
        static string Over(string target, int mean)
        {
            if (!ColorUtility.TryParseHtmlString(target, out var t)) return "";
            float ml = Mathf.GammaToLinearSpace(mean / 255f);
            var tl = t.linear;
            var c = new Color(Mathf.Clamp01(tl.r / ml), Mathf.Clamp01(tl.g / ml), Mathf.Clamp01(tl.b / ml)).gamma;
            return "#" + ColorUtility.ToHtmlStringRGB(c).ToLowerInvariant();
        }
    }
}
