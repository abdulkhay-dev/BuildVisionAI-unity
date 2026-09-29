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
ROW = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)\s+"          # part number: 1, 6.2, 14.1
    r"(\d\.\d{3}\.\d\.\d{2,3}(?:\.[\d.]+)?)\s+"  # code: 6.980.0.01.001 / 6.980.1.03.01
    rf"({NUM})\s+({NUM})\s+({NUM})\s+(\d+)(?![\d.,])"
)


def text_of(pdf, pages=6):
    out = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", str(pages), pdf, "-"],
                         capture_output=True, text=True, errors="replace")
    return out.stdout


def f(s):
    return float(s.replace(",", "."))


def table_page(pdf, pages=6):
    """1-based number of the page holding the cut list."""
    for p in range(1, pages + 1):
        out = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True, errors="replace")
        if any(ROW.search(l) for l in out.stdout.splitlines()):
            return p
    return None


def parse(pdf):
    rows, seen = [], set()
    for line in text_of(pdf).splitlines():
        for m in ROW.finditer(line):
            n, code, a, b, c, cnt = m.groups()
            key = (n, code)
            if key in seen:
                continue
            seen.add(key)
            rows.append({"n": n, "code": code, "size": [f(a), f(b), f(c)], "count": int(cnt)})
    return rows


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
        s = r["size"]
        print(f'{r["n"]:>6}  {r["code"]:<22} {s[0]:>7g} × {s[1]:>7g} × {s[2]:>5g}   ×{r["count"]}')
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
