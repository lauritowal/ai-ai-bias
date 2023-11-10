import logging
import pprint

import dotenv

from llm_text_generator.config import get_text_item_generation_prompt_config
from llm_text_generator.file_io import (
    load_many_human_text_item_descriptions_from_toml_files,
    save_llm_description_batch_to_json_file,
)
from llm_text_generator.prompt_generation import create_text_item_generation_prompt_from_config
from llm_text_generator.query_llm import generate_ai_descriptions

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
dotenv.load_dotenv()


N_AI_ANSWERS = 10


def __main__():
    # TODO: don't hardcode these? or at least make them CONSTANTS/config?
    item_type = "products"
    prompt_nickname = "include_descriptions"
    
    generation_config = get_text_item_generation_prompt_config(
        item_type=item_type,
        prompt_nickname=prompt_nickname,
    )
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
            description_count=N_AI_ANSWERS,
        )

        pprint.pprint(
            llm_description_batch,
            width=200,
        )

        save_llm_description_batch_to_json_file(
            llm_description_batch=llm_description_batch,
        )

