import os
import fitz
from dotenv import load_dotenv
from openai import AzureOpenAI

# ============================================
# LOAD ENV
# ============================================

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
# INPUT PDF
# ============================================

PDF_PATH = "../ico-data/ic-456272-d0b1.pdf"

# ============================================
# OUTPUT FILE
# ============================================

base_name = os.path.splitext(os.path.basename(PDF_PATH))[0]

OUTPUT_FILE = f"../comparison-output/{base_name}_semantic.txt"

# ============================================
# STEP 1 — EXTRACT RAW TEXT
# ============================================

print("\n📄 Extracting PDF text...")

doc = fitz.open(PDF_PATH)

all_text = []

for page in doc:
    text = page.get_text("text")
    all_text.append(text)

raw_text = "\n".join(all_text)

print(f"✅ Extracted {len(raw_text):,} characters")

# ============================================
# STEP 2 — AI NORMALIZATION
# ============================================

print("\n🧹 Running AI normalization...")

NORMALIZE_PROMPT = """
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

normalize_response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "system",
            "content": NORMALIZE_PROMPT
        },
        {
            "role": "user",
            "content": raw_text
        }
    ],
    temperature=0
)

cleaned_text = normalize_response.choices[0].message.content

print(f"✅ Normalized text size: {len(cleaned_text):,} characters")

# ============================================
# STEP 3 — SEMANTIC STRUCTURE TAGGING
# ============================================

print("\n🏛️ Detecting semantic legal structure...")

SEMANTIC_PROMPT = """
You are analyzing legal text.

Your task is to identify semantic legal structure.

You must infer legal section roles from meaning and context,
NOT from formatting.

Examples of semantic tags:

[MAIN_SECTION]
[SUBSECTION]
[LEGAL_TEST]
[FACTUAL_BACKGROUND]
[REQUEST]
[PUBLIC_INTEREST_ANALYSIS]
[ARGUMENTS_FOR_DISCLOSURE]
[ARGUMENTS_FOR_MAINTAINING_EXEMPTION]
[COMMISSIONER_FINDING]
[CONCLUSION]
[RIGHT_OF_APPEAL]

Rules:

- Preserve ALL original text exactly.
- Do NOT rewrite.
- Do NOT summarize.
- Do NOT simplify.
- Do NOT remove content.
- Do NOT reorder content.
- Add semantic tags immediately before headings or section boundaries.
- Use semantic understanding of legal structure.

Return the FULL original text with semantic tags added.
"""

semantic_response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "system",
            "content": SEMANTIC_PROMPT
        },
        {
            "role": "user",
            "content": cleaned_text
        }
    ],
    temperature=0
)

semantic_text = semantic_response.choices[0].message.content

print(f"✅ Semantic text size: {len(semantic_text):,} characters")

# ============================================
# STEP 4 — SAVE FINAL OUTPUT
# ============================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(semantic_text)

print("\n🎉 COMPLETE")
print(f"✅ Saved final semantic file:")
print(OUTPUT_FILE)
