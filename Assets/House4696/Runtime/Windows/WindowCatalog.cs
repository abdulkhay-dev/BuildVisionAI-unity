using System;
using System.Collections.Generic;
using System.Linq;
using House4696.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace House4696.Windows
{
    /// <summary>A catalogue window resolved for one opening.</summary>
    public sealed class ResolvedWindow
    {
        public WindowModel Model;
        public WindowDesign Design;
        public WindowFinish Finish;
        public string Title => $"{Model?.Name ?? Model?.Id} {Finish?.Name}".Trim();
    }

    /// <summary>
    /// The window catalogue in Resources/Windows: catalog.json (finishes, models) and one design per model in Designs/.
    /// Loaded on first use; <see cref="Reload"/> after editing the files in the editor.
    /// </summary>
    public static class WindowCatalog
    {
        public const string Folder = "Windows";

        static readonly JsonSerializerSettings Json = new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver(),
            MissingMemberHandling = MissingMemberHandling.Ignore,
        };

        static WindowCatalogFile _file;
        static readonly Dictionary<string, WindowDesign> _designs = new Dictionary<string, WindowDesign>(StringComparer.OrdinalIgnoreCase);

        public static WindowCatalogFile File { get { Load(); return _file; } }

        public static void Reload()
        {
            _file = null;
            _designs.Clear();
        }

        /// <summary>Uses <paramref name="file"/> and <paramref name="designs"/> instead of the shipped files until <see cref="Reload"/> (previews).</summary>
        public static void Use(WindowCatalogFile file, IEnumerable<WindowDesign> designs)
        {
            Reload();
            _file = file ?? new WindowCatalogFile();
            foreach (var d in designs ?? Enumerable.Empty<WindowDesign>()) if (d?.Id != null) _designs[d.Id] = d;
        }

        public static WindowDesign ParseDesign(string json) => JsonConvert.DeserializeObject<WindowDesign>(json, Json);

        static void Load()
        {
            if (_file != null) return;
            var text = Resources.Load<TextAsset>(Folder + "/catalog");
            try { _file = text != null ? JsonConvert.DeserializeObject<WindowCatalogFile>(text.text, Json) : null; }
            catch (JsonException e) { Debug.LogError("[Windows] catalog.json: " + e.Message); }
            _file ??= new WindowCatalogFile();
        }

        public static WindowModel Model(string id) =>
            string.IsNullOrEmpty(id) ? null : File.Models.Find(m => string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase));

        public static WindowFinish Finish(string id) =>
            string.IsNullOrEmpty(id) ? null : File.Finishes.Find(f => string.Equals(f.Id, id, StringComparison.OrdinalIgnoreCase));

        public static WindowDesign Design(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            if (_designs.TryGetValue(id, out var d)) return d;
            var text = Resources.Load<TextAsset>(Folder + "/Designs/" + id);
            if (text != null)
            {
                try { d = ParseDesign(text.text); }
                catch (JsonException e) { Debug.LogError($"[Windows] design '{id}': {e.Message}"); }
                if (d != null && string.IsNullOrEmpty(d.Id)) d.Id = id;
            }
            _designs[id] = d;
            return d;
        }

        /// <summary>Is the opening a catalogue window (a window / glazing that names a window model)?</summary>
        public static bool IsCatalogueWindow(OpeningDef o) =>
            o != null && (o.Type == OpeningType.Window || o.Type == OpeningType.Glazing) && Model(o.Model) != null;

        /// <summary>The model, design and finish of a window opening; problems (Russian) for the validator.</summary>
        public static ResolvedWindow Resolve(OpeningDef o, List<string> problems = null)
        {
            if (o == null || (o.Type != OpeningType.Window && o.Type != OpeningType.Glazing) || string.IsNullOrEmpty(o.Model)) return null;
            string who = $"окно '{o.Id}'";
            var model = Model(o.Model);
            if (model == null)
            {
                problems?.Add($"{who}: нет модели окна '{o.Model}' (список — house_windows)");
                return null;
            }
            var design = Design(model.Design ?? model.Id);
            if (design == null)
            {
                problems?.Add($"{who}: у модели '{model.Id}' нет чертежа (Windows/Designs/{model.Design ?? model.Id}.json)");
                return null;
            }
            var finish = Finish(o.Finish);
            if (o.Finish != null && finish == null)
                problems?.Add($"{who}: нет цвета рамы '{o.Finish}'; есть: {string.Join(", ", File.Finishes.Select(f => f.Id))}");
            else if (finish != null && model.Finishes != null && model.Finishes.Count > 0 &&
                     !model.Finishes.Contains(finish.Id, StringComparer.OrdinalIgnoreCase))
                problems?.Add($"{who}: {model.Name} бывает в цветах: {string.Join(", ", model.Finishes)}");
            return new ResolvedWindow { Model = model, Design = design, Finish = finish ?? Finish(model.Finish) ?? File.Finishes.FirstOrDefault() };
        }
    }
}
