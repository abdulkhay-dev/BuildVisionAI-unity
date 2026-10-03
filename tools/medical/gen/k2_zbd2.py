"""xy-zbd-ib (upper limb rotary disc, H base) / xy-zbd-iie (bedside lower limb, inclined boom) (kinesio-2)."""
import math
from k2lib import *

# =============== XY-ZBD-IB: light-blue H base, column with hinge, peanut-shaped head with turntable + grips
d = D("xy-zbd-ib", [700, 800, 1300], {
    "blue": "gloss#4a90d9", "white": "gloss#f2f3f5", "black": "plastic#1d1f22", "grip": "rubber#18191b",
    "steel": "metal#c3c7cc", "chrome": "chrome", "disc": "plastic#3a3d42", "red": "gloss#d42a24"})
CX, CZ = 350, 400
for z in (90, 710):
    d.box(f"rail-{z}", [20, 100, z - 25, 680, 150, z + 25], "blue", r=5)
    d.cyl(f"brake-rod-{z}", [60, 140, z + 32], [640, 140, z + 32], 10, "chrome")
    for x in (45, 655):
        caster(d, f"castor-{z}-{x}", [x, 0, z], 75, "rubber#2a2b2e")
        d.box(f"brake-{z}-{x}", [x - 15, 70, z + 28, x + 15, 80, z + 60], "black", r=3)
    for x in (140, 560):
        d.cyl(f"level-{z}-{x}", [x, 20, z], [x, 100, z], 16, "chrome")
        d.cyl(f"level-pad-{z}-{x}", [x, 0, z], [x, 20, z], 52, "black")
d.box("crossbar", [CX - 30, 100, 90, CX + 30, 150, 710], "blue", r=5)
d.tube("footrest", [[CX - 30, 190, 330], [CX - 270, 190, 330], [CX - 270, 190, 490], [CX - 30, 190, 490]], 12, "chrome", bend=15)
# column: blue square tube with two black star knobs, silver telescopic part, hinge bracket + gas spring
d.box("column", [CX - 50, 150, CZ - 50, CX + 50, 620, CZ + 50], "blue", r=6)
star_knob(d, "knob-a", [CX, 470, CZ + 50], "z", 1, dd=50, l=34)
star_knob(d, "knob-b", [CX, 390, CZ + 50], "z", 1, dd=50, l=34)
d.box("telescope", [CX - 42, 600, CZ - 42, CX + 42, 720, CZ + 42], "steel", r=4)
d.box("hinge", [CX - 48, 700, CZ - 60, CX + 48, 770, CZ + 40], "black", r=6)
d.box("hinge-plate", [CX - 52, 690, CZ - 20, CX - 44, 780, CZ + 60], "steel", r=3, copies=[[96, 0, 0]])
d.cyl("gas-spring", [CX + 70, 610, CZ + 20], [CX + 70, 700, CZ + 20], 22, "black")
d.cyl("gas-rod", [CX + 70, 700, CZ + 20], [CX + 70, 775, CZ + 20], 10, "chrome")
# head: deep box part on the left + round part on the right (peanut), turntable on the round part
d.box("head-box", [30, 680, 230, 400, 950, 570], "white", r=55)
d.lathe("head-round", [480, 765, CZ], [[0, 0], [185, 0], [200, 18], [200, 165], [188, 185], [0, 185]], "white")
d.lathe("seam", [480, 800, CZ], [[0, 0], [201, 0], [201, 2], [0, 2]], "plastic#c9ccd0", soft=True)
d.box("seam-box", [30, 799, 569, 330, 801, 571], "plastic#c9ccd0", soft=True)
d.sweep("grab", [[70, 860, 565], [70, 860, 620], [270, 860, 620], [270, 860, 565]], [34, 34], "black", shape="round", bend=32)
d.lathe("estop", [355, 870, 569], [[0, 0], [22, 0], [22, 6], [15, 8], [15, 18], [0, 20]], "red", axis="z")
d.lathe("turntable", [480, 950, CZ], [[0, 0], [150, 0], [152, 6], [0, 8]], "disc")
d.cyl("hub", [480, 955, CZ], [480, 1035, CZ], 56, "chrome")
d.lathe("carrier", [480, 990, CZ], [[0, 0], [72, 0], [72, 8], [0, 8]], "steel")
d.box("bracket", [455, 1005, CZ - 70, 680, 1040, CZ + 10], "black", r=8)
d.box("bracket-up", [600, 1005, CZ - 70, 680, 1110, CZ - 30], "black", r=6)
d.lathe("grip-disc", [500, 1035, CZ - 40], [[0, 0], [45, 0], [45, 6], [0, 6]], "steel")
for i, (x, z) in enumerate(((500, CZ - 40), (625, CZ - 10), (670, CZ - 50))):
    d.cyl(f"grip{i}", [x, 1040, z], [x, 1195, z], 42, "grip")
    d.cyl(f"grip-cap{i}", [x, 1195, z], [x, 1202, z], 34, "black")
d.cyl("roller", [530, 1080, CZ - 15], [600, 1080, CZ - 15], 62, "grip")
# white square screen box on a neck over the rear-left of the box part, tilted back
d.cyl("neck", [170, 950, 290], [170, 1010, 290], 52, "white")
R = rot("x", -14, [170, 1010, 290])
scr(d, "screen", [45, 1010, 255, 295, 1250, 325], "white", r=22, face="front", bezel=30, rot=R)
d.save()

# =============== XY-ZBD-IIE: bedside unit, boom sloping DOWN towards the bed, pendulum knee supports
d = D("xy-zbd-iie", [650, 1450, 1550], {
    "blue": "gloss#2f6fbf", "white": "plastic#eef0f2", "steel": "metal#c8ccd2", "black": "plastic#1d1f22",
    "pad": "leather#1f2023", "strap": "fabric#1a1b1d", "chrome": "chrome"})
CX = 325
# base: white box housing at the back on two flat blue legs reaching forward, castors front and rear
d.slab("housing", "side", "M 10 60 L 400 60 L 400 310 L 120 310 L 10 230 Z", [45, 605], "white", r=20)
d.box("leg", [50, 30, 0, 110, 64, 840], "blue", r=6, mirror="x")
d.add("castor", "caster", at=[80, 0, 810], d=60, mirror="x", copies=[[0, 0, -790]])
# column: blue lower, chrome telescopic upper, blue top block
CZ = 300
d.box("column", [CX - 50, 300, CZ - 50, CX + 50, 690, CZ + 50], "blue", r=8)
d.box("column-in", [CX - 42, 680, CZ - 42, CX + 42, 1190, CZ + 42], "steel", r=6)
d.box("column-collar", [CX - 55, 675, CZ - 55, CX + 55, 705, CZ + 55], "blue", r=8)
# bed-docking support: blue bar with knobs, black saddle under it, black U handle behind the column
d.box("clamp-sleeve", [CX - 56, 880, CZ - 56, CX + 56, 945, CZ + 56], "blue", r=10)
d.box("clamp-bar", [CX - 50, 930, CZ - 60, CX + 50, 965, CZ + 185], "blue", r=8)
# black trough saddle under the bar: a half-moon seen from the side (axis across x), as in the photo
d.slab("saddle", "side", f"M {CZ - 55} 930 L {CZ + 180} 930 Q {CZ + 175} 790 {CZ + 62} 785 Q {CZ - 50} 790 {CZ - 55} 930 Z",
       [CX - 110, CX + 110], "pad", r=25)
star_knob(d, "clamp-knob-f", [CX, 965, CZ + 150], "y", 1, dd=44, l=40)
star_knob(d, "clamp-knob-b", [CX, 965, CZ - 25], "y", 1, dd=44, l=40)
d.sweep("clamp-handle", [[CX - 70, 948, CZ - 55], [CX - 75, 948, CZ - 210], [CX + 75, 948, CZ - 210], [CX + 70, 948, CZ - 55]],
        [26, 26], "black", shape="round", bend=55)
# boom: blue top block, long blue rectangular boom sloping down ~25 deg to the bed, chrome inner section
d.box("top-block", [CX - 55, 1170, CZ - 60, CX + 55, 1310, CZ + 60], "blue", r=10)
A = math.radians(25)
def P(t): return [CX, 1245 - t * math.sin(A), CZ + 40 + t * math.cos(A)]
d.bar("boom", P(0), P(640), [100, 84], "blue", r=8)
d.bar("boom-in", P(620), P(820), [78, 62], "steel", r=6)
d.bar("boom-end", P(810), P(880), [96, 80], "blue", r=8)
pm = P(330)
for s, face in ((1, "right"), (-1, "left")):
    d.decal(f"boom-logo-{face}", [CX + s * 50.8, pm[1], pm[2]], [36, 36], face, "plastic#ffffff", soft=True)
    d.decal(f"boom-name-{face}", [CX + s * 50.8, pm[1] - 4, pm[2] + s * 90], [110, 18], face, "plastic#ffffff", soft=True,
            rot=rot("x", 25, [CX + s * 50.8, pm[1] - 4, pm[2] + s * 90]))
# crank hub at the boom end, blue crank links, white foot shells with black straps
H = P(880)
d.cyl("hub", [CX - 110, H[1], H[2]], [CX + 110, H[1], H[2]], 86, "chrome")
for s, a in ((1, -30), (-1, 150)):
    ra = math.radians(a)
    py, pz = H[1] + 110 * math.sin(ra), H[2] + 110 * math.cos(ra)
    xs = CX + s * 120
    nm = "r" if s > 0 else "l"
    d.bar(f"crank-{nm}", [xs, H[1], H[2]], [xs, py, pz], [24, 50], "blue", r=6)
    xp = CX + s * 175
    d.cyl(f"pedal-axle-{nm}", [xs, py, pz], [xp, py, pz], 24, "steel")
    d.loft(f"foot-shell-{nm}", [sec(pz - 120, 130, 110, 40, xp, py + 10), sec(pz + 170, 120, 90, 40, xp, py + 5)],
           "white", axis="z", dome="end")
    d.box(f"foot-pad-{nm}", [xp - 52, py + 50, pz - 110, xp + 52, py + 62, pz + 150], "black", r=8)
    for k, zz in enumerate((pz - 40, pz + 80)):
        d.strap(f"foot-strap-{nm}{k}", [[xp - 66, py + 20, zz], [xp, py + 80, zz], [xp + 66, py + 20, zz]], [40, 4], "strap",
                bend=30, soft=True)
# narrow blue rod from the boom end up-forward to the top pendulum hub (chrome, two knobs)
T = [CX, 1290, 1300]
d.bar("rod", [CX, H[1] + 30, H[2]], [CX, T[1] - 30, T[2] - 20], [50, 40], "blue", r=6)
d.cyl("top-hub", [CX - 90, T[1], T[2]], [CX + 90, T[1], T[2]], 70, "chrome")
d.cyl("top-hub-cap", [CX - 50, T[1], T[2]], [CX + 50, T[1], T[2]], 80, "blue")
for x in (CX - 60, CX + 60):
    d.cyl(f"top-knob-{x}", [x, T[1] + 30, T[2]], [x, T[1] + 70, T[2]], 24, "chrome")
    d.cyl(f"top-knob-head-{x}", [x, T[1] + 62, T[2]], [x, T[1] + 76, T[2]], 34, "chrome")
# pendulum rods down to the black knee cups (blue frames), one leg forward, one back; blue link to a front foot plate
for s, zc, yc in ((-1, 1400, 1040), (1, 1210, 1060)):
    xk = CX + s * 120
    nm = "l" if s < 0 else "r"
    d.cyl(f"pend-{nm}", [xk, T[1], T[2]], [xk, yc + 60, zc], 14, "black")
    o = (f"M {xk - 75} {yc + 50} L {xk - 75} {yc} Q {xk - 75} {yc - 70} {xk} {yc - 70} Q {xk + 75} {yc - 70} {xk + 75} {yc} "
         f"L {xk + 75} {yc + 50} L {xk + 62} {yc + 50} L {xk + 62} {yc} Q {xk + 62} {yc - 57} {xk} {yc - 57} "
         f"Q {xk - 62} {yc - 57} {xk - 62} {yc} L {xk - 62} {yc + 50} Z")
    d.slab(f"knee-cup-{nm}", "front", o, [zc - 70, zc + 50], "pad", r=6)
    d.box(f"knee-frame-{nm}", [xk - 80, yc - 20, zc - 10, xk + 80, yc + 10, zc + 10], "blue", r=4)
    star_knob(d, f"knee-knob-{nm}", [xk + s * 80, yc - 10, zc], "x", s, dd=36, l=28)
d.bar("front-link", [CX - 120, 1000, 1400], [CX - 120, 840, 1395], [30, 24], "blue", r=5)
d.box("front-foot", [CX - 190, 790, 1300, CX - 50, 830, 1445], "white", r=14)
d.strap("front-foot-strap", [[CX - 190, 830, 1370], [CX - 120, 880, 1370], [CX - 50, 830, 1370]], [40, 4], "strap", bend=30, soft=True)
# swivel touch screen on top of the column block, facing the bed
d.cyl("swivel", [CX, 1310, CZ], [CX, 1345, CZ], 60, "steel")
SR = rot("y", 70, [CX, 1345, CZ])          # swivelled to face the right side (the photo's camera)
scr(d, "screen", [CX - 120, 1345, CZ - 35, CX + 120, 1545, CZ + 35], "white", r=16, face="front", bezel=28, rot=SR)
d.decal("screen-lit", [CX, 1445, CZ + 35.8], [180, 140], "front", "gloss#aab8c6", soft=True, rot=SR)
d.save()
