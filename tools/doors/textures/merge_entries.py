"""Merge door and casegoods (cg_*, cgfab_*, cgprint_*) material entries into Assets/House4696/External/external.json (safely from several writers at once).

    python3 tools/doors/textures/merge_entries.py tools/doors/textures/entries/<family>.json [...]

An entries file is a JSON array of material entries in the shape of external.json's "materials" (id "door_*",
"doorglass_*" or "doorart_*"). The merge replaces entries with the same id and appends new ones after the existing door entries;
every other entry of external.json stays byte-for-byte as it was. A lock file outside Assets (Unity would import it)
serialises concurrent merges.
"""
import fcntl
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Assets/House4696/External/external.json"
LOCK = ROOT / ".cache/external.json.lock"


def merge(files):
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads(MANIFEST.read_text())
        mats = manifest["materials"]
        index = {m["id"]: i for i, m in enumerate(mats)}
        added = replaced = 0
        for f in files:
            for e in json.loads(Path(f).read_text()):
                if not e["id"].startswith(("door_", "doorglass_", "doorart_", "cg_", "cgfab_", "cgprint_", "lift_", "liftfloor_", "liftdoor_", "liftwall_", "liftpanel_")):
                    raise SystemExit(f"{f}: {e['id']} is not a door / casegoods material (door_* / doorglass_* / doorart_* / cg_* / cgfab_* / cgprint_*)")
                if e["id"] in index:
                    mats[index[e["id"]]] = e
                    replaced += 1
                else:
                    index[e["id"]] = len(mats)
                    mats.append(e)
                    added += 1
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
        print(f"external.json: {added} added, {replaced} replaced")


if __name__ == "__main__":
    merge(sys.argv[1:])
