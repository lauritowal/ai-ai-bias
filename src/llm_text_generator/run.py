import logging
import pprint
import sys

import dotenv

from config import get_text_item_generation_prompt_config
from file_io import (
    load_many_human_text_item_descriptions_from_toml_files,
    save_llm_description_batch_to_json_file,
)
from prompt_generation import create_text_item_generation_prompt_from_config
from query_llm import generate_ai_descriptions

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
dotenv.load_dotenv()


def generate_ai_descriptions_for_item_type(
    item_type: str,
    prompt_nickname: str,
    description_count: int,
):
    generation_config = get_text_item_generation_prompt_config(
        item_type=item_type,
        prompt_nickname=prompt_nickname,
    )
    print(generation_config)
    human_text_item_descriptions = load_many_human_text_item_descriptions_from_toml_files(
        item_type=item_type,
        # item_filename="bag.toml",
    )

    for human_description_batch in human_text_item_descriptions:
        generation_prompt = create_text_item_generation_prompt_from_config(
            config=generation_config,
            human_description_batch=human_description_batch,
        )
        pprint.pprint(
            generation_prompt.__dict__,
            width=200,
        )

        llm_description_batch = generate_ai_descriptions(
            generation_prompt=generation_prompt,
            description_count=description_count,
        )

        pprint.pprint(
            llm_description_batch,
            width=200,
        )

        save_llm_description_batch_to_json_file(
            llm_description_batch=llm_description_batch,
        )

if __name__ == '__main__':
    cli_args = sys.argv[1:]
    if len(cli_args) != 3:
        print("Please provide CLI args in the form of `python run.py {item_type} {prompt_nickname} {description_count}`")
        exit(0)
    item_type = cli_args[0]
    prompt_nickname = cli_args[1]
    description_count = int(cli_args[2])
    generate_ai_descriptions_for_item_type(
        item_type=item_type,
        prompt_nickname=prompt_nickname,
        description_count=description_count,
    )