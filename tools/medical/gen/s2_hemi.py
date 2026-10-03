"""symphony-hemisphere-light: LED crystal magic ball — clear faceted dome on a round black body with a front label
plate and foot bracket; black power cord with plug on the left, IR remote lying on the right."""
from s2lib import *

W, Dp, H = 330, 200, 220
d = D("symphony-hemisphere-light", [W, Dp, H], {
    "body": "gloss#121315", "clear": "acrylic#e8eef590", "ring": "acrylic#dce4eccc", "silver": "metal#c0c4c8"})
cx, cz = 150, 98
# round black body with a rounded bottom
d.lathe("body", [cx, 0, cz], [[0, 22], [58, 22], [76, 32], [86, 50], [90, 75], [90, 107], [0, 107]], "body")
# front label plate (photo: 124 x 61, y 23..84, flush on the body front) on the black foot bracket (117 x 23)
d.box("plate", [cx - 62, 22, cz + 40, cx + 62, 86, cz + 88], "body", r=3)
fr = (f"M {cx-60} 24 L {cx+60} 24 L {cx+60} 84 L {cx-60} 84 Z M {cx-57} 27 L {cx+57} 27 L {cx+57} 81 L {cx-57} 81 Z")
d.slab("plate-frame", "front", fr, [cz + 88, cz + 89.5], "silver", r=0.3, soft=True)
d.box("logo", [cx - 30, 62, cz + 88, cx + 30, 74, cz + 89.5], "silver", soft=True)
d.box("logo-k", [cx - 25, 64.5, cz + 89.5, cx + 25, 71.5, cz + 90.5], "black#222326", soft=True)
d.decal("txt", [cx, 48, cz + 88.8], [82, 2.5], "front", "silver", soft=True, copies=[[0, -8, 0]])
d.box("foot", [cx - 58, 0, cz - 50, cx + 58, 23, cz + 82], "body", r=2)
# clear ring band (photo: clear vertical facets showing the black inside, a silver line under it)
d.cyl("band-in", [cx, 106, cz], [cx, 130, cz], 168, "black#1a1b1e")
d.cyl("ring", [cx, 107, cz], [cx, 129, cz], 184, "glass", sides=16)
d.cyl("band-line", [cx, 106, cz], [cx, 109, cz], 185, "silver", soft=True)
# faceted crystal dome: polygonal frustum bands, every other band turned half a facet; a grey LED-lens core inside
# shows through the translucent facets (the photo's grey crystal look)
prof = [(88, 0), (87, 18), (82, 36), (74, 52), (62, 66), (46, 78), (26, 87), (0, 91)]
for k in range(len(prof) - 1):
    (r0, h0), (r1, h1) = prof[k], prof[k + 1]
    n = 14 if k < 5 else 10
    d.cyl(f"dome{k}", [cx, 129 + h0, cz], [cx, 129 + h1, cz], 2 * r0, "acrylic#d4dce4b8", d2=max(2 * r1, 0.5), sides=n,
          rot=rot("y", (180 / n) * (k % 2), [cx, 0, cz]))
# the LED lens cluster inside: a dark faceted ball low in the dome (photo: dark lenses behind the lower facets)
d.cyl("dome-core", [cx, 129, cz], [cx, 175, cz], 120, "black#2a2d32", d2=60, sides=10, soft=True)
# power cord: from the body's left side down to a loose loop on the desk, plug at the end
d.tube("cord", [[cx - 86, 60, cz], [cx - 112, 40, cz + 5], [32, 5, cz + 30], [8, 4, 150], [30, 4, 188], [70, 4, 170],
                [60, 4, 120], [20, 4, 92], [12, 4, 40]], 7, "black#0e0e10", bend=18, soft=True)
d.box("plug", [2, 0, 12, 22, 14, 42], "black#0e0e10", r=3)
d.box("plug-pins", [8, 5, 4, 16, 8, 12], "chrome", soft=True)
# IR remote standing upright on the right, facing front (as on the photo): 56 x 150 x 14, black top with 2 red keys
# and 3 x 3 small dark keys, a white lower panel with 3 x 3 black round keys
rx0, rx1, rz0, rz1 = 249, 305, 120, 134
F2 = rz1
d.box("remote", [rx0, 0, rz0, rx1, 150, rz1], "body", r=5)
d.cyl("rem-red", [rx0 + 12, 136, F2 - 1], [rx0 + 12, 136, F2 + 2], 12, "gloss#d81e22", copies=[[32, 0, 0]])
d.cyl("rem-mid", [rx0 + 28, 140, F2 - 1], [rx0 + 28, 140, F2 + 1.5], 8, "black#3a3c40")
d.box("rem-key", [rx0 + 7, 112, F2 - 1, rx0 + 17, 118, F2 + 1.5], "black#3a3c40", r=2,
      copies=[[i * 16, -j * 12, 0] for i in range(3) for j in range(3) if (i, j) != (0, 0)])
d.box("rem-panel", [rx0 + 4, 10, F2 - 1, rx1 - 4, 70, F2 + 0.8], "plastic#e8eaec", r=2)
d.cyl("rem-key2", [rx0 + 12, 58, F2], [rx0 + 12, 58, F2 + 2.5], 10, "black#151618",
      copies=[[i * 16, -j * 19, 0] for i in range(3) for j in range(3) if (i, j) != (0, 0)])
d.save()
