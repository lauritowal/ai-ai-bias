import scripts_common_setup

import click

from interlab.context import Context
from interlab.ext.pyplot import capture_figure

from generate_llm_descriptions import batch_gen_descriptions
from llm_comparison.llm_comparison import DescriptionBattleTally
from llm_comparison.presentation import (
    compute_avg_llm_win_ratio,
    make_chart,
    make_full_comparison_label,
)
from llm_descriptions_generator.schema import Engine
from run_comparisons import run_comparisons
from storage import cache_friendly_file_storage

DEFAULT_COMPARISON_ENGINE = Engine.gpt4turbo.value
# DEFAULT_COMPARISON_ENGINE = Engine.gpt35turbo
DEFAULT_DESCRIPTION_ENGINE = Engine.gpt4turbo.value
# DEFAULT_DESCRIPTION_ENGINE = Engine.gpt35turbo

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
    default=DEFAULT_COMPARISON_ENGINE,
    help="LLM model/engine to run description comparison script with.",
)
@click.option(
    "--comparison-prompt-key",
    type=str,
    default="",
    help="Specific comparison prompt key/nickname to run comparison script with.",
)
@click.option(
    "--description-engine",
    type=click.Choice(engine_choices, case_sensitive=False),
    default=DEFAULT_DESCRIPTION_ENGINE,
    help="LLM model/engine to run description generation script with.",
)
@click.option(
    "--description-prompt-key",
    type=str,
    default="",
    help="Specific description prompt key/nickname to run comparison script against.",
)
@click.option(
    "--min-description-generation-count",
    type=int,
    default=6,
    help="Target number of descriptions variants to confirm exist already for a single prompt configuration and it, or create up to if not already present in data.",
)
def generate_and_compare_descriptions(
    item_type: str,
    item_title_like: list[str],
    comparison_engine: str,
    comparison_prompt_key: str,
    description_engine: str,
    description_prompt_key: str,
    min_description_generation_count: int,
) -> None:
    # TODO: enable script for multiple prompt keys (or even item types?)

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
        batch_gen_descriptions(
            item_type=item_type,
            prompt_nickname=description_prompt_key,
            item_title_like=item_title_like,
            engine=description_engine,
            target_count=min_description_generation_count,
            all_combos=False,
        )

        (tallies_by_item_title, total_tally) = run_comparisons(
            item_type=item_type,
            item_title_like=item_title_like,
            comparison_engine=comparison_engine,
            comparison_prompt_key=comparison_prompt_key,
            description_engine=description_engine,
            description_prompt_key=description_prompt_key,
        )

        label = make_full_comparison_label(
            item_type=item_type,
            comparison_llm_engine=comparison_engine,
            comparison_prompt_key=comparison_prompt_key,
            description_llm_engine=description_engine,
            description_prompt_key=description_prompt_key,
        )

        # TODO: modify script to handle multiple prompt+engine configurations in one go
        # (so the dictionaries below would contain more than one)
        root_ctx.set_result({
            "avg_llm_win_ratio": {
                label: compute_avg_llm_win_ratio(list(tallies_by_item_title.values())),
            },
            "charts": {
                label: capture_figure(make_chart(label, tallies_by_item_title)),
            }
        })


if __name__ == '__main__':
    generate_and_compare_descriptions()
