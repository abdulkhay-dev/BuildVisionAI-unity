"""xyrt-29 — tumbling barrel: hollow soft cylinder lying along x, nine PVC bands Y/B/R ×3, white seams."""
from pd3_lib import *

W, Dp, H = 760, 600, 600
d = D("xyrt-29", [W, Dp, H], {"y": "leather#f5d020", "b": "leather#1f4fb5", "r": "leather#e02424",
                              "white": "leather#f4f4f0"})
R, Ri = 300, 190
cy = cz = 300
n = 9
bw = W / n
# white core showing in the seams
d.lathe("core", [0, cy, cz], [[Ri + 6, 6], [R - 6, 6], [R - 6, W - 6], [Ri + 6, W - 6], [Ri + 6, 6]], "white",
        axis="x", caps=False, sides=48)
e = 5  # rounded band edge
prof = [[Ri, 0], [R - e, 0], [R - 2, 2.5], [R, e], [R, bw - e], [R - 2, bw - 2.5], [R - e, bw],
        [Ri, bw], [Ri - 0.01, bw * 0.5], [Ri, 0]]
for k, c in enumerate(["y", "b", "r"]):
    d.lathe(f"band-{c}", [k * bw + 2.5, cy, cz], [[p[0], p[1] - 5 if p[1] > bw / 2 else p[1]] for p in prof], c,
            axis="x", caps=False, sides=48, repeat={"n": 3, "step": [3 * bw, 0, 0]})
# white piping between the bands (photo: crisp white lines), outside and in the bore
d.lathe("pipe", [bw - 3, cy, cz], [[R - 6, 0], [R + 0.5, 0], [R + 1.5, 3], [R + 0.5, 6], [R - 6, 6], [R - 6, 0]], "white",
        axis="x", caps=False, sides=48, repeat={"n": n - 1, "step": [bw, 0, 0]})
d.lathe("pipe-in", [bw - 3, cy, cz], [[Ri + 6, 0], [Ri - 0.5, 0], [Ri - 1.5, 3], [Ri - 0.5, 6], [Ri + 6, 6], [Ri + 6, 0]],
        "white", axis="x", caps=False, sides=48, repeat={"n": n - 1, "step": [bw, 0, 0]})
d.save()
