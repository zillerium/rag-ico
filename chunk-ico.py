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
    semantic_text = f.read()

print(f"✅ Loaded {len(semantic_text):,} chars")

# ============================================
# CHUNKING PROMPT
# ============================================

SYSTEM_PROMPT = """
You are creating semantic chunks for a legal RAG system.

The future queries will NOT be simple keyword searches.

The future queries will usually be:
- legal complaints
- legal reasoning
- factual disputes
- public interest arguments
- exemption arguments
- procedural fairness arguments

Your task:

Create coherent legal reasoning chunks.

Rules:

- Keep related legal reasoning together.
- Preserve argumentative continuity.
- Preserve legal tests with their associated analysis.
- Preserve factual context needed to understand reasoning.
- Preserve balancing exercises as unified chunks.
- Do NOT create tiny chunks.
- Do NOT split merely by paragraph count.
- Split only when legal reasoning materially changes.

For each chunk output:

{
  "chunk_id": "...",
  "chunk_type": "...",
  "legal_topic": "...",
  "summary": "...",
  "text": "..."
}

Return ONLY valid JSON array.
"""

# ============================================
# SEND TO MODEL
# ============================================

print("🤖 Creating semantic legal chunks...")

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
# SAVE OUTPUT
# ============================================

OUTPUT_FILE = "../comparison-output/legal_chunks.json"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved chunks:")
print(OUTPUT_FILE)

# ============================================
# OPTIONAL VALIDATION
# ============================================

try:
    chunks = json.loads(content)
    print(f"✅ Parsed {len(chunks)} chunks")
except Exception as e:
    print("❌ JSON parse failed")
    print(e)
