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
# INPUT FILE
# ============================================

INPUT_FILE = "../comparison-output/ic-409851-x6j7_semantic.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

print(f"✅ Loaded {len(text):,} chars")

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
# SEND TO MODEL
# ============================================

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

print("\n📘 Classification Result")
print("=" * 60)
print(content)

# ============================================
# OPTIONAL JSON VALIDATION
# ============================================

try:
    data = json.loads(content)

    classification = data.get("classification")

    print("\n✅ Parsed classification:")
    print(f"   {classification}")

    # ============================================
    # ROUTING LOGIC
    # ============================================

    if classification == "procedural_compliance":
        print("\n➡️ Route to PROCEDURAL chunker")

    else:
        print("\n➡️ Route to SUBSTANTIVE EXEMPTION chunker")

except Exception as e:
    print("\n❌ JSON parse failed")
    print(e)
