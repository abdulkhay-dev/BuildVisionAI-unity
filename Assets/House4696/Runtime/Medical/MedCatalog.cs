using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace House4696.Medical
{
    /// <summary>
    /// The medical equipment catalogue in Resources/Medical: catalog.json (models) and one design per model in Designs/.
    /// Loaded on first use; <see cref="Reload"/> after editing the files in the editor.
    /// </summary>
    public static class MedCatalog
    {
        public const string Folder = "Medical";

        static readonly JsonSerializerSettings Json = new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver(),
            MissingMemberHandling = MissingMemberHandling.Ignore,
        };

        static MedCatalogFile _file;
        static readonly Dictionary<string, MedDesign> _designs = new Dictionary<string, MedDesign>(StringComparer.OrdinalIgnoreCase);

        public static MedCatalogFile File
        {
            get
            {
                if (_file != null) return _file;
                var text = Resources.Load<TextAsset>(Folder + "/catalog");
                try { _file = text != null ? JsonConvert.DeserializeObject<MedCatalogFile>(text.text, Json) : null; }
                catch (JsonException e) { Debug.LogError("[Medical] catalog.json: " + e.Message); }
                return _file ??= new MedCatalogFile();
            }
        }

        public static void Reload() { _file = null; _designs.Clear(); }

        public static MedModel Model(string id) =>
            id == null ? null : File.Models.FirstOrDefault(m => string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase));

        public static MedDesign ParseDesign(string json) => JsonConvert.DeserializeObject<MedDesign>(json, Json);

        public static MedDesign Design(string id)
        {
            if (id == null) return null;
            if (_designs.TryGetValue(id, out var d)) return d;
            var text = Resources.Load<TextAsset>(Folder + "/Designs/" + id);
            if (text == null) return null;
            try { d = ParseDesign(text.text); }
            catch (JsonException e) { Debug.LogError($"[Medical] Designs/{id}.json: {e.Message}"); return null; }
            if (d != null && d.Mats != null) d.Mats = new Dictionary<string, string>(d.Mats, StringComparer.OrdinalIgnoreCase);
            _designs[id] = d;
            return d;
        }
    }
}
