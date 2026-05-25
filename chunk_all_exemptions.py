import os
import json
import re
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

INPUT_DIR = "../ico-exemption"

OUTPUT_JSON_DIR = "../ico-exemption-json"

PROCESSED_DIR = "../ico-exemption-processed"

# ============================================
# CREATE DIRS
# ============================================

os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ============================================
# CLEAN JSON RESPONSE
# ============================================

def clean_json_response(content):

    """
    Remove markdown code fences if the model adds them.
    """

    content = content.strip()

    content = re.sub(
        r"^```json",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"^```",
        "",
        content
    )

    content = re.sub(
        r"```$",
        "",
        content
    )

    return content.strip()

# ============================================
# GET INPUT FILES
# ============================================

txt_files = [
    f for f in os.listdir(INPUT_DIR)
    if f.lower().endswith(".txt")
]

print(f"\n📂 Found {len(txt_files)} exemption files")

# ============================================
# PROCESS FILES
# ============================================

for filename in txt_files:

    print("\n" + "=" * 80)
    print(f"📄 Processing: {filename}")

    INPUT_FILE = os.path.join(INPUT_DIR, filename)

    # ============================================
    # READ FILE
    # ============================================

    try:

        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            semantic_text = f.read()

        print(f"✅ Loaded {len(semantic_text):,} chars")

    except Exception as e:

        print(f"❌ Failed reading file: {e}")
        continue

    # ============================================
    # METADATA
    # ============================================

    # Decision reference from filename
    # Example:
    # ic-409851-x6j7_semantic.txt
    # ->
    # IC-409851-X6J7

    base_name = os.path.splitext(filename)[0]

    decision_ref = (
        base_name
        .replace("_semantic", "")
        .replace("_extracted", "")
        .upper()
    )

    # Lightweight date extraction only

    date_match = re.search(
        r"Date:\s*(.+)",
        semantic_text,
        re.IGNORECASE
    )

    decision_date = (
        date_match.group(1).strip()
        if date_match else "UNKNOWN"
    )

    # Lightweight authority extraction only

    authority_match = re.search(
        r"Public Authority:\s*(.+)",
        semantic_text,
        re.IGNORECASE
    )

    public_authority = (
        authority_match.group(1).strip()
        if authority_match else "UNKNOWN"
    )

    print(f"📅 Decision date: {decision_date}")
    print(f"📘 Reference: {decision_ref}")
    print(f"🏛️ Authority: {public_authority}")

    # ============================================
    # PROMPT
    # ============================================

    SYSTEM_PROMPT = """
You are extracting legal reasoning structures from ICO decisions.

The goal is NOT to summarize the case.

The goal is to extract:

- competing legal arguments
- public interest balancing
- legal thresholds
- precedents
- statutory tests
- Commissioner reasoning
- why one side prevailed

Return ONLY a valid JSON array.

DO NOT include:
- decision_date
- decision_reference
- public_authority
- dn_type

Those fields are added automatically later.

For each legal issue output:

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
  "important_reasoning_patterns": [],
  "outcome": "..."
}

Rules:

- Return ONLY valid JSON
- No markdown
- No explanations
- No code fences
- Preserve legal reasoning accurately
- Separate distinct legal/public-interest issues
"""

    # ============================================
    # SEND TO MODEL
    # ============================================

    try:

        print("🤖 Extracting substantive legal reasoning...")

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

        content = clean_json_response(content)

    except Exception as e:

        print(f"❌ OpenAI request failed: {e}")
        continue

    # ============================================
    # PARSE JSON
    # ============================================

    try:

        data = json.loads(content)

        # Ensure list
        if not isinstance(data, list):

            raise ValueError(
                "Model output was not a JSON array"
            )

        # ============================================
        # ADD METADATA DETERMINISTICALLY
        # ============================================

        for issue in data:

            issue["decision_date"] = decision_date

            issue["decision_reference"] = decision_ref

            issue["public_authority"] = public_authority

            issue["dn_type"] = "public_interest_exemption"

        print(f"✅ Parsed {len(data)} legal issues")

    except Exception as e:

        print("❌ JSON parse failed")
        print(e)

        failed_file = os.path.join(
            OUTPUT_JSON_DIR,
            f"{base_name}_FAILED.txt"
        )

        with open(
            failed_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

        print(f"🛑 Saved failed output: {failed_file}")

        continue

    # ============================================
    # BUILD OUTPUT FILE
    # ============================================

    OUTPUT_FILE = os.path.join(
        OUTPUT_JSON_DIR,
        f"{base_name}_substantive_reasoning.json"
    )

    # ============================================
    # SAVE CLEAN JSON
    # ============================================

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"\n✅ Saved JSON:")
        print(OUTPUT_FILE)

    except Exception as e:

        print(f"❌ Failed saving JSON: {e}")
        continue

    # ============================================
    # MOVE INPUT FILE
    # ============================================

    try:

        processed_path = os.path.join(
            PROCESSED_DIR,
            filename
        )

        shutil.move(
            INPUT_FILE,
            processed_path
        )

        print("\n📦 Moved processed input file:")
        print(processed_path)

    except Exception as e:

        print(f"❌ Failed moving input file: {e}")

# ============================================
# COMPLETE
# ============================================

print("\n🎉 Exemption processing complete")

