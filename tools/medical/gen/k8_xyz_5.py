"""XYZ-5 folding aluminium walker with front wheels. The user stands at the back (z = 0); the cross bars and the
wheels are at the front (z = depth)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 600, 500, 960
d = D("xyz-5", [W, DP, H], {"alu": "metal#c8ccd2", "alu2": "metal#d8dbdf", "grip": "plastic#9a9ea4", "dark": "plastic#4a4d52",
                            "tip": "rubber#8d9196", "tyre": "rubber#1c1d1f", "hinge": "plastic#b4b8bd", "chrome": "chrome"})
XS = [40, W - 40]   # wheels sit outside the legs: legs 40 in so the wheels stay inside W


def fz(y):
    """z of the front leg at height y (above the joint)"""
    return ZF + 6 + (ZFT - ZF - 6) * (y - YJ) / (H - 13 - YJ)


ZF, ZR = 430, 85            # front / rear leg (at the joint)
ZT, ZFT = 175, 405          # rear / front leg tops (both lean in)
YJ = 330                    # telescopic joint
for s, x in (("l", XS[0]), ("r", XS[1])):
    # side frame: rear leg up, rounded top, front leg down (upper tubes)
    d.tube(f"frame-{s}", [[x, YJ, ZR - 18], [x, H - 13, ZT], [x, H - 13, ZFT], [x, YJ, ZF + 6]], 25, "alu", bend=55)
    d.box(f"grip-{s}", [x - 20, H - 32, ZT + 40, x + 20, H + 0, ZFT - 30], "grip", r=14)
    # telescopic lower legs, collars, push-button dots
    d.cyl(f"rlow-{s}", [x, 48, ZR - 48], [x, YJ + 30, ZR - 18], 22, "alu2")
    d.cyl(f"flow-{s}", [x, 118, ZF + 10], [x, YJ + 30, ZF + 6], 22, "alu2")
    for z0, k in ((ZR - 18, "r"), (ZF + 6, "f")):
        d.cyl(f"col{k}-{s}", [x, YJ - 12, z0], [x, YJ + 22, z0], 30, "alu")
        d.cyl(f"btn{k}-{s}", [x, YJ - 40, z0 + 10], [x, YJ - 40, z0 + 14], 7, "dark", soft=True,
              repeat={"n": 5, "step": [0, -40, 0]})
    d.cyl(f"tip-{s}", [x, 0, ZR - 52], [x, 55, ZR - 49], 32, "tip")
    # front wheel on the OUTER side of the leg (photo), on an axle through a small bracket at the leg's foot
    so = -1 if s == "l" else 1
    xw = x + so * 26
    d.box(f"fork-{s}", [min(x, x + so * 14) - 3, 50, ZF - 6, max(x, x + so * 14) + 3, 128, ZF + 24], "dark", r=5)
    d.add(f"wheel-{s}", "wheel", "tyre", at=[xw, 62.5, ZF + 8], d=125, d2=22, axis="x")
    d.cyl(f"hub-{s}", [xw - 14, 62.5, ZF + 8], [xw + 14, 62.5, ZF + 8], 44, "hinge")
    d.cyl(f"axle-{s}", [x, 62.5, ZF + 8], [xw + so * 16, 62.5, ZF + 8], 10, "chrome")
    # side brace front -> rear
    d.cyl(f"brace-{s}", [x, 470, fz(470)], [x, 425, ZR - 18 + (ZT - ZR + 18) * (425 - YJ) / (H - 13 - YJ)], 19, "alu")
    for y in (470, 716, 896):
        zz = fz(y)
        d.box(f"clamp{y}-{s}", [x - 17, y - 16, zz - 16, x + 17, y + 16, zz + 16], "hinge", r=5)
# front cross bars: upper straight with a centre folding hinge, lower bowed forward
d.cyl("cross-up", [XS[0] + 15, 896, fz(896)], [XS[1] - 15, 896, fz(896)], 22, "alu")
d.box("hinge", [W / 2 - 32, 880, fz(896) - 18, W / 2 + 32, 914, fz(896) + 18], "hinge", r=6)
d.box("hinge-l", [W / 2 - 110, 884, fz(896) - 14, W / 2 - 80, 908, fz(896) + 14], "hinge", r=4, copies=[[190, 0, 0]])
d.tube("cross-lo", [[XS[0] + 15, 716, fz(716)], [W / 2, 716, fz(716) + 28], [XS[1] - 15, 716, fz(716)]], 22, "alu", bend=400)
d.save()
