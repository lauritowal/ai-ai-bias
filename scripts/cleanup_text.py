import os
import json
import re

# Folder containing the JSON files
folder_path = "/Users/walt/ai-ai-bias/data/movie/human"

# Updated cleanup function
def cleanup_text(text):
    # Replace Unicode em dash with proper em dash
    text = text.replace("\u2014", "-")
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove spaces before punctuation
    text = re.sub(r'\s([,.;?!])', r'\1', text)
    # Trim leading/trailing whitespace
    text = text.strip()
    return text

# Process all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        
        # Load the JSON data
        with open(file_path, "r") as file:
            data = json.load(file)
        
        # Clean up descriptions if they exist
        if "descriptions" in data:
            cleaned_descriptions = [
                cleanup_text(description) for description in data["descriptions"]
            ]
            data["descriptions"] = cleaned_descriptions
        
        # Save the cleaned data back to the file with ensure_ascii=False
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

