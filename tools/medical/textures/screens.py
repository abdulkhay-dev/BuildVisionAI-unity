"""Screen pictures of the medical devices: every inventory screenCrop → library material med_<id>_screen (fitted, 1×1)."""
import json, os, sys
import numpy as np
from PIL import Image, ImageEnhance

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "Assets/House4696/External/Materials")
inv = json.load(open(os.path.join(ROOT, "tools/medical/inventory.json")))["devices"]
entries = []
for d in inv:
    crop = d.get("screenCrop")
    if not crop or d.get("skip"):
        continue
    src = os.path.join(ROOT, crop)
    if not os.path.exists(src):
        print("missing", src); continue
    mid = f"med_{d['id']}_screen"
    folder = os.path.join(OUT, mid)
    os.makedirs(folder, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.thumbnail((1024, 1024), Image.LANCZOS)
    # a lit display reads brighter and a little more saturated than the photo of it
    im = ImageEnhance.Brightness(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.1)
    im.save(os.path.join(folder, f"{mid}_albedo.jpg"), quality=90)
    w, h = im.size
    Image.new("RGB", (max(4, w // 4), max(4, h // 4)), (128, 128, 255)).save(os.path.join(folder, f"{mid}_normal.jpg"), quality=95)
    m = np.zeros((64, 64, 4), np.uint8); m[..., 1] = 255; m[..., 3] = int(0.85 * 255)   # glass-smooth, not metallic
    Image.fromarray(m, "RGBA").save(os.path.join(folder, f"{mid}_mask.png"))
    entries.append({"id": mid, "name": f"Экран {d.get('code') or d['id']}", "category": "medical", "source": crop, "neutral": False,
                    "metersPerTile": [1.0, 1.0], "maxSize": 1024, "folder": f"Materials/{mid}",
                    "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}})
json.dump(entries, open(os.path.join(ROOT, "tools/medical/textures/entries/screens.json"), "w"), ensure_ascii=False, indent=1)
print(len(entries), "screens")
