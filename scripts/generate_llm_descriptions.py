import scripts_common_setup

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

import click

from llm_descriptions_generator.schema import Engine
from llm_descriptions_generator.config import TEXT_GENERATION_PROMPT_CONFIG
from llm_descriptions_generator.llm_descriptions import generate_llm_descriptions_for_item_type

DEFAULT_ENGINE = Engine.gpt4turbo
MAX_CONCURRENT_WORKERS = 3

engine_choices = [e.value for e in Engine]


def batch_gen_descriptions(
    item_type: str,
    prompt_nickname: str,
    target_count: int,
    all_combos: bool,
    item_title_like: list[str],
    engine: str,
) -> None:
    if all_combos:
        item_prompts_to_generate: list[(str, str)] = []
        for item_type in TEXT_GENERATION_PROMPT_CONFIG:
            item_prompts_to_generate += [
                (item_type, prompt_config.prompt_nickname)
                for prompt_config in TEXT_GENERATION_PROMPT_CONFIG[item_type]
            ]
    else:
        item_prompts_to_generate: list[(str, str)] = [(item_type, prompt_nickname)]
    
    llm_engine = Engine(engine)
    logging.info(f"""
Running item description generator with the following options:
- LLM Engine: {llm_engine}
- Target Description Count: {target_count}
- Item Type & Prompts to iterate over: {item_prompts_to_generate}
"""
    )
    llm_description_batches = []

    def generate_descriptions(item, nickname):
        return generate_llm_descriptions_for_item_type(
            item_type=item,
            prompt_nickname=nickname,
            description_count=target_count,
            llm_engine=llm_engine,
            item_title_like=item_title_like if item_title_like else None,
        )

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_WORKERS) as executor:
        future_to_item = {executor.submit(generate_descriptions, item, nickname): (item, nickname) for item, nickname in item_prompts_to_generate}
        for future in as_completed(future_to_item):
            item, nickname = future_to_item[future]
            try:
                llm_description_batch = future.result()
            except Exception as exc:
                logging.error(f'{item, nickname} generated an exception: {exc}')
                raise exc
            else:
                llm_description_batches.append(llm_description_batch)

    logging.info("Generation done")
    return llm_description_batches

# CLI func
@click.command()
@click.option(
    "--item-type",
    type=str,
    default="",
    help="Item type to run generation script for. (Optional if --all flag is used.)",
)
@click.option(
    "--prompt-nickname",
    type=str,
    default="",
    help="Specific prompt nickname (pseudo ID) to run generation script for. (Optional if --all flag is used.)",
)
@click.option(
    "--target-count",
    type=int,
    default=6,
    help="Target number of descriptions variants to confirm exist already for a single prompt configuration and it, or create up to if not already present in data.",
)
@click.option(
    "--all-combos",
    type=bool,
    default=False,
    is_flag=True,
    help="CAUTION: Flag requesting batch generating descriptions for every prompt configuration in config.py.",
)
@click.option(
    "--item-title-like",
    multiple=True,
    default=[],
    help="(Multiple OK) Optional item title(s) (fragments ok) to limit generation script to.",
)
@click.option(
    "--engine",
    type=click.Choice(engine_choices, case_sensitive=False),
    default=DEFAULT_ENGINE,
    help="LLM model/engine to run description generation script with.",
)
def _cli_func(
    item_type: str,
    prompt_nickname: str,
    target_count: int,
    all_combos: bool,
    item_title_like: list[str],
    engine: str,
) -> None:
    if (
        (not item_type and not prompt_nickname and not all_combos)
        or ((item_type or prompt_nickname) and all_combos)
    ):
        logging.warning("Please provide CLI args indicating one or the other of (A) a specific --item-type and --prompt-nickname combination, or (B) the --all-combos flag.")
        exit(0)
    return batch_gen_descriptions(
        item_type=item_type,
        prompt_nickname=prompt_nickname,
        target_count=target_count,
        all_combos=all_combos,
        item_title_like=item_title_like,
        engine=engine,
    )


if __name__ == '__main__':
    _cli_func()