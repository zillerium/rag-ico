import fitz
import json

PDF_PATH = "../ico-data/ic-409851-x6j7.pdf"

doc = fitz.open(PDF_PATH)

# Page 7 (0-indexed = page 6)
page = doc[6]

data = page.get_text("dict")

# ----------------------------------------
# Remove image/binary blocks
# ----------------------------------------

clean_blocks = []

for block in data["blocks"]:

    # Keep only text blocks
    if block.get("type") != 0:
        continue

    clean_block = {
        "bbox": block.get("bbox"),
        "lines": []
    }

    for line in block.get("lines", []):

        clean_line = {
            "bbox": line.get("bbox"),
            "spans": []
        }

        for span in line.get("spans", []):

            clean_span = {
                "text": span.get("text"),
                "bbox": span.get("bbox"),
                "size": span.get("size"),
                "font": span.get("font")
            }

            clean_line["spans"].append(clean_span)

        clean_block["lines"].append(clean_line)

    clean_blocks.append(clean_block)

# ----------------------------------------
# Save cleaned layout JSON
# ----------------------------------------

output = {
    "page_number": 7,
    "blocks": clean_blocks
}

with open("page7_layout.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("✅ Saved page7_layout.json")

# ----------------------------------------
# Print simplified structure
# ----------------------------------------

print("\n===== STRUCTURE =====\n")

for i, block in enumerate(clean_blocks):

    print(f"\nBLOCK {i}")
    print(f"BBOX: {block['bbox']}")

    for line in block["lines"]:

        line_text = " ".join(
            span["text"]
            for span in line["spans"]
        )

        print(line_text)
