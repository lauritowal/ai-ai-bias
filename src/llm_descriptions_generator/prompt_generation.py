import hashlib
import json
import logging

from llm_descriptions_generator.file_io import generate_descriptions_dirpath, generate_descriptions_filepath, load_description_batch_from_json_file
from llm_descriptions_generator.schema import (
    Origin,
    TextItemDescriptionBatch,
    TextItemGenerationPrompt,
    TextItemGenerationPromptConfig,
)


def create_text_item_generation_prompt_from_config(
    config: TextItemGenerationPromptConfig,
    source_description_batch: TextItemDescriptionBatch,
) -> TextItemGenerationPrompt:
    prompt_text = f"{config.prompt_base_text}"
    if config.match_human_original_length == True:
        if config.item_type == "paper":
            # Special handling: academic papers use original abstract for target count
            meta = getattr(source_description_batch, "meta", {})
            abstract = meta.get("abstract", None)
            target_word_count = len(abstract.split(" "))
            logging.info(f"Using original abstract for target word count: {target_word_count}")
            
        elif config.item_type == "proposal":
            # Read in human file with same title and use the length of the description
            title = source_description_batch.title
            filepath = generate_descriptions_filepath(
                title=title, 
                item_type=config.item_type,
                origin=Origin.Human
            )
            with open(filepath) as f: 
                data = json.load(f)
            
            abstract = data.get("abstract", None)
            target_word_count = len(abstract.split(" "))
        else:
            target_word_count = sum([len(d.split(" ")) for d in source_description_batch.descriptions]) / len(source_description_batch.descriptions)
        if target_word_count is None:
            raise Exception(f"Failed to assess target word count for config <{config.prompt_nickname}> and item <{source_description_batch.title}>")
        prompt_text += f"\n\nPlease limit the response to {target_word_count} words or less."

    prompt_text += "\n\n---"

    if not config.include_title and not config.include_descriptions:
        raise Exception(f"Invalid TextItemGenerationPromptConfig. Must include at least one of title or descriptions: {config}")

    if config.include_title:
        prompt_text += f"\n\n**Title:**\n\n{source_description_batch.title}"
    
    if config.item_type == "movie":
        year = getattr(source_description_batch, "year", None)
        prompt_text += f"\n\n**Year:**\n\n{year}"

    if config.include_descriptions:
        if not source_description_batch.descriptions:
            raise Exception(f"No descriptions found in source file for description generation prompt: {(config, source_description_batch)}")
        for description in source_description_batch.descriptions:
            prompt_text += f"\n\n**Description:**\n\n{description}"
            
    
    return TextItemGenerationPrompt(
        item_type=config.item_type,
        item_title=source_description_batch.title,
        prompt_text=prompt_text,
        prompt_uid=hashlib.md5(prompt_text.encode('utf-8')).hexdigest(),
        prompt_nickname=config.prompt_nickname,
    )
