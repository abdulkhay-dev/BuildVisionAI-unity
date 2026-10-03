"""kinesio-5: progressive muscle training systems xy-zh-1 (four units) and xy-zh-2 (six units).
White square-tube frames with a mid shelf; units are white/cream rounded housings on galvanized slide rails.
Photos are taken from the front-right: the long face is the front (z = depth)."""
from k5lib import *

FR = "plastic#f2f2f0"
MATS = {"frame": FR, "galv": "metal#b8bec5", "shell": "gloss#f4f4f1", "cream": "plastic#efe7d2",
        "black": "plastic#18191b", "grip": "rubber#151618", "chrome": "chrome", "lcd": "screen",
        "red": "gloss#d42a26", "orange": "gloss#f2b01e", "yellow": "gloss#f0c419", "green": "gloss#2fb24a",
        "purple": "plastic#6f6aa8", "bolt": "metal#8d939a"}
T = 50  # frame tube


def frame(d, x0, x1, z0, z1, ytop, yshelf, ylow, legs_extra=()):
    """4 legs, top rectangle, shelf rectangle + white plate, low rectangle (all 50 mm square tube)."""
    for x in (x0, x1 - T):
        for z in (z0, z1 - T):
            d.box(f"leg{x}-{z}", [x, 0, z, x + T, ytop, z + T], "frame", r=3)
            d.box(f"legcap{x}-{z}", [x + 2, ytop - 0.5, z + 2, x + T - 2, ytop + 2, z + T - 2], "black", r=2, soft=True)
    for nm, y in (("top", ytop - T), ("shelf", yshelf - T), ("low", ylow)):
        d.box(f"{nm}-f", [x0 + T, y, z1 - T, x1 - T, y + T, z1], "frame", r=3)
        d.box(f"{nm}-b", [x0 + T, y, z0, x1 - T, y + T, z0 + T], "frame", r=3)
        d.box(f"{nm}-l", [x0, y, z0 + T, x0 + T, y + T, z1 - T], "frame", r=3)
        d.box(f"{nm}-r", [x1 - T, y, z0 + T, x1, y + T, z1 - T], "frame", r=3)
        # bolt heads along the front rail
        n = int((x1 - x0) / 220)
        d.cyl(f"{nm}-bolt", [x0 + 110, y + T / 2, z1], [x0 + 110, y + T / 2, z1 + 3], 9, "bolt", soft=True,
              repeat={"n": n, "step": [(x1 - x0 - 220) / max(n - 1, 1), 0, 0]})
    d.box("shelf-plate", [x0 + T, yshelf - 6, z0 + T, x1 - T, yshelf, z1 - T], "frame", r=2)


def galv(d, id, x, z, y0, y1, w=44, dz=24, holes=True):
    d.box(id, [x - w / 2, y0, z - dz / 2, x + w / 2, y1, z + dz / 2], "galv", r=2)
    if holes:
        d.box(id + "-holes", [x - 4, y0 + 40, z + dz / 2, x + 4, y0 + 52, z + dz / 2 + 0.6], "black", soft=True,
              repeat={"n": int((y1 - y0 - 80) / 60), "step": [0, 60, 0]})


def oval_housing(d, id, c, w, dd, h, axis, mat="shell"):
    """Rounded oval housing: centre c, w across its face, dd thick, h tall; face normal along `axis`
    (z: faces +z; x: faces +x)."""
    x, y, z = c
    r = min(w, dd) * 0.45
    if axis == "z":
        secs = [sec(y - h / 2, w * 0.82, dd, r, x, z), sec(y - h / 2 + w * 0.25, w, dd, r, x, z),
                sec(y + h / 2 - w * 0.25, w, dd, r, x, z), sec(y + h / 2, w * 0.82, dd, r, x, z)]
    else:
        secs = [sec(y - h / 2, dd, w * 0.82, r, x, z), sec(y - h / 2 + w * 0.25, dd, w, r, x, z),
                sec(y + h / 2 - w * 0.25, dd, w, r, x, z), sec(y + h / 2, dd, w * 0.82, r, x, z)]
    d.loft(id, secs, mat, dome="both", domeH=w * 0.22)


def crank(d, id, hub, arm_to, grip_axis, grip_len=130, side=1, mat="frame"):
    """Crank: hub boss on the housing face, arm to `arm_to`, black grip along grip_axis (+side)."""
    d.bar(id + "-arm", hub, arm_to, [34, 18], mat, r=8)
    gx, gy, gz = arm_to
    end = {"x": [gx + side * grip_len, gy, gz], "y": [gx, gy + side * grip_len, gz], "z": [gx, gy, gz + side * grip_len]}[grip_axis]
    d.cyl(id + "-grip", arm_to, end, 36, "grip")
    d.sphere(id + "-grip-end", end, 40, "grip")


# =========================== xy-zh-1 ===========================
W, DD, H = 1300, 900, 1750
d = D("xy-zh-1", [W, DD, H], dict(MATS))
X0, X1, Z0, Z1 = 180, 1120, 0, 760
YS = 780
frame(d, X0, X1, Z0, Z1, H, YS, 85)   # photo: the low rectangle ~100 above the floor
# --- (b) upper/lower limb trainer SXZ-1 on a floor-standing galvanized rail in the front face
RX = 560
galv(d, "rail-front", RX, Z1 + 12, 0, H - 30)
d.box("rail-front-clamp", [RX - 40, 760, Z1, RX + 40, 840, Z1 + 60], "frame", r=6)
oval_housing(d, "sxz-body", [RX, 1090, Z1 + 95], 230, 120, 470, "z")
d.lathe("sxz-disc", [RX, 990, Z1 + 155], [[0, 0], [60, 0], [62, 6], [40, 10], [0, 12]], "metal#d8dadc", axis="z")
crank(d, "sxz-crank-a", [RX, 990, Z1 + 168], [RX + 150, 1130, Z1 + 180], "x", 120, 1, "chrome")
crank(d, "sxz-crank-b", [RX, 990, Z1 + 168], [RX - 150, 850, Z1 + 180], "x", -120 and 120, -1, "chrome")
# strap pedals: a black stirrup (side plates from the grip ends) with a black strap loop hanging under the grip
for s, (px, py) in (("a", (RX + 210, 1130)), ("b", (RX - 210, 850))):
    for sx in (-62, 62):
        d.box(f"sxz-plate-{s}{sx}", [px + sx - 6, py - 70, Z1 + 160, px + sx + 6, py + 20, Z1 + 200], "grip", r=5)
    d.strap(f"sxz-strap-{s}", [[px - 55, py - 60, Z1 + 182], [px - 45, py - 130, Z1 + 182], [px + 45, py - 130, Z1 + 182],
                               [px + 55, py - 60, Z1 + 182]], [34, 4], "grip", bend=28, soft=True)
d.cyl("sxz-foot", [RX - 120, 820, Z1 + 95], [RX + 120, 820, Z1 + 95], 50, "shell")
d.cyl("sxz-foot-end", [RX - 170, 820, Z1 + 95], [RX - 110, 820, Z1 + 95], 64, "black", copies=[[280, 0, 0]])
d.cyl("sxz-neck", [RX, 1320, Z1 + 95], [RX, 1525, Z1 + 95], 70, "black")
d.cyl("sxz-dial", [RX, 1360, Z1 + 95], [RX, 1360, Z1 + 140], 80, "black", rot=rot("x", 0, [RX, 1360, Z1 + 95]))
d.lathe("sxz-dial-face", [RX, 1360, Z1 + 135], [[0, 0], [30, 0], [30, 6], [0, 8]], "metal#cfd2d6", axis="z", soft=True)
d.box("sxz-head", [RX - 70, 1520, Z1 + 50, RX + 70, 1580, Z1 + 150], "shell", r=20, rot=rot("x", 15, [RX, 1520, Z1 + 100]))
d.box("sxz-lcd", [RX - 45, 1570, Z1 + 70, RX + 45, 1582, Z1 + 130], "plastic#9aa0a6", r=4, rot=rot("x", 15, [RX, 1520, Z1 + 100]))
knob(d, "sxz-knob-a", [RX + 40, 1520, Z1 + 20], axis="x", dd=48)
knob(d, "sxz-knob-b", [RX + 40, 780, Z1 + 40], axis="x", dd=48)
# --- (a) shoulder trainer JGJ-1 on a rail in the left face, crank arm and black grip pointing outward (-x)
galv(d, "rail-left", X0 - 12, 560, YS, H - 30, w=24, dz=44)
oval_housing(d, "jgj-body", [X0 - 85, 1260, 560], 300, 120, 450, "x")
d.lathe("jgj-disc", [X0 - 145, 1240, 560], [[0, 0], [70, 0], [72, 6], [45, 10], [0, 12]], "metal#d8dadc", axis="x",
        rot=rot("y", 180, [X0 - 145, 1240, 560]))
d.bar("jgj-arm", [X0 - 160, 1240, 560], [X0 - 150, 1010, 700], [36, 22], "frame", r=8)
# black dumbbell grip pointing outward (-x) from the arm end
d.cyl("jgj-handle", [X0 - 150, 1010, 700], [X0 - 262, 1010, 700], 30, "grip")
d.sphere("jgj-handle-end", [X0 - 262, 1010, 700], 58, "grip", copies=[[78, 0, 0]])
knob(d, "jgj-knob-a", [X0 - 20, 1560, 470], axis="x", flip=True, dd=50)
knob(d, "jgj-knob-b", [X0 - 20, 970, 450], axis="x", flip=True, dd=50)
# --- (c) wrist trainer WGJ-1 on the shelf: round white base, black joystick, lever with knob
WX, WZ = 790, 470
d.lathe("wgj-base", [WX, YS, WZ], [[140, 0], [140, 40], [128, 70], [90, 92], [0, 96]], "shell")
d.cyl("wgj-tube", [WX - 260, YS + 30, WZ - 100], [WX + 200, YS + 30, WZ - 100], 50, "shell")
d.cyl("wgj-end", [WX - 300, YS + 30, WZ - 100], [WX - 250, YS + 30, WZ - 100], 66, "black")
d.cyl("wgj-post", [WX, YS + 96, WZ], [WX, YS + 130, WZ], 34, "chrome")
d.tube("wgj-lever", [[WX, YS + 120, WZ], [WX + 40, YS + 160, WZ - 20], [WX + 70, YS + 215, WZ - 40]], 24, "chrome",
       bend=30)
d.lathe("wgj-stick", [WX + 70, YS + 210, WZ - 40], [[16, 0], [24, 20], [20, 80], [26, 160], [22, 195], [0, 205]], "black")
d.box("wgj-stick-top", [WX + 40, YS + 395, WZ - 55, WX + 100, YS + 420, WZ - 25], "black", r=10)
knob(d, "wgj-knob", [WX - 120, YS + 60, WZ + 130], axis="z", dd=54)
knob(d, "wgj-knob2", [WX + 120, YS + 30, WZ + 100], axis="z", dd=48)
# --- (d) shoulder-elbow trainer JZ-1 on a rail at the back-right leg (right face), crank pointing +x
galv(d, "rail-right", X1 + 12, 140, YS, H - 30, w=24, dz=44)
oval_housing(d, "jz-body", [X1 + 75, 1170, 160], 240, 110, 390, "x")
d.lathe("jz-disc", [X1 + 130, 1180, 160], [[0, 0], [55, 0], [57, 6], [36, 10], [0, 12]], "metal#d8dadc", axis="x")
d.tube("jz-handle", [[X1 + 140, 1180, 160], [X1 + 200, 1180, 160], [X1 + 200, 1180, 250], [X1 + 140, 1100, 300]], 28,
       "frame", bend=30)
d.cyl("jz-grip", [X1 + 145, 1105, 300], [X1 + 175, 1000, 330], 38, "grip")
d.box("jz-lcd", [X1 + 40, 1400, 120, X1 + 110, 1480, 200], "black", r=10)
d.box("jz-lcd-red", [X1 + 108, 1430, 140, X1 + 111, 1460, 180], "red", soft=True)
knob(d, "jz-knob-a", [X1 + 70, 880, 220], axis="z", dd=56)
knob(d, "jz-knob-b", [X1 + 25, 1350, 220], axis="z", dd=46)
d.box("jz-clamp", [X1, 900, 110, X1 + 70, 960, 210], "frame", r=6)
# the units stick out of the 940 x 760 frame (JGJ-1 grip to the left, JZ-1 handle to the right, the SXZ-1 pedals to
# the front): move everything right by 115 and make the size cover it all (estimate size, review 2026-10-03)
shift(d, 115, 0)
d.d["size"] = [1460, 980, 1750]
d.save()

# =========================== xy-zh-2 ===========================
W, DD, H = 1900, 800, 2100
d = D("xy-zh-2", [W, DD, H], dict(MATS))
X0, X1, Z0, Z1 = 200, 1900, 0, 760
YS, YT = 900, 1750
frame(d, X0, X1, Z0, Z1, YT, YS, 140)
# --- wall-bar ladder at the left end (plane along z), white
LX = 120
for z in (40, 700):
    d.box(f"lad-rail{z}", [LX - 20, 0, z, LX + 20, H, z + 50], "frame", r=3)
for k in range(13):
    y = 280 + k * 145
    d.cyl(f"lad-rung{k}", [LX, y, 90], [LX, y, 700], 28, "frame")
d.bar("lad-tie", [LX + 20, YT - 25, 400], [X0, YT - 25, 400], [50, 50], "frame", r=3)
d.bar("lad-tie2", [LX + 20, YS - 25, 400], [X0, YS - 25, 400], [50, 50], "frame", r=3)
# orange peg bars on the ladder's outer side, pegs pointing -x; black handle and knob
for k, (z, y0, y1) in enumerate(((60, 700, 1600), (560, 760, 1550))):
    d.box(f"peg-bar{k}", [LX - 60, y0, z - 20, LX - 22, y1, z + 20], "orange", r=4)
    d.cyl(f"peg{k}", [LX - 60, y0 + 60, z], [LX - 120, y0 + 60, z], 18, "orange",
          repeat={"n": 8, "step": [0, (y1 - y0 - 120) / 7, 0]})
d.cyl("peg-handle", [LX - 60, 1300, 60], [LX - 190, 1300, 60], 34, "grip")
d.sphere("peg-handle-end", [LX - 190, 1300, 60], 44, "grip")
knob(d, "peg-knob", [LX - 22, 760, 90], axis="z", dd=46)
# --- shoulder rehab trainer XY-JGJ-2 (left): oval housing on a galvanized rail, long black crank up-left
#     (photo heights at 1.87 mm/px: housing 1180..1530, LCD ~1570..1650, the crank grip ~1610)
RX = 560
JY = 1360
galv(d, "rail-a", RX, Z1 + 12, YS - 60, YT - 20)
oval_housing(d, "jgj-body", [RX - 90, JY, Z1 + 90], 260, 120, 380, "z")
d.lathe("jgj-disc", [RX - 90, JY - 20, Z1 + 150], [[0, 0], [70, 0], [72, 6], [45, 10], [0, 12]], "metal#d8dadc", axis="z")
d.bar("jgj-arm", [RX - 90, JY - 20, Z1 + 165], [215, 1615, Z1 + 175], [40, 26], "black", r=10)
d.bar("jgj-arm2", [RX - 90, JY - 20, Z1 + 165], [RX - 20, 1190, Z1 + 175], [40, 26], "black", r=10)
d.cyl("jgj-grip", [215, 1615, Z1 + 175], [215, 1615, Z1 + 310], 40, "grip")
d.sphere("jgj-grip-end", [215, 1615, Z1 + 310], 52, "grip")
d.cyl("jgj-grip2", [RX - 20, 1190, Z1 + 175], [RX - 20, 1190, Z1 + 260], 40, "grip")
d.box("jgj-lcd", [RX - 120, 1575, Z1 + 60, RX - 50, 1650, Z1 + 120], "black", r=10)
d.box("jgj-lcd-red", [RX - 110, 1605, Z1 + 120, RX - 60, 1630, Z1 + 122], "red", soft=True)
knob(d, "jgj-knob-a", [RX, 1160, Z1 + 30], axis="z", dd=56)
knob(d, "jgj-knob-b", [RX + 40, 1600, Z1 + 10], axis="x", dd=46)
# --- pulley gantry: post on the front face rising ~130 above the top frame, a short white top arm, the yellow bar
#     under it, an X brace to the post, two pulleys hanging from the yellow bar's ends at the top-rail level, thin
#     grey ropes down to dark grey triangle handles below the shelf
GX = 1370
d.box("gantry-post", [GX - 25, YS, Z1 - 50, GX + 25, 1880, Z1], "frame", r=3)
d.box("gantry-arm", [1060, 1840, Z1 - 45, GX + 25, 1875, Z1 - 5], "frame", r=3)
knob(d, "gantry-knob", [1080, 1875, Z1 - 25], axis="y", dd=26, mat="gloss#2b56b8")
d.bar("gantry-strut", [1300, 1790, Z1 - 25], [GX - 20, 1590, Z1 - 25], [24, 24], "metal#e9e3d0", r=4)
d.bar("gantry-strut2", [1250, 1650, Z1 - 25], [GX - 20, 1840, Z1 - 25], [24, 24], "metal#e9e3d0", r=4)
for x in (1100, 1300):
    d.cyl(f"yb-link{x}", [x, 1840, Z1 - 25], [x, 1805, Z1 - 25], 8, "chrome")
d.cyl("yellow-bar", [810, 1790, Z1 - 25], [1340, 1790, Z1 - 25], 36, "yellow")
for x, sg in ((900, -1), (1240, 1)):
    xe = 830 if sg < 0 else 1320
    d.strap(f"g-hang{x}", [[xe, 1780, Z1 + 5], [x, 1680, Z1 + 30]], [20, 4], "plastic#4a5260")
    pulley(d, f"g-pul{x}", [x, 1660, Z1 + 30], 70, 24, "z", mat="frame", hub="black")
    rx = x + sg * 33
    rope(d, f"g-rope{x}", [[rx, 1660, Z1 + 30], [rx, 880, Z1 + 30]], mat="metal#c0c4c8", dd=5)
    d.tube(f"g-handle{x}", [[rx, 880, Z1 + 30], [rx - 30, 740, Z1 + 30], [rx + 30, 740, Z1 + 30], [rx, 880, Z1 + 30]],
           22, "plastic#4a5260", bend=20)
# --- upper limb trainer (cream) on the shelf: oval body, round LCD head, strap pedals both sides, foot bar
#     (photo: the whole unit ~450 tall, head top ~1330, pedals ~1100)
PX, PZ = 960, 470
d.box("pt-foot", [PX - 220, YS, PZ - 40, PX + 220, YS + 50, PZ + 40], "cream", r=20)
d.cyl("pt-foot-end", [PX - 250, YS + 25, PZ], [PX - 210, YS + 25, PZ], 60, "black", copies=[[460, 0, 0]])
d.cyl("pt-roller", [PX - 30, YS + 40, PZ + 60], [PX + 30, YS + 40, PZ + 60], 70, "black")
oval_housing(d, "pt-body", [PX, 1085, PZ], 220, 140, 330, "x", mat="cream")
d.cyl("pt-neck", [PX, 1240, PZ], [PX, 1265, PZ], 50, "cream")
d.cyl("pt-head", [PX, 1290, PZ - 30], [PX, 1290, PZ + 40], 115, "cream")
d.box("pt-lcd", [PX - 34, 1290, PZ + 40, PX + 34, 1322, PZ + 42], "lcd", r=4)
d.box("pt-lcd-red", [PX - 30, 1262, PZ + 40, PX + 30, 1274, PZ + 42], "red", soft=True)
for s, sg, py in (("l", -1, 1080), ("r", 1, 1110)):
    d.bar(f"pt-crank-{s}", [PX + sg * 70, 1095, PZ], [PX + sg * 90, py, PZ + 120], [26, 14], "chrome", r=6)
    d.cyl(f"pt-grip-{s}", [PX + sg * 90, py, PZ + 120], [PX + sg * 240, py, PZ + 120], 38, "grip")
    d.strap(f"pt-strap-{s}", [[PX + sg * 105, py - 10, PZ + 120], [PX + sg * 120, py - 75, PZ + 120],
                              [PX + sg * 215, py - 75, PZ + 120], [PX + sg * 230, py - 10, PZ + 120]], [28, 3], "grip",
            bend=30, soft=True)
# --- shoulder lifting gauge column (right on the shelf): cream base, dark motor, column slanting up toward -x with a
#     purple scale, head with LCD + red button (top ~1480), chrome bar with black grips through a slider
GCX, GCZ = 1640, 420
d.box("gc-base", [GCX - 140, YS, GCZ - 110, GCX + 120, YS + 60, GCZ + 160], "cream", r=16)
d.box("gc-motor", [GCX - 60, YS + 40, GCZ - 30, GCX + 80, YS + 140, GCZ + 100], "plastic#3f4a5c", r=24)
gr = rot("z", 12, [GCX + 20, YS + 130, GCZ + 30])
d.box("gc-column", [GCX - 40, YS + 130, GCZ - 10, GCX + 70, 1370, GCZ + 70], "cream", r=10, rot=gr)
d.box("gc-scale", [GCX - 5, YS + 200, GCZ + 70, GCX + 35, 1340, GCZ + 74], "purple", r=3, rot=gr)
for k in range(9):
    d.box(f"gc-tick{k}", [GCX, YS + 230 + k * 24 * 5, GCZ + 74, GCX + 20, YS + 234 + k * 24 * 5, GCZ + 75.5],
          "white" if False else "plastic#f2f2f6", soft=True, rot=gr)
d.box("gc-head", [GCX - 60, 1350, GCZ - 30, GCX + 75, 1480, GCZ + 90], "cream", r=12, rot=gr)
d.box("gc-lcd", [GCX - 25, 1440, GCZ + 90, GCX + 45, 1468, GCZ + 92], "lcd", r=3, rot=gr)
d.lathe("gc-button", [GCX + 10, 1400, GCZ + 90], [[0, 0], [16, 0], [16, 6], [0, 8]], "red", axis="z", rot=gr)
d.cyl("gc-bar", [GCX - 330, 1060, GCZ + 40], [GCX + 330, 1060, GCZ + 40], 30, "chrome")
d.cyl("gc-grip", [GCX - 330, 1060, GCZ + 40], [GCX - 200, 1060, GCZ + 40], 40, "grip", copies=[[530, 0, 0]])
d.box("gc-slider", [GCX - 50, 1030, GCZ, GCX + 50, 1100, GCZ + 90], "cream", r=10)
knob(d, "gc-knob", [GCX - 120, YS + 120, GCZ + 160], axis="z", dd=50)
d.box("gc-post", [1440, YS, Z1 - 50, 1480, YT - 50, Z1], "galv", r=2)
knob(d, "gc-knob2", [1460, 1170, Z1], axis="z", dd=46)
# --- finger ladder strip on the right face near the back: green spiky and white segments
FX, FZ = X1 + 10, 130
galv(d, "rail-f", X1 - 15, FZ + 80, YS - 80, YT - 40, w=24, dz=44)
d.box("fl-clamp", [X1 - 30, 1050, FZ - 10, X1 + 10, 1120, FZ + 90], "frame", r=6)
segs = [(720, 875, "green"), (875, 1030, "frame"), (1030, 1185, "green"), (1185, 1340, "frame"), (1340, 1490, "green")]
for i, (y0, y1, c) in enumerate(segs):
    d.box(f"fl-seg{i}", [FX - 10, y0, FZ - 35, FX + 20, y1, FZ + 35], c, r=4)
    d.box(f"fl-teeth{i}", [FX + 20, y0 + 8, FZ - 30, FX + 42, y0 + 22, FZ + 30], c, r=6,
          repeat={"n": int((y1 - y0 - 10) / 24), "step": [0, 24, 0]})
# the units stick out of the frame (peg handle to the left, gauge grips to the right, the JGJ-2 grip to the front):
# move everything right by 95 and let the size cover it all (estimate size, review 2026-10-03)
shift(d, 95, 0)
d.d["size"] = [2070, 1100, 2100]
d.save()
