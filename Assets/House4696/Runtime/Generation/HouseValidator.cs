using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    public enum IssueLevel { Error, Warning }

    public readonly struct Issue
    {
        public readonly IssueLevel Level;
        public readonly string Path, Message;
        public Issue(IssueLevel level, string path, string message) { Level = level; Path = path; Message = message; }
        public override string ToString() => $"{(Level == IssueLevel.Error ? "ОШИБКА" : "предупреждение")} [{Path}]: {Message}";
    }

    /// <summary>
    /// Static checks of a house document before generation. Messages are meant for the author (usually an AI via
    /// MCP): they name the element and say what to change. Errors make the house unbuildable or clearly wrong;
    /// warnings flag likely mistakes.
    /// </summary>
    public static class HouseValidator
    {
        public static List<Issue> Validate(HouseDocument d)
        {
            var list = new List<Issue>();
            void E(string p, string m) => list.Add(new Issue(IssueLevel.Error, p, m));
            void W(string p, string m) => list.Add(new Issue(IssueLevel.Warning, p, m));

            if (d.Format != HouseDocument.CurrentFormat) W("format", $"ожидается \"{HouseDocument.CurrentFormat}\", указано \"{d.Format}\"");

            // ---------------- levels
            var levels = new Dictionary<string, LevelDef>();
            if (d.Levels.Count == 0) E("levels", "нужен хотя бы один этаж");
            foreach (var l in d.Levels)
            {
                if (string.IsNullOrEmpty(l.Id)) { E("levels", "у этажа нет id"); continue; }
                if (!levels.TryAdd(l.Id, l)) E($"levels/{l.Id}", "повторяющийся id этажа");
                if (l.Height < 2.0f || l.Height > 12f) W($"levels/{l.Id}", $"необычная высота этажа {l.Height:0.##} м (обычно 2.5–3.5)");
            }
            var sorted = new List<LevelDef>(d.Levels);
            sorted.Sort((a, b) => a.Elevation.CompareTo(b.Elevation));
            for (int i = 0; i + 1 < sorted.Count; i++)
            {
                var a = sorted[i]; var b = sorted[i + 1];
                float gap = b.Elevation - b.Slab - (a.Elevation + a.Height);
                if (gap < -0.01f) E($"levels/{b.Id}", $"перекрытие ({b.Slab:0.##} м) пересекается с потолком этажа '{a.Id}': подними отметку или уменьши высоту на {-gap:0.##} м");
            }
            bool Lvl(string id, string path, bool required = true)
            {
                if (string.IsNullOrEmpty(id)) { if (required) E(path, "не указан этаж (level)"); return !required; }
                if (!levels.ContainsKey(id)) { E(path, $"нет этажа '{id}'"); return false; }
                return true;
            }

            // ---------------- walls & openings
            var walls = new Dictionary<string, WallDef>();
            foreach (var w in d.Walls)
            {
                string p = $"walls/{w.Id}";
                if (string.IsNullOrEmpty(w.Id)) { E("walls", "у стены нет id"); continue; }
                if (!walls.TryAdd(w.Id, w)) E(p, "повторяющийся id стены");
                Lvl(w.Level, p);
                float len = (w.B - w.A).magnitude;
                if (len < 0.1f) E(p, "стена короче 10 см — проверь точки a и b");
                if (w.Thickness.HasValue && (w.Thickness < 0.05f || w.Thickness > 1f)) W(p, $"необычная толщина {w.Thickness:0.##} м");
                if (w.Bottom.HasValue && w.Top.HasValue && w.Top <= w.Bottom) E(p, "top должен быть выше bottom");
                foreach (var z in w.Zones)
                    if (z.To <= z.From || z.Top <= z.Bottom) W(p, $"пустая зона отделки '{z.Finish}'");
            }
            var byWall = new Dictionary<string, List<OpeningDef>>();
            foreach (var o in d.Openings)
            {
                string p = $"openings/{o.Id}";
                if (!walls.TryGetValue(o.Wall ?? "", out var w)) { E(p, $"нет стены '{o.Wall}'"); continue; }
                float len = (w.B - w.A).magnitude;
                if (o.Width <= 0.1f || o.Height <= 0.1f) E(p, "ширина и высота проёма должны быть больше 10 см");
                if (o.At < -0.01f || o.At + o.Width > len + 0.01f)
                    E(p, $"проём выходит за стену '{w.Id}' длиной {len:0.##} м (at {o.At:0.##} + width {o.Width:0.##})");
                bool isDoor = o.Type == OpeningType.Door || o.Type == OpeningType.EntryDoor || o.Type == OpeningType.SolidDoor;
                if (isDoor && o.Height < 1.9f) W(p, $"дверь ниже 1.9 м ({o.Height:0.##})");
                if (!byWall.TryGetValue(o.Wall, out var ol)) byWall[o.Wall] = ol = new List<OpeningDef>();
                ol.Add(o);
            }
            foreach (var kv in byWall)
            {
                var ol = kv.Value;
                for (int i = 0; i < ol.Count; i++)
                for (int j = i + 1; j < ol.Count; j++)
                {
                    var a = ol[i]; var b = ol[j];
                    bool sOverlap = a.At < b.At + b.Width - 0.01f && b.At < a.At + a.Width - 0.01f;
                    bool yOverlap = a.Sill < b.Sill + b.Height - 0.01f && b.Sill < a.Sill + a.Height - 0.01f;
                    if (sOverlap && yOverlap) E($"openings/{b.Id}", $"пересекается с проёмом '{a.Id}' в стене '{kv.Key}'");
                }
            }

            // ---------------- rooms
            var roomIds = new HashSet<string>();
            foreach (var r in d.Rooms)
            {
                string p = $"rooms/{r.Id}";
                if (string.IsNullOrEmpty(r.Id)) { E("rooms", "у комнаты нет id"); continue; }
                if (!roomIds.Add(r.Id)) E(p, "повторяющийся id комнаты");
                Lvl(r.Level, p);
                if (r.Outline.Count < 3) { E(p, "контур комнаты — минимум 3 точки"); continue; }
                float area = Mathf.Abs(Polygon.SignedArea(r.Outline));
                if (area < 1f) W(p, $"площадь {area:0.##} м² — слишком маленькая комната");
                if (SelfIntersects(r.Outline)) E(p, "контур самопересекается — точки должны идти по периметру по порядку");
            }
            for (int i = 0; i < d.Rooms.Count; i++)
            for (int j = i + 1; j < d.Rooms.Count; j++)
            {
                var a = d.Rooms[i]; var b = d.Rooms[j];
                if (a.Level != b.Level || a.Outline.Count < 3 || b.Outline.Count < 3) continue;
                float ov = OverlapArea(a.Outline, b.Outline);
                if (ov > 0.25f) E($"rooms/{b.Id}", $"перекрывается с комнатой '{a.Id}' (~{ov:0.#} м²): полы наложатся друг на друга");
            }

            // ---------------- roofs, stairs, elements
            foreach (var r in d.Roofs)
            {
                string p = $"roofs/{r.Id}";
                if (r.Outline.Count < 3) E(p, "контур крыши — минимум 3 точки");
                if (r.Type != RoofType.Flat && (r.Pitch < 5f || r.Pitch > 60f)) W(p, $"уклон {r.Pitch:0}° вне обычного диапазона 5–60°");
            }
            foreach (var s in d.Stairs)
            {
                string p = $"stairs/{s.Id}";
                if (!Lvl(s.From, p)) continue;
                if (s.To != null) Lvl(s.To, p);
                if (s.Width < 0.7f) W(p, $"ширина марша {s.Width:0.##} м — меньше 0.7 м");
                if (s.Going < 0.22f || s.Going > 0.35f) W(p, $"проступь {s.Going:0.##} м вне 0.22–0.35");
                // the upper level must leave an opening wherever a tread has less than 2 m headroom
                var toId = s.To ?? NextLevel(sorted, s.From);
                if (toId == null || !levels.TryGetValue(toId, out var toL)) continue;
                var fromL = levels[s.From];
                float H = toL.Elevation - fromL.Elevation, clear = H - toL.Slab - 2.0f;
                int n = Mathf.Max(3, s.Risers ?? Mathf.RoundToInt(H / 0.175f));
                float rise = H / n;
                int k = s.Type == StairType.Straight ? n : Mathf.Clamp(s.FirstFlight ?? n / 2 + 1, 2, n - 2);
                float side = s.Turn != "right" ? -1f : 1f;
                var rot = Quaternion.Euler(0, s.Direction, 0);
                var probes = new List<Vector2>();
                for (int i = 1; i < k; i++)
                    if (i * rise > clear) probes.Add(new Vector2(0, (i - 0.5f) * s.Going));
                if (s.Type == StairType.U)
                    for (int j = 1; j < n - k; j++)
                        if ((k + j) * rise > clear) probes.Add(new Vector2(side * (s.Width + s.Gap), (k - 1) * s.Going - (j - 0.5f) * s.Going));
                string hit = null;
                foreach (var q in probes)
                {
                    var wpt = rot * new Vector3(q.x, 0, q.y);
                    var pt = s.Start + new Vector2(wpt.x, wpt.z);
                    foreach (var r in d.Rooms)
                        if (r.Level == toId && r.Outline.Count >= 3 && Polygon.Contains(r.Outline, pt)) { hit = r.Id; break; }
                    if (hit != null) break;
                }
                if (hit != null)
                    W(p, $"над лестницей меньше 2 м до перекрытия: пол комнаты '{hit}' этажа '{toId}' накрывает марш — вырежи проём в её контуре");
            }
            foreach (var e in d.Elements)
                if (e.Type == ElementType.Railing && e.Path.Count < 2) E($"elements/{e.Id}", "ограждению нужен путь из 2+ точек");

            // ---------------- items, lights, views
            var itemIds = new HashSet<string>();
            foreach (var it in d.Items)
            {
                string p = $"items/{it.Id}";
                if (!string.IsNullOrEmpty(it.Id) && !itemIds.Add(it.Id)) E(p, "повторяющийся id предмета");
                if (ItemCatalog.Get(it.Model) == null) E(p, $"нет модели '{it.Model}' в каталоге");
                if (it.Level != null) Lvl(it.Level, p);
                if (it.Room != null && !roomIds.Contains(it.Room)) W(p, $"нет комнаты '{it.Room}'");
            }
            foreach (var l in d.Lights)
                if (l.Level != null) Lvl(l.Level, $"lights/{l.Id}");
            return list;
        }

        static string NextLevel(List<LevelDef> sorted, string id)
        {
            int i = sorted.FindIndex(l => l.Id == id);
            return i >= 0 && i + 1 < sorted.Count ? sorted[i + 1].Id : null;
        }

        static bool SelfIntersects(IList<Vector2> p)
        {
            int n = p.Count;
            for (int i = 0; i < n; i++)
            for (int j = i + 2; j < n; j++)
            {
                if (i == 0 && j == n - 1) continue;
                if (SegmentsCross(p[i], p[(i + 1) % n], p[j], p[(j + 1) % n])) return true;
            }
            return false;
        }

        static bool SegmentsCross(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
        {
            float Cr(Vector2 o, Vector2 u, Vector2 v) => (u.x - o.x) * (v.y - o.y) - (u.y - o.y) * (v.x - o.x);
            float d1 = Cr(c, d, a), d2 = Cr(c, d, b), d3 = Cr(a, b, c), d4 = Cr(a, b, d);
            return d1 * d2 < -1e-6f && d3 * d4 < -1e-6f;
        }

        /// <summary>Approximate overlap area of two polygons by sampling their common bounding box on a 10 cm grid.</summary>
        static float OverlapArea(IList<Vector2> a, IList<Vector2> b)
        {
            var ra = Polygon.Bounds(a); var rb = Polygon.Bounds(b);
            float x0 = Mathf.Max(ra.xMin, rb.xMin), x1 = Mathf.Min(ra.xMax, rb.xMax);
            float z0 = Mathf.Max(ra.yMin, rb.yMin), z1 = Mathf.Min(ra.yMax, rb.yMax);
            if (x1 - x0 < 0.2f || z1 - z0 < 0.2f) return 0f;
            const float step = 0.1f;
            int hits = 0;
            for (float x = x0 + step * 0.5f; x < x1; x += step)
            for (float z = z0 + step * 0.5f; z < z1; z += step)
            {
                var q = new Vector2(x, z);
                if (Polygon.Contains(a, q) && Polygon.Contains(b, q)) hits++;
            }
            return hits * step * step;
        }
    }
}
