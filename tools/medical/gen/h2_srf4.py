from h2lib import *
# XY-SRF-IV hydrocollator 140 L (photo front-right): stainless tank cabinet on 4 castors, open top with the cover
# pushed back, rear upstand with a white control panel at the right, chrome inlet pipe, chrome handle on the right
# side, big blue logo on the front.
W, DP, H = 620, 520, 1050
d = D("xy-srf-iv", [W, DP, H], {
    "steel": "metal#cbcfd3", "inner": "metal#a9aeb3", "panel": "plastic#f4f5f6", "frame": "plastic#c9cdd2",
    "blue": "gloss#2f6fd0", "dark": "black#1f2226", "water": "acrylic#9fb3bfa0"})
Y0, TOP = 98, 922
d.box("frame", [10, 76, 10, W - 10, Y0 + 2, DP - 10], "metal#8d9196", r=4)
hole = rr(45, 120, W - 45, DP - 45, 14)
d.slab("body", "top", ring(rr(0, 0, W, DP, 6), hole), [Y0, TOP], "steel", r=5)
d.slab("tank-floor", "top", P(rr(40, 40, W - 40, DP - 40, 10)), [TOP - 420, TOP - 400], "inner", r=3)
d.slab("rim", "top", ring(rr(-3, -3, W + 3, DP + 3, 8), hole), [TOP - 6, TOP + 6], "steel", r=4)
d.slab("water", "top", P(offset(hole, 3)), [TOP - 130, TOP - 126], "water", r=2, soft=True)
# cover pushed to the back (flat plate over the rear part of the opening with a round bar along its front edge)
d.box("cover", [30, TOP + 4, 60, W - 30, TOP + 14, 190], "steel", r=3)
d.cyl("cover-bar", [40, TOP + 18, 186], [W - 40, TOP + 18, 186], 18, "steel")
# rear upstand across the back with the control panel at the right
d.box("upstand", [0, TOP, 0, W, H, 62], "steel", r=5)
d.box("ctl", [380, TOP + 30, 58, 590, H - 14, 70], "frame", r=5)
d.box("ctl-face", [388, TOP + 36, 66, 582, H - 20, 72], "panel", r=3)
d.decal("ctl-band", [485, TOP + 46, 72.5], [180, 14], "front", "blue", soft=True)
d.decal("ctl-led", [418, H - 44, 72.5], [40, 24], "front", "screen", soft=True)
d.decal("ctl-key", [470, H - 40, 72.5], [11, 9], "front", "blue", soft=True, repeat=rep(4, [26, 0, 0]),
        copies=[[0, -22, 0]])
# chrome water-inlet pipe out of the upstand front at the right, forward, down into the tank
d.tube("inlet", [[505, 985, 60], [505, 985, 200], [505, TOP - 60, 200]], 22, "chrome", bend=40)
d.lathe("inlet-nut", [505, 985, 60], [[0, 0], [20, 0], [20, 18], [0, 18]], "chrome", axis="z")
# right side grab handle near the front
bar_handle(d, "side-handle", [W, 800, 300], [W, 800, 450], [40, 0, 0], dia=22)
d.box("side-plate", [W - 1, 780, 285, W + 4, 820, 315], "chrome", r=4, copies=[[0, 0, 150]])
# logo on the front, left half
logo_round(d, "logo", [205, 520, DP + 1], 92)
text(d, "logo-t1", "翔宇医疗", [266, 502, DP + 1.5], 40, "blue", stroke=6)
text(d, "logo-t2", "XIANGYU MEDICAL", [266, 478, DP + 1.5], 14, "blue", stroke=2.4)
d.slab("logo-r", "front", ring(ell(268, 572, 8, 8), ell(268, 572, 5.5, 5.5)), [DP, DP + 1.5], "blue", r=0.5, soft=True)
# castors
for i, (x, z) in enumerate([(70, 80), (W - 70, 80), (70, DP - 60), (W - 70, DP - 60)]):
    d.add(f"castor{i}", "caster", at=[x, 0, z], d=75, mat="rubber#6b7077")
d.box("brake", [40, 55, DP - 30, 100, 66, DP + 6], "plastic#9aa0a8", r=4, copies=[[W - 140, 0, 0]])
d.save()
