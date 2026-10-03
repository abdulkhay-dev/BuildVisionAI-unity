"""xyj-2 Shoulder Wheel (wall). Photo front, ~0.99 mm/px: W 770 = the wheel, H 980."""
import math
from k7lib import *

d = D("xyj-2", [770, 340, 980], {
    "teal": "plastic#12906f", "tealdk": "plastic#0b6a50", "chrome": "chrome", "black": "plastic#1b1d1f",
    "rubber": "rubber#202224"})
CX = 385
rail_unit(d, CX, 980, 50, (278, 525), None, plate_h=(40, 52), lever=(661, 454, 36))
WC = [385, 385]          # wheel centre
R = 374                  # rim tube centre radius (outer Ø770)
ZW = (186, 194)          # flat bars' thickness along z
ZR = 194                 # rim tube centre z


def bar_outline(a_deg, w, r0, r1, slots=()):
    """Flat bar along angle a through the wheel centre from radius r0 to r1 (negative = other side), with slot holes."""
    a = math.radians(a_deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    def P(r, s): return (WC[0] + ux * r + nx * s, WC[1] + uy * r + ny * s)
    pts = [P(r0, -w / 2), P(r1, -w / 2), P(r1, w / 2), P(r0, w / 2)]
    out = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    for (s0, s1, sw) in slots:
        q = [P(s0, -sw / 2), P(s0, sw / 2), P(s1, sw / 2), P(s1, -sw / 2)]
        out += " M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in q) + " Z"
    return out


# --- rim: round teal tube
ring = [[WC[0] + R * math.cos(math.radians(k * 7.5)), WC[1] + R * math.sin(math.radians(k * 7.5)), ZR] for k in range(49)]
d.tube("rim", ring, 22, "teal")
# --- two flat bars across the whole diameter, crossing at the hub (~31° and ~-57°); the -57° one is slotted
d.slab("bar-a", "front", bar_outline(31, 44, -R, R), list(ZW), "teal", r=2)
d.slab("bar-b", "front", bar_outline(-57, 44, -R, R, slots=[(-345, -165, 13), (95, 300, 13)]), [ZW[1], ZW[1] + 8],
       "teal", r=2)
# --- hub: black friction disc on the carriage, chrome axle, round teal boss on the crossing, chrome bolt
d.cyl("hub-disc", [WC[0], WC[1], 120], [WC[0], WC[1], 150], 122, "black")
d.cyl("axle", [WC[0], WC[1], 149], [WC[0], WC[1], 186], 30, "chrome")
d.cyl("hub-boss", [WC[0], WC[1], 201], [WC[0], WC[1], 208], 58, "teal")
d.cyl("hub-bolt", [WC[0], WC[1], 207], [WC[0], WC[1], 216], 18, "chrome")
# bolts where the bars meet the rim
for nm, a in (("a", 31), ("b", -57)):
    for s in (1, -1):
        x = WC[0] + s * (R - 26) * math.cos(math.radians(a)); y = WC[1] + s * (R - 26) * math.sin(math.radians(a))
        d.decal(f"rim-bolt-{nm}{'p' if s > 0 else 'm'}", [x, y, (ZW[1] if nm == 'a' else ZW[1] + 8) + 0.6], [7, 7],
                "chrome", face="front", soft=True)
# --- handle on the slotted bar's lower-right half: black knurled knob + chrome grip pointing forward
hr = 226
hx = WC[0] + hr * math.cos(math.radians(-57)); hy = WC[1] + hr * math.sin(math.radians(-57))
d.cyl("handle-bolt", [hx, hy, 180], [hx, hy, 206], 16, "chrome")
d.cyl("handle-knob", [hx, hy, 202], [hx, hy, 240], 44, "rubber")
d.cyl("handle-grip", [hx, hy, 239], [hx, hy, 322], 34, "chrome")
d.sphere("handle-end", [hx, hy, 322], 33, "chrome")
d.save()
