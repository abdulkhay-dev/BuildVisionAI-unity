using UnityEngine;

namespace House4696.Core
{
    /// <summary>Options for a URP/Lit material. Colors are sRGB; tiling is expressed as meters per texture tile.</summary>
    public struct LitOptions
    {
        public Color Color;
        public string Albedo;
        public string Normal;
        public float NormalScale;
        public float MetersPerTile;
        public Vector2 Tiling;          // overrides MetersPerTile when non-zero
        public float Smoothness;
        public float Metallic;
        public bool Cutout;
        public float Cutoff;
        public bool TwoSided;
        public bool Transparent;
        public Color Emission;
        public bool ReceiveShadows;
        /// <summary>
        /// Rough garden surface: no specular highlights and no probe reflections (_SPECULARHIGHLIGHTS_OFF,
        /// _ENVIRONMENTREFLECTIONS_OFF; at smoothness ≤ 0.15 they are ~1 % of the radiance). Applied when the editor writes
        /// the material assets (see <see cref="MaterialLibrary.MatteGarden"/>); the player ships them from the palette.
        /// </summary>
        public bool Matte;

        public static LitOptions Of(Color c, float smoothness = 0.25f) => new LitOptions
        {
            Color = c, NormalScale = 1f, MetersPerTile = 1f, Smoothness = smoothness, Cutoff = 0.5f, ReceiveShadows = true
        };
    }

    /// <summary>
    /// Every material of the scene, created as URP/Lit assets under Generated/Materials.
    /// Colors approximate the reference render: anthracite stucco, dark slate cladding, honey-toned battens.
    /// </summary>
    public sealed class MaterialLibrary
    {
        public Material Stone, Plinth, Wood, SlatBacking, Stucco, Soffit, ConiferCore, BoxTuft, Coping, Frame, Glass, GlassDoor, GlassRailing,
            Curtain, InteriorWall, InteriorFloor, InteriorCeiling, InteriorDark, Porcelain, StepRiser, Paver, Gravel,
            Lawn, Mulch, Soil, Hedge, SpruceBranch, PineTuft, BirchLeaves, DeciduousLeaves, Bark, BirchBark, Blades,
            GreyBlades, Plume, Boulder, BollardWood, BollardCap, BollardLight, Pot, Edging, Rattan, Cushion,
            FurnitureDark, Steel, Sky, GlassInner;

        /// <summary>
        /// Honour <see cref="LitOptions.Matte"/> (foliage, grass blades, lawn, bark, mulch, soil, dwarf-pine surface).
        /// false = those materials keep highlights and reflections, as before. A change takes effect after
        /// House 46-96 → Rebuild Runtime Content (the player reads the material assets from the palette).
        /// </summary>
        public static bool MatteGarden = true;

        public static MaterialLibrary Create()
        {
            var L = new MaterialLibrary();

            // --- facade
            L.Stone = Lit("M_StoneCladding", new LitOptions
            {
                Color = new Color(0.70f, 0.70f, 0.73f), Albedo = "T_Stone", Normal = "T_Stone_N", NormalScale = 1f,
                MetersPerTile = 3.6f, Smoothness = 0.22f, ReceiveShadows = true, Cutoff = 0.5f
            });
            L.Plinth = Lit("M_Plinth", new LitOptions
            {
                Color = Color.white, Albedo = "T_Plinth", Normal = "T_Plinth_N", NormalScale = 0.6f,
                MetersPerTile = 2f, Smoothness = 0.3f, ReceiveShadows = true
            });
            L.Wood = Lit("M_WoodBattens", new LitOptions
            {
                Color = new Color(0.9f, 0.88f, 0.86f), Albedo = "T_Wood", Normal = "T_Wood_N", NormalScale = 0.8f,
                Tiling = new Vector2(1f, 0.5f), Smoothness = 0.2f, ReceiveShadows = true
            });
            L.Soffit = Lit("M_StuccoSoffit", new LitOptions
            {
                Color = new Color(0.25f, 0.25f, 0.26f), Albedo = "T_Stucco", Normal = "T_Stucco_N", NormalScale = 0.5f,
                MetersPerTile = 2f, Smoothness = 0.04f, ReceiveShadows = true
            });
            L.SlatBacking = Lit("M_SlatBacking", LitOptions.Of(new Color(0.08f, 0.055f, 0.035f), 0.1f));
            L.Stucco = Lit("M_StuccoAnthracite", new LitOptions
            {
                Color = new Color(0.97f, 0.97f, 0.99f), Albedo = "T_Stucco", Normal = "T_Stucco_N", NormalScale = 0.5f,
                MetersPerTile = 2f, Smoothness = 0.08f, ReceiveShadows = true
            });
            L.Coping = Lit("M_MetalCoping", LitOptions.Of(new Color(0.075f, 0.075f, 0.08f), 0.3f));
            L.Frame = Lit("M_FrameAnthracite", LitOptions.Of(new Color(0.09f, 0.09f, 0.095f), 0.5f));
            L.Frame.SetFloat("_Metallic", 0.3f);
            L.Steel = Lit("M_Steel", LitOptions.Of(new Color(0.55f, 0.56f, 0.58f), 0.7f));
            L.Steel.SetFloat("_Metallic", 0.9f);

            // reflective double glazing: partly metallic so tree/sky reflections read as strongly as in archviz renders
            var glass = LitOptions.Of(new Color(0.52f, 0.54f, 0.56f, 0.8f), 0.99f);
            glass.Transparent = true; glass.Metallic = 0.95f;
            L.Glass = Lit("M_Glass", glass);
            var railing = LitOptions.Of(new Color(0.30f, 0.33f, 0.35f, 0.045f), 0.98f);
            railing.Transparent = true;
            L.GlassRailing = Lit("M_GlassRailing", railing);
            L.GlassDoor = Lit("M_GlassDoorDark", LitOptions.Of(new Color(0.018f, 0.02f, 0.022f), 0.93f));

            var curtain = LitOptions.Of(new Color(0.86f, 0.84f, 0.80f, 0.78f), 0.1f);
            curtain.Transparent = true; curtain.TwoSided = true;
            L.Curtain = Lit("M_CurtainSheer", curtain);

            // --- interior shell: warm white plaster, oak floor (interiors are lit by probes + lamps, so albedos are realistic)
            L.InteriorWall = Lit("M_InteriorWall", new LitOptions
            {
                Color = new Color(0.92f, 0.915f, 0.9f), Albedo = "T_Plaster", Normal = "T_Plaster_N", NormalScale = 0.35f,
                MetersPerTile = 2f, Smoothness = 0.12f, ReceiveShadows = true
            });
            L.InteriorCeiling = Lit("M_InteriorCeiling", new LitOptions
            {
                Color = new Color(0.95f, 0.95f, 0.945f), Albedo = "T_Plaster", Normal = "T_Plaster_N", NormalScale = 0.25f,
                MetersPerTile = 2f, Smoothness = 0.05f, ReceiveShadows = true
            });
            L.InteriorFloor = Lit("M_InteriorFloor", new LitOptions
            {
                Color = new Color(0.97f, 0.97f, 0.93f), Albedo = "T_OakFloor", Normal = "T_OakFloor_N", NormalScale = 0.6f,
                MetersPerTile = 2.4f, Smoothness = 0.55f, ReceiveShadows = true
            });
            L.InteriorDark = Lit("M_InteriorDark", LitOptions.Of(new Color(0.06f, 0.06f, 0.06f), 0.2f));
            // inner face of window panes: clear, not mirrored (the outer face keeps the archviz reflection)
            var inner = LitOptions.Of(new Color(0.62f, 0.64f, 0.66f, 0.08f), 0.96f);
            inner.Transparent = true;
            L.GlassInner = Lit("M_GlassInner", inner);

            // --- hardscape
            L.Porcelain = Lit("M_PorcelainLight", new LitOptions
            {
                Color = new Color(0.50f, 0.49f, 0.48f), Albedo = "T_Porcelain", Normal = "T_Porcelain_N", NormalScale = 0.5f,
                MetersPerTile = 2.4f, Smoothness = 0.3f, ReceiveShadows = true
            });
            L.StepRiser = L.Stone;
            L.Paver = Lit("M_ConcreteSlab", new LitOptions
            {
                Color = Color.white, Albedo = "T_Paver", Normal = "T_Paver_N", NormalScale = 0.5f,
                MetersPerTile = 2f, Smoothness = 0.2f, ReceiveShadows = true
            });
            L.Gravel = Lit("M_GravelWhite", new LitOptions
            {
                Color = Color.white, Albedo = "T_Gravel", Normal = "T_Gravel_N", NormalScale = 1.2f,
                MetersPerTile = 0.6f, Smoothness = 0.2f, ReceiveShadows = true
            });
            L.Lawn = Lit("M_Lawn", new LitOptions
            {
                Color = new Color(1f, 1f, 0.78f), Albedo = "T_Lawn", Normal = "T_Lawn_N", NormalScale = 0.8f,
                MetersPerTile = 3f, Smoothness = 0.04f, ReceiveShadows = true, Matte = true
            });
            L.Mulch = Lit("M_Mulch", new LitOptions
            {
                Color = Color.white, Albedo = "T_Mulch", Normal = "T_Mulch_N", NormalScale = 1f,
                MetersPerTile = 1.5f, Smoothness = 0.1f, ReceiveShadows = true, Matte = true
            });
            var soil = LitOptions.Of(new Color(0.16f, 0.12f, 0.09f), 0.1f);
            soil.Matte = true;
            L.Soil = Lit("M_Soil", soil);
            L.Edging = Lit("M_SteelEdging", LitOptions.Of(new Color(0.06f, 0.06f, 0.06f), 0.4f));
            L.Boulder = Lit("M_Boulder", new LitOptions
            {
                Color = Color.white, Albedo = "T_Boulder", Normal = "T_Boulder_N", NormalScale = 1f,
                MetersPerTile = 1f, Smoothness = 0.2f, ReceiveShadows = true
            });

            // --- vegetation
            L.Hedge = Lit("M_HedgeBoxwood", new LitOptions
            {
                Color = new Color(0.82f, 0.8f, 0.6f), Albedo = "T_Hedge", Normal = "T_Hedge_N", NormalScale = 1.4f,
                MetersPerTile = 0.8f, Smoothness = 0.2f, ReceiveShadows = true
            });
            L.ConiferCore = Lit("M_PineSurface", new LitOptions
            {
                Color = new Color(0.55f, 0.68f, 0.45f), Albedo = "T_Hedge", Normal = "T_Hedge_N", NormalScale = 1.6f,
                MetersPerTile = 0.6f, Smoothness = 0.02f, ReceiveShadows = true, Matte = true
            });
            L.ConiferCore.SetFloat("_EnvironmentReflections", 0f);
            L.ConiferCore.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");
            L.BoxTuft = Foliage("M_BoxwoodTuft", "T_BoxTuft_A", new Color(0.85f, 0.88f, 0.8f));
            L.SpruceBranch = Foliage("M_SpruceBranch", "T_SpruceBranch_A", new Color(0.85f, 0.95f, 0.9f));
            L.PineTuft = Foliage("M_PineTuft", "T_PineTuft_A", Color.white);
            L.BirchLeaves = Foliage("M_BirchLeaves", "T_BirchLeaves_A", new Color(0.78f, 0.8f, 0.7f));
            L.DeciduousLeaves = Foliage("M_DeciduousLeaves", "T_DeciduousLeaves_A", new Color(0.85f, 0.85f, 0.72f));
            L.Plume = Foliage("M_GrassPlume", "T_Plume_A", Color.white);
            L.Bark = Lit("M_BarkSpruce", new LitOptions
            {
                Color = Color.white, Albedo = "T_Bark", Normal = "T_Bark_N", NormalScale = 1f,
                Tiling = new Vector2(1f, 1f), Smoothness = 0.1f, ReceiveShadows = true, Matte = true
            });
            L.BirchBark = Lit("M_BarkBirch", new LitOptions
            {
                Color = Color.white, Albedo = "T_BirchBark", Normal = "T_BirchBark_N", NormalScale = 0.6f,
                Tiling = new Vector2(1f, 1f), Smoothness = 0.15f, ReceiveShadows = true, Matte = true
            });
            var blades = new LitOptions
            {
                Color = Color.white, Albedo = "T_Blades", Tiling = Vector2.one, Smoothness = 0.05f,
                TwoSided = true, ReceiveShadows = true, NormalScale = 1f, Matte = true
            };
            L.Blades = Lit("M_GrassBlades", blades);
            L.GreyBlades = L.Blades;

            // --- props
            L.BollardWood = Lit("M_BollardWood", new LitOptions
            {
                Color = new Color(1f, 0.9f, 0.85f), Albedo = "T_Wood", Normal = "T_Wood_N", Tiling = new Vector2(1f, 0.5f),
                Smoothness = 0.35f, ReceiveShadows = true, NormalScale = 1f
            });
            L.BollardCap = Lit("M_BollardCap", LitOptions.Of(new Color(0.1f, 0.1f, 0.1f), 0.5f));
            var lamp = LitOptions.Of(new Color(1f, 0.93f, 0.8f), 0.6f);
            lamp.Emission = new Color(1.2f, 0.95f, 0.6f);
            L.BollardLight = Lit("M_BollardLight", lamp);
            L.Pot = Lit("M_PlanterConcrete", new LitOptions
            {
                Color = new Color(0.55f, 0.55f, 0.56f), Albedo = "T_Paver", Normal = "T_Paver_N", MetersPerTile = 1f,
                Smoothness = 0.25f, ReceiveShadows = true, NormalScale = 0.6f
            });
            L.Rattan = Lit("M_Rattan", LitOptions.Of(new Color(0.30f, 0.20f, 0.12f), 0.25f));
            L.Cushion = Lit("M_Cushion", LitOptions.Of(new Color(0.36f, 0.34f, 0.31f), 0.1f));
            L.FurnitureDark = Lit("M_FurnitureDark", LitOptions.Of(new Color(0.12f, 0.12f, 0.13f), 0.35f));

            L.Sky = Source.Sky();
            return L;
        }

        static Material Foliage(string name, string tex, Color tint)
        {
            return Lit(name, new LitOptions
            {
                Color = tint, Albedo = tex, Tiling = Vector2.one, Smoothness = 0.08f,
                Cutout = true, Cutoff = 0.45f, TwoSided = true, ReceiveShadows = true, NormalScale = 1f, Matte = true
            });
        }
        // note: foliage keeps low smoothness so grazing sky reflections do not turn crowns blue

        /// <summary>
        /// Where materials come from: the editor creates/updates material assets (<c>AssetMaterialSource</c>), a
        /// player takes the prebuilt ones from <see cref="HouseContent"/> (their shader variants ship with the build).
        /// </summary>
        public static IMaterialSource Source
        {
            get => _source ??= new PaletteMaterialSource(HouseContent.Load());
            set => _source = value;
        }
        static IMaterialSource _source;

        public static Material Lit(string name, LitOptions o)
        {
            var m = Source.Lit(name, o);
            // only while writing the assets: the player's palette already carries the keywords (and their variants)
            if (o.Matte && MatteGarden && m != null && !(Source is PaletteMaterialSource)) SetMatte(m);
            return m;
        }

        /// <summary>What URP's LitGUI.SetMaterialKeywords derives from the two toggles, set directly (runtime assembly).</summary>
        static void SetMatte(Material m)
        {
            m.SetFloat("_SpecularHighlights", 0f);
            m.SetFloat("_EnvironmentReflections", 0f);
            m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
            m.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");
        }
    }

    public interface IMaterialSource
    {
        Material Lit(string name, LitOptions o);
        Material Sky();
    }

    /// <summary>Runtime material source: looks materials up by name in the prebuilt palette.</summary>
    public sealed class PaletteMaterialSource : IMaterialSource
    {
        readonly HouseContent _content;
        public PaletteMaterialSource(HouseContent content) { _content = content; }
        public Material Lit(string name, LitOptions o) => _content.Material(name);
        public Material Sky() => _content.Material(HouseContent.SkyMaterial);
    }
}
