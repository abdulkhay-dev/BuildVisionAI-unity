# XY-84 / XY-85 shower chairs: white U-cut seat, white backrest on 2 chrome tubes, telescopic legs
# (XY-84: splayed chrome/alu legs with grey tips; XY-85: handle slot in the back, black castors) — other-1
import sys
from o_lib import *
for ID in (sys.argv[1:] or ["xy-84", "xy-85"]):
    cast = ID == "xy-85"
    W, DP, H = 510, 475, (800 if cast else 775)
    d = D(ID, [W, DP, H], {"white": "plastic#efefed", "chrome": "chrome", "alu": "metal#cdd1d6", "grey": "plastic#9ea3a9",
                          "tip": "rubber#8e9399", "blk": "rubber#1f2023"})
    SY = 470 if cast else 445          # seat top
    # seat: U cut-out open to the front
    sx0, sx1, sz0, sz1 = 38, W - 38, 40, DP - 30
    cw, cd = 68, 235
    cx = W / 2
    seat = (f"M {sx0 + 40} {sz0} L {sx1 - 40} {sz0} Q {sx1} {sz0} {sx1} {sz0 + 40} L {sx1} {sz1 - 30} Q {sx1} {sz1} {sx1 - 30} {sz1} "
            f"L {cx + cw + 20} {sz1} Q {cx + cw} {sz1} {cx + cw} {sz1 - 20} L {cx + cw} {sz1 - cd + cw} "
            f"Q {cx + cw} {sz1 - cd} {cx} {sz1 - cd} Q {cx - cw} {sz1 - cd} {cx - cw} {sz1 - cd + cw} L {cx - cw} {sz1 - 20} "
            f"Q {cx - cw} {sz1} {cx - cw - 20} {sz1} L {sx0 + 30} {sz1} Q {sx0} {sz1} {sx0} {sz1 - 30} L {sx0} {sz0 + 40} "
            f"Q {sx0} {sz0} {sx0 + 40} {sz0} Z")
    d.slab("seat", "top", seat, [SY - 36, SY], "white", r=10)
    # backrest panel on two chrome tubes
    by0 = H - 235
    back = rr(45, by0, W - 45, H, 45)
    if cast:
        back += " " + rr(cx - 55, H - 75, cx + 55, H - 35, 12)
    d.slab("back", "front", back, [24, 50], "white", r=8)
    for x in (cx - 110, cx + 110):
        d.tube(f"post{int(x)}", [[x, SY - 50, 80], [x, SY - 45, 40], [x, by0 + 60, 36]], 22, "chrome", bend=30)
    # under-seat frame
    d.tube("frame", [[85, SY - 48, DP - 75], [85, SY - 48, 85], [W - 85, SY - 48, 85], [W - 85, SY - 48, DP - 75]],
           20, "chrome", bend=20)
    # legs
    splay = 40 if cast else 50
    for i, (xt, zt) in enumerate(((85, 85), (W - 85, 85), (85, DP - 75), (W - 85, DP - 75))):
        sx = -1 if xt < cx else 1
        sz = -1 if zt < DP / 2 else 1
        top = [xt, SY - 48, zt]
        yb = 95 if cast else 0
        foot = [xt + sx * splay, yb, zt + sz * splay * 0.85]
        mid = lerp(top, foot, 0.48)
        # (photos: the leg leaves the seat underside vertically and bends outward just below it)
        kink = [xt + sx * 6, SY - 95, zt + sz * 5]
        d.tube(f"leg-up{i}", [top, kink, mid], 25, "alu" if cast else "chrome", bend=40)
        d.cyl(f"leg-lo{i}", mid, lerp(top, foot, 0.98 if cast else 0.92), 21, "alu")
        d.cyl(f"clip{i}", lerp(top, foot, 0.46), lerp(top, foot, 0.52), 29, "grey")
        if cast:
            d.cyl(f"clip2-{i}", lerp(top, foot, 0.78), lerp(top, foot, 0.82), 27, "grey")
            d.box(f"cplate{i}", [foot[0] - 22, 92, foot[2] - 22, foot[0] + 22, 100, foot[2] + 22], "blk", r=3)
            caster(d, f"castor{i}", [foot[0], 0, foot[2] + 12], 70, "blk")
            # black castor body + lock pedal (photo: all-black castors)
            d.box(f"chood{i}", [foot[0] - 19, 48, foot[2] - 22, foot[0] + 19, 93, foot[2] + 14], "blk", r=8)
            d.box(f"cpedal{i}", [foot[0] - 12, 52, foot[2] + 10, foot[0] + 12, 62, foot[2] + 42], "blk", r=3)
        else:
            a = lerp(top, foot, 0.92)
            d.cyl(f"tip{i}", a, foot, 30, "tip", d2=40)   # bell-shaped rubber tip
    d.save()
