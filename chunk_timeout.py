import os
import json
import re
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
# INPUT
# ============================================

INPUT_FILE = "../comparison-output/ic-456272-d0b1_semantic.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    semantic_text = f.read()

print(f"✅ Loaded {len(semantic_text):,} chars")

# ============================================
# EXTRACT METADATA
# ============================================

date_match = re.search(r"Date:\s*(.+)", semantic_text)
decision_date = date_match.group(1).strip() if date_match else "UNKNOWN"

ref_match = re.search(r"Reference:\s*([A-Z0-9\-]+)", semantic_text)
decision_ref = ref_match.group(1).strip() if ref_match else "UNKNOWN"

authority_match = re.search(r"Public Authority:\s*(.+)", semantic_text)
public_authority = authority_match.group(1).strip() if authority_match else "UNKNOWN"

# ============================================
# PROMPT
# ============================================

SYSTEM_PROMPT = f"""
You are extracting procedural legal reasoning structures from ICO decisions.

Decision metadata:

- decision_date: {decision_date}
- decision_reference: {decision_ref}
- public_authority: {public_authority}
- dn_type: procedural_compliance

This decision concerns:
- procedural compliance
- statutory response obligations
- timelines
- enforcement consequences

The request scope itself is legally important.

Preserve:
- chronology
- request scope
- procedural obligations
- statutory deadlines
- enforcement consequences
- contempt of court references
- compliance failures

For each procedural issue output:

{{
  "decision_date": "{decision_date}",
  "decision_reference": "{decision_ref}",
  "public_authority": "{public_authority}",
  "dn_type": "procedural_compliance",
  "issue_id": "...",
  "foi_request_scope": "...",
  "timeline": [],
  "statutory_provisions": [],
  "procedural_failures": [],
  "commissioner_findings": [],
  "required_steps": [],
  "enforcement_risks": [],
  "important_procedural_patterns": [],
  "outcome": "..."
}}

Return ONLY valid JSON array.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("🤖 Extracting procedural legal reasoning...")

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": semantic_text
        }
    ],
    temperature=0.1
)

content = response.choices[0].message.content

# ============================================
# SAVE
# ============================================

base_name = os.path.splitext(
    os.path.basename(INPUT_FILE)
)[0]

OUTPUT_FILE = (
    f"../comparison-output/"
    f"{base_name}_procedural_reasoning.json"
)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved:")
print(OUTPUT_FILE)

# ============================================
# VALIDATE
# ============================================

try:
    data = json.loads(content)
    print(f"✅ Parsed {len(data)} procedural issues")
except Exception as e:
    print("❌ JSON parse failed")
    print(e)
