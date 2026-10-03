from pfx_lib import *
import math
# seated steam capsule: vertical rear, front hood sloping forward-down, domed shoulders with a neck notch on top,
# curved headrest at the rear top; the hood's split line is the green double seam
d = D("hyz-iiia", [800, 1100, 1400], {
  "shell": "gloss#f7f8f8", "seam": "gloss#2e9a3e", "dark": "plastic#4f555b", "pad": "gloss#f1f2f2",
  "label": "gloss#1f6b35", "leaf": "gloss#8cc63f"})
# body: loft along y; (y, w, d, r, cx, cz)
S = [(40, 700, 940, 200, 400, 580), (110, 780, 1030, 230, 400, 555), (250, 800, 1050, 240, 400, 545),
     (600, 800, 960, 240, 400, 500), (950, 800, 820, 240, 400, 430), (1100, 780, 735, 220, 400, 387)]
# the body ends low (the bottom of the neck notch); the shoulders rise above it
d.loft("body", [sec(*s) for s in S], "shell")
def sect(y):
    for i in range(len(S) - 1):
        a, b = S[i], S[i + 1]
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return [a[k] + (b[k] - a[k]) * t for k in range(6)]
    return list(S[-1] if y > S[-1][0] else S[0])
def left_x(y, z):
    _, w, dd, r, cx, cz = sect(y)
    hw, hd = w / 2, dd / 2
    dz = abs(z - cz)
    if dz <= hd - r: return cx - hw
    t = min(dz - (hd - r), r * 0.995)
    return cx - (hw - r) - math.sqrt(r * r - t * t)
def front_z(y): s = sect(y); return s[5] + s[2] / 2
# --- domed shoulders either side of the neck notch (part of the hood)
# two rounded ridges from the seam (rear) to the front face, flush with the front slope and the body sides; their
# inner faces slant so that together they form the deep V-notch at the front of the head opening
d.loft("shoulder", [sec(950, 800, 820, 240, 400, 430), sec(1100, 470, 437, 218, 245, 537),
                    sec(1200, 373, 420, 165, 198.5, 500), sec(1300, 240, 410, 115, 160, 440)],
       "shell", dome="end", domeH=40, mirror="x")
# rear collar (the rear shell behind the split line) rising to shoulder height either side of the neck opening;
# its front face is the seam plane z = 250 + (1230 - y) * 0.679, the shoulders stop just ahead of it -> the groove
d.loft("collar", [sec(1085, 352, 268, 120, 184, 204), sec(1200, 328, 190, 90, 176, 175),
                  sec(1290, 265, 118, 55, 167.5, 149)], "shell", dome="end", domeH=35, mirror="x")
# --- head well behind the notch, ear discs with dark holes on the shoulders' inner faces
d.sphere("head-well", [400, 1180, 460], None, "dark", radii=[42, 10, 180])
d.lathe("ear", [335, 1240, 470], [[0, 0], [45, 0], [45, 10], [70, 28], [62, 32], [0, 26]], "pad", axis="x", mirror="x")
d.lathe("ear-hole", [362, 1240, 470], [[0, 0], [32, 0], [32, 2], [0, 2]], "dark", axis="x", soft=True, mirror="x")
# --- curved headrest shell at the rear top (concave to the front, ends curling forward)
d.slab("headrest", "top", "M 50 330 Q 400 -290 750 330 L 700 350 Q 400 -210 100 350 Z", [1095, 1400], "pad", r=22)
# translucent lid fin at the right rear of the head area
d.box("lid-fin", [600, 1250, 170, 608, 1390, 250], "acrylic#f2f5f7b0", r=4, rot=rot("z", -22, [604, 1250, 210]))
# --- green double seam: sides (diagonal rear-top -> front-bottom), across the front bottom, across the top
def side_path(dy):
    pts = []
    def up_x(y):  # outer side of the shoulder / collar above the body top
        return 8 + (y - 1095) / 105 * 4 if y < 1200 else 12 + (y - 1200) / 90 * 23
    for y in [1290, 1250, 1200, 1150] + list(range(1095, 110, -75)) + [108]:
        yy = y + dy
        z = 250 + (1230 - y) / 1120 * 760
        pts.append([(left_x(yy, z) if yy <= 1095 else up_x(yy)) - 3, yy, z])
    return pts
def front_path(y):
    _, w, dd, r, cx, cz = sect(y)
    hw, hd = w / 2 + 3, dd / 2 + 3
    z0 = 250 + (1230 - 108) / 1120 * 760
    zc = cz + (hd - 3 - r)                 # centre z of the front corner arcs
    a0 = math.asin(max(-1, min(1, (z0 - zc) / (r + 3))))
    arc = [a0 + (math.pi / 2 - a0) * k / 6 for k in range(7)]
    pts = [[cx - (hw - r) - (r + 3) * math.cos(a), y, zc + (r + 3) * math.sin(a)] for a in arc]
    pts += [[cx + (hw - r) + (r + 3) * math.cos(a), y, zc + (r + 3) * math.sin(a)] for a in reversed(arc)]
    return pts
def bez(p0, c, p1, t): return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t * t * p1
def top_path(dz):
    # from the side top over the collar behind the shoulder, down the edge of the neck opening, across behind the head
    half = [[80, 1318, 202], [200, 1328, 196], [310, 1312, 190], [368, 1230, 182], [392, 1120, 178]]
    half = [[x, y, z - dz] for x, y, z in half]
    return half + [[800 - x, y, z] for x, y, z in reversed(half)]
for nm, dy in (("a", 0), ("b", 18)):
    sp = side_path(dy)
    d.tube(f"seam-side-{nm}", sp, 9, "seam", bend=120, soft=True, mirror="x")
    d.tube(f"seam-front-{nm}", front_path(108 + dy), 9, "seam", bend=60, soft=True)
    tp = top_path(dy)
    d.tube(f"seam-top-{nm}", [[sp[0][0], sp[0][1], sp[0][2]]] + tp + [[800 - sp[0][0], sp[0][1], sp[0][2]]],
           9, "seam", bend=60, soft=True)
# --- green leaf label on the upper front right (on the sloping front face)
zl = front_z(1000) + 1.5
lr = rot("x", -27, [480, 1000, zl])
d.decal("label", [480, 1000, zl], [190, 86], "front", "label", soft=True, rot=lr)
d.decal("label-leaf", [500, 1010, zl + 0.6], [120, 30], "front", "leaf", soft=True, rot=rot("x", -27, [500, 1010, zl]))
d.decal("label-text", [470, 980, zl + 0.6], [140, 8], "front", "plastic#e8f2e0", soft=True, rot=rot("x", -27, [470, 980, zl]))
# --- pull handle with small holes at the bottom front, small castors
d.box("handle", [255, 92, 1040, 545, 152, 1100], "pad", r=22)
d.decal("handle-hole", [340, 135, 1100.5], [8, 8], "front", "dark", soft=True, repeat=rep(4, [40, 0, 0]),
        copies=[[0, -28, 0]])
d.add("castor", "caster", at=[170, 0, 150], d=50, copies=[[460, 0, 0], [0, 0, 820], [460, 0, 820]])
d.save()
