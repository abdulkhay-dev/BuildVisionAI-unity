from pd1_lib import *
W, D_, H = 370, 900, 300
d = K("xyrt-117", [W, D_, H], {"y": "gloss#f3a41e", "seat": "leather#f0682c", "red": "leather#e03030",
                                "blk": "rubber#1c1c1c", "dmp": "black#161616", "chrome": "chrome"})
cx = W / 2
# rear foot: cross tube with big rubber end feet; front cross tube with black caps
d.cyl("rear-tube", [40, 45, 45], [W - 40, 45, 45], 40, "y")
d.lathe("rear-foot", [0, 45, 45], [[18, 0], [40, 6], [44, 30], [40, 56], [18, 62]], "blk", axis="x")
d.lathe("rear-foot2", [W - 62, 45, 45], [[18, 0], [40, 6], [44, 30], [40, 56], [18, 62]], "blk", axis="x")
d.box("rear-brk", [cx - 28, 45, 25, cx + 28, 110, 70], "y", r=6)
d.cyl("rear-pad", [31, 0, 45], [31, 6, 45], 84, "blk", copies=[[W - 62, 0, 0]])     # flared rubber pad under each foot (photo)
d.cyl("front-tube", [40, 34, 820], [W - 40, 34, 820], 34, "y")
d.cyl("front-cap", [6, 34, 820], [46, 34, 820], 58, "blk", copies=[[W - 52, 0, 0]])
d.box("front-brk", [cx - 24, 34, 795, cx + 24, 95, 840], "y", r=6)
d.bar("front-post", [cx, 60, 812], [cx, 185, 800], [40, 30], "y", r=5)
# the rail
d.bar("rail", [cx, 115, 30], [cx, 85, 830], [50, 42], "y", r=5)
# seat on its bracket at the rear
d.box("seat-brk", [cx - 50, 125, 80, cx + 50, 205, 270], "y", r=6)
d.sphere("bolt", [cx + 51, 150, 110], 12, "chrome", copies=[[0, 0, 130], [0, 35, 0], [0, 35, 130]], mirror="x")
d.box("seat", [35, 200, 50, W - 35, 292, 305], "seat", r=36, puff=7)
# lever: pivot bracket on the rail, yellow tube up and forward, red foam sleeve, T handle with red grips
d.box("piv", [cx - 30, 95, 440, cx + 30, 150, 500], "y", r=6)
d.sphere("piv-b", [cx + 31, 128, 470], 18, "chrome", mirror="x")
d.tube("lever", [[cx, 130, 470], [cx, 255, 540], [cx, 262, 600], [cx, 262, 862]], 32, "y", bend=60)
d.cyl("sleeve", [cx, 262, 575], [cx, 262, 790], 50, "red")
d.cyl("t-bar", [45, 262, 868], [W - 45, 262, 868], 32, "y")
d.cyl("grip", [40, 262, 868], [150, 262, 868], 48, "red", copies=[[W - 190, 0, 0]])
d.sphere("grip-end", [40, 262, 868], 46, "red", copies=[[W - 80, 0, 0]])
# hydraulic damper from the front bracket to the lever
d.cyl("damper", [cx + 30, 180, 800], [cx + 30, 210, 625], 40, "dmp")
d.cyl("damper-rod", [cx + 30, 210, 625], [cx + 30, 228, 552], 16, "chrome")
d.box("dmp-lug", [cx + 10, 165, 795, cx + 50, 195, 820], "dmp", r=4)
# black footplates with straps both sides of the front bracket
FR = rot("x", -22, [0, 40, 800])
d.box("foot", [45, 40, 785, 145, 175, 806], "blk", r=10, rot=FR, mirror="x")
d.box("foot-heel", [45, 40, 806, 145, 66, 845], "blk", r=8, rot=FR, mirror="x")
d.add("strap", "strap", "fabric#151515", path=[[43, 115, 806], [95, 140, 845], [147, 115, 806]], section=[40, 4], bend=30, rot=FR, mirror="x", soft=True)
d.cyl("foot-axle", [150, 70, 805], [W - 150, 70, 805], 26, "y")
d.save()
