import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# ============================================
# AZURE CLIENT
# ============================================

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_MODEL_EUROPE_ENDPOINT"),
    api_key=os.getenv("AZURE_EUROPE_KEY"),
)

# ============================================
# INPUT DIRECTORY
# ============================================

INPUT_DIR = "../jd-text"

# ============================================
# OUTPUT DIRECTORY
# ============================================

OUTPUT_DIR = "../jd-json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """
You are extracting structured data from messy job adverts (JDs).

The formatting may vary heavily.

The JD may contain:
- duplicated text
- broken formatting
- missing headings
- recruiter text
- legal disclaimers
- salary blocks
- marketing text
- company descriptions
- mixed formatting
- repeated sections
- badly structured paragraphs

Your task is to extract and normalize the information.

Return ONLY valid JSON.

Required JSON structure:

{
  "company": "",
  "job_title": "",
  "job_type": "",
  "job": "",
  "job_details": "",
  "candidate_requirements": "",
  "job_benefits": "",
  "company_description": ""
}

Extraction guidance:

company:
- company advertising the role

job_title:
- actual role title

job_type:
- Permanent / Contract / Temporary / Internship etc

job:
- concise high-level overview of the role
- include mission/purpose/context

job_details:
- responsibilities
- duties
- deliverables
- operational details

candidate_requirements:
- skills
- experience
- qualifications
- technical requirements
- behavioural requirements

job_benefits:
- salary
- bonus
- pension
- remote/hybrid
- perks
- benefits

company_description:
- description of company
- culture
- mission
- market positioning

Important:
- preserve meaning
- do not invent facts
- normalize formatting
- remove duplicated content
- remove boilerplate where possible
- extract the MAIN relevant content
- return empty strings if missing

Return ONLY JSON.
"""

# ============================================
# GET TXT FILES
# ============================================

txt_files = [
    f for f in os.listdir(INPUT_DIR)
    if f.lower().endswith(".txt")
]

print(f"\n📂 Found {len(txt_files)} text files")

# ============================================
# PROCESS FILES
# ============================================

for filename in txt_files:

    print("\n" + "=" * 70)
    print(f"📄 Processing: {filename}")

    input_path = os.path.join(INPUT_DIR, filename)

    # ============================================
    # READ FILE
    # ============================================

    try:

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"✅ Loaded {len(text):,} chars")

    except Exception as e:

        print(f"❌ Failed reading file: {e}")
        continue

    # ============================================
    # LLM EXTRACTION
    # ============================================

    try:

        print("🤖 Extracting JD structure...")

        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": text[:30000]
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        print("\n📘 RAW RESPONSE")
        print(content)

    except Exception as e:

        print(f"❌ Extraction failed: {e}")
        continue

    # ============================================
    # PARSE JSON
    # ============================================

    try:

        data = json.loads(content)

        print("\n✅ JSON parsed successfully")

    except Exception as e:

        print("\n❌ JSON parse failed")
        print(e)

        # fallback structure

        data = {
            "company": "",
            "job_title": "",
            "job_type": "",
            "job": "",
            "job_details": "",
            "candidate_requirements": "",
            "job_benefits": "",
            "company_description": "",
            "parse_error": str(e)
        }

    # ============================================
    # OUTPUT FILE
    # ============================================

    try:

        output_filename = (
            os.path.splitext(filename)[0] + ".json"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            output_filename
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"\n✅ Saved:")
        print(output_path)

    except Exception as e:

        print(f"❌ Failed saving JSON: {e}")

print("\n🎉 JD extraction complete")
