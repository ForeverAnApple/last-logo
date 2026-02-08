import math
import svgwrite

from icon import SIDE, cube_verts, cube_hexagon, cube_edges, l_shape
from icon import iso as cube_iso
from wordmark import make_text, STROKE_W


def draw_cube(dwg, cx, cy, fg="black", bg="white"):
    """Draw the cube icon shifted by (cx, cy)."""
    v = cube_verts(SIDE)
    hexagon = cube_hexagon(v)
    edges = cube_edges(v)
    faces = l_shape(SIDE)

    def shift(pt):
        return (pt[0] + cx, pt[1] + cy)

    # Filled cube background
    dwg.add(dwg.polygon([shift(p) for p in hexagon], fill=bg, stroke="none"))

    # Colored regions
    s = SIDE
    hw = s / 6
    color = "#5A9EA3"

    top_right = [
        cube_iso(0, 0, s),
        cube_iso(s, 0, s),
        cube_iso(s, s / 2 - hw, s),
        cube_iso(0, s / 2 - hw, s),
    ]
    left_square = [
        cube_iso(0, 0, s),
        cube_iso(0, s / 2 - hw, s),
        cube_iso(0, s / 2 - hw, s / 2 + hw),
        cube_iso(0, 0, s / 2 + hw),
    ]
    right_top = [
        cube_iso(0, 0, s),
        cube_iso(s, 0, s),
        cube_iso(s, 0, s / 2 + hw),
        cube_iso(0, 0, s / 2 + hw),
    ]

    for region in [top_right, left_square, right_top]:
        dwg.add(dwg.polygon([shift(p) for p in region], fill=color, stroke="none"))

    # L shape faces
    for face in faces:
        dwg.add(dwg.polygon([shift(p) for p in face], fill=fg, stroke="none"))

    # Wireframe
    for start, end in edges:
        dwg.add(
            dwg.line(
                start=shift(start),
                end=shift(end),
                stroke=fg,
                stroke_width=6,
                stroke_linecap="round",
            )
        )


def draw_text(dwg, cx, cy, fg="black", bg="white", **text_kw):
    """Draw the LAST text shifted by (cx, cy)."""
    letters = make_text(**text_kw)

    def shift(pt):
        return (pt[0] + cx, pt[1] + cy)

    for letter_bars, restore_edges in letters:
        # First pass: draw bars with occlusion masking
        prev_fronts = []
        for faces, edges in letter_bars:
            left, top, front = faces

            for face in (left, top):
                dwg.add(dwg.polygon([shift(p) for p in face], fill=bg, stroke="none"))

            for pf in prev_fronts:
                dwg.add(dwg.polygon([shift(p) for p in pf], fill=fg, stroke="none"))

            dwg.add(dwg.polygon([shift(p) for p in front], fill=fg, stroke="none"))

            for s, e in edges:
                dwg.add(
                    dwg.line(
                        start=shift(s),
                        end=shift(e),
                        stroke=fg,
                        stroke_width=STROKE_W,
                        stroke_linecap="round",
                    )
                )
            prev_fronts.append(front)

        # Cleanup pass: re-draw faces to mask stray edge bleed-through
        prev_fronts = []
        for faces, _ in letter_bars:
            left, top, front = faces
            for face in (left, top):
                dwg.add(dwg.polygon([shift(p) for p in face], fill=bg, stroke="none"))
            for pf in prev_fronts:
                dwg.add(dwg.polygon([shift(p) for p in pf], fill=fg, stroke="none"))
            dwg.add(dwg.polygon([shift(p) for p in front], fill=fg, stroke="none"))
            prev_fronts.append(front)

        # Restore specific edges erased by the cleanup
        _, last_edges = letter_bars[-1]
        for i, s_inset, e_inset in restore_edges:
            s, e = last_edges[i]
            if s_inset or e_inset:
                dx, dy = e[0] - s[0], e[1] - s[1]
                length = math.hypot(dx, dy)
                nx, ny = dx / length, dy / length
                s = (s[0] + nx * s_inset, s[1] + ny * s_inset)
                e = (e[0] - nx * e_inset, e[1] - ny * e_inset)
            dwg.add(
                dwg.line(
                    start=shift(s),
                    end=shift(e),
                    stroke=fg,
                    stroke_width=STROKE_W,
                    stroke_linecap="round",
                )
            )


def get_cube_bounds():
    """Bounding box (x_min, y_min, x_max, y_max) of the cube."""
    v = cube_verts(SIDE)
    hexagon = cube_hexagon(v)
    pad = 6 / 2  # half of wireframe stroke_width
    xs = [p[0] for p in hexagon]
    ys = [p[1] for p in hexagon]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def get_text_bounds(**text_kw):
    """Bounding box (x_min, y_min, x_max, y_max) of the text."""
    letters = make_text(**text_kw)
    all_pts = []
    for letter_bars, _ in letters:
        for faces, _ in letter_bars:
            for face in faces:
                all_pts += face
    pad = STROKE_W / 2 + 1
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def main():
    # Cube geometry height (no padding)
    v = cube_verts(SIDE)
    hexagon = cube_hexagon(v)
    cube_ys = [p[1] for p in hexagon]
    cube_geo_h = max(cube_ys) - min(cube_ys)

    # Default text geometry height (no padding)
    default_letters = make_text()
    all_pts = []
    for letter_bars, _ in default_letters:
        for faces, _ in letter_bars:
            for face in faces:
                all_pts += face
    text_ys = [p[1] for p in all_pts]
    text_geo_h = max(text_ys) - min(text_ys)

    # Scale text params so letter height matches cube height
    scale = cube_geo_h / text_geo_h
    text_kw = dict(
        w=50 * scale, h=70 * scale, bw=15 * scale, gap=25 * scale, d=15 * scale
    )

    cb = get_cube_bounds()
    tb = get_text_bounds(**text_kw)

    cube_w = cb[2] - cb[0]
    cube_h = cb[3] - cb[1]
    text_w = tb[2] - tb[0]
    text_h = tb[3] - tb[1]

    gap = 30
    total_w = cube_w + gap + text_w
    max_h = max(cube_h, text_h)

    # Shared offsets
    cube_cx = -cb[0]
    cube_cy = -cb[1] + (max_h - cube_h) / 2
    text_cx = cube_w + gap - tb[0]
    text_cy = -tb[1] + (max_h - text_h) / 2

    for filename, fg, bg in [
        ("logo-light.svg", "black", "white"),
        ("logo-dark.svg", "white", "black"),
    ]:
        dwg = svgwrite.Drawing(filename, size=(total_w, max_h))
        draw_cube(dwg, cube_cx, cube_cy, fg=fg, bg=bg)
        draw_text(dwg, text_cx, text_cy, fg=fg, bg=bg, **text_kw)
        dwg.save()
        print(f"Saved {filename} ({total_w:.0f}x{max_h:.0f})")


if __name__ == "__main__":
    main()
