using System;
using System.Collections.Generic;
using System.Globalization;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>A polyline of a design shape (ref mm, y up); closed rings run counter-clockwise after <see cref="Shape2D.Orient"/>.</summary>
    public sealed class Poly
    {
        public List<Vector2> P = new List<Vector2>();
        public bool Closed;
    }

    /// <summary>
    /// Shapes of door designs: <c>{"rect": [x0, y0, x1, y1], "r": radius}</c>, <c>{"ellipse": [cx, cy, rx, ry]}</c>,
    /// <c>{"arch": [x0, y0, x1, y1], "rise": h}</c> and <c>{"path": "M … Z"}</c> (SVG path syntax in y-up millimetres: an arc's
    /// sweep flag 1 turns counter-clockwise). Curves are flattened to polylines (≤ <c>tol</c> mm off the curve).
    /// </summary>
    public static class Shape2D
    {
        public static List<Poly> Parse(JToken shape, float tol = 0.25f)
        {
            var list = new List<Poly>();
            if (!(shape is JObject o)) return list;
            if (o["rect"] is JArray r && r.Count >= 4)
            {
                float x0 = (float)r[0], y0 = (float)r[1], x1 = (float)r[2], y1 = (float)r[3];
                list.Add(RoundRect(Mathf.Min(x0, x1), Mathf.Min(y0, y1), Mathf.Max(x0, x1), Mathf.Max(y0, y1), (float?)o["r"] ?? 0f, tol));
            }
            else if (o["ellipse"] is JArray e && e.Count >= 4)
                list.Add(Ellipse((float)e[0], (float)e[1], (float)e[2], (float)e[3], tol));
            else if (o["arch"] is JArray a && a.Count >= 4)
                list.Add(Arch((float)a[0], (float)a[1], (float)a[2], (float)a[3], (float?)o["rise"] ?? 0f, tol));
            else if (o["path"] != null)
                list.AddRange(ParsePath((string)o["path"], tol));
            foreach (var p in list) Orient(p);
            return list;
        }

        /// <summary>Closed rings counter-clockwise (y up).</summary>
        public static void Orient(Poly p)
        {
            if (!p.Closed || p.P.Count < 3) return;
            float a = 0f;
            for (int i = 0; i < p.P.Count; i++)
            {
                Vector2 u = p.P[i], v = p.P[(i + 1) % p.P.Count];
                a += u.x * v.y - v.x * u.y;
            }
            if (a < 0f) p.P.Reverse();
        }

        public static Poly RoundRect(float x0, float y0, float x1, float y1, float r, float tol)
        {
            var p = new Poly { Closed = true };
            r = Mathf.Clamp(r, 0f, Mathf.Min(x1 - x0, y1 - y0) * 0.5f);
            if (r < 0.01f)
            {
                p.P.Add(new Vector2(x0, y0)); p.P.Add(new Vector2(x1, y0)); p.P.Add(new Vector2(x1, y1)); p.P.Add(new Vector2(x0, y1));
                return p;
            }
            int n = ArcSegments(r, Mathf.PI * 0.5f, tol);
            void Corner(float cx, float cy, float a0)
            {
                for (int i = 0; i <= n; i++)
                {
                    float a = a0 + Mathf.PI * 0.5f * i / n;
                    p.P.Add(new Vector2(cx + r * Mathf.Cos(a), cy + r * Mathf.Sin(a)));
                }
            }
            Corner(x1 - r, y0 + r, -Mathf.PI * 0.5f);
            Corner(x1 - r, y1 - r, 0f);
            Corner(x0 + r, y1 - r, Mathf.PI * 0.5f);
            Corner(x0 + r, y0 + r, Mathf.PI);
            return p;
        }

        public static Poly Ellipse(float cx, float cy, float rx, float ry, float tol)
        {
            var p = new Poly { Closed = true };
            int n = Mathf.Max(12, ArcSegments(Mathf.Max(rx, ry), Mathf.PI * 2f, tol));
            for (int i = 0; i < n; i++)
            {
                float a = Mathf.PI * 2f * i / n;
                p.P.Add(new Vector2(cx + rx * Mathf.Cos(a), cy + ry * Mathf.Sin(a)));
            }
            return p;
        }

        /// <summary>Rectangle whose top is a circular arc: straight sides up to y1 - rise, the arc's crown at y1.</summary>
        public static Poly Arch(float x0, float y0, float x1, float y1, float rise, float tol)
        {
            if (x1 < x0) (x0, x1) = (x1, x0);
            if (y1 < y0) (y0, y1) = (y1, y0);
            var p = new Poly { Closed = true };
            float w = x1 - x0;
            rise = Mathf.Clamp(rise, 0f, Mathf.Min(w * 0.5f, y1 - y0));
            p.P.Add(new Vector2(x0, y0));
            p.P.Add(new Vector2(x1, y0));
            if (rise < 0.01f)
            {
                p.P.Add(new Vector2(x1, y1)); p.P.Add(new Vector2(x0, y1));
                return p;
            }
            float half = w * 0.5f, R = (half * half + rise * rise) / (2f * rise), cy = y1 - R, cx = x0 + half;
            float a0 = Mathf.Atan2(y1 - rise - cy, x1 - cx), a1 = Mathf.Atan2(y1 - rise - cy, x0 - cx);
            int n = Mathf.Max(4, ArcSegments(R, a1 - a0, tol));
            for (int i = 0; i <= n; i++)
            {
                float a = Mathf.Lerp(a0, a1, i / (float)n);
                p.P.Add(new Vector2(cx + R * Mathf.Cos(a), cy + R * Mathf.Sin(a)));
            }
            return p;
        }

        static int ArcSegments(float r, float angle, float tol)
        {
            if (r < 1e-3f) return 1;
            float step = 2f * Mathf.Acos(Mathf.Clamp01(1f - tol / r));
            step = Mathf.Clamp(step, 0.02f, 0.35f);
            return Mathf.Max(2, Mathf.CeilToInt(Mathf.Abs(angle) / step));
        }

        // ------------------------------------------------------------------ SVG path
        public static List<Poly> ParsePath(string d, float tol = 0.25f)
        {
            var result = new List<Poly>();
            if (string.IsNullOrWhiteSpace(d)) return result;
            var tok = new Tokenizer(d);
            Poly cur = null;
            Vector2 pos = Vector2.zero, start = Vector2.zero, lastCtrl = Vector2.zero;
            char cmd = ' ', prevCmd = ' ';
            void Begin(Vector2 p)
            {
                if (cur != null && cur.P.Count > 1) result.Add(cur);
                cur = new Poly();
                cur.P.Add(p);
                start = p;
            }
            void LineTo(Vector2 p)
            {
                if (cur == null) Begin(pos);
                if ((cur.P[cur.P.Count - 1] - p).sqrMagnitude > 1e-8f) cur.P.Add(p);
            }
            while (tok.More)
            {
                if (tok.PeekCommand(out char c)) { cmd = c; tok.Skip(); }
                else if (cmd == ' ') break;
                bool rel = char.IsLower(cmd);
                Vector2 Rel(Vector2 p) => rel ? pos + p : p;
                switch (char.ToUpperInvariant(cmd))
                {
                    case 'M':
                        pos = Rel(tok.Vec());
                        Begin(pos);
                        cmd = rel ? 'l' : 'L';   // further pairs are line-tos
                        break;
                    case 'L': pos = Rel(tok.Vec()); LineTo(pos); break;
                    case 'H': { float x = tok.Num(); pos = new Vector2(rel ? pos.x + x : x, pos.y); LineTo(pos); break; }
                    case 'V': { float y = tok.Num(); pos = new Vector2(pos.x, rel ? pos.y + y : y); LineTo(pos); break; }
                    case 'C':
                    {
                        Vector2 c1 = Rel(tok.Vec()), c2 = Rel(tok.Vec()), p = Rel(tok.Vec());
                        Cubic(pos, c1, c2, p, tol, LineTo);
                        lastCtrl = c2; pos = p;
                        break;
                    }
                    case 'S':
                    {
                        Vector2 c1 = "CcSs".IndexOf(prevCmd) >= 0 ? 2f * pos - lastCtrl : pos;
                        Vector2 c2 = Rel(tok.Vec()), p = Rel(tok.Vec());
                        Cubic(pos, c1, c2, p, tol, LineTo);
                        lastCtrl = c2; pos = p;
                        break;
                    }
                    case 'Q':
                    {
                        Vector2 q = Rel(tok.Vec()), p = Rel(tok.Vec());
                        Cubic(pos, pos + 2f / 3f * (q - pos), p + 2f / 3f * (q - p), p, tol, LineTo);
                        lastCtrl = q; pos = p;
                        break;
                    }
                    case 'T':
                    {
                        Vector2 q = "QqTt".IndexOf(prevCmd) >= 0 ? 2f * pos - lastCtrl : pos;
                        Vector2 p = Rel(tok.Vec());
                        Cubic(pos, pos + 2f / 3f * (q - pos), p + 2f / 3f * (q - p), p, tol, LineTo);
                        lastCtrl = q; pos = p;
                        break;
                    }
                    case 'A':
                    {
                        float rx = tok.Num(), ry = tok.Num(), rot = tok.Num();
                        bool large = tok.Flag(), sweep = tok.Flag();
                        Vector2 p = Rel(tok.Vec());
                        Arc(pos, p, rx, ry, rot, large, sweep, tol, LineTo);
                        pos = p;
                        break;
                    }
                    case 'Z':
                        if (cur != null)
                        {
                            if (cur.P.Count > 1 && (cur.P[cur.P.Count - 1] - start).sqrMagnitude < 1e-6f) cur.P.RemoveAt(cur.P.Count - 1);
                            cur.Closed = true;
                            if (cur.P.Count > 1) result.Add(cur);
                            cur = null;
                        }
                        pos = start;
                        break;
                    default:
                        tok.Skip();
                        break;
                }
                prevCmd = cmd;
            }
            if (cur != null && cur.P.Count > 1) result.Add(cur);
            return result;
        }

        static void Cubic(Vector2 p0, Vector2 p1, Vector2 p2, Vector2 p3, float tol, Action<Vector2> add)
        {
            float len = (p1 - p0).magnitude + (p2 - p1).magnitude + (p3 - p2).magnitude;
            int n = Mathf.Clamp(Mathf.CeilToInt(len / Mathf.Max(2f, 12f * tol)), 4, 200);
            for (int i = 1; i <= n; i++)
            {
                float t = i / (float)n, u = 1f - t;
                add(u * u * u * p0 + 3f * u * u * t * p1 + 3f * u * t * t * p2 + t * t * t * p3);
            }
        }

        /// <summary>SVG elliptical arc (endpoint parameterisation, spec F.6.5) flattened; angles in the y-up frame.</summary>
        static void Arc(Vector2 p0, Vector2 p1, float rx, float ry, float rotDeg, bool large, bool sweep, float tol, Action<Vector2> add)
        {
            rx = Mathf.Abs(rx); ry = Mathf.Abs(ry);
            if (rx < 1e-4f || ry < 1e-4f || (p1 - p0).sqrMagnitude < 1e-8f) { add(p1); return; }
            float phi = rotDeg * Mathf.Deg2Rad, cs = Mathf.Cos(phi), sn = Mathf.Sin(phi);
            Vector2 d = (p0 - p1) * 0.5f;
            float x1 = cs * d.x + sn * d.y, y1 = -sn * d.x + cs * d.y;
            float lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry);
            if (lam > 1f) { float s = Mathf.Sqrt(lam); rx *= s; ry *= s; }
            float num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1, den = rx * rx * y1 * y1 + ry * ry * x1 * x1;
            float co = den > 1e-12f ? Mathf.Sqrt(Mathf.Max(0f, num / den)) : 0f;
            if (large == sweep) co = -co;
            float cxp = co * rx * y1 / ry, cyp = -co * ry * x1 / rx;
            Vector2 c = new Vector2(cs * cxp - sn * cyp, sn * cxp + cs * cyp) + (p0 + p1) * 0.5f;
            float Ang(Vector2 u, Vector2 v) { float a = Mathf.Atan2(u.x * v.y - u.y * v.x, Vector2.Dot(u, v)); return a; }
            var v0 = new Vector2((x1 - cxp) / rx, (y1 - cyp) / ry);
            var v1 = new Vector2((-x1 - cxp) / rx, (-y1 - cyp) / ry);
            float th = Mathf.Atan2(v0.y, v0.x), dth = Ang(v0, v1);
            if (!sweep && dth > 0f) dth -= Mathf.PI * 2f;
            else if (sweep && dth < 0f) dth += Mathf.PI * 2f;
            int n = Mathf.Max(2, ArcSegments(Mathf.Max(rx, ry), dth, tol));
            for (int i = 1; i <= n; i++)
            {
                float a = th + dth * i / n;
                float ex = rx * Mathf.Cos(a), ey = ry * Mathf.Sin(a);
                add(i == n ? p1 : c + new Vector2(cs * ex - sn * ey, sn * ex + cs * ey));
            }
        }

        sealed class Tokenizer
        {
            readonly string _s;
            int _i;
            public Tokenizer(string s) { _s = s; }
            void Ws() { while (_i < _s.Length && (char.IsWhiteSpace(_s[_i]) || _s[_i] == ',')) _i++; }
            public bool More { get { Ws(); return _i < _s.Length; } }
            public bool PeekCommand(out char c)
            {
                Ws();
                c = _i < _s.Length ? _s[_i] : ' ';
                return _i < _s.Length && char.IsLetter(c) && c != 'e' && c != 'E';
            }
            public void Skip() => _i++;
            public float Num()
            {
                Ws();
                int st = _i;
                if (_i < _s.Length && (_s[_i] == '+' || _s[_i] == '-')) _i++;
                bool dot = false;
                while (_i < _s.Length)
                {
                    char ch = _s[_i];
                    if (char.IsDigit(ch)) { _i++; continue; }
                    if (ch == '.' && !dot) { dot = true; _i++; continue; }
                    if ((ch == 'e' || ch == 'E') && _i + 1 < _s.Length)
                    {
                        _i++;
                        if (_s[_i] == '+' || _s[_i] == '-') _i++;
                        continue;
                    }
                    break;
                }
                if (_i == st) { _i++; return 0f; }   // garbage: skip a char so parsing ends
                float.TryParse(_s.Substring(st, _i - st), NumberStyles.Float, CultureInfo.InvariantCulture, out float v);
                return v;
            }
            public bool Flag()
            {
                Ws();
                if (_i < _s.Length && (_s[_i] == '0' || _s[_i] == '1')) return _s[_i++] == '1';
                return Num() != 0f;
            }
            public Vector2 Vec() { float x = Num(); float y = Num(); return new Vector2(x, y); }
        }

        // ------------------------------------------------------------------ resizing
        /// <summary>
        /// Maps shapes drawn at the reference size onto the leaf: through the fix/stretch maps, except along an axis where the
        /// whole shape is thinner than <paramref name="thin"/> — there it keeps its size and only its centre moves.
        /// </summary>
        public static void Map(List<Poly> polys, ResizeMap mx, ResizeMap my, float thin = LeafBuilder.ThinMm)
        {
            if (polys.Count == 0) return;
            Vector2 mn = new Vector2(float.MaxValue, float.MaxValue), mxv = new Vector2(float.MinValue, float.MinValue);
            foreach (var p in polys) foreach (var v in p.P) { mn = Vector2.Min(mn, v); mxv = Vector2.Max(mxv, v); }
            var c = (mn + mxv) * 0.5f;
            bool keepX = mxv.x - mn.x < thin, keepY = mxv.y - mn.y < thin;
            float cx = mx.Map(c.x), cy = my.Map(c.y);
            foreach (var p in polys)
                for (int i = 0; i < p.P.Count; i++)
                {
                    var v = p.P[i];
                    p.P[i] = new Vector2(keepX ? cx + (v.x - c.x) : mx.Map(v.x), keepY ? cy + (v.y - c.y) : my.Map(v.y));
                }
        }
    }
}
