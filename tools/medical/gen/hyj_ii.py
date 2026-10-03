from lib import *
import math
# old blue trolley: white front between royal-blue side panels, sloped grey membrane head, one blue tube arm (right rear)
d = D("hyj-ii", [450, 400, 1690], {"shell": "gloss#f2f3f5", "blue": "gloss#2f6db5", "panel": "plastic#c9cdd2",
      "strip": "plastic#6c7279", "chrome": "chrome", "black": "gloss#15171a", "logo": "gloss#2f6fbf"})
d.add("castor", "caster", "rubber#3a3d42", at=[55, 0, 45], d=68, copies=[[340, 0, 0], [0, 0, 300], [340, 0, 300]])
d.box("bottom", [20, 82, 20, 430, 92, 380], "plastic#8a9099", r=6)
# a white centre block (front + head) between two royal-blue side blocks whose tops stay ~60 lower
d.box("front", [66, 88, 30, 384, 800, 396], "shell", r=8)
d.box("side", [0, 92, 15, 72, 770, 400], "blue", r=16, copies=[[378, 0, 0]])
d.cyl("logo", [300, 560, 396], [300, 560, 398], 46, "logo", soft=True)
d.box("logo-x", [298, 545, 397, 302, 575, 399], "shell", soft=True)
d.box("logo-y", [285, 558, 397, 315, 562, 399], "shell", soft=True)
d.box("logo-txt", [165, 553, 396, 268, 571, 398], "logo", soft=True)
d.box("logo-sub", [165, 540, 396, 268, 544, 398], "plastic#8fa8c8", soft=True)
# head
d.add("head", "slab", "shell", plane="side", outline="M 15 796 L 400 796 L 400 872 L 150 955 L 15 955 Z", w=[66, 384], r=14)
# white fairing from the head over the right blue block to the arm post
d.add("fairing", "slab", "shell", plane="side", outline="M 15 766 L 330 766 L 330 800 L 150 880 L 15 880 Z", w=[380, 446], r=12)
ang = math.degrees(math.atan2(955 - 872, 400 - 150))
t = rot("x", ang, [225, 872, 400])
d.box("panel", [80, 869, 400 - 255, 370, 874, 400 - 8], "panel", r=4, rot=t)
y = 874.5
d.box("p-strip", [80, 873, 400 - 40, 370, y, 400 - 8], "strip", soft=True, rot=t)
d.box("p-band", [80, 873, 400 - 255, 370, y, 400 - 205], "plastic#8a9099", soft=True, rot=t)
d.box("p-title", [150, 873.2, 400 - 238, 300, y + 0.2, 400 - 228], "plastic#3d4248", soft=True, rot=t)
d.box("p-win", [240, 873, 400 - 150, 290, y, 400 - 118], "plastic#f4f5f7", soft=True, rot=t, copies=[[62, 0, 0]])
d.box("p-winframe", [236, 872.8, 400 - 154, 294, y - 0.5, 400 - 114], "plastic#5d636b", soft=True, rot=t, copies=[[62, 0, 0]])
d.box("p-btn", [96, 873, 400 - 110, 112, y, 400 - 98], "gloss#2f6fd0", soft=True, rot=t, repeat={"n": 6, "step": [24, 0, 0]})
# arm: blue post up from the right blue block's rear, black clamp, chrome joint, long blue tube, radiator
d.cyl("post", [410, 790, 68], [410, 985, 68], 34, "blue")
d.box("clamp", [385, 980, 38, 435, 1060, 98], "black", r=8)
d.add("joint", "sphere", "chrome", at=[403, 1092, 68], d=44)
d.cyl("joint-knob", [403, 1092, 68], [455, 1092, 68], 16, "chrome")
d.add("joint-knob2", "sphere", "black", at=[460, 1092, 68], d=26)
A = [403, 1110, 72]; T = [165, 1530, 225]
d.cyl("arm", A, T, 30, "blue")
lerp = lambda a, b, s: [a[i] + (b[i] - a[i]) * s for i in range(3)]
d.cyl("sleeve", lerp(A, T, 0.10), lerp(A, T, 0.46), 42, "metal#a7adb5")
d.cyl("sleeve-ring", lerp(A, T, 0.46), lerp(A, T, 0.49), 46, "black")
d.cyl("sleeve-ring2", lerp(A, T, 0.07), lerp(A, T, 0.10), 46, "black")
d.box("bracket", [T[0] - 22, T[1] - 25, T[2] - 22, T[0] + 22, T[1] + 30, T[2] + 22], "chrome", r=8)
d.cyl("lever", [T[0], T[1], T[2]], [T[0] + 90, T[1] + 10, T[2] + 10], 14, "black")
d.add("lever-end", "sphere", "black", at=[T[0] + 95, T[1] + 11, T[2] + 10], d=24)
# radiator: Ø160 × 220 cylinder, axis pointing left and 20° down, back end at the bracket
B = [T[0] + 10, T[1] + 70, T[2]]
a = math.radians(-10)
F = [B[0] - 185 * math.cos(a), B[1] - 185 * math.sin(a), B[2] + 25]
d.cyl("radiator", B, F, 135, "shell", sides=40)
d.add("rad-back", "sphere", "shell", at=B, radii=[15, 66, 66], rot=rot("z", -10, B))
d.cyl("rad-face", F, lerp(F, B, -0.015), 124, "plastic#e4e6e9")
d.cyl("rad-band", lerp(B, F, 0.12), lerp(B, F, 0.16), 138, "plastic#c9cdd2")
# black cable from the radiator back, along the arm, into the head rear
M2 = lerp(A, T, 0.5)
d.tube("cable", [[B[0] + 5, B[1] + 50, B[2] - 20], [T[0] + 45, T[1] + 35, T[2] - 25], [M2[0] + 38, M2[1], M2[2] - 22],
                 [A[0] + 40, A[1] + 10, A[2] - 20], [A[0] + 30, A[1] - 90, A[2] - 30], [400, 905, 40]], 10, "black", bend=70, soft=True)
d.save()
