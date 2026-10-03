from h2lib import *
# XY-SL-CVIII dry hydromassage table, standard and luxury (hood) modes. Photos: front-RIGHT views. White glossy body
# with rounded plan corners, a thick black top band and a dark mattress field with a light seam line, a thin black
# groove line around at ~430 crossed at the left end of the front by a black four-pointed star, a black bottom band on
# the right 55 % with a ramp at its start and the white logo, small chrome feet; a small monitor on a white square pole
# behind the table. Luxury: a white hood over the head (left) end with the lid swung up, a black strip with a speaker.


def build(id, H, hood):
    W, DP = 2100, 900
    Z0 = 60                                      # body back (the monitor pole stands behind it)
    d = D(id, [W, DP, H], {
        "shell": "gloss#f8f9fa", "black": "gloss#1d1f22", "field": "leather#2b2e33", "line": "plastic#9aa0a8",
        "white": "gloss#ffffff"})
    plan = rr(10, Z0, W - 10, DP - 10, 100)
    d.slab("body", "top", P(plan), [40, 600], "shell", r=25)
    d.slab("top-band", "top", P(rr(0, Z0 - 10, W, DP, 110)), [590, 700], "black", r=38)
    d.box("field", [70, 690, Z0 + 50, W - 70, 708, DP - 60], "field", r=24, puff=4)
    d.box("seam", [560, 707, DP - 92, W - 90, 711, DP - 86], "line", r=2, soft=True)
    d.box("seam-x", [560, 707, Z0 + 70, 566, 711, DP - 86], "line", r=2, soft=True)
    d.slab("groove", "top", ring(rr(6, Z0 - 4, W - 6, DP - 6, 104), plan), [424, 440], "black", r=2)
    # black four-pointed star on the front left (concave arms: up, down, left to the corner, right into the groove)
    F = DP - 10
    star = ("M 312 590 L 330 590 Q 314 452 340 442 Q 400 438 760 438 L 760 426 Q 400 424 336 420 Q 284 400 262 60 "
            "L 244 60 Q 268 398 262 422 Q 220 424 112 422 L 112 440 Q 232 440 272 446 Q 300 458 312 590 Z")
    d.slab("star", "front", star, [F - 4, F + 2], "black", r=1)
    # black bottom band on the right part with a ramp at its start; white logo on it
    d.slab("band", "top", P(rr(1150, Z0 - 3, W - 7, DP - 7, [103, 103, 0, 0])), [38, 270], "black", r=10)
    d.slab("band-ramp", "front", "M 980 38 Q 990 270 1160 270 L 1160 38 Z", [F - 6, F + 3], "black", r=6)
    logo_round(d, "logo", [1260, 150, F + 3], 80, blue="gloss#f2f3f5", white="gloss#1d1f22")
    text(d, "logo-t1", "XIANGYU", [1320, 160, F + 3.5], 36, "white")
    text(d, "logo-t2", "MEDICAL", [1320, 104, F + 3.5], 36, "white")
    d.lathe("foot", [200, 0, Z0 + 80], [[0, 0], [16, 0], [16, 42], [0, 42]], "chrome",
            copies=[[1700, 0, 0], [0, 0, 640], [1700, 0, 640], [850, 0, 0], [850, 0, 640]])
    # monitor on a white square pole behind the table
    PX = 950
    d.box("pole-clamp", [PX - 50, 420, Z0 - 40, PX + 50, 580, Z0 + 2], "shell", r=10)
    d.bar("pole", [PX, 430, 28], [PX, 1110, 28], [60, 50], "shell", r=8)
    d.box("monitor", [PX - 140, 1090, 4, PX + 140, H - 10, 52], "shell", r=16)
    d.decal("monitor-screen", [PX, (1090 + H - 10) / 2, 52.5], [220, 150], "front", "gloss#b9dde6", soft=True)
    d.box("monitor-mount", [PX - 40, 1060, 10, PX + 40, 1110, 40], "plastic#c9cdd2", r=8)
    if hood:
        # thicker black frame under the hood, the fixed hood shell, the lid swung up, black strip with a speaker
        d.slab("hood-frame", "top", P(rr(0, Z0 - 10, 1010, DP, [0, 0, 110, 110])), [600, 740], "black", r=30)
        # the hood is frosted translucent white (photo): acrylic, domed head end, rounded shoulder at its right end
        d.loft("hood", [sec(180, 830, 380, 110, 920, 480), sec(660, 830, 380, 110, 920, 480),
                        sec(870, 820, 270, 100, 865, 480), sec(1000, 800, 80, 38, 770, 480)], "acrylic#eef1f4d8", axis="x",
               dome="start", domeH=170)
        lid = rot("x", -64, [0, 1108, Z0 + 140])
        d.box("lid", [40, 1100, Z0 + 140, 960, 1116, Z0 + 565], "acrylic#f3f5f7d0", r=10, rot=lid)
        for i, (x, z, w, h) in enumerate([(300, Z0 + 330, 260, 130), (560, Z0 + 440, 90, 60), (680, Z0 + 440, 60, 90),
                                          (790, Z0 + 440, 70, 50)]):
            d.box(f"lid-print{i}", [x - w / 2, 1117, z - h / 2, x + w / 2, 1120, z + h / 2], "plastic#3a3f46", r=3,
                  soft=True, rot=lid)
        d.box("lid-latch", [600, 1116, Z0 + 520, 760, 1136, Z0 + 560], "plastic#d9dde2", r=6, rot=lid)
        # white speaker housing with the round black speaker, then the black strip, in front of the hood's base
        d.box("spk-box", [460, 700, 700, 575, 815, 885], "white", r=14)
        d.lathe("speaker", [517, 757, 885], [[0, 0], [46, 0], [46, 6], [30, 10], [0, 10]], "black", axis="z")
        d.box("strip", [580, 700, 700, 1010, 805, 885], "black", r=24)
        d.box("lid-box", [380, 1118, Z0 + 470, 560, 1150, Z0 + 545], "white", r=8, rot=lid)
    d.save()


build("xy-sl-cviii", 1330, False)
build("xy-sl-cviii-luxury", 1500, True)
