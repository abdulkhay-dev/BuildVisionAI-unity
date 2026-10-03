from pd1_lib import *
W, D_, H = 960, 1090, 605
d = K("xyrt-103", [W, D_, H], {"top": "plastic#9fd0ec", "wt": "plastic#f4f5f6"})
T = 18


def pedestal(id, cx, cz, top, F, fh, hw, flare=0):
    # flare: the column widens under the top into a short T (photo: the table's column)
    head = [(-hw - flare, top), (-hw - flare, top - 14), (-hw, top - 14 - 2 * flare)] if flare else [(-hw, top)]
    pts = head + [(-hw, fh + 90), (-hw - 25, fh + 25), (-F + 45, fh), (-F, fh - 15), (-F, 0),
           (F, 0), (F, fh - 15), (F - 45, fh), (hw + 25, fh + 25), (hw, fh + 90)] + [(-a, b) for a, b in reversed(head)]
    d.slab(id + "-a", "front", rpoly([(cx + a, b) for a, b in pts], 22), [cz - T / 2, cz + T / 2], "wt", r=3)
    d.slab(id + "-b", "side", rpoly([(cz + a, b) for a, b in pts], 22), [cx - T / 2, cx + T / 2], "wt", r=3)


# table and two stools: light-blue tops on white cross pedestals of interlocking boards
tx, tz = 640, 330
d.box("table", [tx - 240, H - T, tz - 240, tx + 240, H, tz + 240], "top", r=6)
pedestal("tp", tx, tz, H - T, 200, 70, 55, flare=26)
for nm, (sx, sz) in (("sl", (220, 700)), ("sr", (800, 930))):
    d.box(nm, [sx - 150, 282, sz - 150, sx + 150, 300, sz + 150], "top", r=6)
    pedestal(nm + "p", sx, sz, 282, 125, 60, 50)
# toys on the table: 4 peg knobs, a wooden hammer with a purple handle, picture cards
for i, c in enumerate(("#2f6fd0", "#f2c418", "#e03028", "#2fa048")):
    x = 445 + i * 55
    d.lathe(f"peg{i}", [x, H, 140], [[26, 0], [26, 8], [22, 22], [12, 32], [6, 34], [6, 46], [0, 48]], "gloss" + c)
d.cyl("ham-head", [615, H + 22, 235], [690, H + 22, 205], 40, "wood#e2c08c")
d.cyl("ham-h", [652, H + 16, 222], [560, H + 12, 315], 16, "gloss#9a50c0")
d.decal("card", [725, H + 0.6, 125], [58, 44], "top", "plastic#fbfbf8", repeat=rep(3, [64, 0, 0]),
        copies=[[0, 0, 70 * k] for k in range(1, 6)])
d.decal("pic", [725, H + 1.0, 125], [30, 22], "top", "gloss#e0302a", repeat=rep(2, [128, 0, 0]),
        copies=[[0, 0, 140], [0, 0, 280]])
d.decal("pic2", [789, H + 1.0, 195], [30, 22], "top", "gloss#2f9a40", copies=[[0, 0, 140], [0, 0, 280], [-64, 0, 70], [64, 0, 210]])
d.decal("lbl", [600, H + 0.5, 470], [120, 26], "top", "plastic#c4e4f4", copies=[[-130, 0, 0], [0, 0, -90], [-130, 0, -90]])
d.save()
