"""xyrt-28 — hydraulic children stepper: white frame, rear column with counter, two pedals on hydraulic cylinders,
dark grey foam handrails; the user enters at the front (z = D)."""
from pd3_lib import *

W, Dp, H = 560, 700, 970
d = D("xyrt-28", [W, Dp, H], {"white": "plastic#f1f2f2", "foam": "rubber#3a3f46", "black": "plastic#1c1d1f", "strapb": "fabric#262b31",
                              "cap": "rubber#1d1e20", "wood": "wood#d9a75e"})
# floor frame as in the photo: a front and a rear cross rail (black end plugs) joined by one middle spine
for nm, z0 in (("f", 600), ("b", 60)):
    d.box(f"x{nm}", [22, 5, z0, W - 22, 45, z0 + 40], "white", r=5)
    d.box(f"cap-{nm}", [0, 0, z0 - 2, 24, 47, z0 + 42], "cap", r=5, copies=[[W - 24, 0, 0]])
d.box("spine", [258, 5, 100, 302, 45, 600], "white", r=5)
# column + counter
d.box("column", [255, 45, 80, 305, 890, 130], "white", r=6)
RC = rot("x", 25, [280, 900, 120])
d.box("counter", [215, 885, 85, 345, 975, 150], "plastic#8d949c", r=22, rot=RC)
d.box("lcd", [245, 925, 149, 315, 955, 152], "gloss#b8322e", r=4, rot=RC, soft=True)
d.box("cnt-brk", [265, 860, 125, 295, 900, 150], "plastic#c8ccd0", r=4)
d.coil("cnt-cable", [250, 880, 140], [235, 780, 150], 20, 4, 6, "black", soft=True)
# inclined brace
d.bar("brace", [280, 45, 390], [280, 600, 132], [36, 30], "white", r=5)
# chrome turntable / bracket with a knob carrying the cylinders
d.cyl("disc", [280, 640, 130], [280, 655, 130], 140, "chrome")
d.cyl("disc-knob", [280, 655, 130], [280, 690, 130], 36, "black")
# cross tube with chrome end caps (pedal axle level)
d.cyl("axle", [80, 250, 140], [W - 80, 250, 140], 32, "white")
d.cyl("axle-cap", [70, 250, 140], [80, 250, 140], 36, "chrome", copies=[[W - 150, 0, 0]])
d.add("roller", "wheel", "rubber#18191b", at=[280, 50, 175], d=78, d2=50, axis="x")
# pedal levers, cylinders (chrome rod up to the bracket, black body down on the lever), pedals (left up, right down)
def arch(id, px, py, z, w, h, sec, mat):
    """A strap across the foot plate at z: from under the plate edge, up the side, over, down the other side."""
    d.strap(id, [[px - w / 2 + 12, py, z], [px - w / 2 - 2, py, z], [px - w / 2 - 2, py + h, z], [px + w / 2 + 2, py + h, z],
                 [px + w / 2 + 2, py, z], [px + w / 2 - 12, py, z]], sec, mat, bend=24)
for nm, x, ye in (("l", 205, 330), ("r", 355, 160)):
    d.bar(f"lever-{nm}", [x, 130, 140], [x, ye, 560], [30, 36], "white", r=5)
    d.cyl(f"pivot-{nm}", [x - 20, 130, 140], [x + 20, 130, 140], 40, "chrome")
    top = [x, 630, 150]
    low = [x, (130 + (ye - 130) * 0.55), 140 + 420 * 0.55]
    mid = along(top, low, 0.42 if nm == "r" else 0.22)
    d.cyl(f"rod-{nm}", top, mid, 16, "chrome")
    d.cyl(f"hyd-{nm}", mid, low, 46, "black")
    d.cyl(f"hydc-{nm}", along(mid, low, -0.02), along(mid, low, 0.05), 50, "chrome")
    px = x - 70 if nm == "l" else x + 70
    d.box(f"pedal-{nm}", [px - 52, ye - 8, 450, px + 52, ye + 12, 690], "wood", r=4)
    d.bar(f"pbrk-{nm}", [x, ye + 2, 560], [px, ye + 2, 560], [30, 20], "chrome", r=3)
    # heel cup: a black U round the heel (open to the toes), higher at the back
    hz = 500
    cup = (f"M {px - 50} {hz + 30} L {px - 50} {hz} C {px - 50} {hz - 60} {px + 50} {hz - 60} {px + 50} {hz} "
           f"L {px + 50} {hz + 30} L {px + 41} {hz + 30} L {px + 41} {hz} C {px + 41} {hz - 47} {px - 41} {hz - 47} "
           f"{px - 41} {hz} L {px - 41} {hz + 30} Z")
    d.slab(f"heel-{nm}", "top", cup, [ye + 10, ye + 78], "strapb", r=3)
    d.box(f"heelb-{nm}", [px - 30, ye + 40, 452, px + 30, ye + 92, 464], "strapb", r=5)
    # two padded straps over the instep and the toes
    arch(f"strap1-{nm}", px, ye + 12, 565, 104, 50, [58, 9], "strapb")
    arch(f"strap2-{nm}", px, ye + 12, 640, 104, 38, [52, 9], "strapb")
# handrails
for nm, x, xi in (("l", 40, 240), ("r", W - 40, W - 240)):
    d.cyl(f"post-{nm}", [x, 45, 645], [x, 770, 645], 32, "white")
    d.tube(f"up-{nm}", [[x, 760, 645], [x, 805, 645], [x, 905, 150], [xi, 905, 120]], 46, "foam", bend=70)
    d.cyl(f"lo-{nm}", [x, 715, 605], [x, 715, 200], 46, "foam")
    d.cyl(f"lo-f-{nm}", [x, 715, 645], [x, 715, 600], 28, "white")
    d.tube(f"lo-b-{nm}", [[x, 715, 205], [x, 715, 130], [xi + (15 if nm == "l" else -15), 715, 110]], 26, "white", bend=40)
    d.cyl(f"up-b-{nm}", [xi, 905, 120], [280, 905, 110], 26, "white")
d.save()
