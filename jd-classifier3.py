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
# PYDANTIC SCHEMA DEFINITION (RELATIONAL SYNTHESIS)
# ============================================
class IntersectedReality(BaseModel):
    connected_terms: List[str] = Field(
        description="The terms being linked together by the LLM. E.g., ['Java', 'CI/CD', 'Frequent Releases', 'Approachable']"
    )
    operational_implication: str = Field(
        description="What this combination actually means for daily work (e.g., complex versioning, git controls, regression testing matrices, handling rollback strategies)."
    )
    cross_functional_stakeholders: List[str] = Field(
        description="The teams or roles this candidate must collaborate with as a direct result of these linked terms (e.g., QA Testers, Release Managers, Devs, Operations staff)."
    )
    probable_business_context: str = Field(
        description="The underlying business landscape or tension causing this (e.g., rolling out frequent patches in an emerging, highly auditable financial tech ecosystem)."
    )

class TieredSoftwareEngineeringSchema(BaseModel):
    role_tier: str = Field(
        description="The classified segment of this tech role. Must be one of: 'Application Development', 'DevOps & Infrastructure', 'Engineering Management', 'Data Engineering'"
    )
    company: str = Field(description="The organization advertising the role.")
    job_title: str = Field(description="The formal role title.")
    job_summary: str = Field(description="Concise high-level overview of the role's mission and core purpose.")
    
    # Core Extraction Arrays
    tech_stack: List[str] = Field(description="Explicit hard skills, frameworks, languages, cloud tools.")
    methodologies: List[str] = Field(description="Delivery styles, testing practices, deployment cadences.")
    soft_skills: List[str] = Field(description="Interpersonal, behavioral, and leadership traits requested.")
    
    # The Relational Synthesis Layer (Solves the 1,000+ JD scaling problem)
    relational_synthesis: List[IntersectedReality] = Field(
        description="CRITICAL: Read between the lines of the entire JD. Intersect the tech stack, methodologies, and soft skills to deduce the real-world engineering realities, version control pressures, and cross-functional team dynamics."
    )
    
    job_benefits: str = Field(description="Salary, perks, pension, and remote/hybrid policies.")

# ============================================
# SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """
You are an expert technical recruiter and systems architect specializing in Software Engineering and Tech Leadership roles. 

Your task is to parse messy job advertisements into a highly synthesized JSON schema. 
Instead of looking at terms in isolation, you must globally evaluate how the technologies, working methods, and traits connect to form specific, real-world operational realities. 

Deduce what high-level corporate buzzwords like 'Technical Leadership' or 'Frequent Releases' *actually* mean at a practical engineering level for the specified stack.
"""

# ============================================
# GET TXT FILES
# ============================================
txt_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".txt")]
print(f"\n📂 Found {len(txt_files)} text files to synthesize")

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
    # LLM EXTRACTION & SYNTHESIS
    # ============================================
    try:
        print("🤖 Running Relational Synthesis Engine...")

        response = client.beta.chat.completions.parse(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:30000]}
            ],
            response_format=TieredSoftwareEngineeringSchema,
            temperature=0
        )

        # Retrieve the validated data model natively
        extracted_data = response.choices[0].message.parsed
        data_dict = extracted_data.model_dump()
        print("✅ Synthesized JSON generated & validated successfully.")

    except Exception as e:
        print(f"❌ Extraction/Synthesis failed: {e}")
        continue

    # ============================================
    # OUTPUT FILE
    # ============================================
    try:
        output_filename = os.path.splitext(filename)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved deep-mapped JSON to: {output_path}")

    except Exception as e:
        print(f"❌ Failed saving JSON: {e}")

print("\n🎉 All JDs parsed, tiered, and dynamically synthesized!")
