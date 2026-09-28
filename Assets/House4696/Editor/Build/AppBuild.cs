using System;
using System.IO;
using House4696.Setup;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace House4696.Build
{
    /// <summary>
    /// Builds the House app (the runtime generator + local API that the MCP server drives) from the App scene.
    /// Output: &lt;project&gt;/Builds/App/&lt;platform&gt;/. Packaging (bundled MCP server, signing, dmg) is done by
    /// <c>tools/package-mac.sh</c>. CI: <c>-executeMethod House4696.Build.AppBuild.BuildMacCli</c>.
    /// </summary>
    public static class AppBuild
    {
        public const string ProductName = "House";
        const string Company = "Ansormed";
        const string BundleId = "com.ansormed.house";

        [MenuItem("House 46-96/App/Build macOS app", priority = 45)]
        public static void BuildMacMenu() => Log(Build(BuildTarget.StandaloneOSX));

        [MenuItem("House 46-96/App/Build Windows app (x64)", priority = 46)]
        public static void BuildWindowsMenu() => Log(Build(BuildTarget.StandaloneWindows64));

        public static void BuildMacCli()
        {
            // -importLandscape: rebuild the landscape kit first (after tools/landscape/export_kit.py)
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "-importLandscape") >= 0)
                Debug.Log(Setup.LandscapeKitImporter.Import());
            var r = Build(BuildTarget.StandaloneOSX);
            Log(r);
            EditorApplication.Exit(r.StartsWith("[AppBuild] OK", StringComparison.Ordinal) ? 0 : 1);
        }

        /// <summary>CI / batch mode: <c>-buildTarget Win64 -executeMethod House4696.Build.AppBuild.BuildWindowsCli</c>.</summary>
        public static void BuildWindowsCli()
        {
            var r = Build(BuildTarget.StandaloneWindows64);
            Log(r);
            EditorApplication.Exit(r.StartsWith("[AppBuild] OK", StringComparison.Ordinal) ? 0 : 1);
        }

        public static string Build(BuildTarget target)
        {
            bool mac = target == BuildTarget.StandaloneOSX;
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Standalone, target))
                return $"[AppBuild] FAILED: build support for {target} is not installed";
            if (BuildPipeline.isBuildingPlayer) return "[AppBuild] FAILED: another build is running";
            if (!File.Exists(AppSceneSetup.ScenePath)) return "[AppBuild] FAILED: run House 46-96 → App → Create App Scene first";
            if (RealtimeGISetup.ConfigurePlayer()) return "[AppBuild] FAILED: SURFACE_CACHE define was just added — scripts must recompile, build again";
            Core.HouseContentBuilder.Rebuild();

            PlayerSettings.companyName = Company;
            PlayerSettings.productName = ProductName;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Standalone, BundleId);
            PlayerSettings.bundleVersion = App.HouseBootstrap.Version;
            PlayerSettings.runInBackground = true;          // the AI edits while another app has focus
            PlayerSettings.visibleInBackground = true;
            PlayerSettings.enableFrameTimingStats = true;   // GPU frame times for the perf diagnostics
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.resizableWindow = true;
            PlayerSettings.defaultScreenWidth = 1600;
            PlayerSettings.defaultScreenHeight = 900;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            if (mac) EditorUserBuildSettings.SetPlatformSettings(BuildPipeline.GetBuildTargetName(target), "Architecture", "x64ARM64");

            string root = Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? ".", "Builds", "App", mac ? "macOS" : "Windows");
            if (Directory.Exists(root)) Directory.Delete(root, true);
            Directory.CreateDirectory(root);
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { AppSceneSetup.ScenePath },
                locationPathName = Path.Combine(root, mac ? ProductName + ".app" : ProductName + ".exe"),
                target = target,
                targetGroup = BuildTargetGroup.Standalone,
                options = BuildOptions.None,
            });
            var s = report.summary;
            bool produced = File.Exists(s.outputPath) || Directory.Exists(s.outputPath);
            return s.result == BuildResult.Succeeded && produced
                ? $"[AppBuild] OK: {s.outputPath} ({s.totalSize / 1048576f:0} MB, {s.totalTime.TotalSeconds:0} s)"
                : $"[AppBuild] FAILED: {s.result}, {s.totalErrors} error(s), output {(produced ? "present" : "missing")}";
        }

        static void Log(string m)
        {
            if (m.StartsWith("[AppBuild] OK", StringComparison.Ordinal)) Debug.Log(m); else Debug.LogError(m);
        }
    }
}
