"""«Боро» (Пинскдрев, БМ2.759): kids' bed 1-09 with storage in «Дуб Сонома» — by catalogue (p. 96) and the product
photo; no instruction is published. Built with the day-bed scheme of Ирвинг 1.40 (gen/irving.py): two ends rounded down
to the front rail, a low back board, a solid ЛДСП base («Основание сплошное»), three drawers under the front rail with
bronze bar handles, mattress 2000 × 900 (the catalogue recommends 210–240 high; 200 built).

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/boro.py
"""
import json
import os

from irving import day_bed

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG, FIN = "boro", "boro-dub-sonoma"


def main():
    d = day_bed("boro-1-40", 2044, 951, 650, drawers=3, handles=True, back_h=450)
    d.write()
    frag = {"finishes": [{"id": FIN, "name": "Дуб Сонома", "body": "door_enamel_whitey#b99c85", "swatch": "#b99c85"}],
            "profiles": {},
            "collections": [{"id": SLUG, "name": "Боро", "brand": "Пинскдрев", "finishes": [FIN], "metal": "gold#6b5843",
                             "note": "Каталог «Корпусная мебель ч. II» 2025, с. 96 (разворот 188). Кровать детская 1-09 с ящиками, "
                                     "ЛДСП «Дуб Сонома», сплошное основание, три ящика с ручками-скобами; по каталогу и фото."}],
            "models": [{"id": "boro-1-40", "code": "БМ2.759.1.40", "name": "Кровать 1-09 «Боро»", "collection": SLUG,
                        "category": "kids", "size": d.size, "page": 96,
                        "note": "спальное место 2000×900, ящики для белья; по каталогу и фото, без инструкции"}]}
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
    print(d.did)


if __name__ == "__main__":
    main()
