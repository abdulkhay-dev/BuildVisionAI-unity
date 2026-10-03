"""Helpers of batch robot-1 / robot-2 (rehabilitation robots, BWS gait frames) on top of p1lib / lib.
Only used by the r_*.py generators."""
import math
from p1lib import *          # D (with p1lib's method signatures), sec, rot, rep, text, rpoly, rr_path, arc


def harness(d, cx, cz, top, hooks, vest_y=1050, mat="web", pad="vpad", accent=None, legs=True, buckle="steel",
            pre="h", vest_w=360, vest_d=250, strap_w=48):
    """Hanging body-weight-support harness: two shoulder straps from the hook points `hooks` [(x, y, z), ...]
    crossing down to a padded vest at vest_y (its top), a pelvic belt and two leg loops with pads."""
    vb, vt = vest_y - 260, vest_y
    xs = [cx - vest_w * 0.32, cx + vest_w * 0.32]
    for i, (hx, hy, hz) in enumerate(hooks):
        # from each hook: one strap straight down to its own side of the vest, one crossing to the other side
        own, other = xs[i % 2], xs[1 - i % 2] if len(hooks) == 2 else xs[i % 2]
        fz = cz + vest_d * 0.40
        d.strap(f"{pre}-down-{i}", [[hx, hy, hz], [(hx + own) / 2, (hy + vt) / 2, (hz + fz) / 2], [own, vt - 10, fz]],
                [strap_w, 4], mat, bend=80, soft=True)
        d.strap(f"{pre}-cross-{i}", [[hx, hy - 30, hz + 6], [(hx + other) / 2, (hy + vt) / 2 + 40, (hz + fz) / 2 + 8],
                                     [other * 0.6 + cx * 0.4, vt + 20, fz + 8]], [strap_w, 4], mat, bend=80, soft=True)
        d.box(f"{pre}-buckle-{i}", [own - 22, vt + 80, fz - 2 - 8 * 0, own + 22, vt + 108, fz + 10], buckle, r=3, soft=True)
    # vest: padded shell (open top), black bands around it
    d.loft(f"{pre}-vest", [sec(vb, vest_w - 30, vest_d - 20, 100, cx, cz), sec(vb + 120, vest_w, vest_d, 115, cx, cz),
                           sec(vt, vest_w - 10, vest_d - 10, 110, cx, cz)], pad, caps=False, soft=True)
    d.loft(f"{pre}-vest-in", [sec(vb + 5, vest_w - 60, vest_d - 50, 85, cx, cz), sec(vt - 5, vest_w - 40, vest_d - 40, 95, cx, cz)],
           mat, caps=False, soft=True)
    for k, y in enumerate((vb + 40, vb + 130)):
        d.loft(f"{pre}-band-{k}", [sec(y, vest_w + 8, vest_d + 8, 118, cx, cz), sec(y + 55, vest_w + 8, vest_d + 8, 118, cx, cz)],
               mat, caps=False, soft=True)
    d.box(f"{pre}-belt-buckle", [cx - 30, vb + 140, cz + vest_d / 2 + 2, cx + 30, vb + 180, cz + vest_d / 2 + 14],
          accent or buckle, r=4, soft=True)
    if legs:
        for i, s in enumerate((-1, 1)):
            x = cx + s * 80
            d.strap(f"{pre}-leg-strap-{i}", [[x + s * 40, vb + 10, cz + 60], [x + s * 20, vb - 120, cz + 70],
                                             [x, vb - 200, cz + 50]], [40, 4], mat, bend=50, soft=True)
            d.loft(f"{pre}-leg-pad-{i}", [sec(vb - 300, 150, 150, 75, x, cz + 10), sec(vb - 240, 160, 160, 80, x, cz + 10),
                                          sec(vb - 180, 150, 150, 75, x, cz + 10)], pad, caps=False, soft=True)
            d.loft(f"{pre}-leg-band-{i}", [sec(vb - 270, 158, 158, 79, x, cz + 10), sec(vb - 230, 158, 158, 79, x, cz + 10)],
                   mat, caps=False, soft=True)


def hook(d, id, at, mat="steel", drop=90):
    """Swivel hook: a short rod and a ring hanging under the point `at`."""
    x, y, z = at
    d.cyl(f"{id}-rod", [x, y, z], [x, y - drop * 0.45, z], 10, mat)
    d.tube(f"{id}-ring", [[x, y - drop * 0.45, z], [x - 16, y - drop * 0.7, z], [x, y - drop, z], [x + 16, y - drop * 0.7, z],
                          [x, y - drop * 0.45, z]], 7, mat, bend=10)
    return [x, y - drop, z]
