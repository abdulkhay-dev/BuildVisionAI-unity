# Garden look-dev (Blender)

A reference garden (stream with cascades, rock banks, perennial beds, bridge, lanterns, sunset over the
mountains) built by script in Blender. It is the target look before the landscape is split into
reusable parts for the House app.

```bash
/usr/bin/python3 tools/landscape/fetch_garden.py            # Poly Haven models, HDRI, ground textures → .cache/polyhaven
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
    -P tools/landscape/garden/build.py -- --render all --samples 80
```

Output in `Renders/landscape/`: `garden.blend`, one PNG per view, `sheet.png` (reference-style contact
sheet). `--scale 0.4 --samples 24` gives a preview in ~1.5 min; `--quick` skips the lawn and the forest.

## Structure

| Module | Role | Becomes in the app |
|---|---|---|
| `layout.py` | the design as data: stream curve, cascades, paths, bridge, trees, props, sun, views | the `site` section of `house.json` that the AI writes |
| `site.py` | height model: slope, stream pools between cascades carved into the ground | runtime terrain generator |
| `kit.py` | Poly Haven variants per group (rocks, grasses, ferns, shrubs, trees) | landscape catalogue |
| `flora.py` | procedural perennials (salvia, lavender, lupin, daisy, phlox, hosta) | catalogue entries |
| `props.py` | bridge, stone lantern, post lamp, stepping stones, fence | catalogue models / generators |
| `water.py` | level pools, cascade tongues, foam | water generator + shader |
| `scatter.py` | zones (rim, bank, bed, back, lawn), drifts, two-layer planting, bank/weir rocks, forest | runtime scatter with seed |
| `terrain.py` | plot mesh + masks, far land with hills and mountains | terrain + backdrop |
| `stage.py` | sky, sun, cameras, render, contact sheet | time of day, viewpoints |

Blender collections follow the same split: `KIT_*` (instanced variants), `SITE`, `PROPS`, `HOUSE`,
`PLANTING` (one Geometry Nodes instancer per kit group), `STAGE`, `CAMERAS`.

Notes: the sky HDRI is clamped and a sun lamp at 11° lights the scene (at the HDRI's 6° every tree would
shade the garden); trees towards the sun are kept short enough not to shade it; water does not cast
shadows (no caustics); the far land is sunk 4 m under the plot so it never shows in the stream bed.

## In the app (Unity)

```bash
/usr/bin/python3 tools/landscape/fetch_garden.py                     # sources (once)
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/landscape/export_kit.py [-- group ...]
```

`export_kit.py` writes `Assets/House4696/External/Landscape/` (one FBX per variant with `_LOD0`/`_LOD1`, textures in
the furniture-library packing, terrain layers, `landscape.json`). Realtime budgets: boulders 2500/750 triangles,
plants from Poly Haven's lighter LODs, procedural perennials at two details on one palette material. Trees stay the
app's procedural ones (Poly Haven trees are 0.3–2 M triangles).

Unity: House 46-96 → External → Import Landscape Kit (`LandscapeKitImporter`) → `LandscapeKit` in HouseContent.
A document with `site.landscape = "natural"` is built by `Runtime/Landscape/Natural/`:

| File | Role |
|---|---|
| `SiteModel` | heights (slope, pad at 0, streams as pools and cascades), distance fields, zones — port of `site.py` |
| `PlantingPlan` | styles (perennial, meadow, shade, rock), drifts, structure + accents — port of `scatter.py` |
| `NaturalSiteBuilder` | detailed terrain (heights, 4 layers, grass details), plants, rocks, far terrain, forest |
| `PlantField` | GPU-instanced plants and stones: 4 m chunks, LOD per chunk (per instance at band edges), frustum culling, LOD1 shadow casters within 15 m |
| `WaterBuilder` / `WaterFlow` | pool ribbons, cascade tongues, scrolling ripples |
| `SitePropsBuilder` | stepping stones, bridge, stone lanterns, post lamps, fence, single trees |

The format is documented in `Docs/house-format.md` (section «Участок»); `HouseValidator.Site` checks it. Reference
project: `sad-u-ruchya` (the look-dev garden next to the barnhouse sample).

## Performance notes (measured in the built app, MacBook Air M4)

- Plants were **vertex-bound** (render scale did not change their cost). LOD thresholds are real screen fractions
  (PlantField ignores `QualitySettings.lodBias = 2`): full mesh above 12 % of the screen height, LOD1 down to 4 %,
  impostor cards to 0.3 %. Impostors: front, side and top views of every plant in one 2048² atlas
  (`export_kit.py`, Cycles, unlit colour + alpha, cropped to the silhouette); the top card keeps beds planted in
  orbit/top views.
- `groundcover` (terrain-detail meshes, no LODs) must not be planted through PlantField — beds use
  `groundcover_plant` (same plants with LODs and cards).
- Site terrains are not `drawInstanced`: in the player the instanced path drew the ground without sunlight (the
  editor looked right). Always check terrain changes in the built app.
- Depth priming is forced on both URP renderers (identical pictures, −0.3…−2.3 ms).
- The focused frame rate is capped at the panel rate (`FramePacing.FocusedFrameRate = 0`): the fanless Air
  throttled by 40–50 % after long uncapped runs. Diagnostics (`bench`, `ab`, `perf`) run uncapped.
- Measure with `ab` (interleaved A/B on one view) — sequential sweeps drift by several ms as the SoC heats up.
