"""wall-of-blisters: sky-blue bear-ear wall panel with a blue bubble-water display.
The bubble picture is the photo's own panel sampled on a 40 x 72 grid (left half, mirrored about the seam as on the
photo) and reduced to 8 blues by k-means (tools: a one-off sampling of reference/wall-of-blisters.jpg)."""
from s2lib import *

# k-means centres, the 3 lightest lifted towards white (the photo's top / bottom sparkle; the studio light dulls them)
COLS = ["14317b", "144394", "1658a6", "1b71b7", "2d95d2", "4cb2e4", "7cccf0", "c4ecfb"]
GRID = """\
46676777777767576757
65575767665767666767
54475656566767776667
54575646576767676757
45554657475667666757
64565645466766565656
55554545575766466656
45465746565766556545
45355646466666454546
66454634454655454646
46443524455444465535
25543425434655464435
24343544464545465445
23433545354546434445
33233534254445433534
22231425233533334555
03221524164433353433
14132324143444353425
04242323133345333532
03231213122234332323
04110124121333221422
13010313153312322322
21020112132223312210
12132202033324322211
00112401022212222112
00130322121212231111
20110112221312211120
21000113121212211120
00010002131111111020
20020101011211101110
10020002010112111012
00020101010011100011
00010101010001100221
20010001011001101100
00111201012111200110
00000101000011110010
00110001000011100010
00100001001212110110
00110201011111111110
00121200001000111111
21120201012001121211
01220302020111001210
31120212011212001223
10010113011323122221
01111012022213121011
22110001011312131111
31210001112323233312
11210113132223133331
20000213042232252233
20110212023333243444
41110313153325242422
42432423142334241434
52331423342323332434
42321223342434332334
32321235344434332235
42331535352434353323
32352424533644344444
63432534443546443544
62432424442635353644
53433215443445442534
52334335463446353544
51332535453456365556
51324564463445354655
72534454553656665655
43623334454556555666
61532435664645465656
42432466444656255747
64621445244646365577
65646454466656575776
64534454455646664677
52643463463556374777
53756463644635374777"""

W, H, T = 570, 900, 90
d = D("wall-of-blisters", [W, T, H], {
    "case": "plastic#45a6de", "dark": "plastic#3a92c4", "grille": "plastic#2a7fb4"})
# measured on the photo (231 px over the ears = 570 mm): ears r 88 centred (88, 812), body 25..545 up to 880
panel(d, W, H, T, "case", inset=25, ear_c=(88, 812), ear_r=88, yt=880, grille="grille", grille_d=60,
      grille_off=(-29, 34), bumps=(29, 6, 143, 113), logo=(286, 849), logo_d=44,
      buttons=([215, 288, 357], 61, 33), case_dark="dark")
d.add("bezel", "slab", "black#141416", plane="front", box=[79, 125, T - 2, 491, 811, T + 5], radii=[16], r=3)
x0, x1, y0, y1 = 93.5, 476.5, 140, 797
rows = GRID.split("\n")
R, C2 = len(rows), len(rows[0])
cw, rh = (x1 - x0) / (2 * C2), (y1 - y0) / R
d.box("water", [x0, y0, T + 3, x1, y1, T + 6], "gloss#" + COLS[0])
F = T + 6
# each column's vertical runs of one level → one box; one part per (level, run length) with copies, mirrored in x
runs = {}
for i in range(C2):
    j = 0
    while j < R:
        lv = int(rows[j][i]); k = j
        while k < R and rows[k][i] == rows[j][i]: k += 1
        if lv > 0: runs.setdefault((lv, k - j), []).append((i, R - k))   # (column, row from the bottom)
        j = k
for (lv, n), cells in sorted(runs.items()):
    (i0, j0), rest = cells[0], cells[1:]
    bx, by = x0 + i0 * cw, y0 + j0 * rh
    d.box(f"bub{lv}-{n}", [bx, by, F - 0.4, bx + cw, by + n * rh, F + 0.3], "gloss#" + COLS[lv], soft=True,
          mirror="x", copies=[[(i - i0) * cw, (j - j0) * rh, 0] for i, j in rest] or None)
d.box("seam", [W / 2 - 2.5, y0, F, W / 2 + 2.5, y1, F + 0.8], "plastic#4f8bae", soft=True)
d.save()
