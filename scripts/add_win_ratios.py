import pandas as pd
import json

# Load JSON data
with open('/Users/walt/ai-ai-bias/merged_run_outputs/merged.json', 'r') as file:
    data = json.load(file)

# Load the CSV file
csv_file = '/Users/walt/ai-ai-bias/scripts/gptzero_results.csv'
df = pd.read_csv(csv_file)

# Debug: Print available JSON keys
print("Available JSON keys:")
for key in data.keys():
    print(key)


# Iterate through JSON keys and process all matching keys
for key in data:
    if "product---DESCRIPTION-from_json_details|gpt-4-1106-preview" in key and "COMPARISON-marketplace_recommendation_force_decision|" in key:
        # Extract the comparison model name (after the description model)
        comparison_model_name = key.split('|')[-1]
        
        # Extract details and LLM_win_ratios
        details_by_item = data[key].get("details_by_item", {})
        win_ratios = {
            item: metrics.get("LLM_win_ratio", 0)
            for item, metrics in details_by_item.items()
        }
        
        # Debug: Print the first few items from details_by_item
        print(f"\nDetails for {comparison_model_name}:")
        for item, metrics in list(details_by_item.items())[:10]:
            print(f"Title: {item}, Metrics: {metrics}")
        
        # Debug: Check unmatched titles
        unmatched_titles = set(df['title']) - set(details_by_item.keys())
        print(f"\nUnmatched titles for {comparison_model_name}:")
        print(unmatched_titles)

        # Add win_ratio column for the extracted comparison model
        column_name = f"LLM_win_ratio_{comparison_model_name}"
        df[column_name] = df['title'].map(win_ratios).fillna(0)
        
        # Debug: Inspect added column
        print(f"\nPreview of added column '{column_name}':")
        print(df[['title', column_name]].head(10))


win_ratio_columns = [col for col in df.columns if col.startswith("LLM_win_ratio_")]

# Debug: Print the identified win ratio columns
print(f"\nIdentified LLM_win_ratio columns for averaging: {win_ratio_columns}")

# Calculate the average of the win ratios across all LLM columns for each title
df["Average_LLM_win_ratio"] = df[win_ratio_columns].mean(axis=1)

# Debug: Preview the new column with averages
print("\nPreview of the DataFrame with Average_LLM_win_ratio:")
print(df[['title', 'Average_LLM_win_ratio']].head(10))

# Save the updated CSV
output_file = '/Users/walt/ai-ai-bias/data/gpt_zero_results_with_model_comparison_results.csv'
df.to_csv(output_file, index=False)
print(f"\nFiltered and updated CSV with all comparison models saved to {output_file}")
