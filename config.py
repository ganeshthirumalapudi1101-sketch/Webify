import os
APP_NAME="Webify"; TAGLINE="Fill the form. Get a website."
DEMO_USERS={
 "manowebify@gmail.com":{"password":"M@no123","name":"Mano"},
 "amulyawebify@gmail.com":{"password":"@mulya123","name":"Amulya"},
 "hemawebify@gmail.com":{"password":"hem@123","name":"Hema"},
}
AI_PROVIDER=os.getenv("WEBIFY_AI_PROVIDER","auto").lower(); OPENAI_MODEL=os.getenv("OPENAI_MODEL","gpt-5-mini"); GROQ_MODEL=os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")
