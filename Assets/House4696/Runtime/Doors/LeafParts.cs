using System;
using System.Collections.Generic;
using Clipper2Lib;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>
    /// Features of a design over its layout (Docs/door-designs.md, "Parts"): grooves and inlays milled into the faces,
    /// shaped glass through the leaf (with beads), raised / recessed panels, applied mouldings and free boards. A feature
    /// sits on the face of the board under its centre; subtractive ones cut that face.
    /// </summary>
    public sealed partial class LeafBuilder
    {
        sealed class Feature
        {
            public string Type;
            public JObject Spec;
            public List<Poly> Shape;
            /// <summary>1 = front, 2 = back, 3 = both.</summary>
            public int Faces;
            /// <summary>Half thickness of the board the feature sits on, mm.</summary>
            public float BaseH;
            /// <summary>What the feature removes from the faces it is on (null: additive).</summary>
            public PathsD Cut;
            public bool GrainV;
            public Vector2 Off;
        }

        static readonly Dictionary<string, Vector2[]> Profiles = new Dictionary<string, Vector2[]>(StringComparer.OrdinalIgnoreCase)
        {
            // mouldings: across the path from -u to +u along the visible surface (mm)
            ["flat-10"] = V(-5, 0, -5, 3, 5, 3, 5, 0),
            ["bead-8"] = V(-4, 0, -4, 1.5f, -3, 3.2f, -1.2f, 4, 1.2f, 4, 3, 3.2f, 4, 1.5f, 4, 0),
            ["baget-20"] = V(-10, 0, -10, 3, -8.5f, 5.5f, -5.5f, 7, -2, 6.8f, 1, 5.2f, 3.5f, 5.8f, 6.5f, 5.6f, 9, 3.5f, 10, 1.5f, 10, 0),
            ["baget-30"] = V(-15, 0, -15, 4, -13, 7.5f, -9, 10, -4, 10, 0, 8, 3, 7, 7, 8.5f, 11, 7.5f, 14, 4.5f, 15, 2, 15, 0),
            ["cornice"] = V(-20, 0, -20, 6, -16, 12, -10, 14, -4, 14, 2, 12, 8, 13, 14, 12, 19, 7, 20, 3, 20, 0),
        };

        static Vector2[] V(params float[] a)
        {
            var r = new Vector2[a.Length / 2];
            for (int i = 0; i < r.Length; i++) r[i] = new Vector2(a[2 * i], a[2 * i + 1]);
            return r;
        }

        List<Feature> Features()
        {
            var list = new List<Feature>();
            if (Design.Parts == null) return list;
            foreach (var spec in Design.Parts)
            {
                if (spec == null) continue;
                string type = ((string)spec["type"] ?? "").ToLowerInvariant();
                var shapeToken = spec["shape"] ?? (spec["path"] != null ? new JObject { ["path"] = spec["path"] } : null);
                var shape = Shape2D.Parse(shapeToken);
                if (shape.Count == 0) { Debug.LogWarning($"[Doors] {Design.Id}: part '{type}' has no shape"); continue; }
                Shape2D.Map(shape, _mx, _my);
                string face = ((string)spec["face"] ?? "both").ToLowerInvariant();
                var f = new Feature
                {
                    Type = type, Spec = spec, Shape = shape,
                    Faces = face.StartsWith("front") ? 1 : face.StartsWith("back") ? 2 : 3,
                };
                var board = BoardAt(Center(shape));
                f.BaseH = board.HasValue ? board.Value.H * 1000f : Tmm * 0.5f;
                f.GrainV = board?.GrainV ?? true;
                f.Off = board?.Off ?? Vector2.zero;
                switch (type)
                {
                    case "groove":
                    case "inlay":
                    {
                        float w = (float?)spec["width"] ?? (type == "inlay" ? 4f : 6f);
                        var cut = new PathsD();
                        foreach (var p in shape) cut.AddRange(Relief.Band(p.P, p.Closed, -w * 0.5f, w * 0.5f));
                        f.Cut = Relief.Union(cut);
                        break;
                    }
                    case "glass":
                        f.Faces = 3;   // through the leaf
                        f.Cut = Relief.Union(Rings(shape));
                        break;
                    case "panel":
                        f.Cut = Relief.Union(Rings(shape));
                        break;
                    case "molding":
                    case "moulding":
                    case "piece":
                    case "decal":
                        break;
                    default:
                        Debug.LogWarning($"[Doors] {Design.Id}: unknown part type '{type}'");
                        continue;
                }
                list.Add(f);
            }
            return list;
        }

        static PathsD Rings(List<Poly> shape)
        {
            var paths = new PathsD();
            foreach (var p in shape) if (p.Closed && p.P.Count >= 3) paths.Add(Relief.Path(p.P));
            return paths;
        }

        static Vector2 Center(List<Poly> shape)
        {
            Vector2 mn = new Vector2(float.MaxValue, float.MaxValue), mx = new Vector2(float.MinValue, float.MinValue);
            foreach (var p in shape) foreach (var v in p.P) { mn = Vector2.Min(mn, v); mx = Vector2.Max(mx, v); }
            return (mn + mx) * 0.5f;
        }

        Board? BoardAt(Vector2 mm)
        {
            foreach (var b in _boards) if (b.R.Contains(mm)) return b;
            return null;
        }

        static PathsD CutsOn(List<Feature> features, int face)
        {
            PathsD all = null;
            foreach (var f in features)
            {
                if (f.Cut == null || (f.Faces & (face > 0 ? 1 : 2)) == 0) continue;
                all ??= new PathsD();
                all.AddRange(f.Cut);
            }
            return all == null ? null : Relief.Union(all);
        }

        void BuildFeature(Feature f)
        {
            var mat = _mats.Role((string)f.Spec["material"] ?? "finish");
            foreach (float face in new[] { 1f, -1f })
            {
                if ((f.Faces & (face > 0 ? 1 : 2)) == 0) continue;
                switch (f.Type)
                {
                    case "groove": Groove(f, face, mat); break;
                    case "inlay": Inlay(f, face); break;
                    case "glass": GlassEdges(f, face, mat); break;
                    case "panel": Panel(f, face, mat); break;
                    case "molding": case "moulding": Moulding(f, face, mat); break;
                    case "piece": FreeBoard(f, face, mat); break;
                    case "decal": Decal(f, face); break;
                }
            }
            if (f.Type == "glass")
            {
                GlassPane(f);
                GlassBars(f);
            }
        }

        Vector2 FaceUv(Vector2 mm, Feature f) => (f.GrainV ? new Vector2(mm.y, mm.x) : new Vector2(mm.x, mm.y)) / 1000f + f.Off;

        // ------------------------------------------------------------------ grooves and inlays
        void Groove(Feature f, float face, Material mat)
        {
            float w = (float?)f.Spec["width"] ?? 6f, d = Mathf.Min((float?)f.Spec["depth"] ?? 3f, f.BaseH - 1f);
            string prof = ((string)f.Spec["profile"] ?? "v").ToLowerInvariant();
            Vector2[] profile;
            if (prof.StartsWith("u"))
            {
                const int n = 8;
                profile = new Vector2[n + 1];
                for (int i = 0; i <= n; i++)
                {
                    float a = Mathf.PI + Mathf.PI * i / n;   // from the left edge down and up to the right edge
                    profile[i] = new Vector2(w * 0.5f * Mathf.Cos(a), d * Mathf.Sin(a));
                }
            }
            else if (prof.StartsWith("flat")) profile = V(-w * 0.5f, 0, -w * 0.5f, -d, w * 0.5f, -d, w * 0.5f, 0);
            else profile = V(-w * 0.5f, 0, 0, -d, w * 0.5f, 0);
            foreach (var p in f.Shape) Relief.Sweep(_solid, p.P, p.Closed, profile, f.BaseH, face, mat, 0f, capSign: -1);
        }

        void Inlay(Feature f, float face)
        {
            float w = (float?)f.Spec["width"] ?? 4f, proud = (float?)f.Spec["proud"] ?? 0f;
            var mat = _mats.Role((string)f.Spec["material"] ?? "metal");
            var profile = proud > 0.05f ? V(-w * 0.5f, 0, -w * 0.5f, proud, w * 0.5f, proud, w * 0.5f, 0) : V(-w * 0.5f, 0, w * 0.5f, 0);
            foreach (var p in f.Shape) Relief.Sweep(_solid, p.P, p.Closed, profile, f.BaseH, face, mat, 0f, capSign: proud > 0.05f ? 1 : 0);
        }

        // ------------------------------------------------------------------ shaped glass
        static readonly Dictionary<string, Vector2[]> Beads = new Dictionary<string, Vector2[]>(StringComparer.OrdinalIgnoreCase)
        {
            // from the hole's edge inwards (u) — the last point drops to the glass surface (v replaced)
            ["flat"] = V(0, 0, 0, 1.5f, 9, 1.5f, 10, 0),
            ["round"] = V(0, 0, 0, 1, 1.5f, 3.2f, 4, 4.2f, 7, 3.4f, 9, 1.8f, 10, 0),
            ["classic"] = V(0, 0, 0, 2, 1.5f, 4, 3, 4.5f, 5, 3.5f, 6.5f, 4.5f, 9, 5, 11.5f, 2.5f, 13, 0),
        };

        void GlassEdges(Feature f, float face, Material mat)
        {
            float glassHalf = GlassHalfMm(f);
            // the hole's wall down to the middle of the leaf
            var wall = V(0, 0, 0, -f.BaseH);
            foreach (var p in f.Shape)
            {
                if (!p.Closed) continue;
                Relief.Sweep(_solid, p.P, true, wall, f.BaseH, face, mat);
                string bead = (string)f.Spec["bead"];
                if (string.IsNullOrEmpty(bead) || bead == "none" || !Beads.TryGetValue(bead, out var prof)) continue;
                var bp = (Vector2[])prof.Clone();
                bp[bp.Length - 1] = new Vector2(bp[bp.Length - 1].x, -(f.BaseH - glassHalf));
                Relief.Sweep(_solid, p.P, true, bp, f.BaseH, face, mat);
            }
        }

        float GlassHalfMm(Feature f)
        {
            string role = (string)f.Spec["role"] ?? "glass";
            float t = (float?)f.Spec["pane"] ?? (role == "glass" ? _mats.GlassMm : 4f);
            return Mathf.Clamp(t, 2f, Tmm - 0.2f) * 0.5f;
        }

        void GlassPane(Feature f)
        {
            string role = (string)f.Spec["role"] ?? "glass";
            var mat = (role == "glass" ? _mats.Glass : _mats.GlassRole(role)) ?? _mats.Glass;
            var hole = Relief.Union(Rings(f.Shape));
            var pane = Relief.Inflate(hole, GlassInsertMm);
            float half = GlassHalfMm(f);
            // a picture (art glass) spans the hole's bounds; a pattern tiles in metres
            System.Func<Vector2, Vector2> uv = mm => mm / 1000f;
            if (_mats.Fits(role))
            {
                var bounds = Clipper2Lib.Clipper.GetBounds(hole);
                float w = (float)Mathf.Max(1f, (float)(bounds.right - bounds.left)), h = (float)Mathf.Max(1f, (float)(bounds.bottom - bounds.top));
                uv = mm => new Vector2((mm.x - (float)bounds.left) / w, (mm.y - (float)bounds.top) / h);
            }
            float facet = (float?)f.Spec["facet"] ?? (role == "glass" || role == "true" ? _mats.GlassFacetMm : 0f);
            if (facet < 0.5f)
            {
                foreach (float face in new[] { 1f, -1f })
                    Relief.Fill(Translucent(mat) ? _glass : _solid, pane, half, face, mat, uv);
                return;
            }
            // a bevelled (faceted) border of clear glass round the pane's middle, "facet" mm wide where it shows (inside the
            // bead): the border slopes from the hole's edge, thinner, up to the middle's surface
            var fm = _mats.GlassRole((string)f.Spec["facetRole"] ?? "clear") ?? mat;
            string beadId = (string)f.Spec["bead"];
            float beadW = !string.IsNullOrEmpty(beadId) && Beads.TryGetValue(beadId, out var bp) ? bp[bp.Length - 1].x : 0f;
            float band = beadW + facet, drop = Mathf.Min(half * 0.6f, 1.5f);
            var middle = Relief.Inflate(hole, -band);
            var hidden = Relief.Difference(pane, hole);
            var bevel = V(0f, -drop, band, 0f);
            foreach (float face in new[] { 1f, -1f })
            {
                Relief.Fill(Translucent(mat) ? _glass : _solid, middle, half, face, mat, uv);
                Relief.Fill(Translucent(fm) ? _glass : _solid, hidden, half - drop, face, fm, mm => mm / 1000f);
                foreach (var p in f.Shape)
                    if (p.Closed) Relief.Sweep(Translucent(fm) ? _glass : _solid, p.P, true, bevel, half, face, fm);
            }
        }

        // ------------------------------------------------------------------ glazing bars
        /// <summary>
        /// Glazing bars across a glass part (<c>"bars": {"x": [...], "y": [...], "width": 20, "level": -2}</c>): boards
        /// through the glass at the given ref positions (their centres move with the leaf, their width stays), clipped to
        /// the glass shape, their faces <c>level</c> mm below the leaf face.
        /// </summary>
        void GlassBars(Feature f)
        {
            if (!(f.Spec["bars"] is JObject bars)) return;
            float w = (float?)bars["width"] ?? 20f, level = (float?)bars["level"] ?? -2f;
            var hole = Relief.Union(Rings(f.Shape));
            if (hole.Count == 0) return;
            var b = Clipper.GetBounds(hole);
            var mat = _mats.Role((string)bars["material"] ?? "finish");
            void Bar(Rect r, bool vertical)
            {
                var shape = new List<Poly>();
                foreach (var path in Relief.Intersect(Relief.Rect(r), hole))
                {
                    var poly = new Poly { P = Relief.Points(path), Closed = true };
                    if (poly.P.Count < 3) continue;
                    Shape2D.Orient(poly);   // counter-clockwise: +u is inside the bar
                    shape.Add(poly);
                }
                if (shape.Count == 0) return;
                var spec = new JObject { ["level"] = level, ["grain"] = vertical ? "v" : "h", ["radius"] = (float?)bars["radius"] ?? 1.5f };
                var bar = new Feature { Type = "piece", Spec = spec, Shape = shape, Faces = 3, BaseH = f.BaseH };
                foreach (float face in new[] { 1f, -1f }) FreeBoard(bar, face, mat);
            }
            float x0 = (float)b.left - 1f, x1 = (float)b.right + 1f, y0 = (float)b.top - 1f, y1 = (float)b.bottom + 1f;
            if (bars["x"] is JArray xs)
                foreach (var t in xs) { float x = _mx.Map((float)t); Bar(Rect.MinMaxRect(x - w * 0.5f, y0, x + w * 0.5f, y1), true); }
            if (bars["y"] is JArray ys)
                foreach (var t in ys) { float y = _my.Map((float)t); Bar(Rect.MinMaxRect(x0, y - w * 0.5f, x1, y + w * 0.5f), false); }
        }

        // ------------------------------------------------------------------ panels
        void Panel(Feature f, float face, Material mat)
        {
            Vector2[] profile;
            if (f.Spec["profile"] is JArray arr && arr.Count >= 2)
            {
                profile = new Vector2[arr.Count];
                for (int i = 0; i < arr.Count; i++) profile[i] = new Vector2((float)arr[i][0], (float)arr[i][1]);
            }
            else
            {
                string kind = ((string)f.Spec["profile"] ?? "raised").ToLowerInvariant();
                float w = (float?)f.Spec["width"] ?? (kind == "raised" ? 30f : 12f);
                float d = Mathf.Min((float?)f.Spec["depth"] ?? 6f, f.BaseH - 2f);
                profile = kind == "recessed"
                    ? V(0, 0, w, -d)
                    : V(0, 0, 0, -d, 4, -d, w, -Mathf.Min(2f, d * 0.4f));
            }
            var seg = Patina(f, ref profile);
            var last = profile[profile.Length - 1];
            foreach (var p in f.Shape)
            {
                if (!p.Closed) continue;
                Relief.Sweep(_solid, p.P, true, profile, f.BaseH, face, mat, segment: seg);
                // the field: the ring moved in by the profile's width, at its last height
                var field = Relief.Offset(p.P, last.x, true);
                var region = Relief.Union(new PathsD { Relief.Path(field) });
                Relief.Fill(_solid, region, f.BaseH + last.y, face, mat, mm => FaceUv(mm, f));
            }
        }

        // ------------------------------------------------------------------ applied mouldings and free boards
        void Moulding(Feature f, float face, Material mat)
        {
            Vector2[] profile = null;
            if (f.Spec["profile"] is JArray arr && arr.Count >= 2)
            {
                profile = new Vector2[arr.Count];
                for (int i = 0; i < arr.Count; i++) profile[i] = new Vector2((float)arr[i][0], (float)arr[i][1]);
            }
            else if (!Profiles.TryGetValue((string)f.Spec["profile"] ?? "baget-20", out profile)) profile = Profiles["baget-20"];
            var seg = Patina(f, ref profile);
            float uOff = Hash01(f.Shape.Count, (int)f.BaseH) * 2f;
            foreach (var p in f.Shape) Relief.Sweep(_solid, p.P, p.Closed, profile, f.BaseH, face, mat, uOff, capSign: 1, segment: seg);
        }

        /// <summary>
        /// Patina of a moulding or a panel profile: <c>"patina": "gold"</c> paints a 3 mm line along the profile's crest,
        /// <c>"patina": { "material": "gold", "from": u0, "to": u1 }</c> the part of the profile between u0 and u1 (mm across
        /// the path). The profile gets points at u0 and u1 so the line has crisp edges; returns the material per profile segment.
        /// </summary>
        Func<int, Material> Patina(Feature f, ref Vector2[] profile)
        {
            var spec = f.Spec["patina"];
            if (spec == null || spec.Type == JTokenType.Null) return null;
            string role = spec.Type == JTokenType.String ? (string)spec : (string)spec["material"] ?? "gold";
            var pm = _mats.Role(role);
            if (pm == null) return null;
            float u0, u1;
            if (spec is JObject o && o["from"] != null && o["to"] != null) { u0 = (float)o["from"]; u1 = (float)o["to"]; }
            else
            {
                int top = 0;
                for (int i = 1; i < profile.Length; i++) if (profile[i].y > profile[top].y + 1e-4f) top = i;
                float w = spec is JObject oo ? (float?)oo["width"] ?? 3f : 3f;
                u0 = profile[top].x - w * 0.5f; u1 = profile[top].x + w * 0.5f;
            }
            if (u1 < u0) (u0, u1) = (u1, u0);
            // split the profile where it crosses u0 and u1
            var pts = new List<Vector2> { profile[0] };
            for (int i = 1; i < profile.Length; i++)
            {
                Vector2 a = profile[i - 1], b = profile[i];
                foreach (float u in a.x <= b.x ? new[] { u0, u1 } : new[] { u1, u0 })
                    if ((a.x - u) * (b.x - u) < 0f)
                        pts.Add(Vector2.Lerp(a, b, (u - a.x) / (b.x - a.x)));
                pts.Add(b);
            }
            profile = pts.ToArray();
            var prof = profile;
            const float eps = 0.01f;
            return j =>
            {
                float mid = (prof[j].x + prof[j + 1].x) * 0.5f;
                return mid >= u0 - eps && mid <= u1 + eps ? pm : null;
            };
        }

        void FreeBoard(Feature f, float face, Material mat)
        {
            float level = (float?)f.Spec["level"] ?? 0f;
            float h = Mathf.Max(1f, Tmm * 0.5f + level), r = Mathf.Min((float?)f.Spec["radius"] ?? JointRadiusMm, h * 0.9f);
            bool grainV = !(((string)f.Spec["grain"]) ?? "v").StartsWith("h", StringComparison.OrdinalIgnoreCase);
            // every board shows its own part of the film: the offset follows its position (and level)
            var c = Center(f.Shape);
            int kx = Mathf.RoundToInt(c.x), ky = Mathf.RoundToInt(c.y), kh = Mathf.RoundToInt(h * 10f);
            var fb = new Feature { GrainV = grainV, Off = new Vector2(Hash01(7 + kx, kh + 31 * ky) * 2f, Hash01(9 + ky, kh + 17 * kx)) };
            // rounding from the face (inset r) down the edge to the middle plane
            var edge = new Vector2[5];
            for (int i = 0; i < 4; i++)
            {
                float a = Mathf.PI * 0.5f * i / 3f;
                edge[i] = new Vector2(r * (1f - Mathf.Sin(a)), -r * (1f - Mathf.Cos(a)));
            }
            edge[4] = new Vector2(0f, -h);
            // listed up the wall and over the rounding to the face: along a counter-clockwise ring (+u = inside) the
            // tangent turned +90° then points out of the board
            Array.Reverse(edge);
            foreach (var p in f.Shape)
            {
                if (!p.Closed) continue;
                Relief.Sweep(_solid, p.P, true, edge, h, face, mat);
                var top = Relief.Offset(p.P, r, true);
                Relief.Fill(_solid, Relief.Union(new PathsD { Relief.Path(top) }), h, face, mat, mm => FaceUv(mm, fb));
            }
        }


        // ------------------------------------------------------------------ decals (painted ornament, patina, prints)
        /// <summary>
        /// A picture laid on a face: <c>"image"</c> is a library material (transparent where the picture is empty) stretched
        /// over the shape's bounds; <c>"level"</c> (mm, relative to the board's face under it) lifts it onto a panel field.
        /// </summary>
        void Decal(Feature f, float face)
        {
            string id = (string)f.Spec["image"];
            var mat = string.IsNullOrEmpty(id) ? null : _mats.Library?.Invoke(id);
            if (mat == null) { Debug.LogWarning($"[Doors] {Design.Id}: decal image '{id}' is not in the library"); return; }
            float z = f.BaseH + ((float?)f.Spec["level"] ?? 0f) + 0.15f;
            var region = Relief.Union(Rings(f.Shape));
            if (region.Count == 0) return;
            var bounds = Clipper2Lib.Clipper.GetBounds(region);
            float w = Mathf.Max(1f, (float)(bounds.right - bounds.left)), h = Mathf.Max(1f, (float)(bounds.bottom - bounds.top));
            // mirrored on the back face so the picture reads the same way from both sides
            Relief.Fill(Translucent(mat) ? _glass : _solid, region, z, face, mat,
                mm => new Vector2(face > 0 ? (mm.x - (float)bounds.left) / w : 1f - (mm.x - (float)bounds.left) / w, (mm.y - (float)bounds.top) / h));
        }
    }
}
