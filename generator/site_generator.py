from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
import re


def esc(value):
    return escape(str(value or ''))


def slugify(value):
    return re.sub(r'[^a-z0-9]+', '-', str(value or '').lower()).strip('-') or 'section'


def render_items(items, card_class='webify-card'):
    out=[]
    for i,item in enumerate(items or []):
        item = item if isinstance(item, dict) else {'title':str(item),'text':''}
        out.append(f'''<article class="{card_class} reveal"><div class="card-number">{esc(item.get('meta') or f'{i+1:02d}')}</div><h3>{esc(item.get('title'))}</h3><p>{esc(item.get('text'))}</p></article>''')
    return ''.join(out)


def render_pricing(items):
    cards=[]
    for i,item in enumerate(items or []):
        item=item if isinstance(item,dict) else {'title':str(item)}
        feats=[x.strip() for x in str(item.get('meta','')).split(';') if x.strip()]
        features=''.join(f'<li>✓ {esc(x)}</li>' for x in feats)
        cards.append(f'''<article class="pricing-card reveal"><span class="plan-index">PLAN {i+1:02d}</span><h3>{esc(item.get('title'))}</h3><div class="price">{esc(item.get('text'))}</div><ul>{features}</ul><a class="webify-button" href="#contact">Choose plan →</a></article>''')
    return ''.join(cards)


def render_team(items):
    return ''.join(f'''<article class="team-card reveal"><div class="avatar">{esc(str(i.get('title','?'))[:1].upper())}</div><h3>{esc(i.get('title'))}</h3><p>{esc(i.get('text'))}</p><span>{esc(i.get('meta','TEAM'))}</span></article>''' for i in (items or []))


def render_gallery(items):
    cards=[]
    for idx,item in enumerate(items or []):
        item=item if isinstance(item,dict) else {'title':str(item)}
        cards.append(f'''<article class="gallery-card reveal"><div class="gallery-visual gallery-{(idx%6)+1}"><span>{idx+1:02d}</span></div><div class="gallery-caption"><strong>{esc(item.get('title'))}</strong><small>{esc(item.get('text') or 'Visual showcase')}</small></div></article>''')
    return ''.join(cards)


def render_testimonials(items):
    return ''.join(f'''<article class="testimonial-card reveal"><div class="quote">“</div><blockquote>{esc(i.get('title'))}</blockquote><div class="author">{esc(i.get('meta') or 'Customer')}</div></article>''' for i in (items or []))


def render_section(section):
    sid=slugify(section.get('id') or section.get('title') or 'section')
    typ=section.get('type','content')
    items=section.get('items') or []
    heading=f'''<div class="section-heading reveal"><span class="eyebrow">{esc(section.get('eyebrow') or typ.upper())}</span><h2>{esc(section.get('title'))}</h2><p>{esc(section.get('description'))}</p></div>'''
    if typ=='contact':
        return f'''<section class="webify-section contact-section" id="{sid}"><div class="webify-container contact-layout"><div class="contact-copy reveal">{heading}</div><form class="webify-form reveal" onsubmit="submitWebifyForm(event)"><input required placeholder="Your name"><input required type="email" placeholder="Email address"><input placeholder="Phone number"><textarea required placeholder="Tell us about your requirement..."></textarea><button class="webify-button" type="submit">{esc(section.get('cta') or 'Send Message')} →</button><div id="webify-form-message"></div></form></div></section>'''
    if typ=='pricing':
        return f'''<section class="webify-section" id="{sid}"><div class="webify-container">{heading}<div class="pricing-grid">{render_pricing(items)}</div></div></section>'''
    if typ=='team':
        return f'''<section class="webify-section" id="{sid}"><div class="webify-container">{heading}<div class="team-grid">{render_team(items)}</div></div></section>'''
    if typ=='gallery':
        return f'''<section class="webify-section" id="{sid}"><div class="webify-container">{heading}<div class="gallery-grid">{render_gallery(items)}</div></div></section>'''
    if typ=='testimonials':
        return f'''<section class="webify-section" id="{sid}"><div class="webify-container">{heading}<div class="testimonial-grid">{render_testimonials(items)}</div></div></section>'''
    cards=render_items(items)
    return f'''<section class="webify-section section-{slugify(typ)}" id="{sid}"><div class="webify-container">{heading}{f'<div class="card-grid">{cards}</div>' if cards else ''}</div></section>'''


def make_html(plan, requirements):
    style=plan.get('visual_style') or {}
    hero=plan.get('hero') or {}
    footer=plan.get('footer') or {}
    seo=plan.get('seo') or {}
    name=esc(plan.get('title') or 'Webify Website')
    css_vars={
        'brand':style.get('primary') or requirements.get('primary_color') or '#6C4CFF',
        'secondary':style.get('secondary') or '#F0ECFF','accent':style.get('accent') or '#8B76FF',
        'background':style.get('background') or '#FAFAFC','surface':style.get('surface') or '#FFFFFF',
        'ink':style.get('text') or '#111216','muted':style.get('muted') or '#6B6F78',
        'heading-font':style.get('heading_font') or 'Space Grotesk','body-font':style.get('body_font') or 'DM Sans',
        'radius':style.get('radius') or '20px'
    }
    nav_items=plan.get('navigation') or ['Home','Contact']
    nav=''.join(f'<a href="#{"home" if str(x).lower()=="home" else slugify(x)}">{esc(x)}</a>' for x in nav_items)
    sections=''.join(render_section(s) for s in (plan.get('sections') or []))
    socials=''.join(f'<a href="#contact">{esc(x)}</a>' for x in (footer.get('socials') or footer.get('links') or []))
    vars_css=';'.join(f'--{k}:{esc(v)}' for k,v in css_vars.items())
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(seo.get('description') or plan.get('summary'))}"><meta name="keywords" content="{esc(', '.join(seo.get('keywords') or []))}"><title>{esc(seo.get('title') or name)}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="style.css"></head><body style="{vars_css}"><header class="webify-header"><div class="webify-container nav"><a class="webify-logo" href="#home">{name}</a><button class="menu-button" aria-label="Open navigation" onclick="toggleWebifyMenu()">☰</button><nav id="webify-nav">{nav}</nav></div></header><main><section class="webify-hero" id="home"><div class="hero-glow"></div><div class="webify-container hero-container"><div class="hero-content reveal"><span class="hero-badge">✦ {esc(hero.get('badge') or 'BUILT WITH WEBIFY')}</span><h1>{esc(hero.get('headline') or f'Welcome to {name}')}</h1><p>{esc(hero.get('subtitle') or plan.get('summary',''))}</p><div class="hero-actions"><a class="webify-button" href="#contact">{esc(hero.get('primary_cta') or plan.get('cta') or 'Get Started')} →</a>{f'<a class="secondary-button" href="#about">{esc(hero.get("secondary_cta"))}</a>' if hero.get('secondary_cta') else ''}</div></div></div></section>{sections}</main><footer class="webify-footer"><div class="webify-container footer-content"><div><strong>{name}</strong><p>{esc(footer.get('description') or plan.get('summary',''))}</p></div><div class="footer-links">{socials}</div><div>{esc(footer.get('copyright') or f'© {plan.get("title","Webify")}. All rights reserved.')}</div></div></footer><script src="script.js"></script></body></html>'''


def make_css():
    return r'''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--background);color:var(--ink);font-family:var(--body-font),sans-serif}a{color:inherit;text-decoration:none}.webify-container{width:min(1180px,92%);margin:auto}.webify-header{position:sticky;top:0;z-index:100;background:color-mix(in srgb,var(--background) 88%,transparent);backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,0,0,.07)}.nav{min-height:76px;display:flex;align-items:center;justify-content:space-between}.webify-logo{font:700 1.25rem var(--heading-font),sans-serif}.webify-logo:before{content:"✦";color:var(--brand);margin-right:8px}#webify-nav{display:flex;gap:28px;align-items:center}#webify-nav a{color:var(--muted);font-weight:600;transition:.25s}#webify-nav a:hover{color:var(--brand)}.menu-button{display:none;border:0;background:none;font-size:1.5rem}.webify-hero{position:relative;overflow:hidden;min-height:700px;display:grid;place-items:center;background:radial-gradient(circle at 82% 18%,color-mix(in srgb,var(--brand) 25%,transparent),transparent 32%),linear-gradient(135deg,#101114,#211d2b);color:#fff}.hero-glow{position:absolute;width:520px;height:520px;background:var(--brand);filter:blur(160px);opacity:.15;right:-180px;top:-180px}.hero-container{position:relative;z-index:2}.hero-content{max-width:950px}.hero-badge{display:inline-flex;padding:9px 14px;border:1px solid #ffffff26;border-radius:999px;color:#e9e5f5;font-size:.76rem;font-weight:800;letter-spacing:.12em}.hero h1{font:700 clamp(3.5rem,8vw,7.5rem)/.94 var(--heading-font),sans-serif;letter-spacing:-.07em;margin:25px 0;max-width:1000px}.hero p{max-width:720px;font-size:1.2rem;line-height:1.8;color:#c8c5cf}.hero-actions{display:flex;gap:14px;margin-top:32px;flex-wrap:wrap}.webify-button,.secondary-button{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:15px 22px;border-radius:13px;font-weight:800;transition:.25s;border:0;cursor:pointer}.webify-button{background:var(--brand);color:#fff;box-shadow:0 15px 35px color-mix(in srgb,var(--brand) 28%,transparent)}.webify-button:hover{transform:translateY(-3px)}.secondary-button{border:1px solid #ffffff24;background:#ffffff10;color:#fff}.webify-section{padding:110px 0;border-bottom:1px solid rgba(0,0,0,.07)}.section-heading{max-width:800px;margin-bottom:45px}.eyebrow{color:var(--brand);font-size:.76rem;font-weight:900;letter-spacing:.16em}.section-heading h2,.contact-copy h2{font:700 clamp(2.3rem,5vw,4.7rem)/1 var(--heading-font),sans-serif;letter-spacing:-.055em;margin:14px 0}.section-heading p,.contact-copy p{color:var(--muted);line-height:1.8;font-size:1.05rem}.card-grid,.pricing-grid,.team-grid,.gallery-grid,.testimonial-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}.webify-card,.pricing-card,.team-card,.gallery-card,.testimonial-card{background:var(--surface);border:1px solid rgba(0,0,0,.07);border-radius:var(--radius,20px);transition:.3s}.webify-card{padding:30px;min-height:220px}.webify-card:hover,.pricing-card:hover,.team-card:hover,.gallery-card:hover,.testimonial-card:hover{transform:translateY(-7px);box-shadow:0 25px 70px rgba(0,0,0,.09)}.card-number,.plan-index{color:var(--brand);font-size:.75rem;font-weight:900;letter-spacing:.1em}.webify-card h3,.pricing-card h3,.team-card h3{font:700 1.4rem var(--heading-font),sans-serif}.webify-card p,.team-card p{color:var(--muted);line-height:1.7}.pricing-card{padding:30px}.pricing-card .price{font:700 2.2rem var(--heading-font);margin:18px 0}.pricing-card ul{padding:0;list-style:none;color:var(--muted);line-height:2}.pricing-card .webify-button{margin-top:15px}.team-card{padding:28px;text-align:center}.avatar{width:70px;height:70px;border-radius:50%;display:grid;place-items:center;margin:0 auto 18px;background:var(--secondary);color:var(--brand);font:700 1.6rem var(--heading-font)}.team-card span{font-size:.75rem;color:var(--brand);font-weight:800;letter-spacing:.12em}.gallery-card{overflow:hidden}.gallery-visual{height:220px;display:grid;place-items:center;background:linear-gradient(135deg,var(--brand),#111);color:#fff;font:700 3rem var(--heading-font)}.gallery-2{background:linear-gradient(135deg,#111,#755fff)}.gallery-3{background:linear-gradient(135deg,#211d2b,#c2a0ff)}.gallery-4{background:linear-gradient(135deg,#3b2d54,#111)}.gallery-5{background:linear-gradient(135deg,#111,#9d83ff)}.gallery-6{background:linear-gradient(135deg,#625080,#17131f)}.gallery-caption{padding:20px}.gallery-caption strong,.gallery-caption small{display:block}.gallery-caption small{color:var(--muted);margin-top:5px}.testimonial-card{padding:30px}.quote{font:700 4rem/1 var(--heading-font);color:var(--brand)}blockquote{margin:0;font:600 1.2rem/1.6 var(--heading-font)}.author{margin-top:20px;color:var(--muted);font-weight:700}.contact-layout{display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:start}.webify-form{display:grid;gap:14px}.webify-form input,.webify-form textarea{width:100%;padding:16px;border:1px solid rgba(0,0,0,.1);border-radius:12px;background:var(--surface);color:var(--ink);font:inherit}.webify-form textarea{min-height:160px;resize:vertical}#webify-form-message{color:var(--brand);font-weight:700}.webify-footer{padding:42px 0}.footer-content{display:flex;justify-content:space-between;gap:30px;color:var(--muted);flex-wrap:wrap}.footer-content strong{color:var(--ink);font-family:var(--heading-font)}.footer-links{display:flex;gap:14px;flex-wrap:wrap}.footer-links a:hover{color:var(--brand)}.reveal{animation:webifyReveal .7s ease both}@keyframes webifyReveal{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}@media(max-width:760px){.menu-button{display:block;color:var(--ink)}#webify-nav{display:none;position:absolute;top:76px;left:0;right:0;padding:20px;background:var(--surface);flex-direction:column;align-items:flex-start;border-bottom:1px solid rgba(0,0,0,.08)}#webify-nav.open{display:flex}.webify-hero{min-height:620px}.hero h1{font-size:clamp(3rem,15vw,5rem)}.contact-layout{grid-template-columns:1fr;gap:40px}.webify-section{padding:75px 0}.footer-content{flex-direction:column}}
'''


def make_js():
    return r'''function toggleWebifyMenu(){const nav=document.getElementById("webify-nav");if(nav)nav.classList.toggle("open");}function submitWebifyForm(event){event.preventDefault();const message=document.getElementById("webify-form-message");if(message)message.textContent="Thanks! Your message has been received.";event.target.reset();}document.addEventListener("click",e=>{const a=e.target.closest("#webify-nav a");if(a){const nav=document.getElementById("webify-nav");if(nav)nav.classList.remove("open");}});'''


def build_website_zip(plan, requirements):
    html=make_html(plan,requirements); css=make_css(); js=make_js(); memory=BytesIO()
    with ZipFile(memory,'w',ZIP_DEFLATED) as archive:
        archive.writestr('index.html',html); archive.writestr('style.css',css); archive.writestr('script.js',js); archive.writestr('README.md','# Webify Website\n\nGenerated by Webify AI Website Builder.\n\nOpen index.html to preview the website.\n')
    return {'title':plan.get('title','Webify Website'),'summary':plan.get('summary',''),'slug':plan.get('slug') or 'webify-site','html':html,'css':css,'js':js,'zip_bytes':memory.getvalue(),'files':['index.html','style.css','script.js','README.md']}
