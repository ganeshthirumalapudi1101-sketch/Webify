import json
import os
import re
from config import AI_PROVIDER, OPENAI_MODEL, GROQ_MODEL


def _extract_json(text):
    text = re.sub(r'^```(?:json)?\s*', '', str(text).strip(), flags=re.I)
    text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r'\{.*\}', text, re.S)
        if match:
            return json.loads(match.group(0))
        raise


def _call_llm(system, user):
    if AI_PROVIDER in ('auto', 'openai') and os.getenv('OPENAI_API_KEY'):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.2,
                response_format={'type': 'json_object'},
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user},
                ],
            )
            return _extract_json(response.choices[0].message.content)
        except Exception:
            if AI_PROVIDER == 'openai':
                raise

    if AI_PROVIDER in ('auto', 'groq') and os.getenv('GROQ_API_KEY'):
        try:
            from groq import Groq
            client = Groq(api_key=os.environ['GROQ_API_KEY'])
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                temperature=0.2,
                response_format={'type': 'json_object'},
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user},
                ],
            )
            return _extract_json(response.choices[0].message.content)
        except Exception:
            if AI_PROVIDER == 'groq':
                raise

    return None


def _lines(value):
    return [x.strip() for x in str(value or '').splitlines() if x.strip()]


def _parse_pipe_lines(value, widths=3):
    rows = []
    for line in _lines(value):
        parts = [p.strip() for p in line.split('|')]
        while len(parts) < widths:
            parts.append('')
        rows.append(parts[:widths])
    return rows


def _apply_user_content_to_plan(plan, requirements):
    """Deterministically preserve important form answers after the LLM response."""
    plan = dict(plan or {})
    req = requirements or {}
    sections = list(plan.get('sections') or [])

    name = str(req.get('business_name') or plan.get('title') or 'Your Business').strip()
    plan['title'] = name
    plan['slug'] = plan.get('slug') or re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'webify-site'

    if req.get('business_description'):
        plan['summary'] = str(req['business_description']).strip()

    if req.get('cta'):
        plan['cta'] = str(req['cta']).strip()
        hero = dict(plan.get('hero') or {})
        hero['primary_cta'] = str(req['cta']).strip()
        plan['hero'] = hero

    if req.get('primary_color'):
        style = dict(plan.get('visual_style') or {})
        style['primary'] = req['primary_color']
        plan['visual_style'] = style

    if req.get('tagline'):
        hero = dict(plan.get('hero') or {})
        hero.setdefault('badge', 'WELCOME')
        hero['subtitle'] = str(req['tagline']).strip()
        plan['hero'] = hero

    def upsert(section_type, title, description, items):
        nonlocal sections
        if not items:
            return
        existing = next((s for s in sections if s.get('type') == section_type), None)
        payload = {
            'id': section_type,
            'type': section_type,
            'eyebrow': section_type.replace('_', ' ').upper(),
            'title': title,
            'description': description,
            'items': items,
        }
        if existing:
            existing.update(payload)
        else:
            sections.append(payload)

    features = _lines(req.get('features') or req.get('special_features'))
    if features:
        upsert('features', 'What makes us different', 'Key capabilities and benefits selected for this website.', [
            {'title': x.split('|')[0].strip(), 'text': x.split('|', 1)[1].strip() if '|' in x else 'Add a concise benefit description.', 'meta': f'{i+1:02d}'}
            for i, x in enumerate(features[:8])
        ])

    testimonials = _parse_pipe_lines(req.get('testimonials'), 2)
    if testimonials:
        upsert('testimonials', 'What our customers say', 'Real feedback provided for the website.', [
            {'title': f'“{q}”', 'text': '', 'meta': author or 'Customer'} for q, author in testimonials[:8]
        ])

    team = _parse_pipe_lines(req.get('team'), 2)
    if team:
        upsert('team', 'Meet the team', 'Introduce the people behind the organization.', [
            {'title': person, 'text': role, 'meta': 'TEAM'} for person, role in team[:12]
        ])

    pricing = _parse_pipe_lines(req.get('pricing'), 3)
    if pricing:
        items = []
        for i, row in enumerate(pricing[:6]):
            features_text = row[2]
            items.append({'title': row[0], 'text': row[1], 'meta': features_text})
        upsert('pricing', 'Plans that fit your needs', 'Clear options based on the pricing information you supplied.', items)

    gallery = _lines(req.get('gallery'))
    if gallery:
        upsert('gallery', 'A closer look', 'Visual highlights selected for the website.', [
            {'title': x, 'text': 'Visual showcase', 'meta': f'{i+1:02d}'} for i, x in enumerate(gallery[:12])
        ])

    if req.get('services'):
        services = _lines(req.get('services'))
        existing = next((s for s in sections if s.get('type') in ('services', 'products')), None)
        if services and not existing:
            sections.append({
                'id': 'services', 'type': 'services', 'eyebrow': 'SERVICES',
                'title': 'What we do', 'description': 'Explore the services and solutions available.',
                'items': [{'title': x.split('|')[0].strip(), 'text': x.split('|',1)[1].strip() if '|' in x else 'Add a concise description of this offering.', 'meta': f'{i+1:02d}'} for i,x in enumerate(services[:8])]
            })

    if req.get('contact'):
        existing = next((s for s in sections if s.get('type') == 'contact'), None)
        if not existing:
            sections.append({'id': 'contact', 'type': 'contact', 'eyebrow': 'CONTACT', 'title': 'Let’s work together', 'description': str(req['contact']), 'items': [], 'cta': req.get('cta') or 'Send Message'})
        else:
            existing['description'] = str(req['contact'])
            existing['cta'] = req.get('cta') or existing.get('cta') or 'Send Message'

    # Avoid duplicate IDs and guarantee contact for a usable website.
    seen = set()
    clean = []
    for section in sections:
        sid = section.get('id') or re.sub(r'[^a-z0-9]+', '-', str(section.get('title', 'section')).lower()).strip('-')
        if sid in seen:
            continue
        section['id'] = sid
        seen.add(sid)
        clean.append(section)
    if 'contact' not in seen:
        clean.append({'id': 'contact', 'type': 'contact', 'eyebrow': 'CONTACT', 'title': 'Ready to start?', 'description': 'Tell us what you need and we will get back to you.', 'items': [], 'cta': req.get('cta') or 'Send Message'})

    plan['sections'] = clean
    pages = req.get('pages') or []
    if isinstance(pages, list) and pages:
        plan['navigation'] = pages
    elif not plan.get('navigation'):
        plan['navigation'] = ['Home'] + [s.get('title', s.get('id','')) for s in clean if s.get('type') != 'contact'] + ['Contact']
    else:
        nav = list(plan.get('navigation') or [])
        if 'Home' not in nav:
            nav.insert(0, 'Home')
        if 'Contact' not in nav:
            nav.append('Contact')
        plan['navigation'] = nav

    footer = dict(plan.get('footer') or {})
    if req.get('footer_note'):
        footer['copyright'] = req['footer_note']
    if req.get('socials'):
        footer['socials'] = _lines(req.get('socials'))
    footer.setdefault('description', plan.get('summary', ''))
    footer.setdefault('copyright', f'© {name}. All rights reserved.')
    plan['footer'] = footer
    return plan


def analyze_idea(idea):
    system = '''You are Webify's senior requirements analyst and UX researcher. Study the business idea and create a tailored questionnaire, not a generic form. Infer the business category, customer journey, required pages, content, conversion goals, visual direction, functionality and SEO needs. Ask only questions that materially improve the final website. For a restaurant/cafe ask about menu, hours, location, reservations and gallery. For SaaS ask about product, features, pricing, integrations, demo/trial and customer proof. For portfolio ask about projects, services, skills, experience and contact. For real estate ask about properties, locations, filters, agents and enquiry flow. Always include structured fields for features, testimonials, team, pricing, gallery and social links when relevant.
Return JSON only: {summary, assumptions, questions:[{id,label,type,options,help,default}]}.'''
    result = _call_llm(system, idea)
    return result or fallback_analysis(idea)


def fallback_analysis(idea):
    text = idea.lower()
    business_type = 'business'
    if any(x in text for x in ['coffee', 'cafe', 'café']): business_type = 'coffee_shop'
    elif any(x in text for x in ['restaurant', 'bakery', 'food']): business_type = 'restaurant'
    elif any(x in text for x in ['saas', 'software', 'platform', 'app']): business_type = 'saas'
    elif any(x in text for x in ['real estate', 'property', 'properties']): business_type = 'real_estate'
    elif any(x in text for x in ['portfolio', 'designer', 'developer', 'photographer']): business_type = 'portfolio'

    questions = [
        {'id':'business_name','label':'Business / organization name','type':'text','default':'','help':'Name shown in the header, hero and footer.'},
        {'id':'tagline','label':'Tagline / one-line promise','type':'text','default':'','help':'A short memorable value statement.'},
        {'id':'business_description','label':'What do you do?','type':'textarea','default':idea,'help':'Explain the business, service, product or mission.'},
        {'id':'audience','label':'Who is the website for?','type':'textarea','default':'','help':'Describe the target customers or visitors.'},
        {'id':'pages','label':'Pages / sections required','type':'multiselect','options':['Home','About','Services','Products','Projects','Portfolio','Testimonials','Pricing','FAQ','Blog','Gallery','Contact'],'default':['Home','About','Services','Contact']},
        {'id':'services','label':'Services / products','type':'textarea','default':'','help':'One per line. You can use Title | short description.'},
        {'id':'features','label':'Key features / highlights','type':'textarea','default':'','help':'One per line. These become benefit/feature cards.'},
        {'id':'testimonials','label':'Testimonials','type':'textarea','default':'','help':'One per line as Quote | Author.'},
        {'id':'team','label':'Team members','type':'textarea','default':'','help':'One per line as Name | Role.'},
        {'id':'pricing','label':'Pricing plans','type':'textarea','default':'','help':'One per line as Plan | Price | Feature1; Feature2; Feature3.'},
        {'id':'gallery','label':'Gallery / project images','type':'textarea','default':'','help':'One caption or image description per line.'},
        {'id':'cta','label':'Primary call-to-action','type':'text','default':'Get Started','help':'Example: Book a Call, Reserve a Table, Request Quote.'},
        {'id':'contact','label':'Contact information','type':'textarea','default':'','help':'Email, phone, address, WhatsApp, opening hours, etc.'},
        {'id':'socials','label':'Social links','type':'textarea','default':'','help':'One per line: Instagram, LinkedIn, YouTube, etc.'},
        {'id':'visual_style','label':'Visual style','type':'select','options':['Premium & minimal','Modern & bold','Corporate & trustworthy','Creative & energetic','Elegant & luxury'],'default':'Premium & minimal'},
        {'id':'primary_color','label':'Brand primary color','type':'color','default':'#6C4CFF'},
        {'id':'seo','label':'SEO keywords / location','type':'textarea','default':'','help':'Keywords, city/country or search phrases.'},
        {'id':'special_features','label':'Special functionality','type':'textarea','default':'','help':'Booking, maps, filters, calculators, integrations, forms, etc.'},
        {'id':'footer_note','label':'Footer / legal note','type':'text','default':'','help':'Optional copyright, privacy or company note.'},
    ]
    if business_type == 'coffee_shop':
        questions.insert(6, {'id':'menu','label':'Menu / signature items','type':'textarea','default':'','help':'List drinks, food, signature items and prices if available.'})
        questions.insert(7, {'id':'opening_hours','label':'Opening hours & location','type':'textarea','default':'','help':'Hours, address and reservation details.'})
    return {'business_type':business_type,'summary':'Webify studied your idea and prepared a tailored website brief. Complete the relevant fields so the final site reflects your actual business.','assumptions':['Responsive across mobile, tablet and desktop.','Content supplied here should be preserved in the generated site.','Missing facts will be presented as editable, non-deceptive placeholders.'],'questions':questions}


def generate_site_plan(analysis, requirements):
    system = '''You are Webify's creative director, UX architect and conversion-focused web designer. Generate a genuinely business-specific website specification from the analyzed idea and completed requirements. Do not return a generic template. The layout, hierarchy, copy tone, sections and visual direction must fit the business. Preserve every supplied user requirement. Never invent facts such as prices, addresses, ratings, clients or statistics. If content is missing, use tasteful editable placeholders.
Return JSON only with: title,slug,summary,business_type,visual_style{theme,primary,secondary,accent,background,surface,text,muted,heading_font,body_font,radius,shadow,animation},hero{layout,badge,headline,subtitle,primary_cta,secondary_cta,image_direction},navigation[],sections[{id,type,layout,eyebrow,title,description,items[],cta}],footer{description,links[],socials[],copyright},seo{title,description,keywords[]}. Section types may include about, services, products, features, testimonials, team, pricing, gallery, faq, contact, location, process, stats. Each item must contain title,text,meta when useful. Build a coherent customer journey and not just a collection of cards.'''
    result = _call_llm(system, json.dumps({'analysis':analysis,'requirements':requirements}, ensure_ascii=False))
    if result:
        return _apply_user_content_to_plan(result, requirements)

    name = str(requirements.get('business_name') or 'Your Business')
    desc = str(requirements.get('business_description') or 'A modern business focused on great customer experiences.')
    services = _lines(requirements.get('services')) or ['Core Service','Specialized Solutions','Customer Support']
    style = requirements.get('visual_style') or 'Premium & minimal'
    primary = requirements.get('primary_color') or '#6C4CFF'
    sections = [
        {'id':'about','type':'about','eyebrow':'ABOUT','title':'Built around your goals','description':desc,'items':[]},
        {'id':'services','type':'services','eyebrow':'SERVICES','title':'What we do','description':'Explore the services and solutions available.','items':[{'title':x.split('|')[0].strip(),'text':x.split('|',1)[1].strip() if '|' in x else 'Add a concise description of this offering.','meta':f'{i+1:02d}'} for i,x in enumerate(services[:8])]},
    ]
    plan = {'title':name,'slug':re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-') or 'webify-site','summary':desc,'business_type':analysis.get('business_type','business'),'visual_style':{'theme':style,'primary':primary,'secondary':'#F0ECFF','accent':'#8B76FF','background':'#FAFAFC','surface':'#FFFFFF','text':'#111216','muted':'#6B6F78','heading_font':'Space Grotesk','body_font':'DM Sans','radius':'20px','shadow':'soft','animation':'subtle'},'hero':{'layout':'editorial','badge':'BUILT WITH WEBIFY','headline':requirements.get('tagline') or f'Welcome to {name}','subtitle':desc,'primary_cta':requirements.get('cta') or 'Get Started','secondary_cta':'Explore'},'navigation':['Home','About','Services','Contact'],'sections':sections,'footer':{'description':desc,'links':[],'socials':_lines(requirements.get('socials')),'copyright':requirements.get('footer_note') or f'© {name}. All rights reserved.'},'seo':{'title':f'{name} | {requirements.get("tagline","")}'.strip(' |'),'description':desc[:155],'keywords':_lines(requirements.get('seo'))}}
    return _apply_user_content_to_plan(plan, requirements)
