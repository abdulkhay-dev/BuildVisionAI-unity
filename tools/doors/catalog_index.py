"""Extract every door photo of the DveriMebel / el'PORTA catalogue PDF with its caption.

    python3 tools/doors/catalog_index.py ~/Downloads/katalog_dverey_dm_12_02_2020.pdf

Needs poppler (pdftohtml) and Pillow. Output goes to tools/doors/.cache (git-ignored: the photos are the
manufacturer's):
    pdf/          images at their embedded resolution (144 ppi) + cat.xml with placements and text boxes
    photos/       one file per door photo: p<catalog page>_<model>__<finish>.jpg
    index.json    [{page, catPage, model, finish, header, file, w, h, px: [width, height]}]

The PDF pages are spreads: PDF page n holds catalogue pages 2n-4 (left) and 2n-3 (right). A door photo is a tall
image; its caption is the bold line right under it (model, e.g. "ПОРТА-22 MF") and the italic line below (finish).
"""
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"

TRANSLIT = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s",
                     "t", "u", "f", "h", "c", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))


def slug(s):
    s = "".join(TRANSLIT.get(c, c) for c in (s or "unknown").lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def main(pdf):
    raw = CACHE / "pdf"
    photos = CACHE / "photos"
    raw.mkdir(parents=True, exist_ok=True)
    photos.mkdir(parents=True, exist_ok=True)
    if not (raw / "cat.xml").exists():
        subprocess.run(["pdftohtml", "-xml", "-q", str(pdf), str(raw / "cat")], check=True)

    entries = []
    for page in ET.parse(raw / "cat.xml").getroot().iter("page"):
        num = int(page.get("number"))
        width = float(page.get("width"))
        texts = []
        for t in page.iter("text"):
            s = "".join(t.itertext()).strip()
            if s:
                texts.append(dict(top=float(t.get("top")), left=float(t.get("left")), s=s,
                                  italic=t.find(".//i") is not None))
        headers = [t for t in texts if t["top"] < 60]
        for im in page.iter("image"):
            top, left = float(im.get("top")), float(im.get("left"))
            w, h = float(im.get("width")), float(im.get("height"))
            if h < 150 or h < w * 1.2:
                continue  # swatches, profiles, pictograms, double-leaf blocks
            bottom = top + h
            cap = sorted((t for t in texts if bottom - 5 <= t["top"] <= bottom + 70 and left - 25 <= t["left"] <= left + w),
                         key=lambda t: (t["top"], t["left"]))
            model = next((t["s"] for t in cap if not t["italic"]), None)
            finish = next((t["s"] for t in cap if t["italic"]), None)
            if model is None:
                continue
            half_left = left + w / 2 < width / 2
            src = raw / Path(im.get("src")).name
            cat_page = 2 * num - 4 + (0 if half_left else 1)
            name = f"p{cat_page:03d}_{slug(model)}__{slug(finish)}{src.suffix}"
            shutil.copy(src, photos / name)
            with Image.open(src) as img:
                px = list(img.size)
            entries.append(dict(page=num, catPage=cat_page, model=model, finish=finish,
                                header=[t["s"] for t in headers if (t["left"] < width / 2) == half_left],
                                file=name, w=w, h=h, px=px))

    (CACHE / "index.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1))
    print(len(entries), "photos,", len({e["model"] for e in entries}), "captions ->", CACHE)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Downloads/katalog_dverey_dm_12_02_2020.pdf").expanduser())
