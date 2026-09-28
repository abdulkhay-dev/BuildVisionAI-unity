# Brief: window designs 13–48 and a quality pass over 1–12 (cloud session)

The "House" app (Unity 6) builds houses from JSON; catalogue windows are data in a small JSON format built by a C#
engine. Windows 1–12 are done (branch main). Your job: author windows **13–48** so each one reads like its catalogue
picture — realistic, every corner thought through — and then revisit 1–12 with the engine's new features.
There is no Unity here: check everything with the 2D tool; the lead renders all of them in 3D afterwards.

## Read first
- `Docs/window-designs.md` — the format, including the new features: sash rails, hung (sash) windows, doors in
  shopfronts, opaque panels, blinds, members (diagrid, art-deco bars, fins, louvres), awning, shelf, spider fixings,
  keystone, surround without a bottom. What the engine builds for free (profiles, gaskets, handles, grain) is listed there.
- `Assets/House4696/Resources/Windows/catalog.json` — all 48 models: name, section, the catalogue's description,
  a suggested finish, typical size and sill height (estimates — correct them from the picture).
- `Assets/House4696/Resources/Windows/Designs/w01.json … w12.json` — finished examples.
- Pictures: `tools/windows/reference/w01.jpg … w48.jpg` (AI-made perspective photos; read the look).
- `tools/windows/preview2d.py` (2D elevation from outside beside the picture; `pip install numpy pillow` if missing):
  `python3 tools/windows/preview2d.py Assets/House4696/Resources/Windows/Designs/w13.json --finish "#b8bbbe" --photo tools/windows/reference/w13.jpg --out tools/windows/pilot/w13.png`

## Quality bar
- Divisions, proportions and the rhythm of members exactly as the picture shows them: count every mullion, transom,
  bar and panel; keep their relative widths (a slim aluminium mullion 50–60 mm; a curtain-wall mullion 60 wide and
  150–250 deep; a PVC frame 70 + sash 80; a timber frame 80–100; a shopfront frame 60–80).
- Which parts open: side-hung sashes `turn`, shopfront doors `door`, sliding panels `slide`, sash windows `hung`,
  everything else `fixed`. Sashes with visible rails get `rails` (a French window's or a door's tall bottom rail).
- Opaque parts are `panel` cells (spandrels, the chessboard's opaque cells, a shopfront's low panel); frosted bands via
  `frosted` or `panel: "frosted"`.
- Things in front of the glass are `members` with `z` < 0: vertical fins (18), the outer screen (19: glass panes on
  spider `fixings` in front of the main grid — model the screen as the window and the inner grid as members, or the
  reverse; say which), louvres (47). Decorative lines on the glass (22 diagonals, 33 art-deco steps) are `members` with
  `z: null`.
- Stone portals / surrounds (24, 35) and a wooden portal (31: `material: "frame"`), awning (32), shelf (36).
- Tower sections (13–24): design ONE storey-high module of the facade (what repeats), at its real size (≈ 1.2–3.6 m wide,
  2.8–3.4 m high, sill 0), so a house can repeat it along a wall. Corner pieces (20, 29, 45) are one side, as in 9.
- A finish per window as the picture shows; add a finish to `catalog.json` only if none fits (the doc shows how).

## Output
1. `Assets/House4696/Resources/Windows/Designs/w13.json … w48.json`.
2. `catalog.json`: correct each model's `size`, `sillHeight`, `finish`.
3. Revisit 1–12 with the new features where the picture shows them: 04 (tall bottom rails, surround without bottom +
   stone sill), 05 (keystone, surround without bottom), 08 (a real `hung` sash window with a meeting rail), 06 (centre),
   12 / 03 (door-like rails on sliding panels), anything else you see.
4. A check image per window in `tools/windows/pilot/wNN.png` (picture | your elevation). Look at every one and iterate.
5. Commit on a new branch `windows-13-48` and push it. End with a report: per window the size you chose and what the
   design contains, decisions, and anything the format could not express.

## Rules
Do not edit C# or anything outside `Assets/House4696/Resources/Windows/`, `tools/windows/pilot/` and notes in
`Docs/window-designs.md`.
