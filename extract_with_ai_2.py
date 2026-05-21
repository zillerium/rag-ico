from dotenv import load_dotenv
from openai import AzureOpenAI
import os

load_dotenv()

# ============================================
# WORKING CLIENT
# ============================================

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_MODEL_EUROPE_ENDPOINT"),
    api_key=os.getenv("AZURE_EUROPE_KEY"),
)

# ============================================
# LOAD CLEANED TEXT
# ============================================

INPUT_FILE = "../comparison-output/cleaned_ai_output.txt"
OUTPUT_FILE = "../comparison-output/headings_tagged.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    cleaned_text = f.read()

print(f"✅ Loaded {len(cleaned_text):,} characters")

# ============================================
# PROMPT
# ============================================

SYSTEM_PROMPT = """
You are analyzing cleaned legal text.

Your ONLY task is to identify semantic section headings.

Rules:

- Preserve ALL original text exactly.
- Do NOT rewrite content.
- Do NOT summarize.
- Do NOT simplify.
- Do NOT remove content.
- Do NOT reorder content.
- Add the marker [HEADING] immediately before text that functions as a legal section heading.

Examples of headings:
- Request and response
- Scope of the case
- Reasons for decision
- Public interest arguments in favour of disclosure
- Balance of the public interest

Return the FULL original text with heading markers added.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("🤖 Detecting headings...")

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": cleaned_text
        }
    ],
    temperature=0
)

tagged_text = response.choices[0].message.content

# ============================================
# SAVE OUTPUT
# ============================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(tagged_text)

print(f"\n✅ Saved:")
print(OUTPUT_FILE)
