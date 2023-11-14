import logging
import time

import langchain
from interlab.lang_models import query_model
from interlab.queries import QueryFailure
from interlab.queries.experimental.repeat import repeat_on_failure
from openai.error import (
    APIError,
    Timeout,
    APIConnectionError,
    RateLimitError,
)

from llm_descriptions_generator.schema import (
    Engine,
    LlmGeneratedTextItemDescriptionBatch,
    TextItemGenerationPrompt,
    Origin,
)

MAX_SUPER_RETRY_COUNT = 10
SUPER_RETRY_WAIT_INTERVAL_SECONDS = 60


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
        def query_llm_for_new_description():
            # TODO: make retry logic more flexible and/or better integrated with interlab/langchain tooling
            try:
                return query_model(engine, generation_prompt.prompt_text)
            except (APIError, Timeout, APIConnectionError) as e:
                retry_interval = SUPER_RETRY_WAIT_INTERVAL_SECONDS
                logging.warning(e)
                logging.warning(f"Retryable error from LLM's API encountered. Will try again after {retry_interval} seconds.")
                time.sleep(retry_interval)
                raise QueryFailure # triggers interlab repeat_on_failure behavior
            except RateLimitError as e:
                logging.error(e)
                logging.error("Open AI Rate limit and/or quota exceeded. Shutting down until you wait a while and/or buy new credits.")
                exit()
            except Exception as e:
                raise e

        desc = repeat_on_failure(
            fn=query_llm_for_new_description,
            max_repeats=MAX_SUPER_RETRY_COUNT,
            use_context=False,
            throw_if_fail=True,
        )
        
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