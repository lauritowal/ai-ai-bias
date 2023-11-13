import datetime

import langchain

from interlab.lang_models import  query_model

from llm_text_generator.schema import (
    LlmGeneratedTextItemDescriptionBatch,
    TextItemGenerationPrompt,
    Origin,
)

ENGINE = "gpt-3.5-turbo"
# ENGINE = "gpt-4"


def generate_llm_descriptions(
    generation_prompt: TextItemGenerationPrompt,
    description_count: int
) -> LlmGeneratedTextItemDescriptionBatch:
    print("Generating AI text blurbs")
    
    descriptions: list[str] = []

    engine = langchain.chat_models.ChatOpenAI(model_name=ENGINE)

    started_at = datetime.datetime.now().isoformat()

    for i in range(description_count):
        desc = query_model(engine, generation_prompt.prompt_text)
        descriptions.append(desc)

    completed_at = datetime.datetime.now().isoformat()

    llm_description_batch = LlmGeneratedTextItemDescriptionBatch(
        item_type=generation_prompt.item_type,
        title=generation_prompt.item_title,
        descriptions=descriptions,
        origin=Origin.Ai,
        generation_engine=ENGINE,
        generation_prompt_uid=generation_prompt.prompt_uid,
        generation_prompt_nickname=generation_prompt.prompt_nickname,
        generation_prompt_text=generation_prompt.prompt_text,
        generation_started_at=started_at,
        generation_completed_at=completed_at,
    )


    return llm_description_batch