from h1lib import *
# Whirlpool limb bath (prototype): blue lower shell, pale-blue upper tub with a raised back wall (S-curved ends down to
# the rim), a wide arm-support block at the left end (rounded concave inner face) and a narrow ledge at the right end,
# open basin between them; two stainless bow rails slanting from the front / right ledge over to the raised back;
# spout + knob + valve on the back top, grey hand shower in a holder at the back left with a hose looping out to the
# left and down into the base, white power cable; stainless U frame on 4 castors.
# Drawn in the photo's (lowest) position: rim 795 (printed height range 795–1445).
# Review 2026-10-02: arm humps were sunk below the rim (invisible) -> end blocks at rim level + raised back wall;
# rails slanted as in the photo; power cable added.
d = D("limb-whirlpool-bath-prototype", [1060, 660, 1100], {
    "blue": "gloss#6f9ee0", "pale": "gloss#c9dcf6", "inner": "gloss#c2d6f3", "frame": "chrome",
    "hose": "plastic#d9dde2", "dark": "black#2a2d31", "cable": "plastic#f2f2ee"})
CX, CZ = 560, 330
RIM = 796
d.loft("lower", [sec(150, 930, 575, 80, CX, CZ), sec(175, 955, 598, 88, CX, CZ), sec(625, 965, 605, 90, CX, CZ)],
       "blue", caps=False)
d.loft("upper", [sec(605, 972, 612, 92, CX, CZ), sec(632, 1000, 640, 102, CX, CZ), sec(765, 1006, 646, 104, CX, CZ)],
       "pale", caps=False)
# basin opening between the left block and the right ledge, back wall inner face at z 150
hole = rr(390, 150, 905, 575, 70)
tub(d, "", None, hole, rr(54, 4, 1066, 656, 110), RIM - 36, 36, 330, rr(110, 60, 1010, 600, 90), mat="pale", rim_r=17)
d.box("bottom", [130, 140, 60, 990, 160, 600], "blue", r=40)
# left arm-support block: top at the rim, inner face concave in plan, big rounded top edge
blk = [(105, 140), (420, 140)] + [(385 + 35 * math.cos(math.radians(a)), 365 + 225 * math.sin(math.radians(a))) for a in range(-80, 81, 20)] + [(420, 595), (140, 595), (105, 560)]
d.slab("block-l", "top", P(blk), [330, RIM + 2], "pale", r=55)
# right ledge (narrow) with a rounded inner edge
d.slab("ledge-r", "top", P(rr(880, 140, 1008, 598, 40)), [330, RIM + 2], "pale", r=40)
# raised back wall with S-curved ends (front-plane outline extruded along z)
bw = "M 90 780 C 200 780 210 950 330 950 L 790 950 C 900 950 900 780 1000 780 Z"
d.slab("back", "front", bw, [8, 165], "pale", r=45)
# two stainless bow rails slanting over to the raised back
for nm, (fx, fy, fz), (bx, by, bz) in (("rail-l", (440, RIM, 620), (190, 935, 95)), ("rail-r", (965, RIM, 520), (730, 948, 95))):
    d.tube(nm, [[fx, fy, fz], [fx - 10, fy + 190, fz - 20], [(fx + bx) / 2, 1090, (fz + bz) / 2],
                [bx + 5, 1000, bz + 20], [bx, by, bz]], 24, "frame", bend=170)
# spout + knob + valve on the back top, hand shower in a holder at the back left, hose to the base at the lower left
d.tube("spout", [[470, 950, 70], [470, 1000, 70], [500, 1010, 150], [540, 990, 175]], 24, "chrome", bend=40)
d.lathe("knob", [600, 950, 80], [[0, 0], [28, 0], [28, 14], [20, 22], [0, 22]], "chrome")
d.lathe("valve", [430, 950, 110], [[0, 0], [16, 0], [16, 30], [0, 30]], "chrome")
d.box("holder", [150, 925, 30, 230, 965, 100], "chrome", r=10)
d.cyl("handset", [190, 955, 60], [80, 1015, 150], 46, "hose", d2=36)
d.tube("hose", [[80, 1015, 150], [25, 960, 280], [8, 700, 480], [20, 330, 620], [70, 210, 640]], 22, "hose", bend=200,
       soft=True)
d.cyl("hose-port", [95, 210, 620], [70, 210, 650], 36, "chrome")
d.tube("cable", [[450, 230, 600], [450, 120, 640], [300, 40, 660], [60, 0, 660]], 8, "cable", bend=80, soft=True)
d.box("plug", [440, 215, 590, 470, 260, 610], "cable", r=6)
# stainless frame under the tub, short lift posts, 4 castors
d.tube("frame", [[1000, 110, 620], [80, 110, 620], [80, 110, 40], [1000, 110, 40], [1000, 110, 620]], 34, "frame",
       bend=90)
d.cyl("post", [200, 110, 330], [200, 150, 330], 60, "frame", copies=[[720, 0, 0]])
d.add("castor", "caster", at=[120, 0, 600], d=90, copies=[[840, 0, 0], [0, 0, -540], [840, 0, -540]])
d.save()
