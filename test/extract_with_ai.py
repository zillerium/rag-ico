import fitz
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
# EXTRACT PDF
# ============================================

doc = fitz.open("../ico-data/ic-409851-x6j7.pdf")

all_text = []

for page in doc:
    all_text.append(page.get_text("text"))

raw_text = "\n".join(all_text)

print(f"\n✅ Extracted {len(raw_text):,} characters")

# ============================================
# PROMPT
# ============================================

SYSTEM_PROMPT = """
You are cleaning noisy PDF text extraction.

Your ONLY goals are:

- preserve meaning exactly
- preserve legal wording
- preserve numbering
- preserve quotations
- preserve section headings
- merge broken wrapped lines
- remove repeated headers and footers
- remove standalone page numbers
- preserve paragraph continuity

Do NOT:
- summarize
- simplify
- rewrite legally
- omit content
- infer missing content

Return only cleaned legal text.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("\n🤖 Sending to model...")

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": raw_text
        }
    ],
    temperature=0
)

cleaned = response.choices[0].message.content

# ============================================
# SAVE OUTPUT
# ============================================

output_path = "../comparison-output/cleaned_ai_output.txt"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(cleaned)

print(f"\n✅ Saved cleaned output:")
print(output_path)
