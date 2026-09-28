using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>
    /// A catalogue door as installed, by kind (<see cref="DoorKind"/>):
    /// <list type="bullet">
    /// <item>swing — frame («коробка Т» 70 × 22 mm, 32 mm stop, seal) flush with the wall face the door opens to,
    /// extensions («добор») to the other face, casings («наличник Т» 70 × 8 mm) mitred at the head, one or two leaves on
    /// hinges; the active leaf of a double door has the handles and the astragal;</item>
    /// <item>sliding (coupe) — the opening lined and cased, the leaf (or two) hanging from a rail with a cover board on the
    /// wall face, running along the wall;</item>
    /// <item>folding (book) — the opening lined and cased, two or four panels on a top track folding to the swing side;</item>
    /// <item>portal — the opening only lined and cased.</item>
    /// </list>
    /// Depth coordinate w: from the wall face the door opens to (the <see cref="OpeningDef.Swing"/> side) into the wall.
    /// </summary>
    public sealed partial class DoorBlockBuilder
    {
        // «Т» system, metres (catalogue "Погонажные изделия", ЭкоШпон)
        public const float FrameDepth = 0.070f, FrameThick = 0.022f, StopFrom = 0.046f, StopOut = 0.010f, KitFrameThick = 0.040f;
        public const float CasingW = 0.070f, CasingT = 0.008f, CasingBack = 0.008f, DoborT = 0.008f;
        public const float LeafGap = 0.003f, FloorGap = 0.008f, SealT = 0.004f;
        /// <summary>Lining of a framed opening (portal, coupe, book): board thickness and the mounting gap behind it.</summary>
        public const float LiningT = 0.012f, LiningGap = 0.010f;
        /// <summary>How far a swing door opens, degrees (the leaf then stands along the casing); a book folds this far.</summary>
        public const float OpenAngle = 92f, FoldAngle = 80f;

        readonly HouseContext _c;
        public DoorBlockBuilder(HouseContext c) { _c = c; }

        /// <summary>Materials of a resolved door: the finish from the library, glass and metal from the palette.</summary>
        public DoorMaterialSet Materials(ResolvedDoor door)
        {
            var M = _c.M;
            var fallback = M.OakLight;
            Material Library(string id, string color) =>
                !string.IsNullOrEmpty(id) && _c.Mats.Has(id) ? _c.Mats.Get(id, fallback)
                : !string.IsNullOrEmpty(color) ? _c.Mats.Get("plaster" + color, fallback) : null;
            Material finish = door.Finish != null ? Library(door.Finish.Material, door.Finish.Color) ?? fallback : fallback;
            Material finish2 = door.Finish != null && (door.Finish.Material2 != null || door.Finish.Color2 != null)
                ? Library(door.Finish.Material2, door.Finish.Color2) : null;
            var set = new DoorMaterialSet
            {
                Finish = finish, Finish2 = finish2, Satin = M.DoorSatin, Clear = M.Glass, Mirror = M.Mirror, Black = M.BlackGlass,
                Metal = M.DoorAluminium, Chrome = M.Chrome, Seal = M.DoorSeal,
                LacobelBeige = M.DoorLacobelBeige, LacobelWhite = M.DoorLacobelWhite, LacobelSmoke = M.DoorLacobelSmoke,
                Gold = M.Brass, Bronze = M.DoorBronze, BlackMetal = M.BlackMetal,
                PatinaGold = M.DoorPatinaGold, PatinaSilver = M.DoorPatinaSilver, PatinaDark = M.DoorPatinaDark,
            };
            set.Library = id => _c.Mats.Has(id) ? _c.Mats.Get(id, null) : null;
            set.Glass = (!string.IsNullOrEmpty(door.Glass?.Material) ? set.Library(door.Glass.Material) : null)
                        ?? set.GlassRole(door.Glass?.Role ?? "satin") ?? set.Satin;
            set.GlassFit = door.Glass != null && door.Glass.Fit && !string.IsNullOrEmpty(door.Glass.Material);
            set.GlassMm = door.Glass?.Thickness ?? (door.Glass != null && door.Glass.Id.StartsWith("t") ? 8f : 4f);
            set.GlassFacetMm = door.Glass?.Facet ?? 0f;
            return set;
        }

        /// <summary>The handle's finish: the model's or series' choice for the door's colour, else the design's.</summary>
        static string HandleFinish(ResolvedDoor door, HandleSpec hs)
        {
            var map = door.Model?.Handles ?? door.Series?.Handles;
            return map != null && door.Finish != null && map.TryGetValue(door.Finish.Id, out var f) ? f : hs.Finish;
        }

        /// <summary>One door block being built: its wall, opening, materials and the mesh of its fixed parts.</summary>
        sealed class Blk
        {
            public WallFrame F;
            public OpeningDef O;
            public ResolvedDoor Door;
            public DoorMaterialSet Mats;
            public float T, S0, S1, Y0, Y1;
            public bool SwingPlus, HingeAtMin;
            public string Id;
            public MeshBuilder Mb;
            int _k;

            public float Z(float w) => SwingPlus ? T - w : w;
            public Vector3 L(float s, float y, float w) => new Vector3(s, y, Z(w));
            public Vector3 World(float s, float y, float w) => F.ToWorld.MultiplyPoint3x4(L(s, y, w));
            public Vector2 Off() { _k++; return new Vector2(Hash01(Id, _k) * 2f, Hash01(Id, _k + 50)); }
        }

        /// <summary>
        /// Builds the door of opening <paramref name="o"/> (wall-space rectangle s0…s1 × y0…y1 of wall <paramref name="f"/>).
        /// <paramref name="casingOut"/> = the face at d = 0 (outer, right of A→B) takes a casing; <paramref name="casingIn"/> =
        /// the face at d = -T.
        /// </summary>
        public void Build(WallFrame f, OpeningDef o, ResolvedDoor door, float s0, float s1, float y0, float y1,
                          bool casingOut = true, bool casingIn = true)
        {
            var b = new Blk
            {
                F = f, O = o, Door = door, Mats = Materials(door), T = f.T, S0 = s0, S1 = s1, Y0 = y0, Y1 = y1,
                SwingPlus = o.Swing >= 0, HingeAtMin = o.Hinge == Hinge.Start, Id = o.Id ?? f.Def.Id,
                Mb = new MeshBuilder { Transform = f.ToWorld },
            };
            // an entrance door in an exterior wall (no outer casing) always swings out: its street face is on the swing side
            if (door.Entrance && !casingOut) b.SwingPlus = false;
            // the swing side is the d = -T face ("in") when the door swings to the left of A→B
            bool nearOk = b.SwingPlus ? casingIn : casingOut, farOk = b.SwingPlus ? casingOut : casingIn;
            var kind = DoorSizing.KindOf(o);
            if (kind != DoorKind.Portal && door.Design == null) kind = DoorKind.Portal;
            if (door.Entrance && door.Design != null)
            {
                Entrance(b, nearOk, farOk);
                _c.W.Emit("DoorBlock_" + b.Id, _c.Interior, b.Mb);
                return;
            }
            switch (kind)
            {
                case DoorKind.Sliding: Sliding(b, nearOk, farOk); break;
                case DoorKind.Folding: Folding(b, nearOk, farOk); break;
                case DoorKind.Portal: Portal(b, nearOk, farOk); break;
                default: Swing(b, nearOk, farOk); break;
            }
            _c.W.Emit("DoorBlock_" + b.Id, _c.Interior, b.Mb);
        }

        // ================================================================== swing
        void Swing(Blk b, bool nearOk, bool farOk)
        {
            var mats = b.Mats;
            var leafSize = DoorSizing.LeafOf(b.O);
            int n = Mathf.Clamp(DoorSizing.LeavesOf(b.O), 1, 2);
            float mid = (b.S0 + b.S1) * 0.5f;
            // "kit" = a ready-made block as sold (catalogue "1П-03"): a solid 70 × 40 frame, no casings, no extensions
            bool kit = string.Equals(b.Door.Block, "kit", System.StringComparison.OrdinalIgnoreCase);
            float ft = kit ? KitFrameThick : FrameThick;
            float room = (b.S1 - b.S0) - 2f * (ft + LeafGap) - 0.004f - (n - 1) * DoorSizing.MeetingGap;
            float lw = Mathf.Min(leafSize.x, room / n);
            float total = n * lw + (n - 1) * DoorSizing.MeetingGap;
            float sL0 = mid - total * 0.5f, sL1 = mid + total * 0.5f;       // leaves
            float sI0 = sL0 - LeafGap, sI1 = sL1 + LeafGap;                 // frame rebate faces
            float sO0 = sI0 - ft, sO1 = sI1 + ft;                           // frame outer faces
            float floor = b.Y0;
            float lh = Mathf.Min(leafSize.y, (b.Y1 - b.Y0) - FloorGap - LeafGap - ft - 0.004f);
            float yL0 = floor + FloorGap, yL1 = yL0 + lh, yI = yL1 + LeafGap, yO = yI + ft;
            float lt = b.Door.Design.Thickness / 1000f;
            float wLeafBack = StopFrom - SealT, wLeafFront = wLeafBack - lt, wLeafMid = (wLeafBack + wLeafFront) * 0.5f;
            float wFar = Mathf.Max(b.T, FrameDepth);

            Frame(b, sO0, sO1, sI0, sI1, floor, yI, yO);
            if (!kit)
            {
                if (b.T > FrameDepth + 0.004f) Extensions(b, sI0 + StopOut, sI1 - StopOut, floor, yI - StopOut, FrameDepth, b.T, DoborT);
                var casing = DoorGeo.BarProfile(CasingW, CasingT, 0.0015f, 0.004f);
                if (nearOk) Casings(b, casing, 0f, -1f, sI0 - CasingBack, sI1 + CasingBack, yI + CasingBack, floor);
                if (farOk) Casings(b, casing, wFar, 1f, sI0 + StopOut - CasingBack, sI1 - StopOut + CasingBack, yI - StopOut + CasingBack, floor);
            }

            // one leaf hinged at the `hinge` end; a double door has one at each end, the active one (handles, astragal) at `hinge`
            var doors = new List<Door>();
            for (int i = 0; i < n; i++)
            {
                bool hingeMin = n == 1 ? b.HingeAtMin : i == 0;
                bool active = n == 1 || hingeMin == b.HingeAtMin;
                float a0 = n == 1 || i == 0 ? sL0 : sL1 - lw, a1 = a0 + lw;
                var leaf = new LeafBuilder(b.Door.Design, lw, lh, mats);
                float sAxis = hingeMin ? a0 - 0.0015f : a1 + 0.0015f, wAxis = wLeafFront - 0.006f;
                // butt hinges: the knuckles stand proud of the leaf face by about their radius
                foreach (float hy in leaf.Hinges)
                    DoorHardware.Knuckle(b.Mb, b.L(sAxis, yL0 + hy - 0.05f, wAxis), 0.1f, mats.Metal);
                if (n == 1)
                {
                    float sStrike = hingeMin ? sI1 : sI0, hy = yL0 + leaf.Handle.y;
                    Box(b, sStrike - 0.0012f, sStrike + 0.0012f, hy - 0.05f, hy + 0.05f, wLeafFront + 0.004f, wLeafBack - 0.004f, mats.Chrome);
                }
                var (solid, glass) = LeafBuilders(b, hingeMin, a0, a1, yL0, wLeafMid);
                leaf.Build(solid, glass);
                var hs = b.Door.Design.Handle ?? new HandleSpec();
                var hm = mats.Hardware(HandleFinish(b.Door, hs));
                if (active) DoorHardware.Handles(solid, leaf.Handle, leaf.Thickness, hm, hs.Style);
                string lk = (b.O.Lock ?? b.Door.Model?.Lock ?? "").ToLowerInvariant();
                if (active && lk == "wc")
                    DoorHardware.WcTurn(solid, new Vector2(leaf.Handle.x, leaf.Handle.y - hs.WcDrop / 1000f), leaf.Thickness, hm, mats.Seal,
                                        !string.Equals(hs.Style, "round", System.StringComparison.OrdinalIgnoreCase));
                // astragal only where the catalogue shows one (a model's "astragal": true); PORTA X doubles have none
                if (n > 1 && active && (b.Door.Model?.Astragal ?? false))
                {
                    // astragal («притворная планка» 40 × 8 mm) over the meeting gap, on the swing face
                    float t2 = leaf.Thickness * 0.5f;
                    GrainBox(solid, new Vector3(-0.021f, 0.002f, t2 - 0.0005f), new Vector3(0.019f, leaf.Height - 0.002f, t2 + 0.008f), mats.Finish, 1, b.Off());
                }
                var hinge = b.World(sAxis, yL0, wAxis);
                var along = hingeMin ? b.F.A : -b.F.A;          // from the hinges towards the lock
                var side = b.SwingPlus ? -b.F.N : b.F.N;        // the side the leaf swings to
                float angle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * along, side) > 0f ? OpenAngle : -OpenAngle;
                var d = Pivot(i == 0 ? "Door_" + b.Id : $"Door_{b.Id}_{i + 1}", hinge, solid, glass);
                d.OpenAngle = angle;
                doors.Add(d);
            }
            Link(doors, b.O.Open == true);
        }

        // ================================================================== coupe
        void Sliding(Blk b, bool nearOk, bool farOk)
        {
            var mats = b.Mats;
            var leafSize = DoorSizing.LeafOf(b.O);
            int n = Mathf.Clamp(DoorSizing.LeavesOf(b.O), 1, 2);
            float floor = b.Y0;
            float c0 = b.S0 + LiningGap + LiningT, c1 = b.S1 - LiningGap - LiningT, cTop = b.Y1 - LiningGap - LiningT;
            Lining(b, c0, c1, floor, cTop);
            var casing = DoorGeo.BarProfile(CasingW, CasingT, 0.0015f, 0.004f);
            if (nearOk) Casings(b, casing, 0f, -1f, c0 - 0.005f, c1 + 0.005f, cTop + 0.005f, floor);
            if (farOk) Casings(b, casing, b.T, 1f, c0 - 0.005f, c1 + 0.005f, cTop + 0.005f, floor);

            // the leaves hang in front of the wall face (and the casing) on the swing side, 6 mm clear of the casing
            float lt = b.Door.Design.Thickness / 1000f;
            float wBack = -CasingT - 0.006f, wMid = wBack - lt * 0.5f, wFront = wBack - lt;
            float lw = leafSize.x, lh = leafSize.y;
            float yL0 = floor + 0.006f, yL1 = yL0 + lh;
            float mid = (b.S0 + b.S1) * 0.5f, total = n * lw + (n - 1) * DoorSizing.MeetingGap;
            // rail over the opening, long enough to park the leaves beside it; a board in the finish covers it
            float railLen = n == 1 ? 2f * lw + 0.08f : 2f * total + 0.08f;
            float r0 = n == 1 ? (b.HingeAtMin ? mid + total * 0.5f + 0.04f - railLen : mid - total * 0.5f - 0.04f) : mid - railLen * 0.5f;
            float r1 = r0 + railLen;
            Box(b, r0, r1, yL1 + 0.004f, yL1 + 0.040f, wFront - 0.004f, wBack + 0.004f, mats.Metal);
            GrainBox(b.Mb, b.L(r0 - 0.01f, yL1 - 0.012f, wFront - 0.024f), b.L(r1 + 0.01f, yL1 + 0.072f, wFront - 0.008f), mats.Finish, 0, b.Off());
            Box(b, r0 - 0.01f, r1 + 0.01f, yL1 + 0.040f, yL1 + 0.072f, wFront - 0.008f, 0f, mats.Finish);

            var doors = new List<Door>();
            for (int i = 0; i < n; i++)
            {
                // a single leaf runs towards `hinge`; two part from the middle
                bool towardMin = n == 1 ? b.HingeAtMin : i == 0;
                float a0 = mid - total * 0.5f + i * (lw + DoorSizing.MeetingGap), a1 = a0 + lw;
                // the design's lock edge is the leading edge (the one that closes onto the jamb or the other leaf)
                var (solid, glass) = LeafBuilders(b, towardMin, a0, a1, yL0, wMid);
                var leaf = new LeafBuilder(b.Door.Design, lw, lh, mats);
                leaf.Build(solid, glass);
                DoorHardware.FlushPulls(solid, leaf.Handle, leaf.Thickness, mats.Chrome);
                var center = b.World((a0 + a1) * 0.5f, yL0, wMid);
                var d = Pivot(i == 0 ? "Door_" + b.Id : $"Door_{b.Id}_{i + 1}", center, solid, glass);
                d.Motion = DoorMotion.Slide;
                d.SlideBy = (towardMin ? -b.F.A : b.F.A) * (lw + 0.02f);
                doors.Add(d);
            }
            Link(doors, b.O.Open == true);
        }

        // ================================================================== book fold
        void Folding(Blk b, bool nearOk, bool farOk)
        {
            var mats = b.Mats;
            var leafSize = DoorSizing.LeafOf(b.O);
            int n = DoorSizing.LeavesOf(b.O) >= 4 ? 4 : 2;
            float floor = b.Y0;
            float c0 = b.S0 + LiningGap + LiningT, c1 = b.S1 - LiningGap - LiningT, cTop = b.Y1 - LiningGap - LiningT;
            Lining(b, c0, c1, floor, cTop);
            var casing = DoorGeo.BarProfile(CasingW, CasingT, 0.0015f, 0.004f);
            if (nearOk) Casings(b, casing, 0f, -1f, c0 - 0.005f, c1 + 0.005f, cTop + 0.005f, floor);
            if (farOk) Casings(b, casing, b.T, 1f, c0 - 0.005f, c1 + 0.005f, cTop + 0.005f, floor);

            // top track under the head lining; the panels stand just inside the swing face and fold out to that side
            float lt = b.Door.Design.Thickness / 1000f;
            float wMid = lt * 0.5f + 0.006f;
            // the panels fill the lined opening (the catalogue's 400 mm panels in a 167–170 cm opening): books meet in the
            // middle instead of leaving a gap; never more than 2 cm wider than the leaf size
            float pw = Mathf.Min(leafSize.x + 0.02f, ((c1 - c0) - 0.006f - (n - 1) * 0.003f) / n);
            float y0 = floor + 0.010f, ph = Mathf.Min(leafSize.y, cTop - 0.024f - 0.004f - y0);
            // the crossbar («перекладина») with the track and rollers fills the head down to the panels (they hang from
            // it); it is a board in the door's finish, as the catalogue shows
            float trackH = cTop - (y0 + ph) - 0.003f;
            GrainBox(b.Mb, b.L(c0, cTop - trackH, wMid - 0.018f), b.L(c1, cTop, wMid + 0.018f), mats.Finish, 0, b.Off());
            var side = b.SwingPlus ? -b.F.N : b.F.N;
            var doors = new List<Door>();
            for (int bk = 0; bk < n / 2; bk++)
            {
                // one book at the `hinge` end, or one at each end
                bool fromMin = n == 2 ? b.HingeAtMin : bk == 0;
                float dir = fromMin ? 1f : -1f;
                float jamb = fromMin ? c0 + 0.003f : c1 - 0.003f;
                float p1a = jamb, p1b = jamb + dir * pw, p2a = p1b + dir * 0.003f, p2b = p2a + dir * pw;
                // panel 1 turns at the jamb, panel 2 at the joint between them
                var axis1 = b.World(jamb, y0, wMid);
                var axis2 = b.World(p1b + dir * 0.0015f, y0, wMid);
                var p1 = PanelMeshes(b, pw, ph, Mathf.Min(p1a, p1b), Mathf.Max(p1a, p1b), y0, wMid, fromMin, mats, false);
                var p2 = PanelMeshes(b, pw, ph, Mathf.Min(p2a, p2b), Mathf.Max(p2a, p2b), y0, wMid, fromMin, mats, true);
                var d = Pivot($"Door_{b.Id}{(bk == 0 ? "" : "_" + (bk + 1))}", axis1, p1.solid, p1.glass);
                var second = new GameObject("Fold");
                second.transform.SetParent(d.transform, false);
                second.transform.position = axis2;
                foreach (var (mb, name, shadows) in new[] { (p2.solid, "Leaf", true), (p2.glass, "Leaf_Glass", false) })
                {
                    var go = _c.W.Emit(name, second.transform, mb, castShadows: shadows);
                    if (go == null) continue;
                    go.transform.position = Vector3.zero;   // the meshes are in world space
                    _c.W.MarkDynamic(go);
                }
                var along = fromMin ? b.F.A : -b.F.A;
                d.Motion = DoorMotion.Fold;
                d.FoldSecond = second.transform;
                d.OpenAngle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * along, side) > 0f ? FoldAngle : -FoldAngle;
                doors.Add(d);
            }
            Link(doors, b.O.Open == true);
        }

        /// <summary>One panel of a book: the design at the panel's size, its hinge edge towards the jamb; a pull on the free panel.</summary>
        (MeshBuilder solid, MeshBuilder glass) PanelMeshes(Blk b, float pw, float ph, float a0, float a1, float y0, float wMid, bool hingeMin,
                                                           DoorMaterialSet mats, bool pull)
        {
            var (solid, glass) = LeafBuilders(b, hingeMin, a0, a1, y0, wMid);
            var leaf = new LeafBuilder(b.Door.Design, pw, ph, mats);
            leaf.Build(solid, glass);
            if (pull) DoorHardware.FlushPulls(solid, new Vector2(Mathf.Min(leaf.Handle.x, pw * 0.25f), leaf.Handle.y), leaf.Thickness, mats.Chrome);
            // the fold joint: a dark hinge strip in the gap at panel 1's free edge (x < 0 in leaf space)
            else solid.Box(new Vector3(-0.003f, 0.02f, -leaf.Thickness * 0.3f), new Vector3(0f, ph - 0.02f, leaf.Thickness * 0.3f), mats.Seal);
            return (solid, glass);
        }

        // ================================================================== portal
        void Portal(Blk b, bool nearOk, bool farOk)
        {
            float floor = b.Y0;
            float c0 = b.S0 + LiningGap + LiningT, c1 = b.S1 - LiningGap - LiningT, cTop = b.Y1 - LiningGap - LiningT;
            Lining(b, c0, c1, floor, cTop);
            var casing = DoorGeo.BarProfile(CasingW, CasingT, 0.0015f, 0.004f);
            if (nearOk) Casings(b, casing, 0f, -1f, c0 - 0.005f, c1 + 0.005f, cTop + 0.005f, floor);
            if (farOk) Casings(b, casing, b.T, 1f, c0 - 0.005f, c1 + 0.005f, cTop + 0.005f, floor);
        }

        // ================================================================== parts of the block
        /// <summary>Frame: jambs full height, the head between them; rebate part, stop part and the seal on the stop.</summary>
        void Frame(Blk b, float sO0, float sO1, float sI0, float sI1, float floor, float yI, float yO)
        {
            var fin = b.Mats.Finish;
            foreach (bool minSide in new[] { true, false })
            {
                float so = minSide ? sO0 : sO1, si = minSide ? sI0 : sI1, stopFace = minSide ? sI0 + StopOut : sI1 - StopOut;
                GrainBox(b.Mb, b.L(so, floor, 0f), b.L(si, yO, StopFrom), fin, 1, b.Off());
                GrainBox(b.Mb, b.L(so, floor, StopFrom), b.L(stopFace, yO, FrameDepth), fin, 1, b.Off());
                float sa = minSide ? si + 0.0035f : si - 0.0085f;
                Box(b, sa, sa + 0.005f, floor, yI - StopOut, StopFrom - SealT, StopFrom, b.Mats.Seal);
            }
            GrainBox(b.Mb, b.L(sI0, yI, 0f), b.L(sI1, yO, StopFrom), fin, 0, b.Off());
            GrainBox(b.Mb, b.L(sI0 + StopOut, yI - StopOut, StopFrom), b.L(sI1 - StopOut, yO, FrameDepth), fin, 0, b.Off());
            Box(b, sI0 + 0.0035f, sI1 - 0.0035f, yI - 0.0085f, yI - 0.0035f, StopFrom - SealT, StopFrom, b.Mats.Seal);
        }

        /// <summary>Extension boards («добор») lining the reveal between depths w0 and w1, their faces at sIn0 / sIn1 / yIn.</summary>
        void Extensions(Blk b, float sIn0, float sIn1, float floor, float yIn, float w0, float w1, float t)
        {
            var fin = b.Mats.Finish;
            GrainBox(b.Mb, b.L(sIn0 - t, floor, w0), b.L(sIn0, yIn + t, w1), fin, 1, b.Off());
            GrainBox(b.Mb, b.L(sIn1, floor, w0), b.L(sIn1 + t, yIn + t, w1), fin, 1, b.Off());
            GrainBox(b.Mb, b.L(sIn0, yIn, w0), b.L(sIn1, yIn + t, w1), fin, 0, b.Off());
        }

        /// <summary>Lining of a framed opening: boards over the whole reveal, their faces at the clear opening c0…c1 × floor…cTop.</summary>
        void Lining(Blk b, float c0, float c1, float floor, float cTop) => Extensions(b, c0, c1, floor, cTop, 0f, b.T, LiningT);

        /// <summary>
        /// Casings of one face with the series' system (<see cref="SeriesDef.Block"/>): "t70" flat «Т» 70 × 8, "t70-2" «Т» Тип-2
        /// (70 × 10, cove and bead), "t70-3" «Т» Тип-3 (75 × 8, three flutes); "classic" = fluted pilasters on plinth blocks
        /// (цоколь) with capitals, a frieze between them and a cornice (карниз) over the head; "classic-rosette" = the same with
        /// rosette blocks (розетка) instead of capitals (WOOD CLASSIC); "classic-square" = plain square corner blocks (fine-line).
        /// The frieze between the corner pieces is the fluted casing laid along the head.
        /// The profile argument is ignored when the block names one.
        /// </summary>
        void Casings(Blk b, Vector2[] profile, float wFace, float outward, float sIn0, float sIn1, float yIn, float floor)
        {
            // the profile's "up" = out of the wall face (w decreasing on the swing side, increasing on the far side)
            Vector3 up = (b.L(0f, 0f, wFace + outward) - b.L(0f, 0f, wFace)).normalized;
            var m = b.Mats.Finish;
            string block = (b.Door.Block ?? "t70").ToLowerInvariant();
            bool classic = block.StartsWith("classic"), rosette = block == "classic-rosette", square = block == "classic-square";
            profile = block == "t70-2" ? CasingType2() : block == "t70-3" || classic ? CasingType3() : profile;
            float cw = profile[profile.Length - 1].x, ct = 0f;
            foreach (var q in profile) ct = Mathf.Max(ct, q.y);
            float foot = floor;
            if (classic)
            {
                // plinth blocks: a little wider and thicker than the casing, 200 mm tall
                const float ph = 0.20f;
                foreach (bool left in new[] { true, false })
                {
                    float a = left ? sIn0 + 0.003f : sIn1 - 0.003f, z = left ? a - cw - 0.006f : a + cw + 0.006f;
                    PlateOnWall(b, Mathf.Min(a, z), Mathf.Max(a, z), floor, floor + ph, wFace, outward, ct + 0.005f, m, 1);
                }
                foot = floor + ph;
            }
            if (!classic)
            {
                DoorGeo.Moulding(b.Mb, profile, b.L(sIn0, foot, wFace), b.L(sIn0, yIn, wFace), Vector3.left, up, m, false, true, true, false, Hash01(b.Id, 7) * 2f);
                DoorGeo.Moulding(b.Mb, profile, b.L(sIn1, foot, wFace), b.L(sIn1, yIn, wFace), Vector3.right, up, m, false, true, true, false, Hash01(b.Id, 8) * 2f);
                DoorGeo.Moulding(b.Mb, profile, b.L(sIn0, yIn, wFace), b.L(sIn1, yIn, wFace), Vector3.up, up, m, true, true, false, false, Hash01(b.Id, 9) * 2f);
            }
            else
            {
                // classic: fluted pilasters up to the frieze, capitals (or rosettes) above them, a frieze board between, the cornice
                float fz0 = yIn - 0.004f, fz1 = yIn + cw;
                DoorGeo.Moulding(b.Mb, profile, b.L(sIn0, foot, wFace), b.L(sIn0, fz0, wFace), Vector3.left, up, m, false, false, true, true, Hash01(b.Id, 7) * 2f);
                DoorGeo.Moulding(b.Mb, profile, b.L(sIn1, foot, wFace), b.L(sIn1, fz0, wFace), Vector3.right, up, m, false, false, true, true, Hash01(b.Id, 8) * 2f);
                foreach (bool left in new[] { true, false })
                {
                    float a = left ? sIn0 + 0.004f : sIn1 - 0.004f, z = left ? sIn0 - cw - 0.004f : sIn1 + cw + 0.004f;
                    float s0 = Mathf.Min(a, z), s1 = Mathf.Max(a, z);
                    if (square)
                    {
                        // a plain square corner block
                        PlateOnWall(b, s0, s1, fz0, fz1, wFace, outward, ct + 0.004f, m, 0);
                    }
                    else if (rosette)
                    {
                        // a square block with a turned rosette
                        PlateOnWall(b, s0, s1, fz0, fz1, wFace, outward, ct + 0.004f, m, 0);
                        var c = b.L((s0 + s1) * 0.5f, (fz0 + fz1) * 0.5f, wFace + outward * (ct + 0.004f));
                        float r = (s1 - s0) * 0.36f;
                        using (b.Mb.Place(c, Quaternion.FromToRotation(Vector3.up, up)))
                            b.Mb.Lathe(Vector3.zero, new[]
                            {
                                new Vector2(r, 0f), new Vector2(r * 0.97f, 0.002f), new Vector2(r * 0.78f, 0.0035f), new Vector2(r * 0.62f, 0.0022f),
                                new Vector2(r * 0.5f, 0.004f), new Vector2(r * 0.3f, 0.006f), new Vector2(r * 0.12f, 0.0065f), new Vector2(0f, 0.0066f),
                            }, 32, m);
                    }
                    else
                    {
                        // a capital: a block over the pilaster, a necking bead and an abacus plate on top
                        PlateOnWall(b, s0 + 0.002f, s1 - 0.002f, fz0, fz1 - 0.012f, wFace, outward, ct + 0.003f, m, 1);
                        PlateOnWall(b, s0, s1, fz0 + 0.012f, fz0 + 0.018f, wFace, outward, ct + 0.006f, m, 0);
                        PlateOnWall(b, s0 - 0.004f, s1 + 0.004f, fz1 - 0.012f, fz1, wFace, outward, ct + 0.009f, m, 0);
                    }
                }
                // the frieze between the capitals: the fluted casing laid horizontally (its three flutes run along the head)
                DoorGeo.Moulding(b.Mb, profile, b.L(sIn0 + 0.004f, fz0, wFace), b.L(sIn1 - 0.004f, fz0, wFace), Vector3.up, up, m, false, false, true, true,
                    Hash01(b.Id, 10) * 2f);
            }
            if (classic)
            {
                // cornice: a board with the crown moulding on it, across the whole head, returns at its ends
                float s0 = sIn0 - cw - 0.025f, s1 = sIn1 + cw + 0.025f, yb = yIn + cw;
                PlateOnWall(b, s0 + 0.012f, s1 - 0.012f, yb, yb + 0.05f, wFace, outward, ct + 0.012f, m, 0);
                var crown = Cornice();
                // the crown's profile: x out of the wall, y up; listed with the body on its left
                DoorGeo.Moulding(b.Mb, crown, b.L(s0, yb + 0.05f, wFace), b.L(s1, yb + 0.05f, wFace), up, Vector3.up, m, false, false, true, true,
                    Hash01(b.Id, 11), materialSide: 1);
            }
        }

        /// <summary>A board lying on the wall face: s0…s1 × y0…y1, from the face out by <paramref name="t"/>; grain along y (1) or s (0).</summary>
        void PlateOnWall(Blk b, float s0, float s1, float y0, float y1, float wFace, float outward, float t, Material m, int grain)
        {
            Vector3 p = b.L(s0, y0, wFace), q = b.L(s1, y1, wFace + outward * t);
            GrainBox(b.Mb, p, q, m, grain, b.Off());
        }

        /// <summary>«Наличник Т» Тип-2: 70 × 10 mm — a flat band at the opening, a cove, a bead at the outer edge (x from the opening).</summary>
        static Vector2[] CasingType2() => new[]
        {
            new Vector2(0f, 0f), new Vector2(0f, 0.0085f), new Vector2(0.0015f, 0.0098f), new Vector2(0.004f, 0.010f), new Vector2(0.024f, 0.010f),
            new Vector2(0.029f, 0.0092f), new Vector2(0.035f, 0.0074f), new Vector2(0.042f, 0.0064f), new Vector2(0.050f, 0.0062f),
            new Vector2(0.056f, 0.0068f), new Vector2(0.061f, 0.0079f), new Vector2(0.065f, 0.0082f), new Vector2(0.0685f, 0.0068f),
            new Vector2(0.070f, 0.004f), new Vector2(0.070f, 0f),
        };

        /// <summary>«Наличник Т» Тип-3: 75 × 8 mm with three round flutes, the outer edge rounded (x from the opening).</summary>
        static Vector2[] CasingType3()
        {
            var pts = new List<Vector2> { new Vector2(0f, 0f), new Vector2(0f, 0.0068f), new Vector2(0.0015f, 0.008f) };
            foreach (float c in new[] { 0.021f, 0.037f, 0.053f })
            {
                const float r = 0.0045f, depth = 0.0028f;
                pts.Add(new Vector2(c - r, 0.008f));
                for (int k = 1; k < 8; k++)
                {
                    float a = Mathf.PI * k / 8f;
                    pts.Add(new Vector2(c - r * Mathf.Cos(a), 0.008f - depth * Mathf.Sin(a)));
                }
                pts.Add(new Vector2(c + r, 0.008f));
            }
            pts.Add(new Vector2(0.071f, 0.008f));
            pts.Add(new Vector2(0.0738f, 0.0068f));
            pts.Add(new Vector2(0.075f, 0.004f));
            pts.Add(new Vector2(0.075f, 0f));
            return pts.ToArray();
        }

        /// <summary>Crown moulding of a cornice: x across (out of the wall face), y up; it overhangs the board under it.</summary>
        static Vector2[] Cornice() => new[]
        {
            new Vector2(0f, 0f), new Vector2(0.018f, 0f), new Vector2(0.021f, 0.004f), new Vector2(0.024f, 0.006f), new Vector2(0.030f, 0.012f),
            new Vector2(0.034f, 0.020f), new Vector2(0.036f, 0.026f), new Vector2(0.040f, 0.028f), new Vector2(0.040f, 0.034f), new Vector2(0f, 0.034f),
        };

        static void Box(Blk b, float s0, float s1, float y0, float y1, float w0, float w1, Material m)
        {
            Vector3 p = b.L(s0, y0, w0), q = b.L(s1, y1, w1);
            b.Mb.Box(Vector3.Min(p, q), Vector3.Max(p, q), m);
        }

        /// <summary>
        /// Builders for one leaf: leaf space (x from the lock edge, z towards the swing side) → wall local → world. The leaf
        /// spans a0…a1 along the wall; its hinge (trailing) edge is at a0 when <paramref name="hingeMin"/>.
        /// </summary>
        static (MeshBuilder solid, MeshBuilder glass) LeafBuilders(Blk b, bool hingeMin, float a0, float a1, float yL0, float wMid,
                                                                   bool lockRight = false, bool faceFar = false)
        {
            // x of the drawing runs from the lock edge (from the hinge edge when the design is drawn with the lock on the right)
            bool fromMax = hingeMin != lockRight;
            float sx = fromMax ? -1f : 1f, sz = (b.SwingPlus ? 1f : -1f) * (faceFar ? -1f : 1f);
            var toLocal = new Matrix4x4(
                new Vector4(sx, 0f, 0f, 0f), new Vector4(0f, 1f, 0f, 0f), new Vector4(0f, 0f, sz, 0f),
                new Vector4(fromMax ? a1 : a0, yL0, b.Z(wMid), 1f));
            var toWorld = b.F.ToWorld * toLocal;
            bool flip = toLocal.determinant < 0f;
            return (new MeshBuilder { Transform = toWorld, FlipWinding = flip }, new MeshBuilder { Transform = toWorld, FlipWinding = flip });
        }

        /// <summary>
        /// A moving part on its pivot: the meshes keep world-space vertices, so they sit at -pivot. Moving parts are dynamic
        /// and get a kinematic body for their colliders.
        /// </summary>
        Door Pivot(string name, Vector3 at, MeshBuilder solid, MeshBuilder glass)
        {
            var pivot = new GameObject(name);
            pivot.transform.SetParent(_c.Doors, false);
            pivot.transform.position = at;
            foreach (var (mb, part, shadows) in new[] { (solid, "Leaf", true), (glass, "Leaf_Glass", false) })
            {
                var go = _c.W.Emit(part, pivot.transform, mb, castShadows: shadows);
                if (go == null) continue;
                go.transform.localPosition = -at;
                _c.W.MarkDynamic(go);
            }
            var door = pivot.AddComponent<Door>();
            var body = pivot.AddComponent<Rigidbody>();
            body.isKinematic = true;
            body.useGravity = false;
            return door;
        }

        /// <summary>The leaves of one door open together; <paramref name="open"/> shows them open.</summary>
        static void Link(List<Door> doors, bool open)
        {
            if (doors.Count == 2)
            {
                doors[0].Partner = doors[1];
                doors[1].Partner = doors[0];
            }
            if (open) foreach (var d in doors) d.SetOpen(true, instant: true);
        }

        /// <summary>Box with metric UVs whose u runs along <paramref name="grainAxis"/> (0 x, 1 y, 2 z) on every face it lies in.</summary>
        static void GrainBox(MeshBuilder mb, Vector3 p, Vector3 q, Material m, int grainAxis, Vector2 off)
        {
            Vector3 min = Vector3.Min(p, q), max = Vector3.Max(p, q);
            if (m == null || (max - min).x < 1e-5f || (max - min).y < 1e-5f || (max - min).z < 1e-5f) return;
            for (int axis = 0; axis < 3; axis++)
            for (int sgn = -1; sgn <= 1; sgn += 2)
            {
                int a = (axis + 1) % 3, c = (axis + 2) % 3;
                // u along the grain when it lies in this face, else along the face's first axis
                int ua = grainAxis == a || grainAxis == c ? grainAxis : a, va = ua == a ? c : a;
                var n = Vector3.zero;
                n[axis] = sgn;
                float at = sgn < 0 ? min[axis] : max[axis];
                Vector3 V(float s, float t)
                {
                    var v = Vector3.zero;
                    v[axis] = at; v[a] = s; v[c] = t;
                    return v;
                }
                Vector2 Uv(Vector3 v) => new Vector2(v[ua], v[va]) + off;
                Vector3 c0 = V(min[a], min[c]), c1 = V(max[a], min[c]), c2 = V(max[a], max[c]), c3 = V(min[a], max[c]);
                DoorGeo.Quad(mb, c0, c1, c2, c3, n, Uv(c0), Uv(c1), Uv(c2), Uv(c3), m);
            }
        }

        static float Hash01(string s, int salt)
        {
            unchecked
            {
                uint h = 2166136261u ^ (uint)(salt * 16777619);
                foreach (char ch in s ?? "") { h ^= ch; h *= 16777619; }
                h ^= h >> 13; h *= 0x5bd1e995; h ^= h >> 15;
                return (h & 0xffffff) / (float)0x1000000;
            }
        }
    }
}
