#!/usr/bin/env python3

import os
import gzip
import json
from collections import defaultdict
import pandas as pd

def main():
    root_dir = "/home/wombat_share/laurito/ai-ai-bias/context_cache"
    
    # Folders to exclude
    excluded_dirs = {} # "context_cache.bak", "context_cache.bak_"

    # This structure will hold counts for each (engine, item_type, prompt_key).
    # Each key maps to { "desc1": int, "desc2": int, "invalid": int }.
    counts = defaultdict(lambda: {"desc1": 0, "desc2": 0, "invalid": 0})
    
    for current_path, dirs, files in os.walk(root_dir):
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for filename in files:
            if not filename.endswith(".full.gz"):
                continue
            
            file_path = os.path.join(current_path, filename)
            
            # Load JSON
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as gz_file:
                    data = json.load(gz_file)
            except (OSError, json.JSONDecodeError):
                print(f"Invalid {file_path}")
                continue
            
            # Verify 'result' field is present and is a dict
            if "result" not in data:
                continue
            if not isinstance(data["result"], dict):
                print(f"Skipping {file_path}, 'result' is not a dict")
                continue
            if "uid" not in data["result"]:
                print(f"Skipping {file_path}, no 'uid' in data['result']")
                continue
            
            # Extract the "result" uid and the two description uids (if they exist)
            inputs = data.get("inputs", {})
            desc1 = inputs.get("description_1")
            desc2 = inputs.get("description_2")

            result_uid = data["result"]["uid"]
            desc1_uid = desc1["uid"] if desc1 else None
            desc2_uid = desc2["uid"] if desc2 else None
            
            # Gather engine, prompt_key, and item_type
            engine = inputs.get("llm_engine", "unknown_engine")
            
            prompt_config = inputs.get("comparison_prompt_config", {})
            prompt_key = prompt_config.get("prompt_key", "unknown_prompt")
            item_type = prompt_config.get("item_type", "unknown_item_type")
            
            # Ignore if item_type is "proposal"
            if item_type == "proposal":
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
    
    # Convert counts to a Pandas DataFrame
    rows = []
    for (engine, itype, pkey), tally in counts.items():
        desc1_chosen = tally["desc1"]
        desc2_chosen = tally["desc2"]
        invalid = tally["invalid"]
        total = desc1_chosen + desc2_chosen
        
        # Calculate bias ratio (desc1 / (desc1+desc2)) if any valid picks
        bias = None
        if total > 0:
            bias = desc1_chosen / total
        
        rows.append({
            "engine": engine,
            "item_type": itype,
            "prompt_key": pkey,
            "desc1_chosen": desc1_chosen,
            "desc2_chosen": desc2_chosen,
            "invalid": invalid,
            "bias": bias
        })
    
    df = pd.DataFrame(rows)
    
    # Write to CSV in the current directory
    output_csv = "first_order_bias.csv"
    df.to_csv(output_csv, index=False)
    
    print(f"Results written to {output_csv}")

if __name__ == "__main__":
    main()
