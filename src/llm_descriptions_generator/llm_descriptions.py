import logging

from llm_descriptions_generator.config import get_text_item_generation_prompt_config
from llm_descriptions_generator.file_io import (
    generate_descriptions_filepath,
    load_description_batch_from_json_file,
    load_many_human_text_item_descriptions_from_json_files,
    save_description_batch_to_json_file,
)
from llm_descriptions_generator.prompt_generation import create_text_item_generation_prompt_from_config
from llm_descriptions_generator.query_llm import generate_llm_descriptions
from llm_descriptions_generator.schema import Engine, LlmGeneratedTextItemDescriptionBatch, Origin

DEFAULT_ENGINE = Engine.gpt35turbo

def generate_llm_descriptions_for_item_type(
    item_type: str,
    prompt_nickname: str,
    description_count: int,
    llm_engine: Engine = DEFAULT_ENGINE,
) -> list[LlmGeneratedTextItemDescriptionBatch]:
    generation_config = get_text_item_generation_prompt_config(
        item_type=item_type,
        prompt_nickname=prompt_nickname,
    )

    human_text_item_descriptions = load_many_human_text_item_descriptions_from_json_files(
        item_type=item_type,
    )
    llm_description_batches: list[LlmGeneratedTextItemDescriptionBatch] = []

    for human_description_batch in human_text_item_descriptions:
        generation_prompt = create_text_item_generation_prompt_from_config(
            config=generation_config,
            human_description_batch=human_description_batch,
        )

        filepath = generate_descriptions_filepath(
            title=generation_prompt.item_title, 
            item_type=generation_prompt.item_type,
            origin=Origin.LLM,
            prompt_uid=generation_prompt.prompt_uid,
            llm_engine=llm_engine,
        )

        # queries to LLM take a while and often error out, so:
        # - save every item to local files as they are generated
        # - cache past generated descriptions to local files
        # - pick up where we left off, and skip generating new 
        #   files if the target count has already been generated

        for i in range(description_count):
            if not filepath.exists():
                logging.info(f"No existing data found at: {filepath}")
                existing_llm_description_batch = None
                existing_description_count = 0
            else:
                # logging.info(f"Loading existing data at: {filepath}")
                existing_llm_description_batch = load_description_batch_from_json_file(filepath)
                existing_description_count = len(existing_llm_description_batch.descriptions)
            
            logging.info(f"{filepath.name} -- Description count at: ({existing_description_count}/{description_count})")
            if existing_description_count >= description_count:
                logging.info(f"{filepath.name} -- Sufficient descriptions exist ({existing_description_count}/{description_count})")
                llm_description_batches.append(existing_llm_description_batch)
                break

            # if existing_description_count < description_count:
            # generate and save results one at a time in case of failures
            llm_description_batch = generate_llm_descriptions(
                generation_prompt=generation_prompt,
                description_count=1,
                llm_engine=llm_engine,
            )
            # merge existing descriptions with new
            if existing_llm_description_batch:
                llm_description_batch.descriptions += existing_llm_description_batch.descriptions
            save_description_batch_to_json_file(
                description_batch=llm_description_batch,
                filepath=filepath,
            )

    return llm_description_batches
