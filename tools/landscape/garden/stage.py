"""Sky, sun, cameras, render settings and the contact sheet."""
import math
import os
import subprocess

import bpy
import numpy as np
from mathutils import Vector

from . import layout as L
from .util import PH_BLEND, collection


def _sun_vector(azimuth_deg, elevation_deg):
    a, e = math.radians(azimuth_deg), math.radians(elevation_deg)
    return Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))


def hdri_sun(img):
    """Azimuth (clockwise from north, as the HDRI is mapped unrotated) and elevation of the brightest pixel."""
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    lum = px[..., 0] * 0.2126 + px[..., 1] * 0.7152 + px[..., 2] * 0.0722
    y, x = np.unravel_index(int(np.argmax(lum)), lum.shape)
    u, v = (x + 0.5) / w, (y + 0.5) / h
    phi = (u - 0.5) * 2 * math.pi            # = atan2(dir.y, -dir.x) in Blender's equirect mapping
    elev = (v - 0.5) * math.pi
    dx, dy = -math.cos(phi), math.sin(phi)
    az = math.degrees(math.atan2(dx, dy)) % 360
    return az, math.degrees(elev), float(lum.max())


def world():
    sc = bpy.context.scene
    wd = bpy.data.worlds.new("GardenSky")
    sc.world = wd
    wd.use_nodes = True
    nt = wd.node_tree
    bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(PH_BLEND, "hdri", L.HDRI))
    az, el, peak = hdri_sun(env.image)
    # rotate the sky so its sun sits at the layout azimuth
    target = L.SUN["azimuth"]
    phi_hdri = math.atan2(math.cos(math.radians(az)), -math.sin(math.radians(az)))
    phi_target = math.atan2(math.cos(math.radians(target)), -math.sin(math.radians(target)))
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, phi_hdri - phi_target)
    nt.links.new(coord.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    # clamp the sun out of the sky; the lamp lights the scene
    clamp = nt.nodes.new("ShaderNodeVectorMath")
    clamp.operation = "MINIMUM"
    clamp.inputs[1].default_value = (L.SKY_CLAMP,) * 3
    sat = nt.nodes.new("ShaderNodeHueSaturation")
    sat.inputs["Saturation"].default_value = 1.35
    nt.links.new(env.outputs["Color"], sat.inputs["Color"])
    nt.links.new(sat.outputs["Color"], clamp.inputs[0])
    nt.links.new(clamp.outputs["Vector"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = L.SKY_STRENGTH
    print(f"hdri sun: azimuth {az:.1f}, elevation {el:.1f}, peak {peak:.0f} → rotated to {target}", flush=True)
    return el


def sun(elevation):
    s = L.SUN
    if s["strength"] <= 0:
        return None
    light = bpy.data.lights.new("Sun", "SUN")
    light.energy = s["strength"]
    light.color = s["color"]
    light.angle = math.radians(s["angle"])
    obj = bpy.data.objects.new("Sun", light)
    collection("STAGE").objects.link(obj)
    d = _sun_vector(s["azimuth"], elevation)
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return obj


def sun_disk(distance=9000.0):
    """The lamp is invisible to the camera: a far emissive disc marks the sun (and glints on the water)."""
    s = L.SUN
    d = _sun_vector(s["azimuth"], s["elevation"])
    radius = distance * math.tan(math.radians(0.55))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=d * distance, segments=24, ring_count=12)
    obj = bpy.context.active_object
    obj.name = "SunDisk"
    for c in obj.users_collection:
        c.objects.unlink(obj)
    collection("STAGE").objects.link(obj)
    mat = bpy.data.materials.new("M_SunDisk")
    mat.use_nodes = True
    nt = mat.node_tree
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.82, 0.55, 1)
    em.inputs["Strength"].default_value = 160.0
    nt.links.new(em.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
    obj.data.materials.append(mat)
    obj.visible_diffuse = False
    obj.visible_shadow = False
    obj.visible_volume_scatter = False
    return obj


def compositor():
    """Soft bloom around the sun and the lamps."""
    sc = bpy.context.scene
    try:
        tree = bpy.data.node_groups.new("GardenComp", "CompositorNodeTree")
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        sc.compositing_node_group = tree
        n = tree.nodes
        rl = n.new("CompositorNodeRLayers")
        glare = n.new("CompositorNodeGlare")
        out = n.new("NodeGroupOutput")

        def setp(name, value):
            if name in glare.inputs:
                glare.inputs[name].default_value = value
            elif hasattr(glare, name.lower()):
                setattr(glare, name.lower(), value)

        if "Type" in glare.inputs:
            glare.inputs["Type"].default_value = "Bloom"
        else:
            glare.glare_type = "BLOOM"
        setp("Threshold", 2.0)
        setp("Strength", 0.6)
        setp("Size", 0.75)
        tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
        tree.links.new(glare.outputs["Image"], out.inputs[0])
        print("compositor: bloom", flush=True)
    except Exception as e:  # the compositor API moves between versions; the render stays valid without it
        print("compositor skipped:", e, flush=True)


def cameras(site):
    col = collection("CAMERAS")
    cams = {}
    for name, v in L.VIEWS.items():
        cd = bpy.data.cameras.new("CAM_" + name)
        cd.lens = v["lens"]
        cd.clip_start = 0.05
        cd.clip_end = 20000
        obj = bpy.data.objects.new("CAM_" + name, cd)
        col.objects.link(obj)
        loc, tgt = Vector(v["loc"]), Vector(v["target"])
        loc.z += site.height(loc.x, loc.y)
        tgt.z += site.height(tgt.x, tgt.y)
        obj.location = loc
        obj.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
        if v["fstop"]:
            cd.dof.use_dof = True
            cd.dof.focus_distance = (tgt - loc).length
            cd.dof.aperture_fstop = v["fstop"]
        cams[name] = obj
    return cams


def render_settings(samples=128, preview=False):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    cy = sc.cycles
    cy.device = "GPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.03 if preview else 0.015
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 3
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 48
    cy.volume_bounces = 1
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    cy.sample_clamp_indirect = 8.0
    sc.render.use_persistent_data = True
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Base Contrast"):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            continue
    sc.view_settings.exposure = 0.55
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"


def render_views(cams, out_dir, views, scale=1.0):
    sc = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for name in views:
        v = L.VIEWS[name]
        sc.camera = cams[name]
        sc.render.resolution_x = int(v["size"][0] * scale)
        sc.render.resolution_y = int(v["size"][1] * scale)
        sc.render.resolution_percentage = 100
        path = os.path.join(out_dir, f"{name}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        paths[name] = path
        print(f"rendered {name} → {path}", flush=True)
    return paths


FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


def contact_sheet(paths, out):
    """Reference-style sheet: the front view large on the left, right/left/back stacked on the right,
    top/stream/plants along the bottom, each with its label."""
    def labelled(name, w, h):
        src = paths[name]
        tmp = src.replace(".png", f"_{w}x{h}.png")
        lab = L.VIEWS[name]["label"]
        subprocess.run(["magick", src, "-resize", f"{w}x{h}^", "-gravity", "center", "-extent", f"{w}x{h}", "+repage",
                        "-fill", "#0009", "-draw", f"roundrectangle 12,{h - 46} {30 + 11 * len(lab)},{h - 12} 8,8",
                        "-gravity", "southwest", "-font", FONT, "-pointsize", "19", "-fill", "white",
                        "-annotate", "+22+20", lab, tmp],
                       check=True)
        return tmp

    W = 1254
    big = labelled("front", 780, 858)
    side = [labelled(n, 466, 282) for n in ("right", "left", "back")]
    bottom = [labelled(n, 414, 390) for n in ("top", "stream", "plants")]
    col = out.replace(".png", "_col.png")
    subprocess.run(["magick", *side, "-background", "white", "-splice", "0x4", "-append", "-chop", "0x4", "+repage", col],
                   check=True)
    top = out.replace(".png", "_top.png")
    subprocess.run(["magick", big, col, "-background", "white", "-gravity", "north", "-splice", "4x0", "+append",
                    "-chop", "4x0", "+repage", top], check=True)
    row = out.replace(".png", "_row.png")
    subprocess.run(["magick", *bottom, "-background", "white", "-splice", "6x0", "+append", "-chop", "6x0", "+repage", row],
                   check=True)
    subprocess.run(["magick", top, row, "-background", "white", "-splice", "0x6", "-append", "-chop", "0x6",
                    "+repage", "-resize", f"{W}x", out], check=True)
    for p in (col, top, row, big, *side, *bottom):
        os.remove(p)
    return out
