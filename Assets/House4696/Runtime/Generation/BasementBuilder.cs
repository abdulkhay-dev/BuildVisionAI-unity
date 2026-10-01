using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>
    /// What a storey below grade needs outside it: a concrete light well (приямок) in front of every window whose
    /// bottom is below the ground, and an open stair pit leading up to the ground in front of every exterior door
    /// below it — with a kerb and guards along the open edges. The ground (lawn, gravel apron, natural terrain) is cut
    /// away over the basement footprint and the pits (<see cref="HouseContext.GroundCuts"/>), so nothing grows or
    /// collides inside them. Grade at the house walls is 0 (the house stands on a level pad).
    /// </summary>
    public sealed class BasementBuilder
    {
        public enum PitKind { Window, Stair }

        public sealed class Pit
        {
            public PitKind Kind;
            public OpeningDef Opening;
            public WallFrame Wall;
            /// <summary>Wall-space extent of the inner pit: s along the wall, d outward from the outer face; floor height.</summary>
            public float S0, S1, Depth, Floor;
            /// <summary>Plan outline including its walls (convex, counter-clockwise).</summary>
            public Vector2[] Cut;
            public int Risers;
        }

        const float Grade = 0f, WallT = 0.15f, Kerb = 0.1f, WellDepth = 0.9f, Landing = 1.2f, Going = 0.3f, MaxRise = 0.175f;
        readonly HouseContext _c;
        public BasementBuilder(HouseContext c) { _c = c; }

        static bool IsDoor(OpeningType t) => t == OpeningType.Door || t == OpeningType.EntryDoor || t == OpeningType.SolidDoor;

        /// <summary>Works out the pits (before anything is built: the site needs them to cut the ground).</summary>
        public void Plan()
        {
            _c.Pits.Clear();
            foreach (var o in _c.Doc.Openings)
            {
                var f = _c.Wall(o.Wall);
                if (f == null || !f.Exterior) continue;
                float bottom = f.Level.Elevation + (IsDoor(o.Type) ? Mathf.Max(0f, o.Sill) : o.Sill);
                if (bottom > Grade - 0.05f) continue;                       // at or above the ground: nothing to dig
                float s0 = f.SAt(o.At), s1 = s0 + o.Width;
                var pit = new Pit { Opening = o, Wall = f };
                if (IsDoor(o.Type))
                {
                    pit.Kind = PitKind.Stair;
                    pit.Risers = Mathf.Max(1, Mathf.CeilToInt((Grade - bottom) / MaxRise));
                    pit.Floor = bottom;
                    pit.S0 = s0 - 0.3f; pit.S1 = s1 + 0.3f;
                    pit.Depth = Landing + (pit.Risers - 1) * Going;
                }
                else
                {
                    pit.Kind = PitKind.Window;
                    pit.Floor = bottom - 0.2f;
                    pit.S0 = s0 - 0.2f; pit.S1 = s1 + 0.2f;
                    pit.Depth = WellDepth;
                }
                float a = pit.S0 - WallT, b = pit.S1 + WallT, d = pit.Depth + (pit.Kind == PitKind.Window ? WallT : 0f);
                pit.Cut = Ccw(new[] { f.Plan(a, 0f), f.Plan(b, 0f), f.Plan(b, d), f.Plan(a, d) });
                _c.Pits.Add(pit);
            }
        }

        static Vector2[] Ccw(Vector2[] p) => Polygon.SignedArea(p) < 0 ? new[] { p[3], p[2], p[1], p[0] } : p;

        public void Build()
        {
            if (_c.Pits.Count == 0) return;
            var concrete = _c.Mats.Get("concrete_smooth", _c.M.Plaster);
            var gravel = _c.Lib.Gravel;
            var elements = new ElementBuilder(_c);
            foreach (var p in _c.Pits)
            {
                var f = p.Wall;
                var mb = new MeshBuilder { Transform = f.ToWorld };
                float bottom = p.Floor - 0.2f, top = Grade + Kerb;
                // floor slab and the walls around the inner pit (d outward: local z = -d)
                Box(mb, p.S0, p.S1, bottom, p.Floor, 0f, p.Depth, p.Kind == PitKind.Window ? gravel : concrete, concrete);
                Box(mb, p.S0 - WallT, p.S0, bottom, top, 0f, p.Depth + (p.Kind == PitKind.Window ? WallT : 0f), concrete, concrete);
                Box(mb, p.S1, p.S1 + WallT, bottom, top, 0f, p.Depth + (p.Kind == PitKind.Window ? WallT : 0f), concrete, concrete);
                string name = (p.Kind == PitKind.Window ? "LightWell_" : "StairPit_") + (p.Opening.Id ?? f.Def.Id);
                if (p.Kind == PitKind.Window)
                {
                    Box(mb, p.S0, p.S1, bottom, top, p.Depth, p.Depth + WallT, concrete, concrete);
                    _c.W.Emit(name, _c.Shell, mb);
                    continue;
                }
                // steps from the landing up to the ground, away from the door
                float rise = (Grade - p.Floor) / p.Risers;
                for (int i = 1; i < p.Risers; i++)
                    Box(mb, p.S0, p.S1, bottom, p.Floor + i * rise, Landing + (i - 1) * Going, Landing + i * Going + 0.02f, _c.Lib.Paver, concrete);
                _c.W.Emit(name, _c.Shell, mb);
                // guards along both long edges, on the kerb
                foreach (float s in new[] { p.S0 - WallT * 0.5f, p.S1 + WallT * 0.5f })
                    elements.Build(new ElementDef
                    {
                        Id = name + (s < p.S0 ? "_guardL" : "_guardR"), Type = ElementType.Railing, Y = top, Height = 0.9f, Style = "metal",
                        Path = new List<Vector2> { f.Plan(s, 0.05f), f.Plan(s, p.Depth) },
                    });
            }
        }

        /// <summary>Box in wall space: s along the wall, y up, d outward from the outer face.</summary>
        static void Box(MeshBuilder mb, float s0, float s1, float y0, float y1, float d0, float d1, Material top, Material rest) =>
            mb.Box(new Vector3(s0, y0, -d1), new Vector3(s1, y1, -d0), BoxMats.All(rest).With(yp: top));
    }
}
