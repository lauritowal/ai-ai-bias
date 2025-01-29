import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load JSON data
file_path = "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/merged.json"  # Change this to your actual file  path
with open(file_path, "r") as file:
    data = json.load(file)

# Dictionary to store results by item type
results_by_item_type = {}

# Iterate over datasets in the JSON
for dataset_name, dataset_details in data.items():
    details_by_item = dataset_details.get("details_by_item", {})

    # Extract item type from the dataset name
    item_type = dataset_name.split("---")[0] if "---" in dataset_name else "Unknown"

    # Ensure a structure for this item type
    if item_type not in results_by_item_type:
        results_by_item_type[item_type] = {}

    # Process each item under details_by_item
    for item_name, item_data in details_by_item.items():
        if item_name not in results_by_item_type[item_type]:
            results_by_item_type[item_type][item_name] = {
                "Total_Human": 0,
                "Total_LLM": 0,
                "Total_Invalid": 0
            }

        # Aggregate counts
        results_by_item_type[item_type][item_name]["Total_Human"] += item_data.get("Human", 0)
        results_by_item_type[item_type][item_name]["Total_LLM"] += item_data.get("LLM", 0)
        results_by_item_type[item_type][item_name]["Total_Invalid"] += item_data.get("Invalid", 0)

# Convert to DataFrame
df_results_by_item_type = []

for item_type, items in results_by_item_type.items():
    for item_name, counts in items.items():
        df_results_by_item_type.append([
            item_type, item_name, counts["Total_Human"], counts["Total_LLM"], counts["Total_Invalid"]
        ])

df_results_by_item_type = pd.DataFrame(df_results_by_item_type, columns=["Item Type", "Item Name", "Total Human", "Total LLM", "Total Invalid"])

# Calculate LLM Preference Ratio
df_results_by_item_type["LLM_Preference_Ratio"] = df_results_by_item_type["Total LLM"] / (
    df_results_by_item_type["Total LLM"] + df_results_by_item_type["Total Human"]
)

# Calculate variability statistics for each item type
df_item_variability = df_results_by_item_type.groupby("Item Type")
