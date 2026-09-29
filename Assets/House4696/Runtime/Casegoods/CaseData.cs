using System.Collections.Generic;

namespace House4696.Casegoods
{
    /// <summary>
    /// Case furniture of a manufacturer's catalogue (Docs/casegoods-designs.md): a module is the list of its real parts —
    /// the panels of the assembly instruction's cut list at their positions, fronts, mouldings, glass, legs, handles — in
    /// millimetres: x from the left seen from the front, y up from the floor, z from the back (the front at z = depth).
    /// Doors and drawers are groups of parts that move.
    /// </summary>
    public sealed class CaseDesign
    {
        public string Id;
        /// <summary>Overall size [L, B, H] mm as the catalogue gives it (width along x, depth along z, height).</summary>
        public float[] Size;
        public List<CasePart> Parts = new List<CasePart>();
        public List<CaseMove> Moves = new List<CaseMove>();
    }

    public sealed class CasePart
    {
        /// <summary>Unique id inside the module (moves name it); default = <see cref="N"/>.</summary>
        public string Id;
        /// <summary>Number of the part in the instruction's cut list ("1", "6.2", "14.1"); null for hardware.</summary>
        public string N;
        /// <summary>
        /// panel (chipboard, body colour) · back (hardboard) · front (door / drawer front, front colour) · moulding (a profile
        /// swept along <see cref="Path"/>) · glass · mirror · tube (round bar along the box's long axis: legs, hanger rails)
        /// · handle · light (LED) · mattress.
        /// </summary>
        public string Kind = "panel";
        /// <summary>[x0, y0, z0, x1, y1, z1] mm.</summary>
        public float[] Box;
        /// <summary>Material role: body, front, back, white, gold, chrome, black, glass, mirror, led, or a library name ("name#rrggbb").</summary>
        public string Mat;
        /// <summary>Rounding of the edges, mm (panel 1, front 1.5 by default).</summary>
        public float? Edge;
        /// <summary>
        /// rect (default) · circle / ring (an ellipse in the box, cut through its thinnest axis; ring has a hole
        /// <see cref="Inner"/> mm across) · path (<see cref="Outline"/>: an SVG path in the plane across the thinnest axis,
        /// absolute mm — arches, shaped headboards, table tops). <see cref="Radius"/> rounds the corners of a rect.
        /// </summary>
        public string Shape;
        public float? Inner;
        public string Outline;
        public float Radius;
        /// <summary>Wood grain / texture direction on a panel: x, y or z (default: the longest side).</summary>
        public string Grain;

        // ---- front
        /// <summary>A glazed front: frame width and glass rebate; null = a solid front.</summary>
        public FrontGlass Glass;
        /// <summary>Face of a front or panel: flat (default), fluted, frame, grooves, diamond — see <see cref="FaceSpec"/>.</summary>
        public FaceSpec Face;
        /// <summary>A printed picture over the whole front face: a library material fitted to the face (kids' fronts, photo prints).</summary>
        public string Print;

        // ---- rod (legs, frames, rails): a round or square bar between two points, tapering from D to D2
        public float[] From, To;
        public float D2;
        /// <summary>round (default) or square section of a rod.</summary>
        public string Section;

        // ---- soft (upholstered panel)
        /// <summary>Vertical channels across the panel (0 = none) and a grid of buttoned tufts [columns, rows].</summary>
        public int Channels;
        public int[] Tufts;

        // ---- moulding
        /// <summary>Profile id of the catalogue (catalog.json "profiles").</summary>
        public string Profile;
        /// <summary>Plane of the path: front (default, x/y at z = <see cref="Z"/>), top (x/z at y), left / right (z/y at x).</summary>
        public string Plane;
        /// <summary>The moulding's outer edge: points [a, b] in the plane (mm); closed paths are frames with mitred corners.</summary>
        public List<float[]> Path;
        public bool Closed;
        /// <summary>Base of the profile in the plane's normal axis (front plane: the z of the face it sits on).</summary>
        public float Z;
        /// <summary>Open paths: +1 when the profile's width lies to the left of travel, -1 to the right; closed paths lie inside.</summary>
        public int Side = 1;
        /// <summary>Cut-list parts this moulding (or hardware) stands for: "8", "9", "9.1"…</summary>
        public List<string> Covers;

        // ---- handle
        /// <summary>ring-half (a flat half ring; <see cref="Dir"/> = where its arc bulges: up, down, left, right), knob, bar.</summary>
        public string Model;
        /// <summary>Centre point [x, y] on the front face (the half ring: the middle of its cut line).</summary>
        public float[] At;
        public string Dir;
        /// <summary>Handle size: outer diameter / length, band width, thickness, stand-off from the face (mm).</summary>
        public float D, Band, T, Standoff;
    }

    public sealed class FrontGlass
    {
        /// <summary>Width of the front's frame round the glass (mm), how far the glass hides under it, glass thickness, tint.</summary>
        public float Frame = 50f, Rebate = 10f, T = 4f;
        /// <summary>clear, satin (frosted), bronze, grey, black, mirror.</summary>
        public string Tint = "clear";
        /// <summary>Glazing bars (muntins) across the glass at these x / y (absolute mm), <see cref="BarW"/> wide.</summary>
        public float[] BarsX, BarsY;
        public float BarW = 18f;
    }

    /// <summary>
    /// Face of a board. fluted: ribs along <see cref="Dir"/> (y = vertical) every <see cref="Pitch"/> mm, <see cref="Depth"/>
    /// deep, convex "reed" or concave "groove" (<see cref="Flute"/>), <see cref="Gap"/> flat between them. frame: a milled
    /// frame <see cref="Border"/> wide round a panel sunk <see cref="Depth"/>, its inner edge rounded <see cref="R"/> (a
    /// moulding <see cref="Profile"/> may run round the panel). grooves: milled lines <see cref="Lines"/> [[a0, b0, a1, b1], …]
    /// (absolute mm in the front plane), <see cref="W"/> wide, <see cref="Depth"/> deep, V or U (<see cref="Flute"/>).
    /// diamond: pyramids in cells <see cref="Cell"/> [w, h], <see cref="Depth"/> high, inside <see cref="Margin"/>.
    /// </summary>
    public sealed class FaceSpec
    {
        public string Type = "flat";
        public string Dir = "y", Flute = "reed", Profile;
        public float Pitch = 20f, Depth = 3f, Gap = 0f, Border = 60f, R = 2f, W = 4f, Margin = 0f;
        public float[] Cell;
        public List<float[]> Lines;
    }

    public sealed class CaseMove
    {
        /// <summary>
        /// door (turns about a vertical hinge line), flap (about a horizontal one: hinge "bottom" drops down, "top" lifts
        /// up), drawer (slides out along z), slide (a sliding / coupe door: moves by <see cref="By"/>).
        /// </summary>
        public string Type = "door";
        public string Name;
        public List<string> Parts = new List<string>();
        /// <summary>Door: hinge side "left" / "right"; flap: "bottom" / "top".</summary>
        public string Hinge = "left";
        /// <summary>The hinge line: a door [x, z], a flap [y, z] mm (default: the front's outer front edge on the hinge side).</summary>
        public float[] Axis;
        public float Angle = 100f;
        /// <summary>Drawer: how far it slides out, mm.</summary>
        public float Travel = 300f;
        /// <summary>Slide: the offset when open [dx, dy, dz] mm.</summary>
        public float[] By;
    }

    // ------------------------------------------------------------------ catalogue
    public sealed class CaseCatalogFile
    {
        public List<CaseFinish> Finishes = new List<CaseFinish>();
        public Dictionary<string, CaseProfile> Profiles = new Dictionary<string, CaseProfile>();
        public List<CaseCollection> Collections = new List<CaseCollection>();
        public List<CaseModel> Models = new List<CaseModel>();
    }

    /// <summary>A colour of a collection: materials for the body (chipboard), the fronts (painted MDF) and the back.</summary>
    public sealed class CaseFinish
    {
        public string Id, Name;
        /// <summary>Library materials ("name#rrggbb" tints): body, front (default = body), back (default = body).</summary>
        public string Body, Front, Back;
        /// <summary>
        /// More roles of a two- or three-decor finish (a carcass in oak with grey fronts and a black frame): role → library
        /// material; parts name the role in "mat" (top, accent, frame, fabric, …).
        /// </summary>
        public Dictionary<string, string> Roles;
        /// <summary>The catalogue swatch colour (for checks).</summary>
        public string Swatch;
    }

    /// <summary>A moulding profile: points (u across, v up from the face) mm, from the outer edge (u = 0) inwards.</summary>
    public sealed class CaseProfile
    {
        public string Name;
        public List<float[]> Pts = new List<float[]>();
    }

    public sealed class CaseCollection
    {
        public string Id, Name, Brand;
        public List<string> Finishes;
        /// <summary>Handles / legs finish role of the collection (gold, chrome, black).</summary>
        public string Metal;
        public string Note;
    }

    public sealed class CaseModel
    {
        /// <summary>Item model id (collection-code: "flora-0-01") and the design file (default = id).</summary>
        public string Id, Design;
        /// <summary>Catalogue code ("П6.980.0.01"), name, collection, item category (storage, bedroom, living, …).</summary>
        public string Code, Name, Collection, Category;
        public float[] Size;
        /// <summary>floor (default: stands with its back to a wall) or wall (hangs: a mirror; the origin is its middle).</summary>
        public string Mount;
        /// <summary>Default finish and the ones it comes in (default: the collection's).</summary>
        public string Finish;
        public List<string> Finishes;
        /// <summary>Assembly instruction file (tools/casegoods/reference/…/is/), catalogue page, notes.</summary>
        public string Is, Note;
        public int Page;
    }
}
