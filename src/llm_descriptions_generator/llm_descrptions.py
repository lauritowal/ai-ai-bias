import logging
import pprint

import dotenv

from llm_text_generator.config import get_text_item_generation_prompt_config
from llm_text_generator.file_io import (
    load_llm_description_batch_from_json_file,
    load_many_human_text_item_descriptions_from_toml_files,
    save_llm_description_batch_to_json_file,
    generate_filepath
)
from llm_text_generator.prompt_generation import create_text_item_generation_prompt_from_config
from llm_text_generator.query_llm import generate_llm_descriptions

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
dotenv.load_dotenv()


def get_llm_descriptions():
    # TODO: don't hardcode these? or at least make them CONSTANTS/config?
    # Probably arg parse is enough
    item_type = "products"
    prompt_nickname = "include_descriptions"
    n_ai_answers = 10

    generation_config = get_text_item_generation_prompt_config(
        item_type=item_type,
        prompt_nickname=prompt_nickname,
    )

    filepath = generate_filepath(
        title=generation_prompt.title, 
        item_type=generation_prompt.item_type, 
        prompt_uid=generation_prompt.prompt_uid,
    )

    if filepath.exists():
        logging.info(f"File already exists: {filepath}")
        pprint.pprint(f"File already exists: {filepath}. 
            Loading existing file instead of generating new one.")

        llm_description_batch = load_llm_description_batch_from_json_file(filepath)
    else:
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

            generation_prompt.item_type

            llm_description_batch = generate_llm_descriptions(
                generation_prompt=generation_prompt,
                description_count=n_ai_answers,
            )

            pprint.pprint(
                llm_description_batch,
                width=200,
            )

            save_llm_description_batch_to_json_file(
                llm_description_batch=llm_description_batch,
                filepath=filepath,
            )

    return llm_description_batch
