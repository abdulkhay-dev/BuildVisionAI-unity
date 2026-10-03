from t3_alclib import *
d = D("alc-1", [2050, 750, 650], dict(MATS, stripe="gloss#8fb0dc"))
body(d, 0, 2050, 750, 650, stripe="stripe")
d.save()
