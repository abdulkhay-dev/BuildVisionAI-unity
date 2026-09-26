using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    public enum IconKind
    {
        House, Grid, Walk, Orbit, Fly, Sparkle, Sliders, Plus, Close, Trash, Pencil, Copy, Check, Search, Sun,
        Warning, Error, Info, ChevronDown, Folder, Eye, Expand,
        Plan, Pin, Camera, FrameCorners, Help, Undo, More, ChevronLeft, ChevronRight, ChevronUp,
        MouseLeft, MouseRight, MouseWheel, Keyboard, Sort, Layers, Refresh, Duplicate, Door, Stairs, Bed, Sofa, Bath, Kitchen,
        EyeOff, Maximize, ArrowUpRight,
        // furniture library: categories and item commands
        Table, Wardrobe, Lamp, Picture, Rug, SlatPanel, Leaf, Tree, Washer, RotateCw, RotateCcw, Move,
    }

    /// <summary>
    /// Crisp vector icon drawn with Painter2D on a 24×24 grid, scaled to the element; the colour follows the
    /// element's (inherited) text colour, so hover/selected styles recolour icons too.
    /// </summary>
    public sealed class Icon : VisualElement
    {
        IconKind _kind;
        Color _drawn;

        public Icon(IconKind kind)
        {
            _kind = kind;
            AddToClassList("icon");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            // hover/selected styles recolour the parent; generated content does not follow by itself
            schedule.Execute(() => { if (resolvedStyle.color != _drawn && ProgressRing.VisibleInHierarchy(this)) MarkDirtyRepaint(); }).Every(80);
        }

        public IconKind Kind
        {
            get => _kind;
            set { if (_kind == value) return; _kind = value; MarkDirtyRepaint(); }
        }

        void Draw(MeshGenerationContext ctx)
        {
            var r = contentRect;
            float s = Mathf.Min(r.width, r.height) / 24f;
            if (s <= 0f) return;
            var o = new Vector2(r.x + (r.width - 24f * s) * 0.5f, r.y + (r.height - 24f * s) * 0.5f);
            var p = ctx.painter2D;
            var c = _drawn = resolvedStyle.color;
            p.strokeColor = c;
            p.fillColor = c;
            p.lineWidth = Mathf.Max(1.1f, 1.6f * s);
            p.lineCap = LineCap.Round;
            p.lineJoin = LineJoin.Round;
            Vector2 P(float x, float y) => o + new Vector2(x, y) * s;

            void Line(params float[] xy)
            {
                p.BeginPath();
                p.MoveTo(P(xy[0], xy[1]));
                for (int i = 2; i < xy.Length; i += 2) p.LineTo(P(xy[i], xy[i + 1]));
                p.Stroke();
            }
            void Poly(bool fill, params float[] xy)
            {
                p.BeginPath();
                p.MoveTo(P(xy[0], xy[1]));
                for (int i = 2; i < xy.Length; i += 2) p.LineTo(P(xy[i], xy[i + 1]));
                p.ClosePath();
                if (fill) p.Fill(); else p.Stroke();
            }
            void Circle(float x, float y, float rad, bool fill = false)
            {
                p.BeginPath();
                p.Arc(P(x, y), rad * s, Angle.Degrees(0f), Angle.Degrees(360f));
                p.ClosePath();
                if (fill) p.Fill(); else p.Stroke();
            }
            void Arc(float x, float y, float rad, float a0, float a1)
            {
                p.BeginPath();
                p.Arc(P(x, y), rad * s, Angle.Degrees(a0), Angle.Degrees(a1));
                p.Stroke();
            }
            void Rect(float x, float y, float w, float h, float rad)
            {
                p.BeginPath();
                p.MoveTo(P(x + rad, y));
                p.ArcTo(P(x + w, y), P(x + w, y + h), rad * s);
                p.ArcTo(P(x + w, y + h), P(x, y + h), rad * s);
                p.ArcTo(P(x, y + h), P(x, y), rad * s);
                p.ArcTo(P(x, y), P(x + w, y), rad * s);
                p.ClosePath();
                p.Stroke();
            }

            switch (_kind)
            {
                case IconKind.House:
                    Line(3, 11, 12, 3.5f, 21, 11);
                    Line(5.5f, 9.5f, 5.5f, 20, 18.5f, 20, 18.5f, 9.5f);
                    Line(10, 20, 10, 14.5f, 14, 14.5f, 14, 20);
                    break;
                case IconKind.Grid:
                    Rect(3.5f, 3.5f, 7, 7, 1.5f); Rect(13.5f, 3.5f, 7, 7, 1.5f);
                    Rect(3.5f, 13.5f, 7, 7, 1.5f); Rect(13.5f, 13.5f, 7, 7, 1.5f);
                    break;
                case IconKind.Walk:
                    Circle(13, 4.5f, 2f, true);
                    Line(12.5f, 8, 11, 14, 8, 20.5f);
                    Line(11, 14, 14.5f, 16.5f, 15, 20.5f);
                    Line(7.5f, 12, 9.5f, 9, 12.5f, 8, 15, 10.5f, 17.5f, 11.5f);
                    break;
                case IconKind.Orbit:
                    Arc(12, 12, 8f, -60f, 220f);
                    Line(18.5f, 3.2f, 16, 5.1f, 18.4f, 7.5f);
                    Circle(12, 12, 2.4f, true);
                    break;
                case IconKind.Fly:
                    Poly(false, 3, 11, 21, 3.5f, 14.5f, 21, 11, 13);
                    Line(11, 13, 21, 3.5f);
                    break;
                case IconKind.Sparkle:
                    p.BeginPath();
                    p.MoveTo(P(12, 2.5f));
                    p.QuadraticCurveTo(P(13.2f, 10.8f), P(21.5f, 12));
                    p.QuadraticCurveTo(P(13.2f, 13.2f), P(12, 21.5f));
                    p.QuadraticCurveTo(P(10.8f, 13.2f), P(2.5f, 12));
                    p.QuadraticCurveTo(P(10.8f, 10.8f), P(12, 2.5f));
                    p.ClosePath();
                    p.Fill();
                    break;
                case IconKind.Sliders:
                    Line(4, 7, 20, 7); Line(4, 17, 20, 17);
                    Circle(9, 7, 2.4f, true); Circle(15, 17, 2.4f, true);
                    break;
                case IconKind.Plus:
                    Line(12, 5, 12, 19); Line(5, 12, 19, 12);
                    break;
                case IconKind.Close:
                    Line(6, 6, 18, 18); Line(18, 6, 6, 18);
                    break;
                case IconKind.Trash:
                    Line(4, 6.5f, 20, 6.5f);
                    Line(9.5f, 6.5f, 9.5f, 4, 14.5f, 4, 14.5f, 6.5f);
                    Line(6, 6.5f, 7, 20, 17, 20, 18, 6.5f);
                    Line(10.2f, 10.5f, 10.4f, 16.5f); Line(13.8f, 10.5f, 13.6f, 16.5f);
                    break;
                case IconKind.Pencil:
                    Poly(false, 15.5f, 4.5f, 19.5f, 8.5f, 8.5f, 19.5f, 4, 20, 4.5f, 15.5f);
                    Line(13, 7, 17, 11);
                    break;
                case IconKind.Copy:
                    Rect(8.5f, 8.5f, 11.5f, 11.5f, 2f);
                    Line(15.5f, 5.5f, 15.5f, 5, 14, 4, 5.5f, 4, 4, 5.5f, 4, 14, 5, 15.5f, 5.5f, 15.5f);
                    break;
                case IconKind.Check:
                    Line(5, 12.5f, 10, 17.5f, 19.5f, 7);
                    break;
                case IconKind.Search:
                    Circle(10.5f, 10.5f, 6f);
                    Line(15, 15, 20, 20);
                    break;
                case IconKind.Sun:
                    Circle(12, 12, 4f);
                    for (int i = 0; i < 8; i++)
                    {
                        float a = i * Mathf.PI / 4f;
                        var d = new Vector2(Mathf.Cos(a), Mathf.Sin(a));
                        Line(12 + d.x * 7f, 12 + d.y * 7f, 12 + d.x * 9.3f, 12 + d.y * 9.3f);
                    }
                    break;
                case IconKind.Warning:
                    Poly(false, 12, 3.5f, 21.5f, 20, 2.5f, 20);
                    Line(12, 9.5f, 12, 14);
                    Circle(12, 17, 0.9f, true);
                    break;
                case IconKind.Error:
                    Circle(12, 12, 9f);
                    Line(12, 7.5f, 12, 13);
                    Circle(12, 16.3f, 0.9f, true);
                    break;
                case IconKind.Info:
                    Circle(12, 12, 9f);
                    Line(12, 11, 12, 16.5f);
                    Circle(12, 7.8f, 0.9f, true);
                    break;
                case IconKind.ChevronDown:
                    Line(6, 9, 12, 15, 18, 9);
                    break;
                case IconKind.Folder:
                    Line(3.5f, 18.5f, 3.5f, 6, 9.5f, 6, 11.5f, 8.5f, 20.5f, 8.5f, 20.5f, 18.5f, 3.5f, 18.5f);
                    break;
                case IconKind.Eye:
                    p.BeginPath();
                    p.MoveTo(P(2.5f, 12));
                    p.QuadraticCurveTo(P(12, 2.5f), P(21.5f, 12));
                    p.QuadraticCurveTo(P(12, 21.5f), P(2.5f, 12));
                    p.ClosePath();
                    p.Stroke();
                    Circle(12, 12, 3f);
                    break;
                case IconKind.Plan:
                    Rect(3.5f, 3.5f, 17, 17, 2f);
                    Line(12, 3.5f, 12, 11, 20.5f, 11);
                    Line(3.5f, 14, 8, 14);
                    Line(12, 15, 12, 20.5f);
                    break;
                case IconKind.Pin:
                    p.BeginPath();
                    p.MoveTo(P(12, 21));
                    p.BezierCurveTo(P(12, 21), P(5, 14.5f), P(5, 9.5f));
                    p.Arc(P(12, 9.5f), 7f * s, Angle.Degrees(180f), Angle.Degrees(360f));
                    p.BezierCurveTo(P(19, 14.5f), P(12, 21), P(12, 21));
                    p.Stroke();
                    Circle(12, 9.5f, 2.5f);
                    break;
                case IconKind.Camera:
                    Line(3.5f, 18.5f, 3.5f, 8.5f, 7.5f, 8.5f, 9, 5.5f, 15, 5.5f, 16.5f, 8.5f, 20.5f, 8.5f, 20.5f, 18.5f, 3.5f, 18.5f);
                    Circle(12, 13, 3.5f);
                    break;
                case IconKind.FrameCorners:
                    Line(4, 9, 4, 4, 9, 4); Line(15, 4, 20, 4, 20, 9);
                    Line(20, 15, 20, 20, 15, 20); Line(9, 20, 4, 20, 4, 15);
                    Rect(8.5f, 8.5f, 7, 7, 1.5f);
                    break;
                case IconKind.Help:
                    Circle(12, 12, 9f);
                    p.BeginPath();
                    p.MoveTo(P(9.3f, 9.6f));
                    p.BezierCurveTo(P(9.3f, 6.2f), P(14.8f, 6.2f), P(14.8f, 9.4f));
                    p.BezierCurveTo(P(14.8f, 11.6f), P(12, 11.6f), P(12, 14f));
                    p.Stroke();
                    Circle(12, 17.2f, 0.9f, true);
                    break;
                case IconKind.Undo:
                    Line(8, 5, 4, 9, 8, 13);
                    p.BeginPath();
                    p.MoveTo(P(4, 9));
                    p.LineTo(P(14, 9));
                    p.BezierCurveTo(P(22, 9), P(22, 19), P(14, 19));
                    p.LineTo(P(9, 19));
                    p.Stroke();
                    break;
                case IconKind.Refresh:
                    Arc(12, 12, 7.5f, -30f, 250f);
                    Line(19.8f, 4.6f, 19.2f, 8.4f, 15.4f, 8.2f);
                    break;
                case IconKind.More:
                    Circle(6, 12, 1.4f, true); Circle(12, 12, 1.4f, true); Circle(18, 12, 1.4f, true);
                    break;
                case IconKind.ChevronLeft: Line(15, 6, 9, 12, 15, 18); break;
                case IconKind.ChevronRight: Line(9, 6, 15, 12, 9, 18); break;
                case IconKind.ChevronUp: Line(6, 15, 12, 9, 18, 15); break;
                case IconKind.MouseLeft:
                case IconKind.MouseRight:
                case IconKind.MouseWheel:
                {
                    Rect(6.5f, 3.5f, 11, 17, 5.5f);
                    if (_kind == IconKind.MouseWheel)
                    {
                        // wheel: a filled capsule in the middle of the top half
                        p.BeginPath();
                        p.MoveTo(P(12, 6.2f));
                        p.ArcTo(P(13.2f, 6.2f), P(13.2f, 7.4f), 1.2f * s);
                        p.LineTo(P(13.2f, 9.8f));
                        p.ArcTo(P(13.2f, 11f), P(12f, 11f), 1.2f * s);
                        p.ArcTo(P(10.8f, 11f), P(10.8f, 9.8f), 1.2f * s);
                        p.LineTo(P(10.8f, 7.4f));
                        p.ArcTo(P(10.8f, 6.2f), P(12f, 6.2f), 1.2f * s);
                        p.ClosePath();
                        p.Fill();
                        break;
                    }
                    Line(6.5f, 11, 17.5f, 11);
                    Line(12, 3.5f, 12, 11);
                    // the pressed button: its whole quadrant filled, following the rounded corner
                    p.BeginPath();
                    if (_kind == IconKind.MouseLeft)
                    {
                        p.MoveTo(P(12, 3.5f));
                        p.LineTo(P(12, 11));
                        p.LineTo(P(6.5f, 11));
                        p.LineTo(P(6.5f, 9));
                        p.ArcTo(P(6.5f, 3.5f), P(12, 3.5f), 5.5f * s);
                    }
                    else
                    {
                        p.MoveTo(P(12, 3.5f));
                        p.LineTo(P(12, 11));
                        p.LineTo(P(17.5f, 11));
                        p.LineTo(P(17.5f, 9));
                        p.ArcTo(P(17.5f, 3.5f), P(12, 3.5f), 5.5f * s);
                    }
                    p.ClosePath();
                    p.Fill();
                    break;
                }
                case IconKind.Keyboard:
                    Rect(2.5f, 6, 19, 12, 2f);
                    Line(6, 10, 6.01f, 10); Line(9.5f, 10, 9.51f, 10); Line(13, 10, 13.01f, 10); Line(16.5f, 10, 16.51f, 10);
                    Line(8, 14.5f, 16, 14.5f);
                    break;
                case IconKind.Sort:
                    Line(7, 4, 7, 20); Line(3.5f, 16.5f, 7, 20, 10.5f, 16.5f);
                    Line(17, 20, 17, 4); Line(13.5f, 7.5f, 17, 4, 20.5f, 7.5f);
                    break;
                case IconKind.Layers:
                    Poly(false, 12, 3.5f, 21, 8.5f, 12, 13.5f, 3, 8.5f);
                    Line(3, 12.5f, 12, 17.5f, 21, 12.5f);
                    Line(3, 16.5f, 12, 21.5f, 21, 16.5f);
                    break;
                case IconKind.Duplicate:
                    Rect(8.5f, 8.5f, 11.5f, 11.5f, 2f);
                    Rect(4, 4, 11.5f, 11.5f, 2f);
                    break;
                case IconKind.Door:
                    Line(5, 20.5f, 19, 20.5f);
                    Line(7, 20.5f, 7, 3.5f, 17, 3.5f, 17, 20.5f);
                    Circle(14, 12.5f, 0.9f, true);
                    break;
                case IconKind.Stairs:
                    Line(3.5f, 19.5f, 8, 19.5f, 8, 15, 12.5f, 15, 12.5f, 10.5f, 17, 10.5f, 17, 6, 20.5f, 6);
                    break;
                case IconKind.Bed:
                    Line(3.5f, 19, 3.5f, 6);
                    Line(3.5f, 15, 20.5f, 15, 20.5f, 19);
                    Line(3.5f, 11.5f, 17, 11.5f, 20.5f, 13.5f, 20.5f, 15);
                    Rect(6, 8.5f, 4.5f, 3, 1f);
                    break;
                case IconKind.Sofa:
                    Line(5, 12, 5, 8.5f, 19, 8.5f, 19, 12);
                    Rect(2.5f, 11, 19, 6.5f, 2f);
                    Line(5, 17.5f, 5, 19.5f); Line(19, 17.5f, 19, 19.5f);
                    break;
                case IconKind.Bath:
                    Line(3, 12, 21, 12);
                    Line(4.5f, 12, 5.5f, 17.5f, 18.5f, 17.5f, 19.5f, 12);
                    Line(7, 12, 7, 5.5f, 10, 5.5f);
                    Line(7.5f, 17.5f, 6.5f, 20); Line(16.5f, 17.5f, 17.5f, 20);
                    break;
                case IconKind.Kitchen:
                    Rect(4, 3.5f, 16, 17, 2f);
                    Line(4, 9, 20, 9);
                    Line(8, 6.2f, 10, 6.2f); Line(8, 13, 8, 15.5f);
                    break;
                case IconKind.EyeOff:
                    p.BeginPath();
                    p.MoveTo(P(2.5f, 12));
                    p.QuadraticCurveTo(P(12, 2.5f), P(21.5f, 12));
                    p.QuadraticCurveTo(P(12, 21.5f), P(2.5f, 12));
                    p.ClosePath();
                    p.Stroke();
                    Circle(12, 12, 3f);
                    Line(4, 4, 20, 20);
                    break;
                case IconKind.Maximize:
                    Line(14, 4, 20, 4, 20, 10); Line(20, 4, 13, 11);
                    Line(10, 20, 4, 20, 4, 14); Line(4, 20, 11, 13);
                    break;
                case IconKind.ArrowUpRight:
                    Line(7, 17, 17, 7);
                    Line(9, 7, 17, 7, 17, 15);
                    break;
                case IconKind.Expand:
                    Line(4, 9, 4, 4, 9, 4); Line(15, 4, 20, 4, 20, 9);
                    Line(20, 15, 20, 20, 15, 20); Line(9, 20, 4, 20, 4, 15);
                    break;
                case IconKind.Table:            // top and two legs, seen from the front
                    Rect(2.5f, 6.5f, 19, 3.5f, 1f);
                    Line(5.5f, 10, 5.5f, 19.5f); Line(18.5f, 10, 18.5f, 19.5f);
                    break;
                case IconKind.Wardrobe:         // two doors with handles on short feet
                    Rect(5, 3, 14, 16.5f, 1.5f);
                    Line(12, 3, 12, 19.5f);
                    Line(10, 10, 10, 12.5f); Line(14, 10, 14, 12.5f);
                    Line(7, 19.5f, 7, 21.5f); Line(17, 19.5f, 17, 21.5f);
                    break;
                case IconKind.Lamp:             // shade, stem, foot
                    Poly(false, 8.5f, 3.5f, 15.5f, 3.5f, 19, 11, 5, 11);
                    Line(12, 11, 12, 19.5f);
                    Line(8, 20, 16, 20);
                    break;
                case IconKind.Picture:          // frame with hills and a sun
                    Rect(3.5f, 4.5f, 17, 15, 2f);
                    Line(6.5f, 16.5f, 10.5f, 12, 13.5f, 15, 15.5f, 13, 17.5f, 16.5f);
                    Circle(15.5f, 8.8f, 1.4f);
                    break;
                case IconKind.Rug:              // a rug with fringes at both ends
                    Rect(6, 4.5f, 12, 15, 1f);
                    Rect(9, 8, 6, 8, 0.5f);
                    for (int i = 0; i < 4; i++)
                    {
                        float x = 7.5f + i * 3f;
                        Line(x, 2.2f, x, 4.5f); Line(x, 19.5f, x, 21.8f);
                    }
                    break;
                case IconKind.SlatPanel:        // wall panel of vertical slats
                    Rect(3.5f, 3.5f, 17, 17, 2f);
                    Line(8, 3.5f, 8, 20.5f); Line(12, 3.5f, 12, 20.5f); Line(16, 3.5f, 16, 20.5f);
                    break;
                case IconKind.Leaf:
                    p.BeginPath();
                    p.MoveTo(P(5, 19));
                    p.BezierCurveTo(P(4, 10), P(10, 4), P(20, 4));
                    p.BezierCurveTo(P(20, 14), P(14, 20), P(5, 19));
                    p.ClosePath();
                    p.Stroke();
                    Line(5, 19, 13.5f, 10.5f);
                    break;
                case IconKind.Tree:             // round crown on a trunk
                    Circle(12, 9, 6.2f);
                    Line(12, 15.2f, 12, 21);
                    Line(12, 17.5f, 14.5f, 15.5f);
                    break;
                case IconKind.Washer:           // washing machine
                    Rect(4.5f, 3, 15, 18, 2f);
                    Line(4.5f, 7, 19.5f, 7);
                    Circle(12, 14, 4f);
                    Circle(7.8f, 5, 0.8f, true);
                    break;
                case IconKind.RotateCcw:        // ↺: three quarters of a circle, arrow at the top left
                    p.BeginPath();
                    p.Arc(P(12, 12), 8.5f * s, Angle.Degrees(180f), Angle.Degrees(-135f), ArcDirection.CounterClockwise);
                    p.LineTo(P(3.5f, 8.5f));
                    p.Stroke();
                    Line(3.5f, 3.5f, 3.5f, 8.5f, 8.5f, 8.5f);
                    break;
                case IconKind.RotateCw:         // ↻: the mirror image
                    p.BeginPath();
                    p.Arc(P(12, 12), 8.5f * s, Angle.Degrees(0f), Angle.Degrees(315f), ArcDirection.Clockwise);
                    p.LineTo(P(20.5f, 8.5f));
                    p.Stroke();
                    Line(20.5f, 3.5f, 20.5f, 8.5f, 15.5f, 8.5f);
                    break;
                case IconKind.Move:             // four-way arrow
                    Line(12, 3, 12, 21); Line(3, 12, 21, 12);
                    Line(9.5f, 5.5f, 12, 3, 14.5f, 5.5f); Line(9.5f, 18.5f, 12, 21, 14.5f, 18.5f);
                    Line(5.5f, 9.5f, 3, 12, 5.5f, 14.5f); Line(18.5f, 9.5f, 21, 12, 18.5f, 14.5f);
                    break;
            }
        }
    }
}
