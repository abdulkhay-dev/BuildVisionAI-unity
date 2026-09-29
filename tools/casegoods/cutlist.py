#!/usr/bin/env python3
"""Cut list of a Pinskdrev assembly instruction (IS-*.pdf): the table «Номер детали | Код детали | Размеры, мм | Количество».

    python3 tools/casegoods/cutlist.py tools/casegoods/reference/flora/is/IS-P6-980-0-01-SHkaf.pdf [--json out.json]
        [--png page.png [--dpi 110]]

--png renders the page that holds the table (it also has the front / back views with the part numbers).

Prints one row per part: number, code, the three sizes (mm), count. The table is text in the PDF (pdftotext -layout from
poppler); two tables often stand side by side on one line, both are read. Hardware (legs, handles, hinges) is drawn as
pictures with counts — not in this table; designs mark those parts with "covers".
"""
import argparse
import json
import re
import subprocess
import sys

NUM = r"[0-9]+(?:[.,][0-9]+)?"
# A — the current instructions: «1  6.980.0.01.001  1830 402 16  1» (number, code, three sizes, count)
ROW = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)\s+"               # part number: 1, 6.2, 14.1, 002
    r"П?(\d\.\d{3}\.\d\.\d{2,3}(?:\.[\d.]+)?)\s+"  # code: 6.980.0.01.001 / П6.114.1.02.002
    rf"({NUM})\s+({NUM})\s+({NUM})\s+(\d+)(?![\d.,])"
)
# B — «1 6.528.1.09.01 Стенка вертикальная 1» (number or not, code, name, count; the sizes are on the drawing)
ROW_B = re.compile(r"(?:(?<![\d.])(\d{1,3})\s+)?П?(\d\.\d{3}\.\d\.\d{2}\.(\d{1,3}(?:\.\d+)?))\s+([А-ЯЁа-яё][А-ЯЁа-яё \-()]{2,40}?)\s{1,}(\d{1,2})(?![\d.,хx])")
# C — «1 Стенка передняя 61.03101 ЛДСП 16мм ДУБ КАНЬОН 1 1365 268» (name, article, material, count, two sizes)
ROW_C = re.compile(r"(?<![\d.])(\d{1,2})\s+([А-ЯЁа-яё][^\d]{2,40}?)\s+(\d{2}\.\d{4,6})\s+(.{3,45}?)\s+(\d{1,2})\s+(\d{2,4}(?:[.,]\d)?)\s+(\d{2,4}(?:[.,]\d)?)(?![\d])")
# D — «1 Крышка 1500х450 1» (number, name, two or three sizes, count)
ROW_D = re.compile(rf"(?<![\d.])(\d{{1,2}})\s+([А-ЯЁа-яё][^\d]{{2,45}}?)\s+({NUM})\s*[хx×]\s*({NUM})(?:\s*[хx×]\s*({NUM}))?\s+(\d{{1,2}})(?![\d.,хx])")


def text_of(pdf, pages=6):
    out = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", str(pages), pdf, "-"],
                         capture_output=True, text=True, errors="replace")
    return out.stdout


def f(s):
    return float(s.replace(",", "."))


def parse(pdf):
    """Rows of the cut list: {n, code?, name?, size ([3], [2] without the thickness, or None), count, material?}."""
    text = text_of(pdf)
    rows, seen = [], set()

    def add(r):
        if r["n"] in seen:
            return
        seen.add(r["n"])
        rows.append(r)

    for line in text.splitlines():
        for m in ROW.finditer(line):
            n, code, a, b, c, cnt = m.groups()
            add({"n": n.lstrip("0") or n, "code": code, "size": [f(a), f(b), f(c)], "count": int(cnt)})
    if rows:
        return rows
    for line in text.splitlines():
        for m in ROW_C.finditer(line):
            n, name, art, mat, cnt, a, b = m.groups()
            t = re.search(r"(\d+(?:[.,]\d+)?)\s*мм", mat)
            size = [f(a), f(b)] + ([f(t.group(1))] if t else [])
            add({"n": n, "name": name.strip(), "code": art, "material": re.sub(r"\s+", " ", mat.strip()), "size": size, "count": int(cnt)})
    if rows:
        return rows
    for line in text.splitlines():
        for m in ROW_D.finditer(line):
            n, name, a, b, c, cnt = m.groups()
            add({"n": n, "name": name.strip(), "size": [f(a), f(b)] + ([f(c)] if c else []), "count": int(cnt)})
    if rows:
        return rows
    for line in text.splitlines():
        for m in ROW_B.finditer(line):
            n, code, last, name, cnt = m.groups()
            add({"n": n or last.lstrip("0") or last, "code": code, "name": name.strip(), "size": None, "count": int(cnt)})
    return rows


def table_page(pdf, pages=6):
    """1-based number of the page holding the cut list."""
    for p in range(1, pages + 1):
        out = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True, errors="replace")
        if any(r.search(l) for r in (ROW, ROW_B, ROW_C, ROW_D) for l in out.stdout.splitlines()):
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--json", help="write the rows to this file")
    ap.add_argument("--png", help="render the table's page to this PNG")
    ap.add_argument("--dpi", type=int, default=110)
    a = ap.parse_args()
    rows = parse(a.pdf)
    if not rows:
        print("no cut list found (a scanned PDF? read the table from the page image)", file=sys.stderr)
        sys.exit(1)
    for r in rows:
        s = r.get("size")
        size = " × ".join(f"{v:g}" for v in s) if s else "(sizes on the drawing)"
        print(f'{r["n"]:>6}  {(r.get("code") or ""):<20} {(r.get("name") or "")[:26]:<26} {size:<24} ×{r["count"]}  {r.get("material", "")}')
    page = table_page(a.pdf)
    print(f"table on page {page}")
    if a.png and page:
        base = a.png[:-4] if a.png.endswith(".png") else a.png
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(a.dpi), "-png", "-singlefile", a.pdf, base], check=True)
        print("→ " + base + ".png")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
