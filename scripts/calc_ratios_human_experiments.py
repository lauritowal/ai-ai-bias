import argparse
import json
from pathlib import Path


def extract_experiment_data(json_file, names):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            username = data.get("username")
            if username in names:
                model = data.get("model")
                category = data.get("category")
                total_llm_choices = data.get("totalLLMChoices", 0)
                total_human_choices = data.get("totalHumanChoices", 0)
                total_no_preference = data.get("totalNoPreference", 0)
                return model, category, total_llm_choices, total_human_choices, total_no_preference
    except Exception as e:
        print(f"Error reading file {json_file}: {e}")
    return None, None, 0, 0, 0  # Return zero if conditions are not met or error occurs

def calculate_preference_ratio(llm_choices, human_choices, no_preference):
    total_choices = llm_choices + human_choices + no_preference
    if total_choices == 0:  # To avoid division by zero in case of no data
        return 0
    ratio = llm_choices / total_choices
    return ratio

def extract_and_calculate_ratios(json_files, names):
    categories = ['product', 'paper']
    models = ['gpt3_5', 'gpt4']
    totals = {f"{cat}_{mod}_{suffix}": 0 for cat in categories for mod in models for suffix in ['llm', 'human', 'no_preference']}

    for json_file in json_files:
        model, category, llm_choices, human_choices, no_preference = extract_experiment_data(json_file, names)
        if model and category:
            totals[f"{category}_{model}_llm"] += llm_choices
            totals[f"{category}_{model}_human"] += human_choices
            totals[f"{category}_{model}_no_preference"] += no_preference

    ratios = {}
    for category in categories:
        for model in models:
            key = f"{category}_{model}"
            llm_choices = totals[f"{key}_llm"]
            human_choices = totals[f"{key}_human"]
            no_preference = totals[f"{key}_no_preference"]
            ratios[key] = calculate_preference_ratio(llm_choices, human_choices, no_preference)
            total_choices = llm_choices + human_choices + no_preference
            if total_choices == 0:  # To avoid division by zero
                ratios[key + "_no_preference"] = 0
            else:
                ratios[key + "_no_preference"] = no_preference / total_choices

    return ratios, totals

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate ratios for human experiments')
    parser.add_argument('path', type=str, help='Path to the results in form JSON files',
                        default="../human_preference_collector/backend/results", nargs='?')
    parser.add_argument('--names', type=str, nargs='+', default=['Autochthon', 'Verca', 'janpro'],
                        help='List of participant names to use for filtering (default: Autochthon, Verca, janpro)')
    args = parser.parse_args()

    # Use rglob to find all json files in the directory and its subdirectories
    json_files = list(Path(args.path).rglob('*.json'))
    # Exclude all category == demo
    print("JSON files found: ", len(json_files))
    json_files_no_demos = [f for f in json_files if 'demo' not in str(f)]
    print("JSON files found (excluding demos): ", len(json_files_no_demos))
    
    # Run the corrected script using the json_files list and the specified participant names
    ratios, totals = extract_and_calculate_ratios(json_files_no_demos, args.names)
    print("Ratios: ", ratios)
    print("Totals: ", totals)
