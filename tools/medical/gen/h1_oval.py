from h1lib import *
# Oval hydromassage bathtub (cover photo): white egg-shaped tub, wider at the right (control) end, broad rounded rim with
# a seam under it, bulging skirt with two round lamp lenses, foamy water; spout, valves, shower post and a round dial on
# the right end of the rim, two chrome grab bars.
d = D("oval-hydromassage-bathtub", [1900, 1100, 750], {
    "shell": "gloss#f8f9fa", "inner": "gloss#f1f4f6", "water": "acrylic#e4f1f4c8", "seam": "gloss#e3e7ea",
    "lens": "acrylic#dce8f070", "dial": "gloss#c9c3d6"})
CZ = 550
def egg(t):  # half width (z) along the length, wider at the right end
    u = abs(2 * t - 1)
    return 550 * (1 - u ** 2.4) ** (1 / 2.4) * (0.80 + 0.20 * t)
def hw_at(x, off=0):
    return egg(x / 1900) + off
outer = profile_outline(0, 1900, egg, CZ, n=70)
# skirt bulges out wider than the rim (photo: the barrel below the seam stands proud of the rim fascia)
d.slab("body", "top", P(outer), [70, 600], "shell", r=130)
d.slab("plinth", "top", P(offset(outer, -110)), [0, 80], "shell", r=20)
d.slab("seam", "top", ring(offset(outer, -34), offset(outer, -90)), [600, 652], "seam", r=12)
hole = profile_outline(150, 1480, lambda t: 430 * (1 - abs(2 * t - 1) ** 2.2) ** (1 / 2.2) * (0.86 + 0.14 * t), 535, n=60)
tub(d, "", None, hole, offset(outer, -26), 650, 95, 300, offset(outer, -120), water=705, rim_r=45)
# two clear lamp lenses on the upper skirt, just under the seam
for i, x in enumerate((870, 1600)):
    z = CZ + egg(x / 1900) - 4
    slope = (egg((x + 10) / 1900) - egg((x - 10) / 1900)) / 20
    turn = rot("y", round(math.degrees(math.atan(-slope)), 1), [x, 450, z])
    d.sphere(f"lens{i}", [x, 450, z], None, "lens", radii=[70, 70, 7], rot=turn)
    d.lathe(f"lens{i}-ring", [x, 450, z - 6], [[70, 0], [86, 0], [86, 10], [70, 10]], "seam", axis="z", soft=True, rot=turn)
RT = 745
# right end controls
d.tube("spout", [[1300, RT, 880], [1300, RT + 150, 875], [1240, RT + 165, 850], [1215, RT + 90, 835]], 32, "chrome",
       bend=50)
d.lathe("spout-base", [1300, RT - 4, 880], [[0, 0], [30, 0], [30, 8], [20, 14], [0, 14]], "chrome")
valve(d, "valve", 1510, RT - 4, 850, disc=170, lever=60, ang=-120)
d.cyl("valve-col", [1510, RT + 40, 850], [1510, RT + 110, 850], 44, "chrome")
d.lathe("dial", [1745, RT - 4, 720], [[0, 0], [100, 0], [100, 10], [94, 16], [0, 14]], "chrome")
d.lathe("dial-face", [1745, RT + 8, 720], [[0, 0], [88, 0], [88, 3], [0, 3]], "dial", soft=True)
d.cyl("valve-tall", [1650, RT - 4, 470], [1650, RT + 110, 470], 50, "chrome")
d.lathe("valve-tall-base", [1650, RT - 4, 470], [[0, 0], [45, 0], [45, 6], [30, 14], [0, 14]], "chrome")
d.cyl("shower-post", [1560, RT - 4, 300], [1560, RT + 230, 300], 34, "chrome", d2=40)
d.lathe("shower-base", [1560, RT - 4, 300], [[0, 0], [38, 0], [38, 6], [24, 14], [0, 14]], "chrome")
d.lathe("btn", [1170, RT - 4, 930], [[0, 0], [22, 0], [22, 6], [0, 8]], "chrome", copies=[[520, 0, -380]])
# chrome grab bars: an arch over the back rim and a curved bar at the left end
d.tube("bar-back", [[870, RT, 95], [880, RT + 120, 100], [1150, RT + 125, 120], [1190, RT, 135]], 28, "chrome", bend=90)
d.tube("bar-left", [[720, RT, 935], [700, RT + 90, 930], [540, RT + 120, 860], [500, RT, 820]], 28, "chrome", bend=80)
d.save()
