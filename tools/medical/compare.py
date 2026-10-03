"""Side-by-side check sheets: python3 tools/medical/compare.py <id> [<id> ...]
→ tools/medical/renders/<id>-compare.png: the catalogue photo (and extra views) next to the model's angle, front and
side renders, all at the same height, with a 10 cm grid hint in the title. Read it and list every difference."""
import json, os, sys
try:
    from PIL import Image, ImageDraw
except ImportError:
    # the system python has no Pillow: rerun with the project venv that has it
    VENV = os.path.expanduser("~/.cache/house-med-venv/bin/python")
    if os.path.exists(VENV) and os.path.realpath(sys.executable) != os.path.realpath(VENV):
        os.execv(VENV, [VENV] + sys.argv)
    raise

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
inv = {d["id"]: d for d in json.load(open(os.path.join(ROOT, "tools/medical/inventory.json")))["devices"]}
H = 620
for id_ in sys.argv[1:]:
    d = inv[id_]
    imgs = []
    for rel in [d.get("photo")] + (d.get("views") or [])[:2]:
        if rel and os.path.exists(os.path.join(ROOT, rel)):
            imgs.append(("фото", Image.open(os.path.join(ROOT, rel)).convert("RGB")))
    for v in ("angle", "front", "side"):
        p = os.path.join(ROOT, "tools/medical/renders", f"{id_}-{v}.png")
        if os.path.exists(p):
            imgs.append((v, Image.open(p).convert("RGB")))
    tiles = []
    for name, im in imgs:
        im = im.copy(); im.thumbnail((int(H * 1.3), H)); tiles.append((name, im))
    W = sum(t.width for _, t in tiles) + 10 * len(tiles)
    sheet = Image.new("RGB", (max(W, 400), H + 40), "white")
    dr = ImageDraw.Draw(sheet)
    dr.text((6, 4), f"{id_}  {d.get('code') or ''}  size {d['size']} mm  ({'printed' if d.get('printed') else 'estimate'})", fill="black")
    x = 0
    for name, t in tiles:
        sheet.paste(t, (x, 36)); dr.text((x + 4, 22), name, fill="gray"); x += t.width + 10
    out = os.path.join(ROOT, "tools/medical/renders", f"{id_}-compare.png")
    sheet.save(out)
    print(out)
