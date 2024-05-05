import json
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
    llm_version = data["model"]

    base_directory = Path('../../data') / category
    
    human_descriptions = load_json_files(base_directory / "human")
    llm_subfolder = "gpt41106preview" if llm_version == "gpt4" else ("gpt35turbo" if category == 'product' else "gpt35turbo1106")
    llm_directory = base_directory / "llm" / llm_subfolder
    llm_descriptions = load_json_files(llm_directory)

    # pair up the llm descriptions with the human descriptions which have the same title
    paired_descriptions = []
    for human_description in human_descriptions:
        title = human_description.get('title')
        llm_description = next((llm_description for llm_description in llm_descriptions if llm_description.get('title') == title), None)
        if llm_description:
            paired_descriptions.append({
                'human': human_description,
                'llm': llm_description
            })

    print("paired_descriptions", paired_descriptions)

    return jsonify(paired_descriptions)

if __name__ == '__main__':
    app.run(debug=True)