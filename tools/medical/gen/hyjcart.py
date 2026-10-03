"""Shared white Sunnyou microwave cart of HYJ-II (Enhanced) / HYJ-III / HYJ-IV: base, column, rail, head, arms, radiators.
Cart centre x = cx; base z 0..500, column z 65..435; head top 1050 at the rear, 945 at the front."""
import math
from lib import *

MATS = {"shell": "gloss#f2f3f5", "grey": "plastic#8a9099", "rail": "plastic#9aa0a8", "railtop": "plastic#4d5259",
        "base": "plastic#9aa0a8", "dark": "plastic#2c3036", "glass": "gloss#373b41", "arm": "plastic#eceef0",
        "arm2": "plastic#7b8088", "chrome": "chrome", "black": "gloss#15171a", "cable": "plastic#a9aeb5",
        "blue": "gloss#2f7fd0", "white": "plastic#f6f7f8"}
Z0, Z1 = 65, 435          # column back / front
TOP_F, TOP_R = 945, 1050  # head top front / rear
SLOPE = math.degrees(math.atan2(TOP_R - TOP_F, Z1 - Z0))


def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def cart(d, cx, logo="sunnyou"):
    # --- base: one sculpted X plate (grey body, white top skin), concave sides, round lobes over Ø100 castors
    def xbase(a, r, k):
        f, b = 250 + 205, 250 - 205
        return (f"M {cx - a - r} {f} Q {cx - a - r} {f + r} {cx - a} {f + r} Q {cx} {f + r - 2 * k} {cx + a} {f + r} "
                f"Q {cx + a + r} {f + r} {cx + a + r} {f} Q {cx + a + r - 2 * k} 250 {cx + a + r} {b} "
                f"Q {cx + a + r} {b - r} {cx + a} {b - r} Q {cx} {b - r + 2 * k} {cx - a} {b - r} "
                f"Q {cx - a - r} {b - r} {cx - a - r} {b} Q {cx - a - r + 2 * k} 250 {cx - a - r} {f} Z")
    d.slab("base", "top", xbase(240, 40, 30), [118, 156], "base", r=10)
    d.slab("base-top", "top", xbase(236, 36, 30), [150, 162], "shell", r=5)
    d.add("castor", "caster", "plastic#8f949a", at=[cx - 240, 0, 455], d=100, copies=[[480, 0, 0], [0, 0, -410], [480, 0, -410]])
    # --- column
    d.box("column", [cx - 200, 156, Z0, cx + 200, 840, Z1], "shell", r=26)
    d.box("band", [cx - 201, 560, Z1 - 30, cx + 201, 592, Z1 + 2], "grey", r=6)
    d.box("seam", [cx - 199, 757, Z1 - 1, cx + 199, 760, Z1 + 1], "plastic#c9cdd2", soft=True)
    d.box("vent", [cx - 48, 186, Z1, cx - 22, 190, Z1 + 1.5], "dark", soft=True,
          copies=[[35, 0, 0], [70, 0, 0], [5, 20, 0], [40, 20, 0], [75, 20, 0]])
    if logo == "sunnyou":
        d.box("logo", [cx - 55, 290, Z1, cx + 50, 310, Z1 + 1.5], "plastic#7f858d", soft=True)
        d.box("logo-sub", [cx - 30, 318, Z1, cx + 34, 322, Z1 + 1.5], "plastic#9aa0a8", soft=True)
    else:
        d.cyl("logo-mark", [cx - 55, 300, Z1 - 1], [cx - 55, 300, Z1 + 1.5], 28, "plastic#6d7a8a", soft=True)
        d.box("logo-x", [cx - 57, 290, Z1 + 1, cx - 53, 310, Z1 + 2.2], "white", soft=True)
        d.box("logo-y", [cx - 64, 302, Z1 + 1, cx - 46, 306, Z1 + 2.2], "white", soft=True)
        d.box("logo", [cx - 36, 298, Z1, cx + 34, 314, Z1 + 1.5], "plastic#7f8b99", soft=True)
        d.box("logo-sub", [cx - 36, 286, Z1, cx + 34, 290, Z1 + 1.5], "plastic#9aa0a8", soft=True)
    # louvres: slanted slits near the front edge of both sides, two groups
    for g, (y0, n) in enumerate(((300, 8), (520, 9))):
        d.box(f"louvre{g}", [cx + 199, y0, 385, cx + 202, y0 + 4, 410], "plastic#7d838b", soft=True, copies=[[-401, 0, 0]],
              rot=rot("x", 35, [cx + 200, y0 + 2, 397]), repeat={"n": n, "step": [0, 22, 0]})
    # --- tray rail (front bar wider than the column, side rails back along the sides)
    rail = [[cx - 232, 822, 110], [cx - 232, 822, Z1 + 40], [cx + 232, 822, Z1 + 40], [cx + 232, 822, 110]]
    d.add("rail", "sweep", "rail", path=rail, section=[22, 44], shape="rect", r=7, bend=45)
    d.add("rail-top", "sweep", "railtop", path=[[cx - 200, 845, Z1 + 40], [cx + 200, 845, Z1 + 40]], section=[22, 4], shape="rect", r=1)
    d.box("rail-post", [cx - 232, 806, 110, cx - 199, 838, 150], "rail", r=6, copies=[[431, 0, 0]])
    d.box("rail-post-f", [cx - 120, 806, Z1 - 5, cx - 100, 838, Z1 + 30], "rail", r=5, copies=[[220, 0, 0]])
    d.cyl("rail-hole", [cx - 244, 822, 260], [cx - 242, 822, 260], 9, "dark", soft=True, copies=[[0, 0, 22], [0, 0, 44], [487, 0, 0], [487, 0, 22], [487, 0, 44]])
    # --- head: collar, seam, sloped block, black glass panel
    d.box("collar", [cx - 200, 838, Z0, cx + 200, 872, Z1], "shell", r=10)
    d.box("head-seam", [cx - 198, 870, Z0 + 2, cx + 198, 876, Z1 - 2], "plastic#5d636b")
    d.add("head", "slab", "shell", plane="side",
          outline=f"M {Z0} 874 L {Z1} 874 L {Z1} {TOP_F} L {Z0} {TOP_R} Z", w=[cx - 200, cx + 200], r=22)
    t = rot("x", SLOPE, [cx, TOP_F, Z1])
    L = (Z1 - Z0) / math.cos(math.radians(SLOPE))
    zf = lambda s: Z1 - s   # distance s along the slope from the front edge (flat frame, rotated by t)
    d.box("panel", [cx - 182, TOP_F - 3, zf(L - 22), cx + 182, TOP_F + 2, zf(16)], "glass", r=5, rot=t)
    y = TOP_F + 2.5
    d.cyl("p-logo", [cx - 160, y - 1, zf(L - 45)], [cx - 160, y + 0.5, zf(L - 45)], 14, "blue", soft=True, rot=t)
    d.box("p-title", [cx - 70, y - 1, zf(L - 48), cx + 70, y, zf(L - 42)], "plastic#d8dbe0", soft=True, rot=t)
    d.box("p-digits", [cx - 150, y - 1, zf(L - 110), cx - 95, y, zf(L - 85)], "gloss#1e2125", soft=True, rot=t,
          copies=[[85, 0, 0], [180, 0, 0], [265, 0, 0]])
    d.cyl("p-btn", [cx - 150, y - 1, zf(L - 165)], [cx - 150, y + 0.2, zf(L - 165)], 16, "plastic#c9cdd2", soft=True, rot=t,
          copies=[[34, 0, 0], [85, 0, 0], [119, 0, 0], [180, 0, 0], [214, 0, 0], [265, 0, 0], [299, 0, 0],
                  [0, 0, 70], [34, 0, 70], [85, 0, 70], [119, 0, 70], [180, 0, 70], [214, 0, 70], [265, 0, 70], [299, 0, 70]])
    for i, (a0, a1, b0, b1) in enumerate(((-170, 170, L - 70, L - 67), (-170, 170, 60, 63), (-170, -167, 63, L - 70), (167, 170, 63, L - 70))):
        d.box(f"p-frame{i}", [cx + a0, y - 1, zf(b0), cx + a1, y + 0.1, zf(b1)], "plastic#e6e8eb", soft=True, rot=t)
    d.box("p-foot", [cx - 160, y - 1, zf(60), cx + 160, y, zf(56)], "plastic#8a9099", soft=True, rot=t)


def arm(d, nm, H, J, side):
    """Arm from the pivot hub H (on the outer side of the head, side = -1 left / +1 right) to the ball joint J."""
    # pivot hub on the head side: a grey block, a white disc and grey cap
    hx = H[0] - side * 30
    d.box(f"{nm}-mount", [min(hx, hx - side * 18), H[1] - 60, H[2] - 35, max(hx, hx - side * 18), H[1] + 40, H[2] + 35], "grey", r=8)
    d.cyl(f"{nm}-hub", [hx, H[1], H[2]], [H[0], H[1], H[2]], 70, "white")
    d.cyl(f"{nm}-hubcap", [H[0], H[1], H[2]], [H[0] + side * 8, H[1], H[2]], 44, "grey")
    M = [H[0] + (J[0] - H[0]) * 0.45, H[1] + (J[1] - H[1]) * 0.45, H[2] + (J[2] - H[2]) * 0.45]
    d.add(f"{nm}-lower", "bar", "arm", **{"from": H, "to": M}, section=[30, 46], r=6)
    d.add(f"{nm}-upper", "bar", "arm2", **{"from": M, "to": J}, section=[30, 46], r=6)
    # hinge plates, groove on the upper segment, yellow label on the lower
    d.add(f"{nm}-hinge", "bar", "plastic#b8bcc2", **{"from": add(M, [0, -1, 0]), "to": add(M, [(J[0] - H[0]) * .06, (J[1] - H[1]) * .06, (J[2] - H[2]) * .06])},
          section=[36, 50], r=4)
    u = [(J[i] - M[i]) for i in range(3)]
    g0 = [M[i] + u[i] * 0.18 for i in range(3)]; g1 = [M[i] + u[i] * 0.78 for i in range(3)]
    d.add(f"{nm}-groove", "bar", "black", **{"from": add(g0, [0, 0, 15]), "to": add(g1, [0, 0, 15])}, section=[3, 15], r=1.5, soft=True)
    v = [(M[i] - H[i]) for i in range(3)]
    l0 = [H[i] + v[i] * 0.25 for i in range(3)]; l1 = [H[i] + v[i] * 0.45 for i in range(3)]
    d.add(f"{nm}-label", "bar", "plastic#e8c22a", **{"from": add(l0, [0, 0, 15]), "to": add(l1, [0, 0, 15])}, section=[2, 26], r=1, soft=True)
    # ball joint, black lever handle
    d.add(f"{nm}-ball", "sphere", "chrome", at=J, d=46)
    d.cyl(f"{nm}-collar", add(J, [0, -40, 0]), add(J, [0, -10, 0]), 36, "chrome")
    tip = add(J, [side * 70, -35, 75])
    d.cyl(f"{nm}-lever", J, tip, 14, "black")
    d.add(f"{nm}-lever-grip", "bar", "black", **{"from": tip, "to": add(tip, [side * 35, -15, 45])}, section=[14, 26], r=6)


def rect_radiator(d, nm, R, J):
    """White rounded box 450 × 160 × 120 centred at R, ribs on the front face; stem down to the joint J."""
    d.cyl(f"{nm}-stem", J, [J[0], R[1] - 75, J[2]], 30, "arm2")
    d.box(f"{nm}-body", [R[0] - 225, R[1] - 80, R[2] - 60, R[0] + 225, R[1] + 80, R[2] + 60], "shell", r=48)
    d.box(f"{nm}-rib", [R[0] - 190, R[1] - 53, R[2] + 50, R[0] + 165, R[1] - 31, R[2] + 66], "white", r=10,
          copies=[[0, 42, 0], [0, 84, 0]])
    d.cyl(f"{nm}-logo", [R[0] + 197, R[1], R[2] + 52], [R[0] + 197, R[1], R[2] + 62], 36, "plastic#737b85")
    d.box(f"{nm}-logo-x", [R[0] + 195, R[1] - 12, R[2] + 61, R[0] + 199, R[1] + 12, R[2] + 63], "white", soft=True)
    d.box(f"{nm}-logo-y", [R[0] + 187, R[1] - 2, R[2] + 61, R[0] + 207, R[1] + 2, R[2] + 63], "white", soft=True)


def drum_radiator(d, nm, R, J, yaw=0):
    """White drum Ø260 × 200 centred at R (axis z, face +z turned by yaw about y); stem up from the joint J."""
    t = rot("y", yaw, R) if yaw else None
    d.cyl(f"{nm}-stem", J, [J[0], R[1] - 110, J[2]], 30, "arm2")
    d.box(f"{nm}-yoke", [R[0] - 30, R[1] - 140, R[2] - 60, R[0] + 30, R[1] - 115, R[2] + 40], "arm2", r=8, rot=t)
    d.add(f"{nm}-body", "lathe", "shell", at=[R[0], R[1], R[2] - 100], axis="z", sides=48,
          profile=[[0, 0], [112, 0], [126, 12], [130, 40], [130, 188], [124, 200], [0, 200]], rot=t)
    d.add(f"{nm}-boss", "lathe", "plastic#737b85", at=[R[0], R[1], R[2] + 99], axis="z",
          profile=[[0, 0], [26, 0], [24, 8], [0, 9]], rot=t)
    d.box(f"{nm}-boss-x", [R[0] - 2, R[1] - 14, R[2] + 107, R[0] + 2, R[1] + 14, R[2] + 109.5], "white", soft=True, rot=t)
    d.box(f"{nm}-boss-y", [R[0] - 14, R[1] - 2, R[2] + 107, R[0] + 14, R[1] + 2, R[2] + 109.5], "white", soft=True, rot=t)
    d.box(f"{nm}-mark", [R[0] - 22, R[1] + 128, R[2] + 50, R[0] + 22, R[1] + 131.5, R[2] + 80], "gloss#e8662a", soft=True, rot=t)


def cable(d, nm, pts):
    d.tube(nm, pts, 14, "cable", bend=110, soft=True)


def socket(d, nm, cx, side):
    x = cx + side * 200
    d.cyl(f"{nm}", [x, 770, 405], [x + side * 10, 770, 405], 30, "blue")
    d.cyl(f"{nm}-ring", [x, 770, 405], [x + side * 4, 770, 405], 42, "plastic#d8dbe0")
