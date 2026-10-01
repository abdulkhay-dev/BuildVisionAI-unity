using System.Collections.Generic;
using House4696.Core;
using House4696.Model;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Generation
{
    /// <summary>
    /// Rooms: floor slab under the room (top = floor finish), a thin ceiling plate at the room height (a
    /// double-height room simply has no room/slab above it), recessed downlights on a grid and one
    /// box-projected reflection probe per room. Upper slabs have no underside of their own — the ceilings of the
    /// rooms below cover it, which avoids coplanar faces.
    /// </summary>
    public sealed class RoomBuilder
    {
        const float CeilingPlate = 0.1f;   // thick enough that the sun's shadow bias cannot leak light through it
        readonly HouseContext _c;
        public RoomBuilder(HouseContext c) { _c = c; }

        public static string DefaultFloor(RoomType t) =>
            t == RoomType.Bathroom || t == RoomType.Utility ? "tile" : t == RoomType.Terrace ? "porcelain" : t == RoomType.Garage ? "concrete" : "oak";

        public void BuildAll()
        {
            // one mesh set per level: plan renders hide whole renderers above the cut, so a mesh must not span floors
            var sets = new Dictionary<string, (MeshBuilder slab, MeshBuilder finish, MeshBuilder ceilings, MeshBuilder fixtures)>();
            var order = new List<string>();
            (MeshBuilder slab, MeshBuilder finish, MeshBuilder ceilings, MeshBuilder fixtures) Set(LevelDef L)
            {
                string key = L.Id ?? "level";
                if (!sets.TryGetValue(key, out var s))
                {
                    sets[key] = s = (new MeshBuilder(), new MeshBuilder(), new MeshBuilder(), new MeshBuilder());
                    order.Add(key);
                }
                return s;
            }
            // the floor between and around the rooms: under partitions, doorways, passages, areas with no room
            var fill = new FloorFill(_c);
            foreach (var L in _c.Doc.Levels) fill.Build(L, Set(L).slab);
            foreach (var r in _c.Doc.Rooms)
            {
                if (r.Outline == null || r.Outline.Count < 3) { _c.Warn($"room '{r.Id}' needs at least 3 outline points"); continue; }
                var L = _c.Level(r.Level);
                var set = Set(L);
                var slab = set.slab; var finish = set.finish; var ceilings = set.ceilings; var fixtures = set.fixtures;
                float floorY = L.Elevation, h = r.Height ?? L.Height, ceilY = floorY + h;
                bool lowest = _c.IsLowest(L);
                var floorMat = _c.Mats.Get(r.Floor ?? DefaultFloor(r.Type), _c.M.Oak);
                var ceilMat = _c.Mats.Get(r.Ceiling, _c.M.Ceiling);
                var plaster = _c.M.Plaster;

                // structural slab (plaster edges), finish layer on top when it differs from the default oak
                bool tiled = floorMat != _c.M.Oak;
                float slabBottom = floorY - L.Slab + (lowest ? 0.02f : 0f);
                // stairwells: the floor opens over stairs arriving on this level, the ceiling over stairs rising through it
                var floorHoles = Wells(g => g.To.Id == L.Id);
                floorHoles.AddRange(_c.PoolCuts(floorY));   // an indoor pool sinks into the floor
                var ceilHoles = Wells(g => g.From.Elevation < ceilY - 0.01f && g.To.Elevation > ceilY - 0.01f);
                floorHoles.AddRange(_c.LiftCuts(floorY));   // lift shafts run through floors and ceilings
                ceilHoles.AddRange(_c.LiftCuts(ceilY));
                Polygon.Prism(slab, r.Outline, floorHoles, slabBottom, floorY, tiled ? null : floorMat, null, plaster);
                if (tiled)
                {
                    // thin finish plate replaces the slab top (tiles, porcelain, …)
                    Polygon.Prism(finish, r.Outline, floorHoles, floorY - 0.004f, floorY + 0.004f, floorMat, null, floorMat);
                }
                if (r.Type != RoomType.Terrace)
                    Polygon.Prism(ceilings, r.Outline, ceilHoles, ceilY, ceilY + CeilingPlate, null, ceilMat, plaster);

                if (r.Downlights != "none" && r.Type != RoomType.Terrace) Downlights(fixtures, r, ceilY, ceilHoles);
                if (r.Probe && r.Type != RoomType.Terrace) Probe(r, floorY, ceilY);
            }
            foreach (var key in order)
            {
                var set = sets[key];
                string sfx = order.Count > 1 ? "_" + key : "";
                _c.W.Emit("Interior_Slabs" + sfx, _c.Interior, set.slab);
                _c.W.Emit("Interior_FloorFinish" + sfx, _c.Interior, set.finish);
                _c.W.Emit("Interior_Ceilings" + sfx, _c.Interior, set.ceilings);
                _c.W.Emit("Decor_Downlights" + sfx, _c.Interior, set.fixtures, castShadows: false);
            }
        }

        List<Vector2[]> Wells(System.Func<StairGeometry, bool> where)
        {
            var list = new List<Vector2[]>();
            foreach (var g in _c.StairGeometries)
                if (where(g)) list.AddRange(g.Well);
            return list;
        }

        /// <summary>Grid of recessed downlights ~1.5 m apart, kept 0.6 m off the walls, only inside the outline.</summary>
        void Downlights(MeshBuilder mb, RoomDef r, float ceilY, List<Vector2[]> holes)
        {
            var b = Polygon.Bounds(r.Outline);
            const float inset = 0.6f, pitch = 1.5f;
            float w = b.width - 2 * inset, d = b.height - 2 * inset;
            int nx = Mathf.Max(1, Mathf.RoundToInt(w / pitch) + 1), nz = Mathf.Max(1, Mathf.RoundToInt(d / pitch) + 1);
            if (b.width < 1.4f) nx = 1;
            if (b.height < 1.4f) nz = 1;
            for (int i = 0; i < nx; i++)
            for (int j = 0; j < nz; j++)
            {
                float x = nx == 1 ? b.center.x : b.xMin + inset + w * i / (nx - 1);
                float z = nz == 1 ? b.center.y : b.yMin + inset + d * j / (nz - 1);
                var p = new Vector2(x, z);
                if (!Polygon.Contains(r.Outline, p) || holes.Exists(h => Polygon.Contains(h, p))) continue;
                _c.Kit.Downlight(mb, new Vector3(x, ceilY, z));
            }
        }

        /// <summary>
        /// Box-projected probe fitted to the room: floors, marble and mirrors reflect the room, not the garden.
        /// The box reaches past the wall faces to the middle of a thick wall (so the floor in a doorway between two rooms
        /// is inside a box and does not reflect the sky) but stops short of the glazing plane of exterior walls
        /// (panes sit 0.12–0.23 m inside the outer face), so windows keep reflecting the garden.
        /// </summary>
        /// <summary>Rooms up to which every probe gets 256 px; a bigger building gets 128 px probes.</summary>
        public const int FullResolutionRooms = 24;

        /// <summary>
        /// Probe size for a house with <paramref name="rooms"/> rooms. URP Forward+ packs every visible probe (up to 64)
        /// into one atlas per renderer that only grows: a 256 px probe takes a 1024² octahedral block plus mips, so a
        /// building with ~130 rooms filled two 16K atlases (1.5 GB) plus 0.5 GB of probe cubemaps. 128 px is a quarter
        /// of that and still sharp enough for box-projected floors and furniture in a big building.
        /// </summary>
        public static int ProbeResolution(int rooms) => rooms <= FullResolutionRooms ? 256 : 128;

        void Probe(RoomDef r, float floorY, float ceilY)
        {
            const float margin = 0.1f, reach = 0.25f, glassClear = 0.25f;
            var b0 = Polygon.Bounds(r.Outline);
            float x0 = b0.xMin - reach, x1 = b0.xMax + reach, z0 = b0.yMin - reach, z1 = b0.yMax + reach;
            foreach (var f in _c.Walls)
            {
                if (!f.Exterior || f.Y1 < floorY || f.Y0 > ceilY) continue;
                float c = Vector3.Dot(f.O, f.N);                        // outer face along the outward normal
                Vector3 pa = f.WorldA, pb = f.WorldB;
                if (Mathf.Abs(f.N.x) > 0.99f)
                {
                    if (Mathf.Min(pa.z, pb.z) > z1 || Mathf.Max(pa.z, pb.z) < z0) continue;
                    // a wall the room reaches past (an L-shaped room around a projecting entrance) does not bound it
                    if (f.N.x > 0 && c > b0.center.x && b0.xMax < c + 0.05f) x1 = Mathf.Min(x1, c - glassClear);
                    if (f.N.x < 0 && -c < b0.center.x && b0.xMin > -c - 0.05f) x0 = Mathf.Max(x0, -c + glassClear);
                }
                else if (Mathf.Abs(f.N.z) > 0.99f)
                {
                    if (Mathf.Min(pa.x, pb.x) > x1 || Mathf.Max(pa.x, pb.x) < x0) continue;
                    if (f.N.z > 0 && c > b0.center.y && b0.yMax < c + 0.05f) z1 = Mathf.Min(z1, c - glassClear);
                    if (f.N.z < 0 && -c < b0.center.y && b0.yMin > -c - 0.05f) z0 = Mathf.Max(z0, -c + glassClear);
                }
            }
            var b = Rect.MinMaxRect(x0, z0, Mathf.Max(x1, x0 + 0.5f), Mathf.Max(z1, z0 + 0.5f));
            var go = new GameObject("Probe_" + r.Id);
            go.transform.SetParent(_c.Probes, false);
            var center = new Vector3(b.center.x, (floorY + ceilY) * 0.5f, b.center.y);
            float captureY = Mathf.Min(floorY + 1.5f, ceilY - 0.2f);
            go.transform.position = new Vector3(center.x, captureY, center.z);
            var p = go.AddComponent<ReflectionProbe>();
            p.mode = ReflectionProbeMode.Realtime;
            p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
            p.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            p.boxProjection = true;
            p.size = new Vector3(b.width, ceilY - floorY + margin * 2f, b.height);
            p.center = center - go.transform.position;
            p.blendDistance = 0.08f;
            p.importance = 2;
            p.resolution = ProbeResolution(_c.Doc.Rooms.Count);
            p.hdr = true;
            p.nearClipPlane = 0.05f;
            p.farClipPlane = 60f;
        }
    }
}
