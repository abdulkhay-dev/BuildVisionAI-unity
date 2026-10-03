"""xym-4 Pedal Exerciser (upper-limb ergometer). Front (z = depth) = the patient side with the logo and knobs; the
trolley handle and the orange transport wheels at the back. Photo from the front-right."""
import math
from k7lib import *

d = D("xym-4", [520, 500, 850], {
    "shell": "plastic#f1f2f2", "black": "plastic#1a1b1d", "chrome": "chrome", "foam": "rubber#1f2022",
    "orange": "rubber#f0661e", "console": "plastic#56607a"})
ZC, YC, RD = 255, 335, 225      # D shape: centre of the top semicircle (z, y), radius
YB = 18


def dshape(r, y0=YB):
    return (f"M {ZC - r} {y0} L {ZC + r} {y0} L {ZC + r} {YC} A {r} {r} 0 0 1 {ZC - r} {YC} Z")


XL, XR = 108, 412               # housing width
d.slab("cover-l", "side", dshape(RD), [XL, XL + 46], "shell", r=14)
d.slab("cover-r", "side", dshape(RD), [XR - 46, XR], "shell", r=14)
d.slab("band", "side", dshape(RD - 3), [XL + 50, XR - 50], "shell", r=6)
d.slab("seam-l", "side", dshape(RD - 2, YB + 30), [XL + 45, XL + 51], "black")
d.slab("seam-r", "side", dshape(RD - 2, YB + 30), [XR - 51, XR - 45], "black")
d.box("feet", [XL + 30, 0, 400, XL + 70, YB + 2, 450], "black", r=6, copies=[[XR - XL - 100, 0, 0]])
# --- front of the band: round logo, black knob, lower black knob
FZ = ZC + RD
d.cyl("logo", [XL + 92, 300, FZ - 1], [XL + 92, 300, FZ + 1.5], 46, "plastic#e4eaf2", soft=True)
d.cyl("logo-ring", [XL + 92, 300, FZ], [XL + 92, 300, FZ + 1.8], 36, "plastic#5a82c0", soft=True)
d.cyl("logo-in", [XL + 92, 300, FZ], [XL + 92, 300, FZ + 2.1], 28, "plastic#e4eaf2", soft=True)
d.lathe("knob-front", [XL + 92, 238, FZ], [[0, 0], [14, 0], [14, 10], [20, 12], [20, 34], [0, 36]], "black", axis="z")
d.lathe("knob-low", [XL + 70, 100, FZ], [[0, 0], [12, 0], [12, 8], [18, 10], [18, 30], [0, 32]], "black", axis="z")
# --- cranks on both sides: curved slot, chrome arm, black D-loop hand grip (180° apart)
HY = 300
for nm, x0, sgn, ang in (("r", XR, 1, 200), ("l", XL, -1, 20)):
    a0, a1 = math.radians(-55), math.radians(100)
    def P(r, a): return (ZC + r * math.cos(a), HY + r * math.sin(a))
    # photo: a gently curved slot from the link pin (front, low) up to above the hub, bulging to the front
    p1 = (ZC + 146 * math.cos(math.radians(-50)), HY + 146 * math.sin(math.radians(-50)))
    p2 = (ZC - 40, HY + 100)
    nz, ny = (p2[1] - p1[1]), -(p2[0] - p1[0]); ln = math.hypot(nz, ny); nz, ny = nz / ln, ny / ln
    cpt = ((p1[0] + p2[0]) / 2 + 50 * nz, (p1[1] + p2[1]) / 2 + 50 * ny)
    def B(t): return ((1 - t) ** 2 * p1[0] + 2 * t * (1 - t) * cpt[0] + t * t * p2[0],
                      (1 - t) ** 2 * p1[1] + 2 * t * (1 - t) * cpt[1] + t * t * p2[1])
    def off(t, w):
        a_ = B(max(t - 0.01, 0)); b_ = B(min(t + 0.01, 1)); dz, dy = b_[0] - a_[0], b_[1] - a_[1]; L = math.hypot(dz, dy)
        q = B(t); return (q[0] + w * dy / L, q[1] - w * dz / L)
    pts = [off(k / 12, 8) for k in range(13)] + [off(1 - k / 12, -8) for k in range(13)]
    xs = [x0, x0 + sgn * 1.5] if sgn > 0 else [x0 - 1.5, x0]
    d.slab(f"slot-{nm}", "side", "M " + " L ".join(f"{z:.1f} {y:.1f}" for z, y in pts) + " Z", xs, "black")
    xa = x0 + sgn * 8
    a = math.radians(ang)
    ez, ey = ZC + 135 * math.cos(a), HY + 135 * math.sin(a)
    d.cyl(f"hub-{nm}", [x0, HY, ZC], [x0 + sgn * 14, HY, ZC], 50, "chrome")
    d.bar(f"arm-{nm}", [xa, HY, ZC], [xa, ey, ez], [10, 34], "chrome", r=4)
    d.cyl(f"pin-{nm}", [xa, ey, ez], [xa + sgn * 22, ey, ez], 20, "chrome")
    # photo: a flat chrome link from the hub to a pin in the slot's lower (front) end
    la = math.radians(-50)   # the pin sits in the fixed slot on both sides
    lz, ly = ZC + 146 * math.cos(la), HY + 146 * math.sin(la)
    d.bar(f"link-{nm}", [x0 + sgn * 4, HY, ZC], [x0 + sgn * 4, ly, lz], [6, 24], "chrome", r=3)
    d.cyl(f"link-pin-{nm}", [x0 + sgn * 2, ly, lz], [x0 + sgn * 12, ly, lz], 18, "metal#9a9ea3")
    gx0, gx1 = xa + sgn * 22, xa + sgn * 100
    d.cyl(f"grip-{nm}", [gx0, ey, ez], [gx1, ey, ez], 34, "foam")
    d.tube(f"loop-{nm}", [[gx0, ey + 10, ez], [gx0 + sgn * 6, ey + 60, ez], [gx1, ey + 62, ez], [gx1 + sgn * 6, ey + 6, ez]],
           16, "black", bend=18)
# --- top: console on a stalk (LCD, red button), black knob with a brass collar, cable to the back
d.cyl("stalk", [300, YC + RD - 8, 210], [300, YC + RD + 40, 210], 22, "console")
tilt = rot("x", -22, [300, YC + RD + 40, 210])
d.box("console", [250, YC + RD + 30, 192, 350, YC + RD + 120, 232], "console", r=14, rot=tilt)
d.add("lcd", "screen", "plastic#2b2f36", box=[268, YC + RD + 72, 230, 332, YC + RD + 112, 234], r=4, face="front", bezel=4, rot=tilt)
d.box("lcd-glow", [272, YC + RD + 76, 233.5, 328, YC + RD + 108, 235], "plastic#c9d3c4", r=2, soft=True, rot=tilt)
d.box("btn-red", [282, YC + RD + 44, 230, 302, YC + RD + 60, 237], "gloss#d8262a", r=6, rot=tilt)
d.box("btn-grey", [310, YC + RD + 44, 230, 326, YC + RD + 60, 236], "plastic#9aa1ad", r=6, rot=tilt)
d.cyl("knob-collar", [218, YC + RD - 10, 290], [218, YC + RD + 8, 290], 26, "metal#d8c79a")
d.lathe("knob-top", [218, YC + RD + 6, 290], [[0, 0], [10, 0], [10, 10], [17, 12], [17, 34], [0, 36]], "black")
d.tube("cable", [[300, YC + RD + 60, 190], [330, YC + RD + 30, 150], [370, YC + RD - 10, 100]], 8, "black", bend=30, soft=True)
# --- telescopic trolley handle at the back: white sleeve, two chrome tubes, black foam U grip
d.box("sleeve", [175, 300, 0, 345, 610, 46], "shell", r=12)
d.cyl("pole", [195, 600, 22], [195, 770, 22], 24, "chrome", copies=[[130, 0, 0]])
d.tube("handle", [[195, 765, 22], [195, 820, 22], [325, 820, 22], [325, 765, 22]], 32, "foam", bend=45)
# --- orange transport wheels at the bottom back corners
d.add("wheel-l", "wheel", "orange", at=[XL - 18, 48, 40], d=92, d2=30, axis="x")
d.add("wheel-r", "wheel", "orange", at=[XR + 18, 48, 40], d=92, d2=30, axis="x")
d.cyl("wheel-hub", [XL - 35, 48, 40], [XL - 1, 48, 40], 40, "plastic#30343a", copies=[[XR - XL + 36, 0, 0]])
d.save()
