using House4696.Core;
using UnityEngine;
using static House4696.House.HouseSpec;
using static House4696.House.Interior.InteriorPlan;

namespace House4696.House.Interior
{
    /// <summary>Room-by-room furnishing. Coordinates are world metres (see <see cref="InteriorPlan"/> for the room outlines).</summary>
    public sealed partial class InteriorBuilder
    {
        const float G = FloorY, U = UpperFloorY;
        static readonly float ToPosX = Shapes.Facing(Vector3.right), ToNegX = Shapes.Facing(Vector3.left),
                              ToPosZ = Shapes.Facing(Vector3.forward), ToNegZ = Shapes.Facing(Vector3.back);

        void FurnishRooms()
        {
            Living();
            Kitchen();
            Hall();
            GuestRoom();
            GroundBath();
            GroundWardrobe();
            BoilerRoom();
            MasterBedroom();
            MasterEnsuite();
            FamilyBath();
            UpperHall();
            BackBedroom();
            FrontBedroom();
        }

        // ================================================================== ground floor
        void Living()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            // double-height media wall on the hall-side wall
            using (f.Place(new Vector3(FinRightX0, G, 2.2f), ToNegX)) _k.MediaWall(f, 3.7f, UpperCeil - G);
            using (d.Place(new Vector3(7.1f, G, 2.4f))) _k.Rug(d, 3.4f, 3.1f, _m.Rug, _m.RugDark);

            using (f.Place(new Vector3(5.8f, G, 2.4f), ToPosX)) _k.Sofa(f, 3.2f, 1.0f, _m.Boucle, _m.Terracotta, chaise: true);
            using (f.Place(new Vector3(6.95f, G, 2.05f))) _k.RoundTable(f, 0.5f, 0.34f, _m.Travertine);
            using (f.Place(new Vector3(7.62f, G, 2.8f))) _k.RoundTable(f, 0.32f, 0.26f, _m.Walnut);
            _k.Vase(d, new Vector3(6.85f, G + 0.34f, 1.95f), 0.4f, _m.Charcoal, 2);
            _k.Books(d, new Vector3(7.15f, G + 0.34f, 2.25f), 0.2f, 0.035f, 3, true);
            _k.Vase(d, new Vector3(7.62f, G + 0.26f, 2.8f), 0.3f, _m.Stoneware, 1);

            using (f.Place(new Vector3(8.2f, G, 0.95f), Shapes.Facing(new Vector3(-0.7f, 0, 1f)))) _k.Armchair(f, _m.Linen, _m.Walnut);
            using (f.Place(new Vector3(8.15f, G, 4.35f), Shapes.Facing(new Vector3(-0.6f, 0, -1f)))) _k.LoungeChair(f);
            using (f.Place(new Vector3(8.72f, G, 0.36f))) _k.FloorLamp(f);
            using (f.Place(new Vector3(7.5f, G, 0.62f))) _k.WireTable(f, 0.22f, 0.42f);
            _k.Books(d, new Vector3(7.5f, G + 0.425f, 0.62f), 0.2f, 0.03f, 2, true);
            using (f.Place(new Vector3(5.95f, G, 0.5f))) _k.RoundTable(f, 0.22f, 0.5f, _m.Walnut);
            _k.TableLamp(d, new Vector3(5.95f, G + 0.5f, 0.5f), 0.17f);

            // sofa console against the back of the sofa, art on the fin wall above it
            f.RoundBox(new Vector3(4.86f, G + 0.7f, 1.25f), new Vector3(5.22f, G + 0.74f, 3.55f), 0.008f, _m.Walnut);
            foreach (var z in new[] { 1.3f, 3.46f })
                f.Box(new Vector3(4.88f, G, z), new Vector3(5.2f, G + 0.7f, z + 0.04f), _m.Walnut);
            _k.TableLamp(d, new Vector3(5.04f, G + 0.74f, 1.55f), 0.16f);
            _k.Vase(d, new Vector3(5.04f, G + 0.74f, 2.45f), 0.42f, _m.Stoneware, 0);
            _k.Books(d, new Vector3(5.04f, G + 0.74f, 3.1f), 0.2f, 0.04f, 3, true);
            _k.Artwork(f, new Vector3(FinLeftX1, G + 1.65f, 1.35f), Vector3.right, 0.8f, 1.0f, 1);

            // big canvas facing the void on the upper gallery wall (reads from the sofa and the garden)
            _k.Artwork(f, new Vector3(FinLeftX1, U + 1.45f, 3.4f), Vector3.right, 1.3f, 1.3f, 0);

            // cluster chandelier in the double-height void
            _k.Chandelier(d, new Vector3(7.06f, UpperCeil, 2.2f), 2.1f, 0.9f, 2.6f, 21, 11);
            Emit("Living", f, d);

            Plant("Olive_Living", new Vector3(5.2f, G, 0.62f), 2.1f, 0.62f, 21, 0.3f, 0.52f);
            Plant("Under_Stair", new Vector3(7.55f, G, 8.4f), 1.8f, 0.55f, 23, 0.27f, 0.46f, _m.Charcoal);
        }

        void Kitchen()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            float tallLen = BackIn - 7.87f;
            using (f.Place(new Vector3(L0, G, 7.87f + tallLen * 0.5f), ToPosX)) _k.TallUnits(f, tallLen, GroundCeil - G, _m.GlossWhite);
            float runX0 = L0 + 0.64f, runX1 = FinLeftX0, runC = (runX0 + runX1) * 0.5f;
            using (f.Place(new Vector3(runC, G, BackIn), ToNegZ)) _k.KitchenBase(f, runX1 - runX0, sinkAt: 2.42f - runC);
            using (f.Place(new Vector3(2.75f, G, 7.8f))) _k.Island(f, 2.0f, 1.0f);
            foreach (var x in new[] { 2.2f, 2.75f, 3.3f })
                using (f.Place(new Vector3(x, G, 7.08f), ToPosZ)) _k.BarStool(f);
            foreach (var x in new[] { 2.25f, 2.75f, 3.25f })
                _k.PendantGlobe(d, new Vector3(x, GroundCeil, 7.8f), 1.05f, 0.13f);

            // counter styling: bowl, bottles, board
            float top = G + 0.9f;
            _k.Vase(d, new Vector3(3.4f, G + 0.92f, 8.0f), 0.34f, _m.Stoneware, 2);
            _k.Vase(d, new Vector3(1.35f, top, 9.72f), 0.3f, _m.Ceramic, 0);
            _k.Vase(d, new Vector3(1.55f, top, 9.78f), 0.22f, _m.Charcoal, 1);
            d.RoundBox(new Vector3(3.6f, top, 9.9f), new Vector3(4.0f, top + 0.5f, 9.93f), 0.01f, _m.Walnut);
            d.RoundBox(new Vector3(3.75f, top, 9.84f), new Vector3(4.2f, top + 0.35f, 9.87f), 0.01f, _m.OakLight);

            // dining: oak table for eight under a linear pendant
            using (f.Place(new Vector3(2.6f, G, 4.85f))) _k.DiningTable(f, 2.3f, 1.0f);
            foreach (var z in new[] { 4.15f, 4.85f, 5.55f })
            {
                using (f.Place(new Vector3(1.8f, G, z), ToPosX)) _k.DiningChair(f, _m.Linen);
                using (f.Place(new Vector3(3.4f, G, z), ToNegX)) _k.DiningChair(f, _m.Linen);
            }
            using (f.Place(new Vector3(2.6f, G, 3.45f), ToPosZ)) _k.DiningChair(f, _m.Linen);
            using (f.Place(new Vector3(2.6f, G, 6.25f), ToNegZ)) _k.DiningChair(f, _m.Linen);
            _k.LinearPendant(d, new Vector3(2.6f, GroundCeil, 4.85f), 1.45f, 1.8f, alongZ: true);
            _k.Vase(d, new Vector3(2.6f, G + 0.76f, 4.6f), 0.3f, _m.Stoneware, 0);
            _k.Vase(d, new Vector3(2.55f, G + 0.76f, 5.1f), 0.4f, _m.Stoneware, 2);

            // fluted sideboard on the side wall with art and ceramics
            using (f.Place(new Vector3(L0, G, 4.45f), ToPosX)) _k.FlutedCabinet(f, 2.3f, 0.62f, 0.45f, 0.18f);
            float sb = G + 0.18f + 0.62f + 0.025f;
            _k.Vase(d, new Vector3(0.62f, sb, 3.65f), 0.55f, _m.Charcoal, 0);
            _k.Vase(d, new Vector3(0.6f, sb, 3.95f), 0.32f, _m.Stoneware, 1);
            _k.Books(d, new Vector3(0.62f, sb, 5.2f), 0.2f, 0.04f, 4, true);
            _k.Artwork(f, new Vector3(L0, G + 1.9f, 4.45f), Vector3.right, 1.5f, 1.0f, 2);
            Emit("Kitchen", f, d);

            Grass("Kitchen_Corner", new Vector3(4.05f, G, 3.3f), 31, 0.24f, 0.45f);
        }

        void Hall()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            using (f.Place(new Vector3(11.73f, G, 4.5f), ToNegX)) _k.FlutedCabinet(f, 1.3f, 0.35f, 0.38f, 0.55f);
            RoundMirror(f, new Vector3(11.72f, G + 1.65f, 4.5f), Vector3.left, 0.45f);
            _k.TableLamp(d, new Vector3(11.53f, G + 0.925f, 4.0f), 0.16f);
            _k.Vase(d, new Vector3(11.52f, G + 0.925f, 4.95f), 0.3f, _m.Stoneware, 1);

            // bench with cushion and art on the opposite wall
            using (f.Place(new Vector3(FinRightX1, G, 3.0f), ToPosX))
            {
                f.RoundBox(new Vector3(-0.7f, 0.36f, -0.42f), new Vector3(0.7f, 0.42f, 0f), 0.008f, _m.OakLight);
                f.Box(new Vector3(-0.65f, 0, -0.38f), new Vector3(-0.61f, 0.36f, -0.04f), _m.OakLight);
                f.Box(new Vector3(0.61f, 0, -0.38f), new Vector3(0.65f, 0.36f, -0.04f), _m.OakLight);
                f.RoundBox(new Vector3(-0.68f, 0.42f, -0.4f), new Vector3(0.68f, 0.5f, -0.02f), 0.03f, _m.Boucle);
            }
            _k.Artwork(f, new Vector3(FinRightX1, G + 1.55f, 3.0f), Vector3.right, 1.0f, 1.2f, 3);
            using (d.Place(new Vector3(10.72f, G + 0.004f, 3.9f))) _k.Rug(d, 1.1f, 3.4f, _m.RugDark, _m.Linen);
            _k.PendantGlobe(d, new Vector3(10.72f, GroundCeil, 4.2f), 0.85f, 0.22f);
            Emit("Hall", f, d);
            Grass("Hall_Entry", new Vector3(10.0f, G, 2.12f), 33);
        }

        void GuestRoom()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            using (f.Place(new Vector3(R0, G, 8.4f), ToNegX)) _k.Bed(f, 1.6f, 2.0f, _m.Linen, _m.Sage);
            foreach (var z in new[] { 7.25f, 9.55f })
            {
                using (f.Place(new Vector3(R0, G, z), ToNegX)) _k.Nightstand(f, lamp: false);
                _k.PendantGlobe(d, new Vector3(13.95f, GroundCeil, z), 1.75f, 0.1f);
            }
            using (d.Place(new Vector3(12.7f, G, 8.4f))) _k.Rug(d, 2.4f, 2.8f, _m.Rug, null);
            using (f.Place(new Vector3(FinRightX1, G, 8.3f), ToPosX)) _k.FlutedCabinet(f, 1.6f, 0.7f, 0.45f, 0.12f);
            _k.Artwork(f, new Vector3(FinRightX1, G + 1.75f, 8.3f), Vector3.right, 1.2f, 0.9f, 1);
            _k.Vase(d, new Vector3(9.95f, G + 0.845f, 7.8f), 0.4f, _m.Stoneware, 0);
            using (f.Place(new Vector3(10.75f, G, 9.4f), Shapes.Facing(new Vector3(0.4f, 0, -1f)))) _k.Armchair(f, _m.Boucle, _m.OakLight);
            Emit("Guest", f, d);
        }

        void GroundBath()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            TilePanel(f, 11.83f, R0, 4.19f, 4.2f, G, G + 2.4f, _m.Travertine);
            TilePanel(f, R0 - 0.01f, R0, 4.2f, 5.7f, G, G + 1.44f, _m.Travertine);
            TilePanel(f, R0 - 0.01f, R0, 5.7f, 6.68f, G, G + 1.44f, _m.TileDark);
            TilePanel(f, 12.95f, R0, 6.67f, 6.68f, G, G + 2.4f, _m.TileDark);
            using (f.Place(new Vector3(12.45f, G, 4.2f), ToPosZ)) _k.Vanity(f, 1.1f, 1, 0.7f);
            using (f.Place(new Vector3(R0 - 0.01f, G, 4.8f), ToNegX)) _k.Toilet(f);
            using (f.Place(new Vector3(0, G, 0))) _k.Shower(f, 12.95f, R0 - 0.01f, 5.7f, 6.67f, 12.95f, R0 - 0.01f, GroundCeil - G);
            using (f.Place(new Vector3(13.3f, G, 4.2f), ToPosZ)) _k.TowelRail(f, 0.5f, 1.3f);
            using (d.Place(new Vector3(12.4f, G + 0.004f, 5.4f))) _k.Rug(d, 0.6f, 0.9f, _m.Towel, null);
            Emit("Bath", f, d);
        }

        void GroundWardrobe()
        {
            var f = new MeshBuilder();
            using (f.Place(new Vector3(R0, G, (RightIn + 4.07f) * 0.5f), ToNegX)) _k.Wardrobe(f, 4.07f - RightIn, 2.6f, 0.6f, _m.GlossWhite, 0.55f, handles: false);
            using (f.Place(new Vector3(12.73f, G, RightIn), ToPosZ)) _k.Wardrobe(f, 1.8f, 1.8f, 0.45f, _m.GlossWhite, 0.45f, handles: false);
            f.RoundBox(new Vector3(12.7f, G, 2.95f), new Vector3(13.4f, G + 0.42f, 3.45f), 0.06f, _m.Boucle, 3);
            Emit("Wardrobe", f, null);
        }

        void BoilerRoom()
        {
            var f = new MeshBuilder();
            f.RoundBox(new Vector3(FinLeftX1, G + 1.3f, 9.4f), new Vector3(FinLeftX1 + 0.36f, G + 2.05f, 9.85f), 0.02f, _m.Ceramic);
            f.Cylinder(new Vector3(5.1f, G, 10.45f), 0.28f, 1.7f, _m.Ceramic, 28);
            for (int i = 0; i < 3; i++)
                f.Rod(new Vector3(FinLeftX1 + 0.18f, G + 1.3f, 9.5f + i * 0.12f), new Vector3(FinLeftX1 + 0.18f, G + 0.2f, 9.5f + i * 0.12f), 0.014f, _m.Chrome);
            // washer and dryer stack with a shelf
            f.RoundBox(new Vector3(6.25f, G, 7.3f), new Vector3(6.88f, G + 0.85f, 7.92f), 0.02f, _m.Ceramic);
            f.RoundBox(new Vector3(6.25f, G + 0.86f, 7.3f), new Vector3(6.88f, G + 1.71f, 7.92f), 0.02f, _m.Ceramic);
            foreach (var y in new[] { 0.42f, 1.28f })
                using (f.Place(new Vector3(6.25f, G + y, 7.61f), Quaternion.Euler(0, 0, 90f)))
                    f.Cylinder(new Vector3(0, -0.01f, 0), 0.2f, 0.012f, _m.BlackGlass, 28);
            f.Box(new Vector3(6.4f, G + 2.1f, 7.9f), new Vector3(6.9f, G + 2.13f, 9.5f), _m.OakLight);
            Emit("Boiler", f, null);
        }

        // ================================================================== upper floor
        void MasterBedroom()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            // full-height acoustic slat wall behind the bed
            using (f.Place(new Vector3(FinLeftX0, U, 4.7f), ToNegX)) _k.SlatPanel(f, -1.62f, 1.62f, 0, UpperCeil - U, 0f);
            float wall = FinLeftX0 - 0.03f;
            using (f.Place(new Vector3(wall, U, 4.7f), ToNegX)) _k.Bed(f, 1.8f, 2.1f, _m.Boucle, _m.Terracotta);
            foreach (var z in new[] { 3.5f, 5.9f })
            {
                using (f.Place(new Vector3(wall, U, z), ToNegX)) _k.Nightstand(f, lamp: false);
                _k.PendantGlobe(d, new Vector3(4.12f, UpperCeil, z), 1.75f, 0.1f);
            }
            using (d.Place(new Vector3(2.9f, U, 4.7f))) _k.Rug(d, 2.8f, 3.0f, _m.Rug, _m.RugDark);

            // media wall opposite the bed: floating gloss console with TV, oak cubby shelving beside it
            using (f.Place(new Vector3(L0, U, 5.0f), ToPosX))
            using (d.Place(new Vector3(L0, U, 5.0f), ToPosX))
                _k.TvConsole(f, d, 1.6f, 0.36f, 1.1f);
            using (f.Place(new Vector3(L0, U, 3.55f), ToPosX))
            using (d.Place(new Vector3(L0, U, 3.55f), ToPosX))
                _k.CubbyShelf(f, d, 0.9f, 2.4f, 0.32f, 41);
            using (f.Place(new Vector3(1.45f, U, 3.55f), Shapes.Facing(new Vector3(1f, 0, 0.7f)))) _k.Armchair(f, _m.Boucle, _m.OakLight);
            Drapes(d, 1.12f, 1.5f, LeftIn + 0.12f, U, UpperCeil - 0.02f);
            Drapes(d, 3.35f, 3.73f, LeftIn + 0.12f, U, UpperCeil - 0.02f);
            Emit("Master", f, d);
        }

        void MasterEnsuite()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            // walk-in wardrobe
            float len = BackIn - 7.35f, c = 7.35f + len * 0.5f;
            using (f.Place(new Vector3(L0, U, c), ToPosX)) _k.Wardrobe(f, len, 2.6f, 0.6f, _m.Walnut);
            using (f.Place(new Vector3(2.42f, U, c), ToNegX)) _k.Wardrobe(f, len, 2.6f, 0.5f, _m.Walnut);
            // shower room
            TilePanel(f, 2.54f, FinLeftX0, BackIn - 0.01f, BackIn, U, U + 0.94f, _m.TileDark);
            TilePanel(f, FinLeftX0 - 0.01f, FinLeftX0, 7.35f, BackIn, U, U + 2.4f, _m.Travertine);
            TilePanel(f, 2.54f, 2.55f, 9.0f, BackIn, U, U + 2.4f, _m.TileDark);
            using (f.Place(new Vector3(FinLeftX0 - 0.01f, U, 8.3f), ToNegX)) _k.Vanity(f, 1.0f, 1, 0.65f);
            using (f.Place(new Vector3(2.55f, U, 8.45f), ToPosX)) _k.Toilet(f);
            using (f.Place(new Vector3(0, U, 0))) _k.Shower(f, 2.55f, FinLeftX0 - 0.01f, 9.0f, BackIn - 0.01f, 3.2f, FinLeftX0 - 0.01f, UpperCeil - U);
            Emit("Ensuite", f, d);
        }

        void FamilyBath()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            TilePanel(f, FinLeftX1, FinLeftX1 + 0.012f, 7.47f, BayIn, U, UpperCeil, _m.Travertine);
            TilePanel(f, FinLeftX1, 6.9f, BayIn - 0.01f, BayIn, U, U + 0.94f, _m.Travertine);
            using (f.Place(new Vector3(FinLeftX1 + 0.012f, U, 8.75f), ToPosX)) _k.Vanity(f, 1.6f, 2, 0.6f);
            using (f.Place(new Vector3(6.9f, U, 8.6f), ToNegX)) _k.Toilet(f);
            using (f.Place(new Vector3(5.85f, U, 10.2f))) _k.Bathtub(f, 1.6f, 0.76f);
            using (f.Place(new Vector3(6.9f, U, 9.4f), ToNegX)) _k.TowelRail(f, 0.5f, 1.4f);
            using (d.Place(new Vector3(5.85f, U + 0.004f, 9.35f))) _k.Rug(d, 1.1f, 0.6f, _m.Towel, null);
            _k.Chandelier(d, new Vector3(5.85f, UpperCeil, 10.2f), 0.5f, 0.7f, 1.0f, 3, 5);
            Emit("FamilyBath", f, d);
        }

        void UpperHall()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            // built-in walnut bookshelf
            using (f.Place(new Vector3(FinLeftX1, U, 5.3f), ToPosX))
            using (d.Place(new Vector3(FinLeftX1, U, 5.3f), ToPosX))
                _k.CubbyShelf(f, d, 1.7f, 2.5f, 0.34f, 5);
            using (d.Place(new Vector3(6.4f, U, 5.2f))) _k.Rug(d, 2.3f, 1.5f, _m.Rug, null);
            using (f.Place(new Vector3(6.3f, U, 4.97f), ToPosX)) _k.Chaise(f, _m.LeatherWhite, _m.Charcoal);
            using (f.Place(new Vector3(7.62f, U, 4.9f))) _k.WireTable(f, 0.25f, 0.42f);
            _k.Books(d, new Vector3(7.62f, U + 0.425f, 4.9f), 0.2f, 0.03f, 2, true);
            using (f.Place(new Vector3(5.35f, U, 5.62f))) _k.FloorLamp(f);
            _k.Artwork(f, new Vector3(5.37f, U + 1.5f, 7.35f), Vector3.back, 0.9f, 1.2f, 3);
            Emit("UpperHall", f, d);
            Grass("UpperHall", new Vector3(9.05f, U, 5.93f), 37);
        }

        void BackBedroom()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            using (f.Place(new Vector3(12.0f, U, 5.99f), ToPosZ)) _k.SlatPanel(f, -1.8f, 1.8f, 0, UpperCeil - U, 0f);
            float wall = 5.99f + 0.03f;
            using (f.Place(new Vector3(12.0f, U, wall), ToPosZ)) _k.Bed(f, 1.8f, 2.1f, _m.Linen, _m.Charcoal);
            foreach (var x in new[] { 10.8f, 13.2f })
                using (f.Place(new Vector3(x, U, wall), ToPosZ)) _k.Nightstand(f);
            using (d.Place(new Vector3(12.0f, U, 7.3f))) _k.Rug(d, 3.0f, 2.5f, _m.RugDark, _m.Rug);
            using (f.Place(new Vector3(FinRightX1, U, 8.6f), ToPosX)) _k.Wardrobe(f, 2.7f, UpperCeil - U, 0.6f, _m.GlossWhite, 0.54f, handles: false);
            using (f.Place(new Vector3(13.6f, U, 8.95f), Shapes.Facing(new Vector3(-1f, 0, -0.4f)))) _k.Armchair(f, _m.Charcoal, _m.Walnut);
            using (f.Place(new Vector3(13.95f, U, 9.6f))) _k.FloorLamp(f);
            Emit("BackBedroom", f, d);
        }

        void FrontBedroom()
        {
            var f = new MeshBuilder(); var d = new MeshBuilder();
            using (f.Place(new Vector3(12.0f, U, 5.87f), ToNegZ)) _k.Bed(f, 1.6f, 2.0f, _m.Sage, _m.Terracotta);
            foreach (var x in new[] { 10.9f, 13.1f })
                using (f.Place(new Vector3(x, U, 5.87f), ToNegZ)) _k.Nightstand(f);
            using (d.Place(new Vector3(12.0f, U, 4.6f))) _k.Rug(d, 2.6f, 2.4f, _m.Rug, _m.Sage);
            using (f.Place(new Vector3(FinRightX1, U, 3.7f), ToPosX)) _k.Wardrobe(f, 1.8f, UpperCeil - U, 0.6f, _m.GlossWhite, 0.6f, handles: false);
            using (f.Place(new Vector3(FinRightX1, U, 2.33f), ToPosX))
            using (d.Place(new Vector3(FinRightX1, U, 2.33f), ToPosX))
                _k.CubbyShelf(f, d, 0.86f, 2.5f, 0.34f, 23);
            using (f.Place(new Vector3(R0, U, 2.75f), ToNegX))
            using (d.Place(new Vector3(R0, U, 2.75f), ToNegX))
                _k.TvConsole(f, d, 1.6f, 0.36f, 1.0f);
            Drapes(d, 10.62f, 11.0f, RightIn + 0.12f, U, UpperCeil - 0.02f);
            Drapes(d, 12.95f, 13.33f, RightIn + 0.12f, U, UpperCeil - 0.02f);
            Emit("FrontBedroom", f, d);
        }

        // ================================================================== small builders used by several rooms
        void TilePanel(MeshBuilder mb, float x0, float x1, float z0, float z1, float y0, float y1, Material m) =>
            mb.Box(new Vector3(x0, y0, z0), new Vector3(x1, y1, z1), m);

        void RoundMirror(MeshBuilder mb, Vector3 c, Vector3 n, float r)
        {
            using (mb.Place(c, Quaternion.FromToRotation(Vector3.down, n)))
            {
                mb.Disk(Vector3.zero, r, _m.Mirror, true, 48);
                mb.Lathe(Vector3.zero, new[] { new Vector2(r + 0.012f, 0.012f), new Vector2(r + 0.012f, -0.006f), new Vector2(r, -0.006f) }, 48, _m.Brass);
            }
        }

        /// <summary>Heavy linen drape: soft vertical folds along X at depth z.</summary>
        void Drapes(MeshBuilder mb, float x0, float x1, float z, float y0, float y1)
        {
            int n = Mathf.Max(3, Mathf.RoundToInt((x1 - x0) / 0.065f));
            for (int i = 0; i < n; i++)
            {
                float x = Mathf.Lerp(x0, x1, (i + 0.5f) / n);
                float dz = (i % 2 == 0 ? 0.025f : -0.01f);
                mb.Lathe(new Vector3(x, y0 + 0.01f, z + dz), new[] { new Vector2(0.042f, 0), new Vector2(0.04f, y1 - y0 - 0.01f) }, 10, _m.Linen);
            }
            mb.Rod(new Vector3(x0 - 0.1f, y1 - 0.03f, z), new Vector3(x1 + 0.1f, y1 - 0.03f, z), 0.012f, _m.BlackMetal);
        }
    }
}
