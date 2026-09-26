using System;
using System.Collections.Generic;
using House4696.Core;
using UnityEngine;

namespace House4696.Landscape
{
    /// <summary>
    /// Procedural plant meshes built from alpha-cutout cards and thin strips. Foliage cards use
    /// "spherical" normals (pointing away from the crown centre) so crowns shade as soft volumes
    /// instead of flat planes.
    /// Trees take a <c>detail</c> level: 0 is the full crown, 1 the LOD1 crown — the same random stream with every
    /// n-th element kept and widened (<see cref="GardenPerf"/>), so both levels share their silhouette.
    /// </summary>
    public sealed class VegetationFactory
    {
        readonly MaterialLibrary _m;
        public VegetationFactory(MaterialLibrary m) { _m = m; }

        /// <summary>A mesh builder with the vegetation vertex options (<see cref="GardenPerf.IndexedVegetation"/>, <see cref="GardenPerf.CompactVertices"/>).</summary>
        public MeshBuilder NewBuilder() => new MeshBuilder { Weld = GardenPerf.IndexedVegetation, Compact = GardenPerf.CompactVertices };

        // ------------------------------------------------------------------ Norway spruce
        /// <param name="detail">0 = full crown; 1 = LOD1 (every <see cref="GardenPerf.Lod1WhorlStep"/>-th whorl, part of its branches, wider cards, no fillers).</param>
        public MeshBuilder Spruce(float height, int seed, int detail = 0)
        {
            var mb = NewBuilder();
            var rng = new Rng(seed);
            bool low = detail > 0;
            float H = height;
            float R = H * rng.Range(0.19f, 0.23f);
            float baseR = 0.015f * H + 0.06f;
            float crownBase = H * rng.Range(0.03f, 0.09f);
            float lean = rng.Range(-0.01f, 0.01f);

            Trunk(mb, Vector3.zero, H, baseR, 0.03f, low ? GardenPerf.Lod1TrunkSides : 10, _m.Bark, lean, 0f, low ? GardenPerf.Lod1TrunkRings : 8);

            // every random number is drawn in the same order at both levels; LOD1 only skips emitting
            float wide = low ? GardenPerf.Lod1CardWidth : 1f;
            int seg = low ? Mathf.Max(1, GardenPerf.Lod1CardSegments) : 3;
            int whorlStep = Mathf.Max(1, GardenPerf.Lod1WhorlStep);
            float dz = 0.34f;
            int whorl = 0;
            for (float h = crownBase; h < H - 0.5f; h += dz * rng.Range(0.85f, 1.15f), whorl++)
            {
                bool keepWhorl = !low || whorl % whorlStep == 0;
                float t = (h - crownBase) / (H - crownBase);
                float L = R * Mathf.Pow(1f - t, 0.9f) * rng.Range(0.82f, 1.08f) + 0.25f;
                int n = rng.Range(8, 11);
                int keepCount = Mathf.Clamp(Mathf.RoundToInt(n * GardenPerf.Lod1BranchKeep), 1, n);
                float phase = whorl * 2.39996f;
                for (int b = 0; b < n; b++)
                {
                    float az = phase + b * Mathf.PI * 2f / n + rng.Range(-0.25f, 0.25f);
                    float elev = Mathf.Lerp(-16f, 24f, Mathf.Pow(t, 1.3f)) + rng.Range(-6f, 6f);
                    float width = L * rng.Range(0.62f, 0.78f);
                    float roll = rng.Range(-28f, 28f);
                    // LOD1: keepCount of n branches, spread evenly around the stem
                    bool keep = !low || (keepWhorl && (b + 1) * keepCount / n > b * keepCount / n);
                    if (keep)
                        BranchCard(mb, new Vector3(lean * h, h, 0), az, elev, L, width * wide, roll, 0.16f * L, H, seg);
                    // hanging branchlets: a steep card below the outer half of the branch
                    if (L > 0.6f)
                    {
                        float az2 = az + rng.Range(-0.15f, 0.15f);
                        float elev2 = elev - rng.Range(28f, 45f);
                        float roll2 = rng.Range(70f, 110f);
                        if (keep)
                            BranchCard(mb, new Vector3(lean * h, h - 0.05f, 0), az2, elev2, L * 0.85f, L * 0.55f * wide, roll2, 0.1f * L, H, seg);
                    }
                }
                // filler sprays between whorls (LOD0 only)
                if (rng.Value() < 0.8f)
                {
                    int f = rng.Range(2, 5);
                    for (int b = 0; b < f; b++)
                    {
                        float az = rng.Range(0, Mathf.PI * 2);
                        float hh = h + dz * 0.5f;
                        float elev = rng.Range(-30f, 10f);
                        float roll = rng.Range(-60f, 60f);
                        if (!low)
                            BranchCard(mb, new Vector3(lean * hh, hh, 0), az, elev, L * 0.7f, L * 0.45f, roll, 0.2f * L, H, seg);
                    }
                }
            }
            // leader
            for (int k = 0; k < 3; k++)
            {
                float a = k * Mathf.PI / 3f;
                Vector3 dir = new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a));
                Vector3 b0 = new Vector3(lean * H, H - 1.1f, 0), b1 = b0 + Vector3.up * 1.25f;
                Card(mb, b0 - dir * 0.28f, b0 + dir * 0.28f, b1 + dir * 0.02f, b1 - dir * 0.02f, _m.SpruceBranch, new Vector3(0, H * 0.75f, 0), 1f);
            }
            return mb;
        }

        void BranchCard(MeshBuilder mb, Vector3 origin, float azimuth, float elevDeg, float length, float width, float rollDeg,
                        float sag, float H, int seg)
        {
            Vector3 dir = new Vector3(Mathf.Cos(azimuth), 0, Mathf.Sin(azimuth));
            Vector3 fwd = Quaternion.AngleAxis(-elevDeg, Vector3.Cross(Vector3.up, dir)) * dir;
            Vector3 side = Vector3.Cross(Vector3.up, dir).normalized;
            side = Quaternion.AngleAxis(rollDeg, fwd) * side;
            var centre = new Vector3(origin.x, Mathf.Max(origin.y * 0.9f, H * 0.35f), origin.z);
            Vector3 prevL = Vector3.zero, prevR = Vector3.zero; float prevV = 0;
            for (int s = 0; s <= seg; s++)
            {
                float t = s / (float)seg;
                Vector3 p = origin + fwd * (length * t) + Vector3.down * (sag * t * t);
                float w = width * (0.35f + 0.65f * Mathf.Sin(Mathf.Clamp01(t * 0.9f + 0.1f) * Mathf.PI * 0.5f + 0.2f));
                Vector3 l = p - side * (w * 0.5f), r = p + side * (w * 0.5f);
                if (s > 0)
                {
                    Vector3 n0 = SphereNormal(prevL, centre), n1 = SphereNormal(prevR, centre), n2 = SphereNormal(r, centre), n3 = SphereNormal(l, centre);
                    // double-sided material: winding only matters for consistency
                    mb.Triangle(prevL, l, r, n0, n3, n2, new Vector2(0, prevV), new Vector2(0, t), new Vector2(1, t), _m.SpruceBranch);
                    mb.Triangle(prevL, r, prevR, n0, n2, n1, new Vector2(0, prevV), new Vector2(1, t), new Vector2(1, prevV), _m.SpruceBranch);
                }
                prevL = l; prevR = r; prevV = t;
            }
        }

        static Vector3 SphereNormal(Vector3 p, Vector3 centre)
        {
            Vector3 d = p - centre;
            d.y *= 0.6f;
            return (d.normalized + Vector3.up * 0.35f).normalized;
        }

        void Card(MeshBuilder mb, Vector3 a, Vector3 b, Vector3 c, Vector3 d, Material m, Vector3 centre, float vMax)
        {
            Vector3 na = SphereNormal(a, centre), nb = SphereNormal(b, centre), nc = SphereNormal(c, centre), nd = SphereNormal(d, centre);
            mb.Triangle(a, d, c, na, nd, nc, new Vector2(0, 0), new Vector2(0, vMax), new Vector2(1, vMax), m);
            mb.Triangle(a, c, b, na, nc, nb, new Vector2(0, 0), new Vector2(1, vMax), new Vector2(1, 0), m);
        }

        void Trunk(MeshBuilder mb, Vector3 basePos, float height, float r0, float r1, int sides, Material m, float lean, float bend = 0f,
                   int rings = 8)
        {
            rings = Mathf.Max(1, rings);
            sides = Mathf.Max(3, sides);
            Vector3 Centre(float t, float y) =>
                basePos + new Vector3(lean * y + bend * Mathf.Sin(t * Mathf.PI), y, bend * 0.4f * Mathf.Sin(t * 2.2f));
            if (mb.Weld && m != null)
            {
                // indexed grid: (sides + 1) × (rings + 1) points, the u seam duplicated
                var idx = new int[sides + 1, rings + 1];
                for (int k = 0; k <= rings; k++)
                {
                    float t = k / (float)rings, y = t * height, rad = Mathf.Lerp(r0, r1, t);
                    Vector3 c = Centre(t, y);
                    for (int i = 0; i <= sides; i++)
                    {
                        float a = i * Mathf.PI * 2 / sides;
                        Vector3 d = new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a));
                        idx[i, k] = mb.V(c + d * rad, d, new Vector2(i / (float)sides, y));
                    }
                }
                for (int k = 0; k < rings; k++)
                for (int i = 0; i < sides; i++)
                {
                    mb.Tri(idx[i, k], idx[i, k + 1], idx[i + 1, k + 1], m);
                    mb.Tri(idx[i, k], idx[i + 1, k + 1], idx[i + 1, k], m);
                }
                return;
            }
            for (int k = 0; k < rings; k++)
            {
                float t0 = k / (float)rings, t1 = (k + 1) / (float)rings;
                float y0 = t0 * height, y1 = t1 * height;
                float ra = Mathf.Lerp(r0, r1, t0), rb = Mathf.Lerp(r0, r1, t1);
                Vector3 c0 = Centre(t0, y0), c1 = Centre(t1, y1);
                for (int i = 0; i < sides; i++)
                {
                    float a0 = i * Mathf.PI * 2 / sides, a1 = (i + 1) * Mathf.PI * 2 / sides;
                    Vector3 d0 = new Vector3(Mathf.Cos(a0), 0, Mathf.Sin(a0)), d1 = new Vector3(Mathf.Cos(a1), 0, Mathf.Sin(a1));
                    float u0 = i / (float)sides, u1 = (i + 1) / (float)sides;
                    mb.Triangle(c0 + d0 * ra, c1 + d0 * rb, c1 + d1 * rb, d0, d0, d1, new Vector2(u0, y0), new Vector2(u0, y1), new Vector2(u1, y1), m);
                    mb.Triangle(c0 + d0 * ra, c1 + d1 * rb, c0 + d1 * ra, d0, d1, d1, new Vector2(u0, y0), new Vector2(u1, y1), new Vector2(u1, y0), m);
                }
            }
        }

        // ------------------------------------------------------------------ birch
        /// <param name="detail">0 = full crown; 1 = LOD1 (every <see cref="GardenPerf.Lod1LeafStep"/>-th leaf clump, enlarged; thinner trunk and limbs).</param>
        public MeshBuilder Birch(float height, int seed, int detail = 0)
        {
            var mb = NewBuilder();
            var rng = new Rng(seed);
            bool low = detail > 0;
            int leafStep = low ? Mathf.Max(1, GardenPerf.Lod1LeafStep) : 1;
            float leafScale = low ? GardenPerf.Lod1LeafScale : 1f;
            int leaf = 0;
            float H = height;
            float bend = rng.Range(-0.4f, 0.4f);
            Trunk(mb, Vector3.zero, H * 0.92f, 0.012f * H + 0.04f, 0.035f, low ? GardenPerf.Lod1TrunkSides : 9, _m.BirchBark,
                rng.Range(-0.015f, 0.015f), bend, low ? GardenPerf.Lod1TrunkRings : 8);
            Vector3 crownC = new Vector3(bend * 0.5f, H * 0.66f, 0);
            int branches = rng.Range(7, 11);
            for (int b = 0; b < branches; b++)
            {
                float h = H * rng.Range(0.38f, 0.86f);
                float az = rng.Range(0, Mathf.PI * 2);
                Vector3 dir = new Vector3(Mathf.Cos(az), rng.Range(0.25f, 0.7f), Mathf.Sin(az)).normalized;
                float len = H * rng.Range(0.2f, 0.34f) * (1.15f - h / H);
                Vector3 p0 = new Vector3(bend * Mathf.Sin(h / H * Mathf.PI), h, 0);
                Limb(mb, p0, p0 + dir * len, 0.035f, 0.012f, _m.BirchBark, low ? GardenPerf.Lod1LimbSides : 5);
                int clusters = Mathf.Max(6, Mathf.RoundToInt(len * 16));
                for (int c = 0; c < clusters; c++)
                {
                    Vector3 p = Vector3.Lerp(p0, p0 + dir * len, rng.Range(0.3f, 1.05f)) + (Vector3)rng.InsideUnitCircle() * 0.4f;
                    float size = rng.Range(0.55f, 0.95f);
                    LeafClump(mb, p, size * leafScale, _m.BirchLeaves, crownC, rng, leaf++ % leafStep == 0);
                }
            }
            for (int c = 0; c < 140; c++)
            {
                Vector3 p = crownC + Vector3.Scale(rng.InsideUnitSphere(), new Vector3(H * 0.25f, H * 0.3f, H * 0.25f));
                p.x += rng.Range(-0.2f, 0.2f);
                float size = rng.Range(0.6f, 1.0f);
                LeafClump(mb, p, size * leafScale, _m.BirchLeaves, crownC, rng, leaf++ % leafStep == 0);
            }
            return mb;
        }

        void Limb(MeshBuilder mb, Vector3 a, Vector3 b, float r0, float r1, Material m, int sides = 5)
        {
            Vector3 axis = (b - a).normalized;
            Vector3 u = Vector3.Cross(axis, Vector3.up).sqrMagnitude < 1e-4f ? Vector3.right : Vector3.Cross(axis, Vector3.up).normalized;
            Vector3 v = Vector3.Cross(axis, u);
            sides = Mathf.Max(3, sides);
            float len = (b - a).magnitude;
            for (int i = 0; i < sides; i++)
            {
                float a0 = i * Mathf.PI * 2 / sides, a1 = (i + 1) * Mathf.PI * 2 / sides;
                Vector3 d0 = u * Mathf.Cos(a0) + v * Mathf.Sin(a0), d1 = u * Mathf.Cos(a1) + v * Mathf.Sin(a1);
                mb.Triangle(a + d0 * r0, b + d1 * r1, b + d0 * r1, d0, d1, d0, new Vector2(0, 0), new Vector2(0.2f, len), new Vector2(0, len), m);
                mb.Triangle(a + d0 * r0, a + d1 * r0, b + d1 * r1, d0, d1, d1, new Vector2(0, 0), new Vector2(0.2f, 0), new Vector2(0.2f, len), m);
            }
        }

        /// <summary>Three crossed quads of a leaf-cluster texture. <paramref name="emit"/> = false draws the same random numbers but adds nothing (LOD1 decimation).</summary>
        void LeafClump(MeshBuilder mb, Vector3 p, float size, Material m, Vector3 centre, Rng rng, bool emit = true)
        {
            for (int k = 0; k < 3; k++)
            {
                var q = Quaternion.Euler(rng.Range(-40f, 40f), rng.Range(0f, 360f), rng.Range(-40f, 40f));
                if (!emit) continue;
                Vector3 r = q * Vector3.right * (size * 0.5f), up = q * Vector3.up * (size * 0.5f);
                Card(mb, p - r - up, p + r - up, p + r + up, p - r + up, m, centre, 1f);
            }
        }

        // ------------------------------------------------------------------ generic broadleaf / big shrub
        /// <param name="detail">0 = full crown; 1 = LOD1 (every <see cref="GardenPerf.Lod1LeafStep"/>-th leaf clump, enlarged; thinner trunk).</param>
        public MeshBuilder BroadleafTree(float height, float radius, int seed, bool trunk = true, int detail = 0)
        {
            var mb = NewBuilder();
            var rng = new Rng(seed);
            bool low = detail > 0;
            int leafStep = low ? Mathf.Max(1, GardenPerf.Lod1LeafStep) : 1;
            float leafScale = low ? GardenPerf.Lod1LeafScale : 1f;
            int leaf = 0;
            if (trunk)
                Trunk(mb, Vector3.zero, height * 0.55f, 0.02f * height + 0.05f, 0.05f, low ? GardenPerf.Lod1TrunkSides : 8, _m.Bark,
                    rng.Range(-0.02f, 0.02f), 0f, low ? GardenPerf.Lod1TrunkRings : 8);
            Vector3 c = new Vector3(0, height - radius * 0.95f, 0);
            int n = Mathf.RoundToInt(radius * radius * 22f) + 20;
            for (int i = 0; i < n; i++)
            {
                Vector3 d = rng.OnUnitSphere();
                d.y = d.y * 0.85f;
                Vector3 p = c + Vector3.Scale(d, new Vector3(radius, radius * 1.05f, radius)) * rng.Range(0.55f, 1.0f);
                if (p.y < 0.2f) continue;
                float size = rng.Range(0.9f, 1.5f);
                LeafClump(mb, p, size * leafScale, _m.DeciduousLeaves, c, rng, leaf++ % leafStep == 0);
            }
            return mb;
        }

        // ------------------------------------------------------------------ dwarf mountain pine / round conifer
        /// <summary>Bumpy needle-textured mound covered with small needle tufts (reads as a dense dwarf pine).</summary>
        public MeshBuilder RoundConifer(float radius, float height, int seed)
        {
            var mb = NewBuilder();
            var rng = new Rng(seed);
            Vector3 c = new Vector3(0, height * 0.42f, 0);
            Vector3 r = new Vector3(radius, height * 0.58f, radius);
            Vector3 off = new Vector3(seed * 0.13f, seed * 0.07f, seed * 0.11f);
            Vector3 Surf(Vector3 d, out Vector3 n)
            {
                float bump = Noise.Fbm3(d * 2.3f + off, 4, seed) * 0.22f + Noise.Fbm3(d * 7.5f + off, 2, seed + 3) * 0.07f;
                Vector3 p = c + Vector3.Scale(d * (1f + bump), r);
                if (p.y < 0.02f) p.y = 0.02f;
                n = Vector3.Scale(d, new Vector3(1 / r.x, 1 / r.y, 1 / r.z)).normalized;
                return p;
            }
            const int seg = 30, rings = 14;
            Vector3 D(float a, float t) => new Vector3(Mathf.Cos(a) * Mathf.Cos(t), Mathf.Sin(t), Mathf.Sin(a) * Mathf.Cos(t));
            Vector2 U(Vector3 p) => new Vector2(p.x + p.z, p.y);
            if (mb.Weld && _m.ConiferCore != null)
            {
                // indexed grid: every surface point once
                var idx = new int[seg + 1, rings + 1];
                for (int j = 0; j <= rings; j++)
                {
                    float t = Mathf.PI * j / rings - Mathf.PI / 2;
                    for (int i = 0; i <= seg; i++)
                    {
                        float a = Mathf.PI * 2 * i / seg;
                        Vector3 p = Surf(D(a, t), out var n);
                        idx[i, j] = mb.V(p, n, U(p));
                    }
                }
                for (int j = 0; j < rings; j++)
                for (int i = 0; i < seg; i++)
                {
                    mb.Tri(idx[i, j], idx[i, j + 1], idx[i + 1, j + 1], _m.ConiferCore);
                    mb.Tri(idx[i, j], idx[i + 1, j + 1], idx[i + 1, j], _m.ConiferCore);
                }
            }
            else
            {
                for (int j = 0; j < rings; j++)
                {
                    float t0 = Mathf.PI * j / rings - Mathf.PI / 2, t1 = Mathf.PI * (j + 1) / rings - Mathf.PI / 2;
                    for (int i = 0; i < seg; i++)
                    {
                        float a0 = Mathf.PI * 2 * i / seg, a1 = Mathf.PI * 2 * (i + 1) / seg;
                        Vector3 p00 = Surf(D(a0, t0), out var n00), p10 = Surf(D(a1, t0), out var n10);
                        Vector3 p01 = Surf(D(a0, t1), out var n01), p11 = Surf(D(a1, t1), out var n11);
                        mb.Triangle(p00, p01, p11, n00, n01, n11, U(p00), U(p01), U(p11), _m.ConiferCore);
                        mb.Triangle(p00, p11, p10, n00, n11, n10, U(p00), U(p11), U(p10), _m.ConiferCore);
                    }
                }
            }
            int count = Mathf.RoundToInt(radius * radius * 820f) + 90;
            for (int k = 0; k < count; k++)
            {
                Vector3 d = rng.OnUnitSphere();
                if (d.y < -0.3f) { d.y = -d.y * 0.3f; d.Normalize(); }
                Vector3 p = Surf(d, out var nrm);
                float s = rng.Range(0.14f, 0.23f) * Mathf.Clamp(radius, 0.7f, 1.4f);
                Vector3 tang = Vector3.Cross(nrm, rng.OnUnitSphere()).normalized;
                Vector3 dirOut = (nrm + rng.OnUnitSphere() * 0.35f).normalized;
                Vector3 b0 = p - dirOut * (s * 0.45f), b1 = p + dirOut * (s * 0.55f);
                Card(mb, b0 - tang * s * 0.5f, b0 + tang * s * 0.5f, b1 + tang * s * 0.5f, b1 - tang * s * 0.5f, _m.PineTuft, c - Vector3.up * 0.2f, 1f);
            }
            return mb;
        }

        void Ellipsoid(MeshBuilder mb, Vector3 c, Vector3 r, Material m, int seg, int rings)
        {
            for (int j = 0; j < rings; j++)
            {
                float t0 = Mathf.PI * j / rings - Mathf.PI / 2, t1 = Mathf.PI * (j + 1) / rings - Mathf.PI / 2;
                for (int i = 0; i < seg; i++)
                {
                    float a0 = Mathf.PI * 2 * i / seg, a1 = Mathf.PI * 2 * (i + 1) / seg;
                    Vector3 P(float a, float t) => new Vector3(Mathf.Cos(a) * Mathf.Cos(t), Mathf.Sin(t), Mathf.Sin(a) * Mathf.Cos(t));
                    Vector3 p00 = P(a0, t0), p10 = P(a1, t0), p01 = P(a0, t1), p11 = P(a1, t1);
                    Vector3 W(Vector3 u) => c + Vector3.Scale(u, r);
                    mb.Triangle(W(p00), W(p01), W(p11), p00, p01, p11, Vector2.zero, Vector2.up, Vector2.one, m);
                    mb.Triangle(W(p00), W(p11), W(p10), p00, p11, p10, Vector2.zero, Vector2.one, Vector2.right, m);
                }
            }
        }

        // ------------------------------------------------------------------ ornamental grasses
        /// <param name="variant">column of the blade atlas (0..7); 7 = grey-green</param>
        public MeshBuilder GrassClump(float radius, float height, int blades, int variant, int plumes, float plumeHeight, int seed,
                                      float arch = 1f, float plumeSize = 0.32f)
        {
            var mb = NewBuilder();
            var rng = new Rng(seed);
            for (int i = 0; i < blades; i++)
            {
                Vector2 bp = rng.InsideUnitCircle() * radius * 0.35f;
                float az = rng.Range(0, Mathf.PI * 2);
                Vector3 outward = new Vector3(Mathf.Cos(az), 0, Mathf.Sin(az));
                float len = height * rng.Range(0.65f, 1.25f);
                float elev = rng.Range(48f, 86f) * Mathf.Deg2Rad;
                float w0 = rng.Range(0.006f, 0.011f);
                int k = Mathf.Clamp(variant + (rng.Value() < 0.3f ? (rng.Value() < 0.5f ? -1 : 1) : 0), 0, 7);
                float u = (k + 0.5f) / 8f;
                Blade(mb, new Vector3(bp.x, 0, bp.y), outward, elev, len, w0, 5, arch * rng.Range(0.7f, 1.3f), u, _m.Blades);
            }
            for (int p = 0; p < plumes; p++)
            {
                Vector2 bp = rng.InsideUnitCircle() * radius * 0.3f;
                float az = rng.Range(0, Mathf.PI * 2);
                Vector3 outward = new Vector3(Mathf.Cos(az), 0, Mathf.Sin(az));
                float lean = rng.Range(0.05f, 0.35f);
                float h = plumeHeight * rng.Range(0.85f, 1.12f);
                Vector3 b = new Vector3(bp.x, 0, bp.y);
                Vector3 top = b + outward * (h * lean) + Vector3.up * h;
                // stalk
                Blade(mb, b, (top - b).normalized, 88f * Mathf.Deg2Rad, h * 0.8f, 0.004f, 3, 0.1f, (6 + 0.5f) / 8f, _m.Blades, straightDir: (top - b).normalized);
                // plume: two crossed cards hanging from the top, slightly arched
                float ps = plumeSize * rng.Range(0.75f, 1.1f);
                Vector3 axis = (Vector3.up + outward * (lean + 0.25f)).normalized;
                Vector3 pBase = b + (top - b) * 0.78f;
                for (int c = 0; c < 3; c++)
                {
                    Vector3 side = Quaternion.AngleAxis(c * 60f + rng.Range(0, 30f), axis) * Vector3.Cross(axis, outward).normalized;
                    Vector3 a0 = pBase - side * ps * 0.13f, a1 = pBase + side * ps * 0.13f;
                    Vector3 a2 = pBase + axis * ps + side * ps * 0.13f, a3 = pBase + axis * ps - side * ps * 0.13f;
                    var n = (outward + Vector3.up).normalized;
                    mb.Triangle(a0, a3, a2, n, n, n, new Vector2(0, 0), new Vector2(0, 1), new Vector2(1, 1), _m.Plume);
                    mb.Triangle(a0, a2, a1, n, n, n, new Vector2(0, 0), new Vector2(1, 1), new Vector2(1, 0), _m.Plume);
                }
            }
            return mb;
        }

        /// <summary>Tapered, arching blade strip. Normals lean outward/up for soft, grass-like shading.</summary>
        public void Blade(MeshBuilder mb, Vector3 root, Vector3 outward, float elev, float len, float w0, int seg, float arch, float u,
                          Material m, Vector3? straightDir = null)
        {
            Vector3 side = Vector3.Cross(Vector3.up, outward).normalized;
            if (side.sqrMagnitude < 1e-4f) side = Vector3.right;
            Vector3 p = root;
            Vector3 dir = straightDir ?? (outward * Mathf.Cos(elev) + Vector3.up * Mathf.Sin(elev));
            Vector3 n = (Vector3.up * 0.7f + outward * 0.5f).normalized;
            float du = 0.035f;
            for (int s = 0; s < seg; s++)
            {
                float t0 = s / (float)seg, t1 = (s + 1) / (float)seg;
                Vector3 d = straightDir.HasValue ? dir : (dir + Vector3.down * (arch * t0 * 1.1f)).normalized;
                Vector3 q = p + d * (len / seg);
                float wa = w0 * (1 - t0 * 0.9f), wb = w0 * (1 - t1 * 0.9f);
                mb.Triangle(p - side * wa, q - side * wb, q + side * wb, n, n, n, new Vector2(u - du, t0), new Vector2(u - du, t1), new Vector2(u + du, t1), m);
                mb.Triangle(p - side * wa, q + side * wb, p + side * wa, n, n, n, new Vector2(u - du, t0), new Vector2(u + du, t1), new Vector2(u + du, t0), m);
                p = q;
            }
        }

        // ------------------------------------------------------------------ clipped hedge (rounded, noise-displaced box)
        public MeshBuilder Hedge(Vector3 size, float round, int seed, float cell = 0.05f) => HedgeMesh(size, round, seed, cell, false);

        /// <summary>
        /// ShadowsOnly stand-in of <see cref="Hedge"/> (same size, round and seed): <see cref="GardenPerf.HedgeProxyCell"/>
        /// cells, only the large (3.1) noise octave, the surface <see cref="GardenPerf.HedgeProxyInset"/> inside the visible
        /// one (no acne on the lit side), and exactly the visible hedge's tufts, so the ground shadow keeps its leafy fringe.
        /// </summary>
        public MeshBuilder HedgeShadow(Vector3 size, float round, int seed) =>
            HedgeMesh(size, round, seed, Mathf.Max(0.02f, GardenPerf.HedgeProxyCell), true);

        MeshBuilder HedgeMesh(Vector3 size, float round, int seed, float cell, bool shadowProxy)
        {
            var mb = NewBuilder();
            Vector3 half = size * 0.5f;
            Vector3 inner = half - Vector3.one * round;
            inner.y = half.y - round;
            Vector3 centre = new Vector3(0, half.y, 0);
            int ox = seed % 1000;
            Vector3 Surf(Vector3 p, out Vector3 nrm, bool coarse)
            {
                Vector3 local = p - centre;
                Vector3 cl = new Vector3(Mathf.Clamp(local.x, -inner.x, inner.x), Mathf.Clamp(local.y, -half.y, inner.y), Mathf.Clamp(local.z, -inner.z, inner.z));
                Vector3 d = local - cl;
                if (d.sqrMagnitude < 1e-8f) { nrm = Vector3.up; return p; }
                nrm = d.normalized;
                Vector3 s = centre + cl + nrm * round;
                float big = Noise.Fbm3(s * 3.1f + new Vector3(ox, 0, 0), 4, seed) * 0.045f;
                if (coarse) return s + nrm * (big - GardenPerf.HedgeProxyInset);
                float n = big + Noise.Fbm3(s * 13f, 3, seed + 1) * 0.02f;
                return s + nrm * n;
            }
            Vector2 Uv(Vector3 p) => new Vector2(p.x + p.z * 0.7f, p.y + p.z * 0.3f);
            void Face(Vector3 o, Vector3 ua, Vector3 va, float lu, float lv)
            {
                int nu = Mathf.Max(2, Mathf.CeilToInt(lu / cell)), nv = Mathf.Max(2, Mathf.CeilToInt(lv / cell));
                var grid = new Vector3[nu + 1, nv + 1];
                var nrms = new Vector3[nu + 1, nv + 1];
                for (int i = 0; i <= nu; i++)
                for (int j = 0; j <= nv; j++)
                    grid[i, j] = Surf(o + ua * (lu * i / nu) + va * (lv * j / nv), out nrms[i, j], shadowProxy);
                if (mb.Weld && _m.Hedge != null)
                {
                    // indexed grid: every point once
                    var idx = new int[nu + 1, nv + 1];
                    for (int i = 0; i <= nu; i++)
                    for (int j = 0; j <= nv; j++)
                        idx[i, j] = mb.V(grid[i, j], nrms[i, j], Uv(grid[i, j]));
                    for (int i = 0; i < nu; i++)
                    for (int j = 0; j < nv; j++)
                    {
                        mb.Tri(idx[i, j], idx[i, j + 1], idx[i + 1, j + 1], _m.Hedge);
                        mb.Tri(idx[i, j], idx[i + 1, j + 1], idx[i + 1, j], _m.Hedge);
                    }
                    return;
                }
                for (int i = 0; i < nu; i++)
                for (int j = 0; j < nv; j++)
                {
                    Vector3 a = grid[i, j], b = grid[i + 1, j], c = grid[i + 1, j + 1], d = grid[i, j + 1];
                    mb.Triangle(a, d, c, nrms[i, j], nrms[i, j + 1], nrms[i + 1, j + 1], Uv(a), Uv(d), Uv(c), _m.Hedge);
                    mb.Triangle(a, c, b, nrms[i, j], nrms[i + 1, j + 1], nrms[i + 1, j], Uv(a), Uv(c), Uv(b), _m.Hedge);
                }
            }
            float X = size.x, Y = size.y, Z = size.z;
            Vector3 mn = new Vector3(-half.x, 0, -half.z);
            var faces = new (Vector3 o, Vector3 ua, Vector3 va, float lu, float lv)[]
            {
                (mn, Vector3.right, Vector3.up, X, Y),                                       // front (-Z)
                (new Vector3(half.x, 0, half.z), Vector3.left, Vector3.up, X, Y),            // back (+Z)
                (new Vector3(-half.x, 0, half.z), Vector3.back, Vector3.up, Z, Y),           // left (-X)
                (new Vector3(half.x, 0, -half.z), Vector3.forward, Vector3.up, Z, Y),        // right (+X)
                (new Vector3(-half.x, Y, -half.z), Vector3.right, Vector3.forward, X, Z),    // top
            };
            foreach (var f in faces) Face(f.o, f.ua, f.va, f.lu, f.lv);
            // leafy tufts break the clipped silhouette (identical in the shadow proxy: they sit on the full-detail surface)
            var rng = new Rng(seed * 7 + 1);
            foreach (var f in faces)
            {
                int count = Mathf.RoundToInt(f.lu * f.lv * 34f);
                for (int k = 0; k < count; k++)
                {
                    Vector3 p = Surf(f.o + f.ua * (f.lu * rng.Value()) + f.va * (f.lv * rng.Range(0.04f, 1f)), out var nrm, false);
                    float sz = rng.Range(0.12f, 0.19f);
                    Vector3 dirOut = (nrm + rng.OnUnitSphere() * 0.4f).normalized;
                    Vector3 tang = Vector3.Cross(dirOut, rng.OnUnitSphere()).normalized;
                    Vector3 b0 = p - dirOut * (sz * 0.55f), b1 = p + dirOut * (sz * 0.45f);
                    Card(mb, b0 - tang * sz * 0.5f, b0 + tang * sz * 0.5f, b1 + tang * sz * 0.5f, b1 - tang * sz * 0.5f, _m.BoxTuft, centre, 1f);
                }
            }
            return mb;
        }

        // ------------------------------------------------------------------ lawn blades near the camera
        /// <summary>One lawn blade: generated once, emitted into any chunk or LOD level.</summary>
        public struct LawnBlade
        {
            public Vector3 Root, Outward;
            public float Elev, Height, Width, U;
            /// <summary>Uniform [0, 1) from a separate stream: LOD levels keep the blades with Keep below their share.</summary>
            public float Keep;
        }

        /// <summary>The blades of <see cref="LawnBlades"/> as data (same random stream, same blades).</summary>
        public List<LawnBlade> LawnBladeList(Func<Vector2, float> density, Rect area, int seed, float maxBlades)
        {
            var list = new List<LawnBlade>();
            var rng = new Rng(seed);
            var keep = new Rng(seed * 7919 + 17);
            int count = 0;
            float areaM2 = area.width * area.height;
            int tries = Mathf.RoundToInt(areaM2 * 1600);
            for (int i = 0; i < tries && count < maxBlades; i++)
            {
                var p = new Vector2(rng.Range(area.xMin, area.xMax), rng.Range(area.yMin, area.yMax));
                float d = density(p);
                if (d <= 0 || rng.Value() > d) continue;
                float az = rng.Range(0, Mathf.PI * 2);
                Vector3 outward = new Vector3(Mathf.Cos(az), 0, Mathf.Sin(az));
                float h = rng.Range(0.022f, 0.052f);
                int k = rng.Value() < 0.12f ? 6 : rng.Range(1, 6);
                float u = (k + 0.5f) / 8f;
                float elev = rng.Range(58f, 86f) * Mathf.Deg2Rad;
                float w = rng.Range(0.003f, 0.005f);
                list.Add(new LawnBlade { Root = new Vector3(p.x, 0, p.y), Outward = outward, Elev = elev, Height = h, Width = w, U = u, Keep = keep.Value() });
                count++;
            }
            return list;
        }

        /// <summary>Adds one lawn blade; <paramref name="widen"/> scales its width (LOD1 blades are fewer and wider).</summary>
        public void EmitBlade(MeshBuilder mb, LawnBlade b, float widen = 1f) =>
            Blade(mb, b.Root, b.Outward, b.Elev, b.Height, b.Width * widen, 1, 0.4f, b.U, _m.Blades);

        public MeshBuilder LawnBlades(Func<Vector2, float> density, Rect area, int seed, float maxBlades)
        {
            var mb = NewBuilder();
            foreach (var b in LawnBladeList(density, area, seed, maxBlades)) EmitBlade(mb, b);
            return mb;
        }
    }
}
