using House4696.Core;
using UnityEngine;

namespace House4696.Doors
{
    /// <summary>
    /// Entrance (steel) doors of the catalogue: a steel frame with a threshold, the steel leaf with an outer face (its own
    /// design and finish — powder-coated metal with mouldings, or an MDF panel) and an inner panel (EcoShpon, often with
    /// glass or a mirror), two locks, handles, a peephole and barrel hinges outside; inside the opening is lined with an
    /// extension and cased (catalogue: "Обрамление проёма входных дверей"). The model's leaf size is the whole block
    /// (коробка 860 / 960 × 2050); the opening is 2…4 cm larger.
    /// </summary>
    public sealed partial class DoorBlockBuilder
    {
        // steel block, metres (the frame's visible face and the rim round the inner panel come from the series / model)
        const float SteelDepth = 0.090f, Sill = 0.020f, SteelShell = 0.050f, SteelGap = 0.003f;
        const float DefaultFrameFace = 0.070f, DefaultRim = 0.045f;

        /// <summary>
        /// The steel's finish: the model's or series' <c>steel</c>, else the outer finish when it is powder-coated metal,
        /// else Лунный камень (a door with an MDF outer panel has a dark steel frame and box).
        /// </summary>
        Material SteelOf(ResolvedDoor door, Material outerFinish)
        {
            string id = door.Model?.Steel ?? door.Series?.Steel;
            var f = id != null ? DoorCatalog.Finish(id)
                  : door.Finish != null && door.Finish.Line == "Металл" ? null : DoorCatalog.Finish("moonstone");
            return f != null && _c.Mats.Has(f.Material) ? _c.Mats.Get(f.Material, outerFinish) : outerFinish;
        }

        void Entrance(Blk b, bool nearOk, bool farOk)
        {
            var door = b.Door;
            var block = DoorSizing.LeafOf(b.O);
            float frameFace = (door.Model?.Frame ?? door.Series?.Frame ?? DefaultFrameFace * 1000f) / 1000f;
            float rim = (door.Model?.Rim ?? door.Series?.Rim ?? DefaultRim * 1000f) / 1000f;
            float mid = (b.S0 + b.S1) * 0.5f, floor = b.Y0;
            float bw = Mathf.Min(block.x, b.S1 - b.S0 - 0.01f), bh = Mathf.Min(block.y, b.Y1 - b.Y0 - 0.005f);
            float sB0 = mid - bw * 0.5f, sB1 = mid + bw * 0.5f, yTop = floor + bh;
            float sL0 = sB0 + frameFace + SteelGap, sL1 = sB1 - frameFace - SteelGap;
            float yL0 = floor + Sill + SteelGap, yL1 = yTop - frameFace - SteelGap;
            float lw = sL1 - sL0, lh = yL1 - yL0;

            // materials: the outer face and the steel in the outer finish, the inner panel in the inner finish
            var outer = b.Mats;
            var inner = Materials(new ResolvedDoor { Series = door.Series, Model = door.Model, Design = door.Inner, Finish = door.FinishIn ?? door.Finish, Glass = door.Glass });
            var steel = SteelOf(door, outer.Finish);

            // ---- steel frame and threshold, flush with the face the door opens to
            GrainBox(b.Mb, b.L(sB0, floor, 0f), b.L(sB0 + frameFace, yTop, SteelDepth), steel, 1, b.Off());
            GrainBox(b.Mb, b.L(sB1 - frameFace, floor, 0f), b.L(sB1, yTop, SteelDepth), steel, 1, b.Off());
            GrainBox(b.Mb, b.L(sB0 + frameFace, yTop - frameFace, 0f), b.L(sB1 - frameFace, yTop, SteelDepth), steel, 0, b.Off());
            Box(b, sB0 + frameFace, sB1 - frameFace, floor, floor + Sill, 0f, SteelDepth, outer.Metal);
            // rubber seals in the gaps
            Box(b, sL0 - SteelGap, sL0 - 0.0005f, yL0, yL1, 0.012f, 0.03f, outer.Seal);
            Box(b, sL1 + 0.0005f, sL1 + SteelGap, yL0, yL1, 0.012f, 0.03f, outer.Seal);

            // ---- inside: extension from the frame to the far face and the casing (the facade side keeps its reveal)
            float wFar = Mathf.Max(b.T, SteelDepth);
            if (b.T > SteelDepth + 0.004f)
                Extensions(b, sB0 + 0.004f, sB1 - 0.004f, floor, yTop - 0.004f, SteelDepth, b.T, DoborT);
            if (farOk)
            {
                var ib = new Blk
                {
                    F = b.F, O = b.O, Door = new ResolvedDoor { Series = new SeriesDef { Block = "t70" }, Finish = door.FinishIn ?? door.Finish },
                    Mats = inner, T = b.T, S0 = b.S0, S1 = b.S1, Y0 = b.Y0, Y1 = b.Y1, SwingPlus = b.SwingPlus, HingeAtMin = b.HingeAtMin, Id = b.Id, Mb = b.Mb,
                };
                Casings(ib, DoorGeo.BarProfile(CasingW, CasingT, 0.0015f, 0.004f), wFar, 1f, sB0 - 0.004f, sB1 + 0.004f, yTop - 0.004f, floor);
            }

            // ---- the leaf: steel shell, outer face, inner panel
            float tOut = door.Design.Thickness / 1000f, tIn = (door.Inner ?? door.Design).Thickness / 1000f;
            float wFront = 0.004f, wShell0 = wFront + tOut, wShell1 = wShell0 + SteelShell, wBack = wShell1 + tIn;
            bool hingeMin = b.HingeAtMin;
            var (solid, glass) = LeafBuilders(b, hingeMin, sL0, sL1, yL0, (wFront + wBack) * 0.5f);
            // the shell in leaf space (x from the lock edge, z towards the outside face)
            float zMid = (wFront + wBack) * 0.5f;
            float zs0 = zMid - wShell1, zs1 = zMid - wShell0;
            GrainBox(solid, new Vector3(0f, 0f, zs0), new Vector3(lw, lh, zs1), steel, 1, b.Off());
            var outerLeaf = new LeafBuilder(door.Design, lw, lh, outer);
            var innerLeaf = new LeafBuilder(door.Inner ?? door.Design, lw - 2f * rim, lh - 2f * rim, inner);
            var (os, og) = LeafBuilders(b, hingeMin, sL0, sL1, yL0, wFront + tOut * 0.5f, door.Design.LockRight);
            outerLeaf.Build(os, og);
            var innerDesign = door.Inner ?? door.Design;
            var (ins, ing) = LeafBuilders(b, hingeMin, sL0 + rim, sL1 - rim, yL0 + rim, wBack - tIn * 0.5f, innerDesign.LockRight, faceFar: true);
            innerLeaf.Build(ins, ing);
            // hardware through the whole leaf: handles, the second lock and the main lock's cylinder, the peephole
            float total = wBack - wFront;
            var h = outerLeaf.Handle;
            var through = LeafBuilders(b, hingeMin, sL0, sL1, yL0, zMid);
            var hs = door.Design.Handle ?? new HandleSpec();
            var hm = outer.Hardware(HandleFinish(door, hs));
            bool plate = string.Equals(hs.Style, "plate", System.StringComparison.OrdinalIgnoreCase);
            if (plate) DoorHardware.PlateHandles(through.solid, h, total, hm, outer.Seal);
            else DoorHardware.Handles(through.solid, h, total, hm, hs.Style);
            // locks: the upper (lever) lock and the lower cylinder; a plate handle carries the lower one itself
            int locks = Mathf.Clamp(door.Model?.Locks ?? door.Series?.Locks ?? 2, 1, 2);
            string esc = (door.Model?.Escutcheon ?? door.Series?.Escutcheon ?? "round").ToLowerInvariant();
            bool square = esc == "square", oval = esc == "oval";
            if (locks > 1) DoorHardware.Escutcheons(through.solid, new Vector2(h.x, h.y + 0.23f), total, hm, square, oval);
            if (!plate) DoorHardware.Escutcheons(through.solid, new Vector2(h.x, h.y - 0.11f), total, hm, square, oval);
            DoorHardware.Peephole(through.solid, new Vector2(lw * 0.5f, Mathf.Min(1.5f, lh - 0.25f)), total, outer.Chrome);

            // barrel hinges on the outside, at the hinge edge
            float sAxis = hingeMin ? sL0 - SteelGap * 0.5f : sL1 + SteelGap * 0.5f;
            foreach (float hy in new[] { 0.25f, lh - 0.35f })
                DoorHardware.Knuckle(b.Mb, b.L(sAxis, yL0 + hy, -0.004f), 0.12f, outer.Metal);

            var hinge = b.World(sAxis, yL0, -0.004f);
            var along = hingeMin ? b.F.A : -b.F.A;
            var side = b.SwingPlus ? -b.F.N : b.F.N;
            float angle = Vector3.Dot(Quaternion.AngleAxis(90f, Vector3.up) * along, side) > 0f ? OpenAngle : -OpenAngle;
            // all the leaf's parts on one pivot
            var d = Pivot("Door_" + b.Id, hinge, solid, glass);
            foreach (var (mb, name, shadows) in new[] { (os, "Leaf_Outer", true), (og, "Leaf_OuterGlass", false), (ins, "Leaf_Inner", true),
                                                        (ing, "Leaf_InnerGlass", false), (through.solid, "Leaf_Hardware", true) })
            {
                var go = _c.W.Emit(name, d.transform, mb, castShadows: shadows);
                if (go == null) continue;
                go.transform.localPosition = -hinge;
                _c.W.MarkDynamic(go);
            }
            d.OpenAngle = angle;
            if (b.O.Open == true) d.SetOpen(true, instant: true);
        }
    }
}
