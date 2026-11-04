"""Original abstract SVG artwork for the SeaBrick website.

Every brick drawn here is a plain hexagonal prism of roughly brick-like proportions.
No connector, knob, groove, hinge or cavity geometry from the real design is used.
Run:  python src/artwork.py   (writes dist/assets/art/*.svg)
"""
import math, os, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "dist" / "assets" / "art"
OUT.mkdir(parents=True, exist_ok=True)

# palette
OCEAN = "#005492"; OCEAN_DEEP = "#0A3358"; SEA = "#52B09F"; SEA_DARK = "#2F8A7B"
TOP = "#F4EEE2"; SIDE_L = "#D9CFBE"; SIDE_R = "#C2B59F"; EDGE = "#6B5F4F"
TOP_B = "#DCEAF3"; SIDE_LB = "#9EC0D6"; SIDE_RB = "#6F9DBB"; EDGE_B = "#2B4D6B"
WATER = "#CFE4EE"; WATER_LINE = "#8FB8CF"

COS30 = math.cos(math.radians(30)); SIN30 = 0.5


def iso(x, y, z, s=1.0):
    """isometric projection: world (x,y,z) -> screen (sx, sy). Camera from +x,+y,+z."""
    return ((x - y) * COS30 * s, (x + y) * SIN30 * s - z * s)


def hex_pts(cx, cy, R, flat=True):
    off = 0 if flat else 30
    return [(cx + R * math.cos(math.radians(off + 60 * i)), cy + R * math.sin(math.radians(off + 60 * i))) for i in range(6)]


def fmt(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def prism(cx, cy, z0, h, R, s, ox, oy, pal=None, flat=True, stroke_w=0.9, opacity=1.0):
    """Return SVG for one hexagonal prism at world centre (cx,cy), base z0, height h."""
    top, sl, sr, edge = pal or (TOP, SIDE_L, SIDE_R, EDGE)
    base = hex_pts(cx, cy, R, flat)
    n = len(base)
    out = []
    # side faces: visible if outward normal has positive dot with (1,1)
    for i in range(n):
        (x1, y1), (x2, y2) = base[i], base[(i + 1) % n]
        mx, my = (x1 + x2) / 2 - cx, (y1 + y2) / 2 - cy
        if mx + my > 1e-6:
            p = [iso(x1, y1, z0, s), iso(x2, y2, z0, s), iso(x2, y2, z0 + h, s), iso(x1, y1, z0 + h, s)]
            # shade: faces facing +x lighter, +y darker
            col = sl if mx > my else sr
            out.append(f'<polygon points="{fmt([(px+ox, py+oy) for px, py in p])}" fill="{col}" stroke="{edge}" stroke-width="{stroke_w}" stroke-linejoin="round" opacity="{opacity}"/>')
    p = [iso(x, y, z0 + h, s) for x, y in base]
    out.append(f'<polygon points="{fmt([(px+ox, py+oy) for px, py in p])}" fill="{top}" stroke="{edge}" stroke-width="{stroke_w}" stroke-linejoin="round" opacity="{opacity}"/>')
    return "\n".join(out)


def hex_grid(cols, rows, R, flat=True):
    """centres of a close-packed hex grid."""
    pts = []
    if flat:
        dx, dy = 1.5 * R, math.sqrt(3) * R
        for c in range(cols):
            for r in range(rows):
                pts.append((c * dx, r * dy + (dy / 2 if c % 2 else 0)))
    else:
        dx, dy = math.sqrt(3) * R, 1.5 * R
        for r in range(rows):
            for c in range(cols):
                pts.append((c * dx + (dx / 2 if r % 2 else 0), r * dy))
    return pts


def draw_prisms(items, s, ox, oy, R, flat=True, pal=None, sw=0.9):
    """items: list of (cx, cy, z0, h[, pal]). Painter's order by depth."""
    items = sorted(items, key=lambda t: (t[2], t[0] + t[1]))
    return "\n".join(prism(it[0], it[1], it[2], it[3], R, s, ox, oy, (it[4] if len(it) > 4 else pal), flat, sw) for it in items)


def svg(w, h, body, bg=None):
    bgr = f'<rect width="{w}" height="{h}" fill="{bg}" rx="12"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">{bgr}{body}</svg>'


def waves(x0, x1, y, n=4, amp=4, step=14, col=WATER_LINE, op=0.8, w=1.2):
    out = []
    for k in range(n):
        yy = y + k * step
        d = f"M{x0},{yy} "
        seg = 40
        x = x0
        up = True
        while x < x1:
            d += f"q{seg/2},{-amp if up else amp} {seg},0 "
            x += seg
            up = not up
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" opacity="{op - k*0.15}" stroke-linecap="round"/>')
    return "\n".join(out)


def label(x, y, text, anchor="start", size=12, col=OCEAN_DEEP, weight=600, mono=False):
    fam = "Cascadia Code, Consolas, Menlo, monospace" if mono else "Segoe UI, Inter, system-ui, sans-serif"
    text = text.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{col}" text-anchor="{anchor}" letter-spacing="{0.08 if mono else 0}em">{text}</text>'


def leader(x1, y1, x2, y2, col=SEA_DARK):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="1.2" fill="none"/><circle cx="{x1}" cy="{y1}" r="2.5" fill="{col}"/>'


R = 1.0  # brick circumradius (world units)
H = 0.75  # brick height: a chunky hexagonal "paver" proportion

# ---------------------------------------------------------------- hero: a floating platform of hex bricks
def hero():
    s = 30
    cols, rows = 7, 5
    items = []
    for (x, y) in hex_grid(cols, rows, R):
        items.append((x, y, 0, H))
    # a raised second course on part of the mat + one brick hovering, about to lock in
    for (x, y) in hex_grid(3, 2, R):
        items.append((x + 3.0, y + 1.732 * 1.0, H, H))
    hover = (1.5, 1.732 * 2.5, 2.2, H)
    body = []
    ox, oy = 340, 215
    body.append(f'<defs><radialGradient id="sea" cx="50%" cy="55%" r="60%"><stop offset="0" stop-color="#E9F3F7"/><stop offset="1" stop-color="#CFE4EE"/></radialGradient></defs>')
    body.append(f'<ellipse cx="{ox+30}" cy="{oy+105}" rx="310" ry="125" fill="url(#sea)"/>')
    body.append(waves(ox-260, ox+330, oy+135, n=5, amp=5, step=18, op=0.9))
    # shadow under platform
    body.append(f'<ellipse cx="{ox+30}" cy="{oy+100}" rx="190" ry="62" fill="{OCEAN}" opacity="0.10"/>')
    body.append(draw_prisms(items, s, ox, oy, R))
    body.append(prism(hover[0], hover[1], hover[2], hover[3], R, s, ox, oy))
    hx, hy = iso(hover[0], hover[1], hover[2], s)
    body.append(f'<path d="M{ox+hx:.1f},{oy+hy+6:.1f} v26" stroke="{SEA_DARK}" stroke-width="2" stroke-dasharray="3 4" fill="none"/>')
    body.append(f'<path d="M{ox+hx-5:.1f},{oy+hy+26:.1f} l5,7 l5,-7" stroke="{SEA_DARK}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(label(ox-245, oy-150, "FLOATING PLATFORM · CONCEPT", size=11, col=SEA_DARK, mono=True))
    body.append(label(ox-245, oy-132, "Many small bricks, one large floating structure", size=12, col=OCEAN_DEEP, weight=500))
    return svg(720, 460, "\n".join(body))


# ---------------------------------------------------------------- the brick itself (single, with dimension hints)
def brick_single():
    s = 70
    ox, oy = 250, 160
    body = [prism(0, 0, 0, H, R, s, ox, oy, stroke_w=1.3)]
    a = iso(R, 0, H, s); b = iso(-R, 0, H, s)
    lift = 34
    body.append(f'<path d="M{ox+b[0]:.1f},{oy+b[1]-lift:.1f} L{ox+a[0]:.1f},{oy+a[1]-lift:.1f}" stroke="{SEA_DARK}" stroke-width="1.2"/>')
    for (px, py) in (a, b):
        body.append(f'<path d="M{ox+px:.1f},{oy+py-lift-5:.1f} v10" stroke="{SEA_DARK}" stroke-width="1.2"/>')
        body.append(f'<path d="M{ox+px:.1f},{oy+py-lift+6:.1f} L{ox+px:.1f},{oy+py-4:.1f}" stroke="{SEA_DARK}" stroke-width="0.8" stroke-dasharray="2 3"/>')
    body.append(label(ox+(a[0]+b[0])/2, oy+(a[1]+b[1])/2-lift-10, "width across corners", "middle", 11, SEA_DARK, mono=True))
    c = iso(R, 0, 0, s); d = iso(R, 0, H, s)
    gx = 26
    body.append(f'<path d="M{ox+c[0]+gx:.1f},{oy+c[1]:.1f} L{ox+d[0]+gx:.1f},{oy+d[1]:.1f}" stroke="{SEA_DARK}" stroke-width="1.2"/>')
    for (px, py) in (c, d):
        body.append(f'<path d="M{ox+px+gx-5:.1f},{oy+py:.1f} h10" stroke="{SEA_DARK}" stroke-width="1.2"/>')
    body.append(label(ox+c[0]+gx+10, oy+(c[1]+d[1])/2+4, "height ≈ ½ width", "start", 11, SEA_DARK, mono=True))
    body.append(label(ox, 290, "Simplified hexagonal brick. Connection features are intentionally omitted.", "middle", 11, "#5A6B7A", 500))
    return svg(500, 300, chr(10).join(body))


# ---------------------------------------------------------------- 1. interlocking bricks
def interlocking():
    s = 38; ox, oy = 300, 150
    centres = [(0, 0)] + [(1.5 * R * math.cos(math.radians(60 * i)) * 1.1547 * 1.0, 1.5 * R * math.sin(math.radians(60 * i)) * 1.1547) for i in range(6)]
    # neighbours of a flat-top hex sit at distance sqrt(3)*R at angles 30+60k
    centres = [(0, 0)] + [(math.sqrt(3) * R * math.cos(math.radians(30 + 60 * i)), math.sqrt(3) * R * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    items = [(x, y, 0, H) for (x, y) in centres[:-1]]
    body = [draw_prisms(items, s, ox, oy, R)]
    lx, ly = centres[-1]
    body.append(prism(lx, ly, 1.6, H, R, s, ox, oy))
    px, py = iso(lx, ly, 1.6, s)
    body.append(f'<path d="M{ox+px:.1f},{oy+py+4:.1f} v22" stroke="{SEA_DARK}" stroke-width="2" stroke-dasharray="3 4"/>')
    body.append(f'<path d="M{ox+px-5:.1f},{oy+py+22:.1f} l5,7 l5,-7" stroke="{SEA_DARK}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(label(20, 28, "01 · INTERLOCKING BRICKS", size=11, col=SEA_DARK, mono=True))
    body.append(label(20, 46, "Each brick locks to its six neighbours", size=12, col=OCEAN_DEEP, weight=500))
    return svg(600, 300, "\n".join(body))


# ---------------------------------------------------------------- 2. mats
def mats():
    s = 24; ox, oy = 300, 120
    items = [(x, y, 0, H) for (x, y) in hex_grid(9, 6, R)]
    body = [waves(40, 560, 232, n=4, amp=5, step=16)]
    body.append(f'<ellipse cx="{ox+50}" cy="{oy+105}" rx="190" ry="62" fill="{OCEAN}" opacity="0.10"/>')
    body.append(draw_prisms(items, s, ox, oy, R))
    body.append(label(20, 28, "02 · FLOATING MATS", size=11, col=SEA_DARK, mono=True))
    body.append(label(20, 46, "A single course of bricks becomes a buoyant deck", size=12, col=OCEAN_DEEP, weight=500))
    return svg(600, 300, "\n".join(body))


# ---------------------------------------------------------------- 3. tubes & columns
def tubes():
    s = 26; ox, oy = 150, 200
    body = []
    # a ring (annulus) of bricks: hexes around a circle, three courses high -> a tube
    n = 9; rad = 2.55 * R
    items = []
    for course in range(3):
        for i in range(n):
            a = math.radians(360 / n * i + (20 if course % 2 else 0))
            items.append((rad * math.cos(a), rad * math.sin(a), course * H, H))
    body.append(f'<ellipse cx="{ox}" cy="{oy+10}" rx="95" ry="40" fill="{OCEAN}" opacity="0.10"/>')
    body.append(draw_prisms(items, s, ox, oy, R))
    # a solid column: stacked bricks
    ox2 = 430
    col = [(0, 0, k * H, H) for k in range(7)]
    body.append(f'<ellipse cx="{ox2}" cy="{oy+10}" rx="40" ry="18" fill="{OCEAN}" opacity="0.10"/>')
    body.append(draw_prisms(col, s, ox2, oy, R))
    body.append(label(20, 28, "03 · TUBES AND COLUMNS", size=11, col=SEA_DARK, mono=True))
    body.append(label(20, 46, "Rings of bricks form hollow tubes; stacks form columns", size=12, col=OCEAN_DEEP, weight=500))
    body.append(label(ox, 285, "hollow tube", "middle", 11, "#5A6B7A", 500))
    body.append(label(ox2, 285, "column", "middle", 11, "#5A6B7A", 500))
    return svg(600, 300, "\n".join(body))


# ---------------------------------------------------------------- 4. walls
def walls():
    """bricks laid in a vertical plane: hex pattern in the x-z plane (long side faces outward)."""
    s = 26; ox, oy = 290, 240
    body = []
    # draw a wall as a stack of rows; each brick is a hexagonal prism lying on its side -> approximate with
    # a thin prism (height = brick thickness) oriented so the hexagon faces the viewer (y axis is depth).
    # we draw hexagons in x-z plane projected: use pointy-top hex in (x,z) then project with y = depth.
    rows, cols = 5, 6
    Rz = R
    depth = H  # thickness of the wall (brick height)
    polys = []
    for r in range(rows):
        for c in range(cols):
            cx = c * math.sqrt(3) * Rz + (math.sqrt(3) * Rz / 2 if r % 2 else 0)
            cz = r * 1.5 * Rz + Rz
            # hexagon vertices in x-z plane (pointy top)
            verts = [(cx + Rz * math.cos(math.radians(30 + 60 * i)), cz + Rz * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
            # front face at y=0, back at y=depth. Visible: front face (normal -y)? camera at +y sees +y faces.
            # Use back face at y=0 and front face at y=-depth so the face toward camera (+y side) is y=0.
            front = [iso(x, 0, z, s) for (x, z) in verts]
            back = [iso(x, -depth, z, s) for (x, z) in verts]
            # side faces visible: those with outward normal having +x or +z... camera (+1,+1,+1): draw right/top sides
            sides = []
            for i in range(6):
                (x1, z1), (x2, z2) = verts[i], verts[(i + 1) % 6]
                mx, mz = (x1 + x2) / 2 - cx, (z1 + z2) / 2 - cz
                if mx + mz > 1e-6:
                    sides.append([iso(x1, 0, z1, s), iso(x2, 0, z2, s), iso(x2, -depth, z2, s), iso(x1, -depth, z1, s)])
            polys.append((c + r, sides, front))
    polys.sort(key=lambda t: t[0])
    body.append(f'<ellipse cx="{ox+120}" cy="{oy+14}" rx="200" ry="26" fill="{OCEAN}" opacity="0.10"/>')
    for _, sides, front in polys:
        for sd in sides:
            body.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in sd])}" fill="{SIDE_R}" stroke="{EDGE}" stroke-width="0.9" stroke-linejoin="round"/>')
        body.append(f'<polygon points="{fmt([(x+ox-0, y+oy) for x, y in front])}" fill="{TOP}" stroke="{EDGE}" stroke-width="0.9" stroke-linejoin="round"/>')
    body.append(label(20, 28, "04 · WALLS AND ENCLOSURES", size=11, col=SEA_DARK, mono=True))
    body.append(label(20, 46, "Bricks set on edge make walls, hulls and breakwater faces", size=12, col=OCEAN_DEEP, weight=500))
    return svg(600, 300, "\n".join(body))


# ---------------------------------------------------------------- 5. vertical tension cables
def cables():
    s = 22; ox, oy = 300, 150
    body = []
    layers = 3
    items = []
    for L in range(layers):
        for (x, y) in hex_grid(6, 4, R):
            items.append((x, y, L * (H + 0.9), H))
    body.append(waves(40, 560, 262, n=3, amp=5, step=16))
    body.append(f'<ellipse cx="{ox+40}" cy="{oy+110}" rx="150" ry="50" fill="{OCEAN}" opacity="0.10"/>')
    # cables first (behind), then bricks; draw cable segments between layers for a few positions
    cable_pts = [(1.5, 1.732 * 1.5), (4.5, 1.732 * 2.5), (3.0, 1.732 * 0.5), (6.0, 1.732 * 2.0)]
    cab = []
    for (x, y) in cable_pts:
        p0 = iso(x, y, -0.9, s); p1 = iso(x, y, layers * (H + 0.9) + 0.9, s)
        cab.append(f'<line x1="{ox+p0[0]:.1f}" y1="{oy+p0[1]:.1f}" x2="{ox+p1[0]:.1f}" y2="{oy+p1[1]:.1f}" stroke="{OCEAN}" stroke-width="2.2"/>')
        cab.append(f'<circle cx="{ox+p1[0]:.1f}" cy="{oy+p1[1]:.1f}" r="4" fill="{OCEAN}"/>')
    body.append("\n".join(cab))
    body.append(draw_prisms(items, s, ox, oy, R, sw=0.7))
    # redraw cables through the gaps (on top, thin) so they read as passing through
    for (x, y) in cable_pts:
        for L in range(layers - 1):
            p0 = iso(x, y, L * (H + 0.9) + H, s); p1 = iso(x, y, (L + 1) * (H + 0.9), s)
            body.append(f'<line x1="{ox+p0[0]:.1f}" y1="{oy+p0[1]:.1f}" x2="{ox+p1[0]:.1f}" y2="{oy+p1[1]:.1f}" stroke="{OCEAN}" stroke-width="2.2"/>')
    body.append(label(20, 28, "05 · VERTICAL TENSION CABLES", size=11, col=SEA_DARK, mono=True))
    body.append(label(20, 46, "Cables clamp courses together so the stack behaves as one body", size=12, col=OCEAN_DEEP, weight=500))
    return svg(600, 300, "\n".join(body))


# ---------------------------------------------------------------- 6. gel-sealed cavities (section)
def gel():
    body = []
    # a cross-section through a mat: three bricks side by side, each with a sealed void; one drawn as a cutaway
    x0, y0 = 70, 110; bw, bh = 150, 110; gap = 10
    body.append(waves(30, 570, 236, n=3, amp=4, step=14))
    body.append(f'<rect x="30" y="{y0+bh-18}" width="540" height="90" fill="{WATER}" opacity="0.6" rx="6"/>')
    for i in range(3):
        x = x0 + i * (bw + gap)
        body.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="8" fill="{TOP}" stroke="{EDGE}" stroke-width="1.2"/>')
        # shell thickness
        body.append(f'<rect x="{x+18}" y="{y0+18}" width="{bw-36}" height="{bh-36}" rx="6" fill="{'#E8F1F6' if i != 1 else '#BFE0D8'}" stroke="{EDGE}" stroke-width="0.8" stroke-dasharray="{'0' if i == 1 else '4 3'}"/>')
        if i == 1:
            # gel fill hatch
            for k in range(0, bw - 36, 10):
                body.append(f'<line x1="{x+18+k}" y1="{y0+18}" x2="{x+18+k+ (bh-36)}" y2="{y0+bh-18}" stroke="{SEA_DARK}" stroke-width="0.8" opacity="0.55" clip-path="url(#c{i})"/>')
            body.append(f'<defs><clipPath id="c{i}"><rect x="{x+18}" y="{y0+18}" width="{bw-36}" height="{bh-36}" rx="6"/></clipPath></defs>')
    # labels
    body.append(leader(x0 + 9, y0 + 50, x0 - 30, y0 + 20)); body.append(label(x0 - 30, y0 + 14, "outer shell", "end", 11, SEA_DARK, mono=True))
    body.append(leader(x0 + 75, y0 + 55, x0 + 75, y0 - 22)); body.append(label(x0 + 75, y0 - 28, "hollow cavity (buoyancy)", "middle", 11, SEA_DARK, mono=True))
    xm = x0 + bw + gap
    body.append(leader(xm + 75, y0 + 55, xm + 75, y0 - 22)); body.append(label(xm + 75, y0 - 28, "cavity sealed with gel", "middle", 11, SEA_DARK, mono=True))
    xr = x0 + 2 * (bw + gap)
    body.append(leader(xr + 75, y0 + bh - 8, xr + 75, y0 + bh + 40)); body.append(label(xr + 75, y0 + bh + 54, "waterline", "middle", 11, SEA_DARK, mono=True))
    body.append(label(20, 28, "06 · GEL-SEALED CAVITIES", size=11, col=SEA_DARK, mono=True))
    body.append(label(20, 46, "Section view: a sealed cavity keeps buoyancy even if the shell is breached", size=12, col=OCEAN_DEEP, weight=500))
    return svg(600, 300, "\n".join(body))


# ---------------------------------------------------------------- shape evolution strip (concept-level silhouettes)
def evolution():
    s = 22
    body = []
    stages = [
        ("2021", "compressed kelp slab", "slab"),
        ("2022", "square · triangle · hexagon family", "family"),
        ("2022–23", "hollow-core brick", "hollow"),
        ("2023–24", "hinge-lock concept", "hex"),
        ("2025", "component brick (moulded parts)", "parts"),
        ("2026", "hexagonal system brick", "hex2"),
    ]
    for i, (yr, name, kind) in enumerate(stages):
        ox = 70 + i * 118; oy = 120
        if kind == "slab":
            p = [iso(x, y, z, s) for (x, y, z) in [(-1.3, -0.8, 0), (1.3, -0.8, 0), (1.3, 0.8, 0), (-1.3, 0.8, 0)]]
            body.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in [iso(1.3,-0.8,0,s), iso(1.3,0.8,0,s), iso(1.3,0.8,0.3,s), iso(1.3,-0.8,0.3,s)]])}" fill="{SIDE_L}" stroke="{EDGE}" stroke-width="0.9"/>')
            body.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in [iso(-1.3,0.8,0,s), iso(1.3,0.8,0,s), iso(1.3,0.8,0.3,s), iso(-1.3,0.8,0.3,s)]])}" fill="{SIDE_R}" stroke="{EDGE}" stroke-width="0.9"/>')
            body.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in [iso(-1.3,-0.8,0.3,s), iso(1.3,-0.8,0.3,s), iso(1.3,0.8,0.3,s), iso(-1.3,0.8,0.3,s)]])}" fill="{TOP}" stroke="{EDGE}" stroke-width="0.9"/>')
        elif kind == "family":
            # small square, triangle and hexagon prisms
            sq = [(-0.6, -0.6), (0.6, -0.6), (0.6, 0.6), (-0.6, 0.6)]
            def gen_prism(verts, z0, h, ox, oy, s):
                out = []
                cx = sum(v[0] for v in verts) / len(verts); cy = sum(v[1] for v in verts) / len(verts)
                n = len(verts)
                for k in range(n):
                    (x1, y1), (x2, y2) = verts[k], verts[(k + 1) % n]
                    mx, my = (x1 + x2) / 2 - cx, (y1 + y2) / 2 - cy
                    if mx + my > 1e-6:
                        pts = [iso(x1, y1, z0, s), iso(x2, y2, z0, s), iso(x2, y2, z0 + h, s), iso(x1, y1, z0 + h, s)]
                        out.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in pts])}" fill="{SIDE_L if mx > my else SIDE_R}" stroke="{EDGE}" stroke-width="0.9"/>')
                pts = [iso(x, y, z0 + h, s) for x, y in verts]
                out.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in pts])}" fill="{TOP}" stroke="{EDGE}" stroke-width="0.9"/>')
                return "\n".join(out)
            body.append(gen_prism([(x - 1.2, y + 1.0) for x, y in sq], 0, 0.5, ox, oy, s))
            tri = [(0.8 * math.cos(math.radians(90 + 120 * k)) + 1.2, 0.8 * math.sin(math.radians(90 + 120 * k)) - 1.2) for k in range(3)]
            body.append(gen_prism(tri, 0, 0.5, ox, oy, s))
            body.append(prism(0.2, 0.2, 0, 0.5, 0.8, s, ox, oy))
        elif kind == "hollow":
            body.append(prism(0, 0, 0, H, R, s, ox, oy))
            # hint of a hollow: inner hexagon outline on top
            inner = [iso(x, y, H, s) for x, y in hex_pts(0, 0, 0.55)]
            body.append(f'<polygon points="{fmt([(x+ox, y+oy) for x, y in inner])}" fill="none" stroke="{EDGE}" stroke-width="0.8" stroke-dasharray="3 2"/>')
        elif kind == "hex":
            body.append(prism(0, 0, 0, H, R, s, ox, oy))
        elif kind == "parts":
            # exploded: two half-bricks offset vertically
            body.append(prism(0, 0, 0, H / 2, R, s, ox, oy))
            body.append(prism(0, 0, H / 2 + 0.45, H / 2, R, s, ox, oy))
        elif kind == "hex2":
            for (x, y) in [(0, 0), (math.sqrt(3) * R * math.cos(math.radians(30)), math.sqrt(3) * R * math.sin(math.radians(30))), (0, -math.sqrt(3) * R)]:
                pass
            items = [(0, 0, 0, H), (math.sqrt(3) * R * math.cos(math.radians(150)), math.sqrt(3) * R * math.sin(math.radians(150)), 0, H), (math.sqrt(3) * R * math.cos(math.radians(270)), math.sqrt(3) * R * math.sin(math.radians(270)), 0, H)]
            body.append(draw_prisms(items, s * 0.8, ox, oy, R))
        body.append(label(ox, 190, yr, "middle", 12, SEA_DARK, 650, mono=True))
        # wrap long names
        words = name.split(" ")
        line1 = " ".join(words[:2]); line2 = " ".join(words[2:])
        body.append(label(ox, 208, line1, "middle", 11, "#5A6B7A", 500))
        if line2:
            body.append(label(ox, 223, line2, "middle", 11, "#5A6B7A", 500))
        if i < len(stages) - 1:
            body.append(f'<path d="M{ox+48},{oy-10} l18,0" stroke="{WATER_LINE}" stroke-width="1.5" marker-end="url(#arr)"/>')
    body.insert(0, f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{WATER_LINE}"/></marker></defs>')
    body.append(label(20, 28, "SHAPE EVOLUTION · CONCEPT SILHOUETTES ONLY", size=11, col=SEA_DARK, mono=True))
    return svg(760, 240, "\n".join(body))


# ---------------------------------------------------------------- materials strip
def materials():
    body = []
    stages = [("2021–23", "Kelp fibre composite", "#7FA36A"), ("2025", "Flax and hemp fibre", "#C8A96A"), ("2026 →", "Mineral foam + fibre", SEA)]
    for i, (yr, name, col) in enumerate(stages):
        x = 40 + i * 240
        body.append(f'<rect x="{x}" y="60" width="200" height="110" rx="14" fill="#fff" stroke="#D3E0E7" stroke-width="1"/>')
        body.append(f'<rect x="{x}" y="60" width="200" height="8" rx="4" fill="{col}"/>')
        body.append(label(x + 18, 100, yr, "start", 11, SEA_DARK, 650, mono=True))
        body.append(label(x + 18, 126, name, "start", 15, OCEAN_DEEP, 650))
        body.append(label(x + 18, 150, ["research stage", "research stage", "current direction"][i], "start", 11, "#5A6B7A", 500))
        if i < 2:
            body.append(f'<path d="M{x+206},115 l26,0" stroke="{WATER_LINE}" stroke-width="1.5" marker-end="url(#arr2)"/>')
    body.insert(0, f'<defs><marker id="arr2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{WATER_LINE}"/></marker></defs>')
    body.append(label(40, 36, "MATERIAL STRATEGY OVER TIME", size=11, col=SEA_DARK, mono=True))
    return svg(760, 200, "\n".join(body))


# ---------------------------------------------------------------- small icons for cards (mission pillars)
def icon(kind):
    c = OCEAN
    if kind == "adapt":
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 15c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M3 19c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M7 11V7l5-3 5 3v4"/></svg>'
    if kind == "mitigate":
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M12 7c-4 0-6 2-6 5 3 0 6-1 6-5z"/><path d="M12 11c4 0 6 2 6 5-3 0-6-1-6-5z"/><path d="M4 21h16"/></svg>'
    if kind == "open":
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/></svg>'
    if kind == "hex":
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"><path d="M12 2l8.5 5v10L12 22l-8.5-5V7z"/></svg>'
    if kind == "wave":
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"><path d="M2 12c2.5-3 5-3 7.5 0s5 3 7.5 0 5-3 5 0"/><path d="M2 18c2.5-3 5-3 7.5 0s5 3 7.5 0 5-3 5 0"/><path d="M2 6c2.5-3 5-3 7.5 0s5 3 7.5 0 5-3 5 0"/></svg>'
    if kind == "people":
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.5 3-6 6.5-6s6.5 2.5 6.5 6"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 14.5c3 0 6 2 6 5.5"/></svg>'
    return ""


def wave_divider(color="#F5F9FA", flip=False):
    t = ' transform="scale(1,-1) translate(0,-60)"' if flip else ""
    return f'<svg class="waves" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true"><path{t} d="M0,30 C180,60 360,0 540,30 C720,60 900,0 1080,30 C1260,60 1350,45 1440,30 L1440,60 L0,60 Z" fill="{color}"/></svg>'


def write_all():
    files = {
        "hero.svg": hero(), "brick.svg": brick_single(), "interlocking.svg": interlocking(), "mats.svg": mats(),
        "tubes.svg": tubes(), "walls.svg": walls(), "cables.svg": cables(), "gel.svg": gel(),
        "evolution.svg": evolution(), "materials.svg": materials(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", ", ".join(files))


if __name__ == "__main__":
    write_all()
