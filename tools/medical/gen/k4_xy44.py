from k4lib import *
# size: printed 70 x 49 x 54 cm; the photo shows the long (700) side along the inclined rail, the floor rails 490 across
d = K("xy-44", [490, 700, 540], {"white": "plastic#f1f0eb", "cap": "rubber#1b1c1e", "blue": "gloss#2440a8",
                                 "black": "rubber#1a1b1d", "red": "gloss#e0262a", "teal": "gloss#22b5ad", "green": "gloss#2fae6a", "cyan": "gloss#2c98d4"})
CX = 245
# --- H base: two floor rails across (x) with black caps, central spine along z, blue label on the spine
d.box("rail-front", [16, 0, 625, 474, 32, 675], "white", r=4)
d.box("rail-back", [16, 0, 40, 474, 32, 90], "white", r=4)
d.box("rail-cap", [0, 0, 623, 18, 34, 677], "cap", r=3, mirror="x", copies=[[0, 0, -585]])
d.box("spine", [220, 0, 90, 270, 34, 625], "white", r=4)
d.decal("spine-label", [270.6, 18, 330], [190, 14], "right", "blue")
d.decal("spine-label-t", [271.0, 18, 330], [150, 3], "right", "gloss#f2f2f2")
# --- inclined rail (~38 deg) with the blue graduated strip and white ticks
P0, P1 = [CX, 62, 640], [CX, 462, 120]
L = math.dist(P0, P1)
u = [(P1[i] - P0[i]) / L for i in range(3)]
n = [0, -u[2], u[1]]                                   # up-normal of the rail's top face
A = math.degrees(math.atan2(P1[1] - P0[1], P0[2] - P1[2]))
d.bar("incline", P0, P1, [60, 40], "white", r=4)
off = lambda p, k, t=0: [p[i] + n[i] * k + u[i] * t for i in range(3)]
d.bar("scale", off(P0, 20.5, 170), off(P1, 20.5, -15), [44, 1.5], "blue")
for nm, w, k in (("t", 16, 1), ("tl", 30, 5)):
    a = off(P0, 21.6, 185)
    d.bar(f"tick-{nm}", [CX - 21, a[1], a[2]], [CX - 21 + w, a[1], a[2]], [2.5, 0.8], "gloss#f4f4f4",
          repeat=rep(40 // k, [0, u[1] * 12 * k, u[2] * 12 * k]))
d.box("rail-end", [213, 450, 100, 277, 478, 140], "plastic#9aa0a8", r=6)
# --- back support post (telescopic) with a black star knob, weight peg on the spine
d.bar("post-outer", [CX, 30, 215], [CX, 230, 215], [56, 56], "white", r=4)
d.bar("post-inner", [CX, 230, 215], [CX, 385, 215], [44, 44], "white", r=4)
d.lathe("post-knob", [CX + 28, 300, 215], [[0, 0], [9, 0], [9, 12], [26, 16], [26, 32], [0, 35]], "black", axis="x")
d.box("post-head", [217, 370, 185, 273, 405, 245], "white", r=6)
d.cyl("peg", [CX, 32, 330], [CX, 140, 330], 30, "white")
# --- sliding carriage at the bottom of the rail: plate, disc stack, two black handles
CR = rot("x", A, P0)
d.box("carriage", [167, 82, 470, 323, 98, 640], "white", r=6, rot=CR)
d.decal("carriage-label", [CX, 98.6, 500], [60, 18], "top", "blue", rot=CR)
SZ = 595
d.cyl("stack-base", [CX, 110, SZ], [CX, 128, SZ], 70, "white")
for i, (dd, mat) in enumerate(((160, "cyan"), (160, "teal"), (156, "red"), (150, "red"))):
    y0 = 128 + 22 * i
    d.lathe(f"disc{i}", [CX, y0, SZ], [[12, 0], [dd / 2 - 6, 0], [dd / 2, 6], [dd / 2, 16], [dd / 2 - 6, 22], [12, 22]], mat)
d.cyl("pin", [CX, 110, SZ], [CX, 240, SZ], 24, "white")
d.sphere("pin-top", [CX, 240, SZ], 26, "white")
d.decal("pin-dot", [CX, 252.8, SZ], [10, 10], "top", "plastic#202124")
d.cyl("handle", [CX - 70, 112, 640], [CX - 290, 112, 640], 36, "black", mirror="x")
d.cyl("handle-hub", [CX - 75, 112, 640], [CX + 75, 112, 640], 26, "white")
# --- blue counter on top of the rail end facing the user
KR = rot("x", -18, [CX, 475, 120])
d.box("counter", [193, 445, 95, 297, 540, 140], "gloss#2f6fd0", r=14, rot=KR)
d.screen("counter-lcd", [210, 485, 139, 280, 525, 144], "plastic#2a3a4a", face="front", bezel=3, rot=KR)
d.decal("counter-btn", [CX, 465, 140.6], [18, 12], "front", "red", rot=KR)
d.save()
