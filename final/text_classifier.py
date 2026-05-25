import os
import json
import shutil
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
# DIRECTORIES
# ============================================

INPUT_DIR = "../ico-text"

EXEMPTION_DIR = "../ico-exemption"
TIMEOUT_DIR = "../ico-timeout"

# Create output directories if missing
os.makedirs(EXEMPTION_DIR, exist_ok=True)
os.makedirs(TIMEOUT_DIR, exist_ok=True)

# ============================================
# PROMPT
# ============================================

SYSTEM_PROMPT = """
You are classifying ICO Decision Notices (DNs).

You must classify the DN into ONE of these categories:

1. procedural_compliance
2. substantive_exemption

Classification guidance:

procedural_compliance:
- primarily about failure to respond
- section 10 breach
- procedural obligations
- timelines
- compliance failures
- requirement to provide substantive response
- enforcement warnings
- contempt of court references
- administrative compliance focus

substantive_exemption:
- exemptions under FOIA
- public interest balancing
- competing disclosure arguments
- section 30/31/36/40/42 reasoning
- legal professional privilege
- confidentiality
- detailed legal reasoning about disclosure

Important:
- classify based on the MAIN purpose of the DN
- not isolated phrases
- wording may vary
- DNs may mention section 10 incidentally without being procedural cases

Return ONLY valid JSON:

{
  "classification": "...",
  "confidence": "...",
  "reasoning": "..."
}
"""

# ============================================
# GET ALL TXT FILES
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
    # CLASSIFY
    # ============================================

    try:

        print("🤖 Classifying DN...")

        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": text[:15000]
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        print("\n📘 Raw Classification")
        print(content)

    except Exception as e:
        print(f"❌ Classification failed: {e}")
        continue

    # ============================================
    # PARSE JSON
    # ============================================

    try:

        data = json.loads(content)

        classification = data.get(
            "classification",
            "substantive_exemption"
        )

        confidence = data.get("confidence", "unknown")

        print("\n✅ Parsed classification")
        print(f"   Type: {classification}")
        print(f"   Confidence: {confidence}")

    except Exception as e:

        print("\n❌ JSON parse failed")
        print(e)

        print("⚠️ Defaulting to substantive_exemption")

        classification = "substantive_exemption"

    # ============================================
    # MOVE FILE
    # ============================================

    try:

        if classification == "procedural_compliance":

            destination = os.path.join(
                TIMEOUT_DIR,
                filename
            )

            print("\n➡️ Moving to timeout directory")

        else:

            destination = os.path.join(
                EXEMPTION_DIR,
                filename
            )

            print("\n➡️ Moving to exemption directory")

        shutil.move(input_path, destination)

        print(f"✅ Moved file:")
        print(destination)

    except Exception as e:

        print(f"❌ Failed moving file: {e}")

print("\n🎉 Classification complete")
