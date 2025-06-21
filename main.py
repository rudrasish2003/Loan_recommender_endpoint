from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from typing import List
import os
from dotenv import load_dotenv
import re

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

# Output schema
class LoanResponse(BaseModel):
    loan_name: str
    bank: str
    amount: str
    chance: str
    link: str

@app.post("/get-loans", response_model=List[LoanResponse])
async def get_loans(request: FarmerRequest):
    prompt = f"""
You are an expert government loan and microfinance assistant for Indian farmers. 
Given:  
- Location: {request.location}  
- Annual Income: ₹{request.earning}  
- Crop: {request.crop}  

Find the most accessible loans and microloans a farmer in this scenario can apply for in their rural region.

Return results in a table with maximum 5 rows, each being very short and precise (within 20 words total).

Table format:
Loan Name | Bank | Amount (₹) | Chance (%) | Link
"""

    try:
        response = model.generate_content(prompt)
        table = response.text.strip()

        # 🚨 DEBUG: Print raw Gemini output
        print("\n🧾 Raw Gemini Response:\n")
        print(table)
        print("\n🔍 Parsing table rows...\n")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Parse response table
    rows = re.findall(r"^(?!Loan Name).*?\|.*?\|.*?\|.*?\|.*?$", table, re.MULTILINE)

    # 🚨 DEBUG: Print parsed rows
    print(f"🧩 Extracted Rows ({len(rows)}):")
    for r in rows:
        print(r)

    results = []

    for row in rows:
        parts = [part.strip() for part in row.split("|")]
        if len(parts) == 5:
            results.append(LoanResponse(
                loan_name=parts[0],
                bank=parts[1],
                amount=parts[2],
                chance=parts[3],
                link=parts[4]
            ))

    if not results:
        raise HTTPException(status_code=404, detail="No valid loan results found.")
    
    return results
