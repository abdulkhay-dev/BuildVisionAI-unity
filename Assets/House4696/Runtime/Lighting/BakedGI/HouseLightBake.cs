using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace House4696.Lighting
{
    /// <summary>
    /// The bake of a generated house: probes cover the house plus a margin (the garden beyond it keeps the ambient
    /// probe), the rays see the house and the site, every active scene light contributes its bounce.
    /// </summary>
    public static class HouseLightBake
    {
        /// <summary>Horizontal margin of the probe grid around the house, metres.</summary>
        public const float Margin = 3f;
        /// <summary>Garden objects farther than this from the probe grid do not take part in the bake, metres.</summary>
        public const float SiteReach = 8f;

        public static ProbeBakeSettings DefaultSettings(Bounds houseBounds)
        {
            var b = houseBounds;
            var min = new Vector3(b.min.x - Margin, b.min.y - 0.5f, b.min.z - Margin);
            var max = new Vector3(b.max.x + Margin, b.max.y + 1f, b.max.z + Margin);
            var bounds = new Bounds();
            bounds.SetMinMax(min, max);
            return new ProbeBakeSettings { Bounds = bounds };
        }

        public static Bounds HouseBounds(GameObject house)
        {
            var bounds = new Bounds();
            bool any = false;
            foreach (var r in house.GetComponentsInChildren<MeshRenderer>())
            {
                if (!r.enabled) continue;
                if (any) bounds.Encapsulate(r.bounds); else { bounds = r.bounds; any = true; }
            }
            if (!any) bounds = new Bounds(house.transform.position, Vector3.one * 10f);
            return bounds;
        }

        /// <param name="settings">null = <see cref="DefaultSettings"/> around the house.</param>
        public static IEnumerator Bake(ProbeBakeResources resources, GameObject house, GameObject site, ProbeBakeSettings settings,
            Action<BakedGIVolume> done, Action<string> failed, Func<bool> cancelled = null, Action<float> progress = null)
        {
            var s = settings ?? DefaultSettings(HouseBounds(house));
            var renderers = new List<Renderer>();
            var lodCache = new Dictionary<LODGroup, HashSet<Renderer>>();
            foreach (var r in house.GetComponentsInChildren<MeshRenderer>())
                if (!IsCoarseLod(r, lodCache)) renderers.Add(r);
            // the garden only matters near the probes (ground bounce, hedges, nearby trees); distant forest is skipped
            if (site != null)
            {
                var near = s.Bounds;
                near.Expand(new Vector3(SiteReach, SiteReach, SiteReach) * 2f);
                foreach (var r in site.GetComponentsInChildren<MeshRenderer>())
                    if (near.Intersects(r.bounds) && !IsCoarseLod(r, lodCache)) renderers.Add(r);
            }
            var lights = new List<Light>(UnityEngine.Object.FindObjectsByType<Light>());
            return ProbeVolumeBaker.Bake(resources, s, renderers, lights, done, failed, cancelled, progress);
        }

        /// <summary>
        /// Coarse LOD levels (index &gt; 0 of a LODGroup: tree LOD1, lawn-chunk LOD1) stay out of the bake: the rays see the
        /// full-detail level only; tracing both would double crowns and blades in the GI and the bake cost. Renderers of a
        /// group that are in no LOD (tree shadow proxies) stay in. false = every renderer is traced.
        /// </summary>
        public static bool SkipCoarseLods = true;

        static bool IsCoarseLod(Renderer r, Dictionary<LODGroup, HashSet<Renderer>> cache)
        {
            if (!SkipCoarseLods) return false;
            var group = r.GetComponentInParent<LODGroup>();
            if (group == null) return false;
            if (!cache.TryGetValue(group, out var coarse))
            {
                coarse = new HashSet<Renderer>();
                var lods = group.GetLODs();
                var fine = lods.Length > 0 ? lods[0].renderers : null;
                for (int i = 1; i < lods.Length; i++)
                    foreach (var lr in lods[i].renderers)
                        if (lr != null && (fine == null || Array.IndexOf(fine, lr) < 0)) coarse.Add(lr);
                cache[group] = coarse;
            }
            return coarse.Contains(r);
        }
    }
}
