"""XYF-T2 three-way training stair: left and right flights along x, a short front flight from the platform to +z."""
from k6lib import *

W, DEP = 3400, 1400
d = D("xyf-t2", [W, DEP, 1550], {
    "body": "plastic#f2f3f5", "tread": "rubber#a3c1e2", "rail": "chrome", "post": "plastic#f1f1ee",
    "knob": "plastic#1d1f22"})
FL, NT, RISE = 1300, 4, 120
TD = FL / NT
PT = (NT + 1) * RISE            # platform top 600
PZ = 800                        # depth of the side flights and of the platform
RC = 1321                       # rail centre over the platform (top 1340, the lowest setting)
FR = 200                        # front flight: 2 treads of 300, rise 200
# --- side flights (white body, blue speckled covering on treads and risers)
pts = ["M 0 0", f"L 0 {RISE}"]
for k in range(1, NT):
    pts += [f"L {k * TD:.1f} {k * RISE}", f"L {k * TD:.1f} {(k + 1) * RISE}"]
pts += [f"L {FL} {NT * RISE}", f"L {FL} 0 Z"]
d.slab("flight", "front", " ".join(pts), [0, PZ], "body", r=3, mirror="x")
for k in range(1, NT + 1):
    x0 = (k - 1) * TD
    d.box(f"tread{k}", [x0 - 4, k * RISE, 5, k * TD if k < NT else FL, k * RISE + 6, PZ - 5], "tread", r=2, mirror="x")
    d.box(f"riser{k}", [x0 - 4, (k - 1) * RISE + 6 if k > 1 else 3, 5, x0 + 2, k * RISE + 6, PZ - 5], "tread", r=1,
          mirror="x")
# --- platform and the front flight (white), covered
d.box("platform", [FL, 0, 0, W - FL, PT, PZ], "body", r=3)
d.box("plat-top", [FL + 4, PT, 5, W - FL - 4, PT + 6, PZ + 4], "tread", r=2)
d.box("plat-riser", [FL - 3, NT * RISE + 6, 5, FL + 3, PT + 6, PZ - 5], "tread", r=1, mirror="x")
d.slab("front-flight", "side", f"M {PZ} 0 L {PZ} {2 * FR} L {PZ + 300} {2 * FR} L {PZ + 300} {FR} L {DEP} {FR} L {DEP} 0 Z",
       [FL, W - FL], "body", r=3)
# (side-plane outline: z along the first coordinate, y the second)
d.box("ff-riser0", [FL + 5, PT - FR, PZ - 4, W - FL - 5, PT + 6, PZ + 2], "tread", r=1)
d.box("ff-tread1", [FL + 5, 2 * FR, PZ - 4, W - FL - 5, 2 * FR + 6, PZ + 300], "tread", r=2)
d.box("ff-riser1", [FL + 5, FR + 6, PZ + 298, W - FL - 5, 2 * FR + 6, PZ + 304], "tread", r=1)
d.box("ff-tread2", [FL + 5, FR, PZ + 298, W - FL - 5, FR + 6, DEP - 2], "tread", r=2)
d.box("ff-riser2", [FL + 5, 3, DEP - 4, W - FL - 5, FR + 6, DEP + 2], "tread", r=1)


def ry(x):  # side-flight rail centre at x
    x = min(x, W - x)
    return RISE + (PT - RISE) / FL * x + (RC - PT) if x <= FL else RC


def fy(z):  # front-flight rail centre at z (nosing line 600 at z 800 -> 200 at z 1400)
    return PT - (z - PZ) * FR / 300 + (RC - PT)


XF = FL + 40
YD = 960                        # the front rails run level over the front flight, then drop into the front post
# back rail: slope - level over the platform (encloses its back) - slope
d.tube("rail-b", [[25, ry(70) - 120, 40], [70, ry(70), 40], [FL, RC, 40], [W - FL, RC, 40], [W - 70, ry(70), 40],
                  [W - 25, ry(70) - 120, 40]], 38, "rail", bend=55)
# front rails: up the side flight, round the platform corner, down the side of the front flight
d.tube("rail-f", [[25, ry(70) - 120, PZ - 40], [70, ry(70), PZ - 40], [FL - 20, RC, PZ - 40], [XF, RC, PZ - 40],
                  [XF, RC, DEP - 45], [XF, YD, DEP - 45]], 38, "rail",
       bend=35, mirror="x")
for i, (x, lvl) in enumerate(((160, RISE), (2 * TD + 160, 3 * RISE), (FL - 60, NT * RISE))):
    for side, z, out in (("b", 40, -1), ("f", PZ - 40, 1)):
        post(d, f"post-{side}{i}", x, z, lvl + 6, ry(x) - 30, out, frac=0.78)
        post(d, f"post-{side}{i}r", W - x, z, lvl + 6, ry(x) - 30, out, frac=0.78)
# one post at the front end of each front rail, on the bottom tread (the photo shows no middle post)
post(d, "post-ff", XF, DEP - 45, FR + 6, YD, -1, frac=0.7, knob_side="x")
post(d, "post-ffr", W - XF, DEP - 45, FR + 6, YD, 1, frac=0.7, knob_side="x")
post(d, "post-pb", W / 2, 40, PT + 6, RC - 30, -1, frac=0.78)
d.save()
