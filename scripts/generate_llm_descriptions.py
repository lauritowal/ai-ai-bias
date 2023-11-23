import scripts_common_setup

import logging

import click

from llm_descriptions_generator.schema import Engine
from llm_descriptions_generator.config import TEXT_GENERATION_PROMPT_CONFIG
from llm_descriptions_generator.llm_descriptions import generate_llm_descriptions_for_item_type

# ENGINE = Engine.gpt35turbo
# ENGINE = Engine.gpt4
ENGINE = Engine.gpt4turbo

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
def batch_gen_descriptions(
    item_type: str,
    prompt_nickname: str,
    target_count: int,
    all_combos: bool,
) -> None:
    if (
        (not item_type and not prompt_nickname and not all_combos)
        or ((item_type or prompt_nickname) and all_combos)
    ):
        logging.warning("Please provide CLI args indicating one or the other of (A) a specific --item-type and --prompt-nickname combination, or (B) the --all-combos flag.")
        exit(0)
    if all_combos:
        item_prompts_to_generate: list[(str, str)] = []
        for item_type in TEXT_GENERATION_PROMPT_CONFIG:
            item_prompts_to_generate += [
                (item_type, prompt_config.prompt_nickname)
                for prompt_config in TEXT_GENERATION_PROMPT_CONFIG[item_type]
            ]
    else:
        item_prompts_to_generate: list[(str, str)] = [(item_type, prompt_nickname)]
    
    logging.info(f"""
Running item description generator with the following options:
- LLM Engine: {ENGINE}
- Target Description Count: {target_count}
- Item Type & Prompts to iterate over: {item_prompts_to_generate}
"""
    )
    for (item, nickname) in item_prompts_to_generate:
        llm_description_batch = generate_llm_descriptions_for_item_type(
            item_type=item,
            prompt_nickname=nickname,
            description_count=target_count,
            llm_engine=ENGINE,
        )
    logging.info("Generation done")

if __name__ == '__main__':
    batch_gen_descriptions()