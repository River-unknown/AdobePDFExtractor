import os
import json
import datetime
import fitz  # PyMuPDF
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_text_by_page(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        text = " ".join(
            span["text"]
            for block in blocks
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        )
        sections.append({
            "document": os.path.basename(pdf_path),
            "page": page_num + 1,
            "text": text.strip()
        })

    return sections

def rank_relevance(text, job_to_be_done):
    doc1 = nlp(job_to_be_done)
    doc2 = nlp(text)
    return doc1.similarity(doc2)

def run_1b(input_dir, output_path):
    # Load persona and job
    with open(os.path.join(input_dir, "persona_job.json"), "r", encoding="utf-8") as f:
        persona_info = json.load(f)

    persona = persona_info["persona"]
    job = persona_info["job_to_be_done"]

    all_text_blocks = []

    # Process all PDFs
    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            filepath = os.path.join(input_dir, file)
            blocks = extract_text_by_page(filepath)
            all_text_blocks.extend(blocks)

    # Score each page/block
    scored_blocks = [
        (block, rank_relevance(block["text"], job))
        for block in all_text_blocks
        if block["text"].strip()
    ]

    # Sort and select top 5
    top_blocks = sorted(scored_blocks, key=lambda x: x[1], reverse=True)[:5]

    # Generate output
    output_json = {
        "metadata": {
            "input_documents": list(set([block["document"] for block, _ in top_blocks])),
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        "extracted_sections": [],
        "sub_section_analysis": []
    }

    for idx, (block, score) in enumerate(top_blocks, 1):
        output_json["extracted_sections"].append({
            "document": block["document"],
            "page": block["page"],
            "section_title": f"AutoExtracted-Section-{idx}",
            "importance_rank": idx
        })

        output_json["sub_section_analysis"].append({
            "document": block["document"],
            "page": block["page"],
            "refined_text": block["text"]
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2)

    print(f"✅ Output written to {output_path}")

if __name__ == "__main__":
    input_dir = "input"
    output_path = "output/challenge1b_output.json"
    run_1b(input_dir, output_path)
