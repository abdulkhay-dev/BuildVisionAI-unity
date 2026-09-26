"""The garden design as plain data (metres; X east, Y north, Z up).

This is the part an AI would author later (the future `site` section of house.json): curves, zones,
single placements and views. Everything else in this package turns it into geometry.
"""

SEED = 4696

# Garden plot (fence line) and the terrain around it.
PLOT = (-24.0, -26.0, 20.0, 40.0)          # xmin, ymin, xmax, ymax
TERRAIN = (-40.0, -34.0, 34.0, 60.0)       # detailed terrain mesh
SLOPE = 0.07                               # ground rises towards the north (m per m)
GROUND_Y0 = -26.0                          # y of height 0

# Stream: control points from upstream (north) to downstream (south).
STREAM = [(5.0, 52.0), (4.0, 42.0), (2.5, 34.0), (0.5, 27.0), (1.2, 20.0), (1.0, 14.0), (2.6, 8.0),
          (5.0, 3.0), (5.6, -2.0), (4.0, -7.0), (4.6, -12.0), (6.2, -18.0), (7.0, -34.0)]
STREAM_WIDTH = 2.6          # mean water width
STREAM_DEPTH = 0.32         # depth of the bed under the water at the centre line
# Cascades by the y where they sit; water is level between them (pools).
CASCADES_Y = [31.0, 19.0, 8.0, 1.0, -9.0, -20.0]

# Stepping-stone paths (centre lines) and their width.
PATHS = [
    {"id": "main", "points": [(-4.8, -34.0), (-5.2, -20.0), (-4.3, -11.0), (-5.8, -3.0), (-8.4, 2.0),
                              (-11.0, 5.0)], "width": 1.1},
    {"id": "bridge", "points": [(-6.4, -1.0), (-4.6, 5.0), (-2.6, 10.5), (-1.9, 13.4)], "width": 0.9},
    {"id": "east", "points": [(4.2, 14.8), (7.0, 18.5), (9.0, 25.0), (8.0, 33.0)], "width": 0.9},
]

BRIDGE = {"a": (-1.9, 13.5), "b": (4.2, 14.7), "width": 1.5, "rise": 0.55}

HOUSE = {"x0": -25.0, "y0": 3.0, "x1": -13.5, "y1": 15.0, "floor": 0.55, "height": 3.1,
         "deck": (-13.5, 3.0, -10.2, 12.0)}

# Single placements: (kind, x, y, rotation deg, scale)
TREES = [
    ("oak", -9.5, -15.5, 20, 1.15),        # frames the front view top-left
    ("maple_red", -3.8, 18.0, 70, 0.95),   # red accent behind the bridge
    ("maple_red", 13.5, 27.0, 200, 0.75),
    ("fir", -12.5, 24.0, 0, 0.55),
    ("fir", -7.5, 26.0, 40, 0.6),
    ("fir", 11.0, 6.0, 90, 0.42),
    ("fir_small", -6.0, 21.5, 0, 1.0),
    ("fir_small", 6.8, 11.5, 0, 0.9),
    ("birch", 18.0, -15.0, 0, 1.0),
    ("birch", 14.0, 16.0, 130, 1.1),
    ("oak", -16.0, 25.0, 250, 1.0),
    ("oak", -19.0, 31.0, 10, 1.1),
    ("birch", -20.0, -10.0, 60, 0.9),
]

PROPS = [
    ("stone_lantern", 1.9, -4.3, 15),
    ("stone_lantern", -2.9, 12.2, 200),
    ("garden_lamp", -6.6, -8.0, 0),
    ("garden_lamp", -3.2, 7.5, 0),
    ("garden_lamp", -10.4, 1.4, 0),
]

# Hero boulders: (variant, x, y, yaw deg, scale, sink) — the rest are placed along the banks automatically.
BOULDERS = [
    ("boulder_a", -3.0, -16.0, 30, 0.9, 0.25),
    ("boulder_b", 1.2, -13.5, 110, 0.55, 0.2),
    ("boulder_c", 8.2, -6.5, 200, 0.6, 0.25),
    ("boulder_a", -3.6, -9.5, 80, 0.42, 0.18),
    ("boulder_d", 2.3, 3.8, 10, 0.55, 0.2),
    ("boulder_b", -2.4, -5.8, 160, 0.4, 0.15),
]

# A planted vignette for the plant close-up: (species, x, y, scale); random planting keeps clear of it.
FEATURE_BED = {"center": (-3.6, -9.6), "radius": 1.5, "plants": [
    ("daisy", -3.2, -10.3, 1.3), ("daisy", -2.8, -9.7, 1.2), ("daisy", -3.9, -10.6, 1.1), ("daisy", -2.5, -10.4, 1.0),
    ("phlox", -4.4, -9.5, 1.3), ("phlox", -4.0, -8.8, 1.2), ("phlox", -3.3, -8.9, 1.1),
    ("salvia", -4.9, -10.2, 1.1), ("salvia", -2.4, -8.8, 1.0), ("lavender", -4.6, -8.5, 1.1),
    ("hosta", -2.0, -9.5, 1.0), ("tuft", -4.8, -9.0, 1.0), ("fern", -3.0, -8.3, 1.0)]}

# Sun and sky. Azimuth: clockwise from north. The front view looks north into the low sun. The sky HDRI
# glow (its own sun sits at 6°) is rotated to `azimuth`; the sky is clamped at SKY_CLAMP so the light comes
# from the sun lamp, a little higher (at 6° every 10 m tree would throw a 95 m shadow over the garden).
SUN = {"azimuth": 16.0, "elevation": 11.0, "strength": 11.0, "color": (1.0, 0.8, 0.58), "angle": 1.0}
SKY_CLAMP = 12.0
SKY_STRENGTH = 0.9
HDRI = "qwantani_sunset_puresky_4k.hdr"

# Views: camera location and look-at target (z = metres above the ground there), lens mm, f-stop (None = no
# depth of field), label and render size (aspect of its slot on the contact sheet).
VIEWS = {
    "front": {"loc": (3.0, -16.8, 1.5), "target": (1.8, 14.0, 0.2), "lens": 22, "fstop": None,
              "label": "Вид спереди", "size": (1170, 1287)},
    "right": {"loc": (15.5, -4.0, 2.0), "target": (2.0, 8.0, -0.5), "lens": 26, "fstop": None,
              "label": "Вид справа", "size": (1398, 846)},
    "left": {"loc": (-4.5, -6.5, 1.6), "target": (5.0, 8.0, -0.2), "lens": 26, "fstop": None,
             "label": "Вид слева", "size": (1398, 846)},
    "back": {"loc": (2.5, 30.0, 2.6), "target": (3.0, 0.0, -1.0), "lens": 24, "fstop": None,
             "label": "Вид сзади", "size": (1398, 846)},
    "top": {"loc": (-6.0, 0.0, 44.0), "target": (-4.5, 5.5, 0.0), "lens": 30, "fstop": None,
            "label": "Вид сверху", "size": (1242, 1170)},
    "stream": {"loc": (4.4, -2.6, 0.55), "target": (5.1, 1.6, 0.0), "lens": 50, "fstop": 2.8,
               "label": "Деталь ручья", "size": (1242, 1170)},
    "plants": {"loc": (-2.9, -11.9, 0.42), "target": (-3.6, -9.7, 0.3), "lens": 40, "fstop": 2.8,
               "label": "Деталь растений", "size": (1242, 1170)},
}
