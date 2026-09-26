#!/usr/bin/env python3
"""Downloads the Poly Haven (CC0) sources of the garden look-dev scene into .cache/polyhaven/blend/<id>/.

Models come as ready .blend files (materials with alpha-tested leaves included), the sky as an HDRI.
Already downloaded files are skipped. Run with /usr/bin/python3 (python.org builds lack SSL certificates).
Usage: /usr/bin/python3 tools/landscape/fetch_garden.py [id ...]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assets"))
from fetch_polyhaven import API, CACHE, download, fetch_material, get_json  # noqa: E402

OUT = os.path.join(CACHE, "blend")

ROCKS = ["namaqualand_boulder_02", "namaqualand_boulder_03", "namaqualand_boulder_04", "namaqualand_boulder_05",
         "namaqualand_boulder_06", "rock_moss_set_01", "rock_moss_set_02", "stone_01", "rock_07", "rock_09",
         "namaqualand_stones_01"]
PLANTS = ["shrub_01", "shrub_02", "shrub_03", "shrub_04", "fern_02", "grass_medium_01", "grass_medium_02",
          "grass_bermuda_01", "dandelion_01", "celandine_01", "periwinkle_plant", "nettle_plant", "weed_plant_02",
          "flower_gazania", "flower_ursinia", "flower_heliophila", "moss_01", "wild_rooibos_bush", "searsia_lucida"]
TREES = ["fir_tree_01", "island_tree_01", "island_tree_02", "island_tree_03", "tree_small_02", "fir_sapling_medium"]
HDRIS = [("kloppenheim_06_puresky", "4k"), ("qwantani_sunset_puresky", "4k")]
# ground textures (same layout as the material library: .cache/polyhaven/<id>/diff|nor_gl|arm_<res>.jpg)
TEXTURES = [("forest_ground_04", "2k"), ("sparse_grass", "2k"), ("river_small_rocks", "2k"),
            ("brown_mud_leaves_01", "2k"), ("forest_leaves_02", "1k")]


def fetch_blend(asset, res="1k"):
    blend = get_json(f"{API}/files/{asset}")["blend"][res]["blend"]
    out = os.path.join(OUT, asset)
    total = download(blend["url"], os.path.join(out, f"{asset}.blend"))
    for rel, inc in blend.get("include", {}).items():
        total += download(inc["url"], os.path.join(out, rel))
    return total


def fetch_hdri(asset, res):
    hdri = get_json(f"{API}/files/{asset}")["hdri"][res]["hdr"]
    return download(hdri["url"], os.path.join(OUT, "hdri", f"{asset}_{res}.hdr"))


def main():
    only = set(sys.argv[1:])
    grand = 0
    for asset in ROCKS + PLANTS + TREES:
        if not only or asset in only:
            n = fetch_blend(asset)
            grand += n
            print(f"model {asset:24} {n / 1e6:6.1f} MB new", flush=True)
    for asset, res in HDRIS:
        if not only or asset in only:
            n = fetch_hdri(asset, res)
            grand += n
            print(f"hdri  {asset:24} {n / 1e6:6.1f} MB new", flush=True)
    for asset, res in TEXTURES:
        if not only or asset in only:
            n = fetch_material({"source": asset, "res": res})
            grand += n
            print(f"tex   {asset:24} {n / 1e6:6.1f} MB new", flush=True)
    print(f"downloaded {grand / 1e6:.1f} MB into {OUT}")


if __name__ == "__main__":
    main()
