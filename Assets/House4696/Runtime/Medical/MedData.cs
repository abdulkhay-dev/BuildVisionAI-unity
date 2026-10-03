using System.Collections.Generic;

namespace House4696.Medical
{
    /// <summary>
    /// A device of a medical equipment catalogue (Docs/medical-designs.md): the list of its visible parts in millimetres,
    /// x from the left seen from the front, y up from the floor, z from the back (the front — where the patient or the
    /// screen faces — at z = depth). Parts are smooth shells, rounded boxes, tubes, turned parts, lofts, screens, wheels.
    /// </summary>
    public sealed class MedDesign
    {
        public string Id;
        /// <summary>Overall size [W, D, H] mm (width along x, depth along z, height).</summary>
        public float[] Size;
        /// <summary>Material roles of the design: role → material ("shell": "plastic#f2f3f5", "pad": "leather#5b86b8").</summary>
        public Dictionary<string, string> Mats = new Dictionary<string, string>();
        public List<MedPart> Parts = new List<MedPart>();
    }

    public sealed class MedPart
    {
        public string Id;
        /// <summary>
        /// box (rounded box: <see cref="Box"/>, <see cref="R"/>, <see cref="Puff"/>) · cyl (from → to, <see cref="D"/>, taper
        /// <see cref="D2"/>) · tube (a bent tube along <see cref="Path"/>) · lathe (turned: <see cref="Profile"/> [r, h] about
        /// <see cref="Axis"/> at <see cref="At"/>) · sphere (<see cref="At"/>, <see cref="Radii"/> or <see cref="D"/>) · slab (an
        /// outline in a plane, extruded: <see cref="Plane"/>, <see cref="Outline"/> or <see cref="Box"/>, rounded edges
        /// <see cref="R"/>) · loft (rounded-rect <see cref="Sections"/> along an axis) · screen (a box whose face shows a
        /// picture or a dark screen) · caster (a swivel castor at <see cref="At"/>, wheel <see cref="D"/>) · wheel.
        /// </summary>
        public string Kind = "box";
        /// <summary>[x0, y0, z0, x1, y1, z1] mm.</summary>
        public float[] Box;
        /// <summary>Edge radius (box, slab, loft corners), mm.</summary>
        public float R;
        /// <summary>Upholstery: flat faces bulge out by this much (mm).</summary>
        public float Puff;
        /// <summary>Material role of the design or a material ("chrome", "plastic#2f8fd8").</summary>
        public string Mat;
        /// <summary>No collider (cables, small knobs, lamps, decals).</summary>
        public bool Soft;

        // ---- cyl / tube / sphere / lathe / caster
        public float[] From, To, At;
        public float D, D2;
        public List<float[]> Path;
        /// <summary>Tube: round the corners of the path with this bend radius (mm, 0 = sharp).</summary>
        public float Bend;
        public int Sides;
        public bool? Caps;
        /// <summary>Lathe: profile points [r, h] mm from the bottom; axis x, y (default) or z.</summary>
        public List<float[]> Profile;
        public string Axis;
        public float[] Radii;

        // ---- slab
        /// <summary>front (x/y, extruded along z), side (z/y along x), top (x/z along y).</summary>
        public string Plane;
        /// <summary>SVG path in the plane's two axes, absolute mm (curved housings, arched frames, shaped pads).</summary>
        public string Outline;
        /// <summary>Extent along the plane's normal axis [from, to] mm.</summary>
        public float[] W;

        // ---- loft: sections along Axis (default y) — each a rounded rectangle centred at (cx, cz) for y
        public List<MedSection> Sections;

        // ---- screen
        /// <summary>The face that shows the picture: front (default), back, left, right, top.</summary>
        public string Face;
        /// <summary>Picture on the face (a library material fitted to it) and the bezel width round it (mm).</summary>
        public string Print;
        public float Bezel;

        // ---- placement
        /// <summary>A turned part: deg about a line along Axis through About (mm), as in the casegoods format.</summary>
        public MedRot Rot;
        /// <summary>More turns applied after <see cref="Rot"/>, in order (a tilt, then a turn about y…).</summary>
        public List<MedRot> Rots;
        /// <summary>"x": also build the copy mirrored about the middle of the width.</summary>
        public string Mirror;
        /// <summary>Copies: offsets [dx, dy, dz] mm of more copies of the part.</summary>
        public List<float[]> Copies;
        /// <summary>A row of copies: n parts in all, each <see cref="MedRepeat.Step"/> from the previous.</summary>
        public MedRepeat Repeat;

        // ---- bar / sweep / strap / coil
        /// <summary>Cross-section [w, h] mm of a bar, sweep or strap (w across, h "up" of the section frame).</summary>
        public float[] Section;
        /// <summary>Section shape of a sweep: rect (rounded by <see cref="R"/>), oval, round (uses <see cref="D"/>).</summary>
        public string Shape;
        /// <summary>Roll of the section about the path (deg).</summary>
        public float Roll;
        /// <summary>Ribs (corrugated hose): radius bulge in mm every <see cref="Pitch"/> mm along the path.</summary>
        public float Rib, Pitch;
        /// <summary>Coil: turns between from and to, coil diameter = D, wire = D2.</summary>
        public float Turns;

        // ---- loft caps
        /// <summary>Domed ends of a loft: "start", "end" or "both"; <see cref="DomeH"/> mm high (default: half the section).</summary>
        public string Dome;
        public float DomeH;

        // ---- decal
        /// <summary>Decal size [w, h] mm on <see cref="Face"/> centred at <see cref="At"/>.</summary>
        public float[] Size;
    }

    public sealed class MedRepeat
    {
        public int N = 2;
        public float[] Step;
        /// <summary>Step in the part's own turned frame (a row of slots along a tilted face) instead of the design axes.</summary>
        public bool Local;
    }

    public sealed class MedSection
    {
        /// <summary>Position along the loft axis (mm), size across [w, d] and the corner radius; centre offset (mm).</summary>
        public float At, W, D, R;
        public float Cx, Cz;
    }

    public sealed class MedRot
    {
        public string Axis = "x";
        public float Deg;
        public float[] About;
    }

    // ------------------------------------------------------------------ catalogue
    public sealed class MedCatalogFile
    {
        public List<MedModel> Models = new List<MedModel>();
    }

    public sealed class MedModel
    {
        /// <summary>Item id ("xy-k-cdb-ii") and design file (default = id).</summary>
        public string Id, Design;
        public string Code, Name, NameRu, Brand;
        /// <summary>physio, kinesio, robot, table, hydro, pediatric, sensory, other.</summary>
        public string Category;
        /// <summary>floor (default), desk, wall, ceiling.</summary>
        public string Mount;
        public string Note, Source;
    }
}
