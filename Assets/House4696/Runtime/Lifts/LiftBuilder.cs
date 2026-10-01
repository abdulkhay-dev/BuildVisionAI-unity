using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Lifts
{
    /// <summary>
    /// Builds a lift from its <see cref="LiftGeometry"/>: the shaft (concrete walls plastered on the hall side, glass for
    /// panoramic lifts, or nothing when the author walls it), pit floor and head slab, the machine room of an MR drive,
    /// at every stop a landing door with its stainless portal, sill and call button panel, and the car at the parked stop
    /// with the cabin design's walls, ceiling and light, handrails, floor, operating panel and doors. The car and landing
    /// doors at the parked stop open together (a look and a click in walk mode, like any door).
    /// </summary>
    public sealed class LiftBuilder
    {
        const float LeafT = 0.03f;        // door leaf thickness
        const float PanelT = 0.025f;      // car wall panels
        readonly HouseContext _c;
        public LiftBuilder(HouseContext c) { _c = c; }

        LiftGeometry _g;
        LiftSpec _s;
        LiftCabin _cabin;
        string _id;
        Material _concrete, _plaster, _render, _steel, _rail, _alu, _black, _sill;

        public void Build(LiftGeometry g)
        {
            _g = g; _s = g.Spec; _id = g.Def.Id ?? "lift";
            var cat = LiftCatalog.File;
            _cabin = LiftCatalog.Cabin(g.Def.Cabin) ?? LiftCatalog.Cabin(_s.Model.Cabin)
                     ?? cat.Cabins.Find(c => c.Type == (_s.Freight ? "freight" : _s.Panoramic ? "panoramic" : "passenger"))
                     ?? new LiftCabin();
            _concrete = _c.Mats.Tint(_c.M.Plaster, "#9c9b97");
            _plaster = _c.M.Plaster;
            _render = _c.Mats.Get("render", _c.M.Plaster);
            _steel = _c.Mats.Tint(_c.M.WhiteMetal, "#6f7274");
            _rail = _c.Mats.Tint(_c.M.BlackMetal, "#3c3f42");
            _alu = _c.M.DoorAluminium ?? _c.M.Chrome;
            _black = _c.M.BlackMetal;
            // door sills: brushed aluminium (a smooth one mirrors the sky probe as a blue strip)
            _sill = _c.Mats.Get("lift_brushed" + Over("#a9abad", Grey(0xd8)), _alu);

            var root = new GameObject("Lift_" + _id).transform;
            root.SetParent(_c.Shell, false);
            var shaft = Mb(); var glass = Mb(); var car = Mb(); var decor = Mb(); var carDecor = Mb(); var lights = Mb();
            var leafClosed = Mb();

            Shaft(shaft, glass);
            MachineRoom(shaft);
            Equipment(decor);
            var movers = new List<(string name, MeshBuilder mb, Vector3 slide)>();
            foreach (var stop in g.Stops)
            {
                bool parked = stop == g.Parked;
                Landing(stop, decor, parked ? null : leafClosed, parked ? movers : null);
            }
            Car(car, glass, carDecor, lights, movers);

            _c.W.Emit("Shell_Lift_" + _id, root, shaft);
            _c.W.Emit("Lift_" + _id + "_Glass", root, glass, castShadows: false);
            CarLayer(_c.W.Emit("Lift_" + _id + "_Car", root, car), false);
            _c.W.Emit("Lift_" + _id + "_Doors", root, leafClosed);
            _c.W.Emit("Decor_Lift_" + _id, root, decor);
            CarLayer(_c.W.Emit("Decor_Lift_" + _id + "_Car", root, carDecor), false);
            CarLayer(_c.W.Emit("Decor_Lift_" + _id + "_Light", root, lights, castShadows: false), false);
            foreach (var o in Movers(root, movers)) CarLayer(o, true);
            CarLight();
        }

        MeshBuilder Mb() => new MeshBuilder { Transform = _g.ToWorld };

        // ------------------------------------------------------------------ materials
        /// <summary>Library material of a catalogue finish (lift_* / liftprint_*), else a built-in metal of the same look.</summary>
        Material Fin(string finishId, Material fallback = null)
        {
            var f = LiftCatalog.Finish(finishId);
            fallback ??= _c.M.Chrome;
            if (f == null) return finishId != null && _c.Mats.Has(finishId) ? _c.Mats.Get(finishId, fallback) : fallback;
            string tint = f.Tint;
            Material Builtin(Material m) => tint != null ? _c.Mats.Tint(m, tint) : m;
            if (f.Material != null) return _c.Mats.Get(f.Material, Builtin(fallback));
            // the library metals are neutral: "name#rrggbb" multiplies them, so the tint is the finish colour over the texture's mean
            string Lib(string name, Color mean) => tint == null ? name : name + Over(tint, mean);
            switch (f.Base)
            {
                case "mirror": case "etched": return _c.Mats.Get(Lib("lift_mirror", Grey(0xe6)), Builtin(_c.M.Chrome));
                case "painted": return _c.Mats.Get(Lib("lift_painted", Grey(0xe6)), Builtin(_c.M.WhiteMetal));
                case "wood-look": return _c.Mats.Get(Lib("lift_woodmetal", WoodMean), Builtin(_c.M.Walnut));
                case "checker": return _c.Mats.Get("lift_checker", _c.M.Chrome);
                case "glass": return tint != null ? _c.Mats.Tint(_c.M.BlackGlass ?? _c.M.Glass, tint) : _c.M.Glass;
                default: return _c.Mats.Get(Lib("lift_brushed", Grey(0xd8)), Builtin(_c.M.Chrome));
            }
        }

        static Color Grey(int v) => new Color(v / 255f, v / 255f, v / 255f);
        /// <summary>Mean of lift_woodmetal (beech, SL-8055): wood finishes are tinted relative to it.</summary>
        static readonly Color WoodMean = new Color(0xc0 / 255f, 0x94 / 255f, 0x55 / 255f);

        /// <summary>"#rrggbb" that turns a texture of mean <paramref name="mean"/> into <paramref name="target"/> (per channel, linear light).</summary>
        static string Over(string target, Color mean)
        {
            if (!ColorUtility.TryParseHtmlString(target, out var t)) return "";
            var tl = t.linear; var ml = mean.linear;
            var c = new Color(Mathf.Clamp01(tl.r / Mathf.Max(ml.r, 1e-3f)), Mathf.Clamp01(tl.g / Mathf.Max(ml.g, 1e-3f)), Mathf.Clamp01(tl.b / Mathf.Max(ml.b, 1e-3f))).gamma;
            return "#" + ColorUtility.ToHtmlStringRGB(c).ToLowerInvariant();
        }

        /// <summary>Size of a panel showing <paramref name="print"/>: its picture's aspect at <paramref name="h"/> high, no wider than <paramref name="maxW"/>.</summary>
        static Vector2 PanelSize(Material print, float w, float h, float maxW)
        {
            var tex = print != null && print.HasProperty("_BaseMap") ? print.GetTexture("_BaseMap") : null;
            if (tex == null || tex.height == 0) return new Vector2(Mathf.Min(w, maxW), h);
            float aspect = (float)tex.width / tex.height;
            float pw = h * aspect;
            if (pw > maxW) { pw = maxW; h = pw / aspect; }
            return new Vector2(pw, h);
        }

        /// <summary>A picture fitted to a whole surface (floor layout, etched door, button panel), or null when absent.</summary>
        Material Print(string prefix, string id) =>
            id != null && _c.Mats.Has(prefix + id.Replace('-', '_')) ? _c.Mats.Get(prefix + id.Replace('-', '_'), null) : null;

        // ------------------------------------------------------------------ shaft
        void Shaft(MeshBuilder mb, MeshBuilder glass)
        {
            var g = _g;
            if (g.Enclosure == "none") { PitAndHead(mb, false); return; }
            float y0 = g.PitBottom - 0.2f, y1 = g.Top + 0.2f;
            var pts = LocalOutline(0f);
            // side and back walls: one slab per outline edge but the front one, run on past the corners so they close
            for (int i = 1; i < pts.Count; i++)
            {
                Vector2 a = pts[i], b = pts[(i + 1) % pts.Count];
                // curved glass needs a post only every third facet
                if (g.Enclosure == "glass") GlassSegment(glass, mb, a, b, y0 + 0.2f, g.Top, post: _s.Shape == "rect" || i % 3 == 1);
                else WallSegment(mb, a, b, g.T, y0, y1, extA: g.T, extB: g.T);
            }
            FrontWall(mb, glass);
            PitAndHead(mb, g.Enclosure == "glass");
        }

        /// <summary>
        /// Local shaft outline from the front-right corner (+X) to the front-left one, then round the back (the order of
        /// <see cref="LiftGeometry.Outline"/>): edge 0 is the front wall, built separately with its doors.
        /// </summary>
        List<Vector2> LocalOutline(float grow)
        {
            float x0 = -_g.W * 0.5f - grow, x1 = _g.W * 0.5f + grow, zf = -_g.T + grow, zb = -_g.T - _g.D - grow;
            var pts = new List<Vector2> { new Vector2(x1, zf), new Vector2(x0, zf) };
            if (_s.Shape == "semicircle")
            {
                float r = (x1 - x0) * 0.5f, zc = zb + r;
                const int n = 12;
                for (int i = 0; i <= n; i++)
                {
                    float a = Mathf.PI * i / n;
                    pts.Add(new Vector2(-Mathf.Cos(a) * r, zc - Mathf.Sin(a) * r));
                }
            }
            else if (_s.Shape == "rhombus")
            {
                float c = (x1 - x0) * 0.3f;
                pts.Add(new Vector2(x0, zb + c)); pts.Add(new Vector2(x0 + c, zb)); pts.Add(new Vector2(x1 - c, zb)); pts.Add(new Vector2(x1, zb + c));
            }
            else { pts.Add(new Vector2(x0, zb)); pts.Add(new Vector2(x1, zb)); }
            return pts;
        }

        /// <summary>
        /// A wall slab on the outline edge a→b (local plan; the shaft is on its left going a→b… i.e. the clear side),
        /// <paramref name="t"/> thick outwards, run on past its ends by <paramref name="extA"/>/<paramref name="extB"/>.
        /// </summary>
        void WallSegment(MeshBuilder mb, Vector2 a, Vector2 b, float t, float y0, float y1, float extA, float extB)
        {
            var dir = b - a; float len = dir.magnitude;
            if (len < 1e-3f) return;
            dir /= len;
            var outN = new Vector2(dir.y, -dir.x);                     // right of a→b = away from the clear shaft (ccw outline)
            // segment frame: x along a→b, z outwards
            var rot = Quaternion.LookRotation(new Vector3(outN.x, 0, outN.y), Vector3.up);
            var m = Matrix4x4.TRS(new Vector3(a.x, 0, a.y), rot, Vector3.one);
            // in the frame the edge runs along local −X or +X: find it
            var lb = m.inverse.MultiplyPoint3x4(new Vector3(b.x, 0, b.y));
            float s0 = Mathf.Min(0f, lb.x) - (lb.x >= 0 ? extA : extB), s1 = Mathf.Max(0f, lb.x) + (lb.x >= 0 ? extB : extA);
            var keep = mb.Transform;
            mb.Transform = keep * m;
            Bands(mb, s0, s1, y0, y1, 0f, t);
            mb.Transform = keep;
        }

        /// <summary>
        /// Wall body from z0 (shaft side) to z1 (outside) in the current frame, cut into height bands so its outer face
        /// is plaster inside the building and render where the shaft head rises above the roof.
        /// </summary>
        void Bands(MeshBuilder mb, float s0, float s1, float y0, float y1, float z0, float z1)
        {
            float roofY = BuildingTop();
            void Piece(float a, float b, Material outside)
            {
                if (b - a < 0.005f) return;
                mb.Box(new Vector3(s0, a, z0), new Vector3(s1, b, z1), BoxMats.All(_concrete).With(zp: outside));
            }
            if (roofY > y0 && roofY < y1) { Piece(y0, roofY, _plaster); Piece(roofY, y1, _render); }
            else Piece(y0, y1, roofY <= y0 ? _render : _plaster);
        }

        /// <summary>Top of the building around the lift: the roof over the highest storey (its ceiling + slab).</summary>
        float BuildingTop()
        {
            var levels = _c.Doc.Levels;
            var top = levels.Count > 0 ? levels[levels.Count - 1] : _g.Highest;
            return top.Elevation + top.Height + 0.3f;
        }

        void GlassSegment(MeshBuilder glass, MeshBuilder frame, Vector2 a, Vector2 b, float y0, float y1, bool post)
        {
            // panes between steel posts at the outline's corners, transoms at every floor
            const float pw = 0.06f;
            if (post) frame.Box(new Vector3(a.x - pw * 0.5f, y0, a.y - pw * 0.5f), new Vector3(a.x + pw * 0.5f, y1, a.y + pw * 0.5f), _steel);
            var n = Vector2.Perpendicular(b - a).normalized * -0.01f;
            Vector3 P(Vector2 q, float y, Vector2 off) => new Vector3(q.x + off.x, y, q.y + off.y);
            glass.Quad(P(a, y0, n), P(b, y0, n), P(b, y1, n), P(a, y1, n), new Vector3(-n.x, 0, -n.y).normalized,
                new Vector2(0, y0), new Vector2((b - a).magnitude, y0), new Vector2((b - a).magnitude, y1), new Vector2(0, y1), _c.M.Glass);
            glass.Quad(P(b, y0, -n), P(a, y0, -n), P(a, y1, -n), P(b, y1, -n), new Vector3(n.x, 0, n.y).normalized,
                new Vector2(0, y0), new Vector2((b - a).magnitude, y0), new Vector2((b - a).magnitude, y1), new Vector2(0, y1), _c.M.Glass);
            foreach (var L in _g.Stops)
                frame.Box(new Vector3(Mathf.Min(a.x, b.x) - 0.02f, L.Elevation - 0.1f, Mathf.Min(a.y, b.y) - 0.02f),
                          new Vector3(Mathf.Max(a.x, b.x) + 0.02f, L.Elevation, Mathf.Max(a.y, b.y) + 0.02f), _steel);
        }

        /// <summary>The front wall (hall side, z −T…0) with a landing door opening at every stop.</summary>
        void FrontWall(MeshBuilder mb, MeshBuilder glass)
        {
            var g = _g;
            float y0 = g.PitBottom - 0.2f, y1 = g.Top + 0.2f;
            var (dx0, dx1) = g.DoorX;
            float hh = _s.DoorHeight;
            var holes = new List<(float a, float b)>();
            foreach (var L in g.Stops) holes.Add((L.Elevation, L.Elevation + hh + 0.05f));
            float x0 = -g.W * 0.5f, x1 = g.W * 0.5f;
            float zA = -Mathf.Max(g.T, 0.06f), zB = 0f;
            float y = y0;
            void Full(float a, float b)
            {
                if (b - a < 0.005f) return;
                if (g.Enclosure == "glass") GlassBand(glass, mb, x0, x1, a, b);
                else Bands(mb, x0, x1, a, b, zA, zB);
            }
            void Split(float a, float b)
            {
                if (g.Enclosure == "glass")
                {
                    GlassBand(glass, mb, x0, dx0 - 0.05f, a, b);
                    GlassBand(glass, mb, dx1 + 0.05f, x1, a, b);
                    return;
                }
                Bands(mb, x0, dx0 - 0.05f, a, b, zA, zB);
                Bands(mb, dx1 + 0.05f, x1, a, b, zA, zB);
            }
            foreach (var (a, b) in holes)
            {
                Full(y, a);
                Split(a, b);
                y = b;
            }
            Full(y, y1);
        }

        void GlassBand(MeshBuilder glass, MeshBuilder frame, float x0, float x1, float y0, float y1)
        {
            if (x1 - x0 < 0.01f || y1 - y0 < 0.01f) return;
            glass.Quad(new Vector3(x0, y0, -0.02f), new Vector3(x1, y0, -0.02f), new Vector3(x1, y1, -0.02f), new Vector3(x0, y1, -0.02f), Vector3.forward,
                new Vector2(x0, y0), new Vector2(x1, y0), new Vector2(x1, y1), new Vector2(x0, y1), _c.M.Glass);
            glass.Quad(new Vector3(x1, y0, -0.03f), new Vector3(x0, y0, -0.03f), new Vector3(x0, y1, -0.03f), new Vector3(x1, y1, -0.03f), Vector3.back,
                new Vector2(x0, y0), new Vector2(x1, y0), new Vector2(x1, y1), new Vector2(x0, y1), _c.M.Glass);
            frame.Box(new Vector3(x0 - 0.03f, y0, -0.05f), new Vector3(x0 + 0.03f, y1, 0f), _steel);
            frame.Box(new Vector3(x1 - 0.03f, y0, -0.05f), new Vector3(x1 + 0.03f, y1, 0f), _steel);
        }

        void PitAndHead(MeshBuilder mb, bool glassy)
        {
            var g = _g;
            var clear = LocalOutline(0f);
            var outer = LocalOutline(g.T);
            Polygon.Prism(mb, Polygon.CounterClockwise(clear), g.PitBottom - 0.2f, g.PitBottom, _concrete, _concrete, _concrete);
            if (!glassy && g.Enclosure != "none")
                Polygon.Prism(mb, Polygon.CounterClockwise(outer), g.Top, g.Top + 0.2f, g.Top + 0.2f > BuildingTop() ? _render : _plaster, _concrete, _render);
            else if (glassy)
                Polygon.Prism(mb, Polygon.CounterClockwise(outer), g.Top, g.Top + 0.12f, _steel, _steel, _steel);
        }

        /// <summary>MR drives: the machine room on the shaft's head (AM × BM, clear height from the catalogue), rendered outside.</summary>
        void MachineRoom(MeshBuilder mb)
        {
            if (_s.MachineRoom == null) return;
            var mr = _s.MachineRoom.Value;
            float zc = -_g.T - _g.D * 0.5f, y0 = _g.Top + 0.2f, y1 = y0 + _s.MachineHeight + 0.2f;
            float hx = mr.x * 0.5f + 0.2f, hz = mr.y * 0.5f + 0.2f;
            mb.Box(new Vector3(-hx, y0, zc - hz), new Vector3(hx, y1, zc + hz), BoxMats.All(_render).With(yp: _concrete));
            // its steel door towards the landing side
            mb.Box(new Vector3(-0.5f, y0, zc + hz), new Vector3(0.5f, y0 + 2.1f, zc + hz + 0.02f), _steel);
        }

        /// <summary>Guide rails, counterweight with its rails, ropes; the traction machine of an MRL drive in the head.</summary>
        void Equipment(MeshBuilder mb)
        {
            var g = _g;
            float cx = g.CarX, cz = g.CarFront - g.CarD * 0.5f;
            float y0 = g.PitBottom, y1 = g.Top;
            float rx = g.CarW * 0.5f + 0.1f;
            foreach (float sx in new[] { -1f, 1f })
            {
                mb.Box(new Vector3(cx + sx * rx - 0.008f, y0, cz - 0.045f), new Vector3(cx + sx * rx + 0.008f, y1, cz + 0.045f), _rail);
                mb.Box(new Vector3(cx + sx * (rx + 0.035f) - 0.035f, y0, cz - 0.004f), new Vector3(cx + sx * (rx + 0.035f) + 0.035f, y1, cz + 0.004f), _rail);
            }
            // counterweight: behind the car or beside it; it hangs high while the car is low
            float carY = g.Parked.Elevation;
            float cwH = 2.2f;
            float cwY = Mathf.Clamp(g.Top - (carY - g.PitBottom) - cwH - 0.3f, g.PitBottom + 0.6f, g.Top - cwH - 0.2f);
            Vector3 c0, c1;
            if (_s.Model?.Counterweight == "side")
            {
                float sx = g.CarX < 0 ? 1f : -1f;
                float x = sx * (g.W * 0.5f - 0.1f);
                c0 = new Vector3(x - 0.06f, cwY, cz - 0.35f); c1 = new Vector3(x + 0.06f, cwY + cwH, cz + 0.35f);
            }
            else
            {
                float zb = -g.T - g.D;
                c0 = new Vector3(cx - 0.4f, cwY, zb + 0.06f); c1 = new Vector3(cx + 0.4f, cwY + cwH, zb + 0.18f);
            }
            mb.Box(c0, c1, _c.Mats.Tint(_c.M.BlackMetal, "#2c2f33"));
            // ropes from the car's crosshead and the counterweight up to the head
            float carTop = carY + _s.CarHeight + 0.55f;
            for (int i = -1; i <= 1; i++)
            {
                mb.Box(new Vector3(cx + i * 0.03f - 0.005f, carTop, cz - 0.005f), new Vector3(cx + i * 0.03f + 0.005f, y1 - 0.3f, cz + 0.005f), _rail);
                var cc = (c0 + c1) * 0.5f;
                mb.Box(new Vector3(cc.x + i * 0.03f - 0.005f, c1.y, cc.z - 0.005f), new Vector3(cc.x + i * 0.03f + 0.005f, y1 - 0.3f, cc.z + 0.005f), _rail);
            }
            // MRL: the gearless machine on its beam in the head
            if (_s.MachineRoom == null && g.Enclosure != "none")
            {
                var yellow = _c.Mats.Tint(_c.M.GlossWhite, "#e0b020");
                var m0 = new Vector3(cx - 0.3f, y1 - 0.65f, cz - 0.3f);
                mb.Box(m0, m0 + new Vector3(0.6f, 0.5f, 0.6f), BoxMats.All(_c.M.BlackMetal).With(xn: yellow, xp: yellow));
                mb.Box(new Vector3(-g.W * 0.5f, y1 - 0.75f, cz - 0.08f), new Vector3(g.W * 0.5f, y1 - 0.65f, cz + 0.08f), _steel);
            }
            // pit buffers under the car
            foreach (float sx in new[] { -0.3f, 0.3f })
                mb.Box(new Vector3(cx + sx - 0.06f, y0, cz - 0.06f), new Vector3(cx + sx + 0.06f, y0 + 0.45f, cz + 0.06f), _c.Mats.Tint(_c.M.GlossWhite, "#d9a520"));
        }

        // ------------------------------------------------------------------ landings
        void Landing(LevelDef L, MeshBuilder decor, MeshBuilder closed, List<(string, MeshBuilder, Vector3)> movers)
        {
            var g = _g;
            var (dx0, dx1) = g.DoorX;
            float y = L.Elevation, hh = _s.DoorHeight, t = Mathf.Max(g.T, 0.06f);
            var doorDef = LiftCatalog.LandingDoor(g.Def.Door ?? _cabin.LandingDoor ?? _s.Model?.LandingDoor);
            // portals are hairline in the door's colour: a big mirror frame shows the reflection probes' pixels
            var pf = LiftCatalog.Finish(doorDef?.Finish ?? "stainless-hairline");
            var portal = pf != null && (pf.Base == "mirror" || pf.Base == "etched")
                ? _c.Mats.Get("lift_brushed" + (pf.Tint != null ? Over(pf.Tint, Grey(0xd8)) : ""), Fin(pf.Id))
                : Fin(doorDef?.Finish ?? "stainless-hairline");
            const float jamb = 0.05f, proud = 0.012f;
            if (g.Enclosure != "glass")
            {
                // portal round the opening on the hall side, linings in the reveals, a soffit plate on top
                decor.Box(new Vector3(dx0 - jamb, y, 0f), new Vector3(dx0, y + hh + jamb, proud), portal);
                decor.Box(new Vector3(dx1, y, 0f), new Vector3(dx1 + jamb, y + hh + jamb, proud), portal);
                decor.Box(new Vector3(dx0, y + hh, 0f), new Vector3(dx1, y + hh + jamb, proud), portal);
                decor.Box(new Vector3(dx0 - 0.002f, y, -t), new Vector3(dx0 + 0.0f, y + hh, 0.0f), portal);
                decor.Box(new Vector3(dx1, y, -t), new Vector3(dx1 + 0.002f, y + hh, 0.0f), portal);
                decor.Box(new Vector3(dx0, y + hh, -t), new Vector3(dx1, y + hh + 0.002f, 0f), portal);
            }
            // sill flush with the floor at the shaft's edge, under the leaves (the level's floor fill runs through the reveal to it)
            decor.Box(new Vector3(dx0 - 0.03f, y - 0.012f, -t - 0.06f), new Vector3(dx1 + 0.03f, y + 0.002f, -t + 0.03f), _sill);
            // call button panel on the hall wall beside the doors (on the right seen from the hall = −X)
            var call = Print("liftpanel_", g.Def.Call ?? _s.Model?.Call ?? (_s.Freight ? "dl100a" : "dl300"));
            var cs = PanelSize(call, 0.1f, 0.35f, 0.3f);
            float px1 = dx0 - jamb - 0.18f, px0 = px1 - cs.x;
            FittedBox(decor, new Vector3(px0, y + 1.3f - cs.y, 0f), new Vector3(px1, y + 1.3f, 0.012f), Fin("stainless-hairline"), call, Face.ZPos);
            if (call == null)
            {
                decor.Box(new Vector3(px0 + 0.03f, y + 1.06f, 0.012f), new Vector3(px1 - 0.03f, y + 1.1f, 0.018f), _c.M.Led);
                decor.Box(new Vector3(px0 + 0.03f, y + 1.14f, 0.012f), new Vector3(px1 - 0.03f, y + 1.18f, 0.018f), _c.M.Led);
            }
            // landing door leaves inside the shaft behind the front wall
            var face = Print("liftdoor_", doorDef?.Id);
            var leaf = Fin(doorDef?.Finish ?? "stainless-hairline");
            Leaves(closed, movers, "Landing_" + L.Id, y, -t - 0.01f, +1f, leaf, face);
        }

        /// <summary>
        /// Door leaves over the opening dx0…dx1 at height <paramref name="y"/>, their hall-side face at <paramref name="zFace"/>
        /// (<paramref name="faceDir"/> = which way it looks). Centre opening: two leaves part to the sides; two-speed: both
        /// run to +X, the far one twice as far. Closed leaves go into <paramref name="closed"/>; with <paramref name="movers"/>
        /// each leaf becomes a mover group (car and landing leaves that move alike share one).
        /// </summary>
        void Leaves(MeshBuilder closed, List<(string name, MeshBuilder mb, Vector3 slide)> movers, string tag, float y, float zFace, float faceDir,
                    Material m, Material face)
        {
            var (dx0, dx1) = _g.DoorX;
            float jj = dx1 - dx0, hh = _s.DoorHeight + 0.02f;
            const float over = 0.025f;
            var parts = new List<(float x0, float x1, float depth, Vector3 slide, string key)>();
            if (_s.DoorType == "2s")
            {
                parts.Add((dx0 + jj * 0.5f - 0.01f, dx1 + over, 0f, new Vector3(jj * 0.5f, 0, 0), "slow"));
                parts.Add((dx0 - over, dx0 + jj * 0.5f + 0.01f, 0.035f, new Vector3(jj, 0, 0), "fast"));
            }
            else
            {
                parts.Add((dx0 - over, dx0 + jj * 0.5f, 0f, new Vector3(-jj * 0.5f, 0, 0), "left"));
                parts.Add((dx0 + jj * 0.5f, dx1 + over, 0f, new Vector3(jj * 0.5f, 0, 0), "right"));
            }
            foreach (var p in parts)
            {
                float zf = zFace - faceDir * p.depth;
                float zb = zf - faceDir * LeafT;
                var mn = new Vector3(p.x0, y, Mathf.Min(zf, zb));
                var mx = new Vector3(p.x1, y + hh, Mathf.Max(zf, zb));
                MeshBuilder target = closed;
                if (movers != null)
                {
                    int i = movers.FindIndex(q => q.name == p.key);
                    if (i < 0) { movers.Add((p.key, Mb(), p.slide)); i = movers.Count - 1; }
                    target = movers[i].mb;
                }
                if (target == null) continue;
                // the picture spans the whole closed door: each leaf shows its part of it
                Rect uv = new Rect((p.x0 - dx0) / jj, 0f, (p.x1 - p.x0) / jj, 1f);
                FittedBox(target, mn, mx, m, face, faceDir > 0 ? Face.ZPos : Face.ZNeg, uv);
            }
        }

        // ------------------------------------------------------------------ car
        void Car(MeshBuilder car, MeshBuilder glass, MeshBuilder decor, MeshBuilder lights, List<(string, MeshBuilder, Vector3)> movers)
        {
            var g = _g;
            float y = g.Parked.Elevation, ch = _s.CarHeight, hh = _s.DoorHeight;
            float cx = g.CarX, zf = g.CarFront, aa = g.CarW, bb = g.CarD;
            float x0 = cx - aa * 0.5f, x1 = cx + aa * 0.5f, zb = zf - bb;
            var (dx0, dx1) = g.DoorX;
            var outside = _c.Mats.Tint(_c.M.WhiteMetal, "#8d9093");
            var back = Fin(_cabin.Walls?.Back ?? "stainless-hairline");
            var side = Fin(_cabin.Walls?.Side ?? _cabin.Walls?.Back ?? "stainless-hairline");
            var front = Fin(_cabin.Walls?.Front ?? "stainless-hairline");
            var backPrint = Print("liftwall_", _cabin.Id != null ? _cabin.Id + "_back" : null);
            var sidePrint = Print("liftwall_", _cabin.Id != null ? _cabin.Id + "_side" : null);
            bool panoramic = _s.Panoramic;

            // platform and floor finish
            car.Box(new Vector3(x0 - 0.05f, y - 0.16f, zb - 0.05f), new Vector3(x1 + 0.05f, y - 0.004f, zf + 0.03f), outside);
            var floorPrint = Print("liftfloor_", _cabin.Floor);
            var floorMat = floorPrint ?? Fin(_cabin.Floor != null && _cabin.Floor.Contains("checker") ? "checker-plate" : null,
                _s.Freight ? _c.Mats.Get("lift_checker", _c.M.Chrome) : _c.M.TileDark);
            if (panoramic) Polygon.Prism(car, Polygon.CounterClockwise(CarOutline()), y - 0.004f, y, floorMat, floorMat, floorMat);
            else if (floorPrint != null)
                // the layout seen from the door: its top towards the back wall, its left on the left (+X)
                car.Quad(new Vector3(x0, y, zb), new Vector3(x1, y, zb), new Vector3(x1, y, zf), new Vector3(x0, y, zf), Vector3.up,
                    new Vector2(1, 1), new Vector2(0, 1), new Vector2(0, 0), new Vector2(1, 0), floorMat);
            else car.PlanarFace(new Vector3(x0, y, zb), new Vector3(x1, y, zb), new Vector3(x1, y, zf), new Vector3(x0, y, zf), Vector3.up, floorMat);
            car.Box(new Vector3(dx0 - 0.03f, y - 0.012f, zf - 0.002f), new Vector3(dx1 + 0.03f, y + 0.002f, zf + 0.045f), _sill);

            // walls as panels with dark seams; panoramic cars: glass round the back above a steel dado
            if (panoramic) PanoramicWalls(car, glass, y, ch, side);
            else
            {
                // a wall picture has its own panel joints: no seams of ours across it
                Panels(car, new Vector2(x1, zb), new Vector2(x0, zb), y, ch, back, outside, backPrint, backPrint != null ? 1 : Mathf.Max(1, Mathf.RoundToInt(aa / 0.5f)));
                int sideN = sidePrint != null ? 1 : Mathf.Max(2, Mathf.RoundToInt(bb / 0.55f));
                Panels(car, new Vector2(x0, zb), new Vector2(x0, zf), y, ch, side, outside, sidePrint, sideN);
                Panels(car, new Vector2(x1, zf), new Vector2(x1, zb), y, ch, side, outside, sidePrint, sideN);
            }
            // front wall: returns beside the door and the header over it
            car.Box(new Vector3(x0 - PanelT, y, zf - PanelT), new Vector3(dx0, y + ch, zf), BoxMats.All(outside).With(zn: front));
            car.Box(new Vector3(dx1, y, zf - PanelT), new Vector3(x1 + PanelT, y + ch, zf), BoxMats.All(outside).With(zn: front));
            car.Box(new Vector3(dx0, y + hh, zf - PanelT), new Vector3(dx1, y + ch, zf), BoxMats.All(outside).With(zn: front));
            // car roof, frame (sling) and door operator
            car.Box(new Vector3(x0 - PanelT, y + ch, zb - PanelT), new Vector3(x1 + PanelT, y + ch + 0.06f, zf), outside);
            float cz = zf - bb * 0.5f;
            foreach (float sx in new[] { -1f, 1f })
                car.Box(new Vector3(cx + sx * (aa * 0.5f + 0.06f) - 0.04f, y - 0.35f, cz - 0.08f), new Vector3(cx + sx * (aa * 0.5f + 0.06f) + 0.04f, y + ch + 0.55f, cz + 0.08f), _rail);
            car.Box(new Vector3(x0 - 0.12f, y + ch + 0.4f, cz - 0.08f), new Vector3(x1 + 0.12f, y + ch + 0.55f, cz + 0.08f), _rail);
            car.Box(new Vector3(x0 - 0.12f, y - 0.35f, cz - 0.08f), new Vector3(x1 + 0.12f, y - 0.16f, cz + 0.08f), _rail);
            car.Box(new Vector3(dx0 - 0.25f, y + hh + 0.06f, zf), new Vector3(dx1 + 0.25f, y + hh + 0.28f, zf + 0.12f), _black);

            Ceiling(decor, lights, y, ch, x0, x1, zb, zf);
            Handrails(decor, y, x0, x1, zb, zf);
            // operating panel on the front return, right of the door seen from inside (+X)
            var cop = Print("liftpanel_", _g.Def.Panel ?? _s.Model?.Panel ?? (_s.Freight ? "dc1000a_freight" : "dc1000a"));
            var ps = PanelSize(cop, 0.17f, 1.15f, Mathf.Max(0.05f, x1 - 0.05f - (dx1 + 0.08f)));
            float px0 = dx1 + 0.08f, px1 = px0 + ps.x;
            if (px1 - px0 > 0.04f)
            {
                FittedBox(decor, new Vector3(px0, y + 2.0f - ps.y, zf - PanelT - 0.012f), new Vector3(px1, y + 2.0f, zf - PanelT), Fin("stainless-hairline"), cop, Face.ZNeg);
                if (cop == null)
                    for (int i = 0; i < 6; i++)
                    {
                        float by = y + 1.05f + i * 0.09f;
                        decor.Box(new Vector3((px0 + px1) * 0.5f - 0.018f, by, zf - PanelT - 0.018f), new Vector3((px0 + px1) * 0.5f + 0.018f, by + 0.036f, zf - PanelT - 0.012f), _c.M.Chrome);
                    }
            }
            // car doors in front of the car's door line
            Leaves(movers == null ? car : null, movers, "Car", y, zf + 0.03f + LeafT, +1f, Fin(_cabin.Door ?? "stainless-hairline"), null);
            CarProbe(y, ch, x0, x1, zb, zf);
        }

        /// <summary>The car's floor outline (local plan): a rectangle, or with a half-round / chamfered glass back.</summary>
        List<Vector2> CarOutline()
        {
            float x0 = _g.CarX - _g.CarW * 0.5f, x1 = _g.CarX + _g.CarW * 0.5f, zf = _g.CarFront, zb = zf - _g.CarD;
            var pts = new List<Vector2> { new Vector2(x1, zf), new Vector2(x0, zf) };
            if (_s.Shape == "semicircle")
            {
                float r = (x1 - x0) * 0.5f, zc = zb + r;
                const int n = 10;
                for (int i = 0; i <= n; i++) { float a = Mathf.PI * i / n; pts.Add(new Vector2(_g.CarX - Mathf.Cos(a) * r, zc - Mathf.Sin(a) * r)); }
            }
            else if (_s.Shape == "rhombus")
            {
                float c = (x1 - x0) * 0.3f;
                pts.Add(new Vector2(x0, zb + c)); pts.Add(new Vector2(x0 + c, zb)); pts.Add(new Vector2(x1 - c, zb)); pts.Add(new Vector2(x1, zb + c));
            }
            else { pts.Add(new Vector2(x0, zb)); pts.Add(new Vector2(x1, zb)); }
            return pts;
        }

        void PanoramicWalls(MeshBuilder car, MeshBuilder glass, float y, float ch, Material metal)
        {
            var pts = CarOutline();
            float dado = 0.9f;
            for (int i = 1; i < pts.Count; i++)
            {
                Vector2 a = pts[i], b = pts[(i + 1) % pts.Count];
                if ((b - a).sqrMagnitude < 1e-6f) continue;
                bool straightSide = Mathf.Abs(a.x - b.x) < 1e-3f;
                // steel dado and frieze, glass between (the straight returns by the door stay steel up to the top)
                SegmentPanel(car, a, b, y, straightSide ? y + ch : y + dado, metal);
                if (!straightSide)
                {
                    SegmentPanel(car, a, b, y + ch - 0.15f, y + ch, metal);
                    var n = Vector2.Perpendicular(b - a).normalized * 0.012f;
                    glass.Quad(new Vector3(a.x - n.x, y + dado, a.y - n.y), new Vector3(b.x - n.x, y + dado, b.y - n.y), new Vector3(b.x - n.x, y + ch - 0.15f, b.y - n.y),
                        new Vector3(a.x - n.x, y + ch - 0.15f, a.y - n.y), new Vector3(n.x, 0, n.y).normalized, Vector2.zero, Vector2.right, Vector2.one, Vector2.up, _c.M.Glass);
                    glass.Quad(new Vector3(b.x + n.x, y + dado, b.y + n.y), new Vector3(a.x + n.x, y + dado, a.y + n.y), new Vector3(a.x + n.x, y + ch - 0.15f, a.y + n.y),
                        new Vector3(b.x + n.x, y + ch - 0.15f, b.y + n.y), new Vector3(-n.x, 0, -n.y).normalized, Vector2.zero, Vector2.right, Vector2.one, Vector2.up, _c.M.Glass);
                }
            }
            var outline = Polygon.CounterClockwise(pts);
            Polygon.Prism(car, outline, y + ch, y + ch + 0.08f, metal, metal, metal);
            Polygon.Prism(car, outline, y - 0.2f, y - 0.004f, metal, metal, metal);
        }

        void SegmentPanel(MeshBuilder mb, Vector2 a, Vector2 b, float y0, float y1, Material inner)
        {
            var dir = b - a; float len = dir.magnitude;
            if (len < 1e-3f) return;
            var outN = new Vector2(dir.y, -dir.x) / len;
            var rot = Quaternion.LookRotation(new Vector3(outN.x, 0, outN.y), Vector3.up);
            var m = Matrix4x4.TRS(new Vector3(a.x, 0, a.y), rot, Vector3.one);
            var lb = m.inverse.MultiplyPoint3x4(new Vector3(b.x, 0, b.y));
            var keep = mb.Transform;
            mb.Transform = keep * m;
            mb.Box(new Vector3(Mathf.Min(0, lb.x) - 0.004f, y0, 0f), new Vector3(Mathf.Max(0, lb.x) + 0.004f, y1, PanelT), BoxMats.All(inner));
            mb.Transform = keep;
        }

        /// <summary>
        /// A car wall from a to b (seen from inside, a on the left) as <paramref name="n"/> panels with 3 mm dark seams; the
        /// inner face shows the finish, or a picture fitted across the whole wall.
        /// </summary>
        void Panels(MeshBuilder mb, Vector2 a, Vector2 b, float y, float ch, Material inner, Material outer, Material print, int n)
        {
            var dir = b - a; float len = dir.magnitude;
            var inN = new Vector2(-dir.y, dir.x) / len;
            var centre = new Vector2(_g.CarX, _g.CarFront - _g.CarD * 0.5f);
            if (Vector2.Dot(inN, centre - a) < 0f) inN = -inN;      // towards the inside of the car
            var rot = Quaternion.LookRotation(new Vector3(-inN.x, 0, -inN.y), Vector3.up);   // frame z = outwards
            var m = Matrix4x4.TRS(new Vector3(a.x, 0, a.y), rot, Vector3.one);
            var lb = m.inverse.MultiplyPoint3x4(new Vector3(b.x, 0, b.y));
            float s0 = Mathf.Min(0, lb.x), s1 = Mathf.Max(0, lb.x);
            var keep = mb.Transform;
            mb.Transform = keep * m;
            // backing behind the seams
            mb.Box(new Vector3(s0 - PanelT, y, PanelT * 0.6f), new Vector3(s1 + PanelT, y + _s.CarHeight, PanelT), BoxMats.All(outer).With(zn: _black));
            const float seam = 0.003f;
            for (int i = 0; i < n; i++)
            {
                float p0 = Mathf.Lerp(s0, s1, (float)i / n) + (i > 0 ? seam * 0.5f : 0f);
                float p1 = Mathf.Lerp(s0, s1, (float)(i + 1) / n) - (i < n - 1 ? seam * 0.5f : 0f);
                var mn = new Vector3(p0, y + 0.002f, 0f); var mx = new Vector3(p1, y + ch - 0.002f, PanelT * 0.6f);
                // the frame's −Z face looks into the car
                Rect uv = new Rect((p0 - s0) / (s1 - s0), 0f, (p1 - p0) / (s1 - s0), 1f);
                FittedBox(mb, mn, mx, inner, print, Face.ZNeg, uv, outer);
            }
            mb.Transform = keep;
        }

        void Ceiling(MeshBuilder decor, MeshBuilder lights, float y, float ch, float x0, float x1, float zb, float zf)
        {
            var ceil = LiftCatalog.Ceiling(_cabin.Ceiling);
            string colour = _cabin.CeilingColor != null ? LiftCatalog.Color(_cabin.CeilingColor)?.Hex : null;
            var frame = _cabin.CeilingFinish != null ? Fin(_cabin.CeilingFinish) : ceil?.Finish != null ? Fin(ceil.Finish) : colour != null ? _c.Mats.Tint(_c.M.WhiteMetal, colour) : Fin("stainless-hairline");
            float yc = y + ch - 0.06f;
            decor.Box(new Vector3(x0, yc, zb), new Vector3(x1, y + ch, zf - PanelT), frame);
            // lit panel(s) in the middle, spots round it (most designs of the catalogue)
            float w = (x1 - x0), d = (zf - PanelT - zb);
            var c = new Vector3((x0 + x1) * 0.5f, yc - 0.002f, (zb + zf - PanelT) * 0.5f);
            float lw = w * 0.55f, ld = d * 0.5f;
            if (_s.Freight) { lw = w * 0.35f; ld = 0.25f; }
            lights.Quad(new Vector3(c.x - lw * 0.5f, c.y, c.z + ld * 0.5f), new Vector3(c.x + lw * 0.5f, c.y, c.z + ld * 0.5f),
                        new Vector3(c.x + lw * 0.5f, c.y, c.z - ld * 0.5f), new Vector3(c.x - lw * 0.5f, c.y, c.z - ld * 0.5f), Vector3.down,
                        Vector2.zero, Vector2.right, Vector2.one, Vector2.up, _c.M.Led);
            if (!_s.Freight)
                foreach (var (sx, sz) in new[] { (-1f, -1f), (1f, -1f), (-1f, 1f), (1f, 1f) })
                    _c.Kit.Downlight(lights, new Vector3(c.x + sx * (w * 0.5f - 0.18f), yc, c.z + sz * (d * 0.5f - 0.18f)));
        }

        void Handrails(MeshBuilder mb, float y, float x0, float x1, float zb, float zf)
        {
            var hr = LiftCatalog.Handrail(_cabin.Handrail);
            if (hr == null && !_s.Freight) return;
            var m = Fin(hr?.Finish ?? "stainless-mirror");
            float h = y + 0.9f, off = PanelT + 0.05f;
            float size = hr?.Size != null && hr.Size.Length > 0 ? hr.Size[0] / 1000f : 0.04f;
            string profile = hr?.Profile ?? "flat";
            void Rail(Vector3 a, Vector3 b, Vector3 wallN)
            {
                if (_s.Freight)
                {
                    // bumper rails of a freight car
                    foreach (float hy in new[] { y + 0.3f, y + 0.9f })
                        BoxBetween(mb, a + Vector3.up * (hy - h) - wallN * (off - 0.03f), b + Vector3.up * (hy - h) - wallN * (off - 0.03f), 0.2f, 0.02f, Fin("stainless-hairline"));
                    return;
                }
                if (profile.StartsWith("round")) Rod(mb, a, b, size * 0.5f, m);
                else if (profile == "double" || profile == "triple")
                {
                    int k = profile == "double" ? 2 : 3;
                    for (int i = 0; i < k; i++) Rod(mb, a + Vector3.up * (i * 0.04f), b + Vector3.up * (i * 0.04f), 0.0125f, m);
                }
                else BoxBetween(mb, a, b, profile == "flat" ? 0.08f : 0.045f, profile == "flat" ? 0.012f : 0.075f, m);
                // two brackets to the wall
                foreach (var p in new[] { Vector3.Lerp(a, b, 0.1f), Vector3.Lerp(a, b, 0.9f) })
                    BoxBetween(mb, p, p + wallN * off, 0.02f, 0.02f, m);
            }
            float inset = 0.15f;
            Rail(new Vector3(x0 + inset, h, zb + off), new Vector3(x1 - inset, h, zb + off), Vector3.back);
            if (!_s.Panoramic)
            {
                Rail(new Vector3(x0 + off, h, zb + inset), new Vector3(x0 + off, h, zf - 0.35f), Vector3.left);
                Rail(new Vector3(x1 - off, h, zb + inset), new Vector3(x1 - off, h, zf - 0.35f), Vector3.right);
            }
        }

        void CarLight()
        {
            // a wide spot under the lit ceiling panel: a point light in mid-air burns hot spots into the metal walls
            var g = _g;
            float y = g.Parked.Elevation + _s.CarHeight - 0.08f;
            var pos = g.World(g.CarX, y, g.CarFront - g.CarD * 0.5f);
            var go = new GameObject("Light_Lift_" + _id);
            go.transform.SetParent(_c.Lights, false);
            go.transform.SetPositionAndRotation(pos, Quaternion.LookRotation(Vector3.down, g.ToWorld.MultiplyVector(Vector3.forward)));
            var l = go.AddComponent<Light>();
            l.type = LightType.Spot;
            l.spotAngle = 150f;
            l.innerSpotAngle = 90f;
            l.color = new Color(1f, 0.95f, 0.88f);
            l.intensity = _s.Freight ? 1.6f : 1.3f;
            l.range = _s.CarHeight + 0.6f;
            l.shadows = LightShadows.None;
            var data = go.AddComponent<UnityEngine.Rendering.Universal.UniversalAdditionalLightData>();
            data.usePipelineSettings = true;
            data.renderingLayers = CarRenderingLayer;
        }

        void CarProbe(float y, float ch, float x0, float x1, float zb, float zf)
        {
            var g = _g;
            var go = new GameObject("Probe_Lift_" + _id);
            go.transform.SetParent(_c.Probes, false);
            go.transform.position = g.World((x0 + x1) * 0.5f, y + 1.5f, (zb + zf) * 0.5f);
            var p = go.AddComponent<ReflectionProbe>();
            p.mode = ReflectionProbeMode.Realtime;
            p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
            p.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            p.boxProjection = true;
            // probe boxes are world-axis aligned: a turned car gets the box of its rotated footprint
            var a = g.World(x0, y, zb); var b = g.World(x1, y, zf); var c2 = g.World(x0, y, zf); var d = g.World(x1, y, zb);
            float minX = Mathf.Min(Mathf.Min(a.x, b.x), Mathf.Min(c2.x, d.x)), maxX = Mathf.Max(Mathf.Max(a.x, b.x), Mathf.Max(c2.x, d.x));
            float minZ = Mathf.Min(Mathf.Min(a.z, b.z), Mathf.Min(c2.z, d.z)), maxZ = Mathf.Max(Mathf.Max(a.z, b.z), Mathf.Max(c2.z, d.z));
            p.size = new Vector3(maxX - minX, ch + 0.1f, maxZ - minZ);
            p.center = new Vector3((minX + maxX) * 0.5f, y + ch * 0.5f, (minZ + maxZ) * 0.5f) - go.transform.position;
            p.blendDistance = 0.02f;
            p.importance = 3;
            p.resolution = 128;
            p.hdr = true;
            p.nearClipPlane = 0.05f;
            p.farClipPlane = 20f;
        }

        // ------------------------------------------------------------------ movers
        List<GameObject> Movers(Transform root, List<(string name, MeshBuilder mb, Vector3 slide)> movers)
        {
            var made = new List<GameObject>();
            House4696.Runtime.Door first = null;
            foreach (var (name, mb, slide) in movers)
            {
                if (mb.IsEmpty) continue;
                var pivot = new GameObject("Furniture_Lift_" + _id + "_" + name);
                pivot.transform.SetParent(root, false);
                var o = _c.W.Emit("Furniture_Lift_" + _id + "_" + name + "_Leaf", pivot.transform, mb);
                if (o != null) { _c.W.MarkDynamic(o); made.Add(o); }
                _c.W.MarkDynamic(pivot);
                var door = pivot.AddComponent<House4696.Runtime.Door>();
                door.Motion = House4696.Runtime.DoorMotion.Slide;
                // the leaves' meshes are in world space: the slide runs along the shaft's local x
                door.SlideBy = _g.ToWorld.MultiplyVector(slide);
                if (first == null) first = door;
                else { door.Partner = first; first.Partner = door; }
                if (_g.Def.Open) door.SetOpen(true, instant: true);
                var body = pivot.AddComponent<Rigidbody>();
                body.isKinematic = true;
                body.useGravity = false;
            }
            return made;
        }

        /// <summary>
        /// Rendering layer of a car: its light lights only this layer (no glow on the hall walls through the closed
        /// doors) and the hall's lamps, which light layer 1, do not shine into the car through the shaft walls. Door
        /// leaves face both sides and stay on layer 1 as well.
        /// </summary>
        public const uint CarRenderingLayer = 8u;

        static void CarLayer(GameObject o, bool alsoHouse)
        {
            if (o == null) return;
            foreach (var r in o.GetComponentsInChildren<Renderer>(true)) r.renderingLayerMask = CarRenderingLayer | (alsoHouse ? 1u : 0u);
        }

        // ------------------------------------------------------------------ mesh helpers
        enum Face { ZPos, ZNeg }

        /// <summary>A box in the finish <paramref name="m"/>; one face shows <paramref name="print"/> fitted to it (u along +X).</summary>
        void FittedBox(MeshBuilder mb, Vector3 mn, Vector3 mx, Material m, Material print, Face face, Rect? uv = null, Material others = null)
        {
            if (print == null && others == null) { mb.Box(mn, mx, m); return; }
            var o = others ?? m;
            mb.Box(mn, mx, face == Face.ZPos ? BoxMats.All(o).Without(zp: true) : BoxMats.All(o).Without(zn: true));
            var r = uv ?? new Rect(0, 0, 1, 1);
            var mat = print ?? m;
            bool fitted = print != null;
            Vector2 U(float u, float v) => fitted ? new Vector2(r.x + u * r.width, r.y + v * r.height) : MeshBuilder.PlanarUV(new Vector3(Mathf.Lerp(mn.x, mx.x, u), Mathf.Lerp(mn.y, mx.y, v), 0), Vector3.back);
            if (face == Face.ZPos)
                // seen from +Z, +X is on the viewer's left: the picture's u runs the other way
                mb.Quad(new Vector3(mx.x, mn.y, mx.z), new Vector3(mn.x, mn.y, mx.z), new Vector3(mn.x, mx.y, mx.z), new Vector3(mx.x, mx.y, mx.z), Vector3.forward,
                    fitted ? new Vector2(1f - r.xMax, r.yMin) : U(1, 0), fitted ? new Vector2(1f - r.xMin, r.yMin) : U(0, 0),
                    fitted ? new Vector2(1f - r.xMin, r.yMax) : U(0, 1), fitted ? new Vector2(1f - r.xMax, r.yMax) : U(1, 1), mat);
            else
                mb.Quad(new Vector3(mn.x, mn.y, mn.z), new Vector3(mx.x, mn.y, mn.z), new Vector3(mx.x, mx.y, mn.z), new Vector3(mn.x, mx.y, mn.z), Vector3.back,
                    U(0, 0), U(1, 0), U(1, 1), U(0, 1), mat);
        }

        static void FittedQuad(MeshBuilder mb, Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 n, Material m, Rect? uv)
        {
            if (uv == null) { mb.PlanarFace(a, b, c, d, n, m); return; }
            var r = uv.Value;
            mb.Quad(a, b, c, d, n, new Vector2(r.xMin, r.yMin), new Vector2(r.xMax, r.yMin), new Vector2(r.xMax, r.yMax), new Vector2(r.xMin, r.yMax), m);
        }

        /// <summary>A bar of width × thickness from a to b (horizontal), its broad face towards the room.</summary>
        static void BoxBetween(MeshBuilder mb, Vector3 a, Vector3 b, float height, float thick, Material m)
        {
            var dir = b - a; float len = dir.magnitude;
            if (len < 1e-4f) return;
            var rot = Quaternion.LookRotation(dir / len, Vector3.up);
            var keep = mb.Transform;
            mb.Transform = keep * Matrix4x4.TRS(a, rot, Vector3.one);
            mb.Box(new Vector3(-thick * 0.5f, -height * 0.5f, 0f), new Vector3(thick * 0.5f, height * 0.5f, len), m);
            mb.Transform = keep;
        }

        /// <summary>A round bar from a to b (smooth, 12 sides) with flat ends.</summary>
        static void Rod(MeshBuilder mb, Vector3 a, Vector3 b, float r, Material m)
        {
            var axis = (b - a).normalized;
            var u = Vector3.Cross(axis, Mathf.Abs(axis.y) < 0.9f ? Vector3.up : Vector3.right).normalized;
            var v = Vector3.Cross(axis, u);
            const int n = 12;
            float len = (b - a).magnitude;
            for (int i = 0; i < n; i++)
            {
                float t0 = i * Mathf.PI * 2f / n, t1 = (i + 1) * Mathf.PI * 2f / n;
                Vector3 n0 = u * Mathf.Cos(t0) + v * Mathf.Sin(t0), n1 = u * Mathf.Cos(t1) + v * Mathf.Sin(t1);
                Vector3 p0 = a + n0 * r, p1 = a + n1 * r, q0 = b + n0 * r, q1 = b + n1 * r;
                Vector2 uv00 = new Vector2(t0 * r, 0), uv10 = new Vector2(t1 * r, 0), uv01 = new Vector2(t0 * r, len), uv11 = new Vector2(t1 * r, len);
                mb.Triangle(p0, q1, q0, n0, n1, n0, uv00, uv11, uv01, m);
                mb.Triangle(p0, p1, q1, n0, n1, n1, uv00, uv10, uv11, m);
                mb.Triangle(a, p1, p0, -axis, -axis, -axis, Vector2.zero, uv10, uv00, m);
                mb.Triangle(b, q0, q1, axis, axis, axis, Vector2.zero, uv01, uv11, m);
            }
        }
    }
}
