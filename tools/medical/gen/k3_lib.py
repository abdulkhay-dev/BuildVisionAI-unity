"""Helpers of batch kinesio-3 (shared by the k3_*.py generators only)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from p1lib import *   # D (+ bar/lathe/... methods), text, rpoly, rotx, sec, rep, rot


def sq(d, id, a, b, s=50, mat="frame", **kw):
    """Square steel tube a → b."""
    return d.bar(id, a, b, [s, s], mat, r=4, **kw)


class G:
    """A group drawn in a local frame (u right, y up, w towards its front) placed at `o` facing `face`
    (+z, -z, +x, -x). Only right-angle turns, so boxes stay boxes."""
    def __init__(s, d, pre, o, face="+z"):
        s.d, s.pre, s.o, s.face = d, pre, o, face

    def p(s, q):
        u, y, w = q
        ox, oy, oz = s.o
        if s.face == "+z": return [ox + u, oy + y, oz + w]
        if s.face == "-z": return [ox - u, oy + y, oz - w]
        if s.face == "-x": return [ox - w, oy + y, oz + u]
        if s.face == "+x": return [ox + w, oy + y, oz - u]
        raise ValueError(s.face)

    def bx(s, b):
        a, c = s.p(b[:3]), s.p(b[3:])
        return [min(a[0], c[0]), min(a[1], c[1]), min(a[2], c[2]), max(a[0], c[0]), max(a[1], c[1]), max(a[2], c[2])]

    def fc(s, f):
        """local face → world face"""
        order = {"+z": ["front", "right", "back", "left"], "-x": ["left", "front", "right", "back"],
                 "-z": ["back", "left", "front", "right"], "+x": ["right", "back", "left", "front"]}[s.face]
        loc = ["front", "right", "back", "left"]
        return order[loc.index(f)] if f in loc else f

    def ax(s, a):
        if a == "y" or s.face in ("+z", "-z"): return a
        return {"x": "z", "z": "x"}[a]

    def i(s, id): return f"{s.pre}{id}"

    def box(s, id, b, mat, **kw): return s.d.box(s.i(id), s.bx(b), mat, **kw)
    def cyl(s, id, a, b, dd, mat, **kw): return s.d.cyl(s.i(id), s.p(a), s.p(b), dd, mat, **kw)
    def bar(s, id, a, b, sc, mat, **kw): return s.d.bar(s.i(id), s.p(a), s.p(b), sc, mat, **kw)
    def sq(s, id, a, b, sz=50, mat="frame", **kw): return s.d.bar(s.i(id), s.p(a), s.p(b), [sz, sz], mat, r=4, **kw)
    def tube(s, id, path, dd, mat, **kw): return s.d.tube(s.i(id), [s.p(q) for q in path], dd, mat, **kw)
    def strap(s, id, path, sc, mat, **kw): return s.d.strap(s.i(id), [s.p(q) for q in path], sc, mat, **kw)
    def sphere(s, id, at, dd, mat, **kw): return s.d.sphere(s.i(id), s.p(at), dd, mat, **kw)
    def decal(s, id, at, size, face, mat, **kw): return s.d.add(s.i(id), "decal", mat, at=s.p(at), size=size, face=s.fc(face), **kw)
    def wheel(s, id, at, dd, d2, mat, axis="x", **kw): return s.d.add(s.i(id), "wheel", mat, at=s.p(at), d=dd, d2=d2, axis=s.ax(axis), **kw)
    def lathe(s, id, at, prof, mat, axis="y", **kw): return s.d.add(s.i(id), "lathe", mat, at=s.p(at), profile=prof, axis=s.ax(axis), **kw)


def ring(cx, cy, cz, rx, ry, plane="xy", n=16):
    """closed ellipse polyline"""
    pts = []
    for k in range(n + 1):
        a = 2 * math.pi * k / n
        if plane == "xy": pts.append([cx + rx * math.cos(a), cy + ry * math.sin(a), cz])
        elif plane == "zy": pts.append([cx, cy + ry * math.sin(a), cz + rx * math.cos(a)])
        else: pts.append([cx + rx * math.cos(a), cy, cz + ry * math.sin(a)])
    return pts


def pulley_unit(d, pre, o, face="+z", W=630, Dp=200, H=1800, ring_mat="plastic#1c3d8f", stack="plastic#1f9e94",
                cuffs=False, pedals=False, top_label=True, base_h=170, stack_h=180, ring_y=1250, frame="frame", cuff_y=None):
    """Twin-column pulley weight unit (XY-12 type) in a local frame: u 0..W, w 0..Dp (front at Dp), y 0..H.
    Top cap with a blue label, per column two silver guide rods, white ropes, a hand ring, a white U bracket holding
    a teal disc weight stack, a white base box; optional black ankle cuffs on the ropes and black pedals in front."""
    g = G(d, pre, o, face)
    wc = Dp * 0.5
    # top cap
    g.box("cap", [0, H - 45, 0, W, H, Dp], frame, r=6)
    if top_label:
        g.decal("label", [W * 0.42, H - 22, Dp + 0.6], [W * 0.42, 16], "front", "gloss#2a62c8", soft=True)
        g.decal("logo", [W * 0.88, H - 22, Dp + 0.6], [40, 14], "front", "gloss#2a62c8", soft=True)
    # base: two boxes joined by a centre plate, black feet
    cols = [W * 0.25, W * 0.75]
    bw = W * 0.5 - 30
    for k, cx in enumerate(cols):
        g.box(f"base{k}", [cx - bw / 2, 15, 10, cx + bw / 2, base_h, Dp - 5], frame, r=5)
        g.box(f"slot{k}", [cx - bw / 2 + 25, 40, Dp - 4.5, cx + bw / 2 - 25, base_h - 50, Dp - 3], "plastic#bfc4c9", r=3)
        g.box(f"foot{k}", [cx - bw / 2 + 5, 0, 20, cx - bw / 2 + 35, 15, 60], "rubber", copies=[g_step(g, [bw - 40, 0, 0]), g_step(g, [0, 0, Dp - 90]), g_step(g, [bw - 40, 0, Dp - 90])])
        # guide rods
        for j, du in enumerate((-bw / 2 + 22, bw / 2 - 22)):
            g.cyl(f"rod{k}{j}", [cx + du, base_h, wc], [cx + du, H - 45, wc], 22, "metal#c4c8cc")
        # white U bracket round the stack, its top bar
        sy0, sy1 = base_h, base_h + stack_h
        for j, du in enumerate((-bw / 2 + 40, bw / 2 - 40)):
            g.box(f"brk{k}{j}", [cx + du - 14, sy0, wc - 25, cx + du + 14, sy1 + 60, wc + 25], frame, r=3)
        # (review) black rubber stoppers on the base top at the front corners (photo xy-12)
        g.box(f"stop{k}", [cx - bw / 2 + 12, base_h, Dp - 62, cx - bw / 2 + 48, base_h + 26, Dp - 22], "rubber#1e1f21", r=4,
              copies=[g_step(g, [bw - 60, 0, 0])])
        g.box(f"brkt{k}", [cx - bw / 2 + 26, sy1 + 40, wc - 28, cx + bw / 2 - 26, sy1 + 70, wc + 28], frame, r=4)
        # weight stack: discs with dark gaps, top plate, centre stem
        nd = 6
        dh = stack_h / nd
        g.cyl(f"stack{k}", [cx, sy0 + 2, wc], [cx, sy0 + dh - 3, wc], 170, stack, repeat={"n": nd, "step": g_step(g, [0, dh, 0])})
        g.cyl(f"stackc{k}", [cx, sy0, wc], [cx, sy1, wc], 150, "plastic#155f5a")
        g.cyl(f"stem{k}", [cx, sy1, wc], [cx, sy1 + 40, wc], 26, "chrome")
        # ropes: two white ropes per column from the cap to the bracket / stack
        for j, du in enumerate((-22, 22)):
            g.cyl(f"rope{k}{j}", [cx + du, sy1 + 70, wc + 10], [cx + du, H - 50, wc + 10], 6, "plastic#f4f4f0", soft=True)
        g.cyl(f"pul{k}", [cx - 40, H - 75, wc], [cx + 40, H - 75, wc], 40, "plastic#8d9298")
        # hand ring hanging on a rope in front of the column
        g.cyl(f"hrope{k}", [cx, H - 60, wc + 40], [cx, ring_y + 45, wc + 40], 6, "plastic#f4f4f0", soft=True)
        g.tube(f"hring{k}", [[cx + 70 * math.cos(a), ring_y + 38 * math.sin(a), wc + 40] for a in
                              [2 * math.pi * t / 16 for t in range(17)]], 14, ring_mat, soft=True)
        if cuffs:
            cy = cuff_y or ring_y - 450
            g.box(f"cuff{k}", [cx - 75, cy - 70, wc + 20, cx + 75, cy + 70, wc + 80], "fabric#2b2e33", r=18, soft=True)
            g.decal(f"cuffb{k}", [cx, cy, wc + 80.6], [150, 14], "front", "plastic#55595f", soft=True)
    # centre plate between the bases
    g.box("mid", [W / 2 - 30, 15, Dp * 0.3, W / 2 + 30, base_h + 120, Dp * 0.7], frame, r=4)
    if pedals:
        for k, cx in enumerate(cols):
            g.box(f"pedal{k}", [cx - 110, 0, Dp + 140, cx + 110, 32, Dp + 290], "rubber#26282b", r=10)
            g.box(f"pedalt{k}", [cx - 100, 32, Dp + 150, cx + 100, 36, Dp + 280], "rubber#1c1d1f", r=4)
            # (review) the black foot strap folded over each pedal (photo xy-12)
            g.strap(f"pstrap{k}", [[cx - 105, 34, Dp + 230], [cx - 95, 62, Dp + 225], [cx + 95, 62, Dp + 225], [cx + 105, 34, Dp + 230]],
                    [120, 6], "fabric#202226", bend=25, roll=90, soft=True)
            g.tube(f"prope{k}", [[cx, 60, Dp - 5], [cx, 40, Dp + 60], [cx, 26, Dp + 150]], 6, "plastic#9a9ea3", bend=30, soft=True)
    return g


def g_step(g, v):
    """a step vector in the group's frame turned to the world"""
    a = g.p([0, 0, 0]); b = g.p(v)
    return [b[0] - a[0], b[1] - a[1], b[2] - a[2]]


def net(d, id, c, r_top, r_bot, h, n=12, rows=5, white=0.45, d_=6, pw=1.0, sag=0.0):
    """Basketball net: diamond mesh of 2 x n helical strands hanging from a ring centred at c (top centre).
    (review) pw > 1 keeps the net full near the rim and gathers it towards the bottom; sag drops every other row a
    little so the knots do not lie on perfect circles (a looser, hand-knotted look)."""
    k = 0
    for sgn in (1, -1):
        for i in range(n):
            pts = []
            for j in range(rows + 1):
                t = j / rows
                r = r_top + (r_bot - r_top) * t ** pw
                a = 2 * math.pi * (i + sgn * 0.5 * j) / n
                dy = sag * h / rows * (((i * 7 + j * 3) % 5) / 4.0 - 0.5) if 0 < j < rows else 0
                pts.append([c[0] + r * math.cos(a), c[1] - h * t + dy, c[2] + r * math.sin(a)])
            nw = max(1, int(round(rows * white)))
            d.tube(f"{id}w{k}", pts[:nw + 1], d_, "plastic#f2f2f0", soft=True)
            d.tube(f"{id}r{k}", pts[nw:], d_, "plastic#d22a2a", soft=True)
            k += 1


def board_outline(B, T, sag, th, n=10):
    """Side-plane (z, y) outline of a board running from bottom-centre B to top-centre T (points (z, y)), bowed
    `sag` mm towards its front (+z side normal), `th` thick (behind the centreline)."""
    bz, by = B; tz, ty = T
    L = math.hypot(tz - bz, ty - by)
    ux, uy = (tz - bz) / L, (ty - by) / L
    nx, ny = uy, -ux            # normal pointing to the front (+z) for a board leaning back
    if nx < 0: nx, ny = -nx, -ny
    front, back = [], []
    for k in range(n + 1):
        t = k / n
        s = sag * 4 * t * (1 - t)
        cz, cy = bz + (tz - bz) * t + nx * s, by + (ty - by) * t + ny * s
        front.append((cz, cy)); back.append((cz - nx * th, cy - ny * th))
    pts = front + back[::-1]
    return "M " + " L ".join(f"{z:.1f} {y:.1f}" for z, y in pts) + " Z", (nx, ny), (ux, uy)


def straightener(d, pre, ox, oz, x0=0, W=720, Dd=1280, top=1900, bottom_y=640, board_z=(700, 240), loop=True,
                 board="leather#8fc2ea", plate_w=None, back=None):
    """Chest-and-back straightener (XY-10): light-blue padded board bowed to the front, leaning back on white tube
    A-frames that stand on a yellow wooden floor plate; optional white handle loop above the board."""
    BZb, BZt = board_z
    B, T = (oz + BZb, bottom_y), (oz + BZt, top)
    out, nrm, up = board_outline(B, T, 45, 60)
    bx0, bx1 = ox + x0 + W / 2 - 235, ox + x0 + W / 2 + 235
    d.slab(f"{pre}board", "side", out, [bx0, bx1], board, r=22)
    if back:
        bo, _, _ = board_outline((B[0] - nrm[0] * 58, B[1] - nrm[1] * 58), (T[0] - nrm[0] * 58, T[1] - nrm[1] * 58), 45, 6)
        d.slab(f"{pre}back", "side", bo, [bx0 + 6, bx1 - 6], back, r=3)
    # bolts on the board sides near the bottom
    for k, x in enumerate((bx0 + 40, bx1 - 40)):
        d.sphere(f"{pre}bolt{k}", [x, B[1] + up[1] * 70 + nrm[1] * 2, B[0] + up[0] * 70 + nrm[0] * 2], 22, "metal#9fa6ad")
    # floor plate
    pw = plate_w or W
    P0, P1 = oz + Dd - 600, oz + Dd - 5
    d.box(f"{pre}plate", [ox + x0 + (W - pw) / 2 + 5, 32, P0, ox + x0 + (W + pw) / 2 - 5, 58, P1], "plastic#e7a845", r=8)
    d.box(f"{pre}plate-e", [ox + x0 + (W - pw) / 2 + 3, 30, P0 - 2, ox + x0 + (W + pw) / 2 - 3, 50, P1 + 2], "plastic#f1ede4", r=8)
    # white tube frame: floor rails, uprights and diagonals to the board's bottom, cross tube under the board
    for k, x in enumerate((bx0 + 25, bx1 - 25)):
        d.cyl(f"{pre}rail{k}", [x, 14, P0 - 120], [x, 14, P1 - 30], 25, "frame")
        d.cyl(f"{pre}foot{k}", [x, 0, P0 - 110], [x, 10, P0 - 110], 22, "rubber")
        d.cyl(f"{pre}footf{k}", [x, 0, P1 - 40], [x, 10, P1 - 40], 22, "rubber")
        jb = [x, B[1] + up[1] * 40 - nrm[1] * 65, B[0] + up[0] * 40 - nrm[0] * 65]
        # (review) vertical post under the board's bottom edge; the diagonal runs from the plate's front part up and
        # back to a point outboard of the board, joined to the post top by a short stub (photos xy-10 / xy-11)
        so = -70 if k == 0 else 70
        jt = [x + so, jb[1], jb[2] - 70]
        d.cyl(f"{pre}post{k}", [x, 14, jb[2]], jb, 25, "frame")
        d.tube(f"{pre}diag{k}", [[x, 14, P0 + 430], jt, [x, jb[1], jb[2]]], 25, "frame", bend=30)
    d.cyl(f"{pre}cross", [bx0 + 25, B[1] + up[1] * 40 - nrm[1] * 65, B[0] + up[0] * 40 - nrm[0] * 65],
          [bx1 - 25, B[1] + up[1] * 40 - nrm[1] * 65, B[0] + up[0] * 40 - nrm[0] * 65], 25, "frame")
    if loop:
        # rectangular handle loop rising out of the board's top, an inner grip bar
        tb = [T[0] - nrm[0] * 30, T[1] - nrm[1] * 30]
        def at(s, dz=0): return [tb[0] + up[0] * s - nrm[0] * dz, tb[1] + up[1] * s - nrm[1] * dz]
        xa, xb = ox + x0 + W / 2 - 170, ox + x0 + W / 2 + 170
        # (review) the loop is a hook bracket: it rises ~110 out of the board's top, then bends back almost level
        # (photo: a flat white rectangle with one inner bar standing back from the top)
        a0, a1 = at(-120), at(110)
        a2 = [a1[0] - 190, a1[1] + 60]
        d.tube(f"{pre}loop", [[xa, a0[1], a0[0]], [xa, a1[1], a1[0]], [xa, a2[1], a2[0]], [xb, a2[1], a2[0]],
                              [xb, a1[1], a1[0]], [xb, a0[1], a0[0]]], 25, "frame", bend=30)
        g = [a1[0] - 95, a1[1] + 30]
        d.cyl(f"{pre}grip", [xa, g[1], g[0]], [xb, g[1], g[0]], 22, "frame")
    return B, T, nrm, up


def wheel_unit(g, cu, cy, y_top, y_bot, wheel_d=700, spokes=0, tray=None, rods_w=-60, box_w=0):
    """Shoulder wheel on a sliding carriage in group g's frame (front = +w): two chrome rods (at w = rods_w) between
    y_bot and y_top, a white box (front face at w = box_w + 120) with a grey/blue hub, a white ring wheel behind the
    box with a black handle; optional forearm tray to the right ('r') or left ('l')."""
    for k, du in enumerate((-60, 60)):
        g.cyl(f"rod{k}", [cu + du, y_bot, rods_w], [cu + du, y_top, rods_w], 30, "chrome")
    g.box("carr-t", [cu - 110, y_top - 50, rods_w - 25, cu + 110, y_top, rods_w + 25], "frame", r=4)
    g.box("carr-b", [cu - 110, y_bot, rods_w - 25, cu + 110, y_bot + 50, rods_w + 25], "frame", r=4)
    g.box("box", [cu - 110, cy - 140, box_w, cu + 110, cy + 130, box_w + 120], "frame", r=6)
    g.cyl("hub", [cu, cy, box_w + 120], [cu, cy, box_w + 150], 150, "plastic#c9ced4")
    g.cyl("hub2", [cu, cy, box_w + 150], [cu, cy, box_w + 175], 100, "plastic#4568a6")
    g.cyl("shaft", [cu, cy, box_w + 175], [cu, cy, box_w + 215], 30, "chrome")
    if wheel_d:
        R = wheel_d / 2
        wz = rods_w - 50
        g.tube("wheel", [[cu + R * math.cos(2 * math.pi * k / 32), cy + R * math.sin(2 * math.pi * k / 32), wz] for k in range(33)],
               30, "frame")
        g.cyl("whub", [cu, cy, wz - 20], [cu, cy, box_w], 60, "chrome")
        for k in range(spokes):
            a = 2 * math.pi * k / spokes + 0.4
            g.bar(f"spoke{k}", [cu, cy, wz], [cu + R * math.cos(a), cy + R * math.sin(a), wz], [40, 14], "frame", r=4)
        g.cyl("whandle", [cu - R + 10, cy - 60, wz], [cu - R + 10, cy - 60, wz + 110], 26, "chrome")
        g.cyl("whandle-g", [cu - R + 10, cy - 60, wz + 60], [cu - R + 10, cy - 60, wz + 120], 34, "plastic#1d1e20")
    if tray:
        s = 1 if tray == "r" else -1
        y = cy - 170
        g.cyl("tbar", [cu, y, box_w + 90], [cu + s * 420, y, box_w + 90], 32, "chrome")
        g.box("tray", [cu + s * 180 - 0, y + 15, box_w + 30, cu + s * 400, y + 40, box_w + 160], "plastic#9da4ab", r=20) \
            if s > 0 else g.box("tray", [cu - 400, y + 15, box_w + 30, cu - 180, y + 40, box_w + 160], "plastic#9da4ab", r=20)
        g.box("tgrip", [cu + s * 150 - 15, y + 30, box_w + 80, cu + s * 150 + 15, y + 190, box_w + 110], "plastic#5f7aa6", r=8)
        g.box("tcap", [cu + s * 420 - 20, y - 20, box_w + 70, cu + s * 420 + 20, y + 20, box_w + 110], "plastic#1d1e20", r=6)
        g.sphere("tknob", [cu + s * 200, y - 40, box_w + 140], 40, "plastic#1d1e20")


def wrist_unit(g, cu, cy, y_top, y_bot, knob="l", bar=None):
    """Wrist / forearm exerciser box on two chrome rods with a black knob handle (or a wooden bar through it)."""
    for k, du in enumerate((-60, 60)):
        g.cyl(f"rod{k}", [cu + du, y_bot, -40], [cu + du, y_top, -40], 26, "chrome")
    g.box("box", [cu - 100, cy - 130, -10, cu + 100, cy + 130, 100], "frame", r=6)
    g.cyl("hub", [cu, cy, 100], [cu, cy, 125], 110, "plastic#b9bfc5")
    g.cyl("hub2", [cu, cy, 125], [cu, cy, 140], 70, "plastic#4a4e54")
    if bar:
        g.cyl("bar", [cu - bar, cy, 160], [cu + bar, cy, 160], 40, "wood#d9b27c")
        g.cyl("barc", [cu - 40, cy, 160], [cu + 40, cy, 160], 120, "metal#8e959c")
    else:
        s = -1 if knob == "l" else 1
        g.cyl("lever", [cu, cy, 140], [cu + s * 150, cy, 150], 14, "chrome")
        g.sphere("knob", [cu + s * 150, cy, 150], 36, "plastic#1d1e20")
    g.box("dial", [cu - 50, cy + 70, 100, cu + 50, cy + 100, 104], "plastic#d7dade", r=3)


def finger_ladder(g, u, y0, y1, w=0, n=None):
    """Red / green finger ladder strip: alternating coloured teeth on a white board."""
    g.box("flad-b", [u - 60, y0, w - 30, u + 60, y1, w], "frame", r=4)
    n = n or int((y1 - y0) / 34)
    step = (y1 - y0 - 20) / n
    for k in range(n):
        y = y0 + 10 + k * step
        m = "gloss#d3262c" if (k // 8) % 2 == 0 else "gloss#1f9a4a"
        g.box(f"flad-t{k}", [u - 55, y, w, u + 55, y + step * 0.62, w + 60], m, r=4)
        m2 = "gloss#1f9a4a" if (k // 8) % 2 == 0 else "gloss#d3262c"
        g.box(f"flad-s{k}", [u + 10, y, w + 40, u + 55, y + step * 0.62, w + 75], m2, r=4)


def wall_bars(g, u0, u1, y0, y1, w=0, n=10, post=60, rung=32):
    """White wall-bar ladder: two square posts with round rungs."""
    g.sq("wb-l", [u0, 0, w], [u0, y1, w], post)
    g.sq("wb-r", [u1, 0, w], [u1, y1, w], post)
    step = (y1 - y0) / (n - 1)
    g.cyl("wb-rung", [u0 + post / 2, y0, w], [u1 - post / 2, y0, w], rung, "frame",
          repeat={"n": n, "step": g_step(g, [0, step, 0])})


def turn_y(d, start, deg, about):
    """Turn every part added since index `start` about the vertical axis through `about` (+deg turns z towards x)."""
    r = {"axis": "y", "deg": deg, "about": about}
    for p in d.d["parts"][start:]:
        if "rot" in p:
            p["rots"] = p.get("rots", []) + [r]
        else:
            p["rot"] = r


def cage(d, pre, x0, x1, z0, z1, H, S=60, rings=(), caps=True, feet=True, posts_h=None, base=0):
    """Box frame of white square tubes: 4 corner posts (centres x0/x1, z0/z1), top and bottom rings, extra rings at
    the heights in `rings` (y or (y, faces) with faces a string of f/b/l/r)."""
    ph = posts_h or {}
    for k, (x, z) in enumerate(((x0, z0), (x1, z0), (x0, z1), (x1, z1))):
        sq(d, f"{pre}post{k}", [x, base, z], [x, ph.get(k, H), z], S)
        if caps:
            d.box(f"{pre}pcap{k}", [x - S / 2, ph.get(k, H), z - S / 2, x + S / 2, ph.get(k, H) + 3, z + S / 2], "plastic#2a2b2d")
    for j, rg in enumerate([(base + S / 2, "fblr"), (H - S / 2, "fblr")] + [r if isinstance(r, tuple) else (r, "fblr") for r in rings]):
        y, faces = rg
        if "f" in faces: sq(d, f"{pre}r{j}f", [x0, y, z1], [x1, y, z1], S - 10 if j > 1 else S)
        if "b" in faces: sq(d, f"{pre}r{j}b", [x0, y, z0], [x1, y, z0], S - 10 if j > 1 else S)
        if "l" in faces: sq(d, f"{pre}r{j}l", [x0, y, z0], [x0, y, z1], S - 10 if j > 1 else S)
        if "r" in faces: sq(d, f"{pre}r{j}r", [x1, y, z0], [x1, y, z1], S - 10 if j > 1 else S)
    if feet:
        d.box(f"{pre}feet", [x0 - 40, 0, z0 - 40, x0 + 40, 5, z0 + 40], "plastic#d9dbdd",
              copies=[[x1 - x0, 0, 0], [0, 0, z1 - z0], [x1 - x0, 0, z1 - z0]])


def bbox(d):
    """rough bounding box of points named in the parts (for checking the size)"""
    xs, ys, zs = [], [], []
    def add(p):
        xs.append(p[0]); ys.append(p[1]); zs.append(p[2])
    for p in d.d["parts"]:
        if "rot" in p: continue
        if "box" in p: add(p["box"][:3]); add(p["box"][3:])
        for k in ("from", "to", "at"):
            if k in p: add(p[k])
        for q in p.get("path", []): add(q)
    return [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]


def gallows(d, pre, x_post, z, y0, y_top, x_tip, ring_y=1150, n=2, ring_mat="plastic#1f3f9a", gap=260, tip=60):
    """Pulley ring exerciser: an upright on a frame post, a horizontal arm with a diagonal brace, pulleys and ropes
    down to hand rings."""
    sq(d, f"{pre}up", [x_post, y0, z], [x_post, y_top, z], 50)
    sq(d, f"{pre}arm", [x_post, y_top - 25, z], [x_tip, y_top - 25, z], 50)
    s = 1 if x_tip > x_post else -1
    sq(d, f"{pre}brace", [x_post, y_top - 330, z], [x_post + s * 300, y_top - 25, z], 40)
    for k in range(n):
        x = x_tip - s * (tip + k * gap)
        d.add(f"{pre}pul{k}", "wheel", "plastic#c9cdd2", at=[x, y_top - 110, z], d=80, d2=24, axis="z")
        d.box(f"{pre}fork{k}", [x - 12, y_top - 110, z - 18, x + 12, y_top - 50, z + 18], "chrome", r=3)
        d.cyl(f"{pre}rope{k}", [x + 40, y_top - 110, z], [x + 40, ring_y + 55, z], 6, "plastic#f2f2ee", soft=True)
        d.cyl(f"{pre}rope2{k}", [x - 40, y_top - 110, z], [x - 40, y_top - 700 - 200 * k, z], 6, "plastic#f2f2ee", soft=True)
        d.tube(f"{pre}ring{k}", ring(x + 40, ring_y, z, 48, 48, "xy", 16), 16, ring_mat, soft=True)


def peg_rack(d, pre, x, z0, z1, y0, y1, n=7, side=1):
    """Green shoulder-lifting peg rack hung on wall bars: two green uprights with black-tipped pegs (side = +1: pegs
    to +x) and a grey cross bar."""
    for k, z in enumerate((z0, z1)):
        d.box(f"{pre}up{k}", [min(x, x + side * 50), y0, z - 25, max(x, x + side * 50), y1, z + 25], "gloss#2fae48", r=4)
        for j in range(n):
            y = y0 + 60 + j * (y1 - y0 - 120) / (n - 1)
            zz = z + (-1 if k == 0 else 1) * 0
            d.cyl(f"{pre}peg{k}{j}", [x + side * 50, y, zz], [x + side * 230, y, zz], 22, "gloss#2fae48")
            d.sphere(f"{pre}tip{k}{j}", [x + side * 235, y, zz], 34, "plastic#1d1e20")
        d.box(f"{pre}hook{k}", [min(x, x - side * 40), y1 - 60, z - 22, max(x, x - side * 40), y1 - 20, z + 22], "gloss#2fae48", r=3)
    d.cyl(f"{pre}bar", [x + side * 140, (y0 + y1) / 2, z0 - 120], [x + side * 140, (y0 + y1) / 2, z1 + 120], 36, "metal#6f757b")
