namespace House4696.Landscape
{
    /// <summary>
    /// Performance switches of the generated garden, one per optimisation, so each one can be A/B-tested and rolled
    /// back on its own. They are read while a house is generated: a change applies on the next rebuild. The defaults
    /// are the optimised garden; setting a flag to false restores the previous behaviour of that part exactly.
    /// </summary>
    public static class GardenPerf
    {
        // ------------------------------------------------------------------ trees: LOD1 + dithered cross-fade
        /// <summary>Trees get a LODGroup: LOD0 (the full crown, the tree object itself) and LOD1 (a decimated crown, child "&lt;name&gt;_LOD1"). false = LOD0 only.</summary>
        public static bool TreeLod = true;
        /// <summary>
        /// Real screen height (fraction of the viewport height) below which a tree shows LOD1. QualitySettings.lodBias is
        /// compensated, so this is what the viewer sees: 0.25 → a 20 m tree switches at ≈97 m in orbit (45°) and ≈57 m in
        /// walk mode (70°). Tune between 0.25 and 0.35 from screenshots; higher switches closer.
        /// </summary>
        public static float TreeLodScreenHeight = 0.25f;
        /// <summary>Width of the dithered cross-fade band (LOD.fadeTransitionWidth, share of the LOD0 range). Both levels draw inside it.</summary>
        public static float TreeLodFadeWidth = 0.25f;

        // LOD1 crowns are a subset of LOD0 (same random stream, every n-th element kept and widened), so the silhouette
        // and the crown profile match during the fade instead of a differently arranged crown dithering in.
        /// <summary>Spruce LOD1 keeps every n-th whorl (spacing ≈0.68 m instead of 0.34 m).</summary>
        public static int Lod1WhorlStep = 2;
        /// <summary>Spruce LOD1 keeps this share of a whorl's branches, spread evenly around the stem (≈5–6 of 8–10).</summary>
        public static float Lod1BranchKeep = 0.6f;
        /// <summary>Spruce LOD1 branch cards are this much wider (keeps ≈35–40 % of the LOD0 card area).</summary>
        public static float Lod1CardWidth = 1.35f;
        /// <summary>Spruce LOD1 branch card segments along the sag curve (LOD0: 3).</summary>
        public static int Lod1CardSegments = 2;
        /// <summary>LOD1 trunk sides and rings (LOD0: 8–10 sides, 8 rings).</summary>
        public static int Lod1TrunkSides = 6, Lod1TrunkRings = 4;
        /// <summary>Birch LOD1 limb sides (LOD0: 5).</summary>
        public static int Lod1LimbSides = 3;
        /// <summary>Birch / broadleaf LOD1 keeps every n-th leaf clump ...</summary>
        public static int Lod1LeafStep = 2;
        /// <summary>... scaled up by this factor (1.35² / 2 ≈ 0.9 of the LOD0 leaf area).</summary>
        public static float Lod1LeafScale = 1.35f;

        // ------------------------------------------------------------------ lawn blades
        /// <summary>Lawn blades are split into square chunks (frustum / occlusion culling per chunk, 16-bit indices). false = one "Lawn_Blades" renderer.</summary>
        public static bool LawnChunks = true;
        /// <summary>Chunk side, metres. 3 m keeps every chunk under 65k vertices even at full density.</summary>
        public static float LawnChunkSize = 3f;
        /// <summary>Each chunk gets a LODGroup whose LOD1 has fewer, wider blades (same covered area). Needs <see cref="LawnChunks"/>.</summary>
        public static bool LawnLod = true;
        /// <summary>
        /// Camera → chunk-centre distance at which a chunk switches to LOD1, metres, for the walk lens
        /// (<see cref="LawnLodReferenceFov"/>). Longer lenses switch farther: the calibrated reference view (≈38° vertical)
        /// at ≈16 m, orbit (45°) at ≈13.5 m. With 3 m chunks the nearest LOD1 blades are ≥ ~6 m away.
        /// </summary>
        public static float LawnLodDistance = 8f;
        /// <summary>Vertical field of view the switch distance is set for (the walk mode lens).</summary>
        public static float LawnLodReferenceFov = 70f;
        /// <summary>Share of the blades LOD1 keeps (a fixed random subset of LOD0).</summary>
        public static float LawnLodKeep = 0.5f;
        /// <summary>LOD1 blades are 1/keep wider, but never more than this (wider blades turn into square specks at grazing angles).</summary>
        public static float LawnLodMaxWiden = 2.5f;
        /// <summary>Dithered cross-fade band of the lawn chunks (share of the LOD0 range).</summary>
        public static float LawnLodFadeWidth = 0.2f;

        // ------------------------------------------------------------------ shadow casters
        /// <summary>
        /// A tree within the shadow reach whose shadow falls away from the house casts it from a ShadowsOnly proxy (its
        /// LOD1 mesh, outside the LODGroup) and its LOD0/LOD1 cast nothing. Trees that shade the house or the front lawn
        /// keep their full crown. Applied by HouseSession.ReduceGardenShadows. false = full crowns for every near tree.
        /// </summary>
        public static bool TreeShadowProxies = true;
        /// <summary>A tree gets a proxy when cos(shadow direction, direction tree → house centre) is below this (0 = pointing away; lower = stricter).</summary>
        public static float TreeProxyAwayCos = 0f;
        /// <summary>Hedges cast from a coarse ShadowsOnly child "&lt;hedge&gt;_Shadow"; the visible hedge casts nothing. false = the visible hedge casts.</summary>
        public static bool HedgeShadowProxy = true;
        /// <summary>Hedge proxy grid cell, metres (the visible hedge keeps 0.05 m).</summary>
        public static float HedgeProxyCell = 0.10f;
        /// <summary>Hedge proxy surface inset along the normal, metres (keeps the proxy inside the visible surface: no acne on the lit side).</summary>
        public static float HedgeProxyInset = 0.05f;
        /// <summary>The boulder and the dwarf mountain pines cast shadows (contact shadows on mulch and lawn). false = all of "Plants" casts nothing, as before.</summary>
        public static bool PlantShadows = true;

        // ------------------------------------------------------------------ vertex data
        /// <summary>Vegetation meshes share vertices between triangles (cards 4 vertices instead of 6, grids one per point). false = one vertex per corner.</summary>
        public static bool IndexedVegetation = true;
        /// <summary>Vegetation meshes use the compact vertex layout (<see cref="Core.MeshBuilder.Compact"/>): no colour, Float16 tangents only where a normal map needs them. false = 64-byte vertices.</summary>
        public static bool CompactVertices = true;
    }
}
