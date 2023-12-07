import scripts_common_setup

import json
import random
from pathlib import Path

from llm_descriptions_generator.file_io import (
    load_all_academic_papers_as_description_batches,
    load_all_human_description_batches,
    load_all_llm_description_batches,
)

THIS_FILE_DIR = Path(__file__).parent.resolve()
RUN_OUTPUTS_DIR = THIS_FILE_DIR / "../full_run_outputs"


def pick_random_representative_selection(sorted_items: list, count: int = 10) -> list:
    if count > len(sorted_items):
        raise Exception("count must be <= item list size")
    chunk_size = len(sorted_items) // count
    random_selections = []
    start_index = None
    end_index = None
    for i in range(count):
        start_index = 0 if start_index is None else end_index
        end_index = start_index + chunk_size
        random_selections.append(
            random.choice(sorted_items[start_index:end_index])
        )
    return random_selections

run_output_json_filepaths = RUN_OUTPUTS_DIR.glob("*.json")
run_output_json_filepaths = [fp for fp in run_output_json_filepaths if "random_comparison_selections" not in fp.stem]

for run_output_json_filepath in run_output_json_filepaths:

    # filepath = RUN_OUTPUTS_DIR / RUN_DATA_JSON_FILE
    with open(run_output_json_filepath, "r") as f:
        run_data = json.load(f)

    run_name = run_output_json_filepath.stem

    output_filepath = RUN_OUTPUTS_DIR / f"{run_name}_random_comparison_selections.json"
    if output_filepath.is_file():
        # don't overwrite existing random selections
        continue

    metadata = run_data.get("metadata")
    item_type = metadata.get("item_type")
    
    run_permutations_comparison_selections = []

    for permutation_config in metadata.get("engine_and_prompt_permutations"):
        description_prompt_key = permutation_config.get('description_prompt_key')
        description_engine = permutation_config.get('description_engine')
        comparison_prompt_key = permutation_config.get('comparison_prompt_key')
        comparison_engine = permutation_config.get('comparison_engine')
        
        permutation_results = run_data.get("results").get(
            f"{item_type}"
            + f"---DESCRIPTION-{description_prompt_key}|{description_engine}"
            + f"---COMPARISON-{comparison_prompt_key}|{comparison_engine}"
        )

        details_by_item = permutation_results.get("details_by_item")

        # items titles by LLM win ratio
        # pick random titles distributed across list
        titles_and_ratios = [
            (title, tally.get("LLM_win_ratio"))
            for (title, tally) in details_by_item.items()
        ]
        titles_and_ratios.sort(key=lambda x: x[1])


        random_selections = pick_random_representative_selection(titles_and_ratios, 10)
        print(random_selections)
        
        # iterate through selections list
        desc_comparisons = []
        for (title, _) in random_selections:
            # get human description
            print(title)
            if item_type == "paper":
                human_description_batch = load_all_academic_papers_as_description_batches(
                    item_type=item_type,
                    fill_description_with="abstract",
                    item_title_like=[title],
                )[0]
            else:
                human_description_batch = load_all_human_description_batches(
                    item_type=item_type,
                    item_title_like=[title],
                )[0]
            
            #  - take first description in human list
            human_description = human_description_batch.descriptions[0]
            # print(human_description)
            # print(human_description_batch)

            # get LLM descriptions for item + DESCRIPTION prompt-key and engine
            llm_description_batch = load_all_llm_description_batches(
                item_type=item_type,
                title=title,
                llm_engine=description_engine,
                prompt_nickname=description_prompt_key,
            )[0]
            llm_description = random.choice(llm_description_batch.descriptions)
            #  - pick random description from LLM list
            # print(llm_description)

            desc_comparisons.append({
                "title": title,
                "Human": human_description,
                "LLM": llm_description,
            })
            # exit()
        run_permutations_comparison_selections.append({
            "config": permutation_config,
            "description_comparison_selections": desc_comparisons,
        })

        # output description pair for human comparison
    run_comparison_selections_output = {
        "item_type": item_type,
        "run_name": run_name,
        "run_permutations": run_permutations_comparison_selections,
    }
    # print(run_comparison_selections_output)
    # exit()

    with open(output_filepath, "w") as f:
        json.dump(run_comparison_selections_output, f, ensure_ascii=False, indent=4)