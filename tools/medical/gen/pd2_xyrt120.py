# XYRT-120 space walker (children): yellow tube base loop, 4 posts with red foam, front frame with red grips,
# two blue foot platforms each hung from the front and back red cross bars by blue foam arms
from pd2_lib import *

W, D, H = 410, 680, 850
C = W / 2
d = Design("xyrt-120", [W, D, H], {"yel": YEL, "red": RED, "blue": BLU, "blk": BLK, "pad": "leather#2554b0"})
# base loop on the floor (closed, seam in the middle of the back side)
YB = 18
L, R_, B, F = 22, W - 22, 24, D - 24
d.tube("base", [[C, YB, B], [R_, YB, B], [R_, YB, F], [L, YB, F], [L, YB, B], [C, YB, B]], 32, "yel", bend=70)
for i, (x, z) in enumerate([(L, 190), (R_, 190), (L, 490), (R_, 490), (C - 90, F), (C + 90, B)]):
    along_z = x in (L, R_)
    bx = [x - 19, 0, z - 16, x + 19, 38, z + 16] if along_z else [x - 16, 0, z - 19, x + 16, 38, z + 19]
    d.box(f"foot{i}", bx, "blk", r=6)
# four posts: yellow, red foam on the middle
ZB, ZF = 62, D - 62
XL, XR = 40, W - 40
for nm, x, z in (("lb", XL, ZB), ("rb", XR, ZB), ("lf", XL, ZF), ("rf", XR, ZF)):
    top = 728 if nm.endswith("b") else 730
    d.cyl(f"post-{nm}", [x, YB, z], [x, top, z], 32, "yel")
    d.cyl(f"post-foam-{nm}", [x, 105, z], [x, 590, z], 44, "red")
    d.cyl(f"post-foot-{nm}", [x, 6, z], [x, 34, z], 40, "yel")
for nm in ("lb", "rb"):
    x = XL if nm[0] == "l" else XR
    d.lathe(f"post-cap-{nm}", [x, 728, ZB], [[0, 0], [18, 0], [18, 10], [12, 16], [0, 17]], "blk")
# cross bars on top of each frame: yellow tube, red foam in three pieces between the yellow pivot collars
XA = (130, W - 130)
for nm, z in (("b", ZB), ("f", ZF)):
    d.cyl(f"bar-{nm}", [XL, 718, z], [XR, 718, z], 30, "yel")
    for k, (xa0, xa1) in enumerate(((XL + 24, XA[0] - 24), (XA[0] + 24, XA[1] - 24), (XA[1] + 24, XR - 24))):
        d.cyl(f"bar-foam-{nm}{k}", [xa0, 718, z], [xa1, 718, z], 46, "red")
# front grips: the front posts rise above the bar and turn inward (red foam)
for nm, x, s in (("l", XL, 1), ("r", XR, -1)):
    d.tube(f"grip-{nm}", [[x, 718, ZF], [x, 800, ZF], [x + s * 30, 826, ZF], [x + s * 142, 826, ZF]], 32, "yel", bend=40)
    d.tube(f"grip-foam-{nm}", [[x, 770, ZF], [x, 800, ZF], [x + s * 30, 826, ZF], [x + s * 142, 826, ZF]], 44, "red", bend=40)
# foot platforms and their arms: each arm hangs from a yellow collar on the cross bar, drops a little outward,
# bends and runs down to the platform end (blue foam over the bend and the long run)
PZ0, PZ1 = 165, 515
for nm, xa, x0, x1 in (("l", XA[0], 58, 202), ("r", XA[1], W - 202, W - 58)):
    for k, (zt, zb) in enumerate(((ZB, PZ0 + 18), (ZF, PZ1 - 18))):
        s = 1 if zt < zb else -1
        d.cyl(f"clamp-{nm}{k}", [xa - 22, 718, zt], [xa + 22, 718, zt], 50, "yel")
        d.box(f"clamp-tab-{nm}{k}", [xa - 12, 668, zt - 14, xa + 12, 712, zt + 14], "yel", r=5)
        kink = [xa, 612, zt - s * 22]
        path = [[xa, 680, zt], kink, [xa, 175, zb - s * 6]]
        d.tube(f"arm-{nm}{k}", path, 26, "yel", bend=70)
        d.tube(f"arm-foam-{nm}{k}", [[xa, 662, zt - s * 6], kink, [xa, 205, zb - s * 10]], 42, "blue", bend=70)
        d.cyl(f"arm-low-{nm}{k}", [xa, 178, zb - s * 6], [xa, 112, zb], 26, "yel")
    d.box(f"plat-frame-{nm}", [xa - 16, 88, PZ0 + 5, xa + 16, 112, PZ1 - 5], "yel", r=6)
    d.box(f"plat-{nm}", [x0, 108, PZ0, x1, 146, PZ1], "pad", r=12, puff=4)
d.save()
