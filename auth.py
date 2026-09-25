import hmac
from config import DEMO_USERS
def authenticate(email,password):
    user=DEMO_USERS.get(email.strip().lower())
    return {"email":email.strip().lower(),"name":user["name"]} if user and hmac.compare_digest(user["password"],password) else None
