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
            var slab = new MeshBuilder();
            var finish = new MeshBuilder();
            var ceilings = new MeshBuilder();
            var fixtures = new MeshBuilder();
            foreach (var r in _c.Doc.Rooms)
            {
                if (r.Outline == null || r.Outline.Count < 3) { _c.Warn($"room '{r.Id}' needs at least 3 outline points"); continue; }
                var L = _c.Level(r.Level);
                float floorY = L.Elevation, h = r.Height ?? L.Height, ceilY = floorY + h;
                bool lowest = _c.IsLowest(L);
                var floorMat = _c.Mats.Get(r.Floor ?? DefaultFloor(r.Type), _c.M.Oak);
                var ceilMat = _c.Mats.Get(r.Ceiling, _c.M.Ceiling);
                var plaster = _c.M.Plaster;

                // structural slab (plaster edges), finish layer on top when it differs from the default oak
                bool tiled = floorMat != _c.M.Oak;
                float slabBottom = floorY - L.Slab + (lowest ? 0.02f : 0f);
                Polygon.Prism(slab, r.Outline, slabBottom, floorY, tiled ? null : floorMat, null, plaster);
                if (tiled)
                {
                    // thin finish plate replaces the slab top (tiles, porcelain, …)
                    Polygon.Prism(finish, r.Outline, floorY - 0.004f, floorY + 0.004f, floorMat, null, floorMat);
                }
                if (r.Type != RoomType.Terrace)
                    Polygon.Prism(ceilings, r.Outline, ceilY, ceilY + CeilingPlate, null, ceilMat, plaster);

                if (r.Downlights != "none" && r.Type != RoomType.Terrace) Downlights(fixtures, r, ceilY);
                if (r.Probe && r.Type != RoomType.Terrace) Probe(r, floorY, ceilY);
            }
            _c.W.Emit("Interior_Slabs", _c.Interior, slab);
            _c.W.Emit("Interior_FloorFinish", _c.Interior, finish);
            _c.W.Emit("Interior_Ceilings", _c.Interior, ceilings);
            _c.W.Emit("Decor_Downlights", _c.Interior, fixtures, castShadows: false);
        }

        /// <summary>Grid of recessed downlights ~1.5 m apart, kept 0.6 m off the walls, only inside the outline.</summary>
        void Downlights(MeshBuilder mb, RoomDef r, float ceilY)
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
                if (!Polygon.Contains(r.Outline, p)) continue;
                _c.Kit.Downlight(mb, new Vector3(x, ceilY, z));
            }
        }

        /// <summary>
        /// Box-projected probe fitted to the room: floors, marble and mirrors reflect the room, not the garden.
        /// The box reaches just past the wall faces but stops short of the glazing plane of exterior walls
        /// (panes sit 0.12–0.23 m inside the outer face), so windows keep reflecting the garden.
        /// </summary>
        void Probe(RoomDef r, float floorY, float ceilY)
        {
            const float margin = 0.1f, glassClear = 0.25f;
            var b0 = Polygon.Bounds(r.Outline);
            float x0 = b0.xMin - margin, x1 = b0.xMax + margin, z0 = b0.yMin - margin, z1 = b0.yMax + margin;
            foreach (var f in _c.Walls)
            {
                if (!f.Exterior || f.Y1 < floorY || f.Y0 > ceilY) continue;
                float c = Vector3.Dot(f.O, f.N);                        // outer face along the outward normal
                Vector3 pa = f.WorldA, pb = f.WorldB;
                if (Mathf.Abs(f.N.x) > 0.99f)
                {
                    if (Mathf.Min(pa.z, pb.z) > z1 || Mathf.Max(pa.z, pb.z) < z0) continue;
                    if (f.N.x > 0 && c > b0.center.x) x1 = Mathf.Min(x1, c - glassClear);
                    if (f.N.x < 0 && -c < b0.center.x) x0 = Mathf.Max(x0, -c + glassClear);
                }
                else if (Mathf.Abs(f.N.z) > 0.99f)
                {
                    if (Mathf.Min(pa.x, pb.x) > x1 || Mathf.Max(pa.x, pb.x) < x0) continue;
                    if (f.N.z > 0 && c > b0.center.y) z1 = Mathf.Min(z1, c - glassClear);
                    if (f.N.z < 0 && -c < b0.center.y) z0 = Mathf.Max(z0, -c + glassClear);
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
            p.resolution = 256;
            p.hdr = true;
            p.nearClipPlane = 0.05f;
            p.farClipPlane = 60f;
        }
    }
}
