"""Trace the Cascade Labs mark as tapered ribbons.

Coordinates are in the 1536x1024 space of brand/cascade-mark-source.webp. Each ribbon is a
tip, the direction it leaves the tip in, and optionally a neck point where it joins the
bundle; every ribbon ends at the shared pivot. Run with --overlay to draw the trace over the
original for checking:

    python -I tools/ribbons.py --overlay brand/cascade-mark-source.webp overlay.png

build-assets.py turns the same ribbons into the site's SVG.
"""
import json, math, sys

P = (1021.0, 933.0)               # the shared point the ribbons fan from
TRUNK = (0.794, 0.607)            # direction into the pivot along the bundle

# tip centre, slope near the tip as dx/dy (moving towards the pivot), neck point or None,
# tip colour, how hard it leaves the tip (a), how hard it enters the neck (b)
R = [
    ((1126, 172), -1.575, (694, 505), "#4f1afd", 420, 95),
    ((1001, 113), -0.95,  (686, 510), "#6128fd", 360, 100),
    ((855, 89),   -0.50,  (677, 516), "#9862fd", 300, 105),
    ((724, 135),  -0.21,  (668, 520), "#c99cfb", 220, 105),
    ((620, 209),   0.06,  (662, 545), "#ddbbfd", 190, 95),
    ((536, 297),   0.42,  (668, 590), "#debdfc", 150, 80),
    ((471, 385),   0.76,  None,       "#a36cfc", 0, 0),
    ((420, 479),   1.30,  None,       "#854afb", 0, 0),
    ((392, 580),   1.82,  None,       "#4f22fc", 0, 0),
    ((381, 680),   2.62,  None,       "#3d17d5", 0, 0),
    ((400, 777),   4.10,  None,       "#350ec6", 0, 0),
]
W_TIP, W_END = 34.0, 3.0


def unit(x, y):
    l = math.hypot(x, y)
    return (x / l, y / l)


def cubic(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        m = 1 - t
        out.append((m * m * m * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t * t * t * p3[0],
                    m * m * m * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t * t * t * p3[1]))
    return out


def centerline(tip, slope, neck, a, b):
    u = unit(slope, 1.0)
    if neck is None:
        # Straight wedge into the pivot, bowed a touch towards the trunk.
        d = math.dist(tip, P)
        w = unit(P[0] - tip[0], P[1] - tip[1])
        c1 = (tip[0] + u[0] * d * 0.33, tip[1] + u[1] * d * 0.33)
        c2 = (P[0] - w[0] * d * 0.33, P[1] - w[1] * d * 0.33)
        return cubic(tip, c1, c2, P, 60)
    v = unit(0.42, 1.0)  # heading through the neck: down, leaning right
    seg1 = cubic(tip, (tip[0] + u[0] * a, tip[1] + u[1] * a), (neck[0] - v[0] * b, neck[1] - v[1] * b), neck, 40)
    d2 = math.dist(neck, P)
    seg2 = cubic(neck, (neck[0] + v[0] * d2 * 0.35, neck[1] + v[1] * d2 * 0.35),
                 (P[0] - TRUNK[0] * d2 * 0.4, P[1] - TRUNK[1] * d2 * 0.4), P, 40)
    return seg1 + seg2[1:]


def ribbon(pts, necked=False):
    # arc-length fractions
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    total = L[-1]
    left, right = [], []
    for i, p in enumerate(pts):
        q0 = pts[max(i - 1, 0)]
        q1 = pts[min(i + 1, len(pts) - 1)]
        tx, ty = unit(q1[0] - q0[0], q1[1] - q0[1])
        nx, ny = -ty, tx
        s = L[i] / total
        w = (W_TIP * (1 - s) ** (0.5 if necked else 0.85) + W_END * s) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    poly = left + right[::-1]
    return poly, total


def path_d(poly, k=1.0, ox=0.0, oy=0.0):
    f = lambda v: ("%.1f" % v).rstrip("0").rstrip(".")
    pts = ["%s %s" % (f(x * k + ox), f(y * k + oy)) for x, y in poly]
    return "M" + "L".join(pts) + "Z"


def build():
    out = []
    for tip, slope, neck, col, a, b in R:
        pts = centerline(tip, slope, neck, a, b)
        poly, total = ribbon(pts, neck is not None)
        out.append({"tip": tip, "color": col, "poly": poly, "len": total})
    return out


if __name__ == "__main__":
    rs = build()
    if "--overlay" in sys.argv:
        from PIL import Image, ImageDraw
        src, dst = sys.argv[2], sys.argv[3]
        base = Image.open(src).convert("RGBA")
        lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        for r in rs:
            dr.line([(x, y) for x, y in r["poly"]] + [r["poly"][0]], fill=(0, 200, 90, 255), width=2)
        Image.alpha_composite(base, lay).crop((330, 50, 1180, 960)).save(dst)
    if "--json" in sys.argv:
        print(json.dumps([{"d": path_d(r["poly"]), "c": r["color"], "tip": r["tip"]} for r in rs]))
