"""kinesio-5: xy-5 arched sit-up bench. Board high end with the foot rollers at the back (z small), low end at
the front (z = 1310), as in the photo (near end low)."""
import math
from k5lib import *

W, DD, H = 370, 1310, 600
d = D("xy-5", [W, DD, H], {"pad": "leather#4f7fc8", "frame": "plastic#eceae2", "foam": "rubber#1b1b1d",
                            "chrome": "chrome", "knob": "plastic#141416"})
CX = W / 2
# board centre-line: circular arc, apex near the high end
AZ, AY, R = 150, 548, 1944


def arc_y(z):
    return AY - (R - math.sqrt(max(R * R - (z - AZ) ** 2, 0)))


def nrm(z):  # outward (upper) normal of the arc at z, in (dz, dy)
    s = (z - AZ) / R
    return (s, math.sqrt(1 - s * s))


T = 56  # board thickness
Z0, Z1 = 30, 1295
top, bot = [], []
n = 28
for k in range(n + 1):
    z = Z0 + (Z1 - Z0) * k / n
    y = arc_y(z)
    nz, ny = nrm(z)
    top.append((z + nz * T / 2, y + ny * T / 2))
    bot.append((z - nz * T / 2, y - ny * T / 2))
outline = poly(top + bot[::-1])
d.slab("board", "side", outline, [CX - 175, CX + 175], "pad", r=22)
# chrome screw buttons in three pairs along the board
for i, z in enumerate((330, 760, 1170)):
    y = arc_y(z)
    nz, ny = nrm(z)
    # recessed tufting button: a darker dimple, a flat chrome ring round a dark hole (not a dome)
    deg = math.degrees(math.atan2(nz, ny))
    p = [CX - 95, y + ny * (T / 2 - 0.5), z + nz * (T / 2 - 0.5)]
    cp = [[190, 0, 0]]
    d.lathe(f"dimple{i}", p, [[0, 0], [21, 0], [21, 0.8], [0, 1.2]], "leather#33609f", rot=rot("x", deg, p),
            copies=cp, soft=True)
    d.lathe(f"button{i}", p, [[6, 0], [12, 0], [12.5, 2.2], [11, 3.6], [7.5, 3.6], [6, 2.2]], "chrome",
            rot=rot("x", deg, p), copies=cp, soft=True)
    d.lathe(f"hole{i}", p, [[0, 0], [6.5, 0], [6.5, 1.6], [0, 1.6]], "plastic#2a2c30", rot=rot("x", deg, p),
            copies=cp, soft=True)
# --- rear support: T foot, post rising to the board underside, two pairs of foam rollers
d.cyl("foot-r", [22, 22, 190], [W - 22, 22, 190], 44, "frame")
d.lathe("foot-r-cap", [18, 22, 190], [[0, 0], [23, 0], [23, 14], [16, 18], [0, 18]], "frame", axis="x",
        rot=rot("y", 180, [18, 22, 190]), copies=[[0, 0, 0]])
d.lathe("foot-r-cap2", [W - 18, 22, 190], [[0, 0], [23, 0], [23, 14], [16, 18], [0, 18]], "frame", axis="x")
d.bar("post", [CX, 30, 190], [CX, arc_y(150) - T / 2 + 5, 150], [42, 42], "frame", r=5)
for k in range(6):  # adjustment holes on the post front
    y = 300 + k * 32
    zz = 190 - (y - 30) / (arc_y(150) - T / 2 - 25) * 40 + 21
    d.cyl(f"phole{k}", [CX, y, zz], [CX, y, zz + 2], 9, "plastic#3a3a3a", soft=True)
# lower roller pair on a cross axle with a black pop-pin knob
YL, ZL = 255, 183


def roller(id, y, z):
    prof = [[0, 0], [48, 0], [52, 8], [52, 30], [44, 85], [52, 140], [52, 162], [48, 170], [0, 170]]
    d.lathe(id + "-a", [CX - 32, y, z], prof, "foam", axis="x", rot=rot("y", 180, [CX - 32, y, z]))
    d.lathe(id + "-b", [CX + 32, y, z], prof, "foam", axis="x")
    d.cyl(id + "-axle", [CX - 34, y, z], [CX + 34, y, z], 26, "frame")


roller("roll-lo", YL, ZL)
knob(d, "pin", [CX, YL + 60, ZL + 18], axis="z", dd=34)
# upper roller pair at the high end, just under / behind the board end
YU, ZU = 545, 45
roller("roll-hi", YU, ZU)
d.bar("hi-arm", [CX, YU, ZU], [CX, arc_y(150) - T / 2 + 5, 140], [36, 30], "frame", r=4)
# spring latch at the post top: a chrome wire clip hanging on the post's front face
d.tube("hook", [[CX - 13, 505, 176], [CX - 13, 455, 182], [CX + 13, 455, 182], [CX + 13, 505, 176]], 4, "chrome",
       bend=8, soft=True)
d.box("hook-plate", [CX - 17, 495, 172, CX + 17, 512, 178], "chrome", r=2)
# --- front support: T foot and a short post under the low end
ZF = 1215
d.cyl("foot-f", [22, 22, ZF], [W - 22, 22, ZF], 44, "frame")
d.lathe("foot-f-cap", [18, 22, ZF], [[0, 0], [23, 0], [23, 14], [16, 18], [0, 18]], "frame", axis="x",
        rot=rot("y", 180, [18, 22, ZF]))
d.lathe("foot-f-cap2", [W - 18, 22, ZF], [[0, 0], [23, 0], [23, 14], [16, 18], [0, 18]], "frame", axis="x")
d.bar("post-f", [CX, 40, ZF], [CX, arc_y(ZF - 10) - T / 2 + 6, ZF - 10], [36, 36], "frame", r=5)
d.box("bracket-f", [CX - 60, arc_y(ZF) - T / 2 - 12, ZF - 60, CX + 60, arc_y(ZF) - T / 2 + 4, ZF + 40], "frame",
      r=4, rot=rot("x", math.degrees(math.asin((ZF - AZ) / R)), [CX, arc_y(ZF) - T / 2, ZF]))
d.save()
