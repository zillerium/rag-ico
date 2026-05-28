import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from typing import List

# Load environment configuration variables
load_dotenv()

# ============================================
# INITIALIZATION & DIRECTORY ROUTING SETUP
# ============================================
endpoint = os.getenv("AZURE_MODEL_EUROPE_ENDPOINT")
api_key = os.getenv("AZURE_EUROPE_KEY")

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=endpoint if endpoint else "",
    api_key=api_key if api_key else "",
)

SKILLS_LIB_PATH = "skills_library.json"
ROLES_INPUT_DIR = "roles-input"
CV_OUTPUT_DIR = "cv-output"

# Guarantee operational folder structures exist prior to loop execution
os.makedirs(ROLES_INPUT_DIR, exist_ok=True)
os.makedirs(CV_OUTPUT_DIR, exist_ok=True)

# ============================================
# TARGET OUTPUT SCHEMA STRUCTURES
# ============================================
class FinalCVRoleSchema(BaseModel):
    role: str = Field(description="The formal title of the position.")
    company: str = Field(description="The name of the company or venture platform.")
    date: str = Field(description="The time or operational timeframe.")
    description: List[str] = Field(
        description="Dynamic synthesized narrative bullets blending raw achievements with specific context modifiers."
    )
    skills: List[str] = Field(
        description="Flat array containing the exact dot-notated library keys utilized or referenced in this output."
    )

class MasterSynthesizedCVSchema(BaseModel):
    assembled_roles: List[dict] = Field(description="The finalized timeline array of all compiled professional career roles.")

# ============================================
# EXECUTIVE PROMPT DEFINE
# ============================================
SYSTEM_PROMPT = """
You are an advanced CV resume parser engine. Your task is to accept a specific corporate profile role alongside an array of capability directives.
Combine the verified achievements with the specific context modifiers to generate highly professional, cohesive executive bullet points.
"""

# ============================================
# DETACHED UTILITY HELPER METHODS
# ============================================
def extract_nested_skill(library: dict, lookup_key: str) -> List[str]:
    """Traverses dot-notated dictionary keys to extract target capability lists."""
    try:
        parts = lookup_key.split('.')
        current = library
        for part in parts:
            current = current[part]
        return current if isinstance(current, list) else []
    except Exception:
        return []

def load_external_json_data(file_path: str) -> dict:
    """Safely loads localized data payloads out of disk storage matrices."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Critical Error reading data artifact at {file_path}: {e}")
        return {}

# ============================================
# PRIMARY PIPELINE EXECUTION TREE
# ============================================
def run_cv_assembly_pipeline():
    print("🚀 Initializing Decoupled Multi-Role CV Assembly Pipeline...")
    
    # Load Master Lookup Skills Dictionary out of static disk file asset
    if not os.path.exists(SKILLS_LIB_PATH):
        print(f"❌ Halting: Master Skills Reference Library file missing at '{SKILLS_LIB_PATH}'")
        return
    
    master_library = load_external_json_data(SKILLS_LIB_PATH)
    
    # Locate all active configuration files currently residing inside the intake block
    role_files = [f for f in os.listdir(ROLES_INPUT_DIR) if f.lower().endswith(".json")]
    if not role_files:
        print(f"⚠️ Intake pipeline empty! Please place role data instances into: {ROLES_INPUT_DIR}/")
        return
        
    print(f"📂 Detected {len(role_files)} historical role specifications to synthesize.")
    
    # Define collection container to append successful generation blocks into
    master_cv_accumulator = []

    # Sequential isolated processing engine loop tracking execution safely
    for idx, filename in enumerate(role_files, start=1):
        file_target_path = os.path.join(ROLES_INPUT_DIR, filename)
        print(f"\n⚡ Processing Node [{idx}/{len(role_files)}]: Parsing {filename}...")
        
        role_data = load_external_json_data(file_target_path)
        if not role_data or "meta" not in role_data:
            print(f"⏩ Skipping corrupted structural record matrix file: {filename}")
            continue
            
        # Pack only the necessary variables to minimize prompt token footprint
        user_payload = {
            "role_meta": role_data.get("meta", {}),
            "achievements": role_data.get("verifiable_achievements", []),
            "mappings": role_data.get("applied_capability_matrix", [])
        }

        try:
            print(f"🤖 Dispatching token-optimized transaction framework payload to Azure Gateway...")
            response = client.beta.chat.completions.parse(
                model="gpt-5.4-mini", 
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(user_payload, indent=2)}
                ],
                response_format=FinalCVRoleSchema,
                temperature=0
            )
            
            raw_result = response.choices[0].message.parsed
            output_json = raw_result.model_dump()
            
            # ============================================
            # LOCAL PYTHON DETERMINISTIC SKILLS ENRICHMENT
            # ============================================
            print(f"🐍 Local Python Engine running deterministic skill injection macro loops...")
            enriched_skills_bucket = []
            for key in output_json["skills"]:
                deep_phrases = extract_nested_skill(master_library, key)
                if deep_phrases:
                    enriched_skills_bucket.append({
                        "category": key,
                        "verified_capabilities": deep_phrases
                    })
            
            # Re-map the lean JSON schema list structure back to raw expanded parameters
            output_json["skills"] = enriched_skills_bucket
            
            # Append synthesized chunk into the global state collector object tracker
            master_cv_accumulator.append(output_json)
            print(f"✅ Success: Role compiled seamlessly.")
            
        except Exception as e:
            print(f"❌ Error compiling execution stream for block {filename}: {e}")
            continue

    # ============================================
    # GLOBAL ASSEMBLY COMPILATION AND EXPORT
    # ============================================
    final_output_cv_structure = {
        "assembled_roles": master_cv_accumulator
    }
    
    export_output_destination = os.path.join(CV_OUTPUT_DIR, "synthesized_cv.json")
    try:
        with open(export_output_destination, "w", encoding="utf-8") as out_file:
            json.dump(final_output_cv_structure, out_file, indent=2, ensure_ascii=False)
        print("\n" + "="*80)
        print(f"🎉 MASTER BUILD SUCCESSFUL: Integrated resume object dataset generated.")
        print(f"💾 File written safely to disk target at: {export_output_destination}")
        print("="*80)
    except Exception as e:
        print(f"❌ Failed to write file dataset out onto final disk output arrays: {e}")

if __name__ == "__main__":
    run_cv_assembly_pipeline()
