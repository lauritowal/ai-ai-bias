import scripts_common_setup

import click

from llm_descriptions_generator.schema import Engine
from llm_comparison.llm_comparison import compare_saved_description_batches
from llm_comparison.config import get_comparison_prompt_config
from storage import cache_friendly_file_storage

DEFAULT_COMPARISON_ENGINE = Engine.gpt4turbo.value
# DEFAULT_COMPARISON_ENGINE = Engine.gpt35turbo
DEFAULT_DESCRIPTION_ENGINE = Engine.gpt4turbo.value
# DEFAULT_DESCRIPTION_ENGINE = Engine.gpt35turbo

engine_choices = [e.value for e in Engine]


def run_comparisons(
    item_type: str,
    item_title_like: list[str],
    comparison_engine: str,
    comparison_prompt_key: str,
    description_engine: str,
    description_prompt_key: str,
):
    comparison_prompt_config = get_comparison_prompt_config(
        item_type=item_type,
        prompt_key=comparison_prompt_key,
    )
    comparison_llm_engine = Engine(comparison_engine)
    description_llm_engine = Engine(description_engine)

    return compare_saved_description_batches(
        comparison_llm_engine=comparison_llm_engine,
        comparison_prompt_config=comparison_prompt_config,
        item_type=item_type,
        item_title_like=list(item_title_like) if item_title_like else None,
        description_llm_engine=description_llm_engine,
        description_prompt_key=description_prompt_key,
        storage=cache_friendly_file_storage,
    )


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
    help="(Multiple OK) Optional item title(s) (fragments ok) to limit comparison script to.",
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
def _cli_func(
    item_type: str,
    item_title_like: list[str],
    comparison_engine: str,
    comparison_prompt_key: str,
    description_engine: str,
    description_prompt_key: str,
) -> None:
    return run_comparisons(
        item_type=item_type,
        item_title_like=item_title_like,
        comparison_engine=comparison_engine,
        comparison_prompt_key=comparison_prompt_key,
        description_engine=description_engine,
        description_prompt_key=description_prompt_key,
    )
    

if __name__ == '__main__':
    _cli_func()
