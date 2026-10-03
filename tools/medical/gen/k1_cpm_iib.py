"""xy-cpm-iib: lower-limb CPM bed unit. Long axis x, console + foot plate at x=0 end, hip end at x max;
front (z max) = the face with the slot and the DB9 plug; hand controller lies in front."""
from k1lib import *

d = D("xy-cpm-iib", [1060, 480, 560], {
    "white": "gloss#f4f5f6", "panel": "plastic#c6cad0", "lcd": "gloss#a9b48c", "key": "gloss#1f3f8f",
    "chrome": "chrome", "black": "plastic#18191b", "sling": "fabric#1c1d20", "dkgrey": "plastic#4a4f57",
    "steel": "metal#c4c8cc", "pad": "leather#1c1d20", "cream": "plastic#efe6c8", "blue": "gloss#2a62b8"})
Z0, Z1 = 60, 320
# --- long white base, slightly lower toward the hip end; black carriage slot and DB9 on the front face
d.loft("base", [sec(30, 260, 165, 34, 82, 190), sec(1035, 260, 140, 34, 70, 190)], "white", axis="x")
d.box("base-end", [1015, 0, Z0, 1040, 140, Z1], "white", r=20)
d.box("slot", [380, 72, Z1 - 1, 960, 84, Z1 + 1.5], "black", r=5)
d.box("db9", [400, 112, Z1 - 2, 452, 146, Z1 + 24], "plastic#9a9da2", r=5)
d.cyl("screw", [370, 40, Z1], [370, 40, Z1 + 2], 9, "chrome", soft=True, repeat=rep(4, [200, 0, 0]))
# --- console block at the foot end: sloping top with the tilted membrane panel; power inlet on the end
con = "M 60 0 L 322 0 L 322 176 Q 322 196 302 202 L 82 268 Q 60 272 60 250 Z"
d.slab("console", "side", con, [30, 330], "white", r=24)
tilt = rot("x", 16.7, [180, 238, 190])
d.box("panel", [62, 236, 112, 298, 239.5, 268], "panel", r=6, rot=tilt)
d.box("lcd", [150, 239, 130, 236, 241, 196], "lcd", r=3, soft=True, rot=tilt)
# photo layout: green rocker back-left, LCD back-right, the keys in front of them, a larger key front-right
d.box("key", [96, 239, 204, 116, 242, 222], "key", r=3, soft=True, rot=tilt, repeat=rep(3, [32, 0, 0]))
d.box("key-b", [112, 239, 234, 132, 242, 252], "key", r=3, soft=True, rot=tilt, repeat=rep(2, [32, 0, 0]))
d.box("key-c", [236, 239, 214, 270, 242, 250], "key", r=3, soft=True, rot=tilt)
d.box("rocker-frame", [72, 239, 124, 118, 244, 166], "black", r=4, rot=tilt)
d.box("rocker", [78, 241, 130, 112, 250, 160], "gloss#1f9a4a", r=4, rot=tilt)
d.box("inlet", [26, 96, 110, 32, 140, 160], "black", r=4)
# --- foot carriage: dark-grey bracket on flat steel links, upright black padded foot plate with strap
d.bar("foot-link", [372, 150, 100], [386, 262, 100], [32, 8], "steel", r=2, copies=[[0, 0, 180]])
d.box("foot-bracket", [300, 250, 85, 420, 330, 295], "dkgrey", r=8)
d.lathe("foot-knob", [360, 290, 295], [[0, 0], [7, 0], [7, 8], [17, 10], [17, 26], [0, 28]], "black", axis="z", sides=8)
d.box("foot-plate", [318, 300, 92, 372, 560, 288], "pad", r=34, puff=6, rot=rot("z", 8, [345, 300, 190]))
d.strap("foot-strap", [[378, 380, 88], [392, 400, 190], [378, 380, 292]], [50, 4], "sling", bend=60, soft=True,
        rot=rot("z", 8, [345, 300, 190]))
# --- leg frame: chrome rails both sides, knee/ankle hubs with blue caps, steel links, black cradles with straps
for nm, z in (("b", 92), ("f", 288)):
    d.tube(f"rail-{nm}", [[400, 330, z], [860, 345, z], [1030, 332, z], [1040, 150, z]], 20, "chrome", bend=45)
    zo = z - 22 if z < 190 else z + 22
    for hx, hy in ((430, 331), (860, 345)):
        d.cyl(f"hub-{nm}-{hx}", [hx, hy, z], [hx, hy, zo], 60, "chrome")
        # white cap with a small blue logo (photo), not a blue disc
        d.lathe(f"hub-cap-{nm}-{hx}", [hx, hy, zo], [[0, 0], [24, 0], [24, 1.5], [0, 1.5]], "plastic#eceef0", axis="z",
                rot=rot("y", 180, [hx, hy, zo]) if z < 190 else None)
        zl = zo + (1.2 if z > 190 else -1.2)
        d.lathe(f"hub-logo-{nm}-{hx}", [hx, hy, zl], [[0, 0], [10, 0], [10, 1], [0, 1]], "blue", axis="z", soft=True,
                rot=rot("y", 180, [hx, hy, zl]) if z < 190 else None)
    d.bar(f"hub-link-{nm}", [470, 150, zo], [432, 322, zo], [30, 8], "steel", r=2)
    d.lathe(f"rail-knob-{nm}", [760, 318, z], [[0, 0], [8, 0], [8, 6], [14, 8], [14, 22], [0, 24]], "black")
d.box("calf-sling", [450, 304, 100, 840, 350, 280], "sling", r=12, puff=4)
d.box("thigh-sling", [880, 304, 100, 1030, 348, 280], "sling", r=12, puff=4)
for x in (540, 720, 950):
    d.strap(f"sling-strap-{x}", [[x, 330, 82], [x, 362, 190], [x, 330, 298]], [45, 3], "sling", bend=50, soft=True)
# --- low chrome rod frame along both sides, black clamps; foam roller with cream wheels at the foot end
for nm, z, zr in (("f", 345, 300), ("b", 35, 80)):
    d.tube(f"low-rod-{nm}", [[25, 38, z], [1045, 38, z], [1045, 140, zr]], 18, "chrome", bend=40)
    d.box(f"low-clamp-{nm}", [60, 26, z - 14, 92, 54, z + 14], "black", r=5, copies=[[920, 0, 0]])
d.cyl("roller", [25, 35, 30], [25, 35, 350], 40, "rubber#202124")
d.add("roller-wheel", "wheel", "cream", at=[25, 35, 16], d=70, d2=26, axis="z", copies=[[0, 0, 348]])
# --- hand controller in front, coiled cable to the DB9
controller(d, "controller", 520, 392, [426, 128, Z1 + 24])
d.save()
