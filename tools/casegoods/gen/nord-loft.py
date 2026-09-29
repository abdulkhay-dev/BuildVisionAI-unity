"""«Норд Лофт» (Пинскдрев, П3.0560): six nesting coffee tables — a black steel cube frame under a square top.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/nord-loft.py

By the catalogue (p. 79: cut-outs, «Варианты крашения»: «Дуб натуральный» массив / «Дуб Вотан» ЛДСП) and the site's
photos (no instruction exists). 0.01 / 0.02 / 0.03 have a solid oak top (20 mm, eased edges), 0.04 / 0.05 / 0.06 the same
tables with a ЛДСП 25 «Дуб Вотан» top (the photos «Stol_zhyrnalnii_Nord-22 … dyb_vatan»). The frame is a cube of 15 mm
square steel tube: four posts, four rails under the top and four on the floor; the top overhangs the frame by 6 mm
(front-on photo of 0.04: frame 398 under a 410 top, posts 15.5 mm). Sizes 410 / 460 / 510 nest into each other.
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "nord-loft"
TUBE = 15
OVER = 6

TABLES = [  # tail, code, size, top thickness, finish
    ("0-01", "П3.0560.0.01", 410, 420, 20, "dub-massiv"),
    ("0-02", "П3.0560.0.02", 460, 470, 20, "dub-massiv"),
    ("0-03", "П3.0560.0.03", 510, 520, 20, "dub-massiv"),
    ("0-04", "П3.0560.0.04", 410, 420, 25, "votan"),
    ("0-05", "П3.0560.0.05", 460, 470, 25, "votan"),
    ("0-06", "П3.0560.0.06", 510, 520, 25, "votan"),
]


def table(tail, L, H, tt):
    parts = []
    ty = H - tt
    solid = tt == 20
    parts.append({"id": "top", "mat": "top", "grain": "x", "edge": 3 if solid else 1, "box": [0, ty, 0, L, H, L]})
    a, b = OVER, L - OVER
    fh = ty
    posts = [(a, a), (b - TUBE, a), (a, b - TUBE), (b - TUBE, b - TUBE)]
    for k, (x, z) in enumerate(posts):
        parts.append({"id": f"post-{k + 1}", "mat": "metal", "edge": 1, "box": [x, TUBE, z, x + TUBE, fh - TUBE, z + TUBE]})
    for lvl, (y0, y1) in (("top", (fh - TUBE, fh)), ("floor", (0, TUBE))):
        parts.append({"id": f"rail-{lvl}-back", "mat": "metal", "edge": 1, "box": [a, y0, a, b, y1, a + TUBE]})
        parts.append({"id": f"rail-{lvl}-front", "mat": "metal", "edge": 1, "box": [a, y0, b - TUBE, b, y1, b]})
        parts.append({"id": f"rail-{lvl}-l", "mat": "metal", "edge": 1, "box": [a, y0, a + TUBE, a + TUBE, y1, b - TUBE]})
        parts.append({"id": f"rail-{lvl}-r", "mat": "metal", "edge": 1, "box": [b - TUBE, y0, a + TUBE, b, y1, b - TUBE]})
    return dump(f"{SLUG}-{tail}", [L, L, H], parts, [])


def write_catalog():
    models = []
    for tail, code, L, H, tt, fin in TABLES:
        top = "массив дуба 20 мм" if tt == 20 else "ЛДСП 25 «Дуб Вотан»"
        models.append({"id": f"{SLUG}-{tail}", "code": code, "name": "Стол журнальный «Норд Лофт»", "collection": SLUG,
                       "category": "tables", "size": [L, L, H], "page": 79, "finish": f"{SLUG}-{fin}",
                       "note": f"столешница: {top}; по каталогу и фото, без инструкции"})
    frag = {
        "finishes": [
            {"id": f"{SLUG}-dub-massiv", "name": "Дуб натуральный (массив)", "body": "door_enamel_whitey#9a866a",
             "roles": {"top": "door_enamel_whitey#9a866a"}, "swatch": "#9a866a"},
            {"id": f"{SLUG}-votan", "name": "Дуб Вотан (ЛДСП)", "body": "door_enamel_whitey#7a5b41",
             "roles": {"top": "door_enamel_whitey#7a5b41"}, "swatch": "#7a5b41"}],
        "profiles": {},
        "collections": [
            {"id": SLUG, "name": "Норд Лофт", "brand": "Пинскдрев", "finishes": [f"{SLUG}-dub-massiv", f"{SLUG}-votan"],
             "metal": "black",
             "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 79 (каталог 155). Журнальные столы-«кубы» трёх размеров "
                     "(вкладываются друг в друга): каркас из чёрной стальной трубы 15×15 (стойки, обвязка под столешницей "
                     "и на полу), столешница с напуском 6 мм — массив дуба 20 мм (0.01–0.03) или ЛДСП 25 «Дуб Вотан» "
                     "(0.04–0.06)."}],
        "models": models,
    }
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


def main():
    write_catalog()
    for tail, code, L, H, tt, fin in TABLES:
        print(table(tail, L, H, tt))


if __name__ == "__main__":
    main()
