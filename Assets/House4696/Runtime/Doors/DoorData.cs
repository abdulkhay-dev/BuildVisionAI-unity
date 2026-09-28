using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace House4696.Doors
{
    /// <summary>
    /// A door design (Resources/Doors/Designs/&lt;id&gt;.json): the leaf as the catalogue photo shows it, drawn at
    /// <see cref="Ref"/> size in millimetres, x from the lock edge. Format: Docs/door-designs.md.
    /// </summary>
    public sealed class DoorDesign
    {
        /// <summary>A copy with other hinge positions (a model's own hinges, e.g. a ready-made block's).</summary>
        public DoorDesign WithHinges(float[] hinges)
        {
            var d = (DoorDesign)MemberwiseClone();
            d.Hinges = hinges;
            return d;
        }

        public string Id, Name;
        public float[] Ref = { 800f, 2000f };
        public float Thickness = 36f;
        /// <summary>
        /// Which side of the drawing the lock edge is on: "left" (default — the catalogue photo of the face the door opens
        /// to) or "right" (an entrance door's inner panel, photographed from inside). Coordinates stay as drawn.
        /// </summary>
        public string Lock = "left";
        public bool LockRight => string.Equals(Lock, "right", System.StringComparison.OrdinalIgnoreCase);
        /// <summary>Intervals [a, b] (ref mm) that keep their length when the leaf changes width / height.</summary>
        public List<float[]> FixX = new List<float[]>(), FixY = new List<float[]>();
        public EdgeSpec Edge = new EdgeSpec();
        public HandleSpec Handle = new HandleSpec();
        /// <summary>Hinge centres above the leaf bottom (ref mm); null = 250 from the bottom and from the top.</summary>
        public float[] Hinges;
        public LayoutNode Layout;
        /// <summary>Free features over the layout (grooves, inlays, panels, mouldings…); parsed by their builders.</summary>
        public List<JObject> Parts = new List<JObject>();

        public float RefW => Ref != null && Ref.Length > 0 ? Ref[0] : 800f;
        public float RefH => Ref != null && Ref.Length > 1 ? Ref[1] : 2000f;
    }

    public sealed class EdgeSpec
    {
        /// <summary>Radius of the leaf's outer edges (film wrapped round the edge), mm.</summary>
        public float Radius = 2f;
        /// <summary>Null = the leaf's finish; "metal" = aluminium edge (ALU models).</summary>
        public string Material;
    }

    public sealed class HandleSpec
    {
        /// <summary>Handle axis above the leaf bottom and from the lock edge, mm.</summary>
        public float Y = 1000f, X = 60f;
        /// <summary>"square" — lever on a square rose (modern series); "round" — curved lever on a round rose (classic, laminated).</summary>
        public string Style = "square";
        /// <summary>chrome · satin (matte chrome) · gold · bronze · black.</summary>
        public string Finish = "chrome";
        /// <summary>Bathroom thumb-turn ("WC") below the handle axis, mm.</summary>
        public float WcDrop = 90f;
    }

    /// <summary>A node of the layout tree: a rectangle that splits into cells or is one piece (board or glass).</summary>
    public sealed class LayoutNode
    {
        /// <summary>"x" = cut with vertical lines at x = <see cref="At"/>; "y" = horizontal lines; null = a piece.</summary>
        public string Split;
        public float[] At;
        /// <summary>Separator at every cut: a string ("joint", "glass:10", …) or an array with one per cut.</summary>
        public JToken Sep;
        public List<LayoutNode> Cells;
        public float? Level;
        public string Grain;
        public float? Radius;
        public string Material;
        /// <summary>true = the door's glass, a string = a glass role ("mirror", "black"…); null = a board.</summary>
        public JToken Glass;
        /// <summary>
        /// Thickness of the glass panes below this node, mm (inherited): 8 = triplex, a leaf's full thickness minus a
        /// little = glass flush with both faces (Глейс, lacobel of PORTA-51). Null = the glass's own (4, triplex 8).
        /// </summary>
        public float? Pane;
    }

    // ------------------------------------------------------------------ catalogue
    public sealed class DoorCatalogFile
    {
        public List<FinishDef> Finishes = new List<FinishDef>();
        public List<GlassDef> Glass = new List<GlassDef>();
        public List<SeriesDef> Series = new List<SeriesDef>();
    }

    public sealed class FinishDef
    {
        public string Id, Name, Line;
        /// <summary>Library material id ("door_cappuccino_veralinga").</summary>
        public string Material;
        /// <summary>Mean colour of the finish (#rrggbb): fallback tint when the texture is missing.</summary>
        public string Color;
        /// <summary>
        /// Two-tone finishes (Этюд "Ф-27/Ф-01"): library material of the parts a design paints with role "finish2";
        /// <see cref="Color2"/> is its fallback tint. Single finishes leave both empty (finish2 = finish).
        /// </summary>
        public string Material2, Color2;
    }

    public sealed class GlassDef
    {
        public string Id, Name;
        /// <summary>How it renders: satin, clear, mirror, black, lacobel-beige / -white / -smoke (WP / WW / S).</summary>
        public string Role;
        /// <summary>
        /// Patterned or art glass: a library material (category "doorglass", transparent where the glass is clear) instead of
        /// the role's plain one; <see cref="Fit"/> stretches its picture over each pane, otherwise the pattern tiles in metres.
        /// </summary>
        public string Material;
        public bool Fit;
        /// <summary>Pane thickness, mm (triplex 8).</summary>
        public float? Thickness;
        /// <summary>
        /// Bevelled border ("Алмазная грань"), mm visible inside the bead, on every shaped pane of the door's own glass
        /// (a design's glass part may set its own <c>facet</c>).
        /// </summary>
        public float? Facet;
    }

    public sealed class SeriesDef
    {
        public string Id, Name, Line;
        /// <summary>Position in the catalogue (the manufacturer's page order); series files sort by it.</summary>
        public int Order;
        /// <summary>interior (swing), entrance, sliding, folding, portal.</summary>
        public string Kind = "interior";
        /// <summary>Frame / casing / extension system of the door block ("t70").</summary>
        public string Block = "t70";
        public List<string> Finishes = new List<string>();
        public List<string> Glass = new List<string>();
        /// <summary>Entrance doors: finishes of the inner panel (the outer ones are <see cref="Finishes"/>).</summary>
        public List<string> FinishesIn;
        public List<ModelDef> Models = new List<ModelDef>();
        /// <summary>Handle finish by door finish where the catalogue changes it with the colour ("real-oak": "bronze").</summary>
        public Dictionary<string, string> Handles;
        /// <summary>Entrance doors: block sizes sold, [width, height] m (catalogue "205/86" = [0.86, 2.05]); null = 86/96 × 205.</summary>
        public List<float[]> Sizes;
        /// <summary>Entrance doors: finish of the steel (frame, leaf box, rim round the inner panel); null = the outer finish when it is metal, else Лунный камень.</summary>
        public string Steel;
        /// <summary>Entrance doors: visible steel frame face outside, mm (70), and the steel rim round the inner panel, mm (45).</summary>
        public float? Frame, Rim;
        /// <summary>Entrance doors: locks (1 or 2) and their escutcheons ("round" / "square").</summary>
        public int? Locks;
        public string Escutcheon;

        public bool IsEntrance => string.Equals(Kind, "entrance", System.StringComparison.OrdinalIgnoreCase);
    }

    public sealed class ModelDef
    {
        public string Id, Name, Design, Photo;
        /// <summary>Entrance doors: the design of the inner panel (<see cref="Design"/> is the outer face).</summary>
        public string Inner;
        /// <summary>Lock of the model: "wc" = a bathroom thumb-turn under the handle (catalogue "1П-02 WC").</summary>
        public string Lock;
        /// <summary>The model's own frame / casing system when it differs from the series' (a classic model with a cornice).</summary>
        public string Block;
        /// <summary>Leaves of a ready-made door block ("2П-03" = 2) when the opening does not say; null = 1 (folding: 2).</summary>
        public int? Leaves;
        /// <summary>Hinge centres of this model when they differ from its design's (a ready-made block's hinges), mm.</summary>
        public float[] Hinges;
        /// <summary>A double door of this model has an astragal («притворная планка») on the active leaf.</summary>
        public bool? Astragal;
        /// <summary>Handle finish by door finish; null = the series'.</summary>
        public Dictionary<string, string> Handles;
        /// <summary>Entrance doors: the model's own sizes / steel / frame / rim / locks / escutcheon; null = the series'.</summary>
        public List<float[]> Sizes;
        public string Steel;
        public float? Frame, Rim;
        public int? Locks;
        public string Escutcheon;
        /// <summary>Entrance doors: finishes of the inner panel; null = the series'.</summary>
        public List<string> FinishesIn;
        /// <summary>Glass options of the model; null = the series'.</summary>
        public List<string> Glass;
        /// <summary>Finishes of the model; null = the series'.</summary>
        public List<string> Finishes;
    }
}
