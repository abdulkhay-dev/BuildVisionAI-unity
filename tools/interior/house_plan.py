"""Reference house «Современный дом, 12 интерьеров» — the house of the 12-interior reference sheet, built from the Blender
interior library. Generates the house document (format house/1, Docs/house-format.md) that both the app (sample project)
and the Blender look-dev scene (tools/interior/lookdev.py) read.

    python3 tools/interior/house_plan.py   → tools/interior/modern12.house.json + Assets/StreamingAssets/Samples/dom-12-interyerov.house.json

Plan (inner faces, metres; X east, Z north; exterior walls 0.4 m on the 17 × 12 m outline):
  ground (floor +0.3, 3.0 high)  south row z 0.4–4.8: office | hall (entry) | laundry | cinema
                                 north row z 4.8–11.6: living | kitchen (open plan) | stair hall
  upper  (floor +3.6, 2.9 high)  closet | bath | guest bedroom (south) · corridor · bedroom | kids (north) · upper hall
                                 balcony: cantilevered deck north of the bedroom, glass railing
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
G, U = "ground", "upper"
GY, UY = 0.3, 3.6          # floor levels
GH, UH = 3.0, 2.9          # ceiling heights

doc = {
    "format": "house/1",
    "meta": {"name": "Современный дом: 12 интерьеров",
             "description": "Двухэтажный дом 17 × 12 м по референсу из 12 интерьеров: гостиная и кухня, кабинет, прихожая, "
                            "прачечная, кинотеатр; наверху спальня с гардеробной, ванной и балконом, детская, гостевая.",
             "author": "House"},
    "site": {"landscape": "garden", "sunAzimuth": 215, "sunElevation": 32},
    "levels": [
        {"id": G, "name": "1 этаж", "elevation": GY, "height": GH, "slab": 0.3},
        {"id": U, "name": "2 этаж", "elevation": UY, "height": UH, "slab": 0.3},
    ],
    "walls": [], "openings": [], "rooms": [], "roofs": [], "stairs": [], "elements": [], "items": [], "lights": [], "views": [],
}

FACADE = "render#e4ded3"
FACADE_WOOD = "cladding_cedar"
WALL_WARM = "plaster_beige"            # default interior finish
PANEL_DARK = "wood_panels_dark"


# ---------------------------------------------------------------------------------------------------- helpers
def wall(id, level, a, b, **kw):
    w = {"id": id, "level": level, "a": list(a), "b": list(b)}
    w.update(kw)
    doc["walls"].append(w)
    return id


def iwall(id, level, a, b, right=None, left=None, **kw):
    """Interior partition on its axis; right/left = finish of the side to the right/left of a→b."""
    kw = dict(kw)
    kw["kind"] = "interior"
    if right:
        kw["outside"] = right
    if left:
        kw["inside"] = left
    return wall(id, level, a, b, **kw)


def opening(id, w, type, at, width, height, sill=None, **kw):
    o = {"id": id, "wall": w, "type": type, "at": round(at, 3), "width": width, "height": height}
    if sill is not None:
        o["sill"] = sill
    o.update(kw)
    doc["openings"].append(o)


def room(id, name, level, type, x0, z0, x1, z1, **kw):
    r = {"id": id, "name": name, "level": level, "type": type, "outline": [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]}
    r.update(kw)
    doc["rooms"].append(r)


def item(id, model, level, x, z, rot=0, y=0.0, **params):
    it = {"id": id, "model": model, "level": level, "position": [round(x, 3), round(y, 3), round(z, 3)], "rotation": rot}
    if params:
        it["params"] = params
    doc["items"].append(it)


def light(id, level, x, y, z, intensity, range, color="warm", shadows=False, **kw):
    l = {"id": id, "type": "point", "level": level, "position": [x, y, z], "color": color, "intensity": intensity,
         "range": range, "shadows": shadows}
    l.update(kw)
    doc["lights"].append(l)


def view(name, x, level_y, z, yaw, pitch=-4):
    doc["views"].append({"name": name, "type": "walk", "position": [x, level_y, z], "yaw": yaw, "pitch": pitch})


# ---------------------------------------------------------------------------------------------------- shell
for lv in (G, U):
    s = "_u" if lv == U else ""
    wall("south" + s, lv, (0, 0), (17, 0), outside=FACADE, inside=WALL_WARM, plinth=0.3 if lv == G else None)
    wall("east" + s, lv, (17, 0), (17, 12), outside=FACADE, inside=WALL_WARM, plinth=0.3 if lv == G else None)
    wall("north" + s, lv, (17, 12), (0, 12), outside=FACADE_WOOD if lv == U else FACADE, inside=WALL_WARM,
         plinth=0.3 if lv == G else None)
    wall("west" + s, lv, (0, 12), (0, 0), outside=FACADE, inside=WALL_WARM, plinth=0.3 if lv == G else None)
for w in doc["walls"]:
    if w.get("plinth") is None:
        w.pop("plinth", None)

# ground openings (exterior)
opening("office_win", "south", "window", 1.2, 2.0, 1.6, 0.9, columns=2, curtain="none")
opening("entry", "south", "solidDoor", 5.7, 1.1, 2.4, hinge="start", swing=1)
opening("entry_side", "south", "glazing", 6.95, 0.7, 2.4, 0)
opening("laundry_win", "south", "window", 8.9, 1.2, 1.2, 1.1)
opening("stair_win", "east", "glazing", 6.4, 2.6, 2.6, 0.2, columns=2)
opening("kitchen_glazing", "north", "glazing", 17 - 10.2, 2.4, 2.6, 0, columns=2)
opening("living_glazing", "north", "glazing", 17 - 6.8, 5.8, 2.7, 0, columns=3, curtain="full", curtainFraction=0.18)
opening("living_west", "west", "glazing", 2.0, 3.0, 2.6, 0, columns=2)
opening("office_west", "west", "window", 8.6, 2.2, 1.6, 0.9, columns=2, curtain="none")
# upper openings (exterior)
opening("closet_win", "south_u", "window", 1.4, 1.1, 1.4, 1.0, curtain="none")
opening("bath_win", "south_u", "window", 5.0, 1.2, 1.1, 1.3)
opening("guest_win", "south_u", "window", 9.0, 2.0, 1.6, 0.8, columns=2)
opening("hall_win_u", "south_u", "window", 13.6, 2.0, 1.6, 0.8, columns=2)
opening("bed_glazing", "north_u", "glazing", 17 - 4.4, 3.2, 2.5, 0, columns=2, curtain="full", curtainFraction=0.2)
opening("balcony_door", "north_u", "entryDoor", 17 - 5.6, 1.0, 2.4, 0)
opening("kids_win", "north_u", "window", 17 - 11.6, 3.0, 1.6, 0.7, columns=3, curtain="none")
opening("bed_west", "west_u", "window", 2.2, 2.4, 1.8, 0.6, columns=2, curtain="full", curtainFraction=0.25)
opening("hall_east_u", "east_u", "window", 6.6, 2.4, 1.6, 0.8, columns=2)

# ground partitions
iwall("g_z48_w", G, (0.4, 4.8), (7.4, 4.8), right="plaster_white", left=WALL_WARM)           # office/hall | living
opening("hall_living", "g_z48_w", "hole", 4.9, 1.8, 2.5)
iwall("g_z48_e", G, (7.4, 4.8), (16.6, 4.8), right=WALL_WARM, left=WALL_WARM)                # laundry/cinema | kitchen/stair
opening("laundry_door", "g_z48_e", "door", 1.0, 0.9, 2.1, hinge="start", swing=-1)
opening("cinema_door", "g_z48_e", "door", 3.9, 0.9, 2.1, hinge="start", swing=-1)   # behind the screen end
iwall("g_x44", G, (4.4, 0.4), (4.4, 4.8), right="plaster_white", left=WALL_WARM)
opening("office_door", "g_x44", "door", 3.3, 0.9, 2.1, hinge="end", swing=-1)
iwall("g_x80", G, (8.0, 0.4), (8.0, 4.8), right=WALL_WARM, left="plaster_white")
iwall("g_x106", G, (10.6, 0.4), (10.6, 4.8), right=PANEL_DARK, left="plaster_white")         # laundry | cinema (screen wall)
iwall("g_x126", G, (12.6, 4.8), (12.6, 11.6), right="plaster_white", left=WALL_WARM)
opening("kitchen_stair", "g_x126", "hole", 0.35, 1.5, 2.5)

# upper partitions
iwall("u_x36_bath", U, (3.6, 0.4), (3.6, 5.2), right="marble_beige", left=WALL_WARM)        # closet | bath
opening("bath_door", "u_x36_bath", "door", 1.6, 0.9, 2.1, hinge="start", swing=1)
iwall("u_x36_cor", U, (3.6, 5.2), (3.6, 6.6), right=WALL_WARM, left=WALL_WARM)
iwall("u_z66", U, (0.4, 6.6), (12.6, 6.6), right=WALL_WARM, left=WALL_WARM)                  # closet/corridor | bedroom/kids
opening("closet_door", "u_z66", "door", 0.8, 0.9, 2.1, hinge="start", swing=-1)
opening("bed_door", "u_z66", "door", 4.9, 0.9, 2.1, hinge="end", swing=-1)
opening("kids_door", "u_z66", "door", 8.0, 0.9, 2.1, hinge="start", swing=-1)
iwall("u_z52", U, (3.6, 5.2), (12.6, 5.2), right=WALL_WARM, left="marble_beige")              # bath/guest | corridor
opening("guest_door", "u_z52", "door", 5.0, 0.9, 2.1, hinge="end", swing=1)
iwall("u_x74_s", U, (7.4, 0.4), (7.4, 5.2), right=WALL_WARM, left="marble_beige")
iwall("u_x74_n", U, (7.4, 6.6), (7.4, 11.6), right="paint_smooth#c9ced4", left=WALL_WARM)   # bedroom | kids (blue-grey)
iwall("u_x126", U, (12.6, 0.4), (12.6, 11.6), right=WALL_WARM, left=WALL_WARM)
opening("corridor_hall", "u_x126", "hole", 4.85, 1.7, 2.4)

# rooms
room("office", "Кабинет", G, "office", 0.4, 0.4, 4.4, 4.8, floor="oak_planks")
room("hall", "Прихожая", G, "hall", 4.4, 0.4, 8.0, 4.8, floor="porcelain_grey")
room("laundry", "Прачечная", G, "utility", 8.0, 0.4, 10.6, 4.8, floor="porcelain_grey")
room("cinema", "Кинотеатр", G, "other", 10.6, 0.4, 16.6, 4.8, floor="carpet_loop#4a4744", ceiling="paint_smooth#3a3836")
room("living", "Гостиная", G, "living", 0.4, 4.8, 7.4, 11.6, floor="oak_planks")
room("kitchen", "Кухня", G, "kitchen", 7.4, 4.8, 12.6, 11.6, floor="porcelain_grey")
room("stair_hall", "Холл с лестницей", G, "hall", 12.6, 4.8, 16.6, 11.6, floor="oak_planks")
room("closet", "Гардеробная", U, "wardrobe", 0.4, 0.4, 3.6, 6.6, floor="oak_planks")
room("bath", "Ванная комната", U, "bathroom", 3.6, 0.4, 7.4, 5.2, floor="marble_beige")
room("guest", "Гостевая спальня", U, "bedroom", 7.4, 0.4, 12.6, 5.2, floor="oak_planks")
room("corridor", "Коридор", U, "corridor", 3.6, 5.2, 12.6, 6.6, floor="oak_planks")
room("bedroom", "Спальня", U, "bedroom", 0.4, 6.6, 7.4, 11.6, floor="oak_planks")
room("kids", "Детская комната", U, "bedroom", 7.4, 6.6, 12.6, 11.6, floor="laminate_light")
room("upper_hall", "Холл 2 этажа", U, "hall", 12.6, 0.4, 16.6, 11.6, floor="oak_planks")

# balcony: deck on brackets north of the bedroom + glass railing
doc["elements"] += [
    {"id": "balcony", "type": "platform", "min": [0.6, UY - 0.3, 12.0], "max": [6.6, UY, 14.2], "material": "stucco",
     "top": "deck_boards", "bottom": "soffit"},
    {"id": "balcony_rail", "type": "railing", "path": [[0.6, 12.0], [0.6, 14.2], [6.6, 14.2], [6.6, 12.0]], "y": UY,
     "height": 1.05, "style": "glass"},
]

doc["roofs"].append({"id": "main", "type": "flat", "outline": [[0.4, 0.4], [16.6, 0.4], [16.6, 11.6], [0.4, 11.6]],
                     "overhang": 0, "parapet": 0, "material": "coping"})
doc["stairs"].append({"id": "stair", "type": "u", "from": G, "to": U, "start": [13.35, 5.45], "direction": 0, "width": 1.1,
                      "going": 0.27, "risers": 18, "firstFlight": 9, "turn": "right", "gap": 0.1, "landing": 1.15,
                      "style": "floating_oak"})

# ---------------------------------------------------------------------------------------------------- furniture
# rotation = where the front looks (0 north, 90 east, 180 south, 270 west); wall pieces: point on the wall, y = centre height

# living room — TV on the south wall, corner sofa facing it, chaise leg on the west
item("tv_console", "media_console_floating", G, 3.0, 4.86, 0, y=0.45)
item("tv", "tv_flat_75", G, 3.0, 4.86, 0, y=1.45)
item("sofa", "sofa_corner_lounge", G, 3.2, 9.55, 180)       # short leg on the east side
item("rug", "rug_living_abstract", G, 3.1, 7.75, 0)
item("coffee_table", "coffee_table_drum", G, 2.85, 7.75, 0)
item("coffee_decor", "decor_table_set", G, 2.85, 7.75, 20, y=0.40)
item("pouf", "pouf_round_tufted", G, 4.45, 6.35, 0)
item("arc_lamp", "floor_lamp_arc", G, 5.55, 9.4, 200)
item("chandelier", "chandelier_rings", G, 2.9, 7.75, 0, y=GH)
item("art", "art_abstract_canvas", G, 0.46, 5.95, 90, y=1.55)
item("plant_living", "plant_large", G, 0.95, 11.0, 135)
item("plant_living2", "plant_ficus", G, 0.95, 5.35, 90)

# kitchen — tall units and the base run on the east wall, waterfall island with stools on its west side
KX = 12.54                                    # face of the partition
item("fridge", "kitchen_fridge_black", G, KX, 11.05, 270)
item("oven", "kitchen_oven_column", G, KX, 10.3, 270)
item("pantry", "kitchen_tall_cabinet", G, KX, 9.7, 270)
item("base_1", "kitchen_cooktop_base", G, KX, 9.1, 270)
item("base_2", "kitchen_sink_base", G, KX, 8.2, 270)
item("base_3", "kitchen_base_600", G, KX, 7.45, 270)
item("wall_cab_1", "kitchen_wall_cabinet", G, KX, 8.65, 270, y=1.95)
item("wall_cab_2", "kitchen_wall_cabinet", G, KX, 7.75, 270, y=1.95)
item("island", "kitchen_island_waterfall", G, 10.2, 8.9, 270)
for i, z in enumerate((8.0, 8.9, 9.8)):
    item(f"stool_{i + 1}", "bar_stool_upholstered", G, 9.2, z, 90)
for i, z in enumerate((7.9, 8.9, 9.9)):
    item(f"pendant_{i + 1}", "pendant_cylinder_black", G, 10.2, z, 0, y=GH)
item("plant_kitchen", "plant_ficus", G, 7.9, 11.1, 180)

# hall — flush wardrobes on the west wall, floating console + backlit mirror and a bench with hooks on the east wall
item("hall_wardrobe_1", "wardrobe_hall_flush", G, 4.46, 1.0, 90)
item("hall_wardrobe_2", "wardrobe_hall_flush", G, 4.46, 2.0, 90)
item("hall_console", "console_hall_floating", G, 7.94, 3.6, 270, y=0.85)
item("hall_mirror", "mirror_round_backlit", G, 7.94, 3.6, 270, y=1.65)
item("hall_bench", "bench_entry_upholstered", G, 7.94, 1.7, 270)
item("hall_hooks", "coat_hooks_wall", G, 7.94, 1.7, 270, y=1.5)     # pivot = middle of rail + coats
item("hall_runner", "rug_runner", G, 6.25, 2.8, 90)
item("hall_mat", "doormat_entry", G, 6.25, 0.85, 0)
item("plant_hall", "plant_succulent", G, 7.94, 3.6, 270, y=0.85 + 0.17)

# office — bookcase wall on the north, desk facing the south window
for i, x in enumerate((1.4, 2.6)):                           # clear of the door zone at x > 3.6
    item(f"bookcase_{i + 1}", "bookcase_wall_led", G, x, 4.74, 180)
item("desk", "desk_executive", G, 2.3, 1.75, 0)
item("office_chair", "office_chair_mesh", G, 2.3, 2.55, 180)
item("monitor", "monitor_27", G, 2.3, 1.55, 0, y=0.75)
item("office_lamp", "desk_lamp", G, 3.0, 1.55, 200, y=0.75)
item("keyboard", "keyboard_mouse_pad", G, 2.3, 1.9, 0, y=0.75)
item("plant_office", "plant_large", G, 0.95, 0.95, 45)

# laundry — machines and the counter run on the east wall, cabinets above
item("laundry_run", "laundry_counter_run", G, 10.54, 2.6, 270)
item("laundry_upper", "laundry_wall_units", G, 10.54, 2.6, 270, y=1.95)
item("washer", "washer_front_white", G, 10.54, 3.2, 270)
item("dryer", "dryer_front_white", G, 10.54, 2.6, 270)
item("laundry_basket", "laundry_basket_white", G, 8.45, 1.4, 90)

# cinema — screen on the west wall, sectional facing it, acoustic panels on the long walls
item("screen", "cinema_screen_wall", G, 10.66, 2.6, 90, y=1.55)
item("cinema_console", "media_console_low_black", G, 10.66, 2.6, 90)
item("cinema_sofa", "sofa_theater_sectional", G, 15.9, 2.6, 270)   # off the wall: a walkway behind
item("cinema_table", "coffee_table_rect_black", G, 12.9, 2.6, 90)
item("cinema_rug", "rug_cinema", G, 13.3, 2.6, 90)
for i, x in enumerate((11.2, 11.9, 12.6, 13.3, 14.0)):
    item(f"panel_s{i + 1}", "acoustic_panel_dark", G, x, 0.46, 0, y=1.3)
for i, x in enumerate((12.8, 13.5, 14.2, 14.9)):        # east of the door
    item(f"panel_n{i + 1}", "acoustic_panel_dark", G, x, 4.74, 180, y=1.3)
for i, x in enumerate((14.8, 16.0)):
    item(f"sconce_s{i + 1}", "sconce_up_down", G, x, 0.46, 0, y=1.9)

# bedroom — bed against the kids' wall facing west, nightstands with drum lamps, ink painting above
item("bed", "bed_king_panel", U, 7.34, 9.15, 270)
item("nightstand_l", "nightstand_float_dark", U, 7.34, 7.68, 270)
item("nightstand_r", "nightstand_float_dark", U, 7.34, 10.62, 270)
item("lamp_l", "table_lamp_drum", U, 7.12, 7.68, 270, y=0.5)
item("lamp_r", "table_lamp_drum", U, 7.12, 10.62, 270, y=0.5)
item("bed_art", "art_ink_framed", U, 7.34, 9.15, 270, y=1.75)
item("bed_rug", "rug_bedroom", U, 5.6, 9.15, 90)
item("plant_bed", "plant_large", U, 0.95, 11.1, 135)

# closet — hanging and shelf modules along both long walls, ottoman in the aisle
for i, (z, m) in enumerate(((0.95, "closet_shelf_unit"), (1.95, "closet_hanging_unit"), (2.95, "closet_hanging_unit"),
                            (3.95, "closet_shelf_unit"), (4.95, "closet_hanging_unit"), (5.95, "closet_shelf_unit"))):
    item(f"closet_w{i + 1}", m, U, 0.4, z, 90)
for i, (z, m) in enumerate(((3.5, "closet_hanging_unit"), (4.5, "closet_shelf_unit"), (5.5, "closet_hanging_unit"))):
    item(f"closet_e{i + 1}", m, U, 3.54, z, 270)
item("closet_ottoman", "ottoman_rect_tufted", U, 2.0, 3.3, 90)

# bath — double vanity + LED mirror on the corridor wall, shower and toilet on the east wall
item("vanity", "vanity_float_double", U, 5.5, 5.14, 180, y=0.6)
item("bath_mirror", "mirror_led_rect", U, 5.5, 5.14, 180, y=1.55)
item("shower", "shower_glass_black", U, 7.34, 1.1, 270)
item("toilet", "toilet_wall_hung", U, 7.34, 3.0, 270)
item("towel", "towel_ladder_black", U, 3.66, 4.2, 90, y=1.0)
item("bath_mat", "bath_mat", U, 5.4, 3.9, 0)

# kids — single bed on the east wall under rocket posters, desk on the west wall, shelves, bean bag, round rug
item("kids_bed", "bed_single_storage", U, 12.54, 10.35, 270)
for i, (z, m) in enumerate(((9.35, "poster_rocket"), (10.05, "poster_rocket_2"), (10.75, "poster_rocket_3"))):
    item(f"poster_{i + 1}", m, U, 12.54, z, 270, y=1.55)
item("kids_desk", "desk_kids_wall", U, 7.46, 9.3, 90)
item("kids_chair", "chair_kids_swivel", U, 8.25, 9.3, 270)
item("kids_shelf", "shelf_open_kids", U, 12.54, 7.7, 270)
item("bean_bag", "bean_bag_blue", U, 10.2, 7.8, 0)
item("kids_rug", "rug_round_blue", U, 10.0, 9.2, 0)

# guest bedroom (not in the reference — library pieces)
item("guest_bed", "bed_modern", U, 12.54, 2.8, 270)
item("guest_ns", "nightstand_classic", U, 12.35, 1.45, 270)
item("guest_art", "picture_frame_landscape", U, 12.54, 2.8, 270, y=1.6)

# upper hall
item("plant_upper", "plant_ficus", U, 16.1, 11.1, 225)

# balcony — two rattan lounge chairs facing the view with a round teak table
item("balcony_chair_1", "lounge_chair_rattan", U, 2.0, 13.3, 0)
item("balcony_chair_2", "lounge_chair_rattan", U, 3.9, 13.3, 0)
item("balcony_table", "side_table_round_wood", U, 2.95, 13.45, 0)
item("balcony_plant", "plant_large", U, 6.1, 12.5, 0)

# ---------------------------------------------------------------------------------------------------- lights and views
light("chandelier", G, 2.9, 2.2, 7.75, 1.4, 8, shadows=True)
light("arc_lamp", G, 4.9, 1.7, 7.6, 0.6, 4)
light("island", G, 10.2, 2.2, 8.9, 1.2, 6, shadows=True)
light("hall_mirror", G, 7.6, 1.65, 3.6, 0.35, 3)
light("office", G, 2.3, 2.3, 2.5, 0.8, 6)
light("cinema_screen", G, 11.2, 1.5, 2.6, 0.5, 5, color="#cfe0f0")
light("bed_l", U, 7.0, 0.8, 7.75, 0.35, 3)
light("bed_r", U, 7.0, 0.8, 10.55, 0.35, 3)
light("bath_mirror", U, 5.5, 1.6, 4.9, 0.45, 3.5)
light("closet", U, 2.0, 2.3, 3.5, 0.7, 5)

view("Гостиная", 6.6, GY, 5.6, 315, -6)
view("Кухня", 7.9, GY, 6.0, 45, -6)
view("Спальня", 1.2, UY, 7.1, 60, -6)
view("Кабинет", 2.3, GY, 4.4, 180, -8)
view("Ванная комната", 4.0, UY, 0.8, 30, -8)
view("Детская комната", 7.9, UY, 7.1, 60, -8)
view("Прихожая", 6.2, GY, 4.4, 180, -6)
view("Гардеробная", 2.0, UY, 6.3, 180, -6)
view("Кинотеатр", 16.3, GY, 4.4, 245, -8)
view("Прачечная", 8.4, GY, 1.0, 45, -6)
view("Балкон", 6.2, UY, 12.3, 295, -6)


def main():
    for out in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "modern12.house.json"),
                os.path.join(ROOT, "Assets", "StreamingAssets", "Samples", "dom-12-interyerov.house.json")):
        with open(out, "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("wrote", out, len(doc["items"]), "items,", len(doc["rooms"]), "rooms")


if __name__ == "__main__":
    main()
