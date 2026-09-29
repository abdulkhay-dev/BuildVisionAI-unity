#!/usr/bin/env python3
"""Catalogue pages without poppler (PyMuPDF): render a spread, crop it, read a swatch's colour, print its text.

    python3 tools/casegoods/gen/catpage.py 4 --out /tmp/p4.png [--dpi 100]            # the whole spread
    python3 tools/casegoods/gen/catpage.py 4 --crop 0.1,0.2,0.4,0.9 --dpi 250 --out /tmp/c.png
                                                   # a part of it: fractions of the page (x0,y0,x1,y1, 0..1)
    python3 tools/casegoods/gen/catpage.py 4 --swatch 0.61,0.40,0.63,0.42           # mean colour of a flat crop → #rrggbb
    python3 tools/casegoods/gen/catpage.py 4 --text                                   # the spread's text (codes, sizes)

Page numbers are the PDF's (1-based) = the "pages" of reference/index.json. A spread is 1658 × 964 pt.
"""
import argparse
import os

import numpy as np
import pymupdf
from PIL import Image

PDF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference", "catalog_km2.pdf")


def frac_rect(page, s):
    x0, y0, x1, y1 = (float(v) for v in s.split(","))
    r = page.rect
    return pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)


def render(page, dpi, clip=None):
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def swatch(page, s):
    """Trimmed mean (the middle 60 % by brightness) of the crop, rendered at 150 dpi: robust to specks and text."""
    im = np.asarray(render(page, 150, frac_rect(page, s))).reshape(-1, 3).astype(float)
    lum = im @ [0.299, 0.587, 0.114]
    order = np.argsort(lum)
    k = len(order)
    mid = im[order[int(k * 0.2):max(int(k * 0.8), int(k * 0.2) + 1)]]
    m = mid.mean(axis=0)
    return "#" + "".join(f"{int(round(v)):02x}" for v in m), float(im.std(axis=0).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", type=int)
    ap.add_argument("--out")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--crop", help="x0,y0,x1,y1 as fractions of the spread")
    ap.add_argument("--swatch", help="x0,y0,x1,y1 as fractions: print the mean colour")
    ap.add_argument("--text", action="store_true")
    a = ap.parse_args()
    doc = pymupdf.open(PDF)
    page = doc[a.page - 1]
    if a.text:
        print(page.get_text())
    if a.swatch:
        hexc, spread = swatch(page, a.swatch)
        print(f"{hexc}  (spread ±{spread:.1f}: {'flat' if spread < 12 else 'textured / mixed — crop tighter or it is a decor'})")
    if a.out:
        im = render(page, a.dpi, frac_rect(page, a.crop) if a.crop else None)
        im.save(a.out)
        print(f"→ {a.out} ({im.width}×{im.height})")


if __name__ == "__main__":
    main()
