"""XYZL-1 four-person standing frame: a wooden top with a bay notch in the middle of each side, blue padded armrests
along the notch edges, per bay two white posts with a blue padded U hip sling and a blue knee pad, white floor tubes
radiating out with black caps."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 1300, 1300, 1050
d = D("xyzl-1", [W, DP, H], {"frame": "plastic#eeeeec", "wood": "plastic#d49d72", "edge": "plastic#e6c08a", "pad": "leather#3aa0d8",
                             "sling": "leather#3aa2dc", "seam": "leather#2a86c0", "black": "rubber#1a1b1d"})
C = [W / 2, 0, DP / 2]
HT, NU, NW = 450, 215, 230      # top half size, notch half width, notch bottom (distance from centre)
YW0, YW1 = 985, 1010            # wood
# wood top: square with a notch in each side (built as one outline, corners rounded)
pts = []
for face in ("+z", "-x", "-z", "+x"):          # chained: each face's last corner is the next face's +u end
    g = G(d, "", C, face)
    for u, w in ((NU, HT), (NU, NW), (-NU, NW), (-NU, HT), (-HT, HT)):
        q = g.p([u, 0, w]); pts.append((q[0], q[2]))
out = rpoly(pts, 22)
d.slab("top", "top", out, [YW0, YW1], "wood", r=4)
d.slab("top-edge", "top", out, [YW0 - 4, YW0 + 1], "edge", r=1)
for k, face in enumerate(("+z", "+x", "-z", "-x")):
    g = G(d, f"b{k}-", C, face)
    # armrests along both notch edges, white supports, black end caps
    for s in (-1, 1):
        ua = s * (NU + 38)
        g.box(f"arm{s}", [ua - 36, YW1 - 2, NW + 30, ua + 36, H, 645], "pad", r=18, puff=3)
        g.box(f"armsup{s}", [ua - 15, YW0 - 30, HT - 20, ua + 15, YW0, 600], "frame", r=3)
        g.box(f"armcap{s}", [ua - 15, YW0 - 40, 600, ua + 15, YW0, 630], "black", r=3)
    # posts at the notch corners
    for s in (-1, 1):
        g.box(f"post{s}", [s * 200 - 15, 30, NW + 10, s * 200 + 15, YW0, NW + 40], "frame", r=3)
        g.box(f"floor{s}", [s * 200 - 15, 0, 20, s * 200 + 15, 30, 630], "frame", r=3)
        g.box(f"fcap{s}", [s * 200 - 19, 0, 625, s * 200 + 19, 36, 650], "black", r=3)
        g.box(f"clamp{s}", [s * 200 - 20, 640, NW + 5, s * 200 + 20, 670, NW + 45], "frame", r=3)
    g.box("xbar-lo", [-200, 70, NW + 12, 200, 95, NW + 38], "frame", r=3)
    g.box("xbar-hi", [-200, YW0 - 40, NW + 12, 200, YW0 - 15, NW + 38], "frame", r=3)
    g.box("xbar-kn", [-185, 330, NW + 14, 185, 350, NW + 36], "frame", r=3)
    # knee pad (faces out), on two short brackets
    g.box("knee", [-165, 330, NW + 75, 165, 690, NW + 130], "pad", r=22, puff=5)
    g.box("knee-br", [-120, 470, NW + 40, -90, 500, NW + 76], "frame", r=3, copies=None)
    g.box("knee-br2", [90, 470, NW + 40, 120, 500, NW + 76], "frame", r=3)
    # hip sling (photo: soft fabric): a wide band hanging from the two post tops in a U loop out of the bay, sagging
    # ~190 at its outer part down to just above the knee pad, the top edge leaning out; a fold line along its top third
    # Built from 14 straight band pieces (a wide `strap` shades badly because its normals point along its width):
    # each piece is a front-plane slab drawn along +x as a sheared quad (vertical ends, top and bottom edges following
    # the sag), then turned about y onto its chord; a folded cuff (thicker, top 70 mm) along the top edge.
    A, B0, Bw, YA, SAG, HB, N = 196, NW + 45, 235, 900, 160, 230, 14

    def pt(a, off):
        u, w = -A * math.cos(a), B0 + Bw * math.sin(a)
        nu, nw = -Bw * math.cos(a), A * math.sin(a)
        L = math.hypot(nu, nw) or 1
        return [u + nu / L * off, YA - SAG * math.sin(a) ** 1.4, w + nw / L * off]

    for j in range(N):
        a0, a1 = math.pi * j / N, math.pi * (j + 1) / N
        for part, off, y0, y1, th in (("sling", 0, -HB / 2, HB / 2, 9), ("cuff", 9, HB / 2 - 70, HB / 2 + 3, 9)):
            p0, p1 = g.p(pt(a0, off)), g.p(pt(a1, off))
            dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
            hl = math.hypot(dx, dz) + 6
            c = [(p0[i] + p1[i]) / 2 for i in range(3)]
            h = dy / 2
            q = [(c[0] - hl / 2, c[1] + y0 - h), (c[0] + hl / 2, c[1] + y0 + h), (c[0] + hl / 2, c[1] + y1 + h),
                 (c[0] - hl / 2, c[1] + y1 - h)]
            outl = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in q) + " Z"
            d.slab(g.i(f"{part}{j}"), "front", outl, [c[2] - th / 2, c[2] + th / 2], "sling", r=2.5,
                   rot=rot("y", round(math.degrees(math.atan2(-dz, dx)), 1), c))
    for s in (-1, 1):
        g.box(f"strap{s}", [s * 190 - 30, 880, NW + 42, s * 190 + 30, YW0 - 40, NW + 50], "sling", r=3)
d.save()
