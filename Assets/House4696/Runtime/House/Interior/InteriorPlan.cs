using UnityEngine;
using static House4696.House.HouseSpec;

namespace House4696.House.Interior
{
    /// <summary>Door in a partition: [From, To] along the wall's long axis, swinging to the side <see cref="Swing"/> (+1/-1).</summary>
    public readonly struct DoorSpec
    {
        public readonly float From, To, Height;
        public readonly bool HingeAtFrom;
        public readonly int Swing;
        public DoorSpec(float from, float to, float height, bool hingeAtFrom, int swing)
        { From = from; To = to; Height = height; HingeAtFrom = hingeAtFrom; Swing = swing; }
    }

    public readonly struct PartitionSpec
    {
        public readonly string Name;
        public readonly float X0, X1, Z0, Z1, Y0, Y1;
        public readonly DoorSpec[] Doors;
        public PartitionSpec(string name, float x0, float x1, float z0, float z1, float y0, float y1, params DoorSpec[] doors)
        { Name = name; X0 = x0; X1 = x1; Z0 = z0; Z1 = z1; Y0 = y0; Y1 = y1; Doors = doors; }
        public bool AlongX => X1 - X0 >= Z1 - Z0;
    }

    public readonly struct Area
    {
        public readonly float X0, X1, Z0, Z1;
        public Area(float x0, float x1, float z0, float z1) { X0 = x0; X1 = x1; Z0 = z0; Z1 = z1; }
    }

    /// <summary>
    /// Room layout of project 46-96 traced from the catalogue floor plans (same world frame as <see cref="HouseSpec"/>).
    /// Ground: kitchen-dining open to the double-height living room, boiler room, U-stair, entrance hall with
    /// guest bedroom, bathroom and wardrobe. Upper: master suite (wardrobe + bath), family bath, gallery hall,
    /// two bedrooms.
    /// </summary>
    public static class InteriorPlan
    {
        public const float InT = WallThickness;               // 0.38
        public const float L0 = InT, R0 = Width - InT;         // inner faces of the side walls (0.38 / 14.24)
        public const float BackIn = BackZ - InT;               // 9.97
        public const float BayIn = BumpBackZ - InT;            // 10.78
        public const float LeftIn = LeftFrontZ + InT;          // 2.90
        public const float RightIn = RightFrontZ + InT;        // 1.89
        public const float GlazingIn = 0.12f;
        public const float GroundCeil = BandBottom;            // 3.35
        public const float UpperCeil = SoffitY - 0.04f;        // 6.70
        public const float VoidZ = 4.39f;                      // gallery edge above the living room
        public const float DoorG = 2.4f, DoorU = 2.3f;         // door heights above each floor

        // U-stair: 19 risers, flight 1 along the right wall going +Z, landing at the back, flight 2 returning -Z
        public const int Risers = 19, Flight1Risers = 11;
        public const float Rise = (UpperFloorY - FloorY) / Risers;
        public const float Going = 0.26f;
        public const float StairX0 = 7.0f, StairMid0 = 8.13f, StairMid1 = 8.20f, StairX1 = FinRightX0; // 9.33
        public const float StairZ0 = 6.75f;
        public static float LandingZ => StairZ0 + (Flight1Risers - 1) * Going;                       // 9.35
        public static float LandingY => FloorY + Flight1Risers * Rise;
        public static float StairTopZ => LandingZ - (Risers - Flight1Risers - 1) * Going;              // 7.53

        public static PartitionSpec[] Partitions()
        {
            const float g0 = FloorY, g1 = GroundCeil, u0 = UpperFloorY, u1 = UpperCeil;
            return new[]
            {
                // ---------------- ground floor
                new PartitionSpec("Kitchen_Boiler", FinLeftX0, FinLeftX1, 7.0f, BackIn, g0, g1, new DoorSpec(7.75f, 8.55f, DoorG - 0.2f, true, +1)),
                new PartitionSpec("Boiler_Front", FinLeftX1, StairX0, 7.0f, 7.12f, g0, g1),
                new PartitionSpec("Boiler_Stair", 6.9f, StairX0, 7.12f, BayIn, g0, g1),
                new PartitionSpec("Stair_Guest", FinRightX0, FinRightX1, 6.7f, BackZ, g0, g1),
                new PartitionSpec("Living_Hall", FinRightX0, FinRightX1, RightFrontZ, 4.16f, g0, g1),
                new PartitionSpec("Hall_Guest", FinRightX1, R0, 6.68f, 6.8f, g0, g1, new DoorSpec(10.2f, 11.0f, DoorG, true, +1)),
                new PartitionSpec("Hall_Bath", 11.73f, 11.83f, RightIn, 6.68f, g0, g1,
                    new DoorSpec(5.6f, 6.4f, DoorG, false, +1), new DoorSpec(2.6f, 3.4f, DoorG, true, +1)),
                new PartitionSpec("Bath_Wardrobe", 11.83f, R0, 4.07f, 4.19f, g0, g1),

                // ---------------- upper floor
                new PartitionSpec("Master_Hall", FinLeftX0, FinLeftX1, LeftFrontZ, BackIn, u0, u1, new DoorSpec(6.3f, 7.1f, DoorU, false, -1)),
                new PartitionSpec("Master_Ensuite", L0, FinLeftX0, 7.23f, 7.35f, u0, u1,
                    new DoorSpec(1.1f, 1.8f, DoorU - 0.1f, true, +1), new DoorSpec(2.95f, 3.65f, DoorU - 0.1f, false, +1)),
                new PartitionSpec("Wardrobe_Bath", 2.42f, 2.54f, 7.35f, BackIn, u0, u1),
                new PartitionSpec("Bath_Hall", FinLeftX1, StairX0, 7.35f, 7.47f, u0, u1, new DoorSpec(5.95f, 6.7f, DoorU, false, +1)),
                new PartitionSpec("Bath_Stair", 6.9f, StairX0, 7.47f, BayIn, u0, u1),
                new PartitionSpec("Hall_Bedrooms", FinRightX0, FinRightX1, RightFrontZ, BackZ, u0, u1,
                    new DoorSpec(4.85f, 5.65f, DoorU, true, +1), new DoorSpec(6.2f, 7.0f, DoorU, false, +1)),
                new PartitionSpec("Bedrooms", FinRightX1, R0, 5.87f, 5.99f, u0, u1),
            };
        }

        // floor slabs (top at FloorY) and roof ceiling
        public static readonly Area[] GroundAreas =
        {
            new Area(L0, R0, LeftIn, BackIn),
            new Area(FinLeftX1, FinRightX0, GlazingIn, LeftIn),
            new Area(FinRightX1, R0, RightIn, LeftIn),
            new Area(FinLeftX1, FinRightX0, BackIn, BayIn),
        };

        // upper slab (BandBottom..UpperFloorY): void over the living room, opening over the stair
        public static Area[] UpperSlab() => new[]
        {
            new Area(L0, FinLeftX1, LeftIn, BackIn),
            new Area(FinLeftX1, FinRightX0, VoidZ, StairTopZ),
            new Area(FinLeftX1, StairX0, StairTopZ, BayIn),
            new Area(FinRightX0, R0, RightIn, BackIn),
        };

        // tiled floors (everything else is oak)
        public static readonly Area[] TiledGround =
        {
            new Area(FinRightX1, 11.73f, RightIn, 6.68f),     // entrance hall
            new Area(11.83f, R0, 4.19f, 6.68f),               // bathroom
            new Area(FinLeftX1, 6.9f, 7.12f, BayIn),          // boiler room
        };

        public static readonly Area[] TiledUpper =
        {
            new Area(2.54f, FinLeftX0, 7.35f, BackIn),        // master en-suite
            new Area(FinLeftX1, 6.9f, 7.47f, BayIn),          // family bathroom
        };
    }
}
