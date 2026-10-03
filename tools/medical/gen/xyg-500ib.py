from p1lib import *
d = D("xyg-500ib", [520, 560, 1650], {
  "shell": "plastic#f3f4f6", "blue": "plastic#2a8ad4", "dark": "plastic#2b2e33", "grey": "plastic#b9bec5",
  "black": "gloss#141517", "chrome": "chrome"})
# base plinth with a raised middle step, black twin-wheel castors at the corners
d.add("castor", "caster", "rubber#1d1e21", at=[60, 0, 80], d=75, copies=[[400, 0, 0], [0, 0, 400], [400, 0, 400]])
# plinth: four corner pads with shallow notches between them on every side (photo)
L, N = 105, 22
pl = [(10, 40), (10 + L, 40), (10 + L, 40 + N), (510 - L, 40 + N), (510 - L, 40), (510, 40), (510, 40 + L), (510 - N, 40 + L),
      (510 - N, 520 - L), (510, 520 - L), (510, 520), (510 - L, 520), (510 - L, 520 - N), (10 + L, 520 - N), (10 + L, 520), (10, 520),
      (10, 520 - L), (10 + N, 520 - L), (10 + N, 40 + L), (10, 40 + L)]
d.slab("plinth", "top", rpoly(pl, 10), [95, 160], "shell", r=8)
d.box("step", [140, 155, 150, 380, 172, 410], "shell", r=14)
# square column with the blue stripes, logo and vertical lettering
d.box("column", [185, 170, 205, 335, 750, 355], "shell", r=8)
d.box("stripe", [183, 188, 203, 337, 210, 357], "blue", r=3, copies=[[0, 36, 0], [0, 72, 0]])
d.cyl("logo", [218, 655, 355], [218, 655, 356.5], 24, "blue")
d.add("logo-dot", "decal", "shell", at=[218, 655, 356.7], size=[6, 14], face="front", soft=True)
d.add("logo-text", "decal", "blue", at=[268, 660, 355], size=[64, 13], face="front", soft=True)
d.add("logo-sub", "decal", "blue", at=[268, 646, 355], size=[56, 4], face="front", soft=True)
# vertical "XIANGYU MEDICAL" read top to bottom, letters' tops to the right
text(d, "txt", "XIANGYU MEDICAL", [247, 610, 355], 26.5, "blue", along=(0, -1))
# tray and the control box with the LED label (print)
d.box("tray", [75, 750, 150, 445, 770, 450], "shell", r=8)
d.box("ctrl", [125, 770, 205, 395, 890, 395], "shell", r=6)
d.add("panel", "screen", "plastic#cfd8e2", box=[129, 774, 392, 391, 886, 399], r=3, face="front", bezel=2,
      print="med_xyg-500ib_screen")
# telescopic pole: black collar, chrome tube + thin dark tube, white clamps
d.lathe("collar", [265, 890, 300], [[27, 0], [26, 30], [22, 52], [17, 58], [0, 58]], "black")
d.cyl("collar-ring", [265, 948, 300], [265, 962, 300], 30, "shell")
d.bar("pole", [265, 962, 300], [265, 1290, 300], [18, 14], "metal#dfe2e6", r=3)
# two gas springs either side of the post, black bodies on chrome rods, black cross brackets
d.bar("bracket-lo", [236, 968, 300], [294, 968, 300], [10, 12], "black", r=2)
d.bar("bracket-hi", [234, 1262, 300], [296, 1262, 300], [10, 14], "black", r=2)
d.cyl("spring-rod", [242, 975, 300], [242, 1010, 300], 6, "chrome", copies=[[46, 0, 0]])
d.cyl("spring", [242, 1010, 300], [242, 1255, 300], 13, "dark", copies=[[46, 0, 0]])
# joint knob, double arm to the lamp
J = [265, 1300, 300]
M = [178, 1585, 318]
d.add("joint", "sphere", "black", at=J, d=34)
d.cyl("joint-knob", [265, 1300, 300], [300, 1300, 300], 22, "black")
d.bar("arm-1", J, M, [18, 11], "metal#dfe2e6", r=3)
d.cyl("arm-2", [J[0] + 10, J[1] + 22, J[2] + 14], [M[0] + 18, M[1] - 30, M[2] + 14], 13, "dark")
d.tube("cable", [[J[0] + 6, J[1] + 10, J[2] - 8], [J[0] + 12, J[1] + 52, J[2] - 14], [J[0] - 4, J[1] + 66, J[2] - 10], [J[0] - 14, J[1] + 40, J[2] - 6]], 6, "black", soft=True)
d.add("lamp-knob", "sphere", "black", at=M, d=30)
d.cyl("lamp-knob-2", [M[0], M[1], M[2]], [M[0] + 34, M[1], M[2]], 20, "black")
# the bell: axis +z from P, tilted 40 deg down-forward
P = [170, 1600, 330]
R = rot("x", 40, P)
prof = [[0, 0], [40, 5], [62, 18], [78, 40], [90, 75], [98, 120], [102, 170], [103, 200], [101, 206]]
d.add("bell", "lathe", "shell", at=P, axis="z", profile=prof, rot=R)
d.add("bell-in", "lathe", "plastic#3d4147", at=[P[0], P[1], P[2] + 198], axis="z", profile=[[0, 0], [99, 0], [99, 6], [0, 6]], rot=R)
for i, rr in enumerate((22, 44, 66, 86)):
    d.add(f"guard-{i}", "lathe", "grey", at=[P[0], P[1], P[2] + 204], axis="z", caps=False,
          profile=[[rr - 2.5, 0], [rr + 2.5, 0], [rr + 2.5, 4], [rr - 2.5, 4], [rr - 2.5, 0]], rot=R)
for k in range(3):
    a = math.radians(60 * k + 15)
    c, s = 96 * math.cos(a), 96 * math.sin(a)
    d.add(f"spoke-{k}", "bar", "grey", **{"from": rotx([P[0] + c, P[1] + s, P[2] + 206], 40, P), "to": rotx([P[0] - c, P[1] - s, P[2] + 206], 40, P)},
          section=[3, 3], r=1)
d.add("hub", "lathe", "grey", at=[P[0], P[1], P[2] + 205], axis="z", profile=[[0, 0], [12, 0], [12, 7], [0, 7]], rot=R)
# slim slots along the top of the bell
def rb(h):
    for (a, b), (c, e) in zip(prof, prof[1:]):
        if b <= h <= e: return a + (c - a) * (h - b) / (e - b)
    return prof[-1][0]
for k, ph in enumerate((-45, -15, 15, 45)):
    p = math.radians(ph)
    pts = [rotx([P[0] + (rb(h) - 1) * math.sin(p), P[1] + (rb(h) - 1) * math.cos(p), P[2] + h], 40, P) for h in (75, 100, 125, 150, 172)]
    d.tube(f"slot-{k}", pts, 7, "dark")
d.save()
