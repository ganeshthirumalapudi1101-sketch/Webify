import base64
import json
import streamlit as st
import streamlit.components.v1 as components


def inject_css():
    st.markdown('''<style>
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap");
:root{--webify-brand:#6c4cff;--webify-line:#e4e5eb;--webify-muted:#777b85}
html,body,[class*="css"]{font-family:"DM Sans",sans-serif}.stApp{background:radial-gradient(circle at 88% 0%,#6c4cff18,transparent 28%),#f8f8fa}.block-container{max-width:1220px;padding-top:2rem}h1,h2,h3,h4{font-family:"Space Grotesk",sans-serif;letter-spacing:-.035em}.hero{padding:4.6rem 2.4rem 3.5rem;border-radius:30px;background:radial-gradient(circle at 80% 15%,#6c4cff55,transparent 30%),linear-gradient(135deg,#0d0d11,#272230);color:white;box-shadow:0 25px 90px #18132126;margin-bottom:2rem}.hero h1{font:700 4.8rem/1 "Space Grotesk",sans-serif;margin:0}.hero p{color:#cbc7d5;font-size:1.1rem;line-height:1.75;max-width:760px}.badge,.preview-label{display:inline-block}.badge{padding:7px 12px;border:1px solid #ffffff28;border-radius:999px;color:#e4dfef;font-size:.78rem;letter-spacing:.08em;margin-bottom:1rem}.step{padding:11px 12px;border:1px solid var(--webify-line);border-radius:14px;color:#8a8d96;text-align:center;background:#fff;margin-bottom:1.4rem}.step.active{border-color:#cfc7ff;background:#f0edff;color:#5b43d5;font-weight:800}.section-card{background:#fff;border:1px solid #e6e7ec;border-radius:20px;padding:22px;margin:12px 0;box-shadow:0 12px 45px #17172008}.preview-shell{background:#121319;border-radius:22px;padding:10px;box-shadow:0 24px 70px #1210191c}.preview-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#1a1b20;color:#fff;padding:12px 14px;border-radius:15px 15px 0 0}.preview-dots{display:flex;gap:6px}.preview-dots span{width:9px;height:9px;border-radius:50%;background:#686b73}.preview-url{font-size:.78rem;color:#b7b8bf;background:#24252b;border-radius:8px;padding:6px 10px;flex:1;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.file-pill{display:inline-block;padding:7px 11px;margin:3px;border:1px solid #e5e6eb;border-radius:999px;background:#fff;color:#555862;font-size:.82rem}[data-testid="stIFrame"]{width:100%!important;border:1px solid #dedfe5!important;border-radius:16px!important;background:#fff!important;box-shadow:0 20px 60px #14102310!important}.open-preview{display:flex;align-items:center;justify-content:center;padding:12px 16px;border-radius:12px;background:#6c4cff;color:#fff!important;font-weight:800;text-decoration:none!important;margin:10px 0}.open-preview:hover{background:#5840d8}@media(max-width:760px){.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:3rem 1.5rem;border-radius:22px}.hero h1{font-size:3.5rem}.hero p{font-size:1rem}.step{font-size:.72rem;padding:9px 5px}}
</style>''', unsafe_allow_html=True)


def hero():
    st.markdown('''<div class="hero"><div class="badge">✦ AI WEBSITE GENERATION PLATFORM</div><h1>Webify</h1><p>Fill the form. Get a website. Describe your business in plain language and let Webify turn your requirements into a polished, responsive website package.</p></div>''', unsafe_allow_html=True)


def sidebar(user, reset):
    st.sidebar.markdown("## ✦ Webify")
    st.sidebar.caption("AI Website Builder")
    name=user.get('name','User') if isinstance(user,dict) else 'User'
    st.sidebar.success(f"Signed in as {name}")
    st.sidebar.divider(); st.sidebar.markdown('**Workflow**')
    for x in ['1. Describe your idea','2. Answer smart questions','3. Generate the site','4. Preview & export']: st.sidebar.write(x)
    st.sidebar.divider()
    if st.sidebar.button('＋ New project',use_container_width=True): reset(); st.rerun()
    if st.sidebar.button('Sign out',use_container_width=True): st.session_state.user=None; reset(); st.rerun()


def render_requirement_form(questions, previous):
    answers={}; previous=previous or {}; questions=questions or []
    for index,q in enumerate(questions):
        if not isinstance(q,dict): continue
        key=q.get('id') or q.get('label') or f'field_{index}'
        label=q.get('label',key); default=previous.get(key,q.get('default','')); help_text=q.get('help',''); typ=q.get('type','text'); opts=q.get('options') or []
        if typ=='textarea': answers[key]=st.text_area(label,value=str(default or ''),help=help_text,key=f'requirement_{key}')
        elif typ=='select':
            safe=opts or ['Not specified']; idx=safe.index(default) if default in safe else 0
            answers[key]=st.selectbox(label,safe,index=idx,help=help_text,key=f'requirement_{key}')
        elif typ=='multiselect':
            safe=opts; selected=default if isinstance(default,list) else []
            answers[key]=st.multiselect(label,safe,default=[x for x in selected if x in safe],help=help_text,key=f'requirement_{key}')
        elif typ=='color': answers[key]=st.color_picker(label,value=default or '#6C4CFF',help=help_text,key=f'requirement_{key}')
        elif typ=='checkbox': answers[key]=st.checkbox(label,value=bool(default),help=help_text,key=f'requirement_{key}')
        else: answers[key]=st.text_input(label,value=str(default or ''),help=help_text,key=f'requirement_{key}')
    return answers


def _prepare_preview_html(bundle):
    html=bundle.get('html',''); css=bundle.get('css',''); js=bundle.get('js','')
    if not html: return ''
    import re
    html=re.sub(r'<link[^>]+href=["\']style\.css["\'][^>]*>','',html,flags=re.I)
    html=re.sub(r'<script[^>]+src=["\']script\.js["\']\s*></script>','',html,flags=re.I)
    if '</head>' in html: html=html.replace('</head>',f'<style>{css}</style></head>',1)
    else: html=f'<style>{css}</style>'+html
    if '</body>' in html: html=html.replace('</body>',f'<script>{js}</script></body>',1)
    else: html+=f'<script>{js}</script>'
    return html


def _preview_launcher(bundle):
    preview=_prepare_preview_html(bundle)
    encoded=base64.b64encode(preview.encode('utf-8')).decode('ascii')
    safe=json.dumps(encoded)
    return f'''<div style="display:flex;justify-content:flex-end"><button id="webify-open-preview" style="border:0;background:#6c4cff;color:white;border-radius:12px;padding:12px 18px;font-weight:800;cursor:pointer">↗ Open full preview in new window</button></div><script>(function(){{const b=document.getElementById('webify-open-preview');b.addEventListener('click',function(){{const html=atob({safe});const blob=new Blob([html],{{type:'text/html'}});const url=URL.createObjectURL(blob);window.open(url,'_blank','noopener,noreferrer,width=1440,height=1000');}});}})();</script>'''


def render_preview(bundle):
    if not bundle:
        st.warning('No generated website is available.'); return
    title=bundle.get('title','Webify Website'); summary=bundle.get('summary','')
    st.markdown(f'### {title}')
    if summary: st.caption(summary)
    st.markdown('<div class="preview-shell"><div class="preview-toolbar"><div class="preview-dots"><span></span><span></span><span></span></div><div class="preview-url">webify://generated-site/preview</div><div style="font-size:.75rem;color:#aaa">LIVE</div></div>',unsafe_allow_html=True)
    preview_html=_prepare_preview_html(bundle)
    if not preview_html: st.error('Generated website HTML is empty.'); return
    desktop,mobile=st.tabs(['🖥 Desktop preview','📱 Mobile preview'])
    with desktop: components.html(preview_html,height=820,scrolling=True)
    with mobile:
        _,center,_=st.columns([1,2,1]);
        with center: components.html(preview_html,height=820,scrolling=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.components.v1.html(_preview_launcher(bundle),height=70,scrolling=False)
    st.markdown('### Generated files')
    st.markdown(''.join(f'<span class="file-pill">✓ {x}</span>' for x in bundle.get('files',[])),unsafe_allow_html=True)
