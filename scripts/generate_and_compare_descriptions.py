import scripts_common_setup

import json
import click
from datetime import datetime
from pathlib import Path

from interlab.context import Context
from interlab.ext.pyplot import capture_figure

from generate_llm_descriptions import batch_gen_descriptions
from llm_comparison.config import get_all_comparison_prompt_keys_for_item_type
from llm_comparison.presentation import (
    compute_llm_win_ratio,
    compute_avg_llm_win_ratio,
    make_chart,
    make_comparison_run_permutation_label,
)
from llm_descriptions_generator.config import get_all_description_prompt_keys_for_item_type
from llm_descriptions_generator.schema import Engine, Origin
from run_comparisons import run_comparisons
from storage import cache_friendly_file_storage
import llm_comparison.llm_comparison

FULL_RUN_OUTPUT_DIR = Path(__file__).parent.resolve() / "../full_run_outputs"

DEFAULT_COMPARISON_ENGINE = Engine.gpt4turbo.value
# DEFAULT_COMPARISON_ENGINE = Engine.gpt35turbo.value
DEFAULT_DESCRIPTION_ENGINE = Engine.gpt4turbo.value
# DEFAULT_DESCRIPTION_ENGINE = Engine.gpt35turbo.value

engine_choices = [e.value for e in Engine]

@click.command()
@click.option(
    "--item-type",
    type=str,
    default="",
    help="Item type to run comparison script for.",
)
@click.option(
    "--item-title-like",
    multiple=True,
    default=[],
    help="(Multiple OK) Optional item title(s) (fragments ok) to limit generation script to.",
)
@click.option(
    "--comparison-engine",
    type=click.Choice(engine_choices, case_sensitive=False),
    multiple=True,
    default=[DEFAULT_COMPARISON_ENGINE],
    help="LLM model/engine to run description comparison script with.",
)
@click.option(
    "--comparison-prompt-key",
    type=str,
    multiple=True,
    required=True,
    help="Specific comparison prompt key/nickname to run comparison script with.",
)
@click.option(
    "--description-engine",
    type=click.Choice(engine_choices, case_sensitive=False),
    multiple=True,
    default=[DEFAULT_DESCRIPTION_ENGINE],
    help="LLM model/engine to run description generation script with.",
)
@click.option(
    "--description-prompt-key",
    type=str,
    multiple=True,
    required=True,
    help="Specific description prompt key/nickname to run comparison script against.",
)
@click.option(
    "--min-description-generation-count",
    type=int,
    default=6,
    help="Target number of descriptions variants to confirm exist already for a single prompt configuration and it, or create up to if not already present in data.",
)
@click.option(
    "--max-comparison-concurrent-workers",
    type=int,
    default=None,
    help=f"Number of parallel workers to use for comparisons. The current default is {llm_comparison.llm_comparison.MAX_CONCURRENT_WORKERS}",
)
def generate_and_compare_descriptions(
    item_type: str,
    item_title_like: list[str],
    comparison_engine: str,
    comparison_prompt_key: str,
    description_engine: str,
    description_prompt_key: str,
    min_description_generation_count: int,
    max_comparison_concurrent_workers: int | None,
) -> None:
    if max_comparison_concurrent_workers is not None:
        llm_comparison.llm_comparison.MAX_CONCURRENT_WORKERS = max_comparison_concurrent_workers
    print(f"""
            item_type: {item_type}
            item_title_like: {item_title_like}
            comparison_engine: {comparison_engine}
            comparison_prompt_key: {comparison_prompt_key}
            description_engine: {description_engine}
            description_prompt_key: {description_prompt_key}
            min_description_generation_count: {min_description_generation_count}
            max_comparison_concurrent_workers: {llm_comparison.llm_comparison.MAX_CONCURRENT_WORKERS}
          """)
    run_start = datetime.now()

    run_permutations = [
        {
            "comparison_engine": ce,
            "comparison_prompt_key": cpk,
            "description_engine": de,
            "description_prompt_key": dpk,
        }
        for ce in comparison_engine
        for cpk in comparison_prompt_key
        for de in description_engine
        for dpk in description_prompt_key
    ]
    print(run_permutations)


    with Context(
        "root",
        inputs={
            "item_type": item_type,
            "item_title_like": item_title_like,
            "comparison_engine": comparison_engine,
            "comparison_prompt_key": comparison_prompt_key,
            "description_engine": description_engine,
            "description_prompt_key": description_prompt_key,
            "min_description_generation_count": min_description_generation_count,
        },
        storage=cache_friendly_file_storage,
    ) as root_ctx:
        results_data = {}
        charts = {}
        item_names = []

        for rp in run_permutations:
            batch_gen_descriptions(
                item_type=item_type,
                prompt_nickname=rp["description_prompt_key"],
                item_title_like=item_title_like,
                engine=rp["description_engine"],
                target_count=min_description_generation_count,
                all_combos=False,
            )

            (tallies_by_item_title, total_tally) = run_comparisons(
                item_type=item_type,
                item_title_like=item_title_like,
                comparison_engine=rp["comparison_engine"],
                comparison_prompt_key=rp["comparison_prompt_key"],
                description_engine=rp["description_engine"],
                description_prompt_key=rp["description_prompt_key"],
                description_count_limit=min_description_generation_count,
            )

            label = make_comparison_run_permutation_label(
                item_type=item_type,
                comparison_llm_engine=rp["comparison_engine"],
                comparison_prompt_key=rp["comparison_prompt_key"],
                description_llm_engine=rp["description_engine"],
                description_prompt_key=rp["description_prompt_key"],
            )
            details_by_item = {
                title: {
                    "LLM_win_ratio": compute_llm_win_ratio(tally),
                    "Human": tally.get(str(Origin.Human), 0),
                    "LLM": tally.get(str(Origin.LLM), 0), 
                    "Invalid": tally.get("Invalid", 0)
                }
                for (title, tally) in tallies_by_item_title.items()
            }
            total_tallies = total_tally
            avg_llm_win_ratio = compute_avg_llm_win_ratio(list(tallies_by_item_title.values()))
            results_data[label] = {
                "details_by_item": details_by_item,
                "total_tallies": total_tallies,
                "avg_llm_win_ratio": avg_llm_win_ratio,
            }
            charts[label] = capture_figure(make_chart(label, tallies_by_item_title))
            if not item_names:
                item_names = list(details_by_item.keys())

        run_end = datetime.now()
        
        final_run_data = {
            "metadata": {
                "run_start": run_start.isoformat(),
                "run_end": run_end.isoformat(),
                "item_type": item_type,
                "item_title_like": item_title_like,
                "items_covered": item_names,
                "min_description_generation_count": min_description_generation_count,
                "engine_and_prompt_permutations": run_permutations,
            },
            "results": results_data,
        }
        print(json.dumps(final_run_data, indent=4))

        final_run_data_with_charts = {
            **final_run_data,
            "charts": charts,
        }
        root_ctx.set_result(final_run_data_with_charts)

        # save data to json
        # save context w/ charts to html
        filepath = FULL_RUN_OUTPUT_DIR / run_end.strftime("%y%m%dT%H%M")
        filepath.parent.mkdir(exist_ok=True, parents=True) 
        
        with open(f"{filepath}.json", "w") as f:
            json.dump(final_run_data, f, ensure_ascii=False, indent=4)
        root_ctx.write_html(f"{filepath}.html")


if __name__ == '__main__':
    generate_and_compare_descriptions()
