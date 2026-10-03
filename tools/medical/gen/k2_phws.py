"""xy-ph-workstation — balance-system computer trolley: 5-star base, flat silver pole, two tinted glass shelves,
printer, ~40" monitor (kinesio-2)."""
import math
from k2lib import *

d = D("xy-ph-workstation", [900, 720, 1700], {
    "silver": "metal#c3c7cc", "alu": "plastic#b9bdc3", "black": "plastic#18191b", "glass": "acrylic#123a32f4", "glass-edge": "gloss#264c44",
    "white": "plastic#eceef0", "grey": "plastic#9a9fa6", "bezel": "gloss#141517"})
CX, CZ = 450, 360
# --- 5-arm star base (silver, arms sloping down to the castors), one arm pointing straight forward
for i in range(5):
    a = math.radians(90 + i * 72)
    ex, ez = CX + 355 * math.cos(a), CZ + 355 * math.sin(a)
    hx, hz = CX + 50 * math.cos(a), CZ + 50 * math.sin(a)
    d.bar(f"arm{i}", [hx, 175, hz], [ex, 112, ez], [62, 34], "alu", r=12)
    d.cyl(f"arm-cap{i}", [ex, 100, ez], [ex, 128, ez], 52, "alu")
    caster(d, f"castor{i}", [ex, 0, ez], 75, "rubber#d8dadd")
d.lathe("hub", [CX, 100, CZ], [[0, 0], [95, 0], [95, 40], [80, 90], [62, 120], [0, 120]], "alu")
# --- flat silver pole (oval ~120 x 70) with a front groove
d.loft("pole", [sec(210, 120, 70, 35, CX, CZ), sec(1180, 120, 70, 35, CX, CZ)], "silver")
d.box("pole-groove", [CX - 12, 230, CZ + 33, CX + 12, 1150, CZ + 37], "grey", r=3)
# --- shelves: tinted glass on silver brackets; keyboard + mouse up, printer down
for nm, y, z0 in (("upper", 815, CZ + 30), ("lower", 555, CZ + 10)):
    d.box(f"bracket-{nm}", [CX - 60, y - 40, CZ + 20, CX + 60, y, z0 + 250], "silver", r=10)
    d.box(f"shelf-{nm}", [CX - 280, y, z0, CX + 280, y + 10, z0 + 330], "glass", r=6)
    d.box(f"shelf-edge-{nm}", [CX - 281, y, z0 + 327, CX + 281, y + 10, z0 + 331], "glass-edge", r=2)
d.box("keyboard", [CX - 250, 825, CZ + 140, CX + 190, 845, CZ + 290], "black", r=5)
d.box("keys", [CX - 240, 845, CZ + 150, CX + 180, 849, CZ + 280], "plastic#2a2c30", r=2)
d.sphere("mouse", [CX + 235, 838, CZ + 230], 10, "black", radii=[30, 16, 46])
# a small laser printer (~140 high): white body, dark ribbed output tray recessed in its top
d.box("printer", [CX - 190, 565, CZ + 60, CX + 170, 705, CZ + 330], "white", r=14)
d.box("printer-top", [CX - 160, 698, CZ + 90, CX + 140, 708, CZ + 250], "plastic#2b2d31", r=6)
d.decal("printer-rib", [CX - 10, 708.6, CZ + 110], [280, 4], "top", "plastic#45484e", soft=True, repeat=rep(6, [0, 0, 24]))
d.box("printer-slot", [CX - 120, 680, CZ + 329, CX + 100, 688, CZ + 332], "plastic#3a3c40", r=2)
d.decal("printer-vent", [CX + 171, 610, CZ + 280], [6, 36], "right", "grey", soft=True, repeat=rep(5, [0, 0, -14]))
d.box("power-brick", [CX - 270, 565, CZ + 120, CX - 210, 600, CZ + 220], "black", r=6)
# --- monitor: VESA bracket with two black clamp knobs, ~40" landscape panel (lit blue software as decals)
d.box("vesa", [CX - 110, 1120, CZ - 20, CX + 110, 1200, CZ + 40], "black", r=6)
d.box("clamp", [CX - 90, 1090, CZ + 30, CX - 60, 1150, CZ + 60], "black", r=6, copies=[[150, 0, 0]])
Y0, Y1, MZ = 1150, 1700, CZ + 100
d.box("mon-back", [CX - 420, Y0 + 20, CZ + 40, CX + 420, Y1 - 20, MZ - 15], "bezel", r=14)
scr(d, "monitor", [CX - 445, Y0, MZ - 18, CX + 445, Y1, MZ], "bezel", r=6, face="front", bezel=16)
u0, u1, v0, v1, zz = CX - 427, CX + 427, Y0 + 16, Y1 - 16, MZ + 0.8
d.decal("ui-bg", [CX, (v0 + v1) / 2, zz], [u1 - u0, v1 - v0], "front", "gloss#46a9e2", soft=True)
d.decal("ui-title", [CX, v1 - 26, zz + 0.5], [u1 - u0, 50], "front", "gloss#1f63b0", soft=True)
d.decal("ui-tree", [u0 + 85, (v0 + v1) / 2 - 10, zz + 0.5], [150, v1 - v0 - 110], "front", "plastic#f4f6f8", soft=True)
d.decal("ui-form", [CX + 70, (v0 + v1) / 2 + 20, zz + 0.5], [560, v1 - v0 - 170], "front", "gloss#82c7ee", soft=True)
d.decal("ui-field", [CX - 20, v1 - 110, zz + 1.0], [130, 18], "front", "plastic#ffffff", soft=True,
        repeat=rep(9, [0, -32, 0]), copies=[[230, 0, 0]])
d.decal("ui-task", [CX, v0 + 14, zz + 0.5], [u1 - u0, 26], "front", "gloss#0f3f86", soft=True)
d.save()
