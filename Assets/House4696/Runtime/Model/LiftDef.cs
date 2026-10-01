using System.Collections.Generic;
using UnityEngine;

namespace House4696.Model
{
    /// <summary>
    /// A lift of the manufacturer's catalogue (Resources/Lifts/catalog.json, GLZ / NBSL): the shaft through the storeys
    /// with its pit and headroom (and the machine room on top for MR drives), a landing door with its portal and call
    /// button at every stop, the car parked at one stop with the interior of a catalogue cabin design. Every size comes
    /// from the catalogue's table row picked by <see cref="Model"/>, <see cref="Load"/> (and <see cref="Speed"/>,
    /// <see cref="Car"/>).
    /// <para>
    /// <see cref="Position"/> is the plan point in the middle of the landing doors on the shaft's front face (the hall
    /// side); <see cref="Rotation"/> is the compass direction the doors face (0 = +Z, 90 = +X, like stairs and items) —
    /// the shaft lies behind the point.
    /// </para>
    /// </summary>
    public sealed class LiftDef
    {
        public string Id;
        /// <summary>Catalogue model: k600-mr-rear, k600-mr-side, k600l-mrl, k600g-mr, k600g-mrl, h700-mr-2-1, …</summary>
        public string Model;
        /// <summary>Rated load, kg (a row of the model's table; default: the model's 1000 kg row or the nearest).</summary>
        public int? Load;
        /// <summary>Rated speed, m/s (sets the overhead and the pit depth; default: the row's slowest).</summary>
        public float? Speed;
        /// <summary>Car width × depth in mm when a load has several car sizes in the table ([1100, 2100] — a stretcher car).</summary>
        public int[] Car;
        public Vector2 Position;
        public float Rotation;
        /// <summary>Lowest and highest stop (level ids; default: the lowest and the highest storey).</summary>
        public string From, To;
        /// <summary>Stops between them that have no landing door (level ids; default: every storey is served).</summary>
        public List<string> Skip = new List<string>();
        /// <summary>Cabin design of the catalogue (sl-1036, sl-1136, …; default: the model type's standard).</summary>
        public string Cabin;
        /// <summary>Landing door design (sl-7061, …; "stainless" = the plain brushed door; default stainless).</summary>
        public string Door;
        /// <summary>Car operating panel and landing call panel models (dc1000a, dl300, …).</summary>
        public string Panel, Call;
        /// <summary>
        /// Shaft enclosure: "concrete" (default; 0.2 m walls, plastered outside), "glass" (panoramic: glass between steel
        /// posts), "none" (the author's walls enclose it — the lift only cuts the floors and builds doors, car and rails).
        /// </summary>
        public string Shaft;
        /// <summary>Shaft wall thickness, m (concrete shafts).</summary>
        public float? Wall;
        /// <summary>Side counterweight models: the side it runs on, seen from the landing ("left" / "right"; default left).</summary>
        public string Side;
        /// <summary>Stop where the car stands (default: the lowest stop).</summary>
        public string Parked;
        /// <summary>The car's and the landing's doors at the parked stop are shown open.</summary>
        public bool Open;
    }
}
