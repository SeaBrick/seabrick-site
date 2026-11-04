# -*- coding: utf-8 -*-
"""Static site builder for the SeaBrick Society website.

    python src/artwork.py   # (optional) regenerate SVG illustrations
    python src/build.py     # writes dist/*.html and dist/journal/*.html

Everything is plain HTML/CSS/JS; no framework, no external requests, no analytics.
"""
import datetime, html, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = ROOT / "dist"
sys.path.insert(0, str(HERE))
from stories import STORIES  # noqa: E402
from artwork import icon, wave_divider  # noqa: E402
from evolution import ERAS, STRIP, STRIP_LABELS  # noqa: E402

SITE_NAME = "SeaBrick Society"
TAGLINE = "Floating infrastructure for a changing coast"
PREVIEW_BAND = "Local design preview · not published · journal articles are drafts for review"
CONTACT_EMAIL = "john@seabrick.com"
CITY = "Vancouver, British Columbia, Canada"

NAV = [
    ("index.html", "Home"), ("mission.html", "Mission"), ("technology.html", "Technology"),
    ("evolution.html", "Evolution"), ("builder.html", "Builder"),
    ("journal.html", "Journal"), ("society.html", "The Society"),
]


def builder_embed(query, *, depth=0, height=520, title="SeaBrick builder"):
    """An embedded instance of the interactive builder (dist/app/builder.html)."""
    rel = "../" * depth
    return (f'<div class="embed"><iframe src="{rel}app/builder.html?{query}&embed=1" title="{html.escape(title)}" '
            f'loading="lazy" style="height:{height}px" allow="fullscreen"></iframe>'
            f'<div class="embed-foot"><span>Drag to orbit · scroll to zoom · click a brick to identify it</span>'
            f'<a href="{rel}app/builder.html?{query}">Open in the full builder ↗</a></div></div>')


def render_fig(name, caption, *, depth=0, cls="figure", alt=""):
    rel = "../" * depth
    return (f'<figure class="{cls}"><img src="{rel}assets/render/{name}.webp" alt="{html.escape(alt or caption)}" loading="lazy">'
            f'<figcaption>{caption}</figcaption></figure>')

# ------------------------------------------------------------------ layout

def page(title, body, *, active="", depth=0, description="", og_image="assets/img/party-gathering.webp"):
    rel = "../" * depth
    nav = "".join(
        f'<li><a href="{rel}{href}"{" class=\"active\"" if href == active else ""}>{label}</a></li>' for href, label in NAV
    )
    desc = html.escape(description or f"{SITE_NAME}: a Canadian nonprofit researching modular floating infrastructure for coastal adaptation and lower-carbon marine construction.")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {SITE_NAME}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex, nofollow">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{rel}{og_image}">
<link rel="icon" type="image/svg+xml" href="{rel}assets/favicon.svg">
<link rel="stylesheet" href="{rel}assets/site.css">
<link rel="stylesheet" href="{rel}assets/site-additions.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="preview-band">{PREVIEW_BAND}</div>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="{rel}index.html" aria-label="SeaBrick Society home">
      <img src="{rel}assets/seabrick-logo.svg" alt="SeaBrick" width="168" height="30">
      <span class="sub">A nonprofit<br>research society</span>
    </a>
    <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <ul class="menu">{nav}<li><a class="cta" href="{rel}contact.html">Get in touch</a></li></ul>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div class="brandf">
        <img src="{rel}assets/seabrick-logo.svg" alt="SeaBrick">
        <p>SeaBrick Society is a not-for-profit corporation incorporated in Canada in 2022 to promote innovation and standards around environmentally sustainable marine infrastructure building materials.</p>
        <p class="small">{CITY}<br>Corporation number 1378929-2 (Canada Not-for-profit Corporations Act)</p>
      </div>
      <div><h4>Explore</h4><ul>
        <li><a href="{rel}mission.html">Mission</a></li><li><a href="{rel}technology.html">Technology</a></li>
        <li><a href="{rel}story.html">Our story</a></li><li><a href="{rel}journal.html">Journal</a></li></ul></div>
      <div><h4>Society</h4><ul>
        <li><a href="{rel}society.html">About the Society</a></li><li><a href="{rel}society.html#governance">Governance</a></li>
        <li><a href="{rel}society.html#involved">Get involved</a></li><li><a href="{rel}contact.html">Contact</a></li></ul></div>
      <div><h4>Notes</h4><ul>
        <li><a href="{rel}privacy.html">Privacy</a></li>
        <li><a href="{rel}technology.html#status">Research status</a></li></ul></div>
    </div>
    <div class="legal"><span>© {datetime.date.today().year} SeaBrick Society. Not a registered charity.</span><span>3D views and renders use smoothed visualization models that omit the design's connection features.</span></div>
  </div>
</footer>
<script src="{rel}assets/site.js"></script>
</body>
</html>"""


def card(title, text, kind=None, href=None):
    ic = f'<div class="ic">{icon(kind)}</div>' if kind else ""
    inner = f'{ic}<h3>{title}</h3><p>{text}</p>'
    return f'<a class="card" href="{href}">{inner}</a>' if href else f'<div class="card">{inner}</div>'


def post_card(s, depth=0):
    rel = "../" * depth
    d = datetime.date.fromisoformat(s["date"]).strftime("%B %Y")
    return (f'<a class="post-card" href="{rel}journal/{s["slug"]}.html" data-cat="{s["category"]}">'
            f'<div class="thumb{" art" if s["image"].endswith(".svg") else ""}"><img src="{rel}{s["image"]}" alt="{html.escape(s["image_alt"])}"></div>'
            f'<div class="body"><div class="meta">{s["period"]} · {s["category"]}</div><h3>{s["title"]}</h3><p>{s["summary"]}</p></div></a>')


# ------------------------------------------------------------------ pages

def index():
    latest = sorted(STORIES, key=lambda s: s["date"], reverse=True)[:3]
    body = f"""
<section class="hero">
  <div class="wrap">
    <div>
      <span class="eyebrow">SeaBrick Society · {CITY.split(',')[0]}, Canada</span>
      <h1>Building blocks for a <em>rising sea.</em></h1>
      <p class="lead">SeaBrick is a hexagonal, interlocking, buoyant brick, and a nonprofit research programme to turn it into floating infrastructure that coastal communities can build themselves: docks, platforms, breakwaters and the foundations of buildings that rise with the water instead of fighting it.</p>
      <div class="btn-row"><a class="btn primary" href="technology.html">Explore the technology</a><a class="btn ghost" href="mission.html">Read our mission</a></div>
      <p class="hero-note">Research in progress. Material performance and marine durability are being tested; nothing on this site is a product specification.</p>
    </div>
    <figure class="hero-art"><img src="assets/render/mat-3.webp" alt="A three-course floating mat assembled from SeaBricks, rendered from the design model" width="1091" height="735"><figcaption class="hero-note">A three-course mat of SeaBricks, rendered from the design model. <a href="builder.html">Build one yourself</a>.</figcaption></figure>
  </div>
  {wave_divider('#F5F9FA')}
</section>

<section class="band soft" style="padding-top:0">
  <div class="wrap">
    <div class="recog">
      <div><b>Climate Spotlight Award</b><span>Ocean Impact Pitchfest 2023, presented by Star of the South</span></div>
      <div><b>Third Derivative</b><span>Climate accelerator, Cohort 23-2</span></div>
      <div><b>Earthshot Prize nominee</b><span>Nominated by Ashoka for the 2024 cycle</span></div>
      <div><b>Ocean Supercluster</b><span>Ocean Startup grant, waterproofing validation study</span></div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Why floating</span><h2>The coast is moving. Infrastructure should be able to move with it.</h2>
    <p class="lead">Sea level is rising, storms are stronger and the structures we have built along the shore were designed for a sea that stayed put. Floating infrastructure adapts by definition. Built from low-carbon materials, it can also help with the cause.</p></div>
    <div class="grid c3">
      {card("Adapt", "Platforms, docks and foundations that float rise with the tide and the decade. Communities can add, move and repair them without heavy equipment or deep foundations.", "adapt")}
      {card("Mitigate", "Concrete and steel in the sea carry a large carbon cost. SeaBrick's materials strategy aims far below that, using mineral binders and plant fibre instead of Portland cement.", "mitigate")}
      {card("Open", "SeaBrick Society is a nonprofit. Its job is the standard and the public record of what works, so that anyone can build with the system and improve it.", "open")}
    </div>
  </div>
</section>

<section class="band sand">
  <div class="wrap split">
    <div>
      <span class="eyebrow">The brick</span>
      <h2>One small shape, many large structures.</h2>
      <p>A SeaBrick is a hexagonal brick roughly one and a half times as wide as it is tall, light enough to float and shaped to lock to its six neighbours and to the courses above and below. Lay bricks flat and you get a mat. Stack rings and you get a tube or a tower. Add bridging bricks and the courses tie together. Run cables through the stack and the whole thing behaves as one body.</p>
      <p>The technology page explains the brick and its family of shapes, and an interactive builder lets you assemble mats, tubes and towers from the real design model.</p>
      <div class="btn-row"><a class="btn primary" href="technology.html">How it works</a><a class="btn ghost" href="builder.html">Open the builder</a></div>
    </div>
    <figure class="figure"><img src="assets/render/brick-hero.webp" alt="A single SeaBrick rendered from the design model" loading="lazy"><figcaption>The SeaBrick, final design (2026), rendered from the smoothed design model. Connection surfaces are not modelled.</figcaption></figure>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Try it</span><h2>Watch a mat go together</h2><p class="lead">Nineteen bricks to a course, three courses, each course offset so that it bridges the joints below.</p></div>
    {builder_embed("scene=mat&layers=3&play=1", height=480)}
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Journal</span><h2>Marks of progress</h2><p class="lead">Five years of research, told one milestone at a time.</p></div>
    <div class="posts">{''.join(post_card(s) for s in latest)}</div>
    <p style="margin-top:28px"><a class="btn ghost" href="journal.html">All journal articles</a></p>
  </div>
</section>

<section class="band deep">
  <div class="wrap split">
    <div>
      <span class="eyebrow">The Society</span>
      <h2>A nonprofit built to set standards, not to sell bricks.</h2>
      <p class="lead">SeaBrick Society was incorporated under the Canada Not-for-profit Corporations Act in February 2022. It holds the research direction, the public record and the standards work. It does not sell products, take investment or pay dividends.</p>
      <div class="btn-row"><a class="btn primary" href="society.html">About the Society</a><a class="btn ghost" style="background:transparent;color:#fff;border-color:rgba(255,255,255,.35)" href="contact.html">Work with us</a></div>
    </div>
    <figure class="figure"><img src="assets/img/party-tower.webp" alt="Model bricks assembled at the June 2026 SeaBrick party" loading="lazy"><figcaption style="color:#9DB8CC">The June 2026 SeaBrick party. Model bricks of an earlier generation.</figcaption></figure>
  </div>
</section>
"""
    return page("Home", body, active="index.html")


def mission():
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Mission</div>
  <h1>Floating infrastructure for adapting to, and mitigating, climate change and sea level rise.</h1>
  <p class="lead">SeaBrick Society exists to make it possible for coastal communities to build on the water with materials and methods that are light on the planet, open to everyone and proven to be safe.</p>
</div></section>

<section class="band">
  <div class="wrap narrow">
    <h2>The problem we work on</h2>
    <p>More than a tenth of the world's population lives within ten metres of sea level. The sea is rising and will keep rising for centuries, whatever happens to emissions now, and the storms that drive water over the shore are getting stronger. Most coastal infrastructure was designed for a fixed waterline. Raising it, armouring it or moving it inland is slow, expensive and, in many places, simply not possible.</p>
    <p>At the same time, the usual way to build in the sea, with steel and reinforced concrete, carries a large carbon cost and a short life in salt water. We think the sea deserves better materials.</p>
    <h2>Our approach</h2>
    <p>SeaBrick is a modular approach to floating infrastructure. Instead of a single large hull, structures are assembled from many small, buoyant, interlocking bricks. That has consequences we care about:</p>
    <ul>
      <li><strong>Communities can build it.</strong> No heavy equipment, no deep foundations, no dry dock. Bricks can be made close to where they are used and assembled by hand.</li>
      <li><strong>Structures can change.</strong> A dock can grow, a platform can be reshaped, a damaged brick can be swapped. Floating structures rise with the water as a matter of course.</li>
      <li><strong>Materials can be low-carbon.</strong> The current strategy uses mineral binders and short plant fibres rather than Portland cement, with the goal of a material far below the emissions of marine concrete.</li>
      <li><strong>Failure is local.</strong> Many small sealed units are more forgiving than one large hull: damage to a brick is damage to a brick.</li>
    </ul>
    <h2>What the Society does</h2>
    <div class="grid c2" style="margin:1.5rem 0">
      {card("Research", "Materials, connections and marine durability, with university partners and independent engineers. We publish what we learn, including what did not work.", "hex")}
      {card("Standards", "A definition of what a SeaBrick is: dimensions, connections, performance tests. The point is that others can build with the system and improve it.", "open")}
      {card("Pilots", "Small real-world structures with coastal partners: work floats, aquaculture platforms, docks. The first market for floating infrastructure is working infrastructure.", "wave")}
      {card("Community", "Open days, model bricks, students and advisors. A building system people can hold in their hands is one they can understand and question.", "people")}
    </div>
    <h2>Our principles</h2>
    <ol>
      <li><strong>Say what we know.</strong> Lab results are lab results. A material that has not been through marine exposure testing is not a marine product, and we do not describe it as one.</li>
      <li><strong>No petrochemical shortcuts.</strong> Coatings and sealants must not shed microplastics into the sea. That bar has cost us time; we keep it.</li>
      <li><strong>Carbon honesty.</strong> We aim for a material with far lower emissions than concrete. Whether a finished brick is fully carbon-negative depends on feedstock, energy and coating life, and we will only claim it when it is measured.</li>
      <li><strong>The standard belongs to everyone.</strong> The Society keeps the research record and the standard in public hands. Related companies may make and sell bricks; the Society does not.</li>
    </ol>
    <div class="note blue"><strong>Nonprofit, not a charity.</strong> SeaBrick Society is a federally incorporated not-for-profit corporation. It is not a registered charity and does not issue tax receipts. See <a href="society.html">the Society</a> for how it is governed.</div>
  </div>
</section>
"""
    return page("Mission", body, active="mission.html")


# ---- technology, builder, connection lab
SHAPES = [
    ("seabrick", "SeaBrick", "The full brick. All six sides carry connectors; it makes up the body of every mat, tube and tower."),
    ("3-lock-claw", "Half brick, claw", "Half of a SeaBrick ending in a claw face. Closes rings and edges."),
    ("3-lock-tongue", "Half brick, tongue", "The claw's partner: every internal tongue meets a claw."),
    ("4-lock", "Four-connector brick", "Two flat faces for straight wall runs, four connectors."),
    ("5-lock-claw", "Five-connector, claw", "One flat face for a wall, a claw at the end."),
    ("5-lock-tongue", "Five-connector, tongue", "One flat face for a wall, a tongue at the end."),
    ("2-lock-bump", "Two-connector, bump", "A thin wall piece with an outer bump face."),
    ("2-lock-thin", "Two-connector, thin", "The thinnest wall piece."),
    ("2-flat-face", "Two flat faces", "Wall brick with two flat outer faces."),
    ("double-hex-bridge", "Double-height bridge", "Two courses tall: ties one course to the next."),
    ("wedge-insert-1", "Wedge insert 1", "Upright cladding that finishes a wall boundary."),
    ("wedge-insert-2", "Wedge insert 2", "Upright cladding, second orientation."),
]

WAYS = [
    dict(id="bricks", n="01", name="One brick, six neighbours",
         embed="scene=catalogue&shape=0",
         text="Every SeaBrick locks to its six neighbours in the same course and to the courses above and below. The research questions are the ones any dry-laid system has: how much force a joint carries, how far it can flex before it lets go, and whether a brick can be removed and reseated without tools. The <a href=\"connections-lab.html\">connection lab</a> explores joint behaviour on a two-brick model.",
         photos=[("studio-hex-cluster", "Model bricks clustered around a central brick."), ("early-bowl", "Spring 2026: a bowl of model bricks in several shapes.")]),
    dict(id="mats", n="02", name="Floating mats",
         embed="scene=mat&layers=3&play=1",
         text="A single course of bricks laid flat is a mat: a buoyant deck that can be any shape the hex grid allows. Courses sit in one of three registrations, A, B and C, so that each course bridges the joints of the one below. Mats are the basis for work floats, aquaculture platforms and docks, the structures we expect to build first.",
         photos=[("studio-mat", "A model mat, June 2026."), ("studio-mat-2", "Two stacked courses of a model mat.")]),
    dict(id="tubes", n="03", name="Tubes and towers",
         embed="scene=designer&preset=thickHex&layers=6",
         text="Bricks laid in a ring, course on course, make a hollow tube; keep going and it is a tower. Half bricks and edge bricks close the ring so that every internal tongue meets a claw. Tubes are stiff for their weight and were the first thing almost everyone built at the SeaBrick party. In a floating structure they become pontoons, piles, culverts and the legs of a platform.",
         photos=[("studio-ring", "A single-course model ring."), ("party-tower", "A model column with a platform on top.")]),
    dict(id="walls", n="04", name="Walls and enclosures",
         embed="scene=designer&preset=lowDodec",
         text="Straight runs of wall bricks between corners make the sides of an enclosure: the hull of a barge, a breakwater face, a tank for growing fish or seaweed. A twelve-sided ring uses two families of wall direction, with upright wedge inserts cladding the boundary. In the builder, gold marks the bricks whose flat faces form the wall.",
         photos=[("studio-house", "A model hut: walls, a platform and a roof."), ("party-frame", "A square frame built at the party.")]),
    dict(id="bridges", n="05", name="Bridging the courses",
         embed="scene=bridges&layers=4",
         text="A double-height brick spans two courses and ties them together, so a stack of rings behaves as one body rather than a pile of loose layers. Turn the bridges off in the builder and the courses come apart.",
         photos=[("party-column", "A model column built at the party."), ("party-tower-roof", "A roofed model tower.")]),
    dict(id="cables", n="06", name="Vertical tension cables", render="cables",
         text="Dry-laid bricks resist compression well and tension poorly. Vertical cables run through aligned cavities in a stack and clamp the courses together, so a multi-course platform can carry point loads and hold together in a swell. Cables can be tightened, inspected and replaced from above. The render is schematic: cable routing is part of the current design study.",
         photos=[("studio-truss", "A model truss: beams and nodes."), ("party-wheel-2", "A spoked wheel assembled at the party.")]),
    dict(id="gel", n="07", name="Gel-sealed cavities", render="cutaway",
         text="Much of a brick's buoyancy comes from sealed internal cavities. Filling them with a lightweight closed-cell gel means a breached shell loses a little buoyancy rather than all of it, and leaves nothing inside the brick for water or marine growth to colonise. This is a concept under evaluation alongside the barrier coating. The cutaway shows the outer form only; the internal cavity layout is not shown.",
         photos=[("studio-hex-ring", "A hexagonal model ring around a central void."), ("studio-platform", "A hexagonal model platform.")]),
]


def technology():
    shapes = "".join(
        f'<figure class="shape"><img src="assets/render/shape-{sid}.webp" alt="{html.escape(name)}" loading="lazy"><figcaption><b>{name}</b><span>{text}</span></figcaption></figure>'
        for sid, name, text in SHAPES)
    tabs = "".join(f'<button role="tab" aria-selected="false" aria-controls="{w["id"]}"><span class="n">{w["n"]}</span>{w["name"]}</button>' for w in WAYS)
    panels = ""
    for w in WAYS:
        photos = "".join(f'<figure><img src="assets/img/{p}.webp" alt="{html.escape(c)}" loading="lazy"><figcaption>{c}</figcaption></figure>' for p, c in w["photos"])
        visual = builder_embed(w["embed"], height=440, title=w["name"]) if w.get("embed") else render_fig(w["render"], "Rendered from the design model; schematic.", cls="figure framed")
        panels += (f'<div class="panel" id="{w["id"]}" role="tabpanel"><h3>{w["name"]}</h3><p>{w["text"]}</p>{visual}'
                   f'<div class="photo">{photos}</div><p class="small muted" style="margin-top:14px">Photos: model bricks of an earlier design generation, 2026.</p></div>')
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Technology</div>
  <h1>A brick, and a system for building with it.</h1>
  <p class="lead">SeaBrick is a hexagonal, buoyant, interlocking brick. On its own it is a small thing. Connected to thousands of others it is a floating platform, a breakwater, a dock, a foundation. This page has two parts: the <a href="#geometry">geometry of the brick</a> and how bricks fit together, and <a href="#materials">the material</a> it is made of. How both got here is on the <a href="evolution.html">evolution</a> page.</p>
</div></section>

<section class="band" id="geometry">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 1</span><h2>Geometry and design</h2></div>
    <div class="split">
      <figure class="figure"><img src="assets/render/brick-hero.webp" alt="The SeaBrick, rendered from the design model" width="1023" height="934"><figcaption>The SeaBrick, final design (2026). Rendered from the smoothed design model; the connector surfaces on each face are not modelled.</figcaption></figure>
      <div>
        <span class="eyebrow">The unit</span>
        <h3>Hexagonal, hollow, buoyant.</h3>
        <p>A SeaBrick is a hexagonal brick about one and a half times as wide as it is tall. The hexagon tiles the plane with no gaps, gives every brick six equal neighbours and has no long straight joints. Each of the six sides carries a connector; the top and bottom register with the course above and below. Inside, sealed cavities provide buoyancy; outside, a dense shell carries the loads where bricks meet.</p>
        <p>Bricks are designed to be moulded in a single cycle, so they can be made in small facilities close to where they are used. The design has been through more than twenty versions since 2022; <a href="evolution.html">the evolution page</a> shows them.</p>
        <ul class="pill-list"><li>Floats</li><li>Locks to six neighbours</li><li>Stacks in courses</li><li>Moulded, not machined</li><li>Replaceable one at a time</li></ul>
        <div class="triple"><img src="assets/render/brick-top.webp" alt="SeaBrick seen from above"><img src="assets/render/brick-side.webp" alt="SeaBrick seen from the side"><img src="assets/render/tube-small-top.webp" alt="A small ring of bricks seen from above, coloured by brick type"></div>
      </div>
    </div>
  </div>
</section>

<section class="band soft">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">The family</span><h2>One brick, eleven variations</h2><p class="lead">Every shape in the system is a subset of the same brick. The number of connectors says how many of the six sides lock to a neighbour; the rest are flat wall faces. Two upright wedges clad wall boundaries, and a double-height brick ties courses together.</p></div>
    <div class="shapes">{shapes}</div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">The system</span><h2>Seven ways to build with SeaBrick</h2><p class="lead">The same brick, arranged differently. The 3D views are live: drag to orbit, scroll to zoom, click a brick to identify it. The photographs show model bricks from an earlier generation of the design.</p></div>
    <div class="explorer">
      <div class="tabs" role="tablist" aria-label="Ways to build">{tabs}</div>
      {panels}
    </div>
    <p style="margin-top:24px"><a class="btn primary" href="builder.html">Open the full builder</a> <a class="btn ghost" href="connections-lab.html">Open the connection lab</a></p>
  </div>
</section>

<section class="band sand" id="materials">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 2</span><h2>Material technology</h2></div>
    <div class="section-head"><span class="eyebrow">Materials</span><h2>A light mineral core, a dense mineral shell, plant fibre throughout.</h2>
    <p class="lead">The material has two jobs that pull against each other: provide buoyancy, and carry the forces that pass between connected bricks. The current strategy gives each job to a different part of the brick.</p></div>
    <div class="grid c3">
      {card("Core", "A low-density mineral foam, made with lightweight glass particles or controlled air in a magnesium-silicate binder. It supplies most of the buoyancy. The open question is how light it can be before strength, stability and water resistance suffer.")}
      {card("Shell", "A denser mineral layer that protects the core and carries contact loads, with the most solid material concentrated where bricks grip one another. A barrier coating goes over it.")}
      {card("Fibre", "Short, treated plant fibres mixed into the core add strength and reduce brittleness. This is the thread back to the project's kelp and flax years; today the fibre is a reinforcement, not the structure.")}
    </div>
    <figure class="figure" style="margin-top:32px">{(DIST/'assets/art/materials.svg').read_text(encoding='utf-8')}<figcaption>Kelp fibre composites (2021 to 2023) and flax and hemp composites (2025) were research stages. Mineral foam with fibre reinforcement is the current direction. <a href="journal/mineral-foam-and-fibre.html">Read more</a>, or see <a href="evolution.html#materials">how the material evolved</a>.</figcaption></figure>
    <h3 style="margin-top:40px">Why mineral binders</h3>
    <p class="narrow" style="margin:0">Magnesium-silicate binders cure without the high-temperature clinker that gives Portland cement its carbon footprint, they are not degraded by seawater the way reinforced concrete is, and they do not swell. With roughly a tenth of the mix as plant fibre, and some uptake of carbon dioxide by the mineral over its life, the material should have far lower emissions than marine concrete. Whether a finished brick is fully carbon-negative is not yet established, and we will not say so until it is measured.</p>
  </div>
</section>

<section class="band" id="status">
  <div class="wrap split">
    <div>
      <span class="eyebrow">Research status</span>
      <h2>What has been shown, and what has not.</h2>
      <table class="def">
        <tr><th>Shown</th><td>Bio-based composites stronger than concrete in compression on lab specimens (2022 to 2025). Model-scale bricks that assemble into mats, tubes, walls and frames by hand (2026). A moulding approach that produces one brick per cycle. Ring, tube and tower layouts in which every internal tongue has a claw partner (design study, 2026).</td></tr>
        <tr><th>Being tested</th><td>Mineral foam core density and batch variation; water uptake under immersion and wet-dry cycling, including after surface damage; shrinkage and core-to-shell bond through curing and ageing; reliable demoulding; joint clearance and insertion order on the final brick.</td></tr>
        <tr><th>Not yet shown</th><td>A full-size brick qualified for marine use. Joint strength under wave loading at scale. Long-term durability and biofouling behaviour in seawater. Carbon-negativity of a finished brick.</td></tr>
      </table>
      <p class="small muted">We will update this table as results come in. Nothing on this site is a product specification.</p>
    </div>
    <div>
      <div class="card"><h3>Work with the research</h3><p>Universities, marine engineers and coastal partners are welcome. The Society's role is to make the system available to people who want to build with it and test it. <a href="contact.html">Get in touch</a>.</p></div>
      <div class="card" style="margin-top:16px"><h3>About the 3D models</h3><p>The builder and the renders on this site use smoothed visualization models of the final brick family. They are accurate in overall form and spacing; the connector surfaces are intentionally not modelled and the design files are not distributed.</p></div>
    </div>
  </div>
</section>
"""
    return page("Technology", body, active="technology.html", description="The SeaBrick: its geometry and family of shapes, an interactive builder for mats, tubes and towers, and the mineral foam and fibre materials strategy.")


def builder_page():
    body = f"""
<section class="article-head compact"><div class="wrap">
  <div class="meta">Builder</div>
  <h1>Build with SeaBrick</h1>
  <p class="lead">Assemble mats, tubes, towers and bridged courses from the brick family, course by course. Everything you see is generated from the design model and the layouts checked in the 2026 design study.</p>
</div></section>
<section class="band" style="padding-top:0">
  <div class="wrap wide">
    {builder_embed("scene=mat&layers=3&bar=0&panel=1", height=760, title="SeaBrick builder")}
    <div class="grid c3" style="margin-top:28px">
      {card("What the builder shows", "Where each brick goes, which shape it is, how courses register (A, B, C) and how rings close. Colour by course or by shape; separate the courses; watch an assembly go together one brick at a time; save a picture of any view.")}
      {card("What it does not show", "The connector surfaces, which are not modelled; joint clearance and insertion order, which are still under study; and any load or wave behaviour. For joint behaviour on a two-brick model, see the connection lab.", href="connections-lab.html")}
      {card("Units", "Dimensions are in brick pitches: one pitch is the centre-to-centre spacing of neighbouring bricks. A course is one brick tall. Tube radius is measured from the centre to a flat wall.")}
    </div>
  </div>
</section>
"""
    return page("Builder", body, active="builder.html", description="An interactive builder for assembling SeaBrick mats, tubes, towers and bridged courses from the design model.")


def lab_page():
    body = """
<section class="article-head compact"><div class="wrap">
  <div class="meta">Connection lab</div>
  <h1>How two bricks hold on to each other</h1>
  <p class="lead">A joint model on a small mat: apply a force to one brick, change how the mat is supported, and watch how the connections respond and where they reach their limits. Joint behaviour here uses rounded demonstration assumptions, not measured values.</p>
</div></section>
<section class="band" style="padding-top:0">
  <div class="wrap wide">
    <div class="embed"><iframe src="app/connections-lab/index.html" title="SeaBrick connection lab" loading="lazy" style="height:760px"></iframe>
    <div class="embed-foot"><span>Choose an example from the menu on the left. The lab runs entirely in your browser.</span><a href="app/connections-lab/index.html">Open the lab on its own ↗</a></div></div>
    <p class="small muted" style="margin-top:16px">The connection lab is a research tool built for the design programme and is shown here unchanged. Its brick model is the same smoothed visualization model used elsewhere on this site.</p>
  </div>
</section>
"""
    return page("Connection lab", body, active="technology.html", description="A two-brick joint model showing how SeaBrick connections respond to force and support conditions.")


def evolution():
    eras = ""
    for era in ERAS:
        pics = "".join(f'<figure><img src="assets/evolution/{lid.replace("jewel", "brick")}.webp" alt="{html.escape(cap)}" loading="lazy"><figcaption>{cap}</figcaption></figure>' for lid, cap, cam in era["items"]) if era.get("public", True) else ""
        eras += (f'<article class="era" id="{era["id"]}"><div><div class="when">{era["when"]}</div><h3>{era["title"]}</h3><p>{era["text"]}</p>'
                 f'<p class="people">{era["people"]}</p></div>' + (f'<div class="pics">{pics}</div>' if pics else '<div class="pics empty"><p class="small muted">{era.get("note", "No brick design files from this year; the work was in moulds and hand-cast prototypes.")}</p></div>') + '</article>')
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Evolution</div>
  <h1>How the brick got its shape, and its material.</h1>
  <p class="lead">Two threads run through SeaBrick's five years. One is geometry: more than twenty versions of the brick between January 2022 and the final design of 2026, every one of them rendered here from its original design file. The other is material: kelp, then flax and hemp, then mineral foam and fibre.</p>
</div></section>

<section class="band" id="shape">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 1</span><h2>Geometry and design, 2022 to 2026</h2></div>
    <figure class="figure" style="margin-bottom:36px"><img src="assets/evolution/strip.webp" alt="Four brick designs in a row, from the first square of January 2022 to the final SeaBrick of 2026" loading="lazy"><figcaption>Four of the generations, to a common scale on the page but not to each other. Each is rendered from its design file.</figcaption></figure>
    <div class="eras">{eras}</div>
    <p class="small muted" style="margin-top:20px">Renders are made from the project's archived STEP, STL and 3MF files, in the orientation of the original file, with a neutral material. Early files were drawn to be printed at a fifth to a sixteenth of full size. Design files are not distributed; the connection features visible in historical renders have been superseded by the final design.</p>
  </div>
</section>

<section class="band sand" id="materials">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 2</span><h2>Material technology, 2021 to 2026</h2></div>
    <div class="split" style="align-items:start">
      <div>
        <h3>2021 to 2023: kelp</h3>
        <p>The project began as an idea about kelp: a fast-growing feedstock that stores carbon, harvested and pressed into a building block. Six UBC Materials Engineering students took it on as a Capstone project in 2022 and made a kelp fibre composite that tested stronger than concrete in compression. A sponsored research agreement with UBC's BioProducts Institute followed; the composite was named Kelpstone, and small specimens reached around three times the compressive strength of concrete at half the weight. Its density, close to water, is why the brick became hollow.</p>
        <h3>2024 to 2025: other fibres, and keeping water out</h3>
        <p>Work in Western Australia showed sargassum worked as well as kelp, and a simpler process. When seaweed fibre could not be obtained at the scale a pilot needed, flax and hemp from the Prairies were tested in 2025 and performed at least as well. In parallel, an Ocean Supercluster grant funded a validation study of a mineral-based waterproofing method, because a plant-fibre composite that takes up water is not a marine material.</p>
        <h3>2026: mineral foam and fibre</h3>
        <p>The current strategy turns the material inside out. The structure is now mineral: a low-density mineral foam core for buoyancy inside a dense mineral shell that carries the loads where bricks meet, both in a magnesium-silicate binder that cures without clinker and is not degraded by seawater. Short, treated plant fibres remain, at roughly a tenth of the mix, as reinforcement. A marine validation programme is organised around four questions: core density and its variation, water uptake, shrinkage and the core-to-shell bond, and reliable demoulding. <a href="journal/mineral-foam-and-fibre.html">Where the strategy stands</a>.</p>
      </div>
      <div>
        <div class="mat-strip">
          <figure><img src="assets/img/ubc-kelp-drying.webp" alt="Kelp drying on racks" loading="lazy"><figcaption>2022: kelp feedstock drying at UBC.</figcaption></figure>
          <figure><img src="assets/img/kelpstone-cube.webp" alt="A pressed kelp composite cube" loading="lazy"><figcaption>2023: a Kelpstone test cube.</figcaption></figure>
          <figure><img src="assets/img/ubc-mould-feedstock.webp" alt="A mould being filled with composite feedstock" loading="lazy"><figcaption>2023: filling a mould.</figcaption></figure>
        </div>
        <figure class="figure" style="margin-top:16px">{(DIST/'assets/art/materials.svg').read_text(encoding='utf-8')}<figcaption>Three stages, one direction: a material that floats, lasts in seawater and costs the planet very little.</figcaption></figure>
        <table class="def" style="margin-top:16px"><tr><th>2021–23</th><td>Kelp fibre composite ("Kelpstone"), with UBC</td></tr><tr><th>2024–25</th><td>Sargassum; flax and hemp fibre composites; mineral waterproofing study</td></tr><tr><th>2026 →</th><td>Mineral foam core, mineral shell, plant-fibre reinforcement</td></tr></table>
      </div>
    </div>
  </div>
</section>
"""
    return page("Evolution", body, active="evolution.html", description="How the SeaBrick's geometry evolved through more than twenty versions from 2022 to 2026, rendered from the original design files, and how its material moved from kelp to mineral foam and fibre.")


TIMELINE = [
    ("2021", "An idea called Kelp Island", "A research document about building coastal infrastructure from kelp becomes a project. The first pitch, in September 2021, already describes coastal cities building out onto the water. In August the idea changes from a ceramic block to a compressed plant-fibre brick formed in a mould.", ["origin"]),
    ("Feb 2022", "SeaBrick Society incorporated", "A federal not-for-profit corporation is formed to hold the standard and the research record. Its purpose: to promote innovation and standards around environmentally sustainable marine infrastructure building materials.", ["society"]),
    ("Jan–Mar 2022", "First designs and first prints", "A 3D designer turns eight months of sketches into a brick; 3DSMITH in Vancouver prints the first ten-centimetre bricks within days. The first patent application is filed on 10 March 2022, with drawings of a whole family of shapes.", ["shape", "patent"]),
    ("2022", "Kelp fibre composites at UBC", "Six UBC Materials Engineering students take SeaBrick on as a Capstone project and make a kelp composite stronger than concrete. Its density, close to water, leads to a hollow-core brick.", ["mat"]),
    ("2023", "Kelpstone", "A sponsored research agreement with UBC's BioProducts Institute. The composite is named Kelpstone; small specimens test at around three times the compressive strength of concrete at half the weight. Three more Capstone teams join in the autumn. A small manufacturing space is leased on Venables Street.", ["mat"]),
    ("2023", "Recognition", "Accepted to the Third Derivative climate accelerator. Climate Spotlight winner at the Ocean Impact Pitchfest in Sydney. Nominated by Ashoka for the 2024 Earthshot Prize.", ["society"]),
    ("Oct 2023 – Sep 2024", "The hinge-lock", "The tongue-and-bump locking system is replaced by a hinge-lock concept, developed with 3D printing advisor Brady Kirk and designer Xiaoyuan Geng, and declared final for patent purposes in September 2024.", ["shape"]),
    ("2024", "Perth, sargassum and a waterproofing grant", "Materials work continues in Western Australia with a simpler process; sargassum proves to work as well as kelp. Canada's Ocean Supercluster funds a validation study of a mineral-based waterproofing method. Three further patent applications are filed on kelp processing and farming.", ["mat", "patent"]),
    ("2025", "Flax, hemp and a float test", "With seaweed fibre unobtainable at scale, flax and hemp from the Prairies are tested and perform at least as well. An eight-inch hexagonal brick moulded in two halves is float-tested in February. UBC students run the waterproofing study.", ["mat"]),
    ("Aug–Dec 2025", "The component brick", "The brick is redesigned in SolidWorks as a set of simpler moulded parts that assemble into one unit, solving the mould problem. A provisional patent on the new design is filed on 9 December 2025.", ["shape", "patent"]),
    ("Jan–Jun 2026", "A thousand model bricks", "About a thousand toy-scale bricks in some fifty types are printed. On 13 June 2026 friends and advisors spend an afternoon building with them to choose the first brick set.", ["shape", "community"]),
    ("Jul–Oct 2026", "Mineral foam and fibre", "The materials strategy moves to a mineral foam core with a dense mineral shell and short plant-fibre reinforcement. A marine validation programme is designed around density, water uptake, shrinkage and demoulding. In September the first production-oriented brick design, made for a compression press, is completed.", ["mat", "shape"]),
]
TAG_LABEL = {"origin": "Origin", "society": "Society", "shape": "Shape", "mat": "Materials", "patent": "Patents", "community": "Community"}


def story():
    items = ""
    for when, title, text, tags in TIMELINE:
        tg = "".join(f'<span class="tag {t if t in ("mat","shape") else ""}">{TAG_LABEL[t]}</span>' for t in tags)
        items += f'<div class="tl"><div class="when">{when}</div><h3>{title}</h3><p>{text}</p><div class="tags">{tg}</div></div>'
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Our story</div>
  <h1>Five years, one brick, several materials.</h1>
  <p class="lead">SeaBrick began in 2021 as an idea about kelp and coastlines. The brick has been through more than twenty versions and its material three stages since. This is the short version; the <a href="journal.html">journal</a> has the long one.</p>
</div></section>
<section class="band">
  <div class="wrap">
    <figure class="figure" style="max-width:1000px;margin:0 auto 40px"><a href="evolution.html"><img src="assets/evolution/strip.webp" alt="A row of brick designs from 2022 to 2026, rendered from the original design files" loading="lazy"></a><figcaption>How the brick's form evolved, 2022 to 2026, rendered from the original design files. <a href="evolution.html">See every generation</a>.</figcaption></figure>
    <div class="split" style="align-items:start">
      <div class="timeline">{items}</div>
      <div>
        <div class="card"><h3>The materials thread</h3><p>Three stages, one direction: a material that floats, lasts in seawater and costs the planet very little.</p>
        <table class="def" style="margin:1rem 0 0"><tr><th>2021–23</th><td>Kelp fibre composite ("Kelpstone"), with UBC</td></tr><tr><th>2025</th><td>Flax and hemp fibre composites</td></tr><tr><th>2026 →</th><td>Mineral foam core, mineral shell, plant-fibre reinforcement</td></tr></table>
        <p class="small muted" style="margin-top:12px"><a href="journal/mineral-foam-and-fibre.html">Where the strategy stands</a></p></div>
        <div class="card" style="margin-top:16px"><h3>The shape thread</h3><p>Square slab, a family of shapes, a hollow two-part brick, the hinge-lock, the component brick, a thousand toy bricks, and the final SeaBrick. <a href="evolution.html">The evolution page</a> shows each generation; <a href="journal/the-shape-of-a-brick.html">the journal</a> tells the story.</p></div>
        <div class="card" style="margin-top:16px"><h3>People</h3><p>The work has been carried by a founder, a changing cast of directors and CEOs, UBC faculty and students, independent engineers, 3D-printing and design collaborators, patent counsel and a community of advisors and supporters. Named contributors appear in the journal articles where their work is described.</p></div>
      </div>
    </div>
  </div>
</section>
"""
    return page("Our story", body, active="story.html")


def journal():
    cats = ["all"] + sorted({s["category"] for s in STORIES})
    filters = "".join(f'<button data-cat="{c}" aria-pressed="{"true" if c=="all" else "false"}">{"All" if c=="all" else c}</button>' for c in cats)
    posts = "".join(post_card(s) for s in sorted(STORIES, key=lambda s: s["date"], reverse=True))
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Journal</div>
  <h1>Marks of progress</h1>
  <p class="lead">Ten articles that follow SeaBrick from a research document in 2021 to the mineral-foam brick of 2026. They are written from the project's own records and dated by the period they cover.</p>
</div></section>
<section class="band"><div class="wrap">
  <div class="filters" role="group" aria-label="Filter by topic">{filters}</div>
  <div class="posts">{posts}</div>
</div></section>
"""
    return page("Journal", body, active="journal.html")


def article(s, prev, nxt):
    d = datetime.date.fromisoformat(s["date"]).strftime("%-d %B %Y") if sys.platform != "win32" else datetime.date.fromisoformat(s["date"]).strftime("%#d %B %Y")
    # images inside bodies are written relative to journal/ ("../assets/...")
    hero_img = f'<figure><img src="../{s["image"]}" alt="{html.escape(s["image_alt"])}"></figure>' if not s["image"].endswith(".svg") else f'<figure class="figure framed">{(DIST/s["image"]).read_text(encoding="utf-8")}</figure>'
    nav = ""
    if prev: nav += f'<a href="{prev["slug"]}.html">← {prev["title"]}</a>'
    else: nav += "<span></span>"
    if nxt: nav += f'<a href="{nxt["slug"]}.html">{nxt["title"]} →</a>'
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">{s["period"]} · {s["category"]}</div>
  <h1>{s["title"]}</h1>
  <p class="lead">{s["summary"]}</p>
</div></section>
<article class="prose">
{hero_img}
{s["body"]}
</article>
<nav class="post-nav">{nav}</nav>
"""
    return page(s["title"], body, active="journal.html", depth=1, description=s["summary"], og_image=s["image"])


def society():
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">The Society</div>
  <h1>SeaBrick Society</h1>
  <p class="lead">A Canadian not-for-profit corporation, formed in 2022, whose purpose is to promote innovation and standards around environmentally sustainable marine infrastructure building materials.</p>
</div></section>
<section class="band"><div class="wrap">
  <div class="facts">
    <div><b>17 February 2022</b><span>Incorporated under the Canada Not-for-profit Corporations Act</span></div>
    <div><b>1378929-2</b><span>Corporation number, Corporations Canada; registered extraprovincially in British Columbia</span></div>
    <div><b>{CITY.split(',')[0]}</b><span>Registered office in British Columbia, Canada</span></div>
  </div>
  <div class="split" style="margin-top:48px;align-items:start">
    <div>
      <h2 id="purpose">Purpose</h2>
      <blockquote style="border-left:3px solid var(--sea);padding-left:20px;color:var(--ocean-deep);font-size:1.1rem">To promote innovation and standards around environmentally sustainable marine infrastructure building materials.</blockquote>
      <p>The articles of incorporation also provide that the Society is carried on without the purpose of gain for its members, that any profits are used to further its purposes, that directors serve without remuneration, and that on dissolution any remaining property is distributed to qualified donees.</p>
      <h2 id="governance">Governance</h2>
      <p>The Society has one class of members, each entitled to notice of, attendance at and a vote at members' meetings. It is governed by a board of between one and ten directors, elected by the members, who serve without pay. Its financial year ends on 31 December and it files annual returns with Corporations Canada.</p>
      <h2>Relationship to other organisations</h2>
      <p>Commercial development of SeaBrick, including early fundraising, manufacturing trials and the kelp supply chain, has been carried by Kelp Island Inc., a related company formed in 2021. BioLith is the Society's commercial partner for production of SeaBrick and for other uses of the mineral-foam and fibre material now in development. The Society's role in each case is the same: to hold the standard and the public research record, and to make sure what is learned is available to anyone who wants to build with the system.</p>
      <div class="note blue"><strong>Not a registered charity.</strong> SeaBrick Society is a not-for-profit corporation, not a registered charity under the Income Tax Act. It does not issue charitable donation receipts, does not sell shares or memberships with financial returns, and does not pay dividends.</div>
    </div>
    <div>
      <div class="card" id="involved"><h3>Get involved</h3>
        <p><strong>Researchers and students.</strong> Materials, marine engineering, naval architecture, life-cycle assessment. There is a long list of questions and a short list of people.</p>
        <p><strong>Coastal communities and partners.</strong> If you need working infrastructure on the water, a float, a platform, a dock, and would consider a pilot, we would like to talk.</p>
        <p><strong>Builders and makers.</strong> The model bricks exist so that people can try the system. Open days and workshops are announced in the journal.</p>
        <p><a class="btn primary" href="contact.html">Contact the Society</a></p></div>
      <div class="card" style="margin-top:16px"><h3>Advisors and collaborators</h3>
        <p class="small">Over five years the project has drawn on materials engineers, marine engineers, an ocean architect, seaweed scientists, climate strategists and business advisors, as well as UBC faculty and more than thirty engineering students. Their contributions are credited in the journal articles that describe the work.</p></div>
    </div>
  </div>
</div></section>
"""
    return page("The Society", body, active="society.html")


def contact():
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Contact</div>
  <h1>Get in touch</h1>
  <p class="lead">Research collaborations, coastal pilots, students, press. We read everything, and we answer the ones we can help with.</p>
</div></section>
<section class="band"><div class="wrap split" style="align-items:start">
  <div>
    <h2>Write to us</h2>
    <p>Email the Society at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
    <p>{SITE_NAME}<br>{CITY}</p>
    <p class="small muted">This site has no contact form and sets no cookies. Nothing you send is shared with third parties.</p>
  </div>
  <div class="card"><h3>Before you write</h3>
    <ul>
      <li>SeaBrick is a research programme. There are no bricks for sale and no investment offering.</li>
      <li>Design files for the brick's connection features are not distributed. The 3D models on this site are smoothed visualization models for that reason.</li>
      <li>If you are a student or researcher, say which problem interests you: materials, joints, waves, life-cycle assessment or manufacturing.</li>
    </ul></div>
</div></section>
"""
    return page("Contact", body, active="contact.html")


def privacy():
    body = """
<section class="article-head"><div class="wrap"><div class="meta">Privacy</div><h1>Privacy</h1></div></section>
<section class="band"><div class="wrap narrow">
<p>This website is a set of static pages. It sets no cookies, runs no analytics, loads nothing from third-party servers and has no forms. If you email us, we keep your message to reply to it and do not share it.</p>
<p>Photographs of people on this site were taken at SeaBrick events and are used with the permission of the organiser. If you appear in one and would like it removed, write to us.</p>
</div></section>
"""
    return page("Privacy", body)


def notfound():
    body = """<section class="band"><div class="wrap center"><h1>Page not found</h1><p class="lead">That page has drifted. <a href="index.html">Back to the harbour.</a></p></div></section>"""
    return page("Not found", body)


# ------------------------------------------------------------------ build

def build():
    (DIST / "journal").mkdir(parents=True, exist_ok=True)
    out = {
        "index.html": index(), "mission.html": mission(), "technology.html": technology(), "story.html": story(),
        "journal.html": journal(), "society.html": society(), "evolution.html": evolution(), "builder.html": builder_page(), "connections-lab.html": lab_page(), "contact.html": contact(), "privacy.html": privacy(), "404.html": notfound(),
    }
    ordered = sorted(STORIES, key=lambda s: s["date"])
    for i, s in enumerate(ordered):
        out[f"journal/{s['slug']}.html"] = article(s, ordered[i - 1] if i else None, ordered[i + 1] if i + 1 < len(ordered) else None)
    for name, content in out.items():
        (DIST / name).write_text(content, encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    print(f"built {len(out)} pages into {DIST}")


if __name__ == "__main__":
    build()
