import os
import re
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import pdfplumber
import fitz  # PyMuPDF

load_dotenv()

# ========================= CONFIG =========================
PDF_PATH = "../ico-data/ic-409851-x6j7.pdf"
OUTPUT_DIR = "./ico-clean"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========================= HELPERS =========================
def clean_headers(text):
    text = re.sub(r'Reference: IC-409851-X6J.*?Information Commissioner\'s Office', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # lone page numbers
    return text.strip()

def fix_numbered_structure(text):
    # Ensure numbered paragraphs stay together with their content
    text = re.sub(r'(\d+\.\s+[^\n]+)\n(?=\s*[a-zA-Z])', r'\1 ', text)          # join split sentences
    text = re.sub(r'(\d+\.\s)', r'\n\n\1', text)                               # force break before new numbers
    # Keep sub-lists (1., 2., etc.) attached to parent when possible
    text = re.sub(r'(\d+\.\s+[^\n]+?)\n\s*(1\.\s)', r'\1\n    \2', text)       # indent sub-lists
    return text

# ========================= MAIN EXTRACTION =========================
def extract_hybrid():
    print("🔄 Starting hybrid extraction...")

    # 1. Azure for paragraph awareness
    azure_text = ""
    try:
        client = DocumentIntelligenceClient(
            endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"))
        )
        with open(PDF_PATH, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-layout", f)
            result = poller.result()
        
        paragraphs = [p.content.strip() for p in result.paragraphs if p.content and p.content.strip()]
        azure_text = "\n\n".join(paragraphs)
        print(f"✅ Azure: {len(paragraphs)} paragraphs")
    except Exception as e:
        print("⚠️ Azure failed, falling back:", e)

    # 2. PyMuPDF for layout
    pymupdf_text = ""
    try:
        doc = fitz.open(PDF_PATH)
        pages = []
        for i, page in enumerate(doc, 1):
            text = page.get_text("text")
            pages.append(text)
        pymupdf_text = "\n\n".join(pages)
        print("✅ PyMuPDF layout extracted")
    except Exception as e:
        print("⚠️ PyMuPDF failed:", e)

    # Combine intelligently
    base = azure_text if azure_text else pymupdf_text
    cleaned = clean_headers(base)
    cleaned = fix_numbered_structure(cleaned)

    # Final save
    output_path = os.path.join(OUTPUT_DIR, "ic-409851-x6j7_clean.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"💾 Saved improved text → {output_path}")
    print(f"Length: {len(cleaned):,} characters")
    return cleaned

if __name__ == "__main__":
    extract_hybrid()
