from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from google import genai
import os
import traceback


# Load .env
load_dotenv()


# Create FastAPI application
app = FastAPI(title="PocketSmart AI")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Get Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")


# Create Gemini client
client = None

if API_KEY and API_KEY.strip().upper() not in {"YOUR_KEY", "YOUR_API_KEY_HERE"}:
    client = genai.Client(api_key=API_KEY)


# =========================
# HOME PAGE
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


# =========================
# AI RECOMMENDATION
# =========================

@app.post("/recommendation", response_class=HTMLResponse)
async def recommendation(
    request: Request,
    income: float = Form(...),
    expenses: float = Form(...),
    category: str = Form(...)
):

    savings = income - expenses
    context = {
        "request": request,
        "income": income,
        "expenses": expenses,
        "category": category,
        "savings": savings,
    }

    try:
        if (
            not API_KEY
            or API_KEY.strip().upper() in {"YOUR_KEY", "YOUR_API_KEY_HERE"}
            or client is None
        ):
            recommendation_text = """
Gemini API key is missing or still uses the placeholder.

Replace YOUR_KEY in your .env file with your actual Gemini API key:

GEMINI_API_KEY=your_actual_api_key
"""
        else:
            prompt = f"""
You are PocketSmart AI, a helpful personal budgeting assistant.

Analyze the following monthly financial information:

Monthly Income: ₹{income}
Monthly Expenses: ₹{expenses}
Main Expense Category: {category}
Remaining Money: ₹{savings}

Provide a simple financial analysis.

Include these sections:

1. Budget Overview
2. Spending Analysis
3. Suggested Savings Target
4. Three Money-Saving Tips

Use simple language.

Do not give investment, loan, tax, or other regulated financial advice.

Keep the response under 300 words.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            recommendation_text = response.text or "No recommendation was returned. Please try again."
    except Exception:
        traceback.print_exc()
        recommendation_text = (
            "PocketSmart AI encountered an error. Please check the server terminal "
            "for details, then verify your Gemini API key and connection."
        )

    context["recommendation"] = recommendation_text
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )
