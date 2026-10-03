"""NMES XY-K-SISS-A table type and TENS XY-K-SJD-A table type: one desktop housing, lower band teal / grey.
Writes only xy-k-siss-a-table.json and xy-k-sjd-a-table.json."""
from lib import *
from p4lib import ring

W = D_ = 380; H = 190
def build(id_, acc, win, label, vent_left, warn):
    d = D(id_, [W, D_, H], {"shell": "gloss#f7f8f9", "acc": acc, "win": win, "glass": "gloss#17191c",
                            "blue": "gloss#2f7fd0", "dark": "plastic#3a3f45"})
    # lower coloured body, slightly inset under the white shell
    d.add("lower", "slab", "acc", plane="top", box=[8, 0, 8, W - 8, 150, D_ - 8], radii=[54], r=14)
    # white shell: full rounded square on top, its lower edge sweeping down to the front on each side
    prof = [(182, 0), (135, 0), (133, 100), (110, 170), (80, 215), (50, 245), (25, 262)]
    d.loft("shell", [sec(y, W, D_ - z0, 58, W / 2, (D_ + z0) / 2) for y, z0 in prof][::-1], "shell", dome="end", domeH=8)
    # black glass top with three channel blocks
    d.add("top", "slab", "glass", plane="top", box=[18, 184, 18, W - 18, 190.5, D_ - 18], radii=[42], r=2)
    y = 190.6
    blocks = [[0, 0, 85 * k] for k in range(1, 3)]
    d.decal("blk-h", [226, y, 70], [250, 2], "top", "plastic#c9cdd2", soft=True,
            copies=[[0, 0, 68]] + [[0, 0, dz] for _, _, dz in blocks] + [[0, 0, dz + 68] for _, _, dz in blocks])
    d.decal("blk-v", [101, y, 104], [2, 68], "top", "plastic#c9cdd2", soft=True,
            copies=[[250, 0, 0]] + blocks + [[250, 0, dz] for _, _, dz in blocks])
    d.decal("led", [130, y, 95], [28, 20], "top", "plastic#4b4f55", soft=True,
            copies=[[60, 0, 0], [120, 0, 0]] + blocks + [[dx, 0, dz] for dx in (60, 120) for _, _, dz in blocks])
    d.decal("keys", [125, y, 122], [22, 9], "top", "plastic#d9dde2", soft=True,
            copies=[[60, 0, 0], [120, 0, 0], [180, 0, -18]] + [[dx, 0, dz + ddz] for dx, ddz in ((0, 0), (60, 0), (120, 0), (180, -18)) for _, _, dz in blocks])
    d.decal("logo", [62, y, 42], [44, 14], "top", "blue", soft=True)
    d.decal("title", [175, y, 42], [130, 7], "top", "plastic#c9cdd2", soft=True)
    d.decal("note", [275, y, 342], [70, 4], "top", "plastic#c9cdd2", soft=True, copies=[[0, 0, 10]])
    # front: recessed socket window over most of the width: translucent light frame, the panel set back,
    # 6 sockets in its upper part, a lighter lower lip and the coloured label bar at the lower right
    d.slab("win-frame", "front", ring(42, 38, W - 42, 158, 14, 10), [377, 383], "win", r=2)
    d.box("win-panel", [50, 46, 368, W - 50, 150, 379.5], "plastic#d3dde4", r=6)
    d.box("win-lip", [52, 46, 377, W - 52, 74, 380.5], "plastic#eef3f5", r=3)
    row = [[46 * k, 0, 0] for k in range(1, 6)]
    d.cyl("sock-ring", [75, 116, 377], [75, 116, 385], 30, "blue", copies=row)
    d.cyl("sock-in", [75, 116, 384], [75, 116, 387], 19, "plastic#9aa1a9", copies=row)
    d.cyl("sock-pin", [75, 116, 386], [75, 116, 389], 6, "dark", copies=row)
    d.decal("label", [270, 60, 380.7], [86, 9], "front", label, soft=True)
    # side vent grille on the coloured band
    x0, x1 = (4, 9) if vent_left else (W - 9, W - 4)
    d.box("vent", [x0, 30, 185, x1, 80, 250], "plastic#878c93" if acc.endswith("9fa4ab") else "plastic#1a8e9e", r=12)
    xs0, xs1 = (2, 6) if vent_left else (W - 6, W - 2)
    d.box("vent-slot", [xs0, 38, 197, xs1, 41, 238], "plastic#4a4f55", repeat=rep(5, [0, 8, 0]))
    if warn:
        d.decal("warn", [-1, 120, 262], [80, 26], "left", "gloss#f2cf1d", soft=True, rot=rot("x", 12, [-1, 120, 262]))
    d.save()

build("xy-k-siss-a-table", "plastic#1fa3b5", "plastic#a4dde6", "plastic#2aa7b8", True, True)
build("xy-k-sjd-a-table", "plastic#9fa4ab", "plastic#c6d5e4", "plastic#5d9ad6", False, False)
