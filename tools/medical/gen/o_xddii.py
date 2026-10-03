# XDD-II UV sterilizer tower trolley: white tower, navy stripe and lettering, glass panel, 3 quartz tubes — other-1
import math
from o_lib import *
W = 560
C = 280
TW, TD = 230, 210
d = D("xdd-ii", [W, W, 1700], {
    "white": "plastic#f4f5f7", "navy": "gloss#22275e", "blk": "plastic#16171b", "uv": "gloss#f2f8ff",
    "uvglass": "acrylic#9ed6ffa0", "grey": "plastic#9aa0a8", "txt": "plastic#8f94b4", "violet": "gloss#3b3494"})
# X base: 4 legs (white top over a black under-layer) on twin castors
o = 232
ends = [(C - o, C), (C + o, C), (C, C - o), (C, C + o)]
for i, (a, b) in enumerate(((ends[0], ends[1]), (ends[2], ends[3]))):
    d.slab(f"leg-blk{i}", "top", stadium(a, b, 38), [72, 96], "blk", r=5)
    d.slab(f"leg-top{i}", "top", stadium(a, b, 36), [96, 104], "white", r=3)
for i, (x, z) in enumerate(ends):
    caster(d, f"castor{i}", [x, 0, z], 75, "plastic#a9adb3")
# tower: rounded white column with a wider foot
Z1 = C + TD / 2
XL, XR = C - TW / 2, C + TW / 2
d.loft("foot", [sec(100, 280, 260, 60, C, C), sec(122, 262, 242, 52, C, C), sec(140, TW, TD, 36, C, C)], "white")
d.loft("tower", [sec(138, TW, TD, 36, C, C), sec(1000, TW, TD, 36, C, C)], "white")
# navy cap plate, tube sockets, 3 quartz tubes in a triangle, navy top cap
d.box("cap", [C - 128, 998, C - 118, C + 128, 1024, C + 118], "navy", r=8)
tubes = [(C - 30, C + 22), (C + 30, C + 22), (C, C - 30)]
for i, (x, z) in enumerate(tubes):
    d.cyl(f"sock{i}", [x, 1024, z], [x, 1046, z], 36, "navy")
    d.cyl(f"tube{i}", [x, 1046, z], [x, 1658, z], 17, "uv", soft=True)
    d.cyl(f"tubeg{i}", [x, 1046, z], [x, 1658, z], 27, "uvglass", soft=True)
d.box("top", [C - 60, 1656, C - 60, C + 60, 1690, C + 60], "navy", r=8)
d.box("top-lid", [C - 52, 1688, C - 52, C + 52, 1700, C + 52], "navy", r=5)
# front: glass control panel (printed crop, white corners blend into the tower), sensor dot, REAHER logo
def U(u): return XL + u * TW
screen(d, "panel", [U(0.11), 800, Z1 - 1, U(0.11) + 70, 937, Z1 + 1.2], "white", r=4, face="front",
       print="med_xdd-ii_screen", bezel=0)
d.cyl("sensor", [U(0.22), 972, Z1], [U(0.22), 972, Z1 + 3], 9, "grey")
d.decal("logo-g", [U(0.73) - 4, 978, Z1 + 0.6], [16, 10], "front", "gloss#3fae49", soft=True)
d.decal("logo-b", [U(0.73) + 4, 966, Z1 + 0.6], [16, 10], "front", "gloss#2c7fd0", soft=True)
text(d, "reaher", "REAHER", [U(0.62), 944, Z1 + 0.6], 9, "navy", stroke=1.8)
# navy stripe (photos): high up it runs down the rounded right corner, jogs diagonally onto the flat front and runs
# down to the foot; the flat part is a front slab, the corner part a band following the corner arc
RC = 36
st = [(U(0.655), 140), (U(0.80), 140), (U(0.80), 768), (XR - RC + 1, 818), (XR - RC + 1, 880), (U(0.655), 772)]
d.slab("stripe", "front", poly(st), [Z1 - 1, Z1 + 1.2], "navy", soft=True)
ccx, ccz = XR - RC, Z1 - RC


def band(id, a0, a1, y0, y1, n=8):
    pts = [(ccx + (RC + 1.4) * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
            ccz + (RC + 1.4) * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    pts += [(ccx + (RC - 2) * math.cos(math.radians(a1 - (a1 - a0) * k / n)),
             ccz + (RC - 2) * math.sin(math.radians(a1 - (a1 - a0) * k / n))) for k in range(n + 1)]
    d.slab(id, "top", "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in pts) + " Z", [y0, y1], "navy", soft=True)


# slices whose lower ends climb with the diagonal (90 deg = the flat front's edge at y 818 ... 34 deg at y 880)
for k in range(10):
    a0 = 34 + 5.6 * k
    band(f"stripe-c{k}", a0, 90 if k == 0 else a0 + 5.6, 880 - (a0 - 34) / 56 * 62, 1000)
# lettering: UV-C DISINFECTION (blue-violet) reading top to bottom in the middle; UV-C STRIKE GERM-ZAPPING (light
# grey-blue) printed ON the stripe, spaced letters
text(d, "dis", "UV-C DISINFECTION", [U(0.32), 555, Z1 + 0.6], 20, "violet", along=(0, -1), stroke=2.6)
text(d, "zap", "UV-C STRIKE GERM-ZAPPING", [U(0.69), 690, Z1 + 1.8], 20, "txt", along=(0, -1), stroke=2.2, gap=0.48)
# SER mark (photos): a blue-violet "2"-like sign turned a quarter: right bar, short left leg joined by a curved top,
# "SER" under the left leg
ser = (f"M {U(0.219)} 222 L {U(0.29)} 222 L {U(0.29)} 256 Q {U(0.29)} 270 {U(0.3125)} 272 L {U(0.3125)} 196 "
       f"L {U(0.39)} 196 L {U(0.39)} 298 L {U(0.30)} 298 Q {U(0.219)} 292 {U(0.219)} 262 Z")
d.slab("ser-mark", "front", ser, [Z1 - 1, Z1 + 1.2], "violet", soft=True)
text(d, "ser", "SER", [U(0.222), 202, Z1 + 0.6], 10, "violet", stroke=1.6, gap=0.15)
# black handle (photos): a bracket from the front face right of the stripe, out round the front-right corner and back
# into the right side; its grip stands ~36 mm beyond the right side
HY = 902
d.sweep("handle", [[U(0.74), HY, Z1 - 4], [U(0.74), HY, Z1 + 26], [XR + 30, HY, Z1 + 26], [XR + 30, HY, Z1 - 70],
                   [XR - 4, HY, Z1 - 70]], [12, 40], "blk", shape="rect", r=4, bend=16)
d.save()
