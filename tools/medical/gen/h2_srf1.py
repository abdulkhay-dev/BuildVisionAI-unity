from h2lib import *
# XY-SRF-I hydrocollator 70 L: brushed stainless cabinet with black corner trims on a black frame and 4 castors,
# a stainless top rim and flat lid with a chrome bar handle, a white control box at the front upper right,
# recessed chrome grab handles on both sides.
W, DP, H = 620, 430, 860
d = D("xy-srf-i", [W, DP, H], {
    "steel": "metal#cbcfd3", "trim": "black#26292d", "panel": "plastic#f4f5f6", "frame": "plastic#c9cdd2",
    "blue": "gloss#2f6fd0", "dark": "black#1f2226"})
X0, X1 = 18, W - 18                       # body (the side handles stick out to 0 / W)
Y0, TOP = 100, 818
d.box("frame", [X0 + 4, 76, 8, X1 - 4, Y0 + 2, DP - 8], "trim", r=4)
d.box("body", [X0, Y0, 0, X1, TOP, DP], "steel", r=5)
d.box("corner", [X0 - 2, Y0, DP - 8, X0 + 6, TOP - 2, DP + 2], "trim", r=2, copies=[[X1 - X0 - 4, 0, 0]])
d.box("corner-b", [X0 - 2, Y0, -2, X0 + 12, TOP - 2, 14], "trim", r=3, copies=[[X1 - X0 - 10, 0, 0]])
# top rim + lid + bar handle
d.box("rim", [X0 - 4, TOP - 2, -4, X1 + 4, TOP + 22, DP + 4], "steel", r=4)
d.box("lid", [X0 + 14, TOP + 16, 12, X1 - 14, TOP + 30, DP - 6], "steel", r=4)
d.box("lid-hinge", [X0 + 40, TOP + 18, 2, X1 - 40, TOP + 34, 14], "steel", r=5)
d.tube("lid-handle", [[W / 2 - 75, TOP + 30, DP - 40], [W / 2 - 55, TOP + 42, DP - 40], [W / 2 + 55, TOP + 42, DP - 40],
                      [W / 2 + 75, TOP + 30, DP - 40]], 12, "chrome", bend=15)
# control box at the front upper right
CX0, CX1, CY0, CY1 = 335, 505, 630, 745
d.box("ctl", [CX0, CY0, DP - 2, CX1, CY1, DP + 16], "frame", r=8)
d.box("ctl-face", [CX0 + 10, CY0 + 10, DP + 10, CX1 - 10, CY1 - 10, DP + 18], "panel", r=4)
d.decal("ctl-band", [(CX0 + CX1) / 2, CY0 + 26, DP + 18.5], [CX1 - CX0 - 24, 22], "front", "blue", soft=True)
d.decal("ctl-led", [CX0 + 42, CY1 - 42, DP + 18.5], [46, 26], "front", "screen", soft=True)
d.decal("ctl-key", [CX0 + 95, CY1 - 34, DP + 18.5], [12, 10], "front", "gloss#2f6fd0", soft=True,
        repeat=rep(2, [30, 0, 0]), copies=[[0, -24, 0]])
d.decal("ctl-text", [(CX0 + CX1) / 2, CY1 - 16, DP + 18.5], [110, 5], "front", "plastic#9aa0a8", soft=True)
# recessed side grab handles (dark slot + chrome bar), both sides
d.box("slot", [X0 - 2, 715, 250, X0 + 1, 765, 400], "dark", r=10, soft=True, copies=[[X1 - X0 + 1, 0, 0]])
d.cyl("side-bar", [X0 - 16, 752, 255], [X0 - 16, 752, 395], 18, "chrome", copies=[[X1 - X0 + 32, 0, 0]])
d.box("side-bracket", [X0 - 24, 735, 240, X0 + 1, 770, 262], "chrome", r=6,
      copies=[[0, 0, 136], [X1 - X0 + 23, 0, 0], [X1 - X0 + 23, 0, 136]])
# castors (front pair with brake pedals)
for i, (x, z) in enumerate([(70, 80), (W - 70, 80), (70, DP - 50), (W - 70, DP - 50)]):
    d.add(f"castor{i}", "caster", at=[x, 0, z], d=75, mat="rubber#6b7077")
d.box("brake", [40, 55, DP - 22, 100, 66, DP + 10], "plastic#9aa0a8", r=4, copies=[[W - 140, 0, 0]])
d.save()
