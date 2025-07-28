import os
import fitz  # PyMuPDF
import json
import re
from datetime import datetime

def extract_outline_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    filename = os.path.basename(pdf_path)
    result = {
        "title": "",
        "outline": []
    }

    heading_patterns = {
        "H1": re.compile(r"^\d+\.\s"),
        "H2": re.compile(r"^\d+\.\d+\s"),
        "H3": re.compile(r"^\d+\.\d+\.\d+\s")
    }

    # Extract potential title
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                    if 10 < len(line_text) < 100:
                        result["title"] = line_text
                        break
                if result["title"]:
                    break
        if result["title"]:
            break

    # Extract headings
    for i, page in enumerate(doc):
        text = page.get_text()
        for line in text.split("\n"):
            stripped = line.strip()
            for level, pattern in heading_patterns.items():
                if pattern.match(stripped):
                    result["outline"].append({
                        "level": level,
                        "text": stripped,
                        "page": i
                    })
                    break

    return result

def process_all_pdfs(input_dir="/app/input", output_dir="/app/output"):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace(".pdf", ".json"))

            outline = extract_outline_from_pdf(input_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(outline, f, indent=4)

if __name__ == "__main__":
    # process_all_pdfs()
     process_all_pdfs(input_dir="input", output_dir="output")