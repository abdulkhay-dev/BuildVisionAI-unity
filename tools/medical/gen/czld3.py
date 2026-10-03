"""XY-K-CZLD-III whole-body sonic vibration bed. Length along z (inventory size [700, 2000, 1115]): foot end z = 0,
head end with the screen tongue at the front z = 2000. Modelled with the top surface at 850 (range 715-1115)."""
import math
from lib import D, rot
from sflib import poly_path, round_poly, rrect_pts, quad

W, L = 700, 2000
d = D("xy-k-czld-iii", [W, L, 1115], {
    "shell": "plastic#f3f4f6", "base": "plastic#5a5e66", "mat": "leather#7fb3dc", "pillow": "leather#5d9bd3",
    "led": "gloss#33c3d6", "bellows": "rubber#26282b", "logo": "plastic#3d8fd0", "bezel": "plastic#585d65"})
cx = W / 2
# ---- base: dark-grey plate with a white top and cyan rim line, U-notch at the head end, 4 castors with grey covers
bz0, bz1 = 230, 1570
base = round_poly([(25, bz0), (675, bz0), (675, bz1), (460, bz1), (460, bz1 - 130), (240, bz1 - 130), (240, bz1), (25, bz1)], 70, 6)
d.add("base", "slab", "base", plane="top", outline=poly_path(base), w=[92, 150], r=14)
d.add("base-led", "slab", "led", plane="top", outline=poly_path(base), w=[150, 155], r=1)
inner = round_poly([(40, bz0 + 15), (660, bz0 + 15), (660, bz1 - 15), (475, bz1 - 15), (475, bz1 - 145), (225, bz1 - 145), (225, bz1 - 15), (40, bz1 - 15)], 60, 6)
d.add("base-top", "slab", "shell", plane="top", outline=poly_path(inner), w=[150, 172], r=8)
for k, (x, z) in enumerate(((95, bz0 + 70), (605, bz0 + 70), (95, bz1 - 70), (605, bz1 - 70))):
    d.add(f"castor{k}", "caster", at=[x, 0, z], d=75)
    d.box(f"castor{k}-cover", [x - 42, 72, z - 48, x + 42, 100, z + 42], "plastic#9aa0a8", r=10)
# ---- pedestal: white tapered column with the Sunnyou logo, black bellows above it
pc = 870
d.add("pedestal", "loft", "shell", sections=[
    {"at": 170, "w": 440, "d": 820, "r": 70, "cx": cx, "cz": pc},
    {"at": 520, "w": 350, "d": 560, "r": 55, "cx": cx, "cz": pc}])
d.add("logo", "decal", at=[W - 135, 380, pc], size=[230, 34], face="right", mat="logo")
d.add("logo-sub", "decal", at=[W - 140, 345, pc], size=[110, 10], face="right", mat="plastic#9fc6e8")
d.add("bellows", "loft", "bellows", sections=[
    {"at": 518, "w": 310, "d": 500, "r": 40, "cx": cx, "cz": pc},
    {"at": 700, "w": 310, "d": 500, "r": 40, "cx": cx, "cz": pc}])
d.box("bellows-rib", [cx - 162, 540, pc - 257, cx + 162, 552, pc + 257], "bellows", r=10, repeat={"n": 5, "step": [0, 32, 0]})
# ---- under-body: white skirt under the top, tapering down, with a small green button
d.add("underbody", "loft", "shell", sections=[
    {"at": 698, "w": 380, "d": 980, "r": 90, "cx": cx, "cz": pc + 40},
    {"at": 785, "w": 560, "d": 1400, "r": 140, "cx": cx, "cz": pc + 40}])
d.cyl("button", [W - 118, 745, 1180], [W - 108, 745, 1180], 18, "gloss#2fae4f", soft=True)
# ---- top shell: body + narrower tongue at the head end, LED line on its sides
tz = 1640
shell = round_poly([(0, 0), (W, 0), (W, tz), (W - 70, tz + 110), (W - 110, L), (110, L), (70, tz + 110), (0, tz)], 90, 8)
d.add("shell", "slab", "shell", plane="top", outline=poly_path(shell), w=[785, 838], r=16)
d.box("led", [-2, 800, 60, 3, 808, tz - 30], "led", r=2, soft=True, copies=[[W + 1, 0, 0]])
d.box("led-end", [60, 800, -2, W - 60, 808, 3], "led", r=2, soft=True)
d.add("shell-logo", "decal", at=[W + 1, 815, 1230], size=[150, 22], face="right", mat="logo")
# ---- light-blue mattress inset in the shell, arched white side rails, blue pillow at the head end
d.add("mattress", "slab", "mat", plane="top", outline=poly_path(rrect_pts(38, 35, W - 38, tz - 20, 60)), w=[820, 856], r=12)
# a raised white handle arch over each rim at mid-length (open underneath: the mattress shows through, photo 1)
wave = quad((520, 832), (700, 836), (790, 893)) + quad((790, 893), (900, 905), (1010, 893))[1:] + quad((1010, 893), (1100, 836), (1280, 832))[1:]
low = quad((600, 836), (720, 838), (800, 868)) + quad((800, 868), (900, 878), (1000, 868))[1:] + quad((1000, 868), (1080, 838), (1200, 836))[1:]
for k, (x0, x1) in enumerate(((4, 50), (W - 50, W - 4))):
    d.add(f"hump{k}", "slab", "shell", plane="side", outline=poly_path(wave + [(1280, 815)] + list(reversed(low)) + [(520, 815)]),
          w=[x0, x1], r=10)
d.box("pillow", [150, 852, 1330, W - 150, 935, 1590], "pillow", r=34, puff=8)
# ---- the screen in the tongue (dark, slight tilt towards the foot end)
tilt = rot("x", -8, [cx, 838, 1870])
d.box("screen-bezel", [cx - 165, 832, 1735, cx + 165, 846, 1960], "bezel", r=14, rot=tilt)
d.add("screen", "screen", box=[cx - 135, 845, 1760, cx + 135, 849, 1935], face="top", mat="bezel", bezel=6, r=6, rot=tilt)
d.save()
