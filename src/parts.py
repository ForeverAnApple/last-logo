import math
from pathlib import Path

import svgwrite

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

SIDE = 100
ANG = math.radians(30)
IX = (math.cos(ANG), -math.sin(ANG))
IY = (-math.cos(ANG), -math.sin(ANG))
IZ = (0, -1)


def iso(x, y, z):
    px = x * IX[0] + y * IY[0] + z * IZ[0]
    py = x * IX[1] + y * IY[1] + z * IZ[1]
    return (px, py)


def main():
    s = SIDE
    hw = s / 6

    # Same coordinate system as icon.py
    hexagon = [
        iso(s, s, s),
        iso(s, 0, s),
        iso(s, 0, 0),
        iso(0, 0, 0),
        iso(0, s, 0),
        iso(0, s, s),
    ]
    pad = 6 / 2
    xs = [p[0] for p in hexagon]
    ys = [p[1] for p in hexagon]
    cx = -min(xs) + pad
    cy = -min(ys) + pad
    w = max(xs) - min(xs) + 6
    h = max(ys) - min(ys) + 6

    def shift(pt):
        return (pt[0] + cx, pt[1] + cy)

    stroke_opts = dict(stroke="black", stroke_width=6, stroke_linecap="round")

    # ── Key vertices ─────────────────────────────────────────────
    ftl = iso(0, 0, s)
    ftr = iso(s, 0, s)
    fbr = iso(s, 0, 0)
    fbl = iso(0, 0, 0)
    bbl = iso(0, s, 0)
    btl = iso(0, s, s)
    btr = iso(s, s, s)

    # Boundary points (where color regions meet)
    ti = iso(s, s / 2 - hw, s)  # top inner, on btr→ftr
    to = iso(s, s / 2 + hw, s)  # top outer
    li = iso(0, s / 2 - hw, s)  # left-top inner
    lo = iso(0, s / 2 + hw, s)  # left-top outer
    ri = iso(s, 0, s / 2 + hw)  # right inner, on ftr→fbr
    ro = iso(s, 0, s / 2 - hw)  # right outer
    fi = iso(0, 0, s / 2 + hw)  # left-right junction inner
    fo = iso(0, 0, s / 2 - hw)  # left-right junction outer
    ci = iso(0, s / 2 - hw, s / 2 + hw)  # L-elbow inner corner
    co = iso(0, s / 2 + hw, s / 2 - hw)  # L-elbow outer corner

    # Back depth points (at x=s, showing volume)
    bci = iso(s, s / 2 - hw, s / 2 + hw)  # back inner L-corner
    bco = iso(s, s / 2 + hw, s / 2 - hw)  # back outer L-corner

    # ── Flat parts (2D, single polygon + stroke) ─────────────────
    flat_shapes = [
        (
            "part-teal.svg",
            [ftr, ti, li, ci, fi, ri],
            "#5A9EA3",
        ),
        (
            "part-black.svg",
            [to, ti, li, ci, fi, ri, ro, fo, co, lo],
            "black",
        ),
        (
            "part-white.svg",
            [btr, to, lo, co, fo, ro, fbr, fbl, bbl, btl],
            "white",
        ),
    ]

    stroke_flat = dict(stroke="black", stroke_width=6, stroke_linejoin="round")
    for filename, points, fill in flat_shapes:
        dwg = svgwrite.Drawing(str(OUTPUT_DIR / filename), size=(w, h))
        dwg.add(dwg.polygon([shift(p) for p in points], fill=fill, **stroke_flat))
        dwg.save()
        print(f"Saved {filename} ({w:.0f}x{h:.0f})")

    # ── 3D parts (isometric volumes with face shading + wireframe) ─

    # Face shading: top=lightest, right/front=mid, left=darkest
    TEAL = {"top": "#6CB5BA", "right": "#5A9EA3", "left": "#487E82"}
    BLACK = {"top": "#3D3D3D", "right": "#262626", "left": "#151515"}
    WHITE = {"top": "#FFFFFF", "right": "#DCDCDC", "left": "#B8B8B8"}

    def draw_3d(filename, faces, edges):
        dwg = svgwrite.Drawing(str(OUTPUT_DIR / filename), size=(w, h))
        for verts, color in faces:
            dwg.add(dwg.polygon([shift(p) for p in verts], fill=color, stroke="none"))
        for a, b in edges:
            dwg.add(dwg.line(start=shift(a), end=shift(b), **stroke_opts))
        dwg.save()
        print(f"Saved {filename} ({w:.0f}x{h:.0f})")

    # ── TEAL 3D (mini isometric box) ─────────────────────────────
    draw_3d(
        "part-teal-3d.svg",
        faces=[
            ([ftl, li, ci, fi], TEAL["left"]),
            ([ftl, ftr, ri, fi], TEAL["right"]),
            ([ftl, ftr, ti, li], TEAL["top"]),
        ],
        edges=[
            # 3 internal edges from front vertex ftl
            (ftl, ftr),
            (ftl, li),
            (ftl, fi),
            # Top face back edges
            (ftr, ti),
            (ti, li),
            # Right face bottom edges
            (ftr, ri),
            (ri, fi),
            # Left face inner edges
            (li, ci),
            (ci, fi),
        ],
    )

    # ── BLACK L 3D ───────────────────────────────────────────────
    draw_3d(
        "part-black-3d.svg",
        faces=[
            # Left face (L-shaped elbow)
            ([lo, li, ci, fi, fo, co], BLACK["left"]),
            # Front cut face (inside teal notch, faces toward viewer like right)
            ([li, ti, bci, ci], BLACK["right"]),
            # Interior top cut face (floor of teal notch)
            ([ci, bci, ri, fi], BLACK["top"]),
            # Right face
            ([fi, ri, ro, fo], BLACK["right"]),
            # Top face
            ([ti, to, lo, li], BLACK["top"]),
        ],
        edges=[
            # Left face outline
            (lo, li),
            (li, ci),
            (ci, fi),
            (fi, fo),
            (fo, co),
            (co, lo),
            # Top face → back
            (li, ti),
            (lo, to),
            (ti, to),
            # Right face → back
            (fi, ri),
            (fo, ro),
            (ri, ro),
            # Back depth: inner L-corner
            (ti, bci),
            (bci, ri),
            # Back depth: outer L-corner
            (to, bco),
            (bco, ro),
        ],
    )

    # ── WHITE L 3D ───────────────────────────────────────────────
    draw_3d(
        "part-white-3d.svg",
        faces=[
            # Left face (L-shaped)
            ([btl, lo, co, fo, fbl, bbl], WHITE["left"]),
            # Interior right cut face (inside black notch)
            ([lo, to, bco, co], WHITE["right"]),
            # Interior top cut face (floor of black notch)
            ([co, bco, ro, fo], WHITE["top"]),
            # Right face
            ([fo, ro, fbr, fbl], WHITE["right"]),
            # Top face
            ([btr, to, lo, btl], WHITE["top"]),
        ],
        edges=[
            # Left face outline
            (btl, lo),
            (lo, co),
            (co, fo),
            (fo, fbl),
            (fbl, bbl),
            (bbl, btl),
            # Top face → back
            (btl, btr),
            (lo, to),
            (btr, to),
            # Right face → back
            (fbl, fbr),
            (fo, ro),
            (fbr, ro),
            # Back depth: outer L-corner
            (to, bco),
            (bco, ro),
        ],
    )


if __name__ == "__main__":
    main()
