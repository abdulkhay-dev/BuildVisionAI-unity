# Interior library (Blender → app)

Furniture of the 12-interior reference sheet, modelled by Python scripts in Blender and shipped as library models
(`Assets/House4696/External/Models/<id>/`), plus the reference house that uses them.

| file | what |
|---|---|
| `kit.py` | modelling kit: bevelled boxes, cylinders, lathes, tubes, panels, pillows; metre UVs; own textures; FBX export |
| `tex.py` | procedural images for own textures (paintings, posters, rugs, book spines, screen picture) |
| `models_<room>.py` | the models, one file per room (`ENTRIES = [(id, name, category, builder, opts)]`) |
| `models.py`, `build.py` | registry; builds models and merges them into `External/external.json` (file lock, safe in parallel) |
| `materials.py` | Blender look-alikes of the app's materials (library textures + built-in palette) |
| `preview.py` | studio contact sheet of models |
| `house_plan.py` | the reference house → `modern12.house.json` + sample `Assets/StreamingAssets/Samples/dom-12-interyerov.house.json` |
| `lookdev.py`, `sheet.py` | the house in Blender (shell from the JSON + the same models) → `Renders/interior/*.png`, `house.blend` |

Conventions: metres, front towards Blender −Y, floor at z = 0; pivot floor centre / `back` (against a wall) / `wall`
(centre of the back face, y = mounting height) / `hanging` (ceiling point). Slots are named by role and default to a
library or built-in material (`velvet#c9bba8`, `walnut_veneer`, `led`, `glass`); own textured slots may glow
(`emit`) — the Unity importer uses the albedo as the emission map for Blender models.

```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b --python tools/interior/build.py -- [id|room …]                 # models → External/Models + external.json
$B -b --python tools/interior/preview.py -- /tmp/sheet.png <room>     # contact sheet
python3 tools/interior/house_plan.py                                 # house document + sample
$B -b --python tools/interior/lookdev.py -- --samples 96 [view …]     # Blender renders of the walk views
```

Then in Unity: House 46-96 → External → Import Catalog, then Render Catalog Thumbnails. The sample appears in existing
installs too (`ProjectStore.SeedSamples` remembers which samples were offered).
