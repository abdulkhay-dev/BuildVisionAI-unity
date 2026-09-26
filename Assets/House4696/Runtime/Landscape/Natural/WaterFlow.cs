using UnityEngine;

namespace House4696.Landscape.Natural
{
    /// <summary>
    /// Makes the stream flow: scrolls the ripples of the site's own water materials along the flow (the meshes' v
    /// runs downstream). The materials are per-site copies, destroyed with the site.
    /// </summary>
    public sealed class WaterFlow : MonoBehaviour
    {
        public Material Pools, Falls;
        public float PoolSpeed = 0.06f, FallSpeed = 0.9f;

        void Update()
        {
            float t = Time.time;
            if (Pools != null) Pools.mainTextureOffset = new Vector2(0f, -t * PoolSpeed);
            if (Falls != null) Falls.mainTextureOffset = new Vector2(0f, -t * FallSpeed);
        }

        void OnDestroy()
        {
            if (Pools != null) Destroy(Pools);
            if (Falls != null) Destroy(Falls);
        }
    }
}
