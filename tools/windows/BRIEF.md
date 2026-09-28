# Brief: window designs 1–12 (pilot, cloud session)

The "House" app (Unity 6) builds houses from JSON; catalogue windows are data drawn in a small JSON format and built by a
C# engine. Your job: author the designs of catalogue windows **1–12** (section "Дом") so each looks like its catalogue
picture. You have no Unity here — check your work with the 2D tool; the lead renders them in 3D afterwards.

## Read first
- `Docs/window-designs.md` — the format (outline shapes, layout tree, sashes, bars, frosted bands, sills, surround,
  catalog.json). Follow it exactly; if something in a picture cannot be expressed, approximate and write it down.
- `Assets/House4696/Resources/Windows/catalog.json` — the 12 models (names, the catalogue's description, finish, typical
  size, sill height) and the frame finishes.
- `Assets/House4696/Resources/Windows/Designs/w01.json` — the example (window 1). Improve it too if the picture says so.
- Pictures: `tools/windows/reference/w01.jpg … w12.jpg` (1536 × 1024, perspective photos made by an AI; proportions are
  approximate — read the look: outline, divisions, which parts open, bar grid, profile widths relative to the glass,
  sill / surround, colour).
- `tools/windows/preview2d.py` — 2D elevation from outside beside the picture:
  `python3 tools/windows/preview2d.py Assets/House4696/Resources/Windows/Designs/w02.json --finish "#b9a07a" --photo tools/windows/reference/w02.jpg --out /tmp/w02.png`
  (needs numpy + Pillow: `pip install numpy pillow` if missing). Look at every output image and iterate.

## What to produce
For each window N = 01…12:
1. `Assets/House4696/Resources/Windows/Designs/wNN.json` — the design at its natural reference size (estimate it from
   the picture: door-height panoramas ≈ 2400–2700 high, a 2-sash window ≈ 1400 × 1400, etc.), with `fixX`/`fixY` so
   frames, mullions and fanlights keep their widths when the house uses another size.
2. Keep the model entry in `catalog.json` in step: `size` (typical opening, m), `sillHeight`, `finish` (one of the
   finishes; add a finish only if none fits the picture's colour — id in kebab-case, a tintable material as the doc shows).
3. A check image per window: `tools/windows/pilot/wNN.png` (picture | your 2D elevation), made with preview2d.

Decisions per picture (what the catalogue shows):
- 01 two equal sashes, white PVC, stone sill. 02 one big pane (or a fixed pane with a narrow opening sash if you see one),
  light oak, a deep frame. 03 black sliding panorama floor-to-ceiling, three panels. 04 tall French casement pair with small
  bars (a grid), milky paint, a stone architrave (surround). 05 round-top (arch) pair with symmetric bars, ivory, stone
  surround. 06 English grid: several columns and rows of small panes in a dark walnut frame, stone sill. 07 round window,
  graphite, deep frame. 08 a bay (эркер): design the *central* window of the bay (the side windows are the same model on
  the bay's angled walls) — white sash windows with a horizontal division. 09 corner glazing: tall fixed panes with a thin
  anthracite frame (the corner join is a house-level feature — design one side). 10 gable window under the roof slope:
  a pentagon/triangle outline with vertical mullions, natural oak. 11 horizontal ribbon: a low wide window of three
  sections, grey aluminium, metal sill. 12 sliding panorama: four tall sections, bronze aluminium.
- Which sashes open: use `turn` for side-hung sashes you can see (handles, sash frames), `slide` for sliding panels,
  `fixed` otherwise.
- Sills: outside `stone` where the picture shows a stone sill, `metal` for a thin drip, `none` for floor-level glazing;
  inside `board` for windows with a sill height, `none` for floor-to-ceiling ones.

## Rules
- Do not edit C# or anything outside `Assets/House4696/Resources/Windows/`, `tools/windows/pilot/` and (for a real gap
  only) `Docs/window-designs.md` notes.
- Commit your work on a new branch `windows-pilot-1-12` and push it (the lead merges). One commit is fine.
- End with a short report: per window what the design contains, the reference size you chose and why, decisions,
  what the format could not express.
