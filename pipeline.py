import json
import os
import re
import requests
import fitz  #PyMuPDF
from dotenv import load_dotenv

load_dotenv()

#LLM FUNCTIONS
HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://router.huggingface.co/v1/chat/completions"

def llm_call(prompt):
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, headers=headers, json={
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3000, 
            "temperature": 0.1
        }, timeout=90)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM Call Error: {e}")
        return ""

def extract_urbanroof_data(text):
    prompt = f"""
    Extract building findings from this inspection text into a SINGLE JSON object. 
    Identify:
    1. negative_side: Internal symptoms (Dampness, Seepage, etc.)
    2. positive_side: External causes (Tile gaps, plumbing, cracks).
    3. structural_health: Rating of RCC/Plaster.

    TEXT: {text[:8000]}

    RETURN ONLY THE JSON OBJECT:
    {{ "negative_side": [], "positive_side": [], "structural_health": "" }}
    """
    raw = llm_call(prompt)
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except: pass
    return { "negative_side": [], "positive_side": [], "structural_health": "N/A" }

def generate_ddr(extracted_data):
    prompt = f"""
    You are a Senior Building Pathologist at UrbanRoof. Generate a 'Detailed Diagnosis Report' in Markdown.
    Use terms like 'Capillary Action' and 'PMM Grouting'.
    
    Generate a 'Detailed Diagnosis Report' following the UrbanRoof Private Limited format. [cite: 189, 215]

    Structure:
    1. SECTION 1: INTRODUCTION (Background, Objective, Scope of Work) [cite: 259, 264, 270]
    2. SECTION 2: GENERAL INFORMATION (Client details, Description of Site) [cite: 289, 298]
    3. SECTION 3: VISUAL OBSERVATION AND READINGS 
       - 3.1 Summary of Sources of Leakage [cite: 304]
       - 3.2 Negative Side Inputs (Symptoms observed internally) [cite: 60]
       - 3.3 Positive Side Inputs (Causes observed externally) [cite: 62]
    4. SECTION 4: ANALYSIS & SUGGESTIONS
       - 4.1 Actions Required & Suggested Therapies (e.g., Grouting treatment using Liquid Polymer modified mortar, Plaster work with Dr. Fixit URP) [cite: 107, 114]
       - 4.2 Summary Table (Mapping Symptoms to Causes) [cite: 124]
    5. SECTION 5: LIMITATION AND PRECAUTION NOTE [cite: 218]

    DATA: {json.dumps(extracted_data)}
    """
    return llm_call(prompt)

#MAIN PIPELINE
def run_pipeline(insp_path, ther_path):
    text = ""
    for path in [insp_path, ther_path]:
        if os.path.exists(path):
            doc = fitz.open(path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()

    data = extract_urbanroof_data(text)
    report_md = generate_ddr(data)
    
    return report_md