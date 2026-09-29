#!/usr/bin/env python3
"""Index of a Pinskdrev catalogue PDF: every article (code, name, collection, L×B×H, pages, colours named on its pages).

    python3 tools/casegoods/catalog_index.py tools/casegoods/reference/catalog_km2.pdf --out tools/casegoods/reference/index.json

Reads the text of each page (pdftotext -raw): an article is a line "П6.980.0.01: L611xB418xH2012" (the name is the line
before it: «Шкаф «Флора»»); colours come from «Цветовое исполнение: «…»» and the swatch captions of the page. The site
links (instruction PDFs) are merged in by site_links.json when present (made in a browser: the site is behind a JS check).
"""
import argparse
import json
import os
import re
import subprocess
from collections import OrderedDict

CODE = re.compile(r"(?:П|БМ)\d\.\d{2,4}\.\d(?:\.\d+)*(?:-\d+)?")
DIMS = re.compile(r"L?\s*(\d{2,4})\s*[xх×]\s*[BВ]\s*(\d{2,4})\s*[xх×]\s*[HН]\s*(\d{2,4})(?:\s*\((\d+)\))?", re.I)
COLL = re.compile(r"«([^»]+)»")


def pages_text(pdf):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    for p in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-raw", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True, errors="replace").stdout
        yield p, t


def collection_of(name):
    m = COLL.findall(name or "")
    return m[-1].strip() if m else None


CHAIRS = "Стулья, табуреты, банкетки"
TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t",
                                                   "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))


SLUGS = {"Джио": "djio"}


def translit(name):
    if name == CHAIRS:
        return "stulya"
    if name in SLUGS:
        return SLUGS[name]
    s = "".join(TR.get(ch, ch) for ch in name.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def series(code):
    """П6.980.0.01 → П6.980 (a collection's series; a few collections share one)."""
    return ".".join(code.split(".")[:2])


def normalise(items):
    """One spelling per collection; chairs apart; articles whose name did not read get their series' collection and a check flag."""
    names = {}
    for it in items.values():
        c = it.get("collection")
        if c:
            names.setdefault(c.casefold(), []).append(c)
    canon = {k: max(set(v), key=v.count) for k, v in names.items()}
    big = [c for k, c in canon.items() if len(names[k]) >= 3]
    by_series = {}
    for it in items.values():
        c = it.get("collection")
        if not c:
            continue
        c = canon[c.casefold()]
        for b in big:
            if c.casefold().startswith(b.casefold() + " "):
                c = b
        if c.endswith(" М") or c in ("Рустикаль", "Контур", "Тинкер", "Эмбер", "Мэдисон", "Паола Люкс", "Юстина Люкс", "Цезарь Классик",
                                   "Моника Концепт"):
            c = CHAIRS
        # a name with a number is a module's name ("Мартина ТВ1 3Д") or a colour read as the name ("Сосна Карелия 528")
        if re.search(r"\d", c):
            first = c.split()[0]
            c = first if any(o.split()[0] == first and o != c for o in canon.values()) else None
        it["collection"] = c
        if c:
            by_series.setdefault(series(it["code"]), []).append(c)
    for it in items.values():
        if CODE.search(it.get("name") or "") or not it.get("collection"):
            it["check"] = "название / размер прочитаны неуверенно — сверьте со страницей"
        if not it.get("collection"):
            v = by_series.get(series(it["code"]))
            it["collection"] = max(set(v), key=v.count) if v else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    ap.add_argument("--links", help="site_links.json (code → product url, instruction pdf, colours)")
    a = ap.parse_args()
    items = OrderedDict()
    for page, text in pages_text(a.pdf):
        lines = [l.strip() for l in text.splitlines()]
        colours = []
        for l in lines:
            if "исполнение" in l.lower() or "крашение" in l.lower():
                colours += [c.strip() for c in COLL.findall(l)]
        flat = "\n".join(lines)
        codes = list(CODE.finditer(flat))
        for k, m in enumerate(codes):
            code = m.group(0)
            # an article: the code followed (before the next code, within a few lines) by its size L×B×H
            end = codes[k + 1].start() if k + 1 < len(codes) else len(flat)
            window = flat[m.end():min(end, m.end() + 160)]
            d = DIMS.search(window)
            if not d:
                continue
            L, B, H, seat = d.groups()
            # the name: the line(s) just before the code
            before = flat[:m.start()].rstrip().split("\n")
            name = before[-1].strip() if before else ""
            if not COLL.search(name) and len(before) > 1:
                name = (before[-2].strip() + " " + name).strip()
            name = re.sub(r"\s+", " ", name)
            if name and name.upper() == name and len(name) > 3:
                name = name.capitalize()
            note = window[:d.start()].strip(" :\n")
            it = items.setdefault(code, {"code": code, "name": name, "collection": collection_of(name),
                                         "size": [int(L), int(B), int(H)], "pages": [], "colours": []})
            if note and "note" not in it:
                it["note"] = re.sub(r"\s+", " ", note)[:120]
            if seat:
                it["seat"] = int(seat)
            if page not in it["pages"]:
                it["pages"].append(page)
            for c in colours:
                if c not in it["colours"] and c != it.get("collection"):
                    it["colours"].append(c)
    normalise(items)
    if a.links and os.path.exists(a.links):
        with open(a.links) as fh:
            links = json.load(fh)
        for code, it in items.items():
            if code in links:
                it.update(links[code])
    # every article gets its collection's slug: the site's collection address is the transliterated name
    # (a crawl of collection pages mixes other collections' products in, so it is not trusted for this)
    for it in items.values():
        it["slug"] = translit(it["collection"]) if it.get("collection") else None
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(list(items.values()), fh, ensure_ascii=False, indent=1)
    cols = OrderedDict()
    for it in items.values():
        cols.setdefault(it["collection"], 0)
        cols[it["collection"]] += 1
    print(f"{len(items)} articles, {len(cols)} collections")
    for c, n in cols.items():
        print(f"  {n:4}  {c}")


if __name__ == "__main__":
    main()
