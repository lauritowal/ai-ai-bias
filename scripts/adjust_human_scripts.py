import os
import json
from pathlib import Path

def get_title_from_json(json_file):
    try:
        with open(json_file) as f:
            data = json.load(f)
            if 'key_details' in data:
                return data['key_details'].get('title', '')
            return data.get('title', '')
    except FileNotFoundError:
        # File not found - it might have been renamed
        return None
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return None

def rename_human_file(human_file, new_name):
    if human_file == new_name:
        print(f"File already has correct name: {human_file}")
        return True
    try:
        human_file.rename(new_name)
        print(f"Successfully renamed:")
        print(f"From: {human_file}")
        print(f"To: {new_name}")
        return True
    except Exception as e:
        print(f"Error renaming {human_file}: {e}")
        return False

def main():
    # Define directories
    llm_dir = Path('/home/wombat_share/laurito/ai-ai-bias/data/proposal/llm/gpt41106preview')
    human_dir = Path('/home/wombat_share/laurito/ai-ai-bias/data/proposal/human')

    # Get all jsonify files from llm directory
    jsonify_files = [f for f in llm_dir.glob('*-jsonify_key_details_proposal.json')]
    print(f"Found {len(jsonify_files)} jsonify files")

    # Process each jsonify file
    for jsonify_file in jsonify_files:
        # Get title from jsonify file
        jsonify_title = get_title_from_json(jsonify_file)
        if not jsonify_title:
            print(f"Could not extract title from {jsonify_file}")
            continue

        # Get base name for new file
        new_base_name = jsonify_file.name.replace('-jsonify_key_details_proposal.json', '.json')

        # Get fresh list of human files for each iteration
        human_files = list(human_dir.glob('*.json'))
        
        # Search for matching human file
        match_found = False
        for human_file in human_files:
            human_title = get_title_from_json(human_file)
            if human_title == jsonify_title:
                match_found = True
                # Create new path for human file
                new_path = human_file.parent / new_base_name
                print("\nMatch found:")
                print(f"Title: {human_title}")
                print(f"Jsonify file: {jsonify_file}")
                print(f"Human file: {human_file}")
                rename_human_file(human_file, new_path)
                break
        
        if not match_found:
            print(f"\nNo match found for title: {jsonify_title}")

if __name__ == "__main__":
    main()