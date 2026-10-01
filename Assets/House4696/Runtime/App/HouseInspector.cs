using System;
using System.Collections.Generic;
using System.Linq;
using House4696.Generation;
using House4696.Model;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Numbers of the BUILT house for an AI that cannot measure a render: resolved wall heights, openings in plan and
    /// in absolute heights, roof eaves and ridges, stair footprints and stairwells, real item sizes and footprints.
    /// Everything absolute (metres, Y = height above ground), plan points [x, z].
    /// </summary>
    public static class HouseInspector
    {
        public static readonly string[] Sections = { "levels", "walls", "rooms", "roofs", "stairs", "items", "elements" };

        public static JObject Inspect(HouseBuildResult r, string section, string id)
        {
            var c = r?.Context ?? throw new InvalidOperationException("дом ещё не построен");
            if (section != null && !Sections.Contains(section))
                throw new ArgumentException($"section: {string.Join(", ", Sections)} (или не указывать — всё)");
            var o = new JObject();
            bool Want(string s) => section == null || section == s;
            bool Pick(string elementId) => id == null || string.Equals(id, elementId, StringComparison.OrdinalIgnoreCase);

            if (Want("levels"))
                o["levels"] = new JArray(c.Doc.Levels.Where(l => Pick(l.Id)).Select(l => new JObject
                {
                    ["id"] = l.Id, ["floor"] = R(l.Elevation), ["ceiling"] = R(l.Elevation + l.Height), ["slabBelow"] = R(l.Slab),
                    ["structureAbove"] = R(c.TopOfLevel(l)),
                }));
            if (Want("walls"))
                o["walls"] = new JArray(c.Walls.Where(f => Pick(f.Def.Id)).Select(f => Wall(c, f)));
            if (Want("rooms"))
                o["rooms"] = new JArray(c.Doc.Rooms.Where(x => Pick(x.Id) && x.Outline.Count >= 3).Select(x =>
                {
                    var L = c.Level(x.Level);
                    var b = Polygon.Bounds(x.Outline);
                    return new JObject
                    {
                        ["id"] = x.Id, ["level"] = L.Id, ["type"] = x.Type.ToString().ToLowerInvariant(),
                        ["area"] = R(Mathf.Abs(Polygon.SignedArea(x.Outline))), ["min"] = P(b.min), ["max"] = P(b.max),
                        ["floor"] = R(L.Elevation), ["ceiling"] = R(L.Elevation + (x.Height ?? L.Height)),
                    };
                }));
            if (Want("roofs"))
                o["roofs"] = new JArray(c.Doc.Roofs.Where(x => Pick(x.Id) && x.Outline.Count >= 3).Select(x =>
                {
                    float b = c.RoofBase(x);
                    var sh = RoofBuilder.Describe(x, b);
                    var j = new JObject
                    {
                        ["id"] = x.Id, ["type"] = x.Type.ToString().ToLowerInvariant(), ["base"] = R(b), ["baseAuto"] = !x.Base.HasValue,
                        ["eave"] = R(sh.Eave), ["ridge"] = R(sh.Ridge), ["overhang"] = R(x.Overhang),
                    };
                    if (sh.HighSide.HasValue) j["risesTowards"] = Compass(sh.HighSide.Value);
                    if (x.Type == RoofType.Gable || x.Type == RoofType.Hip) j["ridgeAlong"] = Compass(x.Rotation + 90f) + "–" + Compass(x.Rotation + 270f);
                    return j;
                }));
            if (Want("stairs"))
                o["stairs"] = new JArray(c.Doc.Stairs.Where(s => Pick(s.Id)).Select(s =>
                {
                    var g = c.Stair(s);
                    if (g == null) return new JObject { ["id"] = s.Id, ["error"] = "этажи лестницы не заданы или верхний не выше нижнего" };
                    return new JObject
                    {
                        ["id"] = s.Id, ["from"] = g.From.Id, ["to"] = g.To.Id, ["risers"] = g.Risers, ["rise"] = R(g.Rise), ["going"] = R(s.Going),
                        ["firstFlight"] = g.FirstFlight, ["footprint"] = new JArray(g.Footprint.Select(Poly)),
                        ["well"] = new JArray(g.Well.Select(Poly)), ["wellMode"] = s.Well,
                        ["arrival"] = new JObject { ["from"] = P(g.ArrivalA), ["to"] = P(g.ArrivalB), ["walkTowards"] = Compass(Mathf.Atan2(g.ArrivalDir.x, g.ArrivalDir.y) * Mathf.Rad2Deg) },
                    };
                }));
            if (Want("lifts"))
                o["lifts"] = new JArray(c.Lifts.Where(g => Pick(g.Def.Id)).Select(g => new JObject
                {
                    ["id"] = g.Def.Id, ["model"] = g.Spec.Model.Id, ["load"] = g.Spec.Row.Load, ["speed"] = g.Spec.Speed,
                    ["stops"] = new JArray(g.Stops.Select(l => l.Id)), ["parked"] = g.Parked.Id,
                    ["shaftClear"] = new JArray(g.Clear.Select(P)), ["footprint"] = new JArray(g.Footprint.Select(P)),
                    ["car"] = new JArray(R(g.CarW), R(g.CarD), R(g.Spec.CarHeight)), ["door"] = new JArray(R(g.Spec.DoorWidth), R(g.Spec.DoorHeight)),
                    ["doorType"] = g.Spec.DoorType, ["pitBottom"] = R(g.PitBottom), ["shaftTop"] = R(g.Top),
                    ["landing"] = P(g.Landing(0.75f)), ["doorsFace"] = Compass(g.Def.Rotation),
                    ["machineRoom"] = g.Spec.MachineRoom.HasValue ? new JArray(R(g.Spec.MachineRoom.Value.x), R(g.Spec.MachineRoom.Value.y), R(g.Spec.MachineHeight)) : null,
                }));
            if (Want("items"))
                o["items"] = new JArray(r.Items.Where(it => Pick(it.Id)).Select(it => new JObject
                {
                    ["id"] = it.Id, ["model"] = it.Model, ["level"] = it.Def.Level, ["rotation"] = R(it.Def.Rotation),
                    ["size"] = new JArray(R(it.Size.x), R(it.Size.z), R(it.Size.y)), ["y"] = new JArray(R(it.Y0), R(it.Y1)),
                    ["footprint"] = Poly(it.Footprint()),
                }));
            if (Want("elements"))
                o["elements"] = new JArray(c.Doc.Elements.Where(e => Pick(e.Id)).Select(e =>
                {
                    if (e.Type == ElementType.Railing)
                        return new JObject { ["id"] = e.Id, ["type"] = "railing", ["path"] = new JArray(e.Path.Select(P)), ["y"] = new JArray(R(e.Y), R(e.Y + e.Height)) };
                    if (e.Type == ElementType.Pool && c.Pools.FirstOrDefault(p => p.Def == e) is PoolShape pool)
                        return new JObject
                        {
                            ["id"] = e.Id, ["type"] = "pool", ["outline"] = new JArray(pool.Outline.Select(P)),
                            ["rim"] = R(pool.Top + 0.02f), ["water"] = R(pool.Water), ["floor"] = R(pool.Floor),
                            ["footprint"] = new JArray(pool.Grown(PoolShape.Coping, PoolBuilder.Pane).Select(P)),
                            ["glass"] = new JArray(pool.GlassEdges.OrderBy(i => i)),
                        };
                    return new JObject { ["id"] = e.Id, ["type"] = e.Type.ToString().ToLowerInvariant(), ["min"] = V(Vector3.Min(e.Min, e.Max)), ["max"] = V(Vector3.Max(e.Min, e.Max)) };
                }));
            o["note"] = "Всё в абсолютных метрах: Y — высота над землёй; точки плана [x, z]. size предмета = ширина (поперёк фасада) × глубина (вдоль rotation) × высота.";
            return o;
        }

        static JObject Wall(HouseContext c, WallFrame f)
        {
            var d = f.Def;
            var j = new JObject
            {
                ["id"] = d.Id, ["level"] = f.Level.Id, ["kind"] = d.Kind.ToString().ToLowerInvariant(),
                ["a"] = P(d.A), ["b"] = P(d.B), ["length"] = R((d.B - d.A).magnitude), ["thickness"] = R(f.T),
                ["bottom"] = R(f.Y0), ["top"] = R(f.Y1),
                // compass direction the wall's outer side looks to (exterior walls: the facade direction)
                ["faces"] = Compass(Mathf.Atan2(f.N.x, f.N.z) * Mathf.Rad2Deg),
            };
            if (d.Outside != null) j["outside"] = d.Outside;
            var ops = c.Doc.Openings.Where(op => op.Wall == d.Id).OrderBy(op => op.At).Select(op =>
            {
                float floor = f.Level.Elevation;
                // on the wall's own line a→b (the line the author gave), like "at"
                var dir = (d.B - d.A).normalized;
                var jo = new JObject
                {
                    ["id"] = op.Id, ["type"] = op.Type.ToString().ToLowerInvariant(), ["at"] = R(op.At), ["width"] = R(op.Width),
                    ["from"] = P(d.A + dir * op.At), ["to"] = P(d.A + dir * (op.At + op.Width)),
                    ["bottom"] = R(floor + op.Sill), ["top"] = R(floor + op.Sill + op.Height),
                };
                // a catalogue door: what was built (model, finish, glass, leaf) and how the block fits the wall
                if (House4696.Doors.DoorSizing.IsCatalogueDoor(op) && House4696.Doors.DoorCatalog.Resolve(op) is House4696.Doors.ResolvedDoor door)
                {
                    var leaf = House4696.Doors.DoorSizing.LeafOf(op);
                    jo["door"] = new JObject
                    {
                        ["model"] = door.Model.Id, ["name"] = door.Title, ["glass"] = door.Glass?.Id,
                        ["leaf"] = new JArray(R(leaf.x), R(leaf.y)),
                        ["standard"] = House4696.Doors.DoorSizing.IsStandard(leaf),
                        ["frame"] = "коробка 70 мм" + (f.T > House4696.Doors.DoorBlockBuilder.FrameDepth + 0.004f
                            ? $" + добор {Mathf.RoundToInt((f.T - House4696.Doors.DoorBlockBuilder.FrameDepth) * 1000)} мм" : ""),
                        ["opensTo"] = op.Swing >= 0 ? "влево от a→b" : "вправо от a→b",
                        ["hinges"] = op.Hinge == Hinge.Start ? "у a" : "у b",
                    };
                }
                return jo;
            }).ToList();
            if (ops.Count > 0) j["openings"] = new JArray(ops);
            // free stretches of the wall (room for new openings or furniture), from point a
            // corners: the first/last metres of an exterior wall are inside the neighbour's body
            var all = c.Walls.ToList();
            float c0 = f.Exterior ? HouseChecks.CornerDepth(c, f, all, true) : 0f, c1 = f.Exterior ? HouseChecks.CornerDepth(c, f, all, false) : 0f;
            var free = new List<JArray>();
            float cur = c0;
            foreach (var op in c.Doc.Openings.Where(op => op.Wall == d.Id).OrderBy(op => op.At))
            {
                if (op.At - cur > 0.3f) free.Add(new JArray(R(cur), R(op.At)));
                cur = Mathf.Max(cur, op.At + op.Width);
            }
            if (f.Length - c1 - cur > 0.3f) free.Add(new JArray(R(cur), R(f.Length - c1)));
            j["free"] = new JArray(free);
            return j;
        }

        static string Compass(float deg)
        {
            deg = Mathf.Repeat(deg, 360f);
            string[] names = { "север (+Z)", "северо-восток", "восток (+X)", "юго-восток", "юг (−Z)", "юго-запад", "запад (−X)", "северо-запад" };
            return $"{names[Mathf.RoundToInt(deg / 45f) % 8]}, {Mathf.RoundToInt(deg)}°";
        }

        static double R(float v) => Math.Round(v, 2);
        static JArray P(Vector2 p) => new JArray(R(p.x), R(p.y));
        static JArray V(Vector3 p) => new JArray(R(p.x), R(p.y), R(p.z));
        static JArray Poly(Vector2[] ps) => new JArray(ps.Select(P));
    }
}
