#!/usr/bin/env python3
"""Downloads the Poly Haven (CC0) sources listed in tools/assets/catalog.json into .cache/polyhaven/<source>/.

Materials: base colour, OpenGL normal and ARM (AO, roughness, metallic) maps plus info.json (real size).
Models: the glTF geometry (.gltf + .bin, textures skipped) and the ARM/diffuse/normal maps of every material.
Already downloaded files are skipped. Usage: python3 tools/assets/fetch_polyhaven.py [id ...]
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, ".cache", "polyhaven")
API = "https://api.polyhaven.com"
UA = {"User-Agent": "house-app-asset-pipeline"}


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    os.replace(tmp, path)
    return os.path.getsize(path)


def fetch_material(entry):
    src, res = entry["source"], entry.get("res", "1k")
    out = os.path.join(CACHE, src)
    files = get_json(f"{API}/files/{src}")
    info = get_json(f"{API}/info/{src}")
    total = 0
    # colour: "Diffuse", or the first colour variant ("col_01", "coll1") of multi-colour fabrics
    diffuse = "Diffuse" if "Diffuse" in files else next((k for k in sorted(files) if k.startswith("col")), None)
    # roughness/AO/metal packed as "arm"; a few assets only have "Rough"
    wanted = [(diffuse, "diff"), ("nor_gl", "nor_gl"), ("arm" if "arm" in files else "Rough", "arm" if "arm" in files else "rough")]
    for key, name in wanted:
        if key is None or key not in files or res not in files[key]:
            print(f"  {src}: no {name} map")
            continue
        total += download(files[key][res]["jpg"]["url"], os.path.join(out, f"{name}_{res}.jpg"))
    with open(os.path.join(out, "info.json"), "w") as f:
        json.dump({"dimensions_mm": info.get("dimensions"), "name": info.get("name"), "authors": info.get("authors")}, f, ensure_ascii=False)
    return total


def fetch_model(entry):
    src, res = entry["source"], entry.get("res", "1k")
    out = os.path.join(CACHE, src)
    files = get_json(f"{API}/files/{src}")
    info = get_json(f"{API}/info/{src}")
    if "gltf" not in files or res not in files["gltf"]:
        print(f"  {src}: no glTF at {res}, skipped")
        return 0
    gltf = files["gltf"][res]["gltf"]
    total = download(gltf["url"], os.path.join(out, "model.gltf"))
    for rel, inc in gltf.get("include", {}).items():
        if rel.endswith(".bin"):
            total += download(inc["url"], os.path.join(out, rel))
    # per-material maps are "<material>_diff" etc.; single-material models use "Diffuse", "nor_gl", "arm"
    single = {"Diffuse": ("main", "diff"), "nor_gl": ("main", "nor_gl"), "arm": ("main", "arm")}
    maps = {}
    for key, value in files.items():
        if not isinstance(value, dict) or res not in value or "jpg" not in value[res]:
            continue
        if key in single:
            material, kind = single[key]
        else:
            suffix = next((s for s in ("_diff", "_nor_gl", "_arm", "_alpha") if key.endswith(s)), None)
            if suffix is None:
                continue
            material, kind = key[: -len(suffix)], suffix[1:]
        name = f"{material}_{kind}_{res}.jpg"
        total += download(value[res]["jpg"]["url"], os.path.join(out, "maps", name))
        maps.setdefault(material, {})[kind] = f"maps/{name}"
    with open(os.path.join(out, "info.json"), "w") as f:
        json.dump({"name": info.get("name"), "authors": info.get("authors"), "maps": maps}, f, ensure_ascii=False, indent=1)
    return total


def main():
    with open(os.path.join(ROOT, "tools", "assets", "catalog.json")) as f:
        catalog = json.load(f)
    only = set(sys.argv[1:])
    grand = 0
    for entry in catalog["materials"]:
        if not only or entry["id"] in only:
            n = fetch_material(entry)
            grand += n
            print(f"material {entry['id']:22} ← {entry['source']:24} {n / 1e6:6.1f} MB new")
    for entry in catalog["models"]:
        if "source" in entry and (not only or entry["id"] in only):
            n = fetch_model(entry)
            grand += n
            print(f"model    {entry['id']:22} ← {entry['source']:24} {n / 1e6:6.1f} MB new")
    print(f"downloaded {grand / 1e6:.1f} MB into {CACHE}")


if __name__ == "__main__":
    main()
