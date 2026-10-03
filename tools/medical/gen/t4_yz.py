"""YZ-2A / YZ-3 / YZ-4 cervical traction chairs — batch table-4.  python3 t4_yz.py [ids]  (writes only these ids).
Seat faces the front (z = D); x from the left seen from the front."""
import sys, math
from t4lib import *

MATS = {"white": "plastic#f3f4f6", "pad": "leather#c9b8dc", "cap": "rubber#1f2124", "chrome": "chrome",
        "dark": "plastic#26292e", "cable": "metal#d2d5d9", "halter": "fabric#c7c3e3", "edge": "fabric#4f8fd8",
        "hpad": "fabric#f1f1f4"}


def tube_chair(d, x0, x1, z0, z1, seat=450, arm=610, top=960, back_stretch=True, side_stretch=False):
    """White Ø30 accompany chair: inverted-U back frame on the back legs, arm loops from the front legs."""
    zb, zf = z0 + 15, z1 - 25
    xl, xr = x0 + 15, x1 - 15
    d.tube("back-u", [[xl, 0, zb], [xl, top, zb - 18], [xr, top, zb - 18], [xr, 0, zb]], 30, "white", bend=90)
    d.tube("arm-l", [[xl, 0, zf], [xl, arm, zf], [xl, arm, zb + 10]], 30, "white", bend=75)
    d.tube("arm-r", [[xr, 0, zf], [xr, arm, zf], [xr, arm, zb + 10]], 30, "white", bend=75)
    d.cyl("foot", [xl, 0, zb], [xl, 38, zb], 36, "cap", copies=[[xr - xl, 0, 0], [0, 0, zf - zb], [xr - xl, 0, zf - zb]])
    # backrest panel inside the U, seat pan with thick front lip, lilac cushion, side rails
    d.box("back-pad", [xl + 22, seat + 10, zb - 26, xr - 22, top - 20, zb + 18], "pad", r=16, puff=4)
    d.box("seat-pan", [xl + 15, seat - 55, zb + 20, xr - 15, seat, zf + 10], "white", r=10)
    d.box("seat", [xl + 35, seat, zb + 30, xr - 35, seat + 40, zf - 5], "pad", r=14, puff=5)
    d.box("rail", [xl - 12, seat - 60, zb, xl + 12, seat - 20, zf], "white", r=4, copies=[[xr - xl, 0, 0]])
    if back_stretch:
        d.cyl("str-b", [xl, 150, zb], [xr, 150, zb], 26, "white")
    if side_stretch:
        d.cyl("str-s", [xl, 150, zb], [xl, 150, zf], 26, "white", copies=[[xr - xl, 0, 0]] if side_stretch == 2 else None)
    # grey board behind the backrest cushion (its thin dark rim shows round the lilac, photos)
    d.box("back-board", [xl + 16, seat + 4, zb - 22, xr - 16, top - 14, zb + 8], "plastic#8f93a3", r=10)
    return xl, xr, zb, zf


def pole(d, px, pz, y0, ytop, arm_to, sy, sp_mat="chrome", sleeve=False, knob_side=-1, hw=140, sp_shape="peak",
         pul_mat="dark", cross=False, cg=22):
    """Chrome traction pole with the white top bracket, chrome arm to two pulleys side by side (along x) at its end,
    two parallel vertical cables down to the spreader plate (hooks at its ends) and the halter.
    sleeve: the hanging chrome weight on a third cable beside the pole (yz-2a)."""
    d.cyl("pole", [px, y0, pz], [px, ytop, pz], 40, "chrome")
    d.box("brk", [px - 34, ytop - 160, pz - 34, px + 34, ytop + 10, pz + 34], "white", r=12)
    ax, ay, az = arm_to
    d.add("brk-plate", "bar", "white", **{"from": [px, ytop - 60, pz], "to": [px + (ax - px) * 0.35, ay - 10, pz + (az - pz) * 0.35]},
          section=[50, 70], r=14)
    d.cyl("arm", [px, ytop - 5, pz], [ax, ay, az], 28, "chrome")
    d.cyl("knob-stem", [px, ytop + 10, pz], [px, ytop + 35, pz], 12, "chrome")
    d.lathe("knob-top", [px, ytop + 35, pz], [[0, 0], [28, 0], [30, 8], [24, 18], [0, 18]], "dark")
    for k, dy in enumerate((60, 135)):
        d.cyl(f"knob-s{k}", [px + knob_side * 34, ytop - dy, pz], [px + knob_side * 60, ytop - dy, pz], 34, "dark")
    # two pulleys side by side across the arm end, a fork block over them
    d.box("pul-fork", [ax - cg - 30, ay - 30, az - 22, ax + cg + 30, ay + 12, az + 22], "chrome", r=8)
    for k, sg in enumerate((-1, 1)):
        d.add(f"pulley{k}", "wheel", pul_mat, at=[ax + sg * cg, ay - 30, az], d=60, d2=26, axis="z")
        d.cyl(f"cable{k}", [ax + sg * cg, ay - 58, az], [ax + sg * cg, sy + 48, az], 3, "cable", soft=True)
    sx, sz = ax, az
    if sleeve:   # third cable down the pole side to a hanging chrome weight
        wx = px + knob_side * 48
        d.cyl("cable-c", [wx, ytop - 100, pz], [wx, 1180, pz], 3, "cable", soft=True)
        d.cyl("sleeve", [wx, 985, pz], [wx, 1180, pz], 42, "chrome")
        d.cyl("sleeve-cap", [wx, 1180, pz], [wx, 1195, pz], 24, "chrome")
    # spreader plate with hooks at its ends
    if sp_shape == "peak":
        sp_pts = [(sx - hw, sy), (sx + hw, sy), (sx + hw, sy + 22), (sx + 45, sy + 46), (sx, sy + 54), (sx - 45, sy + 46), (sx - hw, sy + 22)]
    else:        # black plate, straight top, bottom ends chamfered
        sp_pts = [(sx - hw + 30, sy), (sx + hw - 30, sy), (sx + hw, sy + 30), (sx + hw, sy + 52), (sx - hw, sy + 52), (sx - hw, sy + 30)]
    front_slab(d, "spreader", sp_pts, sz - 14, sz + 14, sp_mat, r=4)
    d.cyl("sp-bolt", [sx - 35, sy + 30, sz + 14], [sx - 35, sy + 30, sz + 20], 16, "chrome" if sp_shape != "peak" else "plastic#8d9198",
          soft=True, repeat=rep(3, [35, 0, 0]))
    d.cyl("hook", [sx - hw + 18, sy - 40, sz], [sx - hw + 18, sy, sz], 6, "chrome", soft=True, copies=[[2 * hw - 36, 0, 0]])
    d.sphere("hook-ring", [sx - hw + 18, sy - 44, sz], 16, "chrome", soft=True, copies=[[2 * hw - 36, 0, 0]])
    # halter: a side strap from each hook down to a junction, from there a chin band (front) and an occiput band
    # (back) forming a cradle with blue edging, white pentagon pads at the lower corners (photos)
    hb = sy - 330
    jy = sy - 175
    for sg in (-1, 1):
        d.strap(f"halter-s{sg + 1}", [[sx + sg * (hw - 18), sy - 50, sz], [sx + sg * (hw - 26), jy, sz]], [44, 3], "halter", soft=True)
    for nm, dz in (("f", 40), ("b", -40)):
        path = [[sx - hw + 26, jy, sz + dz * 0.3], [sx - hw + 45, hb + 70, sz + dz], [sx - 55, hb, sz + dz * 1.3],
                [sx + 55, hb, sz + dz * 1.3], [sx + hw - 45, hb + 70, sz + dz], [sx + hw - 26, jy, sz + dz * 0.3]]
        d.strap(f"halter-{nm}", path, [50, 3], "halter", bend=70, soft=True)
        d.strap(f"halter-e{nm}", [[p[0], p[1] - 2.5, p[2]] for p in path], [56, 2], "edge", bend=70, soft=True)
    if cross:    # crossing straps in front (yz-3)
        for k, sg in enumerate((-1, 1)):
            d.strap(f"halter-x{k}", [[sx + sg * (hw - 26), jy, sz + 18], [sx - sg * 60, hb + 20, sz + 58]], [36, 3], "halter", soft=True)
    for k, sg in enumerate((-1, 1)):
        pts = [(sx + sg * 62 - 34, hb + 30), (sx + sg * 62 + 34, hb + 30), (sx + sg * 62 + 34, hb - 5), (sx + sg * 62, hb - 38), (sx + sg * 62 - 34, hb - 5)]
        front_slab(d, f"hpad{k}", pts, sz + 56, sz + 66, "hpad", r=3, soft=True)


def yz_2a():
    d = D("yz-2a", [650, 600, 2000], dict(MATS))
    xl, xr, zb, zf = tube_chair(d, 0, 650, 0, 600, side_stretch=2)
    # control box under the seat (left of centre): label front, blue panel left, black rotary knob right
    d.box("ctl", [150, 270, 330, 330, 395, 545], "white", r=6)
    d.decal("ctl-label", [235, 335, 545.5], [110, 90], "front", "plastic#c9ccd1", soft=True)
    d.decal("ctl-txt", [228, 335, 545.8], [80, 60], "front", "plastic#8b9097", soft=True)
    d.decal("ctl-blue", [149.5, 335, 480], [110, 100], "left", "gloss#3c8fd0", soft=True)
    d.cyl("ctl-k", [149, 360, 470], [140, 360, 470], 14, "dark", soft=True, copies=[[0, -45, 0]])
    d.cyl("rotary", [330, 345, 470], [360, 345, 470], 70, "dark")
    d.box("back-plate", [170, 520, zb - 45, 290, 900, zb - 25], "white", r=6)
    pole(d, 240, zb - 60, 520, 1890, [390, 1945, 300], 1470, sleeve=True, pul_mat="metal#b9bdc2")
    d.save()


def yz_3():
    d = D("yz-3", [650, 600, 2000], dict(MATS, halter="fabric#cdd0ea", pad="leather#cbbfdc"))
    xl, xr, zb, zf = tube_chair(d, 90, 650, 0, 600, back_stretch=False, side_stretch=True)
    # light-blue motor unit on the left armrest, black cable loop below
    # (photo: it hangs on the outside of the left armrest, its top at the armrest)
    d.box("motor-box", [0, 395, 330, 125, 615, 560], "plastic#5db6dc", r=6)
    d.box("motor-hook", [70, 590, 400, 115, 640, 490], "plastic#5db6dc", r=4)
    d.decal("motor-seam", [62, 505, 560.5], [3, 200], "front", "plastic#4a9cc0", soft=True)
    d.tube("motor-cable", [[50, 395, 470], [40, 290, 480], [80, 220, 470], [110, 290, 460], [100, 395, 450]], 10, "black#18191b", bend=40, soft=True)
    d.cyl("motor", [230, 330, 420], [400, 330, 420], 85, "plastic#3e4248")
    d.cyl("motor-end", [400, 330, 420], [425, 330, 420], 60, "chrome")
    d.box("remote", [290, 492, 420, 390, 505, 470], "plastic#eef0f2", r=4)
    d.box("back-plate", [210, 520, zb - 45, 330, 900, zb - 25], "white", r=6)
    pole(d, 270, zb - 60, 520, 1890, [425, 1945, 300], 1450, sp_mat="plastic#2b2e33", hw=110, sp_shape="flat", cross=True)
    d.save()


def yz_4():
    d = D("yz-4", [750, 750, 2000], dict(MATS, white="gloss#f5f6f7", pad="leather#cdc3e6", black="leather#1e2024",
                                           red="gloss#b0141c"))
    # white moulded base on low black feet, logo on the front
    d.box("base", [0, 35, 90, 620, 470, 720], "white", r=45)
    d.box("feet", [30, 0, 120, 90, 38, 180], "cap", r=8, copies=[[500, 0, 0], [0, 0, 500], [500, 0, 500]])
    brand(d, "logo", 200, 185, 720, 52, mat="gloss#6a7fd0")
    # seat, arm supports with armrests
    d.box("seat", [70, 470, 260, 550, 540, 735], "pad", r=24, puff=6)
    for nm, x0 in (("l", 0), ("r", 530)):
        front_slab(d, f"arm-sup-{nm}", [(220, 470), (735, 470), (735, 520), (700, 610), (700, 650), (220, 650)], x0, x0 + 90, "white", r=18) \
            if False else None
        d.add(f"arm-sup-{nm}", "slab", "white", plane="side",
              outline=poly_path([(230, 440), (720, 440), (720, 520), (690, 600), (690, 650), (230, 650)]), w=[x0, x0 + 90], r=20)
        d.box(f"armrest-{nm}", [x0 - 8, 650, 330, x0 + 98, 705, 715], "pad", r=20, puff=4)
    # white control box on the right below the armrest, light panel and buttons
    d.box("ctl", [600, 410, 380, 750, 640, 720], "white", r=20)
    d.box("ctl-panel", [615, 640, 440, 735, 646, 700], "plastic#cfe3f2", r=4)
    d.cyl("ctl-btn", [640, 646, 480], [640, 652, 480], 16, "plastic#3b4a5c", soft=True, repeat=rep(4, [0, 0, 50]), copies=[[40, 0, 0]])
    d.decal("ctl-face", [675, 560, 720.5], [110, 60], "front", "plastic#dfe8f0", soft=True)
    d.box("ctl-ped", [610, 35, 420, 700, 410, 700], "white", r=30)
    # tall back: white shell (wings), lilac frame cushion, black split panel with 4 red balls, pillow, pocket
    br = rot("x", -8, [300, 470, 230])
    d.box("back-shell", [40, 470, 120, 560, 960, 230], "white", r=40, rot=br)
    d.box("back-frame", [100, 470, 200, 500, 1150, 270], "pad", r=36, puff=5, rot=br)
    d.box("back-panel", [135, 520, 265, 465, 1090, 290], "black", r=18, puff=4, rot=br)
    d.box("back-split", [135, 815, 285, 465, 830, 296], "pad", r=4, rot=br)
    d.box("pillow", [150, 1000, 270, 450, 1100, 320], "black", r=40, puff=8, rot=br)
    d.box("pocket", [205, 560, 285, 395, 660, 302], "black", r=10, rot=br)
    for k, (bx, by) in enumerate(((215, 862), (385, 862), (215, 725), (385, 725))):
        d.sphere(f"ball{k}", [bx, by, 295], 62, "red", rot=br)
    pole(d, 410, 80, 700, 1890, [235, 1945, 360], 1300, knob_side=1, cross=True)
    d.save()


ids = sys.argv[1:] or ["yz-2a", "yz-3", "yz-4"]
for i, fn in (("yz-2a", yz_2a), ("yz-3", yz_3), ("yz-4", yz_4)):
    if i in ids: fn()
