using System;
using System.Collections;
using House4696.Core;
using House4696.Lighting;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace House4696.App
{
    /// <summary>
    /// Lighting of the open house: after every rebuild the indirect light is baked on the GPU (a few seconds) and
    /// then shown like the editor's baked lighting — clean and free per frame. A newer rebuild cancels a running bake;
    /// the previous (slightly stale) lighting stays visible until the new one is ready. If the bake cannot run
    /// (missing resources, GPU error), Surface Cache realtime GI takes over.
    /// </summary>
    public sealed class HouseLighting
    {
        public enum State { Idle, Baking, Ready, Failed }

        readonly MonoBehaviour _host;
        readonly HouseSession _session;
        readonly HouseContent _content;
        int _generation;

        public State Current { get; private set; } = State.Idle;
        public float Progress { get; private set; }
        public string Error { get; private set; }
        public BakedGIVolume Volume => BakedGIVolume.Active;
        public bool IsBaking => Current == State.Baking;

        /// <summary>Raised on the main thread when a new bake is shown.</summary>
        public event Action Baked;

        public HouseLighting(MonoBehaviour host, HouseSession session, HouseContent content)
        {
            _host = host; _session = session; _content = content;
            // the bake replaces the realtime GI; it only comes back as the fallback
            SetSurfaceCache(!CanBake);
        }

        public bool CanBake => _content.BakedGI != null && _content.BakedGI.IsComplete && SystemInfo.supportsComputeShaders;

        /// <summary>Starts baking the current house; a bake already running is abandoned.</summary>
        public void Rebake()
        {
            int generation = ++_generation;
            if (!CanBake || _session.Result == null) return;
            Current = State.Baking;
            Progress = 0f;
            Error = null;
            _host.StartCoroutine(HouseLightBake.Bake(_content.BakedGI, _session.Result.House, _session.Result.Site, null,
                volume =>
                {
                    if (generation != _generation) { volume.Dispose(); return; }
                    var old = BakedGIVolume.Active;
                    BakedGIVolume.Active = volume;
                    old?.Dispose();
                    SetSurfaceCache(false);
                    Current = State.Ready;
                    Progress = 1f;
                    Debug.Log($"[Lighting] baked in {volume.BakeSeconds:0.0} s: {volume.Stats}");
                    Baked?.Invoke();
                },
                error =>
                {
                    if (generation != _generation) return;
                    Current = State.Failed;
                    Error = error;
                    Debug.LogError("[Lighting] bake failed, falling back to realtime GI: " + error);
                    BakedGIVolume.Active?.Dispose();
                    SetSurfaceCache(true);
                },
                () => generation != _generation,
                p => { if (generation == _generation) Progress = p; }));
        }

        /// <summary>Waits while a bake is running (renders for the AI must show the finished lighting).</summary>
        public IEnumerator WaitForBake(float timeoutSeconds)
        {
            float end = Time.realtimeSinceStartup + timeoutSeconds;
            while (IsBaking && Time.realtimeSinceStartup < end) yield return null;
        }

        /// <summary>One line for the viewer's status bar.</summary>
        public string StatusText()
        {
            switch (Current)
            {
                case State.Baking: return $"свет: расчёт {Progress:P0}";
                case State.Ready: return $"свет: {Volume?.BakeSeconds:0.0} с";
                case State.Failed: return "свет: realtime (ошибка расчёта)";
                default: return CanBake ? "свет: —" : "свет: realtime";
            }
        }

        public JObject ToJson() => new JObject
        {
            ["state"] = Current.ToString().ToLowerInvariant(),
            ["progress"] = Math.Round(Progress, 2),
            ["bakeSeconds"] = Volume != null ? Math.Round(Volume.BakeSeconds, 1) : (double?)null,
            ["probes"] = Volume?.ProbeCount,
            ["details"] = Volume?.Stats,
            ["error"] = Error,
        };

        void SetSurfaceCache(bool on)
        {
            if (_content.RealtimeGIProfile != null && _content.RealtimeGIProfile.TryGet(out SurfaceCacheGIVolumeOverride gi))
                gi.enabled.Override(on);
        }
    }
}
