import math
import svgwrite

ANG = math.radians(30)
IX = (math.cos(ANG), -math.sin(ANG))
IY = (-math.cos(ANG), -math.sin(ANG))
IZ = (0, -1)

STROKE_W = 6


def iso(x, y, z):
    """Project (x, y, z) into 2D isometric coordinates."""
    px = x * IX[0] + y * IY[0] + z * IZ[0]
    py = x * IX[1] + y * IY[1] + z * IZ[1]
    return (px, py)


def bar(x0, z0, x1, z1, d):
    """Faces and edges of a cuboid bar.

    Returns (faces, edges) where:
      faces: [left, top, front] polygons for the 3 visible faces.
      edges: 9 visible edge segments (6 outline + 3 internal).
    """
    fbl, fbr = iso(x0, 0, z0), iso(x1, 0, z0)
    bbl = iso(x0, d, z0)
    ftl, ftr = iso(x0, 0, z1), iso(x1, 0, z1)
    btl, btr = iso(x0, d, z1), iso(x1, d, z1)

    faces = [
        [ftl, btl, bbl, fbl],  # left face (x=x0 plane)
        [ftl, ftr, btr, btl],  # top face (z=z1 plane)
        [ftl, ftr, fbr, fbl],  # front face (y=0 plane)
    ]
    edges = [
        (btr, ftr),
        (ftr, fbr),
        (fbr, fbl),
        (fbl, bbl),
        (bbl, btl),
        (btl, btr),
        (ftl, fbl),
        (ftl, ftr),
        (ftl, btl),
    ]
    return faces, edges


def letter_L(ox, oz, w, h, bw, d):
    # Extend height so the narrow vertical bar's top projects to the same
    # iso height as the wide top bars on A/S/T.
    h_ext = h + math.sin(ANG) * (w - bw)
    bars = [
        bar(ox, oz, ox + w, oz + bw, d),  # bottom horizontal
        bar(ox, oz + bw, ox + bw, oz + h_ext, d),  # vertical (no overlap)
    ]
    k = STROKE_W * 0.75
    return bars, [(1, k, 0)]  # right side: inset top only, bottom is black


def letter_A(ox, oz, w, h, bw, d):
    mid = oz + h / 2 - bw / 2
    bars = [
        bar(ox + w - bw, oz, ox + w, oz + h, d),  # right pillar first
        bar(ox, oz + h - bw, ox + w, oz + h, d),  # top bar
        bar(ox, mid, ox + w, mid + bw, d),  # middle bar
        bar(ox, oz, ox + bw, oz + h, d),  # left pillar last
    ]
    k = STROKE_W * 0.75
    return bars, [(1, k, k)]  # right side


def letter_S(ox, oz, w, h, bw, d):
    mid = oz + h / 2 - bw / 2
    bars = [
        bar(ox, oz, ox + w, oz + bw, d),  # bottom horizontal
        bar(ox + w - bw, oz + bw, ox + w, mid, d),  # square above (right)
        bar(ox, mid, ox + w, mid + bw, d),  # middle horizontal
        bar(ox, mid + bw, ox + bw, oz + h - bw, d),  # square above (left)
        bar(ox, oz + h - bw, ox + w, oz + h, d),  # top horizontal
    ]
    k = STROKE_W * 0.75
    return bars, [(2, k, k)]  # bottom


def letter_T(ox, oz, w, h, bw, d):
    cx = ox + w / 2 - bw / 2
    # Extend stem downward so the centered narrow bar's bottom projects
    # to the same iso depth as full-width bottom bars on L/A/S.
    z_ext = math.sin(ANG) * (w - bw) / 2
    bars = [
        bar(cx, oz - z_ext, cx + bw, oz + h - bw, d),  # vertical stem first
        bar(ox, oz + h - bw, ox + w, oz + h, d),  # top bar second
    ]
    return bars, [(1, 0, 0), (2, 0, 0), (6, 0, 0), (7, 0, 0)]


def make_text(w=50, h=70, bw=15, gap=25, d=15):
    """Return (bars, restore_edges) per letter for independent occlusion."""
    stride = w + gap
    letters = []
    for i, fn in enumerate([letter_L, letter_A, letter_S, letter_T]):
        ox = i * stride
        oz = -ox * math.sin(ANG)
        letters.append(fn(ox, oz, w, h, bw, d))
    return letters


def main():
    letters = make_text()

    # Compute tight bounding box from all geometry
    all_pts = []
    for letter_bars, _ in letters:
        for faces, edges in letter_bars:
            for face in faces:
                all_pts += face
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]

    pad = STROKE_W / 2 + 1  # half stroke + tiny margin
    x_min, x_max = min(xs) - pad, max(xs) + pad
    y_min, y_max = min(ys) - pad, max(ys) + pad
    cw = x_max - x_min
    ch = y_max - y_min

    dwg = svgwrite.Drawing("wordmark.svg", size=(cw, ch))

    def shift(pt):
        return (pt[0] - x_min, pt[1] - y_min)

    # Draw each letter independently.
    # Per bar: white faces mask previous bars' edges, then re-draw all
    # previous front faces so the white never erases black (additive).
    for letter_bars, restore_edges in letters:
        prev_fronts = []

        for faces, edges in letter_bars:
            left, top, front = faces

            # 1. White top/left faces — mask previous bars' edges
            for face in (left, top):
                dwg.add(
                    dwg.polygon([shift(p) for p in face], fill="white", stroke="none")
                )

            # 2. Re-draw all previous front faces — restore black the white just erased
            for pf in prev_fronts:
                dwg.add(
                    dwg.polygon([shift(p) for p in pf], fill="black", stroke="none")
                )

            # 3. This bar's front face
            dwg.add(dwg.polygon([shift(p) for p in front], fill="black", stroke="none"))

            # 4. This bar's edges
            for s, e in edges:
                dwg.add(
                    dwg.line(
                        start=shift(s),
                        end=shift(e),
                        stroke="black",
                        stroke_width=STROKE_W,
                        stroke_linecap="round",
                    )
                )

            prev_fronts.append(front)

        # Cleanup pass: re-draw all faces to mask stray edges from later bars
        # whose edges bled through earlier bars' white faces.
        prev_fronts = []
        for faces, _ in letter_bars:
            left, top, front = faces
            for face in (left, top):
                dwg.add(
                    dwg.polygon([shift(p) for p in face], fill="white", stroke="none")
                )
            for pf in prev_fronts:
                dwg.add(
                    dwg.polygon([shift(p) for p in pf], fill="black", stroke="none")
                )
            dwg.add(dwg.polygon([shift(p) for p in front], fill="black", stroke="none"))
            prev_fronts.append(front)

        # Restore specific front-face edges of the last bar. The cleanup's
        # white faces can erase edges at shared boundaries. Only re-draw
        # edges that don't share a boundary with a previous bar — shared
        # edges are already correctly rendered by the cleanup.
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
                    stroke="black",
                    stroke_width=STROKE_W,
                    stroke_linecap="round",
                )
            )

    dwg.save()
    print(f"Saved wordmark.svg ({cw}x{ch})")


if __name__ == "__main__":
    main()
