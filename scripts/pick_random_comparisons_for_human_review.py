import scripts_common_setup

import logging
import json
import random
from pathlib import Path

import click


from llm_comparison.llm_comparison import (
    find_cached_comparison_result,
    _make_descriptions_from_llm_description_batch,
    _make_descriptions_from_human_description_batch,

)
from llm_comparison.presentation import make_comparison_run_permutation_label
from llm_descriptions_generator.file_io import (
    load_all_academic_papers_as_description_batches,
    load_all_human_description_batches,
    load_all_llm_description_batches,
)
from llm_descriptions_generator.schema import (
    Engine,
    Origin,
)
from storage import cache_friendly_file_storage

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


@click.command()
@click.option(
    "--run-name-like",
    multiple=True,
    default=[],
    help="Name(s) of files to limit script to.",
)
def pick_random_comparisons_for_human_review(
    run_name_like: list[str] = []
) -> None:
    if run_name_like:
        run_output_json_filepaths = []
        for partial_filename in run_name_like:
            run_output_json_filepaths += RUN_OUTPUTS_DIR.glob(f"*{partial_filename}*.json")
    else:
        run_output_json_filepaths = RUN_OUTPUTS_DIR.glob("*.json")
        
    # filter out any globbed outputs of this script
    run_output_json_filepaths = [fp for fp in run_output_json_filepaths if "random_comparison_selections" not in fp.stem]

    for run_output_json_filepath in run_output_json_filepaths:

        cached_result_not_found_ct = 0
        cached_result_expected_ct = 0

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
                make_comparison_run_permutation_label(
                    item_type=item_type,
                    description_prompt_key=description_prompt_key,
                    description_llm_engine=description_engine,
                    comparison_prompt_key=comparison_prompt_key,
                    comparison_llm_engine=comparison_engine,
                )
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
            
            # iterate through selections list
            desc_comparisons = []
            for (title, _) in random_selections:
                # get human description
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
                # human_description = human_description_batch.descriptions[0]
                human_description = _make_descriptions_from_human_description_batch(
                    human_description_batch=human_description_batch,
                )[0]


                # get LLM descriptions for item + DESCRIPTION prompt-key and engine
                llm_description_batch = load_all_llm_description_batches(
                    item_type=item_type,
                    title=title,
                    llm_engine=description_engine,
                    prompt_nickname=description_prompt_key,
                )[0]
                #  - pick random description from LLM list
                # llm_description = random.choice(llm_description_batch.descriptions)
                llm_description = random.choice(
                    _make_descriptions_from_llm_description_batch(
                        llm_description_batch=llm_description_batch,
                    )
                )
                
                # check for comparisons in both directions
                logging.info(f"## Searching comparison cache... [{title}]")
                cached_comparison_result_1 = find_cached_comparison_result(
                    llm_engine=Engine(comparison_engine),
                    description_uid_1=human_description.uid,
                    description_uid_2=llm_description.uid,
                    comparison_prompt_key=comparison_prompt_key,
                    storage=cache_friendly_file_storage,
                )
                cached_comparison_result_2 = find_cached_comparison_result(
                    llm_engine=Engine(comparison_engine),
                    description_uid_1=llm_description.uid,
                    description_uid_2=human_description.uid,
                    comparison_prompt_key=comparison_prompt_key,
                    storage=cache_friendly_file_storage,
                )
                llm_comparison_tally = {
                    str(Origin.Human): 0,
                    str(Origin.LLM): 0,
                    "Invalid": 0,
                }
                if not cached_comparison_result_1 and not cached_comparison_result_2:
                    # probably not in cache at all, so skip this item
                    logging.info(f"## ...comparison result cache not found [{title}]")
                    cached_result_not_found_ct += 1
                    continue
                winner_1 = str(cached_comparison_result_1.origin) if cached_comparison_result_1 else "Invalid"
                winner_2 = str(cached_comparison_result_2.origin) if cached_comparison_result_2 else "Invalid"
                llm_comparison_tally[winner_1] += 1
                llm_comparison_tally[winner_2] += 1

                # output description pair for human comparison
                desc_comparisons.append({
                    "title": title,
                    "human_description": human_description.text,
                    "llm_description": llm_description.text,
                    "llm_comparison_tally": llm_comparison_tally,
                })
                
            run_permutations_comparison_selections.append({
                "config": permutation_config,
                "description_comparison_selections": desc_comparisons,
            })
            cached_result_expected_ct += len(random_selections)
        
        run_comparison_selections_output = {
            "item_type": item_type,
            "run_name": run_name,
            "run_permutations": run_permutations_comparison_selections,
        }

        if cached_result_not_found_ct > 0:
            logging.warning(f"## Missing cached results for '{run_name}' - ({cached_result_not_found_ct}/{cached_result_expected_ct}) missing/expected")
            continue

        with open(output_filepath, "w") as f:
            json.dump(run_comparison_selections_output, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    pick_random_comparisons_for_human_review()