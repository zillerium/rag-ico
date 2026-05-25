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

INPUT_FILE = "../comparison-output/ic-498728-j8r4_semantic.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    semantic_text = f.read()

print(f"✅ Loaded {len(semantic_text):,} chars")

# ============================================
# PROMPT
# ============================================

SYSTEM_PROMPT = """
You are extracting legal reasoning structures from ICO decisions.

The goal is NOT to summarize the case.

The goal is to extract:

- competing legal arguments
- legal thresholds
- statutory tests
- precedents relied upon
- factual drivers
- balancing logic
- Commissioner reasoning
- why one side prevailed

Law works through competing arguments and legal reasoning.

Future users of this system will likely submit:
- complaint narratives
- legal arguments
- regulatory disputes
- exemption arguments

Therefore the extraction must preserve reasoning patterns.

For each major legal issue output:

{
  "issue_id": "...",
  "legal_issue": "...",
  "statutory_provisions": [],
  "precedents": [],
  "factual_context": "...",
  "arguments_for_disclosure": [],
  "arguments_for_withholding": [],
  "legal_tests_applied": [],
  "commissioner_reasoning": "...",
  "why_arguments_succeeded_or_failed": "...",
  "outcome": "...",
  "important_reasoning_patterns": []
}

Return ONLY valid JSON.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("🤖 Extracting legal reasoning structures...")

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

# ============================================
# BUILD OUTPUT FILE NAME
# ============================================

input_filename = os.path.basename(INPUT_FILE)

# Remove extension
base_name = os.path.splitext(input_filename)[0]

# Example:
# ic-409851-x6j7_semantic
# ->
# ic-409851-x6j7_semantic_reasoning.json

OUTPUT_FILE = (
    f"../comparison-output/"
    f"{base_name}_reasoning.json"
)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved:")
print(OUTPUT_FILE)

# ============================================
# VALIDATE JSON
# ============================================

try:
    data = json.loads(content)
    print(f"✅ Parsed {len(data)} legal issues")
except Exception as e:
    print("❌ JSON parse failed")
    print(e)
