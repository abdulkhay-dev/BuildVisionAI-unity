from p1lib import *
d = D("xy-ppzl-ii", [650, 650, 1550], {
  "shell": "plastic#f3f4f6", "graph": "plastic#3d4249", "pole": "plastic#e8e3f0", "silver": "metal#c8ccd1",
  "black": "plastic#1d1f22", "blue": "gloss#2f7fd8", "grid": "plastic#4a4f57", "rib": "plastic#7a8088", "wire": "metal#e0e2e5"})
# 4-arm cross base: graphite arms with white top caps, graphite hub, light-grey castors
C = (325, 262)
# review: broad flat arms (graphite body, white top over most of the width), big castors, white hub disc
def xarms(root, tip, wr, wt, end):
    pts = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        ux, uz = math.cos(a), math.sin(a); vx, vz = -uz, ux
        pts += [(C[0] + ux * root - vx * wr, C[1] + uz * root - vz * wr), (C[0] + ux * tip - vx * wt, C[1] + uz * tip - vz * wt),
                (C[0] + ux * (tip + end), C[1] + uz * (tip + end)),
                (C[0] + ux * tip + vx * wt, C[1] + uz * tip + vz * wt), (C[0] + ux * root + vx * wr, C[1] + uz * root + vz * wr)]
    return pts
d.slab("arms", "top", rpoly(xarms(80, 270, 70, 55, 40), 30), [100, 140], "graph", r=12)
d.slab("arm-caps", "top", rpoly(xarms(80, 262, 60, 46, 34), 26), [138, 152], "shell", r=6)
for k in range(4):
    a = math.radians(45 + 90 * k)
    d.caster(f"castor-{k}", [C[0] + 262 * math.cos(a), 0, C[1] + 262 * math.sin(a)], 90, "rubber#c9cdd2")
d.lathe("hub-top", [C[0], 150, C[1]], [[0, 0], [92, 0], [90, 6], [84, 9], [0, 9]], "shell")
# collar and lilac-white pole
d.cyl("collar", [325, 158, 262], [325, 196, 262], 78, "graph")
d.cyl("pole", [325, 194, 262], [325, 570, 262], 50, "pole")
# control housing: graphite cheeks and back, white front with display and keys, white lip on top
d.box("housing", [255, 560, 207, 395, 880, 317], "graph", r=26)
d.box("front", [262, 578, 269, 388, 866, 322], "shell", r=14)
d.box("display", [303, 782, 321, 347, 816, 324], "gloss#e4ebf3", r=3)
d.box("display-rim", [301, 780, 320.5, 349, 818, 323], "blue", r=3)
text(d, "digits", "88", [312, 790, 324.2], 18, "blue", stroke=2.4, gap=0.4)
d.decal("label-1", [325, 612, 322], [70, 4], "plastic#9aa1a9", face="front", soft=True, repeat={"n": 4, "step": [0, -9, 0]})
d.decal("side-marks", [292, 790, 322], [6, 4], "plastic#9aa1a9", face="front", soft=True, copies=[[66, 0, 0], [0, 14, 0], [66, 14, 0]])
for i, x in enumerate((299, 325, 351)):
    d.lathe(f"key-{i}", [x, 752, 321], [[0, 0], [8, 0], [8, 4], [0, 5]], "blue", axis="z")
d.box("logo", [314, 690, 321, 336, 702, 323], "plastic#8e959e", r=2)
d.slab("lip", "side", "M 323 870 L 323 888 L 182 918 Q 165 921 165 906 L 165 892 Q 167 882 183 880 Z", [258, 392], "shell", r=6)
# articulated arm: silver links with black gas springs, joint knuckles, cable loop
J0, J1, J2 = [325, 885, 240], [325, 1290, 290], [325, 1395, 492]
d.bar("arm-lo", J0, J1, [36, 28], "silver", r=6)
d.cyl("spring-lo", [350, 950, 248], [350, 1245, 284], 16, "black")
d.bar("arm-up", J1, J2, [34, 26], "silver", r=6)
d.cyl("spring-up", [350, 1302, 305], [350, 1385, 468], 15, "black")
d.cyl("knuckle-0", [300, 885, 240], [352, 885, 240], 34, "chrome")
d.cyl("knuckle-1", [298, 1290, 290], [356, 1290, 290], 38, "chrome")
d.cyl("knuckle-2", [300, 1395, 492], [352, 1395, 492], 32, "chrome")
d.tube("cable", [[332, 1305, 310], [372, 1345, 330], [378, 1385, 410], [352, 1402, 470]], 5, "black", bend=30, soft=True)
# radiator: white frame with slot handles, ribbed dark plate behind a wire grille; tilted 30 deg down-forward
Cr = [325, 1380, 560]
TILT = 22
R = rot("x", TILT, Cr)
cy = Cr[1]
out = (f"M 145 {cy-170} L 505 {cy-170} Q 555 {cy-170} 555 {cy-120} L 555 {cy+120} Q 555 {cy+170} 505 {cy+170} "
       f"L 145 {cy+170} Q 95 {cy+170} 95 {cy+120} L 95 {cy-120} Q 95 {cy-170} 145 {cy-170} Z ")
def rr(x0, y0, x1, y1, r):
    return (f"M {x0+r} {y0} L {x1-r} {y0} Q {x1} {y0} {x1} {y0+r} L {x1} {y1-r} Q {x1} {y1} {x1-r} {y1} "
            f"L {x0+r} {y1} Q {x0} {y1} {x0} {y1-r} L {x0} {y0+r} Q {x0} {y0} {x0+r} {y0} Z ")
holes = rr(112, cy - 95, 136, cy + 95, 11) + rr(514, cy - 95, 538, cy + 95, 11) + rr(160, cy - 140, 490, cy + 140, 10)
d.slab("frame", "front", out + holes, [Cr[2] - 35, Cr[2] + 35], "shell", r=12, rot=R)
d.box("plate", [158, cy - 142, Cr[2] - 30, 492, cy + 142, Cr[2] + 8], "grid", rot=R)
d.box("rib", [164, cy - 138, Cr[2] + 7, 168, cy + 138, Cr[2] + 14], "rib", rot=R, repeat={"n": 33, "step": [10, 0, 0]})
st = [0, 60 * math.cos(math.radians(TILT)), 60 * math.sin(math.radians(TILT))]
d.cyl("wire", rotx([160, cy - 120, Cr[2] + 24], TILT, Cr), rotx([490, cy - 120, Cr[2] + 24], TILT, Cr), 4, "wire", repeat={"n": 5, "step": st})
d.box("yoke", [298, 1375, 488, 352, 1415, Cr[2] - 28], "graph", r=8)
d.save()
