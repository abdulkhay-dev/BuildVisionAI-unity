using System;
using UnityEngine;

namespace House4696.Lighting
{
    /// <summary>
    /// Baked indirect lighting on a regular probe grid: L2 spherical harmonics in Unity's shader packing
    /// (SHAr/g/b, SHBr/g/b, SHC — the same layout as unity_SHAr… for light probes) stored as 3D textures, plus
    /// probe validity (1 = in open space, 0 = inside geometry). <see cref="Active"/> is what the viewer shows.
    /// </summary>
    public sealed class BakedGIVolume : IDisposable
    {
        public const int ShTextureCount = 7;

        /// <summary>The volume the renderer feature resolves on screen; null = no baked lighting.</summary>
        public static BakedGIVolume Active { get; set; }

        public readonly Vector3 Origin;       // world position of probe (0,0,0)
        public readonly float Spacing;
        public readonly Vector3Int Size;      // probe counts per axis
        public readonly Texture3D[] Sh = new Texture3D[ShTextureCount];
        public readonly Texture3D Validity;
        public readonly float BakeSeconds;
        /// <summary>Human-readable bake breakdown (world size, timings) for diagnostics.</summary>
        public string Stats = "";
        /// <summary>Raw back-face hit ratio per probe (diagnostics).</summary>
        public float[] BackfaceRatio;

        public int ProbeCount => Size.x * Size.y * Size.z;
        public Bounds Bounds => new Bounds(Origin + (Vector3)(Size - Vector3Int.one) * (Spacing * 0.5f), (Vector3)(Size - Vector3Int.one) * Spacing);

        /// <param name="packed">7 float4 per probe, probe index = x + y·Size.x + z·Size.x·Size.y.</param>
        public BakedGIVolume(Vector3 origin, float spacing, Vector3Int size, Vector4[] packed, float[] validity, float bakeSeconds)
        {
            Origin = origin;
            Spacing = spacing;
            Size = size;
            BakeSeconds = bakeSeconds;
            int n = ProbeCount;
            if (packed.Length != n * ShTextureCount || validity.Length != n) throw new ArgumentException("probe data size mismatch");

            var slice = new Color[n];
            for (int t = 0; t < ShTextureCount; t++)
            {
                for (int i = 0; i < n; i++)
                {
                    var v = packed[i * ShTextureCount + t];
                    slice[i] = new Color(v.x, v.y, v.z, v.w);
                }
                Sh[t] = Create(TextureFormat.RGBAHalf, "BakedGI_SH" + t);
                Sh[t].SetPixels(slice);
                Sh[t].Apply(false, true);
            }
            var val = new Color[n];
            for (int i = 0; i < n; i++) val[i] = new Color(validity[i], 0, 0, 0);
            Validity = Create(TextureFormat.RHalf, "BakedGI_Validity");
            Validity.SetPixels(val);
            Validity.Apply(false, true);
        }

        Texture3D Create(TextureFormat format, string name) => new Texture3D(Size.x, Size.y, Size.z, format, false)
        {
            name = name, wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Point, hideFlags = HideFlags.HideAndDontSave,
        };

        public void Dispose()
        {
            if (Active == this) Active = null;
            foreach (var t in Sh) Release(t);
            Release(Validity);
        }

        internal static void Release(UnityEngine.Object o)
        {
            if (o == null) return;
            if (Application.isPlaying) UnityEngine.Object.Destroy(o); else UnityEngine.Object.DestroyImmediate(o);
        }
    }
}
