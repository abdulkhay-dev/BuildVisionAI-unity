using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using House4696.Generation;
using House4696.Model;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Commands of the local API (one per MCP tool, roughly). Every editing command answers with what changed,
    /// the validation issues and the generator's warnings, so the AI sees the consequences immediately.
    /// </summary>
    public sealed class ApiHandlers
    {
        static readonly Newtonsoft.Json.JsonSerializer Camel = Newtonsoft.Json.JsonSerializer.Create(new Newtonsoft.Json.JsonSerializerSettings
        {
            ContractResolver = new Newtonsoft.Json.Serialization.CamelCasePropertyNamesContractResolver(),
            NullValueHandling = Newtonsoft.Json.NullValueHandling.Ignore,
        });

        readonly HouseSession _s;
        readonly ViewRenderer _renderer;
        readonly HouseLighting _lighting;
        readonly MonoBehaviour _host;
        readonly string _version;

        public ApiHandlers(HouseSession session, ViewRenderer renderer, HouseLighting lighting, MonoBehaviour host, string version)
        {
            _s = session; _renderer = renderer; _lighting = lighting; _host = host; _version = version;
        }

        public void Execute(LocalApi.Call c)
        {
            var a = c.Args;
            switch (c.Command)
            {
                case "status": c.Done.SetResult(Status()); return;
                case "catalog": c.Done.SetResult(Catalog((string)a["category"], (string)a["id"])); return;
                case "doors": c.Done.SetResult(Doors((string)a["series"], (string)a["id"])); return;
                case "materials": c.Done.SetResult(Materials((string)a["category"])); return;
                case "inspect": RequireProject(); c.Done.SetResult(HouseInspector.Inspect(_s.Result, (string)a["section"], (string)a["id"])); return;
                case "list_projects": c.Done.SetResult(JArray.FromObject(_s.Store.List(), Camel)); return;
                case "create_project": c.Done.SetResult(CreateProject(a)); return;
                case "open_project": _s.Open(Req(a, "id")); c.Done.SetResult(Changed(new List<string> { $"открыт проект '{_s.ProjectId}'" })); return;
                case "delete_project": c.Done.SetResult(DeleteProject(Req(a, "id"))); return;
                case "get_project": c.Done.SetResult(GetProject((string)a["id"])); return;
                case "replace_project": c.Done.SetResult(Replace(a)); return;
                case "upsert": c.Done.SetResult(Edit(n => DocumentOps.Upsert(_s.Doc, Req(a, "kind"), a["data"], n))); return;
                case "remove":
                    c.Done.SetResult(Edit(n => DocumentOps.Remove(_s.Doc, Req(a, "kind"), (a["ids"] as JArray)?.Select(t => (string)t).ToList()
                        ?? throw new ArgumentException("ids: нужен массив id"), n)));
                    return;
                case "exterior_walls": c.Done.SetResult(ExteriorWalls(a)); return;
                case "validate": RequireProject(); c.Done.SetResult(Changed(new List<string>())); return;
                case "summary": RequireProject(); c.Done.SetResult(DocumentOps.Summary(_s.Doc)); return;
                case "undo":
                    RequireProject();
                    c.Done.SetResult(Changed(new List<string> { _s.Undo() ? "последнее изменение отменено" : "отменять нечего" }));
                    return;
                case "render": RequireProject(); _host.StartCoroutine(Guarded(Render(a, c), c)); return;
                case "tune": c.Done.SetResult(PerfProbe.Tune(a, _s)); return;
                case "measure":
                    _host.StartCoroutine(Guarded(PerfProbe.Measure(a["warmup"] != null ? (int)a["warmup"] : 120, a["frames"] != null ? (int)a["frames"] : 120,
                        r => c.Done.TrySetResult(r)), c));
                    return;
                case "bench":
                    _host.StartCoroutine(Guarded(PerfProbe.Bench(_s, _renderer, a["frames"] != null ? (int)a["frames"] : 240, (string)a["shots"],
                        r => c.Done.TrySetResult(r)), c));
                    return;
                case "ab":
                    RequireProject();
                    _host.StartCoroutine(Guarded(PerfProbe.AB(_s, a, r => c.Done.TrySetResult(r)), c));
                    return;
                case "perf":
                    _host.StartCoroutine(Guarded(PerfProbe.Sweep(_s, House4696.Core.HouseContent.Load().RealtimeGIRendererIndex,
                        a["frames"] != null ? (int)a["frames"] : 90, r => c.Done.TrySetResult(r)), c));
                    return;
                default: throw new ArgumentException($"неизвестная команда '{c.Command}'");
            }
        }

        // ------------------------------------------------------------------ projects
        JObject Status() => new JObject
        {
            ["app"] = "house", ["version"] = _version, ["project"] = _s.ProjectId, ["name"] = _s.Doc?.Meta?.Name,
            ["undo"] = _s.UndoCount, ["issues"] = _s.Issues.Count, ["buildMs"] = _s.LastBuildMs, ["projectsDir"] = _s.Store.Root,
            ["samples"] = new JArray(ProjectStore.Samples().Keys),
            ["lighting"] = _lighting?.ToJson(),
        };

        /// <summary>
        /// Runs a long command as a coroutine; an exception inside it answers the call with the error instead of
        /// leaving the client waiting for the timeout.
        /// </summary>
        static System.Collections.IEnumerator Guarded(System.Collections.IEnumerator work, LocalApi.Call c)
        {
            // nested enumerators are stepped here too, so an exception at any depth reaches the catch
            var stack = new Stack<System.Collections.IEnumerator>();
            stack.Push(work);
            while (stack.Count > 0)
            {
                object current;
                try
                {
                    if (!stack.Peek().MoveNext()) { stack.Pop(); continue; }
                    current = stack.Peek().Current;
                }
                catch (Exception e)
                {
                    // dispose every level so their finally blocks (render cleanup, queue release) run
                    while (stack.Count > 0) (stack.Pop() as IDisposable)?.Dispose();
                    Debug.LogException(e);
                    c.Done.TrySetException(e is ArgumentException || e is InvalidOperationException ? e : new InvalidOperationException(e.Message, e));
                    yield break;
                }
                if (current is System.Collections.IEnumerator nested) { stack.Push(nested); continue; }
                yield return current;
            }
        }

        JObject CreateProject(JObject a)
        {
            string template = (string)a["template"] ?? "empty";
            string id = _s.Create((string)a["name"], (string)a["description"], template, "AI");
            return Changed(new List<string> { $"создан проект '{id}' из шаблона '{template}' и открыт" });
        }

        JObject DeleteProject(string id)
        {
            bool current = id == _s.ProjectId;
            _s.Delete(id);
            return new JObject { ["notes"] = new JArray($"проект '{id}' перемещён в корзину" + (current ? " (он был открыт — теперь проект не открыт)" : "")) };
        }

        JToken GetProject(string id)
        {
            if (!string.IsNullOrEmpty(id) && id != _s.ProjectId) return JObject.Parse(HouseJson.Serialize(_s.Store.Load(id)));
            RequireProject();
            return JObject.Parse(HouseJson.Serialize(_s.Doc));
        }

        JObject Replace(JObject a)
        {
            RequireProject();
            var d = a["document"] as JObject ?? throw new ArgumentException("document: нужен объект проекта");
            HouseDocument doc;
            try { doc = HouseJson.Deserialize(d.ToString()); }
            catch (Exception e) { throw new ArgumentException("документ не читается: " + e.Message); }
            var notes = new List<string> { "проект заменён целиком" };
            House4696.Doors.DoorSizing.Normalize(doc, notes);
            _s.Apply(doc);
            return Changed(notes);
        }

        JObject ExteriorWalls(JObject a)
        {
            var pts = (a["outline"] as JArray)?.Select(p => new Vector2((float)p[0], (float)p[1])).ToList()
                      ?? throw new ArgumentException("outline: массив точек [[x,z], …]");
            return Edit(n => DocumentOps.ExteriorWalls(_s.Doc, (string)a["level"] ?? _s.Doc.Levels.FirstOrDefault()?.Id, pts,
                (string)a["prefix"] ?? "w", (float?)a["thickness"], (string)a["outside"], (float?)a["plinth"], n));
        }

        // ------------------------------------------------------------------ editing
        JObject Edit(Func<List<string>, HouseDocument> op)
        {
            RequireProject();
            var notes = new List<string>();
            var next = op(notes);
            _s.Apply(next);
            return Changed(notes);
        }

        /// <summary>Uniform answer after a change: notes, validation issues, generator warnings, short stats.</summary>
        JObject Changed(List<string> notes)
        {
            var o = new JObject { ["project"] = _s.ProjectId, ["notes"] = new JArray(notes) };
            if (_s.HasProject)
            {
                o["issues"] = new JArray(_s.Issues.Select(i => new JObject
                {
                    ["level"] = i.Level == IssueLevel.Error ? "error" : "warning", ["path"] = i.Path, ["message"] = i.Message,
                }));
                o["buildWarnings"] = new JArray(_s.Result?.Warnings ?? new List<string>());
                o["buildMs"] = _s.LastBuildMs;
                var d = _s.Doc;
                o["counts"] = new JObject
                {
                    ["levels"] = d.Levels.Count, ["walls"] = d.Walls.Count, ["openings"] = d.Openings.Count, ["rooms"] = d.Rooms.Count,
                    ["roofs"] = d.Roofs.Count, ["stairs"] = d.Stairs.Count, ["elements"] = d.Elements.Count, ["items"] = d.Items.Count,
                };
            }
            return o;
        }

        void RequireProject()
        {
            if (!_s.HasProject) throw new InvalidOperationException("нет открытого проекта — вызови create_project или open_project");
        }

        static string Req(JObject a, string key) =>
            (string)a[key] is string s && s.Length > 0 ? s : throw new ArgumentException($"не указан параметр '{key}'");

        // ------------------------------------------------------------------ catalogue & materials
        JObject Catalog(string category, string id)
        {
            var sizes = HouseBuilder.MeasureCatalog(_s.Mats);
            var arr = new JArray();
            var cats = new SortedSet<string>();
            foreach (var m in ItemCatalog.All.OrderBy(m => m.Category).ThenBy(m => m.Id))
            {
                cats.Add(m.Category);
                if (!string.IsNullOrEmpty(category) && m.Category != category) continue;
                if (!string.IsNullOrEmpty(id) && !string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase)) continue;
                var o = new JObject { ["id"] = m.Id, ["name"] = m.Name, ["category"] = m.Category };
                if (!string.IsNullOrEmpty(m.Params)) o["params"] = m.Params;
                if (sizes.TryGetValue(m.Id, out var b)) Describe(o, m, b);
                arr.Add(o);
            }
            return new JObject
            {
                ["frame"] = "size = [ширина поперёк фасада, глубина вдоль rotation, высота] с параметрами по умолчанию (меняются параметрами length/width/…). " +
                            "rotation — куда смотрит перед предмета (сиденье, дверцы, изножье кровати). fromOrigin — сколько предмет занимает от точки position в каждую сторону: " +
                            "front — вперёд по rotation, back — назад (к стене), left/right — влево/вправо, если стоять за предметом лицом по rotation.",
                ["categories"] = new JArray(cats),
                ["models"] = arr,
            };
        }

        /// <summary>
        /// The door catalogue for openings: series with their models, finishes and glass, standard sizes and how an opening
        /// follows its leaf. Filtered by series id or model id (the full list grows with the catalogue).
        /// </summary>
        const string DoorsHowTo =
            "Дверь из каталога — проём type door с полями model (id модели), finish (id цвета серии), glass (id стекла модели, " +
            "если у модели есть стекло) и leaf [ширина, высота] — размер полотна, м. Проём в стене (width/height) считается из полотна " +
            "сам: +0.095 по ширине и +0.07 по высоте (таблица каталога), поэтому для таких дверей задавай leaf, а не width. " +
            "Строится весь дверной блок: коробка, доборы под толщину стены, наличники с двух сторон (классика — пилястры, капители, карниз), петли, ручки. " +
            "hinge — сторона петель (start/end), swing — куда открывается (1 — влево от a→b стены, -1 — вправо), open: true — показать открытой. " +
            "kind: swing (распашная; leaves: 2 — двустворчатая), sliding (купе; едет вдоль стены к стороне hinge), " +
            "folding (книжка; leaf 0.35/0.4, leaves 2 или 4), portal (только обрамление проёма, нужен finish). Серии купе/книжек/порталов " +
            "дают kind сами. Готовые блоки (серия porta-x-blocks: 1П-03, 1П-02 WC, 2П-03) несут свои створки и замок. " +
            "Входные двери (kind серии entrance): ставь в наружную стену, leaf = размер блока из sizes серии (например [0.96, 2.05]), " +
            "finish — наружная отделка, finishIn — внутренняя панель (finishesIn), glass — стекло/зеркало внутренней панели.";

        static JObject Doors(string series, string id)
        {
            var cat = House4696.Doors.DoorCatalog.File;
            // no filter: a compact overview (the full catalogue is ~300 models) — series with their model ids and names
            if (string.IsNullOrEmpty(series) && string.IsNullOrEmpty(id))
            {
                var overview = new JArray();
                foreach (var s in cat.Series)
                    overview.Add(new JObject
                    {
                        ["id"] = s.Id, ["name"] = s.Name, ["line"] = s.Line, ["kind"] = s.Kind,
                        ["models"] = new JArray(s.Models.Select(m => (object)$"{m.Id} ({m.Name})")),
                    });
                return new JObject
                {
                    ["howTo"] = "Каталог дверей по сериям. Цвета (finish) и стёкла (glass) серии — house_doors с series=<id серии> " +
                                "или id=<id модели>. " + DoorsHowTo,
                    ["series"] = overview,
                };
            }
            var usedFinishes = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var usedGlass = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var list = new JArray();
            foreach (var s in cat.Series)
            {
                if (!string.IsNullOrEmpty(series) && !string.Equals(s.Id, series, StringComparison.OrdinalIgnoreCase)) continue;
                var models = new JArray();
                foreach (var m in s.Models)
                {
                    if (!string.IsNullOrEmpty(id) && !string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase)) continue;
                    var mo = new JObject { ["id"] = m.Id, ["name"] = m.Name };
                    var g = House4696.Doors.DoorCatalog.GlassOf(s, m);
                    if (g.Count > 0) mo["glass"] = new JArray(g);
                    if (m.Finishes != null) mo["finishes"] = new JArray(m.Finishes);
                    foreach (var x in g) usedGlass.Add(x);
                    foreach (var x in House4696.Doors.DoorCatalog.FinishesOf(s, m)) usedFinishes.Add(x);
                    models.Add(mo);
                }
                if (models.Count == 0) continue;
                var so = new JObject
                {
                    ["id"] = s.Id, ["name"] = s.Name, ["line"] = s.Line, ["kind"] = s.Kind,
                    ["finishes"] = new JArray(s.Finishes), ["models"] = models,
                };
                if (s.IsEntrance)
                {
                    if (s.FinishesIn != null) so["finishesIn"] = new JArray(s.FinishesIn);
                    var sizes = s.Sizes ?? new List<float[]> { new[] { 0.86f, 2.05f }, new[] { 0.96f, 2.05f } };
                    so["sizes"] = new JArray(sizes.Select(z => (object)new JArray(z[0], z[1])));
                    foreach (var x in s.FinishesIn ?? new List<string>()) usedFinishes.Add(x);
                }
                list.Add(so);
            }
            return new JObject
            {
                ["howTo"] = DoorsHowTo,
                ["sizes"] = new JObject
                {
                    ["leafWidths"] = new JArray(House4696.Doors.DoorSizing.Widths.Select(w => (object)w)),
                    ["leafHeight"] = House4696.Doors.DoorSizing.Height,
                    ["opening"] = "leaf + [0.095, 0.07]",
                },
                ["finishes"] = new JArray(cat.Finishes.Where(f => usedFinishes.Contains(f.Id))
                    .Select(f => new JObject { ["id"] = f.Id, ["name"] = f.Name, ["line"] = f.Line })),
                ["glass"] = new JArray(cat.Glass.Where(g => usedGlass.Contains(g.Id))
                    .Select(g => new JObject { ["id"] = g.Id, ["name"] = g.Name })),
                ["series"] = list,
            };
        }

        /// <summary>Size, extent from the placement point and a plain-words note about orientation and origin.</summary>
        static void Describe(JObject o, ItemModel m, Bounds b)
        {
            // model frame: front faces -Z, so forward = -z and (looking forward) right = -x
            float front = -b.min.z, back = b.max.z, right = -b.min.x, left = b.max.x;
            o["size"] = new JArray(Math.Round(b.size.x, 2), Math.Round(b.size.z, 2), Math.Round(b.size.y, 2));
            o["fromOrigin"] = new JObject
            {
                ["front"] = Math.Round(front, 2), ["back"] = Math.Round(back, 2), ["left"] = Math.Round(left, 2), ["right"] = Math.Round(right, 2),
                ["down"] = Math.Round(-b.min.y, 2), ["up"] = Math.Round(b.max.y, 2),
            };
            var notes = new List<string>();
            if (b.max.y <= 0.02f && b.min.y < -0.1f) notes.Add("точка — на потолке, предмет свисает вниз (Y = высота потолка над полом)");
            else if (b.size.z < 0.16f && back < 0.03f && b.size.x >= 0.3f) notes.Add("настенный: точка — на стене (задняя сторона), Y — высота этой точки над полом");
            else if (back < 0.05f && b.size.z > 0.3f) notes.Add("точка — у задней стороны: ставь её к стене, перед смотрит в комнату");
            if (b.size.z > b.size.x * 1.25f) notes.Add("длинная сторона идёт вдоль rotation");
            else if (b.size.x > b.size.z * 1.25f) notes.Add("длинная сторона — поперёк rotation (вдоль стены)");
            if (notes.Count > 0) o["note"] = string.Join("; ", notes);
        }

        /// <summary>Library materials (real PBR scans, with names and categories) and the built-in palette names.</summary>
        JObject Materials(string category)
        {
            var r = new MaterialResolver(_s.Mats, new House4696.Catalog.InteriorMaterials(_s.Mats));
            var library = new JArray();
            var ext = House4696.Core.ExternalCatalog.Load();
            var ids = new HashSet<string>();
            var cats = new SortedSet<string>();
            if (ext != null)
                foreach (var e in ext.Materials.OrderBy(e => e.Category).ThenBy(e => e.Id))
                {
                    ids.Add(MaterialResolver.Key(e.Id));
                    cats.Add(e.Category);
                    if (!string.IsNullOrEmpty(category) && e.Category != category) continue;
                    library.Add(new JObject { ["id"] = e.Id, ["name"] = e.Name, ["category"] = e.Category, ["tint"] = e.Neutral ? "задайте цвет: id#rrggbb" : "свой цвет; можно подкрасить id#rrggbb" });
                }
            var o = new JObject
            {
                ["howTo"] = "library — сканы с реальным масштабом рисунка (метр в метре): для полов, стен, фасадов, кровли, мощения, мебели. " +
                            "basic — встроенная палитра генератора: stone/plinth/stucco/wood/render — фасадные отделки стен; lawn, gravel, paver — поверхности участка " +
                            "(для верха элементов-газонов бери lawn, не ground-сканы); glass, led — служебные. Категории library: " + string.Join(", ", cats) + ".",
                ["library"] = library,
            };
            if (string.IsNullOrEmpty(category)) o["basic"] = new JArray(r.Names.Where(n => !ids.Contains(n)).OrderBy(n => n));
            return o;
        }

        // ------------------------------------------------------------------ rendering
        System.Collections.IEnumerator Render(JObject a, LocalApi.Call c)
        {
            var q = new RenderRequest();
            string mode = (string)a["mode"] ?? "orbit";
            q.Mode = mode == "plan" ? RenderMode.Plan : mode == "walk" ? RenderMode.Walk : RenderMode.Orbit;
            if (a["yaw"] != null) q.Yaw = (float)a["yaw"];
            if (a["pitch"] != null) q.Pitch = (float)a["pitch"];
            if (a["distance"] != null) q.Distance = (float)a["distance"];
            if (a["fov"] != null) q.Fov = (float)a["fov"];
            if (a["width"] != null) q.Width = (int)a["width"];
            if (a["height"] != null) q.Height = (int)a["height"];
            // interiors converge slower (less direct light, more bounces) than exterior views
            q.Frames = a["frames"] != null ? (int)a["frames"] : q.Mode == RenderMode.Walk ? 96 : 48;
            q.Level = (string)a["level"];
            if (a["position"] is JArray p && p.Count >= 2)
            {
                // walk position: [x, z] on the level floor or [x, y, z] absolute feet position
                float y = p.Count >= 3 ? (float)p[1] : ElevationOf(q.Level);
                q.Position = p.Count >= 3 ? new Vector3((float)p[0], y, (float)p[2]) : new Vector3((float)p[0], y, (float)p[1]);
            }
            if (q.Mode == RenderMode.Walk && a["position"] == null) { c.Done.SetException(new ArgumentException("walk: нужен position [x, z] (и level) или [x, y, z]")); yield break; }
            // the AI must see the finished lighting of what it just built
            if (_lighting != null && q.Mode != RenderMode.Plan) yield return _lighting.WaitForBake(120f);
            yield return _renderer.Render(q,
                png => c.Done.TrySetResult(new JObject { ["png"] = Convert.ToBase64String(png), ["width"] = q.Width, ["height"] = q.Height, ["mode"] = mode }),
                err => c.Done.TrySetException(new InvalidOperationException(err)));
        }

        float ElevationOf(string level)
        {
            var l = _s.Doc.Levels.Find(x => x.Id == level) ?? _s.Doc.Levels.FirstOrDefault();
            return l?.Elevation ?? 0f;
        }
    }
}
