using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Profiling;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace House4696.App
{
    /// <summary>
    /// Memory diagnostics in the running app (API command <c>memory</c>): what is loaded, grouped by kind, with the
    /// biggest textures and meshes. Sizes are computed from formats and vertex layouts, so they work in release
    /// players too (Profiler.GetRuntimeMemorySizeLong only reports in development builds).
    /// </summary>
    public static class MemoryProbe
    {
        const long MB = 1 << 20;

        public static JObject Report(int top)
        {
            var groups = new Dictionary<string, (long bytes, int count)>();
            var items = new List<(long bytes, string name)>();
            void Add(string group, long bytes, string name)
            {
                groups.TryGetValue(group, out var g);
                groups[group] = (g.bytes + bytes, g.count + 1);
                items.Add((bytes, $"{group}: {name}"));
            }

            foreach (var t in Resources.FindObjectsOfTypeAll<Texture>())
            {
                long b = TextureBytes(t, out var kind);
                if (b > 0) Add(kind, b, $"{t.name} {t.width}x{t.height} {t.graphicsFormat}");
            }
            foreach (var m in Resources.FindObjectsOfTypeAll<Mesh>())
            {
                long b = MeshBytes(m);
                string g = m.isReadable ? "mesh (readable: CPU+GPU)" : "mesh";
                if (m.isReadable) b *= 2;
                Add(g, b, $"{m.name} v{m.vertexCount}");
            }

            // textures that no renderer, terrain or UI of the scene uses: what lazy loading of the library would save
            var used = new HashSet<Texture>();
            var mats = new HashSet<Material>();
            foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsInactive.Include)) foreach (var m in r.sharedMaterials) if (m != null) mats.Add(m);
            foreach (var t in Object.FindObjectsByType<Terrain>(FindObjectsInactive.Include))
            {
                if (t.materialTemplate != null) mats.Add(t.materialTemplate);
                if (t.terrainData == null) continue;
                foreach (var l in t.terrainData.terrainLayers) if (l != null) { used.Add(l.diffuseTexture); used.Add(l.normalMapTexture); used.Add(l.maskMapTexture); }
                foreach (var p in t.terrainData.detailPrototypes) if (p.prototypeTexture != null) used.Add(p.prototypeTexture);
                foreach (var a in t.terrainData.alphamapTextures) used.Add(a);
            }
            foreach (var m in mats)
                foreach (var id in m.GetTexturePropertyNameIDs()) { var tx = m.GetTexture(id); if (tx != null) used.Add(tx); }
            long unused = 0; int unusedCount = 0;
            foreach (var t in Resources.FindObjectsOfTypeAll<Texture2D>())
                if (!used.Contains(t)) { unused += TextureBytes(t, out _); unusedCount++; }

            long total = groups.Values.Sum(g => g.bytes);
            return new JObject
            {
                ["estimatedMB"] = total / MB,
                ["unityAllocatedMB"] = Profiler.GetTotalAllocatedMemoryLong() / MB,
                ["unityReservedMB"] = Profiler.GetTotalReservedMemoryLong() / MB,
                ["monoUsedMB"] = Profiler.GetMonoUsedSizeLong() / MB,
                ["gfxDriverMB"] = Profiler.GetAllocatedMemoryForGraphicsDriver() / MB,
                ["texture2DNotInSceneMB"] = unused / MB,
                ["texture2DNotInScene"] = unusedCount,
                ["sceneMaterials"] = mats.Count,
                ["groups"] = new JArray(groups.OrderByDescending(g => g.Value.bytes)
                    .Select(g => $"{g.Value.bytes / MB} MB ×{g.Value.count}  {g.Key}")),
                ["biggest"] = new JArray(items.OrderByDescending(i => i.bytes).Take(top)
                    .Select(i => $"{Math.Round(i.bytes / (double)MB, 1)} MB  {i.name}")),
            };
        }

        static long TextureBytes(Texture t, out string kind)
        {
            switch (t)
            {
                case RenderTexture rt:
                    kind = "render texture";
                    if (!rt.IsCreated()) return 0;
                    if (rt.dimension == TextureDimension.Cube) kind = "render cubemap";
                    long px = (long)rt.width * rt.height * Math.Max(1, rt.volumeDepth) * Math.Max(1, rt.antiAliasing)
                              * (rt.dimension == TextureDimension.Cube ? 6 : 1);
                    long b = px * Bpp(rt.graphicsFormat) / 8 + px * Bpp(rt.depthStencilFormat) / 8;
                    return rt.useMipMap ? b * 4 / 3 : b;
                case Texture2D t2:
                    kind = t2.isReadable ? "texture2D (readable: CPU+GPU)" : "texture2D";
                    long s = Chain(t2.width, t2.height, 1, t2.mipmapCount, t2.graphicsFormat);
                    return t2.isReadable ? s * 2 : s;
                case Cubemap c:
                    kind = "cubemap";
                    return 6 * Chain(c.width, c.height, 1, c.mipmapCount, c.graphicsFormat);
                case Texture3D t3:
                    kind = "texture3D";
                    return Chain(t3.width, t3.height, t3.depth, t3.mipmapCount, t3.graphicsFormat);
                case Texture2DArray ta:
                    kind = "texture array";
                    return ta.depth * Chain(ta.width, ta.height, 1, ta.mipmapCount, ta.graphicsFormat);
                default:
                    kind = t.GetType().Name;
                    return 0;
            }
        }

        static long Chain(int w, int h, int d, int mips, GraphicsFormat f)
        {
            if (f == GraphicsFormat.None) return 0;
            long sum = 0;
            for (int i = 0; i < Math.Max(1, mips); i++)
            {
                sum += (long)GraphicsFormatUtility.ComputeMipmapSize(Math.Max(1, w >> i), Math.Max(1, h >> i), f) * Math.Max(1, d >> i);
            }
            return sum;
        }

        static long Bpp(GraphicsFormat f) =>
            f == GraphicsFormat.None ? 0 : GraphicsFormatUtility.GetBlockSize(f) * 8L / Math.Max(1, GraphicsFormatUtility.GetBlockWidth(f) * GraphicsFormatUtility.GetBlockHeight(f));

        static long MeshBytes(Mesh m)
        {
            long vb = 0;
            for (int s = 0; s < m.vertexBufferCount; s++) vb += (long)m.GetVertexBufferStride(s) * m.vertexCount;
            long ib = 0;
            for (int i = 0; i < m.subMeshCount; i++) ib += (long)m.GetIndexCount(i);
            return vb + ib * (m.indexFormat == IndexFormat.UInt32 ? 4 : 2);
        }
    }
}
