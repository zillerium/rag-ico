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
# INPUT / OUTPUT
# ============================================

INPUT_FILE = "../comparison-output/cleaned_ai_output.txt"
OUTPUT_FILE = "../comparison-output/semantic_structure.txt"

# ============================================
# LOAD CLEANED TEXT
# ============================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    cleaned_text = f.read()

print(f"✅ Loaded {len(cleaned_text):,} characters")

# ============================================
# PROMPT
# ============================================

SYSTEM_PROMPT = """
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
- The same wording may have different semantic roles depending on context.

Return the FULL original text with semantic tags added.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("🤖 Detecting semantic legal structure...")

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

semantic_text = response.choices[0].message.content

# ============================================
# SAVE OUTPUT
# ============================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(semantic_text)

print("\n✅ Saved semantic structure output:")
print(OUTPUT_FILE)
