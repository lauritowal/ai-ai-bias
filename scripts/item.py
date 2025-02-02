import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



def to_safe_filename(
    title_text: str,
) -> str:
    # Remove the file extension before cleaning
    base_name = os.path.splitext(title_text)[0]
    cleaned_title = re.sub(r'[^A-Za-z0-9 _]+', "", base_name).replace(" ", "_").lower()
    cleaned_shortened_title = cleaned_title[:32]
    filename = cleaned_shortened_title

    return filename

# Paths to the input files
merged_json_path = "/home/wombat_share/laurito/ai-ai-bias/merged_run_outputs/merged.json"
human_results = "/home/wombat_share/laurito/ai-ai-bias/human_preference_collector/backend/results"

# # Load merged.json
with open(merged_json_path, "r", encoding="utf-8") as file:
    merged_data = json.load(file)


def get_llm_ratio_gpt4(item_type, description_model, item_title):
    """
    Retrieves the LLM_win_ratio for a given item type, description model, and item title,
    **but only considers the comparison model gpt-4-1106-preview**.
    """
    formatted_title = item_title.strip().lower().replace(" ", "_").replace("'", "").replace(":", "").replace(",", "")

    llm_ratios = []  # Store matching LLM_win_ratios

    # Iterate through merged_data keys
    for key, value in merged_data.items():
        parts = key.split("---")
        if len(parts) >= 3:
            json_item_type = parts[0]
            descriptor_info = parts[1].split("|")
            comparison_info = parts[2].split("|")

            if len(descriptor_info) >= 2:
                json_description_model = descriptor_info[1]  # Extract description model

            if len(comparison_info) >= 2:
                json_comparison_model = comparison_info[1]  # Extract comparison model
            else:
                json_comparison_model = "Unknown"

            # Check if item type, description model, and comparison model match
            if (
                json_item_type == item_type
                and json_description_model == description_model
                and json_comparison_model == "gpt-4-1106-preview"
            ):
                # Check if the item title exists in details_by_item
                if "details_by_item" in value and formatted_title in value["details_by_item"]:
                    llm_ratio = value["details_by_item"][formatted_title].get("LLM_win_ratio", None)
                    if llm_ratio is not None:
                        llm_ratios.append(llm_ratio)

    # Return the average LLM_win_ratio if any valid ones exist
    return sum(llm_ratios) / len(llm_ratios) if llm_ratios else None

def get_llm_ratio(item_type, description_model, item_title):
    """
    Retrieves the average LLM_win_ratio for a given item type, description model, and item title,
    averaging over all available comparison models.
    
    It prints the comparison models and their respective LLM_win_ratio values.
    """
    formatted_title = item_title.strip().lower().replace(" ", "_").replace("'", "").replace(":", "").replace(",", "")

    llm_ratios = []
    comparison_models = []  # Store comparison models for debugging

    # Iterate through merged_data keys
    for key, value in merged_data.items():
        parts = key.split("---")
        if len(parts) >= 3:
            json_item_type = parts[0]
            descriptor_info = parts[1].split("|")
            comparison_info = parts[2].split("|")

            if len(descriptor_info) >= 2:
                json_description_model = descriptor_info[1]  # Extract description model

                if len(comparison_info) >= 2:
                    json_comparison_model = comparison_info[1]  # Extract comparison model
                else:
                    json_comparison_model = "Unknown"

                # Check if item type and description model match
                if json_item_type == item_type and json_description_model == description_model:
                    
                    # Check if the item title exists in details_by_item
                    if "details_by_item" in value and formatted_title in value["details_by_item"]:
                        llm_ratio = value["details_by_item"][formatted_title].get("LLM_win_ratio", None)
                        if llm_ratio is not None:
                            llm_ratios.append(llm_ratio)
                            comparison_models.append(json_comparison_model)  # Track comparison models

    # Print the comparison models and their LLM_win_ratio values
    if llm_ratios:
        # print(f"\nItem Type: {item_type}, Description Model: {description_model}, Title: {item_title}")
        # print("-" * 60)
        # for model, ratio in zip(comparison_models, llm_ratios):
        #     print(f"   Comparison Model: {model:20} | LLM_win_ratio: {ratio:.4f}")
        average_ratio = sum(llm_ratios) / len(llm_ratios)
        # print(f"   --> Averaged LLM_win_ratio: {average_ratio:.4f}\n")

        return average_ratio

    return None

def extract_all_user_choices_corrected(base_path):
    user_choices_data = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as json_file:
                        data = json.load(json_file)

                        # Extract model and username
                        model = data.get("model", "Unknown")
                        username = data.get("username", "Unknown")

                        # Extract userChoices if present
                        if "userChoices" in data and isinstance(data["userChoices"], list):
                            for choice_entry in data["userChoices"]:
                                item_title = choice_entry.get("description", {}).get("human", {}).get("title") or \
                                             choice_entry.get("description", {}).get("llm", {}).get("title")

                                item_type = choice_entry.get("description", {}).get("human", {}).get("item_type", "Unknown")

                                # Assign values: 0 for human choice, 1 for LLM choice
                                human_choice = 0 if choice_entry.get("choice") == "human" else 1 if choice_entry.get("choice") == "llm" else None

                                if item_type == "paper":
                                    if model == "gpt3_5":
                                        model = "gpt-3.5-turbo-1106"
                                    elif model == "gpt4":
                                        model = "gpt-4-1106-preview"
                                else:
                                    if model == "gpt3_5":
                                        model = "gpt-3.5-turbo"
                                    elif model == "gpt4":
                                        model = "gpt-4-1106-preview"


                                # Append corrected data
                                user_choices_data.append({
                                    "File Name": file,
                                    "Item Type": item_type,
                                    "Item Title": to_safe_filename(item_title),
                                    "Description Model": model,
                                    "Human Prefers LLM (ratio)": human_choice,
                                    "User": username
                                })

                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

    return pd.DataFrame(user_choices_data)

# Extract user choices
df_human_user_choices = extract_all_user_choices_corrected(human_results)

# Compute the average Human Choice per Item Type, Item Title, and Description Model
df_human_avg_per_item = df_human_user_choices.groupby(["Item Type", "Item Title", "Description Model"], as_index=False)["Human Prefers LLM (ratio)"].mean()

# add llm ratio for each "Item Type", "Item Title", "Description Model"
for index, row in df_human_avg_per_item.iterrows():
    item_type = row["Item Type"]
    item_title = row["Item Title"]
    model = row["Description Model"]
    llm_ratio = get_llm_ratio_gpt4(item_type, model, item_title)
    df_human_avg_per_item.loc[index, "LLM Prefers LLM (ratio)"] = llm_ratio

    if row["Human Prefers LLM (ratio)"] is None or llm_ratio is None:
        print(f"Skipping {item_type} - {item_title} - {model}, because of missing data")
        continue

    df_human_avg_per_item.loc[index, "Human Prefers LLM - LLM Prefers LLM"] = row["Human Prefers LLM (ratio)"] - llm_ratio


# Save the final processed table as CSV
df_human_avg_per_item.to_csv("final_human_results.csv", index=False)

### **Visualization Functions**
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

def generate_and_save_visualizations(df, output_dir):
    """Generates and saves visualizations for Human vs. LLM Preferences."""
    df_valid = df.dropna(subset=["Human Prefers LLM - LLM Prefers LLM"])

    # 1. Overall Histogram
    plt.figure(figsize=(12, 6))
    sns.histplot(df_valid["Human Prefers LLM - LLM Prefers LLM"], bins=30, kde=True)
    plt.axvline(x=0, color='r', linestyle='--', label="Equal Preference (0.0)")
    plt.title("Overall Distribution of Human Prefers LLM - LLM Prefers LLM Difference")
    plt.xlabel("Human Prefers LLM - LLM Prefers LLM Difference")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/overall_histogram.png")
    plt.close()

    # 2. Boxplot by Item Type
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_valid, x="Item Type", y="Human Prefers LLM - LLM Prefers LLM")
    plt.axhline(y=0, color='r', linestyle='--', label="Equal Preference (0.0)")
    plt.title("Boxplot of Human Prefers LLM - LLM Prefers LLM Difference by Item Type")
    plt.xlabel("Item Type")
    plt.ylabel("Difference in Preference")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/boxplot_by_item_type.png")
    plt.close()

    # 3. Histograms for each Item Type
    unique_item_types = df_valid["Item Type"].unique()
    for item_type in unique_item_types:
        subset = df_valid[df_valid["Item Type"] == item_type]
        plt.figure(figsize=(12, 6))
        sns.histplot(subset["Human Prefers LLM - LLM Prefers LLM"], bins=30, kde=True)
        plt.axvline(x=0, color='r', linestyle='--', label="Equal Preference (0.0)")
        plt.title(f"Distribution of Human Prefers LLM - LLM Prefers LLM Difference ({item_type})")
        plt.xlabel("Human Prefers LLM - LLM Prefers LLM Difference")
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{output_dir}/histogram_{item_type}.png")
        plt.close()


# Generate visualizations
generate_and_save_visualizations(df_human_avg_per_item, output_dir)
print(f"Visualizations saved to {output_dir}")

