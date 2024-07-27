import pandas as pd
import json
import os

name = "3_jerry"
# Code to read one text file and transform it to a json file, just do a loop over ur own folder 
file_path = [f"../data/page_texts/{name}/page_{i}.txt" for i in range(31,46)]
for i in range(len(file_path)):
    with open(file_path[i], 'r', encoding='utf-8') as file:
        page_content = file.read()
    
        
    page_num = int(file_path[i].split("/")[-1].split(".")[0][-2:])
    page_dict = {f'page_{page_num}': {}}
    page_dict[f'page_{page_num}']['Text'] = page_content
    page_dict[f'page_{page_num}']['Page'] = int(file_path[i].split("/")[-1].split(".")[0][-2:])

    json_file_path = f'../data/cleaned_pages/{name}/page_{page_num}.json'
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    # Write the dictionary to a JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(page_dict, json_file, ensure_ascii=False, indent=4)