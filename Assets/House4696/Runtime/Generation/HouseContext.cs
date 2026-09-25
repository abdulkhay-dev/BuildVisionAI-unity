using System.Collections.Generic;
using House4696.Core;
using House4696.Catalog;
using House4696.Landscape;
using House4696.Model;
using UnityEngine;

namespace House4696.Generation
{
    /// <summary>Shared state of one generation run: the document with lookups, materials, writer and output groups.</summary>
    public sealed class HouseContext
    {
        public readonly HouseDocument Doc;
        public readonly MaterialResolver Mats;
        public readonly InteriorMaterials M;
        public readonly MaterialLibrary Lib;
        public readonly FurnitureKit Kit;
        public readonly VegetationFactory Veg;
        public readonly SceneWriter W;
        public readonly List<string> Warnings = new List<string>();

        readonly Dictionary<string, LevelDef> _levels = new Dictionary<string, LevelDef>();
        readonly Dictionary<string, WallFrame> _walls = new Dictionary<string, WallFrame>();

        public Transform Root, Shell, Interior, Doors, Furniture, Plants, Lights, Probes;

        public HouseContext(HouseDocument doc, MaterialLibrary lib, SceneWriter w)
        {
            Doc = doc; Lib = lib; W = w;
            M = new InteriorMaterials(lib);
            Mats = new MaterialResolver(lib, M);
            Kit = new FurnitureKit(M);
            Veg = new VegetationFactory(lib);
            var sorted = new List<LevelDef>(doc.Levels);
            sorted.Sort((a, b) => a.Elevation.CompareTo(b.Elevation));
            doc.Levels.Clear();
            doc.Levels.AddRange(sorted);
            foreach (var l in doc.Levels) if (!string.IsNullOrEmpty(l.Id)) _levels[l.Id] = l;
            foreach (var wd in doc.Walls) _walls[wd.Id ?? ("wall" + _walls.Count)] = new WallFrame(wd, this);
            DetectCorners();
        }

        /// <summary>
        /// Outside corners of exterior walls (end of one wall meets the start of the next with a left turn, i.e. a
        /// convex corner of a counter-clockwise outline): the cladding wraps around them unless set explicitly.
        /// </summary>
        void DetectCorners()
        {
            foreach (var f in _walls.Values)
            foreach (var g in _walls.Values)
            {
                if (f == g || !f.Exterior || !g.Exterior) continue;
                if ((f.WorldB - g.WorldA).sqrMagnitude > 0.0004f) continue;
                bool convex = Vector3.Cross(f.A, g.A).y < -1e-4f;
                if (!convex) continue;
                if (f.Def.WrapEnd == null) f.WrapEnd = true;
                if (g.Def.WrapStart == null) g.WrapStart = true;
            }
        }

        public void Warn(string msg) { Warnings.Add(msg); Debug.LogWarning("[House] " + msg); }

        public LevelDef Level(string id)
        {
            if (id != null && _levels.TryGetValue(id, out var l)) return l;
            return Doc.Levels.Count > 0 ? Doc.Levels[0] : new LevelDef { Id = "ground" };
        }

        public float Elevation(string levelId) => string.IsNullOrEmpty(levelId) ? 0f : Level(levelId).Elevation;

        /// <summary>The level directly above, or null for the top level.</summary>
        public LevelDef Above(LevelDef l)
        {
            int i = Doc.Levels.IndexOf(l);
            return i >= 0 && i + 1 < Doc.Levels.Count ? Doc.Levels[i + 1] : null;
        }

        public bool IsLowest(LevelDef l) => Doc.Levels.Count == 0 || Doc.Levels[0] == l;

        /// <summary>Height of the underside of the structure above a level's ceiling (next floor's slab bottom or roof).</summary>
        public float TopOfLevel(LevelDef l)
        {
            var up = Above(l);
            return up != null ? up.Elevation : l.Elevation + l.Height + 0.3f;
        }

        public WallFrame Wall(string id) => id != null && _walls.TryGetValue(id, out var f) ? f : null;
        public IEnumerable<WallFrame> Walls => _walls.Values;
    }
}
