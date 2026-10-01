using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using House4696.Generation;
using House4696.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Edits of a house document used by the MCP tools. Elements are addressed by kind ("wall", "room", …) and id;
    /// upserts merge fields into an existing element (so an AI can change one property) or append a new one.
    /// Unknown fields are reported instead of silently ignored — they are almost always typos.
    /// </summary>
    public static class DocumentOps
    {
        sealed class Kind
        {
            public string Array, Key;
            public Type Type;
        }

        static readonly Dictionary<string, Kind> Kinds = new Dictionary<string, Kind>(StringComparer.OrdinalIgnoreCase)
        {
            { "level", new Kind { Array = "levels", Key = "id", Type = typeof(LevelDef) } },
            { "wall", new Kind { Array = "walls", Key = "id", Type = typeof(WallDef) } },
            { "opening", new Kind { Array = "openings", Key = "id", Type = typeof(OpeningDef) } },
            { "room", new Kind { Array = "rooms", Key = "id", Type = typeof(RoomDef) } },
            { "roof", new Kind { Array = "roofs", Key = "id", Type = typeof(RoofDef) } },
            { "stair", new Kind { Array = "stairs", Key = "id", Type = typeof(StairDef) } },
            { "lift", new Kind { Array = "lifts", Key = "id", Type = typeof(LiftDef) } },
            { "element", new Kind { Array = "elements", Key = "id", Type = typeof(ElementDef) } },
            { "item", new Kind { Array = "items", Key = "id", Type = typeof(ItemDef) } },
            { "light", new Kind { Array = "lights", Key = "id", Type = typeof(LightDef) } },
            { "view", new Kind { Array = "views", Key = "name", Type = typeof(ViewDef) } },
        };

        public static IEnumerable<string> KindNames => Kinds.Keys;

        static Kind KindOf(string kind)
        {
            if (kind != null && kind.EndsWith("s") && !Kinds.ContainsKey(kind)) kind = kind.Substring(0, kind.Length - 1);
            if (kind == null || !Kinds.TryGetValue(kind, out var k))
                throw new ArgumentException($"неизвестный вид '{kind}'. Допустимо: {string.Join(", ", Kinds.Keys)}, meta, site");
            return k;
        }

        static JObject ToJ(HouseDocument d) => JObject.Parse(HouseJson.Serialize(d));

        static HouseDocument FromJ(JObject o)
        {
            try { return HouseJson.Deserialize(o.ToString(Formatting.None)); }
            catch (JsonException e) { throw new ArgumentException("документ не читается: " + e.Message); }
        }

        /// <summary>Adds or updates elements; returns notes (created/updated ids, unknown fields).</summary>
        public static HouseDocument Upsert(HouseDocument doc, string kind, JToken data, List<string> notes)
        {
            var root = ToJ(doc);
            if (kind == "meta" || kind == "site")
            {
                if (!(data is JObject patch)) throw new ArgumentException($"{kind}: нужен объект");
                CheckFields(patch, kind == "meta" ? typeof(HouseMeta) : typeof(SiteDef), kind, notes);
                if (!(root[kind] is JObject target)) { target = new JObject(); root[kind] = target; }
                target.Merge(patch, new JsonMergeSettings { MergeArrayHandling = MergeArrayHandling.Replace });
                notes.Add($"{kind} обновлено");
                return FromJ(root);
            }
            var k = KindOf(kind);
            // note: assigning a token that already has a parent clones it, so only attach a new array
            if (!(root[k.Array] is JArray arr)) { arr = new JArray(); root[k.Array] = arr; }
            var list = data is JArray a ? a.Children<JObject>().ToList() : data is JObject one ? new List<JObject> { one } : null;
            if (list == null || list.Count == 0) throw new ArgumentException("data: нужен объект или массив объектов");
            int auto = arr.Count;
            foreach (var item in list)
            {
                CheckFields(item, k.Type, kind, notes);
                string id = item[k.Key]?.Value<string>();
                if (string.IsNullOrEmpty(id))
                {
                    do id = $"{kind}_{++auto}"; while (arr.Children<JObject>().Any(e => (string)e[k.Key] == id));
                    item[k.Key] = id;
                }
                var existing = arr.Children<JObject>().FirstOrDefault(e => (string)e[k.Key] == id);
                // a catalogue door resized by its opening (width/height without leaf): the leaf is derived again from the opening
                if (existing != null && k.Array == "openings" && item["leaf"] == null && (item["width"] != null || item["height"] != null))
                    existing.Remove("leaf");
                if (existing != null)
                {
                    existing.Merge(item, new JsonMergeSettings { MergeArrayHandling = MergeArrayHandling.Replace, MergeNullValueHandling = MergeNullValueHandling.Merge });
                    notes.Add($"обновлено {kind} '{id}'");
                }
                else
                {
                    arr.Add(item);
                    notes.Add($"добавлено {kind} '{id}'");
                }
            }
            var result = FromJ(root);
            if (k.Array == "openings") House4696.Doors.DoorSizing.Normalize(result, notes);
            return result;
        }

        /// <summary>Removes elements by id; removing a wall also removes its openings, a level everything on it.</summary>
        public static HouseDocument Remove(HouseDocument doc, string kind, IList<string> ids, List<string> notes)
        {
            var k = KindOf(kind);
            var set = new HashSet<string>(ids);
            var root = ToJ(doc);
            var arr = root[k.Array] as JArray ?? new JArray();
            foreach (var id in ids)
                if (!arr.Children<JObject>().Any(e => (string)e[k.Key] == id)) notes.Add($"{kind} '{id}' не найден");
            int n = RemoveWhere(arr, e => set.Contains((string)e[k.Key]));
            notes.Add($"удалено {kind}: {n}");
            if (k.Array == "walls")
            {
                int o = RemoveWhere(root["openings"] as JArray, e => set.Contains((string)e["wall"]));
                if (o > 0) notes.Add($"вместе со стенами удалено проёмов: {o}");
            }
            if (k.Array == "levels")
            {
                foreach (var dep in new[] { "walls", "rooms", "items" })
                {
                    int c = RemoveWhere(root[dep] as JArray, e => set.Contains((string)e["level"]));
                    if (c > 0) notes.Add($"вместе с этажом удалено {dep}: {c}");
                }
            }
            return FromJ(root);
        }

        static int RemoveWhere(JArray arr, Func<JObject, bool> pred)
        {
            if (arr == null) return 0;
            var victims = arr.Children<JObject>().Where(pred).ToList();
            foreach (var v in victims) v.Remove();
            return victims.Count;
        }

        /// <summary>Reports fields that the target type does not have (typos such as "heigth" or "thicknes").</summary>
        /// <summary>Lists of the site edited element by element (by id), with their item types.</summary>
        public static readonly Dictionary<string, Type> SiteLists = new Dictionary<string, Type>(StringComparer.OrdinalIgnoreCase)
        {
            { "areas", typeof(SiteAreaDef) }, { "paths", typeof(SitePathDef) }, { "objects", typeof(SiteObjectDef) },
            { "hedges", typeof(SiteHedgeDef) }, { "beds", typeof(BedDef) }, { "streams", typeof(StreamDef) },
        };

        static string SiteList(string name)
        {
            if (name != null && !SiteLists.ContainsKey(name) && SiteLists.ContainsKey(name + "s")) name += "s";
            if (name == null || !SiteLists.ContainsKey(name))
                throw new ArgumentException($"список участка '{name}' неизвестен. Есть: {string.Join(", ", SiteLists.Keys)}");
            return name.ToLowerInvariant();
        }

        /// <summary>
        /// Edits the site: <paramref name="set"/> merges settings (landscape, plot, terrain, planting, fence, street, …),
        /// <paramref name="upsert"/> adds or updates list elements by id ({"areas": [...], "objects": [...]}; fields merge
        /// into an existing element), <paramref name="remove"/> deletes them by id ({"objects": ["t1"]}).
        /// </summary>
        public static HouseDocument Site(HouseDocument doc, JObject set, JObject upsert, JObject remove, List<string> notes)
        {
            var root = ToJ(doc);
            if (!(root["site"] is JObject site)) { site = new JObject(); root["site"] = site; }
            if (set != null && set.HasValues)
            {
                foreach (var p in set.Properties().ToList())
                    if (SiteLists.ContainsKey(p.Name))
                        throw new ArgumentException($"set.{p.Name}: списки участка правь через upsert/remove (по id), а не целиком");
                CheckFields(set, typeof(SiteDef), "site", notes);
                site.Merge(set, new JsonMergeSettings { MergeArrayHandling = MergeArrayHandling.Replace, MergeNullValueHandling = MergeNullValueHandling.Merge });
                notes.Add("настройки участка: " + string.Join(", ", set.Properties().Select(p => p.Name)));
            }
            if (upsert != null)
                foreach (var p in upsert.Properties())
                {
                    string name = SiteList(p.Name), single = name.TrimEnd('s');
                    if (!(site[name] is JArray arr)) { arr = new JArray(); site[name] = arr; }
                    var items = p.Value is JArray a ? a.Children<JObject>().ToList() : p.Value is JObject one ? new List<JObject> { one } : null;
                    if (items == null || items.Count == 0) throw new ArgumentException($"upsert.{p.Name}: нужен объект или массив объектов");
                    int auto = arr.Count;
                    foreach (var item in items)
                    {
                        CheckFields(item, SiteLists[name], $"site.{name}", notes);
                        string id = (string)item["id"];
                        if (string.IsNullOrEmpty(id))
                        {
                            do id = $"{single}{++auto}"; while (arr.Children<JObject>().Any(e => (string)e["id"] == id));
                            item["id"] = id;
                        }
                        var existing = arr.Children<JObject>().FirstOrDefault(e => (string)e["id"] == id);
                        if (existing != null)
                        {
                            existing.Merge(item, new JsonMergeSettings { MergeArrayHandling = MergeArrayHandling.Replace, MergeNullValueHandling = MergeNullValueHandling.Merge });
                            notes.Add($"обновлено {name} '{id}'");
                        }
                        else { arr.Add(item); notes.Add($"добавлено {name} '{id}'"); }
                    }
                }
            if (remove != null)
                foreach (var p in remove.Properties())
                {
                    string name = SiteList(p.Name);
                    var ids = new HashSet<string>(p.Value is JArray a ? a.Select(t => (string)t) : new[] { (string)p.Value });
                    var arr = site[name] as JArray;
                    foreach (var id in ids)
                        if (arr == null || !arr.Children<JObject>().Any(e => (string)e["id"] == id)) notes.Add($"{name} '{id}' не найден");
                    int n = RemoveWhere(arr, e => ids.Contains((string)e["id"]));
                    notes.Add($"удалено {name}: {n}");
                }
            return FromJ(root);
        }

        static void CheckFields(JObject o, Type t, string kind, List<string> notes)
        {
            // JSON names: an explicit [JsonProperty] name, else the camel-cased field name
            var names = new HashSet<string>(t.GetFields(BindingFlags.Public | BindingFlags.Instance).Select(f =>
                f.GetCustomAttribute<JsonPropertyAttribute>()?.PropertyName ?? char.ToLowerInvariant(f.Name[0]) + f.Name.Substring(1)));
            foreach (var p in o.Properties())
                if (!names.Contains(p.Name))
                    notes.Add($"ВНИМАНИЕ: у {kind} нет поля '{p.Name}' — оно проигнорировано. Поля: {string.Join(", ", names)}");
        }

        /// <summary>
        /// Exterior walls along a plan outline (any orientation; made counter-clockwise), ids prefix1..N. Existing walls
        /// with the same ids are replaced.
        /// </summary>
        public static HouseDocument ExteriorWalls(HouseDocument doc, string level, IList<Vector2> outline, string prefix,
                                                  float? thickness, string outside, float? plinth, List<string> notes)
        {
            if (outline == null || outline.Count < 3) throw new ArgumentException("outline: нужно минимум 3 точки");
            // counter-clockwise, but still starting at the caller's first point so wall 1 is the edge it expects
            var ccw = new List<Vector2>(outline);
            if (Polygon.SignedArea(ccw) < 0)
            {
                ccw.Reverse();
                ccw.Insert(0, ccw[ccw.Count - 1]);
                ccw.RemoveAt(ccw.Count - 1);
            }
            var data = new JArray();
            for (int i = 0; i < ccw.Count; i++)
            {
                var a = ccw[i]; var b = ccw[(i + 1) % ccw.Count];
                var w = new JObject
                {
                    ["id"] = $"{prefix}{i + 1}", ["level"] = level, ["kind"] = "exterior",
                    ["a"] = new JArray(Math.Round(a.x, 4), Math.Round(a.y, 4)), ["b"] = new JArray(Math.Round(b.x, 4), Math.Round(b.y, 4)),
                };
                if (thickness.HasValue) w["thickness"] = thickness.Value;
                if (outside != null) w["outside"] = outside;
                if (plinth.HasValue) w["plinth"] = plinth.Value;
                data.Add(w);
            }
            if (Polygon.SignedArea(outline) < 0) notes.Add("контур был по часовой стрелке — развёрнут против часовой (наружная грань снаружи)");
            var res = Upsert(doc, "wall", data, notes);
            notes.Add($"стены по контуру: {string.Join(", ", data.Select(w => (string)w["id"]))} (стена i идёт от точки i к точке i+1 развёрнутого контура)");
            return res;
        }

        /// <summary>Compact overview for an AI: sizes, levels, walls with lengths and openings, rooms with areas, counts.</summary>
        public static JObject Summary(HouseDocument d)
        {
            var o = new JObject { ["name"] = d.Meta?.Name, ["description"] = d.Meta?.Description };
            float x0 = float.MaxValue, z0 = float.MaxValue, x1 = float.MinValue, z1 = float.MinValue;
            foreach (var w in d.Walls)
            {
                if (w.Kind != WallKind.Exterior) continue;
                foreach (var p in new[] { w.A, w.B }) { x0 = Mathf.Min(x0, p.x); x1 = Mathf.Max(x1, p.x); z0 = Mathf.Min(z0, p.y); z1 = Mathf.Max(z1, p.y); }
            }
            if (x1 > x0) o["footprint"] = new JObject { ["min"] = new JArray(x0, z0), ["max"] = new JArray(x1, z1), ["size"] = $"{x1 - x0:0.##} × {z1 - z0:0.##} м" };
            o["levels"] = new JArray(d.Levels.Select(l => new JObject { ["id"] = l.Id, ["name"] = l.Name, ["elevation"] = l.Elevation, ["height"] = l.Height }));
            o["walls"] = new JArray(d.Walls.Select(w => new JObject
            {
                ["id"] = w.Id, ["level"] = w.Level, ["kind"] = w.Kind.ToString().ToLowerInvariant(), ["length"] = Math.Round((w.B - w.A).magnitude, 2),
                ["openings"] = new JArray(d.Openings.Where(op => op.Wall == w.Id).Select(op => $"{op.Id}: {op.Type.ToString().ToLowerInvariant()} at {op.At:0.##} w {op.Width:0.##}")),
            }));
            o["rooms"] = new JArray(d.Rooms.Select(r => new JObject
            {
                ["id"] = r.Id, ["name"] = r.Name, ["level"] = r.Level, ["type"] = r.Type.ToString().ToLowerInvariant(),
                ["area"] = r.Outline.Count >= 3 ? Math.Round(Mathf.Abs(Polygon.SignedArea(r.Outline)), 1) : 0,
                ["items"] = d.Items.Count(i => i.Room == r.Id || i.Room == null && i.Level == r.Level && r.Outline.Count >= 3 && Polygon.Contains(r.Outline, new Vector2(i.Position.x, i.Position.z))),
            }));
            o["roofs"] = new JArray(d.Roofs.Select(r => $"{r.Id}: {r.Type.ToString().ToLowerInvariant()} base {(r.Base.HasValue ? r.Base.Value.ToString("0.##") : "auto")} pitch {r.Pitch:0}"));
            o["stairs"] = new JArray(d.Stairs.Select(s => $"{s.Id}: {s.Type.ToString().ToLowerInvariant()} {s.From}→{s.To}"));
            o["counts"] = new JObject { ["elements"] = d.Elements.Count, ["items"] = d.Items.Count, ["lights"] = d.Lights.Count, ["views"] = d.Views.Count };
            return o;
        }
    }
}
