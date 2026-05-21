import os
from dotenv import load_dotenv

# Azure
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

# Local extractors
import fitz  # PyMuPDF
import pdfplumber

# =========================
# CONFIG
# =========================

PDF_PATH = "../ico-data/ic-409851-x6j7.pdf"
OUTPUT_DIR = "../comparison-output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# LOAD ENV
# =========================

load_dotenv()

endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# =========================
# AZURE CLIENT
# =========================

azure_client = None

if endpoint and key:
    azure_client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    print("✅ Azure client initialized")
else:
    print("⚠️ Azure credentials missing - skipping Azure extraction")

# =========================================================
# 1. AZURE DOCUMENT INTELLIGENCE (PARAGRAPH BASED)
# =========================================================

def extract_azure(pdf_path):
    print("\n🔵 Running Azure Document Intelligence...")

    with open(pdf_path, "rb") as f:
        poller = azure_client.begin_analyze_document(
            "prebuilt-layout",
            f
        )

        result = poller.result()

    paragraphs = []

    if result.paragraphs:
        for para in result.paragraphs:
            text = para.content.strip()

            if text:
                paragraphs.append(text)

    output = "\n\n".join(paragraphs)

    return output

# =========================================================
# 2. PYMUPDF
# =========================================================

def extract_pymupdf(pdf_path):
    print("\n🟢 Running PyMuPDF...")

    doc = fitz.open(pdf_path)

    pages = []

    for page_num, page in enumerate(doc, 1):

        text = page.get_text("text")

        pages.append(f"--- PAGE {page_num} ---\n{text}")

    return "\n\n".join(pages)

# =========================================================
# 3. PDFPLUMBER
# =========================================================

def extract_pdfplumber(pdf_path):
    print("\n🟣 Running pdfplumber...")

    pages = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, 1):

            text = page.extract_text()

            if text:
                pages.append(f"--- PAGE {page_num} ---\n{text}")

    return "\n\n".join(pages)

# =========================================================
# SAVE OUTPUT
# =========================================================

def save_output(name, content):

    path = os.path.join(OUTPUT_DIR, f"{name}.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"💾 Saved: {path}")
    print(f"   Characters: {len(content):,}")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print(f"\n📄 Testing extraction on:")
    print(PDF_PATH)

    # -----------------------------
    # Azure
    # -----------------------------
    if azure_client:
        try:
            azure_text = extract_azure(PDF_PATH)
            save_output("azure_paragraphs", azure_text)

        except Exception as e:
            print("❌ Azure extraction failed")
            print(e)

    # -----------------------------
    # PyMuPDF
    # -----------------------------
    try:
        pymupdf_text = extract_pymupdf(PDF_PATH)
        save_output("pymupdf", pymupdf_text)

    except Exception as e:
        print("❌ PyMuPDF extraction failed")
        print(e)

    # -----------------------------
    # pdfplumber
    # -----------------------------
    try:
        plumber_text = extract_pdfplumber(PDF_PATH)
        save_output("pdfplumber", plumber_text)

    except Exception as e:
        print("❌ pdfplumber extraction failed")
        print(e)

    print("\n🎉 Extraction comparison complete!")
