from lib import *
from p2util import *
import math
# tower cart with a sloped black-glass top (touch screen), dark tongue + S badge on the front, boom arm with an arch radiator
cx = 280
d = D("xy-wb-ei", [900, 600, 1590], {"shell": "plastic#e9eaec", "base": "plastic#9aa0a8", "dark": "plastic#3a3f46",
      "glass": "gloss#121315", "black": "plastic#17191c", "white": "plastic#f4f5f7", "rad": "plastic#b4b9bf",
      "cable": "plastic#b4b8be", "teal": "gloss#3aa8c8"})
X0, X1, Z0, Z1 = cx - 190, cx + 190, 130, 550
# base: front and back crossbars, spine, castors
d.box("bar", [cx - 285, 100, 20, cx + 285, 140, 90], "base", r=20, copies=[[0, 0, 490]])
d.box("side-bar", [cx - 285, 104, 40, cx - 225, 136, 570], "base", r=14, copies=[[510, 0, 0]])
d.add("castor", "caster", "rubber#d0d3d8", at=[cx - 250, 0, 60], d=75, copies=[[500, 0, 0], [0, 0, 490], [500, 0, 490]])
# tower
TF, TR = 1065, 1165                       # top front / rear
d.add("tower", "slab", "shell", plane="side", outline=f"M {Z0} 140 L {Z1} 140 L {Z1} {TF} L {Z0} {TR} Z", w=[X0, X1], r=55)
ang = math.degrees(math.atan2(TR - TF, Z1 - Z0))
t = rot("x", ang, [cx, TF, Z1])
L = (Z1 - Z0) / math.cos(math.radians(ang))
d.box("top-rim", [X0 + 4, TF - 8, Z1 - L + 4, X1 - 4, TF + 4, Z1 - 4], "plastic#2a2d31", r=10, rot=t)
# the screen as a front-facing plate laid back onto the slope, so the picture's top points to the back
d.add("screen", "screen", "glass", box=[X0 + 10, TF + 18, Z1 - 16, X1 - 10, TF + L, Z1 - 4], r=8, face="front", bezel=26,
      print="med_xy-wb-ei_screen", rot=rot("x", -(90 - ang), [cx, TF + 9, Z1 - 4]))
# front tongue, LED bar, S badge, lettering, vents
d.add("tongue", "slab", "dark", plane="front", outline=f"M {cx - 52} {TF + 2} L {cx + 52} {TF + 2} L {cx + 52} 720 A 52 52 0 0 1 {cx - 52} 720 Z",
      w=[Z1 - 6, Z1 + 3], r=3)
d.box("led", [cx - 5, 860, Z1 + 2, cx + 5, 1020, Z1 + 4], "gloss#8fdcf5", r=4, soft=True)
d.cyl("badge", [cx, 730, Z1 + 2], [cx, 730, Z1 + 5], 62, "teal", soft=True)
d.add("badge-s", "slab", "white", plane="front", outline=f"M {cx + 14} 748 L {cx - 12} 748 L {cx - 12} 732 L {cx + 12} 728 L {cx + 12} 712 L {cx - 14} 712 L {cx - 14} 718 L {cx + 6} 718 L {cx + 6} 724 L {cx - 18} 728 L {cx - 18} 742 L {cx + 14} 742 Z",
      w=[Z1 + 5, Z1 + 6], soft=True)
d.box("brand", [cx - 120, 560, Z1, cx - 30, 576, Z1 + 1.5], "plastic#6c7279", soft=True)
d.box("brand-cn", [cx - 25, 560, Z1, cx + 15, 576, Z1 + 1.5], "plastic#6c7279", soft=True)
d.box("brand-sub", [cx - 100, 548, Z1, cx - 10, 551, Z1 + 1.5], "plastic#a6abb1", soft=True)
d.box("vent", [cx - 95, 230, Z1, cx - 70, 234, Z1 + 1.5], "plastic#4d5259", soft=True,
      copies=[[32, 0, 0], [64, 0, 0], [8, -16, 0], [40, -16, 0], [72, -16, 0]])
# front-right corner vent strip, right side seam and RF socket
d.box("vent-strip", [X1 - 20, 150, Z1 - 30, X1 + 2, 745, Z1 - 2], "black", r=6)
d.box("vent-slot", [X1 + 1, 160, Z1 - 26, X1 + 3, 164, Z1 - 6], "plastic#3a3f46", soft=True, repeat={"n": 36, "step": [0, 16, 0]})
d.box("seam", [X1, 150, Z1 - 70, X1 + 1, TF - 20, Z1 - 67], "plastic#c3c7cc", soft=True)
d.cyl("rf", [X1, 880, Z1 - 120], [X1 + 22, 880, Z1 - 120], 40, "plastic#b8bcc2")
d.cyl("rf-pin", [X1 + 22, 880, Z1 - 120], [X1 + 34, 880, Z1 - 120], 20, "chrome")
d.cyl("rf-icon", [X1, 880, Z1 - 175], [X1 + 1.5, 880, Z1 - 175], 18, "gloss#2f8fd8", soft=True)
# boom: curved post (white covers, black inner face), horizontal segment with joint caps, stem, bracket
P0 = [cx + 40, TR - 20, 170]
post = [P0, [cx + 40, 1300, 165], [cx + 25, 1450, 185], [cx + 70, 1560, 210]]
d.add("post", "sweep", "white", path=post, section=[70, 60], shape="rect", r=22, bend=120)
d.add("post-black", "sweep", "black", path=[add(p, [0, 0, 26]) for p in post[:3]] + [[cx + 80, 1530, 236]], section=[50, 14], shape="rect", r=6, bend=120)
d.cyl("post-base", [cx + 40, TR - 40, 170], [cx + 40, TR + 10, 170], 90, "black")
J1 = [cx + 90, 1560, 220]; J2 = [cx + 330, 1560, 270]; J3 = [cx + 560, 1555, 330]
d.cyl("j1", [J1[0], J1[1] - 40, J1[2]], [J1[0], J1[1] + 35, J1[2]], 74, "white")
d.add("seg1", "bar", "white", **{"from": J1, "to": J2}, section=[60, 70], r=26)
d.cyl("j2", [J2[0], J2[1] - 40, J2[2]], [J2[0], J2[1] + 35, J2[2]], 70, "white")
d.cyl("j2-cap", [J2[0], J2[1] + 35, J2[2]], [J2[0], J2[1] + 38, J2[2]], 46, "plastic#c3c7cc")
d.add("seg2", "bar", "white", **{"from": J2, "to": J3}, section=[55, 60], r=24)
d.cyl("j3", [J3[0], J3[1] - 35, J3[2]], [J3[0], J3[1] + 32, J3[2]], 64, "white")
d.cyl("stem", [J3[0], J3[1] - 30, J3[2]], [J3[0], 1440, J3[2]], 40, "plastic#d8dbe0")
# radiator: shallow arch shell along x, white inner layer, bracket on top
RX0, RX1, RZ, RY = cx + 310, cx + 810, J3[2], 1290          # x range, centre z, bottom edge y
R, H = 260, 135                                               # arc radius, rise
c = R - H                                                     # arc centre below the crown
half = math.sqrt(R * R - c * c)
yc = RY + H - R
def arch(r_out, r_in):
    ho = math.sqrt(r_out ** 2 - (RY - yc) ** 2); hi = math.sqrt(r_in ** 2 - (RY - yc) ** 2)
    return (f"M {RZ - ho:.1f} {RY} A {r_out} {r_out} 0 0 0 {RZ + ho:.1f} {RY} L {RZ + hi:.1f} {RY} "
            f"A {r_in} {r_in} 0 0 1 {RZ - hi:.1f} {RY} Z")
d.add("rad", "slab", "rad", plane="side", outline=arch(R, R - 16), w=[RX0, RX1], r=6)
d.add("rad-in", "slab", "white", plane="side", outline=arch(R - 15, R - 24), w=[RX0 + 6, RX1 - 6], r=3)
d.box("rad-rim", [RX0, RY, RZ - half - 8, RX1, RY + 14, RZ - half + 16], "white", r=6, copies=[[0, 0, 2 * half - 8]])
d.box("bracket", [J3[0] - 45, 1420, RZ - 35, J3[0] + 45, 1445, RZ + 35], "white", r=10)
d.box("handle", [J3[0] - 60, 1400, RZ - 12, J3[0] + 60, 1428, RZ + 12], "plastic#d8dbe0", r=10)
# cable from the radiator down to the RF socket
d.tube("cable", [[RX0 + 30, 1320, RZ + 60], [X1 + 140, 1250, Z1 - 60], [X1 + 220, 900, Z1 - 60], [X1 + 150, 760, Z1 - 100],
                 [X1 + 40, 880, Z1 - 120]], 10, "cable", bend=150, soft=True)
d.save()
