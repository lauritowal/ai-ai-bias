import hashlib
from typing import Optional

from llm_text_generator.schema import (
    HumanTextItemDescriptionBatch,
    TextItemGenerationPrompt,
    TextItemGenerationPromptConfig,
)
from llm_text_generator.config import get_text_item_generation_prompt_config


def append_item_title(
    base_text: str,
    title: str,
) -> str:
    return base_text + f"\n\nTitle: {title}"

def append_item_title_and_descriptions(
    base_text: str,
    title: str,
    descriptions: Optional[list[str]],
) -> str:
    text = base_text
    if descriptions is None or len(descriptions) == 0:
        text += f"\n\n---"
        text += f"\n\nTitle: {title}"
        text += f"\n\nDescription: <No provided descriptions.>"
    else:
        for description in descriptions:
            text += f"\n\n---"
            text += f"\n\nTitle: {title}"
            text += f"\n\nDescription: {description}"
    return text

def create_text_item_generation_prompt_from_config(
    config: TextItemGenerationPromptConfig,
    human_description_batch: HumanTextItemDescriptionBatch,
) -> TextItemGenerationPrompt:
    prompt_text = config.prompt_base_text
    if not config.include_human_descriptions:
        prompt_text = append_item_title(
            base_text=config.prompt_base_text,
            title=human_description_batch.title,
        )
    elif config.include_human_descriptions == True:
        prompt_text = append_item_title_and_descriptions(
            base_text=config.prompt_base_text,
            title=human_description_batch.title,
            descriptions=human_description_batch.descriptions,
        )
    
    return TextItemGenerationPrompt(
        item_type=config.item_type,
        item_title=human_description_batch.title,
        prompt_text=prompt_text,
        prompt_uid=hashlib.md5(prompt_text.encode('utf-8')).hexdigest(),
        prompt_nickname=config.prompt_nickname,
    )


    