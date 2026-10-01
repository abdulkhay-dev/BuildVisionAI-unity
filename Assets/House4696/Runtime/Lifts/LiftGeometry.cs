using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>
    /// Where a lift is, in plan and in height. Local frame: origin = <see cref="LiftDef.Position"/> at grade (y 0), +Z =
    /// the direction the landing doors face (into the hall), so +X is on the LEFT of someone in the hall facing the doors
    /// (and on the right inside the car, facing out). The shaft lies behind the origin: its front wall from z −T to 0, the clear shaft (AH × BH) from
    /// z −T − BH to −T. Heights are absolute.
    /// </summary>
    public sealed class LiftGeometry
    {
        public readonly LiftDef Def;
        public readonly LiftSpec Spec;
        public readonly Matrix4x4 ToWorld;
        /// <summary>Shaft wall thickness (0 for an author-walled or glass shaft's structure).</summary>
        public readonly float T;
        /// <summary>Clear shaft width and depth (AH, BH).</summary>
        public readonly float W, D;
        /// <summary>Storeys with a landing door (low → high), the lowest and highest stop, where the car stands.</summary>
        public readonly List<LevelDef> Stops = new List<LevelDef>();
        public readonly LevelDef Lowest, Highest, Parked;
        /// <summary>Bottom of the pit and the underside of the shaft's head (absolute).</summary>
        public readonly float PitBottom, Top;
        /// <summary>Car: centre x, front face z (the car door line), width, depth (local, metres).</summary>
        public readonly float CarX, CarFront, CarW, CarD;
        /// <summary>
        /// Gap between the shaft's front wall and the car front: landing leaves, sill clearance, car leaves (a two-speed
        /// door has its leaves at two depths).
        /// </summary>
        public readonly float FrontGap;
        public readonly string Enclosure;

        public LiftGeometry(LiftDef def, LiftSpec spec, IList<LevelDef> levels)
        {
            Def = def; Spec = spec;
            ToWorld = Matrix4x4.TRS(new Vector3(def.Position.x, 0f, def.Position.y), Quaternion.Euler(0f, def.Rotation, 0f), Vector3.one);
            Enclosure = (def.Shaft ?? (spec.Panoramic ? "glass" : "concrete")).ToLowerInvariant();
            T = Enclosure == "concrete" ? Mathf.Clamp(def.Wall ?? 0.2f, 0.1f, 0.4f) : Enclosure == "glass" ? 0.06f : 0f;
            W = spec.ShaftWidth; D = spec.ShaftDepth;

            LevelDef Find(string id) => id == null ? null : ((List<LevelDef>)levels).Find(l => l.Id == id);
            var from = Find(def.From) ?? (levels.Count > 0 ? levels[0] : null);
            var to = Find(def.To) ?? (levels.Count > 0 ? levels[levels.Count - 1] : null);
            if (from != null && to != null)
                foreach (var l in levels)
                    if (l.Elevation >= from.Elevation - 0.01f && l.Elevation <= to.Elevation + 0.01f && (def.Skip == null || !def.Skip.Contains(l.Id)))
                        Stops.Add(l);
            if (Stops.Count == 0 && from != null) Stops.Add(from);
            Lowest = Stops.Count > 0 ? Stops[0] : new LevelDef();
            Highest = Stops.Count > 0 ? Stops[Stops.Count - 1] : Lowest;
            Parked = Find(def.Parked) is LevelDef p && Stops.Contains(p) ? p : Lowest;
            PitBottom = Lowest.Elevation - spec.Pit;
            Top = Highest.Elevation + spec.Overhead;

            CarW = spec.CarWidth; CarD = spec.CarDepth;
            FrontGap = spec.DoorType == "2s" ? 0.15f : 0.115f;
            CarFront = -T - FrontGap;
            // a side counterweight runs between the car and one side wall: the car moves to the other side
            float spare = Mathf.Max(0f, (W - CarW) * 0.5f - 0.12f);
            bool sideCw = spec.Model?.Counterweight == "side";
            bool cwLeft = def.Side != "right";        // left seen from the landing = +X
            CarX = sideCw ? (cwLeft ? -spare : spare) : 0f;
        }

        /// <summary>Local point (x, y, z) to world.</summary>
        public Vector3 World(float x, float y, float z) => ToWorld.MultiplyPoint3x4(new Vector3(x, y, z));

        public Vector2 Plan(float x, float z) { var p = World(x, 0f, z); return new Vector2(p.x, p.z); }

        /// <summary>The clear shaft in plan (counter-clockwise, world): what every floor it crosses is cut by.</summary>
        public Vector2[] Clear => Outline(0f);

        /// <summary>The shaft with its walls in plan (counter-clockwise, world).</summary>
        public Vector2[] Footprint => Outline(T);

        /// <summary>
        /// Shaft outline grown by <paramref name="grow"/>: a rectangle; panoramic shafts end in a half circle or a
        /// chamfered nose at the back (the side away from the doors).
        /// </summary>
        public Vector2[] Outline(float grow)
        {
            float x0 = -W * 0.5f - grow, x1 = W * 0.5f + grow, zf = -T + grow, zb = -T - D - grow;
            var pts = new List<Vector2>();
            if (Spec.Shape == "semicircle")
            {
                float r = (x1 - x0) * 0.5f, zc = zb + r;
                pts.Add(new Vector2(x1, zf));
                pts.Add(new Vector2(x0, zf));
                const int n = 16;
                for (int i = 0; i <= n; i++)
                {
                    float a = Mathf.PI * i / n;                       // from −X round the back to +X
                    pts.Add(new Vector2(-Mathf.Cos(a) * r, zc - Mathf.Sin(a) * r));
                }
            }
            else if (Spec.Shape == "rhombus")
            {
                float c = (x1 - x0) * 0.3f;
                pts.Add(new Vector2(x1, zf));
                pts.Add(new Vector2(x0, zf));
                pts.Add(new Vector2(x0, zb + c));
                pts.Add(new Vector2(x0 + c, zb));
                pts.Add(new Vector2(x1 - c, zb));
                pts.Add(new Vector2(x1, zb + c));
            }
            else
            {
                pts.Add(new Vector2(x1, zf));
                pts.Add(new Vector2(x0, zf));
                pts.Add(new Vector2(x0, zb));
                pts.Add(new Vector2(x1, zb));
            }
            var world = new List<Vector2>(pts.Count);
            foreach (var q in pts) world.Add(Plan(q.x, q.y));
            return Polygon.CounterClockwise(world).ToArray();
        }

        /// <summary>The shaft passes through a floor or ceiling plane at this height (open from the pit to its head).</summary>
        public bool Crosses(float y) => y > PitBottom + 0.05f && y < Top - 0.05f;

        /// <summary>Landing door opening on the shaft's front wall at a stop: local x range and height.</summary>
        public (float x0, float x1) DoorX => (CarX - Spec.DoorWidth * 0.5f, CarX + Spec.DoorWidth * 0.5f);

        /// <summary>Plan point in front of the landing doors, <paramref name="ahead"/> metres into the hall.</summary>
        public Vector2 Landing(float ahead) => Plan(CarX, ahead);
    }
}
