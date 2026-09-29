using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace House4696.Casegoods
{
    /// <summary>
    /// The case furniture catalogue in Resources/Casegoods: catalog.json (finishes, profiles, collections, models) and one
    /// design per model in Designs/. Loaded on first use; <see cref="Reload"/> after editing the files in the editor.
    /// </summary>
    public static class CaseCatalog
    {
        public const string Folder = "Casegoods";

        static readonly JsonSerializerSettings Json = new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver(),
            MissingMemberHandling = MissingMemberHandling.Ignore,
        };

        static CaseCatalogFile _file;
        static readonly Dictionary<string, CaseDesign> _designs = new Dictionary<string, CaseDesign>(StringComparer.OrdinalIgnoreCase);

        public static CaseCatalogFile File { get { Load(); return _file; } }

        public static void Reload()
        {
            _file = null;
            _designs.Clear();
        }

        public static CaseDesign ParseDesign(string json) => JsonConvert.DeserializeObject<CaseDesign>(json, Json);

        static void Load()
        {
            if (_file != null) return;
            var text = Resources.Load<TextAsset>(Folder + "/catalog");
            try { _file = text != null ? JsonConvert.DeserializeObject<CaseCatalogFile>(text.text, Json) : null; }
            catch (JsonException e) { Debug.LogError("[Casegoods] catalog.json: " + e.Message); }
            _file ??= new CaseCatalogFile();
            // profile ids are case-insensitive like everything else
            _file.Profiles = new Dictionary<string, CaseProfile>(_file.Profiles ?? new Dictionary<string, CaseProfile>(), StringComparer.OrdinalIgnoreCase);
        }

        public static CaseModel Model(string id) =>
            string.IsNullOrEmpty(id) ? null : File.Models.Find(m => string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase));

        public static CaseFinish Finish(string id) =>
            string.IsNullOrEmpty(id) ? null : File.Finishes.Find(f => string.Equals(f.Id, id, StringComparison.OrdinalIgnoreCase));

        public static CaseCollection Collection(string id) =>
            string.IsNullOrEmpty(id) ? null : File.Collections.Find(c => string.Equals(c.Id, id, StringComparison.OrdinalIgnoreCase));

        public static CaseProfile Profile(string id) =>
            id != null && File.Profiles.TryGetValue(id, out var p) ? p : null;

        public static CaseDesign Design(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            if (_designs.TryGetValue(id, out var d)) return d;
            var text = Resources.Load<TextAsset>(Folder + "/Designs/" + id);
            if (text != null)
            {
                try { d = ParseDesign(text.text); }
                catch (JsonException e) { Debug.LogError($"[Casegoods] design '{id}': {e.Message}"); }
                if (d != null && string.IsNullOrEmpty(d.Id)) d.Id = id;
            }
            _designs[id] = d;
            return d;
        }

        /// <summary>Finishes a model comes in: its own list, else its collection's.</summary>
        public static List<string> FinishesOf(CaseModel m) =>
            m.Finishes ?? Collection(m.Collection)?.Finishes ?? new List<string>();

        /// <summary>The finish an item asks for (a finish id), else the model's default, else the first it comes in.</summary>
        public static CaseFinish FinishFor(CaseModel m, string wanted) =>
            Finish(wanted) ?? Finish(m.Finish) ?? FinishesOf(m).Select(Finish).FirstOrDefault(f => f != null) ?? File.Finishes.FirstOrDefault();
    }
}
