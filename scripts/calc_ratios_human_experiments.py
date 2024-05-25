import argparse
import json
from pathlib import Path


def extract_experiment_data(json_file, model_name, category):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            if data["model"] == model_name and category in str(json_file):
                return data.get("totalLLMChoices", 0), data.get("totalHumanChoices", 0)
    except Exception as e:
        return 0, 0  # Return zero in case of an error or if the file cannot be read
    return 0, 0  # Return zero if conditions are not met

def calculate_preference_ratio(llm_choices, human_choices):
    total_choices = llm_choices + human_choices
    if total_choices == 0:  # To avoid division by zero in case of no data
        return 0
    ratio = llm_choices / total_choices
    return ratio

def extract_and_calculate_ratios(json_files):
    categories = ['product', 'paper']
    models = ['gpt3_5', 'gpt4']
    totals = {f"{cat}_{mod}_{suffix}": 0 for cat in categories for mod in models for suffix in ['llm', 'human']}

    for json_file in json_files:
        for model in models:
            for category in categories:
                llm_choices, human_choices = extract_experiment_data(json_file, model, category)
                totals[f"{category}_{model}_llm"] += llm_choices
                totals[f"{category}_{model}_human"] += human_choices

    ratios = {}
    for category in categories:
        for model in models:
            key = f"{category}_{model}"
            ratios[key] = calculate_preference_ratio(totals[f"{key}_llm"], totals[f"{key}_human"])
    return ratios

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate ratios for human experiments')
    parser.add_argument('path', type=str, help='Path to the results in form JSON files',
                        default="../human_preference_collector/backend/results", nargs='?')
    args = parser.parse_args()

    # Use rglob to find all json files in the directory and its subdirectories
    json_files = list(Path(args.path).rglob('*.json'))
    print("JSON files found: ", json_files)
    
    # Run the corrected script using the json_files list
    results = extract_and_calculate_ratios(json_files)
    print("Ratios: ", results)
