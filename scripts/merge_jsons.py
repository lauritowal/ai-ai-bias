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

def is_unwanted_key(key):
    # Check for unwanted models from the filter list
    if any(model in key for model in models_to_filter):
        return True

    # Check for unwanted experiment types
    if any(experiment in key for experiment in experiment_filters):
        return True

    # if "product_listing" in key:
    #     return True

    if "product" in key and "gpt-3.5-turbo-1106" in key:
        return True

    if "movie" in key and "gpt-3.5-turbo-1106" in key:
        return True

    # For keys related to papers, if any segment uses a gpt-3.5-turbo model,
    # ensure it is exactly "gpt-3.5-turbo-1106". Other models are allowed.
    if "paper" in key:
        segments = key.split('---')
        for segment in segments:
            if '|' in segment:
                # Extract the model (assumed to be after the last pipe symbol)
                model = segment.split('|')[-1].strip()
                # If the model starts with "gpt-3.5-turbo" but isn't the approved variant,
                # mark the key as unwanted.
                if model.startswith("gpt-3.5-turbo") and model != "gpt-3.5-turbo-1106":
                    return True

    # Special case: exclude keys with 'write_xml_paper_abstract' unless they include 'control_word_count'
    if "write_xml_paper_abstract" in key and "control_word_count" not in key:
        return True

    return False

def get_invalid_count(result_value):
    """
    Extracts the number of invalids from a result value.
    We assume the result value is a dict with a key "num_invalids" holding the count.
    If not available, we return a high number (infinity) so that such results are
    less likely to overwrite valid ones.
    """
    try:
        return result_value.get("num_invalids", float("inf"))
    except AttributeError:
        # If result_value is not a dict, assume it's invalid
        return float("inf")

def merge_and_filter_json(input_folder, output_folder="./merged_run_outputs"):
    merged_data = {}

    # List all JSON files in the input folder.
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".json")]

    # Process each file
    for file_path in files:
        with open(file_path, "r") as file:
            try:
                data = json.load(file)

                # Filter out unwanted keys from the results.
                filtered_results = {
                    key: value
                    for key, value in data["results"].items()
                    if not is_unwanted_key(key)
                }

                # Merge the filtered results.
                # For duplicate keys, retain the result with the lower number of invalids.
                for key, value in filtered_results.items():
                    new_invalids = get_invalid_count(value)
                    if key in merged_data:
                        current_invalids = get_invalid_count(merged_data[key])
                        if new_invalids < current_invalids:
                            merged_data[key] = value
                    else:
                        merged_data[key] = value

                print(f"Processed {file_path}")

            except (KeyError, json.JSONDecodeError) as e:
                print(f"Skipping {file_path}: {e}")

    print("Merged data:", merged_data)
    # Save the merged and filtered data.
    output_file_path = os.path.join(output_folder, "merged_llms.json")
    with open(output_file_path, "w") as file:
        json.dump(merged_data, file, indent=2)
        print(f"Merged and filtered data saved to {output_file_path}")

# Run the merging and filtering process
merge_and_filter_json(input_folder, output_folder)
