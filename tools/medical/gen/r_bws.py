"""Mobile electric BWS gait frames of batch robot-1: xy-k-e2, xy-k-e3 (same frame), xy-k-g2, xy-k-g3, xy-k-g6, xy-k-g7.
Frame: column at the back centre on a rear crossbar with upturned double risers, two long legs running forward
(open front), handrails on the column, a top bar reaching forward with the hooks, a harness hanging in front.
usage: python3 r_bws.py [id ...]"""
import sys
from r_lib import *


def base(d, W, legs_mat, riser_mat, CZ, leg_z=(30, 1120), XL=70, cast=100, cast_mat="rubber#d4d7db", bar_y=300,
         riser_z=(190, 360), caps="cap", shape=None):
    """Two legs along z (rect tube), braked castors at both ends, an inverted-U double riser per side carrying the
    rear crossbar on which the column stands."""
    XR = W - XL
    ly0, ly1 = cast + 18, cast + 63            # leg tube bottom/top
    d.bar("leg", [XL, (ly0 + ly1) / 2, leg_z[0]], [XL, (ly0 + ly1) / 2, leg_z[1]], [60, ly1 - ly0], legs_mat, r=6, mirror="x")
    d.box("leg-cap", [XL - 31, ly0 - 1, leg_z[1] - 2, XL + 31, ly1 + 1, leg_z[1] + 8], caps, r=6, mirror="x",
          copies=[[0, 0, leg_z[0] - leg_z[1] - 6]])
    d.caster("castor", [XL, 0, leg_z[0] + 55], cast, cast_mat, mirror="x", copies=[[0, 0, leg_z[1] - leg_z[0] - 110]])
    # risers: two parallel inverted-U rect tubes per side, their feet bolted to the leg
    z0, z1 = riser_z
    for k, dx in enumerate((-14, 30)):
        d.sweep(f"riser-{k}", [[XL + dx, ly1, z0], [XL + dx, bar_y + 20, z0], [XL + dx, bar_y + 20, z1], [XL + dx, ly1, z1]],
                [36, 40], riser_mat, bend=45, r=5, mirror="x", shape=shape)
    d.box("riser-plate", [XL + 31, ly0 + 4, z0 - 40, XL + 34, ly1 + 30, z1 + 40], riser_mat, r=2, mirror="x")
    d.decal("riser-bolt", [XL + 34.5, ly1 + 8, z0 - 20], [9, 9], "plastic#8d939a", face="right", soft=True, mirror="x",
            repeat=rep(4, [0, 0, (z1 - z0 + 40) / 3]))
    d.bar("crossbar", [XL + 10, bar_y + 20, (z0 + z1) / 2 - 10], [XR - 10, bar_y + 20, (z0 + z1) / 2 - 10], [100, 46],
          riser_mat, r=6)
    return bar_y + 43


def handrails(d, CX, CZ, y, half=300, z0=None, z1=None, foam="foam", clamp="white", cross="chrome", knobs=None):
    """Clamp on the column front, a crossbar along x, elbows and two foam handles pointing forward."""
    z0 = CZ - 40 if z0 is None else z0
    z1 = CZ + 500 if z1 is None else z1
    zc = CZ + 95
    d.box("rail-clamp", [CX - 45, y - 40, CZ + 50, CX + 45, y + 40, zc + 30], clamp, r=10)
    d.cyl("rail-cross", [CX - half, y, zc], [CX + half, y, zc], 32, cross)
    d.sphere("rail-elbow", [CX - half, y, zc], 40, cross, copies=[[2 * half, 0, 0]])
    d.cyl("handle", [CX - half, y, z0], [CX - half, y, z1], 42, foam, copies=[[2 * half, 0, 0]])
    d.sphere("handle-end", [CX - half, y, z1], 42, foam, copies=[[2 * half, 0, 0], [0, 0, z0 - z1], [2 * half, 0, z0 - z1]])
    if knobs:
        d.lathe("rail-knob", [CX - 75, y, zc], [[0, 0], [12, 0], [12, 14], [26, 18], [26, 40], [0, 42]], knobs, axis="z",
                copies=[[150, 0, 0]])


def vtop(d, CX, CZ, y, half, reach, mat, sec_=(50, 50), cap="cap", plate=False):
    """Top bar: two square arms from the column top fanning forward (a shallow V in plan) to the hook points."""
    ends = [(CX - half, CZ + reach), (CX + half, CZ + reach)]
    for i, (x, z) in enumerate(ends):
        d.bar(f"top-arm-{i}", [CX, y, CZ - 20], [x, y, z], list(sec_), mat, r=5)
        d.box(f"top-cap-{i}", [x - sec_[0] / 2 - 4, y - sec_[1] / 2 - 4, z - 4, x + sec_[0] / 2 + 4, y + sec_[1] / 2 + 4, z + 14],
              cap, r=6)
    return ends


def utop(d, CX, CZ, y, half, reach, mat, sec_=(50, 50), cap="cap"):
    """Top frame (review 2026-10-03, photos of E2/E3): a U in plan - a crossbar along x over the column top and two
    parallel square arms running forward to the hook points, black square end caps on their front ends."""
    d.bar("top-cross", [CX - half - sec_[0] / 2, y, CZ], [CX + half + sec_[0] / 2, y, CZ], list(sec_), mat, r=5)
    ends = [(CX - half, CZ + reach), (CX + half, CZ + reach)]
    for i, (x, z) in enumerate(ends):
        d.bar(f"top-arm-{i}", [x, y, CZ - sec_[1] / 2], [x, y, z], list(sec_), mat, r=5)
        d.box(f"top-cap-{i}", [x - sec_[0] / 2 - 4, y - sec_[1] / 2 - 4, z - 4, x + sec_[0] / 2 + 4, y + sec_[1] / 2 + 4, z + 14],
              cap, r=6)
    d.box("top-cap-back", [CX - half - sec_[0] / 2 - 18, y - sec_[1] / 2 - 4, CZ - sec_[1] / 2 - 4,
                           CX - half - sec_[0] / 2 - 4, y + sec_[1] / 2 + 4, CZ + sec_[1] / 2 + 4], cap, r=6,
          copies=[[2 * half + sec_[0] + 22, 0, 0]])
    return ends


def gen_e(id_):
    d = D(id_, [900, 1150, 2000], {
        "white": "plastic#f3f4f5", "chrome": "chrome", "steel": "metal#cfd3d8", "navy": "plastic#2e3a4c",
        "cap": "plastic#2b2f36", "foam": "rubber#1d1f22", "web": "fabric#1f2328", "vpad": "fabric#4c5763",
        "blue": "gloss#3da6e0", "black": "plastic#1b1d20", "grey": "plastic#9aa0a8"})
    CX, CZ = 450, 270
    top = base(d, 900, "white", "white", CZ, riser_z=(200, 350))
    # column foot: white block left of the column and the control box on its right (+x) with a blue label
    d.box("foot-block", [CX - 120, top, CZ - 75, CX - 40, top + 130, CZ + 75], "white", r=8)
    d.box("ctrl-box", [CX + 50, top, CZ - 80, CX + 300, top + 165, CZ + 80], "white", r=10)
    d.box("ctrl-label", [CX + 300, top + 30, CZ - 50, CX + 302, top + 135, CZ + 30], "blue", r=1, soft=True)
    d.lathe("ctrl-btn", [CX + 130, top + 165, CZ + 20], [[0, 0], [9, 0], [9, 6], [0, 7]], "black", copies=[[45, 0, 0]])
    d.box("ctrl-led", [CX + 220, top + 165, CZ - 10, CX + 250, top + 169, CZ + 30], "gloss#3fb4a0", r=3, soft=True)
    # column: white outer square, Linak actuator on its front face, blue scale on its right face, navy collar,
    # chrome inner stage and a white top that turns into the V top bar
    d.box("column", [CX - 50, top, CZ - 50, CX + 50, 1590, CZ + 50], "white", r=5)
    d.box("act-body", [CX - 32, 800, CZ + 50, CX + 32, 1360, CZ + 92], "chrome", r=8)
    d.box("act-bracket", [CX - 44, 790, CZ + 48, CX + 44, 820, CZ + 98], "steel", r=4, copies=[[0, 545, 0]])
    d.box("scale", [CX + 50, 860, CZ - 10, CX + 52, 1340, CZ + 10], "blue", r=1, soft=True)
    d.box("collar", [CX - 64, 1570, CZ - 64, CX + 64, 1635, CZ + 64], "navy", r=4)
    d.box("inner-chrome", [CX - 38, 1635, CZ - 38, CX + 38, 1720, CZ + 38], "chrome", r=4)
    d.box("inner-top", [CX - 38, 1720, CZ - 38, CX + 38, 1915, CZ + 38], "white", r=4)
    d.cyl("strut", [CX + 150, top + 165, CZ + 40], [CX + 52, 1050, CZ + 30], 16, "black")
    handrails(d, CX, CZ, 1080, half=290, z1=CZ + 640, cross="foam")
    ends = utop(d, CX, CZ, 1940, 200, 520, "white")
    hooks = [hook(d, f"hook-{i}", [x, 1915, z], "steel", 110) for i, (x, z) in enumerate(ends)]
    harness(d, CX, CZ + 500, 1940, hooks, vest_y=1130, mat="web", pad="vpad", buckle="steel")
    d.save()


def arc_top(d, CX, CZ, y, half, reach, mat, w=110, t=30, back=0, n=8):
    """Flat top bar bent in plan into an arc: middle on the column top, both ends forward (the hook points)."""
    pts = []
    for k in range(-n, n + 1):
        u = k / n
        pts.append([CX + half * u, y, CZ + 10 + reach * u * u])
    d.sweep("top-bar", pts, [w, t], mat, bend=40, r=6)
    if back:
        d.box("top-back", [CX - w / 2, y - t / 2, CZ - back, CX + w / 2, y + t / 2, CZ + 20], mat, r=6)
    return [(CX - half, CZ + 10 + reach), (CX + half, CZ + 10 + reach)]


def gen_g23(id_):
    g3 = id_ == "xy-k-g3"
    W, Dp = 1000, (1300 if g3 else 1200)
    d = D(id_, [W, Dp, 2050], {
        "white": "plastic#f2f3f4", "chrome": "chrome", "steel": "metal#cfd3d8", "navy": "plastic#2c3a54",
        "legs": "plastic#2b2e33" if g3 else "plastic#2c3a54", "cap": "plastic#3a4049", "pulley": "plastic#3f454d",
        "foam": "rubber#1d1f22", "web": "fabric#1d2026", "vpad": "fabric#a6accb" if g3 else "fabric#6c727b",
        "blue": "gloss#2f86d0", "black": "plastic#1b1d20", "red": "gloss#d42a26", "grey": "plastic#9aa0a8"})
    CX, CZ = W / 2, 260
    # review 2026-10-03: the risers stand ~250 above the legs in both photos (bar_y 300 -> 400)
    top = base(d, W, "legs", "white", CZ, leg_z=(30, Dp - 80), riser_z=(190, 340), caps="cap", bar_y=400)
    sg = -1 if g3 else 1        # G3's photo (front-left view) shows the long control box on the column's -x side
    xb0, xb1 = sorted((CX - sg * 240, CX - sg * 55))
    d.box("foot-block", [xb0, top, CZ - 75, xb1, top + 140, CZ + 75], "white", r=8)
    xc0, xc1 = sorted((CX + sg * 55, CX + sg * 330))
    d.box("ctrl-box", [xc0, top, CZ - 80, xc1, top + 150, CZ + 80], "white", r=10)
    xl = CX + sg * 330
    d.box("ctrl-label", [min(xl, xl + sg * 2), top + 25, CZ - 45, max(xl, xl + sg * 2), top + 125, CZ + 20], "blue", r=1, soft=True)
    d.lathe("ctrl-btn", [CX + sg * 120, top + 150, CZ + 10], [[0, 0], [8, 0], [8, 6], [0, 7]], "black", copies=[[sg * 40, 0, 0]])
    # column: white square with a navy collar, chrome actuator rods on the front, blue scale on the right face
    d.box("column", [CX - 55, top, CZ - 55, CX + 55, 1895, CZ + 55], "white", r=5)
    if g3:      # G3: a big dark collar block high on the column with a steel band above it
        d.box("collar", [CX - 82, 1600, CZ - 80, CX + 82, 1740, CZ + 80], "navy", r=6)
        d.box("collar-band", [CX - 60, 1740, CZ - 60, CX + 60, 1775, CZ + 60], "steel", r=4)
    else:
        d.box("collar", [CX - 70, 1480, CZ - 70, CX + 70, 1540, CZ + 70], "navy", r=4)
    d.cyl("act-rod", [CX - 25, 930, CZ + 70], [CX - 25, 1470, CZ + 70], 26, "chrome", copies=[[42, 0, 0]])
    d.box("act-bracket", [CX - 50, 905, CZ + 50, CX + 50, 935, CZ + 90], "steel", r=4, copies=[[0, 535, 0]])
    xs = CX + sg * 55          # the scale and the pendant are on the control box side
    d.box("scale", [min(xs, xs + sg * 2), 960, CZ - 12, max(xs, xs + sg * 2), 1440, CZ + 12], "blue", r=1, soft=True)
    d.box("pendant", [min(xs + sg * 2, xs + sg * 30), 1060, CZ - 20, max(xs + sg * 2, xs + sg * 30), 1180, CZ + 20], "blue", r=8)
    d.tube("pendant-cable", [[xs + sg * 17, 1060, CZ], [xs + sg * 25, 900, CZ - 10], [xs + sg * 30, 700, CZ - 30]], 7, "black",
           bend=60, soft=True)
    handrails(d, CX, CZ, 1050, half=300, z1=CZ + 620, knobs="black")
    d.cyl("handle-ring", [CX - 300, 1050, CZ + 641], [CX - 300, 1050, CZ + 652], 30, "white", copies=[[600, 0, 0]])
    ends = arc_top(d, CX, CZ, 1905, 330, 330, "white", back=90)
    hooks = []
    for i, (x, z) in enumerate(ends):
        d.box(f"pulley-{i}", [x - 45, 1918, z - 50, x + 45, 2050, z + 50], "pulley", r=22)
        d.decal(f"pulley-bolt-{i}", [x, 2015, z + 50.5], [14, 14], "steel", face="front", soft=True)
        hooks.append(hook(d, f"hook-{i}", [x, 1890, z], "steel", 120))
    if g3:
        d.box("top-label", [CX - 60, 1920, CZ + 20, CX + 20, 1922, CZ + 70], "blue", r=1, soft=True)
    else:       # G2: the round blue Xiangyu mark on the front edge of the top bar (second photo)
        d.cyl("top-logo", [CX, 1905, CZ + 64], [CX, 1905, CZ + 67], 27, "blue", soft=True)
        d.decal("top-logo-v", [CX, 1903, CZ + 67.5], [5, 16], "plastic#ffffff", "front", soft=True)
        d.decal("top-logo-h", [CX, 1908, CZ + 67.5], [16, 4], "plastic#ffffff", "front", soft=True)
    harness(d, CX, CZ + 440, 2000, hooks, vest_y=1150, mat="web", pad="vpad", accent="red", buckle="steel")
    d.save()


def gen_g6():
    W, Dp = 950, 1150
    d = D("xy-k-g6", [W, Dp, 2000], {
        "white": "plastic#f3f4f5", "chrome": "chrome", "steel": "metal#cfd3d8", "navy": "plastic#2c3a54",
        "cap": "plastic#2b2f36", "green": "gloss#2e9e57", "foam": "rubber#1d1f22", "web": "fabric#1d2026",
        "vpad": "fabric#6c727b", "blue": "gloss#2f86d0", "black": "plastic#1b1d20", "rope": "fabric#e9e4d6",
        "cream": "plastic#efe6c8", "slot": "plastic#c9cdd2", "red": "gloss#d42a26"})
    CX, CZ = W / 2, 250
    top = base(d, W, "navy", "navy", CZ, leg_z=(30, Dp - 30), cast=75, cast_mat="rubber#c9ccd0", bar_y=400,
               riser_z=(170, 340), caps="cap")
    # tall white housing with a green display head and a green edge stripe, a slot with the handrail carriage
    HB, HT = top, 1300
    d.box("housing", [CX - 130, HB, CZ - 100, CX + 130, HT, CZ + 100], "white", r=8)
    d.box("stripe", [CX + 128, 1000, CZ + 70, CX + 133, HT - 10, CZ + 98], "green", r=2)
    d.screen("display", [CX - 125, 1160, CZ + 100, CX + 115, 1270, CZ + 140], "green", print="med_xy-k-g6_screen",
             face="front", r=6)
    d.box("pend", [CX - 115, 1080, CZ + 100, CX - 35, 1120, CZ + 125], "blue", r=5, copies=[[115, 0, 0]])
    d.box("slot", [CX - 60, 820, CZ + 99, CX + 60, 1070, CZ + 101], "slot", r=4)
    d.cyl("guide", [CX - 35, 820, CZ + 106], [CX - 35, 1070, CZ + 106], 14, "chrome", copies=[[70, 0, 0]])
    d.cyl("screw", [CX, 820, CZ + 106], [CX, 1070, CZ + 106], 10, "steel")
    for i, s in enumerate((-1, 1)):
        d.coil(f"coil-cable-{i}", [CX + s * 100, 1075, CZ + 125], [CX + s * 100, 880, CZ + 125], 34, 6, 14, "black", soft=True)
    d.box("carriage", [CX - 55, 830, CZ + 100, CX + 55, 900, CZ + 150], "white", r=6)
    zc = CZ + 125
    d.cyl("rail-cross", [CX - 280, 880, zc], [CX + 280, 880, zc], 32, "black")
    d.cyl("handle", [CX - 280, 880, zc - 40], [CX - 280, 880, CZ + 640], 42, "foam", copies=[[560, 0, 0]])
    d.sphere("handle-end", [CX - 280, 880, CZ + 640], 42, "foam", copies=[[560, 0, 0]])
    # upper column and the top arm (shallow V) with the rope pulleys; ropes from the column pulleys to the harness
    d.box("upper", [CX - 60, HT, CZ - 60, CX + 60, 1940, CZ + 60], "white", r=5)
    ends = vtop(d, CX, CZ, 1960, 210, 400, "white", sec_=(60, 45), cap="white")
    hooks = []
    for i, (x, z) in enumerate(ends):
        d.add(f"pulley-{i}", "wheel", "cream", at=[x, 1910, z], d=60, d2=22, axis="x")
        d.cyl(f"pulley-fork-{i}", [x, 1938, z], [x, 1960, z], 24, "steel")
        cy = 1500
        d.add(f"col-pulley-{i}", "wheel", "cream", at=[CX + (i * 2 - 1) * 40, cy, CZ + 72], d=50, d2=18, axis="x")
        d.cyl(f"rope-up-{i}", [CX + (i * 2 - 1) * 40, cy + 25, CZ + 72], [x, 1890, z], 5, "rope", soft=True)
        d.cyl(f"rope-in-{i}", [CX + (i * 2 - 1) * 40, cy - 25, CZ + 72], [CX + (i * 2 - 1) * 40, HT, CZ + 72], 5, "rope", soft=True)
        d.cyl(f"rope-down-{i}", [x, 1880, z], [x, 1700, z], 5, "rope", soft=True)
        d.coil(f"spring-{i}", [x, 1700, z], [x, 1640, z], 18, 4, 5, "steel")
        hooks.append(hook(d, f"hook-{i}", [x, 1640, z], "steel", 80))
    harness(d, CX, CZ + 470, 1960, hooks, vest_y=1130, mat="web", pad="vpad", accent="red", buckle="steel")
    d.save()


def gen_g7():
    W, Dp = 900, 1100
    d = D("xy-k-g7", [W, Dp, 2000], {
        "white": "plastic#eceef0", "frame": "plastic#e4e6e9", "alu": "metal#c7ccd2", "alu2": "metal#b8bec5",
        "chrome": "chrome", "cap": "plastic#3a3f46", "foam": "rubber#1d1f22", "web": "fabric#16181b",
        "vpad": "fabric#202327", "grey": "plastic#9aa0a8", "lcd": "plastic#cfd8dc", "black": "plastic#1b1d20",
        "red": "gloss#d42a26"})
    CX, CZ = W / 2, 250
    top = base(d, W, "frame", "frame", CZ, leg_z=(30, Dp - 30), cast=75, cast_mat="rubber#c9ccd0", bar_y=400,
               riser_z=(170, 330), caps="cap", shape="round")
    # aluminium telescopic column (review 2026-10-03, photo): a NARROW lower stage on the base plate and the WIDER
    # grooved upper stage over it, a long rail / gas spring along its right side, then the display box
    d.box("col-plate", [CX - 75, top, CZ - 70, CX + 75, top + 12, CZ + 70], "black", r=3)
    d.box("col-inner", [CX - 50, top + 12, CZ - 44, CX + 50, 730, CZ + 44], "alu", r=4)
    d.box("col-outer", [CX - 64, 720, CZ - 54, CX + 64, 1400, CZ + 54], "alu", r=4)
    d.box("col-groove", [CX - 65, 760, CZ - 10, CX + 65, 1370, CZ + 10], "alu2", r=2)
    d.box("col-groove-f", [CX - 30, 760, CZ + 54, CX - 20, 1370, CZ + 55], "alu2", r=2, copies=[[50, 0, 0]])
    d.bar("gas-rail", [CX + 80, 780, CZ + 10], [CX + 80, 1320, CZ + 10], [22, 34], "alu2", r=4)
    d.cyl("gas-rod", [CX + 80, 560, CZ + 10], [CX + 80, 780, CZ + 10], 10, "chrome")
    d.box("display-box", [CX - 105, 1400, CZ - 70, CX + 105, 1530, CZ + 75], "white", r=8)
    d.box("display", [CX - 90, 1415, CZ + 75, CX + 60, 1515, CZ + 79], "lcd", r=3)
    d.box("display-icon", [CX - 80, 1480, CZ + 79, CX - 50, 1505, CZ + 80], "grey", r=2, soft=True, copies=[[90, 0, 0], [0, -50, 0], [90, -50, 0]])
    d.box("display-keys", [CX + 66, 1420, CZ + 75, CX + 98, 1510, CZ + 78], "grey", r=2)
    d.loft("upper", [sec(1530, 100, 110, 20, CX, CZ), sec(1800, 110, 130, 22, CX, CZ + 20),
                     sec(1950, 120, 170, 24, CX, CZ + 45)], "white")
    ends = arc_top(d, CX, CZ + 30, 1965, 230, 330, "white", w=70, t=50, back=0)
    d.box("top-back", [CX - 40, 1940, CZ - 140, CX + 40, 1990, CZ + 60], "white", r=6)
    hooks = []
    for i, (x, z) in enumerate(ends):
        d.box(f"top-end-{i}", [x - 42, 1935, z - 45, x + 42, 2000, z + 45], "white", r=8)
        d.box(f"top-end-face-{i}", [x - 22, 1950, z + 45, x + 22, 1985, z + 47], "cap", r=2)
        hooks.append(hook(d, f"hook-{i}", [x, 1935, z], "chrome", 90))
    # J handles (review 2026-10-03, photo): a clamp with two black knobs on each side face of the wide stage, the black
    # handle runs sideways (slightly forward) and bends up into the vertical grip; a big knob on the handle root
    HY = 1020
    d.box("rail-clamp", [CX + 64, HY - 60, CZ - 35, CX + 92, HY + 60, CZ + 35], "alu", r=6, mirror="x")
    d.lathe("rail-knob", [CX + 92, HY + 48, CZ], [[0, 0], [8, 0], [8, 10], [18, 13], [18, 30], [0, 32]], "black", axis="x",
            copies=[[0, -96, 0]], mirror="x")
    d.lathe("rail-knob2", [CX + 160, HY + 18, CZ + 40], [[0, 0], [12, 0], [12, 10], [26, 14], [26, 34], [0, 36]], "black",
            mirror="x")
    d.tube("handle", [[CX + 85, HY, CZ + 10], [CX + 300, HY - 12, CZ + 60], [CX + 318, HY + 180, CZ + 64]],
           40, "foam", bend=60, mirror="x")
    harness(d, CX, CZ + 470, 1965, hooks, vest_y=1330, mat="web", pad="vpad", accent="red", buckle="grey", vest_w=420,
            vest_d=280)
    d.save()


GEN = {"xy-k-e2": lambda: gen_e("xy-k-e2"), "xy-k-e3": lambda: gen_e("xy-k-e3"),
       "xy-k-g2": lambda: gen_g23("xy-k-g2"), "xy-k-g3": lambda: gen_g23("xy-k-g3"), "xy-k-g6": gen_g6, "xy-k-g7": gen_g7}

if __name__ == "__main__":
    for i in (sys.argv[1:] or list(GEN)):
        GEN[i]()
