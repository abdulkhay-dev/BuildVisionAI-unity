"""kinesio-5: xyc-t1 (white step modules + platform + ramp with blue-grey anti-slip tops) and
xyc-t2 (four nesting light-wood step boxes laid out as a staircase)."""
from k5lib import *


def slot(d, id, at, face, w=110, h=30, mat="plastic#1b1b1d", rim=None):
    """Oval hand slot: a dark rounded inset (proud by 1 mm) on a face; at = centre on the face plane."""
    x, y, z = at
    if face == "front":
        b = [x - w / 2, y - h / 2, z - 2, x + w / 2, y + h / 2, z + 1]
    elif face == "left":
        b = [x - 1, y - h / 2, z - w / 2, x + 2, y + h / 2, z + w / 2]
    else:  # right
        b = [x - 2, y - h / 2, z - w / 2, x + 1, y + h / 2, z + w / 2]
    if rim:
        g = 7
        rb = [b[0] - (g if face != "front" else g), b[1] - g, b[2] - (g if face != "front" else 0),
              b[3] + (g if face != "front" else g), b[4] + g, b[5] + (g if face != "front" else 0)]
        if face == "front":
            rb = [b[0] - g, b[1] - g, z - 1.5, b[3] + g, b[4] + g, z + 0.5]
        elif face == "left":
            rb = [x - 0.5, b[1] - g, b[2] - g, x + 1.5, b[4] + g, b[5] + g]
        else:
            rb = [x - 1.5, b[1] - g, b[2] - g, x + 0.5, b[4] + g, b[5] + g]
        d.box(id + "-rim", rb, rim, r=min(h / 2 + g, 12), soft=True)
    d.box(id, b, mat, r=min(h / 2, 12), soft=True)


# ---------------- xyc-t1 ----------------
W, D_, H = 3030, 850, 350
d = D("xyc-t1", [W, D_, H], {"box": "plastic#f1f2f4", "mat": "rubber#86a5d6", "trim": "metal#c4c8cd",
                              "dark": "plastic#55595f", "foot": "rubber#3a3c40"})
# boxes from the left: three nesting steps (pulled out of the platform box), the platform, the ramp
steps = [  # x0, x1, height, z inset (nested boxes are a little narrower)
    (0, 380, 95, 45), (330, 710, 180, 30), (660, 1040, 265, 15), (990, 2130, 350, 0)]
for i, (x0, x1, h, ins) in enumerate(steps):
    z0, z1 = ins, D_ - ins
    d.box(f"box{i}", [x0, 8, z0, x1, h - 14, z1], "box", r=6)
    d.box(f"trim{i}", [x0, h - 16, z0, x1, h - 2, z1], "trim", r=3)
    d.box(f"mat{i}", [x0 + 22, h - 4, z0 + 22, x1 - 22, h, z1 - 22], "mat", r=3)
    d.box(f"plinth{i}", [x0 + 10, 0, z0 + 10, x1 - 10, 10, z1 - 10], "box", r=3)
    # carrying slot on the box's left end (exposed above the next lower box) and the front face
    yl = (h + (steps[i - 1][2] if i else 0)) / 2 if i else h * 0.55
    slot(d, f"slot-l{i}", [x0, yl, D_ / 2], "left", w=110, h=22, rim="trim", mat="dark")
d.box("trim-front-seam", [2128, 20, 0, 2134, 345, D_], "trim", r=2)
# ramp: wedge from the platform top down to the floor at the right end
RX0, RX1 = 2134, W
ramp = poly([(RX0, 0), (RX1, 0), (RX1, 6), (RX0, H - 2)])
d.slab("ramp", "front", ramp, [0, D_], "box", r=4)
import math
ang = math.degrees(math.atan2(H - 8, RX1 - RX0))
L = math.hypot(H - 8, RX1 - RX0)
d.box("ramp-mat", [RX0 + 20, H - 6, 22, RX0 + L - 40, H - 2, D_ - 22], "mat", r=3,
      rot=rot("z", -ang, [RX0, H - 6, 0]))
d.box("ramp-trim", [RX0, H - 10, 0, RX0 + L - 10, H - 2, 18], "trim", r=3,
      rot=rot("z", -ang, [RX0, H - 6, 0]), copies=[[0, 0, D_ - 18]])
d.box("ramp-trim-lo", [RX0, 0, 0, RX1, 12, 4], "trim", copies=[[0, 0, D_ - 4]], soft=True)
for k, xs in enumerate((2450, 2700)):
    yy = (H - 8) * (RX1 - xs) / (RX1 - RX0) * 0.55
    slot(d, f"slot-r{k}", [xs, yy, D_], "front", w=80, h=20, rim="trim", mat="dark")
# (the platform front face is plain on the photo: no slot)
d.save()

# ---------------- xyc-t2 ----------------
# nesting boxes: sizes from the photo's nested block (h 400/310/215/125, w 600/570/535/495), staircase toward +z
d = D("xyc-t2", [600, 1200, 400], {"wood": "plastic#e2b57a", "top": "plastic#ecc995", "edge": "plastic#cf9f62",
                                   "dark": "plastic#1d1a18"})
boxes = [(600, 330, 400, 0), (568, 310, 310, 300), (536, 290, 215, 600), (500, 280, 125, 920)]
for i, (w, dz, h, zf) in enumerate(boxes):
    x0, x1 = (600 - w) / 2, (600 + w) / 2
    z1 = zf + dz if i == 0 else zf + dz - 20 if i < 3 else 1200
    z0 = z1 - dz
    if i == 0:
        d.box(f"box{i}", [x0, 0, z0, x1, h - 16, z1], "wood", r=5)
    else:
        # open-bottom box: front and back panels, end panels with the bottom cut out between two feet (photo)
        t = 18
        d.box(f"box{i}", [x0, 0, z1 - t, x1, h - 16, z1], "wood", r=5)
        d.box(f"back{i}", [x0, 0, z0, x1, h - 16, z0 + t], "wood", r=4)
        nh = min(45, h * 0.3)
        end = poly([(z0, 0), (z0 + 55, 0), (z0 + 55, nh), (z1 - 55, nh), (z1 - 55, 0), (z1, 0), (z1, h - 16), (z0, h - 16)])
        d.slab(f"end{i}", "side", end, [x0, x0 + t], "wood", r=3, copies=[[w - t, 0, 0]])
        d.box(f"inside{i}", [x0 + t, nh - 2, z0 + t, x1 - t, nh, z1 - t], "plastic#8a6a44", soft=True)
    d.box(f"lid{i}", [x0, h - 18, z0, x1, h, z1], "top", r=5)
    d.box(f"edge{i}", [x0 + 2, 0, z1 - 2, x1 - 2, 4, z1 + 0.5], "edge", soft=True)
    yn = boxes[i + 1][2] if i < 3 else 0
    if i > 0:  # the biggest box has hand slots only on its ends (photo), the others on their fronts
        slot(d, f"slot{i}", [300, (h + yn) / 2 if i < 3 else h * 0.5, z1], "front", w=86, h=24)
    if i == 0:
        slot(d, "slot-side", [600, 300, z0 + dz / 2], "right", w=86, h=24)
        slot(d, "slot-side2", [0, 300, z0 + dz / 2], "left", w=86, h=24)
d.save()
