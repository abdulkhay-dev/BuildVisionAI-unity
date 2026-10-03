"""variable-speed-fan-game-box: blue bear-ear wall panel with 4 fans and 4 different controls (CAD render)."""
from s2lib import *

W, H, T = 500, 900, 150
d = D("variable-speed-fan-game-box", [W, T, H], {
    "case": "plastic#1a9cde", "dark": "plastic#1784bb", "grille": "plastic#16729e"})
panel(d, W, H, T, "case", inset=17, ear_c=(63, 837), ear_r=63, yt=875, rb=30, grille="grille", grille_d=48,
      bumps=(21, 3, 117, 108), bump_ring=42, case_dark="dark", step=45)
# recessed face panel framed by a thin groove
d.add("face-groove", "slab", "dark", plane="front", box=[55, 117, T - 2, 436, 799, T + 0.3], radii=[8], r=1)
d.add("face", "slab", "case", plane="front", box=[60, 122, T - 2, 431, 794, T + 0.9], radii=[6], r=1)
F = T + 0.9
ys = [653, 523, 397, 267]
for i, y in enumerate(ys):
    # black round fan grille (slightly taller than wide) with a 3-blade blue star
    # the photo's grille is dark navy (25,74,107 → 30,66,90), not black, with concentric guard rings
    d.add(f"fan{i}", "loft", "plastic#1d3f58", axis="z", sections=[
        sec(F - 2, 76, 84, 38, 159, y), sec(F + 4, 76, 84, 38, 159, y), sec(F + 7, 68, 76, 34, 159, y)])
    for k, (rw, rh) in enumerate(((56, 62), (36, 40))):
        d.add(f"fan{i}-ring{k}", "loft", "plastic#2f5f80", axis="z", soft=True, sections=[
            sec(F + 7, rw, rh, rw / 2, 159, y), sec(F + 7.8, rw, rh, rw / 2, 159, y)])
        d.add(f"fan{i}-ringin{k}", "loft", "plastic#1d3f58", axis="z", soft=True, sections=[
            sec(F + 7.1, rw - 5, rh - 5, (rw - 5) / 2, 159, y), sec(F + 8, rw - 5, rh - 5, (rw - 5) / 2, 159, y)])
    for k, a in enumerate((90, 210, 330)):
        d.box(f"fan{i}-b{k}", [159, y - 2, F + 8, 159 + 30, y + 2, F + 9.5], "gloss#3a7fd0", soft=True,
              rot=rot("z", a, [159, y, F + 7]))
    d.cyl(f"led{i}", [260, y, F - 1], [260, y, F + 4], 12, "gloss#c81a1a")
# controls on the right: yellow knob, push rod, small button, blue crank face
d.cyl("knob-ring", [352, 653, F - 1], [352, 653, F + 4], 50, "black#18191c")
d.lathe("knob", [352, 653, F + 4], [[0, 0], [20, 0], [20, 10], [17, 16], [0, 17]], "gloss#f2e40e", axis="z")
d.box("rod-slot", [322, 517, F - 1, 382, 529, F + 2], "black#18191c", r=3)
d.box("rod", [328, 519, F + 1, 378, 527, F + 6], "gloss#f4f4f4", r=3)
d.sphere("rod-knob", [325, 523, F + 10], 20, "gloss#2a9a3e")
d.cyl("btn", [356, 397, F - 1], [356, 397, F + 4], 8, "plastic#8a96a0")
d.add("crank", "loft", "gloss#1f3fa0", axis="z", sections=[
    sec(F - 1, 88, 96, 44, 358, 257), sec(F + 10, 88, 96, 44, 358, 257), sec(F + 14, 80, 88, 40, 358, 257)])
d.sphere("eye-l", [340, 270, F + 14], 13, "gloss#d42020")
d.box("eye-r", [366, 266, F + 13, 382, 273, F + 16], "gloss#f2d020", r=3)
d.slab("smile", "front", "M 330 247 L 386 247 Q 386 220 358 220 Q 330 220 330 247 Z", [F + 13, F + 16], "gloss#3cbf4a", r=1)
d.save()
