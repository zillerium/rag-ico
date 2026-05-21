import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

# =========================
# Load environment variables
# =========================
load_dotenv()
endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

if not endpoint or not key:
    raise ValueError("❌ Missing AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT or KEY in .env file")

if not endpoint.startswith("https://"):
    raise ValueError("❌ Endpoint should start with https://")

print(f"✅ Using endpoint: {endpoint}")

# =========================
# Azure Document Intelligence Client
# =========================
client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# =========================
# Directories
# =========================
INPUT_DIR = "../ico-data"      # Where your PDFs are
OUTPUT_DIR = "../ico-text"     # Where TXT files will be saved

# Create directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# Get all PDF files
# =========================
pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

print(f"📂 Found {len(pdf_files)} PDF file(s) in {INPUT_DIR}")

# =========================
# Process each PDF
# =========================
for pdf_file in pdf_files:
    pdf_path = os.path.join(INPUT_DIR, pdf_file)
    print(f"\n🔄 Processing: {pdf_file}")

    try:
        with open(pdf_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-layout",  # Good for structured documents like decision notices
                f
            )
            result = poller.result()

        print(f"   ✅ Processed {len(result.pages)} pages")

        # Extract text from all pages
        full_text = []
        for page_num, page in enumerate(result.pages, 1):
            page_lines = [
                line.content.strip()
                for line in (page.lines or [])
                if line.content and line.content.strip()
            ]
            if page_lines:
                full_text.append(f"--- Page {page_num} ---\n" + "\n".join(page_lines))

        # Combine all pages
        document_text = "\n\n".join(full_text)

        # Save as .txt
        txt_filename = os.path.splitext(pdf_file)[0] + ".txt"
        txt_path = os.path.join(OUTPUT_DIR, txt_filename)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(document_text)

        print(f"   💾 Saved: {txt_filename} ({len(document_text):,} characters)")

    except Exception as e:
        print(f"   ❌ Failed processing {pdf_file}")
        print(f"   Error: {e}")

print("\n🎉 All PDFs processed! Text files saved to ./ico-text/")
