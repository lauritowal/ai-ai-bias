import os
import json

# Path to the folder containing the JSON files
folder_path = "/home/wombat_share/laurito/ai-ai-bias/full_run_outputs"

# Initialize accumulators for the totals
total_human = 0
total_llm = 0
total_invalid = 0

# Read and process each JSON file
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as file:
            data = json.load(file)

            if "metadata" not in data:
                print(f"Skipping {file_path}, 'metadata' is not present")
                continue

            # Check the conditions: item_type is "movie" and comparison_engine contains "gpt-3.5-turbo"
            if data["metadata"]["item_type"] == "movie":
                for permutation in data["metadata"]["engine_and_prompt_permutations"]:
                    if "gpt-3.5-turbo" in permutation["comparison_engine"]:
                        tallies = data["results"].get(
                            f'movie---DESCRIPTION-from_title_and_year|{permutation["description_engine"]}---COMPARISON-movie_pick_one|{permutation["comparison_engine"]}',
                            {}).get("total_tallies", {})
                        total_human += tallies.get("Human", 0)
                        total_llm += tallies.get("LLM", 0)
                        total_invalid += tallies.get("Invalid", 0)

# Output the total tallies
print({
    "Total Human": total_human,
    "Total LLM": total_llm,
    "Total Invalid": total_invalid
})

print("all", total_human + total_llm + total_invalid)
