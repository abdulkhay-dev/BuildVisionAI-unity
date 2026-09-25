using House4696.Core;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using static House4696.House.HouseSpec;
using static House4696.House.Interior.InteriorPlan;

namespace House4696.House.Interior
{
    /// <summary>
    /// Warm (≈2700 K) lighting scheme: recessed downlights, grazing spots on the fluted media wall, lamps and
    /// pendants as real light sources, plus one box-projected reflection probe per room so floors, marble and
    /// mirrors reflect the room instead of the garden. Lights are Mixed: direct light stays realtime, their
    /// bounce is baked into the adaptive probe volume together with the sun and sky.
    /// </summary>
    public sealed class InteriorLighting
    {
        static readonly Color Warm = new Color(1f, 0.86f, 0.71f);
        static readonly Color Neutral = new Color(1f, 0.93f, 0.85f);

        readonly InteriorMaterials _m;
        readonly FurnitureKit _k;
        readonly SceneWriter _w;
        Transform _lights;

        public InteriorLighting(InteriorMaterials m, FurnitureKit k, SceneWriter w) { _m = m; _k = k; _w = w; }

        public void Build(Transform root)
        {
            _lights = _w.Group("Interior_Lights", root);
            Downlights(root);
            const float G = FloorY, U = UpperFloorY;

            // ---- living room
            Point("Chandelier", new Vector3(7.06f, 4.4f, 2.2f), Warm, 1.3f, 9f, true);
            Spot("MediaWall_Graze_A", new Vector3(8.95f, UpperCeil - 0.05f, 1.2f), new Vector3(9.33f, G, 1.2f), 34f, 9f, 9f, Neutral, true);
            Spot("MediaWall_Graze_B", new Vector3(8.95f, UpperCeil - 0.05f, 3.2f), new Vector3(9.33f, G, 3.2f), 34f, 9f, 9f, Neutral, true);
            Point("Fireplace", new Vector3(8.6f, G + 0.45f, 2.2f), new Color(1f, 0.55f, 0.25f), 0.9f, 2.6f, false);
            Point("Floor_Lamp_Living", new Vector3(8.72f, G + 1.35f, 0.36f), Warm, 0.8f, 3f, false);
            Point("Sofa_Lamp", new Vector3(5.04f, G + 1.15f, 1.55f), Warm, 0.6f, 2.5f, false);
            Point("Gallery_Cove", new Vector3(7.06f, BandBottom - 0.25f, VoidZ + 0.3f), Warm, 1.0f, 4f, false);

            // ---- kitchen & dining
            Point("Island_Pendants", new Vector3(2.75f, G + 1.9f, 7.8f), Warm, 1.6f, 4f, true);
            Point("Dining_Pendant", new Vector3(2.6f, G + 1.6f, 4.85f), Warm, 1.6f, 4f, true);
            Spot("Counter_Downlight", new Vector3(2.7f, GroundCeil - 0.02f, 9.35f), new Vector3(2.7f, G, 9.6f), 80f, 3.5f, 4f, Neutral, false);

            // ---- hall, guest, bath, stair
            Point("Hall_Pendant", new Vector3(10.72f, G + 2.1f, 4.2f), Warm, 1.4f, 5f, false);
            Point("Guest_Pendants", new Vector3(13.1f, G + 1.5f, 8.4f), Warm, 0.8f, 3.5f, false);
            Point("Bath_Mirror", new Vector3(12.45f, G + 1.6f, 4.45f), Neutral, 0.9f, 3f, false);
            Point("Stair_Landing", new Vector3(8.2f, LandingY + 1.3f, 10.0f), Warm, 1.2f, 5f, false);

            // ---- upper floor
            Point("Gallery_Reading", new Vector3(5.55f, U + 1.35f, 4.75f), Warm, 0.8f, 3f, false);
            Spot("Upper_Hall_Down", new Vector3(7.5f, UpperCeil - 0.02f, 6.2f), new Vector3(7.5f, U, 6.2f), 90f, 3f, 4f, Neutral, false);
            Point("Master_Bedside", new Vector3(3.5f, U + 1.2f, 4.7f), Warm, 0.9f, 3.5f, false);
            Point("Master_Reading", new Vector3(0.66f, U + 1.35f, 3.2f), Warm, 0.6f, 2.5f, false);
            Point("Ensuite", new Vector3(3.6f, U + 2.2f, 8.4f), Neutral, 1.0f, 3.5f, false);
            Point("FamilyBath", new Vector3(5.85f, U + 1.9f, 9.6f), Warm, 1.2f, 4f, false);
            Point("BackBedroom_Lamps", new Vector3(12.0f, U + 1.2f, 7.0f), Warm, 0.9f, 3.5f, false);
            Point("FrontBedroom_Lamps", new Vector3(12.0f, U + 1.2f, 4.9f), Warm, 0.9f, 3.5f, false);
            Point("FrontBedroom_Desk", new Vector3(13.9f, U + 1.2f, 2.3f), Warm, 0.5f, 2f, false);

            Probes(root);
        }

        // ------------------------------------------------------------------ recessed downlights (geometry only)
        void Downlights(Transform root)
        {
            var mb = new MeshBuilder();
            void Row(float y, float z, params float[] xs) { foreach (var x in xs) _k.Downlight(mb, new Vector3(x, y, z)); }
            void Col(float y, float x, params float[] zs) { foreach (var z in zs) _k.Downlight(mb, new Vector3(x, y, z)); }
            float g = GroundCeil, u = UpperCeil;
            Row(g, 9.35f, 1.4f, 2.4f, 3.4f);               // kitchen counter
            Row(g, 6.4f, 1.4f, 3.9f);
            Col(g, 0.9f, 3.6f, 5.2f);                     // sideboard wash
            Row(g, 5.6f, 5.6f, 6.6f);                     // under the gallery
            Row(g, 6.4f, 7.7f, 8.8f);
            Col(g, 10.72f, 2.6f, 5.9f);                   // hall
            Row(g, 7.6f, 10.6f, 12.2f); Row(g, 9.3f, 10.6f, 12.2f); // guest
            Row(g, 5.4f, 12.4f, 13.6f);                   // bath
            Row(g, 3.0f, 12.6f, 13.6f);                   // wardrobe
            Row(u, 4.0f, 1.4f, 2.8f); Row(u, 6.4f, 1.4f, 2.8f);     // master
            Row(u, 8.6f, 1.4f); Row(u, 8.6f, 3.5f); Row(u, 9.4f, 3.5f); // wardrobe / ensuite
            Row(u, 8.4f, 5.4f, 6.4f);                     // family bath
            Row(u, 5.3f, 5.6f, 8.6f); Row(u, 6.6f, 5.6f, 8.6f);     // gallery hall
            Row(u, 7.9f, 11.0f, 13.0f); Row(u, 9.3f, 11.0f, 13.0f); // back bedroom
            Row(u, 2.6f, 11.0f, 13.0f); Row(u, 4.0f, 11.0f, 13.0f); // front bedroom
            // recessed linear LED profiles along the wardrobe / media walls
            void Slot(float y, float xa, float za, float xb, float zb) => _k.LedSlot(mb, new Vector3(xa, y, za), new Vector3(xb, y, zb));
            Slot(u, 0.95f, 3.1f, 0.95f, 7.0f);          // master, over the media wall
            Slot(u, 10.55f, 6.25f, 10.55f, 9.75f);       // back bedroom, along the wardrobe
            Slot(u, 10.55f, 2.1f, 10.55f, 5.65f);        // front bedroom
            Slot(u, 5.0f, 6.95f, 9.1f, 6.95f);           // gallery hall
            Slot(g, 10.3f, 2.1f, 10.3f, 6.4f);           // entrance hall
            _w.Emit("Decor_Downlights", root, mb, castShadows: false);
        }

        // ------------------------------------------------------------------ lights
        Light Make(string name, Vector3 pos, LightType type, Color c, float intensity, float range, bool shadows)
        {
            var go = new GameObject("Light_" + name);
            go.transform.SetParent(_lights, false);
            go.transform.position = pos;
            var l = go.AddComponent<Light>();
            l.type = type;
            l.color = c;
            l.intensity = intensity;
            l.range = range;
            l.shadows = shadows ? LightShadows.Soft : LightShadows.None;
            l.shadowBias = 0.02f;
            l.shadowNormalBias = 0.3f;
            l.shadowNearPlane = 0.1f;
#if UNITY_EDITOR
            l.lightmapBakeType = LightmapBakeType.Mixed; // editor bake only; a player build lights everything in realtime
#endif
            l.bounceIntensity = 1f;
            var data = go.AddComponent<UniversalAdditionalLightData>();
            data.usePipelineSettings = true;
            return l;
        }

        void Point(string name, Vector3 pos, Color c, float intensity, float range, bool shadows) =>
            Make(name, pos, LightType.Point, c, intensity, range, shadows);

        void Spot(string name, Vector3 pos, Vector3 target, float angle, float intensity, float range, Color c, bool shadows)
        {
            var l = Make(name, pos, LightType.Spot, c, intensity, range, shadows);
            l.transform.rotation = Quaternion.LookRotation(target - pos, Vector3.forward);
            l.spotAngle = angle;
            l.innerSpotAngle = angle * 0.45f;
        }

        // ------------------------------------------------------------------ per-room reflection probes
        void Probes(Transform root)
        {
            var group = new GameObject("Interior_ReflectionProbes").transform;
            group.SetParent(root, false);
            void Probe(string name, float x0, float x1, float y0, float y1, float z0, float z1, float captureY)
            {
                var go = new GameObject("Probe_" + name);
                go.transform.SetParent(group, false);
                var center = new Vector3((x0 + x1) * 0.5f, (y0 + y1) * 0.5f, (z0 + z1) * 0.5f);
                go.transform.position = new Vector3(center.x, captureY, center.z);
                var p = go.AddComponent<ReflectionProbe>();
                p.mode = ReflectionProbeMode.Baked;
                p.boxProjection = true;
                // the box reaches just past the wall faces (mirrors and panels get full weight) but stops short
                // of the window panes, which sit ≥ 0.15 m inside the walls and must keep the garden reflection
                const float margin = 0.1f;
                p.size = new Vector3(x1 - x0, y1 - y0, z1 - z0) + Vector3.one * (margin * 2f);
                p.center = center - go.transform.position;
                p.blendDistance = 0.08f;
                p.importance = 2;
                p.resolution = 256;
                p.hdr = true;
                p.nearClipPlane = 0.05f;
                p.farClipPlane = 60f;
            }
            const float G = FloorY, U = UpperFloorY;
            Probe("Living", FinLeftX1, FinRightX0, G, UpperCeil, 0.33f, 7.0f, G + 1.6f);
            Probe("Kitchen", L0, FinLeftX1, G, GroundCeil, LeftIn, BackIn, G + 1.5f);
            Probe("Stair", StairX0, FinRightX0, G, UpperCeil, 7.0f, BayIn, G + 2.6f);
            Probe("Hall", FinRightX1, 11.73f, G, GroundCeil, RightIn, 6.68f, G + 1.5f);
            Probe("Guest", FinRightX1, R0, G, GroundCeil, 6.8f, BackIn, G + 1.5f);
            Probe("Bath", 11.83f, R0, G, GroundCeil, 4.19f, 6.68f, G + 1.5f);
            Probe("Master", L0, FinLeftX0, U, UpperCeil, LeftIn, 7.23f, U + 1.5f);
            Probe("Ensuite", 2.54f, FinLeftX0, U, UpperCeil, 7.35f, BackIn, U + 1.5f);
            Probe("FamilyBath", FinLeftX1, 6.9f, U, UpperCeil, 7.47f, BayIn, U + 1.5f);
            Probe("UpperHall", FinLeftX1, FinRightX0, U, UpperCeil, VoidZ, 7.35f, U + 1.5f);
            Probe("BackBedroom", FinRightX1, R0, U, UpperCeil, 5.99f, BackIn, U + 1.5f);
            Probe("FrontBedroom", FinRightX1, R0, U, UpperCeil, RightIn, 5.87f, U + 1.5f);
        }
    }
}
