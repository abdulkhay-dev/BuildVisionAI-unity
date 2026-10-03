"""Shared body of the ALC far-infrared massage beds (table-3 batch): a long white glossy capsule shell bulging out
to a navy pin stripe, rounding over to a flat top with a light-blue towel mat, tucked in to a vertical plinth on
4 small castors. Bed length along x (x0 .. x0+L), width along z (0 .. Dp), top at Ht."""
import math
from lib import *

MATS = {"shell": "gloss#f3f4f6", "plinth": "plastic#eceef1", "navy": "gloss#24408f", "mat": "fabric#8fb0e2",
        "panel": "plastic#d9dde2", "dark": "plastic#2a2e33", "chr": "chrome", "cast": "rubber#7d848c"}


# stroke font (unit box 0..1 wide, 0..1 high) for the XIANGYUYILIAO lettering: letter -> list of polylines
FONT = {
    "X": [[(0, 1), (1, 0)], [(0, 0), (1, 1)]],
    "I": [[(0.5, 0), (0.5, 1)]],
    "A": [[(0, 0), (0.5, 1), (1, 0)], [(0.22, 0.38), (0.78, 0.38)]],
    "N": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    "G": [[(1, 0.85), (0.75, 1), (0.25, 1), (0, 0.75), (0, 0.25), (0.25, 0), (0.75, 0), (1, 0.2), (1, 0.45), (0.55, 0.45)]],
    "Y": [[(0, 1), (0.5, 0.5), (1, 1)], [(0.5, 0.5), (0.5, 0)]],
    "U": [[(0, 1), (0, 0.25), (0.25, 0), (0.75, 0), (1, 0.25), (1, 1)]],
    "L": [[(0, 1), (0, 0), (0.85, 0)]],
    "O": [[(0.25, 0), (0, 0.25), (0, 0.75), (0.25, 1), (0.75, 1), (1, 0.75), (1, 0.25), (0.75, 0), (0.25, 0)]],
}


def lettering(d, text, cx, y0, z, h=52, w=36, step=52, mat="navy", stroke=11, name="txt"):
    """Letters drawn with thin tubes on a front (+z) face; repeated letters share a part via copies."""
    adv = {"I": 0.5, "L": 0.88}
    tot = sum(step * adv.get(ch, 1) for ch in text) - step * adv.get(text[-1], 1) + w
    x = cx - tot / 2; where = {}
    for ch in text:
        off = 5 - w / 2 if ch == "I" else 0      # narrow I: its stroke sits at the start of its cell
        where.setdefault(ch, []).append(x + off); x += step * adv.get(ch, 1)
    for ch, xl in where.items():
        cp = [[x - xl[0], 0, 0] for x in xl[1:]] or None
        for k, line in enumerate(FONT[ch]):
            path = [[xl[0] + u * w, y0 + v * h, z] for u, v in line]
            d.tube(f"{name}-{ch}{k}", path, stroke, mat, bend=3, soft=True, copies=cp)


def body(d, x0, L, Dp, Ht, end_panel=True, stripe="navy"):
    cx = x0 + L / 2; cz = Dp / 2
    ys = Ht * 0.70           # widest line = the navy stripe
    secs = []
    def s(y, inset, r=None):
        w, dd = L - 2 * inset, Dp - 2 * inset
        secs.append(sec(y, w, dd, r if r is not None else min(dd * 0.36, 260), cx, cz))
    s(80, 40, 150); s(175, 38, 150)             # plinth (vertical)
    s(180, 30); s(200, 22)                       # bottom of the shell
    for k in range(1, 5):                        # gentle bulge up to the stripe
        t = k / 4; s(200 + (ys - 200) * t, 20 * (1 - math.sin(t * math.pi / 2)))
    R = 75                                       # top rounding
    for k in range(1, 8):
        t = k / 7; a = t * math.pi / 2
        s(ys + (Ht - 8 - ys) * math.sin(a), R * (1 - math.cos(a)))
    d.loft("shell", secs, "shell")
    d.loft("stripe", [sec(ys - 5, L + 4, Dp + 4, min((Dp + 4) * 0.36, 260), cx, cz),
                      sec(ys + 5, L + 4, Dp + 4, min((Dp + 4) * 0.36, 260), cx, cz)], stripe, soft=True)
    # light-blue towel mat on the flat top
    d.box("mat", [x0 + 80, Ht - 12, 78, x0 + L - 80, Ht + 3, Dp - 78], "mat", r=6, puff=2)
    # navy XIANGYUYILIAO lettering on the front, a row of letter blocks
    lettering(d, "XIANGYUYILIAO", cx, ys - 170, Dp - 3)
    # castors under the plinth corners (photo: white swivel housing, grey wheel Ø62 with a darker hub)
    cp = [[L - 260, 0, 0], [0, 0, Dp - 220], [L - 260, 0, Dp - 220]]
    d.box("castor-plate", [x0 + 105, 74, 85, x0 + 155, 82, 135], "plinth", r=3, copies=cp)
    d.box("castor-fork", [x0 + 112, 30, 98, x0 + 162, 76, 122], "plinth", r=8, copies=cp)
    d.add("castor-wheel", "wheel", "cast", at=[x0 + 140, 31, 110], d=62, d2=20, axis="z", copies=cp)
    d.cyl("castor-hub", [x0 + 140, 31, 96], [x0 + 140, 31, 124], 26, "plastic#5d636b", soft=True, copies=cp)
    if end_panel:   # head-end face (x max): a grey rating label and a small dark logo sticker (no screen)
        d.decal("label", [x0 + L, Ht - 170, cz - 160], [70, 140], "right", "panel", soft=True)
        d.decal("logo", [x0 + L, Ht - 190, cz - 40], [40, 30], "right", "dark", soft=True)
