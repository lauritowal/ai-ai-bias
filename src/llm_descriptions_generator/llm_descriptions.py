import logging
import typing as t

import openai
import tiktoken
from interlab.context import Context, FileStorage

from llm_descriptions_generator.config import \
    get_text_item_generation_prompt_config
from llm_descriptions_generator.file_io import (
    generate_descriptions_filepath,
    load_all_academic_papers_as_description_batches,
    load_all_human_description_batches, load_all_llm_json_summary_batches,
    load_description_batch_from_json_file, save_description_batch_to_json_file)
from llm_descriptions_generator.prompt_generation import \
    create_text_item_generation_prompt_from_config
from llm_descriptions_generator.query_llm import generate_llm_descriptions
from llm_descriptions_generator.schema import (
    Engine, LlmGeneratedTextItemDescriptionBatch, Origin,
    PromptDescriptionSource, TextItemDescriptionBatch)
from storage import cache_friendly_file_storage

DEFAULT_ENGINE = Engine.gpt35turbo
DEFAULT_STORAGE = cache_friendly_file_storage

def generate_llm_descriptions_for_item_type(
    item_type: str,
    prompt_nickname: str,
    description_count: int,
    llm_engine: Engine = DEFAULT_ENGINE,
    item_title_like: t.Optional[list[str]] = None,
) -> list[LlmGeneratedTextItemDescriptionBatch]:
    with Context(
        name="generate_descriptions",
        storage=DEFAULT_STORAGE,
        inputs={
            "item_type": item_type,
            "prompt_nickname": prompt_nickname,
            "description_count": description_count,
            "llm_engine": llm_engine,
            "item_title_like": item_title_like,
        },
        tags=[
            f"engine:{llm_engine}",
            f"item_type:{item_type}",
        ],
        directory=True,
    ) as ctx:
        # ctx = current_context()
        generation_config = get_text_item_generation_prompt_config(
            item_type=item_type,
            prompt_nickname=prompt_nickname,
        )

        source_description_batches: list[TextItemDescriptionBatch] = []

        if generation_config.description_source == PromptDescriptionSource.Human:
            source_description_batches = load_all_human_description_batches(
                item_type=item_type,
                item_title_like=item_title_like,
            )
        elif generation_config.description_source == PromptDescriptionSource.LLM_JSON_Summary:
            source_description_batches = load_all_llm_json_summary_batches(
                item_type=item_type,
                item_title_like=item_title_like,
            )
        elif generation_config.description_source == PromptDescriptionSource.AcademicPaperBody:
            source_description_batches = load_all_academic_papers_as_description_batches(
                item_type=item_type,
                fill_description_with="body",
                item_title_like=item_title_like,
            )
        
        llm_description_batches: list[LlmGeneratedTextItemDescriptionBatch] = []

        for source_description_batch in source_description_batches:
            generation_prompt = create_text_item_generation_prompt_from_config(
                config=generation_config,
                source_description_batch=source_description_batch,
            )

            filepath = generate_descriptions_filepath(
                title=generation_prompt.item_title, 
                item_type=generation_prompt.item_type,
                origin=Origin.LLM,
                # prompt_uid=generation_prompt.prompt_uid,
                prompt_key=generation_prompt.prompt_nickname,
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
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-1106")
                tokens = encoding.encode(generation_prompt.prompt_text)
                if llm_engine == Engine.gpt35turbo1106 and len(tokens) >= 16385:
                    print(f"Skip. prompt {generation_prompt.prompt_nickname} is too long for gpt35turbo1106")
                else:
                    llm_description_batch = generate_llm_descriptions(
                        generation_prompt=generation_prompt,
                        description_count=1,
                        llm_engine=llm_engine,
                        output_description_type=generation_config.output_description_type,
                    )
                    # merge existing descriptions with new
                    if existing_llm_description_batch:
                        llm_description_batch.descriptions += existing_llm_description_batch.descriptions
                    save_description_batch_to_json_file(
                        description_batch=llm_description_batch,
                        filepath=
                        filepath,
                    )

        ctx.set_result(llm_description_batches)
        return llm_description_batches
