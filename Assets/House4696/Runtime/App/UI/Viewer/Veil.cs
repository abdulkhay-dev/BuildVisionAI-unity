using System;
using System.IO;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.App.UI
{
    /// <summary>
    /// Full-window veil (spec §3.7) for the app start, opening/creating a project and its first lighting bake: the
    /// project's preview (a soft-focus copy, tinted) or a plot-grid illustration, the name, «Расчёт освещения · 53 %» with a bar,
    /// «Смотреть сейчас» after 1.5 s (↩ / Esc) and «Все проекты» top-left. Leaves with a 400 ms fade when the light is
    /// ready or the user skips. The startup variant runs before the services exist (<c>ui.S</c> is null until Bind).
    /// </summary>
    public sealed class Veil
    {
        enum Phase { Hidden, Startup, Opening, Waiting }

        const float SkipAfter = 1.5f, LoopSeconds = 1.1f, SegmentShare = 0.3f;
        const long OutMs = 420;                     // 400 ms fade + a frame
        const string DefaultName = "House";
        /// <summary>Soft-focus copy of the 640×400 preview: two bilinear halvings (320×200, then 160×100).</summary>
        const int SoftW1 = 320, SoftH1 = 200, SoftW2 = 160, SoftH2 = 100;

        static readonly string[] PctText = new string[101];

        readonly AppUI _ui;
        readonly VisualElement _image, _mark, _bar, _fill, _seg, _skip, _home;
        readonly VeilGrid _grid;
        readonly Label _name, _status, _pct;

        Phase _phase;
        Texture2D _ownTexture;                      // the startup preview read from disk (ours to destroy)
        RenderTexture _soft1, _soft2;               // soft-focus copy of the preview (released when the veil hides)
        Texture _softSource;                        // the preview the copy was made from
        string _projectId;
        bool _fromStartup, _homeRequested, _indeterminate, _skipOn, _subscribed;
        float _shownProgress, _loopT, _waitingSince;
        int _pctShown = -1;
        IVisualElementScheduledItem _hideDone;

        public VisualElement Element { get; }
        public bool Visible { get; private set; }

        public Veil(AppUI ui)
        {
            _ui = ui;
            Element = Ui.El("layer veil-root");

            _image = Ui.El("veil-image");
            _image.pickingMode = PickingMode.Ignore;
            _grid = new VeilGrid();

            _mark = Ui.El("veil-mark", Ui.Icon(IconKind.House, 24));
            _name = Ui.Text(DefaultName, "veil-name");
            _status = Ui.Text("", "veil-status");
            _pct = Ui.Text("", "veil-pct");
            var statusRow = Ui.El("veil-status-row", _status, _pct);
            _fill = Ui.El("veil-fill");
            _seg = Ui.El("veil-seg");
            _seg.usageHints = UsageHints.DynamicTransform;
            _fill.usageHints = UsageHints.DynamicTransform;
            _bar = Ui.El("veil-bar", _fill, _seg);

            _skip = Ui.Button(ButtonKind.Ghost, "Смотреть сейчас", Skip, null, "veil-skip");
            _skip.Add(Ui.Kbd("↩", true));
            Tooltips.Tip(_skip, "Показать дом сейчас — свет досчитается в фоне", "Esc");

            var col = Ui.El("veil-col", _mark, _name, statusRow, _bar, _skip);
            var center = Ui.El("veil-center", col);
            foreach (var e in new[] { col, center, _mark, statusRow, _bar, _fill, _seg }) e.pickingMode = PickingMode.Ignore;

            _home = Ui.Button(ButtonKind.Ghost, "Все проекты", OpenHome, IconKind.Grid, "veil-home");
            Tooltips.Tip(_home, "Открыть список проектов");

            Element.Add(_image);
            Element.Add(_grid);
            Element.Add(center);
            Element.Add(_home);
            Element.pickingMode = PickingMode.Ignore;
            SetSkip(false);
            Ui.Show(Element, false);
        }

        // ------------------------------------------------------------------ API
        /// <summary>App start: shown from the first frame, before services exist (ui.S is null until Bind).</summary>
        public void ShowStartup()
        {
            _fromStartup = true;
            _homeRequested = false;
            // the last project's name and preview straight from disk, so the app opens onto the house
            ReadLastProject(out string id, out string name, out var tex);
            _projectId = id;
            SetTexture(tex, true);
            _name.text = string.IsNullOrEmpty(name) ? DefaultName : name;
            SetIndeterminate(string.IsNullOrEmpty(id) ? "Запуск…" : "Открываем проект…");
            Enter(Phase.Startup);
        }

        /// <summary>Opening/creating a project: its preview (null id = none yet) and name.</summary>
        public void ShowOpening(string projectId, string name)
        {
            _fromStartup = false;
            _homeRequested = false;
            _projectId = projectId;
            SetTexture(Thumb(projectId), false);
            _name.text = string.IsNullOrEmpty(name) ? "Новый проект" : name;
            SetIndeterminate(projectId == null ? "Создаём проект…" : "Открываем проект…");
            Enter(Phase.Opening);
        }

        /// <summary>Stay until the lighting bake of the open house finishes (or the user skips).</summary>
        public void WaitForLighting()
        {
            var s = _ui.S;
            if (!Visible) return;
            if (s?.Session == null || !s.Session.HasProject) { Hide(); return; }
            if (_homeRequested)
            {
                // «Все проекты» was pressed while the house was being built
                Hide();
                _ui.ShowHome();
                return;
            }
            EnsureSubscribed();
            _projectId = s.Session.ProjectId;
            _name.text = _ui.NameOf(_projectId);
            SetTexture(Thumb(_projectId), false);
            Ui.Show(_home, true);

            var light = s.Lighting;
            if (light == null || !light.IsBaking) { Hide(); return; }   // nothing to wait for (no GPU bake)
            _waitingSince = Time.unscaledTime;
            SetDeterminate(light.Progress);
            _phase = Phase.Waiting;
        }

        public void Hide()
        {
            if (_phase == Phase.Hidden && !Visible) return;
            Visible = false;
            _phase = Phase.Hidden;
            _homeRequested = false;
            SetSkip(false);
            Element.pickingMode = PickingMode.Ignore;
            _home.pickingMode = PickingMode.Ignore;
            Element.RemoveFromClassList("veil-instant");
            Element.AddToClassList("veil-out");
            _hideDone?.Pause();
            _hideDone = Element.schedule.Execute(() =>
            {
                Ui.Show(Element, false);
                _fromStartup = false;
                // gone: drop the startup preview and the soft-focus render textures (the next show makes them again)
                SetTexture(null, false);
            });
            _hideDone.ExecuteLater(OutMs);
        }

        /// <summary>«Смотреть сейчас» / ↩ / Esc.</summary>
        public void Skip()
        {
            // while the house is still being built there is nothing to show yet
            if (!Visible || _phase != Phase.Waiting) return;
            Hide();
        }

        public void Tick()
        {
            if (!Ui.IsShown(Element)) return;
            float dt = Mathf.Min(Time.unscaledDeltaTime, 0.1f);

            if (_phase == Phase.Waiting)
            {
                var s = _ui.S;
                var light = s?.Lighting;
                if (s?.Session == null || !s.Session.HasProject || light == null || !light.IsBaking)
                {
                    if (light != null && light.Current == HouseLighting.State.Ready) ShowProgress(1f);
                    Hide();
                }
                else
                {
                    float target = Mathf.Clamp01(light.Progress);
                    _shownProgress = Mathf.MoveTowards(_shownProgress, target,
                        Mathf.Max(0.02f, Mathf.Abs(target - _shownProgress) * 8f) * dt);
                    ShowProgress(_shownProgress);
                    if (!_skipOn && Time.unscaledTime - _waitingSince >= SkipAfter) SetSkip(true);
                }
            }

            if (_indeterminate)
            {
                float w = _bar.layout.width;
                if (!float.IsNaN(w) && w > 0f)
                {
                    _loopT = (_loopT + dt / LoopSeconds) % 1f;
                    float e = 0.5f - 0.5f * Mathf.Cos(_loopT * Mathf.PI);
                    float seg = w * SegmentShare;
                    _seg.style.translate = new Translate(Mathf.Lerp(-seg, w, e), 0);
                }
            }
        }

        // ------------------------------------------------------------------ internals
        void Enter(Phase phase)
        {
            _phase = phase;
            Visible = true;
            _hideDone?.Pause();
            Element.pickingMode = PickingMode.Position;        // nothing below takes clicks while it is up
            // instant in: the main thread blocks right after (the house is built), a half-faded veil would freeze
            Element.AddToClassList("veil-instant");
            Element.RemoveFromClassList("veil-out");
            Ui.Show(Element, true);
            Ui.Show(_mark, _fromStartup);
            bool services = _ui.S != null;
            Ui.Show(_home, services);
            _home.pickingMode = PickingMode.Position;
            _home.RemoveFromClassList("veil-pressed");
            SetSkip(false);
            Tooltips.HideNow();
        }

        void OpenHome()
        {
            if (!Visible || _ui.S == null) return;
            if (_phase != Phase.Waiting)
            {
                // the house is being built (the main thread is busy): go to the list as soon as it is done
                _homeRequested = true;
                _home.AddToClassList("veil-pressed");
                return;
            }
            Hide();
            _ui.ShowHome();
        }

        void SetSkip(bool on)
        {
            _skipOn = on;
            _skip.EnableInClassList("veil-on", on);
            _skip.pickingMode = on ? PickingMode.Position : PickingMode.Ignore;
        }

        void SetIndeterminate(string status)
        {
            _indeterminate = true;
            _loopT = 0f;
            _status.text = status;
            Ui.Show(_pct, false);
            Ui.Show(_fill, false);
            Ui.Show(_seg, true);
            _seg.style.translate = new Translate(-1000f, 0);
        }

        void SetDeterminate(float progress)
        {
            _indeterminate = false;
            _status.text = "Расчёт освещения ·";
            Ui.Show(_pct, true);
            Ui.Show(_fill, true);
            Ui.Show(_seg, false);
            _shownProgress = Mathf.Clamp01(progress);
            _pctShown = -1;
            ShowProgress(_shownProgress);
        }

        void ShowProgress(float p)
        {
            p = Mathf.Clamp01(p);
            _fill.style.scale = new Scale(new Vector2(p, 1f));
            int pct = Mathf.RoundToInt(p * 100f);
            if (pct == _pctShown) return;
            _pctShown = pct;
            _pct.text = PctText[pct] ??= pct + " %";
        }

        /// <param name="refresh">the same texture object got new pixels: make the soft-focus copy again</param>
        void SetTexture(Texture2D tex, bool owned, bool refresh = false)
        {
            if (tex != null && !Soften(tex, refresh))
            {
                // no render texture here: the plot grid instead (a preview read for this call alone is dropped)
                if (owned && tex != _ownTexture) UnityEngine.Object.Destroy(tex);
                tex = null;
                owned = false;
            }
            if (_ownTexture != null && _ownTexture != tex)
            {
                UnityEngine.Object.Destroy(_ownTexture);
                _ownTexture = null;
            }
            if (owned) _ownTexture = tex;
            if (tex != null)
            {
                // the preview is 640×400 under a full window (2.5×, 5× on Retina): shown sharp it stair-steps, so the
                // veil shows a soft-focus copy — scale-and-crop and the #464951 tint come from USS (.veil-image)
                _image.style.backgroundImage = new StyleBackground(Background.FromRenderTexture(_soft2));
                Ui.Show(_image, true);
                Ui.Show(_grid, false);
            }
            else
            {
                _image.style.backgroundImage = new StyleBackground(StyleKeyword.None);
                ReleaseSoft();
                Ui.Show(_image, false);
                Ui.Show(_grid, true);
            }
        }

        /// <summary>
        /// Soft-focus copy of <paramref name="tex"/>: blitted to 320×200, then to 160×100 (bilinear, so each step
        /// averages 2×2 texels), then stretched by the UI with bilinear filtering. Once per veil show — nothing per frame.
        /// </summary>
        bool Soften(Texture2D tex, bool refresh)
        {
            if (!refresh && tex == _softSource && _soft2 != null && _soft2.IsCreated()) return true;
            try
            {
                if (_soft1 == null) _soft1 = SoftTarget(SoftW1, SoftH1, "veil_soft_320");
                if (_soft2 == null) _soft2 = SoftTarget(SoftW2, SoftH2, "veil_soft_160");
                Graphics.Blit(tex, _soft1);
                Graphics.Blit(_soft1, _soft2);
                _softSource = tex;
                return true;
            }
            catch (Exception e)
            {
                Debug.LogWarning("[Veil] soft preview: " + e.Message);
                ReleaseSoft();
                return false;
            }
        }

        static RenderTexture SoftTarget(int w, int h, string name)
        {
            var rt = new RenderTexture(w, h, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
            {
                name = name,
                filterMode = FilterMode.Bilinear,
                wrapMode = TextureWrapMode.Clamp,
                useMipMap = false,
            };
            rt.Create();
            return rt;
        }

        void ReleaseSoft()
        {
            _softSource = null;
            DestroyTarget(ref _soft1);
            DestroyTarget(ref _soft2);
        }

        static void DestroyTarget(ref RenderTexture rt)
        {
            if (rt == null) return;
            rt.Release();
            UnityEngine.Object.Destroy(rt);
            rt = null;
        }

        Texture2D Thumb(string id)
        {
            var thumbs = _ui.S?.Thumbs;
            if (thumbs == null || !ProjectStore.IsValidId(id)) return null;
            try { return thumbs.Get(id); }
            catch (Exception) { return null; }
        }

        void EnsureSubscribed()
        {
            if (_subscribed || _ui.S?.Thumbs == null) return;
            _subscribed = true;
            // a preview written while the veil is up replaces the old one (the cache destroys the old texture)
            _ui.S.Thumbs.Updated += id =>
            {
                if (Ui.IsShown(Element) && id == _projectId) SetTexture(Thumb(id), false, true);
            };
        }

        /// <summary>
        /// The project the app will open (the last one) with its preview, read directly from the projects folder: the
        /// services do not exist yet on the first frame. Read-only; any failure just leaves the generic startup.
        /// </summary>
        static void ReadLastProject(out string id, out string name, out Texture2D tex)
        {
            id = null;
            name = null;
            tex = null;
            try
            {
                string last = PlayerPrefs.GetString(HouseSession.LastProjectPref, "");
                if (!ProjectStore.IsValidId(last)) return;
                string dir = Path.Combine(ProjectStore.DefaultRoot(), last);
                string json = Path.Combine(dir, ProjectStore.FileName);
                if (!File.Exists(json)) return;
                id = last;
                name = ReadName(json);
                string thumb = Path.Combine(dir, "thumb.jpg");
                if (!File.Exists(thumb)) return;
                var t = new Texture2D(2, 2, TextureFormat.RGB24, false) { name = "veil_startup", wrapMode = TextureWrapMode.Clamp };
                if (t.LoadImage(File.ReadAllBytes(thumb), true)) tex = t;
                else UnityEngine.Object.Destroy(t);
            }
            catch (Exception e)
            {
                Debug.LogWarning("[Veil] last project preview: " + e.Message);
            }
        }

        /// <summary>meta.name of a house document without parsing the whole file.</summary>
        static string ReadName(string path)
        {
            using (var sr = new StreamReader(path))
            using (var r = new JsonTextReader(sr))
            {
                while (r.Read())
                {
                    if (r.TokenType != JsonToken.PropertyName || r.Depth != 1) continue;
                    if (!string.Equals(r.Value as string, "meta")) { r.Skip(); continue; }
                    if (!r.Read() || r.TokenType != JsonToken.StartObject) return null;
                    while (r.Read() && r.TokenType == JsonToken.PropertyName)
                    {
                        if (string.Equals(r.Value as string, "name")) return r.ReadAsString();
                        r.Skip();
                    }
                    return null;
                }
            }
            return null;
        }
    }

    /// <summary>
    /// The veil's illustration when a project has no preview yet: a survey grid on bg-app that fades out towards the
    /// window edges (opaque colours blended in code, no alpha over anything) with a staked plot in the middle.
    /// Colours: USS --veil-bg / --veil-line / --veil-line-major / --veil-plot / --veil-stake.
    /// </summary>
    public sealed class VeilGrid : VisualElement
    {
        const float Cell = 40f;
        const int PlotCellsX = 12, PlotCellsY = 8;

        static readonly CustomStyleProperty<Color> BgProp = new CustomStyleProperty<Color>("--veil-bg");
        static readonly CustomStyleProperty<Color> LineProp = new CustomStyleProperty<Color>("--veil-line");
        static readonly CustomStyleProperty<Color> MajorProp = new CustomStyleProperty<Color>("--veil-line-major");
        static readonly CustomStyleProperty<Color> PlotProp = new CustomStyleProperty<Color>("--veil-plot");
        static readonly CustomStyleProperty<Color> StakeProp = new CustomStyleProperty<Color>("--veil-stake");

        Color _bg = new Color32(0x0C, 0x0D, 0x10, 0xFF);
        Color _line = new Color32(0x14, 0x15, 0x19, 0xFF);
        Color _major = new Color32(0x1A, 0x1C, 0x21, 0xFF);
        Color _plot = new Color32(0x2C, 0x2F, 0x37, 0xFF);
        Color _stake = new Color32(0x4A, 0x4E, 0x56, 0xFF);

        public VeilGrid()
        {
            AddToClassList("veil-grid");
            pickingMode = PickingMode.Ignore;
            generateVisualContent += Draw;
            RegisterCallback<CustomStyleResolvedEvent>(OnStyle);
        }

        void OnStyle(CustomStyleResolvedEvent e)
        {
            var cs = e.customStyle;
            if (cs.TryGetValue(BgProp, out var bg)) _bg = bg;
            if (cs.TryGetValue(LineProp, out var line)) _line = line;
            if (cs.TryGetValue(MajorProp, out var major)) _major = major;
            if (cs.TryGetValue(PlotProp, out var plot)) _plot = plot;
            if (cs.TryGetValue(StakeProp, out var stake)) _stake = stake;
            MarkDirtyRepaint();
        }

        void Draw(MeshGenerationContext ctx)
        {
            var r = contentRect;
            if (r.width < Cell || r.height < Cell) return;
            var p = ctx.painter2D;
            p.lineWidth = 1f;
            p.lineCap = LineCap.Butt;
            var c = new Vector2(Mathf.Round(r.center.x), Mathf.Round(r.center.y));
            float reach = Mathf.Max(r.width, r.height) * 0.6f;
            int nx = Mathf.CeilToInt(r.width * 0.5f / Cell) + 1, ny = Mathf.CeilToInt(r.height * 0.5f / Cell) + 1;

            // grid lines, cell by cell so each piece fades with its distance from the centre
            for (int i = -nx; i <= nx; i++)
            {
                float x = c.x + i * Cell + 0.5f;
                if (x < r.xMin || x > r.xMax) continue;
                var col = i % 4 == 0 ? _major : _line;
                for (int j = -ny; j < ny; j++)
                {
                    float y0 = Mathf.Max(c.y + j * Cell, r.yMin), y1 = Mathf.Min(c.y + (j + 1) * Cell, r.yMax);
                    if (y1 <= y0) continue;
                    float k = Fade(new Vector2(x, (y0 + y1) * 0.5f), c, reach);
                    if (k <= 0.01f) continue;
                    p.strokeColor = Color.Lerp(_bg, col, k);
                    p.BeginPath();
                    p.MoveTo(new Vector2(x, y0));
                    p.LineTo(new Vector2(x, y1));
                    p.Stroke();
                }
            }
            for (int j = -ny; j <= ny; j++)
            {
                float y = c.y + j * Cell + 0.5f;
                if (y < r.yMin || y > r.yMax) continue;
                var col = j % 4 == 0 ? _major : _line;
                for (int i = -nx; i < nx; i++)
                {
                    float x0 = Mathf.Max(c.x + i * Cell, r.xMin), x1 = Mathf.Min(c.x + (i + 1) * Cell, r.xMax);
                    if (x1 <= x0) continue;
                    float k = Fade(new Vector2((x0 + x1) * 0.5f, y), c, reach);
                    if (k <= 0.01f) continue;
                    p.strokeColor = Color.Lerp(_bg, col, k);
                    p.BeginPath();
                    p.MoveTo(new Vector2(x0, y));
                    p.LineTo(new Vector2(x1, y));
                    p.Stroke();
                }
            }

            // the plot: a lot on the grid with a stake at every corner
            float hw = PlotCellsX * Cell * 0.5f, hh = PlotCellsY * Cell * 0.5f;
            if (hw * 2f + 32f > r.width || hh * 2f + 32f > r.height) return;
            float l = c.x - hw + 0.5f, t = c.y - hh + 0.5f, rr = c.x + hw + 0.5f, b = c.y + hh + 0.5f;
            p.strokeColor = _plot;
            p.lineWidth = 1.5f;
            p.lineJoin = LineJoin.Miter;
            p.BeginPath();
            p.MoveTo(new Vector2(l, t));
            p.LineTo(new Vector2(rr, t));
            p.LineTo(new Vector2(rr, b));
            p.LineTo(new Vector2(l, b));
            p.ClosePath();
            p.Stroke();
            p.fillColor = _stake;
            Stake(p, l, t);
            Stake(p, rr, t);
            Stake(p, rr, b);
            Stake(p, l, b);
        }

        static void Stake(Painter2D p, float x, float y)
        {
            const float s = 2.5f;
            p.BeginPath();
            p.MoveTo(new Vector2(x - s, y - s));
            p.LineTo(new Vector2(x + s, y - s));
            p.LineTo(new Vector2(x + s, y + s));
            p.LineTo(new Vector2(x - s, y + s));
            p.ClosePath();
            p.Fill();
        }

        /// <summary>1 up to 20 % of <paramref name="reach"/> → smoothly 0 at <paramref name="reach"/>.</summary>
        static float Fade(Vector2 p, Vector2 c, float reach)
        {
            // Mathf.SmoothStep(a, b, t) interpolates between a and b; the edge form is needed here
            float t = Mathf.InverseLerp(0.2f, 1f, Vector2.Distance(p, c) / reach);
            return 1f - t * t * (3f - 2f * t);
        }
    }
}
