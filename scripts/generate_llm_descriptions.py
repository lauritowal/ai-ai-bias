import scripts_common_setup

import logging
import sys

from llm_descriptions_generator.schema import Engine
from llm_descriptions_generator.llm_descriptions import generate_llm_descriptions_for_item_type

ENGINE = Engine.gpt35turbo
# ENGINE = Engine.gpt4

cli_args = sys.argv[1:]
if len(cli_args) != 3:
    logging.warning("Please provide CLI args in the form of `python scripts/generate_llm_descriptions.py {item_type} {prompt_nickname} {description_count}`")
    exit(0)
item_type = cli_args[0]
prompt_nickname = cli_args[1]
description_count = int(cli_args[2])
llm_description_batch = generate_llm_descriptions_for_item_type(
    item_type=item_type,
    prompt_nickname=prompt_nickname,
    description_count=description_count,
    llm_engine=ENGINE,
)
logging.info("Generation done")