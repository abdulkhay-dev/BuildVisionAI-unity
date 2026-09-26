using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using House4696.Generation;
using House4696.Model;
using UnityEngine;

namespace House4696.App
{
    /// <summary>Short description of a stored project for lists.</summary>
    public sealed class ProjectInfo
    {
        public string Id, Name, Description, Modified;
        public int Levels, Rooms, Items;
        public float Area;
    }

    /// <summary>
    /// Projects on disk: one folder per project under <c>persistentDataPath/Projects/&lt;id&gt;/</c> holding
    /// <c>house.json</c>. Writes are atomic (temp file + replace); deleted projects move to <c>Trash</c>. On first
    /// run the bundled samples are copied in so the list is never empty.
    /// </summary>
    public sealed class ProjectStore
    {
        public const string FileName = "house.json";
        public readonly string Root;

        public ProjectStore(string root = null)
        {
            Root = root ?? DefaultRoot();
            bool fresh = !Directory.Exists(Root);
            Directory.CreateDirectory(Root);
            if (fresh && root == null) MigrateFrom(Path.Combine(Application.persistentDataPath, "Projects"));
            SeedSamples();
        }

        /// <summary>
        /// One projects folder for the editor and every build (it must not depend on the product name):
        /// macOS ~/Library/Application Support/House/Projects, Windows %APPDATA%\House\Projects.
        /// </summary>
        public static string DefaultRoot()
        {
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string baseDir = Application.platform == RuntimePlatform.OSXPlayer || Application.platform == RuntimePlatform.OSXEditor
                ? Path.Combine(home, "Library", "Application Support")
                : Application.platform == RuntimePlatform.WindowsPlayer || Application.platform == RuntimePlatform.WindowsEditor
                    ? Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)
                    : Path.Combine(home, ".local", "share");
            return Path.Combine(baseDir, "House", "Projects");
        }

        /// <summary>Copies projects from an older location (the per-product persistentDataPath) on first use.</summary>
        void MigrateFrom(string old)
        {
            if (!Directory.Exists(old) || Path.GetFullPath(old) == Path.GetFullPath(Root)) return;
            foreach (var dir in Directory.GetDirectories(old))
            {
                string src = Path.Combine(dir, FileName), id = Path.GetFileName(dir);
                if (!File.Exists(src) || Directory.Exists(Path.Combine(Root, id))) continue;
                Directory.CreateDirectory(Path.Combine(Root, id));
                File.Copy(src, Path.Combine(Root, id, FileName));
            }
            Debug.Log($"[ProjectStore] migrated projects from {old}");
        }

        string Dir(string id) => Path.Combine(Root, id);
        string FileOf(string id) => Path.Combine(Dir(id), FileName);

        /// <summary>Preview picture of a project (written by the app after the lighting of the open project is baked).</summary>
        public string ThumbPath(string id) => Path.Combine(Dir(id), "thumb.jpg");

        public bool Exists(string id) => IsValidId(id) && File.Exists(FileOf(id));

        public static bool IsValidId(string id)
        {
            if (string.IsNullOrEmpty(id) || id.Length > 80) return false;
            foreach (char c in id)
                if (!(c >= 'a' && c <= 'z' || c >= '0' && c <= '9' || c == '-' || c == '_')) return false;
            return true;
        }

        public HouseDocument Load(string id)
        {
            if (!Exists(id)) throw new ArgumentException($"проект '{id}' не найден");
            return HouseJson.Deserialize(File.ReadAllText(FileOf(id)));
        }

        public void Save(string id, HouseDocument doc)
        {
            if (!IsValidId(id)) throw new ArgumentException($"недопустимый id проекта '{id}'");
            Directory.CreateDirectory(Dir(id));
            doc.Meta ??= new HouseMeta();
            doc.Meta.Modified = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
            string path = FileOf(id), tmp = path + ".tmp";
            File.WriteAllText(tmp, HouseJson.Serialize(doc), new UTF8Encoding(false));
            if (File.Exists(path)) File.Replace(tmp, path, null); else File.Move(tmp, path);
        }

        /// <summary>Creates a project from a document (name → readable unique id).</summary>
        public string Create(HouseDocument doc)
        {
            doc.Meta ??= new HouseMeta();
            doc.Meta.Created ??= DateTime.UtcNow.ToString("yyyy-MM-dd");
            string baseId = Slug(doc.Meta.Name);
            string id = baseId;
            for (int i = 2; Directory.Exists(Dir(id)); i++) id = baseId + "-" + i;
            Save(id, doc);
            return id;
        }

        /// <summary>Copies a project under a new name ("… (копия)"); the preview is copied too.</summary>
        public string Duplicate(string id)
        {
            var doc = Load(id);
            doc.Meta ??= new HouseMeta();
            doc.Meta.Name = (doc.Meta.Name ?? id) + " (копия)";
            doc.Meta.Created = DateTime.UtcNow.ToString("yyyy-MM-dd");
            string copy = Create(doc);
            try { if (File.Exists(ThumbPath(id))) File.Copy(ThumbPath(id), ThumbPath(copy), true); }
            catch (Exception) { /* the preview is re-rendered when the copy is opened */ }
            return copy;
        }

        /// <summary>Folder of a project on disk.</summary>
        public string FolderOf(string id) => Dir(id);

        /// <summary>Moves a project to <c>Projects/../Trash</c> (recoverable).</summary>
        public void Delete(string id)
        {
            if (!Exists(id)) throw new ArgumentException($"проект '{id}' не найден");
            string trash = Path.Combine(Path.GetDirectoryName(Root) ?? Root, "Trash");
            Directory.CreateDirectory(trash);
            string target = Path.Combine(trash, id + "-" + DateTime.UtcNow.ToString("yyyyMMddHHmmss"));
            Directory.Move(Dir(id), target);
        }

        // parsed summaries by file time: the project list re-reads only changed projects
        readonly Dictionary<string, (DateTime time, ProjectInfo info)> _infoCache = new Dictionary<string, (DateTime, ProjectInfo)>();

        public List<ProjectInfo> List()
        {
            var list = new List<ProjectInfo>();
            foreach (var dir in Directory.GetDirectories(Root))
            {
                string id = Path.GetFileName(dir);
                if (!Exists(id)) continue;
                DateTime time;
                try { time = File.GetLastWriteTimeUtc(FileOf(id)); }
                catch (Exception) { continue; }
                if (_infoCache.TryGetValue(id, out var hit) && hit.time == time) { list.Add(hit.info); continue; }
                ProjectInfo info;
                try { info = Info(id, Load(id)); }
                catch (Exception e) { info = new ProjectInfo { Id = id, Name = id, Description = "не читается: " + e.Message }; }
                _infoCache[id] = (time, info);
                list.Add(info);
            }
            list.Sort((a, b) => string.CompareOrdinal(b.Modified ?? "", a.Modified ?? ""));
            return list;
        }

        public static ProjectInfo Info(string id, HouseDocument d)
        {
            float area = 0f;
            foreach (var r in d.Rooms) if (r.Outline.Count >= 3) area += Mathf.Abs(Polygon.SignedArea(r.Outline));
            return new ProjectInfo
            {
                Id = id, Name = d.Meta?.Name, Description = d.Meta?.Description, Modified = d.Meta?.Modified ?? d.Meta?.Created,
                Levels = d.Levels.Count, Rooms = d.Rooms.Count, Items = d.Items.Count, Area = Mathf.Round(area * 10f) / 10f,
            };
        }

        /// <summary>Bundled sample documents (StreamingAssets/Samples) by file name without extension.</summary>
        public static Dictionary<string, string> Samples()
        {
            var map = new Dictionary<string, string>();
            string dir = Path.Combine(Application.streamingAssetsPath, "Samples");
            if (!Directory.Exists(dir)) return map;
            foreach (var f in Directory.GetFiles(dir, "*.house.json"))
                map[Path.GetFileName(f).Replace(".house.json", "")] = f;
            return map;
        }

        void SeedSamples()
        {
            string marker = Path.Combine(Root, ".seeded");
            if (File.Exists(marker)) return;
            foreach (var kv in Samples())
            {
                try { if (!Exists(kv.Key)) Save(kv.Key, HouseJson.Deserialize(File.ReadAllText(kv.Value))); }
                catch (Exception e) { Debug.LogWarning($"[ProjectStore] sample {kv.Key}: {e.Message}"); }
            }
            File.WriteAllText(marker, DateTime.UtcNow.ToString("o"));
        }

        static readonly string[] Translit =
        {
            "a", "b", "v", "g", "d", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya",
        };

        /// <summary>Readable id from a name: Cyrillic transliterated, lower case, dashes.</summary>
        public static string Slug(string name)
        {
            var sb = new StringBuilder();
            foreach (char ch in (name ?? "").ToLowerInvariant())
            {
                if (ch >= 'а' && ch <= 'я') sb.Append(Translit[ch - 'а']);
                else if (ch == 'ё') sb.Append("e");
                else if (ch >= 'a' && ch <= 'z' || ch >= '0' && ch <= '9') sb.Append(ch);
                else if (sb.Length > 0 && sb[sb.Length - 1] != '-') sb.Append('-');
            }
            string s = sb.ToString().Trim('-');
            if (s.Length > 40) s = s.Substring(0, 40).Trim('-');
            return s.Length == 0 ? "project" : s;
        }
    }
}
