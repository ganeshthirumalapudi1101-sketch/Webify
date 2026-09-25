# Webify — AI Website Builder

**Tagline:** Fill the form. Get a website.

Webify is a Streamlit-based AI website builder that accepts a natural-language business idea, studies it, creates a tailored questionnaire, generates a structured website plan, renders a professional responsive HTML/CSS/JS site, previews it, and exports it as a ZIP.

## Run
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## AI providers
Set `WEBIFY_AI_PROVIDER=groq` with `GROQ_API_KEY`, or `WEBIFY_AI_PROVIDER=openai` with `OPENAI_API_KEY`. `auto` tries OpenAI then Groq. With no key, a deterministic fallback still makes the app usable.

## Current demo login
- manowebify@gmail.com / M@no123
- amulyawebify@gmail.com / @mulya123
- hemawebify@gmail.com / hem@123

**Production:** move credentials to Streamlit Secrets or replace demo authentication with a real identity provider/database-backed auth before public launch.

## Production checklist
Use HTTPS, secrets management, real auth, per-user project storage, asset uploads, server-side validation/retries, real contact-form integrations, object storage, audit logs, rate limits, billing/usage controls, accessibility/link tests, and monitoring.
