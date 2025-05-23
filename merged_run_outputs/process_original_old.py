import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any
import pandas as pd

def process_json_files(input_paths: List[str]) -> Dict[str, Any]:
    # Initialize the main results dictionary
    results = defaultdict(lambda: {
        "details_by_item": defaultdict(lambda: {"Human": 0, "LLM": 0, "Invalid": 0}),
        "total_tallies": {"Human": 0, "LLM": 0, "Invalid": 0},
        "avg_llm_win_ratio": 0.0
    })
    
    for input_path in input_paths:
        with open(input_path, 'r') as f:
            data = json.load(f)
            
            # Extract key information
            model = data['model']
            category = data['category']
            
            for choice in data['userChoices']:
                # Get the generation prompt nickname from LLM description
                gen_prompt_nickname = choice['description']['llm']['generation_prompt_nickname']
                
                # Create the key for this comparison
                key = f"{category}---DESCRIPTION-{gen_prompt_nickname}|{model}---COMPARISON-pick_one|humans"
                
                # Get the item identifier (e.g., movie name)
                item_id = choice['description']['human']['filename']
                
                # Validate and normalize choice value
                choice_value = choice['choice'].capitalize()  # Convert to title case
                if choice_value not in ['Human', 'Llm', 'Invalid']:
                    print(f"Warning: Unexpected choice value '{choice_value}' in {input_path}, treating as Invalid")
                    choice_value = 'Invalid'
                
                # Convert 'Llm' to 'LLM' for consistency
                if choice_value == 'Llm':
                    choice_value = 'LLM'
                
                # Count the choice
                results[key]['details_by_item'][item_id][choice_value] += 1
                results[key]['total_tallies'][choice_value] += 1
    
    # Calculate LLM win ratios
    for key in results:
        for item_id in results[key]['details_by_item']:
            item_stats = results[key]['details_by_item'][item_id]
            total_valid = item_stats['Human'] + item_stats['LLM']
            item_stats['LLM_win_ratio'] = item_stats['LLM'] / total_valid if total_valid > 0 else 0
        
        # Calculate average LLM win ratio across all items
        details = results[key]['details_by_item']
        valid_ratios = [stats['LLM_win_ratio'] for stats in details.values()]
        results[key]['avg_llm_win_ratio'] = sum(valid_ratios) / len(valid_ratios) if valid_ratios else 0
    
    # Convert defaultdict to regular dict for JSON serialization
    return {k: dict(v) for k, v in results.items()}

def main():
    parser = argparse.ArgumentParser(description='Process human evaluation results')
    parser.add_argument('input_files', nargs='+', help='Input JSON files to process')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Process the files
    results = process_json_files(args.input_files)
    
    # Write the results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
