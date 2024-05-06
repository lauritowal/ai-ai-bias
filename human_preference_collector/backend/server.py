import datetime
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes

def load_json_file(file_path):
    """
    Load a single JSON file.
    :param file_path: Pathlib Path object pointing to the file
    :return: Contents of the JSON file
    """
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None  # Return None if file does not exist

def load_json_files(directory):
    """
    Load all JSON files in a given directory.
    :param directory: Pathlib Path object pointing to the directory
    :return: List of contents of all JSON files
    """
    descriptions = []
    for file_path in directory.glob('*.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['filename'] = file_path.stem  # Add filename (without extension) to the data
            descriptions.append(data)

    return descriptions


# TODO: Need to change this. We need to load the human descriptions first, then load the llms
# Then filter by title and create the pairs and append to a list
@app.route('/descriptions', methods=['POST'])
def get_descriptions():
    data = request.json

    category = data["category"]
    model = data["model"]

    base_directory = Path('../../data') / category
    
    human_descriptions = load_json_files(base_directory / "human")
    llm_subfolder = "gpt41106preview" if model == "gpt4" else ("gpt35turbo" if category == 'product' else "gpt35turbo1106")
    llm_directory = base_directory / "llm" / llm_subfolder
    llm_descriptions = load_json_files(llm_directory)

    # filter for llm_descriptions that have "details" in filname
    if category == "product":
        llm_descriptions_listings = []
        llm_details_descriptions = []
        for description in llm_descriptions:
            if "details" in description["filename"]:
                llm_details_descriptions.append(description)
            if "listing" in description["filename"]:
                llm_descriptions_listings.append(description)
        # pair up the llm_descriptions_listings with llm_details_descriptions where the title is the same

        llm_descriptions = []
        for llm_listing in llm_descriptions_listings:
            title = llm_listing.get('title')
            print("title", title)
            
            llm_detail = next((llm_detail for llm_detail in llm_details_descriptions if llm_detail.get('title') == title), None)

            if llm_detail:
                llm_descriptions.append({
                    'listing': llm_listing,
                    'detail': llm_detail
                })

    # pair up the llm descriptions with the human descriptions which have the same title
    paired_descriptions = []
    for human_description in human_descriptions:
        # remove full paper to make size smaller, if it exists
        if "article" in human_description:
            del human_description["article"]

        title = human_description.get('title')
        llm_description = next((llm_description for llm_description in llm_descriptions if llm_description["listing"].get('title') == title), None)
        if llm_description:
            paired_descriptions.append({
                'human': human_description,
                'llm': llm_description
            })
    
    return jsonify(paired_descriptions)

@app.route('/results', methods=['POST'])
def save_results():
    # calc timestamp via pyhton
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # replace  with request data
    results_folder = Path('./results')  / f"{request.json.get('username')}" / f"{request.json.get('model')}" / f"{request.json.get('category')}"
    results_path = results_folder / f"experiment_{timestamp}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w', encoding='utf-8') as file:
        output = {
            'timestamp': timestamp,
            'username': request.json.get('username'),
            'email': request.json.get('email'),
            'model': request.json.get('model'),
            'category': request.json.get('category'),
            'totalLLMChoices': request.json["totalLLMChoices"],
            'totalHumanChoices': request.json["totalHumanChoices"],
            'totalNoPreference': request.json["totalNoPreference"],
            'userChoices': request.json["userChoices"],
        }
        json.dump(output, file, ensure_ascii=False, indent=4) 

    return jsonify({'message': 'success'})

if __name__ == '__main__':
    app.run(debug=True)