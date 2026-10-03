"""Wooden positioning items of batch pediatric-4/5: XYRT-8 children's standing frame, XYRT-9 sitting posture chair.
Front = +z, x from the left seen from the front."""
from pd4lib import *
from sflib import round_poly


def xyrt8():
    W, DD, H = 800, 650, 1320
    d = D("xyrt-8", [W, DD, H], {"wood": "wood#ecca8e", "woodd": "wood#d08e48", "steel": "chrome",
                                 "pad": "leather#8e9be0", "padd": "leather#7584d4", "blk": "rubber#1c1d1f"})
    # base board with raised edge strips at the back and along both sides of the back half
    d.box("base", [0, 0, 0, W, 34, DD], "wood", r=4)
    d.box("strip-b", [0, 34, 0, W, 72, 44], "woodd", r=4)
    d.box("strip-l", [0, 34, 44, 44, 72, 380], "woodd", r=4)
    d.box("strip-l2", [120, 34, 44, 160, 60, 300], "woodd", r=4)
    d.box("strip-r", [W - 44, 34, 44, W, 72, 300], "woodd", r=4)
    # foot platform with a vertical back plate, black heel plates with scale ticks, black foot straps
    d.box("foot-board", [240, 34, 300, 720, 64, 610], "wood", r=6)
    d.box("foot-back", [250, 64, 300, 650, 196, 330], "wood", r=5)
    d.box("heel", [300, 70, 330, 430, 150, 342], "blk", r=6, copies=[[160, 0, 0]])
    d.box("tick", [312, 160, 330.5, 314, 186, 331.5], "plastic#3a3026", soft=True, repeat=rep(14, [24, 0, 0]))
    d.box("tick2", [312, 64.5, 360, 314, 65.5, 380], "plastic#3a3026", soft=True, repeat=rep(14, [24, 0, 0]))
    d.box("foot-strap", [300, 64, 470, 440, 70, 505], "blk", r=4, copies=[[160, 0, 0]])
    # mast: two chrome tubes joined by a U at the top, the tall J handle from the back-left corner over into it
    xm0, xm1, zm = 400, 470, 170
    d.tube("mast", [[xm1, 34, zm], [xm1, 1290, zm], [xm0, 1290, zm], [xm0, 34, zm]], 25, "steel", bend=35)
    d.tube("j-handle", [[205, 34, 70], [205, 1180, 70], [235, 1300, 85], [370, 1300, 150], [xm0, 1240, zm]], 25,
           "steel", bend=70)
    d.box("top-clamp", [330, 1215, zm - 18, 560, 1250, zm + 18], "woodd", r=6)
    d.sphere("top-label", [445, 1232, zm + 18], None, "plastic#f4f4f4", radii=[22, 10, 2], soft=True)
    # foot-assembly clamp on the mast with a blue knob
    d.box("foot-clamp", [370, 230, zm - 25, 520, 285, zm + 30], "woodd", r=8)
    d.cyl("foot-clamp-knob", [370, 258, zm], [335, 258, zm], 26, "plastic#3a7fd0", sides=10)
    # foot-width rod with periwinkle end blocks and black knobs
    d.cyl("width-rod", [300, 262, 380], [690, 262, 380], 16, "steel")
    for i, x in enumerate((300, 690)):
        d.box(f"end-block{i}", [x - 40, 225, 350, x + 40, 300, 395], "pad", r=10)
        d.box(f"end-plate{i}", [x - 28, 236, 395, x + 28, 290, 399], "metal#c8ccd0", r=3)
        d.cyl(f"end-knob{i}", [x, 262, 399], [x, 262, 425], 30, "blk", sides=10)
    # chest and knee supports: flat periwinkle plate, padded wedge block, strap loop hanging in front
    for nm, y0 in (("chest", 830), ("knee", 515)):
        d.box(f"{nm}-plate", [245, y0, zm + 14, 610, y0 + 210, zm + 34], "pad", r=6)
        d.slab(f"{nm}-block", "side", P(round_poly([(zm + 34, y0 + 30), (zm + 190, y0 + 30), (zm + 175, y0 + 140),
                                                    (zm + 34, y0 + 175)], 30)), [285, 575], "pad", r=24)
        d.strap(f"{nm}-strap", [[288, y0 + 110, zm + 175], [300, y0 - 20, zm + 215], [430, y0 - 80, zm + 235],
                                [560, y0 - 10, zm + 210], [572, y0 + 110, zm + 175]], [76, 4], "padd", bend=60,
                soft=True)
    return d


def xyrt9():
    W, DD, H = 600, 720, 800
    wood = "wood#ffbe6a"
    d = D("xyrt-9", [W, DD, H], {"wood": wood, "woodl": "wood#fde2b0", "lea": "leather#6e2a2c", "steel": "metal#c9cdd2",
                                 "blk": "rubber#1c1d1f"})
    T = 18
    A, B = 70, 530                     # outer faces of the side panels (body 460 wide; the tray is 600)
    cx = (A + B) / 2
    # side panels: back edge upright, front edge leaning forward to the floor, round hand hole, arch cut at the bottom
    ol = [(30, 62), (30, 560), (60, 585), (330, 585), (360, 560), (600, 62), (470, 62), (440, 180), (190, 200), (130, 62)]
    hole = circ(225, 430, 52, 24)
    path = P(round_poly(ol, 30)) + " " + P(hole)
    d.slab("panel-l", "side", path, [A, A + T], "wood", r=4)
    d.slab("panel-r", "side", path, [B - T, B], "wood", r=4)
    d.box("arm-l", [A - 4, 585, 70, A + T + 4, 600, 300], "woodl", r=5)
    d.box("arm-r", [B - T - 4, 585, 70, B + 4, 600, 300], "woodl", r=5)
    for i, (z, y) in enumerate(((60, 560), (160, 330), (520, 140), (300, 240), (60, 300))):
        d.cyl(f"bolt{i}", [A - 1, y, z], [A + T + 1, y, z], 9, "steel", copies=[[B - A - T, 0, 0]])
    # seat frame and front apron under the seat, slotted back board of the footrest, low front stretcher
    d.box("seat-board", [A + T, 280, 140, B - T, 300, 500], "wood", r=3)
    d.box("apron", [A + T + 30, 210, 470, B - T - 30, 285, 490], "woodl", r=4)
    d.box("foot-back", [A + T, 60, 400, B - T, 210, 418], "woodl", r=3)
    d.box("slot", [A + 70, 90, 417, A + 80, 200, 419], "plastic#6a5030", soft=True, copies=[[B - A - 150, 0, 0]])
    d.box("stretcher", [A + T, 66, 560, B - T, 95, 585], "woodl", r=4)
    d.box("stretcher-b", [A + T, 140, 60, B - T, 170, 80], "wood", r=4)
    # footboard projecting forward with a middle divider and rainbow foot straps
    d.box("footboard", [A + 35, 140, 418, B - 35, 160, DD], "woodl", r=5)
    d.box("divider", [cx - 32, 160, 520, cx + 32, 215, DD - 10], "woodl", r=10)
    rainbow = ["fabric#e8c21c", "fabric#2f9a3c", "fabric#d4262a", "fabric#2050c0"]
    for side, x0 in (("l", A + 55), ("r", cx + 45)):
        for k, col in enumerate(rainbow):
            dz = k * 9
            d.strap(f"fstrap-{side}{k}", [[x0, 160, 560 + dz], [x0 + 15, 200, 560 + dz], [x0 + 90, 205, 560 + dz],
                                          [x0 + 105, 160, 560 + dz]], [9, 3], col, bend=25, soft=True)
    # upholstery: seat cushion, reclined tall backrest, headrest with the striped band
    d.box("seat", [A + T + 6, 300, 150, B - T - 6, 360, 520], "lea", r=18, puff=6)
    br = rot("x", -8, [cx, 300, 150])
    d.box("back", [A + T + 20, 330, 85, B - T - 20, 735, 150], "lea", r=30, puff=6, rot=br)
    d.box("back-board", [A + T + 30, 330, 70, B - T - 30, 720, 86], "wood", r=6, rot=br)
    d.box("head", [cx - 120, 742, 70, cx + 120, 830, 165], "lea", r=30, puff=4, rot=br)
    stripes = ["fabric#e8c21c", "fabric#2f9a3c", "fabric#d4262a", "fabric#2f62c8", "fabric#e07a20"]
    for k, col in enumerate(stripes):
        d.box(f"head-band{k}", [cx - 123, 748 + k * 8, 67, cx + 123, 755 + k * 8, 168], col, r=3, rot=br, soft=True)
    # abductor pommel on a steel flat bar with a black knob under the seat
    d.box("pommel", [cx - 55, 370, 470, cx + 55, 510, 545], "lea", r=20, puff=4)
    d.box("pommel-seam", [cx - 48, 377, 545, cx + 48, 503, 547], "leather#8a4a48", r=10, soft=True)
    d.bar("pommel-bar", [cx, 225, 548], [cx, 500, 548], [24, 4], "steel")
    d.cyl("pommel-knob-s", [cx, 225, 520], [cx, 190, 520], 12, "steel")
    d.cyl("pommel-knob", [cx, 200, 520], [cx, 175, 520], 40, "blk", sides=8)
    # removable light-wood tray on the armrests (photo 2), curved cut-out around the child
    tray = [(0, 150), (cx - 150, 150)] + [(cx - 150 * math.cos(math.radians(t)), 250 + 90 * math.sin(math.radians(t)))
                                          for t in range(15, 166, 15)] + [(cx + 150, 150), (W, 150), (W, 610), (0, 610)]
    d.slab("tray", "top", P(round_poly(tray, 25)), [600, 620], "plastic#f1d9a8", r=5)   # photo 2: smooth pale laminate
    # castors under the panel feet
    for x in (A + T / 2, B - T / 2):
        for z in (80, 540):
            d.box(f"cplate-{x}-{z}", [x - 25, 56, z - 25, x + 25, 64, z + 25], "steel", r=2)
            caster(d, f"castor-{x}-{z}", x, z, 40)
    return d

if __name__ == "__main__":
    main({"xyrt-8": xyrt8, "xyrt-9": xyrt9})
