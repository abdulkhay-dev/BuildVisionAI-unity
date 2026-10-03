"""XYF-Z3 walker with carved wooden forearm rests. Closed end with the grips = front (z = depth); the floor
runners are open toward the user at the back."""
from k6lib import *

W, DEP, H = 800, 760, 1150
d = D("xyf-z3", [W, DEP, H], {"tube": "plastic#f3f2ef", "red": "gloss#b8322a", "redc": "metal#b0574c",
                              "wood": "wood#dc9550", "foam": "rubber#1f2023", "black": "plastic#1d1f22"})
XA = 55
YR = 100                     # runner centre (on Ø75 castors)
RT = 1000                    # rest top
ZM = 360                     # main uprights
# --- base: a flat U at castor height (floor runners joined at the front by a cross tube at the same height: the
# castors stand under its front corners on the photo); mid-height U from the uprights, closed in front
d.tube("base", [[XA, YR, 25], [XA, YR, DEP - 40], [W - XA, YR, DEP - 40], [W - XA, YR, 25]], 25, "tube", bend=80)
d.cyl("runner-end", [XA, YR, 18], [XA, YR, 26], 23, "plastic#e2e2de", mirror="x")
ZC = DEP - 170                # front cross of the mid U, the centre post and the rests' cross tube
d.tube("mid-u", [[XA, 500, ZM], [XA, 500, ZC], [W - XA, 500, ZC], [W - XA, 500, ZM]], 25, "tube", bend=80)
for z in (55, DEP - 80):
    caster(d, f"cas{z}", [XA, 0, z], 75, "rubber#3a3d42", mirror="x")
    # red wheel discs (photo): only the dark tyre rim shows round them
    d.cyl(f"hub{z}", [XA - 14.5, 37.5, z - 22.5], [XA + 14.5, 37.5, z - 22.5], 58, "red", mirror="x", soft=True)
# --- main uprights: white outer tube, red-chrome inner, black knob at the joint
YJ = 640
d.cyl("up", [XA, YR, ZM], [XA, YJ, ZM], 32, "tube", mirror="x")
d.cyl("up-col", [XA, YJ - 8, ZM], [XA, YJ + 14, ZM], 38, "tube", mirror="x")
d.cyl("up-in", [XA, YJ, ZM], [XA, RT - 70, ZM], 26, "redc", mirror="x")
star_knob(d, "up-knob", [XA - 16, YJ - 30, ZM], "x", -1, "black", dd=40)
star_knob(d, "up-knob-r", [W - XA + 16, YJ - 30, ZM], "x", 1, "black", dd=40)
# --- one centre post (photo): white square upper tube from the rests' cross tube down to a clamp on the mid U,
# a red telescopic leg below it ending in a black foot cap just above the floor
XP = W / 2
d.bar("fp", [XP, 480, ZC], [XP, RT - 75, ZC], [28, 28], "tube", r=4)
d.bar("fp-leg", [XP, 40, ZC], [XP, 490, ZC], [24, 24], "red", r=3)
d.box("fp-foot", [XP - 15, 22, ZC - 15, XP + 15, 44, ZC + 15], "black", r=3)
d.box("fp-clamp", [XP - 21, 482, ZC - 21, XP + 21, 518, ZC + 21], "tube", r=4)
# flat cross bar joining the rests, white rest brackets
d.box("cross", [XA + 60, RT - 85, ZC - 25, W - XA - 60, RT - 60, ZC + 25], "tube", r=4)
d.box("bracket", [XA - 30, RT - 86, ZM - 150, XA + 120, RT - 60, ZM + 260], "tube", r=4, mirror="x")
# --- carved wooden forearm rests (mirror pair), ~60 thick: straight outer edge; the inner edge is carved into a
# long concave scoop between a wide front end (the grip) and a narrower horn at the user end
ZB, ZF = 230, DEP - 40
X0, X1 = 15, 255
out = (f"M {X0} {ZB + 40} Q {X0} {ZB} {X0 + 40} {ZB} L {X1 - 55} {ZB} Q {X1 - 30} {ZB} {X1 - 30} {ZB + 30} "
       f"C {X1 - 30} {ZB + 110} {X1 - 80} {ZB + 130} {X1 - 80} {ZB + 220} "
       f"C {X1 - 80} {ZB + 320} {X1} {ZF - 230} {X1} {ZF - 120} "
       f"L {X1} {ZF - 40} Q {X1} {ZF} {X1 - 40} {ZF} L {X0 + 40} {ZF} Q {X0} {ZF} {X0} {ZF - 40} Z")
d.slab("rest", "top", out, [RT - 60, RT], "wood", r=12, mirror="x")
# black foam grips near the front end of each rest
GX, GZ = 140, ZF - 70
d.cyl("grip-stem", [GX, RT - 5, GZ], [GX, RT + 25, GZ], 24, "chrome", mirror="x")
d.cyl("grip", [GX, RT + 20, GZ], [GX, H, GZ], 36, "foam", mirror="x")
star_knob(d, "rest-knob", [XA + 60, RT - 86, ZM + 120], "y", -1, "black", dd=34, l=26, mirror="x")
d.save()
