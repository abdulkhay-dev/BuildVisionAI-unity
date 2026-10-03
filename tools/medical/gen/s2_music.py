"""music-training-device: glossy orange rounded cube with white pads over the top edges, dark-red giraffe spots,
on a black plinth with arched cut-outs."""
import math
from s2lib import *

W = Dp = 500
H, B, R = 520, 130, 80          # height, plinth height, edge radius of the cube
d = D("music-training-device", [W, Dp, H], {
    "orange": "gloss#f4a01e", "white": "gloss#e9ebee", "base": "gloss#1c1d20", "inner": "black#0d0e10",
    "spot": "gloss#b03a28"})
# --- plinth: four arched walls and round corner posts
def arch(a0, a1, w=230, h=115, y0=8, y1=B):
    c = (a0 + a1) / 2
    pts = [(a0, y0), (c - w / 2, y0)]
    for k in range(1, 16):
        t = math.pi * k / 16
        pts.append((c - w / 2 * math.cos(t), y0 + h * math.sin(t)))
    pts += [(c + w / 2, y0), (a1, y0), (a1, y1), (a0, y1)]
    return pts_path(pts)
d.slab("plinth-f", "front", arch(R, W - R), [Dp - R, Dp], "base", r=6)
d.slab("plinth-b", "front", arch(R, W - R), [0, R], "base", r=6)
d.slab("plinth-l", "side", arch(R, Dp - R), [0, R], "base", r=6)
d.slab("plinth-r", "side", arch(R, Dp - R), [W - R, W], "base", r=6)
d.cyl("plinth-c", [R, 8, R], [R, B, R], 2 * R, "base", copies=[[W - 2 * R, 0, 0], [0, 0, Dp - 2 * R], [W - 2 * R, 0, Dp - 2 * R]])
d.box("plinth-in", [R, 8, R, W - R, B - 2, Dp - R], "inner")
d.cyl("speaker", [W / 2, 60, Dp - R - 1], [W / 2, 60, Dp - R + 1], 130, "black#202226", copies=[[0, 0, -(Dp - 2 * R) - 0]])
d.cyl("speaker-s", [R - 1, 60, Dp / 2], [R + 1, 60, Dp / 2], 130, "black#202226", copies=[[W - 2 * R, 0, 0]])
d.cyl("foot", [R - 10, 0, R - 10], [R - 10, 8, R - 10], 40, "rubber", copies=[[W - 2 * R + 20, 0, 0], [0, 0, Dp - 2 * R + 20], [W - 2 * R + 20, 0, Dp - 2 * R + 20]])
# --- orange cube: straight sides from the plinth, rounded top edge (loft sections on a quarter circle)
secs = [sec(B, W, Dp, R, W / 2, Dp / 2)]
for th in (0, 25, 45, 62, 76, 86, 90):
    t = math.radians(th)
    ins = R * (1 - math.cos(t))
    secs.append(sec(H - R + R * math.sin(t), W - 2 * ins, Dp - 2 * ins, max(R - ins, 1), W / 2, Dp / 2))
d.loft("cube", secs, "orange")
# --- white pads over the middle of each top edge (an extrusion of the cube's edge profile, 1.5 mm proud)
o, ext_top, ext_side = 1.5, 150, 120
def pad_secs(a0, a1, rc):
    """Sections along the pad; at both ends the pad's lower (side) and inner (top) edges pull back on a quarter
    circle of radius rc, so its corners are round as on the photo."""
    out, ends = [], []
    for t in (0, 1.5, 5, 10, 17, 25, 33, 40):
        t = t * rc / 40
        ends.append((t, rc - math.sqrt(max(rc * rc - (rc - t) ** 2, 0))))
    seq = [(a0 + t, c) for t, c in ends] + [(a1 - t, c) for t, c in reversed(ends)]
    for a, c in seq:
        z0 = Dp - (ext_top + 68) + c        # inner edge on the top = z0 + 68
        y0 = H - (ext_side + 68) + c        # lower edge on the side = y0 + 68
        z1, y1 = Dp + o, H + o
        out.append({"at": a, "w": z1 - z0, "d": y1 - y0, "r": R + o, "cx": (y0 + y1) / 2, "cz": (z0 + z1) / 2})
    return out
d.add("pad-f", "loft", "white", axis="x", sections=pad_secs(120, 380, 42))
d.add("pad-b", "loft", "white", axis="x", sections=[dict(s, cz=Dp - s["cz"]) for s in pad_secs(120, 380, 42)])
side = []
for s in pad_secs(120, 380, 42):          # the same profile turned to the x = W side: axis z, cx = x, cz = y
    side.append({"at": s["at"], "w": s["w"], "d": s["d"], "r": s["r"], "cx": W - (Dp - s["cz"]), "cz": s["cx"]})
d.add("pad-r", "loft", "white", axis="z", sections=side)
d.add("pad-l", "loft", "white", axis="z", sections=[dict(s, cx=W - s["cx"]) for s in side])
# embossed ring on the top centre
d.lathe("top-ring", [W / 2, H - 0.5, Dp / 2], [[62, 0], [70, 0], [70, 1.6], [62, 1.6], [62, 0]], "gloss#e8901a", soft=True)
# --- dark-red spots: pairs of overlapping discs, 1.2 mm proud
def spot(id, face, f, y, dia):
    """face: front / back / left / right; f = 0..1 along the face as seen from outside, left to right."""
    if face == "front":
        x = f * W; d.cyl(id, [x, y, Dp - 1], [x, y, Dp + 1.2], dia, "spot", soft=True)
    elif face == "back":
        x = W - f * W; d.cyl(id, [x, y, 1], [x, y, -1.2], dia, "spot", soft=True)
    elif face == "left":
        z = f * Dp; d.cyl(id, [1, y, z], [-1.2, y, z], dia, "spot", soft=True)
    else:
        z = Dp - f * Dp; d.cyl(id, [W - 1, y, z], [W + 1.2, y, z], dia, "spot", soft=True)
LEFT = [(0.15, 380, 40), (0.17, 337, 55), (0.48, 255, 56), (0.55, 280, 40), (0.74, 398, 38), (0.75, 365, 44)]
RIGHT = [(0.22, 352, 40), (0.25, 312, 55), (0.57, 268, 56), (0.64, 298, 42), (0.84, 441, 40), (0.85, 408, 46)]
# the photo shows the front (its left face) and the x = W side (its right face); the back and left repeat them
for face, pat in (("front", LEFT), ("right", RIGHT), ("back", LEFT), ("left", RIGHT)):
    for i, (f, y, dia) in enumerate(pat):
        spot(f"spot-{face}{i}", face, f, y * H / 550, dia * 1.15)
d.save()
