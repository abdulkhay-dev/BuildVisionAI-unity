"""xy-qjhd-bh / xy-qjhd-bv — interactive evaluation display stands with a 3D camera (kinesio-2)."""
from k2lib import *

MATS = {"white": "plastic#f3f4f6", "graph": "plastic#3a3f46", "bezel": "plastic#3a3b3f", "dark": "plastic#26282c",
        "black": "plastic#18191b", "cam": "gloss#1c1e22", "blue": "gloss#2f7fd0", "steel": "metal#c9ccd0"}


def stand(d, cab_top, CW=540, CD=260):
    """X base (graphite legs to 4 castors), white column cabinet, dark camera band, front foot tray, side hook."""
    CX, CZ = 625, 330
    for sx in (-1, 1):
        for sz in (-1, 1):
            ex, ez = CX + sx * 545, CZ + sz * 300
            d.bar(f"leg-{sx}{sz}", [CX + sx * 120, 125, CZ + sz * 60], [ex, 125, ez], [70, 46], "graph", r=6)
            d.cyl(f"leg-cap-{sx}{sz}", [ex, 100, ez], [ex, 150, ez], 64, "graph")
            caster(d, f"castor-{sx}{sz}", [ex, 0, ez + 20], 75, "rubber#e8e9eb")
    d.box("hub", [CX - CW / 2 + 40, 100, CZ - 100, CX + CW / 2 - 40, 150, CZ + 100], "graph", r=8)
    x0, x1, z0, z1 = CX - CW / 2, CX + CW / 2, CZ - CD / 2, CZ + CD / 2
    d.box("cabinet", [x0, 150, z0, x1, cab_top, z1], "white", r=10)
    # door seam on the front, recessed grip slot on the right side by the front edge, hook bracket higher up
    d.box("door-seam", [x0 + 30, 300, z1 - 0.5, x0 + 32, cab_top - 120, z1 + 0.8], "plastic#d9dbde", soft=True)
    d.box("grip", [x1 - 1, 330, z1 - 60, x1 + 2, 500, z1 - 35], "dark", r=6)
    hy = cab_top - 330
    d.slab("hook", "side", f"M {z1 - 120} {hy} L {z1 - 20} {hy} L {z1 - 20} {hy + 70} L {z1 - 34} {hy + 70} L {z1 - 34} {hy + 14} "
           f"L {z1 - 106} {hy + 14} L {z1 - 106} {hy + 70} L {z1 - 120} {hy + 70} Z", [x1, x1 + 70], "white", r=3)
    d.box("hook-plate", [x1, hy - 20, z1 - 130, x1 + 8, hy + 90, z1 - 10], "white", r=3)
    xy_logo(d, "logo", [CX - 150, cab_top - 110, z1 + 0.6], 46, "front")
    # dark band with the depth camera on top of the cabinet
    d.box("band", [x0, cab_top, z0, x1, cab_top + 90, z1], "graph", r=6)
    d.box("cam", [CX - 160, cab_top + 22, z1 - 2, CX + 160, cab_top + 68, z1 + 3], "cam", r=6)
    d.decal("cam-lens", [CX - 90, cab_top + 45, z1 + 3.6], [22, 22], "front", "plastic#4a5058", soft=True, copies=[[60, 0, 0], [180, 0, 0]])
    # white foot tray in front of the cabinet foot
    d.box("tray", [CX - 200, 150, z1, CX + 200, 260, z1 + 150], "white", r=12)
    d.box("tray-in", [CX - 180, 230, z1 + 12, CX + 180, 262, z1 + 135], "plastic#e2e4e7", r=8)
    return CX, CZ, z0, z1


# ---------- BH: landscape 55" display on a tall cabinet
d = D("xy-qjhd-bh", [1250, 700, 1800], MATS)
CX, CZ, z0, z1 = stand(d, 990)
Y0, Y1, X0, X1 = 1080, 1800, 5, 1245
d.box("disp-back", [X0 + 30, Y0 + 30, CZ - 50, X1 - 30, Y1 - 30, CZ + 20], "bezel", r=12)
scr(d, "display", [X0, Y0, CZ + 20, X1, Y1, CZ + 50], "bezel", r=6, face="front", bezel=18, print="med_xy-qjhd-bh_screen")
# the screen picture is the main photo's display, rectified (tools/medical/scratch/kinesio-2-review/rectify.py,
# inner screen quad TL (122,66) TR (727,36.5) BR (725.5,440.5) BL (128,440.5) -> 1024 x 580): no mask needed
d.save()

# ---------- BV: portrait 55" display on a short cabinet, operator monitor and keyboard tray on the right
d = D("xy-qjhd-bv", [1250, 700, 2000], MATS)
CX, CZ, z0, z1 = stand(d, 640)
Y0, Y1, X0, X1 = 730, 2000, 245, 1005          # display incl. bezel
d.box("disp-back", [X0 + 25, Y0 + 25, CZ - 50, X1 - 25, Y1 - 25, CZ + 20], "bezel", r=12)
d.box("disp-bottom", [X0, Y0, CZ + 20, X1, Y0 + 16, CZ + 50], "bezel", r=4)
# the crop has its own left / top / right bezel and no bottom one: picture from the bottom bezel up
scr(d, "display", [X0, Y0 + 16, CZ + 20, X1, Y1, CZ + 50], "bezel", r=4, face="front", bezel=1, print="med_xy-qjhd-bv_screen")
# crop 399 x 800: top 14 px (bezel + white corner) and right of col 391 (display side) masked dark
cw, ch = (X1 - 1) - (X0 + 1), (Y1 - 1) - (Y0 + 17)
d.box("display-mask-top", [X0, Y1 - 14 / 800 * ch - 1, CZ + 53.2, X1, Y1, CZ + 54.5], "bezel", soft=True)
d.box("display-mask-r", [X0 + 1 + 391 / 399 * cw, Y0 + 16, CZ + 53.2, X1, Y1, CZ + 54.5], "bezel", soft=True)
# operator station: white arm from behind the display, ~15.6" monitor, black V bracket, keyboard tray
d.box("arm", [X1 - 80, 1055, CZ - 30, X1 + 150, 1085, CZ + 10], "white", r=8)
d.box("arm-post", [X1 + 110, 1000, CZ - 25, X1 + 145, 1085, CZ + 140], "white", r=8)
d.box("arm-fwd", [X1 + 110, 1000, CZ + 100, X1 + 145, 1030, CZ + 200], "white", r=8)
MX0, MX1, MY0, MY1, MZ = 880, 1240, 805, 1050, CZ + 230
# the operator monitor is turned ~25 deg to the right (towards +x), as in the photo: black thin bezel, light chin
MR = rot("y", 25, [(MX0 + MX1) / 2, MY0, MZ - 20])
d.box("mon-back", [MX0, MY0, MZ - 30, MX1, MY1, MZ - 4], "black", r=10, rot=MR)
scr(d, "mon", [MX0, MY0 + 22, MZ - 6, MX1, MY1, MZ], "black", r=6, face="front", bezel=10, rot=MR)
d.box("mon-chin", [MX0, MY0, MZ - 8, MX1, MY0 + 24, MZ + 1], "plastic#e4e6e9", r=6, rot=MR)
d.decal("mon-ui", [(MX0 + MX1) / 2, (MY0 + MY1) / 2 + 12, MZ + 0.8], [MX1 - MX0 - 24, MY1 - MY0 - 46], "front", "gloss#eef4fa", soft=True, rot=MR)
d.decal("mon-ui-bar", [MX0 + 34, (MY0 + MY1) / 2 + 12, MZ + 1.4], [36, MY1 - MY0 - 50], "front", "gloss#3a8fd8", soft=True, rot=MR)
d.decal("mon-ui-tile", [MX0 + 100, MY1 - 75, MZ + 1.4], [46, 56], "front", "plastic#b8d4ee", soft=True,
        repeat={"n": 5, "step": [52, 0, 0], "local": True}, copies=[[0, -88, 0]], rot=MR)
d.add("bracket", "slab", "black", plane="front", outline=f"M {MX0 + 60} {MY0} L {MX0 + 80} {MY0} L {(MX0 + MX1) / 2} 712 "
      f"L {MX1 - 80} {MY0} L {MX1 - 60} {MY0} L {(MX0 + MX1) / 2 + 12} 698 L {(MX0 + MX1) / 2 - 12} 698 Z", w=[MZ - 40, MZ - 20], r=2,
      rot=MR)
d.box("kb-tray", [830, 682, MZ - 90, 1250, 698, MZ + 130], "black", r=4)
d.box("keyboard", [880, 698, MZ - 40, 1220, 714, MZ + 110], "plastic#2b2d31", r=4)
d.save()
