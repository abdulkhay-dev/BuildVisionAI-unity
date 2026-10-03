"""Shared body of the round hand-rehabilitation tables XY-101C and JY-CT-II (same body, different station sets and
colours): X base on 4 braked castors, square silver lift column, 4 drawers under a round white top with a black edge,
a brushed-aluminium tower with a screen and a weight-stack slot on each face, hand stations around the edge joined to
the tower by thin cables over small pulleys."""
import math
from k9lib import *
import t4lib   # registers the 医 / 疗 glyphs of the brand (keeps lib's D methods)

CX = CZ = 650
TT = 680                      # table top (the photos show the table lowered to ~670; full lift +400 → 1540 overall)
TW = 380                      # tower width
TH = 470                      # tower height above the table


def polar(r, a):
    return CX + r * math.cos(math.radians(a)), CZ + r * math.sin(math.radians(a))


def body(d, plate, armcap, print_front=None, button=False, colmat="metal#c9cdd2", tw=TW, th=TH,
         scr=(-153, 122, 237, 69), slot=(-15, 19, 175, 75), btn=(100, 215), logo_cn=True):
    """scr = (x0, x1 from CX; bottom and top below the tower top); slot = (centre dx, y0, y1 above the table, width);
    btn = (dx, y above the table) of the blue power button."""
    # --- base: 4 rectangular arms on the diagonals, hub plate, castors with brakes
    for k, a in enumerate((45, 135, 225, 315)):
        ex, ez = polar(600, a)
        d.bar(f"arm-{k}", [CX, 150, CZ], [ex, 150, ez], [95, 60], "base", r=6)
        ex2, ez2 = polar(625, a)
        d.bar(f"arm-cap-{k}", [ex, 150, ez], [ex2, 150, ez2], [97, 62], armcap, r=6)
        cx_, cz_ = polar(585, a)
        d.caster(f"castor-{k}", [cx_, 0, cz_], 100, "plastic#f2f3f4")
        d.box(f"brake-{k}", [cx_ - 20, 70, cz_ - 20, cx_ + 20, 82, cz_ + 20], "plastic#8a8e94", r=4,
              rot=rot("y", -a, [cx_, 76, cz_]))
    d.box("hub", [CX - 170, 118, CZ - 170, CX + 170, 186, CZ + 170], "base", r=20, rot=rot("y", 45, [CX, 150, CZ]))
    # brand on the hub (photo of XY-101C: blue mark + 翔宇医疗)
    text(d, "hub-logo", "翔宇医疗" if logo_cn else "翔宇", [CX - 60, 186.6, CZ + 205], 30, "gloss#2a5fb0", face="top", along=(1, 0))
    d.decal("hub-mark", [CX - 88, 186.6, CZ + 190], [32, 32], "top", "gloss#2a5fb0")
    # --- lift column and drawer block
    d.box("column", [CX - 100, 185, CZ - 100, CX + 100, TT - 95, CZ + 100], colmat, r=6)
    d.box("column-in", [CX - 88, TT - 120, CZ - 88, CX + 88, TT - 80, CZ + 88], "metal#b9bdc2", r=4)
    for k in range(4):
        R = rot("y", 90 * k, [CX, 0, CZ])
        d.box(f"drawer-{k}", [CX - 200, TT - 92, CZ + 60, CX + 200, TT - 26, CZ + 470], "drawer", r=6, rot=R)
        d.decal(f"drawer-lbl-{k}", [CX, TT - 59, CZ + 470.6], [30, 30], "front", "plastic#d9dbdd", rot=R)
        d.decal(f"drawer-pull-{k}", [CX, TT - 85, CZ + 470.6], [120, 6], "front", "plastic#b8bcc1", rot=R)
    d.box("top-frame", [CX - 260, TT - 30, CZ - 260, CX + 260, TT - 24, CZ + 260], "plastic#6d7075", r=4)
    # --- round top: black edge band, white surface
    d.cyl("top-edge", [CX, TT - 25, CZ], [CX, TT - 1, CZ], 1300, "black", sides=96)
    d.cyl("top", [CX, TT - 4, CZ], [CX, TT + 0.5, CZ], 1297, "tabletop", sides=96)
    # --- tower: aluminium box, black rounded top-corner caps, a screen + weight-stack slot on each face
    h = tw / 2
    d.box("tower", [CX - h, TT, CZ - h, CX + h, TT + th - 20, CZ + h], "alu", r=10)
    d.box("tower-top", [CX - h + 2, TT + th - 22, CZ - h + 2, CX + h - 2, TT + th, CZ + h - 2], "alu", r=12)
    for k, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        d.box(f"tcap-{k}", [CX + sx * h - 24, TT + th - 48, CZ + sz * h - 24, CX + sx * h + 24, TT + th + 3, CZ + sz * h + 24],
              "black", r=16)   # photo: small rounded corner caps (~45 mm)
    sdx, sy0, sy1, sw = slot
    for k in range(4):
        R = rot("y", 90 * k, [CX, 0, CZ])
        zf = CZ + h
        ux0, ux1, uy0, uy1 = CX + scr[0], CX + scr[1], TT + th - scr[2], TT + th - scr[3]
        if k == 0 and print_front:
            crop_screen(d, "screen-0", "black", print_front, [ux0, uy0, ux1, uy1], zf + 2, (597, 459), (82, 158, 494, 404),
                        "alu", outer=[CX - h + 12, TT + 10, CX + h - 12, TT + th - 30], rot_=R)
        else:
            d.screen(f"screen-{k}", [ux0, uy0, zf, ux1, uy1, zf + 3], "black", bezel=4, r=2, rot=R)
        o = 6 if (k == 0 and print_front) else 0
        # weight-stack slot: black opening with silver plates and a rod; a pulley at its foot
        sc = CX + sdx
        d.box(f"slot-{k}", [sc - sw / 2, TT + sy0, zf - 1 + o, sc + sw / 2, TT + sy1, zf + 1.2 + o], "black", r=2, soft=True, rot=R)
        n = max(3, int((sy1 - sy0) * 0.45 / 17))
        d.decal(f"plates-{k}", [sc, TT + sy0 + 30, zf + 1.8 + o], [sw - 18, 10], "front", "metal#b9bec4", rot=R, repeat=rep(n, [0, 17, 0]))
        d.decal(f"rod-{k}", [sc, TT + sy0 + 30 + n * 17 + (sy1 - sy0 - 30 - n * 17) / 2, zf + 2 + o], [6, sy1 - sy0 - 40 - n * 17],
                "front", "chrome", rot=R)
        d.wheel(f"pulley-{k}", [sc, TT + 22, zf + 22], 40, "black", d2=18, axis="x", rot=R)
        d.decal(f"tlogo-{k}", [CX - h + 40, TT + th - 60, zf + 0.6 + o], [26, 14], "front", "gloss#2a5fb0", rot=R)
        if button:
            d.cyl(f"power-{k}", [CX + btn[0], TT + btn[1], zf], [CX + btn[0], TT + btn[1], zf + 5], 22, "gloss#2f86d0", rot=R)
            d.cyl(f"power-ring-{k}", [CX + btn[0], TT + btn[1], zf], [CX + btn[0], TT + btn[1], zf + 3], 30, "plastic#2a2c30", rot=R)


def cable(d, id, a, rr=470):
    """A thin black cable from a station (angle a, radius rr) to the tower foot over a small pulley block."""
    x0, z0 = polar(rr - 60, a)
    x1, z1 = polar(250, a)
    d.tube(id, [[x0, TT + 30, z0], [x1, TT + 30, z1], [x1, TT + 10, z1]], 4, "black", soft=True, bend=10)
    d.box(id + "-blk", [x1 - 22, TT, z1 - 22, x1 + 22, TT + 35, z1 + 22], "plate", r=6, rot=rot("y", -a, [x1, 0, z1]))
    d.wheel(id + "-pul", [x1, TT + 45, z1], 34, "black", d2=14, axis="x", rot=rot("y", 90 - a, [x1, 0, z1]))


# ---- hand stations (built at the origin of their own frame, then turned to angle `face`, placed at (x, z)) ----
class St:
    def __init__(s, d, id, x, z, face):
        s.d, s.id, s.x, s.z, s.face = d, id, x, z, face
        s.n0 = len(d.d["parts"])
    def done(s):
        # turn about y so the station's local +z faces outward (towards the patient at the table edge)
        R = rot("y", 90 - s.face, [s.x, 0, s.z])
        for p in s.d.d["parts"][s.n0:]:
            if "rot" in p:
                p.setdefault("rots", []).append(R)
            else:
                p["rot"] = R


def st_plate(d, id, x, z, w, dd, r=30):
    d.box(id, [x - w / 2, TT, z - dd / 2, x + w / 2, TT + 8, z + dd / 2], "plate", r=r)


def arch_path(c, y0, span, top, leg):
    """SVG path of an n-shaped stand plate in a slab plane: legs `leg` wide at c +- span/2 from y0 up, a round top
    whose outer arc peaks at `top` (centre at top - span/2)."""
    r = span / 2; ri = r - leg; yc = top - r
    return (f"M {c - r:.1f} {y0:.1f} L {c - r:.1f} {yc:.1f} Q {c - r:.1f} {top:.1f} {c:.1f} {top:.1f} Q {c + r:.1f} {top:.1f} {c + r:.1f} {yc:.1f} "
            f"L {c + r:.1f} {y0:.1f} L {c + ri:.1f} {y0:.1f} L {c + ri:.1f} {yc:.1f} Q {c + ri:.1f} {yc + ri:.1f} {c:.1f} {yc + ri:.1f} "
            f"Q {c - ri:.1f} {yc + ri:.1f} {c - ri:.1f} {yc:.1f} L {c - ri:.1f} {y0:.1f} Z")


def post_ball(d, id, x, z, face, rod, h=200, legs=False, stand=None, ball=48, post=30, ring_mat="plate"):
    """A post with a ball knob on a plate. stand: None, "arch" (a blue n-plate around the post, the post through its
    top) or "cage" (a blue disc on 4 posts of the rod colour, the knob post through it); legs=True = "cage"."""
    stand = stand or ("cage" if legs else None)
    s = St(d, id, x, z, face)
    st_plate(d, id + "-pl", x, z, 150, 160, r=50)
    if stand == "arch":
        d.slab(id + "-arch", "front", arch_path(x, TT + 8, 120, TT + h * 0.72, 22), [z - 18, z + 18], "plate", r=4)
    elif stand == "cage":
        for k, (dx, dz) in enumerate(((-45, -45), (45, -45), (45, 45), (-45, 45))):
            d.cyl(f"{id}-leg{k}", [x + dx, TT + 8, z + dz], [x + dx, TT + h * 0.62, z + dz], 22, rod)
        d.cyl(id + "-ring", [x, TT + h * 0.62, z], [x, TT + h * 0.62 + 10, z], 150, ring_mat)
    d.cyl(id + "-rod", [x, TT + 8, z], [x, TT + h, z], post, rod)
    d.cyl(id + "-neck", [x, TT + h - 5, z], [x, TT + h + ball * 0.3, z], post * 0.55, rod)
    d.sphere(id + "-ball", [x, TT + h + ball * 0.5, z], ball, rod)
    s.done()

def pegs(d, id, x, z, face, rod, n=3, h=230, hs=None, dia=36, bar_mat=None, extra=None):
    """A row of pegs (heights hs) on a plate, a bar across near their tops; extra = (dx, dz, h) one more peg."""
    hs = hs or [h - k * 25 for k in range(n)]
    s = St(d, id, x, z, face)
    st_plate(d, id + "-pl", x, z, 70 * len(hs) + 60, 150, r=45)
    x0 = x - 35 * (len(hs) - 1)
    for k, hh in enumerate(hs):
        xx = x0 + k * 70
        d.cyl(f"{id}-r{k}", [xx, TT + 8, z], [xx, TT + hh, z], dia, rod)
        d.sphere(f"{id}-t{k}", [xx, TT + hh, z], dia * 0.98, rod, radii=[dia / 2, dia * 0.2, dia / 2])
    by = TT + min(hs) - 30
    d.cyl(id + "-bar", [x0 - 30, by, z], [x0 + 70 * (len(hs) - 1) + 30, by, z], 16, bar_mat or "chrome")
    if extra:
        d.cyl(f"{id}-rx", [x + extra[0], TT + 8, z + extra[1]], [x + extra[0], TT + extra[2], z + extra[1]], dia, rod)
        d.sphere(f"{id}-tx", [x + extra[0], TT + extra[2], z + extra[1]], dia * 0.98, rod, radii=[dia / 2, dia * 0.2, dia / 2])
    s.done()

def grip_pair(d, id, x, z, face, rod):
    s = St(d, id, x, z, face)
    st_plate(d, id + "-pl", x, z, 150, 260)
    d.cyl(id + "-a", [x - 30, TT + 8, z + 40], [x - 30, TT + 280, z + 40], 44, rod)
    d.cyl(id + "-b", [x + 30, TT + 8, z - 20], [x + 30, TT + 300, z - 20], 44, rod)
    d.cyl(id + "-c", [x, TT + 8, z - 80], [x, TT + 230, z - 80], 30, rod)
    d.decal(id + "-lbl", [x - 30, TT + 230, z + 62.6], [16, 16], "front", "plastic#e6e6e6")
    s.done()


def roller_st(d, id, x, z, face, rod, ball=None, length=300, dia=64, cy=125, ends=("cap", "cap"), thin=None):
    """A roller across two blue n-shaped end stands (the roller through the round tops). ends: "cap" (a short
    rounded end cap of the roller colour) or "dome" (a knob ball beyond the stand); thin = (from dx, dia) a thinner
    second section of the roller towards +x (JY-CT-II)."""
    s = St(d, id, x, z, face)
    L = length / 2
    st_plate(d, id + "-pl", x, z, length + 80, 170, r=40)
    for k, xx in enumerate((x - L, x + L)):
        d.slab(f"{id}-stand{k}", "side", arch_path(z, TT + 8, 110, TT + cy + 55, 26), [xx - 9, xx + 9], "plate", r=3)
        d.cyl(f"{id}-boss{k}", [xx - 12, TT + cy, z], [xx + 12, TT + cy, z], dia + 24, "plate")
    if thin:
        d.cyl(id + "-roll", [x - L + 10, TT + cy, z], [x + thin[0], TT + cy, z], dia, rod)
        d.cyl(id + "-roll2", [x + thin[0], TT + cy, z], [x + L + 10, TT + cy, z], thin[1], rod)
    else:
        d.cyl(id + "-roll", [x - L + 10, TT + cy, z], [x + L - 10, TT + cy, z], dia, rod)
    for k, (e, xx, sg) in enumerate(zip(ends, (x - L, x + L), (-1, 1))):
        if e == "dome":
            d.sphere(f"{id}-k{k}", [xx + sg * 30, TT + cy, z], dia * 0.95, ball or rod, radii=[dia * 0.42, dia * 0.47, dia * 0.47])
        elif e == "cap":
            d.sphere(f"{id}-k{k}", [xx + sg * 14, TT + cy, z], dia, ball or rod, radii=[dia * 0.25, dia * 0.5, dia * 0.5])
    s.done()

def wheel_st(d, id, x, z, face, rod, wd=150, wy=110):
    """Crank wheel (photo of XY-101C): an open blue spoked wheel facing the patient (axis outward), on an upright
    blue plate; a blue lever across its face carries a black crank handle pointing at the patient; the base plate has
    a rectangular hole at its outer end."""
    s = St(d, id, x, z, face)
    pl = rpoly([(x - 80, z - 150), (x + 80, z - 150), (x + 80, z + 150), (x - 80, z + 150)], 60)
    hole = f"M {x - 38} {z + 50} L {x - 38} {z + 115} L {x + 38} {z + 115} L {x + 38} {z + 50} Z"
    d.slab(id + "-pl", "top", pl + " " + hole, [TT, TT + 8], "plate", r=2)
    zw = z - 40                                       # wheel plane
    d.slab(id + "-up", "front", f"M {x - 55} {TT + 8} L {x + 55} {TT + 8} L {x + 18} {TT + wy + 10} L {x - 18} {TT + wy + 10} Z",
           [zw - 30, zw - 16], "plate", r=3)
    R0 = wd / 2
    d.slab(id + "-rim", "front", circle(x, TT + wy, R0) + " " + circle(x, TT + wy, R0 - 14), [zw, zw + 12], "plate", r=3)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        d.bar(f"{id}-sp{k}", [x, TT + wy, zw + 6], [x + (R0 - 8) * math.cos(a), TT + wy + (R0 - 8) * math.sin(a), zw + 6],
              [16, 10], "plate", r=3)
    d.cyl(id + "-hub", [x, TT + wy, zw - 16], [x, TT + wy, zw + 22], 34, "chrome")
    a = math.radians(-35)
    ex, ey = x + 52 * math.cos(a), TT + wy + 52 * math.sin(a)
    d.bar(id + "-lev", [x, TT + wy, zw + 26], [ex, ey, zw + 26], [30, 10], "plate", r=4)
    d.cyl(id + "-bolt", [x, TT + wy, zw + 30], [x, TT + wy, zw + 36], 18, "chrome")
    d.cyl(id + "-handle", [ex, ey, zw + 30], [ex, ey, zw + 160], 34, rod)
    s.done()


def wrist_st(d, id, x, z, face, rod, piv=(140, 120), foot=-230, mid=(130, -110), cradle=True, strap="fabric#c9ccd0",
             loop=None, pad="leather#8fb4e8"):
    """Wrist / forearm lever (photo): two blue runners on the table, two blue curved arms from an inner foot (local z =
    foot) rising through `mid` (height, dz) to a pivot at (piv height, dz) near the outer end, a short leg down from
    the pivot; chrome bolts at the pivot. cradle: a padded forearm trough on the pivot (overhanging the edge) with a
    tall strap loop; loop: a black strap loop hanging from the pivot instead."""
    s = St(d, id, x, z, face)
    py, pz = TT + piv[0], z + piv[1]
    for k, xx in enumerate((x - 55, x + 55)):
        d.box(f"{id}-run{k}", [xx - 18, TT, z + foot - 30, xx + 18, TT + 7, pz + 70], "plate", r=8)
    d.box(id + "-runx", [x - 75, TT, z + foot - 30, x + 75, TT + 7, z + foot + 30], "plate", r=12)
    for k, xx in enumerate((x - 34, x + 34)):
        d.sweep(f"{id}-arm{k}", [[xx, TT + 8, z + foot], [xx, TT + mid[0], z + mid[1]], [xx, py, pz]], [12, 34], "plate",
                shape="rect", r=3, bend=140)
        d.bar(f"{id}-leg{k}", [xx, TT + 8, pz + 55], [xx, py, pz], [12, 30], "plate", r=3)
        for j, dy in enumerate((0, -40)):
            d.cyl(f"{id}-bolt{k}{j}", [xx - (12 if k == 0 else -12), py + dy, pz - j * 25], [xx + (-6 if k == 0 else 6), py + dy, pz - j * 25],
                  18, "chrome")
    d.cyl(id + "-axle", [x - 40, py, pz], [x + 40, py, pz], 22, "chrome")
    if cradle:
        cy = py + 22
        d.box(id + "-cradle", [x - 62, cy, pz - 60, x + 62, cy + 30, pz + 175], pad, r=14, puff=4)
        for k, xx in enumerate((x - 62, x + 62)):
            d.box(f"{id}-lip{k}", [xx - 10, cy + 10, pz - 50, xx + 10, cy + 62, pz + 170], pad, r=9)
        zz = pz + 95
        d.strap(id + "-strap", [[x - 70, cy + 50, zz], [x - 64, cy + 160, zz - 10], [x, cy + 180, zz - 12], [x + 64, cy + 160, zz - 10],
                                [x + 70, cy + 50, zz]], [55, 5], strap, bend=45, soft=True)
    if loop:
        d.strap(id + "-loop", [[x, py + 12, pz + 18], [x, py - 10, pz + 75], [x, py - 75, pz + 92], [x, py - 82, pz + 50],
                               [x, py - 25, pz + 22]], [24, 5], loop, bend=25, soft=True)
    s.done()


def knob_post(d, id, x, z, face, rod):
    """Short black post with a pulley disc on top (cable anchor; photo of XY-101C)."""
    s = St(d, id, x, z, face)
    d.cyl(id + "-post", [x, TT, z], [x, TT + 65, z], 34, rod)
    d.cyl(id + "-cap", [x, TT + 65, z], [x, TT + 80, z], 44, "chrome")
    d.wheel(id + "-pul", [x, TT + 95, z], 46, rod, d2=22, axis="x")
    s.done()


def oval_grip(d, id, x, z, a, y=TT + 18):
    """Black oval hand grip lying on the table at the end of a cable (pointing along angle a)."""
    R = rot("y", -a, [x, y, z])
    d.sphere(id, [x, y, z], 60, "plastic#1d1e21", radii=[42, 17, 22], rot=R)
    d.cyl(id + "-clip", [x - 42, y, z], [x - 62, y, z], 14, "chrome", rot=R)

def aframe(d, id, x, z, face, rod, strap="fabric#202124", cradle_mat=None):
    """Big A-frame forearm lever: two slanted plates up to a pivot, a forearm cradle with a strap on top."""
    s = St(d, id, x, z, face)
    st_plate(d, id + "-pl", x, z, 220, 380, r=40)
    for k, xx in enumerate((x - 70, x + 70)):
        d.slab(f"{id}-side{k}", "side",
               f"M {z - 170} {TT + 8} L {z - 120} {TT + 8} L {z + 20} {TT + 200} L {z + 150} {TT + 8} L {z + 190} {TT + 8} "
               f"L {z + 40} {TT + 250} L {z} {TT + 250} Z", [xx - 7, xx + 7], "plate", r=3)
        d.cyl(f"{id}-bolt{k}", [xx - 10, TT + 230, z + 20], [xx + 10, TT + 230, z + 20], 26, "chrome")
    d.cyl(id + "-axle", [x - 80, TT + 230, z + 20], [x + 80, TT + 230, z + 20], 18, "chrome")
    d.box(id + "-cradle", [x - 75, TT + 250, z - 40, x + 75, TT + 280, z + 200], cradle_mat or "plate", r=20)
    d.box(id + "-cradle-l", [x - 80, TT + 260, z - 40, x - 65, TT + 330, z + 200], cradle_mat or "plate", r=6)
    d.box(id + "-cradle-r", [x + 65, TT + 260, z - 40, x + 80, TT + 330, z + 200], cradle_mat or "plate", r=6)
    d.strap(id + "-strap", [[x - 78, TT + 330, z + 120], [x, TT + 380, z + 120], [x + 78, TT + 330, z + 120]], [55, 5], strap,
            bend=40, soft=True)
    d.cyl(id + "-lever", [x, TT + 230, z + 20], [x, TT + 120, z + 240], 22, rod)
    s.done()


def cradle_stool(d, id, x, z, face, rod, strap="fabric#202124", pad="plate", dome=None, knob=False):
    """Padded saddle on a blue 4-leg stand with an X brace, a strap loop over it; dome = colour of a black dome knob at
    its inner end (XY-101C)."""
    s = St(d, id, x, z, face)
    st_plate(d, id + "-pl", x, z, 200, 220)
    for k, (dx, dz) in enumerate(((-70, -70), (70, -70), (70, 70), (-70, 70))):
        d.cyl(f"{id}-leg{k}", [x + dx, TT + 8, z + dz], [x + dx * 0.7, TT + 150, z + dz * 0.7], 16, "plate")
    for k, sx in enumerate((-1, 1)):
        d.cyl(f"{id}-x{k}a", [x + sx * 68, TT + 20, z - 66], [x + sx * 52, TT + 135, z + 52], 10, "plate")
        d.cyl(f"{id}-x{k}b", [x + sx * 68, TT + 20, z + 66], [x + sx * 52, TT + 135, z - 52], 10, "plate")
    d.box(id + "-seat", [x - 90, TT + 150, z - 110, x + 90, TT + 195, z + 110], pad, r=20, puff=5)
    d.strap(id + "-strap", [[x - 92, TT + 175, z], [x - 60, TT + 260, z], [x + 60, TT + 260, z], [x + 92, TT + 175, z]],
            [70, 6], strap, bend=50, soft=True)
    if dome:
        d.sphere(id + "-dome", [x, TT + 195, z - 75], 84, dome, radii=[44, 40, 40])
    if knob:
        d.sphere(id + "-knob", [x, TT + 120, z - 120], 50, rod)
    s.done()

def forearm_pad(d, id, x, z, face, strap="fabric#202124"):
    s = St(d, id, x, z, face)
    d.box(id + "-pad", [x - 150, TT, z - 90, x + 150, TT + 85, z + 90], "plate", r=30, puff=6)
    for k, xx in enumerate((x - 70, x + 60)):
        d.strap(f"{id}-s{k}", [[xx, TT + 10, z - 92], [xx, TT + 88, z - 60], [xx, TT + 88, z + 60], [xx, TT + 10, z + 92]],
                [60, 5], strap, bend=30, soft=True)
    s.done()


def lever_st(d, id, x, z, face, rod):
    s = St(d, id, x, z, face)
    st_plate(d, id + "-pl", x, z, 110, 150)
    d.box(id + "-blk", [x - 35, TT + 8, z - 30, x + 35, TT + 70, z + 30], "metal#c9cdd2", r=6)
    d.cyl(id + "-lev", [x, TT + 60, z], [x, TT + 230, z + 60], 30, rod)
    d.sphere(id + "-end", [x, TT + 235, z + 62], 34, rod)
    s.done()
