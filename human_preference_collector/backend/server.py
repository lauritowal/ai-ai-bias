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


@app.route('/descriptions', methods=['POST'])
def get_descriptions():
    data = request.json
    category = data["category"]
    model = data["model"]

    # Construct base directory path relative to the application
    base_directory = DATA_DIR / category

    # Load human descriptions
    human_descriptions = load_json_files(base_directory / "human")

    # Load the appropriate LLM subfolder based on the model
    llm_subfolder = "gpt41106preview" if model == "gpt4" else ("gpt35turbo" if category == 'product' else "gpt35turbo1106")
    llm_directory = base_directory / "llm" / llm_subfolder
    llm_descriptions = load_json_files(llm_directory)

    if category == 'product':
        # Separate LLM descriptions into 'listing' and 'detail'
        llm_descriptions_listings = [desc for desc in llm_descriptions if "listing" in desc["filename"]]
        llm_details_descriptions = [desc for desc in llm_descriptions if "details" in desc["filename"] and "jsonify" not in desc["filename"]]

        # Combine listings and details
        llm_descriptions = []
        for listing in llm_descriptions_listings:
            human_title = listing.get('title')
            matching_detail = next((detail for detail in llm_details_descriptions if detail.get('title') == human_title), None)

            llm_descriptions.append({
                'listing': listing,
                'detail': matching_detail if matching_detail else {}
            })

    # Pair the LLM and human descriptions based on titles
    paired_descriptions = []
    for human in human_descriptions:
        human_title = human.get('title').strip()

        if category == 'product':
            llm_pair = next((llm for llm in llm_descriptions if llm['listing'].get('title', '').strip() == human_title), None)

            # Only assert if both listing and detail titles are available
            if llm_pair and llm_pair['detail']:
                assert human_title == llm_pair['listing']['title'].strip() == llm_pair['detail']['title'].strip(), f"Titles do not match: {human_title}, {llm_pair['listing']['title']}, {llm_pair['detail']['title']}"
        elif category == 'paper':
            llm_pair = next((llm for llm in llm_descriptions if llm.get('title', '').strip() == human_title), None)
            # Removing specific keys that might not be needed in the response
            if "article" in human:
                del human["article"]
            if "abstract_xml" in human:
                del human["abstract_xml"]

            if llm_pair:
                assert human_title == llm_pair['title'].strip(), f"Titles do not match: {human_title}, {llm_pair['title']}"

        if llm_pair:
            paired_descriptions.append({
                'human': human,
                'llm': llm_pair
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
    data_folder = BASE_DIR / '../../data' / 'paper' / 'human'
    return jsonify([f.name for f in data_folder.iterdir() if f.is_file()])


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
