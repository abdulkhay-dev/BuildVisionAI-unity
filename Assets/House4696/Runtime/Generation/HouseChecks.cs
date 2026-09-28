using System.Collections.Generic;
using System.Linq;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Checks of the BUILT house — what the document validator cannot see: real item sizes, resolved wall heights,
    /// stairwells, roof surfaces. They catch the mistakes an author (an AI working blind through MCP) usually finds only
    /// in a render: furniture in walls or doorways, doors onto a drop, windows higher than their wall, openings inside
    /// a corner, roofs cutting through rooms, stairs arriving in a wall. Every message names the element and says what
    /// to change, with numbers.
    /// </summary>
    public static class HouseChecks
    {
        const float DoorClearance = 0.8f;   // free depth in front of a door on both sides
        const float PassHeight = 1.9f;

        public static List<Issue> Run(HouseContext c, List<ItemBox> items)
        {
            var list = new List<Issue>();
            void W(string p, string m) => list.Add(new Issue(IssueLevel.Warning, p, m));
            void E(string p, string m) => list.Add(new Issue(IssueLevel.Error, p, m));
            var doc = c.Doc;
            var walls = new List<WallFrame>(c.Walls);

            // ---------------------------------------------------------------- walls: closed outline
            foreach (var f in walls)
            {
                if (!f.Exterior) continue;
                foreach (bool atB in new[] { false, true })
                {
                    var end = atB ? f.WorldB : f.WorldA;
                    var p = new Vector2(end.x, end.z);
                    float best = float.MaxValue; string near = null;
                    bool joined = false;
                    foreach (var g in walls)
                    {
                        if (g == f || !g.Exterior || !SameStorey(f, g)) continue;
                        foreach (var q in new[] { g.WorldA, g.WorldB })
                        {
                            float dq = (new Vector2(q.x, q.z) - p).magnitude;
                            if (dq < best) { best = dq; near = g.Def.Id; }
                        }
                        // T-junction or a wall ending on another wall's body
                        if (DistanceToBody(g, p) < 0.03f) joined = true;
                    }
                    if (joined || best < 0.03f) continue;
                    W($"walls/{f.Def.Id}", $"конец {(atB ? "b" : "a")} {Fmt(p)} не примыкает ни к одной наружной стене этажа" +
                        (near != null ? $" (ближайший конец — у стены '{near}' в {best:0.##} м)" : "") +
                        " — контур дома не замкнут: совмести точки или вызови house_exterior_walls по всему контуру");
                }
            }

            // partitions stopping just short of a wall are extended to it by HouseContext (no slit, no warning)

            // ---------------------------------------------------------------- openings
            foreach (var o in doc.Openings)
            {
                var f = c.Wall(o.Wall);
                if (f == null) continue;
                string path = $"openings/{o.Id}";
                float floor = f.Level.Elevation, top = floor + o.Sill + o.Height;
                bool door = o.Type == OpeningType.Door || o.Type == OpeningType.EntryDoor || o.Type == OpeningType.SolidDoor;
                if (top > f.Y1 + 0.01f)
                    E(path, $"верх проёма (отметка {top:0.##} м) выше верха стены '{f.Def.Id}' ({f.Y1:0.##} м): " +
                        (door && o.Sill > 0.05f ? "у двери sill должен быть 0 (сейчас " + o.Sill.ToString("0.##") + ")"
                                                : $"уменьши height до {Mathf.Max(0.3f, f.Y1 - 0.05f - floor - o.Sill):0.##} или sill"));
                else if (floor + o.Sill < f.Y0 - 0.01f)
                    E(path, $"низ проёма ({floor + o.Sill:0.##} м) ниже низа стены '{f.Def.Id}' ({f.Y0:0.##} м): sill отсчитывается от пола этажа '{f.Level.Id}'");
                if (door && o.Sill > 0.05f && top <= f.Y1 + 0.01f)
                    W(path, $"дверь висит на {o.Sill:0.##} м над полом этажа '{f.Level.Id}' — поставь sill: 0");
                // an opening inside a corner cuts into the body of the neighbouring wall
                if (f.Exterior)
                {
                    float t = CornerDepth(c, f, walls, atStart: true);
                    if (t > 0 && o.At < t - 0.02f)
                        W(path, $"проём начинается в {o.At:0.##} м от угла — там тело примыкающей стены (толщина {t:0.##}): at должен быть ≥ {t:0.##} (угловое окно — проёмы в обеих стенах до угла)");
                    t = CornerDepth(c, f, walls, atStart: false);
                    if (t > 0 && o.At + o.Width > f.Length - t + 0.02f)
                        W(path, $"проём заканчивается в {f.Length - o.At - o.Width:0.##} м от угла — там тело примыкающей стены (толщина {t:0.##}): at + width должно быть ≤ {f.Length - t:0.##} (угловое окно — проёмы в обеих стенах до угла)");
                }
                if (f.Exterior && IsPassage(o)) DoorToDrop(c, f, o, W);
            }

            // ---------------------------------------------------------------- items
            var blocked = new HashSet<string>();
            foreach (var it in items)
            {
                if (Skip(it)) continue;
                string path = $"items/{it.Id}";
                // openings covered by the item (a wardrobe in front of a window, a bed across a door, art over a door)
                foreach (var o in doc.Openings)
                {
                    var f = c.Wall(o.Wall);
                    if (f == null || it.Model == "drapes") continue;
                    float floor = f.Level.Elevation;
                    float s0 = f.SAt(o.At), s1 = s0 + o.Width, y0 = floor + o.Sill, y1 = y0 + o.Height;
                    var box = WallSpace(f, it);
                    bool hit = box.min.x < s1 - 0.03f && box.max.x > s0 + 0.03f &&
                               box.min.y < y1 - 0.03f && box.max.y > y0 + 0.03f &&
                               box.min.z < 0.06f && box.max.z > -f.T - 0.06f;
                    if (!hit) continue;
                    // a window is blocked only by something tall against it (a wardrobe), not by a sofa under the sill line
                    // of a floor-to-ceiling glazing; shower screens and tubs under bathroom windows are normal
                    bool passage = IsPassage(o);
                    float along = Mathf.Min(box.max.x, s1) - Mathf.Max(box.min.x, s0);
                    if (!passage)
                    {
                        float covered = Mathf.Min(box.max.y, y1) - Mathf.Max(box.min.y, y0);
                        if (covered < 0.4f * (y1 - y0) || along < 0.25f * o.Width || it.Category == "bath") continue;
                    }
                    else if (along < 0.1f) continue;
                    blocked.Add(it.Id + "|" + o.Id);
                    W(path, $"'{it.Model}' закрывает {Kind(o)} '{o.Id}' в стене '{f.Def.Id}' (проём {s0 - f.S0:0.##}–{s1 - f.S0:0.##} м от точки a, " +
                            $"высота {y0:0.##}–{y1:0.##} м) — сдвинь предмет вдоль стены или к другой стене");
                }
                // free space in front of doors
                foreach (var o in doc.Openings)
                {
                    var f = c.Wall(o.Wall);
                    if (f == null || !IsPassage(o) || blocked.Contains(it.Id + "|" + o.Id)) continue;
                    float floor = f.Level.Elevation;
                    if (it.Y1 < floor + 0.05f || it.Y0 > floor + PassHeight) continue;
                    float s0 = f.SAt(o.At), s1 = s0 + o.Width;
                    var box = WallSpace(f, it);
                    if (box.min.x > s1 - 0.05f || box.max.x < s0 + 0.05f) continue;
                    // cells of the item's real footprint inside the free zone on either side of the door
                    Vector2 Q(float s, float d) { var q = f.P(s, 0, d); return new Vector2(q.x, q.z); }
                    var zoneIn = Ccw(new[] { Q(s0 + 0.05f, -f.T - 0.02f), Q(s1 - 0.05f, -f.T - 0.02f), Q(s1 - 0.05f, -f.T - DoorClearance), Q(s0 + 0.05f, -f.T - DoorClearance) });
                    var zoneOut = Ccw(new[] { Q(s0 + 0.05f, 0.02f), Q(s1 - 0.05f, 0.02f), Q(s1 - 0.05f, DoorClearance), Q(s0 + 0.05f, DoorClearance) });
                    if (it.CellsIn(zoneIn) + it.CellsIn(zoneOut) < 3) continue;
                    W(path, $"'{it.Model}' стоит в проходе у двери '{o.Id}' (стена '{f.Def.Id}'): перед дверью нужно {DoorClearance:0.#} м свободного места — отодвинь предмет");
                }
                // bodies of walls
                foreach (var f in walls)
                {
                    if (it.Y1 < f.Y0 + 0.02f || it.Y0 > f.Y1 - 0.02f) continue;
                    var box = WallSpace(f, it);
                    if (box.max.x < f.S0 + 0.02f || box.min.x > f.S1 - 0.02f) continue;
                    if (box.max.z < -f.T + 0.02f || box.min.z > -0.02f) continue;
                    if (InOpening(c, f, box)) continue;
                    // push towards the side the item's centre is on
                    float mid = (box.min.z + box.max.z) * 0.5f;
                    bool roomSide = mid < -f.T * 0.5f;
                    float depth = roomSide ? box.max.z + f.T : -box.min.z;
                    // a few centimetres (a headboard on a partition's axis) do not show; 10 cm or poking through does
                    if (depth < Mathf.Min(0.1f, f.T - 0.02f)) continue;
                    var n = roomSide ? -f.N : f.N;
                    W(path, $"'{it.Model}' заходит в стену '{f.Def.Id}' на {depth * 100f:0} см — сдвинь на {depth + 0.01f:0.##} м в направлении [{n.x:0.##}, {n.z:0.##}]" +
                            $" (габарит предмета {it.Size.x:0.##}×{it.Size.z:0.##} м, см. house_catalog)");
                }
            }
            // items on top of each other
            for (int i = 0; i < items.Count; i++)
            for (int j = i + 1; j < items.Count; j++)
            {
                var a = items[i]; var b = items[j];
                // chairs go under tables and counters, appliances (washers, dishwashers) under worktops
                if (Skip(a) || Skip(b) || Small(a) || Small(b) || Pair(a, b, "seating", "tables") || Pair(a, b, "seating", "kitchen") ||
                    Pair(a, b, "utility", "kitchen")) continue;
                float yo = Mathf.Min(a.Y1, b.Y1) - Mathf.Max(a.Y0, b.Y0);
                if (yo < 0.2f) continue;
                if (!Polygon.BoundsOverlap(a.Footprint(), b.Footprint())) continue;
                float area = a.SharedCore(b);
                if (area < 0.04f || area < 0.25f * Mathf.Min(a.CoreArea, b.CoreArea)) continue;
                W($"items/{b.Id}", $"'{b.Model}' пересекается с '{a.Id}' ({a.Model}) на ~{area:0.##} м² — разнеси их (габариты {b.Size.x:0.##}×{b.Size.z:0.##} и {a.Size.x:0.##}×{a.Size.z:0.##} м)");
            }
            // items standing in the air on upper levels
            foreach (var it in items)
            {
                if (it.Def.Level == null || Skip(it)) continue;
                var L = c.Level(it.Def.Level);
                // things hung on walls or ceilings (art above a double-height space) do not need a floor
                if (c.IsLowest(L) || it.Y0 > L.Elevation + 0.3f) continue;
                var pc = it.PlanCenter;
                bool onFloor = doc.Rooms.Exists(r => r.Level == L.Id && r.Outline.Count >= 3 && Polygon.Contains(r.Outline, pc));
                if (onFloor) continue;
                bool onElement = doc.Elements.Exists(e => e.Type != ElementType.Railing && Mathf.Abs(Mathf.Max(e.Min.y, e.Max.y) - L.Elevation) < 0.3f &&
                    pc.x >= Mathf.Min(e.Min.x, e.Max.x) && pc.x <= Mathf.Max(e.Min.x, e.Max.x) && pc.y >= Mathf.Min(e.Min.z, e.Max.z) && pc.y <= Mathf.Max(e.Min.z, e.Max.z));
                if (onElement) continue;
                W($"items/{it.Id}", $"'{it.Model}' в точке {Fmt(pc)} не стоит ни в одной комнате этажа '{L.Id}' — под ним нет пола; проверь координаты или level");
                if (c.StairGeometries != null)
                    foreach (var g in c.StairGeometries)
                        if (g.To.Id == L.Id && g.InWell(pc)) { W($"items/{it.Id}", $"'{it.Model}' попал в проём лестницы '{g.Def.Id}'"); break; }
            }

            // ---------------------------------------------------------------- pools
            foreach (var pool in c.Pools)
            {
                string path = $"elements/{pool.Def.Id}";
                var cut = pool.Cut;
                foreach (var f in walls)
                {
                    if (f.Y1 < pool.Floor + 0.1f || f.Y0 > pool.Top - 0.05f) continue;
                    if (OverlapArea(cut, Body(f, -0.02f)) > 0.01f)
                    {
                        W(path, $"бассейн заходит в стену '{f.Def.Id}' — чаша со стенками (0.2 м) и бортом должна стоять отдельно: сдвинь min/max");
                        break;
                    }
                }
                foreach (var it in items)
                {
                    if (Skip(it)) continue;
                    var p = new Vector2(it.Position.x, it.Position.z);
                    if (it.Y0 < pool.Top + 0.3f && it.Y1 > pool.Floor && Polygon.Contains(cut, p))
                        W($"items/{it.Id}", $"'{it.Model}' стоит в бассейне '{pool.Def.Id}' (точка {Fmt(p)}) — перенеси на борт или террасу");
                }
                // the rim should sit on something: the ground, a deck or a floor around it
                bool onGround = Mathf.Abs(pool.Top) < 0.35f;
                bool onDeck = doc.Elements.Exists(e => (e.Type == ElementType.Platform || e.Type == ElementType.Box) &&
                    Mathf.Abs(Mathf.Max(e.Min.y, e.Max.y) - pool.Top) < 0.35f && Polygon.BoundsOverlap(
                        new[] { new Vector2(e.Min.x, e.Min.z), new Vector2(e.Max.x, e.Min.z), new Vector2(e.Max.x, e.Max.z), new Vector2(e.Min.x, e.Max.z) }, cut));
                bool onFloor = doc.Rooms.Exists(r => r.Outline.Count >= 3 && Mathf.Abs(c.Level(r.Level).Elevation - pool.Top) < 0.35f && Polygon.BoundsOverlap(r.Outline, cut));
                if (!onGround && !onDeck && !onFloor && pool.Top > 0.35f)
                    W(path, $"борт бассейна на {pool.Top:0.##} м, а вокруг ни террасы, ни пола на этой высоте — бассейн стоит на земле как бак. " +
                        "Опусти max.y до уровня земли/террасы или поставь вокруг platform с верхом на этой высоте");
            }

            // ---------------------------------------------------------------- roofs
            foreach (var r in doc.Roofs)
            {
                if (r.Outline == null || r.Outline.Count < 3) continue;
                string path = $"roofs/{r.Id}";
                float? walls0 = WallTopUnder(c, r);
                if (r.Base.HasValue && walls0.HasValue && Mathf.Abs(r.Base.Value - walls0.Value) > 0.25f)
                    W(path, $"base = {r.Base:0.##} м, а верх стен под крышей — {walls0:0.##} м: крыша {(r.Base > walls0 ? "висит над стенами" : "утоплена в стены")}. " +
                            $"Убери base (он посчитается по стенам) или задай {walls0:0.##}");
                float b = c.RoofBase(r);
                foreach (var room in doc.Rooms)
                {
                    if (room.Type == RoomType.Terrace || room.Outline.Count < 3) continue;
                    var L = c.Level(room.Level);
                    float floorY = L.Elevation, ceilY = floorY + (room.Height ?? L.Height);
                    float low = float.MaxValue; Vector2 at = default;
                    foreach (var p in Samples(room.Outline))
                    {
                        var u = RoofBuilder.UndersideAt(r, b, p);
                        if (u == null || u.Value < floorY + 0.3f || u.Value > ceilY - 0.1f) continue;
                        if (u.Value < low) { low = u.Value; at = p; }
                    }
                    if (low < float.MaxValue)
                        W(path, $"крыша проходит сквозь комнату '{room.Id}': в точке {Fmt(at)} низ крыши на {low:0.##} м, а потолок комнаты на {ceilY:0.##} м — " +
                                "уменьши свес (overhang) или контур крыши над этой комнатой, либо подними base");
                }
            }
            // before any roof exists this is the normal order of work, not a mistake: one reminder instead of one per room
            bool noRoofYet = doc.Roofs.Count == 0 && !doc.Elements.Exists(e => e.Type != ElementType.Railing && e.Type != ElementType.Pool);
            if (noRoofYet && doc.Rooms.Exists(r => r.Type != RoomType.Terrace))
                W("roofs", "крыши пока нет — добавь её (roof), когда стены и комнаты готовы; base указывать не нужно");
            foreach (var room in doc.Rooms)
            {
                if (noRoofYet || room.Type == RoomType.Terrace || room.Outline.Count < 3) continue;
                var L = c.Level(room.Level);
                float ceilY = L.Elevation + (room.Height ?? L.Height);
                // covered = a floor above, a slab element, a roof or the body of a wall above; the room counts as open
                // when over a fifth of its plan (0.5 m grid) is not covered — one sample point may land in a wall
                bool Covered(Vector2 pc)
                {
                    if (doc.Rooms.Exists(o => o != room && o.Outline.Count >= 3 && c.Level(o.Level).Elevation >= ceilY - 0.05f && Polygon.Contains(o.Outline, pc))) return true;
                    if (doc.Elements.Exists(e => e.Type != ElementType.Railing && e.Type != ElementType.Pool && Mathf.Min(e.Min.y, e.Max.y) >= ceilY - 0.3f &&
                            pc.x >= Mathf.Min(e.Min.x, e.Max.x) && pc.x <= Mathf.Max(e.Min.x, e.Max.x) && pc.y >= Mathf.Min(e.Min.z, e.Max.z) && pc.y <= Mathf.Max(e.Min.z, e.Max.z))) return true;
                    foreach (var r in doc.Roofs)
                    {
                        var u = RoofBuilder.UndersideAt(r, c.RoofBase(r), pc);
                        if (u != null && u.Value >= ceilY - 0.15f) return true;
                    }
                    return walls.Exists(w => w.Spans(ceilY + 0.2f) && w.DistanceTo(pc) < 0.01f);
                }
                int total = 0, open = 0; Vector2 firstOpen = default;
                foreach (var pc in Samples(room.Outline))
                {
                    total++;
                    if (Covered(pc)) continue;
                    if (open++ == 0) firstOpen = pc;
                }
                if (total > 0 && open > total * 0.2f)
                {
                    var pc = firstOpen;
                    W($"rooms/{room.Id}", $"над комнатой нет ни крыши, ни этажа выше (точка {Fmt(pc)}, потолок {ceilY:0.##} м) — добавь крышу (roof) над этим контуром");
                }
            }

            // open floor edges (stairwells, double-height rooms) get glass guards automatically: EdgeGuards

            // ---------------------------------------------------------------- stairs
            foreach (var g in c.StairGeometries)
            {
                string path = $"stairs/{g.Def.Id}";
                if (g.LowHeadroomTreads > 0)
                    W(path, $"над {g.LowHeadroomTreads} ступенями первого марша меньше {StairGeometry.Headroom:0} м до перекрытия — сдвинь лестницу, увеличь firstFlight или высоту этажа");
                var mid = (g.ArrivalA + g.ArrivalB) * 0.5f;
                var off = mid + g.ArrivalDir * 0.4f;
                float yTo = g.To.Elevation;
                bool floor = doc.Rooms.Exists(r => r.Level == g.To.Id && r.Outline.Count >= 3 && Polygon.Contains(r.Outline, off));
                WallFrame hitWall = null;
                foreach (var f in walls)
                    if (f.Y0 < yTo + 1f && f.Y1 > yTo + 1f && DistanceToBody(f, off) < 0.05f) { hitWall = f; break; }
                if (hitWall != null)
                    W(path, $"лестница выходит в стену '{hitWall.Def.Id}' (точка схода {Fmt(off)} на этаже '{g.To.Id}') — поверни её (direction/turn) или сдвинь start");
                else if (!floor)
                    W(path, $"сход с лестницы {Fmt(off)} не попадает ни в одну комнату этажа '{g.To.Id}' — поверни её (direction/turn) или сдвинь start");
                foreach (var f in walls)
                {
                    if (f.Y1 < g.From.Elevation + 0.5f || f.Y0 > g.To.Elevation - 0.5f) continue;
                    var body = Body(f, -0.03f);
                    foreach (var rect in g.Footprint)
                        if (OverlapArea(rect, body) > 0.02f)
                        {
                            W(path, $"марш пересекает стену '{f.Def.Id}' — габарит лестницы см. в house_inspect (stairs.footprint), сдвинь start или уменьши width");
                            goto nextStair;
                        }
                }
                nextStair:;
            }
            return list;
        }

        // ------------------------------------------------------------------ helpers
        static string Fmt(Vector2 p) => $"[{p.x:0.##}, {p.y:0.##}]";

        static string Kind(OpeningDef o) =>
            o.Type == OpeningType.Window ? "окно" : o.Type == OpeningType.Glazing ? "витраж" : o.Type == OpeningType.Hole ? "проём" : "дверь";

        /// <summary>A door or an empty doorway people walk through (fixed glazing down to the floor is not one).</summary>
        public static bool IsPassage(OpeningDef o) =>
            o.Type == OpeningType.Door || o.Type == OpeningType.EntryDoor || o.Type == OpeningType.SolidDoor ||
            o.Type == OpeningType.Hole && o.Sill < 0.15f && o.Height >= PassHeight;

        static bool SameStorey(WallFrame a, WallFrame b) => a.SameStorey(b);

        /// <summary>Rugs, curtains and hanging fittings do not block anything.</summary>
        static bool Skip(ItemBox it) =>
            it.Model == "rug" || it.Model == "drapes" || it.Size.y < 0.05f || it.Size.x * it.Size.z < 1e-4f ||
            it.Category == "lighting" && it.Y0 > it.FloorY + 1.2f;

        /// <summary>Decor that sits on furniture (vases, books, lamps).</summary>
        static bool Small(ItemBox it) =>
            it.Category == "decor" && it.Size.x * it.Size.z < 0.25f || it.Category == "lighting" || it.Y0 > it.FloorY + 0.3f;

        static bool Pair(ItemBox a, ItemBox b, string c1, string c2) =>
            a.Category == c1 && b.Category == c2 || a.Category == c2 && b.Category == c1;

        /// <summary>Axis-aligned box of the item in wall space: x = s along the wall, y = height, z = d outward from the outer face.</summary>
        static Bounds WallSpace(WallFrame f, ItemBox it)
        {
            var rot = Quaternion.Euler(0, it.Yaw, 0);
            float o = Vector3.Dot(f.O, f.N);
            var b = new Bounds();
            for (int i = 0; i < 8; i++)
            {
                var lc = it.Solid.center + Vector3.Scale(it.Solid.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                var w = it.Position + rot * lc;
                var p = new Vector3(Vector3.Dot(w, f.A), w.y, Vector3.Dot(w, f.N) - o);
                if (i == 0) b = new Bounds(p, Vector3.zero); else b.Encapsulate(p);
            }
            return b;
        }

        /// <summary>Is the part of the item that overlaps the wall inside one of its openings?</summary>
        static bool InOpening(HouseContext c, WallFrame f, Bounds box)
        {
            foreach (var o in c.Doc.Openings)
            {
                if (o.Wall != f.Def.Id) continue;
                float s0 = f.SAt(o.At), y0 = f.Level.Elevation + o.Sill;
                if (box.min.x >= s0 - 0.02f && box.max.x <= s0 + o.Width + 0.02f && box.min.y >= y0 - 0.02f && box.max.y <= y0 + o.Height + 0.02f) return true;
            }
            return false;
        }

        static Vector2[] Body(WallFrame f, float grow = 0f) => f.PlanBody(grow);

        static float DistanceToBody(WallFrame f, Vector2 p) => f.DistanceTo(p);

        /// <summary>Thickness of the exterior wall that meets this one at its start/end corner (0 = free end or no corner).</summary>
        public static float CornerDepth(HouseContext c, WallFrame f, List<WallFrame> walls, bool atStart)
        {
            var end = atStart ? f.WorldA : f.WorldB;
            foreach (var g in walls)
            {
                if (g == f || !g.Exterior || !SameStorey(f, g)) continue;
                var q = atStart ? g.WorldB : g.WorldA;
                if ((q - end).sqrMagnitude > 0.0025f) continue;
                // only a turn makes a corner (a collinear continuation does not)
                if (Mathf.Abs(Vector3.Dot(g.A, f.A)) > 0.9f) continue;
                // convex corner: the neighbour's body lies inside this wall's run; a concave one lies outside the house
                bool convex = Vector3.Cross(atStart ? g.A : f.A, atStart ? f.A : g.A).y < 0;
                if (!convex) return 0f;
                // the neighbour's inner face meets this wall's inner face T·tan(θ/2) from the corner (θ = turn angle)
                float depth = g.T * Mathf.Tan(Vector3.Angle(g.A, f.A) * 0.5f * Mathf.Deg2Rad);
                // a corner window: the neighbour is open right up to the same corner
                float glen = g.Length;
                bool cornerWindow = c.Doc.Openings.Exists(o => o.Wall == g.Def.Id && (atStart ? o.At + o.Width > glen - f.T - 0.05f : o.At < f.T + 0.05f));
                return cornerWindow ? 0f : depth;
            }
            return 0f;
        }

        static float? WallTopUnder(HouseContext c, RoofDef r)
        {
            var saved = r.Base;
            r.Base = null;
            float auto = c.RoofBase(r);
            r.Base = saved;
            return c.WallsUnder(r).Count > 0 ? auto : (float?)null;
        }

        /// <summary>A door or floor-level glazing in an exterior wall: what is outside it, and how far down?</summary>
        static void DoorToDrop(HouseContext c, WallFrame f, OpeningDef o, System.Action<string, string> warn)
        {
            float floor = f.Level.Elevation + o.Sill;
            var outer = f.P(f.SAt(o.At + o.Width * 0.5f), 0, 0.6f);
            var p = new Vector2(outer.x, outer.z);
            float support = 0f;
            string by = "земля";
            foreach (var e in c.Doc.Elements)
            {
                if (e.Type == ElementType.Railing || e.Type == ElementType.Pool) continue;
                float top = Mathf.Max(e.Min.y, e.Max.y);
                if (top > floor + 0.05f || top <= support) continue;
                if (p.x < Mathf.Min(e.Min.x, e.Max.x) || p.x > Mathf.Max(e.Min.x, e.Max.x) || p.y < Mathf.Min(e.Min.z, e.Max.z) || p.y > Mathf.Max(e.Min.z, e.Max.z)) continue;
                support = top; by = $"элемент '{e.Id}'";
            }
            foreach (var r in c.Doc.Rooms)
            {
                if (r.Outline.Count < 3 || !Polygon.Contains(r.Outline, p)) continue;
                float y = c.Level(r.Level).Elevation;
                if (y > floor + 0.05f || y <= support) continue;
                support = y; by = $"комната '{r.Id}'";
            }
            foreach (var r in c.Doc.Roofs)
            {
                if (r.Type != RoofType.Flat) continue;
                var u = RoofBuilder.UndersideAt(r, c.RoofBase(r), p);
                if (u == null) continue;
                float y = u.Value + r.Thickness;
                if (y > floor + 0.05f || y <= support) continue;
                support = y; by = $"плоская крыша '{r.Id}'";
            }
            float drop = floor - support;
            bool lowest = c.IsLowest(f.Level);
            if (drop > 0.6f || !lowest && drop > 0.3f)
                warn($"openings/{o.Id}", $"{Kind(o)} в наружной стене '{f.Def.Id}' выходит на высоте {drop:0.##} м над опорой ({by}) — снаружи обрыв. " +
                    $"Добавь балкон/террасу (element platform с верхом на {floor:0.##} м перед проёмом) или ступени, либо сделай окно с подоконником (sill ≥ 0.9)");
            else if (drop > 0.45f)
                warn($"openings/{o.Id}", $"перед {Kind(o)} '{o.Id}' перепад {drop:0.##} м до земли — добавь крыльцо/ступени (element box ступенями по ~0.17 м)");
        }

        static Vector2[] Ccw(Vector2[] p) => Polygon.SignedArea(p) < 0 ? new[] { p[3], p[2], p[1], p[0] } : p;

        /// <summary>Area of the intersection of two convex counter-clockwise polygons.</summary>
        public static float OverlapArea(IList<Vector2> a, IList<Vector2> b)
        {
            var poly = new List<Vector2>(a);
            for (int i = 0; i < b.Count && poly.Count >= 3; i++) poly = Polygon.ClipLeft(poly, b[i], b[(i + 1) % b.Count]);
            return poly.Count >= 3 ? Mathf.Abs(Polygon.SignedArea(poly)) : 0f;
        }

        /// <summary>Grid of plan points (0.5 m) inside an outline, plus its vertices pulled 0.3 m towards the centroid.</summary>
        static IEnumerable<Vector2> Samples(IList<Vector2> outline)
        {
            var b = Polygon.Bounds(outline);
            for (float x = b.xMin + 0.25f; x < b.xMax; x += 0.5f)
            for (float z = b.yMin + 0.25f; z < b.yMax; z += 0.5f)
            {
                var p = new Vector2(x, z);
                if (Polygon.Contains(outline, p)) yield return p;
            }
            var cen = Polygon.Centroid(outline);
            foreach (var v in outline)
            {
                var d = cen - v;
                var p = v + d.normalized * Mathf.Min(0.3f, d.magnitude * 0.5f);
                if (Polygon.Contains(outline, p)) yield return p;
            }
        }
    }
}
