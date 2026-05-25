import fitz
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# ============================================
# CONFIG
# ============================================

PDF_PATH = "../ico-data/ic-409851-x6j7.pdf"
OUTPUT_PATH = "../comparison-output/normalized_output.txt"

MODEL = "gpt-5.4-mini"

# ============================================
# LOAD ENV
# ============================================

load_dotenv()

print("ENDPOINT =", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("KEY EXISTS =", bool(os.getenv("AZURE_OPENAI_KEY")))
print("API VERSION =", os.getenv("OPENAI_API_VERSION"))

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-12-01-preview"
)

# ============================================
# EXTRACT ENTIRE DOCUMENT
# ============================================

print("📄 Extracting PDF text...")

doc = fitz.open(PDF_PATH)

all_pages = []

for page_num, page in enumerate(doc, 1):

    text = page.get_text("text")

    all_pages.append(f"\n--- PAGE {page_num} ---\n{text}")

raw_text = "\n".join(all_pages)

print(f"✅ Extracted {len(raw_text):,} characters")

# ============================================
# SYSTEM PROMPT
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
- remove repeated page headers
- remove repeated page footers
- remove standalone page numbers
- preserve paragraph continuity

Do NOT:
- summarize
- simplify
- rewrite legally
- infer missing content
- restructure the document
- omit substantive content

Return only lightly normalized legal text.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("🤖 Sending to model...")

response = client.chat.completions.create(
    model=MODEL,
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

normalized_text = response.choices[0].message.content

# ============================================
# SAVE OUTPUT
# ============================================

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(normalized_text)

print(f"✅ Saved normalized output to:")
print(OUTPUT_PATH)

print(f"✅ Final size: {len(normalized_text):,} characters")
