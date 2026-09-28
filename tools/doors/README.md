# Door catalogue tools

The app's doors are generated from data (format: `Docs/door-designs.md`; code: `Assets/House4696/Runtime/Doors`). These
tools turn the manufacturer's catalogue (DveriMebel / el'PORTA / BRAVO, 2020, PDF) into that data and check the result.
Python needs numpy + Pillow (a venv is fine); poppler (`pdftohtml`, `pdftoppm`) for the PDF.

| step | tool | what it does |
|---|---|---|
| 1 | `catalog_index.py <pdf>` | every door photo of the catalogue with its caption → `.cache/photos/`, `.cache/index.json` (git-ignored: the photos are the manufacturer's) |
| 2 | `measure.py <photo>` | leaf bounds and the edges of joints, glass strips, steps in leaf millimetres; `--out` draws them over the photo |
| 3 | `preview2d.py <design> --photo …` | the design drawn in 2D next to and over the photo; `--check` prints the offset of every line; `--sheet` shows resizing |
| 4 | `textures/make_finishes.py` | finish textures (wood-like films), colour-fitted to the catalogue → `Assets/House4696/External/Materials/door_*` + `external.json` |
| 5 | Unity: `House4696.Doors.DoorPreview` | the real generator: `RenderDesign(designPath, finish, glass, outPng, view)` renders a design file without a catalogue entry; `Render(Shot, png)` a catalogue model; `Compare(photo, render, out)` side by side |

After new finishes: Unity → House 46-96 → External → Import Catalog (materials), then House 46-96 → Rebuild Runtime Content.

Conventions worth remembering:

- Designs are drawn at 800 × 2000 mm as the catalogue photo shows the leaf: x = 0 is the lock edge (handle on the left).
- The big catalogue photos are ~0.4 px/mm (373 × 817 px), small ones ~0.17 px/mm — measure on the big ones, cross-check
  every colour of a model.
- Finish textures: grain along U (horizontal in the image), 2.0 × 1.0 m per tile, tileable.
- A series lives in `Assets/House4696/Resources/Doors/Series/<id>.json` (or in `catalog.json`), a design in
  `…/Designs/<id>.json`; finishes and glass are shared in `catalog.json`.
