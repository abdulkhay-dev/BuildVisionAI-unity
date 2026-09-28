using System.Collections.Generic;
using System.Linq;
using House4696.Model;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>How a catalogue door opens.</summary>
    public enum DoorKind { Swing, Sliding, Folding, Portal }

    /// <summary>
    /// Sizes of catalogue doors: standard leaves and the wall opening a door needs. The catalogue's table 1 ("Расчёт
    /// рекомендуемых проёмов") gives the opening from the leaf: swing +9…10 cm in width and +6…8 cm in height (the frame
    /// 2 × 22 mm, the leaf gaps 2 × 3 mm, a mounting gap the casings cover); book fold +9…10 / +9…10 (TWIGGY table:
    /// 2 × 35 → 77…80 cm); coupe with framing 0 / +2…5; the opening of a portal is the portal.
    /// </summary>
    public static class DoorSizing
    {
        /// <summary>Standard leaf widths, m (the catalogue's 60, 70, 80, 90 cm).</summary>
        public static readonly float[] Widths = { 0.6f, 0.7f, 0.8f, 0.9f };
        /// <summary>Standard panel widths of folding doors, m (35, 40 cm).</summary>
        public static readonly float[] FoldWidths = { 0.35f, 0.4f };
        /// <summary>Standard leaf height, m.</summary>
        public const float Height = 2.0f;
        /// <summary>Swing door: opening = leaves + this (the middle of +9…10 / +6…8 cm).</summary>
        public static readonly Vector2 SwingAllowance = new Vector2(0.095f, 0.07f);
        /// <summary>Gap between the two leaves of a double door, m.</summary>
        public const float MeetingGap = 0.004f;
        /// <summary>A derived leaf this close to a standard size is the standard size.</summary>
        const float SnapWidth = 0.015f, SnapHeight = 0.02f;

        public static bool IsDoor(OpeningType t) => t == OpeningType.Door || t == OpeningType.EntryDoor || t == OpeningType.SolidDoor;

        /// <summary>A door opening that names a catalogue model (or a framed portal).</summary>
        public static bool IsCatalogueDoor(OpeningDef o) =>
            o != null && (IsDoor(o.Type) || o.Type == OpeningType.Hole) && (!string.IsNullOrEmpty(o.Model) || KindOf(o) == DoorKind.Portal && o.Finish != null);

        public static DoorKind KindOf(OpeningDef o)
        {
            // an opening that does not say takes its model's kind when the catalogue sells the model only as a portal,
            // a sliding or a folding door (TWIGGY); a model that is also a swing door stays a swing door
            if (o?.Kind == null && !string.IsNullOrEmpty(o?.Model))
            {
                var offers = DoorCatalog.Offers(o.Model);
                if (offers.Count > 0 && offers.All(of => SeriesKind(of.series) != DoorKind.Swing)) return SeriesKind(offers[0].series);
            }
            return Parse(o?.Kind);
        }

        static DoorKind Parse(string kind)
        {
            switch ((kind ?? "swing").Trim().ToLowerInvariant())
            {
                case "sliding": case "slide": case "coupe": case "купе": return DoorKind.Sliding;
                case "folding": case "fold": case "book": case "книжка": return DoorKind.Folding;
                case "portal": case "портал": return DoorKind.Portal;
                default: return DoorKind.Swing;
            }
        }

        /// <summary>Kind of door a series sells (interior and entrance series: swing doors).</summary>
        public static DoorKind SeriesKind(SeriesDef s) => Parse(s?.Kind);

        /// <summary>Leaves the opening's model comes with (a ready-made "2П-03" block), if the catalogue says.</summary>
        static int? ModelLeaves(OpeningDef o)
        {
            if (string.IsNullOrEmpty(o?.Model)) return null;
            var offers = DoorCatalog.Offers(o.Model);
            return offers.Count > 0 ? offers[0].model.Leaves : null;
        }

        /// <summary>Leaves of a swing / sliding door (1–2), panels of a folding door (2 or 4).</summary>
        public static int LeavesOf(OpeningDef o)
        {
            if (IsEntrance(o)) return 1;
            var kind = KindOf(o);
            if (kind == DoorKind.Portal) return 0;
            if (kind == DoorKind.Folding) return (o.Leaves ?? ModelLeaves(o) ?? 2) >= 4 ? 4 : 2;
            return Mathf.Clamp(o.Leaves ?? ModelLeaves(o) ?? 1, 1, 2);
        }

        /// <summary>Standard entrance door blocks (коробка), m: 860 / 960 × 2050.</summary>
        public static readonly float[] EntranceWidths = { 0.86f, 0.96f };
        public const float EntranceHeight = 2.05f;

        /// <summary>Block sizes an entrance model is sold in (its own, its series', else 86/96 × 205).</summary>
        public static List<Vector2> EntranceSizes(OpeningDef o)
        {
            var list = new List<Vector2>();
            if (!string.IsNullOrEmpty(o?.Model))
            {
                var offers = DoorCatalog.Offers(o.Model);
                var sizes = offers.Count > 0 ? offers[0].model.Sizes ?? offers[0].series.Sizes : null;
                if (sizes != null) foreach (var s in sizes) if (s != null && s.Length >= 2) list.Add(new Vector2(s[0], s[1]));
            }
            if (list.Count == 0) foreach (float w in EntranceWidths) list.Add(new Vector2(w, EntranceHeight));
            return list;
        }

        /// <summary>A model of an entrance series: its "leaf" size is the whole steel block (коробка), the opening +2…4 cm.</summary>
        public static bool IsEntrance(OpeningDef o)
        {
            if (o == null || string.IsNullOrEmpty(o.Model)) return false;
            var offers = DoorCatalog.Offers(o.Model);
            return offers.Count > 0 && offers[0].series.IsEntrance;
        }

        /// <summary>Opening minus the leaves (all of them side by side) for the door's kind.</summary>
        public static Vector2 Allowance(OpeningDef o)
        {
            if (IsEntrance(o)) return new Vector2(0.03f, 0.03f);
            switch (KindOf(o))
            {
                case DoorKind.Folding: return new Vector2(0.085f, 0.095f);
                case DoorKind.Sliding: return new Vector2(-0.02f, 0.035f);   // the leaf overlaps the framed opening a little
                case DoorKind.Portal: return Vector2.zero;
                default: return SwingAllowance;
            }
        }

        static float Between(OpeningDef o) => KindOf(o) == DoorKind.Folding ? 0.003f : MeetingGap;

        /// <summary>The leaf (one of them) of a catalogue door: its own size, else derived from the opening (snapped to a standard size nearby).</summary>
        public static Vector2 LeafOf(OpeningDef o)
        {
            if (o.Leaf.HasValue) return o.Leaf.Value;
            int n = Mathf.Max(1, LeavesOf(o));
            var a = Allowance(o);
            float w = (o.Width - a.x - (n - 1) * Between(o)) / n, h = o.Height - a.y;
            if (IsEntrance(o))
            {
                foreach (var e in EntranceSizes(o))
                    if (Mathf.Abs(w - e.x) <= SnapWidth && Mathf.Abs(h - e.y) <= SnapHeight) return e;
                return new Vector2(Mathf.Max(0.25f, w), Mathf.Max(1.2f, h));
            }
            foreach (float s in KindOf(o) == DoorKind.Folding ? FoldWidths : Widths)
                if (Mathf.Abs(w - s) <= SnapWidth) { w = s; break; }
            if (Mathf.Abs(h - Height) <= SnapHeight) h = Height;
            return new Vector2(Mathf.Max(0.25f, w), Mathf.Max(1.2f, h));
        }

        public static bool IsStandard(OpeningDef o, Vector2 leaf)
        {
            if (IsEntrance(o)) return EntranceSizes(o).Any(e => Mathf.Abs(leaf.x - e.x) < 0.001f && Mathf.Abs(leaf.y - e.y) < 0.001f);
            var widths = KindOf(o) == DoorKind.Folding ? FoldWidths : Widths;
            return widths.Any(s => Mathf.Abs(leaf.x - s) < 0.001f) && Mathf.Abs(leaf.y - Height) < 0.001f;
        }

        public static bool IsStandard(Vector2 leaf) =>
            Widths.Any(s => Mathf.Abs(leaf.x - s) < 0.001f) && Mathf.Abs(leaf.y - Height) < 0.001f;

        /// <summary>The wall opening for a leaf size (all leaves side by side), m.</summary>
        public static Vector2 OpeningFor(OpeningDef o, Vector2 leaf)
        {
            int n = Mathf.Max(1, LeavesOf(o));
            var a = Allowance(o);
            return new Vector2(Round(n * leaf.x + (n - 1) * Between(o) + a.x), Round(leaf.y + a.y));
        }

        /// <summary>
        /// Catalogue doors that give their leaf size get the opening it needs (width and height; <c>at</c> stays, so the
        /// opening keeps its start edge). Idempotent; notes list the openings that changed.
        /// </summary>
        public static void Normalize(HouseDocument doc, List<string> notes = null)
        {
            if (doc?.Openings == null) return;
            foreach (var o in doc.Openings)
            {
                // a steel entrance door in an exterior wall opens outwards (its street face is the side it swings to)
                if (o.Swing >= 0 && IsEntrance(o) && doc.Walls != null &&
                    doc.Walls.Exists(w => w.Id == o.Wall && w.Kind == WallKind.Exterior))
                {
                    o.Swing = -1;
                    notes?.Add($"проём '{o.Id}': входная дверь открывается наружу — swing −1 (уличная панель снаружи)");
                }
                if (!IsCatalogueDoor(o) || !o.Leaf.HasValue || KindOf(o) == DoorKind.Portal) continue;
                var size = OpeningFor(o, o.Leaf.Value);
                if (Mathf.Abs(o.Width - size.x) < 0.0005f && Mathf.Abs(o.Height - size.y) < 0.0005f) continue;
                int n = LeavesOf(o);
                notes?.Add($"проём '{o.Id}': {o.Width:0.###}×{o.Height:0.###} → {size.x:0.###}×{size.y:0.###} м под " +
                           $"{(n > 1 ? n + " × " : "")}полотно {o.Leaf.Value.x:0.###}×{o.Leaf.Value.y:0.###} (таблица каталога)");
                o.Width = size.x;
                o.Height = size.y;
            }
        }

        static float Round(float v) => Mathf.Round(v * 1000f) / 1000f;
    }
}
