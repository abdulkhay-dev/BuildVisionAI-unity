// This folder compiles into an assembly named "Assembly-CSharp-Editor-testable" on purpose (HouseBakedGI.asmdef):
// the render-pipelines core package exposes its GPU path tracer (UnityEngine.PathTracing.*, the engine behind the
// editor's probe bake), its sampling resources and unified ray tracing only through InternalsVisibleTo, and this is
// the one name on all three lists that no installed package already uses (the package test assemblies are
// registered even when not compiled). It ships in the player like any runtime assembly.
// Everything else in the project talks to the public House4696.Lighting API below.

using UnityEngine;

namespace House4696.Lighting
{
    /// <summary>
    /// Shaders and textures the runtime GI baker needs in the player. The package loads them through the
    /// AssetDatabase, which does not exist there, so the editor (BakedGISetup) references them here and this asset
    /// ships with the build.
    /// </summary>
    public sealed class ProbeBakeResources : ScriptableObject
    {
        [Header("Path tracing (compute variants of the .urtshader files)")]
        public ComputeShader IndirectRadiance;
        public ComputeShader DirectStochasticLight;
        public ComputeShader DirectDirectionalAndEnvironment;
        public ComputeShader Validity;
        public ComputeShader SegmentedReduction;
        public ComputeShader ProbePostProcessing;

        [Header("Sampling")]
        public Texture2D SobolScramblingTile;
        public Texture2D SobolRankingTile;
        public Texture2D SobolOwenScrambled256;

        [Header("Environment and display")]
        public Shader PassthroughSkybox;
        public ComputeShader Resolve;

        public bool IsComplete =>
            IndirectRadiance && DirectStochasticLight && DirectDirectionalAndEnvironment && Validity && SegmentedReduction &&
            ProbePostProcessing && SobolScramblingTile && SobolRankingTile && SobolOwenScrambled256 && PassthroughSkybox && Resolve;
    }
}
