import os
import json
from collections import defaultdict

# Define the folder containing JSON files and the output folder
input_folder = "/Users/walt/ai-ai-bias/tmp_for_viz"
output_folder = "/Users/walt/ai-ai-bias/merged_run_outputs"
os.makedirs(output_folder, exist_ok=True)

# Function to extract the `run_end` timestamp from the file content
def extract_run_end(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data["metadata"]["run_end"]
    except (KeyError, json.JSONDecodeError):
        return None  # If missing or invalid, skip the file

# Function to merge JSON files by item type
def merge_json_files_by_item_type(input_folder, output_folder):
    merged_data = defaultdict(lambda: defaultdict(dict))  # Nested default dictionary for merging

    # Get the list of files and sort them by `run_end` timestamp
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".json")]
    sorted_files = sorted(files, key=lambda f: extract_run_end(f))

    # Loop through files in sorted order
    for file_path in sorted_files:
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
                item_type = data["metadata"]["item_type"]
                
                # Merge data by overwriting keys with the same name
                for key, value in data["results"].items():
                    merged_data[item_type][key] = value

            except (KeyError, json.JSONDecodeError) as e:
                print(f"Skipping {file_path}: {e}")

    # Write merged data to separate files by item type
    for item_type, results in merged_data.items():
        output_file = os.path.join(output_folder, f"{item_type}_merged.json")
        with open(output_file, "w") as outfile:
            json.dump({"item_type": item_type, "results": results}, outfile, indent=4)

# Run the merging process
merge_json_files_by_item_type(input_folder, output_folder)
