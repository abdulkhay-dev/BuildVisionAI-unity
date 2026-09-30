# Brief: decor textures of the casegoods catalogue (wave 6)

680 case furniture modules of the Pinskdrev catalogue are built (Assets/House4696/Resources/Casegoods). Their finishes
still show every wood / stone / fabric decor as a provisional plain colour (`door_enamel_whitey#rrggbb`). This wave
makes the decors real: library materials with textures, colour-matched to the catalogue's swatches, that the lead then
puts into the finishes. The user wants the furniture one to one with the catalogue.

## Read first
- `tools/casegoods/decors.md` — every decor the collections need: name as the catalogue writes it, which collections /
  finish roles use it, the catalogue page and crop of its swatch (`gen/catpage.py <page> --crop … --dpi 300 --out x.png`,
  `--swatch …` for the mean colour), close-ups, character, grain direction, provisional colour. The same decor may be
  listed by several collections with slightly different colours (different swatch prints): make ONE material per decor,
  its colour from the best, flattest swatch (say which), and note the conflict.
- `tools/doors/BRIEF-textures.md` and the door texture machinery `tools/doors/textures/finish_kit.py` (a family module
  declares FAMILY and calls `finish_kit.main`) + `make_finishes.py` (colour maths, periodic noise, laminations, photo
  statistics, merge), `eco_oak.py`, `crosscut.py`, `veneer.py`, `laminate.py`, `grain.py` — proven generators of oak /
  softwood / film decors. Build on them: write your own module `tools/casegoods/textures/<family>.py` that imports them
  (do not edit the door modules).
- CC0 textures already in the library for structure: `Assets/House4696/External/Materials/` (oak / ash / walnut / cherry
  veneers, concrete_*, boucle_teddy, …; see `External/external.json`).
- Product photos (pinskdrev.by, `photos` in `tools/casegoods/reference/index.json`) show the decors at furniture scale.
- Python: /private/tmp/claude-501/venv/bin/python (numpy, Pillow, PyMuPDF). The generator itself needs only numpy + Pillow.

## Output per material (M = material id, given below)
- `Assets/House4696/External/Materials/M/M_albedo.jpg` — sRGB 2048×1024, tileable both ways, 2.0 m × 1.0 m, the grain
  along U (image x); `M_normal.jpg` (OpenGL, 1024×512, tileable); `M_mask.png` (R metallic, G AO 255, B 0, A smoothness;
  256×128). Uni / stone / fabric decors keep the same format (fabric: tile to its weave; set `metersPerTile` to it).
- Entries `tools/casegoods/textures/entries/<family>.json` (the shape of external.json's materials: id, name (the
  catalogue's), category "casegoods", source, neutral false, metersPerTile, maxSize 2048, folder, textures), merged with
  `python3 tools/doors/textures/merge_entries.py tools/casegoods/textures/entries/<family>.json` (it locks; ids must
  start with cg_ / cgfab_ / cgprint_).
- `tools/casegoods/textures/<family>.md` — per material: the swatch used (page, crop, mean hex), the texture's mean hex
  and ΔE76 (≤ 1.5 to the chosen swatch colour), the conflicts between collections, anything unsure.
- A check sheet `tools/casegoods/textures/sheets/<family>.png` (swatch crop | photo crop | texture at the swatch's scale
  | 1:1 m), and Read it; iterate until it matches.

## Quality bar
Photoreal at 1–2 m on furniture: no seams, no visible repetition across a 2 m wardrobe side, the catalogue's colour and
the character of the pattern — oak cathedrals, knots, cracks, saw marks and synchronised pores where the swatch shows
them (Pinskdrev's SWN / SWA / WML are synchronised-pore melamine films: matt with pore relief), pine's soft rings, the
calm cloud of a concrete, the veins of a marble, the pile of a velour.

## Rules
Do not edit C#, catalog.json, designs, the door modules or other families' files; no git; do not run Unity (the lead
imports). Write only your family's files listed above.
