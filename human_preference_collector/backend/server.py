import datetime
import json
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# Define the base directory as the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
# Set the static folder relative to the base directory
FRONTEND_DIR = BASE_DIR / '../frontend/app/build'
DATA_DIR = BASE_DIR / '../../data'

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='/')
CORS(app)  # Enable CORS for all routes

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    return app.send_static_file('index.html')


def load_human_files(directory):
    """
    Load all JSON files in a given directory.
    :param directory: Pathlib Path object pointing to the directory
    :return: List of contents of all JSON files
    """
    descriptions = []
    for file_path in directory.glob('*.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['filename'] = file_path.stem
            descriptions.append(data)

    return descriptions

def load_llm_files(directory, category):
    """
    Load all JSON files in a given directory.
    :param directory: Pathlib Path object pointing to the directory
    :return: List of contents of all JSON files
    """
    descriptions = []
    for file_path in directory.glob('*.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['filename'] = file_path.stem
            if category == 'product' and '_details' in str(data['filename']) and not 'jsonify' in str(data['filename']):
                descriptions.append(data)
            elif category == 'paper':
                descriptions.append(data)
            elif category == 'demo':
                descriptions.append(data)
    return descriptions

def count_words(text):
    """Count words in the given text."""
    return len(text.strip().split()) if text else 0


def is_valid_description(description, min_words=10):
    """
    Determine if a description is valid based on word count.
    :param description: The text description to validate
    :param min_words: Minimum number of words required for validity
    :return: True if valid, False otherwise
    """
    return description and count_words(description) >= min_words


@app.route('/descriptions', methods=['POST'])
def get_descriptions():
    data = request.json
    category = data["category"]
    model = data["model"]

    # Construct base directory path relative to the application
    base_directory = DATA_DIR / category

    # Load human descriptions
    human_descriptions = load_human_files(base_directory / "human")

    # Load the appropriate LLM subfolder based on the model
    llm_subfolder = "gpt41106preview" if model == "gpt4" else ("gpt35turbo" if category == 'product' else "gpt35turbo1106")
    llm_directory = base_directory / "llm" / llm_subfolder
    llm_descriptions = load_llm_files(llm_directory, category)

    # Pair the LLM and human descriptions based on titles
    paired_descriptions = []
    for human_text in human_descriptions:
        human_title = human_text.get('title').strip()
        llm_text = next((llm for llm in llm_descriptions if llm.get('title', '').strip() == human_title), None)

        # Remove specific keys not needed
        if "article" in human_text:
            del human_text["article"]
        if "abstract_xml" in human_text:
            del human_text["abstract_xml"]

        # Check if the LLM description is valid
        if llm_text:
            assert human_title == llm_text['title'].strip(), f"Titles do not match: {human_title}, {llm_text['title']}"

            # Check both human and LLM descriptions for validity
            human_desc = human_text.get('abstract', '') or human_text.get('descriptions', [''])[0]
            if category == 'product':
                for i in range(len(human_text["descriptions"])):
                    human_text["descriptions"][i] = human_text["title"] + "\n\n" + human_text["descriptions"][i]

            llm_desc = llm_text.get('descriptions', [''])[0] or llm_text.get('detail', {}).get('descriptions', [''])[0]

            if is_valid_description(human_desc) and is_valid_description(llm_desc):
                paired_descriptions.append({
                    'human': human_text,
                    'llm': llm_text
                })

    return jsonify(paired_descriptions)


@app.route('/results', methods=['POST'])
def save_results():
    # Calculate timestamp via Python
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Replace with request data and construct paths correctly
    results_folder = BASE_DIR / 'results' / request.json.get('username') / request.json.get('model') / request.json.get('category')
    results_path = results_folder / f"experiment_{timestamp}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w', encoding='utf-8') as file:
        output = {
            'timestamp': timestamp,
            'username': request.json.get('username'),
            'email': request.json.get('email'),
            'model': request.json.get('model'),
            'category': request.json.get('category'),
            'totalLLMChoices': request.json.get("totalLLMChoices"),
            'totalHumanChoices': request.json.get("totalHumanChoices"),
            'totalNoPreference': request.json.get("totalNoPreference"),
            'userChoices': request.json.get("userChoices"),
        }
        json.dump(output, file, ensure_ascii=False, indent=4)

    return jsonify({'message': 'success'})


@app.route('/test', methods=['GET'])
def test():
    # Return a list of files in the data folder for "paper/human"
    data_folder = DATA_DIR / 'paper' / 'human'
    return jsonify([f.name for f in data_folder.iterdir() if f.is_file()])


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
