from lib import *
from p2util import *
# beige pelvic-floor magnetic chair: waisted side panels, padded armrests, seat with coil ring, 3-panel front skirt, backrest + headrest
d = D("sd-pdc-2", [800, 900, 1250], {"pu": "leather#ddd3c2", "pu2": "leather#d6cbb9", "line": "plastic#c9bda9",
      "seam": "plastic#a89c88", "black": "gloss#121315", "chrome": "chrome", "white": "plastic#f8f8f6", "logo": "gloss#2f8fd8"})
side = "M 90 0 L 790 0 Q 845 0 845 60 L 845 190 Q 845 330 770 420 Q 735 470 765 540 L 800 625 L 90 625 Z"
d.add("side", "slab", "pu", plane="side", outline=side, w=[0, 150], r=30, copies=[[650, 0, 0]])
d.add("arm", "box", "pu", box=[-5, 615, 70, 165, 702, 880], r=36, puff=4, copies=[[640, 0, 0]])
# decorative recessed lines on the outer faces
for sx, x in (("l", -1.5), ("r", 801.5)):
    # A: from under the armrest diagonally down-back to the rear bottom; B: horizontal from the front at ~355 then down-back;
    # C: horizontal from the front at ~160 then down to the floor
    d.add(f"line1-{sx}", "sweep", "line", path=[[x, 600, 450], [x, 330, 270], [x, 60, 120]], section=[3, 15], shape="rect", r=1, bend=250, soft=True)
    d.add(f"line2-{sx}", "sweep", "line", path=[[x, 355, 835], [x, 355, 520], [x, 20, 300]], section=[3, 15], shape="rect", r=1, bend=160, soft=True)
    d.add(f"line3-{sx}", "sweep", "line", path=[[x, 160, 835], [x, 160, 660], [x, 20, 570]], section=[3, 13], shape="rect", r=1, bend=90, soft=True)
# seat, coil ring, seat seams
d.box("seat", [150, 350, 220, 650, 470, 800], "pu", r=32, puff=10)
d.add("ring", "lathe", "white", at=[400, 481, 330], profile=[[92, 0], [112, 0], [112, 3], [92, 3]], caps=False)
d.box("seat-seam", [310, 360, 805, 313, 462, 810], "seam", soft=True, copies=[[177, 0, 0]])
# front skirt in 3 panels
d.box("skirt", [162, 20, 780, 638, 430, 848], "pu", r=26, puff=6)
d.box("skirt-seam", [318, 40, 852, 321, 410, 856], "black", soft=True, copies=[[161, 0, 0]])
# backrest + headrest, tilted back
t = rot("x", -8, [400, 440, 150])
d.box("back", [165, 430, 60, 635, 1060, 230], "pu", r=42, puff=8, rot=t)
d.box("back-band", [285, 450, 225, 515, 1045, 242], "pu2", r=20, puff=4, rot=t)
d.box("back-seam", [285, 815, 245, 515, 819, 248], "seam", soft=True, rot=t)
d.cyl("head-post", [335, 1040, 150], [335, 1090, 150], 16, "chrome", rot=t, copies=[[130, 0, 0]])
d.box("head", [238, 1075, 95, 562, 1250, 205], "pu", r=55, puff=8, rot=t)
d.box("head-seam", [290, 1080, 211, 293, 1245, 214], "line", soft=True, rot=t, copies=[[217, 0, 0]])
# right panel: control panel and logo
d.box("ctrl-rim", [797, 468, 500, 803, 552, 645], "metal#c9ccd0", r=12)
d.box("ctrl", [799, 474, 506, 805, 546, 639], "black", r=9)
d.box("ctrl-icon", [805, 488, 540, 806, 498, 585], "white", soft=True)
d.box("ctrl-icon2", [805, 500, 592, 806, 530, 602], "white", soft=True, rot=rot("x", -20, [805, 515, 597]))
d.cyl("logo", [800, 255, 690], [802.5, 255, 690], 44, "logo", soft=True)
d.box("logo-t", [800, 257, 575, 802.5, 275, 662], "logo", soft=True)
d.box("logo-s", [800, 242, 575, 802.5, 248, 662], "logo", soft=True)
d.save()
