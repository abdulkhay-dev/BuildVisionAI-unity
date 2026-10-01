using System.Collections.Generic;
using System.Linq;
using House4696.Generation;
using House4696.Model;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// The site as the AI sees it through <c>house_site</c>: what is on the plot now (with the resolved plot, entrances,
    /// street side, the approach paths the generator adds, ground heights) and the vocabulary of site elements.
    /// </summary>
    public static class SiteInfo
    {
        public static readonly string[] AreaTypes = { "paving", "asphalt", "parking", "gravel", "deck", "rubber", "lawn" };
        public static readonly string[] PathStyles = { "stepping", "paving", "gravel", "asphalt", "deck" };
        public static readonly string[] ObjectTypes = { "tree", "shrub", "boulder", "bench", "bollard", "garden_lamp", "stone_lantern", "bridge" };
        public static readonly string[] TreeSpecies = { "oak", "birch", "spruce", "maple_red" };
        public static readonly string[] PlantingStyles = { "garden", "lawn", "perennial", "meadow", "shade", "rock", "none" };

        static JArray P(Vector2 p) => new JArray(R(p.x), R(p.y));
        static float R(float v) => Mathf.Round(v * 100f) / 100f;
        static JArray Rect4(Rect r) => new JArray(R(r.xMin), R(r.yMin), R(r.xMax), R(r.yMax));

        static SiteLayout Layout(HouseBuildResult r) =>
            r?.Context == null ? null : r.Context.Layout ?? new SiteLayout(r.Context, r.Footprint);

        /// <summary>Short state after an edit.</summary>
        public static JObject Brief(HouseDocument d, HouseBuildResult r)
        {
            var s = d.Site;
            var o = new JObject { ["landscape"] = s.Landscape.ToString().ToLowerInvariant() };
            var lay = Layout(r);
            if (lay != null)
            {
                o["plot"] = Rect4(lay.Plot);
                o["street"] = lay.Street;
                if (s.Landscape == LandscapePreset.Natural)
                    o["approach"] = new JArray(lay.Approach.Select(p => new JObject { ["id"] = p.Id, ["path"] = new JArray(p.Path.Select(P)) }));
            }
            o["counts"] = new JObject
            {
                ["areas"] = s.Areas.Count, ["paths"] = s.Paths.Count, ["objects"] = s.Objects.Count, ["hedges"] = s.Hedges.Count,
                ["beds"] = s.Beds.Count, ["streams"] = s.Streams.Count,
            };
            return o;
        }

        /// <summary>Everything about the site plus the vocabulary (house_site without arguments).</summary>
        public static JObject Describe(HouseDocument d, HouseBuildResult r)
        {
            var s = d.Site;
            var o = Brief(d, r);
            if (r != null) o["house"] = Rect4(r.Footprint);
            var lay = Layout(r);
            if (lay != null)
                o["entrances"] = new JArray(lay.Entrances.Select(e => new JObject
                {
                    ["opening"] = e.OpeningId, ["wall"] = e.WallId, ["at"] = P(e.Point), ["faces"] = SiteLayout.SideOf(e.Out),
                }));
            var m = r?.Context?.SiteModel;
            if (m != null)
            {
                var pl = m.Plot;
                float lo = float.MaxValue, hi = float.MinValue;
                for (float x = pl.xMin; x <= pl.xMax; x += 2f)
                for (float z = pl.yMin; z <= pl.yMax; z += 2f)
                {
                    float h = m.Height(x, z);
                    lo = Mathf.Min(lo, h); hi = Mathf.Max(hi, h);
                }
                o["ground"] = new JObject
                {
                    ["min"] = R(lo), ["max"] = R(hi),
                    ["corners"] = new JObject
                    {
                        ["sw"] = R(m.Height(pl.xMin, pl.yMin)), ["se"] = R(m.Height(pl.xMax, pl.yMin)),
                        ["nw"] = R(m.Height(pl.xMin, pl.yMax)), ["ne"] = R(m.Height(pl.xMax, pl.yMax)),
                    },
                    ["note"] = "дом стоит на ровной площадке на отметке 0; площадки (areas) выравниваются на своей высоте level",
                };
                o["areaLevels"] = new JArray(m.Areas.Select(a => new JObject { ["id"] = a.Def.Id, ["type"] = a.Def.Type, ["level"] = R(a.Level) }));
            }
            o["site"] = JObject.Parse(HouseJson.Serialize(new HouseDocument { Site = s }))["site"];
            o["vocabulary"] = new JObject
            {
                ["landscape"] = "natural — участок с рельефом и всеми элементами ниже (для работы с участком нужен он); garden/lawn/none — простой газон",
                ["areas.type"] = new JArray(AreaTypes),
                ["paths.style"] = new JArray(PathStyles),
                ["objects.type"] = new JArray(ObjectTypes),
                ["objects.species (tree)"] = new JArray(TreeSpecies),
                ["planting.style"] = new JArray(PlantingStyles),
                ["planting.flowers"] = new JArray(Landscape.Natural.PlantingPlan.Flowers),
                ["fence / street"] = new JArray(SiteLayout.Sides),
            };
            o["howTo"] = "house_site: set — настройки (landscape, plot, terrain, planting, fence, street, approach, sunAzimuth…), " +
                         "upsert — добавить/изменить элементы по id: {\"areas\": [...], \"paths\": [...], \"objects\": [...], \"hedges\": [...], \"beds\": [...], \"streams\": [...]}, " +
                         "remove — удалить по id: {\"objects\": [\"t1\"]}. Ряд одинаковых объектов (аллея, фонари вдоль дорожки) — один объект с path и spacing. " +
                         "Проверь: house_render mode=site (генплан сверху) и orbit.";
            return o;
        }
    }
}
