using System;
using System.Collections.Generic;
using House4696.Generation;
using House4696.Model;
using UnityEngine;

namespace House4696.App
{
    /// <summary>What placing needs to know about a model: its extent (in its own frame) and how it attaches.</summary>
    public struct ItemShape
    {
        public Bounds Local;
        public ItemMount Mount;
        public bool AgainstWall, OnSurfaces;

        public static ItemShape Of(FurnitureCatalog.Entry e, Bounds local) => new ItemShape
        {
            Local = local, Mount = e?.Mount ?? ItemMount.Floor, AgainstWall = e?.AgainstWall ?? false, OnSurfaces = e?.OnSurfaces ?? false,
        };
    }

    /// <summary>A place for an item in the document's terms (level, position, rotation) and as a world pose of its object.</summary>
    public struct Placement
    {
        /// <summary>The pointer is over something the item can go to (else <see cref="Problem"/> says where to point).</summary>
        public bool Found;
        /// <summary>Level id; null = an absolute height (the garden below the lowest floor).</summary>
        public string Level;
        /// <summary>X, height above the level's floor (absolute without a level), Z.</summary>
        public Vector3 Position;
        public float Rotation;
        /// <summary>The item's origin in the world.</summary>
        public Vector3 World;
        /// <summary>Why the item cannot stay here (null = it can).</summary>
        public string Problem;

        public bool Valid => Found && Problem == null;
        public Quaternion WorldRotation => FurnitureGeometry.ItemRotation(Rotation);
    }

    public static class FurnitureGeometry
    {
        /// <summary>Object rotation of an item turned to <paramref name="compass"/> (models are built facing -Z).</summary>
        public static Quaternion ItemRotation(float compass) => Quaternion.Euler(0f, compass + 180f, 0f);

        /// <summary>Plan direction the front faces: 0 = +Z (north), 90 = +X.</summary>
        public static Vector3 Facing(float compass)
        {
            float r = compass * Mathf.Deg2Rad;
            return new Vector3(Mathf.Sin(r), 0f, Mathf.Cos(r));
        }

        public static float CompassOf(Vector3 dir) => Normalize(Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg);

        /// <summary>0 ≤ angle &lt; 360, rounded to 0.1° (so 90° steps stay exact in the file).</summary>
        public static float Normalize(float deg)
        {
            deg = Mathf.Round(deg * 10f) / 10f % 360f;
            if (deg < 0f) deg += 360f;
            return deg >= 359.95f ? 0f : deg;
        }

        /// <summary>The lowest level whose floor is at or under <paramref name="y"/> — the highest such; null below every floor.</summary>
        public static LevelDef LevelAt(HouseDocument doc, float y)
        {
            LevelDef best = null;
            foreach (var l in doc.Levels)
                if (l != null && l.Elevation <= y + 0.1f && (best == null || l.Elevation > best.Elevation)) best = l;
            return best;
        }

        /// <summary>Ray against an axis-aligned box in a transform's frame (unit scale): entry distance.</summary>
        public static bool RayBox(Ray ray, Matrix4x4 worldToLocal, Bounds local, float pad, out float enter)
        {
            var o = worldToLocal.MultiplyPoint3x4(ray.origin);
            var d = worldToLocal.MultiplyVector(ray.direction);
            return RayAabb(o, d, local.min - Vector3.one * pad, local.max + Vector3.one * pad, out enter);
        }

        public static bool RayAabb(Vector3 o, Vector3 d, Vector3 min, Vector3 max, out float enter)
        {
            float t0 = 0f, t1 = float.MaxValue;
            enter = 0f;
            for (int a = 0; a < 3; a++)
            {
                if (Mathf.Abs(d[a]) < 1e-9f)
                {
                    if (o[a] < min[a] || o[a] > max[a]) return false;
                    continue;
                }
                float inv = 1f / d[a];
                float ta = (min[a] - o[a]) * inv, tb = (max[a] - o[a]) * inv;
                if (ta > tb) (ta, tb) = (tb, ta);
                t0 = Mathf.Max(t0, ta);
                t1 = Mathf.Min(t1, tb);
                if (t0 > t1) return false;
            }
            enter = t0;
            return true;
        }

        /// <summary>Möller–Trumbore, both faces.</summary>
        public static bool RayTriangle(Vector3 o, Vector3 d, Vector3 a, Vector3 b, Vector3 c, out float t)
        {
            t = 0f;
            Vector3 e1 = b - a, e2 = c - a;
            var p = Vector3.Cross(d, e2);
            float det = Vector3.Dot(e1, p);
            if (det > -1e-10f && det < 1e-10f) return false;
            float inv = 1f / det;
            var s = o - a;
            float u = Vector3.Dot(s, p) * inv;
            if (u < 0f || u > 1f) return false;
            var q = Vector3.Cross(s, e1);
            float v = Vector3.Dot(d, q) * inv;
            if (v < 0f || u + v > 1f) return false;
            t = Vector3.Dot(e2, q) * inv;
            return t > 1e-5f;
        }
    }

    /// <summary>
    /// The built house as surfaces to put things on and as items to pick. Placing: the pointer ray finds a floor (or a table top
    /// for small things), a wall (the item turns its back to it) or a ceiling; floor furniture snaps to the 5 cm grid and walls
    /// within 30 cm pull its back and sides flush; an item cutting into a wall is refused. Picking: the item whose real triangles
    /// the ray meets first, in front of the first wall.
    /// </summary>
    public sealed class FurnitureScene
    {
        public const float Grid = 0.05f;
        /// <summary>Walls this close to an item's back or side pull it flush.</summary>
        public const float MagnetRange = 0.3f;
        const float MaxDistance = 400f;
        const int Mask = ~(1 << 2);       // everything but Ignore Raycast (the walker, previews)

        enum Kind { Skip, Floor, Wall, Ceiling, Item, Roof, Stop }

        readonly RaycastHit[] _hits = new RaycastHit[64];
        readonly Collider[] _overlaps = new Collider[32];
        readonly Dictionary<Mesh, (Vector3[] v, int[] t)> _meshes = new Dictionary<Mesh, (Vector3[], int[])>();
        readonly Dictionary<GameObject, MeshFilter[]> _filters = new Dictionary<GameObject, MeshFilter[]>();
        readonly List<(ItemBox box, float t)> _candidates = new List<(ItemBox, float)>();
        static readonly IComparer<RaycastHit> ByDistance = Comparer<RaycastHit>.Create((a, b) => a.distance.CompareTo(b.distance));
        Transform _items, _doors;
        HouseDocument _doc;

        /// <summary>Follows the current build (call after every rebuild): which colliders are items and doors.</summary>
        public void Bind(HouseBuildResult result, HouseDocument doc)
        {
            _items = result?.Context?.Furniture;
            _doors = result?.Context?.Doors;
            _doc = doc;
            _meshes.Clear();
            _filters.Clear();
        }

        public HouseDocument Doc => _doc;

        // ------------------------------------------------------------------ picking
        /// <summary>The item under the pointer (null = none), with the distance to the point hit.</summary>
        public ItemBox Pick(Ray ray, IReadOnlyList<ItemBox> items, out float distance)
        {
            distance = float.MaxValue;
            if (items == null) return null;
            float wall = FirstWall(ray);
            _candidates.Clear();
            foreach (var b in items)
            {
                if (b?.Object == null || !b.Object.activeInHierarchy) continue;
                if (!FurnitureGeometry.RayBox(ray, b.Object.transform.worldToLocalMatrix, b.Local, 0.02f, out float t) || t > wall) continue;
                _candidates.Add((b, t));
            }
            _candidates.Sort((a, b) => a.t.CompareTo(b.t));
            ItemBox best = null;
            float bestT = wall;
            foreach (var (box, enter) in _candidates)
            {
                if (enter >= bestT) break;            // later boxes start behind the point already hit
                if (RayItem(ray, box.Object, bestT, out float t)) { bestT = t; best = box; }
            }
            // tiny or unreadable pieces the triangles missed: the smallest box the ray passes through
            if (best == null && _candidates.Count > 0)
            {
                float vol = float.MaxValue;
                foreach (var (box, enter) in _candidates)
                {
                    var s = box.Local.size;
                    float v = s.x * s.y * s.z;
                    if (v < vol && Mathf.Max(s.x, Mathf.Max(s.y, s.z)) < 0.4f) { vol = v; best = box; bestT = enter; }
                }
            }
            distance = bestT;
            return best;
        }

        /// <summary>Distance to the first thing that hides items (walls, floors, doors; not glass, not furniture).</summary>
        float FirstWall(Ray ray)
        {
            int n = Physics.RaycastNonAlloc(ray, _hits, MaxDistance, Mask, QueryTriggerInteraction.Ignore);
            float best = MaxDistance;
            for (int i = 0; i < n; i++)
            {
                var k = Classify(_hits[i], null);
                if (k == Kind.Skip || k == Kind.Item) continue;
                best = Mathf.Min(best, _hits[i].distance);
            }
            return best;
        }

        bool RayItem(Ray ray, GameObject go, float maxT, out float best)
        {
            best = maxT;
            bool hit = false;
            if (!_filters.TryGetValue(go, out var filters))
            {
                filters = go.GetComponentsInChildren<MeshFilter>(false);
                _filters[go] = filters;
            }
            foreach (var mf in filters)
            {
                if (mf == null) continue;
                var r = mf.GetComponent<Renderer>();
                var mesh = mf.sharedMesh;
                if (r == null || !r.enabled || mesh == null || !mesh.isReadable) continue;
                var m = mf.transform.worldToLocalMatrix;
                // t stays a world distance: the direction is transformed but not re-normalised
                var o = m.MultiplyPoint3x4(ray.origin);
                var d = m.MultiplyVector(ray.direction);
                var mb = mesh.bounds;
                if (!FurnitureGeometry.RayAabb(o, d, mb.min, mb.max, out float enter) || enter > best) continue;
                if (!_meshes.TryGetValue(mesh, out var data))
                {
                    data = (mesh.vertices, mesh.triangles);
                    _meshes[mesh] = data;
                }
                var v = data.v;
                var tri = data.t;
                for (int i = 0; i + 2 < tri.Length; i += 3)
                {
                    if (FurnitureGeometry.RayTriangle(o, d, v[tri[i]], v[tri[i + 1]], v[tri[i + 2]], out float t) && t < best)
                    {
                        best = t;
                        hit = true;
                    }
                }
            }
            return hit;
        }

        // ------------------------------------------------------------------ placing
        /// <summary>
        /// Where the pointer ray puts an item: by its mount — floor pieces on floors (small ones also on furniture tops) or
        /// against the wall pointed at, wall pieces on walls, ceiling pieces under ceilings. <paramref name="ignore"/> = the
        /// item being moved (its own colliders are no obstacle).
        /// </summary>
        public Placement FromRay(Ray ray, ItemShape s, float rotation, bool snap, GameObject ignore)
        {
            var miss = new Placement { Rotation = rotation };
            if (_doc == null) return miss;
            int n = Physics.RaycastNonAlloc(ray, _hits, MaxDistance, Mask, QueryTriggerInteraction.Ignore);
            Array.Sort(_hits, 0, n, ByDistance);
            for (int i = 0; i < n; i++)
            {
                var h = _hits[i];
                var k = Classify(h, ignore);
                if (k == Kind.Skip) continue;
                if (k == Kind.Item)
                {
                    if (s.OnSurfaces && s.Mount == ItemMount.Floor && h.normal.y > 0.8f) return OnFloor(h.point, s, rotation, snap, ignore, false);
                    continue;           // big pieces go to the floor under the furniture pointed at
                }
                switch (s.Mount)
                {
                    case ItemMount.Wall:
                        if (k == Kind.Wall) return OnWall(h, s, snap);
                        return Miss(miss, "Наведите на стену");
                    case ItemMount.Ceiling:
                        // a hanging piece belongs to the floor under it (a double-height room: the lower level)
                        if (k == Kind.Ceiling)
                            return UnderCeiling(h.point, FloorUnder(h.point - Vector3.up * 0.05f, ignore, out var below)
                                ? FurnitureGeometry.LevelAt(_doc, below.y) : FurnitureGeometry.LevelAt(_doc, h.point.y - 0.3f), s, rotation, snap);
                        if (k == Kind.Floor) return UnderCeiling(CeilingOver(h.point), FurnitureGeometry.LevelAt(_doc, h.point.y), s, rotation, snap);
                        return Miss(miss, "Наведите на пол или потолок комнаты");
                    default:
                        if (k == Kind.Floor) return OnFloor(h.point, s, rotation, snap, ignore, true);
                        if (k == Kind.Wall) return AgainstWall(h, s, snap, ignore, miss);
                        return Miss(miss, k == Kind.Roof ? "Это крыша — зайдите в дом" : "Наведите на пол");
                }
            }
            return Miss(miss, null);
        }

        /// <summary>
        /// A floor or ceiling piece moved (dragged, turned) to <paramref name="origin"/> at its own height on the same level:
        /// optionally snapped to the grid and pulled flush by nearby walls (floor pieces).
        /// </summary>
        public Placement Slide(Vector3 origin, ItemShape s, float rotation, bool grid, bool magnet, GameObject ignore, string level)
        {
            if (grid) { origin.x = Snap(origin.x); origin.z = Snap(origin.z); }
            if (magnet && s.Mount == ItemMount.Floor) origin = Magnet(origin, s, rotation, ignore);
            var lv = level != null ? _doc?.Levels.Find(l => l.Id == level) : null;
            return Make(origin, rotation, lv, s, ignore, s.Mount == ItemMount.Floor);
        }

        Placement OnFloor(Vector3 point, ItemShape s, float rotation, bool snap, GameObject ignore, bool magnet)
        {
            var c = s.Local.center;
            var o = point - FurnitureGeometry.ItemRotation(rotation) * new Vector3(c.x, 0f, c.z);
            o.y = point.y;
            if (snap) { o.x = Snap(o.x); o.z = Snap(o.z); }
            if (snap && magnet) o = Magnet(o, s, rotation, ignore);
            return Make(o, rotation, FurnitureGeometry.LevelAt(_doc, point.y), s, ignore, true);
        }

        /// <summary>A floor piece pointed at a wall: back to that wall, standing on the floor at its foot, centred under the pointer.</summary>
        Placement AgainstWall(RaycastHit h, ItemShape s, bool snap, GameObject ignore, Placement miss)
        {
            var f = new Vector3(h.normal.x, 0f, h.normal.z).normalized;
            if (!FloorUnder(h.point + f * 0.1f, ignore, out var floor)) return Miss(miss, "Наведите на пол");
            float rot = FurnitureGeometry.CompassOf(f);
            var R = FurnitureGeometry.ItemRotation(rot);
            var foot = new Vector3(h.point.x, floor.y, h.point.z);
            var o = foot + f * s.Local.max.z - R * new Vector3(s.Local.center.x, 0f, 0f);
            o.y = floor.y;
            if (snap) o = Magnet(o, s, rot, ignore);
            return Make(o, rot, FurnitureGeometry.LevelAt(_doc, floor.y), s, ignore, true);
        }

        /// <summary>A wall piece: back on the wall, its centre at the pointer (heights on the 5 cm grid).</summary>
        Placement OnWall(RaycastHit h, ItemShape s, bool snap)
        {
            var f = new Vector3(h.normal.x, 0f, h.normal.z).normalized;
            float rot = FurnitureGeometry.CompassOf(f);
            var R = FurnitureGeometry.ItemRotation(rot);
            var level = FurnitureGeometry.LevelAt(_doc, h.point.y);
            float floorY = level?.Elevation ?? 0f;
            var o = h.point + f * s.Local.max.z - R * new Vector3(s.Local.center.x, 0f, 0f);
            o.y = h.point.y - s.Local.center.y;
            if (snap) o.y = floorY + Snap(o.y - floorY);
            return Make(o, rot, level, s, null, false);
        }

        Placement UnderCeiling(Vector3 point, LevelDef level, ItemShape s, float rotation, bool snap)
        {
            var c = s.Local.center;
            var o = point - FurnitureGeometry.ItemRotation(rotation) * new Vector3(c.x, 0f, c.z);
            o.y = point.y;
            if (snap) { o.x = Snap(o.x); o.z = Snap(o.z); }
            return Make(o, rotation, level, s, null, false);
        }

        /// <summary>The ceiling above a floor point (or the level's own ceiling height where the ray finds none).</summary>
        Vector3 CeilingOver(Vector3 floorPoint)
        {
            int n = Physics.RaycastNonAlloc(new Ray(floorPoint + Vector3.up * 0.05f, Vector3.up), _hits, 20f, Mask, QueryTriggerInteraction.Ignore);
            float best = float.MaxValue;
            for (int i = 0; i < n; i++)
                if (Classify(_hits[i], null) == Kind.Ceiling && _hits[i].distance < best) best = _hits[i].distance;
            if (best < float.MaxValue) return floorPoint + Vector3.up * (best + 0.05f);
            var level = FurnitureGeometry.LevelAt(_doc, floorPoint.y);
            return new Vector3(floorPoint.x, level != null ? level.Elevation + level.Height : floorPoint.y + 2.7f, floorPoint.z);
        }

        bool FloorUnder(Vector3 p, GameObject ignore, out Vector3 floor)
        {
            floor = default;
            int n = Physics.RaycastNonAlloc(new Ray(p, Vector3.down), _hits, 30f, Mask, QueryTriggerInteraction.Ignore);
            float best = float.MaxValue;
            for (int i = 0; i < n; i++)
            {
                if (Classify(_hits[i], ignore) != Kind.Floor || _hits[i].distance >= best) continue;
                best = _hits[i].distance;
                floor = _hits[i].point;
            }
            return best < float.MaxValue;
        }

        Placement Make(Vector3 o, float rotation, LevelDef level, ItemShape s, GameObject ignore, bool checkWalls)
        {
            var p = new Placement
            {
                Found = true, Rotation = FurnitureGeometry.Normalize(rotation), World = o, Level = level?.Id,
                Position = new Vector3(Round(o.x), Round(o.y - (level?.Elevation ?? 0f)), Round(o.z)),
            };
            if (checkWalls && CutsWall(o, FurnitureGeometry.ItemRotation(p.Rotation), s, ignore)) p.Problem = "Мешает стена";
            return p;
        }

        static Placement Miss(Placement p, string problem)
        {
            p.Found = false;
            p.Problem = problem;
            return p;
        }

        /// <summary>
        /// Walls within <see cref="MagnetRange"/> of the item's back and sides pull those faces flush (a wardrobe into a corner);
        /// an item already cutting into a wall is pushed out of it the same way.
        /// </summary>
        Vector3 Magnet(Vector3 o, ItemShape s, float rotation, GameObject ignore)
        {
            var b = s.Local;
            var R = FurnitureGeometry.ItemRotation(rotation);
            float y = Mathf.Clamp(b.max.y * 0.5f, 0.1f, 1f);
            // the back (local +Z), then the right and left sides (local ±X)
            var dirs = new[] { Vector3.forward, Vector3.right, Vector3.left };
            var reach = new[] { b.max.z - b.center.z, b.max.x - b.center.x, b.center.x - b.min.x };
            for (int i = 0; i < dirs.Length; i++)
            {
                var d = R * dirs[i];
                var from = o + R * new Vector3(b.center.x, 0f, b.center.z) + Vector3.up * y;
                if (WallAlong(new Ray(from, d), reach[i] + MagnetRange, ignore, out float dist))
                {
                    float shift = dist - reach[i];
                    if (shift > -reach[i] && shift < MagnetRange) o += d * shift;
                }
            }
            return o;
        }

        /// <summary>The nearest wall face across the ray, facing back at its origin.</summary>
        bool WallAlong(Ray ray, float range, GameObject ignore, out float dist)
        {
            dist = float.MaxValue;
            int n = Physics.RaycastNonAlloc(ray, _hits, range, Mask, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < n; i++)
            {
                var h = _hits[i];
                if (Classify(h, ignore) != Kind.Wall || h.distance >= dist) continue;
                if (Vector3.Dot(h.normal, -ray.direction) < 0.9f) continue;
                dist = h.distance;
            }
            return dist < float.MaxValue;
        }

        /// <summary>The item's body (4 cm inside its box) overlaps architecture — walls, stairs, doors, ceilings.</summary>
        bool CutsWall(Vector3 o, Quaternion R, ItemShape s, GameObject ignore)
        {
            var b = s.Local;
            var half = b.extents - Vector3.one * 0.04f;
            if (half.x < 0.01f || half.y < 0.01f || half.z < 0.01f) return false;
            int n = Physics.OverlapBoxNonAlloc(o + R * b.center, half, _overlaps, R, Mask, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < n; i++)
            {
                var col = _overlaps[i];
                if (col == null) continue;
                var t = col.transform;
                if (ignore != null && t.IsChildOf(ignore.transform)) continue;
                if (_items != null && t.IsChildOf(_items)) continue;        // furniture may touch furniture (a rug under a table)
                if (col is TerrainCollider || col.name.StartsWith("Lawn", StringComparison.Ordinal)) continue;   // uneven ground
                return true;
            }
            return false;
        }

        Kind Classify(RaycastHit h, GameObject ignore)
        {
            var col = h.collider;
            if (col == null) return Kind.Skip;
            var t = col.transform;
            if (ignore != null && t.IsChildOf(ignore.transform)) return Kind.Skip;
            if (_items != null && t.IsChildOf(_items)) return Kind.Item;
            string n = col.name;
            if (n.IndexOf("Glass", StringComparison.Ordinal) >= 0) return Kind.Skip;       // see-through: windows, glass partitions
            if (_doors != null && t.IsChildOf(_doors)) return Kind.Stop;
            float ny = h.normal.y;
            if (n.StartsWith("Roof_", StringComparison.Ordinal)) return ny > 0.95f ? Kind.Floor : Kind.Roof;   // flat roofs are terraces
            if (ny > 0.8f) return Kind.Floor;
            if (ny < -0.8f) return Kind.Ceiling;
            if (Mathf.Abs(ny) < 0.35f) return n.StartsWith("Stair_", StringComparison.Ordinal) ? Kind.Stop : Kind.Wall;
            return Kind.Stop;
        }

        public static float Snap(float v) => Mathf.Round(v / Grid) * Grid;
        static float Round(float v) => Mathf.Round(v * 1000f) / 1000f;
    }
}
