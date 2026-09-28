using System.Collections.Generic;
using House4696.Core;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>Door furniture: lever handles on square roses (as the catalogue shows), latch and strike plates, hinges.</summary>
    public static class DoorHardware
    {
        /// <summary>
        /// Lever handle pair on a leaf (leaf space: x from the lock edge, z towards the front face): a square rose on each
        /// face at <paramref name="axis"/> (x, y), the lever pointing towards the hinges; the latch face plate on the lock edge.
        /// </summary>
        public static void Handles(MeshBuilder mb, Vector2 axis, float thickness, Material chrome, string style = "square")
        {
            if (chrome == null) return;
            float x = axis.x, y = axis.y, half = thickness * 0.5f;
            if (string.Equals(style, "round", System.StringComparison.OrdinalIgnoreCase))
            {
                RoundHandles(mb, axis, thickness, chrome);
                return;
            }
            foreach (float s in new[] { 1f, -1f })
            {
                float face = s * half;
                // square rose 52 × 52 × 9 mm with soft corners
                mb.RoundBox(new Vector3(x - 0.026f, y - 0.026f, Mathf.Min(face, face + s * 0.009f)),
                            new Vector3(x + 0.026f, y + 0.026f, Mathf.Max(face, face + s * 0.009f)), 0.0025f, chrome, 2);
                // neck out of the rose, then the lever towards the hinges
                float zOut = face + s * 0.052f;
                mb.Rod(new Vector3(x, y, face + s * 0.008f), new Vector3(x, y, zOut), 0.0085f, chrome, 16);
                float z0 = Mathf.Min(zOut - s * 0.012f, zOut + s * 0.001f), z1 = Mathf.Max(zOut - s * 0.012f, zOut + s * 0.001f);
                mb.RoundBox(new Vector3(x - 0.012f, y - 0.009f, z0), new Vector3(x + 0.128f, y + 0.009f, z1), 0.0045f, chrome, 3);
            }
            // latch face plate on the lock edge
            mb.RoundBox(new Vector3(-0.0015f, y - 0.055f, -0.011f), new Vector3(0.0002f, y + 0.055f, 0.011f), 0.0005f, chrome, 1);
        }

        /// <summary>
        /// Classic handle pair: a round rose with a stepped profile, a short neck and a lever that curves out and down towards
        /// the hinges, ending in a rounded tip; the latch plate on the lock edge.
        /// </summary>
        static void RoundHandles(MeshBuilder mb, Vector2 axis, float thickness, Material m)
        {
            float x = axis.x, y = axis.y, half = thickness * 0.5f;
            foreach (float s in new[] { 1f, -1f })
            {
                float face = s * half;
                using (mb.Place(new Vector3(x, y, face), Quaternion.FromToRotation(Vector3.up, new Vector3(0f, 0f, s))))
                    mb.Lathe(Vector3.zero, new[]
                    {
                        new Vector2(0.027f, 0f), new Vector2(0.027f, 0.002f), new Vector2(0.024f, 0.005f), new Vector2(0.018f, 0.0075f),
                        new Vector2(0.012f, 0.009f), new Vector2(0.0095f, 0.012f), new Vector2(0.0095f, 0.02f), new Vector2(0f, 0.02f),
                    }, 28, m);
                // neck out of the rose, a knuckle, then the lever: it runs towards the hinges, dropping and bending back
                // towards the leaf, and ends in a rounded tip
                float zOut = face + s * 0.05f;
                mb.Rod(new Vector3(x, y, face + s * 0.018f), new Vector3(x, y, zOut), 0.0075f, m, 12);
                mb.Sphere(new Vector3(x, y, zOut), 0.0088f, m, 12, 8);
                const int n = 12;
                var pts = new Vector3[n + 1];
                var radii = new float[n + 1];
                for (int i = 0; i <= n; i++)
                {
                    float t = i / (float)n;
                    pts[i] = new Vector3(x + 0.13f * t, y - 0.01f * t * t, face + s * (0.05f - 0.007f * t * t));
                    radii[i] = 0.0075f - 0.0013f * t;
                }
                Tube(mb, pts, radii, m, 14);
                mb.Sphere(pts[n], 0.0074f, m, 12, 8);
            }
            mb.RoundBox(new Vector3(-0.0015f, y - 0.055f, -0.011f), new Vector3(0.0002f, y + 0.055f, 0.011f), 0.0005f, m, 1);
        }

        /// <summary>A smooth tube along a polyline (rings share their vertices' normals; ends are left open for caps).</summary>
        static void Tube(MeshBuilder mb, IList<Vector3> pts, IList<float> radii, Material m, int sides)
        {
            int n = pts.Count;
            if (n < 2) return;
            var rings = new Vector3[n, sides];
            var norms = new Vector3[n, sides];
            Vector3 frame = Vector3.zero;
            for (int i = 0; i < n; i++)
            {
                Vector3 t = (pts[Mathf.Min(n - 1, i + 1)] - pts[Mathf.Max(0, i - 1)]).normalized;
                // parallel transport of the ring's frame so it does not twist along the tube
                frame = i == 0 ? Vector3.Cross(t, Mathf.Abs(t.y) < 0.9f ? Vector3.up : Vector3.right).normalized
                               : Vector3.ProjectOnPlane(frame, t).normalized;
                Vector3 bin = Vector3.Cross(t, frame);
                for (int k = 0; k < sides; k++)
                {
                    float a = k * Mathf.PI * 2f / sides;
                    Vector3 d = frame * Mathf.Cos(a) + bin * Mathf.Sin(a);
                    rings[i, k] = pts[i] + d * radii[i];
                    norms[i, k] = d;
                }
            }
            for (int i = 0; i + 1 < n; i++)
                for (int k = 0; k < sides; k++)
                {
                    int k1 = (k + 1) % sides;
                    float u0 = k / (float)sides, u1 = (k + 1) / (float)sides, v0 = i * 0.02f, v1 = (i + 1) * 0.02f;
                    DoorGeo.Quad(mb, rings[i, k], rings[i, k1], rings[i + 1, k1], rings[i + 1, k],
                        norms[i, k], norms[i, k1], norms[i + 1, k1], norms[i + 1, k],
                        new Vector2(u0, v0), new Vector2(u1, v0), new Vector2(u1, v1), new Vector2(u0, v1), m);
                }
        }

        /// <summary>
        /// Flush pulls of a sliding leaf or a folding panel («ракушка»): a narrow rounded plate on each face at
        /// <paramref name="axis"/>, set into the leaf with a dark recess.
        /// </summary>
        public static void FlushPulls(MeshBuilder mb, Vector2 axis, float thickness, Material chrome)
        {
            if (chrome == null) return;
            float x = axis.x, y = axis.y, half = thickness * 0.5f;
            foreach (float s in new[] { 1f, -1f })
            {
                float face = s * half;
                mb.RoundBox(new Vector3(x - 0.012f, y - 0.075f, Mathf.Min(face - s * 0.001f, face + s * 0.0015f)),
                            new Vector3(x + 0.012f, y + 0.075f, Mathf.Max(face - s * 0.001f, face + s * 0.0015f)), 0.006f, chrome, 3);
            }
        }

        /// <summary>
        /// Bathroom lock («фиксатор WC»): round roses under the handle; a thumb-turn on the front face, the emergency release
        /// slot with its red / white indicator on the back.
        /// </summary>
        public static void WcTurn(MeshBuilder mb, Vector2 axis, float thickness, Material chrome, Material indicator, bool square = false)
        {
            if (chrome == null) return;
            float half = thickness * 0.5f;
            foreach (float s in new[] { 1f, -1f })
            {
                using (mb.Place(new Vector3(axis.x, axis.y, s * half), Quaternion.FromToRotation(Vector3.up, new Vector3(0f, 0f, s))))
                {
                    // the rose matches the handle's: square (modern) or round with a stepped edge (classic)
                    if (square) mb.RoundBox(new Vector3(-0.025f, 0f, -0.025f), new Vector3(0.025f, 0.008f, 0.025f), 0.0025f, chrome, 2);
                    else mb.Lathe(Vector3.zero, new[]
                    {
                        new Vector2(0.025f, 0f), new Vector2(0.025f, 0.002f), new Vector2(0.022f, 0.006f), new Vector2(0.012f, 0.008f), new Vector2(0f, 0.008f),
                    }, 28, chrome);
                    if (s > 0f) mb.RoundBox(new Vector3(-0.004f, 0.006f, -0.014f), new Vector3(0.004f, 0.022f, 0.014f), 0.003f, chrome, 2);
                    else if (indicator != null) mb.Box(new Vector3(-0.006f, 0.0075f, -0.0015f), new Vector3(0.006f, 0.0085f, 0.0015f), indicator);
                }
            }
        }

        /// <summary>Round lock escutcheons (a cylinder's or a lever lock's cover) on both faces at <paramref name="axis"/>.</summary>
        public static void Escutcheons(MeshBuilder mb, Vector2 axis, float thickness, Material chrome, bool square = false, bool oval = false)
        {
            if (chrome == null) return;
            float half = thickness * 0.5f;
            foreach (float s in new[] { 1f, -1f })
            {
                var c = new Vector3(axis.x, axis.y, s * half);
                if (oval)
                {
                    // an oval cover (Border): a flattened dome, half of it standing out of the face
                    mb.Sphere(c, new Vector3(0.021f, 0.034f, 0.007f), chrome, 24, 10);
                    continue;
                }
                using (mb.Place(c, Quaternion.FromToRotation(Vector3.up, new Vector3(0f, 0f, s))))
                    if (square) mb.RoundBox(new Vector3(-0.024f, 0f, -0.024f), new Vector3(0.024f, 0.008f, 0.024f), 0.003f, chrome, 2);
                    else mb.Lathe(Vector3.zero, new[]
                    {
                        new Vector2(0.024f, 0f), new Vector2(0.024f, 0.002f), new Vector2(0.022f, 0.006f), new Vector2(0.017f, 0.0085f),
                        new Vector2(0.008f, 0.0095f), new Vector2(0f, 0.0095f),
                    }, 28, chrome);
            }
        }

        /// <summary>
        /// Plate handles of a budget steel door: a long narrow plate on each face (lever at <paramref name="axis"/>, the
        /// cylinder's keyhole below it) and a lever on a short neck.
        /// </summary>
        public static void PlateHandles(MeshBuilder mb, Vector2 axis, float thickness, Material m, Material keyhole)
        {
            if (m == null) return;
            float x = axis.x, y = axis.y, half = thickness * 0.5f;
            foreach (float s in new[] { 1f, -1f })
            {
                float face = s * half, top = face + s * 0.007f;
                mb.RoundBox(new Vector3(x - 0.022f, y - 0.175f, Mathf.Min(face, top)), new Vector3(x + 0.022f, y + 0.045f, Mathf.Max(face, top)), 0.004f, m, 2);
                if (keyhole != null)
                    mb.Box(new Vector3(x - 0.004f, y - 0.135f, Mathf.Min(top, top + s * 0.0005f)), new Vector3(x + 0.004f, y - 0.105f, Mathf.Max(top, top + s * 0.0005f)), keyhole);
                float zOut = face + s * 0.05f;
                mb.Rod(new Vector3(x, y, top), new Vector3(x, y, zOut), 0.008f, m, 14);
                float z0 = Mathf.Min(zOut - s * 0.012f, zOut + s * 0.001f), z1 = Mathf.Max(zOut - s * 0.012f, zOut + s * 0.001f);
                mb.RoundBox(new Vector3(x - 0.012f, y - 0.009f, z0), new Vector3(x + 0.125f, y + 0.009f, z1), 0.0045f, m, 3);
            }
        }

        /// <summary>Door viewer: a small chrome lens ring on both faces.</summary>
        public static void Peephole(MeshBuilder mb, Vector2 at, float thickness, Material chrome)
        {
            if (chrome == null) return;
            float half = thickness * 0.5f;
            foreach (float s in new[] { 1f, -1f })
                using (mb.Place(new Vector3(at.x, at.y, s * half), Quaternion.FromToRotation(Vector3.up, new Vector3(0f, 0f, s))))
                    mb.Lathe(Vector3.zero, new[]
                    {
                        new Vector2(0.014f, 0f), new Vector2(0.014f, 0.002f), new Vector2(0.011f, 0.004f), new Vector2(0.006f, 0.0045f), new Vector2(0f, 0.004f),
                    }, 20, chrome);
        }

        /// <summary>Hinge knuckle: a barrel with rounded finials, standing on the hinge axis.</summary>
        public static void Knuckle(MeshBuilder mb, Vector3 bottom, float height, Material m)
        {
            if (m == null) return;
            const float r = 0.0065f;
            mb.Lathe(bottom, new[]
            {
                new Vector2(0.0f, -0.004f), new Vector2(r * 0.55f, -0.0035f), new Vector2(r * 0.95f, -0.0015f), new Vector2(r, 0f),
                new Vector2(r, height), new Vector2(r * 0.95f, height + 0.0015f), new Vector2(r * 0.55f, height + 0.0035f), new Vector2(0f, height + 0.004f),
            }, 16, m);
        }
    }
}
