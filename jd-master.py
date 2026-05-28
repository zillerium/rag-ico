import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from typing import List

# Ensure we explicitly look for a .env file in the current or parent path if needed
load_dotenv()

# ============================================
# DIAGNOSTIC INTEGRITY CHECK
# ============================================
endpoint = os.getenv("AZURE_MODEL_EUROPE_ENDPOINT")
api_key = os.getenv("AZURE_EUROPE_KEY")

if not endpoint or not api_key:
    print("⚠️ WARNING: Environment variables failed to load!")
    print(f"Endpoint found: {endpoint}")
    print(f"API Key loaded: {'Yes' if api_key else 'No'}")

# ============================================
# INITIALIZE AZURE CLIENT
# ============================================
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=endpoint if endpoint else "",
    api_key=api_key if api_key else "",
)

# ============================================
# MOCK DATA STRUCTURES FOR VANTAGE EXPERIMENT
# ============================================
ROLE_JSON_DATA = {
  "role_id": "vantage_ai_models_founder_2026",
  "meta": {
    "organization": "Vantage AI Models",
    "role_title": "Founder / Principal AI Systems Architect",
    "timeline": "March 2026 - Present"
  },
  "verifiable_achievements": [
    "Founded Vantage AI Models to spearhead venture-scale exploration, market validation, and architectural design of frontier agentic AI systems within the Lawtech, Edtech, and digital commerce ecosystems.",
    "Orchestrated technical feasibility roundtables and strategic commercial discovery loops with founders, co-founders, early adopters, and venture partners to align technological breakthroughs with institutional market fits.",
    "Engineered and presented high-accuracy semantic parsing, structured data extraction, and RAG-driven document intelligence frameworks to validate product-market fit against real-world client operational requirements."
  ],
  "applied_capability_matrix": [
    {
      "library_key": "Startup_Ecosystem_Venture_Incubation.acceleration_ecosystem_engagement",
      "context_modifier": "Leveraging elite accelerator networks and venture frameworks to position agentic AI architectures within emerging vertical markets, specifically targeting high-growth Lawtech and Edtech pipelines."
    },
    {
      "library_key": "Startup_Ecosystem_Venture_Incubation.founder_governance_equity_structuring",
      "context_modifier": "Driving strategic alignment, technical feasibility mappings, and early-stage venture discussions with potential co-founders and investment partners to structure collaborative intellectual property and equity models."
    },
    {
      "library_key": "Business_Financial_Engineering.market_positioning_defensibility",
      "context_modifier": "Engaged in active commercial market-searching and competitive landscape analysis to discover defensible data moats for automated CV parsing, legal code indexing, and cross-reference pattern matching."
    },
    {
      "library_key": "AI_Development.large_language_models",
      "context_modifier": "Translating enterprise-grade Azure OpenAI and cognitive infrastructure capabilities into high-level strategic product maps during client discovery workshops and investor presentations."
    },
    {
      "library_key": "AI_Development.vector_search_rag",
      "context_modifier": "Architecting early-stage RAG topologies and custom vector search layouts explicitly designed to solve concrete case law and complex document isolation challenges raised by early adopters."
    },
    {
      "library_key": "System_Development_Lifecycle.architectural_conceptualization",
      "context_modifier": "Managing user engagement analysis and high-level design definitions to guide rapid Proof of Concept (POC) deployments directly informed by external founder and client feedback loops."
    }
  ]
}

MASTER_LIBRARY_DATA = {
  "UI": {
    "core": ["Next.js", "TypeScript", "Tailwind CSS"],
    "infrastructure": ["Vercel", "GitHub Actions (CI/CD)"]
  },
  "AI_Development": {
    "large_language_models": [
      "Programmatic LLM Engineering & Context Window Management (OpenAI API)",
      "Enterprise Cognitive Infrastructure Architecture (Azure OpenAI, Azure AI Foundry)"
    ],
    "vector_search_rag": [
      "Retrieval-Augmented Generation (RAG) Model Design & Semantic Topologies",
      "High-Performance Vector Database Deployment & Indexing (Pinecone)"
    ]
  },
  "System_Development_Lifecycle": {
    "architectural_conceptualization": [
      "User Engagement Analysis & Behavioral Design Requirements Gathering",
      "High-Level Design (HLD) Topologies & Low-Level Design (LLD) Code Specifications",
      "Proof of Concept (POC) Prototyping & Feasibility Validation Testing"
    ]
  },
  "Business_Financial_Engineering": {
    "market_positioning_defensibility": [
      "Strategic Business Model Architecture (Enterprise B2B, Consumer B2C, Syndicated B2B2C Hybrid Ecosystems)",
      "Defensible Data Moat Engineering & Proprietary IP Value-Capture Strategies",
      "Competitive Landscape Asymmetry Analysis & Product Uniqueness Validation"
    ]
  },
  "Startup_Ecosystem_Venture_Incubation": {
    "acceleration_ecosystem_engagement": [
      "Venture Incubation & Accelerator Optimization (AI Forge Elite Cohorts, Barclays Eagle Labs, Decent Network Ecosystem)",
      "High-Performance Technical Hackathon Execution & Non-Dilutive Capital Prize Acquisition",
      "Emerging Industrial Sector Exploitation & Venture Engineering (Generative AI, Sovereign Decoupled Blockchains)"
    ],
    "founder_governance_equity_structuring": [
      "Co-Founder Legal Alignment, Structural Equity Negotiations & Shareholder Rights Agreements",
      "Early-Stage Venture Valuation Modeling & Post-Money Market Capitalization Forecasting"
    ]
  }
}

# ============================================
# TARGET OUTPUT SCHEMA STRUCTURE
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

# ============================================
# EXECUTIVE PROMPT & PROCESSING
# ============================================
SYSTEM_PROMPT = """
You are an advanced CV resume parser engine. Your task is to accept a specific corporate profile role alongside an array of capability directives.
Combine the verified achievements with the specific context modifiers to generate highly professional, cohesive executive bullet points.
"""

def extract_nested_skill(library: dict, lookup_key: str) -> List[str]:
    try:
        parts = lookup_key.split('.')
        current = library
        for part in parts:
            current = current[part]
        return current if isinstance(current, list) else []
    except Exception:
        return []

def run_test_pipeline():
    print("🚀 Initializing Minimal Token Processing Test Pipeline...")
    
    user_payload = {
        "role_meta": ROLE_JSON_DATA["meta"],
        "achievements": ROLE_JSON_DATA["verifiable_achievements"],
        "mappings": ROLE_JSON_DATA["applied_capability_matrix"]
    }

    try:
        # Match your exact production sample settings
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
        # LOCAL PYTHON ENRICHMENT ENGINE
        # ============================================
        enriched_skills_bucket = []
        for key in output_json["skills"]:
            deep_phrases = extract_nested_skill(MASTER_LIBRARY_DATA, key)
            if deep_phrases:
                enriched_skills_bucket.append({
                    "category": key,
                    "verified_capabilities": deep_phrases
                })
        
        output_json["skills"] = enriched_skills_bucket
        
        print("\n🏆 TARGET RESULT STRUCTURAL TEST OUTPUT:")
        print(json.dumps(output_json, indent=2))
        
    except Exception as e:
        print(f"❌ Error compiling output execution tree: {e}")

if __name__ == "__main__":
    run_test_pipeline()
