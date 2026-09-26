using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Vector floor plan of one level (walls, openings, rooms with names and areas) drawn with Painter2D, fitted to the
    /// element, north up. Shows the viewer's position and view direction; hovering highlights a room
    /// (<see cref="RoomHovered"/>), a click on a room (press and release on the same room) raises
    /// <see cref="RoomClicked"/>, and <see cref="Highlighted"/> lets a list highlight a room from outside.
    /// Colours come from USS custom properties (--plan-*, declared on .floor-plan) so the plan follows the theme.
    /// </summary>
    public sealed class FloorPlanView : VisualElement
    {
        /// <summary>
        /// How room labels are chosen. <see cref="Full"/>: the full name (plus the area where it fits).
        /// <see cref="Compact"/> (small panel): the full name, else the short name (text before « (», «-», «,»), else the
        /// type name — the first that fits its room; Micro text-3, no area line.
        /// </summary>
        public enum LabelMode { Full, Compact }

        static readonly CustomStyleProperty<Color> WallColor = new CustomStyleProperty<Color>("--plan-wall");
        static readonly CustomStyleProperty<Color> RoomColor = new CustomStyleProperty<Color>("--plan-room");
        static readonly CustomStyleProperty<Color> RoomHover = new CustomStyleProperty<Color>("--plan-room-hover");
        static readonly CustomStyleProperty<Color> RoomCurrent = new CustomStyleProperty<Color>("--plan-room-current");
        static readonly CustomStyleProperty<Color> WindowColor = new CustomStyleProperty<Color>("--plan-window");
        static readonly CustomStyleProperty<Color> MarkerColor = new CustomStyleProperty<Color>("--plan-marker");

        // UI Toolkit blends in linear space: 0.18 here reads as the spec's sRGB α 0.3 over --plan-room-current
        const float ConeAlpha = 0.18f;
        const float LabelInset = 3f;
        const float CanvasInset = 4f;          // the current room's label stays this far inside the canvas
        const float OpeningSnap = 0.05f;       // a wall end this close to an opening end is a jamb: never extended
        const float ProbeStep = 0.02f;         // how far past a wall end to look for the wall it joins
        const float ProbeSlack = 0.01f;        // a probe this close outside a wall still touches it
        const float WindowCentreMinPx = 6f;    // the window's centre line only where the wall is at least this thick
        static readonly char[] ShortCuts = { '(', '-', '–', '—', ',' };

        Color _wall = new Color32(0xA3, 0xA8, 0xB1, 0xFF), _room = new Color32(0x1F, 0x22, 0x28, 0xFF),
            _hover = new Color32(0x2A, 0x2E, 0x36, 0xFF), _current = new Color32(0x20, 0x26, 0x4D, 0xFF),
            _window = new Color32(0x93, 0xA2, 0xFF, 0xFF), _markerColor = new Color32(0x5A, 0x6A, 0xF7, 0xFF);

        struct WindowMark
        {
            public Vector2 A, B, N;     // centre-line ends and unit normal (plan metres)
            public float T;             // host wall thickness
        }

        PlanGeometry _plan;
        readonly VisualElement _labels, _marker;
        // hidden labels with the label styles: text sizes for the fit test (they live in the tree from the start, so
        // their style is resolved even for labels created a moment ago)
        readonly Label _measureName, _measureArea;
        readonly List<VisualElement> _roomLabels = new List<VisualElement>();
        readonly List<Label> _nameLabels = new List<Label>();
        readonly List<Label> _areaLabels = new List<Label>();
        readonly List<string[]> _candidates = new List<string[]>();     // label texts per room, preferred first
        readonly List<Vector2[]> _sizes = new List<Vector2[]>();        // measured size of each candidate
        readonly List<Vector2> _areaSizes = new List<Vector2>();
        bool _sizesValid;
        // free half-width / half-height (plan metres) around each room's label point: does the label fit?
        readonly List<float> _halfW = new List<float>(), _halfH = new List<float>();
        // drawing geometry derived from the plan once per plan: walls with filled joints, window symbols
        readonly List<Vector2[]> _wallQuads = new List<Vector2[]>();
        readonly List<WindowMark> _windows = new List<WindowMark>();
        PlanGeometry.Room _hovered, _highlighted, _currentRoom, _pressed;
        LabelMode _labelMode = LabelMode.Full;
        float _scale;
        Vector2 _origin;
        bool _hasViewer;
        Vector2 _viewerPos;
        float _viewerYaw;

        /// <summary>A room was clicked (left button pressed and released over the same room).</summary>
        public event Action<PlanGeometry.Room> RoomClicked;
        /// <summary>The room under the pointer changed (null = none).</summary>
        public event Action<PlanGeometry.Room> RoomHovered;
        /// <summary>The room the viewer stands in changed (null = none / outside).</summary>
        public event Action<PlanGeometry.Room> CurrentRoomChanged;
        /// <summary>The plan was fitted anew (size or plan changed): <see cref="PixelsPerMeter"/> is valid.</summary>
        public event Action LayoutChanged;

        public bool ShowLabels = true;
        /// <summary>Second label line with the room area (where it fits; <see cref="LabelMode.Full"/> only).</summary>
        public bool ShowAreas;
        public float Padding = 10f;
        /// <summary>Average label glyph advance in px — only a fallback for when text cannot be measured yet.</summary>
        public float LabelCharWidth = 6.4f;

        public FloorPlanView()
        {
            AddToClassList("floor-plan");
            generateVisualContent += DrawPlan;
            _labels = new VisualElement { pickingMode = PickingMode.Ignore };
            _labels.style.position = Position.Absolute;
            _labels.style.left = 0; _labels.style.top = 0; _labels.style.right = 0; _labels.style.bottom = 0;
            _marker = new VisualElement { pickingMode = PickingMode.Ignore };
            _marker.style.position = Position.Absolute;
            _marker.style.left = 0; _marker.style.top = 0; _marker.style.right = 0; _marker.style.bottom = 0;
            _marker.generateVisualContent += DrawMarker;
            _measureName = MeasureLabel("plan-label-name");
            _measureArea = MeasureLabel("plan-label-area");
            Add(_measureName);
            Add(_measureArea);
            Add(_labels);
            Add(_marker);
            // a font change (mode class, stage font size) changes the measurers' size: measure again
            _measureName.RegisterCallback<GeometryChangedEvent>(OnMeasureChanged);
            _measureArea.RegisterCallback<GeometryChangedEvent>(OnMeasureChanged);
            RegisterCallback<GeometryChangedEvent>(_ => Relayout());
            RegisterCallback<CustomStyleResolvedEvent>(OnStyle);
            RegisterCallback<PointerMoveEvent>(e => SetHovered(RoomAtLocal(e.localPosition)));
            RegisterCallback<PointerLeaveEvent>(_ => { SetHovered(null); _pressed = null; });
            RegisterCallback<PointerDownEvent>(e => { if (e.button == 0) _pressed = RoomAtLocal(e.localPosition); });
            RegisterCallback<PointerUpEvent>(e =>
            {
                if (e.button != 0) return;
                var pressed = _pressed;
                _pressed = null;
                var r = RoomAtLocal(e.localPosition);
                if (r != null && r == pressed) RoomClicked?.Invoke(r);
            });
        }

        static Label MeasureLabel(string cls)
        {
            var l = new Label("Кухня") { pickingMode = PickingMode.Ignore };
            l.AddToClassList(cls);
            l.style.position = Position.Absolute;
            l.style.left = 0;
            l.style.top = 0;
            l.style.visibility = Visibility.Hidden;
            return l;
        }

        /// <summary>Label style: <see cref="LabelMode.Full"/> (large plan) or <see cref="LabelMode.Compact"/> (small panel).</summary>
        public LabelMode Labels
        {
            get => _labelMode;
            set
            {
                if (_labelMode == value) return;
                _labelMode = value;
                EnableInClassList("plan-compact", value == LabelMode.Compact);
                RebuildCandidates();
                PlaceLabels();
            }
        }

        public PlanGeometry Plan
        {
            get => _plan;
            set
            {
                _plan = value;
                bool hadHover = _hovered != null;
                var oldCurrent = _currentRoom;
                _hovered = null;
                _highlighted = null;
                _pressed = null;
                _labels.Clear();
                _roomLabels.Clear();
                _nameLabels.Clear();
                _areaLabels.Clear();
                _halfW.Clear();
                _halfH.Clear();
                if (_plan != null)
                    foreach (var r in _plan.Rooms)
                    {
                        var name = new Label(RoomTitle(r)) { pickingMode = PickingMode.Ignore };
                        name.AddToClassList("plan-label-name");
                        var area = new Label(Ui.Area(r.Area)) { pickingMode = PickingMode.Ignore };
                        area.AddToClassList("plan-label-area");
                        var box = new VisualElement { pickingMode = PickingMode.Ignore };
                        box.AddToClassList("plan-label");
                        box.style.position = Position.Absolute;
                        box.style.translate = new Translate(Length.Percent(-50), Length.Percent(-50));
                        box.Add(name);
                        box.Add(area);
                        Ui.Show(box, false);            // shown by PlaceLabels once it is known to fit
                        _labels.Add(box);
                        _roomLabels.Add(box);
                        _nameLabels.Add(name);
                        _areaLabels.Add(area);
                        Spans(r.Outline, r.Label, out float hw, out float hh);
                        _halfW.Add(hw);
                        _halfH.Add(hh);
                    }
                RebuildCandidates();
                BuildGeometry();
                _currentRoom = _hasViewer && _plan != null ? _plan.RoomAt(_viewerPos) : null;
                EnableInClassList("over-room", false);
                if (hadHover) RoomHovered?.Invoke(null);
                if (oldCurrent != _currentRoom) CurrentRoomChanged?.Invoke(_currentRoom);
                Relayout();
                MarkDirtyRepaint();
                _marker.MarkDirtyRepaint();
            }
        }

        /// <summary>The viewer's plan position and yaw (degrees, 0 = +Z/north); null hides the marker.</summary>
        public void SetViewer(Vector2? pos, float yaw)
        {
            bool changed = pos.HasValue != _hasViewer || (pos.HasValue && ((pos.Value - _viewerPos).sqrMagnitude > 1e-4f || Mathf.Abs(Mathf.DeltaAngle(yaw, _viewerYaw)) > 0.5f));
            _hasViewer = pos.HasValue;
            if (pos.HasValue) { _viewerPos = pos.Value; _viewerYaw = yaw; }
            if (!changed) return;
            _marker.MarkDirtyRepaint();
            var room = _hasViewer && _plan != null ? _plan.RoomAt(_viewerPos) : null;
            if (room == _currentRoom) return;
            _currentRoom = room;
            UpdateLabelStates();
            PlaceLabels();                  // the current room's label is always on; the previous one may not fit
            MarkDirtyRepaint();
            CurrentRoomChanged?.Invoke(room);
        }

        /// <summary>The room the viewer stands in (null outside, or when the marker is hidden).</summary>
        public PlanGeometry.Room CurrentRoom => _currentRoom;
        /// <summary>The room under the pointer.</summary>
        public PlanGeometry.Room Hovered => _hovered;

        /// <summary>A room highlighted from outside (e.g. the room list under the pointer); drawn like hover.</summary>
        public PlanGeometry.Room Highlighted
        {
            get => _highlighted;
            set
            {
                if (_highlighted == value) return;
                _highlighted = value;
                UpdateLabelStates();
                MarkDirtyRepaint();
            }
        }

        /// <summary>Current fit: panel px per plan metre (0 before the first layout).</summary>
        public float PixelsPerMeter => _scale;
        /// <summary>The plan has walls or rooms to draw.</summary>
        public bool HasContent => _plan != null && (_plan.Rooms.Count > 0 || _plan.Walls.Count > 0);
        /// <summary>Plan point [x, z] in metres → element-local px.</summary>
        public Vector2 PlanToLocal(Vector2 plan) => _plan == null ? Vector2.zero : ToLocal(plan);

        /// <summary>The name to show for a room: its own name, or the type name when it has none.</summary>
        public static string RoomTitle(PlanGeometry.Room r)
        {
            if (r == null) return "";
            return string.IsNullOrWhiteSpace(r.Name) || r.Name == r.Id ? PlanGeometry.TypeName(r.Type) : r.Name;
        }

        /// <summary>«Кухня-столовая» → «Кухня», «Гостиная (второй свет)» → «Гостиная»; null when there is nothing to cut.</summary>
        public static string ShortTitle(string title)
        {
            if (string.IsNullOrEmpty(title)) return null;
            int cut = title.IndexOfAny(ShortCuts);
            if (cut <= 0) return null;
            string s = title.Substring(0, cut).Trim();
            return s.Length >= 2 && s != title ? s : null;
        }

        void OnStyle(CustomStyleResolvedEvent e)
        {
            var s = e.customStyle;
            if (s.TryGetValue(WallColor, out var c)) _wall = c;
            if (s.TryGetValue(RoomColor, out c)) _room = c;
            if (s.TryGetValue(RoomHover, out c)) _hover = c;
            if (s.TryGetValue(RoomCurrent, out c)) _current = c;
            if (s.TryGetValue(WindowColor, out c)) _window = c;
            if (s.TryGetValue(MarkerColor, out c)) _markerColor = c;
            MarkDirtyRepaint();
            _marker.MarkDirtyRepaint();
        }

        void OnMeasureChanged(GeometryChangedEvent e)
        {
            if (e.oldRect.size == e.newRect.size) return;
            _sizesValid = false;
            PlaceLabels();
        }

        void SetHovered(PlanGeometry.Room r)
        {
            if (r == _hovered) return;
            _hovered = r;
            EnableInClassList("over-room", r != null);
            UpdateLabelStates();
            MarkDirtyRepaint();
            RoomHovered?.Invoke(r);
        }

        void UpdateLabelStates()
        {
            if (_plan == null) return;
            int n = Mathf.Min(_roomLabels.Count, _plan.Rooms.Count);
            for (int i = 0; i < n; i++)
            {
                var room = _plan.Rooms[i];
                _roomLabels[i].EnableInClassList("plan-hover", room == _hovered || room == _highlighted);
                _roomLabels[i].EnableInClassList("plan-current", room == _currentRoom);
            }
        }

        void Relayout()
        {
            var r = contentRect;
            if (_plan == null || float.IsNaN(r.width) || float.IsNaN(r.height) || r.width <= 0f || r.height <= 0f)
            {
                // no fit yet: never hit-test or draw a new plan with the previous plan's scale and origin
                _scale = 0f;
                return;
            }
            var b = _plan.Bounds;
            float sx = (r.width - Padding * 2f) / Mathf.Max(b.width, 1f), sy = (r.height - Padding * 2f) / Mathf.Max(b.height, 1f);
            _scale = Mathf.Min(sx, sy);
            if (_scale <= 0f) { _scale = 0f; return; }
            _origin = new Vector2(r.x + (r.width - b.width * _scale) * 0.5f, r.y + (r.height - b.height * _scale) * 0.5f);
            PlaceLabels();
            MarkDirtyRepaint();
            _marker.MarkDirtyRepaint();
            LayoutChanged?.Invoke();
        }

        // ------------------------------------------------------------------ labels
        void RebuildCandidates()
        {
            _candidates.Clear();
            _sizesValid = false;
            if (_plan == null) return;
            var list = new List<string>(3);
            foreach (var r in _plan.Rooms)
            {
                list.Clear();
                string full = RoomTitle(r);
                list.Add(full);
                if (_labelMode == LabelMode.Compact)
                {
                    string shortTitle = ShortTitle(full);
                    if (shortTitle != null && !list.Contains(shortTitle)) list.Add(shortTitle);
                    string type = PlanGeometry.TypeName(r.Type);
                    if (!list.Contains(type)) list.Add(type);
                }
                _candidates.Add(list.ToArray());
            }
        }

        /// <summary>Measures every label candidate (once per plan / font); false when text cannot be measured yet.</summary>
        bool EnsureSizes()
        {
            if (_sizesValid) return true;
            if (_plan == null) return false;
            bool measurable = _measureName.panel != null;
            _sizes.Clear();
            _areaSizes.Clear();
            int n = Mathf.Min(_candidates.Count, _plan.Rooms.Count);
            for (int i = 0; i < n; i++)
            {
                var texts = _candidates[i];
                var sizes = new Vector2[texts.Length];
                for (int c = 0; c < texts.Length; c++) sizes[c] = Measure(_measureName, texts[c], measurable);
                _sizes.Add(sizes);
                _areaSizes.Add(Measure(_measureArea, _areaLabels.Count > i ? _areaLabels[i].text : "", measurable));
            }
            _sizesValid = measurable;
            return true;
        }

        Vector2 Measure(Label reference, string text, bool measurable)
        {
            if (measurable)
            {
                var size = reference.MeasureTextSize(text, 0, VisualElement.MeasureMode.Undefined, 0, VisualElement.MeasureMode.Undefined);
                if (size.x > 0f && size.y > 0f && !float.IsNaN(size.x) && !float.IsNaN(size.y))
                    return new Vector2(Mathf.Ceil(size.x), Mathf.Ceil(size.y));
            }
            return new Vector2(text.Length * LabelCharWidth, 14f);   // before the first style pass only
        }

        /// <summary>
        /// Which label each room shows and where: the first candidate that fits the room (measured text), none when
        /// nothing fits — except the room the viewer stands in, which always shows (accent) and stays inside the canvas.
        /// </summary>
        void PlaceLabels()
        {
            if (_plan == null || _scale <= 0f || !EnsureSizes()) return;
            var rect = contentRect;
            int n = Mathf.Min(Mathf.Min(_roomLabels.Count, _plan.Rooms.Count), _sizes.Count);
            for (int i = 0; i < n; i++)
            {
                var room = _plan.Rooms[i];
                var sizes = _sizes[i];
                float availW = (_halfW[i] * _scale - LabelInset) * 2f, availH = (_halfH[i] * _scale - LabelInset) * 2f;
                int pick = -1;
                if (ShowLabels)
                    for (int c = 0; c < sizes.Length; c++)
                        if (sizes[c].x <= availW && sizes[c].y <= availH) { pick = c; break; }
                bool current = room == _currentRoom;
                if (current && pick < 0 && ShowLabels && sizes.Length > 0)
                {
                    pick = 0;
                    for (int c = 1; c < sizes.Length; c++)
                        if (sizes[c].x < sizes[pick].x) pick = c;
                }
                var box = _roomLabels[i];
                if (pick < 0)
                {
                    Ui.Show(box, false);
                    continue;
                }
                var name = _nameLabels[i];
                string text = _candidates[i][pick];
                if (name.text != text) name.text = text;
                var nameSize = sizes[pick];
                var areaSize = _areaSizes[i];
                bool areaOn = _labelMode == LabelMode.Full && ShowAreas && pick == 0
                              && availW >= areaSize.x && availH >= nameSize.y + 1f + areaSize.y;
                Ui.Show(_areaLabels[i], areaOn);
                Ui.Show(box, true);

                var p = ToLocal(room.Label);
                if (current)
                {
                    // always legible: keep the whole label inside the canvas even where it overflows its room
                    float w = Mathf.Max(nameSize.x, areaOn ? areaSize.x : 0f), h = nameSize.y + (areaOn ? 1f + areaSize.y : 0f);
                    p.x = ClampCentre(p.x, w, rect.xMin, rect.xMax);
                    p.y = ClampCentre(p.y, h, rect.yMin, rect.yMax);
                }
                box.style.left = p.x;
                box.style.top = p.y;
            }
            UpdateLabelStates();
        }

        static float ClampCentre(float c, float size, float min, float max)
        {
            float lo = min + CanvasInset + size * 0.5f, hi = max - CanvasInset - size * 0.5f;
            return lo > hi ? (min + max) * 0.5f : Mathf.Clamp(c, lo, hi);
        }

        /// <summary>Distance from <paramref name="p"/> to the outline along the horizontal and the vertical (nearest side).</summary>
        static void Spans(List<Vector2> poly, Vector2 p, out float halfW, out float halfH)
        {
            float left = float.MaxValue, right = float.MaxValue, down = float.MaxValue, up = float.MaxValue;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                Vector2 a = poly[j], b = poly[i];
                if ((a.y > p.y) != (b.y > p.y))
                {
                    float x = a.x + (p.y - a.y) / (b.y - a.y) * (b.x - a.x);
                    if (x >= p.x) right = Mathf.Min(right, x - p.x);
                    else left = Mathf.Min(left, p.x - x);
                }
                if ((a.x > p.x) != (b.x > p.x))
                {
                    float y = a.y + (p.x - a.x) / (b.x - a.x) * (b.y - a.y);
                    if (y >= p.y) up = Mathf.Min(up, y - p.y);
                    else down = Mathf.Min(down, p.y - y);
                }
            }
            halfW = Mathf.Min(left, right);
            halfH = Mathf.Min(up, down);
            if (halfW == float.MaxValue) halfW = 0f;
            if (halfH == float.MaxValue) halfH = 0f;
        }

        // ------------------------------------------------------------------ wall geometry (once per plan)
        /// <summary>
        /// Walls with filled joints and the window symbols. <see cref="PlanGeometry"/> cuts each wall into quads that end
        /// square at the wall's end points, so two centre-aligned walls meeting in an L leave the outer corner square
        /// empty, and two outer-aligned exterior walls leave the square at an inner (reflex) corner empty. Each quad end
        /// that touches a crossing wall is extended to that wall's far face (<see cref="JointExtension"/>). Ends at an
        /// opening (jambs) and free ends are left alone, so nothing sticks out.
        /// </summary>
        void BuildGeometry()
        {
            _wallQuads.Clear();
            _windows.Clear();
            if (_plan == null) return;
            var walls = _plan.Walls;
            for (int i = 0; i < walls.Count; i++)
            {
                var q = walls[i];
                if (q == null || q.Length < 4) continue;
                Vector2 axis = q[1] - q[0];
                float len = axis.magnitude;
                if (len < 1e-4f || (q[3] - q[0]).sqrMagnitude < 1e-8f)
                {
                    _wallQuads.Add(Oriented(q[0], q[1], q[2], q[3]));
                    continue;
                }
                axis /= len;
                float e0 = JointExtension(i, q[0], q[3], -axis);
                float e1 = JointExtension(i, q[1], q[2], axis);
                _wallQuads.Add(Oriented(q[0] - axis * e0, q[1] + axis * e1, q[2] + axis * e1, q[3] - axis * e0));
            }
            foreach (var o in _plan.Openings)
            {
                if (o.Door) continue;
                Vector2 d = o.B - o.A;
                float len = d.magnitude;
                if (len < 1e-4f) continue;
                d /= len;
                _windows.Add(new WindowMark { A = o.A, B = o.B, N = new Vector2(-d.y, d.x), T = OpeningThickness(o.A, d) });
            }
        }

        /// <summary>
        /// How far to extend the wall end <paramref name="e0"/>–<paramref name="e1"/> (outward = unit direction past
        /// it): up to the far face of each crossing wall it touches, measured at the end's middle. That is half the
        /// other wall for a centre-aligned L, the rest of the wall for a T, the full thickness for the inner corner of
        /// two outer-aligned exterior walls, and 0 for a convex outer-aligned corner (the walls already overlap).
        /// </summary>
        float JointExtension(int self, Vector2 e0, Vector2 e1, Vector2 outward)
        {
            // a jamb: the wall stops exactly at its opening
            foreach (var o in _plan.Openings)
                if (SegmentDistance(o.A, e0, e1) < OpeningSnap || SegmentDistance(o.B, e0, e1) < OpeningSnap) return 0f;
            var walls = _plan.Walls;
            var mid = (e0 + e1) * 0.5f;
            float ext = 0f;
            for (int j = 0; j < walls.Count; j++)
            {
                if (j == self) continue;
                var w = walls[j];
                if (w == null || w.Length < 4) continue;
                Vector2 wd = w[1] - w[0];
                float wl = wd.magnitude;
                if (wl < 1e-4f) continue;
                wd /= wl;
                // a collinear continuation abuts edge to edge (one path, no seam): no corner to fill
                float across = Cross(wd, outward);
                if (Mathf.Abs(across) < 0.5f || !Touches(w, e0, e1, outward)) continue;
                // where the end's middle, moved along `outward`, crosses each face line of the other wall
                float sOuter = Cross(wd, w[0] - mid) / across, sInner = Cross(wd, w[3] - mid) / across;
                float far = Mathf.Min(Mathf.Max(sOuter, sInner), (w[3] - w[0]).magnitude + ProbeStep);
                ext = Mathf.Max(ext, far);
            }
            return ext;
        }

        /// <summary>The quad <paramref name="w"/> touches the wall end (corners included) just past it.</summary>
        static bool Touches(Vector2[] w, Vector2 e0, Vector2 e1, Vector2 outward)
        {
            for (int k = 0; k <= 4; k++)
                if (InQuad(w, Vector2.Lerp(e0, e1, k * 0.25f) + outward * ProbeStep, -ProbeSlack)) return true;
            return false;
        }

        /// <summary>
        /// The thickness of the wall an opening sits in (PlanGeometry.Opening does not carry it): the jamb quads of that
        /// wall end on its centre line exactly at the opening; the nearest parallel quad on the same centre line decides.
        /// A wall that is one opening end to end has no quad: 0.2 m then.
        /// </summary>
        float OpeningThickness(Vector2 a, Vector2 dir)
        {
            float best = -1f, bestD = float.MaxValue;
            foreach (var q in _plan.Walls)
            {
                if (q == null || q.Length < 4) continue;
                Vector2 qd = q[1] - q[0];
                float ql = qd.magnitude;
                if (ql < 1e-4f || Mathf.Abs(Cross(qd / ql, dir)) > 0.05f) continue;
                Vector2 m0 = (q[0] + q[3]) * 0.5f, m1 = (q[1] + q[2]) * 0.5f;        // on the wall's centre line
                if (Mathf.Abs(Cross(dir, a - m0)) > 0.02f) continue;                 // another wall line
                float d = SegmentDistance(a, m0, m1);
                if (d < bestD) { bestD = d; best = (q[3] - q[0]).magnitude; }
            }
            return best > 0f ? best : 0.2f;
        }

        static Vector2[] Oriented(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
        {
            // one winding for every quad: overlapping joints must add up under the non-zero rule, never cancel out
            float area2 = Cross(b - a, c - b) + Cross(d - c, a - d);
            return area2 >= 0f ? new[] { a, b, c, d } : new[] { d, c, b, a };
        }

        static float Cross(Vector2 a, Vector2 b) => a.x * b.y - a.y * b.x;

        static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b)
        {
            Vector2 ab = b - a;
            float t = Mathf.Clamp01(Vector2.Dot(p - a, ab) / Mathf.Max(ab.sqrMagnitude, 1e-8f));
            return (a + ab * t - p).magnitude;
        }

        /// <summary><paramref name="p"/> lies inside the convex quad, at least <paramref name="margin"/> from its edges.</summary>
        static bool InQuad(Vector2[] q, Vector2 p, float margin)
        {
            float orient = Cross(q[1] - q[0], q[2] - q[1]);
            if (Mathf.Abs(orient) < 1e-10f) return false;
            float sign = Mathf.Sign(orient);
            for (int k = 0; k < 4; k++)
            {
                Vector2 a = q[k], e = q[(k + 1) & 3] - a;
                float l = e.magnitude;
                if (l < 1e-6f) return false;
                if (sign * Cross(e, p - a) / l < margin) return false;
            }
            return true;
        }

        Vector2 ToLocal(Vector2 plan) => new Vector2(_origin.x + (plan.x - _plan.Bounds.xMin) * _scale, _origin.y + (_plan.Bounds.yMax - plan.y) * _scale);
        Vector2 ToPlan(Vector2 local) => new Vector2((local.x - _origin.x) / _scale + _plan.Bounds.xMin, _plan.Bounds.yMax - (local.y - _origin.y) / _scale);

        PlanGeometry.Room RoomAtLocal(Vector2 local) => _plan == null || _scale <= 0f ? null : _plan.RoomAt(ToPlan(local));

        // ------------------------------------------------------------------ drawing
        void DrawPlan(MeshGenerationContext ctx)
        {
            if (_plan == null || _scale <= 0f) return;
            var p = ctx.painter2D;
            foreach (var room in _plan.Rooms)
            {
                if (room.Outline == null || room.Outline.Count < 3) continue;
                p.fillColor = room == _hovered || room == _highlighted ? _hover : room == _currentRoom ? _current : _room;
                p.BeginPath();
                p.MoveTo(ToLocal(room.Outline[0]));
                for (int i = 1; i < room.Outline.Count; i++) p.LineTo(ToLocal(room.Outline[i]));
                p.ClosePath();
                p.Fill();
            }

            // windows: the wall body between the jambs reads as glass (room colour) under the lines
            if (_windows.Count > 0)
            {
                p.fillColor = _room;
                foreach (var w in _windows)
                {
                    var h = w.N * (w.T * 0.5f);
                    p.BeginPath();
                    p.MoveTo(ToLocal(w.A + h));
                    p.LineTo(ToLocal(w.B + h));
                    p.LineTo(ToLocal(w.B - h));
                    p.LineTo(ToLocal(w.A - h));
                    p.ClosePath();
                    p.Fill();
                }
            }

            // walls: one fill per piece (a single multi-subpath fill tessellates into stray diagonal triangles)
            if (_wallQuads.Count > 0)
            {
                p.fillColor = _wall;
                foreach (var q in _wallQuads)
                {
                    p.BeginPath();
                    p.MoveTo(ToLocal(q[0]));
                    p.LineTo(ToLocal(q[1]));
                    p.LineTo(ToLocal(q[2]));
                    p.LineTo(ToLocal(q[3]));
                    p.ClosePath();
                    p.Fill();
                }
            }

            // window symbol: 1 px lines on both wall faces (just inside the jambs' outline), a centre line where the
            // wall is thick enough on screen to keep three lines apart
            if (_windows.Count > 0)
            {
                p.strokeColor = _window;
                p.lineWidth = 1f;
                p.lineCap = LineCap.Butt;
                p.BeginPath();
                foreach (var w in _windows)
                {
                    Vector2 a = ToLocal(w.A), b = ToLocal(w.B);
                    var n = new Vector2(w.N.x, -w.N.y);         // plan → screen: y points down
                    float tpx = w.T * _scale;
                    float face = Mathf.Max(0f, tpx * 0.5f - 0.5f);
                    p.MoveTo(a + n * face);
                    p.LineTo(b + n * face);
                    p.MoveTo(a - n * face);
                    p.LineTo(b - n * face);
                    if (tpx >= WindowCentreMinPx)
                    {
                        p.MoveTo(a);
                        p.LineTo(b);
                    }
                }
                p.Stroke();
            }
        }

        void DrawMarker(MeshGenerationContext ctx)
        {
            if (!_hasViewer || _plan == null || _scale <= 0f) return;
            var p = ctx.painter2D;
            var c = ToLocal(_viewerPos);
            // view cone: a translucent wedge of the marker colour (no gradients in UI Toolkit)
            float yaw = _viewerYaw * Mathf.Deg2Rad, half = 35f * Mathf.Deg2Rad, reach = Mathf.Clamp(3.2f * _scale, 18f, 46f);
            Vector2 Dir(float a) => new Vector2(Mathf.Sin(a), -Mathf.Cos(a));
            var cone = _markerColor;
            p.fillColor = new Color(cone.r, cone.g, cone.b, ConeAlpha);
            p.BeginPath();
            p.MoveTo(c);
            p.LineTo(c + Dir(yaw - half) * reach);
            p.ArcTo(c + Dir(yaw) * reach * 1.08f, c + Dir(yaw + half) * reach, reach);
            p.LineTo(c + Dir(yaw + half) * reach);
            p.ClosePath();
            p.Fill();
            p.fillColor = Color.white;
            p.BeginPath();
            p.Arc(c, 6.5f, Angle.Degrees(0f), Angle.Degrees(360f));
            p.Fill();
            p.fillColor = cone;
            p.BeginPath();
            p.Arc(c, 4.5f, Angle.Degrees(0f), Angle.Degrees(360f));
            p.Fill();
        }
    }
}
