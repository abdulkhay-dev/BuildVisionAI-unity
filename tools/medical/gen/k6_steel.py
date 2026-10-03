"""XYF-T3 / XYF-T4 steel training ladders: sheet-steel stringers and folded treads (open risers), a platform at 600
(T3: on a white square-tube frame; T4: a closed box with two box steps toward the front), silver/blue handrails on
white posts with chrome inner tubes and black star knobs."""
import sys
from k6lib import *

NT, RISE = 5, 100
PT = (NT + 1) * RISE          # 600
RC = 1321                     # rail centre over the platform (top 1340: the lowest setting, as on the photos)


def build(id, W, DEP, PZ, steel, tread, rail, inner, front_steps):
    PW = 700
    FL = (W - PW) / 2
    TD = FL / NT
    d = D(id, [W, DEP, 1540], {"steel": steel, "tread": tread, "rail": rail, "frame": "plastic#f1f1ee", "post": "plastic#f1f1ee",
                               "knob": "plastic#1d1f22", "foot": "rubber#2a2c30"})
    S0, S1 = 30, PZ - 30           # stringer inner faces
    # stringer: zig-zag top under the treads, straight underside parallel to the pitch, rounded foot on the floor
    slope = PT / FL
    pts = [(0, 0), (0, RISE - 4)]
    for k in range(1, NT + 1):
        pts += [((k) * TD - 4 if k < NT else FL, k * RISE - 4)]
        if k < NT:
            pts += [(k * TD - 4, (k + 1) * RISE - 4)]
    pts += [(FL, PT - 4), (FL, PT - 130)]
    xb = FL - (PT - 130) / slope * 1.0
    outline = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + f" L {xb + 60:.1f} 30 Q {xb - 20:.1f} 0 {xb - 140:.1f} 0 Z"
    for nm, z0 in (("a", S0 - 8), ("b", S1)):
        d.slab(f"stringer-{nm}", "front", outline, [z0, z0 + 8], "steel", r=2, mirror="x")
    # folded sheet treads: top plate + front lip
    for k in range(1, NT + 1):
        x0, x1 = (k - 1) * TD - 12, k * TD - 4 if k < NT else FL
        d.box(f"tread{k}", [x0, k * RISE - 4, S0, x1, k * RISE, S1], "tread", r=1.5, mirror="x")
        # closed riser: the folded sheet runs down the whole rise (the photos show lit risers on the near flight)
        d.box(f"lip{k}", [x0, (k - 1) * RISE, S0, x0 + 4, k * RISE, S1], "tread", r=1, mirror="x")
    d.box("foot", [10, 0, S0 - 20, 60, 6, S1 + 20], "foot", r=2, mirror="x")
    # --- platform
    # platform: a sheet-steel box ~190 deep on a white square-tube frame (legs, bottom and top rectangles)
    DB = 190
    d.box("deck", [FL, PT - DB, 0, W - FL, PT, PZ], "steel", r=3)
    d.box("deck-top", [FL + 4, PT, 4, W - FL - 4, PT + 3, PZ - 4], "tread", r=1.5)
    for (x, z) in ((FL + 20, 20), (FL + 20, PZ - 20)):
        d.bar(f"leg{z}", [x, 0, z], [x, PT - DB, z], [40, 40], "frame", r=3, mirror="x")
    for y in (30, PT - DB - 20):
        d.bar(f"rail-x{y}", [FL + 40, y, 20], [W - FL - 40, y, 20], [40, 40], "frame", r=3, copies=[[0, 0, PZ - 40]])
        d.bar(f"rail-z{y}", [FL + 20, y, 40], [FL + 20, y, PZ - 40], [40, 40], "frame", r=3, mirror="x")
    if front_steps:
        d.box("step1", [FL, 0, PZ, W - FL, 2 * PT / 3, PZ + 220], "steel", r=3)
        d.box("step1-lip", [FL - 3, 2 * PT / 3 - 100, PZ, W - FL + 3, 2 * PT / 3, PZ + 223], "steel", r=3)
        d.box("step2", [FL, 0, PZ + 220, W - FL, PT / 3, DEP], "steel", r=3)
        d.box("step2-lip", [FL - 3, PT / 3 - 100, PZ + 220, W - FL + 3, PT / 3, DEP + 3], "steel", r=3)
        d.box("seam", [FL + 10, 2 * PT / 3 - 101, PZ + 223.5, W - FL - 10, 2 * PT / 3 - 99, PZ + 224], "rubber#7d8a98",
              soft=True, copies=[[0, -PT / 3, DEP - PZ - 220]])

    def ry(x):
        x = min(x, W - x)
        return RISE + (PT - RISE) / FL * x + (RC - PT) if x <= FL else RC

    def yb(x):  # stringer underside at x (post feet)
        x = min(x, W - x)
        return max(20, (x - (FL - (PT - 130) / slope)) * slope)

    zr = (S0 - 30, S1 + 22)
    d.tube("rail-b", [[25, ry(70) - 120, zr[0]], [70, ry(70), zr[0]], [FL, RC, zr[0]], [W - FL, RC, zr[0]],
                      [W - 70, ry(70), zr[0]], [W - 25, ry(70) - 120, zr[0]]], 38, "rail", bend=55)
    if not front_steps:
        d.tube("rail-f", [[25, ry(70) - 120, zr[1]], [70, ry(70), zr[1]], [FL, RC, zr[1]], [W - FL, RC, zr[1]],
                          [W - 70, ry(70), zr[1]], [W - 25, ry(70) - 120, zr[1]]], 38, "rail", bend=55)
    else:
        XF = FL + 30

        # front rails (photo): round the platform corner, level over the front steps, then bend down into a tall
        # post standing at the front corner of the lowest step
        ZF, YD = DEP - 40, RC - 110
        d.tube("rail-f", [[25, ry(70) - 120, zr[1]], [70, ry(70), zr[1]], [FL - 20, RC, zr[1]], [XF, RC, zr[1]],
                          [XF, RC, ZF], [XF, YD, ZF]], 38, "rail", bend=40, mirror="x")
        post(d, "post-ff", XF, ZF, PT / 3, YD, -1, inner=inner, frac=0.55, knob_side="x")
        post(d, "post-ffr", W - XF, ZF, PT / 3, YD, 1, inner=inner, frac=0.55, knob_side="x")
    xs = [150, FL - 170]          # bottom post and top-of-flight post (photos)
    for i, x in enumerate(xs):
        for side, z, out in (("b", zr[0], -1), ("f", zr[1], 1)):
            post(d, f"post-{side}{i}", x, z, yb(x), ry(x) - 30, out, inner=inner, frac=0.66, flange=False)
            post(d, f"post-{side}{i}r", W - x, z, yb(x), ry(x) - 30, out, inner=inner, frac=0.66, flange=False)
    # platform corner posts
    for z in (zr[0], zr[1]):
        out = -1 if z == zr[0] else 1
        xp = FL + 30 if (front_steps and z == zr[1]) else FL + 40
        y0 = PT if (front_steps and z == zr[1]) else PT - DB     # T4's front corner posts stand on the deck
        post(d, f"post-p{z}", xp, z, y0, RC - 30, out, inner=inner, frac=0.7, flange=y0 == PT)
        post(d, f"post-p{z}r", W - xp, z, y0, RC - 30, out, inner=inner, frac=0.7, flange=y0 == PT)
    d.save()


build("xyf-t3", 3470, 870, 870, "plastic#a6a8d4", "plastic#bccbe8", "metal#b8c8dc", "chrome", False)
build("xyf-t4", 3470, 1140, 700, "plastic#b6cbea", "plastic#bdd0ec", "plastic#7fa6d6", "metal#cfc6a0", True)
