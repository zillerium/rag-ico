import fitz
import json

doc = fitz.open("../ico-data/ic-409851-x6j7.pdf")

page = doc[6]  # page 7 (0-indexed)

data = page.get_text("dict")

with open("page7_layout.json", "w") as f:
    json.dump(data, f, indent=2)

print("saved page7_layout.json")
