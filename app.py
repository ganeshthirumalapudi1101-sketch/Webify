import streamlit as st
from auth import authenticate
from config import APP_NAME, TAGLINE
from agents.ai_engine import analyze_idea, generate_site_plan
from generator.site_generator import build_website_zip
from ui import inject_css, hero, sidebar, render_requirement_form, render_preview

st.set_page_config(page_title=f"{APP_NAME} — AI Website Builder", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
inject_css()

for k, v in {"user":None,"stage":"idea","analysis":None,"requirements":{},"site_bundle":None}.items():
    if k not in st.session_state: st.session_state[k]=v

def reset_project():
    st.session_state.stage="idea"; st.session_state.analysis=None; st.session_state.requirements={}; st.session_state.site_bundle=None

if not st.session_state.user:
    hero(); st.markdown("### Sign in to Webify"); st.caption("Turn a business idea into a polished, exportable website.")
    with st.form("login"):
        email=st.text_input("Email", placeholder="you@company.com")
        password=st.text_input("Password", type="password")
        submitted=st.form_submit_button("Continue to Webify", use_container_width=True)
        if submitted:
            user=authenticate(email,password)
            if user: st.session_state.user=user; st.rerun()
            else: st.error("Invalid email or password.")
    st.info("Demo accounts are included for local development. Move credentials to Streamlit Secrets before production deployment.")
    st.stop()

sidebar(st.session_state.user, reset_project)
st.markdown(f"# {APP_NAME}"); st.markdown(f"### {TAGLINE}"); st.caption("AI-powered platform that converts structured business requirements into fully functional websites automatically.")
steps=["01 · Idea","02 · Requirements","03 · Generate","04 · Preview & Export"]; cols=st.columns(4)
idx={"idea":0,"requirements":1,"generate":2,"preview":3}.get(st.session_state.stage,0)
for i,label in enumerate(steps): cols[i].markdown(f'<div class="step {"active" if i==idx else ""}">{label}</div>', unsafe_allow_html=True)

if st.session_state.stage=="idea":
    st.markdown("## Tell Webify what you need"); st.write("Describe your organization, product, service, audience, goals, and the kind of website you imagine. Plain language is enough.")
    idea=st.text_area("Your idea", height=230, placeholder="Example: We run a premium interior design studio in Hyderabad. We need a modern website that shows our projects, services, process, testimonials and lets visitors request a consultation...")
    c1,c2=st.columns([3,1])
    with c1:
        if st.button("Study my idea →", type="primary", use_container_width=True):
            if not idea.strip(): st.warning("Please describe your idea first.")
            else:
                with st.spinner("Webify is studying your business and designing the requirement form..."):
                    st.session_state.analysis=analyze_idea(idea); st.session_state.stage="requirements"
                st.rerun()
    with c2: st.metric("AI workflow","Plan → Build → Review")

elif st.session_state.stage=="requirements":
    analysis=st.session_state.analysis or {}; st.markdown("## Let’s shape your website"); st.write("Webify converted your idea into a focused requirement form. Review every section before generating.")
    st.success(analysis.get("summary","Your business requirements have been analyzed."))
    if analysis.get("assumptions"):
        with st.expander("AI assumptions & things to confirm"):
            for item in analysis["assumptions"]: st.write("• "+item)
    with st.form("requirements_form"):
        answers=render_requirement_form(analysis.get("questions",[]), st.session_state.requirements)
        c1,c2=st.columns(2)
        with c1: back=st.form_submit_button("← Edit idea", use_container_width=True)
        with c2: generate=st.form_submit_button("Generate my website ✦", type="primary", use_container_width=True)
        if back: st.session_state.stage="idea"; st.rerun()
        if generate: st.session_state.requirements=answers; st.session_state.stage="generate"; st.rerun()

elif st.session_state.stage=="generate":
    st.markdown("## Building your website"); st.write("Webify is turning the approved requirements into a complete website package.")
    with st.status("Webify build pipeline", expanded=True) as status:
        st.write("✓ Requirements validated")
        plan=generate_site_plan(st.session_state.analysis, st.session_state.requirements); st.write("✓ Site architecture created")
        bundle=build_website_zip(plan, st.session_state.requirements); st.write("✓ Responsive HTML/CSS/JS generated")
        st.write("✓ Accessibility, SEO and responsive checks applied"); st.session_state.site_bundle=bundle
        status.update(label="Website ready", state="complete")
    st.session_state.stage="preview"; st.rerun()

else:
    bundle=st.session_state.site_bundle
    st.markdown("## Your website is ready")
    if not bundle: st.warning("No generated site is available. Start a new project."); st.stop()
    render_preview(bundle)
    st.markdown("### Export"); c1,c2=st.columns(2)
    with c1: st.download_button("Download website ZIP", data=bundle["zip_bytes"], file_name=f'{bundle["slug"]}.zip', mime="application/zip", use_container_width=True)
    with c2:
        if st.button("Start a new website", use_container_width=True): reset_project(); st.rerun()
    st.caption("The ZIP contains a standalone website that can be hosted on any static hosting provider.")
