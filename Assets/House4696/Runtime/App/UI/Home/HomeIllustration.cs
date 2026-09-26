using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Empty-library illustration (spec §5, 96 px): a house on a plot with a dotted survey grid and the AI sparkle,
    /// drawn with Painter2D. Colours come from USS custom properties (--illo-*) so the sheet owns the palette.
    /// </summary>
    internal sealed class HomeIllustration : VisualElement
    {
        static readonly CustomStyleProperty<Color> PlotProp = new CustomStyleProperty<Color>("--illo-plot");
        static readonly CustomStyleProperty<Color> EdgeProp = new CustomStyleProperty<Color>("--illo-edge");
        static readonly CustomStyleProperty<Color> DotProp = new CustomStyleProperty<Color>("--illo-dot");
        static readonly CustomStyleProperty<Color> LineProp = new CustomStyleProperty<Color>("--illo-line");
        static readonly CustomStyleProperty<Color> AccentProp = new CustomStyleProperty<Color>("--illo-accent");
        static readonly CustomStyleProperty<Color> AiProp = new CustomStyleProperty<Color>("--illo-ai");

        Color _plot = new Color32(0x15, 0x17, 0x1B, 0xFF);
        Color _edge = new Color32(0x30, 0x33, 0x3A, 0xFF);
        Color _dot = new Color32(0x38, 0x3B, 0x43, 0xFF);
        Color _line = new Color32(0xA3, 0xA8, 0xB1, 0xFF);
        Color _accent = new Color32(0x93, 0xA2, 0xFF, 0xFF);
        Color _ai = new Color32(0xA7, 0x8B, 0xFA, 0xFF);

        public HomeIllustration()
        {
            AddToClassList("home-illo");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(OnStyles);
        }

        void OnStyles(CustomStyleResolvedEvent e)
        {
            var s = e.customStyle;
            if (s.TryGetValue(PlotProp, out var plot)) _plot = plot;
            if (s.TryGetValue(EdgeProp, out var edge)) _edge = edge;
            if (s.TryGetValue(DotProp, out var dot)) _dot = dot;
            if (s.TryGetValue(LineProp, out var line)) _line = line;
            if (s.TryGetValue(AccentProp, out var accent)) _accent = accent;
            if (s.TryGetValue(AiProp, out var ai)) _ai = ai;
            MarkDirtyRepaint();
        }

        void Draw(MeshGenerationContext ctx)
        {
            var r = contentRect;
            float s = Mathf.Min(r.width, r.height) / 96f;
            if (s <= 0f) return;
            var o = new Vector2(r.x + (r.width - 96f * s) * 0.5f, r.y + (r.height - 96f * s) * 0.5f);
            var p = ctx.painter2D;
            p.lineJoin = LineJoin.Round;
            p.lineCap = LineCap.Round;
            Vector2 P(float x, float y) => o + new Vector2(x, y) * s;

            void RoundRect(float x, float y, float w, float h, float rad)
            {
                p.BeginPath();
                p.MoveTo(P(x + rad, y));
                p.ArcTo(P(x + w, y), P(x + w, y + h), rad * s);
                p.ArcTo(P(x + w, y + h), P(x, y + h), rad * s);
                p.ArcTo(P(x, y + h), P(x, y), rad * s);
                p.ArcTo(P(x, y), P(x + w, y), rad * s);
                p.ClosePath();
            }
            void Poly(params float[] xy)
            {
                p.BeginPath();
                p.MoveTo(P(xy[0], xy[1]));
                for (int i = 2; i < xy.Length; i += 2) p.LineTo(P(xy[i], xy[i + 1]));
            }

            // plot
            p.fillColor = _plot;
            p.strokeColor = _edge;
            p.lineWidth = Mathf.Max(1f, 1f * s);
            RoundRect(6f, 6f, 84f, 84f, 14f);
            p.Fill();
            p.Stroke();

            // survey grid: dots every 10 px
            p.fillColor = _dot;
            for (int gy = 0; gy < 7; gy++)
            for (int gx = 0; gx < 7; gx++)
            {
                p.BeginPath();
                p.Arc(P(18f + gx * 10f, 18f + gy * 10f), 0.9f * s, Angle.Degrees(0f), Angle.Degrees(360f));
                p.ClosePath();
                p.Fill();
            }

            // house silhouette (filled with the plot colour so the grid stops at its outline)
            p.fillColor = _plot;
            Poly(30f, 72f, 30f, 49f, 48f, 32f, 66f, 49f, 66f, 72f);
            p.ClosePath();
            p.Fill();

            float stroke = Mathf.Max(1.2f, 2f * s);
            p.lineWidth = stroke;
            p.strokeColor = _line;
            // walls + roof
            Poly(30f, 72f, 30f, 49f);
            p.Stroke();
            Poly(66f, 49f, 66f, 72f);
            p.Stroke();
            Poly(25f, 53f, 48f, 31f, 71f, 53f);
            p.Stroke();
            // chimney
            Poly(58f, 39f, 58f, 33f, 62f, 33f, 62f, 43f);
            p.Stroke();
            // windows
            RoundRect(35f, 53f, 7f, 7f, 1.5f);
            p.Stroke();
            RoundRect(54f, 53f, 7f, 7f, 1.5f);
            p.Stroke();
            // ground
            Poly(20f, 72f, 76f, 72f);
            p.Stroke();

            // door (accent: the way in)
            p.strokeColor = _accent;
            Poly(44f, 72f, 44f, 60f, 52f, 60f, 52f, 72f);
            p.Stroke();

            // the AI sparkle
            p.fillColor = _ai;
            float cx = 74f, cy = 21f, a = 8f, k = 1.2f;
            p.BeginPath();
            p.MoveTo(P(cx, cy - a));
            p.QuadraticCurveTo(P(cx + k, cy - k), P(cx + a, cy));
            p.QuadraticCurveTo(P(cx + k, cy + k), P(cx, cy + a));
            p.QuadraticCurveTo(P(cx - k, cy + k), P(cx - a, cy));
            p.QuadraticCurveTo(P(cx - k, cy - k), P(cx, cy - a));
            p.ClosePath();
            p.Fill();
        }
    }
}
