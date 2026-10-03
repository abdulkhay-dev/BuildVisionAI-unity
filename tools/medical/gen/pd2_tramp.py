# XYRT-15 trampoline with handrail and XYRT-16 trampoline: blue padded round frame cover, black mat, 6 short legs
# with rubber feet; XYRT-15 adds a white two-post handrail with a black foam top bar at the back.
import math
from pd2_lib import *


def trampoline(id, dia, top, pad_h, leg_mat, foot_d, blue, pleats=0, thin=False):
    R = dia / 2
    d = Design(id, [dia, dia, 1000 if id == "xyrt-15" else top], {
        "pad": f"leather#{blue}", "mat": "fabric#1b1c1e", "leg": leg_mat, "foot": "rubber#18191b",
        "post": "plastic#f2f2f0", "foam": "leather#1e1f21", "knob": "plastic#1c1d1f", "ring": "black#2a2b2d"})
    c = [R, 0, R]
    ri = R - 125                                   # inner edge of the cover
    # padded cover: flat-topped ring with a rounded outer edge draping down
    prof = [[ri, top - 18], [ri + 6, top - 4], [ri + 30, top], [R - 40, top], [R - 10, top - 10], [R, top - 34],
            [R, top - pad_h + 10], [R - 8, top - pad_h], [R - 30, top - pad_h + 4], [ri + 20, top - 26], [ri, top - 18]]
    if thin:   # XYRT-15: a thin vinyl band sloping down to a short hanging skirt (not a fat pad)
        prof = [[ri, top - 10], [ri + 14, top], [R - 70, top - 12], [R - 24, top - 26], [R - 4, top - 46], [R, top - pad_h],
                [R - 6, top - pad_h], [R - 9, top - 48], [R - 26, top - 32], [R - 70, top - 18], [ri + 14, top - 6],
                [ri, top - 10]]
    d.lathe("cover", c, prof[::-1], "pad", sides=64, caps=False if thin else None)
    # the jumping mat inside, a little lower than the cover
    d.lathe("mat", [R, top - 22, R], [[0, 0], [ri + 10, 0], [ri + 10, 6], [0, 6]], "mat", sides=64)
    d.lathe("frame", [R, top - pad_h - 14, R], [[R - 34, 0], [R - 12, 0], [R - 12, 22], [R - 34, 22], [R - 34, 0]], "ring",
            sides=64)
    # wrinkles of the vinyl skirt (the XYRT-15 cover is gathered)
    for k in range(pleats):
        d.box(f"pleat{k}", [2 * R - 4, top - pad_h + 2, R - 3, 2 * R + 2, top - 44, R + 3], "pad", r=2, soft=True,
              rot=rot("y", 360 * k / pleats + 4, [R, 0, R]))
    # 6 legs with rubber feet
    rl = R - 70
    for k in range(6):
        a = math.radians(30 + 60 * k)
        x, z = R + rl * math.cos(a), R + rl * math.sin(a)
        d.cyl(f"leg{k}", [x, 30, z], [x, top - pad_h, z], 30, "leg")
        d.lathe(f"foot{k}", [x, 0, z], [[0, 0], [foot_d / 2, 0], [foot_d / 2, 8], [foot_d / 2 - 3, 44], [14, 50], [0, 50]],
                "foot")
    return d, R


# XYRT-16: no handrail, light silver legs; height 330 instead of the printed 230: the photo's legs (~240 visible
# under a ~65 cover) clearly do not fit 230
d, R = trampoline("xyrt-16", 960, 330, 64, "metal#d9dcdf", 44, "3a8fd8")
d.save()

# XYRT-15: taller black legs, handrail at the back (z = 0 side)
d, R = trampoline("xyrt-15", 970, 380, 82, "black#1e1f21", 44, "2f8ad6", pleats=90, thin=True)
ang = 64                                            # posts at +-48 deg from the back
YB = 980
for nm, s in (("l", -1), ("r", 1)):
    a = math.radians(-90 + s * ang)
    x, z = R + (R + 24) * math.cos(a), R + (R + 24) * math.sin(a)     # outside the skirt
    xi, zi = R + (R - 26) * math.cos(a), R + (R - 26) * math.sin(a)
    d.cyl(f"post-{nm}", [x, 262, z], [x, YB - 60, z], 34, "post")
    d.box(f"post-clamp-{nm}", [x - 22, 250, z - 22, x + 22, 290, z + 22], "knob", r=6)
    d.cyl(f"post-arm-{nm}", [xi, 280, zi], [x, 280, z], 26, "knob")      # bracket from the frame ring under the skirt
    d.lathe(f"knob-{nm}", [x + s * 17, YB - 98, z], [[0, 0], [6, 0], [6, 10], [15, 12], [15, 26], [0, 28]], "knob",
            axis="x", rot=rot("y", 180, [x + s * 17, YB - 98, z]) if s < 0 else None)
    if nm == "l":
        xl, zl = x, z
    else:
        xr, zr = x, z
d.tube("bar", [[xl, YB - 70, zl], [xl, YB, zl], [xr, YB, zr], [xr, YB - 70, zr]], 40, "foam", bend=60)
d.save()
