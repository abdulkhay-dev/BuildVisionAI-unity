using System;
using System.Collections.Generic;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.App
{
    /// <summary>
    /// Perf plan step 8: per-camera budget for lamp shadow maps. Every shadowed lamp costs URP a full shadow render
    /// every frame (a point lamp = 6 cube faces), wherever the camera is. For the viewer camera only, a lamp keeps
    /// its shadow when its light or its shadows can be seen:
    /// <list type="bullet">
    /// <item>(b) its lit volume (range sphere, or the spot cone) reaches a room the camera stands in, or a room seen
    /// from there through an open interior door, an interior window or a glass screen (<see cref="PortalRooms"/>) —
    /// otherwise its unshadowed light would leak through the walls into a visible room;</item>
    /// <item>(a') the camera is outside the house, and an exterior opening within the lamp's effective radius is in
    /// view and faces the camera (the lit room is seen through the glazing);</item>
    /// <item>(c) the lamp or a point of the pool it lights is in view and not hidden by a wall, partition, slab,
    /// ceiling or roof (glass, doors and furniture do not hide).</item>
    /// </list>
    /// Otherwise the shadow strength is held for <see cref="HoldSeconds"/>, then faded out; at 0 URP drops the
    /// lamp from the shadow atlas (variant-safe: the shadow keyword stays on). Any other camera (AI stills,
    /// snapshots, thumbnails, reflection probes, the editor scene view) always renders every lamp's shadow.
    /// </summary>
    public sealed class LampShadowBudget : MonoBehaviour
    {
        /// <summary>
        /// Master switch. Off = every lamp keeps its own shadow strength. PerfProbe sweep / bench should turn it off
        /// (and restore it after) so their measurements are not view dependent.
        /// </summary>
        public static bool Enabled = true;

        /// <summary>
        /// Rule (b) also covers rooms seen from the camera's room through an interior opening in view (open door,
        /// interior window / hole, steel-glass screen): a lamp next door whose light reaches that room through the
        /// wall keeps its shadow (e.g. the media-wall grazers leak into the hall seen from the guest room). Off = rule
        /// (b) tests the camera's own rooms only (the plan's rule).
        /// </summary>
        public static bool PortalRooms = true;

        /// <summary>
        /// The camera is in none of the document's rooms but inside the house footprint below the top ceiling (a space
        /// the document does not describe as a room, e.g. an undefined corridor, or a balcony / terrace without a
        /// terrace room): the room rules cannot judge it, so every lamp keeps its shadow there.
        /// </summary>
        public static bool GuardUnmappedInterior = true;

        /// <summary>Diagnostics: shadowed lamps managed and how many currently render no shadow map for the viewer.</summary>
        public static int LampCount { get; private set; }
        public static int DroppedCount { get; private set; }

        // --------------------------------------------------------------- tuning (conservative defaults)
        /// <summary>A lamp that is no longer needed keeps its shadow this long before fading (turning, doorways).</summary>
        const float HoldSeconds = 1f;
        /// <summary>Fade-out speed of the shadow strength once the hold ran out (per second: 4 = a quarter second).</summary>
        const float RampPerSecond = 4f;
        /// <summary>Illuminance (URP light units) below which a lamp's light is considered invisible: sets its effective radius.</summary>
        const float EffectiveIlluminance = 0.03f;
        /// <summary>Rule (a'): cosine between an opening's outward normal and the direction to the camera.</summary>
        const float OpeningFacingMin = 0.2f;
        /// <summary>Rule (b): fraction of the lamp range tested against the camera's room (1 = the whole lit volume).</summary>
        const float RoomReachScale = 1f;
        /// <summary>The camera counts as standing in a room within this plan distance of it (doorways, wall thickness).</summary>
        const float RoomSnap = 0.6f, RoomSnapY = 0.3f;
        /// <summary>Rule (c): points sampled around the centre of the lamp's pool of light.</summary>
        const int PoolRing = 8;
        const float PoolMinRadius = 0.3f, PoolMaxRadius = 4f;
        /// <summary>Rule (c): a sample counts as in view up to this far outside the frustum, metres.</summary>
        const float FrustumMargin = 0.5f;
        /// <summary>Samples sit this far in front of the surface they lie on, so the ray to them does not hit it.</summary>
        const float SurfaceOffset = 0.05f;
        /// <summary>Narrow spots (half angle ≤ 45°): the cone is covered by this many spheres for the room test.</summary>
        const int SpotCoverSpheres = 8;
        /// <summary><see cref="PortalRooms"/>: a room belongs to an interior opening when its outline lies within half the wall thickness plus this.</summary>
        const float PortalSnap = 0.15f;

        sealed class Lamp
        {
            public Light Light;
            public float Original;               // the lamp's own shadow strength
            public float Budget = 1f;            // 0..1 factor the viewer renders with
            public float Hold = HoldSeconds;
            public Vector4 Tight;                // sphere containing the lit volume: xyz centre, w radius
            public Vector4[] Cover;              // spheres covering a narrow spot cone (null: Tight only)
            public Bounds Reach;                 // AABB of Tight, frustum pre-test for rule (c)
            public readonly List<int> Openings = new List<int>();          // exterior openings within the effective radius
            public readonly List<Vector3> Samples = new List<Vector3>();    // the lamp + points of its pool of light
        }

        struct Opening { public Bounds Bounds; public Vector3 Centre, Normal; }
        struct Prism { public List<Vector2> Outline; public float Y0, Y1; public bool Terrace; }
        /// <summary>Interior opening: the rooms on its sides and its door leaf (null: always see-through).</summary>
        struct Portal { public Bounds Bounds; public int[] Rooms; public Door Door; }

        readonly List<Lamp> _lamps = new List<Lamp>();
        readonly List<Opening> _openings = new List<Opening>();
        readonly List<Prism> _prisms = new List<Prism>();
        readonly List<Portal> _portals = new List<Portal>();
        readonly List<int> _cameraRooms = new List<int>();
        readonly List<int> _visibleRooms = new List<int>();     // camera rooms + rooms seen through their interior openings
        Rect _footprint;
        float _interiorTop = float.MinValue;                    // highest ceiling of the document
        readonly HashSet<Collider> _blockers = new HashSet<Collider>();
        readonly Plane[] _planes = new Plane[6];
        readonly RaycastHit[] _hits = new RaycastHit[64];

        HouseSession _session;
        Camera _viewer;
        int _mask = Physics.DefaultRaycastLayers;
        bool _dirty, _ready;
        int _dirtyFrame = -1, _evalFrame = -1;

        public void Init(HouseSession session)
        {
            _session = session;
            _session.Rebuilt += MarkDirty;
            _session.ProjectChanged += MarkDirty;
            if (_session.Result != null) MarkDirty();
        }

        void OnEnable() => RenderPipelineManager.beginCameraRendering += OnBeginCamera;

        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering -= OnBeginCamera;
            Restore();
        }

        void OnDestroy()
        {
            if (_session == null) return;
            _session.Rebuilt -= MarkDirty;
            _session.ProjectChanged -= MarkDirty;
        }

        /// <summary>The house was rebuilt: the lamp list is rebuilt a frame later, when the old house is gone.</summary>
        void MarkDirty()
        {
            Restore();
            _lamps.Clear();
            _ready = false;
            _dirty = true;
            _dirtyFrame = Time.frameCount;
        }

        void OnBeginCamera(ScriptableRenderContext context, Camera cam)
        {
            if (!Enabled || !IsViewer(cam))
            {
                Restore();
                return;
            }
            if (_dirty && Time.frameCount > _dirtyFrame) Build();
            if (!_ready) return;
            if (_evalFrame != Time.frameCount)
            {
                _evalFrame = Time.frameCount;
                Evaluate(cam, Mathf.Min(Time.unscaledDeltaTime, 0.1f));
            }
            int dropped = 0;
            foreach (var l in _lamps)
            {
                if (l.Light == null) continue;
                float s = l.Original * l.Budget;
                if (l.Light.shadowStrength != s) l.Light.shadowStrength = s;
                if (s <= 0f) dropped++;
            }
            DroppedCount = dropped;
        }

        bool IsViewer(Camera cam)
        {
            if (_viewer != null) return cam == _viewer;
            if (cam.cameraType != CameraType.Game || !cam.TryGetComponent<HouseViewer>(out _)) return false;
            _viewer = cam;
            return true;
        }

        /// <summary>Every lamp back to its own shadow strength (other cameras, switched off, rebuilt).</summary>
        void Restore()
        {
            foreach (var l in _lamps)
                if (l.Light != null && l.Light.shadowStrength != l.Original) l.Light.shadowStrength = l.Original;
            if (!Enabled)
                foreach (var l in _lamps) { l.Budget = 1f; l.Hold = HoldSeconds; }
            DroppedCount = 0;
        }

        // --------------------------------------------------------------- per frame
        void Evaluate(Camera cam, float dt)
        {
            var eye = cam.transform.position;
            GeometryUtility.CalculateFrustumPlanes(cam, _planes);
            _cameraRooms.Clear();
            bool outside = true;
            var e = new Vector2(eye.x, eye.z);
            for (int i = 0; i < _prisms.Count; i++)
            {
                var p = _prisms[i];
                if (eye.y < p.Y0 - RoomSnapY || eye.y > p.Y1 + RoomSnapY) continue;
                bool strict = eye.y >= p.Y0 && eye.y <= p.Y1 && Polygon.Contains(p.Outline, e);
                if (strict && !p.Terrace) outside = false;
                if (strict || DistanceToOutline(p.Outline, e) <= RoomSnap) _cameraRooms.Add(i);
            }
            CollectVisibleRooms();
            // inside the house but in no described room: the rules below cannot judge it, keep everything
            bool unmapped = GuardUnmappedInterior && _cameraRooms.Count == 0 && eye.y < _interiorTop && _footprint.Contains(e);

            foreach (var l in _lamps)
            {
                if (l.Light == null) continue;
                bool keep = unmapped || !l.Light.isActiveAndEnabled || NeedsShadow(l, eye, outside);
                if (keep) { l.Budget = 1f; l.Hold = HoldSeconds; }
                else if (l.Hold > 0f) l.Hold -= dt;
                else l.Budget = Mathf.Max(0f, l.Budget - RampPerSecond * dt);
            }
        }

        /// <summary>
        /// The camera's rooms plus, with <see cref="PortalRooms"/>, the rooms on the other side of an interior opening
        /// of a camera room that is in view (a closed door hides its room; the hold covers the closing swing).
        /// </summary>
        void CollectVisibleRooms()
        {
            _visibleRooms.Clear();
            _visibleRooms.AddRange(_cameraRooms);
            if (!PortalRooms || _cameraRooms.Count == 0) return;
            foreach (var p in _portals)
            {
                if (p.Door != null && !p.Door.IsOpen) continue;
                bool touches = false;
                foreach (int r in p.Rooms)
                    if (_cameraRooms.Contains(r)) { touches = true; break; }
                if (!touches || !GeometryUtility.TestPlanesAABB(_planes, p.Bounds)) continue;
                foreach (int r in p.Rooms)
                    if (!_visibleRooms.Contains(r)) _visibleRooms.Add(r);
            }
        }

        bool NeedsShadow(Lamp l, Vector3 eye, bool outside)
        {
            // (b) the lamp lights the room the camera stands in, or one seen from it through an interior opening
            foreach (int i in _visibleRooms)
                if (LitVolumeReaches(l, _prisms[i])) return true;

            // (a') seen from outside through an exterior opening next to the lamp
            if (outside)
                foreach (int i in l.Openings)
                {
                    var o = _openings[i];
                    var to = eye - o.Centre;
                    float d = to.magnitude;
                    if (d > 1e-3f && Vector3.Dot(o.Normal, to / d) > OpeningFacingMin && GeometryUtility.TestPlanesAABB(_planes, o.Bounds))
                        return true;
                }

            // (c) the lamp or its pool of light is in view and not hidden by construction
            if (!GeometryUtility.TestPlanesAABB(_planes, l.Reach)) return false;
            foreach (var s in l.Samples)
                if (InFrustum(s) && Unblocked(eye, s)) return true;
            return false;
        }

        bool InFrustum(Vector3 p)
        {
            for (int i = 0; i < _planes.Length; i++)
                if (_planes[i].GetDistanceToPoint(p) < -FrustumMargin) return false;
            return true;
        }

        bool Unblocked(Vector3 from, Vector3 to)
        {
            var dir = to - from;
            float dist = dir.magnitude;
            if (dist < 0.05f) return true;
            int n = Physics.RaycastNonAlloc(from, dir / dist, _hits, dist - 0.02f, _mask, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < n; i++)
                if (_blockers.Contains(_hits[i].collider)) return false;
            return true;
        }

        static bool LitVolumeReaches(Lamp l, Prism p)
        {
            if (!SphereTouchesPrism(l.Tight, p)) return false;
            if (l.Cover == null) return true;
            foreach (var s in l.Cover)
                if (SphereTouchesPrism(s, p)) return true;
            return false;
        }

        /// <summary>Exact sphere / vertical prism test: plan distance to the outline and height distance to [Y0, Y1].</summary>
        static bool SphereTouchesPrism(Vector4 s, Prism p)
        {
            float dy = s.y < p.Y0 ? p.Y0 - s.y : s.y > p.Y1 ? s.y - p.Y1 : 0f;
            float rh2 = s.w * s.w - dy * dy;
            if (rh2 < 0f) return false;
            var c = new Vector2(s.x, s.z);
            if (Polygon.Contains(p.Outline, c)) return true;
            return DistanceToOutline(p.Outline, c) <= Mathf.Sqrt(rh2);
        }

        static float DistanceToOutline(List<Vector2> poly, Vector2 p)
        {
            float best = float.MaxValue;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                Vector2 a = poly[j], ab = poly[i] - a;
                float len2 = ab.sqrMagnitude;
                float t = len2 > 1e-8f ? Mathf.Clamp01(Vector2.Dot(p - a, ab) / len2) : 0f;
                best = Mathf.Min(best, (a + ab * t - p).sqrMagnitude);
            }
            return Mathf.Sqrt(best);
        }

        // --------------------------------------------------------------- after a rebuild
        void Build()
        {
            _dirty = false;
            _ready = false;
            _lamps.Clear(); _openings.Clear(); _prisms.Clear(); _portals.Clear(); _blockers.Clear();
            _visibleRooms.Clear(); _cameraRooms.Clear();
            LampCount = 0; DroppedCount = 0;
            var result = _session?.Result;
            var doc = _session?.Doc;
            if (result == null || result.House == null || doc == null) return;
            _footprint = result.Footprint;
            _interiorTop = float.MinValue;
            foreach (var lv in doc.Levels)
                if (lv != null) _interiorTop = Mathf.Max(_interiorTop, lv.Elevation + lv.Height);

            Physics.SyncTransforms();
            int layer = LayerMask.NameToLayer("House");
            _mask = layer >= 0 ? 1 << layer : Physics.DefaultRaycastLayers;
            var surfaces = new HashSet<Collider>();          // what a lamp lights: anything solid of the house
            foreach (var col in result.House.GetComponentsInChildren<Collider>(true))
            {
                if (col.isTrigger) continue;
                string n = col.gameObject.name;
                if (IsBlocker(n)) _blockers.Add(col);
                if (n.IndexOf("Glass", StringComparison.Ordinal) < 0) surfaces.Add(col);
            }
            BuildRooms(doc);
            foreach (var p in _prisms)
                if (!p.Terrace) _interiorTop = Mathf.Max(_interiorTop, p.Y1);
            BuildOpenings(doc);
            BuildPortals(doc, result.House);

            foreach (var light in result.House.GetComponentsInChildren<Light>(true))
            {
                if ((light.type != LightType.Point && light.type != LightType.Spot) || light.shadows == LightShadows.None) continue;
                if (light.shadowStrength <= 0f) continue;
                var lamp = new Lamp { Light = light, Original = light.shadowStrength };
                LitVolume(lamp);
                float eff = EffectiveRadius(light);
                var pos = light.transform.position;
                for (int i = 0; i < _openings.Count; i++)
                    if (_openings[i].Bounds.SqrDistance(pos) <= eff * eff) lamp.Openings.Add(i);
                Pool(lamp, eff, surfaces);
                _lamps.Add(lamp);
            }
            LampCount = _lamps.Count;
            _ready = true;
        }

        /// <summary>Opaque construction that hides a lamp: walls, partitions (not their glass), slabs / ceilings / floors, roofs.</summary>
        static bool IsBlocker(string n) =>
            n.StartsWith("Wall_", StringComparison.Ordinal) || n.StartsWith("Interior_", StringComparison.Ordinal) ||
            n.StartsWith("Roof_", StringComparison.Ordinal) ||
            (n.StartsWith("Partition_", StringComparison.Ordinal) && !n.StartsWith("Partition_Glass_", StringComparison.Ordinal));

        /// <summary>The lit volume: the range sphere; a spot's cone sector gets its bounding sphere plus covering spheres.</summary>
        static void LitVolume(Lamp lamp)
        {
            var l = lamp.Light;
            var pos = l.transform.position;
            float r = Mathf.Max(0.01f, l.range * RoomReachScale);
            lamp.Tight = new Vector4(pos.x, pos.y, pos.z, r);
            if (l.type == LightType.Spot)
            {
                float half = Mathf.Clamp(l.spotAngle * 0.5f, 0.5f, 90f) * Mathf.Deg2Rad;
                var f = l.transform.forward;
                if (half < 89.5f * Mathf.Deg2Rad)
                {
                    // smallest sphere around the sector {|x| ≤ r, angle ≤ half}: through apex and rim up to 45°, around the rim beyond
                    Vector3 c; float rad;
                    if (half <= 45f * Mathf.Deg2Rad) { rad = r / (2f * Mathf.Cos(half)); c = pos + f * rad; }
                    else { rad = r * Mathf.Sin(half); c = pos + f * (r * Mathf.Cos(half)); }
                    lamp.Tight = new Vector4(c.x, c.y, c.z, rad);
                }
                if (half <= 45f * Mathf.Deg2Rad)
                {
                    // the cone (axial reach ≤ r) cut into segments, each inside a sphere: a much tighter room test
                    lamp.Cover = new Vector4[SpotCoverSpheres];
                    float tan = Mathf.Tan(half), step = r / SpotCoverSpheres;
                    for (int i = 0; i < SpotCoverSpheres; i++)
                    {
                        float t1 = step * (i + 1);
                        var c = pos + f * (t1 - step * 0.5f);
                        lamp.Cover[i] = new Vector4(c.x, c.y, c.z, Mathf.Sqrt(step * step * 0.25f + t1 * tan * t1 * tan));
                    }
                }
            }
            var t = lamp.Tight;
            lamp.Reach = new Bounds(new Vector3(t.x, t.y, t.z), Vector3.one * (2f * t.w));
        }

        /// <summary>Distance at which the lamp's light (URP falloff: I/d² · smooth range window) drops below <see cref="EffectiveIlluminance"/>.</summary>
        static float EffectiveRadius(Light l)
        {
            var c = l.color.linear;
            float i = l.intensity * Mathf.Max(c.r, Mathf.Max(c.g, c.b));
            float r = Mathf.Max(0.01f, l.range);
            float lo = Mathf.Min(0.05f, r), hi = r;
            if (Illuminance(i, r, lo) < EffectiveIlluminance) return lo;
            for (int k = 0; k < 24; k++)
            {
                float m = (lo + hi) * 0.5f;
                if (Illuminance(i, r, m) >= EffectiveIlluminance) lo = m; else hi = m;
            }
            return lo;
        }

        static float Illuminance(float intensity, float range, float d)
        {
            float q = d * d / (range * range);
            float s = Mathf.Clamp01(1f - q * q);
            return intensity / Mathf.Max(d * d, 1e-4f) * s * s;
        }

        /// <summary>
        /// Rule (c) samples: the lamp itself, the centre of its pool (first surface along the spot axis, or below a
        /// point lamp) and a ring around it, each moved onto the surface the lamp really lights in that direction.
        /// </summary>
        void Pool(Lamp lamp, float eff, HashSet<Collider> surfaces)
        {
            var l = lamp.Light;
            var pos = l.transform.position;
            lamp.Samples.Add(pos);
            var axis = l.type == LightType.Spot ? l.transform.forward : Vector3.down;
            Vector3 centre, n;
            float h;
            if (CastSurface(pos, axis, l.range, surfaces, out var hit))
            {
                centre = hit.point + hit.normal * SurfaceOffset; n = hit.normal; h = hit.distance;
            }
            else
            {
                h = Mathf.Min(l.range, 3f); centre = pos + axis * h; n = -axis;
            }
            lamp.Samples.Add(centre);

            float rho = l.type == LightType.Spot ? h * Mathf.Tan(Mathf.Min(l.spotAngle * 0.5f, 80f) * Mathf.Deg2Rad) : float.MaxValue;
            rho = eff > h ? Mathf.Min(rho, Mathf.Sqrt(eff * eff - h * h)) : PoolMinRadius;
            rho = Mathf.Clamp(rho, PoolMinRadius, PoolMaxRadius);
            var u = Vector3.Cross(n, Mathf.Abs(n.y) < 0.9f ? Vector3.up : Vector3.forward).normalized;
            var v = Vector3.Cross(n, u);
            for (int k = 0; k < PoolRing; k++)
            {
                float a = k * (2f * Mathf.PI / PoolRing);
                var q = centre + (u * Mathf.Cos(a) + v * Mathf.Sin(a)) * rho;
                var dir = q - pos;
                float dist = dir.magnitude;
                if (dist < 1e-3f) continue;
                lamp.Samples.Add(CastSurface(pos, dir / dist, l.range, surfaces, out var h2) ? h2.point + h2.normal * SurfaceOffset : q);
            }
        }

        bool CastSurface(Vector3 from, Vector3 dir, float maxDist, HashSet<Collider> surfaces, out RaycastHit best)
        {
            best = default;
            float bestD = float.MaxValue;
            int n = Physics.RaycastNonAlloc(from, dir, _hits, maxDist, _mask, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < n; i++)
                if (_hits[i].distance < bestD && surfaces.Contains(_hits[i].collider)) { best = _hits[i]; bestD = best.distance; }
            return bestD < float.MaxValue;
        }

        void BuildRooms(HouseDocument doc)
        {
            var levels = SortedLevels(doc);
            foreach (var r in doc.Rooms)
            {
                if (r == null || r.Outline == null || r.Outline.Count < 3) continue;
                var level = FindLevel(levels, r.Level);
                if (level == null) continue;
                _prisms.Add(new Prism
                {
                    Outline = new List<Vector2>(r.Outline), Y0 = level.Elevation, Y1 = level.Elevation + (r.Height ?? level.Height),
                    Terrace = r.Type == RoomType.Terrace,
                });
            }
        }

        /// <summary>
        /// Openings of exterior walls (a steel-glass wall counts as one opening) as the generator places them:
        /// the wall line per its alignment, heights above the level floor, outward normal checked against the rooms.
        /// </summary>
        void BuildOpenings(HouseDocument doc)
        {
            var levels = SortedLevels(doc);
            foreach (var w in doc.Walls)
            {
                if (w == null || w.Kind != WallKind.Exterior) continue;
                var level = FindLevel(levels, w.Level);
                if (level == null) continue;
                Vector2 d = w.B - w.A;
                float len = d.magnitude;
                if (len < 1e-4f) continue;
                d /= len;
                float t = w.Thickness ?? 0.4f;
                var align = w.Align ?? WallAlign.Outer;
                var right = new Vector2(d.y, -d.x);                   // outside of a counter-clockwise outline
                float off = align == WallAlign.Outer ? 0f : align == WallAlign.Center ? t * 0.5f : t;
                var mid = w.A + right * (off - t * 0.5f);             // centre line of the wall body

                if (w.System == WallSystem.SteelGlass)
                {
                    int li = levels.IndexOf(level);
                    var above = li >= 0 && li + 1 < levels.Count ? levels[li + 1] : null;
                    float y0 = w.Bottom ?? (li == 0 ? 0f : level.Elevation - level.Slab);
                    float y1 = w.Top ?? (above != null ? above.Elevation - above.Slab : level.Elevation + level.Height + 0.3f);
                    AddOpening(mid, d, right, t, 0f, len, y0, y1);
                }
                if (string.IsNullOrEmpty(w.Id)) continue;
                foreach (var o in doc.Openings)
                {
                    if (o == null || o.Wall != w.Id) continue;
                    float s0 = Mathf.Clamp(o.At, 0f, len), s1 = Mathf.Clamp(o.At + o.Width, 0f, len);
                    if (s1 - s0 < 0.01f) continue;
                    float y0 = level.Elevation + o.Sill;
                    AddOpening(mid, d, right, t, s0, s1, y0, y0 + o.Height);
                }
            }
        }

        void AddOpening(Vector2 mid, Vector2 d, Vector2 right, float t, float s0, float s1, float y0, float y1)
        {
            Vector2 a = mid + d * s0, b = mid + d * s1, half = right * (t * 0.5f + 0.02f);
            var mn = Vector2.Min(Vector2.Min(a - half, a + half), Vector2.Min(b - half, b + half));
            var mx = Vector2.Max(Vector2.Max(a - half, a + half), Vector2.Max(b - half, b + half));
            var bounds = new Bounds();
            bounds.SetMinMax(new Vector3(mn.x, Mathf.Min(y0, y1), mn.y), new Vector3(mx.x, Mathf.Max(y0, y1), mx.y));
            var c2 = (a + b) * 0.5f;
            float yc = (y0 + y1) * 0.5f;
            // the outward side is the one without a room behind it (walls listed clockwise have `right` inside)
            var probe = c2 + right * (t * 0.5f + 0.3f);
            bool flip = false;
            foreach (var p in _prisms)
                if (!p.Terrace && yc >= p.Y0 && yc <= p.Y1 && Polygon.Contains(p.Outline, probe)) { flip = true; break; }
            var n = flip ? -right : right;
            _openings.Add(new Opening { Bounds = bounds, Centre = new Vector3(c2.x, yc, c2.y), Normal = new Vector3(n.x, 0f, n.y) });
        }

        /// <summary>
        /// Openings of interior walls (a steel-glass screen counts as one) with the rooms on their sides, placed as the
        /// generator places them (WallFrame / WallBuilder.OpeningsOf); doors keep their leaf (pivot "Door_" + id).
        /// </summary>
        void BuildPortals(HouseDocument doc, GameObject house)
        {
            var doors = new Dictionary<string, Door>();
            foreach (var dr in house.GetComponentsInChildren<Door>(true))
                if (!doors.ContainsKey(dr.gameObject.name)) doors.Add(dr.gameObject.name, dr);
            var levels = SortedLevels(doc);
            foreach (var w in doc.Walls)
            {
                if (w == null || w.Kind != WallKind.Interior) continue;
                var level = FindLevel(levels, w.Level);
                if (level == null) continue;
                Vector2 d = w.B - w.A;
                float len = d.magnitude;
                if (len < 1e-4f) continue;
                d /= len;
                float t = w.Thickness ?? 0.12f;
                var align = w.Align ?? WallAlign.Center;
                var right = new Vector2(d.y, -d.x);
                float off = align == WallAlign.Outer ? 0f : align == WallAlign.Center ? t * 0.5f : t;
                var mid = w.A + right * (off - t * 0.5f);             // centre line of the wall body
                float wy0 = w.Bottom ?? level.Elevation, wy1 = w.Top ?? level.Elevation + level.Height;

                if (w.System == WallSystem.SteelGlass) AddPortal(mid, d, right, t, 0f, len, wy0, wy1, null);
                if (string.IsNullOrEmpty(w.Id)) continue;
                foreach (var o in doc.Openings)
                {
                    if (o == null || o.Wall != w.Id) continue;
                    float s0 = Mathf.Clamp(o.At, 0f, len), s1 = Mathf.Clamp(o.At + o.Width, 0f, len);
                    if (s1 - s0 < 0.01f) continue;
                    bool door = o.Type == OpeningType.Door || o.Type == OpeningType.EntryDoor || o.Type == OpeningType.SolidDoor;
                    float y0 = level.Elevation + (door ? Mathf.Max(0f, o.Sill) : o.Sill);
                    Door leaf = null;
                    if (door) doors.TryGetValue("Door_" + (o.Id ?? w.Id), out leaf);
                    AddPortal(mid, d, right, t, s0, s1, y0, y0 + o.Height, leaf);
                }
            }
        }

        void AddPortal(Vector2 mid, Vector2 d, Vector2 right, float t, float s0, float s1, float y0, float y1, Door leaf)
        {
            Vector2 a = mid + d * s0, b = mid + d * s1, half = right * (t * 0.5f + 0.02f);
            var mn = Vector2.Min(Vector2.Min(a - half, a + half), Vector2.Min(b - half, b + half));
            var mx = Vector2.Max(Vector2.Max(a - half, a + half), Vector2.Max(b - half, b + half));
            float lo = Mathf.Min(y0, y1), hi = Mathf.Max(y0, y1);
            var bounds = new Bounds();
            bounds.SetMinMax(new Vector3(mn.x, lo, mn.y), new Vector3(mx.x, hi, mx.y));
            var c2 = (a + b) * 0.5f;
            float reach = t * 0.5f + PortalSnap;
            var rooms = new List<int>();
            for (int i = 0; i < _prisms.Count; i++)
            {
                var p = _prisms[i];
                if (hi < p.Y0 || lo > p.Y1) continue;
                if (Polygon.Contains(p.Outline, c2) || DistanceToOutline(p.Outline, c2) <= reach) rooms.Add(i);
            }
            if (rooms.Count < 2) return;   // an opening into no described room cannot extend the view
            _portals.Add(new Portal { Bounds = bounds, Rooms = rooms.ToArray(), Door = leaf });
        }

        static List<LevelDef> SortedLevels(HouseDocument doc)
        {
            var list = new List<LevelDef>();
            foreach (var l in doc.Levels) if (l != null) list.Add(l);
            list.Sort((a, b) => a.Elevation.CompareTo(b.Elevation));
            return list;
        }

        /// <summary>As the generator resolves levels: by id, else the lowest.</summary>
        static LevelDef FindLevel(List<LevelDef> levels, string id)
        {
            if (id != null)
                foreach (var l in levels)
                    if (l.Id == id) return l;
            return levels.Count > 0 ? levels[0] : null;
        }
    }
}
