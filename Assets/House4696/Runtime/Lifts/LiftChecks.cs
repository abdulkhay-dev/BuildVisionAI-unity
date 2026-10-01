using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>
    /// Checks of the built lifts: the shaft through walls, stairs or furniture, landing doors facing a wall or nothing,
    /// the shaft outside the building. Every message names the lift and what to move, with numbers.
    /// </summary>
    public static class LiftChecks
    {
        /// <summary>Free depth in front of the landing doors (a wheelchair turns, a stretcher is wheeled in).</summary>
        const float Landing = 1.5f;

        public static List<Issue> Run(HouseContext c, List<ItemBox> items)
        {
            var list = new List<Issue>();
            void W(string p, string m) => list.Add(new Issue(IssueLevel.Warning, p, m));
            foreach (var g in c.Lifts)
            {
                string path = $"lifts/{g.Def.Id}";
                var foot = g.Footprint;
                string Pt(Vector2 v) => $"[{v.x:0.##}, {v.y:0.##}]";
                // walls of the document inside the shaft (an author-walled shaft: inside its clear area)
                var body = g.Enclosure == "none" ? g.Clear : foot;
                foreach (var f in c.Walls)
                {
                    if (f.Y1 < g.PitBottom + 0.1f || f.Y0 > g.Top - 0.1f) continue;
                    if (Overlap(f.PlanBody(-0.02f), body) > 0.01f)
                    {
                        W(path, $"шахта лифта пересекает стену '{f.Def.Id}' на этаже '{f.Level.Id}' — " +
                                (g.Enclosure == "none" ? "внутри шахты не должно быть стен" : "шахта строится со своими стенами: убери эту стену или сдвинь лифт (position)") +
                                $" (шахта {g.W + 2 * g.T:0.##}×{g.D + 2 * g.T:0.##} м, см. house_inspect lifts)");
                        break;
                    }
                }
                foreach (var s in c.StairGeometries)
                {
                    if (s.To.Elevation < g.PitBottom || s.From.Elevation > g.Top) continue;
                    foreach (var r in s.Footprint)
                        if (Overlap(r, foot) > 0.01f) { W(path, $"шахта лифта пересекает лестницу '{s.Def.Id}' — сдвинь лифт или лестницу"); goto stairsDone; }
                }
                stairsDone:
                foreach (var it in items)
                {
                    if (it.Cells == null || it.Y1 < g.PitBottom || it.Y0 > g.Top) continue;
                    int n = 0;
                    foreach (var key in it.Cells)
                    {
                        var p = new Vector2(((int)(key >> 32) + 0.5f) * ItemBox.Cell, ((int)(uint)(key & 0xffffffffL) + 0.5f) * ItemBox.Cell);
                        if (Polygon.Contains(foot, p) && ++n > 3) break;
                    }
                    if (n > 3) W(path, $"предмет '{it.Id}' стоит в шахте лифта — передвинь его");
                }
                // at every stop: a room in front of the doors, no wall across them (one message for all the storeys)
                var walled = new List<string>(); var bare = new List<string>(); string wallId = null;
                foreach (var L in g.Stops)
                {
                    var front = g.Landing(0.6f);
                    bool room = c.Doc.Rooms.Exists(r => c.Level(r.Level) == L && r.Outline != null && r.Outline.Count >= 3 && Polygon.Contains(r.Outline, front));
                    WallFrame across = null;
                    foreach (var f in c.Walls)
                    {
                        if (!f.Spans(L.Elevation + 1f)) continue;
                        for (float d = 0.1f; d <= Landing; d += 0.1f)
                            if (f.DistanceTo(g.Landing(d)) < f.T * 0.5f) { across = f; break; }
                        if (across != null) break;
                    }
                    if (across != null) { walled.Add(L.Id); wallId ??= across.Def.Id; }
                    else if (!room) bare.Add(L.Id);
                }
                if (walled.Count > 0)
                    W(path, $"перед дверями лифта стена ближе {Landing} м (этажи {string.Join(", ", walled)}; стена '{wallId}') — двери должны выходить в холл: поверни лифт (rotation) или сдвинь его");
                if (bare.Count > 0)
                    W(path, $"перед дверями лифта ({Pt(g.Landing(0.6f))}) нет помещения на этажах {string.Join(", ", bare)} — поставь двери в холл или коридор (position — середина дверей на передней грани шахты, rotation — куда они смотрят)");
                // the shaft must stand inside the building on every storey it serves
                foreach (var L in g.Stops)
                {
                    var outline = c.Outline(L);
                    if (outline == null) continue;
                    int outside = 0;
                    foreach (var q in foot) if (!Polygon.Contains(outline, q)) outside++;
                    if (outside > foot.Length / 2)
                    {
                        W(path, $"шахта лифта выходит за наружные стены этажа '{L.Id}' — сдвинь лифт внутрь здания (или сделай его панорамным снаружи: shaft \"glass\")");
                        break;
                    }
                }
            }
            return list;
        }

        /// <summary>Approximate overlap area of two convex-ish plan polygons (5 cm sampling of the first one's box).</summary>
        static float Overlap(IList<Vector2> a, IList<Vector2> b)
        {
            var ra = Polygon.Bounds(a); var rb = Polygon.Bounds(b);
            if (!ra.Overlaps(rb)) return 0f;
            float x0 = Mathf.Max(ra.xMin, rb.xMin), x1 = Mathf.Min(ra.xMax, rb.xMax), z0 = Mathf.Max(ra.yMin, rb.yMin), z1 = Mathf.Min(ra.yMax, rb.yMax);
            const float step = 0.05f;
            int hit = 0;
            for (float x = x0 + step * 0.5f; x < x1; x += step)
            for (float z = z0 + step * 0.5f; z < z1; z += step)
            {
                var p = new Vector2(x, z);
                if (Polygon.Contains(a, p) && Polygon.Contains(b, p)) hit++;
            }
            return hit * step * step;
        }
    }
}
