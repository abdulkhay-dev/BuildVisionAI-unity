using System;
using System.Collections.Generic;
using System.Linq;
using House4696.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>
    /// The lift catalogue in Resources/Lifts/catalog.json (GLZ / NBSL 2024): models with their size tables, cabin designs,
    /// landing doors, ceilings, handrails, floors, panels, paint colours and the finish vocabulary. Sizes are in mm as
    /// printed; <see cref="Resolve"/> turns a <see cref="LiftDef"/> into the metres the builder uses.
    /// </summary>
    public static class LiftCatalog
    {
        public const string Folder = "Lifts";

        static readonly JsonSerializerSettings Json = new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver(),
            MissingMemberHandling = MissingMemberHandling.Ignore,
        };

        static LiftCatalogFile _file;

        public static LiftCatalogFile File
        {
            get
            {
                if (_file != null) return _file;
                var text = Resources.Load<TextAsset>(Folder + "/catalog");
                try { _file = text != null ? JsonConvert.DeserializeObject<LiftCatalogFile>(text.text, Json) : null; }
                catch (JsonException e) { Debug.LogError("[Lifts] catalog.json: " + e.Message); }
                return _file ??= new LiftCatalogFile();
            }
        }

        public static void Reload() => _file = null;

        static T Find<T>(List<T> list, string id, Func<T, string> key) where T : class =>
            id == null || list == null ? null : list.FirstOrDefault(x => string.Equals(key(x), id, StringComparison.OrdinalIgnoreCase));

        public static LiftModel Model(string id) => Find(File.Models, id, m => m.Id);
        public static LiftCabin Cabin(string id) => Find(File.Cabins, id, m => m.Id);
        public static LiftLandingDoor LandingDoor(string id) => Find(File.LandingDoors, id, m => m.Id);
        public static LiftCeiling Ceiling(string id) => Find(File.Ceilings, id, m => m.Id);
        public static LiftHandrail Handrail(string id) => Find(File.Handrails, id, m => m.Id);
        public static LiftFloor Floor(string id) => Find(File.Floors, id, m => m.Id);
        public static LiftPanel Panel(string id) => Find(File.Panels, id, m => m.Id);
        public static LiftColor Color(string id) => Find(File.Colors, id, m => m.Id);
        public static LiftFinish Finish(string id) => Find(File.Finishes, id, m => m.Id);

        /// <summary>
        /// The table row and the sizes of a lift (null with <paramref name="error"/> when the model or a row does not
        /// exist). Load: the asked one, else 1000 kg, else the nearest; car: the asked width × depth among the load's rows.
        /// </summary>
        public static LiftSpec Resolve(LiftDef d, out string error)
        {
            error = null;
            var m = Model(d.Model);
            if (m == null)
            {
                error = $"нет модели лифта '{d.Model}'. Модели: {string.Join(", ", File.Models.Select(x => x.Id))} (house_lifts)";
                return null;
            }
            if (m.Rows == null || m.Rows.Count == 0) { error = $"у модели '{m.Id}' нет таблицы размеров"; return null; }
            int want = d.Load ?? 1000;
            var loads = m.Rows.Select(r => r.Load).Distinct().ToList();
            int load = loads.Contains(want) ? want : loads.OrderBy(l => Mathf.Abs(l - want)).First();
            if (d.Load.HasValue && load != d.Load.Value)
            {
                error = $"у модели '{m.Id}' нет грузоподъёмности {d.Load} кг. Есть: {string.Join(", ", loads)} кг";
                return null;
            }
            var rows = m.Rows.Where(r => r.Load == load).ToList();
            var row = rows[0];
            if (d.Car != null && d.Car.Length >= 2)
            {
                row = rows.FirstOrDefault(r => r.Car != null && r.Car[0] == d.Car[0] && r.Car[1] == d.Car[1]);
                if (row == null)
                {
                    error = $"у '{m.Id}' {load} кг нет кабины {d.Car[0]}×{d.Car[1]}. Есть: {string.Join(", ", rows.Select(r => $"{r.Car[0]}×{r.Car[1]}"))}";
                    return null;
                }
            }
            var speeds = row.Speeds ?? new List<float> { 1f };
            float speed = d.Speed ?? (speeds.Count > 0 ? speeds.Min() : 1f);
            if (d.Speed.HasValue && !speeds.Any(s => Mathf.Abs(s - d.Speed.Value) < 0.01f))
            {
                error = $"'{m.Id}' {load} кг не бывает на скорости {d.Speed} м/с. Есть: {string.Join(", ", speeds)} м/с";
                return null;
            }
            int Pick(Dictionary<string, int> bySpeed, int fallback)
            {
                if (bySpeed == null || bySpeed.Count == 0) return fallback;
                foreach (var kv in bySpeed)
                    if (float.TryParse(kv.Key, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var s) &&
                        Mathf.Abs(s - speed) < 0.01f) return kv.Value;
                return bySpeed.Values.Max();
            }
            bool freight = m.Type == "freight" || m.Type == "car";
            var spec = new LiftSpec
            {
                Model = m, Row = row, Speed = speed,
                CarWidth = row.Car[0] / 1000f, CarDepth = row.Car[1] / 1000f, CarHeight = (row.Car.Length > 2 ? row.Car[2] : 2385) / 1000f,
                DoorWidth = row.Door / 1000f,
                ShaftWidth = row.ShaftSize[0] / 1000f, ShaftDepth = row.ShaftSize[1] / 1000f,
                Overhead = Pick(row.Overhead, 4200) / 1000f, Pit = Pick(row.Pit, 1400) / 1000f,
                // an MR table without AM × BM (the side counterweight one): the machine room covers the shaft
                MachineRoom = m.Drive != "mr" ? (Vector2?)null
                    : row.MachineRoom != null && row.MachineRoom.Length >= 2 ? new Vector2(row.MachineRoom[0] / 1000f, row.MachineRoom[1] / 1000f)
                    : new Vector2(row.ShaftSize[0] / 1000f, row.ShaftSize[1] / 1000f),
                MachineHeight = (m.MachineHeight ?? (freight ? 2500 : 2650)) / 1000f,
                DoorType = (row.DoorType ?? m.DoorType ?? (freight ? "2s" : "co")).ToLowerInvariant(),
                Shape = (row.Shape ?? m.Shaft ?? "rect").ToLowerInvariant(),
                Freight = freight,
                Panoramic = m.Type == "panoramic",
            };
            // door height: passenger lifts 2.1 m; freight ones as high as the car allows, up to 2.3 m
            spec.DoorHeight = row.DoorHeight.HasValue ? row.DoorHeight.Value / 1000f
                : freight ? Mathf.Min(spec.CarHeight, 2.3f) : Mathf.Min(2.1f, spec.CarHeight - 0.15f);
            return spec;
        }
    }

    /// <summary>A lift resolved to sizes in metres.</summary>
    public sealed class LiftSpec
    {
        public LiftModel Model;
        public LiftRow Row;
        public float Speed;
        public float CarWidth, CarDepth, CarHeight, DoorWidth, DoorHeight;
        public float ShaftWidth, ShaftDepth, Overhead, Pit;
        public Vector2? MachineRoom;
        public float MachineHeight;
        /// <summary>co (centre opening, two leaves) or 2s (two-speed telescopic, both leaves to one side).</summary>
        public string DoorType;
        /// <summary>rect, semicircle or rhombus (panoramic cars and their shafts).</summary>
        public string Shape;
        public bool Freight, Panoramic;
    }

    // ------------------------------------------------------------------ catalogue file
    public sealed class LiftCatalogFile
    {
        public List<LiftModel> Models = new List<LiftModel>();
        public List<LiftCabin> Cabins = new List<LiftCabin>();
        public List<LiftLandingDoor> LandingDoors = new List<LiftLandingDoor>();
        public List<LiftCeiling> Ceilings = new List<LiftCeiling>();
        public List<LiftHandrail> Handrails = new List<LiftHandrail>();
        public List<LiftFloor> Floors = new List<LiftFloor>();
        public List<LiftPanel> Panels = new List<LiftPanel>();
        public List<LiftColor> Colors = new List<LiftColor>();
        public List<LiftFinish> Finishes = new List<LiftFinish>();
    }

    public sealed class LiftModel
    {
        public string Id, Name;
        /// <summary>passenger, panoramic, freight, car (the car lift).</summary>
        public string Type;
        /// <summary>mr (machine room on top) or mrl (machine-room-less).</summary>
        public string Drive;
        public string Counterweight, Roping, Shaft, Note;
        /// <summary>Default door type of the model's rows (co / 2s).</summary>
        public string DoorType;
        public int Page;
        public int? MachineHeight, TopClearance, PitBottomGap;
        /// <summary>Default cabin design, landing door, car and landing panels of the model.</summary>
        public string Cabin, LandingDoor, Panel, Call;
        public List<LiftRow> Rows = new List<LiftRow>();
    }

    public sealed class LiftRow
    {
        public int Load;
        public List<float> Speeds;
        /// <summary>Door clear width JJ, car width × depth × height AA × BB × CH, shaft AH × BH, machine room AM × BM (mm).</summary>
        public int Door;
        public int? DoorHeight;
        public string DoorType;
        public int[] Car, ShaftSize, MachineRoom;
        /// <summary>Headroom above the top stop (OH) and pit depth (PD), mm, by speed ("1.0" → 4200).</summary>
        public Dictionary<string, int> Overhead, Pit;
        public string Shape;
    }

    public sealed class LiftCabin
    {
        public string Id, Type, Name;
        public int Page;
        /// <summary>Finish ids of the car's back, side and front walls.</summary>
        public LiftWalls Walls = new LiftWalls();
        /// <summary>Finish of the car door; ceiling model and its paint colour; light; handrail model; floor.</summary>
        public string Door, Ceiling, CeilingColor, CeilingFinish, Light, Handrail, Floor, Canopy, Text, LandingDoor;
    }

    public sealed class LiftWalls { public string Back, Side, Front; }

    public sealed class LiftLandingDoor { public string Id, Name, Finish, Pattern; public int Page; }

    public sealed class LiftCeiling { public string Id, Name, Finish, Layout; }

    public sealed class LiftHandrail
    {
        public string Id, Name, Profile, Finish;
        /// <summary>Diameter or width × thickness, mm.</summary>
        public float[] Size;
    }

    public sealed class LiftFloor { public string Id, Type, Name; public int Page; }

    public sealed class LiftPanel { public string Id, Kind, Display, Finish; public int Page; }

    public sealed class LiftColor { public string Id, Hex; public int Page; }

    public sealed class LiftFinish
    {
        public string Id, Name;
        /// <summary>brushed, mirror, painted, etched, pvc, wood-look, checker.</summary>
        public string Base;
        public string Tint, Note;
        /// <summary>Library material that renders it (lift_* / liftprint_*); null = derived from <see cref="Base"/> and <see cref="Tint"/>.</summary>
        public string Material;
    }
}
