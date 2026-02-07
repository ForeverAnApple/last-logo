import math
import svgwrite

SIDE = 100
# Isometric axes: 30° from horizontal
ANG = math.radians(30)
IX = (math.cos(ANG), -math.sin(ANG))  # x-axis projects right and up
IY = (-math.cos(ANG), -math.sin(ANG))  # y-axis projects left and up
IZ = (0, -1)  # z-axis projects straight up


def iso(x, y, z):
    """Project (x, y, z) into 2D isometric coordinates."""
    px = x * IX[0] + y * IY[0] + z * IZ[0]
    py = x * IX[1] + y * IY[1] + z * IZ[1]
    return (px, py)


def cube_edges(s):
    """Return the 9 visible edges of an isometric cube as (start, end) pairs."""
    v = {
        "fbl": iso(0, 0, 0),
        "fbr": iso(s, 0, 0),
        "bbl": iso(0, s, 0),
        "ftl": iso(0, 0, s),
        "ftr": iso(s, 0, s),
        "btl": iso(0, s, s),
        "btr": iso(s, s, s),
    }
    return [
        # # Hexagon outline
        # (v["btr"], v["ftr"]),
        # (v["ftr"], v["fbr"]),
        # (v["fbr"], v["fbl"]),
        # (v["fbl"], v["bbl"]),
        # (v["bbl"], v["btl"]),
        # (v["btl"], v["btr"]),
        # # 3 internal edges from center
        # (v["ftl"], v["fbl"]),
        # (v["ftl"], v["ftr"]),
        # (v["ftl"], v["btl"]),
    ]


def l_shape(s):
    """Build the L as 3 face polygons with chop lines on top and right faces.

    Each face's bar segment is a separate polygon so they're easy to style
    independently.  Chop lines run along the bar length, splitting its width
    into 3 equal strips on the top and right faces.
    """
    hw = s / 6  # half-width → total bar width = s/3
    bx = s * 2 / 3  # bar extent along x-axis on top / right faces

    # ── Top face (z=s plane) ─────────────────────────────────────────
    top = [
        iso(bx, s / 2 + hw, s),
        iso(0, s / 2 + hw, s),
        iso(0, s / 2 - hw, s),
        iso(bx, s / 2 - hw, s),
    ]
    # lines run along x (the bar length), at 1/3 and 2/3 of the width
    # top_chops = [
    #     (iso(bx, s / 2 - hw / 3, s), iso(0, s / 2 - hw / 3, s)),
    #     (iso(bx, s / 2 + hw / 3, s), iso(0, s / 2 + hw / 3, s)),
    # ]

    # ── Left face (x=0 plane) — the L-shaped elbow, no chop lines ───
    left = [
        iso(0, s / 2 + hw, s),  # top outer
        iso(0, s / 2 - hw, s),  # top inner
        iso(0, s / 2 - hw, s / 2 + hw),  # inner corner of L
        iso(0, 0, s / 2 + hw),  # bottom-right outer
        iso(0, 0, s / 2 - hw),  # bottom-right inner
        iso(0, s / 2 + hw, s / 2 - hw),  # bottom-left outer
    ]

    # ── Right face (y=0 plane) ───────────────────────────────────────
    right = [
        iso(0, 0, s / 2 + hw),
        iso(bx, 0, s / 2 + hw),
        iso(bx, 0, s / 2 - hw),
        iso(0, 0, s / 2 - hw),
    ]
    # lines run along x (the bar length), at 1/3 and 2/3 of the width
    # right_chops = [
    #     (iso(0, 0, s / 2 - hw / 3), iso(bx, 0, s / 2 - hw / 3)),
    #     (iso(0, 0, s / 2 + hw / 3), iso(bx, 0, s / 2 + hw / 3)),
    # ]

    return {
        "faces": [top, left, right],
        # "chops": top_chops + right_chops,
    }


def main():
    w, h = 300, 300
    dwg = svgwrite.Drawing("cube.svg", size=(w, h))

    edges = cube_edges(SIDE)
    shape = l_shape(SIDE)

    all_pts = [p for edge in edges for p in edge]
    for face in shape["faces"]:
        all_pts += face
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    cx = w / 2 - (min(xs) + max(xs)) / 2
    cy = h / 2 - (min(ys) + max(ys)) / 2

    # L shape — one polygon per face
    for face in shape["faces"]:
        shifted = [(x + cx, y + cy) for x, y in face]
        dwg.add(dwg.polygon(shifted, fill="black", stroke="none"))

    # Chop lines — split top and right face bars into 3 strips along length
    # for start, end in shape["chops"]:
    #     dwg.add(
    #         dwg.line(
    #             start=(start[0] + cx, start[1] + cy),
    #             end=(end[0] + cx, end[1] + cy),
    #             stroke="white",
    #             stroke_width=2,
    #         )
    #     )

    # Cube wireframe on top
    for start, end in edges:
        dwg.add(
            dwg.line(
                start=(start[0] + cx, start[1] + cy),
                end=(end[0] + cx, end[1] + cy),
                stroke="black",
                stroke_width=6,
                stroke_linecap="round",
            )
        )

    dwg.save()
    print(f"Saved cube.svg ({w}x{h})")


if __name__ == "__main__":
    main()
