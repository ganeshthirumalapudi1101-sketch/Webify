import streamlit as st

def inject_css():
 st.markdown('''<style>@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap");:root{--brand:#6c4cff;--line:#e8e9ed}html,body,[class*="css"]{font-family:DM Sans,sans-serif}.stApp{background:radial-gradient(circle at 90% 0%,#6c4cff14,transparent 28%),#fbfbfc}.block-container{max-width:1180px;padding-top:2.2rem}h1,h2,h3,h4{font-family:Space Grotesk,sans-serif;letter-spacing:-.03em}.hero{padding:4.5rem 2rem 3rem;border-radius:30px;background:linear-gradient(135deg,#111217,#272334);color:white;box-shadow:0 24px 80px #14102329;margin-bottom:2rem}.hero h1{font-size:4.4rem;margin:0}.hero p{color:#c9c6d4;font-size:1.15rem;max-width:720px}.badge{display:inline-block;padding:7px 12px;border:1px solid #ffffff25;border-radius:999px;color:#ddd8ee;font-size:.82rem;margin-bottom:1rem}.step{padding:11px 12px;border:1px solid var(--line);border-radius:14px;color:#8a8d96;text-align:center;background:white;margin-bottom:1.4rem}.step.active{border-color:#cfc7ff;background:#f2efff;color:#5b43d5;font-weight:700}.preview{background:#15161a;border-radius:20px;padding:10px}.stButton button,.stDownloadButton button{border-radius:12px!important;min-height:46px}[data-testid="stSidebar"]{border-right:1px solid var(--line)}</style>''',unsafe_allow_html=True)

def hero(): st.markdown('<div class="hero"><div class="badge">✦ AI WEBSITE GENERATION PLATFORM</div><h1>Webify</h1><p>Fill the form. Get a website. Describe your business in plain language and let Webify turn the requirements into a polished, responsive website package.</p></div>',unsafe_allow_html=True)
def sidebar(user,reset):
 st.sidebar.markdown("## ✦ Webify"); st.sidebar.caption("AI Website Builder"); st.sidebar.success(f"Signed in as {user['name']}"); st.sidebar.divider(); st.sidebar.markdown("**Workflow**"); [st.sidebar.write(x) for x in ["1. Describe your idea","2. Answer smart questions","3. Generate the site","4. Preview & export"]]; st.sidebar.divider()
 if st.sidebar.button("New project",use_container_width=True): reset(); st.rerun()
 if st.sidebar.button("Sign out",use_container_width=True): st.session_state.user=None; reset(); st.rerun()
def render_requirement_form(questions,previous):
 answers={}
 for q in questions:
  key=q.get("id",q.get("label","field")); label=q.get("label",key); default=previous.get(key,q.get("default","")); help_text=q.get("help",""); typ=q.get("type","text"); opts=q.get("options",[])
  if typ=="textarea": answers[key]=st.text_area(label,value=str(default),help=help_text)
  elif typ=="select": answers[key]=st.selectbox(label,opts or ["Not specified"],index=opts.index(default) if default in opts else 0,help=help_text)
  elif typ=="multiselect": answers[key]=st.multiselect(label,opts or [],default=default if isinstance(default,list) else [],help=help_text)
  elif typ=="color": answers[key]=st.color_picker(label,value=default or "#6C4CFF",help=help_text)
  elif typ=="checkbox": answers[key]=st.checkbox(label,value=bool(default),help=help_text)
  else: answers[key]=st.text_input(label,value=str(default),help=help_text)
 return answers
def render_preview(bundle):
 st.markdown(f"### {bundle['title']}"); st.caption(bundle["summary"]); st.markdown('<div class="preview">',unsafe_allow_html=True); st.components.v1.html(bundle["html"],height=670,scrolling=True); st.markdown('</div>',unsafe_allow_html=True)
 with st.expander("Generated files"):
  for f in bundle["files"]: st.write("• "+f)
