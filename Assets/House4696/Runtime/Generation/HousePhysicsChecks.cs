using System.Collections.Generic;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// Checks of the built house by its colliders — what a person walking through it would run into, whatever
    /// combination of walls, slabs, guards, elements and other stairs caused it: headroom over every stair (the walker
    /// is 1.8 m tall, codes ask 2 m) and a clear way onto and off each stair (a wall, a guard or an element across the
    /// bottom step or the arrival, no floor to step on). Run once per full build, right after the colliders are made;
    /// the results live in <see cref="HouseContext.PhysicalIssues"/> and every later check run repeats them.
    /// </summary>
    public static class HousePhysicsChecks
    {
        const float Headroom = StairGeometry.Headroom;
        const float Approach = 0.8f;   // free depth before the first step and after the last one
        const float Body = 1.9f;       // height that must be free there

        public static void Run(HouseContext c, GameObject root)
        {
            c.PhysicalIssues.Clear();
            if (root == null) return;
            Physics.SyncTransforms();
            bool back = Physics.queriesHitBackfaces;
            Physics.queriesHitBackfaces = true;   // slabs and walls are open meshes: hit them from either side
            try
            {
                foreach (var g in c.StairGeometries) Stair(c, root.transform, g);
            }
            finally { Physics.queriesHitBackfaces = back; }
        }

        static void Stair(HouseContext c, Transform root, StairGeometry g)
        {
            string id = g.Def.Id ?? "stair", own = "Stair_" + id, path = $"stairs/{id}";
            void W(string m) => c.PhysicalIssues.Add(new Issue(IssueLevel.Warning, path, m));

            // headroom over the treads and landings (inset from the edges: the handrails run there)
            float min = float.MaxValue; Vector2 at = default; string what = null;
            foreach (var rect in g.Footprint)
            {
                var b = Polygon.Bounds(rect);
                for (float x = b.xMin + 0.15f; x < b.xMax - 0.1f; x += 0.2f)
                for (float z = b.yMin + 0.15f; z < b.yMax - 0.1f; z += 0.2f)
                {
                    var p = new Vector2(x, z);
                    if (!Polygon.Contains(rect, p)) continue;
                    float? top = TreadTop(root, own, p, g);
                    if (top == null) continue;
                    var hit = First(root, new Vector3(x, top.Value + 0.02f, z), Vector3.up, Headroom + 0.5f, own);
                    if (hit == null || hit.Value.distance >= min) continue;
                    min = hit.Value.distance; at = p; what = Describe(hit.Value.collider.name);
                }
            }
            if (min < Headroom - 0.05f)
                W($"над лестницей в {Fmt(at)} свободно только {min:0.00} м (нужно ≥ {Headroom:0.#} м, человек упирается головой) — мешает {what}. " +
                  "Сдвинь лестницу или то, что над ней; над лестницей другого этажа ставь её точно над нижней (start/direction те же) — " +
                  "тогда проём и конструкция считаются сами");

            // a clear way on and off
            var m = Quaternion.Euler(0, g.Def.Direction, 0);
            var fwd3 = m * Vector3.forward;
            var fwd = new Vector2(fwd3.x, fwd3.z);
            var right = new Vector2(fwd.y, -fwd.x);
            float hw = g.Def.Width * 0.5f;
            Zone(c, root, own, g.Def.Start - fwd * Approach, fwd, right, hw, g.From.Elevation, "перед первой ступенью", W);
            var arr = (g.ArrivalA + g.ArrivalB) * 0.5f;
            var across = (g.ArrivalB - g.ArrivalA).normalized;
            float aw = (g.ArrivalB - g.ArrivalA).magnitude * 0.5f;
            Zone(c, root, own, arr, g.ArrivalDir, across, aw, g.To.Elevation, $"на сходе с лестницы (этаж '{g.To.Id}')", W);
        }

        /// <summary>
        /// Zone <paramref name="depth"/>=<see cref="Approach"/> long from <paramref name="start"/> along <paramref name="dir"/>,
        /// ±<paramref name="half"/> across: something standing in it up to <see cref="Body"/>, or no floor under it.
        /// </summary>
        static void Zone(HouseContext c, Transform root, string own, Vector2 start, Vector2 dir, Vector2 across, float half, float floorY,
                         string where, System.Action<string> warn)
        {
            string blocker = null; Vector2 blockAt = default;
            int noFloor = 0, samples = 0; Vector2 holeAt = default;
            for (float t = 0.1f; t < Approach; t += 0.2f)
            for (float s = -half + 0.12f; s <= half - 0.12f + 1e-3f; s += Mathf.Max(0.2f, (2f * half - 0.24f) / 4f))
            {
                var p = start + dir * t + across * s;
                samples++;
                if (blocker == null)
                {
                    var down = First(root, new Vector3(p.x, floorY + Body, p.y), Vector3.down, Body - 0.08f, own);
                    var up = First(root, new Vector3(p.x, floorY + 0.08f, p.y), Vector3.up, Body - 0.08f, own);
                    var h = down ?? up;
                    if (h != null) { blocker = Describe(h.Value.collider.name); blockAt = p; }
                }
                var floor = First(root, new Vector3(p.x, floorY + 0.05f, p.y), Vector3.down, 0.3f, own);
                if (floor == null) { noFloor++; holeAt = p; }
            }
            if (blocker != null)
                warn($"проход {where} перегорожен: в {Fmt(blockAt)} стоит {blocker}. Нужно ≥ {Approach:0.#} м свободного места шириной с лестницу — " +
                     "сдвинь/поверни лестницу или убери препятствие");
            else if (noFloor * 3 > samples)
                warn($"{where} нет пола (например в {Fmt(holeAt)}) — лестница начинается/кончается над проёмом или вне комнат. " +
                     "Проверь start/direction/turn (house_inspect → stairs) и комнаты этажа");
        }

        /// <summary>Top of this stair's treads/landing at a plan point (below the upper floor).</summary>
        static float? TreadTop(Transform root, string own, Vector2 p, StairGeometry g)
        {
            float? best = null;
            var from = new Vector3(p.x, g.To.Elevation + 0.05f, p.y);
            foreach (var h in Physics.RaycastAll(from, Vector3.down, g.H + 0.5f))
                if (h.collider.name == own && h.collider.transform.IsChildOf(root) && (best == null || h.point.y > best.Value)) best = h.point.y;
            return best;
        }

        /// <summary>Nearest hit of the house's own colliders, skipping this stair's treads.</summary>
        static RaycastHit? First(Transform root, Vector3 o, Vector3 dir, float dist, string own)
        {
            RaycastHit? best = null;
            foreach (var h in Physics.RaycastAll(o, dir, dist))
            {
                var n = h.collider.name;
                if (n == own || n.StartsWith("Stair_Rails_") || n.StartsWith("Stair_Glass_") || !h.collider.transform.IsChildOf(root)) continue;
                if (best == null || h.distance < best.Value.distance) best = h;
            }
            return best;
        }

        /// <summary>What an object of the built house is, in the author's terms.</summary>
        public static string Describe(string name)
        {
            string After(string prefix) => name.Substring(prefix.Length);
            if (name.StartsWith("Stair_")) return $"лестница '{After("Stair_")}'";
            if (name.StartsWith("Railing_stair_") || name.StartsWith("Railing_void_")) return "автоматическое ограждение проёма в перекрытии";
            if (name.StartsWith("Railing_Glass_")) return $"ограждение '{After("Railing_Glass_")}'";
            if (name.StartsWith("Railing_")) return $"ограждение '{After("Railing_")}'";
            if (name.StartsWith("Element_")) return $"элемент '{After("Element_").Replace("_Cap", "")}'";
            if (name.StartsWith("Wall_")) return $"стена '{After("Wall_")}'";
            if (name.StartsWith("Partition_Glass_")) return $"стена '{After("Partition_Glass_")}'";
            if (name.StartsWith("Partition_")) return $"стена '{After("Partition_")}'";
            if (name.StartsWith("Steel_Partition_") || name.StartsWith("Steel_Glass_")) return $"стеклянная перегородка '{name.Substring(name.IndexOf('_', 6) + 1)}'";
            if (name.StartsWith("Threshold_")) return $"порог стены '{After("Threshold_")}'";
            if (name.StartsWith("Frames_") || name.StartsWith("Glass_")) return $"окно/дверь стены '{name.Substring(name.IndexOf('_') + 1)}'";
            if (name.StartsWith("Interior_Slabs") || name.StartsWith("Interior_FloorFinish")) return "перекрытие (пол этажа выше)";
            if (name.StartsWith("Interior_Ceilings")) return "потолок";
            if (name.StartsWith("Roof")) return "крыша";
            if (name.StartsWith("Furniture_") || name.StartsWith("Model_") || name == "Leaf") return "предмет мебели или дверь";
            return name;
        }

        static string Fmt(Vector2 p) => $"[{p.x:0.##}, {p.y:0.##}]";
    }
}
