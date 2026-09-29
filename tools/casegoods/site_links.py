#!/usr/bin/env python3
"""Links of the catalogue's articles on the manufacturer's site (pinskdrev.by — the .ru site is behind a JS check).

    python3 tools/casegoods/site_links.py            # updates tools/casegoods/reference/site_links.json

Finds every article of reference/index.json in the site map by its code in the product's address
(П7.056.1.16 → p7-056-1-16, БМ2.748.1.32 → bm2-748-1-32), then reads each product page: the assembly instruction
(a.pinskdrev.ru/web/pdf/IS-….pdf), the product photos and the colour variants. Keeps what an earlier run (or the
browser crawl) found. Then run catalog_index.py with --links to merge it into index.json.
"""
import concurrent.futures as cf
import html
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")
SITE = "https://pinskdrev.by"


def get(url, tries=3):
    """curl (it brings its own certificates, which a bare python.org Python may not have)."""
    for _ in range(tries):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "40", "-A", "Mozilla/5.0", url], capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode("utf-8", "replace")
    return ""


def token(code):
    return re.sub(r"^(П|БМ)", lambda m: "p" if m.group(1) == "П" else "bm", code).replace(".", "-").lower()


def main():
    with open(os.path.join(REF, "index.json")) as fh:
        index = json.load(fh)
    path = os.path.join(REF, "site_links.json")
    links = json.load(open(path)) if os.path.exists(path) else {}
    smap = get(SITE + "/sitemap.xml")
    urls = []
    subs = re.findall(r"<sitemap>\s*<loc>([^<]+)</loc>", smap)
    for m in subs or [None]:
        urls += re.findall(r"<loc>([^<]+)</loc>", get(m.replace("https://pinskdrev.ru", SITE)) if m else smap)
    urls = [u.replace("https://pinskdrev.ru", SITE) for u in urls if "/catalog/" in u]
    print(len(urls), "product urls")
    todo = []
    for it in index:
        code = it["code"]
        tok = token(code)
        hits = [u for u in urls if re.search(re.escape(tok) + r"(?![\d])", u)]
        if not hits:
            continue
        e = links.setdefault(code, {})
        e.setdefault("site", hits[0])
        todo.append((code, hits[0]))

    def read(job):
        code, url = job
        page = get(url)
        pdf = re.findall(r'href="(https://a\.pinskdrev\.(?:ru|by|kz)/web/pdf/[^"]+\.pdf)"', page)
        imgs = re.findall(r'"(/web/catalogfiles/(?:catalog/offers|photogallery/Offer/\d+)/[^"\s]+\.(?:jpe?g|png))"', page)
        title = html.unescape((re.search(r"<title>([^<]*)", page) or [None, ""])[1]).split(" купить")[0]
        return code, pdf[0] if pdf else None, list(dict.fromkeys(SITE + i for i in imgs))[:8], title

    with cf.ThreadPoolExecutor(8) as ex:
        for code, pdf, imgs, title in ex.map(read, todo):
            e = links[code]
            if pdf and not e.get("pdf"):
                e["pdf"] = pdf
            if imgs:
                e["photos"] = imgs
            if title:
                e["site_title"] = title
    with open(path, "w") as fh:
        json.dump(links, fh, ensure_ascii=False, indent=1)
    print(len(links), "articles on the site;", sum(1 for e in links.values() if e.get("pdf")), "with an instruction")


if __name__ == "__main__":
    main()
