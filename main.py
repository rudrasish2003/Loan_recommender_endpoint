from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found in environment.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FarmerRequest(BaseModel):
    earning: int
    location: str
    crop: str

@app.post("/get-loans")
async def get_loans(request: FarmerRequest):
    prompt = f"""
You are a government loan assistant.

Given:
- Location: {request.location}
- Income: ₹{request.earning}
- Crop: {request.crop}

Provide values for these 25 variables (no explanation):

loan1_name: ...
loan1_bank: ...
loan1_amount: ...
loan1_chance: ...
loan1_link: ...

loan2_name: ...
loan2_bank: ...
loan2_amount: ...
loan2_chance: ...
loan2_link: ...

(continue till loan5)
Only return all 25 key-value lines exactly like shown.
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        print("🧾 Gemini Output:\n", raw_text)

        # Convert key-value text into dictionary
        values = {}
        for line in raw_text.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                values[key.strip()] = value.strip()

        # Reconstruct into list of 5 loans
        loans = []
        for i in range(1, 6):
            loan = {
                "loan_name": values.get(f"loan{i}_name", ""),
                "bank": values.get(f"loan{i}_bank", ""),
                "amount": values.get(f"loan{i}_amount", ""),
                "chance": values.get(f"loan{i}_chance", ""),
                "link": values.get(f"loan{i}_link", "")
            }
            loans.append(loan)

        return loans

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
