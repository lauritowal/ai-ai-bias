import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any
import pandas as pd
import os

def process_json_files(input_paths: List[str]) -> Dict[str, Any]:
    # Initialize the main results dictionary
    results = defaultdict(lambda: {
        "details_by_item": defaultdict(lambda: {"Human": 0, "LLM": 0, "Invalid": 0}),
        "total_tallies": {"Human": 0, "LLM": 0, "Invalid": 0},
        "llm_win_ratio": 0.0
    })
    
    # Create a mapping for paper prompts that should be merged
    paper_prompts = ["write_xml_paper_abstract", "write_xml_paper_abstract_control_word_count"]
    
    for input_path in input_paths:
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
                
                # Extract key information
                model = data.get('model', 'unknown')
                category = data.get('category', 'unknown')
                
                for choice in data.get('userChoices', []):
                    try:
                        # Get the generation prompt nickname from LLM description, with fallback
                        llm_desc = choice.get('description', {}).get('llm', {})
                        gen_prompt_nickname = llm_desc.get('generation_prompt_nickname', 
                                                         llm_desc.get('prompt_nickname', 'unknown'))
                        
                        # For papers, merge both prompt types into one
                        if category == 'paper' and gen_prompt_nickname in paper_prompts:
                            gen_prompt_nickname = "write_xml_paper_abstract_combined"
                        
                        # Create the key for this comparison
                        key = f"{category}---DESCRIPTION-{gen_prompt_nickname}|{model}---COMPARISON-pick_one|humans"
                        
                        # Get the item identifier (e.g., movie name)
                        item_id = choice.get('description', {}).get('human', {}).get('filename', 'unknown')
                        
                        # Validate and normalize choice value
                        choice_value = str(choice.get('choice', 'Invalid')).capitalize()  # Handle None values
                        choice_value = 'Invalid' if choice_value == 'None' else choice_value
                        if choice_value not in ['Human', 'Llm', 'Invalid']:
                            print(f"Warning: Unexpected choice value '{choice_value}' in {input_path}, treating as Invalid")
                            choice_value = 'Invalid'
                        
                        # Convert 'Llm' to 'LLM' for consistency
                        if choice_value == 'Llm':
                            choice_value = 'LLM'
                        
                        # Count the choice
                        results[key]['details_by_item'][item_id][choice_value] += 1
                        results[key]['total_tallies'][choice_value] += 1
                    except Exception as e:
                        print(f"Warning: Error processing choice in {input_path}: {e}")
                        continue
        except Exception as e:
            print(f"Warning: Error processing file {input_path}: {e}")
            continue
    
    # Calculate LLM win ratio for each item (keeping this for reference)
    for key in results:
        for item_id in results[key]['details_by_item']:
            item_stats = results[key]['details_by_item'][item_id]
            total_valid = item_stats['Human'] + item_stats['LLM']
            item_stats['LLM_win_ratio'] = item_stats['LLM'] / total_valid if total_valid > 0 else 0
        
        # Calculate overall LLM win ratio (total LLM wins / total valid comparisons)
        total_valid = results[key]['total_tallies']['Human'] + results[key]['total_tallies']['LLM']
        results[key]['llm_win_ratio'] = results[key]['total_tallies']['LLM'] / total_valid if total_valid > 0 else 0
    
    # Convert defaultdict to regular dict for JSON serialization
    return {k: dict(v) for k, v in results.items()}

def leave_one_out_analysis(input_paths: List[str], output_path: str) -> Dict[str, Any]:
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Now process once for each file left out
    for input_path in input_paths:
        # Skip empty paths
        if not input_path or input_path.isspace():
            print(f"Skipping empty or whitespace-only path")
            continue
            
        # Remove the current file from the list
        reduced_input_paths = [p for p in input_paths if p != input_path]
        results = process_json_files(reduced_input_paths)
        
        try:
            # Get username from the JSON file
            with open(input_path, 'r') as f:
                data = json.load(f)
                user_name = data.get('username', 'unknown')
            
            path = f"{output_path}_without_{user_name}.json"
            print(f"Writing to {path}")

            with open(path, 'w') as f:
                json.dump(results, f, indent=2)
        except FileNotFoundError:
            print(f"Warning: File not found: {input_path}")
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in file: {input_path}")
        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Process human evaluation results')
    parser.add_argument('input_files', nargs='+', help='Input JSON files to process')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file path')
    parser.add_argument('--leave_one_out', default=False, action='store_true', help='Perform leave-one-out analysis')
    
    args = parser.parse_args()

    if args.leave_one_out:
        results = leave_one_out_analysis(args.input_files, args.output)
    else:
        results = process_json_files(args.input_files)
        # Write the results
        with open(args.output + ".json", 'w') as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
