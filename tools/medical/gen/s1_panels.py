"""Sensory wall panels of the 'bear-ear' family: cognitive-training-board, color-conversion-control-panel,
dynamic-color-wheel, endless-depth-light-mirror, fiber-optic-curtain-wall. Usage: s1_panels.py [id ...]"""
import math, sys
from s1lib import *

DP = 90
RED, YEL, GRN, BLU = "gloss#d8231c", "gloss#f4d31a", "gloss#2fb43a", "gloss#1f55c8"


def cognitive():
    W, H = 618, 900
    d = D("cognitive-training-board", [W, DP, H], {
        "case": "plastic#3fab45", "grille": "plastic#2f8a36", "face": "plastic#eccb10", "black": "plastic#111213"})
    cx = W / 2
    panel_case(d, W, H, DP, ears=[(75, 825, 75), (W - 75, 825, 75)], body=(16, 0, W - 16, 880, 60),
               bumps=[(80, 62, 120), (W - 80, 62, 120)],
               buttons=[(cx - 77, 59, 30, RED), (cx, 59, 30, YEL), (cx + 77, 59, 30, GRN)],
               logo=(cx, 847), grille_mat="grille")
    z = DP
    front_slab(d, "face", rrect_pts(89, 124, W - 89, 812, 20), z - 1, z + 1.5, "face", r=1)
    # screen band and display
    d.box("bezel", [89, 319, z + 1, W - 89, 637, z + 3], "black", r=1)
    d.add("display", "screen", "black", box=[102, 330, z + 2, W - 102, 627, z + 4], r=2, face="front", bezel=0)
    zs = z + 4.3
    # interface (no screenCrop), as on the photo: a golden 'bamboo' background over the whole display, a green title
    # banner, a peach column of 2 x 7 white cards at the left, the red-framed white page with an ink painting (pot and
    # figure), a column of 5 pink tabs at the right and 4 green round buttons on a dark strip under the page
    d.decal("ui-bg", [309, 478.5, zs], [412, 295], "front", "gloss#b8923a", soft=True)
    for k in range(9):
        d.decal(f"ui-bamboo{k}", [118 + k * 48, 609, zs + 0.2], [6, 24], "front", "gloss#8f6c26", soft=True)
    d.decal("ui-banner", [340, 609, zs + 0.4], [150, 28], "front", "gloss#3d7a2a", soft=True)
    d.decal("ui-title", [340, 609, zs + 0.6], [112, 8], "front", "gloss#e8d040", soft=True)
    d.decal("ui-col", [141, 466, zs + 0.2], [72, 252], "front", "gloss#f0c4a0", soft=True)
    for r_ in range(7):
        for c_, x in enumerate((124, 158)):
            d.decal(f"ui-card{r_}{c_}", [x, 571 - r_ * 35, zs + 0.4], [28, 27], "front", "gloss#f6f6f4", soft=True)
    d.decal("ui-frame", [342, 471, zs + 0.2], [315, 242], "front", "gloss#d8323c", soft=True)
    d.decal("ui-page", [342, 471, zs + 0.4], [302, 229], "front", "gloss#f7f7f5", soft=True)
    for k in range(5):
        d.decal(f"ui-tab{k}", [509, 576 - k * 30, zs + 0.4], [13, 22], "front", "gloss#f2b6c8", soft=True)
    d.decal("ui-strip", [342, 339, zs + 0.2], [315, 20], "front", "gloss#4a3020", soft=True)
    for k in range(4):
        front_slab(d, f"ui-btn{k}", ellipse_pts(219 + k * 50, 339, 18, 10, 16), zs + 1.0, zs + 1.6, "gloss#6cc040", soft=True)
    d.decal("ui-corner", [497, 341, zs + 0.4], [18, 12], "front", "gloss#8a50c0", soft=True)
    # the painting: an olive-brown pot with green leaves, a white figure in it, a title and a green cluster
    front_slab(d, "ui-pot", ellipse_pts(342, 440, 70, 36, 20), zs + 1.4, zs + 2.0, "gloss#5d5530", soft=True)
    disc(d, "ui-leaf", 300, 452, zs + 2.0, 34, "gloss#7d8a3c", h=0.4)
    disc(d, "ui-leaf2", 372, 430, zs + 2.0, 30, "gloss#6f7a34", h=0.4)
    d.decal("ui-figure", [354, 492, zs + 2.6], [24, 62], "front", "gloss#e4ead4", soft=True)
    d.decal("ui-cluster", [432, 540, zs + 0.8], [38, 50], "front", "gloss#93a07c", soft=True)
    d.box("ui-text", [226, 562, zs + 0.4, 286, 570, zs + 1.2], "black", soft=True)
    # cat face above the screen: whisker bars, dots
    for i, (y, x0, x1) in enumerate([(757, 102, 182), (726, 100, 190), (696, 102, 182)]):
        front_slab(d, f"wh{i}L", rrect_pts(x0, y - 8, x1, y + 8, 7.9), z + 1, z + 2.3, "black", soft=True)
        front_slab(d, f"wh{i}R", rrect_pts(W - x1, y - 8, W - x0, y + 8, 7.9), z + 1, z + 2.3, "black", soft=True)
    for i, (x, y, dd) in enumerate([(cx - 31, 701, 22), (cx + 31, 701, 22), (cx - 80, 730, 13), (cx - 39, 729, 13),
                                    (cx - 64, 712, 13), (cx + 80, 730, 13), (cx + 39, 729, 13), (cx + 64, 712, 13)]):
        disc(d, f"dot{i}", x, y, z + 1, dd, "black", h=1.3)
    # speakers and grille lines under the screen
    disc(d, "spkL", 137, 222, z + 1, 66, "black", h=1.3)
    disc(d, "spkR", W - 137, 222, z + 1, 66, "black", h=1.3)
    for i, (y, hw) in enumerate([(240, 80), (217, 72), (194, 80)]):
        d.box(f"line{i}", [cx - hw, y - 4, z + 1, cx + hw, y + 4, z + 2.3], "black", soft=True)
    d.save()


def color_conversion():
    W, H = 600, 900
    d = D("color-conversion-control-panel", [W, DP, H], {
        "case": "plastic#d65b84", "grille": "plastic#b84a70", "face": "plastic#ebe2d0", "black": "plastic#111213"})
    cx = W / 2
    panel_case(d, W, H, DP, ears=[(60, 840, 60), (W - 60, 840, 60)], body=(0, 0, W, 868, 55),
               bumps=[(70, 60, 110), (W - 70, 60, 110)],
               buttons=[(cx - 80, 50, 42, "gloss#a8182a"), (cx, 50, 42, YEL), (cx + 80, 50, 42, BLU)],
               logo=(cx, 875), grille_mat="grille", btn_ring="black")
    # remove the logo: the photo shows none on this panel (the ears/top are plain)
    d.d["parts"] = [p for p in d.d["parts"] if not p["id"].startswith(("logo", "grille"))]
    z = DP
    d.box("frame", [80, 92, z - 1, W - 80, 846, z + 2], "black", r=1)
    d.box("face", [89, 101, z, W - 89, 837, z + 3], "face", r=1)
    zt = z + 3
    fw, fh, fx0, fy1 = W - 178, 736, 89, 837
    def P(fx, fy): return (fx0 + fx * fw, fy1 - fy * fh)
    tris = [("r1a", 0.25, 0.20, "right", "gloss#d81e1e"), ("r1b", 0.5, 0.20, "up", "gloss#f2dc10"),
            ("r1c", 0.75, 0.20, "left", "gloss#1838c0"), ("r2a", 0.25, 0.36, "right", "gloss#e8558c"),
            ("r2b", 0.5, 0.36, "up", "gloss#f2dc10"), ("r2c", 0.75, 0.36, "left", "gloss#0e8a4a"),
            ("dpu", 0.5, 0.72, "up", "gloss#f2dc10"), ("dpl", 0.33, 0.79, "left", "gloss#e8558c"),
            ("dpr", 0.67, 0.79, "right", "gloss#0e8a4a"), ("dpd", 0.5, 0.86, "down", "gloss#0e8a4a")]
    for id_, fx, fy, dr, mat in tris:
        x, y = P(fx, fy)
        front_slab(d, "tri-" + id_, round_poly(tri_pts(x, y, 46, dr), 4, 3), zt - 1, zt + 16, mat, r=3, soft=True)
    # the photo shows a small black port low on the x = 0 side
    d.box("port", [-1, 185, 35, 1.5, 215, 52], "black", r=2, soft=True)
    d.save()


def dynamic_wheel():
    W, H = 575, 900
    d = D("dynamic-color-wheel", [W, DP, H], {
        "case": "plastic#bdb6dc", "grille": "plastic#9a90c4", "face": "gloss#f3f4f7", "black": "plastic#111213"})
    cx = W / 2
    panel_case(d, W, H, DP, ears=[(57, 842, 57), (W - 57, 842, 57)], body=(25, 0, W - 25, 882, 55),
               bumps=[(77, 64, 112), (W - 77, 64, 112)],
               buttons=[(cx - 74, 59, 32, RED), (cx, 59, 32, YEL), (cx + 74, 59, 32, GRN)],
               logo=(cx, 850), grille_mat="grille", btn_ring="plastic#9a92c0")
    z = DP
    d.box("bezel", [81, 120, z - 1, W - 81, 814, z + 2], "black", r=4)
    d.box("face", [98, 138, z, W - 98, 797, z + 3], "face", r=1)
    zf = z + 3
    ccx, ccy = cx, 471
    # the photo's LED windmill: 8 slightly curved arms (deep cyan near the centre) that open into feathery fans of
    # light-cyan dots, inside a lobed disc of faint dot lines; white petals between the arms near the centre.
    # Seen from the front the arms turn clockwise as they go out.
    def spiral(a0, r0, r1, n, twist):
        return [(ccx + (r0 + (r1 - r0) * t) * math.cos(a0 - twist * t), ccy + (r0 + (r1 - r0) * t) * math.sin(a0 - twist * t))
                for t in [j / (n - 1) for j in range(n)]]
    lobe = [(ccx + (172 + 12 * math.cos(8 * a + 0.4)) * math.cos(a), ccy + (172 + 12 * math.cos(8 * a + 0.4)) * math.sin(a))
            for a in [2 * math.pi * k / 96 for k in range(96)]]
    front_slab(d, "halo", lobe, zf, zf + 0.4, "gloss#e2f2f7", soft=True)
    disc(d, "core", ccx, ccy, zf + 0.4, 190, "gloss#f6f8f9", h=0.4)
    faint, fan, arm = [], [], []
    for k in range(8):
        a0 = 2 * math.pi * k / 8 + 0.3
        for j in range(5):                       # faint dot lines filling the outer disc
            faint.append(spiral(a0 + (j - 2) * 0.13, 95, 176, 4, 0.55))
        for j in (-1, 1):                        # the fan the arm opens into
            fan.append(spiral(a0 + j * 0.07, 55, 140, 4, 0.55 + j * 0.12))
        arm.append(spiral(a0, 4, 105, 5, 0.42))
    strokes(d, "dots", faint, zf + 0.9, 2.2, "gloss#b4e0ec")
    strokes(d, "fan", fan, zf + 1.1, 3.5, "gloss#7ccbe0")
    strokes(d, "arm", arm, zf + 1.3, 6.5, "gloss#2fa2c8")
    d.save()


def endless_mirror():
    W, H = 620, 900
    d = D("endless-depth-light-mirror", [W, DP, H], {
        "case": "plastic#2ca33a", "grille": "plastic#22862e", "face": "gloss#f2f2f3", "black": "plastic#111213"})
    cx = W / 2
    panel_case(d, W, H, DP, ears=[(66, 831, 64), (W - 66, 831, 64)], body=(28, 0, W - 28, 880, 60),
               bumps=[(86, 61, 118), (W - 86, 61, 118)],
               buttons=[(cx - 77, 61, 30, RED), (cx, 61, 30, YEL), (cx + 77, 61, 30, GRN)],
               logo=(cx, 847), grille_mat="grille", btn_ring="plastic#22862d")
    z = DP
    d.box("bezel", [86, 126, z - 1, W - 86, 811, z + 2], "black", r=4)
    d.box("face", [106, 146, z, W - 106, 790, z + 3], "face", r=1)
    zf = z + 3
    ccx, cyt, cyb = cx, 541, 378     # the two white circles of the "8"
    # a pale pink field shaped like an 8 (two discs of r 200), dotted rays radiating from each circle (stronger near
    # it, fading outwards), two white circles, and the bright red waist with a small red ellipse
    for i, cy in enumerate((cyt, cyb)):
        disc(d, f"halo{i}", ccx, cy, zf, 400, "gloss#fbf0f0", h=0.3)
    inner, outer = [], []
    for i, (cy, oy) in enumerate(((cyt, cyb), (cyb, cyt))):
        for k in range(44):
            a = 2 * math.pi * (k + 0.5 * i) / 44
            ca, sa = math.cos(a), math.sin(a)
            def P(r): return (ccx + r * ca, cy + r * sa)
            def free(r):     # outside the other circle's white disc
                x, y = P(r); return (x - ccx) ** 2 + (y - oy) ** 2 > 100 ** 2
            if not free(96):
                continue
            r1 = 150
            while r1 > 100 and not free(r1):
                r1 -= 6
            inner.append([P(97), P(r1)])
            r2 = 198
            if free(r1 + 4):
                while r2 > r1 + 8 and not free(r2):
                    r2 -= 6
                if r2 > r1 + 8:
                    outer.append([P(r1 + 4), P(r2)])
    strokes(d, "rayo", outer, zf + 0.5, 2.2, "gloss#f2c6c6")
    strokes(d, "rayi", inner, zf + 0.7, 2.6, "gloss#e79090")
    for i, cy in enumerate((cyt, cyb)):
        front_slab(d, f"white{i}", ellipse_pts(ccx, cy, 94, 84, 32), zf + 0.9, zf + 1.2, "gloss#f6f4f4", soft=True)
    wy = (cyt + cyb) / 2
    rays = []
    for sx in (-1, 1):
        for k in range(-3, 4):
            rays.append([(ccx + sx * 40, wy + k * 2), (ccx + sx * 140, wy + k * 12)])
    strokes(d, "ray", rays, zf + 1.3, 2.5, "gloss#e04848")
    ell = [(ccx + 50 * math.cos(a), wy + 10 * math.sin(a)) for a in [2 * math.pi * k / 16 for k in range(17)]]
    strokes(d, "ell", [ell], zf + 1.4, 3.5, "gloss#d42a2a")
    d.save()


def fibre_wall():
    W, H = 565, 900
    d = D("fiber-optic-curtain-wall", [W, DP, H], {
        "case": "plastic#c4358b", "grille": "plastic#a02a70", "band": "plastic#36bcc0", "fibre": "gloss#f6f6f8"})
    cx = W / 2
    panel_case(d, W, H, DP, ears=[(56, 835, 57), (W - 56, 835, 57)], body=(24, 0, W - 24, 884, 55),
               bumps=[(76, 59, 112), (W - 76, 59, 112)],
               buttons=[(cx - 72, 59, 30, RED), (cx, 59, 30, YEL), (cx + 72, 59, 30, GRN)],
               logo=(cx, 843), grille_mat="grille", btn_ring="plastic#9a2468")
    z = DP
    # raised lip around the face
    lip = path(rrect_pts(76, 116, W - 76, 811, 14)) + " " + path(list(reversed(rrect_pts(90, 130, W - 90, 797, 6))))
    front_slab(d, "lip", lip, z - 1, z + 8, "case", r=3)
    d.box("fibrebed", [90, 130, z - 1, W - 90, 715, z + 2], "fibre", r=1)
    d.box("band", [90, 719, z - 1, W - 90, 797, z + 4], "band", r=2)
    # the glowing fibre field: a faint pink glow along its edges and ~20 wavy, dotted-looking vertical strands
    for i, (at, sz) in enumerate([([97, 422, z + 2.1], [12, 580]), ([W - 97, 422, z + 2.1], [12, 580]),
                                  ([cx, 137, z + 2.1], [W - 180, 12])]):
        d.decal(f"glow{i}", at, sz, "front", "gloss#f4d2e6", soft=True)
    strands = []
    for k in range(20):
        x = 104 + k * (W - 208) / 19
        pts = [(x + 6 * math.sin(j * 1.3 + k * 1.7), 136 + j * 72.5) for j in range(9)]
        strands.append(pts)
    strokes(d, "strand", strands, z + 2.2, 3.0, "gloss#cdcdd6")
    # stars on the band
    for i, (x, R, mat) in enumerate([(135, 24, "gloss#c83a96"), (213, 22, "gloss#f2df2a"), (cx, 29, "gloss#11963c"),
                                     (W - 213, 22, "gloss#f2df2a"), (W - 135, 24, "gloss#c83a96")]):
        front_slab(d, f"star{i}", star_pts(x, 756, R, R * 0.45), z + 3, z + 5, mat, soft=True)
    d.save()


ALL = {"cognitive-training-board": cognitive, "color-conversion-control-panel": color_conversion,
       "dynamic-color-wheel": dynamic_wheel, "endless-depth-light-mirror": endless_mirror,
       "fiber-optic-curtain-wall": fibre_wall}
if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()
