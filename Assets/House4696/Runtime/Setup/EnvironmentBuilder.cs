using House4696.Core;
using House4696.Runtime;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace House4696.Setup
{
    /// <summary>
    /// Camera calibrated against the reference render (2-point perspective with vertical lens shift):
    /// least-squares fit of 40 image measurements to the plan geometry, RMS error ≈ 3 px on 1600×1195.
    /// </summary>
    public static class CameraSpec
    {
        public static readonly Vector3 Position = new Vector3(-5.79f, 1.42f, -17.15f);
        public const float Yaw = 30.62f;
        public const float FocalLength = 38.68f;                       // mm on a 36 mm wide sensor (f = 1719 px)
        public static readonly Vector2 Sensor = new Vector2(36f, 26.8875f); // 1600:1195
        public static readonly Vector2 LensShift = new Vector2(0f, 0.1833f); // horizon 219 px below centre
        public const int RefWidth = 1600, RefHeight = 1195;
        public static Vector3 Forward => Quaternion.Euler(0, Yaw, 0) * Vector3.forward;
    }

    /// <summary>
    /// Scene environment shared by the editor rebuild and the player: sun, sky, ambient, fog, post-processing
    /// volume, garden reflection probe and the viewer camera. Pipeline configuration and baking stay in the
    /// editor (<c>EnvironmentSetup</c>).
    /// </summary>
    public static class EnvironmentBuilder
    {
        public static readonly Vector3 SunEuler = new Vector3(33f, -5f, 0f); // near-frontal sun: matches shadow lengths/sides in the reference

        /// <param name="sunEuler">Sun rotation (elevation, yaw); null keeps the calibrated 46-96 sun.</param>
        public static GameObject Build(MaterialLibrary m, VolumeProfile postProfile, Vector3? sunEuler = null)
        {
            var root = new GameObject("Environment");

            // --- sun
            var sunGo = new GameObject("Sun");
            sunGo.transform.SetParent(root.transform, false);
            sunGo.transform.rotation = Quaternion.Euler(sunEuler ?? SunEuler);
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.96f, 0.91f);
            sun.intensity = 3.1f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 1f;
            var lightData = sunGo.AddComponent<UniversalAdditionalLightData>();
            lightData.usePipelineSettings = false;
            lightData.renderingLayers = uint.MaxValue;   // the sun lights every rendering layer (the garden sits on its own)
            sun.shadowBias = 0.25f;
            sun.shadowNormalBias = 0.35f;

            // --- sky, ambient, fog
            RenderSettings.skybox = m.Sky;
            RenderSettings.sun = sun;
            // trilight ambient: bright sky, neutral horizon, almost no bounce from below (the reference
            // render has near-black soffits and well lit shaded walls)
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.63f, 0.63f, 0.64f);
            RenderSettings.ambientEquatorColor = new Color(0.45f, 0.44f, 0.42f);
            RenderSettings.ambientGroundColor = new Color(0.05f, 0.05f, 0.045f);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            RenderSettings.reflectionIntensity = 1f;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.72f, 0.79f, 0.86f);
            RenderSettings.fogStartDistance = 60f;
            RenderSettings.fogEndDistance = 520f;

            // --- post processing
            var volGo = new GameObject("PostProcess_Volume");
            volGo.transform.SetParent(root.transform, false);
            var vol = volGo.AddComponent<Volume>();
            vol.isGlobal = true;
            vol.sharedProfile = postProfile;

            // --- reflection probe in front of the facade (captures sky, trees, lawn; the house is excluded)
            var probeGo = new GameObject("ReflectionProbe_Garden");
            probeGo.transform.SetParent(root.transform, false);
            probeGo.transform.position = new Vector3(7.3f, 3.2f, -9f);
            var probe = probeGo.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Baked;
            probe.size = new Vector3(90f, 30f, 50f);
            probe.boxProjection = false;
            probe.resolution = 1024;
            probe.hdr = true;
            probe.importance = 1;
            probe.intensity = 1f;
            probe.nearClipPlane = 0.3f;
            probe.farClipPlane = 800f;

            // --- camera
            var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
            camGo.transform.SetParent(null);
            var cam = camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            ApplyCamera(cam);
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
            data.dithering = true;
            data.renderShadows = true;
            camGo.AddComponent<HouseViewer>(); // tours come from the house document (the caller configures it)
            return root;
        }

        /// <summary>Sun rotation for a site: azimuth = compass direction the sun shines from (0 = north/+Z, clockwise).</summary>
        public static Vector3 SunFrom(float azimuth, float elevation) => new Vector3(elevation, azimuth - 180f, 0f);

        public static void ApplyCamera(Camera cam)
        {
            cam.transform.position = CameraSpec.Position;
            cam.transform.rotation = Quaternion.Euler(0f, CameraSpec.Yaw, 0f);
            cam.usePhysicalProperties = true;
            cam.sensorSize = CameraSpec.Sensor;
            cam.focalLength = CameraSpec.FocalLength;
            cam.lensShift = CameraSpec.LensShift;
            cam.gateFit = Camera.GateFitMode.Horizontal;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 1500f;
            cam.allowHDR = true;
            cam.allowMSAA = true;
            cam.clearFlags = CameraClearFlags.Skybox;
        }

    }
}
