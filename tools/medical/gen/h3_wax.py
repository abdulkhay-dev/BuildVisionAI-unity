"""XYL-I, XYL-II, XYL-V paraffin wax heaters: glossy white tank, sloped mauve-grey control strip, dark lid with a
U handle, dark-brown band with triangle marks; II on a black castor frame, V on a dark-brown lift frame with bellows."""
import sys
from h3lib import *

BROWN = "plastic#4a3530"
MATS = {"shell": "gloss#f4f4f4", "panel": "plastic#cbbcbb", "brown": BROWN, "lid": "plastic#57504d",
        "disp": "gloss#2e2422", "key": "plastic#6b5d5b", "white": "gloss#fbfbfb"}


def panel_keys(d, pre, x_of, z_of, y, rotp, n_fn=3):
    """Keys on a flat panel at height y (before the panel's rotation rotp): power, +, −, function keys."""
    btn(d, pre + "pwr", [x_of(0.12), y, z_of(0.25)], 16, "top", "key", h=4, rot=rotp)
    btn(d, pre + "pm", [x_of(0.45), y, z_of(0.40)], 16, "top", "key", h=4, rot=rotp, copies=[[x_of(0.55) - x_of(0.45), 0, z_of(0.43) - z_of(0.40)]])
    btn(d, pre + "fn", [x_of(0.62), y, z_of(0.72)], 18, "top", "key", h=4, rot=rotp,
        copies=[[x_of(0.62 + 0.09 * k) - x_of(0.62), 0, z_of(0.72) - z_of(0.72)] for k in range(1, n_fn)])


def triangles(d, pre, plane, pts_list, w, mat_fill, mat_line):
    for i, (kind, pts) in enumerate(pts_list):
        if kind == "fill":
            d.slab(f"{pre}{i}", plane, P(pts), w, mat_fill, soft=True)
        else:
            inner = offset(pts, -3)
            d.slab(f"{pre}{i}", plane, P(pts) + " " + P(inner), w, mat_line, soft=True)


def xyl_i():
    W, D, H = 550, 460, 340
    d = D_("xyl-i", [W, D, H])
    # plinth + body (side-plane outline with the front slope), vertical corners rounded by r
    d.loft("plinth", [sec(0, W - 16, D - 16, 50, W / 2, D / 2), sec(26, W - 16, D - 16, 50, W / 2, D / 2)], "brown")
    zs, ys = D - 165, H - 100          # slope from (zs, H) down to (D, ys)
    d.slab("body", "side", rp([(0, 24), (D, 24), (D, ys), (zs, H), (0, H)], [12, 14, 24, 22, 26]), [0, W], "shell", r=46)
    ang = math.degrees(math.atan2(H - ys, D - zs))
    rp_ = rot("x", ang, [0, H, zs])
    L = math.hypot(D - zs, H - ys)
    # panel lying flat at y = H before the turn, from u = 10 to L - 12 down the slope (z = zs + u)
    d.box("panel", [38, H - 3, zs + 10, W - 38, H + 0.8, zs + L - 12], "panel", r=3, rot=rp_)
    zf = lambda t: zs + 10 + (L - 22) * t
    xf = lambda t: 38 + (W - 76) * t
    # review: the photo's display sits at the upper middle-left, the power key left of it lower down,
    # +/- under the display, three function keys lower right, a small brand logo at the right
    d.box("disp", [xf(0.18), H, zf(0.07), xf(0.55), H + 1.6, zf(0.33)], "disp", r=2, rot=rp_)
    btn(d, "k-pwr", [xf(0.07), H + 0.8, zf(0.45)], 16, "top", "key", h=4, rot=rp_)
    btn(d, "k-pm", [xf(0.36), H + 0.8, zf(0.57)], 16, "top", "key", h=4, rot=rp_, copies=[[xf(0.43) - xf(0.36), 0, 0]])
    btn(d, "k-fn", [xf(0.62), H + 0.8, zf(0.74)], 17, "top", "key", h=4, rot=rp_,
        copies=[[xf(0.62 + 0.09 * k) - xf(0.62), 0, 0] for k in (1, 2)])
    d.box("ptitle", [xf(0.6), H, zf(0.25), xf(0.8), H + 1.0, zf(0.25) + 8], "plastic#8f7c7a", soft=True, rot=rp_)
    d.box("ptext", [xf(0.02), H, zf(0.84), xf(0.36), H + 1.0, zf(0.84) + 4], "plastic#8f7c7a", soft=True, rot=rp_,
          copies=[[0, 0, 11]])
    d.box("ptext2", [xf(0.45), H, zf(0.9), xf(0.78), H + 1.0, zf(0.9) + 4], "plastic#8f7c7a", soft=True, rot=rp_)
    d.box("plogo", [xf(0.86), H, zf(0.52), xf(0.88), H + 1.4, zf(0.52) + 12], "brown", r=1, soft=True, rot=rp_)
    d.box("plogo-t", [xf(0.895), H, zf(0.54), xf(0.96), H + 1.2, zf(0.54) + 6], "brown", soft=True, rot=rp_)
    # lid inset on the top behind the slope + chrome U handle running front to back
    d.slab("lid", "top", rrp(64, 34, W - 64, zs - 12, 48), [H - 2, H + 2.5], "lid", r=2)
    d.sweep("handle", [[W / 2, H + 2, 52], [W / 2, H + 48, 66], [W / 2, H + 48, zs - 52], [W / 2, H + 2, zs - 38]],
            [26, 11], "chrome", bend=26, r=4)
    # front: dark-brown logo
    logo(d, "logo", [100, 192, D], 58, "front", blue=BROWN, word_mat=BROWN)
    # right side: band near the bottom, white label "XYL-I" at its front end, triangle marks
    y0, y1, sk = 52, 96, 16
    xr = [W, W + 1.6]
    d.slab("band", "side", P([(62, y0), (238, y0), (238 - sk, y1), (62 - sk, y1)]), xr, "brown", soft=True)
    lab = [(246, y0), (374, y0), (374 - sk, y1), (246 - sk, y1)]
    d.slab("label", "side", P(lab), xr, "white", soft=True)
    d.slab("label-line", "side", P(lab) + " " + P(offset(lab, -3)), [W + 1.6, W + 2.4], "brown", soft=True)
    text3(d, "model", "XYL-I", [W + 2.6, y0 + 9, 352], 26, "brown", u=(0, 0, -1), face="right", gap=0.3)
    triangles(d, "tri-", "side", [
        ("line", [(400, y1), (382, y1), (391, y0 + 8)]), ("fill", [(381, y1 - 18), (372, y1 - 18), (377, y0 + 6)]),
        ("line", [(40, y1 + 6), (22, y1 + 6), (31, y1 - 14)]), ("fill", [(52, y1 + 8), (43, y1 + 8), (48, y1 - 4)])],
              [W + 0.2, W + 2.0], "brown", "brown")
    return d


def tank(d, x0, x1, z0, z1, y0, y1, slope_len, slope_drop, lid, liftkey=False):
    """Long tank with the control slope at its left end (x0). Returns the rot of the panel and the slope geometry."""
    xs, ys = x0 + slope_len, y1 - slope_drop
    d.slab("body", "front", rp([(x0, y0), (x1, y0), (x1, y1), (xs, y1), (x0, ys)], [14, 14, 26, 22, 26]), [z0, z1],
           "shell", r=42)
    ang = math.degrees(math.atan2(slope_drop, slope_len))
    rp_ = rot("z", ang, [xs, y1, 0])
    L = math.hypot(slope_len, slope_drop)
    # flat at y1 before the turn: u down the slope -> x = xs - u
    d.box("panel", [xs - L + 12, y1 - 3, z0 + 22, xs - 10, y1 + 0.8, z1 - 22], "panel", r=3, rot=rp_)
    d.box("disp", [xs - 70, y1, z1 - 200, xs - 22, y1 + 1.6, z1 - 40], "disp", r=2, rot=rp_)
    xf = lambda t: xs - 22 - (L - 44) * t      # t across the slope (0 at the top edge)
    zf = lambda t: z1 - 40 - (z1 - z0 - 80) * t
    btn(d, "k-pwr", [xf(0.25), y1 + 0.8, zf(0.05)], 16, "top", "key", h=4, rot=rp_)
    btn(d, "k-pm", [xf(0.55), y1 + 0.8, zf(0.30)], 16, "top", "key", h=4, rot=rp_, copies=[[0, 0, -34]])
    btn(d, "k-fn", [xf(0.58), y1 + 0.8, zf(0.52)], 18, "top", "key", h=4, rot=rp_, copies=[[0, 0, -40], [0, 0, -80]])
    d.box("ptext", [xf(0.95), y1, zf(0.05) - 200, xf(0.95) + 6, y1 + 1.0, zf(0.05)], "plastic#8f7c7a", soft=True,
          rot=rp_, copies=[[14, 0, 0]])
    d.box("plogo", [xf(0.2) - 10, y1, zf(0.95), xf(0.2) + 10, y1 + 1.2, zf(0.95) + 18], "brown", r=2, rot=rp_, soft=True)
    if liftkey:
        d.box("liftkey", [xf(0.85) - 20, y1, zf(1.0) - 4, xf(0.35) + 0, y1 + 3, zf(1.0) + 30], "plastic#f2eeee", r=14, rot=rp_)
        btn(d, "liftkey-b", [xf(0.48), y1 + 3, zf(1.0) + 13], 16, "top", "key", h=4, rot=rp_, copies=[[-34, 0, 0]])
    # lid inset + U handle along x
    lx0, lz0, lx1, lz1 = lid
    d.slab("lid", "top", rrp(lx0, lz0, lx1, lz1, 45), [y1 - 2, y1 + 2.5], "lid", r=2)
    cx, cz = (lx0 + lx1) / 2, (lz0 + lz1) / 2
    return rp_, cx, cz


def xyl_ii():
    W, D, H = 900, 420, 560
    d = D_("xyl-ii", [W, D, H])
    y0 = 125
    tank(d, 0, W, 0, D, y0, H, 190, 110, (285, 55, 705, 365))
    d.sweep("handle", [[400, H + 2, 210], [412, H + 46, 210], [578, H + 46, 210], [590, H + 2, 210]], [24, 16],
            "plastic#2b2b2b", bend=20, r=5)
    d.box("handle-top", [418, H + 50, 202, 572, H + 56, 218], "chrome", r=3)
    d.box("recess", [770, H - 1, 18, 880, H + 0.6, 34], "plastic#d9d9d9", r=6, soft=True)
    logo(d, "logo", [-0.0, 330, 120], 40, "left", blue="plastic#7a6f6c", word_mat="plastic#7a6f6c")
    # front band near the bottom with triangle marks at both ends
    b0, b1, sk = 166, 200, 14
    zr = [D, D + 1.6]
    d.slab("band", "front", P([(350, b0), (875, b0), (875 + sk, b1), (350 + sk, b1)]), zr, "brown", soft=True)
    triangles(d, "tri-", "front", [
        # review: photo — left end ▽▼▽ (pointing down), right end △▲ (pointing up)
        ("line", [(300, b1 - 4), (312, b1 - 4), (306, b1 - 14)]), ("fill", [(314, b1 - 4), (326, b1 - 4), (320, b1 - 15)]),
        ("line", [(326, b1 + 2), (346, b1 + 2), (336, b0 + 2)]),
        ("line", [(884, b0 + 2), (906, b0 + 2), (895, b1 + 4)]), ("fill", [(908, b0 + 2), (920, b0 + 2), (914, b0 + 13)])],
              [D + 0.2, D + 2.0], "brown", "brown")
    # black castor frame + motor box, 4 grey castors
    fy0, fy1 = 82, y0
    d.box("rail", [28, fy0, 360, W - 28, fy1, 392], "plastic#2a2626", r=4, copies=[[0, 0, -332]])
    d.box("end", [28, fy0, 28, 64, fy1, 392], "plastic#2a2626", r=4, copies=[[W - 92, 0, 0]])
    d.box("motor", [380, 62, 150, 560, fy0, 330], "plastic#2a2626", r=6)
    casters(d, "castor", [(60, 60), (60, 360), (W - 60, 60), (W - 60, 360)], 76, "rubber#8c9196")
    return d


def xyl_v():
    W, D, H = 850, 450, 750
    d = D_("xyl-v", [W, D, H])
    y0 = 285
    tank(d, 0, W, 15, D - 15, y0, H, 185, 110, (280, 70, 690, 380), liftkey=True)
    d.sweep("handle", [[395, H + 2, 225], [407, H + 46, 225], [563, H + 46, 225], [575, H + 2, 225]], [26, 16],
            "plastic#5a5452", bend=20, r=5)
    d.box("recess", [740, H - 1, 32, 830, H + 0.6, 48], "plastic#d9d9d9", r=6, soft=True)
    logo(d, "logo", [0, 560, 135], 46, "left", blue="plastic#5d4a46", word_mat="plastic#5d4a46")
    # front band: "Liftable" label then brown fill to the right end, triangle marks at the left end
    b0, b1, sk = y0 + 14, y0 + 56, 16
    z = D - 15
    zr = [z, z + 1.6]
    lab = [(290, b0), (540, b0), (540 + sk, b1), (290 + sk, b1)]
    d.slab("label", "front", P(lab), zr, "white", soft=True)
    d.slab("label-line", "front", P(lab) + " " + P(offset(lab, -3)), [z + 1.6, z + 2.4], "brown", soft=True)
    d.slab("band", "front", P([(548, b0), (W - 22, b0), (W - 22, b1), (548 + sk, b1)]), zr, "brown", soft=True)
    text3(d, "model", "LIFTABLE", [330, b0 + 11, z + 2.6], 22, "brown", face="front", gap=0.3)
    triangles(d, "tri-", "front", [
        ("fill", [(258, b0 + 4), (276, b0 + 4), (267 + 6, b1 - 4)]), ("line", [(238, b0 + 4), (262, b0 + 4), (256, b1 - 2)])],
              [z + 0.2, z + 2.0], "brown", "brown")
    # lift: dark-brown U frame (rails + right column), black bellows, castors
    fb = "plastic#4a3e3a"
    d.box("rail", [20, 80, D - 75, W - 20, 140, D - 15], fb, r=6, copies=[[0, 0, -(D - 90)]])
    # review: the photo's column is a narrow block (~110) between the rails at the right end, behind the front rail;
    # the bellows are 7 deep rounded pleats from just above the floor plate to the tank, between the rails
    d.box("column", [W - 140, 80, 70, W - 22, y0 + 2, D - 70], fb, r=8)
    d.box("bellows-plate", [60, 84, 78, W - 140, 96, D - 78], "plastic#1a1a1a", r=4)
    d.box("bellows-core", [80, 96, 100, W - 150, y0, D - 100], "plastic#0e0e0e", r=8)
    d.box("pleat", [62, 102, 76, W - 142, 120, D - 76], "plastic#262626", r=9, repeat=rep(7, [0, 26, 0]))
    casters(d, "castor", [(55, 45), (55, D - 45), (W - 55, 45), (W - 55, D - 45)], 76, "rubber#8c9196")
    return d


def D_(id, size):
    return D(id, size, dict(MATS))


if __name__ == "__main__":
    for i in (sys.argv[1:] or ["xyl-i", "xyl-ii", "xyl-v"]):
        go({"xyl-i": xyl_i, "xyl-ii": xyl_ii, "xyl-v": xyl_v}[i]())
