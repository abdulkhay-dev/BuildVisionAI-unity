using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// What grows where (port of tools/landscape/garden/scatter.py). Planting follows garden practice: drifts
    /// (Voronoi cells ~1.9 m) of one species; per zone a green structure (shrubs, grasses, ferns) that covers the
    /// ground and flower drifts interplanted as accents; spacing per species.
    /// </summary>
    public sealed class PlantingPlan
    {
        public readonly struct Species
        {
            public readonly string Group;
            public readonly float Spacing, ScaleMin, ScaleMax, Sink;
            public Species(string group, float spacing, float s0, float s1, float sink = 0f)
            { Group = group; Spacing = spacing; ScaleMin = s0; ScaleMax = s1; Sink = sink; }
        }

        public static readonly Dictionary<string, Species> All = new Dictionary<string, Species>
        {
            { "salvia", new Species("flower_salvia", 0.42f, 0.9f, 1.25f) },
            { "lavender", new Species("flower_lavender", 0.5f, 1.0f, 1.35f) },
            { "lupin", new Species("flower_lupin", 0.55f, 0.9f, 1.2f) },
            { "daisy", new Species("flower_daisy", 0.38f, 0.9f, 1.3f) },
            { "phlox", new Species("flower_pink", 0.45f, 0.9f, 1.3f) },
            { "yellow", new Species("flower_yellow", 0.35f, 1.2f, 1.7f) },
            { "orange", new Species("flower_orange", 1.2f, 0.45f, 0.6f) },
            { "hosta", new Species("hosta", 0.55f, 1.0f, 1.5f) },
            { "fern", new Species("fern", 0.75f, 0.9f, 1.4f) },
            { "tuft", new Species("grass_tuft", 0.5f, 1.8f, 2.8f, 0.02f) },
            { "shrub", new Species("shrub", 0.8f, 0.55f, 1.0f, 0.05f) },
            { "groundcover", new Species("groundcover_plant", 0.3f, 1.3f, 2.2f) },
        };

        /// <summary>Flower names an author may use (<see cref="PlantingDef.Flowers"/>).</summary>
        public static readonly string[] Flowers = { "salvia", "lavender", "lupin", "daisy", "phlox", "yellow", "orange" };

        sealed class Mix
        {
            public (string sp, float w)[] Structure, Accents;
            public float AccentShare;
            public Mix((string, float)[] s, (string, float)[] a, float share) { Structure = s; Accents = a; AccentShare = share; }
        }

        readonly Dictionary<Zone, Mix> _zones = new Dictionary<Zone, Mix>();
        readonly Dictionary<long, string> _cells = new Dictionary<long, string>();
        readonly int _seed;
        public readonly float Density;

        public PlantingPlan(PlantingDef def, int seed)
        {
            _seed = seed;
            Density = Mathf.Clamp(def.Density, 0.2f, 1.6f);
            string style = string.IsNullOrEmpty(def.Style) ? "perennial" : def.Style;
            (string, float)[] accents;
            switch (style)
            {
                case "meadow":
                    _zones[Zone.Bed] = new Mix(new[] { ("tuft", 4f), ("groundcover", 2f), ("shrub", 0.5f) },
                        accents = new[] { ("daisy", 3f), ("yellow", 2f), ("salvia", 1.5f), ("lupin", 1f), ("orange", 0.5f) }, 0.6f);
                    break;
                case "shade":
                    _zones[Zone.Bed] = new Mix(new[] { ("fern", 4f), ("hosta", 3f), ("groundcover", 2f), ("tuft", 1f) },
                        accents = new[] { ("lupin", 0.5f), ("daisy", 0.3f) }, 0.2f);
                    break;
                case "rock":
                    _zones[Zone.Bed] = new Mix(new[] { ("groundcover", 2f), ("tuft", 2f), ("shrub", 1f) },
                        accents = new[] { ("lavender", 2f), ("yellow", 1f), ("orange", 1f) }, 0.5f);
                    break;
                case "none":
                    accents = new (string, float)[0];
                    break;
                default:
                    _zones[Zone.Bed] = new Mix(new[] { ("shrub", 3f), ("tuft", 2.5f), ("groundcover", 2f), ("fern", 1f), ("hosta", 1f) },
                        accents = new[] { ("salvia", 3f), ("daisy", 2.5f), ("phlox", 2.5f), ("lavender", 2f), ("lupin", 1.2f),
                                          ("yellow", 0.6f), ("orange", 0.3f) }, 0.72f);
                    break;
            }
            if (def.Flowers != null && def.Flowers.Count > 0)
            {
                var own = new List<(string, float)>();
                foreach (var f in def.Flowers) if (All.ContainsKey(f)) own.Add((f, 1f));
                if (own.Count > 0) accents = own.ToArray();
            }
            if (style == "none") return;
            if (_zones.TryGetValue(Zone.Bed, out var bed)) bed.Accents = accents;
            _zones[Zone.Rim] = new Mix(new[] { ("groundcover", 3f), ("fern", 1f), ("tuft", 1.2f) }, new (string, float)[0], 0f);
            _zones[Zone.Bank] = new Mix(new[] { ("fern", 3f), ("hosta", 2.5f), ("tuft", 3f), ("groundcover", 2f), ("shrub", 1.2f) },
                FilterAccents(accents, new[] { "salvia", "daisy", "lupin", "lavender" }), 0.4f);
            _zones[Zone.Back] = new Mix(new[] { ("shrub", 4f), ("fern", 1.5f), ("tuft", 1.5f) },
                FilterAccents(accents, new[] { "lupin", "salvia" }), 0.3f);
        }

        static (string, float)[] FilterAccents((string, float)[] accents, string[] keep)
        {
            var list = new List<(string, float)>();
            foreach (var a in accents) if (System.Array.IndexOf(keep, a.Item1) >= 0) list.Add(a);
            return list.Count > 0 ? list.ToArray() : accents;
        }

        public bool Plants(Zone z) => _zones.ContainsKey(z);

        /// <summary>Species of the drift at a point; layer 0 = structure, 1 = accents (null: this drift has none).</summary>
        public string SpeciesAt(Zone zone, float x, float z, int layer)
        {
            if (!_zones.TryGetValue(zone, out var mix)) return null;
            var items = layer == 0 ? mix.Structure : mix.Accents;
            if (items.Length == 0) return null;
            float size = layer == 0 ? 1.9f : 1.4f;
            float gx = x / size, gz = z / size;
            int ix = Mathf.FloorToInt(gx), iz = Mathf.FloorToInt(gz);
            float best = float.MaxValue;
            string result = null;
            for (int dx = -1; dx <= 1; dx++)
            for (int dz = -1; dz <= 1; dz++)
            {
                int cx = ix + dx, cz = iz + dz;
                float px = cx + Noise.Hash01(cx, cz, _seed + 11 + layer), pz = cz + Noise.Hash01(cx, cz, _seed + 23 + layer);
                float d = (px - gx) * (px - gx) + (pz - gz) * (pz - gz);
                if (d < best) { best = d; result = Cell(zone, layer, cx, cz, items, mix.AccentShare); }
            }
            return result;
        }

        string Cell(Zone zone, int layer, int cx, int cz, (string sp, float w)[] items, float share)
        {
            long key = ((long)cx << 36) ^ ((long)(cz & 0xFFFFFF) << 8) ^ ((int)zone << 1) ^ layer;
            if (_cells.TryGetValue(key, out var sp)) return sp;
            float r = Noise.Hash01(cx * 3 + (int)zone, cz * 7 + layer, _seed + 101);
            if (layer == 1 && Noise.Hash01(cx, cz, _seed + 202 + (int)zone) > share) return _cells[key] = null;
            float total = 0f;
            foreach (var it in items) total += it.w;
            float pick = r * total;
            sp = items[items.Length - 1].sp;
            foreach (var it in items)
            {
                pick -= it.w;
                if (pick <= 0f) { sp = it.sp; break; }
            }
            return _cells[key] = sp;
        }
    }
}
