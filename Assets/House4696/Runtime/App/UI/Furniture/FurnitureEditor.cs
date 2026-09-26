using System;
using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using Newtonsoft.Json.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

namespace House4696.App.UI
{
    /// <summary>
    /// Arranging furniture by hand while the library is open («Мебель», B). In the 3D view: hover shows what is under the
    /// pointer, a click selects, a drag moves the item over its floor (walls pull backs and sides flush, 5 cm grid, ⌥ = free),
    /// R / ⇧R turn it by 90° (the wheel by 15° while dragging), ⌫ deletes, ⌘D duplicates, the arrows nudge; right click opens
    /// the item's menu. A model from the library follows the pointer as a live preview until a click puts it down (⇧ keeps
    /// placing). Every change is one document edit through <see cref="HouseSession.ApplyItems"/>: undoable with ⌘Z, visible
    /// to the AI, rebuilt in milliseconds. The camera keeps its controls, except that the left button belongs to the items
    /// (the walk looks around with the right button while this mode is on).
    /// </summary>
    public sealed class FurnitureEditor
    {
        public enum State { Idle, Pressing, Dragging, Placing }

        const float DragThreshold = 5f;
        const float HoverInterval = 1f / 30f;
        const float WheelStep = 15f;
        const float NudgeStep = 0.05f, NudgeBig = 0.25f, NudgeFine = 0.01f;
        const int IgnoreRaycastLayer = 2;

        readonly AppUI _ui;
        readonly FurnitureScene _scene = new FurnitureScene();
        readonly SceneWriter _ghostWriter = new SceneWriter();

        public bool Active { get; private set; }
        public State Current { get; private set; }
        public ItemBox Hover { get; private set; }
        public ItemBox Selected { get; private set; }
        /// <summary>The model being placed (from the library or a duplicate), or null.</summary>
        public FurnitureCatalog.Entry Placing { get; private set; }
        /// <summary>Placing started by dragging a card out of the library: the model goes down where the button is released.</summary>
        public bool PlacingByDrag { get; private set; }
        /// <summary>Where the dragged item or the placed model would go now (while dragging / placing).</summary>
        public Placement Target { get; private set; }
        /// <summary>What the pointer should do or what is wrong with the spot (null = nothing to say).</summary>
        public string Hint { get; private set; }
        /// <summary>The preview of the model being placed (null while it is not shown).</summary>
        public GameObject Ghost => _ghost != null && _ghost.activeSelf ? _ghost : null;
        public ItemShape GhostShape => _ghostShape;
        /// <summary>Selection, mode or placing changed (the library and the overlay follow).</summary>
        public event Action Changed;
        /// <summary>Where the pointer is (screen px, origin at the bottom left): the hint follows it.</summary>
        public Vector2 PointerScreen { get; private set; }

        /// <summary>A pointer that tours and tests drive: while set, the editor reads it instead of the mouse.</summary>
        public sealed class ScriptedPointer
        {
            public Vector2 Position;
            public bool Left, Right;
            /// <summary>Wheel steps for the next frame (consumed once).</summary>
            public float Wheel;
            internal bool WasLeft, WasRight;
        }

        public ScriptedPointer Scripted { get; set; }

        /// <summary>The pointer as read this frame.</summary>
        struct Pointer
        {
            public Vector2 Position;
            public bool Left, LeftDown, Right, RightDown, Middle;
            public float Wheel;
        }

        FurnitureCatalog Catalog => FurnitureCatalog.Instance;
        HouseSession Session => _ui.S.Session;
        bool HasHouse => _ui.S?.Session != null && Session.HasProject && Session.Result?.Context != null;

        string _selectedId;
        float _nextHover;
        bool _emptyPress, _placePress, _rightPress;
        Vector2 _pressScreen, _rightScreen;
        Ray _pressRay;
        float _pressDistance;

        // dragging
        GameObject _dragObject;
        ItemShape _dragShape;
        Vector3 _dragStartPos, _grab;
        Quaternion _dragStartRot;
        float _dragRotation, _planeY;
        string _dragLevel;

        // placing
        GameObject _ghostRoot, _ghost;
        ItemShape _ghostShape;
        JObject _ghostParams;
        float _placeRotation;

        public FurnitureEditor(AppUI ui)
        {
            _ui = ui;
            var s = ui.S.Session;
            s.Rebuilt += OnHouseRebuilt;
            s.ItemsChanged += OnItemsChanged;
            s.ProjectChanged += OnProjectChanged;
        }

        // ------------------------------------------------------------------ mode
        public void SetActive(bool on)
        {
            if (Active == on) return;
            Active = on;
            if (on) _scene.Bind(Session.Result, Session.Doc);
            else
            {
                CancelPlacing();
                CancelDrag();
                Deselect(false);
                Hover = null;
                Hint = null;
                ReleaseInput();
            }
            Changed?.Invoke();
        }

        static void ReleaseInput()
        {
            ViewerInput.PointerTool = false;
            ViewerInput.LeftClaimed = false;
            ViewerInput.ArrowsClaimed = false;
            ViewerInput.WheelClaimed = false;
        }

        /// <summary>Esc: stop placing / dragging, then drop the selection; false when there was nothing to stop.</summary>
        public bool Escape()
        {
            if (!Active) return false;
            if (Current == State.Placing) { CancelPlacing(); return true; }
            if (Current == State.Dragging || Current == State.Pressing) { CancelDrag(); return true; }
            if (Selected != null) { Deselect(); return true; }
            return false;
        }

        // ------------------------------------------------------------------ frame
        /// <summary>Runs before the camera (the app UI's update): claims the left button, the wheel and the arrows it uses.</summary>
        public void Tick()
        {
            // the clean view (H) is for looking: the pointer goes back to the camera until the interface returns
            bool on = Active && HasHouse && !_ui.CleanView;
            bool pointer = ReadPointer(out var ptr);
            ViewerInput.PointerTool = on;
            ViewerInput.WheelClaimed = false;
            if (!pointer || !ptr.Left) ViewerInput.LeftClaimed = false;     // a claim lasts until release
            ViewerInput.ArrowsClaimed = on && Selected != null && Current == State.Idle;
            if (!on && _ghost != null && _ghost.activeSelf) _ghost.SetActive(false);
            if (!on || !pointer) return;
            var cam = Camera.main;
            if (cam == null) return;
            if (Selected != null && Selected.Object == null) Reselect();

            bool blocked = _ui.ModalOpen || _ui.HomeOpen || _ui.VeilVisible || (_ui.Plan != null && _ui.Plan.LargeOpen);
            if (blocked)
            {
                if (Current == State.Dragging || Current == State.Pressing) CancelDrag();
                if (_ghost != null && _ghost.activeSelf) _ghost.SetActive(false);
                SetHover(null);
                return;
            }
            var screen = ptr.Position;
            PointerScreen = screen;
            bool inside = screen.x >= 0f && screen.y >= 0f && screen.x <= Screen.width && screen.y <= Screen.height;
            bool overUi = !inside || _ui.PointerOverUI(screen) || _ui.PopoverOpen || _ui.PopoverClosedThisFrame;
            var ray = cam.ScreenPointToRay(screen);
            var kb = Keyboard.current;
            bool free = kb != null && (kb.leftAltKey.isPressed || kb.rightAltKey.isPressed);       // ⌥: no grid, no magnet
            bool shift = kb != null && (kb.leftShiftKey.isPressed || kb.rightShiftKey.isPressed);

            switch (Current)
            {
                case State.Placing: TickPlacing(ptr, ray, overUi, !free, shift); break;
                case State.Pressing:
                case State.Dragging: TickDrag(ptr, ray, screen, !free); break;
                default: TickIdle(ptr, ray, screen, overUi); break;
            }
            TickContextMenu(ptr, ray, screen, overUi);
        }

        bool ReadPointer(out Pointer p)
        {
            p = default;
            var s = Scripted;
            if (s != null)
            {
                p.Position = s.Position;
                p.Left = s.Left;
                p.Right = s.Right;
                p.LeftDown = s.Left && !s.WasLeft;
                p.RightDown = s.Right && !s.WasRight;
                p.Wheel = s.Wheel;
                s.WasLeft = s.Left;
                s.WasRight = s.Right;
                s.Wheel = 0f;
                return true;
            }
            var m = Mouse.current;
            if (m == null) return false;
            p.Position = m.position.ReadValue();
            p.Left = m.leftButton.isPressed;
            p.LeftDown = m.leftButton.wasPressedThisFrame;
            p.Right = m.rightButton.isPressed;
            p.RightDown = m.rightButton.wasPressedThisFrame;
            p.Middle = m.middleButton.isPressed;
            p.Wheel = m.scroll.ReadValue().y;
            return true;
        }

        void TickIdle(in Pointer mouse, Ray ray, Vector2 screen, bool overUi)
        {
            bool down = mouse.LeftDown;
            bool held = (mouse.Left && !down) || mouse.Right || mouse.Middle;
            if (overUi || held) SetHover(null);
            else if (down || Time.unscaledTime >= _nextHover)
            {
                _nextHover = Time.unscaledTime + HoverInterval;
                SetHover(_scene.Pick(ray, Session.Result?.Items, out _pressDistance));
            }
            Hint = null;

            if (down && !overUi)
            {
                if (Hover != null)
                {
                    ViewerInput.LeftClaimed = true;
                    Select(Hover);
                    _pressScreen = screen;
                    _pressRay = ray;
                    Current = State.Pressing;
                }
                else
                {
                    _emptyPress = true;
                    _pressScreen = screen;
                }
            }
            if (_emptyPress && !mouse.Left)
            {
                _emptyPress = false;
                // a click on empty space (not the end of a camera drag) drops the selection
                if ((screen - _pressScreen).sqrMagnitude < DragThreshold * DragThreshold) Deselect();
            }
        }

        void SetHover(ItemBox box)
        {
            if (Hover == box) return;
            Hover = box;
        }

        // ------------------------------------------------------------------ selection
        public void Select(ItemBox box)
        {
            if (box == null) { Deselect(); return; }
            if (Selected == box) return;
            Selected = box;
            _selectedId = box.Id;
            Changed?.Invoke();
        }

        public void Deselect() => Deselect(true);

        void Deselect(bool notify)
        {
            if (Selected == null && _selectedId == null) return;
            Selected = null;
            _selectedId = null;
            if (notify) Changed?.Invoke();
        }

        ItemBox FindBox(string id)
        {
            var items = Session.Result?.Items;
            if (items == null || id == null) return null;
            foreach (var b in items)
                if (b.Id == id && b.Object != null) return b;
            return null;
        }

        void Reselect()
        {
            var before = Selected;
            Selected = FindBox(_selectedId);
            if (Selected == null) _selectedId = null;
            Hover = null;
            if (before != Selected) Changed?.Invoke();
        }

        ItemDef DocItem(string id) => id == null ? null : Session.Doc?.Items.Find(i => i.Id == id);

        /// <summary>Russian name of a built item's model.</summary>
        public string NameOf(ItemBox b) => b == null ? "" : Catalog.Get(b.Model)?.Name ?? b.Model;

        public ItemShape ShapeOf(ItemBox b) => ItemShape.Of(Catalog.Get(b.Model), b.Local);

        /// <summary>The checks' messages about the selected item (in a doorway, over a window, overlapping…).</summary>
        public List<string> SelectedIssues()
        {
            var list = new List<string>();
            if (_selectedId == null || !HasHouse) return list;
            string path = "items/" + _selectedId;
            foreach (var i in Session.Issues)
                if (i.Path == path) list.Add(i.Message);
            return list;
        }

        // ------------------------------------------------------------------ dragging
        void TickDrag(in Pointer mouse, Ray ray, Vector2 screen, bool snap)
        {
            ViewerInput.LeftClaimed = true;
            if (Selected?.Object == null) { CancelDrag(); return; }
            if (Current == State.Pressing)
            {
                if (!mouse.Left) { Current = State.Idle; return; }        // a click: selected, nothing moved
                if ((screen - _pressScreen).sqrMagnitude < DragThreshold * DragThreshold) return;
                BeginDrag();
            }
            float wheel = mouse.Wheel;
            if (Mathf.Abs(wheel) > 0.01f)
            {
                ViewerInput.WheelClaimed = true;
                RotateDrag(Mathf.Sign(wheel) * WheelStep);
            }
            var t = DragTarget(ray, snap);
            if (t.Found)
            {
                Target = t;
                _dragObject.transform.SetPositionAndRotation(t.World, t.WorldRotation);
            }
            if (!mouse.Left) EndDrag();
        }

        void BeginDrag()
        {
            var box = Selected;
            _dragObject = box.Object;
            var tr = _dragObject.transform;
            _dragStartPos = tr.position;
            _dragStartRot = tr.rotation;
            var it = DocItem(box.Id);
            _dragRotation = it?.Rotation ?? 0f;
            _dragLevel = it?.Level;
            _dragShape = ShapeOf(box);
            // the item slides at its own height and the point grabbed stays under the pointer (the plane is at the grabbed
            // point's height, at most 1.2 m above the origin, so a tall body does not make the drag oversensitive)
            float grabbedY = _pressRay.GetPoint(Mathf.Min(_pressDistance, 200f)).y;
            _planeY = _dragShape.Mount == ItemMount.Ceiling
                ? Mathf.Clamp(grabbedY, _dragStartPos.y - 3f, _dragStartPos.y)
                : Mathf.Clamp(grabbedY, _dragStartPos.y, _dragStartPos.y + 1.2f);
            _grab = RayPlane(_pressRay, _planeY, out var p) ? new Vector3(_dragStartPos.x - p.x, 0f, _dragStartPos.z - p.z) : Vector3.zero;
            Target = new Placement { Found = true, World = _dragStartPos, Rotation = _dragRotation, Level = _dragLevel, Position = it?.Position ?? Vector3.zero };
            Current = State.Dragging;
            Changed?.Invoke();
        }

        Placement DragTarget(Ray ray, bool snap)
        {
            var s = _dragShape;
            Hint = null;
            if (s.Mount == ItemMount.Wall || s.OnSurfaces)
            {
                // pictures follow the walls, small things the surfaces under the pointer
                var p = _scene.FromRay(ray, s, _dragRotation, snap, _dragObject);
                if (p.Found) { Hint = p.Problem; return p; }
                Hint = p.Problem;
                return default;
            }
            if (!RayPlane(ray, _planeY, out var hit)) return default;
            var origin = new Vector3(hit.x + _grab.x, _dragStartPos.y, hit.z + _grab.z);
            // a ray nearly along the floor would throw the item to the horizon
            if ((origin - _dragStartPos).sqrMagnitude > 60f * 60f) return default;
            var t = _scene.Slide(origin, s, _dragRotation, snap, snap, _dragObject, _dragLevel);
            Hint = t.Problem;
            return t;
        }

        /// <summary>Turns the dragged item about its footprint centre (not its origin, which may be at its back).</summary>
        void RotateDrag(float deg)
        {
            if (_dragShape.Mount == ItemMount.Wall) return;
            float next = FurnitureGeometry.Normalize(_dragRotation + deg);
            var c = new Vector3(_dragShape.Local.center.x, 0f, _dragShape.Local.center.z);
            _grab += FurnitureGeometry.ItemRotation(_dragRotation) * c - FurnitureGeometry.ItemRotation(next) * c;
            _dragRotation = next;
        }

        void EndDrag()
        {
            var t = Target;
            var box = Selected;
            Current = State.Idle;
            Hint = null;
            ViewerInput.LeftClaimed = false;
            if (box == null || _dragObject == null) { Changed?.Invoke(); return; }
            var it = DocItem(box.Id);
            bool moved = it != null && t.Found && ((t.Position - it.Position).sqrMagnitude > 1e-6f
                                                   || Mathf.Abs(Mathf.DeltaAngle(t.Rotation, it.Rotation)) > 0.05f || t.Level != it.Level);
            if (!moved || !t.Valid)
            {
                Revert();
                if (moved && t.Problem != null) _ui.Toast(t.Problem + " — предмет вернулся на место", IconKind.Warning);
                Changed?.Invoke();
                return;
            }
            Commit(box.Id, d =>
            {
                d.Position = t.Position;
                d.Rotation = t.Rotation;
                d.Level = t.Level;
                d.Room = null;          // the level says where it stands; a room would go stale after a move
            });
            Changed?.Invoke();
        }

        void Revert()
        {
            if (_dragObject != null) _dragObject.transform.SetPositionAndRotation(_dragStartPos, _dragStartRot);
        }

        void CancelDrag()
        {
            if (Current != State.Dragging && Current != State.Pressing) return;
            if (Current == State.Dragging) Revert();
            Current = State.Idle;
            Hint = null;
            ViewerInput.LeftClaimed = false;
            Changed?.Invoke();
        }

        static bool RayPlane(Ray ray, float y, out Vector3 point)
        {
            point = default;
            if (Mathf.Abs(ray.direction.y) < 1e-4f) return false;
            float t = (y - ray.origin.y) / ray.direction.y;
            if (t <= 0f) return false;
            point = ray.GetPoint(t);
            return true;
        }

        // ------------------------------------------------------------------ placing
        /// <summary>
        /// Starts placing a model: a preview follows the pointer. <paramref name="byDrag"/>: dragged out of the library (goes
        /// down on release); else the next click in the view puts it down. Parameters and rotation come from a duplicated item.
        /// </summary>
        public void BeginPlace(FurnitureCatalog.Entry e, bool byDrag, JObject parameters = null, float? rotation = null)
        {
            if (e == null || !HasHouse) return;
            if (!Active) SetActive(true);
            CancelDrag();
            DestroyGhost();
            Placing = e;
            PlacingByDrag = byDrag;
            _ghostParams = parameters?.DeepClone() as JObject;
            _placeRotation = rotation ?? FacingCamera();
            _placePress = false;
            Target = default;
            Hint = null;
            Deselect(false);
            SetHover(null);
            BuildGhost();
            if (Placing == null) return;          // the model failed to build
            Current = State.Placing;
            Changed?.Invoke();
        }

        /// <summary>Default turn of a new model: its front towards the camera, on a 90° step.</summary>
        static float FacingCamera()
        {
            var cam = Camera.main;
            if (cam == null) return 0f;
            var back = -cam.transform.forward;
            back.y = 0f;
            if (back.sqrMagnitude < 1e-4f) return 0f;
            return FurnitureGeometry.Normalize(Mathf.Round(FurnitureGeometry.CompassOf(back) / 90f) * 90f);
        }

        public void CancelPlacing()
        {
            if (Current != State.Placing && Placing == null) return;
            DestroyGhost();
            Placing = null;
            PlacingByDrag = false;
            _placePress = false;
            Hint = null;
            if (Current == State.Placing) Current = State.Idle;
            ViewerInput.LeftClaimed = false;
            Changed?.Invoke();
        }

        void BuildGhost()
        {
            var c = Session.Result?.Context;
            if (c == null || Placing == null) return;
            if (_ghostRoot == null) _ghostRoot = new GameObject("FurniturePreview");
            var def = new ItemDef { Id = "preview", Model = Placing.Id, Params = _ghostParams };
            _ghost = HouseBuilder.BuildItemObject(c, def, _ghostRoot.transform, _ghostWriter);
            if (_ghost == null)
            {
                _ui.Toast("Не удалось загрузить модель «" + Placing.Name + "»", IconKind.Error, ToastKind.Error);
                Placing = null;
                return;
            }
            // Ignore Raycast: the preview is never under the pointer, never an obstacle, never walked into
            foreach (var t in _ghost.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = IgnoreRaycastLayer;
            FurnitureCatalog.Measure(Placing, _ghost);
            _ghostShape = ItemShape.Of(Placing, ItemBox.LocalBounds(_ghost));
            _ghost.SetActive(false);
        }

        void DestroyGhost()
        {
            if (_ghost == null) return;
            _ghostWriter.Release(_ghost);
            UnityEngine.Object.Destroy(_ghost);
            _ghost = null;
        }

        void TickPlacing(in Pointer mouse, Ray ray, bool overUi, bool snap, bool shift)
        {
            if (PlacingByDrag || _placePress) ViewerInput.LeftClaimed = mouse.Left;
            if (!overUi)
            {
                float wheel = mouse.Wheel;
                if (Mathf.Abs(wheel) > 0.01f)
                {
                    ViewerInput.WheelClaimed = true;
                    _placeRotation = FurnitureGeometry.Normalize(_placeRotation + Mathf.Sign(wheel) * WheelStep);
                }
            }
            bool show = !overUi && !ViewRenderer.Busy;
            if (show)
            {
                var p = _scene.FromRay(ray, _ghostShape, _placeRotation, snap, null);
                Target = p;
                Hint = p.Problem;
                if (p.Found) _placeRotation = p.Rotation;          // a wall pointed at turns the model; the turn stays
            }
            else Hint = null;
            if (_ghost != null)
            {
                bool visible = show && Target.Found;
                if (_ghost.activeSelf != visible) _ghost.SetActive(visible);
                if (visible) _ghost.transform.SetPositionAndRotation(Target.World, Target.WorldRotation);
            }

            if (PlacingByDrag)
            {
                if (mouse.Left) return;
                if (!overUi && Target.Valid) PlaceHere(false);
                else CancelPlacing();
                return;
            }
            if (mouse.LeftDown && !overUi)
            {
                _placePress = true;
                ViewerInput.LeftClaimed = true;
            }
            if (_placePress && !mouse.Left)
            {
                _placePress = false;
                if (!overUi && Target.Valid) PlaceHere(shift);
            }
        }

        void PlaceHere(bool keepPlacing)
        {
            var e = Placing;
            var t = Target;
            if (e == null || !t.Valid) return;
            string id = NewId(Session.Doc, e.Id);
            var next = HouseJson.Clone(Session.Doc);
            next.Items.Add(new ItemDef
            {
                Id = id, Model = e.Id, Level = t.Level, Position = t.Position, Rotation = t.Rotation,
                Params = _ghostParams?.DeepClone() as JObject,
            });
            if (!keepPlacing) CancelPlacing();
            if (!Apply(next, id)) return;
            if (keepPlacing) return;
            _selectedId = id;
            Selected = FindBox(id);
            Changed?.Invoke();
        }

        static string NewId(HouseDocument doc, string model)
        {
            var ids = new HashSet<string>();
            foreach (var i in doc.Items) if (i.Id != null) ids.Add(i.Id);
            for (int n = 1; ; n++)
            {
                string id = model + "_" + n;
                if (!ids.Contains(id)) return id;
            }
        }

        // ------------------------------------------------------------------ commands
        /// <summary>R / ⇧R, the ↻ ↺ buttons: turns the placed model, the dragged item or the selected one (about its centre).</summary>
        public void Rotate(float deg)
        {
            switch (Current)
            {
                case State.Placing:
                    _placeRotation = FurnitureGeometry.Normalize(_placeRotation + deg);
                    return;
                case State.Dragging:
                    RotateDrag(deg);
                    return;
                case State.Pressing:
                    return;
            }
            var box = Selected;
            var it = DocItem(box?.Id);
            if (box?.Object == null || it == null) return;
            var shape = ShapeOf(box);
            if (shape.Mount == ItemMount.Wall)
            {
                _ui.Toast("Предмет висит на стене — перетащите его на другую стену", IconKind.Info);
                return;
            }
            var c = new Vector3(box.Local.center.x, 0f, box.Local.center.z);
            var centre = box.Object.transform.position + FurnitureGeometry.ItemRotation(it.Rotation) * c;
            float rot = FurnitureGeometry.Normalize(it.Rotation + deg);
            var origin = centre - FurnitureGeometry.ItemRotation(rot) * c;
            // walls push the turned body out of them; if it does not fit at all, it stays as it was
            var t = _scene.Slide(origin, shape, rot, false, shape.Mount == ItemMount.Floor, box.Object, it.Level);
            if (!t.Valid)
            {
                _ui.Toast("Не помещается: " + (t.Problem ?? "мешает стена").ToLowerInvariant() + " — отодвиньте предмет", IconKind.Warning);
                return;
            }
            Commit(box.Id, d =>
            {
                d.Rotation = t.Rotation;
                d.Position = new Vector3(t.Position.x, d.Position.y, t.Position.z);
            });
        }

        public void DeleteSelected()
        {
            var box = Selected;
            if (box == null || Current != State.Idle) return;
            string id = box.Id, name = NameOf(box);
            var next = HouseJson.Clone(Session.Doc);
            if (next.Items.RemoveAll(i => i.Id == id) == 0) return;
            Deselect();
            if (Apply(next, id)) _ui.Toast("Удалено: " + name, IconKind.Trash, ToastKind.Info, "Вернуть", _ui.Undo);
        }

        /// <summary>⌘D: the same model with the same parameters and turn follows the pointer, ready to be put down.</summary>
        public void DuplicateSelected()
        {
            var box = Selected;
            var it = DocItem(box?.Id);
            var e = Catalog.Get(box?.Model);
            if (it == null || e == null || Current != State.Idle) return;
            BeginPlace(e, false, it.Params, it.Rotation);
        }

        /// <summary>Arrow keys: 5 cm (⇧ 25 cm, ⌥ 1 cm) along the axis closest to where the camera looks; wall pieces go up/down and along their wall.</summary>
        void Nudge(Vector2 dir, float step)
        {
            var box = Selected;
            var it = DocItem(box?.Id);
            var cam = Camera.main;
            if (box?.Object == null || it == null || cam == null) return;
            var shape = ShapeOf(box);
            Vector3 move;
            if (shape.Mount == ItemMount.Wall)
            {
                var along = Vector3.Cross(Vector3.up, FurnitureGeometry.Facing(it.Rotation));
                if (Vector3.Dot(along, cam.transform.right) < 0f) along = -along;
                move = along * dir.x * step + Vector3.up * dir.y * step;
            }
            else
            {
                var f = cam.transform.forward;
                f.y = 0f;
                var axis = Mathf.Abs(f.x) > Mathf.Abs(f.z) ? new Vector3(Mathf.Sign(f.x), 0f, 0f) : new Vector3(0f, 0f, Mathf.Sign(f.z));
                var right = new Vector3(axis.z, 0f, -axis.x);
                move = (axis * dir.y + right * dir.x) * step;
            }
            var p = it.Position + move;
            Commit(box.Id, d => d.Position = new Vector3(Mathf.Round(p.x * 1000f) / 1000f, Mathf.Round(p.y * 1000f) / 1000f, Mathf.Round(p.z * 1000f) / 1000f),
                "nudge:" + box.Id);
        }

        bool Commit(string id, Action<ItemDef> edit, string mergeKey = null)
        {
            var next = HouseJson.Clone(Session.Doc);
            var it = next.Items.Find(i => i.Id == id);
            if (it == null) return false;
            edit(it);
            return Apply(next, id, mergeKey);
        }

        bool Apply(HouseDocument next, string id, string mergeKey = null)
        {
            try
            {
                Session.ApplyItems(next, new[] { id }, mergeKey);
                return true;
            }
            catch (Exception e)
            {
                Debug.LogException(e);
                _ui.Toast("Не удалось изменить: " + e.Message, IconKind.Error, ToastKind.Error);
                return false;
            }
        }

        // ------------------------------------------------------------------ keys & context menu
        /// <summary>Viewer keys while the mode is on (R, ⌫, arrows); true when used.</summary>
        public bool OnKey(Keyboard kb, bool shift, bool alt)
        {
            if (!Active || !HasHouse) return false;
            bool Down(Key k) => kb[k].wasPressedThisFrame;
            if (Down(Key.R)) { Rotate(shift ? -90f : 90f); return true; }
            if (Current != State.Idle || Selected == null) return false;
            if (Down(Key.Delete) || Down(Key.Backspace)) { DeleteSelected(); return true; }
            float step = alt ? NudgeFine : shift ? NudgeBig : NudgeStep;
            if (Down(Key.UpArrow)) { Nudge(Vector2.up, step); return true; }
            if (Down(Key.DownArrow)) { Nudge(Vector2.down, step); return true; }
            if (Down(Key.LeftArrow)) { Nudge(Vector2.left, step); return true; }
            if (Down(Key.RightArrow)) { Nudge(Vector2.right, step); return true; }
            return false;
        }

        /// <summary>⌘ keys (⌘D); true when used.</summary>
        public bool OnCommandKey(Keyboard kb)
        {
            if (!Active || !HasHouse || Selected == null) return false;
            if (kb[Key.D].wasPressedThisFrame) { DuplicateSelected(); return true; }
            return false;
        }

        /// <summary>A right click on an item (without dragging the camera) selects it and opens its menu.</summary>
        void TickContextMenu(in Pointer mouse, Ray ray, Vector2 screen, bool overUi)
        {
            if (Current != State.Idle) { _rightPress = false; return; }
            if (mouse.RightDown && !overUi)
            {
                _rightPress = true;
                _rightScreen = screen;
            }
            if (!_rightPress || mouse.Right) return;
            _rightPress = false;
            if ((screen - _rightScreen).sqrMagnitude >= DragThreshold * DragThreshold || overUi) return;
            var box = _scene.Pick(ray, Session.Result?.Items, out _);
            if (box == null) return;
            Select(box);
            bool wall = ShapeOf(box).Mount == ItemMount.Wall;
            _ui.ShowMenuAt(_ui.PointerPanelPosition(), new List<MenuItem>
            {
                MenuItem.Title(NameOf(box)),
                new MenuItem { Label = "Повернуть по часовой", Icon = IconKind.RotateCw, Shortcut = "R", Disabled = wall, Action = () => Rotate(90f) },
                new MenuItem { Label = "Повернуть против часовой", Icon = IconKind.RotateCcw, Shortcut = "⇧R", Disabled = wall, Action = () => Rotate(-90f) },
                new MenuItem { Label = "Дублировать", Icon = IconKind.Duplicate, Shortcut = "⌘D", Action = DuplicateSelected },
                MenuItem.Sep(),
                new MenuItem { Label = "Удалить", Icon = IconKind.Trash, Shortcut = "⌫", Danger = true, Action = DeleteSelected },
            }, 240);
        }

        // ------------------------------------------------------------------ house events
        void OnHouseRebuilt()
        {
            _scene.Bind(Session.Result, Session.Doc);
            if (Current == State.Dragging || Current == State.Pressing)
            {
                // the dragged object was replaced by the rebuild (an AI edit): the drag ends where it is
                Current = State.Idle;
                Hint = null;
                ViewerInput.LeftClaimed = false;
            }
            if (Placing != null)
            {
                // the preview may use tinted materials of the old build: made again from the new one
                DestroyGhost();
                BuildGhost();
                if (Placing == null) { Current = State.Idle; Changed?.Invoke(); }
            }
            Reselect();
        }

        void OnItemsChanged()
        {
            _scene.Bind(Session.Result, Session.Doc);
            if ((Current == State.Dragging || Current == State.Pressing) && (_dragObject == null || Selected?.Object == null))
            {
                Current = State.Idle;
                Hint = null;
            }
            Reselect();
            Changed?.Invoke();
        }

        void OnProjectChanged()
        {
            CancelPlacing();
            CancelDrag();
            Deselect();
            Hover = null;
            if (Session.HasProject) _scene.Bind(Session.Result, Session.Doc);
        }
    }
}
