using System;
using System.IO;
using House4696.Core;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace House4696.Build
{
    /// <summary>
    /// Standalone builds of the house tour (only the house scene). Menu: House 46-96 → Build; CI:
    /// <c>Unity -batchmode -quit -projectPath . -executeMethod House4696.Build.HouseBuild.BuildAllCli</c>.
    /// Output goes to &lt;project&gt;/Builds/&lt;platform&gt;/.
    /// </summary>
    public static class HouseBuild
    {
        public const string ProductName = "House 46-96";
        const string BundleId = "com.ansormed.house4696";

        static readonly (BuildTarget target, string folder, string file)[] Targets =
        {
            (BuildTarget.StandaloneOSX, "macOS", ProductName + ".app"),
            (BuildTarget.StandaloneWindows64, "Windows", ProductName + ".exe"),
        };

        [MenuItem("House 46-96/Build/macOS", priority = 40)]
        public static void BuildMacMenu() => Report(Build(BuildTarget.StandaloneOSX));

        [MenuItem("House 46-96/Build/Windows (x64)", priority = 41)]
        public static void BuildWindowsMenu() => Report(Build(BuildTarget.StandaloneWindows64));

        [MenuItem("House 46-96/Build/macOS + Windows", priority = 42)]
        public static void BuildAllMenu()
        {
            foreach (var t in Targets) Report(Build(t.target));
        }

        /// <summary>Batch-mode entry point: exit code 1 if any platform failed.</summary>
        public static void BuildAllCli()
        {
            bool ok = true;
            foreach (var t in Targets)
            {
                var r = Build(t.target);
                Report(r);
                ok &= r.StartsWith("[House4696] OK", StringComparison.Ordinal);
            }
            EditorApplication.Exit(ok ? 0 : 1);
        }

        public static string Build(BuildTarget target)
        {
            var spec = Array.Find(Targets, t => t.target == target);
            if (spec.folder == null) return "[House4696] FAILED: unsupported target " + target;
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Standalone, target))
                return $"[House4696] FAILED {spec.folder}: build support for {target} is not installed (Unity Hub → Add modules)";
            if (BuildPipeline.isBuildingPlayer) return "[House4696] FAILED: another build is already running";
            if (!File.Exists(AssetPaths.ScenePath))
                return "[House4696] FAILED: scene not found, run House 46-96 → Rebuild Scene first";

            ConfigurePlayer(target);
            string root = Path.Combine(Path.GetDirectoryName(Application.dataPath) ?? ".", "Builds", spec.folder);
            if (Directory.Exists(root)) Directory.Delete(root, true); // no stale files from previous builds
            Directory.CreateDirectory(root);

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { AssetPaths.ScenePath },
                locationPathName = Path.Combine(root, spec.file),
                target = target,
                targetGroup = BuildTargetGroup.Standalone,
                options = BuildOptions.None,
            });

            // a failing post-process step can still report Succeeded, so the output itself is the proof
            var s = report.summary;
            bool produced = File.Exists(s.outputPath) || Directory.Exists(s.outputPath);
            return s.result == BuildResult.Succeeded && produced
                ? $"[House4696] OK {spec.folder}: {s.outputPath} ({s.totalSize / 1048576f:0} MB, {s.totalTime.TotalSeconds:0} s)"
                : $"[House4696] FAILED {spec.folder}: {s.result}, output {(produced ? "present" : "missing")}, {s.totalErrors} error(s) — see the console";
        }

        static void ConfigurePlayer(BuildTarget target)
        {
            PlayerSettings.productName = ProductName;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Standalone, BundleId);
            PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
            PlayerSettings.resizableWindow = true;
            PlayerSettings.defaultScreenWidth = 1600;
            PlayerSettings.defaultScreenHeight = 900;
            // Mono: IL2CPP cannot cross-compile Windows players on a Mac
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            if (target == BuildTarget.StandaloneOSX)
                EditorUserBuildSettings.SetPlatformSettings(BuildPipeline.GetBuildTargetName(target), "Architecture", "x64ARM64"); // universal: Intel + Apple silicon
        }

        static void Report(string message)
        {
            if (message.StartsWith("[House4696] OK", StringComparison.Ordinal)) Debug.Log(message);
            else Debug.LogError(message);
        }
    }
}
