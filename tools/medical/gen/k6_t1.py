"""XYF-T1 two-way wooden training stair."""
from k6lib import *

W, DEP = 3370, 830
d = D("xyf-t1", [W, DEP, 1550], {
    "body": "plastic#c6ae90", "tread": "plastic#abc1e8", "rail": "metal#9fbadb", "post": "plastic#f1f1ee",
    "knob": "plastic#1d1f22", "seam": "plastic#8d7a62"})
FL, NT, RISE = 1285, 4, 120
TD = FL / NT
RC = 1321          # rail centre over the platform: top 1340, the lowest setting as on the photo (range 1340-1550)
PT = (NT + 1) * RISE           # platform top 600
# --- left flight body (mirrored = right flight): beige laminate stair block
pts = ["M 0 0", f"L 0 {RISE}"]
for k in range(1, NT):
    pts += [f"L {k * TD:.1f} {k * RISE}", f"L {k * TD:.1f} {(k + 1) * RISE}"]
pts += [f"L {FL} {NT * RISE}", f"L {FL} 0 Z"]
d.slab("flight", "front", " ".join(pts), [0, DEP], "body", r=3, mirror="x")
# grey-blue anti-slip rubber on every tread and riser (L profile with a small nosing)
for k in range(1, NT + 1):
    x0 = (k - 1) * TD
    d.box(f"tread{k}", [x0 - 4, k * RISE, 6, k * TD if k < NT else FL - 2, k * RISE + 6, DEP - 6], "tread", r=2, mirror="x")
    d.box(f"riser{k}", [x0 - 4, (k - 1) * RISE + 6 if k > 1 else 4, 6, x0 + 2, k * RISE + 6, DEP - 6], "tread", r=1,
          mirror="x")
# --- platform module between the flights (its own box: seams at both ends), covered top, small label
d.box("platform", [FL + 3, 0, 0, W - FL - 3, PT, DEP], "body", r=3)
d.box("plat-top", [FL + 3, PT, 6, W - FL - 3, PT + 6, DEP - 6], "tread", r=2)
d.box("plat-riser", [FL - 3, NT * RISE + 6, 6, FL + 3, PT + 6, DEP - 6], "tread", r=1, mirror="x")
d.box("seam", [FL - 1, 0, -0.5, FL + 3, PT, DEP + 0.5], "seam", soft=True, mirror="x")
d.decal("label", [W - FL - 70, PT - 40, DEP + 0.6], [60, 22], "front", "plastic#6f6a66", soft=True)


# --- handrails both sides: sloped over the flights, level over the platform, ends turned down; white posts
def ry(x):  # rail centre height above the step nosing line (rail top 1550 over the platform)
    x = min(x, W - x)
    return RISE + (PT - RISE) / FL * x + (RC - PT) if x <= FL else RC


for side, z, out in (("f", DEP - 45, 1), ("b", 45, -1)):
    path = [[25, ry(70) - 120, z], [70, ry(70), z], [FL, RC, z], [W - FL, RC, z], [W - 70, ry(70), z],
            [W - 25, ry(70) - 120, z]]
    d.tube(f"rail-{side}", path, 38, "rail", bend=55)
    for i, (x, lvl) in enumerate(((160, RISE), (2 * TD + 160, 3 * RISE), (FL + 45, PT))):
        post(d, f"post-{side}{i}", x, z, lvl + 6, ry(x) - 30, out, inner="metal#e6e6e2", frac=0.8)
        rail_saddle(d, f"sad-{side}{i}", x, ry(x), z)
        # the mirrored post on the right flight
        post(d, f"post-{side}{i}r", W - x, z, lvl + 6, ry(x) - 30, out, inner="metal#e6e6e2", frac=0.8)
        rail_saddle(d, f"sad-{side}{i}r", W - x, ry(x), z)
d.save()
