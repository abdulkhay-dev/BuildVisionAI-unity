from h2lib import *
# HYZ-IIIC horizontal steam capsule (photo: the long side with the round control panel = front; head end LEFT).
# White glossy car-like shell: tallest over the head end, the top sloping down over the foot end to a rounded nose;
# a grey chassis / lower skirt, grey head-end panel, the white shell's lower edge arching up at the head end;
# blue double seam (lid split) with a V on both sides, two stainless hinges near the foot end; a hand hole with a
# stainless bar on each side; an oval cover plate and a blue tinted window on the top; round control panel and a
# music-player speaker on the front; 5 castors.
W, DP, H = 1950, 900, 1310
CZ = DP / 2
d = D("hyz-iiic", [W, DP, H], {
    "shell": "gloss#f8f9fa", "grey": "plastic#8a909a", "blue": "gloss#3a5fd0", "groove": "plastic#c9ced4",
    "steel": "metal#c8ccd0", "dark": "black#2b2f35", "win": "acrylic#3f6fd0c8", "green": "gloss#2fa84a"})
# white shell: (x, y_bottom, y_top, width z, corner r)
S = [(30, 360, 1150, 820, 220), (150, 380, 1240, 870, 260), (420, 300, 1265, 895, 290), (650, 130, 1270, 900, 300),
     (900, 110, 1270, 900, 300), (1180, 110, 1185, 900, 300), (1480, 116, 960, 890, 300), (1680, 122, 760, 870, 270),
     (1800, 140, 600, 820, 220)]
d.loft("shell", [sec(x, w, t - b, r, (t + b) / 2, CZ) for x, b, t, w, r in S], "shell", axis="x", dome="end", domeH=150)
# grey chassis: head-end panel and lower skirt
G = [(0, 40, 1120, 800, 200), (70, 40, 1130, 820, 220), (330, 40, 430, 860, 150), (620, 40, 210, 860, 70),
     (1720, 60, 200, 760, 70)]
d.loft("chassis", [sec(x, w, t - b, r, (t + b) / 2, CZ) for x, b, t, w, r in G], "grey", axis="x")


def sect(x):
    for a, b in zip(S, S[1:]):
        if a[0] <= x <= b[0]:
            u = (x - a[0]) / (b[0] - a[0])
            return [a[k] + (b[k] - a[k]) * u for k in range(5)]
    return list(S[0] if x < S[0][0] else S[-1])


def side_z(x, y):
    """z of the front side surface of the shell at (x, y)."""
    _, b, t, w, r = sect(x)
    lo, hi = b + r, t - r
    dy = 0 if lo <= y <= hi else (lo - y if y < lo else y - hi)
    dy = min(dy, r * 0.999)
    return CZ + (w / 2 - r) + math.sqrt(r * r - dy * dy)


# blue double seam with a grey groove between (front; the back side mirrored in z). Review: the photo's seam drops
# almost vertically from the roof just right of the round panel, curves into a long diagonal to a sharp V at ~half the
# length, rises to the two hinges and runs level to ~0.82 of the length; over the roof it crosses to the other side.
seam = [(500, 1150), (502, 1040), (510, 950), (540, 895), (600, 855), (760, 770), (900, 700), (960, 684), (1010, 700),
        (1150, 760), (1280, 805), (1340, 812), (1400, 814), (1450, 815), (1500, 816), (1550, 816), (1600, 816)]


def seam_path(off, back=False, lift=3.0):
    pts = []
    n = len(seam)
    for i, (x, y) in enumerate(seam):
        ax, ay = seam[max(0, i - 1)]; bx, by = seam[min(n - 1, i + 1)]
        tx, ty = bx - ax, by - ay; L = math.hypot(tx, ty) or 1
        nx, ny = ty / L, -tx / L                       # normal pointing down/right of the path
        px, py = x + nx * off, y + ny * off
        z = side_z(px, py) + lift
        pts.append([px, py, DP - z if back else z])
    return pts


def roof(off, lift=1.0):
    """The seam over the roof at x ~ 500: around the section's two upper corners from the side seam's top."""
    x = 500 - off
    _, b, t, w, r = sect(x)
    yc = t - r
    a0 = math.degrees(math.asin(max(-1, min(1, (1150 - yc) / r))))
    pts = []
    for k in range(9):
        a = math.radians(a0 + (90 - a0) * k / 8)
        pts.append([x, yc + (r + lift) * math.sin(a), CZ + (w / 2 - r) + (r + lift) * math.cos(a)])
    back = [[p[0], p[1], DP - p[2]] for p in reversed(pts)]
    return pts + back


for back in (False, True):
    sfx = "-b" if back else ""
    d.tube("seam-a" + sfx, seam_path(0, back), 10, "blue", bend=60, soft=True)
    d.tube("seam-g" + sfx, seam_path(13, back), 8, "groove", bend=60, soft=True)
    d.tube("seam-c" + sfx, seam_path(26, back), 10, "blue", bend=60, soft=True)
for i, off in enumerate((0, 13, 26)):
    d.tube(f"seam-roof{i}", roof(off), 10 if off != 13 else 8, "blue" if off != 13 else "groove", bend=40, soft=True)
for back in (False, True):
    sfx = "-b" if back else ""
    # hand hole with a stainless bar
    zf = side_z(740, 900)
    zz = (lambda v: DP - v) if back else (lambda v: v)
    w0, w1 = (zf - 6, zf + 2) if not back else (DP - zf - 2, DP - zf + 6)
    d.slab("hand-hole" + sfx, "front", P(rr(620, 860, 860, 1000, 55)), [w0, w1], "plastic#e9ecef", r=4)
    d.slab("hand-hole-in" + sfx, "front", P(rr(645, 878, 835, 982, 42)),
           [w1 - 0.5, w1 + 0.5] if not back else [w0 - 0.5, w0 + 0.5], "plastic#b8bec5", r=0.5)
    d.cyl("hand-bar" + sfx, [655, 930, zz(zf + 8)], [825, 930, zz(zf + 8)], 26, "steel")
    # hinges near the foot end
    for i, x in enumerate((1340, 1490)):
        z = side_z(x, 813)
        d.box(f"hinge{i}{sfx}", [x - 60, 790, zz(z - 6), x + 60, 836, zz(z + 5)], "steel", r=4)
# round control panel and the music-player speaker on the front
zp = side_z(330, 600)
d.lathe("panel", [330, 600, zp - 10], [[0, 0], [235, 0], [235, 14], [225, 22], [0, 24]], "shell", axis="z")
d.decal("panel-label", [210, 720, zp + 14.5], [70, 120], "front", "plastic#dfe3e8", soft=True)
for i, (x, y) in enumerate([(300, 610), (340, 618), (310, 580), (350, 588)]):
    d.lathe(f"btn{i}", [x, y, zp + 14], [[0, 0], [11, 0], [11, 5], [0, 7]], "green", axis="z", soft=True)
d.decal("panel-lcd", [328, 555, zp + 14.5], [40, 24], "front", "screen", soft=True)
d.tube("panel-ring", [[330 + 205 * math.cos(a / 12 * math.pi), 600 + 205 * math.sin(a / 12 * math.pi), zp + 14]
                      for a in range(25)], 4, "plastic#d8dce1", soft=True)
zs = side_z(300, 1125)
d.lathe("speaker", [300, 1125, zs - 8], [[0, 0], [72, 0], [72, 10], [64, 14], [0, 14]], "shell", axis="z",
        rot=rot("x", -26, [300, 1125, zs]))
# oval cover plate and blue tinted window on the top
d.slab("cover", "top", P(ell(720, 520, 130, 70)), [1256, 1271], "plastic#eef0f2", r=5)
d.loft("window", [sec(1180, 330, 380, 160, 1060, CZ), sec(1235, 300, 350, 150, 1060, CZ)], "win", dome="end", domeH=45)
# castors
d.add("castor", "caster", at=[170, 0, 170], d=60, mat="rubber#6b7077", copies=[[0, 0, 560], [1350, 0, 0], [1350, 0, 560]])
d.add("castor-nose", "caster", at=[1680, 0, CZ], d=60, mat="rubber#6b7077")
d.save()
