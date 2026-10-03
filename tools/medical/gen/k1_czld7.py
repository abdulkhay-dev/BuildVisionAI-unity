"""xy-k-czld-vii: sonic vibration walkway with parallel bars. Long axis x; front (z max) = the side with the console column.
Rails drawn at the lowest printed armrest height (1050)."""
import math
from k1lib import *

d = D("xy-k-czld-vii", [3600, 1000, 1210], {
    "white": "plastic#f3f4f5", "blue": "plastic#8fb6d8", "rail": "gloss#8fb3d3", "chrome": "chrome",
    "plinth": "plastic#8a8f96", "dark": "plastic#3a3f46", "tick": "plastic#9aa3ad", "screen": "screen"})
Z0, Z1 = 120, 900          # platform
B = 60                     # white border
PY = 150                   # platform top
# --- ramps at both ends (white body, blue top, tick marks along both borders)
ang = math.degrees(math.atan2(PY - 10, 600))
for nm, x0, x1, s in (("l", 0, 600, 1), ("r", 3600, 3000, -1)):
    lo, hi = min(x0, x1), max(x0, x1)
    body = f"M {x0} 0 L {x1} 0 L {x1} {PY} L {x0} 10 Z"
    d.slab(f"ramp-{nm}", "front", body, [Z0, Z1], "white", r=4)
    top = f"M {x0} 10 L {x1} {PY} L {x1} {PY + 3} L {x0} 13 Z"
    d.slab(f"ramp-top-{nm}", "front", top, [Z0 + B, Z1 - B], "blue", r=1)
    T = rot("z", s * ang, [x0, 10, 0])
    for zn, zc in (("f", Z1 - B / 2), ("b", Z0 + B / 2)):
        d.box(f"ramp-tick-{nm}-{zn}", [x0 + s * 30 - 2, 11, zc - 18, x0 + s * 30 + 2, 13, zc + 18], "tick", soft=True,
              rot=T, repeat={"n": 18, "step": [s * 33, 0, 0], "local": True})
    d.decal(f"ramp-logo-{nm}", [(x0 + x1) / 2, (10 + PY) / 2 + 3, (Z0 + Z1) / 2], [180, 40], "top", "plastic#c9dbea",
            soft=True, rot=rot("z", s * ang, [(x0 + x1) / 2, (10 + PY) / 2, 0]))
# --- platform: white frame on a recessed grey plinth, blue walking surface, footprints, ruler ticks
d.box("plinth", [1000, 0, Z0 + 100, 2600, 50, Z1 - 100], "plinth", r=6)
d.box("motor", [1700, 8, Z1 - 110, 1950, 48, Z1 - 95], "dark", r=4)
d.box("platform", [600, 45, Z0, 3000, PY, Z1], "white", r=10)
d.box("walk", [600, PY - 1, Z0 + B, 3000, PY + 2, Z1 - B], "blue", r=1)
d.box("tick", [640, PY, Z1 - B + 6, 643, PY + 1.5, Z1 - 8], "tick", soft=True, repeat=rep(70, [34, 0, 0]),
      copies=[[0, 0, -(Z1 - Z0 - B)]])
for i, x in enumerate(range(800, 2900, 420)):
    for side, zc, dx in (("a", 440, 0), ("b", 590, 210)):
        if x + dx > 2850:
            continue
        d.slab(f"foot-{i}{side}", "top", ellipse(x + dx, zc, 85, 34), [PY + 2, PY + 3.5], "white", r=0.5, soft=True)
        d.slab(f"toe-{i}{side}", "top", ellipse(x + dx + 108, zc, 18, 30), [PY + 2, PY + 3.5], "white", r=0.5, soft=True)
# --- posts: white 80x80 with a light-blue inlay outside, T head (blue stub, chrome joint, stem up to the rail)
RY = 1050
posts = (("nl", 950, Z1 - 45, 1), ("nr", 2880, Z1 - 45, 1), ("fl", 800, Z0 + 45, -1), ("fr", 2700, Z0 + 45, -1))
for nm, x, z, s in posts:
    d.box(f"post-{nm}", [x - 40, PY, z - 40, x + 40, 920, z + 40], "white", r=6)
    zf = z + s * 40
    d.box(f"post-inlay-{nm}", [x - 28, PY + 40, min(zf, zf + s * 2), x + 28, 900, max(zf, zf + s * 2)], "blue", r=3)
    d.box(f"post-latch-{nm}", [x - 12, 300, min(zf, zf - s * 4) - 0, x + 12, 420, max(zf, zf - s * 4)], "tick", r=3,
          soft=True)
    # width-adjust handle: a short blue stub pointing outward, across the walkway (photo), rounded end
    d.cyl(f"stub-{nm}", [x, 940, z], [x, 940, z + s * 125], 34, "rail")
    d.sphere(f"stub-end-{nm}", [x, 940, z + s * 125], 34, "rail")
    d.box(f"joint-{nm}", [x - 28, 918, z - 28, x + 28, 965, z + 28], "chrome", r=8)
    d.cyl(f"stem-{nm}", [x, 960, z], [x, RY, z], 30, "rail")
# near rail: single straight tube with rounded ends
d.cyl("rail-near", [450, RY, Z1 - 45], [3200, RY, Z1 - 45], 40, "rail")
d.sphere("rail-near-end", [450, RY, Z1 - 45], 40, "rail", copies=[[2750, 0, 0]])
# far rail: closed loop of two tubes 100 apart joined by U bends
zf = Z0 + 45
d.tube("rail-far", [[300, RY, zf], [3050, RY, zf], [3050, RY, zf + 100], [300, RY, zf + 100], [300, RY, zf]], 40,
       "rail", bend=50)
# --- console column on the floor in front of the near border: blue inlay, round logo, sloped top with the screen
col = "M 850 0 L 1000 0 L 1000 1200 L 850 1130 Z"
d.slab("console", "side", col, [1000, 1200], "white", r=10)
d.box("console-inlay", [1032, 250, 999, 1168, 1100, 1003], "blue", r=4)
# round-cornered blue logo tile at the foot of the column with a white "S" (photo)
d.box("console-logo", [1040, 70, 999, 1160, 210, 1004], "blue", r=18)
text(d, "console-S", "S", [1100 - 21, 105, 1004.5], 70, "white", stroke=11)
# "Sunnyou 翔宇" reading up the inlay (photo)
text(d, "console-text", "Sunnyou", [1100 + 17, 520, 1003.5], 34, "white", along=(0, 1))
text(d, "console-text-cn", "翔宇", [1100 + 17, 520 + text_len("Sunnyou ", 34) + 6, 1003.5], 34, "white", along=(0, 1))
T = rot("x", -25, [1100, 1165, 925])
d.box("screen-bezel", [1018, 1160, 862, 1182, 1168, 988], "white", r=8, rot=T)
d.add("screen", "screen", "dark", box=[1030, 1166, 874, 1170, 1171, 976], r=4, face="top", bezel=3, rot=T)
d.save()
