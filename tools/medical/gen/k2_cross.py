"""xy-szld-ia / recumbent-cross-trainer-interactive — recumbent cross trainers (kinesio-2).
Frame: the seat at the back, the user faces +z; levers + pedals pivot low at the front of the base shell,
two big white square-tube arcs rise from the floor in front and curve back to the console."""
import math
from k2lib import *


def P(path, x):
    return [[x, y, z] for z, y in path]


def lever(d, nm, cx_side, piv, ang, top_y, white, black, cx):
    """Swing lever: white square tube from the low pivot up-back, black vertical grip; pedal plate with heel cup on it.
    ang = swing (deg) about the pivot, + forward."""
    pz, py = piv
    R = rot("x", -ang, [cx_side, py, pz])   # -deg turns y towards -z: positive ang swings the top forward
    up = [cx_side, top_y - 380, pz - 330]
    d.bar(f"lever-{nm}", [cx_side, py, pz], up, [52, 46], white, r=8, rot=R)
    d.box(f"lever-cap-{nm}", [cx_side - 30, up[1] - 20, up[2] - 30, cx_side + 30, up[1] + 30, up[2] + 30], black, r=8, rot=R)
    d.cyl(f"grip-{nm}", [cx_side, up[1] + 25, up[2]], [cx_side, top_y, up[2] - 25], 40, "foam", rot=R)
    d.cyl(f"grip-end-{nm}", [cx_side, top_y, up[2] - 25], [cx_side, top_y + 8, up[2] - 26], 34, black, rot=R)
    # pedal: black plate leaning back ~35 deg from vertical with a heel cup and toe strap, on a short link
    fz, fy = pz - 90, py + 170
    d.bar(f"pedal-link-{nm}", [cx_side, py + 40, pz - 20], [cx_side, fy, fz], [30, 30], "steel", r=4, rot=R)
    sx = 1 if cx_side > cx else -1
    xo = cx_side - sx * 110
    o = f"M {fz - 40} {fy - 170} L {fz + 70} {fy - 150} L {fz + 120} {fy + 160} L {fz + 40} {fy + 200} L {fz - 20} {fy + 120} Z"
    d.slab(f"pedal-{nm}", "side", o, [xo - 70, xo + 70], black, r=10, rot=R)
    d.box(f"heel-{nm}", [xo - 72, fy - 175, fz - 60, xo + 72, fy - 110, fz + 30], black, r=14, rot=R)
    d.strap(f"toe-strap-{nm}", [[xo - 72, fy + 80, fz + 75], [xo, fy + 70, fz + 20], [xo + 72, fy + 80, fz + 75]], [45, 4], "fabric#1a1b1d",
            bend=30, soft=True, rot=R)


def lever2(d, nm, x, piv, ang, L, grip_top, white, black, chrome="chrome"):
    """Arm lever pivoting low at the front of the arcs: a straight white square tube rising back at `ang` deg from
    the horizontal, a black clamp collar, a chrome tube bending up and a black grip (tilted a little back)."""
    pz, py = piv
    cz, cy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    E = [x, py + L * cy, pz - L * cz]
    d.bar(f"lever-{nm}", [x, py, pz], E, [56, 44], white, r=10)
    d.lathe(f"lever-hub-{nm}", [x - 40, py, pz], [[0, 0], [38, 0], [38, 80], [0, 80]], "steel", axis="x")
    C = [x, E[1] + 26 * cy, E[2] - 26 * cz]
    d.bar(f"lever-collar-{nm}", E, C, [64, 52], black, r=6)
    G0 = [x, C[1] + 90, C[2] - 70]
    d.tube(f"lever-bend-{nm}", [C, [x, C[1] + 40 * cy, C[2] - 40 * cz], G0], 26, chrome, bend=40)
    G1 = [x, grip_top, G0[2] - 0.2 * (grip_top - G0[1])]
    d.cyl(f"grip-{nm}", G0, G1, 38, "foam")
    d.cyl(f"grip-end-{nm}", G1, [x, G1[1] + 8, G1[2] - 2], 32, black)
    # the clamp knob under the lever (photo 2) and the pad-bracket block on it (photo 1)
    K = [x, py + 0.78 * L * cy, pz - 0.78 * L * cz]
    d.cyl(f"knob-stem-{nm}", K, [x, K[1] - 60, K[2]], 12, "chrome")
    d.lathe(f"knob-{nm}", [x, K[1] - 95, K[2]], [[0, 0], [16, 0], [22, 14], [22, 30], [12, 36], [0, 36]], black)




def pedal2(d, nm, x, sx, top, foot, hub, black, chrome="chrome"):
    """Pedal: black swing arm hanging from an upper pivot `top` (z, y) to the foot plate at `foot` (z, y), a black
    foot plate leaning back with heel cup and frame, a black link rod with chrome ends down to the crank hub."""
    tz, ty = top; fz, fy = foot; hz, hy = hub
    d.bar(f"pedal-arm-{nm}", [x, ty, tz], [x, fy + 60, fz + 10], [34, 46], black, r=6)
    xo0, xo1 = (x, x + sx * 150) if sx > 0 else (x + sx * 150, x)
    o = f"M {fz - 70} {fy - 30} L {fz + 60} {fy - 30} L {fz + 150} {fy + 260} L {fz + 40} {fy + 290} Z"
    d.slab(f"pedal-{nm}", "side", o, [xo0, xo1], black, r=10)
    d.box(f"heel-{nm}", [xo0 - 4, fy - 40, fz - 90, xo1 + 4, fy + 40, fz - 30], black, r=14)
    d.box(f"pedal-frame-{nm}", [x - 10, fy + 20, fz - 20, x + 10, fy + 240, fz + 120], "plastic#2a2c30", r=6,
          rot=rot("x", -18, [x, fy + 20, fz - 20]))
    d.cyl(f"pedal-link-{nm}", [x, fy - 20, fz + 20], [x, hy + 20, hz - 20], 20, black)
    d.cyl(f"pedal-rod-{nm}", [x, hy + 20, hz - 20], [x, hy, hz], 12, chrome)
    d.sphere(f"pedal-eye-{nm}", [x, hy, hz], 30, chrome)


def build(id_, size, M, shell_outline, interactive):
    d = D(id_, size, M)
    W, DD, H = size
    CX = W / 2
    SW = 210                       # half width of the base shell
    # --- base shell (rounded slab along x) and its details
    d.slab("shell", "side", shell_outline, [CX - SW, CX + SW], "shell", r=75)
    return d, CX, SW


# ======================= XY-SZLD-IA (grey shell, tractor seat, lime-green seat handles)
M = {"shell": "plastic#d6d4cf", "white": "plastic#f2f3f5", "black": "plastic#1d1e21", "seat": "leather#1c1d20",
     "green": "gloss#8cc63f", "steel": "metal#c8ccd2", "foam": "rubber#1a1b1d", "chrome": "chrome", "slot": "plastic#2a2b2e"}
shell = ("M 30 40 L 30 330 Q 30 470 170 470 L 760 470 Q 840 470 900 400 L 1060 260 Q 1110 215 1180 200 "
         "Q 1240 190 1250 120 L 1250 60 Q 1250 30 1210 30 L 60 30 Q 30 30 30 40 Z")
d, CX, SW = build("xy-szld-ia", [870, 1630, 1160], M, shell, False)
d.cyl("rear-axle", [CX - SW - 30, 45, 70], [CX + SW + 30, 45, 70], 20, "steel")
for s in (-1, 1):
    x = CX + s * (SW + 30)
    d.add(f"rear-wheel{s}", "wheel", "rubber#e2d2b0", at=[x, 45, 70], d=90, d2=28, axis="x")
    d.cyl(f"rear-hub{s}", [x - 16, 45, 70], [x + 16, 45, 70], 40, "steel")
    xs = CX + s * (SW + 0.8)
    face = "right" if s > 0 else "left"
    d.decal(f"cross-logo{s}", [xs, 300, 200], [74, 74], face, "plastic#cfcdc7", soft=True)
    d.decal(f"cross-v{s}", [xs + s * 0.4, 296, 200], [16, 54], face, "plastic#bab8b1", soft=True)
    d.decal(f"cross-h{s}", [xs + s * 0.4, 312, 200], [44, 14], face, "plastic#bab8b1", soft=True)
    d.decal(f"slot{s}", [xs, 330, 470], [190, 50], face, "slot", soft=True, rot=rot("x", 12, [xs, 330, 470]))
    star_knob(d, f"slot-knob{s}", [CX + s * SW, 250, 520], "x", s, dd=44, l=40)
# seat slide rails on the shell top, seat post, tractor seat with backrest and hinge brackets
d.box("rail", [CX - 90, 470, 250, CX - 60, 495, 900], "black", r=4, copies=[[150, 0, 0]])
d.box("seat-post", [CX - 90, 480, 360, CX + 90, 555, 600], "black", r=10)
d.box("seat-pan", [CX - 215, 545, 270, CX + 215, 575, 690], "black", r=20)
d.box("cushion", [CX - 220, 570, 265, CX + 220, 650, 700], "seat", r=35, puff=10)
d.box("cushion-seam", [CX - 160, 649, 330, CX + 160, 653, 640], "plastic#2a2b2f", r=20, soft=True)
BR = rot("x", -14, [CX, 600, 250])
d.box("backrest", [CX - 215, 640, 175, CX + 215, 1090, 255], "seat", r=40, puff=10, rot=BR)
d.box("back-shell", [CX - 205, 650, 160, CX + 205, 1080, 178], "black", r=30, rot=BR)
d.box("back-seam", [CX - 140, 760, 254, CX + 140, 764, 258], "plastic#2a2b2f", soft=True, rot=BR, copies=[[0, 150, 0]])
for s in (-1, 1):
    xb = CX + s * 225
    d.box(f"hinge{s}", [min(xb, xb + s * 16), 560, 200, max(xb, xb + s * 16), 760, 300], "black", r=8)
    d.lathe(f"hinge-knob{s}", [xb + s * 16, 640, 260], [[0, 0], [10, 0], [10, 14], [20, 16], [20, 30], [0, 32]], "chrome", axis="x",
            rot=rot("y", 0 if s > 0 else 180, [xb + s * 16, 640, 260]))
    # lime-green U handle beside the seat
    d.sweep(f"seat-handle{s}", [[CX + s * 150, 540, 650], [CX + s * 275, 540, 650], [CX + s * 275, 540, 320], [CX + s * 150, 540, 320]],
            [30, 30], "green", shape="round", bend=55)
# arcs: two white square tubes from the floor in front, rising and curving back to the console
arc = [[1190, 40], [1460, 40], [1585, 180], [1600, 520], [1470, 860], [1290, 1040], [1180, 1060]]
for s in (-1, 1):
    pts = []
    for i, (z, y) in enumerate(arc):
        t = i / (len(arc) - 1)
        pts.append([CX + s * (240 - 150 * t * t), y, z])
    d.sweep(f"arc{s}", pts, [70, 70], "white", r=14, bend=150)
d.box("foot-pad", [CX - 270, 0, 1420, CX - 210, 10, 1500], "black", r=4, copies=[[480, 0, 0]])
# console: white back shell, black oval face tilted to the user
CR = rot("x", 50, [CX, 1080, 1190])
def oval(cx, cy, a, b): return f"M {cx - a} {cy} A {a} {b} 0 1 0 {cx + a} {cy} A {a} {b} 0 1 0 {cx - a} {cy} Z"
# a big oval console: white rim shell round a black face, tilted to the user
d.slab("console-back", "front", oval(CX, 1080, 205, 150), [1185, 1222], "white", r=12, rot=CR)
d.slab("console-face", "front", oval(CX, 1080, 178, 126), [1172, 1186], "black", r=5, rot=CR)
d.box("console-neck", [CX - 50, 1010, 1150, CX + 50, 1080, 1230], "white", r=12)
# levers + pedals (pivot low at the shell nose), gas springs
for s, nm, ang in ((-1, "l", 10), (1, "r", -10)):
    xs = CX + s * 260
    lever(d, nm, xs, (1200, 230), ang, 1150, "white", "black", CX)
    d.cyl(f"pivot-{nm}", [CX + s * SW, 230, 1200], [xs + s * 30, 230, 1200], 50, "steel")
    d.cyl(f"gas-{nm}", [xs - s * 40, 160, 1120], [xs - s * 40, 360, 1090], 26, "black")
    d.cyl(f"gas-rod-{nm}", [xs - s * 40, 360, 1090], [xs - s * 40, 520, 1060], 12, "chrome")
d.save()

# ======================= Recumbent cross trainer + scenario interactive mode (white shell, dark plinth, armrest seat)
M = {"shell": "gloss#f2f3f5", "white": "plastic#eef0f2", "black": "plastic#1d1e21", "seat": "leather#1c1d20",
     "plinth": "plastic#2e3238", "steel": "metal#c8ccd2", "foam": "rubber#1a1b1d", "chrome": "chrome", "orange": "gloss#f08a24"}
shell = ("M 150 90 L 150 380 Q 150 560 330 560 L 840 560 Q 930 560 990 470 L 1120 300 Q 1170 240 1250 225 "
         "Q 1320 215 1330 150 L 1330 120 Q 1330 90 1300 90 Z")
d, CX, SW = build("recumbent-cross-trainer-interactive", [800, 1700, 1300], M, shell, True)
d.slab("plinth", "side", "M 140 20 L 1340 20 L 1340 105 L 140 105 Z", [CX - SW - 6, CX + SW + 6], "plinth", r=30)
d.slab("front-foot", "side", "M 1150 20 L 1450 20 Q 1500 20 1500 70 L 1500 110 Q 1500 140 1450 140 L 1150 140 Z",
       [CX - 170, CX + 170], "shell", r=30)
d.box("front-foot-plinth", [CX - 176, 0, 1150, CX + 176, 40, 1495], "plinth", r=12)
# left side (photo 1): a dark grip slot rising to the back high on the shell, the blue LED dots on a dark line under it,
# the blue logo behind it; right side (photo 2): the LED line high under the seat
xl = CX - SW - 0.8
d.box("grip-recess", [CX - SW - 6, 385, 440, CX - SW + 6, 420, 690], "plinth", r=16, rot=rot("x", -8, [CX - SW, 400, 560]))
d.decal("led-l", [xl, 320, 580], [300, 9], "left", "plinth", soft=True)
d.decal("led-dot-l", [xl - 0.5, 320, 440], [6, 6], "left", "gloss#3a8fe8", soft=True, repeat=rep(15, [0, 0, 20]))
d.decal("logo-mark", [xl, 345, 330], [30, 30], "left", "gloss#2f6fbf", soft=True)
d.decal("logo-name", [xl, 342, 265], [80, 18], "left", "gloss#2f6fbf", soft=True)
xr = CX + SW + 0.8
d.decal("led-r", [xr, 470, 500], [380, 9], "right", "plinth", soft=True, rot=rot("x", 8, [xr, 470, 500]))
for i in range(18):
    z = 330 + 20 * i
    d.decal(f"led-dot-r{i}", [xr + 0.5, 470 - (z - 500) * math.tan(math.radians(8)), z], [6, 6], "right", "gloss#d8dde4", soft=True)
for x in (CX - 150, CX + 150):
    d.cyl(f"level-foot{x}", [x, 0, 1440], [x, 25, 1440], 40, "black")
d.box("t-foot", [CX - 40, 5, 1150, CX + 40, 30, 1430], "black", r=6)
# rear wheel and the swing-out stabiliser leg
d.add("rear-wheel", "wheel", "rubber#3a3c40", at=[CX, 55, 175], d=110, d2=36, axis="x")
d.cyl("rear-hub", [CX - 22, 55, 175], [CX + 22, 55, 175], 46, "steel")
d.box("stab-bracket", [CX - 30, 380, 110, CX + 30, 440, 170], "black", r=8)
d.bar("stab-arm", [CX, 420, 140], [CX, 330, 40], [40, 50], "black", r=8)
d.cyl("stab-leg", [CX, 340, 40], [CX, 30, 30], 30, "chrome")
d.cyl("stab-foot", [CX, 0, 30], [CX, 30, 30], 60, "black")
# seat: black slide base, automotive seat with side bolsters, two armrests with orange reflectors
d.box("rail", [CX - 90, 560, 300, CX - 60, 585, 920], "black", r=4, copies=[[150, 0, 0]])
d.box("seat-base", [CX - 170, 575, 300, CX + 170, 650, 760], "black", r=12)
d.box("cushion", [CX - 250, 640, 280, CX + 250, 730, 780], "seat", r=40, puff=10)
for s in (-1, 1):
    d.box(f"bolster{s}", [CX + s * 250 - (70 if s > 0 else 0), 650, 290, CX + s * 250 + (0 if s > 0 else 70), 760, 760], "seat", r=35)
BR = rot("x", -12, [CX, 700, 300])
d.box("backrest", [CX - 250, 720, 220, CX + 250, 1280, 310], "seat", r=45, puff=10, rot=BR)
d.box("back-shell", [CX - 240, 730, 205, CX + 240, 1270, 225], "black", r=35, rot=BR)
d.box("back-seam", [CX - 4, 780, 309, CX + 4, 1220, 313], "plastic#2b2c30", soft=True, rot=BR)
for s in (-1, 1):
    xa = CX + s * 290
    d.box(f"armrest{s}", [xa - 40, 930, 280, xa + 40, 990, 640], "black", r=22)
    d.box(f"armrest-post{s}", [xa - 25, 760, 300, xa + 25, 940, 350], "black", r=8)
    d.decal(f"reflector{s}", [xa + s * 40.8, 960, 590], [70, 18], "right" if s > 0 else "left", "orange", soft=True)
    d.decal(f"reflector-top{s}", [xa, 990.8, 560], [40, 50], "top", "orange", soft=True)
# arcs: the right one rises from the shell nose, the left one has a long foot on the floor in front
arcR = [[1300, 150], [1440, 260], [1500, 520], [1450, 860], [1330, 1110], [1260, 1170]]
arcL = [[1250, 40], [1450, 40], [1620, 40], [1690, 220], [1650, 600], [1500, 960], [1330, 1150], [1260, 1180]]
for s, arc in ((1, arcR), (-1, arcL)):
    pts = []
    for i, (z, y) in enumerate(arc):
        t = i / (len(arc) - 1)
        pts.append([CX + s * (230 - 150 * t * t), y, z])
    d.sweep(f"arc{s}", pts, [72, 72], "white", r=14, bend=170)
d.bar("arc-foot-link", [CX - 230, 60, 1470], [CX - 120, 60, 1470], [60, 50], "white", r=12)
d.cyl("nose-hub", [CX - 120, 150, 1300], [CX + 240, 150, 1300], 60, "steel")
# console: white back shell, black face, black bracket under it with a wire hook
CR = rot("x", 52, [CX, 1200, 1290])
d.box("console-back", [CX - 190, 1100, 1285, CX + 190, 1300, 1320], "white", r=55, rot=CR)
d.box("console-face", [CX - 175, 1112, 1268, CX + 175, 1288, 1288], "black", r=48, rot=CR)
d.box("console-bracket", [CX - 70, 1080, 1210, CX + 70, 1180, 1300], "black", r=14)
d.tube("wire-hook", [[CX + 60, 1110, 1220], [CX + 120, 900, 1180], [CX + 130, 870, 1100], [CX + 90, 900, 1080]], 6, "black",
       bend=20, soft=True)
# arm levers pivot low at the front of the arcs (photo 2: the left lever forward and steep, the right one pulled back
# almost level to the hip); pedals hang on black swing arms with link rods to the nose crank
PIV = (1580, 420)
d.cyl("lever-pin", [CX - 330, PIV[1], PIV[0]], [CX - 240, PIV[1], PIV[0]], 34, "steel", copies=[[570, 0, 0]])
lever2(d, "l", CX - 285, PIV, 56, 760, 1255, "white", "black")
lever2(d, "r", CX + 285, PIV, 27, 790, 1090, "white", "black")
d.cyl("pedal-pin", [CX - 160, 820, 1470], [CX - 80, 820, 1470], 40, "steel", copies=[[240, 0, 0]])
pedal2(d, "l", CX - 120, -1, (1470, 820), (1470, 300), (1300, 150), "black")
pedal2(d, "r", CX + 120, 1, (1470, 820), (1360, 330), (1300, 150), "black")
d.save()
