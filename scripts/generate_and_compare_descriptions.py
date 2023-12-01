import scripts_common_setup

import click

from generate_llm_descriptions import batch_gen_descriptions
from run_comparisons import run_comparisons
from llm_descriptions_generator.schema import Engine

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
    batch_gen_descriptions(
        item_type=item_type,
        prompt_nickname=description_prompt_key,
        item_title_like=item_title_like,
        engine=description_engine,
        target_count=min_description_generation_count,
        all_combos=False,
    )

    run_comparisons(
        item_type=item_type,
        item_title_like=item_title_like,
        comparison_engine=comparison_engine,
        comparison_prompt_key=comparison_prompt_key,
        description_engine=description_engine,
        description_prompt_key=description_prompt_key,
    )

if __name__ == '__main__':
    generate_and_compare_descriptions()
