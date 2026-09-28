"""Registry of the interior library models: every models_<room>.py lists ENTRIES = [(id, name, category, builder, opts)]."""
import importlib

ROOMS = ["living", "kitchen", "bedroom", "office", "bath", "kids", "hall", "closet", "cinema", "laundry", "balcony"]


def entries():
    out = []
    for room in ROOMS:
        try:
            mod = importlib.import_module("models_" + room)
        except ModuleNotFoundError as ex:
            if ex.name != "models_" + room:
                raise
            continue
        for (mid, name, cat, fn, opts) in mod.ENTRIES:
            e = {"id": mid, "name": name, "category": cat, "blender": fn.__name__, "room": room}
            e.update(opts)
            out.append((e, fn))
    return out
