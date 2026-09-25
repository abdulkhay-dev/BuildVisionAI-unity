using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace House4696.Model
{
    /// <summary>
    /// A house project as data (<c>*.house.json</c>): the single source the generator builds geometry from and
    /// the MCP tools edit. Units are meters and degrees. World frame: X to the right, Y up (0 = finished grade),
    /// Z "north". Plan points are <c>[x, z]</c>; heights of walls/openings are relative to their level's floor
    /// unless stated otherwise. Everything optional has a sensible default so an AI can describe a house briefly.
    /// </summary>
    public sealed class HouseDocument
    {
        public const string CurrentFormat = "house/1";

        public string Format = CurrentFormat;
        public HouseMeta Meta = new HouseMeta();
        public SiteDef Site = new SiteDef();
        public List<LevelDef> Levels = new List<LevelDef>();
        public List<WallDef> Walls = new List<WallDef>();
        public List<OpeningDef> Openings = new List<OpeningDef>();
        public List<RoomDef> Rooms = new List<RoomDef>();
        public List<RoofDef> Roofs = new List<RoofDef>();
        public List<StairDef> Stairs = new List<StairDef>();
        public List<ElementDef> Elements = new List<ElementDef>();
        public List<ItemDef> Items = new List<ItemDef>();
        public List<LightDef> Lights = new List<LightDef>();
        public List<ViewDef> Views = new List<ViewDef>();
    }

    public sealed class HouseMeta
    {
        public string Name = "Новый дом";
        public string Description;
        public string Author;
        public string Created;
        public string Modified;
    }

    public enum LandscapePreset { None, Lawn, Garden, Catalog4696 }

    public sealed class SiteDef
    {
        public LandscapePreset Landscape = LandscapePreset.Garden;
        /// <summary>Sun direction: azimuth from north (+Z) clockwise, elevation above the horizon.</summary>
        public float SunAzimuth = 175f, SunElevation = 33f;
    }

    /// <summary>A storey. <see cref="Elevation"/> = finished floor above grade; <see cref="Height"/> = clear floor-to-ceiling height.</summary>
    public sealed class LevelDef
    {
        public string Id;
        public string Name;
        public float Elevation;
        public float Height = 2.8f;
        /// <summary>Thickness of the floor build-up under this level (structure + finish).</summary>
        public float Slab = 0.3f;
    }

    public enum WallKind { Exterior, Interior }
    public enum WallAlign { Center, Outer, Inner }
    public enum WallSystem { Masonry, SteelGlass }

    /// <summary>
    /// Straight wall from <see cref="A"/> to <see cref="B"/>. For <see cref="WallAlign.Outer"/> the line is the
    /// outer (exterior) face and the wall body lies on the LEFT of A→B seen from above — i.e. list exterior walls
    /// counter-clockwise around the house. Bottom/Top are absolute heights; by default an exterior wall runs from
    /// grade (ground level) or its level's floor to the next level's floor (or the level ceiling + roof slab).
    /// </summary>
    public sealed class WallDef
    {
        public string Id;
        public string Level;
        public WallKind Kind = WallKind.Exterior;
        public WallSystem System = WallSystem.Masonry;
        public Vector2 A, B;
        public float? Thickness;
        public WallAlign? Align;
        public float? Bottom, Top;
        /// <summary>Exterior cladding (stone, plinth, stucco, wood) and interior finish (plaster, …).</summary>
        public string Outside, Inside;
        /// <summary>Height of the plinth zone above the wall bottom (0 = none).</summary>
        public float? Plinth;
        public List<FinishZoneDef> Zones = new List<FinishZoneDef>();
        /// <summary>Wrap the cladding around the start/end (outside corners). Null = detect from the joints.</summary>
        public bool? WrapStart, WrapEnd;
    }

    /// <summary>Cladding patch on the outer face: From/To along the wall from A, Bottom/Top absolute heights.</summary>
    public sealed class FinishZoneDef
    {
        public float From, To, Bottom, Top;
        public string Finish;
    }

    public enum OpeningType { Window, Glazing, Door, EntryDoor, SolidDoor, Hole }
    public enum CurtainType { None, Full, Left, Right }
    public enum Hinge { Start, End }

    /// <summary>Opening in a wall: <see cref="At"/> = distance from the wall's A to the opening edge; sill above the level floor.</summary>
    public sealed class OpeningDef
    {
        public string Id;
        public string Wall;
        public OpeningType Type = OpeningType.Window;
        public float At, Width = 1.2f, Sill = 0.9f, Height = 1.5f;
        public int Columns = 1;
        /// <summary>Transom bar heights above the sill.</summary>
        public List<float> Transoms = new List<float>();
        public CurtainType Curtain = CurtainType.None;
        public float CurtainFraction = 0.35f;
        public Hinge Hinge = Hinge.Start;
        /// <summary>Doors: +1 swings to the wall's left side (inside for exterior walls), -1 to the right.</summary>
        public int Swing = 1;
    }

    public enum RoomType { Living, Kitchen, Dining, Bedroom, Bathroom, Hall, Corridor, Wardrobe, Utility, Office, Stair, Garage, Terrace, Other }

    /// <summary>
    /// Room on a level, outlined by the inner faces of its walls. A room gets a floor slab with its floor finish,
    /// a ceiling at <see cref="Height"/> (default: the level height; a double-height room spans the level above,
    /// leaving a void there), downlights and a reflection probe.
    /// </summary>
    public sealed class RoomDef
    {
        public string Id;
        public string Name;
        public string Level;
        public RoomType Type = RoomType.Other;
        public List<Vector2> Outline = new List<Vector2>();
        public string Floor;
        public string Ceiling;
        public float? Height;
        /// <summary>Automatic recessed downlights ("auto") or none ("none").</summary>
        public string Downlights = "auto";
        public bool Probe = true;
    }

    public enum RoofType { Flat, Shed, Gable, Hip }

    /// <summary>
    /// Roof over a plan outline. Flat roofs accept any polygon (slab + optional parapet on the outline); pitched roofs
    /// use the outline's bounding rectangle in the roof's own frame (<see cref="Rotation"/>, ridge along local X).
    /// <see cref="Base"/> is the absolute height of the roof's underside at the walls.
    /// </summary>
    public sealed class RoofDef
    {
        public string Id;
        public RoofType Type = RoofType.Gable;
        public List<Vector2> Outline = new List<Vector2>();
        public float Base;
        public float Thickness = 0.3f;
        public float Overhang = 0.5f;
        public float Pitch = 30f;
        public float Rotation;
        public float Parapet;
        public string Material;
        public string Soffit;
        /// <summary>Finish of gable/shed end walls between the wall tops and the roof (default stucco).</summary>
        public string Gable;
    }

    public enum StairType { Straight, L, U }

    /// <summary>
    /// Stair from level <see cref="From"/> to <see cref="To"/>. <see cref="Start"/> = plan point at the bottom of the
    /// first flight on its centre line, <see cref="Direction"/> = walking direction of the first flight (degrees,
    /// 0 = +Z, 90 = +X). L and U stairs turn to <see cref="Turn"/> ("left"/"right").
    /// </summary>
    public sealed class StairDef
    {
        public string Id;
        public StairType Type = StairType.Straight;
        public string From, To;
        public Vector2 Start;
        public float Direction;
        public float Width = 1.0f;
        public float Going = 0.27f;
        public int? Risers;
        public int? FirstFlight;
        public string Turn = "left";
        public float Gap = 0.1f;
        public string Style = "floating_oak";
        /// <summary>Depth of the landing (L/U stairs); default = stair width.</summary>
        public float? Landing;
    }

    public enum ElementType { Box, Column, Railing, Platform, Beam }

    /// <summary>
    /// Architectural element: <c>box</c> (belts, canopies, parapets — Min/Max absolute), <c>column</c>,
    /// <c>railing</c> (Path in plan, Y = its base), <c>platform</c> (terrace/porch with a step), <c>beam</c>.
    /// </summary>
    public sealed class ElementDef
    {
        public string Id;
        public ElementType Type;
        public Vector3 Min, Max;
        public List<Vector2> Path = new List<Vector2>();
        public float Y, Height = 1.0f;
        public string Material;
        /// <summary>Box faces: top and underside materials ("none" = no face), thin cap on top (coping) with its height/overhang.</summary>
        public string Top, Bottom, Cap;
        public float CapHeight = 0.035f, CapOverhang = 0.012f;
        public string Style;
        public bool Collide = true;
    }

    /// <summary>
    /// Catalogue object (furniture, decor, plant, fixture). Position: plan X/Z, Y above the level floor (or absolute
    /// when no level is given). Rotation = compass direction the item's front faces (0 = +Z, 90 = +X, like stairs and views).
    /// </summary>
    public sealed class ItemDef
    {
        public string Id;
        public string Model;
        public string Level;
        public string Room;
        public Vector3 Position;
        public float Rotation;
        public JObject Params;
    }

    public enum LightKind { Point, Spot }

    /// <summary>Light source. Position/Target are absolute unless <see cref="Level"/> is set (then Y is above that floor).</summary>
    public sealed class LightDef
    {
        public string Id;
        public string Level;
        public LightKind Type = LightKind.Point;
        public Vector3 Position;
        public Vector3? Target;
        public string Color = "warm";
        public float Intensity = 1f, Range = 4f, Angle = 60f;
        public bool Shadows;
    }

    public enum ViewKind { Walk, Orbit }

    /// <summary>Presentation viewpoint: walk stop (feet position, yaw, pitch) or orbit angle around the house.</summary>
    public sealed class ViewDef
    {
        public string Name;
        public ViewKind Type = ViewKind.Walk;
        public Vector3 Position;
        public float Yaw, Pitch, Distance = 24f;
    }
}
