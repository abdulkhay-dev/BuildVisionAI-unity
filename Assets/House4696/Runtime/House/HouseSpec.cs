using System.Collections.Generic;
using UnityEngine;

namespace House4696.House
{
    public enum Finish { Stone, Wood, Stucco, Plinth }

    public enum OpeningKind { Window, Glazing, EntryDoor, SolidDoor }

    public enum CurtainSide { None, Full, Left, Right }

    /// <summary>Opening in a wall, in world coordinates along the wall (X for front/back walls, Z for side walls).</summary>
    public sealed class Opening
    {
        public float From, To, Y0, Y1;
        public OpeningKind Kind = OpeningKind.Window;
        public int Columns = 1;
        public float[] Transoms = new float[0];
        public CurtainSide Curtain = CurtainSide.None;
        public float CurtainFraction = 0.35f;
    }

    public sealed class FinishZone
    {
        public float From, To, Y0, Y1;
        public Finish Finish;
    }

    public enum Facing { Front, Back, Left, Right } // outward normal: -Z, +Z, -X, +X

    /// <summary>
    /// One exterior wall face. <see cref="Plane"/> is the coordinate of the outer structural face
    /// (Z for front/back, X for left/right); From/To run along the wall in world units.
    /// </summary>
    public sealed class WallSpec
    {
        public string Name;
        public Facing Facing;
        public float Plane, From, To, Y0, Y1;
        public float Thickness = HouseSpec.WallThickness;
        public Finish Default = Finish.Stone;
        public bool CornerAtFrom, CornerAtTo;  // outside corners: cladding wraps past the wall end
        public readonly List<FinishZone> Zones = new List<FinishZone>();
        public readonly List<Opening> Openings = new List<Opening>();

        public WallSpec Zone(float from, float to, float y0, float y1, Finish f)
        {
            Zones.Add(new FinishZone { From = from, To = to, Y0 = y0, Y1 = y1, Finish = f });
            return this;
        }

        public WallSpec Open(float from, float to, float y0, float y1, OpeningKind kind = OpeningKind.Window,
                             int columns = 1, float[] transoms = null, CurtainSide curtain = CurtainSide.None, float curtainFraction = 0.35f)
        {
            Openings.Add(new Opening
            {
                From = from, To = to, Y0 = y0, Y1 = y1, Kind = kind, Columns = columns,
                Transoms = transoms ?? new float[0], Curtain = curtain, CurtainFraction = curtainFraction
            });
            return this;
        }

        public Vector3 Normal => Facing == Facing.Front ? Vector3.back : Facing == Facing.Back ? Vector3.forward
                               : Facing == Facing.Left ? Vector3.left : Vector3.right;

        /// <summary>Wall axis pointing to the viewer's right when looking at the face from outside.</summary>
        public Vector3 Axis => Vector3.Cross(Vector3.up, -Normal).normalized;

        /// <summary>Origin on the outer plane such that world coordinate "along" maps to s = dot(p - origin, Axis).</summary>
        public Vector3 Origin => Facing == Facing.Front || Facing == Facing.Back ? new Vector3(0, 0, Plane) : new Vector3(Plane, 0, 0);

        public float ToS(float along)
        {
            Vector3 p = Facing == Facing.Front || Facing == Facing.Back ? new Vector3(along, 0, Plane) : new Vector3(Plane, 0, along);
            return Vector3.Dot(p - Origin, Axis);
        }
    }

    /// <summary>
    /// Geometry of project 46-96 (catalog-plans.ru), measured from the floor plans and orthographic facades.
    /// World frame: X along the front facade (0 = left outer face, 14.62 = right), Y up (0 = finished grade),
    /// Z into the house (0 = front face of the living-room glazing fins, 11.16 = rear of the stair bay).
    /// </summary>
    public static class HouseSpec
    {
        // --- overall
        public const float Width = 14.62f;
        public const float WallThickness = 0.38f;

        // --- levels (m above grade)
        public const float FloorY = 0.30f;       // ±0.000 finished floor
        public const float StepY = 0.15f;        // intermediate step
        public const float BandBottom = 3.35f;   // inter-floor belt / balcony slab edge
        public const float BandTop = 3.88f;
        public const float UpperFloorY = 3.90f;
        public const float SoffitY = 6.74f;      // canopy underside
        public const float CanopyTop = 7.30f;
        public const float CanopyCoping = 0.075f; // dark metal flashing on the canopy edge
        public const float ParapetTop = 7.96f;
        public const float WindowHead = 6.50f;    // upper windows stop ~0.24 m below the soffit
        public const float GlazingHead = 6.48f;   // living-room / stair glazing head

        // --- blocks in plan
        public const float LeftFrontZ = 2.52f;   // kitchen / bedroom front wall (behind terrace & balcony)
        public const float RightFrontZ = 1.51f;  // porch back wall / bedroom front wall
        public const float BackZ = 10.35f;
        public const float BumpBackZ = 11.16f;   // boiler room & stair bay
        public const float FinLeftX0 = 4.41f, FinLeftX1 = 4.79f;
        public const float FinRightX0 = 9.33f, FinRightX1 = 9.72f;
        public const float BumpX0 = 4.39f, BumpX1 = 9.72f;

        // --- canopies (flat roof overhangs, ~1 m past each block's walls)
        public static readonly (float x0, float x1, float z0, float z1)[] Canopies =
        {
            (-1.00f, 3.35f, 1.49f, 11.34f),   // left block
            (3.35f, 10.72f, -1.00f, 12.16f),  // central double-height block (projects furthest)
            (10.72f, 15.62f, 0.51f, 11.34f),  // right block
        };

        // --- parapet volumes (building outline above the canopies)
        public static readonly (float x0, float x1, float z0, float z1)[] Parapets =
        {
            (0f, FinLeftX0, LeftFrontZ, BackZ),
            (FinLeftX0, FinRightX1, 0f, BumpBackZ),
            (FinRightX1, Width, RightFrontZ, BackZ),
        };

        // --- columns (stone clad)
        public static readonly (float x0, float x1, float z0, float z1)[] Columns =
        {
            (0.05f, 0.40f, 0.05f, 0.91f),     // terrace column
            (14.24f, 14.58f, 0.05f, 0.66f),   // porch column
        };

        public static readonly float[] GlazingTransoms = { 3.31f, 3.99f };

        public static List<WallSpec> Walls()
        {
            const float G0 = 0f, G1 = BandBottom, U0 = BandBottom, U1 = SoffitY, P = FloorY;
            var list = new List<WallSpec>();

            // ---------------- front
            list.Add(new WallSpec { Name = "Front_Left", Facing = Facing.Front, Plane = LeftFrontZ, From = 0f, To = FinLeftX0, Y0 = G0, Y1 = U1, Default = Finish.Wood, CornerAtFrom = true }
                .Zone(0, FinLeftX0, G0, P, Finish.Plinth)
                .Open(1.29f, 3.54f, P, 3.29f, OpeningKind.Window, 2, null, CurtainSide.Left, 0.3f)
                .Open(1.31f, 3.55f, 3.95f, WindowHead, OpeningKind.Window, 2, null, CurtainSide.Right, 0.22f));

            list.Add(new WallSpec { Name = "Front_Center", Facing = Facing.Front, Plane = 0f, From = FinLeftX0, To = FinRightX1, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtFrom = true, CornerAtTo = true }
                .Zone(FinLeftX0, FinRightX1, G0, P, Finish.Plinth)
                .Zone(FinLeftX0, FinRightX1, U0, U1, Finish.Stucco)
                .Open(FinLeftX1, FinRightX0, P, GlazingHead, OpeningKind.Glazing, 3, GlazingTransoms, CurtainSide.Full));

            list.Add(new WallSpec { Name = "Front_Right", Facing = Facing.Front, Plane = RightFrontZ, From = FinRightX1, To = Width, Y0 = G0, Y1 = U1, Default = Finish.Wood, CornerAtTo = true }
                .Zone(FinRightX1, Width, G0, P, Finish.Plinth)
                .Zone(12.37f, Width, P, G1, Finish.Stone)
                .Open(10.28f, 11.52f, P, 2.75f, OpeningKind.EntryDoor)
                .Open(12.40f, 13.63f, 2.15f, 2.75f)
                .Open(10.85f, 13.09f, 3.95f, WindowHead, OpeningKind.Window, 2, null, CurtainSide.Left, 0.4f));

            // ---------------- left side
            list.Add(new WallSpec { Name = "Left_Main", Facing = Facing.Left, Plane = 0f, From = LeftFrontZ, To = BackZ, Y0 = G0, Y1 = U1, Default = Finish.Wood, CornerAtFrom = true, CornerAtTo = true }
                .Zone(LeftFrontZ, BackZ, G0, P, Finish.Plinth)
                .Zone(5.92f, BackZ, P, G1, Finish.Stone)
                .Open(5.92f, 6.96f, P, 3.29f)
                .Open(5.91f, 6.94f, 3.95f, WindowHead));

            list.Add(new WallSpec { Name = "Left_Fin", Facing = Facing.Left, Plane = FinLeftX0, From = 0f, To = LeftFrontZ, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtFrom = true }
                .Zone(0f, LeftFrontZ, U0, U1, Finish.Stucco));

            list.Add(new WallSpec { Name = "Left_Bay", Facing = Facing.Left, Plane = BumpX0, From = BackZ, To = BumpBackZ, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtTo = true }
                .Zone(BackZ, BumpBackZ, G0, P, Finish.Plinth)
                .Zone(BackZ, BumpBackZ, U0, U1, Finish.Wood));

            // ---------------- right side
            list.Add(new WallSpec { Name = "Right_Main", Facing = Facing.Right, Plane = Width, From = RightFrontZ, To = BackZ, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtFrom = true, CornerAtTo = true }
                .Zone(RightFrontZ, BackZ, G0, P, Finish.Plinth)
                .Zone(3.94f, 7.89f, P, G1, Finish.Wood)
                .Zone(RightFrontZ, BackZ, U0, U1, Finish.Wood)
                .Open(5.41f, 6.45f, 1.74f, 2.73f)
                .Open(3.90f, 4.94f, 3.95f, WindowHead)
                .Open(6.91f, 7.97f, 3.95f, WindowHead));

            list.Add(new WallSpec { Name = "Right_Fin", Facing = Facing.Right, Plane = FinRightX1, From = 0f, To = RightFrontZ, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtFrom = true }
                .Zone(0f, RightFrontZ, U0, U1, Finish.Stucco));

            list.Add(new WallSpec { Name = "Right_Bay", Facing = Facing.Right, Plane = BumpX1, From = BackZ, To = BumpBackZ, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtTo = true }
                .Zone(BackZ, BumpBackZ, G0, P, Finish.Plinth)
                .Zone(BackZ, BumpBackZ, U0, U1, Finish.Wood));

            // ---------------- back
            list.Add(new WallSpec { Name = "Back_Left", Facing = Facing.Back, Plane = BackZ, From = 0f, To = BumpX0, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtFrom = true }
                .Zone(0f, BumpX0, G0, P, Finish.Plinth)
                .Zone(0f, BumpX0, U0, U1, Finish.Wood)
                .Open(1.29f, 3.54f, 1.22f, 3.30f, OpeningKind.Window, 2)
                .Open(1.31f, 1.95f, 4.85f, WindowHead)
                .Open(2.90f, 3.54f, 4.85f, WindowHead));

            list.Add(new WallSpec { Name = "Back_Right", Facing = Facing.Back, Plane = BackZ, From = BumpX1, To = Width, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtTo = true }
                .Zone(BumpX1, Width, G0, P, Finish.Plinth)
                .Zone(BumpX1, Width, U0, U1, Finish.Wood)
                .Open(10.85f, 13.09f, 1.22f, 3.30f, OpeningKind.Window, 2)
                .Open(10.85f, 13.09f, 3.95f, WindowHead, OpeningKind.Window, 2));

            list.Add(new WallSpec { Name = "Back_Bay", Facing = Facing.Back, Plane = BumpBackZ, From = BumpX0, To = BumpX1, Y0 = G0, Y1 = U1, Default = Finish.Stone, CornerAtFrom = true, CornerAtTo = true }
                .Zone(BumpX0, BumpX1, G0, P, Finish.Plinth)
                .Zone(BumpX0, BumpX1, U0, U1, Finish.Wood)
                .Open(5.40f, 6.43f, P, 2.75f, OpeningKind.SolidDoor)
                .Open(5.40f, 6.43f, 4.85f, WindowHead)
                .Open(7.09f, 9.35f, 0.38f, GlazingHead, OpeningKind.Window, 2, GlazingTransoms));

            return list;
        }
    }
}
