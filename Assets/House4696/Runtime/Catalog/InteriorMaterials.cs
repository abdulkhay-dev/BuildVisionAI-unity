using House4696.Core;
using UnityEngine;

namespace House4696.Catalog
{
    /// <summary>
    /// Palette of the interior: warm minimalism — natural oak, walnut, travertine and calacatta marble,
    /// oatmeal linen and bouclé, black metal and brushed brass accents, warm 2700 K light sources.
    /// </summary>
    public sealed class InteriorMaterials
    {
        public readonly MaterialLibrary Shell;
        public Material Plaster => Shell.InteriorWall;
        public Material Ceiling => Shell.InteriorCeiling;
        public Material Oak => Shell.InteriorFloor;

        public Material Tile, TileDark, Marble, Travertine, Walnut, OakLight,
            Linen, Boucle, Sage, Terracotta, Charcoal, Bedding, Leather, Rug, RugDark, Towel,
            BlackMetal, Brass, Chrome, Ceramic, Stoneware, Mirror, Glass, Screen, BlackGlass,
            LampShade, Globe, Led, Downlight, Fire, Art, Soil,
            GlossWhite, SlatWood, Felt, Cloth, LeatherWhite, WhiteMetal, SoftWhite,
            // doors of the catalogue (House4696.Doors): glass roles, aluminium inserts, the frame's seal
            DoorSatin, DoorAluminium, DoorSeal, DoorLacobelBeige, DoorLacobelWhite, DoorLacobelSmoke, DoorBronze,
            DoorPatinaGold, DoorPatinaSilver, DoorPatinaDark;

        public InteriorMaterials(MaterialLibrary shell)
        {
            Shell = shell;
            Tile = Tex("M_IntTile", new Color(0.93f, 0.91f, 0.88f), "T_Tile", 1.2f, 0.55f, 0.5f);
            TileDark = Tex("M_IntTileDark", new Color(0.36f, 0.35f, 0.34f), "T_Tile", 1.2f, 0.6f, 0.5f);
            Marble = Tex("M_IntMarble", Color.white, "T_Marble", 2f, 0.82f, 0f, normal: false);
            Travertine = Tex("M_IntTravertine", Color.white, "T_Travertine", 1.2f, 0.3f, 0.8f);
            Walnut = Grain("M_IntWalnut", new Color(0.47f, 0.32f, 0.21f), 0.45f);
            OakLight = Grain("M_IntOak", new Color(0.86f, 0.70f, 0.52f), 0.35f);

            Linen = Fabric("M_IntLinen", new Color(0.80f, 0.75f, 0.66f), 0.25f, 1f);
            Boucle = Fabric("M_IntBoucle", new Color(0.93f, 0.90f, 0.84f), 0.1f, 1.8f);
            Sage = Fabric("M_IntSage", new Color(0.50f, 0.57f, 0.48f), 0.25f, 1f);
            Terracotta = Fabric("M_IntTerracotta", new Color(0.70f, 0.39f, 0.26f), 0.2f, 1.2f);
            Charcoal = Fabric("M_IntCharcoal", new Color(0.27f, 0.26f, 0.25f), 0.2f, 1.2f);
            Bedding = Fabric("M_IntBedding", new Color(0.96f, 0.95f, 0.93f), 0.35f, 0.6f);
            Towel = Fabric("M_IntTowel", new Color(0.90f, 0.88f, 0.84f), 0.06f, 2f);
            Rug = Fabric("M_IntRug", new Color(0.84f, 0.80f, 0.72f), 0.12f, 2.4f);
            RugDark = Fabric("M_IntRugDark", new Color(0.36f, 0.33f, 0.30f), 0.12f, 2.4f);
            Leather = Lit("M_IntLeather", new Color(0.50f, 0.28f, 0.15f), 0.48f);

            BlackMetal = Lit("M_IntBlackMetal", new Color(0.035f, 0.035f, 0.035f), 0.45f, 0.6f);
            Brass = Lit("M_IntBrass", new Color(0.80f, 0.62f, 0.36f), 0.72f, 1f);
            Chrome = Lit("M_IntChrome", new Color(0.85f, 0.85f, 0.86f), 0.92f, 1f);
            Ceramic = Lit("M_IntCeramic", new Color(0.95f, 0.94f, 0.92f), 0.86f);
            Stoneware = Lit("M_IntStoneware", new Color(0.74f, 0.70f, 0.63f), 0.3f);
            Mirror = Lit("M_IntMirror", new Color(0.92f, 0.92f, 0.92f), 0.985f, 1f);
            Screen = Lit("M_IntScreen", new Color(0.012f, 0.012f, 0.014f), 0.94f);
            BlackGlass = Lit("M_IntBlackGlass", new Color(0.02f, 0.02f, 0.022f), 0.9f);
            var glass = LitOptions.Of(new Color(0.85f, 0.9f, 0.9f, 0.07f), 0.97f);
            glass.Transparent = true;
            Glass = MaterialLibrary.Lit("M_IntGlass", glass);

            LampShade = Emissive("M_IntLampShade", new Color(0.95f, 0.91f, 0.84f), new Color(0.9f, 0.7f, 0.46f), "T_Fabric", 0.2f);
            Globe = Emissive("M_IntGlobe", new Color(0.95f, 0.93f, 0.90f), new Color(1.35f, 1.1f, 0.8f));
            Led = Emissive("M_IntLed", new Color(1f, 0.9f, 0.75f), new Color(3.2f, 2.3f, 1.3f));
            Downlight = Emissive("M_IntDownlight", new Color(1f, 0.97f, 0.9f), new Color(4f, 3.3f, 2.4f));
            Fire = Emissive("M_IntFire", new Color(1f, 0.5f, 0.2f), new Color(6f, 2.2f, 0.55f));

            var art = LitOptions.Of(Color.white, 0.12f);
            art.Albedo = "T_Art"; art.Tiling = Vector2.one;
            Art = MaterialLibrary.Lit("M_IntArt", art);
            Soil = shell.Soil;

            // high-gloss lacquer (wardrobes, TV console): mirror-like sheen that reads the room through the probes
            GlossWhite = Lit("M_IntGlossWhite", new Color(0.93f, 0.925f, 0.91f), 0.9f);
            // acoustic slat panels: solid-wood slats from the batten atlas (each slat its own plank) on black felt
            SlatWood = MaterialLibrary.Lit("M_IntSlatWood", new LitOptions
            {
                Color = new Color(0.92f, 0.82f, 0.74f), Albedo = "T_Wood", Normal = "T_Wood_N", NormalScale = 0.6f,
                Tiling = new Vector2(1f, 0.5f), Smoothness = 0.38f, ReceiveShadows = true
            });
            Felt = Fabric("M_IntFelt", new Color(0.035f, 0.033f, 0.032f), 0.1f, 1.5f);
            // bedding cloth is seen from both sides where the duvet hangs
            var cloth = new LitOptions
            {
                Color = new Color(0.95f, 0.94f, 0.92f), Albedo = "T_Fabric", Normal = "T_Fabric_N", NormalScale = 0.5f,
                MetersPerTile = 0.3f, Smoothness = 0.12f, TwoSided = true, ReceiveShadows = true
            };
            Cloth = MaterialLibrary.Lit("M_IntCloth", cloth);
            SoftWhite = Fabric("M_IntSoftWhite", new Color(0.93f, 0.92f, 0.9f), 0.25f, 0.8f);
            LeatherWhite = Lit("M_IntLeatherWhite", new Color(0.9f, 0.88f, 0.84f), 0.62f);
            WhiteMetal = Lit("M_IntWhiteMetal", new Color(0.9f, 0.9f, 0.89f), 0.55f, 0.2f);

            // satin (acid-etched) glass: milky, lets light and shapes through faintly
            // (it glows faintly: light passes through and scatters, which a lit transparent surface alone does not show)
            var satin = LitOptions.Of(new Color(0.95f, 0.925f, 0.89f, 0.9f), 0.4f);
            satin.Transparent = true;
            satin.Emission = new Color(0.11f, 0.104f, 0.094f);
            DoorSatin = MaterialLibrary.Lit("M_DoorGlassSatin", satin);
            // aluminium profiles and edges ("МатХром", ALU): brushed, satin sheen
            DoorAluminium = Lit("M_DoorAluminium", new Color(0.78f, 0.78f, 0.80f), 0.62f, 1f);
            DoorSeal = Lit("M_DoorSeal", new Color(0.07f, 0.07f, 0.075f), 0.2f);
            // door furniture: antique bronze (classic handles)
            DoorBronze = Lit("M_DoorBronze", new Color(0.42f, 0.30f, 0.18f), 0.55f, 1f);
            // patina: metallic paint on the crests of classic mouldings (Classico G-27)
            DoorPatinaGold = Lit("M_DoorPatinaGold", new Color(0.86f, 0.66f, 0.34f), 0.5f, 0.8f);
            DoorPatinaSilver = Lit("M_DoorPatinaSilver", new Color(0.80f, 0.80f, 0.80f), 0.5f, 0.8f);
            // toning of milled profiles on veneer doors (fine-line): a dark walnut stain in the channels
            DoorPatinaDark = Lit("M_DoorPatinaDark", new Color(0.17f, 0.105f, 0.065f), 0.35f);
            // lacobel: glass painted on the back — opaque, glossy
            DoorLacobelBeige = Lit("M_DoorLacobelBeige", new Color(0.86f, 0.80f, 0.70f), 0.93f);
            DoorLacobelWhite = Lit("M_DoorLacobelWhite", new Color(0.92f, 0.92f, 0.91f), 0.93f);
            DoorLacobelSmoke = Lit("M_DoorLacobelSmoke", new Color(0.30f, 0.30f, 0.30f), 0.93f);
        }

        static Material Lit(string name, Color c, float smooth, float metallic = 0f)
        {
            var o = LitOptions.Of(c, smooth);
            o.Metallic = metallic;
            return MaterialLibrary.Lit(name, o);
        }

        static Material Tex(string name, Color c, string tex, float meters, float smooth, float normalScale, bool normal = true) =>
            MaterialLibrary.Lit(name, new LitOptions
            {
                Color = c, Albedo = tex, Normal = normal ? tex + "_N" : null, NormalScale = normalScale,
                MetersPerTile = meters, Smoothness = smooth, ReceiveShadows = true
            });

        static Material Grain(string name, Color c, float smooth) => Tex(name, c, "T_Grain", 1f, smooth, 0.5f);

        static Material Fabric(string name, Color c, float meters, float normalScale) =>
            MaterialLibrary.Lit(name, new LitOptions
            {
                Color = c, Albedo = "T_Fabric", Normal = "T_Fabric_N", NormalScale = normalScale,
                MetersPerTile = meters, Smoothness = 0.08f, ReceiveShadows = true
            });

        static Material Emissive(string name, Color c, Color emission, string tex = null, float meters = 1f) =>
            MaterialLibrary.Lit(name, new LitOptions
            {
                Color = c, Albedo = tex, Normal = tex != null ? tex + "_N" : null, NormalScale = 0.5f, MetersPerTile = meters,
                Smoothness = 0.2f, Emission = emission, ReceiveShadows = true
            });
    }
}
