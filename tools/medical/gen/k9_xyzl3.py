"""XYZL-3 two-person standing frame. One long table; a patient stands at each end (x ends) facing the middle,
arms on two grey padded bars, hips in a grey wrap pad, knees against a blue-grey knee board. White frame: two long floor
rails with bent ends and black caps, two cross bars, four square posts up to the table."""
from k9lib import *
d = K("xyzl-3", [1440, 600, 1100], {
    "frame": "plastic#f1f2f0", "wood": "wood#d6a46c", "pad": "leather#5d6166", "knee": "leather#5f7c99",
    "knob": "plastic#18191b", "chrome": "chrome", "cap": "rubber#18191b"})
W, CX = 1440, 720
TY = 1060
# --- floor rails with bent ends, black caps; cross bars
for nm, zi, zo in (("f", 510, 575), ("b", 90, 25)):
    d.tube(f"rail-{nm}", [[30, 22, zo], [190, 22, zi], [W - 190, 22, zi], [W - 30, 22, zo]], 34, "frame", bend=140)
    for k, x in enumerate((30, W - 30)):
        d.box(f"rail-cap-{nm}{k}", [x - 22, 0, zo - 22, x + 22, 44, zo + 22], "cap", r=4)
for k, x in enumerate((420, W - 420)):
    d.bar(f"cross-{k}", [x, 22, 90], [x, 22, 510], [40, 32], "frame", r=3)
# --- table: wood middle panel, white end frames carrying the grey arm bars
d.box("table", [360, TY, 20, W - 360, TY + 22, 580], "wood", r=4)
d.bar("tframe-f", [20, TY - 18, 545], [W - 20, TY - 18, 545], [40, 30], "frame", r=3)
d.bar("tframe-b", [20, TY - 18, 55], [W - 20, TY - 18, 55], [40, 30], "frame", r=3)
for nm, x0, x1 in (("l", 0, 400), ("r", W - 400, W)):
    for zn, z0, z1 in (("f", 495, 595), ("b", 5, 105)):
        d.box(f"arm-{nm}{zn}", [x0, TY + 2, z0, x1, TY + 40, z1], "pad", r=18, puff=4)
        d.box(f"arm-base-{nm}{zn}", [x0 + 5, TY - 4, z0 + 5, x1 - 5, TY + 4, z1 - 5], "frame", r=3)
# --- the two stations (mirror images about the middle)
def station(nm, s):
    """s = -1 left station (patient at x ~ 0..400 facing +x), +1 right station."""
    xp = CX + s * 300                       # posts
    for zn, z in (("f", 470), ("b", 130)):
        d.bar(f"post-{nm}{zn}", [xp, 30, z], [xp, TY - 30, z], [40, 40], "frame", r=3)
    # knee board (photo): a blue-grey board in the plane of the posts inside a white frame (bars between the posts),
    # a grey pad on the patient's side; clamp blocks with black knobs and chrome rods on the middle side
    for k, y in enumerate((370, 750)):
        d.bar(f"kframe-{nm}{k}", [xp, y, 130], [xp, y, 470], [34, 30], "frame", r=3)
    a, b = sorted([xp + s * 10, xp + s * 30])
    d.box(f"knee-{nm}", [a, 170, 170, b, 720, 430], "knee", r=8)
    a, b = sorted([xp + s * 28, xp + s * 72])
    d.box(f"knee-pad-{nm}", [a, 220, 180, b, 640, 420], "pad", r=16, puff=5)
    for k, (y, z) in enumerate(((560, 250), (470, 360))):
        a, b = sorted([xp - s * 20, xp - s * 70])
        d.box(f"clamp-{nm}{k}", [a, y - 25, z - 30, b, y + 25, z + 30], "frame", r=4)
        d.cyl(f"clamp-rod-{nm}{k}", [xp - s * 60, y, z], [xp - s * 200, y, z], 20, "chrome")
        d.lathe(f"knob-{nm}{k}", [xp - s * 45, y + 25, z], [[0, 0], [16, 0], [18, 8], [18, 22], [0, 26]], "knob")
    # hip wrap (photo): a soft grey band, U-shaped in plan and open towards the posts, its ends fixed at the posts; it
    # droops outward (the outer end ~10 deg lower), light piping along the top edge, a seam line along the front
    xo = CX + s * 600                        # outer (back of the patient)
    Y, H = 760, 250
    R = rot("z", -s * 10, [xp, Y + H / 2, 300])
    path = [[xp + s * 25, Y, 135], [xo, Y, 165], [xo, Y, 435], [xp + s * 25, Y, 465]]
    d.sweep(f"sling-{nm}", path, [26, H], "pad", shape="rect", r=10, bend=120, rot=R)
    d.tube(f"sling-rim-{nm}", [[p[0], Y + H / 2, p[2]] for p in path], 18, "leather#9a9ea3", bend=120, rot=R, soft=True)
    d.tube(f"sling-seam-{nm}", [[p[0], Y - 30, p[2]] for p in path], 28, "leather#53575c", bend=125, rot=R, soft=True)
    for zn, z in (("f", 450), ("b", 150)):
        d.box(f"sling-clip-{nm}{zn}", [min(xp, xp + s * 45), Y - 60, z - 22, max(xp, xp + s * 45), Y + 60, z + 22], "frame", r=4)
    # white support arm under the front of the wrap, and the lower curved arm with the black strut (with ball knob)
    a = rot("z", -s * 10, [xp, Y + H / 2, 300])
    d.bar(f"sup-{nm}", [xp, Y - 140, 470], [xo + s * 40, Y - 140 - 75, 470], [30, 30], "frame", r=3)
    d.tube(f"arm-low-{nm}", [[xp, 300, 470], [xo + s * 30, 340, 470], [xo + s * 50, 470, 470]], 30, "frame", bend=90)
    hydro(d, f"strut-{nm}", [xo + s * 45, 460, 485], [xo + s * 15, Y - 30, 480], body=0.55, dia=30)
    d.cyl(f"strut-stem-{nm}", [xo + s * 32, 620, 485], [xo + s * 32, 620, 540], 12, "chrome")
    d.sphere(f"strut-knob-{nm}", [xo + s * 32, 620, 548], 40, "knob")
station("l", -1)
station("r", 1)
for p in d.d["parts"]:
    if p["id"].startswith("strut"):
        p["mat"] = "black#1d1e21" if p["mat"] == "cyl" else p["mat"]
d.save()
