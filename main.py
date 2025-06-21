from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found in environment.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

# Input schema
class FarmerRequest(BaseModel):
    earning: int
    location: str
    crop: str

@app.post("/get-loans")
async def get_loans(request: FarmerRequest):
    prompt = f"""
You are an expert government loan and microfinance assistant for Indian farmers.

Given the following:
- Location: {request.location}
- Annual Income: ₹{request.earning}
- Crop: {request.crop}

Suggest up to 5 relevant government or microfinance loan schemes for this farmer.

Return the response **only as a JSON array** with the following fields:
- loan_name
- bank
- amount
- chance
- link

Example output format:
[
  {{
    "loan_name": "Kisan Credit Card",
    "bank": "State Bank of India",
    "amount": "₹50,000",
    "chance": "85%",
    "link": "https://example.com/kcc"
  }},
  ...
]
Do not include any explanation — return only the JSON.
"""

    try:
        response = model.generate_content(prompt)
        raw_json = response.text.strip()
        print("🧾 Raw Gemini Output:\n", raw_json)
        return raw_json  # Return as plain string
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
