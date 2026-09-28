using System;
using System.Collections.Generic;
using System.Linq;
using House4696.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>A catalogue door resolved for one opening: model, design, finish and glass, and where they come from.</summary>
    public sealed class ResolvedDoor
    {
        public SeriesDef Series;
        public ModelDef Model;
        public DoorDesign Design;
        public FinishDef Finish;
        public GlassDef Glass;
        /// <summary>Entrance doors: the inner panel's design and finish (Design / Finish are the outer face).</summary>
        public DoorDesign Inner;
        public FinishDef FinishIn;

        public bool Entrance => Series != null && Series.IsEntrance;

        public string Block => Model?.Block ?? Series?.Block ?? "t70";
        public string Title => $"{Model?.Name ?? Model?.Id ?? "Портал"} {Finish?.Name}".Trim();
    }

    /// <summary>
    /// The door catalogue shipped in Resources/Doors: catalog.json (lines, series, models, finishes, glass) and one
    /// design per model in Designs/. Loaded on first use; <see cref="Reload"/> after editing the files in the editor.
    /// </summary>
    public static class DoorCatalog
    {
        public const string Folder = "Doors";

        static readonly JsonSerializerSettings Json = new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver(),
            MissingMemberHandling = MissingMemberHandling.Ignore,
        };

        static DoorCatalogFile _file;
        static readonly Dictionary<string, List<(SeriesDef series, ModelDef model)>> _offers =
            new Dictionary<string, List<(SeriesDef, ModelDef)>>(StringComparer.OrdinalIgnoreCase);
        static readonly Dictionary<string, DoorDesign> _designs = new Dictionary<string, DoorDesign>(StringComparer.OrdinalIgnoreCase);

        public static DoorCatalogFile File { get { Load(); return _file; } }

        public static void Reload()
        {
            _file = null;
            _offers.Clear();
            _designs.Clear();
        }

        /// <summary>
        /// Uses <paramref name="file"/> (and <paramref name="designs"/>) instead of the shipped files until <see cref="Reload"/>:
        /// previews of a design being drawn, tests.
        /// </summary>
        public static void Use(DoorCatalogFile file, IEnumerable<DoorDesign> designs = null)
        {
            Reload();
            _file = file ?? new DoorCatalogFile();
            foreach (var s in _file.Series)
            foreach (var m in s.Models)
            {
                if (string.IsNullOrEmpty(m.Id)) continue;
                if (!_offers.TryGetValue(m.Id, out var list)) _offers[m.Id] = list = new List<(SeriesDef, ModelDef)>();
                list.Add((s, m));
            }
            if (designs != null)
                foreach (var d in designs)
                    if (d != null && !string.IsNullOrEmpty(d.Id)) _designs[d.Id] = d;
        }

        /// <summary>Parses a design (the JSON of a design file).</summary>
        public static DoorDesign ParseDesign(string json) => JsonConvert.DeserializeObject<DoorDesign>(json, Json);

        /// <summary>Parses a catalogue (the JSON of catalog.json).</summary>
        public static DoorCatalogFile ParseCatalog(string json) => JsonConvert.DeserializeObject<DoorCatalogFile>(json, Json);

        static void Load()
        {
            if (_file != null) return;
            var text = Resources.Load<TextAsset>(Folder + "/catalog");
            try { _file = text != null ? JsonConvert.DeserializeObject<DoorCatalogFile>(text.text, Json) : null; }
            catch (JsonException e) { Debug.LogError("[Doors] catalog.json: " + e.Message); }
            _file ??= new DoorCatalogFile();
            // more series, one per file (Series/<id>.json): the catalogue grows series by series without merge conflicts
            var extra = new List<(int order, string name, SeriesDef s)>();
            foreach (var t in Resources.LoadAll<TextAsset>(Folder + "/Series"))
            {
                try
                {
                    var s = JsonConvert.DeserializeObject<SeriesDef>(t.text, Json);
                    if (s != null && !_file.Series.Exists(x => x.Id == s.Id)) extra.Add((s.Order, t.name, s));
                }
                catch (JsonException e) { Debug.LogError($"[Doors] Series/{t.name}.json: {e.Message}"); }
            }
            extra.Sort((a, b) => a.order != b.order ? a.order.CompareTo(b.order) : string.CompareOrdinal(a.name, b.name));
            foreach (var e in extra) _file.Series.Add(e.s);
            // finishes and glass of later waves, one file per family (Finishes/<family>.json, Glass/<family>.json: arrays)
            foreach (var t in Resources.LoadAll<TextAsset>(Folder + "/Finishes"))
            {
                try
                {
                    foreach (var f in JsonConvert.DeserializeObject<List<FinishDef>>(t.text, Json) ?? new List<FinishDef>())
                        if (f?.Id != null && !_file.Finishes.Exists(x => string.Equals(x.Id, f.Id, StringComparison.OrdinalIgnoreCase))) _file.Finishes.Add(f);
                }
                catch (JsonException e) { Debug.LogError($"[Doors] Finishes/{t.name}.json: {e.Message}"); }
            }
            foreach (var t in Resources.LoadAll<TextAsset>(Folder + "/Glass"))
            {
                try
                {
                    foreach (var g in JsonConvert.DeserializeObject<List<GlassDef>>(t.text, Json) ?? new List<GlassDef>())
                        if (g?.Id != null && !_file.Glass.Exists(x => string.Equals(x.Id, g.Id, StringComparison.OrdinalIgnoreCase))) _file.Glass.Add(g);
                }
                catch (JsonException e) { Debug.LogError($"[Doors] Glass/{t.name}.json: {e.Message}"); }
            }
            foreach (var s in _file.Series)
            foreach (var m in s.Models)
            {
                if (string.IsNullOrEmpty(m.Id)) continue;
                if (!_offers.TryGetValue(m.Id, out var list)) _offers[m.Id] = list = new List<(SeriesDef, ModelDef)>();
                list.Add((s, m));
            }
        }

        /// <summary>Model ids in catalogue order.</summary>
        public static IEnumerable<string> ModelIds { get { Load(); return _offers.Keys; } }

        /// <summary>Series that sell the model (the same design in several finishes lines), empty when unknown.</summary>
        public static IReadOnlyList<(SeriesDef series, ModelDef model)> Offers(string modelId)
        {
            Load();
            return modelId != null && _offers.TryGetValue(modelId, out var list) ? list : (IReadOnlyList<(SeriesDef, ModelDef)>)Array.Empty<(SeriesDef, ModelDef)>();
        }

        public static FinishDef Finish(string id) => id == null ? null : File.Finishes.Find(f => string.Equals(f.Id, id, StringComparison.OrdinalIgnoreCase));
        public static GlassDef Glass(string id) => id == null ? null : File.Glass.Find(g => string.Equals(g.Id, id, StringComparison.OrdinalIgnoreCase));

        public static List<string> FinishesOf(SeriesDef s, ModelDef m) => m.Finishes ?? s.Finishes ?? new List<string>();
        public static List<string> GlassOf(SeriesDef s, ModelDef m) => m.Glass ?? s.Glass ?? new List<string>();

        /// <summary>A design by id (cached), or null when there is no such file or it does not parse.</summary>
        public static DoorDesign Design(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            if (_designs.TryGetValue(id, out var d)) return d;
            var text = Resources.Load<TextAsset>(Folder + "/Designs/" + id);
            if (text != null)
            {
                try { d = JsonConvert.DeserializeObject<DoorDesign>(text.text, Json); }
                catch (JsonException e) { Debug.LogError($"[Doors] design '{id}': {e.Message}"); }
            }
            if (d != null && string.IsNullOrEmpty(d.Id)) d.Id = id;
            _designs[id] = d;
            return d;
        }

        /// <summary>
        /// The catalogue door of an opening: the model, the series that sells it in the requested finish, the finish and the
        /// glass (defaults: the first ones of the model). Problems go to <paramref name="problems"/> in Russian (unknown
        /// ids, a colour the model is not made in); null when the model or its design is missing — the opening then gets
        /// the plain built-in door.
        /// </summary>
        public static ResolvedDoor Resolve(OpeningDef o, List<string> problems = null)
        {
            if (o == null) return null;
            string who = $"проём '{o.Id}'";
            // a portal frames the opening: no leaf, no design — only a finish (its own, or the model's first)
            if (DoorSizing.KindOf(o) == DoorKind.Portal)
            {
                var pf = Finish(o.Finish);
                var po = string.IsNullOrEmpty(o.Model) ? null : Offers(o.Model);
                if (o.Finish != null && pf == null) problems?.Add($"{who}: нет отделки '{o.Finish}' (список — house_doors)");
                if (pf == null && po != null && po.Count > 0) pf = Finish(FinishesOf(po[0].series, po[0].model).FirstOrDefault());
                if (pf == null) { problems?.Add($"{who}: порталу нужна отделка finish (цвет из house_doors)"); return null; }
                return new ResolvedDoor { Finish = pf, Series = po != null && po.Count > 0 ? po[0].series : null, Model = po != null && po.Count > 0 ? po[0].model : null };
            }
            if (string.IsNullOrEmpty(o.Model)) return null;
            // series of the opening's kind first (TWIGGY is sold as a sliding and as a folding door; any interior door can
            // also hang as a sliding one)
            var kind = DoorSizing.KindOf(o);
            var offers = Offers(o.Model).OrderBy(of => DoorSizing.SeriesKind(of.series) == kind ? 0 : 1).ToList();
            if (offers.Count == 0)
            {
                problems?.Add($"{who}: нет модели двери '{o.Model}' в каталоге (список — house_catalog, раздел doors)");
                return null;
            }
            var r = new ResolvedDoor();
            var finish = Finish(o.Finish);
            if (o.Finish != null && finish == null)
                problems?.Add($"{who}: нет отделки '{o.Finish}'; у модели {offers[0].model.Name}: {string.Join(", ", FinishesOf(offers[0].series, offers[0].model))}");
            // the series that sells this model in the finish, else the first one
            var offer = finish != null ? offers.FirstOrDefault(of => FinishesOf(of.series, of.model).Contains(finish.Id, StringComparer.OrdinalIgnoreCase)) : default;
            if (offer.series == null)
            {
                if (finish != null)
                    problems?.Add($"{who}: {offers[0].model.Name} не выпускается в цвете {finish.Name} — есть: " +
                                  string.Join(", ", offers.SelectMany(of => FinishesOf(of.series, of.model)).Distinct()));
                offer = offers[0];
            }
            r.Series = offer.series;
            r.Model = offer.model;
            r.Finish = finish ?? Finish(FinishesOf(offer.series, offer.model).FirstOrDefault());

            var glassIds = GlassOf(offer.series, offer.model);
            var glass = Glass(o.Glass);
            if (o.Glass != null && glass == null)
                problems?.Add($"{who}: нет стекла '{o.Glass}'; у модели: {(glassIds.Count > 0 ? string.Join(", ", glassIds) : "без стекла")}");
            else if (glass != null && glassIds.Count > 0 && !glassIds.Contains(glass.Id, StringComparer.OrdinalIgnoreCase))
                problems?.Add($"{who}: {r.Model.Name} не выпускается со стеклом {glass.Id} — есть: {string.Join(", ", glassIds)}");
            r.Glass = glass ?? Glass(glassIds.FirstOrDefault()) ?? Glass("mf");

            r.Design = Design(offer.model.Design ?? offer.model.Id);
            if (r.Design == null)
            {
                problems?.Add($"{who}: у модели '{o.Model}' нет чертежа (Designs/{offer.model.Design ?? offer.model.Id}.json)");
                return null;
            }
            if (offer.model.Hinges != null && offer.model.Hinges.Length > 0) r.Design = r.Design.WithHinges(offer.model.Hinges);
            if (r.Entrance)
            {
                // the inner panel: its own design and finish (the catalogue writes them "outer / inner")
                r.Inner = Design(offer.model.Inner) ?? r.Design;
                var ins = offer.model.FinishesIn ?? offer.series.FinishesIn ?? new List<string>();
                var fin = Finish(o.FinishIn);
                if (o.FinishIn != null && fin == null) problems?.Add($"{who}: нет отделки '{o.FinishIn}' для внутренней панели; есть: {string.Join(", ", ins)}");
                else if (fin != null && ins.Count > 0 && !ins.Contains(fin.Id, StringComparer.OrdinalIgnoreCase))
                    problems?.Add($"{who}: внутренняя панель {r.Model.Name} не выпускается в цвете {fin.Name} — есть: {string.Join(", ", ins)}");
                r.FinishIn = fin ?? Finish(ins.FirstOrDefault()) ?? r.Finish;
            }
            return r;
        }
    }
}
