import os
import shutil
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

load_dotenv()

# ============================================
# AZURE CONFIG
# ============================================

endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

if not endpoint or not key:
    raise ValueError("❌ Missing credentials in .env file")

# Basic validation
if not endpoint.startswith("https://"):
    raise ValueError(
        "❌ Endpoint should start with https://"
    )

print(f"Using endpoint: {endpoint}")

# ============================================
# CLIENT
# ============================================

client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# ============================================
# DIRECTORIES
# ============================================

INPUT_DIR = "../jd-pdf"
OUTPUT_DIR = "../jd-text"
OLD_PDF_DIR = "../jd-old-pdf"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OLD_PDF_DIR, exist_ok=True)

# ============================================
# GET ALL PDF FILES
# ============================================

pdf_files = [
    f for f in os.listdir(INPUT_DIR)
    if f.lower().endswith(".pdf")
]

print(f"\n📂 Found {len(pdf_files)} PDF files")

# ============================================
# PROCESS PDF FILES
# ============================================

for index, filename in enumerate(pdf_files, 1):

    print("\n" + "=" * 70)
    print(f"📄 Processing PDF ({index}/{len(pdf_files)})")
    print(f"📄 File: {filename}")

    pdf_path = os.path.join(INPUT_DIR, filename)

    # ============================================
    # ANALYZE PDF
    # ============================================

    try:

        print("🔄 Analyzing PDF...")

        with open(pdf_path, "rb") as f:

            poller = client.begin_analyze_document(
                "prebuilt-layout",
                f
            )

            result = poller.result()

        print(
            f"✅ Successfully processed "
            f"{len(result.pages)} pages"
        )

    except Exception as e:

        print(f"❌ Failed processing PDF: {e}")
        continue

    # ============================================
    # EXTRACT TEXT
    # ============================================

    try:

        full_text = []

        for page_num, page in enumerate(result.pages, 1):

            page_content = [
                line.content.strip()
                for line in page.lines
                if line.content and line.content.strip()
            ]

            if page_content:

                full_text.append(
                    "\n".join(page_content)
                )

        # ============================================
        # OUTPUT TXT FILE
        # ============================================

        txt_filename = (
            os.path.splitext(filename)[0] + ".txt"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            txt_filename
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("\n\n".join(full_text))

        print(f"✅ Saved text file:")
        print(output_path)

    except Exception as e:

        print(f"❌ Failed extracting text: {e}")
        continue

    # ============================================
    # MOVE PDF TO OLD DIRECTORY
    # ============================================

    try:

        old_pdf_path = os.path.join(
            OLD_PDF_DIR,
            filename
        )

        shutil.move(pdf_path, old_pdf_path)

        print("📦 Moved processed PDF:")
        print(old_pdf_path)

    except Exception as e:

        print(f"❌ Failed moving PDF: {e}")

print("\n🎉 All PDF extraction complete")
