using System.Collections.Generic;
using House4696.Generation;
using House4696.Model;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// A level of the house as a 2D architectural plan built from the document (not from rendered geometry, so floors
    /// never overlap): wall bodies split around their openings, window/door marks, and room polygons with labels.
    /// Plan coordinates are the document's [x, z] in metres.
    /// </summary>
    public sealed class PlanGeometry
    {
        public sealed class Room
        {
            public string Id, Name;
            public RoomType Type;
            public List<Vector2> Outline;
            public Vector2 Label;
            public float Area;
        }

        public sealed class Opening
        {
            public Vector2 A, B;          // on the wall's centre line
            public bool Door;
        }

        public string LevelId, LevelName;
        public float Elevation, Height;
        public readonly List<Vector2[]> Walls = new List<Vector2[]>();      // quads (4 corners)
        public readonly List<Opening> Openings = new List<Opening>();
        public readonly List<Room> Rooms = new List<Room>();
        public Rect Bounds;

        public static PlanGeometry Build(HouseDocument doc, LevelDef level)
        {
            var g = new PlanGeometry { LevelId = level.Id, LevelName = level.Name ?? level.Id, Elevation = level.Elevation, Height = level.Height };
            float minX = float.MaxValue, minY = float.MaxValue, maxX = float.MinValue, maxY = float.MinValue;
            void Grow(Vector2 p)
            {
                minX = Mathf.Min(minX, p.x); minY = Mathf.Min(minY, p.y);
                maxX = Mathf.Max(maxX, p.x); maxY = Mathf.Max(maxY, p.y);
            }

            // architectural cut 1.2 m above the floor: walls of this level, plus taller walls of other levels passing
            // through the cut (a two-storey glass wall of the ground floor shows on the upper plan too)
            float cut = level.Elevation + 1.2f;
            foreach (var w in doc.Walls)
            {
                var wl = doc.Levels.Find(l => l.Id == w.Level);
                bool own = w.Level == level.Id;
                if (!own && (wl == null || !Spans(doc, w, wl, cut))) continue;
                bool ext = w.Kind == WallKind.Exterior;
                float t = w.Thickness ?? (ext ? 0.4f : 0.12f);
                var align = w.Align ?? (ext ? WallAlign.Outer : WallAlign.Center);
                Vector2 d = w.B - w.A;
                float len = d.magnitude;
                if (len < 1e-4f) continue;
                d /= len;
                var right = new Vector2(d.y, -d.x);                           // outside of a CCW exterior wall
                float off = align == WallAlign.Outer ? 0f : align == WallAlign.Center ? t * 0.5f : t;
                Vector2 outer = w.A + right * off, inner = outer - right * t;

                // body segments between openings
                var cuts = new List<(float s0, float s1, bool door)>();
                foreach (var o in doc.Openings)
                    if (o.Wall == w.Id && (wl == null || (wl.Elevation + o.Sill <= cut + 0.3f && wl.Elevation + o.Sill + o.Height >= cut)))
                    {
                        bool door = o.Type == OpeningType.Door || o.Type == OpeningType.EntryDoor || o.Type == OpeningType.SolidDoor || o.Type == OpeningType.Hole;
                        cuts.Add((Mathf.Clamp(o.At, 0f, len), Mathf.Clamp(o.At + o.Width, 0f, len), door));
                    }
                cuts.Sort((a, b) => a.s0.CompareTo(b.s0));
                float s = 0f;
                foreach (var c in cuts)
                {
                    if (c.s0 > s + 0.01f) g.Walls.Add(Quad(outer, inner, d, s, c.s0));
                    var mid = (outer + inner) * 0.5f;
                    g.Openings.Add(new Opening { A = mid + d * c.s0, B = mid + d * c.s1, Door = c.door });
                    s = Mathf.Max(s, c.s1);
                }
                if (len > s + 0.01f) g.Walls.Add(Quad(outer, inner, d, s, len));
                Grow(outer); Grow(outer + d * len); Grow(inner); Grow(inner + d * len);
            }

            foreach (var r in doc.Rooms)
            {
                if (r.Level != level.Id || r.Outline.Count < 3) continue;
                var room = new Room
                {
                    Id = r.Id, Name = string.IsNullOrEmpty(r.Name) ? r.Id : r.Name, Type = r.Type,
                    Outline = new List<Vector2>(r.Outline), Area = Mathf.Abs(Polygon.SignedArea(r.Outline)),
                };
                room.Label = InteriorPoint(room.Outline, out _);
                g.Rooms.Add(room);
                foreach (var p in r.Outline) Grow(p);
            }
            g.Bounds = minX <= maxX ? Rect.MinMaxRect(minX, minY, maxX, maxY) : new Rect(0, 0, 10, 10);
            return g;
        }

        /// <summary>The wall's vertical extent (as the generator resolves it) contains height <paramref name="y"/>.</summary>
        static bool Spans(HouseDocument doc, WallDef w, LevelDef l, float y)
        {
            LevelDef above = null, lowest = l;
            foreach (var x in doc.Levels)
            {
                if (x.Elevation > l.Elevation && (above == null || x.Elevation < above.Elevation)) above = x;
                if (x.Elevation < lowest.Elevation) lowest = x;
            }
            float y0, y1;
            if (w.Kind == WallKind.Exterior)
            {
                y0 = w.Bottom ?? (lowest == l ? 0f : l.Elevation - l.Slab);
                y1 = w.Top ?? (above != null ? above.Elevation - above.Slab : l.Elevation + l.Height + 0.3f);
            }
            else
            {
                y0 = w.Bottom ?? l.Elevation;
                y1 = w.Top ?? l.Elevation + l.Height;
            }
            return y0 <= y && y1 >= y;
        }

        static Vector2[] Quad(Vector2 outer, Vector2 inner, Vector2 d, float s0, float s1) =>
            new[] { outer + d * s0, outer + d * s1, inner + d * s1, inner + d * s0 };

        /// <summary>The room at a plan point, or null.</summary>
        public Room RoomAt(Vector2 p)
        {
            Room best = null;
            foreach (var r in Rooms)
                if (Contains(r.Outline, p) && (best == null || r.Area < best.Area)) best = r;
            return best;
        }

        public static bool Contains(List<Vector2> poly, Vector2 p)
        {
            bool inside = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
                if ((poly[i].y > p.y) != (poly[j].y > p.y) &&
                    p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)
                    inside = !inside;
            return inside;
        }

        static float EdgeDistance(List<Vector2> poly, Vector2 p)
        {
            float best = float.MaxValue;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                Vector2 a = poly[j], b = poly[i], ab = b - a;
                float t = Mathf.Clamp01(Vector2.Dot(p - a, ab) / Mathf.Max(ab.sqrMagnitude, 1e-6f));
                best = Mathf.Min(best, (a + ab * t - p).magnitude);
            }
            return best;
        }

        /// <summary>
        /// A point well inside the polygon (the grid point farthest from its edges) — the centroid of an L-shaped room
        /// can lie outside it. <paramref name="clearance"/> = distance to the nearest edge.
        /// </summary>
        public static Vector2 InteriorPoint(List<Vector2> poly, out float clearance)
        {
            var bb = BoundsOf(poly);
            float step = Mathf.Max(0.1f, Mathf.Max(bb.width, bb.height) / 40f);
            Vector2 best = bb.center;
            clearance = -1f;
            for (float x = bb.xMin + step * 0.5f; x < bb.xMax; x += step)
            for (float y = bb.yMin + step * 0.5f; y < bb.yMax; y += step)
            {
                var p = new Vector2(x, y);
                if (!Contains(poly, p)) continue;
                float e = EdgeDistance(poly, p);
                if (e > clearance) { clearance = e; best = p; }
            }
            return best;
        }

        /// <summary>
        /// Where to stand to see a room: a free spot (no furniture) at least 0.55 m from the walls that sees farthest
        /// across the room, looking towards the room's middle — like the corner a photographer picks.
        /// </summary>
        public static bool ViewSpot(List<Vector2> poly, float floorY, out Vector3 feet, out float yaw)
        {
            var mid = InteriorPoint(poly, out float midClear);
            var bb = BoundsOf(poly);
            float step = 0.2f, bestScore = -1f;
            Vector2 best = mid;
            for (float x = bb.xMin + step * 0.5f; x < bb.xMax; x += step)
            for (float y = bb.yMin + step * 0.5f; y < bb.yMax; y += step)
            {
                var p = new Vector2(x, y);
                if (!Contains(poly, p) || EdgeDistance(poly, p) < Mathf.Min(0.55f, midClear * 0.8f)) continue;
                if (!Free(p, floorY)) continue;
                float far = 0f;
                foreach (var v in poly) far = Mathf.Max(far, (v - p).sqrMagnitude);
                if (far > bestScore) { bestScore = far; best = p; }
            }
            feet = new Vector3(best.x, floorY + 0.02f, best.y);
            var look = mid - best;
            if (look.sqrMagnitude < 0.25f) look = bb.width >= bb.height ? Vector2.right : Vector2.up;
            yaw = Mathf.Atan2(look.x, look.y) * Mathf.Rad2Deg;
            return bestScore >= 0f;
        }

        /// <summary>Standing room for a person (capsule above the floor hits nothing but the floor).</summary>
        static bool Free(Vector2 p, float floorY)
        {
            var a = new Vector3(p.x, floorY + 0.45f, p.y);
            var b = new Vector3(p.x, floorY + 1.5f, p.y);
            return !Physics.CheckCapsule(a, b, 0.3f, ~(1 << 2), QueryTriggerInteraction.Ignore);
        }

        static Rect BoundsOf(List<Vector2> poly)
        {
            float minX = float.MaxValue, minY = float.MaxValue, maxX = float.MinValue, maxY = float.MinValue;
            foreach (var p in poly)
            {
                minX = Mathf.Min(minX, p.x); minY = Mathf.Min(minY, p.y);
                maxX = Mathf.Max(maxX, p.x); maxY = Mathf.Max(maxY, p.y);
            }
            return Rect.MinMaxRect(minX, minY, maxX, maxY);
        }

        /// <summary>Russian room-type names for rooms without their own name.</summary>
        public static string TypeName(RoomType t) => t switch
        {
            RoomType.Living => "Гостиная", RoomType.Kitchen => "Кухня", RoomType.Dining => "Столовая",
            RoomType.Bedroom => "Спальня", RoomType.Bathroom => "Санузел", RoomType.Hall => "Холл",
            RoomType.Corridor => "Коридор", RoomType.Wardrobe => "Гардероб", RoomType.Utility => "Техническое",
            RoomType.Office => "Кабинет", RoomType.Stair => "Лестница", RoomType.Garage => "Гараж",
            RoomType.Terrace => "Терраса", _ => "Помещение",
        };
    }
}
