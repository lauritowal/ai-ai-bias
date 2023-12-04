import hashlib

from llm_descriptions_generator.schema import (
    TextItemDescriptionBatch,
    TextItemGenerationPrompt,
    TextItemGenerationPromptConfig,
)



def create_text_item_generation_prompt_from_config(
    config: TextItemGenerationPromptConfig,
    source_description_batch: TextItemDescriptionBatch,
) -> TextItemGenerationPrompt:
    prompt_text = f"{config.prompt_base_text}\n\n---"

    if not config.include_title and not config.include_descriptions:
        raise Exception(f"Invalid TextItemGenerationPromptConfig. Must include at least one of title or descriptions: {config}")

    if config.include_title:
        prompt_text += f"\n\n**Title:**\n\n{source_description_batch.title}"
    
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


    