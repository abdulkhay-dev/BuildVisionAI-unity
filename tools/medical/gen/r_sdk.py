"""Smart assisted walking robots of batch robot-2: xy-r-sdk-i (2-DOF, black pelvic cuff) and xy-r-sdk-iv (4-DOF,
pelvic frame with side arms and padded shorts). Same chassis: low U base open to the front (patient stands inside),
rear tower (brushed shells, white front band with a blue LED line and the slide slot), handle wings with joysticks,
a 10" touch screen on a stalk facing the patient.
usage: python3 r_sdk.py [id ...]"""
import sys
from r_lib import *

W, DP, H = 800, 1100, 1550
CX, TZ = 400, 250          # tower centre (x, z)


def chassis(d):
    u = ("M 70 0 L 730 0 Q 800 0 800 70 L 800 1040 Q 800 1100 745 1100 L 665 1100 Q 625 1100 625 1060 L 625 440 "
         "Q 625 400 585 400 L 215 400 Q 175 400 175 440 L 175 1060 Q 175 1100 135 1100 L 55 1100 Q 0 1100 0 1040 "
         "L 0 70 Q 0 0 70 0 Z")
    d.slab("base-skirt", "top", u, [40, 125], "silver", r=30)
    ui = ("M 80 12 L 720 12 Q 788 12 788 80 L 788 1030 Q 788 1086 740 1086 L 670 1086 Q 638 1086 638 1050 L 638 445 "
          "Q 638 388 585 388 L 215 388 Q 162 388 162 445 L 162 1050 Q 162 1086 130 1086 L 60 1086 Q 12 1086 12 1030 "
          "L 12 80 Q 12 12 80 12 Z")
    d.slab("base-top", "top", ui, [118, 150], "white", r=14)
    # foot-rest humps on the arms, inner recess bands, castors at the front tips, drive wheels at the rear
    for x in (88, 712):
        d.loft(f"hump-{x}", [sec(150, 120, 300, 55, x, 760), sec(185, 105, 270, 50, x, 760), sec(205, 70, 220, 35, x, 760)],
               "silver", dome="end", domeH=15)
    d.caster("castor", [88, 0, 1040], 75, "rubber#d8dade", copies=[[624, 0, 0]])
    d.add("drive", "wheel", "rubber#1d1f22", at=[60, 75, 180], d=150, d2=45, axis="x", copies=[[680, 0, 0]])
    d.box("port", [CX - 40, 160, 399, CX + 40, 210, 403], "dark", r=4)


def tower(d):
    sx = [sec(150, 400, 330, 120, CX, TZ), sec(320, 320, 280, 110, CX, TZ), sec(1150, 300, 270, 100, CX, TZ),
          sec(1250, 270, 240, 90, CX, TZ)]
    d.loft("tower", sx, "silver", dome="end", domeH=55)
    # white front band (glossy) with the vertical slide slot and the light-blue LED line around it
    d.loft("band", [sec(150, 300, 120, 50, CX, TZ + 110), sec(330, 200, 110, 50, CX, TZ + 102),
                    sec(1200, 190, 100, 45, CX, TZ + 98), sec(1265, 150, 70, 35, CX, TZ + 95)], "white",
           dome="end", domeH=25)
    d.box("slot", [CX - 26, 520, TZ + 140, CX + 26, 1180, TZ + 150], "dark", r=10)
    d.box("led-l", [CX - 92, 360, TZ + 128, CX - 86, 1210, TZ + 146], "led", r=2, soft=True, copies=[[178, 0, 0]])
    d.box("led-top", [CX - 92, 1205, TZ + 128, CX + 92, 1211, TZ + 146], "led", r=2, soft=True)
    # brushed side shells with the S logo
    for s in (-1, 1):
        x = CX + s * 155
        d.cyl(f"logo-disc-{s}", [x, 640, TZ], [x + s * 4, 640, TZ], 84, "logo")
                # the side render shows +z to the left on the right face: there the S is drawn turned over (reads right)
        if s < 0:
            text(d, f"logo-s-{s}", "S", [x - 5, 612, TZ - 16], 56, "dark", along=(1, 0), stroke=11, face="left")
        else:   # review 2026-10-03: on the +x face text() reads mirrored; draw along +z and mirror the strokes in z
            n0 = len(d.d["parts"])
            text(d, f"logo-s-{s}", "S", [x + 5, 612, TZ - 16], 56, "dark", along=(1, 0), stroke=11, face="right")
            for p in d.d["parts"][n0:]:
                p["at"][2] = round(2 * TZ - p["at"][2], 1)
                p["rot"]["deg"] = -p["rot"]["deg"]
                p["rot"]["about"] = list(p["at"])
    # screen on a stalk, facing the patient, slightly tilted back
    # review 2026-10-03: the photo's screen case is light silver-grey with a thick lower border, ~4:3, on a short stalk
    d.box("stalk", [CX - 40, 1260, TZ - 30, CX + 40, 1330, TZ + 40], "silver", r=16)
    tilt = rot("x", -12, [CX, 1440, TZ + 20])
    d.box("screen-case", [CX - 150, 1318, TZ - 10, CX + 150, 1550, TZ + 40], "case", r=24, rot=tilt)
    d.box("screen-bezel", [CX - 132, 1352, TZ + 40, CX + 132, 1534, TZ + 46], "bezel", r=10, rot=tilt)
    d.box("screen-ui", [CX - 124, 1358, TZ + 46, CX + 124, 1528, TZ + 48], "ui", r=4, rot=tilt)
    d.box("screen-tile", [CX - 98, 1385, TZ + 48, CX - 66, 1435, TZ + 49.5], "tile", r=3, soft=True, rot=tilt,
          repeat={"n": 5, "step": [40, 0, 0]})
    d.box("screen-icon", [CX - 88, 1400, TZ + 49.5, CX - 76, 1420, TZ + 50.5], "ui", r=2, soft=True, rot=tilt,
          repeat={"n": 5, "step": [40, 0, 0]})
    d.box("screen-head", [CX - 110, 1490, TZ + 48, CX - 30, 1500, TZ + 49.5], "tile", r=2, soft=True, rot=tilt)
    d.box("screen-head2", [CX - 110, 1470, TZ + 48, CX - 10, 1477, TZ + 49.5], "tile", r=2, soft=True, rot=tilt)
    d.box("screen-brand", [CX - 30, 1538, TZ + 40, CX + 30, 1544, TZ + 41.5], "dark", r=1, soft=True, rot=tilt)


def wings(d):
    """Handle wings: a flat grey pad on each side of the tower with a black joystick and a red e-stop on a yellow
    ring, the grey rim grip around its outer and front edge."""
    Y = 1050
    for s in (-1, 1):
        xi, xo = CX + s * 150, CX + s * 300
        x0, x1 = min(xi, xo), max(xi, xo)
        d.box(f"wing-pad-{s}", [x0, Y - 20, TZ - 40, x1, Y + 18, TZ + 430], "grey", r=16)
        d.box(f"wing-top-{s}", [x0 + 15, Y + 18, TZ + 40, x1 - 15, Y + 22, TZ + 400], "padtop", r=12)
        xm = CX + s * 360
        d.sweep(f"wing-rim-{s}", [[CX + s * 140, Y, TZ - 60], [xm, Y + 10, TZ - 40], [xm + s * 10, Y + 20, TZ + 300],
                                  [CX + s * 300, Y + 15, TZ + 480], [CX + s * 175, Y, TZ + 470]],
                [70, 50], "grey", shape="oval", bend=110)
        xj = CX + s * 225
        d.lathe(f"stick-{s}", [xj, Y + 22, TZ + 230], [[0, 0], [30, 0], [26, 10], [9, 14], [9, 70], [14, 80], [14, 130],
                                                        [8, 140], [0, 140]], "stick")
        d.lathe(f"stick-boot-{s}", [xj, Y + 22, TZ + 230], [[0, 0], [36, 0], [36, 8], [20, 14], [0, 14]], "dark")
        d.lathe(f"estop-ring-{s}", [xj, Y + 22, TZ + 70], [[0, 0], [24, 0], [24, 6], [0, 6]], "yellow")
        d.lathe(f"estop-{s}", [xj, Y + 28, TZ + 70], [[0, 0], [15, 0], [15, 14], [19, 18], [19, 30], [0, 32]], "red")
    d.box("wing-bridge", [CX - 155, Y - 40, TZ + 110, CX + 155, Y + 10, TZ + 175], "silver", r=18)


MATS = {"white": "gloss#f4f5f7", "silver": "metal#c5c9ce", "grey": "plastic#a8acb2", "padtop": "plastic#8d9298",
        "dark": "plastic#26292d", "led": "acrylic#7fd0ffcc", "logo": "metal#b3b8be", "bezel": "plastic#3a3d42",
        "ui": "gloss#4f9de0", "tile": "plastic#eef4fb", "yellow": "gloss#f2c618", "red": "gloss#d42a26",
        "black": "rubber#17181a", "web": "fabric#17181a",
        "case": "metal#c3c7cc", "stick": "plastic#e6e8eb"}


def gen_i():
    d = D("xy-r-sdk-i", [W, DP, H], dict(MATS))
    chassis(d); tower(d); wings(d)
    # 2-DOF pelvic support (review 2026-10-03, photo): a carriage in the slot carries a grey bridge across x; from it
    # TWO parallel silver arms run forward along the cuff's sides - the -x one with the white joint and the yellow
    # warning label, the +x one with "Sunnyou" on its outer face - and hold the black pelvic cuff between them
    Y = 990
    d.box("carriage", [CX - 60, Y - 70, TZ + 140, CX + 60, Y + 50, TZ + 200], "silver", r=14)
    d.box("bridge", [CX - 250, Y - 45, TZ + 175, CX + 250, Y + 40, TZ + 260], "grey", r=22)
    d.box("bridge-grille", [CX - 250, Y + 40, TZ + 190, CX - 170, Y + 42, TZ + 245], "dark", r=6, soft=True)
    for s_ in (-1, 1):
        ax = CX - 40 + s_ * 235
        d.cyl(f"arm-{s_}", [ax, Y, TZ + 240], [ax, Y, TZ + 820], 62, "silver")
        d.sphere(f"arm-end-{s_}", [ax, Y, TZ + 820], 62, "silver")
        d.box(f"arm-root-{s_}", [ax - 40, Y - 40, TZ + 220, ax + 40, Y + 40, TZ + 330], "grey", r=16)
    d.cyl("arm-joint", [CX - 275, Y, TZ + 420], [CX - 275, Y, TZ + 500], 82, "white")
    d.decal("warn", [CX - 275, Y + 30, TZ + 460], [22, 20], "yellow", face="top", soft=True)
    # on a +x face text() reads mirrored from outside: draw along +z, then mirror the strokes in z (as k1lib.text_right)
    n0 = len(d.d["parts"])
    text(d, "sunnyou", "Sunnyou", [CX + 227, Y - 9, TZ + 580], 22, "dark", along=(1, 0), stroke=3, face="right")
    zm = TZ + 580 + text_len("Sunnyou", 22) / 2
    for p in d.d["parts"][n0:]:
        p["at"][2] = round(2 * zm - p["at"][2], 1)
        p["rot"]["deg"] = -p["rot"]["deg"]
        p["rot"]["about"] = list(p["at"])
    cz = TZ + 700
    d.lathe("cuff", [CX - 40, Y - 300, cz], [[180, 0], [205, 0], [210, 20], [210, 250], [200, 270], [180, 270]], "black",
            caps=False)
    d.lathe("cuff-in", [CX - 40, Y - 280, cz], [[178, 0], [178, 250]], "black", caps=False)
    for k, y in enumerate((Y - 240, Y - 140)):
        d.lathe(f"cuff-strap-{k}", [CX - 40, y, cz], [[212, 0], [218, 0], [218, 45], [212, 45]], "web", caps=False)
    d.box("cuff-buckle", [CX - 190, Y - 210, cz + 140, CX - 140, Y - 120, cz + 200], "dark", r=8, rot=rot("y", -40, [CX - 165, 0, cz + 170]))
    d.box("cuff-mount", [CX - 260, Y - 60, cz - 30, CX - 230, Y + 10, cz + 30], "dark", r=6, copies=[[440, 0, 0]])
    d.save()


def gen_iv():
    d = D("xy-r-sdk-iv", [W, DP, H], dict(MATS, stick="plastic#26292d"))   # IV photos: black joysticks
    chassis(d); tower(d); wings(d)
    # 4-DOF pelvic module: carriage box, arm forward, crossbar with telescopic side arms and clamp pads,
    # black padded pelvic shorts between them
    Y = 910
    d.box("carriage", [CX - 85, Y - 120, TZ + 140, CX + 85, Y + 90, TZ + 230], "silver", r=12)
    d.box("carriage-face", [CX - 70, Y - 100, TZ + 230, CX + 70, Y + 60, TZ + 236], "grey", r=8)
    d.box("arm", [CX - 45, Y - 40, TZ + 230, CX + 45, Y + 40, TZ + 420], "silver", r=18)
    d.cyl("cross", [CX - 300, Y, TZ + 450], [CX + 300, Y, TZ + 450], 64, "silver")
    d.box("cross-hub", [CX - 70, Y - 45, TZ + 400, CX + 70, Y + 45, TZ + 495], "white", r=20)
    d.lathe("knob", [CX, Y - 45, TZ + 450], [[0, 0], [12, 0], [12, -20], [28, -24], [28, -36], [0, -38]], "dark")
    for s in (-1, 1):
        x = CX + s * 300
        d.box(f"elbow-{s}", [x - 42, Y - 42, TZ + 410, x + 42, Y + 42, TZ + 500], "silver", r=18)
        d.cyl(f"side-arm-{s}", [x, Y, TZ + 495], [x, Y, TZ + 820], 62, "silver")
        d.cyl(f"side-tip-{s}", [x, Y, TZ + 820], [x, Y, TZ + 900], 56, "white")
        d.cyl(f"side-cap-{s}", [x, Y, TZ + 900], [x, Y, TZ + 910], 50, "dark")
        d.box(f"clamp-{s}", [x - s * 40 - 22, Y - 90, TZ + 600, x - s * 40 + 22, Y + 10, TZ + 700], "dark", r=8)
    cz = TZ + 650
    d.loft("shorts", [sec(Y - 330, 330, 260, 110, CX, cz), sec(Y - 170, 360, 280, 120, CX, cz),
                      sec(Y - 40, 340, 270, 115, CX, cz)], "black", caps=False)
    for k, y in enumerate((Y - 300, Y - 160)):
        d.loft(f"shorts-band-{k}", [sec(y, 368, 288, 124, CX, cz), sec(y + 40, 368, 288, 124, CX, cz)], "web", caps=False)
    d.box("shorts-pad", [CX - 200, Y - 320, cz - 60, CX - 184, Y - 120, cz + 60], "dark", r=6, mirror="x")
    d.save()


GEN = {"xy-r-sdk-i": gen_i, "xy-r-sdk-iv": gen_iv}

if __name__ == "__main__":
    for i in (sys.argv[1:] or list(GEN)):
        GEN[i]()
