from h2lib import *
# XY-SL-RII children whirlpool tub with LCD (photo front-left): a control tower at the left end (white front and top,
# dark graphite left end panel with a bulging profile and a concave cut at the bottom front), a membrane/LCD panel and a
# red button on its top, a chrome dial; the tub to the right with a big rectangular glass window, tall lilac bars on the
# front and back rims, a horizontal groove low on the front, a rounded plinth edge.
W, DP, H = 1493, 1012, 1128
RY, RT = 960, 45
d = D("xy-sl-rii", [W, DP, H], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "line": "plastic#dfe3e8", "lilac": "leather#b4abe2",
    "graph": "gloss#3a3f46", "blue": "gloss#2f6fd0", "red": "gloss#d93a32", "water": "acrylic#b5dccf70",
    "panel": "plastic#e9ebee"})
TX = 340                                          # tower width
# tower: side profile (z, y): back vertical, rounded top, front down to 430, then a concave cut back to the floor
prof = (f"M 0 0 L 0 {H - 120} Q 0 {H} 120 {H} L {DP - 150} {H} Q {DP} {H} {DP} {H - 150} L {DP} 470 "
        f"Q {DP} 330 {DP - 140} 260 Q {DP - 260} 190 {DP - 250} 0 Z")
d.slab("tower-side", "side", prof, [0, TX + 10], "graph", r=14)
prof_w = (f"M 12 300 L 12 {H - 118} Q 12 {H + 2} 132 {H + 2} L {DP - 150} {H + 2} Q {DP + 2} {H + 2} {DP + 2} {H - 150} "
          f"L {DP + 2} 470 Q {DP + 2} 360 {DP - 80} 300 Z")
d.slab("tower", "side", prof_w, [26, TX + 20], "shell", r=30)
# tower top: membrane / LCD panel, red button, chrome dial with a blue ring
d.box("ctl", [70, H - 4, 380, 290, H + 0, 760], "panel", r=10)
d.add("lcd", "screen", "black#2b2f35", box=[120, H - 6, 480, 240, H + 3, 610], r=4, face="top", bezel=8)
d.decal("ctl-keys", [180, H + 0.5, 690], [170, 60], "top", "plastic#c9cdd3", soft=True)
d.lathe("btn-red", [180, H - 2, 290], [[0, 0], [20, 0], [20, 12], [15, 16], [0, 16]], "red")
d.lathe("dial-ring", [260, H - 2, 880], [[0, 0], [36, 0], [36, 8], [0, 8]], "blue")
d.lathe("dial", [260, H + 6, 880], [[0, 0], [26, 0], [26, 14], [18, 20], [0, 20]], "chrome")
logo_round(d, "logo", [0, 820, 830], 50, face="left", blue="gloss#cfd3d8")
# tub part
Y0 = 70
d.slab("end-r", "top", P(rr(W - 160, 0, W, DP, [170, 170, 0, 0])), [Y0, RY + 2], "shell", r=40)
d.box("back", [TX, Y0, 0, W - 150, RY + 2, 45], "shell", r=20)
WX0, WX1, WB, WT, WR = 540, 1260, 520, RY - 50, 50
front = (f"M {TX} {Y0} L {W - 150} {Y0} L {W - 150} {RY} L {TX} {RY} Z "
         f"M {WX0 + WR} {WB} L {WX1 - WR} {WB} Q {WX1} {WB} {WX1} {WB + WR} L {WX1} {WT} L {WX0} {WT} L {WX0} {WB + WR} Q {WX0} {WB} {WX0 + WR} {WB} Z")
d.slab("front", "front", front, [DP - 50, DP], "shell", r=18)
d.slab("glass", "front", P(rr(WX0 - 15, WB - 15, WX1 + 15, WT + 15, WR)), [DP - 36, DP - 28], "glass", r=2)
# low recessed band on the right part of the front (rounded left end)
d.slab("recess", "front", ring(rr(735, 225, W - 40, 335, [10, 10, 55, 55]), rr(745, 233, W - 40, 327, [6, 6, 47, 47])), [DP - 2, DP + 1.5], "line", r=1)
d.box("recess-shade", [745, 300, DP - 2, W - 40, 327, DP + 0.8], "plastic#e7eaee", r=2, soft=True)
d.box("plinth", [TX, 0, 40, W - 40, Y0 + 20, DP - 30], "shell", r=30)
# basin + rim, water
hole = rr(TX + 15, 60, W - 170, DP - 40, 50)
d.slab("basin-floor", "top", P(rr(TX, 40, W - 150, DP - 30, 40)), [300, 330], "inner", r=4)
U = [(TX, 40), (W - 150, 40), (W - 150, DP - 51), (W - 170, DP - 51), (W - 170, 60), (TX + 15, 60), (TX + 15, DP - 51), (TX, DP - 51)]
d.slab("walls", "top", P(U), [320, RY], "inner", r=4)
d.slab("rim", "top", ring(rr(TX - 10, 0, W, DP, [170, 170, 0, 0]), hole), [RY, RY + RT], "shell", r=18)
d.slab("water", "top", P(offset(hole, 4)), [330, 864], "water", r=2, soft=True)
# tall lilac padded bars
# the bars are the rims themselves: top level with the right end shoulder, front face flush with the front (photo)
d.box("bar-front", [TX + 10, RY - 45, DP - 75, W - 160, RY + RT + 5, DP + 4], "lilac", r=26)
d.box("bar-back", [TX + 10, RY - 20, 4, W - 160, RY + RT + 5, 78], "lilac", r=26)
d.lathe("jet", [W - 172, 820, 380], [[0, 0], [24, 0], [24, 8], [16, 12], [0, 12]], "chrome", axis="x",
        rot=rot("z", 180, [W - 172, 820, 380]))
d.save()
