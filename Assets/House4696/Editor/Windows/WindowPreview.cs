using System.IO;
using House4696.Doors;
using House4696.Model;
using House4696.Windows;
using UnityEngine;

namespace House4696.Windows
{
    /// <summary>
    /// Renders a window design file in a test facade wall (no catalogue entry needed) with the door preview's calibrated
    /// studio: "front" = orthographic from outside at 400 px/m, "inside" = the same from the room, "angle" = outside at an angle.
    /// </summary>
    public static class WindowPreview
    {
        public static string RenderDesign(string designPath, string finish, string outPath, string view = "front",
                                          float width = 1.4f, float height = 1.4f, float sill = 0.9f, bool open = false, float wall = 0.4f)
        {
            if (!File.Exists(designPath)) return "[WindowPreview] no file " + designPath;
            WindowDesign d;
            try { d = WindowCatalog.ParseDesign(File.ReadAllText(designPath)); }
            catch (System.Exception e) { return "[WindowPreview] the design does not parse: " + e.Message; }
            if (d == null) return "[WindowPreview] empty design";
            if (string.IsNullOrEmpty(d.Id)) d.Id = Path.GetFileNameWithoutExtension(designPath);
            WindowCatalog.Reload();
            var file = WindowCatalog.File;
            string model = "_preview-" + d.Id;
            file.Models.Insert(0, new WindowModel { Id = model, Name = d.Name, Design = d.Id, Finish = finish });
            WindowCatalog.Use(file, new[] { d });
            try
            {
                var doc = new HouseDocument();
                doc.Meta.Name = "window-preview";
                doc.Site.Landscape = LandscapePreset.None;
                doc.Levels.Add(new LevelDef { Id = "ground", Elevation = 0f, Height = Mathf.Max(2.8f, sill + height + 0.4f), Slab = 0.2f });
                // B → A along −X: the outside (right of A→B) faces +Z, where the front camera stands
                doc.Walls.Add(new WallDef { Id = "w", Level = "ground", Kind = WallKind.Exterior, A = new Vector2(3f, 0f), B = new Vector2(-3f, 0f),
                                            Thickness = wall, Outside = "render#e9e4dc" });
                doc.Openings.Add(new OpeningDef { Id = "win", Wall = "w", Type = OpeningType.Window, At = 3f - width * 0.5f, Width = width, Height = height,
                                                  Sill = sill, Model = model, Finish = finish, Open = open ? true : (bool?)null });
                bool inside = view == "inside";
                return DoorPreview.Render(new DoorPreview.Shot
                {
                    Model = model, Doc = doc, View = inside ? "back" : view, HideWall = view == "front" || inside,
                    FrontSize = new Vector2(width + 0.6f, height + 0.6f), FrontCenterY = sill + height * 0.5f,
                }, outPath);
            }
            finally { WindowCatalog.Reload(); }
        }
    }
}
