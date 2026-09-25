using House4696.Runtime;
using UnityEngine;
using static House4696.House.HouseSpec;

namespace House4696.Setup
{
    /// <summary>
    /// House-specific data for <see cref="HouseViewer"/>: walk-tour stops (feet slightly above the floor, the
    /// controller settles onto it) and orbit presets. Yaw 0 looks along +Z (at the front facade).
    /// </summary>
    public static class TourSpec
    {
        public static readonly Vector3 Pivot = new Vector3(Width * 0.5f, 3.2f, 5.6f);

        const float Ground = 0.05f, Floor = FloorY + 0.05f, Upper = UpperFloorY + 0.05f, Balcony = BandTop + 0.1f;

        public static WalkPoint[] Walk() => new[]
        {
            P("Дорожка к входу", 10.9f, Ground, -2.6f, 0f, -4f),
            P("Терраса", 3.2f, Floor, 0.4f, 215f, 0f),
            P("Холл у входа", 10.7f, Floor, 2.3f, 10f, 0f),
            P("Гостиная, второй свет", 7.06f, Floor, 5.8f, 180f, -12f),
            P("Медиастена и камин", 5.9f, Floor, 5.2f, 125f, -2f),
            P("Кухня-столовая", 4.1f, Floor, 4.5f, 327f, -6f),
            P("Лестница", 7.6f, Floor, 6.1f, 20f, 8f),
            P("Гостевая спальня", 10.4f, Floor, 7.3f, 110f, -8f),
            P("Галерея 2-го этажа", 7.6f, Upper, 6.1f, 200f, 12f),
            P("Главная спальня", 1.5f, Upper, 6.6f, 136f, -10f),
            P("Ванная с отдельностоящей ванной", 6.3f, Upper, 8.1f, 345f, -14f),
            P("Спальня 2", 10.75f, Upper, 2.4f, 45f, -8f),
            P("Спальня 3", 10.25f, Upper, 6.95f, 75f, -8f),
            P("Балкон", 3.9f, Balcony, 1.2f, 200f, 5f),
            P("Задний двор", 7.0f, Ground, 16.5f, 180f, -6f),
        };

        public static OrbitPoint[] Orbit() => new[]
        {
            O("Фасад 3/4 (как на фото)", 30f, 8f, 26f),
            O("Главный фасад", 0f, 5f, 24f),
            O("Правый фасад", -90f, 6f, 22f),
            O("Задний фасад", 180f, 6f, 24f),
            O("Левый фасад", 90f, 6f, 22f),
            O("Вид сверху", 20f, 80f, 34f),
        };

        static WalkPoint P(string name, float x, float y, float z, float yaw, float pitch) =>
            new WalkPoint { Name = name, Feet = new Vector3(x, y, z), Yaw = yaw, Pitch = pitch };

        static OrbitPoint O(string name, float yaw, float pitch, float distance) =>
            new OrbitPoint { Name = name, Yaw = yaw, Pitch = pitch, Distance = distance };
    }
}
