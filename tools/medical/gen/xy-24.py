from p1lib import *
d = D("xy-24", [780, 480, 1250], {
  "frame": "plastic#f1efe9", "blue": "leather#2b48a8", "dblue": "plastic#2a46a6", "cap": "rubber#1c1d20",
  "motor": "metal#b9bcc0", "drum": "plastic#5a1e22", "belt": "fabric#8f9a8c", "node": "plastic#d9d9d4"})
# white square-tube floor frame, U-shaped and rounded at the right end, black end caps at the left
T = 40
d.add("rail", "sweep", "frame", path=[[230, 20, 70], [740, 20, 70], [740, 20, 410], [230, 20, 410]], section=[T, T], shape="rect", r=4, bend=60)
d.box("cap", [222, 0, 50, 232, 40, 90], "cap", r=3, copies=[[0, 0, 340]])
d.box("cross-1", [300, 2, 70, 340, 38, 410], "frame", r=4)
d.box("cross-2", [430, 2, 70, 470, 38, 410], "frame", r=4)
# blue padded platform on the right half
d.box("platform", [470, 40, 85, 720, 75, 395], "blue", r=14, puff=4)
# base plate and the white square column; motor head on top
d.box("plate", [330, 38, 190, 440, 46, 290], "frame", r=6)
d.box("column", [350, 46, 205, 420, 1060, 275], "frame", r=6)
d.box("bracket", [340, 1050, 200, 430, 1075, 300], "frame", r=6)
d.lathe("motor", [255, 1140, 290], [[0, 0], [40, 0], [62, 8], [72, 30], [74, 260], [62, 252], [40, 260], [0, 260]], "motor", axis="x")
d.lathe("drum", [320, 1140, 290], [[76, 0], [77, 4], [77, 126], [76, 130], [0, 130], [0, 0], [76, 0]], "drum", axis="x")
# white handlebars from the head out to both sides and forward, blue grips
d.tube("bar", [[360, 1065, 250], [200, 1100, 260], [140, 1130, 330], [140, 1135, 400]], 30, "frame", bend=70, mirror="x")
d.cyl("grip", [140, 1135, 380], [140, 1138, 478], 40, "dblue", mirror="x")
# belt: webbing from the drum down to the front in a V, massage nodules at the bottom, chrome springs
for i, x in enumerate((330, 440)):
    d.add(f"belt-{i}", "strap", "belt", path=[[x, 1080, 360], [x, 900, 390], [x + (40 if x < 385 else -40), 640, 450]],
          section=[60, 4], bend=60, soft=True)
    d.cyl(f"spring-{i}", [x + (-28 if x < 385 else 28), 1080, 345], [x + (12 if x < 385 else -12), 650, 450], 8, "chrome")
d.add("belt-loop", "strap", "belt", path=[[370, 640, 450], [385, 600, 470], [400, 640, 450]], section=[60, 4], bend=30, soft=True)
d.box("pad", [340, 590, 445, 430, 680, 470], "node", r=10)
d.sphere("node", [352, 605, 470], 14, "node", copies=[[22 * i, 20 * j, 0] for i in range(4) for j in range(4) if i + j > 0])
# blue twist disc on a short black post in front of the left end
d.cyl("disc-post", [150, 0, 380], [150, 40, 380], 30, "cap")
d.lathe("disc", [150, 40, 380], [[0, 0], [150, 0], [150, 18], [140, 24], [0, 24]], "dblue")
d.bar("disc-arm", [150, 20, 380], [235, 20, 380], [36, 36], "frame", r=4)
d.save()
