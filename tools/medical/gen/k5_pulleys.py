"""kinesio-5: rope-and-pulley passive trainers xy-6 (hemiplegia device: base with a wooden board, two pedals,
T column with pulleys, yellow rings) and xy-6a (limbs passive trainer: floor rail, black mesh office chair,
pedal levers, front post with green D-handles, pulley column)."""
from k5lib import *

# ---------------- xy-6 ----------------
# photo: the base is clearly deeper than wide -> [480, 870, 1700] (printed 87 x 48 x 170, long side = depth)
W, DD, H = 480, 870, 1700
d = D("xy-6", [W, DD, H], {"frame": "plastic#f1f1ee", "board": "wood#4a2a1a", "foot": "rubber#141416",
                            "pul": "plastic#1b1c1f", "blue": "gloss#2a3f9a", "ring": "gloss#f2d21a",
                            "rope": "fabric#f4f4f0", "pedal": "plastic#f4f4f2", "chrome": "chrome"})
# base frame: white tube rectangle with rounded corners, black glides
d.tube("base", [[30, 25, 30], [450, 25, 30], [450, 25, 845], [30, 25, 845], [30, 25, 30]], 30, "frame", bend=45)
for x in (30, 450):
    for z in (30, 845):
        d.box(f"glide{x}-{z}", [x - 18, 0, z - 18, x + 18, 10, z + 18], "foot", r=4)
d.bar("base-mid", [30, 25, 450], [450, 25, 450], [30, 30], "frame", r=4)
# dark wooden standing board in the front part of the frame
d.box("board", [45, 26, 462, 435, 44, 832], "frame", r=4)
d.box("board-top", [52, 43, 468, 428, 46, 826], "board", r=2)
# column: rises from the middle cross tube, slightly curved near the top, T bar on top
CX, CZ = 240, 420
d.tube("column", [[CX, 40, CZ], [CX, 900, CZ - 10], [CX, 1450, CZ - 10], [CX, 1660, CZ - 40]], 46, "frame", bend=400)
d.bar("strut", [CX, 30, 120], [CX, 520, CZ - 18], [34, 34], "frame", r=4)
d.bar("strut-base", [CX, 25, 30], [CX, 25, CZ], [30, 30], "frame", r=4)
d.cyl("top-bar", [10, 1680, CZ - 40], [470, 1680, CZ - 40], 40, "frame")
d.box("top-tee", [CX - 30, 1650, CZ - 65, CX + 30, 1700, CZ - 15], "frame", r=8)
# rope routing (photo): each top end pulley has two strands: the outer one carries the big yellow hand ring, the
# inner one drops vertically to the mid pulley on the same side; from the mid pulley the rope runs out-and-down over a
# small guide pulley, then hangs down to the small yellow loop and on to the pedal's rope clamp.
TPX = {"l": 105, "r": 375}      # top pulleys (d 70)
MPX = {"l": 171, "r": 309}     # mid pulleys (d 62): outer edge under the top pulley's inner strand
GPX = {"l": 117, "r": 363}      # small guide pulleys below, further out
d.cyl("mid-bar", [100, 1130, CZ - 10], [380, 1130, CZ - 10], 34, "frame")
for s, sg in (("l", -1), ("r", 1)):
    pulley(d, f"mid-pul-{s}", [MPX[s], 1130, CZ + 30], 62, 22, "z", mat="pul")
    pulley(d, f"low-pul-{s}", [GPX[s], 1050, CZ + 30], 40, 16, "z", mat="pul")
    d.box(f"low-fork-{s}", [GPX[s] - 4, 1050, CZ + 18, GPX[s] + 4, 1118, CZ + 42], "chrome", r=2, soft=True)
# top end pulleys hanging under the bar ends on forks: black (left), blue (right)
for s, m in (("l", "pul"), ("r", "blue")):
    pulley(d, f"top-pul-{s}", [TPX[s], 1625, CZ - 40], 70, 26, "z", mat=m)
    d.box(f"top-fork-{s}", [TPX[s] - 20, 1640, CZ - 56, TPX[s] + 20, 1664, CZ - 24], "chrome", r=3)
# blue scale strip on the column front, a clear clamp block under it
d.box("scale", [CX - 14, 820, CZ + 20, CX + 14, 1080, CZ + 26], "blue", r=3)
for k in range(9):
    d.box(f"tick{k}", [CX - 9, 835 + k * 27, CZ + 25.5, CX + 2, 839 + k * 27, CZ + 27], "plastic#f4f6fb", soft=True)
d.box("scale-clamp", [CX - 26, 760, CZ - 30, CX + 26, 805, CZ + 30], "acrylic#cfe0f0b0", r=6)
for s, sg in (("l", -1), ("r", 1)):
    t, m, g = TPX[s], MPX[s], GPX[s]
    xo = t + sg * 35          # outer strand of the top pulley
    xi = t - sg * 35          # inner strand
    # big hand ring: a wide rounded stirrup with a small peak where the rope ties on
    rc, ry = xo, 960
    d.tube(f"ring-{s}", [[rc, ry + 74, CZ - 40], [rc + 58, ry + 64, CZ - 40], [rc + 60, ry, CZ - 40],
                         [rc - 60, ry, CZ - 40], [rc - 58, ry + 64, CZ - 40], [rc, ry + 74, CZ - 40]], 20, "ring",
           bend=24)
    rope(d, f"rope-top-{s}", [[xo, 1625, CZ - 40], [xo, ry + 76, CZ - 40]])
    rope(d, f"rope-in-{s}", [[xi, 1625, CZ - 40], [xi, 1135, CZ + 30]])
    rope(d, f"rope-mg-{s}", [[m, 1099, CZ + 30], [g - sg * 20, 1052, CZ + 30]])
    # small yellow loop under the guide pulley, then on down to the pedal clamp
    d.tube(f"loop-{s}", [[g - 20, 710, CZ + 30], [g + 20, 710, CZ + 30], [g + 16, 630, CZ + 30], [g - 16, 630, CZ + 30],
                        [g - 20, 710, CZ + 30]], 16, "ring", bend=14)
    rope(d, f"rope-mid-{s}", [[g + sg * 20, 1050, CZ + 30], [g, 718, CZ + 30]])
    px = 137 if s == "l" else 347
    rope(d, f"rope-low-{s}", [[g, 624, CZ + 30], [px, 112, 395]])
# pedals: white plates hinged at the column, rear ends raised
for s, x0 in (("l", 75), ("r", 285)):
    pr = rot("x", 12, [x0, 60, 430])
    d.box(f"pedal-{s}", [x0, 50, 80, x0 + 125, 68, 430], "pedal", r=8, rot=pr)
    d.box(f"pedal-rib-{s}", [x0 + 10, 66, 100, x0 + 115, 70, 410], "plastic#e6e7e8", r=4, rot=pr)
    d.box(f"pedal-clip-{s}", [x0 + 52, 66, 380, x0 + 72, 110, 405], "pul", r=4, rot=pr)
    d.bar(f"pedal-link-{s}", [x0 + 62, 30, 440], [x0 + 62, 75, 430], [26, 26], "frame", r=4)
d.save()

# ---------------- xy-6a ----------------
# photo: the floor rail runs from the chair to the pulley column -> [700, 1600, 1600] (printed 160 x 70 x 160, long
# side = depth); chair at the front (z = 1600) facing the column at the back
W, DD, H = 700, 1600, 1600
d = D("xy-6a", [W, DD, H], {"frame": "plastic#f2f2ef", "cap": "rubber#141416", "mesh": "fabric#1c1c1e",
                             "seat": "fabric#18181a", "plastic": "plastic#1a1b1d", "pul": "plastic#1b1c1f",
                             "green": "gloss#1f8a3c", "rope": "fabric#121214", "pedal": "plastic#232427",
                             "chrome": "chrome", "wood": "wood#6a3a24"})
CX = 350
# floor: two T feet along x and the long rail along z
for z in (70, 1470):
    d.bar(f"tfoot{z}", [0, 25, z], [W, 25, z], [60, 50], "frame", r=4)
    d.box(f"tcap{z}a", [-2, 0, z - 31, 20, 52, z + 31], "cap", r=3, copies=[[W - 18, 0, 0]])
d.bar("rail", [CX, 25, 70], [CX, 25, 1500], [70, 50], "frame", r=4)
d.box("rail-slot", [CX - 22, 50, 900, CX + 22, 54, 1380], "plastic", r=2)
d.box("rail-wood", [CX - 36, 20, 1180, CX + 36, 52, 1300], "wood", r=3)
# --- pulley column at the back: vertical up to the mid bar, then curving toward the chair into the top bar
TZ = 175
d.sweep("column", [[CX, 50, 70], [CX, 1000, 70], [CX, 1300, 90], [CX, 1490, 140], [CX, 1560, TZ]], [60, 50], "frame",
        shape="rect", r=5, bend=260)
d.bar("top-bar", [CX - 230, 1575, TZ], [CX + 230, 1575, TZ], [50, 40], "frame", r=4)
d.box("top-cap-l", [CX - 238, 1550, TZ - 22, CX - 226, 1600, TZ + 22], "cap", r=3, copies=[[464, 0, 0]])
for x in (CX - 200, CX + 200):
    pulley(d, f"top-pul{x}", [x, 1515, TZ], 80, 24, "z", mat="pul")
    d.box(f"top-fork{x}", [x - 5, 1515, TZ - 18, x + 5, 1560, TZ + 18], "chrome", r=2, soft=True)
d.bar("mid-bar", [CX - 200, 1080, 100], [CX + 200, 1080, 100], [50, 40], "frame", r=4)
d.box("mid-cap-l", [CX - 208, 1055, 78, CX - 196, 1105, 122], "cap", r=3, copies=[[404, 0, 0]])
for x in (CX - 175, CX + 175):
    pulley(d, f"mid-pul{x}", [x, 1025, 100], 70, 22, "z", mat="pul")
    d.box(f"mid-fork{x}", [x - 5, 1025, 84, x + 5, 1060, 116], "chrome", r=2, soft=True)
    d.box(f"mid-blk{x}", [x - 22, 1100, 84, x + 22, 1122, 116], "cap", r=3)
d.box("collar", [CX - 38, 860, 42, CX + 38, 900, 98], "frame", r=4)
# rope eye on the column front at ~780 where the pedal ropes gather
d.lathe("eye", [CX, 780, 95], [[0, 0], [14, 0], [14, 12], [0, 12]], "chrome", axis="z")
EYE = [CX, 780, 108]
# horizontal arm from the column to the front post
FZ = 760
d.bar("arm", [CX, 520, 95], [CX, 520, FZ], [50, 40], "frame", r=4)
d.bar("front-post", [CX, 50, FZ], [CX, 1000, FZ], [50, 40], "frame", r=4)
d.bar("front-post2", [CX + 34, 300, FZ + 6], [CX + 34, 960, FZ + 6], [22, 22], "frame", r=4)
d.cyl("handle-bar", [CX - 150, 1000, FZ], [CX + 150, 1000, FZ], 40, "plastic")   # black foam cross bar
# green stirrup handles (green moulded grips): an upper pair hanging from the black cross bar, a lower pair on ropes
def dhandle(id, x, y, z):
    d.tube(id, [[x - 22, y, z], [x + 22, y, z], [x + 52, y - 120, z], [x - 52, y - 120, z], [x - 22, y, z]], 22,
           "green", bend=22)
    d.cyl(id + "-grip", [x - 42, y - 116, z], [x + 42, y - 116, z], 32, "green")
HX = 120
for s, sg in (("l", -1), ("r", 1)):
    x = CX + sg * HX
    tp, mp = CX + sg * 200, CX + sg * 175
    dhandle(f"dh-up-{s}", x, 990, FZ + 30)
    dhandle(f"dh-lo-{s}", x, 830, FZ + 30)
    # top pulley: the outer strand runs long and diagonal down to the upper handle, the inner one drops to the
    # mid pulley; the mid pulley sends one rope to the lower handle and one down to the pedal lever
    rope(d, f"rope-up-{s}", [[tp + sg * 40, 1515, TZ + 10], [x, 995, FZ + 30]], mat="rope", dd=5)
    rope(d, f"rope-top-{s}", [[tp - sg * 40, 1515, TZ], [mp - sg * 35, 1030, 100]], mat="rope", dd=5)
    rope(d, f"rope-lo-{s}", [[mp, 990, 112], [x, 835, FZ + 30]], mat="rope", dd=5)
    rope(d, f"rope-ped-{s}", [[mp + sg * 35, 1025, 112], [CX + sg * 60, 330, FZ + 200]], mat="rope", dd=5)
    # the lower handle's tail rope runs back to the column eye, and from the eye down to the pedal
    rope(d, f"rope-eye-{s}", [[x, 712, FZ + 30], EYE], mat="rope", dd=5)
    rope(d, f"rope-eye2-{s}", [EYE, [CX + sg * 85, 310, FZ + 230]], mat="rope", dd=5)
# pedals: two black foot plates on levers pivoting at the front post, toward the chair
for s, sx, ang in (("l", -1, 14), ("r", 1, -8)):
    x = CX + sx * 85
    d.bar(f"lever-{s}", [CX + sx * 30, 330, FZ + 20], [x, 300, FZ + 230], [26, 26], "chrome", r=3)
    d.box(f"pedal-{s}", [x - 65, 280, FZ + 180, x + 65, 310, FZ + 450], "pedal", r=10,
          rot=rot("x", ang, [x, 295, FZ + 230]))
    d.box(f"pedal-heel-{s}", [x - 65, 300, FZ + 180, x + 65, 350, FZ + 200], "pedal", r=8,
          rot=rot("x", ang, [x, 295, FZ + 230]))
d.cyl("pedal-axle", [CX - 40, 330, FZ + 20], [CX + 40, 330, FZ + 20], 30, "frame")
knob(d, "post-knob", [CX, 640, FZ + 20], axis="z", dd=32)
# --- black mesh office chair on a white mount on the rail (facing the column, -z)
SZ = 1300
d.box("chair-mount", [CX - 50, 50, SZ - 60, CX + 50, 130, SZ + 60], "frame", r=6)
d.cyl("gas", [CX, 130, SZ], [CX, 380, SZ], 50, "plastic")
d.cyl("gas-top", [CX, 330, SZ], [CX, 420, SZ], 34, "chrome")
d.box("seat-plate", [CX - 120, 410, SZ - 140, CX + 120, 430, SZ + 140], "plastic", r=8)
d.box("seat", [CX - 245, 420, SZ - 250, CX + 245, 500, SZ + 230], "seat", r=40, puff=10)
d.bar("lever", [CX + 100, 418, SZ - 40], [CX + 240, 400, SZ - 60], [16, 10], "plastic", r=3)
# backrest: mesh panel in a black frame, behind the seat (z larger), leaning back
br = rot("x", 10, [CX, 520, SZ + 230])
d.tube("back-frame", [[CX - 215, 560, SZ + 235], [CX - 225, 1010, SZ + 235],
       [CX + 225, 1010, SZ + 235], [CX + 215, 560, SZ + 235], [CX - 215, 560, SZ + 235]], 30, "plastic", bend=60, rot=br)
d.box("back-mesh", [CX - 212, 565, SZ + 232, CX + 212, 1005, SZ + 238], "acrylic#1e1e21c8", r=40, rot=br)
for k in range(5):
    d.bar(f"lumbar{k}", [CX - 100 + k * 50, 600, SZ + 228], [CX - 100 + k * 50, 720, SZ + 228], [26, 12], "plastic", r=5,
          rot=br)
d.bar("back-spine", [CX, 440, SZ + 150], [CX, 620, SZ + 250], [60, 20], "plastic", r=6)
# armrests: black loops from the seat sides
for s, x in (("l", CX - 255), ("r", CX + 255)):
    d.tube(f"arm-{s}", [[x, 440, SZ + 120], [x + (-10 if x < CX else 10), 660, SZ + 110], [x, 660, SZ - 160],
                        [x, 500, SZ - 190]], 30, "plastic", bend=60)
d.save()
