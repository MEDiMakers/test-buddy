import json
import os

def export_text():
    all_txts = os.listdir('../../data/combined_txts')

    all_sections = []

    for i in range(len(all_txts)):
        with open(f"../data/combined_txts/{all_txts[i]}", "r", encoding='utf-8') as fin:
            text = fin.read()
            sections = text.split("\n\n\n")
            all_sections.extend(sections)
            
    with open("../data/all_pdf_text.json", "w", encoding='utf-8') as fout:
        json.dump(all_sections, fout, ensure_ascii=False, indent=4)
