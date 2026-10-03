from pd1_lib import *
W, D_, H = 2000, 1700, 910
d = K("triangle-ball-pool", [W, D_, H], {"red": "leather#e02020", "yel": "leather#f6d21a", "blue": "leather#1f4fb5"})
HT, TH = 600, 200


def bez(a, b, bulge, n=16):
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz)
    nx, nz = dz / L, -dx / L                       # right-hand normal of a→b
    c = (mx + nx * bulge * 2, mz + nz * bulge * 2)
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1])
            for t in [k / n for k in range(n)]]


# wall centre line: rounded triangle, apex at the left, long convex front wall, short right wall, back wall
A, B, C = (110, 780), (1900, 1600), (1700, 100)
pts = bez(A, C, 90) + bez(C, B, 0) + bez(B, A, 160)    # clockwise in (x, z) seen from above with z down → outward bulges
for _ in range(3):                                      # Chaikin: round the corners
    q = []
    for i in range(len(pts)):
        p0, p1 = pts[i], pts[(i + 1) % len(pts)]
        q += [(0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]), (0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1])]
    pts = q
# fit into the size: centre line 100 in from the bounding box
xs, zs = [p[0] for p in pts], [p[1] for p in pts]
sx, sz = (W - 2 * 100) / (max(xs) - min(xs)), (D_ - 2 * 100) / (max(zs) - min(zs))
pts = [(100 + (p[0] - min(xs)) * sx, 100 + (p[1] - min(zs)) * sz) for p in pts]
# resample by arc length into an even number of segments ~280 long
per = [0.0]
for i in range(len(pts)):
    a, b = pts[i], pts[(i + 1) % len(pts)]; per.append(per[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
N = int(round(per[-1] / 280 / 2)) * 2
def at(s):
    s %= per[-1]
    for i in range(len(pts)):
        if per[i + 1] >= s:
            a, b = pts[i], pts[(i + 1) % len(pts)]; t = (s - per[i]) / max(1e-6, per[i + 1] - per[i])
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
seg = [at(per[-1] * k / N) for k in range(N)]
cxm, czm = sum(p[0] for p in seg) / N, sum(p[1] for p in seg) / N
def hump_seg(id, a, b, mat):
    """A yellow wall segment of the back / right walls: its top a rounded hump (the photo's wavy wall top)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dz) + 24
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    x0, x1 = mx - L / 2, mx + L / 2
    out = f"M {x0:.1f} 0 L {x1:.1f} 0 L {x1:.1f} {HT - 25} Q {mx:.1f} {HT + 85} {x0:.1f} {HT - 25} Z"
    d.slab(id, "front", out, [mz - TH / 2, mz + TH / 2], mat, r=24, rot=rot("y", round(yrot_deg(dx, dz), 2), [mx, 0, mz]))


for k in range(N):
    a, b = seg[k], seg[(k + 1) % N]
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    tx, tz = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, tz)
    nx, nz = tz / L, -tx / L
    if (mx - cxm) * nx + (mz - czm) * nz < 0: nx, nz = -nx, -nz
    # photo: the right wall and the back wall (except near the left apex) are yellow with a wavy top
    if nx > 0.5 or (nz < -0.5 and mx > 650):
        hump_seg(f"w{k}", a, b, "yel")
    else:
        plan_box(d, f"w{k}", a, b, TH / 2, 0, HT, "red" if k % 2 == 0 else "yel", r=26, ext=12)


def offset(poly_, dist):
    """Offset towards the inside (towards the centroid) by dist."""
    out = []
    n = len(poly_)
    for i in range(n):
        p0, p1, p2 = poly_[i - 1], poly_[i], poly_[(i + 1) % n]
        tx, tz = p2[0] - p0[0], p2[1] - p0[1]; L = math.hypot(tx, tz) or 1
        nx, nz = -tz / L, tx / L
        if (cxm - p1[0]) * nx + (czm - p1[1]) * nz < 0: nx, nz = -nx, -nz
        out.append((p1[0] + nx * dist, p1[1] + nz * dist))
    return out


fine = [at(per[-1] * k / 72) for k in range(72)]
inner = offset(fine, TH / 2)
lin = offset(fine, TH / 2 + 16)
d.slab("liner", "top", poly(inner) + " " + poly(lin), [0, HT - 45], "blue", r=4)
fill = offset(fine, TH / 2 + 10)
d.slab("fill", "top", poly(fill), [0, 395], "plastic#2a5fb0", r=2)
# balls: a grid of 4 colours on top of the fill
def inside(x, z, P):
    c = False
    for i in range(len(P)):
        a, b = P[i - 1], P[i]
        if (a[1] > z) != (b[1] > z) and x < a[0] + (z - a[1]) * (b[0] - a[0]) / (b[1] - a[1]): c = not c
    return c
safe = offset(fine, TH / 2 + 50)
cols = ["gloss#e02a2a", "gloss#2fae4a", "gloss#f2d23a", "gloss#2a5fd0"]
SP = 78
nb = 0
for iz, z in enumerate(range(160, D_ - 100, 68)):
    xs_ = [x for x in range(100, W - 80, SP // 2) if inside(x + (SP // 2 if iz % 2 else 0), z, safe)]
    if not xs_: continue
    x0 = min(xs_) + (SP // 2 if iz % 2 else 0); x1 = max(xs_) + (SP // 2 if iz % 2 else 0)
    n_all = int((x1 - x0) // SP) + 1
    for c in range(4):
        k0 = (c + iz) % 4
        n = len(range(k0, n_all, 4))
        if n == 0: continue
        d.sphere(f"b{iz}-{c}", [x0 + k0 * SP, 420 + (iz % 2) * 10 + c * 3, z], 76, cols[c], repeat=rep(n, [4 * SP, 0, 0]))
        nb += 1
# striped soft cylinder on a two-tier round base at the back right
X, Z = 1260, 640
d.lathe("base", [X, 0, Z], [[360, 0], [360, 320], [345, 340], [0, 340]], "leather#d8962e")
d.lathe("base-top", [X, 0, Z], [[330, 330], [330, 400], [312, 418], [0, 418]], "leather#1e9a4a")
bands = ["red", "yel", "blue", "red", "yel", "blue"]     # bottom → top (photo: blue band at the top)
y = 418
for i, m in enumerate(bands):
    d.lathe(f"band{i}", [X, 0, Z], [[220, y], [220, y + 82]], m, caps=False)
    if i: d.lathe(f"line{i}", [X, 0, Z], [[223, y - 4], [224, y], [223, y + 4]], "plastic#f4f4f4", caps=False)
    y += 82
d.lathe("rim", [X, 0, Z], [[220, y - 2], [216, y + 6], [204, y + 6], [204, y - 6]], "blue", caps=False)
d.lathe("lining", [X, 0, Z], [[204, y - 6], [204, y - 260]], "red", caps=False)   # hollow: red inner wall
d.lathe("inner-floor", [X, 0, Z], [[205, y - 260], [0, y - 260]], "leather#c8903e")
d.save()
print("ball parts", nb)
