"""YHZ-IAJ steel traction table (micro-switch) — batch table-4. Writes only yhz-iaj."""
from t4lib import *

d = D("yhz-iaj", [2000, 650, 650], {
    "tray": "plastic#f3f4f6", "pad": "leather#ab8fae", "cab": "plastic#f1f2f4", "seam": "plastic#a7abb2",
    "frame": "plastic#55595f", "cap": "rubber#1f2124", "strap": "fabric#aeb2b8", "edge": "fabric#5a62a8", "buck": "plastic#3d5a4c", "harn": "leather#c6a6cc",
    "panel": "gloss#1f7c9e", "white": "plastic#f4f6f8", "dark": "plastic#26292e", "chrome": "chrome"})
W, DP = 2000, 650

def outline(id, x0, y0, x1, y1, z, mat="seam", t=3):
    d.decal(id + "-t", [(x0 + x1) / 2, y1, z], [x1 - x0, t], "front", mat, soft=True, copies=[[0, y0 - y1, 0]])
    d.decal(id + "-s", [x0, (y0 + y1) / 2, z], [t, y1 - y0], "front", mat, soft=True, copies=[[x1 - x0, 0, 0]])

# --- two white trays with lilac pads, split in the middle
for nm, x0, x1 in (("a", 0, 882), ("b", 908, 2000)):
    top_pad(d, f"tray-{nm}", x0, x1, 0, DP, 590, 618, "tray", cr=70, r=8)
    top_pad(d, f"pad-{nm}", x0 + 22, x1 - 22, 22, DP - 22, 615, 650, "pad", cr=50, r=12)
# --- dark steel top frame under the trays, chrome lock knob, bolt
d.box("frame", [120, 560, 590, 1880, 590, 625], "frame", r=4, copies=[[0, 0, -565]])
d.box("frame-end", [120, 560, 60, 160, 590, 590], "frame", r=4, copies=[[1720, 0, 0]])
d.cyl("lock", [705, 575, 625], [705, 575, 650], 24, "chrome", soft=True)
d.cyl("lock-stem", [705, 575, 615], [705, 575, 628], 12, "chrome", soft=True)
d.cyl("bolt", [237, 575, 625], [237, 575, 633], 16, "chrome", soft=True)
# --- white sheet-steel cabinet, three front panels
d.box("cab", [210, 150, 70, 1800, 560, 590], "cab", r=6)
z = 590.5
d.decal("seam", [903, 355, z], [4, 400], "front", "seam", soft=True, copies=[[360, 0, 0]])
outline("pl", 240, 175, 880, 540, z)
outline("pr", 1285, 175, 1775, 540, z)
d.decal("sticker", [345, 430, z + 0.3], [70, 105], "front", "plastic#f8f8f6", soft=True)
d.decal("sticker-txt", [345, 470, z + 0.6], [56, 4], "front", "plastic#8d9198", soft=True, repeat=rep(9, [0, -9, 0]))
d.decal("sticker-hd", [325, 476, z + 0.9], [18, 10], "front", "plastic#5d7fa6", soft=True)
# --- blue control panel (middle door)
d.box("panel", [938, 245, 586, 1236, 495, 594], "panel", r=3)
z = 594.6
d.decal("p-logo", [962, 474, z], [20, 20], "front", "white", soft=True)
d.decal("p-title", [1105, 476, z], [150, 10], "front", "white", soft=True)
d.decal("p-sub", [1105, 461, z], [150, 5], "front", "white", soft=True)
d.decal("p-led", [1100, 420, z], [64, 30], "front", "dark", soft=True)
d.decal("p-digits", [1100, 420, z + 0.4], [50, 18], "front", "gloss#ff3b30", soft=True)
d.decal("p-led-txt", [1100, 395, z], [60, 5], "front", "white", soft=True)
d.decal("p-sw", [985, 412, z], [20, 28], "front", "dark", soft=True)
d.decal("p-sw-g", [985, 418, z + 0.4], [14, 10], "front", "gloss#39b54a", soft=True)
d.cyl("p-go", [1035, 345, 594], [1035, 345, 600], 22, "gloss#36b24a", soft=True)
d.cyl("p-stop", [1165, 345, 594], [1165, 345, 600], 22, "gloss#e8452c", soft=True)
d.decal("p-btn-txt", [1035, 368, z], [26, 5], "front", "white", soft=True, copies=[[130, 0, 0]])
d.cyl("p-knob", [1080, 290, 594], [1080, 290, 604], 17, "dark", soft=True, repeat=rep(3, [21, 0, 0]))
d.decal("p-foot", [1087, 262, z], [200, 5], "front", "white", soft=True, copies=[[0, -12, 0]])
d.decal("p-spec", [1195, 300, z], [50, 20], "front", "white", soft=True)
# --- 4 white square legs, black feet
d.box("leg", [215, 40, 75, 260, 152, 120], "cab", r=3, copies=corners(215, 75, 1745, 530))
d.box("foot", [212, 0, 72, 263, 42, 123], "cap", r=4, copies=corners(212, 72, 1742, 527))
# --- grey traction straps (clips at the ends): one along the back edge of each pad, one running from the
#     front part of the end to the middle of the harness (photo)
for nm, xa, xb, sg in (("a", 45, 640, 1), ("b", 1955, 1150, -1)):
    d.strap(f"st-{nm}0", [[xa, 651, 88], [xb, 652, 135]], [30, 3], "strap", soft=True)
    d.strap(f"st-{nm}1", [[xa, 651, 470 if nm == "a" else 340], [xb, 652, 340]], [46 if nm == "a" else 30, 3], "strap", soft=True)
    d.box(f"clip-{nm}", [xa - 14, 648, 75, xa + 14, 657, 102], "dark", r=2, soft=True,
          copies=[[0, 0, (470 if nm == "a" else 340) - 88]])
# --- harness: thin contoured lilac flaps (chest on the left tray, pelvis on the right) with grey webbing
#     (blue edging): transverse straps whose tabs stand up at the back, longitudinal straps bridging the split,
#     dark green buckles
for nm, x0, x1 in (("c", 615, 870), ("p", 920, 1170)):
    m = (x0 + x1) / 2
    pts = [(x0 + 20, 150), (m, 125), (x1 - 15, 150), (x1, 330), (x1 - 15, 510), (m, 530), (x0 + 20, 510), (x0 - 10, 330)]
    d.add(f"harn-{nm}", "slab", "harn", plane="top", outline=poly_path(round_poly(pts, 45)), w=[650, 668], r=6)
    for k, xx in enumerate((x0 + 55, x1 - 70)):
        path = [[xx, 670, 545], [xx, 670, 165], [xx + 4, 688, 138], [xx + 6, 702, 130]]
        d.strap(f"tr-{nm}{k}", path, [44, 3], "edge", bend=20, soft=True)
        d.strap(f"tr-{nm}{k}g", [[q[0], q[1] + 1.5, q[2]] for q in path], [36, 3], "strap", bend=20, soft=True)
    d.box(f"buckle-{nm}", [x0 + 38, 671, 420, x0 + 92, 683, 470], "buck", r=3, soft=True, copies=[[x1 - x0 - 125, 0, 0]])
for k, zz in enumerate((255, 405)):
    path = [[640, 670, zz], [880, 672, zz], [895, 676, zz], [910, 672, zz], [1150, 670, zz]]
    d.strap(f"lg-{k}", path, [42, 3], "edge", bend=10, soft=True)
    d.strap(f"lg-{k}g", [[q[0], q[1] + 1.5, q[2]] for q in path], [34, 3], "strap", bend=10, soft=True)
d.box("buckle-m", [860, 675, 230, 935, 689, 280], "buck", r=3, soft=True, copies=[[0, 0, 150]])
d.save()
