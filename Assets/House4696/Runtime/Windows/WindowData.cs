using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace House4696.Windows
{
    /// <summary>
    /// A window design (Docs/window-designs.md): the frame's outline, its members and the sashes, drawn in millimetres at a
    /// reference size (x from the left edge seen from outside, y up from the bottom); resized by fixed zones like doors.
    /// </summary>
    public sealed class WindowDesign
    {
        public string Id, Name;
        public float[] Ref = { 1200f, 1400f };
        /// <summary>Outer outline of the frame: rect / arch / ellipse / path (Shape2D); null = the whole reference rectangle.</summary>
        public JToken Shape;
        public List<float[]> FixX, FixY;
        public FrameSpec Frame = new FrameSpec();
        public SashSpec Sash = new SashSpec();
        public WindowNode Layout = new WindowNode();
        /// <summary>Glass of the panes unless a cell says otherwise: clear, frosted, tinted, mirror.</summary>
        public string Glass = "clear";
        public SillSpec Sill = new SillSpec();
        /// <summary>A surround on the facade round the window (stone architrave, wooden portal); null = none.</summary>
        public SurroundSpec Surround;
        /// <summary>Things on the window: awning, louvres, blinds, shelf (see the docs).</summary>
        public List<JObject> Extras;

        public float RefW => Ref != null && Ref.Length > 0 ? Ref[0] : 1200f;
        public float RefH => Ref != null && Ref.Length > 1 ? Ref[1] : 1400f;
    }

    public sealed class FrameSpec
    {
        /// <summary>Visible face width of the frame (mm) and its depth in the wall.</summary>
        public float Width = 70f, Depth = 70f;
        /// <summary>The frame's outer face behind the facade's face, mm (the reveal outside).</summary>
        public float Inset = 120f;
        /// <summary>Rounding of the frame's edges, mm.</summary>
        public float Radius = 2f;
    }

    public sealed class SashSpec
    {
        /// <summary>Visible face width of a sash (mm), its depth, and how far its outer face sits behind the frame's.</summary>
        public float Width = 60f, Depth = 70f, Offset = 6f;
        /// <summary>How far sliding sashes overlap each other (interlock), mm.</summary>
        public float Overlap = 30f;
    }

    /// <summary>A node of the window's layout: a split into cells by mullions / transoms, or a cell (glass, sash).</summary>
    public sealed class WindowNode
    {
        /// <summary>"x": vertical mullions at x = At[i]; "y": horizontal transoms at y = At[i]; null = a cell.</summary>
        public string Split;
        public float[] At;
        /// <summary>Width of the mullions (mm): a number for every cut, or an array per cut; default 80. 0 = sashes meet (sliding).</summary>
        public JToken Mullion;
        public List<WindowNode> Cells;

        /// <summary>Cell: "fixed" (glass in the frame), "turn" / "tilt-turn" (sash on side hinges), "tilt" (hinged at the bottom), "slide".</summary>
        public string Sash;
        /// <summary>Turn sashes: hinge side seen from inside ("left" / "right"); slide: the way the sash slides ("left" / "right").</summary>
        public string Hinge;
        /// <summary>Glass of this cell (overrides the design's).</summary>
        public string Glass;
        public BarsSpec Bars;
        /// <summary>Frosted band from the bottom of the pane up to this height, mm (privacy).</summary>
        public float? Frosted;
    }

    /// <summary>Glazing bars (раскладка) across a cell's glass at reference positions; their width stays on any size.</summary>
    public sealed class BarsSpec
    {
        public float[] X, Y;
        public float Width = 25f;
        /// <summary>Bars as a regular grid instead of positions: columns × rows.</summary>
        public int? Cols, Rows;
    }

    public sealed class SillSpec
    {
        /// <summary>Outside: "metal" (отлив), "stone" (a stone sill), "none"; inside: "board" (подоконник), "none".</summary>
        public string Outside = "metal", Inside = "board";
        /// <summary>Outside: how far it stands out of the facade; inside: out of the wall's inner face, mm.</summary>
        public float Overhang = 40f, InsideOverhang = 50f;
        /// <summary>Stone sill thickness and how far it runs past the opening on each side, mm.</summary>
        public float Thickness = 50f, Ears = 40f;
        public string Material, InsideMaterial;
    }

    public sealed class SurroundSpec
    {
        /// <summary>Band width round the opening, how far it stands out of the facade, mm; material: library id or "frame" (the window's finish).</summary>
        public float Width = 150f, Depth = 40f;
        public string Material = "sandstone_light";
        /// <summary>Extra height of the head (a cornice-like lintel), mm.</summary>
        public float Head;
    }

    public sealed class WindowCatalogFile
    {
        public List<WindowFinish> Finishes = new List<WindowFinish>();
        public List<WindowModel> Models = new List<WindowModel>();
    }

    public sealed class WindowFinish
    {
        public string Id, Name;
        /// <summary>Library material, tintable "name#rrggbb" allowed ("metal_painted#2f3236").</summary>
        public string Material;
        public string Color;
    }

    public sealed class WindowModel
    {
        public string Id, Name, Design;
        /// <summary>Catalogue number (1–48), section (home / tower / shop / clinic), style and the catalogue's description.</summary>
        public int Number;
        public string Section, Style, Note;
        /// <summary>Default finish and the finishes it comes in (null = any of the catalogue).</summary>
        public string Finish;
        public List<string> Finishes;
        /// <summary>Typical size [width, height] m and sill height m, for a house that does not say.</summary>
        public float[] Size;
        public float? SillHeight;
        public string Photo;
    }
}
