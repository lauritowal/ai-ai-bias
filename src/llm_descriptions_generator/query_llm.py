import logging

import langchain
from interlab.lang_models import  query_model

from llm_descriptions_generator.schema import (
    Engine,
    LlmGeneratedTextItemDescriptionBatch,
    TextItemGenerationPrompt,
    Origin,
)


def generate_llm_descriptions(
    generation_prompt: TextItemGenerationPrompt,
    description_count: int,
    llm_engine: Engine,
) -> LlmGeneratedTextItemDescriptionBatch:
    logging.info(
        "Querying LLM for new description for prompt uid: "
        + dict(
            item_title=generation_prompt.item_title,
            prompt_uid=generation_prompt.prompt_uid,
            llm_engine=llm_engine,
        ).__repr__()
    )
    
    descriptions: list[str] = []
    engine = langchain.chat_models.ChatOpenAI(model_name=llm_engine)

    for i in range(description_count):
        desc = query_model(engine, generation_prompt.prompt_text)
        descriptions.append(desc)

    llm_description_batch = LlmGeneratedTextItemDescriptionBatch(
        item_type=generation_prompt.item_type,
        title=generation_prompt.item_title,
        descriptions=descriptions,
        origin=Origin.LLM,
        llm_engine=llm_engine,
        generation_prompt_uid=generation_prompt.prompt_uid,
        generation_prompt_nickname=generation_prompt.prompt_nickname,
        generation_prompt_text=generation_prompt.prompt_text,
    )

    return llm_description_batch