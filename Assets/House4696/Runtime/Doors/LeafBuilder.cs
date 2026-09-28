using System;
using System.Collections.Generic;
using System.Globalization;
using House4696.Core;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>Materials of one door by role (see Docs/door-designs.md, "Materials").</summary>
    public sealed class DoorMaterialSet
    {
        public Material Finish, Finish2, Glass, Satin, Clear, Mirror, Black, Metal, Chrome, Seal, LacobelBeige, LacobelWhite, LacobelSmoke;
        /// <summary>Door furniture finishes.</summary>
        public Material Gold, Bronze, BlackMetal;
        /// <summary>Patina paints for moulding crests (roles "gold", "silver").</summary>
        public Material PatinaGold, PatinaSilver, PatinaDark;

        /// <summary>Material of the handles for a design's handle finish.</summary>
        public Material Hardware(string finish)
        {
            switch ((finish ?? "chrome").ToLowerInvariant())
            {
                case "gold": case "brass": return Gold ?? Chrome;
                case "bronze": case "copper": case "brown": return Bronze ?? Chrome;
                case "black": return BlackMetal ?? Chrome;
                case "satin": case "matte": return Metal ?? Chrome;
                default: return Chrome;
            }
        }
        /// <summary>Thickness of the door's own glass, mm (4 tempered, 8 triplex).</summary>
        public float GlassMm = 4f;
        /// <summary>Facet of the door's own glass on shaped panes, mm (0: none).</summary>
        public float GlassFacetMm;
        /// <summary>The door's own glass is a picture stretched over each pane (art glass), not a tiled pattern.</summary>
        public bool GlassFit;
        /// <summary>Library materials by id (art glass named by a design: "art:doorglass_sprig").</summary>
        public System.Func<string, Material> Library;

        /// <summary>Is a glass role a picture to stretch over its pane?</summary>
        public bool Fits(string role) => role != null && role.StartsWith("art:", System.StringComparison.OrdinalIgnoreCase)
                                         || (role == null || role == "glass" || role == "true") && GlassFit;

        public Material Role(string role)
        {
            switch ((role ?? "finish").ToLowerInvariant())
            {
                case "finish": return Finish;
                case "finish2": return Finish2 ?? Finish;
                case "metal": case "aluminium": case "aluminum": return Metal;
                case "chrome": return Chrome;
                case "black": return Black;
                case "black-matte": case "paint-black": return BlackMetal ?? Black;
                case "gold": case "patina-gold": return PatinaGold ?? Gold ?? Finish;
                case "silver": case "patina-silver": return PatinaSilver ?? Chrome ?? Finish;
                case "patina-dark": case "toned": return PatinaDark ?? Finish;
                case "bronze": return Bronze ?? Finish;
                default: return GlassRole(role) ?? Finish;
            }
        }

        public Material GlassRole(string role)
        {
            if (role != null && role.StartsWith("art:", System.StringComparison.OrdinalIgnoreCase)) return Library?.Invoke(role.Substring(4)) ?? Satin;
            switch ((role ?? "glass").ToLowerInvariant())
            {
                case "glass": case "true": return Glass;
                case "satin": return Satin;
                case "clear": return Clear;
                case "mirror": return Mirror;
                case "black": return Black;
                case "lacobel-beige": case "wp": return LacobelBeige;
                case "lacobel-white": case "ww": return LacobelWhite;
                case "lacobel-smoke": case "s": return LacobelSmoke;
                default: return null;
            }
        }
    }

    /// <summary>
    /// Builds a door leaf from its design at the size a house needs. Leaf space (metres): x from the lock edge towards the
    /// hinges, y up from the leaf bottom, z from the leaf's middle plane towards the front face (the face the catalogue
    /// photo shows). Boards go through the leaf, so the back face is the same construction seen from behind.
    /// Opaque parts go to one builder, glass to another (it must not cast solid shadows).
    /// </summary>
    public sealed partial class LeafBuilder
    {
        /// <summary>Cells and parts thinner than this (mm) keep their size when the leaf is resized.</summary>
        public const float ThinMm = 60f;
        /// <summary>Default edge radius of boards (the hairline of a joint), mm.</summary>
        public const float JointRadiusMm = 1.2f;
        /// <summary>How far glass runs into the boards around it (hidden in their grooves), mm.</summary>
        const float GlassInsertMm = 6f;
        /// <summary>
        /// Boards of a joint stand this far apart (mm), with a dark seam at the bottom of the gap: the hairline the catalogue
        /// renders show comes from occlusion in that crevice, which real-time lighting does not produce by itself.
        /// </summary>
        public const float JointGapMm = 0.8f;

        public readonly DoorDesign Design;
        /// <summary>Leaf size, mm.</summary>
        public readonly float Wmm, Hmm, Tmm;
        readonly ResizeMap _mx, _my;
        readonly DoorMaterialSet _mats;
        MeshBuilder _solid, _glass;
        int _pieces;

        public float Width => Wmm / 1000f;
        public float Height => Hmm / 1000f;
        public float Thickness => Tmm / 1000f;

        public LeafBuilder(DoorDesign design, float widthM, float heightM, DoorMaterialSet mats)
        {
            Design = design;
            Wmm = widthM * 1000f;
            Hmm = heightM * 1000f;
            // entrance doors' steel skins and inner panels are thin (2–12 mm); the block places them by this thickness
            Tmm = Mathf.Clamp(design.Thickness, 2f, 120f);
            _mats = mats;
            _mx = new ResizeMap(design.RefW, Wmm, design.FixX);
            _my = new ResizeMap(design.RefH, Hmm, design.FixY);
        }

        /// <summary>Handle axis in leaf space (m): its distance from the lock edge and height stay as drawn (a handle is at hand height on any leaf).</summary>
        public Vector2 Handle
        {
            get
            {
                var h = Design.Handle ?? new HandleSpec();
                return new Vector2(Mathf.Clamp(h.X, 30f, Wmm * 0.4f), Mathf.Clamp(h.Y, 300f, Hmm - 300f)) / 1000f;
            }
        }

        /// <summary>Hinge centres above the leaf bottom (m): the lower ones keep their distance from the bottom, the upper ones from the top.</summary>
        public List<float> Hinges
        {
            get
            {
                var list = new List<float>();
                var src = Design.Hinges != null && Design.Hinges.Length > 0 ? Design.Hinges : new[] { 250f, Design.RefH - 250f };
                foreach (float y in src)
                    list.Add((y <= Design.RefH * 0.5f ? y : Hmm - (Design.RefH - y)) / 1000f);
                return list;
            }
        }

        public void Build(MeshBuilder solid, MeshBuilder glass)
        {
            _solid = solid;
            _glass = glass;
            _pieces = 0;
            _boards.Clear();
            var root = Design.Layout ?? new LayoutNode();
            Walk(root, new Rect(0f, 0f, Design.RefW, Design.RefH), new Rect(0f, 0f, Wmm, Hmm), Vector4.zero,
                new Props { Level = 0f, GrainV = true, Material = "finish" });
            // features over the boards (they need the boards' levels), then the boards with the features cut into their faces
            var features = Features();
            foreach (var b in _boards)
                DoorGeo.Slab(_solid, M(b.R), b.H, b.Rad, b.Mat, b.GrainV, b.Off, 3, CutsOn(features, 1), CutsOn(features, -1));
            foreach (var f in features) BuildFeature(f);
            Edge();
        }

        /// <summary>A board of the layout, emitted after the features are known (they cut into its faces).</summary>
        struct Board
        {
            public Rect R;          // mm
            public float H;         // half thickness, m
            public float Rad;       // edge radius, m
            public Material Mat;
            public bool GrainV;
            public Vector2 Off;
        }

        readonly List<Board> _boards = new List<Board>();

        // ------------------------------------------------------------------ layout
        struct Props
        {
            public float Level;
            public float? Radius;
            public bool GrainV;
            public string Material;
            public float? Pane;
        }

        struct Sep
        {
            public string Kind;     // joint, none, pane, metal, groove
            public float W, D;      // width; groove depth / metal proud, mm
            public string Role;     // glass role of a pane
        }

        /// <summary>
        /// One node: <paramref name="r"/> is its layout rectangle (between the centres of the cuts around it, target mm), the
        /// cut positions map from it exactly as in the reference (tools/doors/preview2d.py); <paramref name="ins"/> (left, right,
        /// bottom, top) is what the separators on its sides take off the material of its boards.
        /// </summary>
        void Walk(LayoutNode n, Rect refR, Rect r, Vector4 ins, Props p)
        {
            if (n != null)
            {
                if (n.Level.HasValue) p.Level = n.Level.Value;
                if (n.Radius.HasValue) p.Radius = n.Radius.Value;
                if (!string.IsNullOrEmpty(n.Grain)) p.GrainV = !n.Grain.StartsWith("h", StringComparison.OrdinalIgnoreCase);
                if (!string.IsNullOrEmpty(n.Material)) p.Material = n.Material;
                if (n.Pane.HasValue) p.Pane = n.Pane.Value;
            }
            var inner = Rect.MinMaxRect(r.xMin + ins.x, r.yMin + ins.z, r.xMax - ins.y, r.yMax - ins.w);
            string glassRole = GlassRoleOf(n?.Glass);
            if (glassRole != null) { GlassCell(inner, glassRole, p.Pane); return; }
            if (n == null || string.IsNullOrEmpty(n.Split) || n.At == null || n.At.Length == 0) { Piece(inner, p); return; }

            bool alongX = n.Split.StartsWith("x", StringComparison.OrdinalIgnoreCase);
            var map = alongX ? _mx : _my;
            int nc = n.At.Length;
            // positions of the cell bounds: the node's own bounds and the cuts, in ref and in target mm
            var pr = new float[nc + 2];
            var pt = new float[nc + 2];
            float loR = alongX ? refR.xMin : refR.yMin, hiR = alongX ? refR.xMax : refR.yMax;
            float loN = alongX ? r.xMin : r.yMin, hiN = alongX ? r.xMax : r.yMax;
            // the map, fitted onto the node's actual extent when the thin rule above moved or kept it
            float ma = map.Map(loR), mb = map.Map(hiR);
            bool exact = Mathf.Abs(ma - loN) < 1e-3f && Mathf.Abs(mb - hiN) < 1e-3f || Mathf.Abs(mb - ma) < 1e-4f;
            float F(float v) => exact ? map.Map(v) : loN + (map.Map(v) - ma) * (hiN - loN) / (mb - ma);
            pr[0] = loR; pr[nc + 1] = hiR; pt[0] = loN; pt[nc + 1] = hiN;
            for (int i = 0; i < nc; i++) { pr[i + 1] = n.At[i]; pt[i + 1] = F(n.At[i]); }
            // thin cells keep their size: a run of consecutive thin cells keeps its total size, centred on the mapped
            // centre of the run, or anchored to the node's start / end when it touches them (Docs/door-designs.md)
            for (int i = 0; i <= nc;)
            {
                if (pr[i + 1] - pr[i] >= ThinMm) { i++; continue; }
                int j = i;
                while (j < nc && pr[j + 2] - pr[j + 1] < ThinMm) j++;
                if (!(i == 0 && j == nc))
                {
                    float size = pr[j + 1] - pr[i];
                    float start = i == 0 ? pt[0] : j == nc ? pt[nc + 1] - size : F((pr[i] + pr[j + 1]) * 0.5f) - size * 0.5f;
                    for (int k = Mathf.Max(1, i); k <= Mathf.Min(nc, j + 1); k++) pt[k] = start + (pr[k] - pr[i]);
                }
                i = j + 1;
            }
            var seps = new Sep[nc + 2];
            for (int i = 1; i <= nc; i++) seps[i] = ParseSep(SepString(n.Sep, i - 1));

            float o0 = alongX ? inner.yMin : inner.xMin, o1 = alongX ? inner.yMax : inner.xMax;
            for (int i = 0; i <= nc; i++)
            {
                if (pt[i + 1] - pt[i] < 0.5f) continue;
                var child = n.Cells != null && i < n.Cells.Count ? n.Cells[i] : null;
                var cr = alongX ? Rect.MinMaxRect(pt[i], r.yMin, pt[i + 1], r.yMax) : Rect.MinMaxRect(r.xMin, pt[i], r.xMax, pt[i + 1]);
                var crRef = alongX ? Rect.MinMaxRect(pr[i], refR.yMin, pr[i + 1], refR.yMax) : Rect.MinMaxRect(refR.xMin, pr[i], refR.xMax, pr[i + 1]);
                // the cell's material stops at half the separators on its sides; the node's own insets pass to the end cells
                float before = i == 0 ? (alongX ? ins.x : ins.z) : seps[i].W * 0.5f;
                float after = i == nc ? (alongX ? ins.y : ins.w) : seps[i + 1].W * 0.5f;
                var ci = alongX ? new Vector4(before, after, ins.z, ins.w) : new Vector4(ins.x, ins.y, before, after);
                Walk(child, crRef, cr, ci, p);
            }
            for (int i = 1; i <= nc; i++)
            {
                // the lower of the two boards meeting at a cut: a seam must sit below both faces
                var before = n.Cells != null && i - 1 < n.Cells.Count ? n.Cells[i - 1] : null;
                var after = n.Cells != null && i < n.Cells.Count ? n.Cells[i] : null;
                float low = Mathf.Min(LevelOf(before, p.Level), LevelOf(after, p.Level));
                Separator(seps[i], pt[i], alongX, o0, o1, p, low);
            }
        }

        static string SepString(JToken sep, int i)
        {
            if (sep == null || sep.Type == JTokenType.Null) return "joint";
            if (sep is JArray arr) return arr.Count == 0 ? "joint" : (string)arr[Mathf.Min(i, arr.Count - 1)];
            return (string)sep;
        }

        static Sep ParseSep(string s)
        {
            var parts = (s ?? "joint").Split(':');
            var sep = new Sep { Kind = parts[0].Trim().ToLowerInvariant() };
            if (parts.Length > 1) float.TryParse(parts[1], NumberStyles.Float, CultureInfo.InvariantCulture, out sep.W);
            if (parts.Length > 2) float.TryParse(parts[2], NumberStyles.Float, CultureInfo.InvariantCulture, out sep.D);
            switch (sep.Kind)
            {
                case "glass": case "satin": case "clear": case "mirror": case "black":
                    sep.Role = sep.Kind;
                    sep.Kind = "pane";
                    if (sep.W <= 0f) sep.W = 10f;
                    break;
                case "metal":
                    if (sep.W <= 0f) sep.W = 4f;
                    break;
                case "groove":
                    if (sep.W <= 0f) sep.W = 6f;
                    if (sep.D <= 0f) sep.D = 3f;
                    break;
                case "none":
                    sep.W = 0f;
                    break;
                default:
                    sep.Kind = "joint";
                    sep.W = JointGapMm;
                    break;
            }
            return sep;
        }

        static float LevelOf(LayoutNode n, float inherited) => n?.Level ?? inherited;

        static string GlassRoleOf(JToken g)
        {
            if (g == null || g.Type == JTokenType.Null) return null;
            if (g.Type == JTokenType.Boolean) return (bool)g ? "glass" : null;
            var s = (string)g;
            return string.IsNullOrEmpty(s) ? null : s;
        }

        // ------------------------------------------------------------------ emitters (mm in, metres out)
        static Rect M(Rect mm) => Rect.MinMaxRect(mm.xMin / 1000f, mm.yMin / 1000f, mm.xMax / 1000f, mm.yMax / 1000f);

        float HalfAt(float level) => Mathf.Max(0.5f, Tmm * 0.5f + level) / 1000f;

        bool OnPerimeter(Rect r) => r.xMin < 0.5f || r.yMin < 0.5f || r.xMax > Wmm - 0.5f || r.yMax > Hmm - 0.5f;

        void Piece(Rect r, Props p)
        {
            if (r.width < 0.5f || r.height < 0.5f) return;
            float rad = p.Radius ?? JointRadiusMm;
            if (OnPerimeter(r)) rad = Mathf.Max(rad, Design.Edge?.Radius ?? 2f);
            var mat = _mats.Role(p.Material);
            // each board shows its own part of the film
            int k = _pieces++;
            var off = new Vector2(Hash01(k, 1) * 2f, Hash01(k, 2));
            _boards.Add(new Board { R = r, H = HalfAt(p.Level), Rad = rad / 1000f, Mat = mat, GrainV = p.GrainV, Off = off });
        }

        void GlassCell(Rect r, string role, float? paneMm = null)
        {
            var pane = Rect.MinMaxRect(r.xMin - GlassInsertMm, r.yMin - GlassInsertMm, r.xMax + GlassInsertMm, r.yMax + GlassInsertMm);
            EmitPane(pane, role, r, paneMm);
        }

        /// <summary>A pane over <paramref name="mm"/> (it runs into the boards around it); a picture fits the visible part <paramref name="visible"/>.</summary>
        void EmitPane(Rect mm, string role, Rect visible, float? paneMm = null)
        {
            // never out of the leaf
            mm = Rect.MinMaxRect(Mathf.Max(mm.xMin, 1f), Mathf.Max(mm.yMin, 1f), Mathf.Min(mm.xMax, Wmm - 1f), Mathf.Min(mm.yMax, Hmm - 1f));
            var mat = (role == "glass" ? _mats.Glass : _mats.GlassRole(role)) ?? _mats.Glass;
            float t = Mathf.Clamp(paneMm ?? (role == "glass" ? _mats.GlassMm : 4f), 2f, Tmm - 0.2f);
            Rect? fit = _mats.Fits(role) ? M(visible) : (Rect?)null;
            DoorGeo.Pane(Translucent(mat) ? _glass : _solid, M(mm), t * 0.5f / 1000f, mat, fit);
        }

        /// <summary>See-through glass renders without solid shadows; lacobel, mirror and black glass are opaque (they cast them).</summary>
        bool Translucent(Material m) => m != null && (m == _mats.Satin || m == _mats.Clear || m.renderQueue >= 2500);

        void Separator(Sep s, float c, bool alongX, float o0, float o1, Props p, float lowLevel)
        {
            switch (s.Kind)
            {
                case "joint":
                {
                    // the dark seam at the bottom of the crevice, just under the boards' rounded edges
                    float a = c - s.W * 0.5f - 0.05f, b = c + s.W * 0.5f + 0.05f;
                    var r = M(alongX ? Rect.MinMaxRect(a, o0, b, o1) : Rect.MinMaxRect(o0, a, o1, b));
                    float h = HalfAt(lowLevel) - (p.Radius ?? JointRadiusMm) / 1000f - 0.0003f;
                    if (h > 0.001f) _solid.Box(new Vector3(r.xMin, r.yMin, -h), new Vector3(r.xMax, r.yMax, h), _mats.Seal);
                    break;
                }
                case "pane":
                {
                    float a = c - s.W * 0.5f - GlassInsertMm, b = c + s.W * 0.5f + GlassInsertMm;
                    float oa = o0 - GlassInsertMm, ob = o1 + GlassInsertMm;
                    var vis = alongX ? Rect.MinMaxRect(c - s.W * 0.5f, o0, c + s.W * 0.5f, o1) : Rect.MinMaxRect(o0, c - s.W * 0.5f, o1, c + s.W * 0.5f);
                    EmitPane(alongX ? Rect.MinMaxRect(a, oa, b, ob) : Rect.MinMaxRect(oa, a, ob, b), s.Role, vis, p.Pane);
                    break;
                }
                case "metal":
                {
                    float a = c - s.W * 0.5f, b = c + s.W * 0.5f;
                    var r = alongX ? Rect.MinMaxRect(a, o0, b, o1) : Rect.MinMaxRect(o0, a, o1, b);
                    float h = HalfAt(p.Level + s.D);
                    var mr = M(r);
                    _solid.Box(new Vector3(mr.xMin, mr.yMin, -h), new Vector3(mr.xMax, mr.yMax, h), _mats.Metal);
                    break;
                }
                case "groove":
                {
                    float a = c - s.W * 0.5f, b = c + s.W * 0.5f;
                    var r = alongX ? Rect.MinMaxRect(a, o0, b, o1) : Rect.MinMaxRect(o0, a, o1, b);
                    DoorGeo.Slab(_solid, M(r), HalfAt(p.Level - s.D), 0f, _mats.Role(p.Material), p.GrainV, Vector2.zero, 0);
                    break;
                }
            }
        }

        /// <summary>ALU models: aluminium strips over the vertical edges of the leaf.</summary>
        void Edge()
        {
            if (!string.Equals(Design.Edge?.Material, "metal", StringComparison.OrdinalIgnoreCase)) return;
            float h = Tmm * 0.5f / 1000f + 0.0003f, H = Height, W = Width;
            _solid.Box(new Vector3(-0.0012f, 0f, -h), new Vector3(0.0004f, H, h), _mats.Metal);
            _solid.Box(new Vector3(W - 0.0004f, 0f, -h), new Vector3(W + 0.0012f, H, h), _mats.Metal);
        }

        static float Hash01(int a, int b)
        {
            unchecked
            {
                uint h = (uint)(a * 73856093) ^ (uint)(b * 19349663) ^ 0x9e3779b9u;
                h ^= h >> 13; h *= 0x5bd1e995; h ^= h >> 15;
                return (h & 0xffffff) / (float)0x1000000;
            }
        }
    }
}
