using System;
using System.Collections;
using System.IO;
using House4696.App;
using House4696.App.UI;
using House4696.Runtime;
using UnityEditor;
using UnityEngine;

namespace House4696.Experiments
{
    /// <summary>
    /// Screenshot tour of the furniture mode in Play mode, driven through the editor's scripted pointer (the unfocused
    /// editor keeps synthetic Input System events to itself) and its commands (the keys map to them 1:1): walks into the
    /// living room, opens the library, places a sofa with a click, turns it, drags it, deletes it, undoes, aims a picture at
    /// a wall. Saves PNGs (camera + UI) and logs the document state after every step as "[FurnitureTour] …";
    /// "[FurnitureTour] done" at the end.
    /// </summary>
    public static class FurnitureTour
    {
        static IEnumerator _run;
        static double _until;
        static int _untilFrame = -1;

        public static string Start(string outDir, string model = "sofa_modern")
        {
            if (!EditorApplication.isPlaying) return "enter play mode first";
            var ui = UnityEngine.Object.FindAnyObjectByType<AppUI>();
            if (ui == null || ui.S == null) return "app not ready";
            _run = Tour(ui, outDir, model);
            EditorApplication.update -= Step;
            EditorApplication.update += Step;
            return "started";
        }

        /// <summary>
        /// Placement checks on the open project (use a copy — it edits the document): a pendant under the ceiling, a vase on a
        /// table, a picture on a wall, a wardrobe pulled flush to a wall, the item menu; commit timings in the log.
        /// </summary>
        public static string StartChecks(string outDir)
        {
            if (!EditorApplication.isPlaying) return "enter play mode first";
            var ui = UnityEngine.Object.FindAnyObjectByType<AppUI>();
            if (ui == null || ui.S == null) return "app not ready";
            _run = Checks(ui, outDir);
            EditorApplication.update -= Step;
            EditorApplication.update += Step;
            return "started";
        }

        static IEnumerator Checks(AppUI ui, string dir)
        {
            Directory.CreateDirectory(dir);
            _pointer = new FurnitureEditor.ScriptedPointer();
            ui.Furniture.Scripted = _pointer;
            try
            {
                UiTour.Reset(ui);
                if (!ui.Library.IsOpen) ui.Library.Open();
                GoToLiving(ui);
                yield return 100;
                var cam = Camera.main;
                var fe = ui.Furniture;
                var feet = ui.S.Viewer.WalkFeet;
                var ahead = cam.transform.forward;
                ahead.y = 0f;
                ahead.Normalize();

                // ---- pendant: aimed at the floor, it must hang from the ceiling above that point
                fe.BeginPlace(FurnitureCatalog.Instance.Get("pendant_globe_modern"), false);
                Mouse(cam.WorldToScreenPoint(feet + ahead * 2.5f));
                yield return 12;
                Log(ui, "pendant over floor");
                foreach (var x in Shot(dir, "c1-pendant")) yield return x;
                foreach (var x in Click(fe)) yield return x;
                Log(ui, "pendant placed");

                // ---- vase: aimed at the top of a table, it must stand on it
                var table = ui.S.Session.Result.Items.Find(b => b.Model == "dining_table" || b.Model == "round_table" || b.Model == "kitchen_island");
                if (table != null)
                {
                    var tr = table.Object.transform;
                    var top = tr.localToWorldMatrix.MultiplyPoint3x4(new Vector3(table.Local.center.x, table.Local.max.y, table.Local.center.z));
                    fe.BeginPlace(FurnitureCatalog.Instance.Get("vase_white_round"), false);
                    Mouse(cam.WorldToScreenPoint(top));
                    yield return 12;
                    Log(ui, $"vase over {table.Id} (top {top.y:0.00})");
                    foreach (var x in Shot(dir, "c2-vase")) yield return x;
                    foreach (var x in Click(fe)) yield return x;
                    Log(ui, "vase placed");
                }

                // ---- picture: aimed at the nearest wall around the viewer
                var eye = cam.transform.position;
                RaycastHit wall = default;
                bool found = false;
                for (int a = 0; a < 360 && !found; a += 15)
                {
                    var d = Quaternion.Euler(0f, a, 0f) * ahead;
                    foreach (var h in Physics.RaycastAll(new Ray(eye, d), 12f, ~(1 << 2)))
                        if (h.collider.name.StartsWith("Wall_") || h.collider.name.StartsWith("Partition_"))
                        {
                            if (Vector3.Dot(h.normal, -d) < 0.8f) continue;
                            wall = h;
                            found = true;
                            break;
                        }
                }
                if (found)
                {
                    cam.transform.rotation = Quaternion.LookRotation(wall.point - eye);
                    ui.S.Viewer.TeleportWalk(new WalkPoint { Feet = feet, Yaw = Quaternion.LookRotation(wall.point - eye).eulerAngles.y, Pitch = 0f });
                    yield return 20;
                    fe.BeginPlace(FurnitureCatalog.Instance.Get("painting_classic"), false);
                    Mouse(cam.WorldToScreenPoint(wall.point + Vector3.up * 0.2f));
                    yield return 12;
                    Log(ui, "picture over " + wall.collider.name);
                    foreach (var x in Shot(dir, "c3-picture")) yield return x;
                    foreach (var x in Click(fe)) yield return x;
                    Log(ui, "picture placed");

                    // ---- wardrobe: aimed at the floor 15 cm in front of that wall, facing away from it — pulled flush
                    fe.BeginPlace(FurnitureCatalog.Instance.Get("wardrobe"), false, null, FurnitureGeometry.CompassOf(wall.normal));
                    var near = new Vector3(wall.point.x, feet.y, wall.point.z) + wall.normal * 0.45f;
                    Mouse(cam.WorldToScreenPoint(near));
                    yield return 12;
                    var t = fe.Target;
                    float gap = t.Found ? Vector3.Dot(t.World - new Vector3(wall.point.x, t.World.y, wall.point.z), wall.normal) : -1f;
                    Log(ui, $"wardrobe near wall: origin-to-wall {gap:0.000} m (0 = flush)");
                    foreach (var x in Shot(dir, "c4-wardrobe")) yield return x;
                    fe.Escape();
                    yield return 5;
                }

                // ---- timings of a commit: a turn of the last placed item, ten times
                var sel = fe.Selected;
                if (sel != null)
                {
                    var sw = System.Diagnostics.Stopwatch.StartNew();
                    for (int i = 0; i < 4; i++) fe.Rotate(90f);
                    Debug.Log($"[FurnitureTour] 4 turns: {sw.ElapsedMilliseconds} ms total, last rebuild {ui.S.Session.LastBuildMs} ms, items {ui.S.Session.Doc.Items.Count}");
                }

                // ---- the item menu (right click on the selected item)
                sel = fe.Selected;
                if (sel?.Object != null)
                {
                    var c = sel.Object.transform.localToWorldMatrix.MultiplyPoint3x4(sel.Local.center);
                    var at = (Vector2)cam.WorldToScreenPoint(c);
                    Mouse(at, right: true);
                    yield return "frame";
                    Mouse(at);
                    yield return 20;
                    foreach (var x in Shot(dir, "c5-menu")) yield return x;
                    ui.ClosePopover();
                }
            }
            finally
            {
                ui.Furniture.Scripted = null;
                _pointer = null;
            }
        }

        /// <summary>Nudge, duplicate, the item menu, the shortcuts dialog, the orbit toast and the toolbar between both panels.</summary>
        public static string StartExtras(string outDir)
        {
            if (!EditorApplication.isPlaying) return "enter play mode first";
            var ui = UnityEngine.Object.FindAnyObjectByType<AppUI>();
            if (ui == null || ui.S == null) return "app not ready";
            _run = Extras(ui, outDir);
            EditorApplication.update -= Step;
            EditorApplication.update += Step;
            return "started";
        }

        static IEnumerator Extras(AppUI ui, string dir)
        {
            Directory.CreateDirectory(dir);
            _pointer = new FurnitureEditor.ScriptedPointer();
            ui.Furniture.Scripted = _pointer;
            try
            {
                UiTour.Reset(ui);
                ui.SwitchMode(HouseViewer.Mode.Walk);
                if (!ui.Library.IsOpen) ui.Library.Open();
                GoToLiving(ui);
                yield return 100;
                var cam = Camera.main;
                var fe = ui.Furniture;
                var box = ui.S.Session.Result.Items.Find(b => b.Model == "armchair") ?? ui.S.Session.Result.Items[0];
                fe.Select(box);
                yield return 5;
                Log(ui, "selected " + box.Id);

                // ---- nudges: three in a row are one undo step
                var nudge = typeof(FurnitureEditor).GetMethod("Nudge", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                int undo0 = ui.S.Session.UndoCount;
                for (int i = 0; i < 3; i++) { nudge.Invoke(fe, new object[] { Vector2.right, 0.05f }); yield return 3; }
                Log(ui, $"nudged ×3 (undo steps added: {ui.S.Session.UndoCount - undo0})");

                // ---- duplicate: the copy follows the pointer, a click puts it down
                fe.DuplicateSelected();
                var feet = ui.S.Viewer.WalkFeet;
                var ahead = cam.transform.forward;
                ahead.y = 0f;
                Mouse(cam.WorldToScreenPoint(feet + ahead.normalized * 2f + cam.transform.right * 0.8f));
                yield return 12;
                Log(ui, "duplicate following the pointer");
                foreach (var x in Click(fe)) yield return x;
                Log(ui, "duplicate placed");

                // ---- the item menu: a right click on the selected item
                var sel = fe.Selected;
                if (sel?.Object != null)
                {
                    var c = sel.Object.transform.localToWorldMatrix.MultiplyPoint3x4(sel.Local.center);
                    var at = (Vector2)cam.WorldToScreenPoint(c);
                    Mouse(at);
                    yield return "frame";
                    Mouse(at, right: true);
                    yield return "frame";
                    Mouse(at);
                    yield return 20;
                    foreach (var x in Shot(dir, "e1-menu")) yield return x;
                    Log(ui, "menu open: " + ui.PopoverOpen);
                    ui.ClosePopover();
                    yield return 10;
                }

                // ---- shortcuts dialog with the furniture section
                ui.ShowShortcuts();
                yield return 30;
                foreach (var x in Shot(dir, "e2-shortcuts")) yield return x;
                UiTour.Reset(ui);
                yield return 10;

                // ---- from outside: the library offers to walk in; the toolbar between the library and the plan
                ui.Library.Close();
                ui.SwitchMode(HouseViewer.Mode.Orbit);
                ui.GoToView(HouseViewer.Mode.Orbit, 0);
                yield return 60;
                ui.Plan.SetOpen(true);
                ui.Library.Open();
                yield return 40;
                foreach (var x in Shot(dir, "e3-orbit")) yield return x;
                ui.Library.Close();
                ui.SwitchMode(HouseViewer.Mode.Walk);
                GoToLiving(ui);
                yield return 30;
            }
            finally
            {
                ui.Furniture.Scripted = null;
                _pointer = null;
            }
        }

        static IEnumerable Click(FurnitureEditor fe)
        {
            _pointer.Left = true;
            yield return "frame";
            yield return "frame";
            _pointer.Left = false;
            yield return 20;
        }

        static void Step()
        {
            if (!EditorApplication.isPlaying || _run == null) { EditorApplication.update -= Step; return; }
            if (EditorApplication.timeSinceStartup < _until) return;
            if (_untilFrame >= 0 && Time.frameCount < _untilFrame) return;
            _untilFrame = -1;
            try
            {
                if (!_run.MoveNext()) { _run = null; EditorApplication.update -= Step; Debug.Log("[FurnitureTour] done"); return; }
                if (_run.Current is string s && s == "frame") { _untilFrame = Time.frameCount + 1; _until = 0; }
                else _until = EditorApplication.timeSinceStartup + (_run.Current is int n ? n : 1) / 60.0;
            }
            catch (Exception e)
            {
                Debug.LogException(e);
                _run = null;
                EditorApplication.update -= Step;
                Debug.Log("[FurnitureTour] done (error)");
            }
        }

        static IEnumerator Tour(AppUI ui, string dir, string model)
        {
            Directory.CreateDirectory(dir);
            _pointer = new FurnitureEditor.ScriptedPointer();
            ui.Furniture.Scripted = _pointer;
            try
            {
                UiTour.Reset(ui);
                if (ui.Library.IsOpen) ui.Library.Close();
                GoToLiving(ui);
                yield return 100;
                var cam = Camera.main;
                var centre = new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
                Mouse(centre);
                yield return "frame";

                ui.Library.Open();
                yield return 40;
                foreach (var x in Shot(dir, "01-library")) yield return x;
                ui.Library.SelectCategory("seating");
                yield return 20;
                foreach (var x in Shot(dir, "02-seating")) yield return x;

                // ---- place a model with a click on the floor 2.8 m ahead
                var entry = FurnitureCatalog.Instance.Get(model);
                ui.Furniture.BeginPlace(entry, false);
                var feet = ui.S.Viewer.WalkFeet;
                var ahead = cam.transform.forward;
                ahead.y = 0f;
                var floor = feet + ahead.normalized * 2.8f;
                var at = (Vector2)cam.WorldToScreenPoint(floor);
                Mouse(at);
                yield return "frame";
                yield return 12;
                Log(ui, "placing");
                foreach (var x in Shot(dir, "03-placing")) yield return x;
                Mouse(at, left: true);
                yield return "frame";
                Mouse(at);
                yield return 30;
                Log(ui, "placed");
                foreach (var x in Shot(dir, "04-placed")) yield return x;

                // ---- turn it (R)
                ui.Furniture.Rotate(90f);
                yield return 30;
                Log(ui, "rotated");
                foreach (var x in Shot(dir, "05-rotated")) yield return x;

                // ---- drag it 260 px to the right
                var sel = ui.Furniture.Selected;
                if (sel?.Object != null)
                {
                    var c = sel.Object.transform.localToWorldMatrix.MultiplyPoint3x4(sel.Local.center);
                    var from = (Vector2)cam.WorldToScreenPoint(c);
                    Mouse(from);
                    yield return "frame";
                    Mouse(from, left: true);
                    yield return "frame";
                    for (int i = 1; i <= 10; i++)
                    {
                        Mouse(from + new Vector2(26f * i, -4f * i), left: true);
                        yield return "frame";
                    }
                    Log(ui, "dragging");
                    foreach (var x in Shot(dir, "06-dragging")) yield return x;
                    Mouse(from + new Vector2(260f, -40f));
                    yield return 30;
                    Log(ui, "moved");
                    foreach (var x in Shot(dir, "07-moved")) yield return x;
                }

                // ---- delete (⌫), then undo (⌘Z)
                ui.Furniture.DeleteSelected();
                yield return 30;
                Log(ui, "deleted");
                foreach (var x in Shot(dir, "08-deleted")) yield return x;
                ui.Undo();
                yield return 30;
                Log(ui, "undone");

                // ---- a picture aimed at the wall straight ahead
                ui.Furniture.BeginPlace(FurnitureCatalog.Instance.Get("painting_classic"), false);
                var eye = cam.transform.position;
                if (Physics.Raycast(new Ray(eye, ahead.normalized), out var hit, 30f, ~(1 << 2)))
                {
                    var wallAt = (Vector2)cam.WorldToScreenPoint(hit.point + Vector3.up * 0.1f);
                    Mouse(wallAt);
                    yield return "frame";
                    yield return 12;
                    Log(ui, "wall art over " + hit.collider.name);
                    foreach (var x in Shot(dir, "09-wall-art")) yield return x;
                }
                ui.Furniture.Escape();
                yield return 10;
                Log(ui, "escaped");
            }
            finally
            {
                ui.Furniture.Scripted = null;
                _pointer = null;
            }
        }

        static IEnumerable Shot(string dir, string name)
        {
            UiShot.Begin(Path.Combine(dir, name + ".png"));
            yield return "frame";
            UiShot.End();
        }

        static void Log(AppUI ui, string step)
        {
            var f = ui.Furniture;
            var doc = ui.S.Session.Doc;
            var sel = f.Selected;
            var it = sel != null ? doc.Items.Find(i => i.Id == sel.Id) : null;
            Debug.Log($"[FurnitureTour] {step}: state={f.Current} items={doc.Items.Count} selected={sel?.Id ?? "-"}" +
                      (it != null ? $" pos={it.Position} rot={it.Rotation} level={it.Level}" : "") +
                      $" target={(f.Target.Found ? f.Target.Position.ToString() : "none")} valid={f.Target.Valid} hint={f.Hint ?? "-"} undo={ui.S.Session.UndoCount} buildMs={ui.S.Session.LastBuildMs}");
        }

        static FurnitureEditor.ScriptedPointer _pointer;

        static void Mouse(Vector2 pos, bool left = false, bool right = false)
        {
            if (_pointer == null) return;
            _pointer.Position = pos;
            _pointer.Left = left;
            _pointer.Right = right;
        }

        static void GoToLiving(AppUI u)
        {
            foreach (var plan in u.Plans)
                foreach (var r in plan.Rooms)
                    if (r.Type == House4696.Model.RoomType.Living) { u.GoToRoom(plan, r); return; }
            if (u.Plans.Count > 0 && u.Plans[0].Rooms.Count > 0) u.GoToRoom(u.Plans[0], u.Plans[0].Rooms[0]);
        }
    }
}
