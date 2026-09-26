"""Builds the garden look-dev scene in Blender and optionally renders the reference views.

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
        -P tools/landscape/garden/build.py -- [--render all|front,top,…] [--samples 128] [--scale 1.0] \
        [--out Renders/landscape] [--quick]

Collections: KIT (instanced variants, excluded), SITE (terrain, water), PROPS, HOUSE, PLANTING (instancers),
STAGE, CAMERAS. Output: <out>/garden.blend, <out>/<view>.png, <out>/sheet.png.
"""
import argparse
import math
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bpy  # noqa: E402

from garden import flora, house, kit as kitmod, layout as L, props, scatter, stage, terrain, water  # noqa: E402
from garden.site import Site  # noqa: E402
from garden.util import ROOT, collection  # noqa: E402


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--render", default="")
    p.add_argument("--samples", type=int, default=128)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--out", default=os.path.join(ROOT, "Renders", "landscape"))
    p.add_argument("--quick", action="store_true", help="no lawn/forest instancing (fast iteration)")
    return p.parse_args(argv)


def clear():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)


def main():
    a = args()
    t0 = time.time()

    def step(msg):
        print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)

    clear()
    bpy.context.scene.unit_settings.system = "METRIC"
    site = Site()
    step(f"site: stream {site.stream.length:.1f} m, pools {[round(p.level, 2) for p in site.pools]}")

    kit = kitmod.Kit()
    kit.load_ph()
    flora.build_all(kit)
    kitmod.recolor_leaves(kit.group("tree_maple").objects, hue=0.25, sat=1.5, val=0.95)
    # the Namaqualand boulders are red sandstone; the reference has grey granite
    kitmod.recolor_leaves(kit.group("rock_boulder").objects, hue=0.5, sat=0.25, val=1.05, suffix="_grey",
                          match=("boulder",))
    step("kit loaded")

    site_col = collection("SITE")
    terrain.build_plot(site, site_col)
    terrain.build_far(site, site_col)
    step("terrain")
    water.build(site, site_col)
    step("water")

    props_col = collection("PROPS")
    props.bridge(props_col)
    for kind, x, y, yaw in L.PROPS:
        obj = props.stone_lantern(props_col, f"StoneLantern_{x:.0f}_{y:.0f}") if kind == "stone_lantern" else \
            props.garden_lamp(props_col, f"GardenLamp_{x:.0f}_{y:.0f}")
        obj.location = (x, y, site.height(x, y) - 0.03)
        obj.rotation_euler = (0, 0, math.radians(yaw))
        if kind == "stone_lantern":
            props.lamp_light(obj, 0.88, 6.0)
        else:
            props.lamp_light(obj, 1.06, 12.0)
    props.stepping_stones(site, props_col)
    props.fence(site, props_col)
    step("props")

    house.build(site, collection("HOUSE"))
    step("house")

    planter = scatter.Planter(site, kit)
    planter.trees()
    planter.rocks()
    n = planter.plant_beds()
    step(f"beds: {n} plants")
    if not a.quick:
        planter.plant_lawn()
        noise = terrain.ValueNoise(L.SEED + 3)
        planter.forest(lambda x, y: terrain.far_height(site, noise, x, y))
        step("lawn + forest")
    planter.build(collection("PLANTING"))
    kit.finish()

    elevation = stage.world()
    stage.sun(L.SUN["elevation"])
    stage.sun_disk()
    stage.compositor()
    cams = stage.cameras(site)
    stage.render_settings(a.samples, preview=a.scale < 0.75)
    bpy.context.scene.camera = cams["front"]
    os.makedirs(a.out, exist_ok=True)
    blend = os.path.join(a.out, "garden.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=False)
    step(f"saved {blend}")

    if a.render:
        views = list(L.VIEWS) if a.render == "all" else a.render.split(",")
        paths = stage.render_views(cams, a.out, views, a.scale)
        step("rendered")
        if set(L.VIEWS) <= set(paths):
            sheet = stage.contact_sheet(paths, os.path.join(a.out, "sheet.png"))
            step(f"sheet {sheet}")


main()
