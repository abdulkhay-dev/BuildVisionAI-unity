using System.Collections.Generic;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// How the house meets its plot — shared by the site builder, the checks and the inspector: the entrance doors,
    /// the street side, the approach paths the generator adds from each entrance to the street, and the footprints of
    /// things standing on the ground next to the house (porches, terraces, steps) where nothing may grow.
    /// </summary>
    public sealed class SiteLayout
    {
        public sealed class Entrance
        {
            public string OpeningId, WallId;
            /// <summary>Middle of the door on the wall's outer face (plan).</summary>
            public Vector2 Point;
            /// <summary>Outward (plan, unit).</summary>
            public Vector2 Out;
            public float Width;
        }

        public readonly Rect House, Plot;
        public readonly List<Entrance> Entrances = new List<Entrance>();
        public readonly string Street;
        public readonly List<SitePathDef> Approach = new List<SitePathDef>();
        public readonly List<Vector2[]> Solids = new List<Vector2[]>();

        public static readonly string[] Sides = { "north", "east", "south", "west" };

        public SiteLayout(HouseContext c, Rect house)
        {
            House = house;
            var site = c.Doc.Site;
            Plot = Landscape.Natural.SiteModel.PlotOf(site, house);

            // entrances: entrance doors in exterior walls of the storey at grade (not a basement); failing those, any door there
            var lowest = c.GroundLevel;
            foreach (bool entryOnly in new[] { true, false })
            {
                foreach (var o in c.Doc.Openings)
                {
                    bool door = o.Type == OpeningType.EntryDoor || (!entryOnly && (o.Type == OpeningType.Door || o.Type == OpeningType.SolidDoor));
                    if (!door) continue;
                    var f = c.Wall(o.Wall);
                    if (f == null || !f.Exterior || (lowest != null && f.Level != lowest)) continue;
                    float s = f.SAt(o.At + o.Width * 0.5f);
                    Entrances.Add(new Entrance
                    {
                        OpeningId = o.Id, WallId = f.Def.Id, Point = f.Plan(s, 0f), Out = new Vector2(f.N.x, f.N.z).normalized, Width = o.Width,
                    });
                }
                if (Entrances.Count > 0) break;
            }

            Street = !string.IsNullOrEmpty(site.Street) ? site.Street : Entrances.Count > 0 ? SideOf(Entrances[0].Out) : "south";

            foreach (var e in c.Doc.Elements)
            {
                if (e.Type == ElementType.Railing || e.Type == ElementType.Pool) continue;
                if (Mathf.Min(e.Min.y, e.Max.y) > 0.3f) continue;          // canopies, belts: not on the ground
                float x0 = Mathf.Min(e.Min.x, e.Max.x), x1 = Mathf.Max(e.Min.x, e.Max.x), z0 = Mathf.Min(e.Min.z, e.Max.z), z1 = Mathf.Max(e.Min.z, e.Max.z);
                if (x1 - x0 < 0.05f || z1 - z0 < 0.05f) continue;
                Solids.Add(new[] { new Vector2(x0, z0), new Vector2(x1, z0), new Vector2(x1, z1), new Vector2(x0, z1) });
            }

            if (site.Approach != "none")
                foreach (var e in Entrances)
                {
                    if (Served(site, e)) continue;
                    var path = Route(e);
                    if (path != null) Approach.Add(new SitePathDef { Id = "approach_" + e.OpeningId, Path = path, Width = Mathf.Max(1.4f, e.Width + 0.4f), Style = "paving" });
                }
        }

        /// <summary>Compass side a direction points to.</summary>
        public static string SideOf(Vector2 d) =>
            Mathf.Abs(d.x) > Mathf.Abs(d.y) ? (d.x > 0 ? "east" : "west") : (d.y > 0 ? "north" : "south");

        static Vector2 Dir(string side) =>
            side == "north" ? Vector2.up : side == "east" ? Vector2.right : side == "west" ? Vector2.left : Vector2.down;

        /// <summary>Does an author's path or paved area already start at this door?</summary>
        public static bool Served(SiteDef site, Entrance e)
        {
            var front = e.Point + e.Out * 0.8f;
            foreach (var p in site.Paths)
                if (p.Path != null)
                    for (int i = 0; i + 1 < p.Path.Count; i++)
                        if (StairGeometry.DistanceToSegment(front, p.Path[i], p.Path[i + 1]) < 2f + p.Width * 0.5f) return true;
            foreach (var a in site.Areas)
                if (a.Outline != null && a.Outline.Count >= 3 && a.Type != "lawn" && Landscape.Natural.SiteModel.DistanceToPolygon(a.Outline, front) < 1f) return true;
            return false;
        }

        /// <summary>
        /// From the door straight out, then to the street edge of the plot (and 1 m past it, through the fence gap);
        /// around the house when the street is behind it.
        /// </summary>
        List<Vector2> Route(Entrance e)
        {
            var street = Dir(Street);
            var pts = new List<Vector2> { e.Point + e.Out * 0.2f };
            var p = e.Point + e.Out * 2.5f;
            pts.Add(p);
            float Edge(Vector2 q) => street.y > 0 ? Plot.yMax + 1f : street.y < 0 ? Plot.yMin - 1f : street.x > 0 ? Plot.xMax + 1f : Plot.xMin - 1f;
            bool alongZ = street.x == 0f;
            if (Vector2.Dot(e.Out, street) < -0.5f)
            {
                // the street is behind the house: go round the nearer side
                if (alongZ)
                {
                    float x = p.x - House.xMin < House.xMax - p.x ? House.xMin - 2.5f : House.xMax + 2.5f;
                    pts.Add(new Vector2(x, p.y));
                    p = new Vector2(x, p.y);
                }
                else
                {
                    float z = p.y - House.yMin < House.yMax - p.y ? House.yMin - 2.5f : House.yMax + 2.5f;
                    pts.Add(new Vector2(p.x, z));
                    p = new Vector2(p.x, z);
                }
            }
            var end = alongZ ? new Vector2(p.x, Edge(p)) : new Vector2(Edge(p), p.y);
            if ((end - p).magnitude < 0.5f) return pts.Count >= 2 ? pts : null;
            pts.Add(end);
            return pts;
        }
    }
}
