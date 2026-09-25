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
        readonly MonoBehaviour _host;
        readonly string _version;

        public ApiHandlers(HouseSession session, ViewRenderer renderer, MonoBehaviour host, string version)
        {
            _s = session; _renderer = renderer; _host = host; _version = version;
        }

        public void Execute(LocalApi.Call c)
        {
            var a = c.Args;
            switch (c.Command)
            {
                case "status": c.Done.SetResult(Status()); return;
                case "catalog": c.Done.SetResult(Catalog((string)a["category"])); return;
                case "materials": c.Done.SetResult(new JArray(Materials())); return;
                case "list_projects": c.Done.SetResult(JArray.FromObject(_s.Store.List(), Camel)); return;
                case "create_project": c.Done.SetResult(CreateProject(a)); return;
                case "open_project": _s.Open(Req(a, "id")); Remember(); c.Done.SetResult(Changed(new List<string> { $"открыт проект '{_s.ProjectId}'" })); return;
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
                case "render": RequireProject(); _host.StartCoroutine(Render(a, c)); return;
                default: throw new ArgumentException($"неизвестная команда '{c.Command}'");
            }
        }

        // ------------------------------------------------------------------ projects
        JObject Status() => new JObject
        {
            ["app"] = "house", ["version"] = _version, ["project"] = _s.ProjectId, ["name"] = _s.Doc?.Meta?.Name,
            ["undo"] = _s.UndoCount, ["issues"] = _s.Issues.Count, ["buildMs"] = _s.LastBuildMs, ["projectsDir"] = _s.Store.Root,
            ["samples"] = new JArray(ProjectStore.Samples().Keys),
        };

        JObject CreateProject(JObject a)
        {
            string name = (string)a["name"] ?? "Новый дом";
            string template = (string)a["template"] ?? "empty";
            HouseDocument doc;
            if (template == "empty")
            {
                doc = new HouseDocument();
                doc.Levels.Add(new LevelDef { Id = "ground", Name = "1 этаж", Elevation = 0.3f, Height = 2.8f, Slab = 0.3f });
            }
            else
            {
                if (!ProjectStore.Samples().TryGetValue(template, out var path))
                    throw new ArgumentException($"нет шаблона '{template}'. Есть: empty, {string.Join(", ", ProjectStore.Samples().Keys)}");
                doc = HouseJson.Deserialize(File.ReadAllText(path));
            }
            doc.Meta = new HouseMeta { Name = name, Description = (string)a["description"] ?? doc.Meta?.Description, Author = "AI", Created = DateTime.UtcNow.ToString("yyyy-MM-dd") };
            string id = _s.Store.Create(doc);
            _s.Open(id);
            Remember();
            return Changed(new List<string> { $"создан проект '{id}' из шаблона '{template}' и открыт" });
        }

        JObject DeleteProject(string id)
        {
            bool current = id == _s.ProjectId;
            _s.Store.Delete(id);
            if (current) _s.Close();
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
            _s.Apply(doc);
            return Changed(new List<string> { "проект заменён целиком" });
        }

        JObject ExteriorWalls(JObject a)
        {
            var pts = (a["outline"] as JArray)?.Select(p => new Vector2((float)p[0], (float)p[1])).ToList()
                      ?? throw new ArgumentException("outline: массив точек [[x,z], …]");
            return Edit(n => DocumentOps.ExteriorWalls(_s.Doc, (string)a["level"] ?? _s.Doc.Levels.FirstOrDefault()?.Id, pts,
                (string)a["prefix"] ?? "w", (float?)a["thickness"], (string)a["outside"], (float?)a["plinth"], n));
        }

        void Remember()
        {
            if (_s.ProjectId != null) PlayerPrefs.SetString("house.lastProject", _s.ProjectId);
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
        static JArray Catalog(string category)
        {
            var arr = new JArray();
            foreach (var m in ItemCatalog.All.OrderBy(m => m.Category).ThenBy(m => m.Id))
                if (string.IsNullOrEmpty(category) || m.Category == category)
                    arr.Add(new JObject { ["id"] = m.Id, ["name"] = m.Name, ["category"] = m.Category, ["params"] = m.Params });
            return arr;
        }

        IEnumerable<string> Materials()
        {
            var lib = House4696.Core.MaterialLibrary.Create();
            var r = new MaterialResolver(lib, new House4696.Catalog.InteriorMaterials(lib));
            return r.Names.OrderBy(n => n);
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
