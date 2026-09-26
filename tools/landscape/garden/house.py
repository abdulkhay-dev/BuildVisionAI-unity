"""Backdrop house: a single-storey timber house with a low hip roof, big warm-lit glazing and a deck.
In the app the house comes from the house document; here it only frames the garden."""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from . import layout as L
from .props import _box, _finish
from .util import flat_material, pbr_material


def build(site, col):
    h = L.HOUSE
    x0, y0, x1, y1 = h["x0"], h["y0"], h["x1"], h["y1"]
    base = site.house_pad
    fl = base + h["floor"]
    top = fl + h["height"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, d = x1 - x0, y1 - y0

    m_wall = pbr_material("M_HouseCladding", "japanese_cedar_planks", scale=0.9, tint=(0.62, 0.45, 0.32))
    m_plinth = pbr_material("M_HousePlinth", "stacked_stone_wall", scale=0.6, tint=(0.6, 0.58, 0.55))
    m_roof = pbr_material("M_HouseRoof", "roof_slates_03", scale=0.6, tint=(0.5, 0.5, 0.52))
    m_deck = pbr_material("M_Deck", "wood_floor_deck", scale=0.6, tint=(0.75, 0.6, 0.5))
    m_frame = flat_material("M_WindowFrame", (0.03, 0.028, 0.025), rough=0.4, metal=0.6)
    m_glass = flat_material("M_Glass", (0.9, 0.92, 0.9), rough=0.02, transmission=1.0)
    m_inside = flat_material("M_InteriorGlow", (0.9, 0.7, 0.5), rough=0.8, emission=(1.0, 0.7, 0.42), strength=1.6)
    m_soffit = pbr_material("M_Soffit", "japanese_cedar_planks", scale=1.2, tint=(0.8, 0.6, 0.42))
    mats = [m_wall, m_plinth, m_roof, m_deck, m_frame, m_glass, m_inside, m_soffit]
    WALL, PLINTH, ROOF, DECK, FRAME, GLASS, INSIDE, SOFFIT = range(8)

    bm = bmesh.new()
    # plinth and walls
    _box(bm, Vector((cx, cy, (base - 0.4 + fl) / 2)), (w, d, fl - base + 0.4), mat=PLINTH)
    _box(bm, Vector((cx, cy, (fl + top) / 2)), (w - 0.02, d - 0.02, top - fl), mat=WALL)

    def window(p, along, width, height, sill):
        """Glazing on the wall face at `p` (face centre at floor level), `along` = unit vector of the face."""
        n = Vector((along.y, -along.x, 0))       # outward for counter-clockwise faces
        rot = Matrix.Rotation(math.atan2(along.y, along.x), 4, "Z")
        c = p + Vector((0, 0, fl + sill + height / 2))
        # a lit "room" panel on the wall face behind the glass (walls are solid boxes)
        _box(bm, c + n * 0.005, (width, 0.01, height), rot, mat=INSIDE)
        _box(bm, c + n * 0.035, (width, 0.02, height), rot, mat=GLASS)
        for dz in (-height / 2, height / 2):
            _box(bm, c + n * 0.05 + Vector((0, 0, dz)), (width + 0.08, 0.1, 0.07), rot, mat=FRAME)
        k = max(1, int(width / 1.3))
        for i in range(k + 1):
            off = -width / 2 + i * width / k
            _box(bm, c + n * 0.05 + along * off, (0.07, 0.1, height + 0.08), rot, mat=FRAME)

    # east (garden) facade: full-height glass; south: large windows; north/west: a few
    east = Vector((0, 1, 0))
    for yy, ww in ((y0 + 2.4, 3.2), (cy + 0.6, 4.2), (y1 - 1.8, 2.2)):
        window(Vector((x1, yy, 0)), east, ww, 2.6, 0.05)
    south = Vector((1, 0, 0))
    for xx, ww in ((x0 + 2.2, 2.4), (cx + 0.5, 3.6), (x1 - 1.4, 1.6)):
        window(Vector((xx, y0, 0)), south, ww, 2.1 if ww < 3 else 2.6, 0.5 if ww < 3 else 0.05)
    north = Vector((-1, 0, 0))
    for xx in (x0 + 3, x1 - 3):
        window(Vector((xx, y1, 0)), north, 1.6, 1.5, 0.9)

    # hip roof with a deep overhang, fascia and soffit
    ov, pitch = 1.3, math.radians(17)
    rx0, ry0, rx1, ry1 = x0 - ov, y0 - ov, x1 + ov, y1 + ov
    eave = top + 0.15
    half = min(rx1 - rx0, ry1 - ry0) / 2
    ridge_h = eave + half * math.tan(pitch)
    if (rx1 - rx0) >= (ry1 - ry0):
        r0, r1 = Vector((rx0 + half, (ry0 + ry1) / 2, ridge_h)), Vector((rx1 - half, (ry0 + ry1) / 2, ridge_h))
    else:
        r0, r1 = Vector(((rx0 + rx1) / 2, ry0 + half, ridge_h)), Vector(((rx0 + rx1) / 2, ry1 - half, ridge_h))
    c = [Vector((rx0, ry0, eave)), Vector((rx1, ry0, eave)), Vector((rx1, ry1, eave)), Vector((rx0, ry1, eave))]
    thick = Vector((0, 0, 0.22))
    for quad in ((c[0], c[1], r1, r0), (c[2], c[3], r0, r1)) if (rx1 - rx0) >= (ry1 - ry0) else \
            ((c[1], c[2], r1, r0), (c[3], c[0], r0, r1)):
        vs = [bm.verts.new(v + thick) for v in quad]
        bm.faces.new(vs).material_index = ROOF
    tris = ((c[1], c[2], r1), (c[3], c[0], r0)) if (rx1 - rx0) >= (ry1 - ry0) else ((c[0], c[1], r0), (c[2], c[3], r1))
    for tri in tris:
        vs = [bm.verts.new(v + thick) for v in tri]
        bm.faces.new(vs).material_index = ROOF
    # fascia band and flat soffit
    for i in range(4):
        a, b = c[i], c[(i + 1) % 4]
        vs = [bm.verts.new(v) for v in (a, b, b + thick, a + thick)]
        bm.faces.new(vs).material_index = SOFFIT
    vs = [bm.verts.new(v) for v in reversed(c)]
    bm.faces.new(vs).material_index = SOFFIT

    # deck on the garden side, with steps down
    dx0, dy0, dx1, dy1 = h["deck"]
    _box(bm, Vector(((dx0 + dx1) / 2, (dy0 + dy1) / 2, fl - 0.08)), (dx1 - dx0, dy1 - dy0, 0.12), mat=DECK)
    for i in range(3):
        z = fl - 0.18 * (i + 1)
        _box(bm, Vector((dx1 + 0.2 + i * 0.32, (dy0 + dy1) / 2 - 1.5, z - 0.02)), (0.34, 2.4, 0.08), mat=DECK)
    obj = _finish(bm, "House", col, mats)

    return obj
