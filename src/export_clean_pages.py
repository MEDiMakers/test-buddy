import pandas as pd
import os
import json
import re

# Define the path to the directory

def combine_cleaned_json(
    directory_path = '../data/cleaned_pages'
):
    
    combined_jsons = []
    def process_json_file(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Add your processing logic here
            combined_jsons.append(data)

    def extract_number(file_name):
        match = re.search(r'(\d+)', file_name)
        return int(match.group(1)) if match else float('inf')

    for folder_name in sorted(os.listdir(directory_path)):
        folder_path = os.path.join(directory_path, folder_name)
        
        if os.path.isdir(folder_path):
            files = sorted(os.listdir(folder_path), key=extract_number)
            for file_name in files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    process_json_file(file_path)
    return combined_jsons

def export_combined_jsons(combined_jsons):
    with open("../data/all_pages_v1.json", "w", encoding='utf-8') as fout:
        json.dump(combined_jsons, fout, indent=3)
    return

def main():
    pdf_data = combine_cleaned_json()
    export_combined_jsons(pdf_data)
    
    
if __name__ == "__main__":
    main()