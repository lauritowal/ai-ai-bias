import os
import json

# Define the folder containing JSON files and the output folder
input_folder = "full_run_outputs"
output_folder = "merged_run_outputs"
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
def merge_json_files_by_item_type(input_folder, output_folder="./merged_run_outputs"):
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
                
                # Merge data by overwriting keys with the same name
                for key, value in data["results"].items():
                    merged_data[key] = value
                print("adding", file_path)

            except (KeyError, json.JSONDecodeError) as e:
                print(f"Skipping {file_path}: {e}")

    with open(os.path.join(output_folder, "merged.json"), "w") as file:
        json.dump(merged_data, file, indent=2)
        print("Merged data saved to", os.path.join(output_folder, "merged.json"))
        

# Run the merging process
merge_json_files_by_item_type(input_folder, output_folder)
