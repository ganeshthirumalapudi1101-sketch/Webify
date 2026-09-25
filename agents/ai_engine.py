import json,os,re
from config import AI_PROVIDER,OPENAI_MODEL,GROQ_MODEL

def _extract_json(text):
 text=re.sub(r'^```(?:json)?\s*','',text.strip(),flags=re.I); text=re.sub(r'\s*```$','',text)
 try:return json.loads(text)
 except Exception:
  m=re.search(r'\{.*\}',text,re.S)
  if m:return json.loads(m.group(0))
  raise

def _call_llm(system,user):
 if AI_PROVIDER in ('auto','openai') and os.getenv('OPENAI_API_KEY'):
  try:
   from openai import OpenAI
   r=OpenAI(api_key=os.environ['OPENAI_API_KEY']).chat.completions.create(model=OPENAI_MODEL,temperature=.2,response_format={'type':'json_object'},messages=[{'role':'system','content':system},{'role':'user','content':user}]); return _extract_json(r.choices[0].message.content)
  except Exception:
   if AI_PROVIDER=='openai': raise
 if AI_PROVIDER in ('auto','groq') and os.getenv('GROQ_API_KEY'):
  try:
   from groq import Groq
   r=Groq(api_key=os.environ['GROQ_API_KEY']).chat.completions.create(model=GROQ_MODEL,temperature=.2,response_format={'type':'json_object'},messages=[{'role':'system','content':system},{'role':'user','content':user}]); return _extract_json(r.choices[0].message.content)
  except Exception:
   if AI_PROVIDER=='groq': raise
 return None

def analyze_idea(idea):
 system='''You are Webify requirements analyst. Convert a plain-language website idea into a complete practical questionnaire. Return JSON only with summary, assumptions, and questions. Each question has id,label,type(text|textarea|select|multiselect|color|checkbox),options,help,default. Cover brand, audience, goals, pages, content, services/products, CTAs, contact, social links, visual direction, SEO, legal/footer and functionality. Do not request secrets.'''
 result=_call_llm(system,idea)
 return result or fallback_analysis(idea)

def fallback_analysis(idea):
 return {'summary':'Webify understood your concept and prepared a complete website brief. Answer these questions so the generated site reflects your requirements.','assumptions':['Responsive across mobile, tablet and desktop.','A clear primary call-to-action will be included.','Content remains editable in the exported files.'],'questions':[
 {'id':'business_name','label':'Business / organization name','type':'text','default':'','help':'Name shown in header, hero and footer.'},{'id':'tagline','label':'Tagline','type':'text','default':'','help':'Short value statement.'},{'id':'business_description','label':'What do you do?','type':'textarea','default':idea,'help':'Explain your work, services, products or mission.'},{'id':'audience','label':'Who is the website for?','type':'textarea','default':'','help':'Describe target customers or visitors.'},{'id':'pages','label':'Pages / sections required','type':'multiselect','options':['Home','About','Services','Products','Projects','Portfolio','Testimonials','Pricing','FAQ','Blog','Contact'],'default':['Home','About','Services','Contact']},{'id':'services','label':'Main services / products','type':'textarea','default':'','help':'List important offerings and short descriptions.'},{'id':'cta','label':'Primary call-to-action','type':'text','default':'Get Started','help':'Example: Book a Call, Request Quote, Shop Now.'},{'id':'contact','label':'Contact details','type':'textarea','default':'','help':'Email, phone, address, WhatsApp, hours.'},{'id':'socials','label':'Social links','type':'textarea','default':'','help':'Instagram, LinkedIn, YouTube, Facebook, etc.'},{'id':'visual_style','label':'Visual style','type':'select','options':['Premium & minimal','Modern & bold','Corporate & trustworthy','Creative & energetic','Elegant & luxury'],'default':'Premium & minimal'},{'id':'primary_color','label':'Brand primary color','type':'color','default':'#6C4CFF'},{'id':'seo','label':'SEO keywords / location','type':'textarea','default':'','help':'Keywords, city/country or phrases.'},{'id':'special_features','label':'Special functionality','type':'textarea','default':'','help':'Forms, booking, filters, calculators, maps, integrations.'},{'id':'footer_note','label':'Footer / legal note','type':'text','default':'','help':'Optional copyright/privacy/company note.'}]}

def generate_site_plan(analysis,requirements):
 system='''You are Webify website architect. Return JSON with title,slug,summary,hero_title,hero_subtitle,cta,sections,nav,seo_title,seo_description,keywords. Sections contain type,title,intro,items where each item has title,text,meta. Do not invent business facts; use tasteful editable placeholders when missing.'''
 result=_call_llm(system,json.dumps({'analysis':analysis,'requirements':requirements},ensure_ascii=False))
 if result:return result
 name=requirements.get('business_name') or 'Your Business'; desc=requirements.get('business_description') or 'A modern business built around great customer experiences.'; raw=str(requirements.get('services','')); services=[x.strip() for x in raw.splitlines() if x.strip()] or ['Core Service','Specialized Solutions','Customer Support']
 sections=[{'type':'about','title':'Built around your goals','intro':desc,'items':[]},{'type':'services','title':'What we do','intro':'Explore the services and solutions available.','items':[{'title':s,'text':'Add a concise description of this offering.','meta':''} for s in services[:6]]},{'type':'contact','title':'Let’s work together','intro':'Tell us what you need and we’ll get back to you.','items':[]}]
 return {'title':name,'slug':re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-') or 'webify-site','summary':desc,'hero_title':requirements.get('tagline') or f'Welcome to {name}','hero_subtitle':desc,'cta':requirements.get('cta') or 'Get Started','sections':sections,'nav':['Home']+[x for x in requirements.get('pages',[]) if x!='Home'],'seo_title':f"{name} | {requirements.get('tagline','')}",'seo_description':desc[:155],'keywords':[x.strip() for x in str(requirements.get('seo','')).split(',') if x.strip()]}
