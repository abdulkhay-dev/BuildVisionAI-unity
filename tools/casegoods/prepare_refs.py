#!/usr/bin/env python3
"""References for authoring designs without the manufacturer's site (a cloud session cannot pass its JS check).

    python3 tools/casegoods/prepare_refs.py [--collections flora,monako] [--dpi 100]

For every article of tools/casegoods/reference/index.json that has an instruction ("pdf", from the site crawl): downloads
the PDF into tools/casegoods/.cache/is/ (git-ignored) and writes into tools/casegoods/reference/<collection slug>/:
  cutlists/<model id>.json   — the cut list (cutlist.py; rows with broken text are missing: read the page)
  pages/<model id>.png       — the table page with the front / back views and part numbers (grey); when the PDF has no
                               text layer: pages/<model id>-p1…p4.png (read the table from the picture)
  pages/<model id>-cover.png — the first page: the overall drawing with the catalogue sizes
Model id = <collection slug>-<the code's last groups>: П6.980.0.01 → flora-0-01.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REF = os.path.join(HERE, "reference")
CACHE = os.path.join(HERE, ".cache", "is")
sys.path.insert(0, HERE)
import cutlist  # noqa: E402


def model_id(slug, code):
    parts = re.sub(r"^(П|БМ)", "", code).split(".")
    tail = ".".join(parts[2:]) if len(parts) > 2 else parts[-1]
    return f"{slug}-{tail.replace('.', '-')}"


def fetch(url, path):
    """curl from a.pinskdrev.ru; files only on a.pinskdrev.by come from there (its certificate chain is incomplete, so that
    host is fetched without verification — public instruction PDFs only)."""
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    name = url.rsplit("/", 1)[-1]
    for host, extra in (("a.pinskdrev.ru", []), ("a.pinskdrev.by", ["-k"])):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-A", "Mozilla/5.0", *extra, "-o", path, "-w", "%{http_code}",
                            f"https://{host}/web/pdf/{name}"], capture_output=True, text=True)
        if r.stdout.strip() == "200" and os.path.exists(path) and os.path.getsize(path) > 1000:
            return True
    print(f"  ! {name}: not on a.pinskdrev.ru / .by")
    if os.path.exists(path):
        os.remove(path)
    return False


def grey(png, dpi_note=None):
    try:
        from PIL import Image
        Image.open(png).convert("L").save(png, optimize=True)
    except ImportError:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--collections", help="comma-separated collection slugs (default: all)")
    ap.add_argument("--dpi", type=int, default=100)
    a = ap.parse_args()
    with open(os.path.join(REF, "index.json")) as fh:
        index = json.load(fh)
    want = set(a.collections.split(",")) if a.collections else None
    done = 0
    for it in index:
        slug, pdf = it.get("slug"), it.get("pdf")
        if not slug or not pdf or (want and slug not in want):
            continue
        mid = model_id(slug, it["code"])
        local = os.path.join(CACHE, os.path.basename(pdf))
        if not fetch(pdf, local):
            continue
        out = os.path.join(REF, slug)
        os.makedirs(os.path.join(out, "cutlists"), exist_ok=True)
        os.makedirs(os.path.join(out, "pages"), exist_ok=True)
        rows = cutlist.parse(local)
        page = cutlist.table_page(local)
        with open(os.path.join(out, "cutlists", mid + ".json"), "w") as fh:
            json.dump({"code": it["code"], "name": it.get("name"), "size": it.get("size"), "is": os.path.basename(pdf),
                       "table_page": page, "rows": rows}, fh, ensure_ascii=False, indent=1)
        base = os.path.join(out, "pages", mid)
        if page and not os.path.exists(base + ".png"):
            subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(a.dpi), "-png", "-singlefile", local, base], check=False)
            grey(base + ".png")
        elif not page:
            # no text layer (a scan, or drawn as curves): its first pages as pictures — the parts table is read by eye
            info = subprocess.run(["pdfinfo", local], capture_output=True, text=True).stdout
            n = int(re.search(r"Pages:\s+(\d+)", info).group(1)) if "Pages:" in info else 1
            for k in range(1, min(n, 4) + 1):
                png = f"{base}-p{k}"
                if not os.path.exists(png + ".png"):
                    subprocess.run(["pdftoppm", "-f", str(k), "-l", str(k), "-r", str(a.dpi), "-png", "-singlefile", local, png], check=False)
                    grey(png + ".png")
        if not os.path.exists(base + "-cover.png"):
            subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "60", "-png", "-singlefile", local, base + "-cover"], check=False)
            grey(base + "-cover.png")
        done += 1
        print(f"{mid:28} {it['code']:18} rows {len(rows):3}  page {page}")
    print(f"{done} articles")


if __name__ == "__main__":
    main()
