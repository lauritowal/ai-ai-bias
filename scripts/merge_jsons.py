import os
import json

# Define the folder containing JSON files and the output folder
input_folder = "full_run_outputs"
output_folder = "merged_run_outputs"
os.makedirs(output_folder, exist_ok=True)

# List of models to filter out
models_to_filter = [
    "Llama-3-70b-chat-hf",
    "Llama-3-8b-chat-hf",
    "Llama-3.3-70B",
    "Meta-Llama-3-8B",
    "Meta-Llama-3.1-8B",
    "Qwen2.5-7B",
    "groq-llama3-70b-8192",
    "groq-llama3-8b-8192",
    "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    "Qwen1.5"
]

# List of proposal/product experiment keywords to filter out
experiment_filters = [
    "proposal",
    "from_json_non_native",
    "from_json_old_person",
    "short_and_pointed",
    "from_json_avg_human",
    "old_person_confused_2",
    "submit_tomorrow_with_full_paper_details_matter"
]

# Function to extract the `run_end` timestamp from the file content
def extract_run_end(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data["metadata"]["run_end"]
    except (KeyError, json.JSONDecodeError):
        return None  # If missing or invalid, skip the file

# Function to filter keys in `results` based on model names or experiment keywords
def is_unwanted_key(key):
    # Check for unwanted models
    if any(model in key for model in models_to_filter):
        return True
    # Check for unwanted experiment types
    if any(experiment in key for experiment in experiment_filters):
        return True

    if "paper---DESCRIPTION-write_xml_paper_abstract_control_word_count|gpt-3.5-turbo---" in key:
        return True
    
    if "---COMPARISON-literature_review_pick_one|gpt-3.5-turbo" and not "---COMPARISON-literature_review_pick_one|gpt-3.5-turbo-1106":
        return True

    if "product_listing" in key:
        return True

    # Exclude comparisons involving 'gpt-3.5-turbo' unless it is 'gpt-3.5-turbo-1106'
    if "1106" not in key and "---COMPARISON-literature_review_pick_one|gpt-3.5-turbo" in key and "paper" in key:
        return True
    
    if "---COMPARISON-marketplace_recommendation_force_decision|gpt-3.5-turbo-1106":
        return True

    # Special case: exclude 'write_xml_paper_abstract' but keep 'write_xml_paper_abstract_control_word_count'
    if "write_xml_paper_abstract" in key and "control_word_count" not in key:
        return True

    return False

# Function to merge JSON files by filtering unwanted models and experiments
def merge_and_filter_json(input_folder, output_folder="./merged_run_outputs"):
    merged_data = {}

    # Get the list of files and sort them by `run_end` timestamp
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".json")]

    valid_files = []
    for file in files:
        run_end = extract_run_end(file)
        if run_end is not None:
            valid_files.append(file)

    sorted_files = sorted(valid_files, key=lambda f: extract_run_end(f))

    # Loop through files in sorted order
    for file_path in sorted_files:
        with open(file_path, "r") as file:
            try:
                data = json.load(file)

                # Filter results by excluding unwanted keys
                filtered_results = {
                    key: value
                    for key, value in data["results"].items()
                    if not is_unwanted_key(key)
                }

                # Merge filtered results
                for key, value in filtered_results.items():
                    merged_data[key] = value

                print(f"Processed {file_path}")

            except (KeyError, json.JSONDecodeError) as e:
                print(f"Skipping {file_path}: {e}")

    # Save the merged and filtered data
    output_file_path = os.path.join(output_folder, "merged.json")
    with open(output_file_path, "w") as file:
        json.dump(merged_data, file, indent=2)
        print(f"Merged and filtered data saved to {output_file_path}")

# Run the merging and filtering process
merge_and_filter_json(input_folder, output_folder)
