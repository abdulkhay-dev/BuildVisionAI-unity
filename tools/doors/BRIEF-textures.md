# Brief for door finish texture authors (waves 2–5)

Door leaves, frames and casings of the "House" app are generated in Unity; their surface finishes (films, veneers,
laminates, paint, powder-coated metal) are library materials made from your textures. The user wants the doors of the
DveriMebel / el'PORTA / BRAVO catalogue (2020) **one to one**. Repo: /Users/abdulxay/Documents/works/ansormed/unity.
Do NOT edit C# and do not run the Unity importer (the lead does it); do not touch other authors' families.

## Read first
- `tools/doors/textures/make_finishes.py` — wave 1's generator (Veralinga, Golden Reef, 3D-Graf): its structure,
  seeds, colour fitting against the catalogue photos, `--compare` sheet. Build on it: import its helpers from your own
  module `tools/doors/textures/<family>.py` (do not edit make_finishes.py itself — other authors run in parallel), or
  copy the pieces you need.
- `tools/doors/ids.md` — the finish ids and names of your family (material id = `door_` + id with `-` → `_`).
- Catalogue photos: `tools/doors/.cache/photos/` + `index.json` (finish captions, e.g. "Chalet Grande", "Л-11
  (ИталОрех)"). Big photos ≈0.4 px/mm, small ≈0.17. Swatches in the PDF (~/Downloads/katalog_dverey_dm_12_02_2020.pdf)
  are tiny but show the colour; render a page with `pdftoppm -r 300 -f N -l N -png` (PDF page n = catalogue pages 2n−4 /
  2n−3).
- CC0 photo textures already in the repo can be a base for structure (oak cathedrals, knots): e.g.
  `Assets/House4696/External/Materials/oak_veneer/`, `white_oak_veneer/`, `grey_oak_veneer/`, `walnut_veneer/`,
  `ash_veneer/` (1K; `.cache/polyhaven/` may hold larger sources; Poly Haven is CC0 — you may download 2K/4K sources of
  veneers with `/usr/bin/python3 tools/assets/fetch_polyhaven.py`-style requests if you need them).
- Python with numpy / pillow / opencv / scipy:
  /private/tmp/claude-501/-Users-abdulxay-Documents-works-ansormed-unity/b1c0ef17-d5fe-4050-9d5b-7b6ab2c0b683/scratchpad/venv/bin/python
  (the generator itself must need only numpy + Pillow).

## Output per finish (M = material id)
- `Assets/House4696/External/Materials/M/M_albedo.jpg` — sRGB 2048×1024, grain along U (image x), tileable both ways,
  2.0 m × 1.0 m; `M_normal.jpg` (OpenGL, 1024×512, tileable); `M_mask.png` (R metallic, G AO 255, B 0, A smoothness;
  256×128). Paint and metal have no grain but keep the same format (metals: R metallic > 0).
- `tools/doors/textures/entries/<family>.json` — the external.json entries (shape as wave 1's: id, name, category
  "door", source, neutral false, metersPerTile [2.0, 1.0], maxSize 2048, folder, textures) — then run
  `python3 tools/doors/textures/merge_entries.py tools/doors/textures/entries/<family>.json` (it locks and merges).
- `Assets/House4696/Resources/Doors/Finishes/<family>.json` — a JSON array of the family's finishes:
  `{ "id", "name" (catalogue name), "line" (ЭкоШпон / ЕвроШпон / Шпон натуральный / …), "material", "color" (mean hex) }`.
- `tools/doors/.cache/finishes_<family>.png` — check sheet like wave 1's (photo crop | texture at the photo's scale |
  1:1), and a colour table (ΔE76 of means ≤ 1.5).

## Quality bar
Photoreal interior at 1–2 m: no seams, no obvious repetition within a 2 m stile, the catalogue's colour and the
character of the pattern (oak cathedrals and knots where the catalogue shows them, rustic cracks for Chalet, fine lines
for veneers, crosshatch for Crosscut, printed-film look for laminates, smooth orange-peel paint for enamel, hammered
powder coat for metals). Iterate on the check sheet (Read the PNG) until it matches.
