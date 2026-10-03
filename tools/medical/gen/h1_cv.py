from h1lib import *
# XY-SL-CV walk-in tub: white box tub with a flat rim, horizontal ribs on the left side, a U-shaped front door with a
# grey frame line, XIANGYU logo, latch blocks and a top handle, a louvre panel right of the door; on the rim an armrest,
# buttons, three faucet knobs, spout, drain knob, a lever switch and a hand shower on a post. Rim 1000 (printed), shower
# head to ~1170.
d = D("xy-sl-cv", [1300, 750, 1170], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "frame": "plastic#c3c9d0", "line": "plastic#dfe3e8",
    "blue": "gloss#2f7fd8", "dark": "black#2b2e33", "grey": "plastic#aeb5bd"})
RY, RT = 935, 65
FZ = 742                                      # front face
hole = rr(95, 95, 1040, 640, 70)
d.slab("body", "top", ring(rr(16, 8, 1296, FZ, 24), rr(60, 60, 1080, 690, 60)), [25, RY + 2], "shell", r=10)
d.box("plinth", [30, 0, 20, 1280, 30, FZ - 15], "line", r=6)
tub(d, "", None, hole, rr(10, 0, 1300, 750, 26), RY, RT, 160, rr(75, 75, 1060, 660, 70), rim_r=14)
# inner seat at the left
d.box("seat", [100, 160, 100, 520, 470, 630], "inner", r=30)
# left side: horizontal ribs
d.box("rib", [0, 120, 60, 20, 210, 690], "shell", r=8, repeat=rep(5, [0, 160, 0]))
# door (U shape) with a grey frame line, proud of the front
# Review 2026-10-02: door wider (photo: 240 .. 1085, the louvre right next to it), big round corner at the bottom left
# only (J shape, the hinge side right is nearly square), real XIANGYU MEDICAL lettering, armrest = grab handle on the
# inner back wall.
DX0, DX1, DY0, DY1, DR, DR2 = 240, 1085, 220, 990, 250, 50
door = f"M {DX0} {DY1} L {DX0} {DY0 + DR} Q {DX0} {DY0} {DX0 + DR} {DY0} L {DX1 - DR2} {DY0} Q {DX1} {DY0} {DX1} {DY0 + DR2} L {DX1} {DY1} Z"
fr = 16
frame = (f"M {DX0 - fr} {DY1} L {DX0 - fr} {DY0 + DR} Q {DX0 - fr} {DY0 - fr} {DX0 + DR} {DY0 - fr} L {DX1 - DR2} {DY0 - fr} "
         f"Q {DX1 + fr} {DY0 - fr} {DX1 + fr} {DY0 + DR2} L {DX1 + fr} {DY1} Z")
d.slab("door-frame", "front", frame, [FZ - 4, FZ + 6], "frame", r=3)
d.slab("door", "front", door, [FZ, FZ + 14], "shell", r=5)
from p1lib import text
d.lathe("logo", [585, 735, FZ + 14], [[0, 0], [48, 0], [48, 1.5], [0, 1.5]], "blue", axis="z", soft=True)
d.lathe("logo-c", [585, 735, FZ + 15.5], [[0, 0], [20, 0], [20, 1], [0, 1]], "shell", axis="z", soft=True)
text(d, "logo-t1", "XIANGYU", [650, 750, FZ + 15], 42, "blue", stroke=8)
text(d, "logo-t2", "MEDICAL", [650, 690, FZ + 15], 42, "blue", stroke=8)
d.box("label", [290, 760, FZ + 13, 420, 930, FZ + 15], "plastic#eceef0", r=2, soft=True)
d.box("label-line", [305, 901, FZ + 14.5, 405, 904, FZ + 15.5], "plastic#cfd3d8", repeat=rep(8, [0, -18, 0]), soft=True)
d.box("latch", [DX0 - 25, DY1 - 50, FZ - 10, DX0 + 30, DY1 + 6, FZ + 22], "grey", r=6, copies=[[DX1 - DX0 - 5, 0, 0]])
# louvre panel right of the door
d.box("louvre", [1115, 260, FZ - 2, 1272, 900, FZ + 6], "shell", r=6)
d.box("louvre-slot", [1140, 300, FZ + 5, 1247, 312, FZ + 8], "line", r=3, repeat=rep(8, [0, 75, 0]), soft=True)
# rim: armrest, buttons (back), faucets / spout / drain / switch / shower (right end)
T = RY + RT
d.tube("armrest", [[380, T - 120, 96], [400, T - 70, 135], [560, T - 70, 135], [580, T - 120, 96]], 32, "shell", bend=40)
d.lathe("btn", [640, T - 4, 50], [[0, 0], [16, 0], [16, 6], [0, 7]], "chrome", repeat=rep(3, [45, 0, 0]))
d.lathe("knob", [1180, T - 4, 300], [[0, 0], [24, 0], [24, 40], [20, 50], [0, 50]], "chrome", repeat=rep(3, [0, 0, 70]))
d.tube("spout", [[1080, T - 4, 70], [1080, T + 40, 70], [1080, T + 40, 140]], 30, "chrome", bend=20)
d.lathe("drain", [1090, T - 4, 560], [[0, 0], [30, 0], [30, 20], [22, 30], [0, 30]], "chrome")
d.box("switch-base", [1015, T - 4, 640, 1075, T + 40, 720], "grey", r=12)
d.bar("switch", [1045, T + 30, 680], [1000, T + 150, 620], [26, 20], "shell", r=8)
d.cyl("shower-post", [1180, T - 4, 120], [1180, T + 120, 120], 26, "chrome")
d.cyl("shower-grip", [1180, T + 60, 140], [1180, T + 130, 150], 30, "chrome")
d.lathe("shower-head", [1180, T + 140, 160], [[0, 0], [50, 0], [52, 10], [24, 22], [0, 24]], "dark", axis="z",
        rot=rot("x", -25, [1180, T + 140, 160]))
d.save()
