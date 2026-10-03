from h1lib import *
# XY-SL-BVII four-limb hydro/electro bath (printed 1150 × 1030 × 740 = the base box; the arm troughs reach ~950):
# sky-blue lower shell, light-blue top: a control block on the left (touch screen + chrome square knobs) and the
# foot-basin tray on the right; two light-blue arm troughs with domed elbow ends on chrome stalks.
d = D("xy-sl-bvii", [1150, 1030, 990], {
    "sky": "gloss#3aa6e6", "light": "gloss#a9d6f3", "inner": "gloss#bfe1f6", "grey": "plastic#9ea7b0",
    "dark": "black#2a2d31", "green": "gloss#2fae7a"})
CX, CZ = 340, 655
d.loft("lower", [sec(40, 590, 660, 190, CX, CZ), sec(110, 655, 728, 205, CX, CZ), sec(300, 680, 750, 210, CX, CZ),
                 sec(482, 680, 750, 210, CX, CZ)], "sky")
d.cyl("foot", [130, 0, 420], [130, 42, 420], 60, "dark", copies=[[420, 0, 0], [0, 0, 480], [420, 0, 480]])
# control block (front), rounded top edges
d.slab("block", "top", "M 0 680 L 680 680 L 680 820 Q 680 1030 470 1030 L 210 1030 Q 0 1030 0 820 Z", [478, 740], "light", r=45)
# foot-basin tray (back) with an open basin, a divider, light floor
hole = rr(55, 330, 625, 662, 70)
d.slab("tray", "top", ring(rr(0, 280, 680, 690, [210, 1, 1, 210]), hole), [478, 610], "light", r=24)
d.slab("tray-floor", "top", P(hole), [470, 492], "inner", r=4)
d.box("divider", [328, 488, 330, 352, 540, 662], "light", r=12)
# touch screen + chrome knobs on the block
d.add("screen", "screen", box=[110, 734, 720, 350, 746, 860], r=12, face="top", bezel=0, mat="grey",
      print="med_xy-sl-bvii_screen")
for i, (x, z) in enumerate(((70, 780), (150, 715), (440, 950), (630, 900))):
    d.box(f"knob{i}", [x - 26, 740, z - 26, x + 26, 800, z + 26], "chrome", r=8)
    d.box(f"knob{i}-cap", [x - 18, 800, z - 18, x + 18, 806, z + 18], "green" if i % 2 else "gloss#2f7fd8", r=4, soft=True)
d.lathe("knob-round", [545, 740, 925], [[0, 0], [24, 0], [24, 40], [18, 50], [0, 50]], "chrome")
# front socket plate, side logo
d.box("socket", [140, 560, 1026, 240, 650, 1036], "grey", r=8)
d.decal("socket-dots", [190, 605, 1036.5], [60, 20], "front", "dark", soft=True)
d.lathe("logo", [681, 300, 760], [[0, 0], [75, 0], [75, 3], [0, 3]], "gloss#58b3ea", axis="x", soft=True)
# arm troughs along x (photo: both long sides face the front, the domed elbow hood at the left end):
# sky-blue body, light rim band, light-blue domed hood over the elbow end; chrome stalks.
# Review 2026-10-02: troughs turned from z to x, left trough over the back of the control block (its stalk at 30 %
# from the elbow end), the right one lower on an S stalk from the rim of the foot basin; H 950 -> 990.
def trough(nm, x0, x1, z0, z1, y0, y1):
    w = z1 - z0
    out = rr(x0, z0, x1, z1, [70, 70, w / 2 - 2, w / 2 - 2])
    inn = rr(x0 + 140, z0 + 24, x1 - 24, z1 - 24, 50)
    d.slab(nm, "top", ring(out, inn), [y0, y1 - 40], "sky", r=30)
    d.slab(nm + "-rim", "top", ring(offset(out, 3), inn), [y1 - 45, y1], "light", r=20)
    d.slab(nm + "-floor", "top", P(inn), [y0 + 30, y0 + 50], "inner", r=4)
    d.loft(nm + "-elbow", [sec(y1 - 50, 160, w + 4, 78, x0 + 82, (z0 + z1) / 2),
                           sec(y1, 160, w + 4, 78, x0 + 82, (z0 + z1) / 2)], "light", dome="end", domeH=55)
trough("trough-l", 250, 770, 630, 860, 790, 990)
trough("trough-r", 650, 1150, 260, 490, 700, 900)
d.cyl("stalk-l", [410, 740, 745], [410, 792, 745], 64, "chrome")
d.lathe("stalk-l-nut", [410, 735, 745], [[0, 0], [48, 0], [48, 30], [0, 30]], "chrome")
d.tube("stalk-r", [[660, 595, 375], [668, 640, 375], [700, 660, 375], [712, 702, 375]], 40, "chrome", bend=30)
d.save()
