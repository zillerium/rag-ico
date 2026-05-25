import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

# ============================================
# AZURE CLIENT
# ============================================
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_MODEL_EUROPE_ENDPOINT"),
    api_key=os.getenv("AZURE_EUROPE_KEY"),
)

INPUT_DIR = "../jd-text"
OUTPUT_DIR = "../jd-json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================
# PYDANTIC SCHEMA DEFINITION
# ============================================
class SoftwareEngineeringRoleSchema(BaseModel):
    company: str = Field(description="The organization advertising the role.")
    job_title: str = Field(description="The formal role title.")
    job_type: str = Field(description="Permanent, Contract, Temporary, Internship, etc.")
    job_summary: str = Field(description="Concise high-level overview of the role, its mission, and core purpose.")
    
    # Deepened technical breakdown for CV matching
    tech_stack: List[str] = Field(description="Explicitly mentioned hard technologies, languages, frameworks, cloud providers, databases. e.g., ['Java', 'Spring', 'AWS']")
    methodologies: List[str] = Field(description="Engineering practices, delivery frameworks, or deployment styles. e.g., ['CI/CD', 'Automated Testing', 'Agile']")
    soft_skills: List[str] = Field(description="Interpersonal traits, leadership qualities, and behavioral skills. e.g., ['Problem-solving', 'Conflict resolution', 'Mentoring']")
    domain_context: List[str] = Field(description="Industry-specific realities or functional responsibilities. e.g., ['Regulated Environment', 'Fintech', 'Application Ownership']")
    
    job_details_raw: str = Field(description="Full text breakdown of daily operational responsibilities and duties.")
    job_benefits: str = Field(description="Salary, pension, bonus, hybrid policies, and perks.")
    company_description: str = Field(description="Description of company culture, history, and market positioning.")

# ============================================
# SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """
You are an expert technical recruiter specializing in Software Engineering and Tech Leadership roles. 
Your task is to parse messy job advertisements into a clean, structured schema tailored for CV alignment.

Normalize technology terms into standard industry naming conventions where appropriate (e.g., transform 'Continuous Integration' or 'automated deployment pipelines' into 'CI/CD'). 
Extract skills carefully based on their context; do not hallucinate skills that are not explicitly stated or heavily implied by the text.
"""

# ============================================
# GET TXT FILES
# ============================================
txt_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".txt")]
print(f"\n📂 Found {len(txt_files)} text files")

# ============================================
# PROCESS FILES
# ============================================
for filename in txt_files:
    print("\n" + "=" * 70)
    print(f"📄 Processing: {filename}")
    input_path = os.path.join(INPUT_DIR, filename)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"✅ Loaded {len(text):,} chars")
    except Exception as e:
        print(f"❌ Failed reading file: {e}")
        continue

    # ============================================
    # LLM EXTRACTION VIA STRUCTURED OUTPUTS
    # ============================================
    try:
        print("🤖 Extracting structured data using Software Engineering schema...")

        response = client.beta.chat.completions.parse(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:30000]}
            ],
            response_format=SoftwareEngineeringRoleSchema,
            temperature=0
        )

        # The response object is natively validated into our Pydantic model
        extracted_data = response.choices[0].message.parsed
        
        # Convert Pydantic object directly to a standard Python dictionary
        data_dict = extracted_data.model_dump()
        print("✅ Structured extraction complete & validated.")

    except Exception as e:
        print(f"❌ Structured extraction failed: {e}")
        continue

    # ============================================
    # OUTPUT FILE
    # ============================================
    try:
        output_filename = os.path.splitext(filename)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved parsing target to: {output_path}")

    except Exception as e:
        print(f"❌ Failed saving JSON: {e}")

print("\n🎉 JD extraction complete")
