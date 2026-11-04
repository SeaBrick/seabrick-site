# -*- coding: utf-8 -*-
"""Static site builder for the SeaBrick Society website, version 4 (Tidal Paper system, John's feedback of 4 Nov 2026).

    python src/artwork.py   # (optional) regenerate SVG illustrations
    python src/build.py     # writes dist/*.html and dist/journal/*.html

Plain HTML/CSS/JS. The only outside requests are the Google Drive video embeds on the evolution page.
"""
import datetime, html, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = ROOT / "dist"
sys.path.insert(0, str(HERE))
from stories import STORIES  # noqa: E402
from artwork import icon  # noqa: E402
from evolution import ERAS  # noqa: E402
from media import VIDEOS, OLD_PHOTOS  # noqa: E402

SITE_NAME = "SeaBrick Society"
TAGLINE = "Building blocks for a rising sea"
PREVIEW_BAND = "Version 4 · local design preview · not published"
CONTACT_EMAIL = "john@seabrick.com"
CITY = "Vancouver, British Columbia, Canada"
MODELS_NOTE = "The 3D models shown are simplified versions of the brick."

NAV = [
    ("mission.html", "Mission"), ("technology.html", "Technology"),
    ("evolution.html", "Evolution"), ("builder.html", "Builder"),
    ("journal.html", "Journal"), ("society.html", "Society"),
]


def builder_embed(query, *, depth=0, height=520, title="SeaBrick builder"):
    """An embedded instance of the interactive builder (dist/app/builder.html)."""
    rel = "../" * depth
    return (f'<div class="embed"><iframe src="{rel}app/builder.html?{query}&embed=1" title="{html.escape(title)}" '
            f'loading="lazy" style="height:{height}px" allow="fullscreen"></iframe>'
            f'<div class="embed-foot"><span>Drag to turn · scroll to zoom · click a brick to name it</span>'
            f'<a href="{rel}app/builder.html?{query}">Open in the full builder ↗</a></div></div>')


def render_fig(name, caption, *, depth=0, cls="figure", alt=""):
    rel = "../" * depth
    return (f'<figure class="{cls}"><img src="{rel}assets/render/{name}.webp" alt="{html.escape(alt or caption)}" loading="lazy">'
            f'<figcaption>{caption}</figcaption></figure>')


def video_embed(v, depth=0):
    """A Google Drive video preview. The file must be shared with anyone who has the link."""
    return (f'<figure class="video"><div class="frame"><iframe src="https://drive.google.com/file/d/{v["id"]}/preview" '
            f'title="{html.escape(v["title"])}" loading="lazy" allow="autoplay; fullscreen" allowfullscreen></iframe></div>'
            f'<figcaption><b>{html.escape(v["title"])}</b> <span class="muted">{v["when"]}</span><br>{v["text"]}</figcaption></figure>')

# ------------------------------------------------------------------ layout

def page(title, body, *, active="", depth=0, description="", og_image="assets/img/party-gathering.webp"):
    rel = "../" * depth
    nav = "".join(
        f'<li><a href="{rel}{href}"{" class=\"active\"" if href == active else ""}>{label}</a></li>' for href, label in NAV
    )
    desc = html.escape(description or f"{SITE_NAME}: a low-cost, carbon-negative interlocking brick system for marine and flood-resistant infrastructure, and a nonprofit research program to build floating infrastructure that coastal communities can build themselves.")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {SITE_NAME}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{rel}{og_image}">
<link rel="icon" type="image/svg+xml" href="{rel}assets/favicon.svg">
<link rel="preload" href="{rel}assets/fonts/NotoSans-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/NotoSans-Bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/site.css">
<link rel="stylesheet" href="{rel}assets/site-additions.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="{rel}index.html" aria-label="SeaBrick Society home">
      <img src="{rel}assets/seabrick-logo.svg" alt="SeaBrick" width="200" height="36">
      <span class="sub">Nonprofit<br>research</span>
    </a>
    <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <ul class="menu">{nav}<li><a class="cta" href="{rel}contact.html">Contact</a></li></ul>
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
        <p>A nonprofit research society building low-cost, carbon-negative floating infrastructure for coastal communities facing rising seas.</p>
        <p class="small">{CITY}</p>
      </div>
      <div><h4>Explore</h4><ul>
        <li><a href="{rel}mission.html">Mission</a></li><li><a href="{rel}technology.html">Technology</a></li>
        <li><a href="{rel}evolution.html">Evolution</a></li><li><a href="{rel}builder.html">Builder</a></li></ul></div>
      <div><h4>Read</h4><ul>
        <li><a href="{rel}story.html">Our story</a></li><li><a href="{rel}journal.html">Journal</a></li>
        <li><a href="{rel}society.html">The Society</a></li><li><a href="{rel}contact.html">Contact</a></li></ul></div>
      <div><h4>Notes</h4><ul>
        <li><a href="{rel}privacy.html">Privacy</a></li>
        <li><a href="{rel}connections-lab.html">Connection lab</a></li></ul></div>
    </div>
    <div class="legal"><span>© {datetime.date.today().year} SeaBrick Society</span><span>{MODELS_NOTE}</span></div>
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
      <span class="eyebrow">SeaBrick Society · Nonprofit research</span>
      <h1>Building blocks for a <em>rising sea.</em></h1>
      <p class="lead">SeaBrick is a low-cost, carbon-negative interlocking brick system for marine and flood-resistant infrastructure. It is also a nonprofit research program to create sustainable floating infrastructure that coastal communities can build themselves: docks, platforms, breakwaters and the foundations of buildings that rise with the water instead of fighting it.</p>
      <div class="btn-row"><a class="btn primary" href="technology.html">Explore the technology</a><a class="textlink" href="builder.html">Try the builder ↗</a></div>
    </div>
    <figure class="hero-art hero-live"><iframe src="app/builder.html?scene=catalogue&shape=0&embed=1&hero=1&spin=1&colour=plain" title="The SeaBrick, turning slowly" loading="eager"></iframe><figcaption class="hero-note">The SeaBrick. Drag to turn it.</figcaption></figure>
  </div>
</section>

<section class="band" style="padding-top:0">
  <div class="wrap">
    <div class="recog">
      <div><b>Climate Spotlight Award</b><span>Ocean Impact Pitchfest 2023, to Kelp Island</span></div>
      <div><b>Third Derivative</b><span>Climate accelerator, Cohort 23-2, Kelp Island</span></div>
      <div><b>Earthshot Prize nominee</b><span>Nominated by Ashoka, 2024</span></div>
      <div><b>Ocean Supercluster</b><span>Grant for a waterproofing study</span></div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="routes">
      <article><span class="chapter-no">01 / Adapt</span><h2>Build out into the water.</h2><p>Rising seas will take the homes of hundreds of millions of people over the next thirty years. Floating infrastructure lets coastal communities build out onto the water, replacing land rather than losing it.</p><a href="mission.html">Why floating →</a></article>
      <article><span class="chapter-no">02 / Mitigate</span><h2>Carbon negative, not carbon heavy.</h2><p>Everything in the marine infrastructure market today is concrete, steel or petroleum. Cement alone is 9% of global emissions. A SeaBrick stores more carbon than it took to make.</p><a href="technology.html#materials">The material →</a></article>
      <article><span class="chapter-no">03 / Build</span><h2>Community ownership, community control.</h2><p>Bricks are made close to where they are used, in low-tech plants that ship in a container, and put together by hand. The tools for adaptation belong to the communities that need them.</p><a href="builder.html">Try the builder →</a></article>
    </div>
  </div>
</section>

<section class="band rule">
  <div class="wrap split">
    <div>
      <span class="eyebrow">The brick</span>
      <h2>One small shape. Any size of structure.</h2>
      <p>A SeaBrick is a hollow hexagon that floats. Bricks lock side to side into a mat that is strong but flexible, like chainmail. Courses stack, like Lego with hooked sides. Lay them flat for a platform. Stack them in rings for a tube or a tower. Tie the courses together with cables and the whole thing moves as one body in the water.</p>
      <div class="btn-row"><a class="btn primary" href="technology.html">How it fits together</a><a class="btn ghost" href="evolution.html">How it got here</a></div>
    </div>
    <figure class="figure threestate" id="threestate">
      <img src="assets/render/brick-hero.webp" alt="One SeaBrick" data-state="brick" class="on">
      <img src="assets/render/mat-1.webp" alt="A mat of nineteen SeaBricks" data-state="mat">
      <img src="assets/render/tower-hex.webp" alt="A hexagonal tower of SeaBricks" data-state="structure">
      <div class="states" role="group" aria-label="Show">
        <button type="button" data-state="brick" aria-pressed="true">A brick</button>
        <button type="button" data-state="mat" aria-pressed="false">A mat</button>
        <button type="button" data-state="structure" aria-pressed="false">A structure</button>
      </div>
      <figcaption><a href="builder.html">Build your own</a>.</figcaption>
    </figure>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Watch it go together</span><h2>Nineteen bricks to a course.</h2><p class="lead">Each course sits a little offset from the one below, so it bridges the joints. Drag to turn it, or open the full builder for tubes and towers.</p></div>
    {builder_embed("scene=mat&layers=3&play=1", height=480)}
  </div>
</section>

<section class="band rule">
  <div class="wrap split">
    <div>
      <span class="eyebrow">The material</span>
      <h2>A brick that turns to stone.</h2>
      <p>The material is a light mineral foam inside a dense mineral shell, with organic fibre throughout. The foam floats. The shell carries the load where bricks grip one another. The fibres mineralize over time into an internal scaffolding that gives the brick strength and flexibility, and the brick gets stronger as it ages.</p>
      <p>Fibre is where SeaBrick began, with kelp. <a href="technology.html#materials">Where the material stands now</a>.</p>
    </div>
    <figure class="figure"><img src="assets/img/kelpstone-cube-2.webp" alt="A pressed kelp composite test cube" loading="lazy"><figcaption>2023: a Kelpstone test cube from the UBC years.</figcaption></figure>
  </div>
</section>

<section class="band deep">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Journal</span><h2>Marks of progress</h2><p class="lead">Five years of work, one milestone at a time.</p></div>
    <div class="posts">{''.join(post_card(s) for s in latest)}</div>
    <p style="margin-top:32px"><a class="btn ghost" href="journal.html">Read the journal</a></p>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div>
      <span class="eyebrow">The Society</span>
      <h2>A nonprofit with one mission.</h2>
      <p class="lead">SeaBrick Society exists to build low-cost, climate-resilient infrastructure for the coastal communities that need it most. It was founded by John Richardson in 2022 and has drawn in dozens of engineers, designers, researchers and climate activists since.</p>
      <div class="btn-row"><a class="btn primary" href="society.html">About the Society</a><a class="btn ghost" href="contact.html">Get in touch</a></div>
    </div>
    <figure class="figure"><img src="assets/img/party-ring-held.webp" alt="A guest holding up a large ring assembled from model bricks" loading="lazy"><figcaption>The June 2026 SeaBrick party.</figcaption></figure>
  </div>
</section>
"""
    return page("Home", body, active="index.html")


def mission():
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Mission</div>
  <h1>Low-cost, climate-resilient infrastructure for a rising sea.</h1>
  <p class="lead">SeaBrick Society's mission is to build floating, water-resistant infrastructure that coastal communities facing rising sea levels can build and own themselves.</p>
</div></section>

<section class="band">
  <div class="wrap narrow prose-page">
    <h2>The water is coming, and concrete is the wrong answer</h2>
    <p>One third of the world's people live in coastal communities. Rising sea levels will destroy the homes of hundreds of millions of them over the next thirty years. Heat, fire and storms will displace billions more. We need low-cost ways of producing resilient infrastructure that does not rely on concrete.</p>
    <p>There are no renewable products in the marine infrastructure market. Everything is concrete, steel or petroleum. Cement production alone accounts for 9% of global CO2 emissions. The way we build in the sea is part of the problem it is meant to solve.</p>

    <h2>Build into the ocean instead of retreating from it</h2>
    <p>A floating structure rises with the water. It does not need deep foundations, a dry dock or heavy equipment. SeaBrick lets cities and coastal communities build out into the water, replacing land rather than losing it. Docks, platforms and breakwaters come first. Floating homes and whole communities come after. Bricks are just the means to that end.</p>

    <h2>Carbon negative, by design</h2>
    <p>Organic fibre is cellulose, and cellulose is about 40% carbon. Each SeaBrick stores more than its own weight in CO2, locked into a mineral matrix for the life of the structure. The opposite of floating concrete and steel.</p>

    <h2>A hard line on sustainability</h2>
    <p>The question we keep asking is how inexpensive and how scalable we can get while holding a hard line on sustainability. No petrochemicals as an input. No coatings that can shed microparticles into the sea. Materials that mineralize and strengthen over time instead of corroding. That line has cost us time. We keep it.</p>

    <h2>Community ownership, community control</h2>
    <p>The long-term vision is a decentralized, cooperative manufacturing ecosystem. Low-tech production plants that ship in a container to wherever they are needed, so that communities affected by climate change can build their own floating infrastructure from materials at hand. The tools for adaptation belong in the hands of the people most affected. Long-term ownership held by the communities themselves, and in Canada by Indigenous communities in particular.</p>

    <h2>What the Society does</h2>
    <div class="grid c2" style="margin:32px 0">
      {card("Research", "Materials, connections and marine durability, with university partners and independent engineers. We publish what we learn, including what did not work.", "hex")}
      {card("The standard", "What a SeaBrick is: its dimensions, its connections and its tests. The Society holds the form so that anyone can build with it.", "open")}
      {card("Pilots", "Small real structures with coastal partners: work floats, aquaculture platforms, docks. Working infrastructure first.", "wave")}
      {card("Community", "Open days, model bricks, students and advisors. A building system people can hold in their hands is one they can understand.", "people")}
    </div>
    <p>Where to from here? <a href="technology.html">The technology</a> shows how the bricks fit together. <a href="contact.html">Get in touch</a> if you want to build with them.</p>
  </div>
</section>
"""
    return page("Mission", body, active="mission.html")


# ---- technology, builder, connection lab
WAYS = [
    dict(id="bricks", n="01", name="One brick, six neighbours",
         embed="scene=catalogue&shape=0",
         text="Each brick locks to six neighbours in its course and to the courses above and below. The smooth side locking, together with the hexagonal geometry, gives connected bricks a structural fluidity: individual bricks are rigid, but an assembly flexes and absorbs the forces of the sea. Half bricks, edge bricks and bridges close the edges and tie the courses. <a href=\"connections-lab.html\">The connection lab</a> shows how a joint behaves under load.",
         photos=[("studio-hex-cluster", "Model bricks clustered around a central brick."), ("early-bowl", "Spring 2026: a bowl of model bricks in several shapes.")]),
    dict(id="mats", n="02", name="Floating mats",
         embed="scene=mat&layers=3&play=1",
         text="One course of bricks laid flat is a mat: a floating deck in any shape the hex grid allows, strong but flexible, like chainmail. Each course sits in one of three positions, A, B or C, so it bridges the joints below. Mats are the first things we will build: work floats, aquaculture platforms and docks.",
         photos=[("studio-mat", "A model mat, June 2026."), ("studio-mat-2", "Two stacked courses of a model mat.")]),
    dict(id="tubes", n="03", name="Tubes and towers",
         embed="scene=designer&preset=thickHex&layers=6",
         text="Bricks laid in a ring, course on course, make a hollow tube. Keep going and it is a tower. Tubes are stiff for their weight. At the SeaBrick party they were the first thing almost everyone built. In a floating structure they become pontoons, piles, culverts and the legs of a platform. Hollow bricks can be filled with rock for ballast.",
         photos=[("studio-ring", "A single-course model ring."), ("party-tower", "A model column with a platform on top.")]),
    dict(id="walls", n="04", name="Walls and enclosures",
         embed="scene=designer&preset=lowDodec",
         text="Straight runs of wall bricks between corners make the sides of an enclosure: a barge hull, a breakwater face, a tank for fish or seaweed. In the builder, gold marks the bricks whose flat faces form the wall.",
         photos=[("studio-house", "A model hut: walls, a platform and a roof."), ("party-frame", "A square frame built at the party.")]),
    dict(id="bridges", n="05", name="Bridging the courses",
         embed="scene=bridges&layers=4",
         text="A double-height brick spans two courses and ties them together, so a stack of rings behaves as one body rather than a pile of loose layers. Turn the bridges off in the builder and the courses come apart.",
         photos=[("party-column", "A model column built at the party."), ("party-tower-roof", "A roofed model tower.")]),
    dict(id="cables", n="06", name="Vertical tension cables", render="cables-corners", render2="cables-corners-top",
         caption="Cables run down through the holes at the corners, where three bricks meet.", caption2="Seen from above, every cable sits at a corner of the top course.",
         text="Bricks resist compression well and tension poorly. Vertical cables run through the holes at the corners of the bricks, from the top course to the bottom, and squeeze the courses tightly together. That turns a stack of loose layers into a rigid structure that carries point loads and holds together in a swell. Cables are tightened, inspected and replaced from above.",
         photos=[("studio-truss", "A model truss: beams and nodes."), ("party-wheel-2", "A spoked wheel assembled at the party.")]),
    dict(id="gel", n="07", name="Gel-sealed cavities", render="gel-joint",
         caption="Two bricks locked together, cut through the joint. The gel, in green, fills the gap between them.",
         text="Where two bricks lock together there is a gap. Fill that gap with a gel and let it harden, and the joint is sealed: the mat becomes watertight and the cavity between the bricks gives more buoyancy. Tension cables make the structure rigid; the gel makes it impermeable.",
         photos=[("studio-hex-ring", "A hexagonal model ring around a central void."), ("studio-platform", "A hexagonal model platform.")]),
]


def technology():
    tabs = "".join(f'<button role="tab" aria-selected="false" aria-controls="{w["id"]}"><span class="n">{w["n"]}</span>{w["name"]}</button>' for w in WAYS)
    panels = ""
    for w in WAYS:
        photos = "".join(f'<figure><img src="assets/img/{p}.webp" alt="{html.escape(c)}" loading="lazy"><figcaption>{c}</figcaption></figure>' for p, c in w["photos"])
        if w.get("embed"):
            visual = builder_embed(w["embed"], height=440, title=w["name"])
        else:
            visual = render_fig(w["render"], w["caption"], cls="figure framed")
            if w.get("render2"):
                visual = f'<div class="pair">{visual}{render_fig(w["render2"], w["caption2"], cls="figure framed")}</div>'
        panels += (f'<div class="panel" id="{w["id"]}" role="tabpanel"><h3>{w["name"]}</h3><p>{w["text"]}</p>{visual}'
                   f'<div class="photo">{photos}</div><p class="small muted" style="margin-top:14px">Photos: model bricks, 2026.</p></div>')
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Technology</div>
  <h1>A brick, and a system for building with it.</h1>
  <p class="lead">On its own a SeaBrick is a small thing. Locked to thousands of others it is a platform, a breakwater, a dock or a foundation. This page has two parts: <a href="#geometry">the shape</a> and how bricks fit together, and <a href="#materials">the material</a>. How both got here is on the <a href="evolution.html">evolution</a> page.</p>
</div></section>

<section class="band" id="geometry">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 1</span><h2>Geometry and design</h2></div>
    <div class="split">
      <figure class="figure"><img src="assets/render/brick-hero.webp" alt="The SeaBrick" width="1023" height="934"><figcaption>The SeaBrick, final design, 2026. {MODELS_NOTE}</figcaption></figure>
      <div>
        <span class="eyebrow">The unit</span>
        <h3>Hexagonal, hollow, buoyant.</h3>
        <p>A SeaBrick is a hexagon about one and a half times as wide as it is tall. Hexagons tile with no gaps and give every brick six equal neighbours. Each side locks smoothly to the next brick. The top and bottom register with the course above and below. The hollow inside makes it float; the dense shell carries the loads where bricks meet.</p>
        <p>A brick is moulded in one cycle, so it can be made in a small plant close to where it is used. The design has been through more than twenty versions since 2022. <a href="evolution.html">The evolution page</a> shows them.</p>
        <ul class="pill-list"><li>Floats</li><li>Locks to six neighbours</li><li>Stacks in courses</li><li>Moulded, not machined</li><li>Replaceable one at a time</li></ul>
        <div class="triple"><img src="assets/render/brick-top.webp" alt="SeaBrick seen from above"><img src="assets/render/brick-side.webp" alt="SeaBrick seen from the side"><img src="assets/render/tube-small-top.webp" alt="A small ring of bricks seen from above, coloured by brick type"></div>
      </div>
    </div>
  </div>
</section>

<section class="band rule">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">The system</span><h2>Seven ways to build with SeaBrick</h2><p class="lead">The same brick, arranged seven ways. The 3D views are live. Drag to turn, scroll to zoom, click a brick to name it.</p></div>
    <div class="explorer">
      <div class="tabs" role="tablist" aria-label="Ways to build">{tabs}</div>
      {panels}
    </div>
    <p style="margin-top:24px"><a class="btn primary" href="builder.html">Open the full builder</a> <a class="btn ghost" href="connections-lab.html">Open the connection lab</a></p>
  </div>
</section>

<section class="band rule" id="materials">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 2</span><h2>Material technology</h2></div>
    <div class="section-head"><span class="eyebrow">Materials</span><h2>A light mineral core, a dense mineral shell, organic fibre throughout.</h2>
    <p class="lead">The material has two jobs that pull against each other. It has to float, and it has to carry the forces that pass between bricks. We give each job to a different part of the brick.</p></div>
    <div class="grid c3">
      {card("Core", "A low-density mineral foam. It supplies most of the buoyancy. The lighter the core, the more a structure can carry.")}
      {card("Shell", "A denser mineral layer that protects the core and carries contact loads, thickest where bricks grip one another. A mineral coating goes over it.")}
      {card("Fibre", "Organic fibre remains an important part of the composite. The fibres mineralize into an internal scaffolding which gives the brick strength and flexibility. Flax, hemp and kelp all work.")}
    </div>
    <figure class="figure" style="margin-top:40px">{(DIST/'assets/art/materials.svg').read_text(encoding='utf-8')}<figcaption>Kelp fibre composites (2021 to 2023), flax and hemp (2025), and mineral foam with fibre (2026). <a href="journal/mineral-foam-and-fibre.html">Read more</a>, or see <a href="evolution.html#materials">how the material evolved</a>.</figcaption></figure>
    <h3 style="margin-top:48px">Why mineral</h3>
    <p class="narrow" style="margin:0">Mineral binders cure without the clinker that gives Portland cement its carbon footprint, and seawater does not eat them the way it eats reinforced concrete. Mineralizing agents mixed with the fibres crystallize as water slowly permeates, so the brick becomes a self-healing, stone-like matrix and gets stronger with age. The fibre inside is sequestered carbon: each brick stores more than its own weight in CO2.</p>
  </div>
</section>
"""
    return page("Technology", body, active="technology.html", description="The SeaBrick: its geometry, seven ways to build with it, an interactive builder, and the mineral foam and fibre material.")


def builder_page():
    body = f"""
<section class="article-head compact"><div class="wrap">
  <div class="meta">Builder</div>
  <h1>Build with SeaBrick</h1>
  <p class="lead">Put mats, tubes, towers and bridged courses together from the brick family, one course at a time. {MODELS_NOTE}</p>
</div></section>
<section class="band" style="padding-top:0">
  <div class="wrap wide">
    {builder_embed("scene=mat&layers=3&bar=0&panel=1", height=760, title="SeaBrick builder")}
    <div class="grid c2" style="margin-top:32px">
      {card("What it shows", "Where each brick goes and which shape it is. How courses offset (A, B, C) and how rings close. Colour by course or by shape. Pull the courses apart. Watch an assembly go together one brick at a time. Save a picture of any view.")}
      {card("Units", "Sizes are in brick pitches. One pitch is the distance between the centres of two neighbouring bricks. A course is one brick tall. Tube radius runs from the centre to a flat wall. For joints under load, see the <a href=\"connections-lab.html\">connection lab</a>.")}
    </div>
  </div>
</section>
"""
    return page("Builder", body, active="builder.html", description="An interactive builder for assembling SeaBrick mats, tubes, towers and bridged courses.")


def lab_page():
    body = f"""
<section class="article-head compact"><div class="wrap">
  <div class="meta">Connection lab</div>
  <h1>How two bricks hold on to each other</h1>
  <p class="lead">A joint model on a small mat. Push or lift one brick, change how the mat is supported, and watch how the connections respond. {MODELS_NOTE}</p>
</div></section>
<section class="band" style="padding-top:0">
  <div class="wrap wide">
    <div class="embed lab"><iframe id="labframe" src="app/connections-lab/index.html" title="SeaBrick connection lab" loading="lazy" style="height:760px"></iframe>
    <div class="embed-foot"><span>Choose an example from the menu on the left. The lab runs in your browser.</span><a href="app/connections-lab/index.html">Open the lab on its own ↗</a></div></div>
  </div>
</section>
"""
    return page("Connection lab", body, active="technology.html", description="A two-brick joint model showing how SeaBrick connections respond to force and support.")


def evolution():
    eras = ""
    for era in ERAS:
        pics = "".join(f'<figure><img src="assets/evolution/{lid.replace("jewel", "brick")}.webp" alt="{html.escape(cap)}" loading="lazy"><figcaption>{cap}</figcaption></figure>' for lid, cap, cam in era["items"]) if era.get("public", True) else ""
        eras += (f'<article class="era" id="{era["id"]}"><div><div class="when">{era["when"]}</div><h3>{era["title"]}</h3><p>{era["text"]}</p>'
                 f'<p class="people">{era["people"]}</p></div>' + (f'<div class="pics">{pics}</div>' if pics else '<div class="pics empty"><p class="small muted">' + era.get("note", "No brick design files from this year; the work was in moulds and hand-cast prototypes.") + '</p></div>') + '</article>')
    videos = "".join(video_embed(v) for v in VIDEOS)
    photos = "".join(f'<figure><img src="assets/img/old/{p["file"]}" alt="{html.escape(p["alt"])}" loading="lazy"><figcaption><b>{p["when"]}</b> {p["caption"]}</figcaption></figure>' for p in OLD_PHOTOS)
    photo_block = f"""
    <div class="section-head" style="margin-top:64px"><span class="eyebrow">Photographs</span><h2>The bricks you could hold</h2><p class="lead">Prints, moulds and cast prototypes, from the first ten-centimetre print to the toy family.</p></div>
    <div class="oldphotos">{photos}</div>""" if OLD_PHOTOS else ""
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Evolution</div>
  <h1>How the brick got its shape, and its material.</h1>
  <p class="lead">Two threads run through five years of SeaBrick. One is the shape: more than twenty versions between January 2022 and the final design of 2026, each rendered here from its original design file. The other is the material: kelp, then flax and hemp, then mineral foam and fibre.</p>
</div></section>

<section class="band" id="shape">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 1</span><h2>Geometry and design, 2022 to 2026</h2></div>
    <figure class="figure" style="margin-bottom:28px"><img src="assets/evolution/strip.webp" alt="Four brick designs in a row, from the first square of January 2022 to the final SeaBrick of 2026" loading="lazy"><figcaption>Four of the generations, each rendered from its design file.</figcaption></figure>
    <div class="turning">
      <h3>Five turning points</h3>
      <ol>
        <li><b>January 2022: a square brick.</b> The first 3D model, printed within days at ten centimetres. <a href="#2022-first">More</a></li>
        <li><b>November 2022: the hexagon.</b> Six equal neighbours and no long straight joints. Every design since has been a hexagon. <a href="#2022-hexagon">More</a></li>
        <li><b>October 2023: the hinge-lock.</b> Bricks that join with a turn instead of force. Declared final for the patent in September 2024. <a href="#2024-hingelock">More</a></li>
        <li><b>January 2025: two moulded halves.</b> The brick becomes parts that assemble, which solves the mould. A toy version at one centimetre follows and becomes a kit of fifty shapes. <a href="#2025-component">More</a></li>
        <li><b>August to October 2026: the final SeaBrick.</b> A production design for a press, and a family of shapes drawn from it. <a href="#2026-final">More</a></li>
      </ol>
    </div>

    <div class="section-head" style="margin-top:56px"><span class="eyebrow">Walkthroughs</span><h2>Watch the brick explained</h2><p class="lead">Videos John has made over the years to show how the bricks lock. The most recent shows the final locking system.</p></div>
    <div class="videos">{videos}</div>
    {photo_block}

    <div class="section-head" style="margin-top:64px"><span class="eyebrow">Every generation</span><h2>The full chronology</h2><p class="lead">Era by era, with the design files rendered.</p></div>
    <div class="eras">{eras}</div>
    <p class="small muted" style="margin-top:20px">Renders are made from the project's archived design files, in the orientation of the original file. Early files were drawn to be printed at a fifth to a sixteenth of full size.</p>
  </div>
</section>

<section class="band rule" id="materials">
  <div class="wrap">
    <div class="part-head"><span class="part">Part 2</span><h2>Material technology, 2021 to 2026</h2></div>
    <div class="split" style="align-items:start">
      <div>
        <h3>2021 to 2023: kelp</h3>
        <p>SeaBrick began as an idea about kelp: a feedstock that grows two feet a day and stores carbon, harvested and pressed into a building block. Six UBC Materials Engineering students took it on as a Capstone project in 2022 and made a kelp fibre composite stronger than concrete in compression. A research agreement with UBC's BioProducts Institute followed. The composite was named Kelpstone, and small specimens reached three times the compressive strength of concrete at half the weight. Its density, close to water, is why the brick became hollow.</p>
        <h3>2024 to 2025: other fibres, and keeping water out</h3>
        <p>Work in Western Australia showed that sargassum worked as well as kelp, with a simpler process. When seaweed fibre could not be bought at the scale a pilot needed, flax and hemp from the Prairies were tested in 2025 and maxed out the compression press. In parallel, an Ocean Supercluster grant funded a study of a mineral waterproofing method that needs no petrochemicals and sheds no microparticles.</p>
        <h3>2026: mineral foam and fibre</h3>
        <p>The current material turns the composite inside out. A low-density mineral foam core gives buoyancy. A dense mineral shell carries the loads where bricks meet. Organic fibre runs through both and mineralizes over time into an internal scaffolding that gives strength and flexibility. The brick turns to stone, and gets stronger as it does. <a href="journal/mineral-foam-and-fibre.html">Where the material stands</a>.</p>
      </div>
      <div>
        <div class="mat-strip">
          <figure><img src="assets/img/ubc-kelp-drying.webp" alt="Kelp drying on racks" loading="lazy"><figcaption>2022: kelp feedstock drying at UBC.</figcaption></figure>
          <figure><img src="assets/img/kelpstone-cube.webp" alt="A pressed kelp composite cube" loading="lazy"><figcaption>2023: a Kelpstone test cube.</figcaption></figure>
          <figure><img src="assets/img/ubc-mould-feedstock.webp" alt="A mould being filled with composite feedstock" loading="lazy"><figcaption>2023: filling a mould.</figcaption></figure>
        </div>
        <figure class="figure" style="margin-top:16px">{(DIST/'assets/art/materials.svg').read_text(encoding='utf-8')}<figcaption>Three stages, one direction: a material that floats, lasts in seawater and stores carbon.</figcaption></figure>
        <table class="def" style="margin-top:16px"><tr><th>2021–23</th><td>Kelp fibre composite ("Kelpstone"), with UBC</td></tr><tr><th>2024–25</th><td>Sargassum; flax and hemp; mineral waterproofing study</td></tr><tr><th>2026 →</th><td>Mineral foam core, mineral shell, mineralizing fibre</td></tr></table>
      </div>
    </div>
  </div>
</section>
"""
    return page("Evolution", body, active="evolution.html", description="How the SeaBrick's shape evolved through more than twenty versions from 2022 to 2026, with walkthrough videos and renders from the original design files, and how its material moved from kelp to mineral foam and fibre.")


TIMELINE = [
    ("2021", "An idea called Kelp Island", "A research document about building coastal infrastructure from kelp becomes a project. The first pitch, in September 2021, already describes coastal cities building out onto the water. In August the idea changes from a ceramic block to a compressed plant-fibre brick formed in a mould.", ["origin"]),
    ("Feb 2022", "SeaBrick Society incorporated", "A nonprofit is formed to hold the brick and the research. Its purpose: to promote innovation and standards around environmentally sustainable marine infrastructure building materials.", ["society"]),
    ("Jan–Mar 2022", "First designs and first prints", "A 3D designer turns eight months of sketches into a brick; 3DSMITH in Vancouver prints the first ten-centimetre bricks within days. The first patent application is filed on 10 March 2022, with drawings of a whole family of shapes.", ["shape", "patent"]),
    ("2022", "Kelp fibre composites at UBC", "Six UBC Materials Engineering students take SeaBrick on as a Capstone project and make a kelp composite stronger than concrete. Its density, close to water, leads to a hollow brick.", ["mat"]),
    ("2023", "Kelpstone", "A sponsored research agreement with UBC's BioProducts Institute. The composite is named Kelpstone; small specimens test at three times the compressive strength of concrete at half the weight. Three more Capstone teams join in the autumn. A small manufacturing space is leased on Venables Street.", ["mat"]),
    ("2023", "Recognition", "Accepted to the Third Derivative climate accelerator. Climate Spotlight winner at the Ocean Impact Pitchfest in Sydney. Nominated by Ashoka for the 2024 Earthshot Prize.", ["society"]),
    ("Oct 2023 – Sep 2024", "The hinge-lock", "The tongue-and-bump lock is replaced by a hinge-lock, developed with 3D printing advisor Brady Kirk and designer Xiaoyuan Geng, and declared final for patent purposes in September 2024.", ["shape"]),
    ("2024", "Perth, sargassum and a waterproofing grant", "Materials work continues in Western Australia with a simpler process; sargassum proves to work as well as kelp. Canada's Ocean Supercluster funds a study of a mineral waterproofing method. Three further patent applications are filed on kelp processing and farming.", ["mat", "patent"]),
    ("2025", "Flax, hemp and a float test", "With seaweed fibre unobtainable at scale, flax and hemp from the Prairies are tested and max out the press. An eight-inch hexagonal brick moulded in two halves is float-tested in February. UBC students run the waterproofing study.", ["mat"]),
    ("Aug–Dec 2025", "The component brick", "The brick is redesigned in SolidWorks as a set of simpler moulded parts that assemble into one unit, solving the mould problem. A provisional patent on the new design is filed on 9 December 2025.", ["shape", "patent"]),
    ("Jan–Jun 2026", "A thousand model bricks", "About a thousand toy-scale bricks in some fifty types are printed. On 13 June 2026 friends and advisors spend an afternoon building with them to choose the first brick set.", ["shape", "community"]),
    ("Jul–Oct 2026", "Mineral foam and fibre", "The material moves to a mineral foam core with a dense mineral shell and mineralizing fibre. In September the first production brick design, made for a compression press, is completed.", ["mat", "shape"]),
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
    <figure class="figure" style="max-width:1000px;margin:0 auto 40px"><a href="evolution.html"><img src="assets/evolution/strip.webp" alt="A row of brick designs from 2022 to 2026, rendered from the original design files" loading="lazy"></a><figcaption>How the brick's form evolved, 2022 to 2026. <a href="evolution.html">See every generation</a>.</figcaption></figure>
    <div class="split" style="align-items:start">
      <div class="timeline">{items}</div>
      <div>
        <div class="card"><h3>The materials thread</h3><p>Three stages, one direction: a material that floats, lasts in seawater and stores carbon.</p>
        <table class="def" style="margin:16px 0 0"><tr><th>2021–23</th><td>Kelp fibre composite ("Kelpstone"), with UBC</td></tr><tr><th>2025</th><td>Flax and hemp fibre composites</td></tr><tr><th>2026 →</th><td>Mineral foam core, mineral shell, mineralizing fibre</td></tr></table>
        <p class="small muted" style="margin-top:12px"><a href="journal/mineral-foam-and-fibre.html">Where the material stands</a></p></div>
        <div class="card" style="margin-top:32px"><h3>The shape thread</h3><p>Square slab, a family of shapes, a hollow two-part brick, the hinge-lock, the component brick, a thousand toy bricks, and the final SeaBrick. <a href="evolution.html">The evolution page</a> shows each generation; <a href="journal/the-shape-of-a-brick.html">the journal</a> tells the story.</p></div>
        <div class="card" style="margin-top:32px"><h3>People</h3><p>Dozens of engineers, designers, researchers and climate activists have carried the work, with UBC faculty and more than twenty engineering students. They are named in the journal articles that describe what they did.</p></div>
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
  <p class="lead">Ten articles that follow SeaBrick from a research document in 2021 to the mineral-foam brick of 2026, written from the project's own records.</p>
</div></section>
<section class="band"><div class="wrap">
  <div class="filters" role="group" aria-label="Filter by topic">{filters}</div>
  <div class="posts">{posts}</div>
</div></section>
"""
    return page("Journal", body, active="journal.html")


def article(s, prev, nxt):
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
<div class="wrap"><article class="prose">
{hero_img}
{s["body"]}
</article>
<nav class="post-nav">{nav}</nav></div>
"""
    return page(s["title"], body, active="journal.html", depth=1, description=s["summary"], og_image=s["image"])


def society():
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">The Society</div>
  <h1>SeaBrick Society</h1>
  <p class="lead">A Canadian nonprofit with one mission: low-cost, climate-resilient infrastructure for the coastal communities that need it most.</p>
</div></section>
<section class="band"><div class="wrap narrow prose-page">
  <h2>What we are</h2>
  <p>SeaBrick Society is a federally incorporated Canadian not-for-profit, based in Vancouver. It holds the SeaBrick brick and coordinates the research, the partnerships and the testing that will take it from a model on a table to infrastructure on the water. BioLith is the Society's commercial partner for production of SeaBrick and for other uses of the mineral-foam and fibre material now in development.</p>
  <h2>What we are for</h2>
  <p>Floating, water-resistant infrastructure that coastal communities facing rising seas can build and own themselves. Docks, platforms and breakwaters first. Then the foundations of homes and communities that rise with the water instead of fighting it. Carbon negative, made from materials at hand, in plants small enough to ship in a container. <a href="mission.html">The mission</a> says why.</p>
  <h2>Work with us</h2>
  <p>Researchers and students: materials, marine engineering, naval architecture, manufacturing. Coastal communities and partners: if you need working infrastructure on the water and would consider a pilot, we would like to talk. Builders and makers: the model bricks exist so that people can try the system. <a href="contact.html">Get in touch</a>.</p>
  <hr>
  <p class="small muted">SeaBrick Society was founded by John Richardson in 2022. It has attracted the interest and support of dozens of engineers, designers, researchers and climate activists, along with funding support from government and charitable organizations including the Government of British Columbia, Canada's Ocean Supercluster, Third Derivative and the Ocean Impact Organization.</p>
</div></section>
"""
    return page("The Society", body, active="society.html")


def contact():
    body = f"""
<section class="article-head"><div class="wrap">
  <div class="meta">Contact</div>
  <h1>Get in touch</h1>
  <p class="lead">Research partners, coastal communities, students, press. We read everything.</p>
</div></section>
<section class="band"><div class="wrap narrow">
  <h2>Write to us</h2>
  <p>Email the Society at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
  <p>{SITE_NAME}<br>{CITY}</p>
  <p>If you are a student or researcher, say which problem interests you: materials, joints, waves or manufacturing. If you are a coastal community, tell us what you need on the water.</p>
</div></section>
"""
    return page("Contact", body, active="contact.html")


def privacy():
    body = """
<section class="article-head"><div class="wrap"><div class="meta">Privacy</div><h1>Privacy</h1></div></section>
<section class="band"><div class="wrap narrow">
<p>This website is a set of static pages. It sets no cookies and runs no analytics. The videos on the evolution page are played from Google Drive, which may set its own cookies when you play one. If you email us, we keep your message to reply to it.</p>
<p>Photographs of people on this site were taken at SeaBrick events. If you appear in one and would like it removed, write to us.</p>
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
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://seabrick.com/sitemap.xml\n", encoding="utf-8")
    (DIST / "CNAME").write_text("seabrick.com\n", encoding="utf-8")
    (DIST / ".nojekyll").touch()
    pages = sorted(q for q in DIST.rglob("*.html") if q.name != "404.html" and "app" not in q.relative_to(DIST).parts)
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>https://seabrick.com/{q.relative_to(DIST).as_posix().replace('index.html', '')}</loc><lastmod>{today}</lastmod></url>\n" for q in pages)
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n', encoding="utf-8")
    print(f"built {len(out)} pages into {DIST}")


if __name__ == "__main__":
    build()
