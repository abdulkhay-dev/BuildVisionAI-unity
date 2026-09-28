"""Builds the interior library models and merges them into Assets/House4696/External/external.json.

    /Applications/Blender.app/Contents/MacOS/Blender -b --python tools/interior/build.py [-- id|room ...]

No arguments = every model. Then Unity: House 46-96 → External → Import Catalog, and Render Catalog Thumbnails."""
import fcntl
import json
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models  # noqa: E402
from kit import OUT, ROOT  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = set(argv)
    path = os.path.join(OUT, "external.json")
    built = {}
    failed = []
    for e, fn in models.entries():
        if only and e["id"] not in only and e["room"] not in only:
            continue
        t = time.time()
        try:
            m = fn(e)
        except Exception:
            traceback.print_exc()
            failed.append(e["id"])
            continue
        m["room"] = e["room"]
        built[e["id"]] = m
        print(f"model {m['id']:28s} size {m['size']} tris {m['triangles']:6d} slots {[s['slot'] for s in m['slots']]} "
              f"{time.time() - t:.1f}s", flush=True)
    # several builds may run at once (one per room): merge under a lock
    lock_path = os.path.join(ROOT, ".cache", "external.json.lock")      # outside Assets: Unity would import it
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    with open(lock_path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.load(open(path))
        order = [m["id"] for m in manifest["models"]]
        by_id = {m["id"]: m for m in manifest["models"]}
        for i, m in built.items():
            if i not in by_id:
                order.append(i)
            by_id[i] = m
        manifest["models"] = [by_id[i] for i in order]
        with open(path + ".tmp", "w") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1)
        os.replace(path + ".tmp", path)
    print("manifest", path, "failed", failed)


main()
