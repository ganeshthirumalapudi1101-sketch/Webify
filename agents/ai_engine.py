import json
import os
import re
from config import AI_PROVIDER, OPENAI_MODEL, GROQ_MODEL


# ============================================================
# JSON HELPERS
# ============================================================

def _extract_json(text):
    """
    Safely extract JSON from an LLM response.
    Handles ```json ... ``` responses as well.
    """
    if not text:
        raise ValueError("Empty AI response")

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)
    except json.JSONDecodeError:

        # Try extracting the largest JSON object
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)

        if match:
            return json.loads(match.group(0))

        raise


# ============================================================
# LLM CALL
# ============================================================

def _call_llm(system, user):

    # --------------------------------------------------------
    # OPENAI
    # --------------------------------------------------------

    if (
        AI_PROVIDER in ("auto", "openai")
        and os.getenv("OPENAI_API_KEY")
    ):

        try:

            from openai import OpenAI

            client = OpenAI(
                api_key=os.environ["OPENAI_API_KEY"]
            )

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.25,
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {
                        "role": "system",
                        "content": system
                    },
                    {
                        "role": "user",
                        "content": user
                    }
                ]
            )

            content = response.choices[0].message.content

            return _extract_json(content)

        except Exception as exc:

            print("OpenAI error:", exc)

            if AI_PROVIDER == "openai":
                raise


    # --------------------------------------------------------
    # GROQ
    # --------------------------------------------------------

    if (
        AI_PROVIDER in ("auto", "groq")
        and os.getenv("GROQ_API_KEY")
    ):

        try:

            from groq import Groq

            client = Groq(
                api_key=os.environ["GROQ_API_KEY"]
            )

            response = client.chat.completions.create(
                model=GROQ_MODEL,
                temperature=0.25,
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {
                        "role": "system",
                        "content": system
                    },
                    {
                        "role": "user",
                        "content": user
                    }
                ]
            )

            content = response.choices[0].message.content

            return _extract_json(content)

        except Exception as exc:

            print("Groq error:", exc)

            if AI_PROVIDER == "groq":
                raise

    return None


# ============================================================
# REQUIREMENT ANALYST
# ============================================================

def analyze_idea(idea):

    system = r"""
You are WEBIFY AI — a senior product strategist, UX researcher,
website architect and conversion specialist.

Your task is to deeply understand a user's natural-language
business description.

DO NOT create a generic questionnaire.

First understand:

1. What type of business is this?
2. What does the business sell or provide?
3. Who are the customers?
4. What problem does it solve?
5. What is the primary business goal of the website?
6. What action should visitors take?
7. What pages are appropriate?
8. What content is required?
9. What functionality is required?
10. What visual style fits the business?
11. What information is still missing?
12. What SEO information is required?

The questions MUST adapt to the business.

Examples:

COFFEE SHOP:
Ask about:
- menu
- opening hours
- location
- reservation
- food images
- signature items
- gallery

SAAS:
Ask about:
- product
- features
- pricing
- integrations
- free trial
- dashboard
- customers
- demo booking

REAL ESTATE:
Ask about:
- property types
- locations
- price range
- property listings
- agents
- enquiry
- property search

PORTFOLIO:
Ask about:
- projects
- skills
- experience
- clients
- case studies
- resume
- contact

RESTAURANT:
Ask about:
- cuisine
- menu
- chef
- reservations
- delivery
- location
- gallery

ECOMMERCE:
Ask about:
- products
- categories
- pricing
- offers
- checkout
- shipping
- payment
- customer accounts

Do not ask irrelevant questions.

Do not ask for passwords, API keys, payment credentials
or other secrets.

Return ONLY valid JSON.

Use this exact structure:

{
  "business_type": "",
  "business_name": "",
  "summary": "",
  "website_goal": "",
  "target_audience": "",

  "assumptions": [],

  "recommended_pages": [],

  "recommended_features": [],

  "questions": [
    {
      "id": "",
      "label": "",
      "type": "text|textarea|select|multiselect|color|checkbox",
      "options": [],
      "help": "",
      "default": ""
    }
  ]
}

The questionnaire should be detailed enough to build the
actual website without missing important requirements.
"""


    result = _call_llm(
        system,
        idea
    )

    if result:
        return result

    return fallback_analysis(idea)


# ============================================================
# FALLBACK ANALYSIS
# ============================================================

def fallback_analysis(idea):

    text = idea.lower()

    business_type = "business"

    if any(
        x in text
        for x in [
            "coffee",
            "cafe",
            "restaurant",
            "bakery",
            "food"
        ]
    ):
        business_type = "restaurant"

    elif any(
        x in text
        for x in [
            "saas",
            "software",
            "startup",
            "platform",
            "app"
        ]
    ):
        business_type = "saas"

    elif any(
        x in text
        for x in [
            "real estate",
            "property",
            "apartment",
            "villa"
        ]
    ):
        business_type = "real_estate"

    elif any(
        x in text
        for x in [
            "portfolio",
            "designer",
            "developer",
            "photographer"
        ]
    ):
        business_type = "portfolio"


    common = [

        {
            "id": "business_name",
            "label": "Business / organization name",
            "type": "text",
            "options": [],
            "help": "Name displayed throughout the website.",
            "default": ""
        },

        {
            "id": "business_description",
            "label": "Describe your business",
            "type": "textarea",
            "options": [],
            "help": "Explain what you do, what you sell and why customers choose you.",
            "default": idea
        },

        {
            "id": "audience",
            "label": "Who is your target audience?",
            "type": "textarea",
            "options": [],
            "help": "Describe your ideal customers.",
            "default": ""
        },

        {
            "id": "cta",
            "label": "Primary call-to-action",
            "type": "text",
            "options": [],
            "help": "Example: Book Now, Get Started, Request Quote.",
            "default": "Get Started"
        },

        {
            "id": "contact",
            "label": "Contact information",
            "type": "textarea",
            "options": [],
            "help": "Phone, email, address, WhatsApp and opening hours.",
            "default": ""
        },

        {
            "id": "visual_style",
            "label": "Visual style",
            "type": "select",
            "options": [
                "Premium",
                "Modern",
                "Minimal",
                "Luxury",
                "Corporate",
                "Creative",
                "Bold"
            ],
            "help": "Choose the overall visual personality.",
            "default": "Modern"
        },

        {
            "id": "primary_color",
            "label": "Primary brand color",
            "type": "color",
            "options": [],
            "help": "Main brand color.",
            "default": "#6C4CFF"
        },

        {
            "id": "seo",
            "label": "SEO keywords / location",
            "type": "textarea",
            "options": [],
            "help": "Keywords and location you want to target.",
            "default": ""
        }
    ]


    if business_type == "restaurant":

        common.extend([

            {
                "id": "menu",
                "label": "Menu / signature items",
                "type": "textarea",
                "options": [],
                "help": "List important dishes, drinks or specialties.",
                "default": ""
            },

            {
                "id": "opening_hours",
                "label": "Opening hours",
                "type": "textarea",
                "options": [],
                "help": "Example: Mon-Sun 8 AM - 10 PM.",
                "default": ""
            },

            {
                "id": "reservation",
                "label": "Do customers need reservations?",
                "type": "checkbox",
                "options": [],
                "help": "",
                "default": True
            }
        ])


    return {

        "business_type": business_type,

        "business_name": "",

        "summary":
            "Webify analyzed your idea and created a business-specific website questionnaire.",

        "website_goal":
            "Create a professional website that converts visitors into customers.",

        "target_audience": "",

        "assumptions": [
            "The website will be responsive.",
            "The website will have a clear primary CTA.",
            "The exported content remains editable."
        ],

        "recommended_pages": [
            "Home",
            "About",
            "Services",
            "Contact"
        ],

        "recommended_features": [
            "Responsive design",
            "Contact form",
            "SEO metadata",
            "Mobile navigation"
        ],

        "questions": common
    }


# ============================================================
# WEBSITE ARCHITECT
# ============================================================

def generate_site_plan(
    analysis,
    requirements
):

    system = r"""
You are WEBIFY AI CREATIVE DIRECTOR.

You receive:
1. A business analysis.
2. User-approved requirements.

Your task is to design the ACTUAL website.

This is NOT a generic template.

You must design a website specifically for the business.

The generated specification controls:

- layout
- sections
- colors
- typography
- navigation
- hero
- cards
- CTAs
- content
- responsive behavior
- visual personality
- business-specific components

Different businesses MUST receive different layouts.

For example:

Restaurant:
Hero → Menu → Story → Gallery → Testimonials → Location → Reservation

SaaS:
Hero → Product Preview → Benefits → Features → Workflow →
Integrations → Pricing → Testimonials → FAQ → CTA

Real Estate:
Hero Search → Featured Properties → Property Types →
Locations → Why Choose Us → Agents → Testimonials → Enquiry

Portfolio:
Hero → Selected Work → About → Skills → Case Studies →
Experience → Testimonials → Contact

Ecommerce:
Hero → Categories → Featured Products → Offers →
Product Grid → Reviews → Newsletter

Do NOT force sections that don't make sense.

Use the user's actual information.

Do NOT invent factual business information.

If something is missing, use clearly editable placeholder text.

The website should feel like a professional agency-designed website.

Return ONLY valid JSON.

Return this structure:

{
  "title": "",
  "slug": "",
  "summary": "",

  "business_type": "",

  "visual_style": {
    "theme": "",
    "primary": "",
    "secondary": "",
    "accent": "",
    "background": "",
    "surface": "",
    "text": "",
    "muted": "",
    "heading_font": "",
    "body_font": "",
    "radius": "",
    "shadow": "",
    "animation": ""
  },

  "hero": {
    "layout": "",
    "badge": "",
    "headline": "",
    "subtitle": "",
    "primary_cta": "",
    "secondary_cta": "",
    "image_direction": ""
  },

  "navigation": [],

  "sections": [
    {
      "id": "",
      "type": "",
      "layout": "",
      "eyebrow": "",
      "title": "",
      "description": "",
      "items": [],
      "cta": ""
    }
  ],

  "footer": {
    "description": "",
    "links": [],
    "copyright": ""
  },

  "seo": {
    "title": "",
    "description": "",
    "keywords": []
  }
}
"""


    payload = json.dumps(
        {
            "business_analysis": analysis,
            "user_requirements": requirements
        },
        ensure_ascii=False,
        indent=2
    )


    result = _call_llm(
        system,
        payload
    )


    if result:
        return result


    return fallback_site_plan(
        analysis,
        requirements
    )


# ============================================================
# FALLBACK WEBSITE PLAN
# ============================================================

def fallback_site_plan(
    analysis,
    requirements
):

    name = (
        requirements.get("business_name")
        or "Your Business"
    )

    description = (
        requirements.get("business_description")
        or "A modern business focused on delivering excellent customer experiences."
    )

    business_type = (
        analysis.get("business_type")
        or "business"
    )


    if business_type == "restaurant":

        sections = [

            {
                "id": "featured",
                "type": "featured_items",
                "layout": "three_cards",
                "eyebrow": "SIGNATURES",
                "title": "Our favorites",
                "description": "Discover some of our most-loved offerings.",
                "items": [
                    {
                        "title": "Signature Coffee",
                        "text": "Freshly prepared specialty coffee.",
                        "meta": "From ₹180"
                    },
                    {
                        "title": "Fresh Breakfast",
                        "text": "Made fresh every morning.",
                        "meta": "Chef's choice"
                    },
                    {
                        "title": "House Dessert",
                        "text": "A sweet finish to your visit.",
                        "meta": "Fresh daily"
                    }
                ],
                "cta": "View Menu"
            },

            {
                "id": "story",
                "type": "story",
                "layout": "image_text",
                "eyebrow": "OUR STORY",
                "title": "Made for moments worth remembering",
                "description": description,
                "items": [],
                "cta": ""
            },

            {
                "id": "testimonials",
                "type": "testimonials",
                "layout": "cards",
                "eyebrow": "REVIEWS",
                "title": "Loved by our customers",
                "description": "",
                "items": [
                    {
                        "title": "Wonderful experience",
                        "text": "Add your verified customer review here.",
                        "meta": "Customer"
                    }
                ],
                "cta": ""
            },

            {
                "id": "contact",
                "type": "contact",
                "layout": "split",
                "eyebrow": "VISIT US",
                "title": "Come say hello",
                "description": "We would love to welcome you.",
                "items": [],
                "cta": "Get Directions"
            }
        ]

        hero = {
            "layout": "center",
            "badge": "WELCOME",
            "headline": (
                requirements.get("tagline")
                or f"Welcome to {name}"
            ),
            "subtitle": description,
            "primary_cta": (
                requirements.get("cta")
                or "Explore Menu"
            ),
            "secondary_cta": "Visit Us",
            "image_direction": "warm coffee shop photography"
        }

        theme = {
            "theme": "warm_luxury",
            "primary": requirements.get(
                "primary_color",
                "#8B5E3C"
            ),
            "secondary": "#F4E7D5",
            "accent": "#D6A66B",
            "background": "#FFF9F2",
            "surface": "#FFFFFF",
            "text": "#211A16",
            "muted": "#756B63",
            "heading_font": "Playfair Display",
            "body_font": "DM Sans",
            "radius": "18px",
            "shadow": "soft",
            "animation": "subtle"
        }

    else:

        sections = [

            {
                "id": "about",
                "type": "about",
                "layout": "image_text",
                "eyebrow": "ABOUT",
                "title": "Built around your goals",
                "description": description,
                "items": [],
                "cta": ""
            },

            {
                "id": "services",
                "type": "services",
                "layout": "three_cards",
                "eyebrow": "WHAT WE DO",
                "title": "Our services",
                "description": "Explore what we can do for you.",
                "items": [
                    {
                        "title": "Core Service",
                        "text": "Add your service description.",
                        "meta": ""
                    },
                    {
                        "title": "Specialized Solutions",
                        "text": "Add your service description.",
                        "meta": ""
                    },
                    {
                        "title": "Customer Support",
                        "text": "Add your service description.",
                        "meta": ""
                    }
                ],
                "cta": ""
            },

            {
                "id": "contact",
                "type": "contact",
                "layout": "split",
                "eyebrow": "CONTACT",
                "title": "Let's work together",
                "description": "Tell us what you need.",
                "items": [],
                "cta": requirements.get(
                    "cta",
                    "Get Started"
                )
            }
        ]

        hero = {
            "layout": "center",
            "badge": "WELCOME",
            "headline": (
                requirements.get("tagline")
                or f"Welcome to {name}"
            ),
            "subtitle": description,
            "primary_cta": requirements.get(
                "cta",
                "Get Started"
            ),
            "secondary_cta": "",
            "image_direction": "professional business photography"
        }

        theme = {
            "theme": "modern",
            "primary": requirements.get(
                "primary_color",
                "#6C4CFF"
            ),
            "secondary": "#ECE8FF",
            "accent": "#8B76FF",
            "background": "#FAFAFC",
            "surface": "#FFFFFF",
            "text": "#111216",
            "muted": "#6B6F78",
            "heading_font": "Space Grotesk",
            "body_font": "DM Sans",
            "radius": "18px",
            "shadow": "soft",
            "animation": "subtle"
        }


    return {

        "title": name,

        "slug": re.sub(
            r"[^a-z0-9]+",
            "-",
            name.lower()
        ).strip("-") or "webify-site",

        "summary": description,

        "business_type": business_type,

        "visual_style": theme,

        "hero": hero,

        "navigation": [
            "Home"
        ] + [
            x
            for x in requirements.get(
                "pages",
                []
            )
            if x != "Home"
        ],

        "sections": sections,

        "footer": {
            "description": description,
            "links": [],
            "copyright": f"© {name}"
        },

        "seo": {
            "title": name,
            "description": description[:155],
            "keywords": [
                x.strip()
                for x in str(
                    requirements.get(
                        "seo",
                        ""
                    )
                ).split(",")
                if x.strip()
            ]
        }
    }