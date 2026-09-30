using System.Collections.Generic;
using System.IO;
using System.Text;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using UnityEngine;

namespace House4696.Experiments
{
    /// <summary>
    /// Physical audit of a built project in the editor scene (raycasts against its colliders): floor holes, low
    /// headroom over stairs, see-through slits in walls. Used to find generator defects, not shipped.
    /// </summary>
    public static class BuildAudit
    {
        static HouseBuildResult _r;
        static SceneWriter _w;

        public static string ProjectsDir =>
            Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.Personal), "Library/Application Support/House/Projects");

        public static HouseBuildResult Build(string projectId)
        {
            return Build(Load(projectId));
        }

        public static HouseDocument Load(string projectId) =>
            HouseJson.Deserialize(File.ReadAllText(Path.Combine(ProjectsDir, projectId, "house.json")));

        public static HouseBuildResult Build(HouseDocument doc)
        {
            Dispose();
            _w = new SceneWriter();
            _r = HouseBuilder.Build(doc, MaterialLibrary.Create(), _w);
            Physics.SyncTransforms();
            return _r;
        }

        public static void Dispose()
        {
            // a domain reload forgets _r but not the objects: drop every audit build left in the scene
            foreach (var go in UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects())
                if (go.name.StartsWith("House_") || go.name == "Landscape") Object.DestroyImmediate(go);
            if (_r == null) return;
            if (_r.House) Object.DestroyImmediate(_r.House);
            if (_r.Site) Object.DestroyImmediate(_r.Site);
            foreach (var m in _r.CreatedMaterials) Object.DestroyImmediate(m);
            foreach (var m in _w.RuntimeMeshes) Object.DestroyImmediate(m);
            _r = null;
        }

        public static string Run(string projectId, bool keep = false)
        {
            var r = Build(projectId);
            var sb = new StringBuilder();
            Physics.queriesHitBackfaces = true;
            try
            {
                sb.AppendLine("checks: " + r.Checks.Count + ", warnings: " + string.Join(" | ", r.Warnings));
                FloorHoles(r, sb);
                StairHeadroom(r, sb);
                Slits(r, sb);
            }
            finally
            {
                Physics.queriesHitBackfaces = false;
                if (!keep) Dispose();
            }
            return sb.ToString();
        }

        /// <summary>
        /// Picture of the built house (keep it built with <see cref="Build(string)"/>): a perspective view or, with
        /// <paramref name="ortho"/> &gt; 0, an orthographic section whose near plane cuts <paramref name="near"/> m in front of the camera.
        /// </summary>
        public static string Shot(string file, Vector3 pos, Vector3 euler, float fov = 70f, float ortho = 0f, float near = 0.05f, int w = 1400, int h = 900)
        {
            var go = new GameObject("AuditCamera") { hideFlags = HideFlags.HideAndDontSave };
            var cam = go.AddComponent<Camera>();
            var main = Camera.main;
            if (main != null) cam.CopyFrom(main);
            cam.transform.SetPositionAndRotation(pos, Quaternion.Euler(euler));
            cam.fieldOfView = fov;
            cam.orthographic = ortho > 0f;
            if (ortho > 0f) cam.orthographicSize = ortho;
            cam.nearClipPlane = near; cam.farClipPlane = 200f;
            var rt = new RenderTexture(w, h, 24);
            cam.targetTexture = rt;
            for (int i = 0; i < 3; i++) cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            RenderTexture.active = null;
            File.WriteAllBytes(file, tex.EncodeToPNG());
            Object.DestroyImmediate(tex); cam.targetTexture = null; Object.DestroyImmediate(rt); Object.DestroyImmediate(go);
            return file;
        }

        public static string RunAll()
        {
            var sb = new StringBuilder();
            foreach (var dir in Directory.GetDirectories(ProjectsDir))
            {
                if (!File.Exists(Path.Combine(dir, "house.json"))) continue;
                var id = Path.GetFileName(dir);
                try { sb.AppendLine("=== " + id).Append(Run(id)); }
                catch (System.Exception e) { sb.AppendLine("=== " + id + " FAILED " + e.Message); }
            }
            return sb.ToString();
        }

        static bool Enclosed(Vector3 o)
        {
            foreach (var d in new[] { Vector3.left, Vector3.right, Vector3.forward, Vector3.back })
                if (!Physics.Raycast(o, d, 80f)) return false;
            return true;
        }

        /// <summary>Indoor points of each level (ceiling above, enclosed) whose floor is missing.</summary>
        public static void FloorHoles(HouseBuildResult r, StringBuilder sb)
        {
            var c = r.Context;
            var fp = r.Footprint;
            foreach (var L in c.Doc.Levels)
            {
                int holes = 0, indoor = 0;
                var cells = new List<Vector2>();
                var byCollider = new Dictionary<string, int>();
                for (float x = fp.xMin + 0.05f; x < fp.xMax; x += 0.1f)
                for (float z = fp.yMin + 0.05f; z < fp.yMax; z += 0.1f)
                {
                    var o = new Vector3(x, L.Elevation + 0.4f, z);
                    if (!Physics.Raycast(o, Vector3.up, out var up, L.Height + 0.3f)) continue;
                    if (up.normal.y > 0.5f) continue;   // inside a wall: its top face seen from within
                    if (!Enclosed(o)) continue;
                    indoor++;
                    bool hit = Physics.Raycast(o, Vector3.down, out var dn, 6f);
                    if (hit && dn.point.y > L.Elevation - 0.06f) continue;
                    var p2 = new Vector2(x, z);
                    bool inExt = false;
                    foreach (var f in c.Walls) if (f.Exterior && f.Def.System != WallSystem.SteelGlass && f.Spans(L.Elevation + 0.5f) && f.DistanceTo(p2) < 0.001f) { inExt = true; break; }
                    if (inExt) continue;   // window reveals etc.: the wall itself is the floor there
                    bool well = false;
                    foreach (var g in c.StairGeometries) if (g.To == L && g.InWell(p2)) well = true;
                    if (well) continue;
                    holes++;
                    cells.Add(p2);
                    string k = hit ? dn.collider.name : "none";
                    byCollider[k] = byCollider.TryGetValue(k, out var n) ? n + 1 : 1;
                }
                sb.AppendLine($"[{L.Id}] indoor {indoor} cells, floor holes {holes} ({holes * 0.01f:0.00} m²); below: " +
                              string.Join(", ", Summ(byCollider)));
                foreach (var cl in Clusters(cells, 0.15f))
                {
                    var b = cl.b;
                    sb.AppendLine($"   hole {cl.n} cells x {b.xMin:0.00}..{b.xMax:0.00} z {b.yMin:0.00}..{b.yMax:0.00}");
                }
            }
        }

        static IEnumerable<string> Summ(Dictionary<string, int> d)
        {
            foreach (var kv in d) yield return kv.Key + "×" + kv.Value;
        }

        /// <summary>Connected groups of grid points (4-neighbours within <paramref name="link"/>).</summary>
        public static List<(int n, Rect b)> Clusters(List<Vector2> pts, float link)
        {
            var res = new List<(int, Rect)>();
            var used = new bool[pts.Count];
            for (int i = 0; i < pts.Count; i++)
            {
                if (used[i]) continue;
                var q = new Queue<int>(); q.Enqueue(i); used[i] = true;
                Vector2 mn = pts[i], mx = pts[i]; int n = 0;
                while (q.Count > 0)
                {
                    int a = q.Dequeue(); n++;
                    mn = Vector2.Min(mn, pts[a]); mx = Vector2.Max(mx, pts[a]);
                    for (int j = 0; j < pts.Count; j++)
                        if (!used[j] && (pts[j] - pts[a]).sqrMagnitude < link * link) { used[j] = true; q.Enqueue(j); }
                }
                res.Add((n, Rect.MinMaxRect(mn.x, mn.y, mx.x, mx.y)));
            }
            res.Sort((a, b) => b.Item1.CompareTo(a.Item1));
            return res;
        }

        /// <summary>
        /// Wall ends that touch no other wall of their storey but have one within 0.6 m in some direction: a
        /// see-through slit (probed in 16 directions, measured between the bodies).
        /// </summary>
        public static void Slits(HouseBuildResult r, StringBuilder sb)
        {
            var walls = new List<WallFrame>(r.Context.Walls);
            int n = 0;
            foreach (var f in walls)
            {
                var others = walls.FindAll(g => g != f && g.SameStorey(f));
                foreach (bool atB in new[] { false, true })
                {
                    var p = f.Plan(atB ? f.S1 : f.S0, -f.T * 0.5f);
                    if (others.Exists(g => g.DistanceTo(p) < 0.03f)) continue;
                    float best = 9f; string who = null;
                    for (float s = -f.T * 0.5f; s <= f.T * 0.5f + 0.001f; s += f.T * 0.5f)
                    {
                        var q = f.Plan(atB ? f.S1 : f.S0, -f.T * 0.5f + s);
                        var ahead = new Vector2(f.A.x, f.A.z) * (atB ? 1f : -1f);
                        foreach (var g in others)
                        {
                            // nearest point of g's body: only what lies ahead of the end (not beside its own body)
                            var body = g.PlanBody();
                            Vector2 near = body[0]; float dn = float.MaxValue;
                            for (int e = 0; e < 4; e++)
                            {
                                Vector2 a = body[e], ab = body[(e + 1) % 4] - a;
                                var cp = a + ab * Mathf.Clamp01(Vector2.Dot(q - a, ab) / ab.sqrMagnitude);
                                if ((cp - q).magnitude < dn) { dn = (cp - q).magnitude; near = cp; }
                            }
                            if (dn > 1e-3f && Vector2.Dot((near - q).normalized, ahead) < 0.2f) continue;
                            float d = g.DistanceTo(q);
                            if (d < best) { best = d; who = g.Def.Id; }
                        }
                    }
                    if (best < 0.6f) { n++; sb.AppendLine($"   slit {best:0.00} m: {f.Def.Id}.{(atB ? "b" : "a")} ({p.x:0.00}, {p.y:0.00}) ↔ {who}"); }
                }
            }
            sb.AppendLine($"slits: {n}");
        }

        /// <summary>Clear height above the walking line of each stair (every 10 cm along the treads).</summary>
        public static void StairHeadroom(HouseBuildResult r, StringBuilder sb)
        {
            foreach (var g in r.Context.StairGeometries)
            {
                float min = 99f; Vector3 at = default; string what = "";
                int low = 0, total = 0;
                foreach (var fpr in g.Footprint)
                {
                    var b = Polygon.Bounds(fpr);
                    for (float x = b.xMin + 0.15f; x < b.xMax - 0.1f; x += 0.1f)
                    for (float z = b.yMin + 0.15f; z < b.yMax - 0.1f; z += 0.1f)
                    {
                        var top = new Vector3(x, g.To.Elevation + 1f, z);
                        float best = float.MinValue;
                        foreach (var h in Physics.RaycastAll(top, Vector3.down, g.H + 1.2f))
                            if (h.collider.name == "Stair_" + g.Def.Id) best = Mathf.Max(best, h.point.y);
                        if (best == float.MinValue) continue;
                        var o = new Vector3(x, best + 0.02f, z);
                        total++;
                        float clear = Physics.Raycast(o, Vector3.up, out var up, 5f) ? up.distance : 5f;
                        if (clear < 2.0f) low++;
                        if (clear < min) { min = clear; at = o; what = up.collider ? up.collider.name : ""; }
                    }
                }
                sb.AppendLine($"stair {g.Def.Id}: min headroom {min:0.00} m at ({at.x:0.00}, {at.y:0.00}, {at.z:0.00}) under {what}; {low}/{total} points < 2 m");
            }
        }
    }
}
