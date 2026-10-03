using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using House4696.Generation;
using House4696.Medical;
using UnityEditor;
using UnityEngine;

namespace House4696.MedicalEditor
{
    /// <summary>
    /// Renders medical designs as they are written, for the people and agents drawing them outside Unity: every few
    /// seconds it looks at Resources/Medical/Designs/*.json and, for each file changed since its last render, imports it
    /// and renders angle / front / side views to tools/medical/renders/&lt;id&gt;-&lt;view&gt;.png, then writes
    /// &lt;id&gt;.txt with "ok" or the build errors and warnings (written last: wait for it). Start / Stop from code.
    /// </summary>
    [InitializeOnLoad]
    public static class MedWatch
    {
        // runs again after every script reload (a compile would otherwise stop the watch until someone restarts it)
        static MedWatch()
        {
            // update ticks while the editor is in the background too (delayCall does not)
            if (!Application.isBatchMode) EditorApplication.update += Boot;
        }

        static void Boot()
        {
            EditorApplication.update -= Boot;
            Start();
        }

        const string Designs = "Assets/House4696/Resources/Medical/Designs";
        /// <summary>Screen pictures med_&lt;id&gt;_screen: a picture changed outside Unity is reimported and its device re-rendered.</summary>
        const string Screens = "Assets/House4696/External/Materials";
        static readonly Dictionary<string, DateTime> _seen = new Dictionary<string, DateTime>();
        static readonly Dictionary<string, DateTime> _pics = new Dictionary<string, DateTime>();
        static double _next;
        static bool _on;

        public static string Start()
        {
            if (!_on) EditorApplication.update += Tick;
            _on = true;
            // files already rendered (their .txt newer than the design) are not redone
            foreach (var f in Directory.GetFiles(Designs, "*.json"))
            {
                string id = Path.GetFileNameWithoutExtension(f);
                var stamp = Path.Combine(Out, id + ".txt");
                if (File.Exists(stamp) && File.GetLastWriteTimeUtc(stamp) >= File.GetLastWriteTimeUtc(f)) _seen[id] = File.GetLastWriteTimeUtc(f);
            }
            foreach (var f in ScreenPictures()) _pics[f] = File.GetLastWriteTimeUtc(f);
            return "[MedWatch] watching " + Designs + " → " + Out;
        }

        public static string Stop()
        {
            EditorApplication.update -= Tick;
            _on = false;
            return "[MedWatch] stopped";
        }

        static string Out => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "tools", "medical", "renders"));

        static void Tick()
        {
            if (EditorApplication.timeSinceStartup < _next || EditorApplication.isCompiling || EditorApplication.isPlaying) return;
            _next = EditorApplication.timeSinceStartup + 3.0;
            CheckScreens();
            string todo = null;
            foreach (var f in Directory.GetFiles(Designs, "*.json"))
            {
                string id = Path.GetFileNameWithoutExtension(f);
                var t = File.GetLastWriteTimeUtc(f);
                if (_seen.TryGetValue(id, out var s) && s == t) continue;
                // a file still being written: wait until it is a second old
                if ((DateTime.UtcNow - t).TotalSeconds < 1.0) continue;
                todo = f;
                _seen[id] = t;
                break;
            }
            if (todo != null) Render(todo);
        }

        static IEnumerable<string> ScreenPictures()
        {
            if (!Directory.Exists(Screens)) yield break;
            foreach (var dir in Directory.GetDirectories(Screens, "med_*_screen"))
                foreach (var f in Directory.GetFiles(dir))
                    if (!f.EndsWith(".meta", StringComparison.Ordinal)) yield return f.Replace('\\', '/');
        }

        /// <summary>Reimports screen pictures rewritten on disk and touches their device's design so it renders again.</summary>
        static void CheckScreens()
        {
            foreach (var f in ScreenPictures())
            {
                var t = File.GetLastWriteTimeUtc(f);
                if (_pics.TryGetValue(f, out var s) && s == t) continue;
                if ((DateTime.UtcNow - t).TotalSeconds < 1.0) continue;
                bool known = _pics.ContainsKey(f);
                _pics[f] = t;
                if (!known) continue;
                AssetDatabase.ImportAsset(f, ImportAssetOptions.ForceSynchronousImport);
                // med_<id>_screen → the device id
                string folder = Path.GetFileName(Path.GetDirectoryName(f));
                string id = folder.Substring(4, folder.Length - 4 - "_screen".Length);
                string design = Path.Combine(Designs, id + ".json");
                if (File.Exists(design)) _seen.Remove(id);
            }
        }

        static void Render(string file)
        {
            string id = Path.GetFileNameWithoutExtension(file);
            Directory.CreateDirectory(Out);
            var log = new StringBuilder();
            void Capture(string msg, string stack, LogType type)
            {
                if (type == LogType.Error || type == LogType.Exception || type == LogType.Warning || type == LogType.Assert)
                    if (!msg.StartsWith("[CasePreview] " + id + " ", StringComparison.Ordinal)) log.AppendLine(type + ": " + msg);
            }
            Application.logMessageReceived += Capture;
            try
            {
                AssetDatabase.ImportAsset(file.Replace('\\', '/'), ImportAssetOptions.ForceSynchronousImport);
                MedCatalog.Reload();
                ItemCatalog.ReloadCasegoods();
                if (MedCatalog.Model(id) == null) log.AppendLine($"Error: модели '{id}' нет в Resources/Medical/catalog.json");
                else
                {
                    var d = MedCatalog.Design(id);
                    if (d == null) log.AppendLine("Error: чертёж не читается (JSON)");
                    else
                        foreach (var view in new[] { "angle", "front", "side", "top" })
                        {
                            var r = House4696.CasegoodsEditor.CasePreview.Render(id, null, Path.Combine(Out, $"{id}-{view}.png"), view, false, 500f, false);
                            if (!r.Contains(" → ")) log.AppendLine("Error: " + r);
                        }
                }
            }
            catch (Exception e) { log.AppendLine("Exception: " + e.Message); }
            finally { Application.logMessageReceived -= Capture; }
            File.WriteAllText(Path.Combine(Out, id + ".txt"), log.Length == 0 ? "ok\n" : log.ToString());
            Debug.Log($"[MedWatch] {id}: {(log.Length == 0 ? "ok" : "errors")}");
        }
    }
}
