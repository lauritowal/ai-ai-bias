#!/usr/bin/env python3

import os
import gzip
import json
from collections import defaultdict

def main():
    root_dir = "/Users/walt/ai-ai-bias/context_cache.bak"
    
    # This structure will hold counts for each (engine, item_type, prompt_key).
    # For each key, store { "desc1": int, "desc2": int, "invalid": int }.
    counts = defaultdict(lambda: {"desc1": 0, "desc2": 0, "invalid": 0})
    
    for current_path, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".root.gz"):
                continue
            
            file_path = os.path.join(current_path, filename)
            
            # Load JSON
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as gz_file:
                    data = json.load(gz_file)
            except (OSError, json.JSONDecodeError):
                # If unreadable JSON, just skip
                continue
            
            # Check for the necessary fields
            if (
                "result" not in data or
                "uid" not in data["result"] or
                "inputs" not in data or
                "description_1" not in data["inputs"] or
                "description_2" not in data["inputs"] or
                "uid" not in data["inputs"]["description_1"] or
                "uid" not in data["inputs"]["description_2"]
            ):
                # If missing fields, skip
                continue
            
            # Extract the "result" uid and the two description uids
            result_uid = data["result"]["uid"]
            desc1_uid = data["inputs"]["description_1"]["uid"]
            desc2_uid = data["inputs"]["description_2"]["uid"]
            
            # Gather engine, prompt_key, and item_type
            inputs = data["inputs"]
            engine = inputs.get("llm_engine", "unknown_engine")
            
            prompt_config = inputs.get("comparison_prompt_config", {})
            prompt_key = prompt_config.get("prompt_key", "unknown_prompt")
            item_type = prompt_config.get("item_type", "unknown_item_type")
            if item_type == "proposal":
                # ignroe
                continue
            
            # Create the dictionary key for counting
            key = (engine, item_type, prompt_key)
            
            # Tally based on which description was chosen
            if result_uid == desc1_uid:
                counts[key]["desc1"] += 1
            elif result_uid == desc2_uid:
                counts[key]["desc2"] += 1
            else:
                # If neither description matches, increment invalid
                counts[key]["invalid"] += 1
    
    # Print the results 
    # Each key is (engine, item_type, prompt_key)
    for (engine, itype, pkey), tally in counts.items():
        print(f"Engine: {engine},  Item Type: {itype},  Prompt: {pkey}")
        print(f"  Description 1 chosen: {tally['desc1']}")
        print(f"  Description 2 chosen: {tally['desc2']}")
        print(f"  Invalid (no match):   {tally['invalid']}")
        print("-" * 60)

if __name__ == "__main__":
    main()
