from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
import re


def esc(value):
    return escape(str(value or ""))


def slugify(value):
    return re.sub(
        r"[^a-z0-9]+",
        "-",
        str(value).lower()
    ).strip("-")


# ============================================================
# CARD GENERATOR
# ============================================================

def render_items(items):

    output = ""

    for item in items or []:

        output += f"""
        <article class="webify-card reveal">

            <div class="card-number">
                {esc(item.get("meta", ""))}
            </div>

            <h3>
                {esc(item.get("title", ""))}
            </h3>

            <p>
                {esc(item.get("text", ""))}
            </p>

        </article>
        """

    return output


# ============================================================
# SECTION GENERATOR
# ============================================================

def render_section(section):

    sid = (
        section.get("id")
        or slugify(
            section.get(
                "title",
                "section"
            )
        )
    )

    section_type = section.get(
        "type",
        "content"
    )

    items = section.get(
        "items",
        []
    )

    cards = render_items(items)

    # --------------------------------------------------------
    # SERVICES / CARDS
    # --------------------------------------------------------

    if section_type in (
        "services",
        "featured_items",
        "features",
        "products"
    ):

        return f"""
        <section
            class="webify-section section-{section_type}"
            id="{sid}"
        >

            <div class="webify-container">

                <div class="section-heading reveal">

                    <span class="eyebrow">
                        {esc(section.get("eyebrow", ""))}
                    </span>

                    <h2>
                        {esc(section.get("title", ""))}
                    </h2>

                    <p>
                        {esc(section.get("description", ""))}
                    </p>

                </div>

                <div class="card-grid">

                    {cards}

                </div>

            </div>

        </section>
        """


    # --------------------------------------------------------
    # TESTIMONIALS
    # --------------------------------------------------------

    if section_type == "testimonials":

        return f"""
        <section
            class="webify-section testimonials"
            id="{sid}"
        >

            <div class="webify-container">

                <div class="section-heading reveal">

                    <span class="eyebrow">
                        {esc(section.get("eyebrow", "TESTIMONIALS"))}
                    </span>

                    <h2>
                        {esc(section.get("title", ""))}
                    </h2>

                </div>

                <div class="testimonial-grid">

                    {cards}

                </div>

            </div>

        </section>
        """


    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    if section_type == "contact":

        return f"""
        <section
            class="webify-section contact-section"
            id="{sid}"
        >

            <div class="webify-container contact-layout">

                <div class="contact-copy reveal">

                    <span class="eyebrow">
                        {esc(section.get("eyebrow", "CONTACT"))}
                    </span>

                    <h2>
                        {esc(section.get("title", "Let's talk"))}
                    </h2>

                    <p>
                        {esc(section.get("description", ""))}
                    </p>

                </div>


                <form
                    class="webify-form reveal"
                    onsubmit="submitWebifyForm(event)"
                >

                    <input
                        required
                        placeholder="Your name"
                    >

                    <input
                        required
                        type="email"
                        placeholder="Email address"
                    >

                    <input
                        placeholder="Phone number"
                    >

                    <textarea
                        required
                        placeholder="Tell us about your requirement..."
                    ></textarea>

                    <button
                        class="webify-button"
                        type="submit"
                    >
                        {esc(
                            section.get(
                                "cta",
                                "Send Message"
                            )
                        )}
                        →
                    </button>

                    <div
                        id="webify-form-message"
                    ></div>

                </form>

            </div>

        </section>
        """


    # --------------------------------------------------------
    # DEFAULT CONTENT SECTION
    # --------------------------------------------------------

    return f"""
    <section
        class="webify-section"
        id="{sid}"
    >

        <div class="webify-container">

            <div class="content-section reveal">

                <span class="eyebrow">
                    {esc(section.get("eyebrow", ""))}
                </span>

                <h2>
                    {esc(section.get("title", ""))}
                </h2>

                <p>
                    {esc(section.get("description", ""))}
                </p>

            </div>

        </div>

    </section>
    """


# ============================================================
# HTML GENERATOR
# ============================================================

def make_html(plan, requirements):

    style = plan.get(
        "visual_style",
        {}
    )

    hero = plan.get(
        "hero",
        {}
    )

    name = esc(
        plan.get(
            "title",
            "Webify Website"
        )
    )

    primary = style.get(
        "primary",
        "#6C4CFF"
    )

    secondary = style.get(
        "secondary",
        "#ECE8FF"
    )

    accent = style.get(
        "accent",
        "#8B76FF"
    )

    background = style.get(
        "background",
        "#FAFAFC"
    )

    surface = style.get(
        "surface",
        "#FFFFFF"
    )

    text = style.get(
        "text",
        "#111216"
    )

    muted = style.get(
        "muted",
        "#6B6F78"
    )

    heading_font = style.get(
        "heading_font",
        "Space Grotesk"
    )

    body_font = style.get(
        "body_font",
        "DM Sans"
    )


    navigation = ""

    for item in plan.get(
        "navigation",
        []
    ):

        target = (
            "home"
            if str(item).lower() == "home"
            else slugify(item)
        )

        navigation += f"""
        <a href="#{target}">
            {esc(item)}
        </a>
        """


    sections = ""

    for section in plan.get(
        "sections",
        []
    ):

        sections += render_section(
            section
        )


    footer = plan.get(
        "footer",
        {}
    )


    return f"""
<!doctype html>

<html lang="en">

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
    {esc(
        plan.get(
            "seo",
            {}
        ).get(
            "title",
            name
        )
    )}
</title>

<meta
    name="description"
    content="{esc(
        plan.get(
            "seo",
            {}
        ).get(
            "description",
            plan.get("summary", "")
        )
    )}"
>

<meta
    name="keywords"
    content="{esc(
        ", ".join(
            plan.get(
                "seo",
                {}
            ).get(
                "keywords",
                []
            )
        )
    )}"
>


<link
    rel="preconnect"
    href="https://fonts.googleapis.com"
>

<link
    href="https://fonts.googleapis.com/css2?
family=DM+Sans:wght@400;500;600;700&
family=Space+Grotesk:wght@500;600;700&
family=Playfair+Display:wght@500;600;700
&display=swap"
    rel="stylesheet"
>

<link
    rel="stylesheet"
    href="style.css"
>

</head>


<body
    style="
        --brand:{esc(primary)};
        --secondary:{esc(secondary)};
        --accent:{esc(accent)};
        --background:{esc(background)};
        --surface:{esc(surface)};
        --ink:{esc(text)};
        --muted:{esc(muted)};
        --heading-font:'{esc(heading_font)}';
        --body-font:'{esc(body_font)}';
    "
>


<header class="webify-header">

    <div class="webify-container nav">

        <a
            class="webify-logo"
            href="#home"
        >
            {name}
        </a>

        <button
            class="menu-button"
            onclick="toggleWebifyMenu()"
        >
            ☰
        </button>

        <nav id="webify-nav">

            {navigation}

        </nav>

    </div>

</header>


<main>


<section
    class="webify-hero"
    id="home"
>

    <div class="hero-glow"></div>

    <div class="webify-container hero-container">

        <div class="hero-content reveal">

            <span class="hero-badge">
                ✦ {esc(
                    hero.get(
                        "badge",
                        "WELCOME"
                    )
                )}
            </span>

            <h1>
                {esc(
                    hero.get(
                        "headline",
                        "Build something remarkable."
                    )
                )}
            </h1>

            <p>
                {esc(
                    hero.get(
                        "subtitle",
                        plan.get(
                            "summary",
                            ""
                        )
                    )
                )}
            </p>

            <div class="hero-actions">

                <a
                    class="webify-button"
                    href="#contact"
                >
                    {esc(
                        hero.get(
                            "primary_cta",
                            "Get Started"
                        )
                    )}
                    →
                </a>

                {
                    f'''
                    <a
                        class="secondary-button"
                        href="#about"
                    >
                        {esc(
                            hero.get(
                                "secondary_cta"
                            )
                        )}
                    </a>
                    '''
                    if hero.get(
                        "secondary_cta"
                    )
                    else ""
                }

            </div>

        </div>

    </div>

</section>


{sections}


</main>


<footer class="webify-footer">

    <div class="webify-container footer-content">

        <div>

            <strong>
                {name}
            </strong>

            <p>
                {esc(
                    footer.get(
                        "description",
                        ""
                    )
                )}
            </p>

        </div>

        <div>

            {esc(
                footer.get(
                    "copyright",
                    ""
                )
            )}

        </div>

    </div>

</footer>


<script src="script.js"></script>

</body>

</html>
"""


# ============================================================
# CSS
# ============================================================

def make_css():

    return r"""
*{
    box-sizing:border-box;
}

html{
    scroll-behavior:smooth;
}

body{
    margin:0;
    background:var(--background);
    color:var(--ink);
    font-family:var(--body-font),sans-serif;
}

a{
    color:inherit;
    text-decoration:none;
}

.webify-container{
    width:min(1180px,92%);
    margin:auto;
}

.webify-header{
    position:sticky;
    top:0;
    z-index:100;
    background:color-mix(
        in srgb,
        var(--background) 88%,
        transparent
    );
    backdrop-filter:blur(20px);
    border-bottom:1px solid rgba(0,0,0,.07);
}

.nav{
    min-height:76px;
    display:flex;
    align-items:center;
    justify-content:space-between;
}

.webify-logo{
    font-family:var(--heading-font);
    font-size:1.25rem;
    font-weight:700;
}

#webify-nav{
    display:flex;
    gap:28px;
    align-items:center;
}

#webify-nav a{
    color:var(--muted);
    font-weight:600;
    transition:.25s;
}

#webify-nav a:hover{
    color:var(--brand);
}

.menu-button{
    display:none;
    border:0;
    background:none;
    font-size:1.5rem;
}


.webify-hero{
    position:relative;
    overflow:hidden;
    min-height:680px;
    display:grid;
    place-items:center;
    background:
        radial-gradient(
            circle at 80% 20%,
            color-mix(
                in srgb,
                var(--brand) 25%,
                transparent
            ),
            transparent 32%
        ),
        var(--background);
}

.hero-glow{
    position:absolute;
    width:500px;
    height:500px;
    background:var(--brand);
    filter:blur(160px);
    opacity:.12;
    right:-200px;
    top:-180px;
}

.hero-container{
    position:relative;
    z-index:2;
}

.hero-content{
    max-width:900px;
}

.hero-badge{
    display:inline-flex;
    padding:9px 14px;
    border-radius:999px;
    background:var(--secondary);
    color:var(--brand);
    font-size:.78rem;
    font-weight:800;
    letter-spacing:.12em;
}

.hero h1{
    font-family:var(--heading-font);
    font-size:clamp(
        3.5rem,
        8vw,
        7.5rem
    );
    line-height:.94;
    letter-spacing:-.07em;
    margin:25px 0;
    max-width:1000px;
}

.hero p{
    max-width:700px;
    font-size:1.2rem;
    line-height:1.8;
    color:var(--muted);
}

.hero-actions{
    display:flex;
    gap:14px;
    margin-top:32px;
    flex-wrap:wrap;
}

.webify-button,
.secondary-button{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    padding:15px 22px;
    border-radius:13px;
    font-weight:800;
    transition:.25s;
}

.webify-button{
    background:var(--brand);
    color:#fff;
    box-shadow:0 15px 35px
        color-mix(
            in srgb,
            var(--brand) 28%,
            transparent
        );
}

.webify-button:hover{
    transform:translateY(-3px);
}

.secondary-button{
    border:1px solid rgba(0,0,0,.1);
    background:var(--surface);
}


.webify-section{
    padding:110px 0;
    border-bottom:1px solid rgba(0,0,0,.07);
}

.section-heading{
    max-width:800px;
    margin-bottom:45px;
}

.eyebrow{
    color:var(--brand);
    font-size:.76rem;
    font-weight:900;
    letter-spacing:.16em;
}

.section-heading h2,
.content-section h2,
.contact-copy h2{
    font-family:var(--heading-font);
    font-size:clamp(
        2.3rem,
        5vw,
        4.7rem
    );
    line-height:1;
    letter-spacing:-.055em;
    margin:14px 0;
}

.section-heading p,
.content-section p,
.contact-copy p{
    color:var(--muted);
    line-height:1.8;
    font-size:1.05rem;
}


.card-grid{
    display:grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(240px,1fr)
        );
    gap:18px;
}

.webify-card{
    background:var(--surface);
    border:1px solid rgba(0,0,0,.07);
    border-radius:var(--radius,20px);
    padding:30px;
    min-height:220px;
    transition:.3s;
}

.webify-card:hover{
    transform:translateY(-7px);
    box-shadow:
        0 25px 70px rgba(0,0,0,.09);
}

.card-number{
    color:var(--brand);
    font-size:.78rem;
    font-weight:800;
    margin-bottom:25px;
}

.webify-card h3{
    font-family:var(--heading-font);
    font-size:1.4rem;
}

.webify-card p{
    color:var(--muted);
    line-height:1.7;
}


.testimonial-grid{
    display:grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(280px,1fr)
        );
    gap:20px;
}


.contact-layout{
    display:grid;
    grid-template-columns:
        1fr 1fr;
    gap:80px;
    align-items:start;
}

.webify-form{
    display:grid;
    gap:14px;
}

.webify-form input,
.webify-form textarea{
    width:100%;
    padding:16px;
    border:1px solid rgba(0,0,0,.1);
    border-radius:12px;
    background:var(--surface);
    color:var(--ink);
    font:inherit;
}

.webify-form textarea{
    min-height:160px;
    resize:vertical;
}

#webify-form-message{
    color:var(--brand);
    font-weight:700;
}


.webify-footer{
    padding:40px 0;
}

.footer-content{
    display:flex;
    justify-content:space-between;
    gap:30px;
    color:var(--muted);
}

.footer-content strong{
    color:var(--ink);
    font-family:var(--heading-font);
}

.reveal{
    animation:webifyReveal .7s ease both;
}

@keyframes webifyReveal{
    from{
        opacity:0;
        transform:translateY(20px);
    }
    to{
        opacity:1;
        transform:translateY(0);
    }
}


@media(max-width:760px){

    .menu-button{
        display:block;
    }

    #webify-nav{
        display:none;
        position:absolute;
        top:76px;
        left:0;
        right:0;
        padding:20px;
        background:var(--surface);
        flex-direction:column;
        align-items:flex-start;
        border-bottom:1px solid rgba(0,0,0,.08);
    }

    #webify-nav.open{
        display:flex;
    }

    .webify-hero{
        min-height:600px;
    }

    .hero h1{
        font-size:clamp(
            3rem,
            15vw,
            5rem
        );
    }

    .contact-layout{
        grid-template-columns:1fr;
        gap:40px;
    }

    .webify-section{
        padding:75px 0;
    }

    .footer-content{
        flex-direction:column;
    }
}
"""


# ============================================================
# JAVASCRIPT
# ============================================================

def make_js():

    return r"""
function toggleWebifyMenu(){

    const nav =
        document.getElementById(
            "webify-nav"
        );

    nav.classList.toggle(
        "open"
    );
}


function submitWebifyForm(event){

    event.preventDefault();

    const message =
        document.getElementById(
            "webify-form-message"
        );

    message.textContent =
        "Thanks! Your message has been received.";

    event.target.reset();
}
"""


# ============================================================
# ZIP
# ============================================================

def build_website_zip(
    plan,
    requirements
):

    html = make_html(
        plan,
        requirements
    )

    css = make_css()

    js = make_js()

    memory = BytesIO()

    with ZipFile(
        memory,
        "w",
        ZIP_DEFLATED
    ) as archive:

        archive.writestr(
            "index.html",
            html
        )

        archive.writestr(
            "style.css",
            css
        )

        archive.writestr(
            "script.js",
            js
        )

        archive.writestr(
            "README.md",
            """# Webify Website

Generated by Webify AI Website Builder.

Files:
- index.html
- style.css
- script.js

Open index.html to preview the website.
"""
        )

    return {

        "title":
            plan.get(
                "title",
                "Webify Website"
            ),

        "summary":
            plan.get(
                "summary",
                ""
            ),

        "slug":
            plan.get(
                "slug",
                "webify-site"
            ),

        "html":
            html,

        "zip_bytes":
            memory.getvalue(),

        "files": [
            "index.html",
            "style.css",
            "script.js",
            "README.md"
        ]
    }