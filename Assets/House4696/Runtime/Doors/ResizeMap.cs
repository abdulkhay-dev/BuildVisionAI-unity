using System.Collections.Generic;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>
    /// Maps a design coordinate (drawn at the reference size) to the leaf being built: fixed intervals (stiles, rails)
    /// keep their length and move, everything else stretches by one common factor. Piecewise linear and monotonic.
    /// When the leaf is too small for the fixed parts, everything scales uniformly instead.
    /// </summary>
    public sealed class ResizeMap
    {
        readonly List<float> _src = new List<float>(), _dst = new List<float>();

        public ResizeMap(float refLength, float length, IList<float[]> fixedIntervals)
        {
            var fixedSpans = new List<(float a, float b)>();
            if (fixedIntervals != null)
                foreach (var iv in fixedIntervals)
                {
                    if (iv == null || iv.Length < 2) continue;
                    float a = Mathf.Clamp(Mathf.Min(iv[0], iv[1]), 0f, refLength), b = Mathf.Clamp(Mathf.Max(iv[0], iv[1]), 0f, refLength);
                    if (b > a) fixedSpans.Add((a, b));
                }
            fixedSpans.Sort((p, q) => p.a.CompareTo(q.a));
            // merge overlaps
            var merged = new List<(float a, float b)>();
            foreach (var s in fixedSpans)
            {
                if (merged.Count > 0 && s.a <= merged[merged.Count - 1].b)
                    merged[merged.Count - 1] = (merged[merged.Count - 1].a, Mathf.Max(merged[merged.Count - 1].b, s.b));
                else merged.Add(s);
            }
            float fixedLen = 0f;
            foreach (var s in merged) fixedLen += s.b - s.a;
            float stretchLen = refLength - fixedLen;
            // leaves narrower than their fixed parts (or designs with nothing to stretch): uniform scale
            if (stretchLen < 1f || length - fixedLen < stretchLen * 0.25f)
            {
                _src.Add(0f); _dst.Add(0f);
                _src.Add(refLength); _dst.Add(length);
                return;
            }
            float k = (length - fixedLen) / stretchLen;
            float src = 0f, dst = 0f;
            _src.Add(0f); _dst.Add(0f);
            foreach (var s in merged)
            {
                if (s.a > src) { dst += (s.a - src) * k; src = s.a; Add(src, dst); }
                dst += s.b - s.a; src = s.b; Add(src, dst);
            }
            if (refLength > src) { dst += (refLength - src) * k; Add(refLength, dst); }
        }

        void Add(float s, float d)
        {
            if (_src.Count > 0 && Mathf.Abs(_src[_src.Count - 1] - s) < 1e-4f) { _dst[_dst.Count - 1] = d; return; }
            _src.Add(s); _dst.Add(d);
        }

        /// <summary>Target coordinate of a design coordinate (linear beyond the ends).</summary>
        public float Map(float v)
        {
            int n = _src.Count;
            if (n < 2) return v;
            int i = 0;
            while (i < n - 2 && v > _src[i + 1]) i++;
            float s0 = _src[i], s1 = _src[i + 1];
            float t = s1 - s0 > 1e-5f ? (v - s0) / (s1 - s0) : 0f;
            return Mathf.LerpUnclamped(_dst[i], _dst[i + 1], t);
        }

        /// <summary>
        /// Maps a span [a, b]: a span thinner than <paramref name="thin"/> keeps its length around its mapped centre
        /// (glass strips, narrow inserts), a wider one maps both ends.
        /// </summary>
        public (float a, float b) MapSpan(float a, float b, float thin = 60f)
        {
            if (b - a < thin)
            {
                float c = Map((a + b) * 0.5f), h = (b - a) * 0.5f;
                return (c - h, c + h);
            }
            return (Map(a), Map(b));
        }
    }
}
