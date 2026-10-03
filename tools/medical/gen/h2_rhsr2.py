from h2lib import *
# RH-SR-II compact hydrocollator: brushed stainless box, acrylic lid with a moulded handle, chrome side handle,
# oval logo plate, thermostat knob in a blue ring + 2 lamps, vent patch on the left side, rubber feet.
W, DP, H = 420, 340, 660
d = D("rh-sr-ii", [W, DP, H], {
    "steel": "metal#c3c7cb", "dark": "black#2a2d31", "lid": "glass", "lidh": "acrylic#cfd8dfa0", "blue": "gloss#2f6fd0",
    "white": "gloss#ffffff", "lamp": "gloss#d8f0dc"})
TOP = 632
d.box("body", [0, 14, 0, W, TOP, DP], "steel", r=6)
d.box("lip", [-3, TOP - 4, -3, W + 3, TOP + 14, DP + 3], "steel", r=4)
d.box("lip-inner", [14, TOP + 2, 14, W - 14, TOP + 15, DP - 14], "dark", r=3, soft=True)
d.box("lid", [10, TOP + 8, 10, W - 10, TOP + 20, DP - 10], "lid", r=6)
# moulded arched handle across the width at the middle of the lid
d.box("lid-rim", [8, TOP + 8, 8, W - 8, TOP + 34, 20], "lidh", r=5, copies=[[0, 0, DP - 28]])
d.sweep("lid-handle", [[30, TOP + 18, DP * 0.4], [36, TOP + 50, DP * 0.4], [W - 36, TOP + 50, DP * 0.4], [W - 30, TOP + 18, DP * 0.4]],
        [30, 16], "lidh", shape="rect", r=7, bend=30)
# corner shadow lines
d.box("corner", [-1, 20, DP - 4, 3, TOP - 6, DP + 1], "metal#8d9196", r=1, soft=True, copies=[[W - 2, 0, 0]])
# chrome grab handle on the left side near the front
d.sweep("side-handle", [[0, 560, 80], [-40, 560, 95], [-40, 560, 245], [0, 560, 260]], [40, 14], "chrome", shape="rect", r=6, bend=25, roll=90)
d.box("side-plate", [-4, 538, 65, 1, 582, 95], "chrome", r=4, copies=[[0, 0, 150]])
# vent perforation patch at the lower front of the left side
d.box("vent", [-1.5, 70, 130, 0, 190, 200], "metal#9da1a6", r=2, soft=True)
d.box("vent-hole", [-2.5, 78, 138, -1, 84, 144], "dark", r=1, soft=True,
      repeat=rep(9, [0, 12.5, 0]), copies=[[0, 0, 13], [0, 0, 26], [0, 0, 39], [0, 0, 52]])
# oval logo plate
d.slab("logo", "front", P(ell(220, 440, 76, 30)), [DP - 1, DP + 2], "white", r=1)
logo_round(d, "logo-mark", [176, 440, DP + 2], 34)
text(d, "logo-t1", "翔宇医疗", [200, 437, DP + 2.5], 16, "blue", stroke=2.6)
d.decal("logo-t2", [237, 428, DP + 2.5], [72, 3], "front", "gloss#7f9fd8", soft=True)
# thermostat knob in a blue ring, two lamps
d.lathe("knob-ring", [362, 110, DP], [[0, 0], [32, 0], [32, 6], [24, 8], [0, 8]], "blue", axis="z")
d.lathe("knob", [362, 110, DP + 6], [[0, 0], [22, 0], [22, 22], [18, 26], [0, 26]], "black#202224", axis="z")
d.box("knob-grip", [359, 92, DP + 26, 365, 128, DP + 34], "black#202224", r=3)
d.lathe("lamp", [225, 108, DP], [[0, 0], [8, 0], [8, 5], [5, 8], [0, 8]], "lamp", axis="z", copies=[[45, 0, 0]])
# rubber feet
d.cyl("foot", [40, 0, 40], [40, 16, 40], 34, "rubber", copies=[[W - 80, 0, 0], [0, 0, DP - 80], [W - 80, 0, DP - 80]])
d.save()
